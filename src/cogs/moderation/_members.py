"""
Moderation — member-action commands (kick, ban, unban, warn, mute …).
"""
import asyncio as _asyncio

import discord
from discord.ext import commands
from config.emojis import get_emoji
from ._messages import msg, _cv2


class _ModConfirmView(discord.ui.LayoutView):
    """LayoutView with Confirm + Cancel buttons for kick/ban confirmation."""

    def __init__(self, prompt: str, *, invoker_id: int, timeout: float = 30.0):
        super().__init__(timeout=timeout)
        self.invoker_id = invoker_id
        self.confirmed: bool | None = None
        self._event = _asyncio.Event()

        self._confirm_btn = discord.ui.Button(
            label="Confirm",
            style=discord.ButtonStyle.danger,
            emoji=get_emoji("icon_tick") or "✅",
        )
        self._cancel_btn = discord.ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_cross") or "❌",
        )
        self._confirm_btn.callback = self._on_confirm
        self._cancel_btn.callback = self._on_cancel

        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=prompt),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(self._confirm_btn, self._cancel_btn),
        ))

    async def _check_invoker(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.invoker_id:
            err = discord.ui.LayoutView()
            err.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"{get_emoji('icon_cross')} Only the command invoker can use these buttons.")
            ))
            await interaction.response.send_message(view=err, ephemeral=True)
            return False
        return True

    async def _on_confirm(self, interaction: discord.Interaction):
        if not await self._check_invoker(interaction):
            return
        self.confirmed = True
        self._confirm_btn.disabled = True
        self._cancel_btn.disabled = True
        await interaction.response.edit_message(view=self)
        self._event.set()

    async def _on_cancel(self, interaction: discord.Interaction):
        if not await self._check_invoker(interaction):
            return
        self.confirmed = False
        self._confirm_btn.disabled = True
        self._cancel_btn.disabled = True
        cancelled = discord.ui.LayoutView()
        cancelled.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('icon_cross')} Action cancelled.")
        ))
        await interaction.response.edit_message(view=cancelled)
        self._event.set()

    async def on_timeout(self):
        if self.confirmed is None:
            self.confirmed = False
            self._event.set()

    async def wait_for_response(self) -> bool:
        await self._event.wait()
        return bool(self.confirmed)


