"""
Moderation — member-action commands (kick, ban, unban, warn, mute …).
"""
import asyncio as _asyncio

import discord
from discord.ext import commands
from config.emojis import get_emoji
from ._messages import msg, _cv2
from utils.ratelimit import mass_role_limiter


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


MASSROLE_ACTIONS = {"add": "Add", "remove": "Remove"}
MASSROLE_TARGETS = {"humans": "Humans", "bots": "Bots", "all": "All"}


def _massrole_member_matches(member, target_type: str) -> bool:
    """Return whether a member belongs to the panel's selected target group."""
    if target_type == "humans":
        return not member.bot
    if target_type == "bots":
        return member.bot
    return True


def _massrole_estimate_seconds(member_count: int) -> int:
    """Estimate work time from the shared guild-scoped role limiter."""
    if member_count <= 0:
        return 0
    return max(1, int((member_count * mass_role_limiter.per) / mass_role_limiter.rate) + 1)


def _massrole_status_view(content: str, accent: discord.Colour) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=content),
        accent_colour=accent,
    ))
    return view


class _MassRoleActionSelect(discord.ui.Select):
    def __init__(self, panel: "MassRolePanel"):
        self.panel = panel
        super().__init__(
            placeholder="Choose an action…",
            options=[
                discord.SelectOption(
                    label=label,
                    value=value,
                    description=f"{label} the selected roles.",
                    default=panel.action == value,
                )
                for value, label in MASSROLE_ACTIONS.items()
            ],
        )

    async def callback(self, interaction: discord.Interaction):
        self.panel.action = self.values[0]
        await self.panel.refresh(interaction)


class _MassRoleTargetSelect(discord.ui.Select):
    def __init__(self, panel: "MassRolePanel"):
        self.panel = panel
        super().__init__(
            placeholder="Choose who to target…",
            options=[
                discord.SelectOption(
                    label=label,
                    value=value,
                    description=f"Apply this change to {label.lower()}.",
                    default=panel.target_type == value,
                )
                for value, label in MASSROLE_TARGETS.items()
            ],
        )

    async def callback(self, interaction: discord.Interaction):
        self.panel.target_type = self.values[0]
        await self.panel.refresh(interaction)


class _MassRoleSelect(discord.ui.RoleSelect):
    def __init__(self, panel: "MassRolePanel"):
        self.panel = panel
        super().__init__(
            placeholder="Choose roles (multiple allowed)…",
            min_values=0,
            max_values=25,
            default_values=list(panel.selected_roles),
            required=False,
        )

    async def callback(self, interaction: discord.Interaction):
        self.panel.selected_roles = tuple(self.values)
        await self.panel.refresh(interaction)


class _MassRoleApplyButton(discord.ui.Button):
    def __init__(self, panel: "MassRolePanel"):
        self.panel = panel
        super().__init__(
            label="Apply",
            style=discord.ButtonStyle.success,
            emoji=get_emoji("icon_tick") or "✅",
            disabled=not panel.selected_roles,
        )

    async def callback(self, interaction: discord.Interaction):
        await self.panel.apply(interaction)


class MassRolePanel(discord.ui.LayoutView):
    """Invoker-bound Components v2 panel for a rate-limited mass role change."""

    def __init__(self, guild: discord.Guild, invoker_id: int, bot_member: discord.Member):
        super().__init__(timeout=600)
        self.guild = guild
        self.invoker_id = invoker_id
        self.bot_member = bot_member
        self.action = "add"
        self.target_type = "humans"
        self.selected_roles: tuple[discord.Role, ...] = ()
        self._running = False
        self._build()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Guard every select and button, including after permissions change."""
        if interaction.user.id != self.invoker_id:
            await interaction.response.send_message(
                "Only the person who opened this panel can use it.", ephemeral=True
            )
            return False
        if interaction.guild is None or interaction.guild.id != self.guild.id:
            await interaction.response.send_message(
                "This panel can only be used in its original server.", ephemeral=True
            )
            return False
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You no longer have the **Manage Roles** permission.", ephemeral=True
            )
            return False
        if not self.bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "I need the **Manage Roles** permission before I can change roles.", ephemeral=True
            )
            return False
        if self._running:
            await interaction.response.send_message(
                "This mass role update is already in progress.", ephemeral=True
            )
            return False
        return True

    def _build(self) -> None:
        self.clear_items()
        role_text = ", ".join(role.mention for role in self.selected_roles) or "*No roles selected yet.*"
        summary = (
            "### Mass role manager\n"
            "Choose an action, target group, and one or more roles, then apply the change.\n\n"
            f"**Action:** {MASSROLE_ACTIONS[self.action]}\n"
            f"**Targets:** {MASSROLE_TARGETS[self.target_type]}\n"
            f"**Roles:** {role_text}"
        )
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=summary),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(_MassRoleActionSelect(self)),
            discord.ui.ActionRow(_MassRoleTargetSelect(self)),
            discord.ui.ActionRow(_MassRoleSelect(self)),
            discord.ui.ActionRow(_MassRoleApplyButton(self)),
            accent_colour=discord.Colour(0x5865F2),
        ))

    async def refresh(self, interaction: discord.Interaction) -> None:
        self._build()
        await interaction.response.edit_message(view=self)

    def _plan(self) -> tuple[list[tuple[discord.Member, tuple[discord.Role, ...]]], int, str | None]:
        if not self.selected_roles:
            return [], 0, "Select at least one role before applying the change."

        invalid_roles = [
            role for role in self.selected_roles
            if role.is_default() or role.managed or role >= self.bot_member.top_role
        ]
        if invalid_roles:
            names = ", ".join(f"`{role.name}`" for role in invalid_roles[:5])
            suffix = "…" if len(invalid_roles) > 5 else ""
            return [], 0, f"I cannot manage these roles: {names}{suffix}"

        operations: list[tuple[discord.Member, tuple[discord.Role, ...]]] = []
        skipped = 0
        for member in self.guild.members:
            if member.id == self.bot_member.id or not _massrole_member_matches(member, self.target_type):
                continue
            if member.top_role >= self.bot_member.top_role:
                skipped += 1
                continue
            if self.action == "add":
                roles = tuple(role for role in self.selected_roles if role.id not in {r.id for r in member.roles})
            else:
                roles = tuple(role for role in self.selected_roles if role.id in {r.id for r in member.roles})
            if roles:
                operations.append((member, roles))
        return operations, skipped, None

    async def apply(self, interaction: discord.Interaction) -> None:
        operations, skipped, error = self._plan()
        if error:
            return await interaction.response.edit_message(
                view=_massrole_status_view(f"{get_emoji('icon_cross')} {error}", discord.Colour.red())
            )

        self._running = True
        count = len(operations)
        estimate = _massrole_estimate_seconds(count)
        action_label = MASSROLE_ACTIONS[self.action]
        target_label = MASSROLE_TARGETS[self.target_type]
        await interaction.response.edit_message(view=_massrole_status_view(
            f"### {get_emoji('icon_loading')} Applying mass role update\n"
            f"**Action:** {action_label} · **Targets:** {target_label}\n"
            f"Updating **{count:,}** member{'s' if count != 1 else ''}. "
            f"Estimated completion: **about {estimate} second{'s' if estimate != 1 else ''}**.\n"
            "Please keep this panel open while Discord processes the changes.",
            discord.Colour.orange(),
        ))
        updated = 0
        failed = 0
        roles = ", ".join(role.name for role in self.selected_roles[:3])
        try:
            for member, member_roles in operations:
                await mass_role_limiter.acquire(self.guild.id)
                try:
                    if self.action == "add":
                        await member.add_roles(*member_roles, reason=f"Mass role update by {interaction.user} ({roles})")
                    else:
                        await member.remove_roles(*member_roles, reason=f"Mass role update by {interaction.user} ({roles})")
                    updated += 1
                except (discord.Forbidden, discord.HTTPException):
                    failed += 1
        finally:
            self.stop()

        skipped_text = f"\nSkipped **{skipped:,}** member{'s' if skipped != 1 else ''} above my role." if skipped else ""
        failed_text = f"\nFailed for **{failed:,}** member{'s' if failed != 1 else ''}." if failed else ""
        await interaction.message.edit(view=_massrole_status_view(
            f"### {get_emoji('icon_tick') if not failed else get_emoji('warning')} Mass role update complete\n"
            f"Successfully updated **{updated:,}** member{'s' if updated != 1 else ''}."
            f"{failed_text}{skipped_text}",
            discord.Colour.green() if not failed else discord.Colour.orange(),
        ))


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
        await utils.add_warn(ctx.guild.id, member.id, ctx.author.id, reason)
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
        warns = await utils.get_warnings(ctx.guild.id, member.id)
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
        await utils.clear_warnings(ctx.guild.id, member.id)
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
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "unmuted", member=member))
        ))
        await ctx.send(view=view)
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

    # ── MASSROLE ─────────────────────────────────────────────────────────────
    @commands.hybrid_command(
        name="massrole",
        description="Open an interactive panel to add or remove roles in bulk",
        help="{ 'en': 'Open an interactive panel to add or remove roles in bulk.', 'de': 'Öffne ein interaktives Panel, um Rollen gesammelt hinzuzufügen oder zu entfernen.', 'es': 'Abre un panel interactivo para añadir o quitar roles en masa.' }",
    )
    @commands.has_permissions(manage_roles=True)
    async def massrole(self, ctx):
        """Open the no-argument mass role management panel."""
        if ctx.guild is None:
            return await ctx.send("This command can only be used in a server.")
        bot_member = ctx.guild.me or ctx.guild.get_member(self.bot.user.id)
        if bot_member is None or not bot_member.guild_permissions.manage_roles:
            return await ctx.send("I need the **Manage Roles** permission before I can change roles.")
        await ctx.send(view=MassRolePanel(ctx.guild, ctx.author.id, bot_member))