class MembersMixin:
    """Kick, ban, unban, warn, mute/unmute/tempmute commands."""

    # ── KICK ────────────────────────────────────────────────────────────────
    @commands.hybrid_command(description="Kick a member from the server",
                             help="{ 'en': 'Kick a member from the server.', 'de': 'Mitglied kicken.', 'es': 'Expulsa a un miembro del servidor.' }")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="kick"))

        prompt = (
            f"### 👟 Confirm Kick\n"
            f"Are you sure you want to kick **{member}** (`{member.id}`)?\n"
            f"**Reason:** {reason}"
        )
        confirm_view = _ModConfirmView(prompt, invoker_id=ctx.author.id)
        confirm_msg = await ctx.send(view=confirm_view)

        if not await confirm_view.wait_for_response():
            return

        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            return await ctx.send(view=_cv2(f"{get_emoji('icon_cross')} I don't have permission to kick that member."))
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(f"{get_emoji('icon_cross')} Failed to kick: {e}"))

        result_view = _cv2(msg(ctx, "kicked", member=member, reason=reason))
        try:
            await confirm_msg.edit(view=result_view)
        except Exception:
            await ctx.send(view=result_view)

        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Kick\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Kick", body, target_id=member.id, action_key="Kick")

    # ── BAN ─────────────────────────────────────────────────────────────────
    @commands.hybrid_command(description="Ban a member from the server",
                             help="{ 'en': 'Ban a member from the server.', 'de': 'Mitglied bannen.', 'es': 'Banea a un miembro del servidor.' }")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User = None, *, reason: str = "No reason provided"):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="ban"))

        prompt = (
            f"### 🔨 Confirm Ban\n"
            f"Are you sure you want to ban **{member}** (`{member.id}`)?\n"
            f"**Reason:** {reason}"
        )
        confirm_view = _ModConfirmView(prompt, invoker_id=ctx.author.id)
        confirm_msg = await ctx.send(view=confirm_view)

        if not await confirm_view.wait_for_response():
            return

        try:
            await ctx.guild.ban(member, reason=reason, delete_message_days=7)
        except discord.Forbidden:
            return await ctx.send(view=_cv2(f"{get_emoji('icon_cross')} I don't have permission to ban that user."))
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(f"{get_emoji('icon_cross')} Failed to ban: {e}"))

        result_view = _cv2(msg(ctx, "banned", member=member, reason=reason))
        try:
            await confirm_msg.edit(view=result_view)
        except Exception:
            await ctx.send(view=result_view)

        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Ban\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Ban", body, target_id=member.id, action_key="Ban")

    # ── UNBAN ────────────────────────────────────────────────────────────────
    @commands.hybrid_command(description="Unban a user by ID",
                             help="{ 'en': 'Unban a member from the server.', 'de': 'Mitglied entbannen.', 'es': 'Desbanea a un miembro del servidor.' }")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id=None, reason=None):
        if not user_id:
            return await ctx.send(msg(ctx, "no_user_id"))
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(view=_cv2(msg(ctx, "unbanned", user=user)))
        body = (
            f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n"
            f"**Action:** Unban\n**Reason:** {reason or 'No reason provided'}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Unban", body, target_id=user.id, action_key="Unban")

    # ── WARN ─────────────────────────────────────────────────────────────────
    @commands.hybrid_command(description="Warn a member",
                             help="{ 'en': 'Warn a member.', 'de': 'Mitglied verwarnen.', 'es': 'Advierte a un miembro.' }")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="warn"))
        utils.add_warn(ctx.guild.id, member.id, ctx.author.id, reason)
        await ctx.send(view=_cv2(msg(ctx, "warned", member=member, reason=reason)))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Warn\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Warn", body, target_id=member.id, action_key="Warn")

    @commands.hybrid_command(description="View a member's warnings",
                             help="{ 'en': 'View a members warnings.', 'de': 'Verwarnungen anzeigen.', 'es': 'Ver las advertencias de un miembro.' }")
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="view warnings for"))
        warns = utils.get_warnings(ctx.guild.id, member.id)
        if not warns:
            return await ctx.send(msg(ctx, "no_warnings", member=member))
        lines = msg(ctx, "warnings_title", member=member)
        for i, w in enumerate(warns, start=1):
            mod = ctx.guild.get_member(w["mod"])
            lines += f"**#{i}** by {mod or w['mod']}\nReason: {w['reason']}\nTime: {w['time']}\n\n"
        await ctx.send(view=_cv2(lines))

    @commands.hybrid_command(description="Clear all warnings for a member",
                             help="{ 'en': 'Clear all warnings for a member.', 'de': 'Verwarnungen löschen.', 'es': 'Borra todas las advertencias de un miembro.' }")
    @commands.has_permissions(moderate_members=True)
    async def clearwarnings(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member_warns"))
        utils.clear_warnings(ctx.guild.id, member.id)
        await ctx.send(msg(ctx, "warnings_cleared", member=member))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Clear Warnings\n**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Clear Warnings", body, target_id=member.id)

    # ── MUTE / TEMPMUTE / UNMUTE ─────────────────────────────────────────────
    @commands.hybrid_command(description="Mute a member",
                             help="{ 'en': 'Mute a member.', 'de': 'Mitglied stummschalten.', 'es': 'Silencia a un miembro.' }")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="mute"))
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        await utils.mute_member(ctx.guild, member, duration=None, reason=reason)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "muted", member=member, reason=reason))
        ))
        await ctx.send(view=view)
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Mute\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Mute", body, target_id=member.id, action_key="Mute")

    @commands.hybrid_command(description="Temporarily mute a member (seconds)",
                             help="{ 'en': 'Temporarily mute a member (seconds).', 'de': 'Zeitlich stummschalten.', 'es': 'Silencia temporalmente a un miembro (segundos).' }")
    @commands.has_permissions(moderate_members=True)
    async def tempmute(self, ctx, member: discord.Member = None, duration=None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="tempmute"))
        if not duration:
            return await ctx.send(msg(ctx, "no_duration"))
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        await utils.mute_member(ctx.guild, member, duration=int(duration), reason=reason)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "tempmuted", member=member, duration=duration, reason=reason))
        ))
        await ctx.send(view=view)
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Tempmute\n**Duration:** {duration}s\n**Reason:** {reason}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Tempmute", body, target_id=member.id, action_key="Tempmute")

    @commands.hybrid_command(description="Unmute a member",
                             help="{ 'en': 'Unmute a member.', 'de': 'Stummschaltung aufheben.', 'es': 'Quita el silencio a un miembro.' }")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="unmute"))
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        await utils.unmute_member(member, reason=f"Unmuted by {ctx.author}")
        await ctx.send(msg(ctx, "unmuted", member=member))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Action:** Unmute\n**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Unmute", body, target_id=member.id)

    # ── NICK ─────────────────────────────────────────────────────────────────
    @commands.hybrid_command(description="Change a member's nickname",
                             help="{ 'en': 'Change a members nickname.', 'de': 'Spitznamen ändern.', 'es': 'Cambia el apodo de un miembro.' }")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member = None, *, nickname=None):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="rename"))
        if not nickname:
            return await ctx.send(msg(ctx, "no_nickname"))
        await member.edit(nick=nickname)
        await ctx.send(msg(ctx, "nick_changed", member=member, nickname=nickname))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**New Nickname:** `{nickname}`\n**Changed By:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Nickname Changed", body, target_id=member.id)
