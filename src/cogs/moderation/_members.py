"""
Moderation — member-action commands (kick, ban, unban, warn, mute …).
"""
import asyncio as _asyncio
from datetime import datetime

import discord
from discord.ext import commands
from config.emojis import get_emoji
from ._messages import msg, _cv2
from utils.i18n import make_flat_msg
from utils.locales import load_locales
from utils.ratelimit import mass_role_limiter

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

#: The mass role panel's own table, kept beside this module's commands.
MASSROLE = load_locales(__package__, "massrole")
_massmsg = make_flat_msg(MASSROLE, {"loading": get_emoji("loading"), "tick": get_emoji("tick"),
                                     "cross": get_emoji("cross"), "warning": get_emoji("warning")})


def _can_view_warnings(ctx) -> bool:
    """Reading a member's warning history needs Moderate Members or Manage
    Messages — a helper who can already clear this channel's messages should not
    have to be given Timeout Members just to read the list.

    Reads ``permissions``, which both a Context and an Interaction expose as the
    member's resolved channel permissions, so one check covers prefix and slash.
    """
    permissions = getattr(ctx, "permissions", None) or getattr(ctx, "guild_permissions", None)
    return bool(permissions and (permissions.moderate_members or permissions.manage_messages))


def _relative_time(value) -> str:
    """A Discord timestamp for a stored ISO time, in the bot's usual style.

    Warnings are stored as ISO strings; printing those raw (as this used to)
    showed the reader a UTC wall clock instead of their own time zone.
    """
    try:
        return f"<t:{int(datetime.fromisoformat(str(value)).timestamp())}:R>"
    except (TypeError, ValueError, OverflowError, OSError):
        return str(value) if value else "unknown"


class _ModConfirmView(discord.ui.LayoutView):
    """LayoutView with Confirm + Cancel buttons for kick/ban confirmation.

    Every string is passed in already localised, because the timeout and the
    invoker check both have to answer without a command context to hand.
    """

    def __init__(self, prompt: str, *, invoker_id: int, cancelled_text: str,
                 timeout_text: str, invoker_text: str, timeout: float = 30.0,
                 confirm_label: str = "Confirm", cancel_label: str = "Cancel"):
        super().__init__(timeout=timeout)
        self.invoker_id = invoker_id
        self.confirmed: bool | None = None
        self._cancelled_text = cancelled_text
        self._timeout_text = timeout_text
        self._invoker_text = invoker_text
        self._event = _asyncio.Event()

        # No Unicode fallback: a member of the generated set or no emoji at
        # all, so the buttons never draw Discord's colourful built-ins.
        self._confirm_btn = discord.ui.Button(
            label=confirm_label,
            style=discord.ButtonStyle.danger,
            emoji=get_emoji("tick"),
        )
        self._cancel_btn = discord.ui.Button(
            label=cancel_label,
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("cross"),
        )
        self._confirm_btn.callback = self._on_confirm
        self._cancel_btn.callback = self._on_cancel

        self._text = discord.ui.TextDisplay(content=prompt)
        self.add_item(discord.ui.Container(
            self._text,
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(self._confirm_btn, self._cancel_btn),
        ))

    def _disable(self) -> None:
        self._confirm_btn.disabled = True
        self._cancel_btn.disabled = True

    def _notice(self, text: str) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
        return view

    async def _check_invoker(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.invoker_id:
            await interaction.response.send_message(
                view=self._notice(self._invoker_text), ephemeral=True)
            return False
        return True

    async def _on_confirm(self, interaction: discord.Interaction):
        if not await self._check_invoker(interaction):
            return
        self.confirmed = True
        self._disable()
        await interaction.response.edit_message(view=self)
        self._event.set()

    async def _on_cancel(self, interaction: discord.Interaction):
        if not await self._check_invoker(interaction):
            return
        self.confirmed = False
        self._disable()
        await interaction.response.edit_message(view=self._notice(self._cancelled_text))
        self._event.set()

    async def on_timeout(self):
        if self.confirmed is not None:
            # Already answered: the caller replaced this message with its result.
            return
        self.confirmed = False
        self._event.set()
        self._disable()
        self._text.content = self._timeout_text
        try:
            if self.message is not None:
                await self.message.edit(view=self)
        except (discord.HTTPException, discord.Forbidden):
            # The prompt is gone; the disabled buttons went with it.
            pass

    async def wait_for_response(self) -> bool:
        await self._event.wait()
        return bool(self.confirmed)


MASSROLE_ACTIONS = ("add", "remove")
MASSROLE_TARGETS = ("humans", "bots", "all")


def _massrole_action(locale, action: str) -> str:
    return _massmsg(locale, f"action_{action}")


def _massrole_target(locale, target: str) -> str:
    return _massmsg(locale, f"target_{target}")


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
        locale = panel.locale
        super().__init__(
            placeholder=_massmsg(locale, "action_placeholder"),
            options=[
                discord.SelectOption(
                    label=label,
                    value=value,
                    description=_massmsg(locale, "action_option_description", label=label),
                    default=panel.action == value,
                )
                for value in MASSROLE_ACTIONS
                for label in [_massrole_action(locale, value)]
            ],
        )

    async def callback(self, interaction: discord.Interaction):
        self.panel.action = self.values[0]
        await self.panel.refresh(interaction)


class _MassRoleTargetSelect(discord.ui.Select):
    def __init__(self, panel: "MassRolePanel"):
        self.panel = panel
        locale = panel.locale
        super().__init__(
            placeholder=_massmsg(locale, "target_placeholder"),
            options=[
                discord.SelectOption(
                    label=label,
                    value=value,
                    description=_massmsg(locale, "target_option_description", label=label),
                    default=panel.target_type == value,
                )
                for value in MASSROLE_TARGETS
                for label in [_massrole_target(locale, value)]
            ],
        )

    async def callback(self, interaction: discord.Interaction):
        self.panel.target_type = self.values[0]
        await self.panel.refresh(interaction)


class _MassRoleSelect(discord.ui.RoleSelect):
    def __init__(self, panel: "MassRolePanel"):
        self.panel = panel
        super().__init__(
            placeholder=_massmsg(panel.locale, "roles_placeholder"),
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
            label=_massmsg(panel.locale, "apply"),
            style=discord.ButtonStyle.success,
            emoji=get_emoji("tick"),
            disabled=not panel.selected_roles,
        )

    async def callback(self, interaction: discord.Interaction):
        await self.panel.apply(interaction)


class MassRolePanel(discord.ui.LayoutView):
    """Invoker-bound Components v2 panel for a rate-limited mass role change."""

    def __init__(self, guild: discord.Guild, invoker_id: int, bot_member: discord.Member, locale=None):
        super().__init__(timeout=600)
        self.guild = guild
        self.invoker_id = invoker_id
        self.bot_member = bot_member
        self.locale = locale
        self.action = "add"
        self.target_type = "humans"
        self.selected_roles: tuple[discord.Role, ...] = ()
        self._running = False
        self._build()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Guard every select and button, including after permissions change."""
        if interaction.user.id != self.invoker_id:
            await interaction.response.send_message(
                _massmsg(interaction, "not_invoker"), ephemeral=True
            )
            return False
        if interaction.guild is None or interaction.guild.id != self.guild.id:
            await interaction.response.send_message(
                _massmsg(interaction, "wrong_guild"), ephemeral=True
            )
            return False
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                _massmsg(interaction, "need_user_permission"), ephemeral=True
            )
            return False
        if not self.bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message(
                _massmsg(interaction, "need_bot_permission"), ephemeral=True
            )
            return False
        if self._running:
            await interaction.response.send_message(
                _massmsg(interaction, "already_running"), ephemeral=True
            )
            return False
        return True

    def _build(self) -> None:
        self.clear_items()
        role_text = ", ".join(role.mention for role in self.selected_roles) or _massmsg(
            self.locale, "no_roles_selected"
        )
        summary = _massmsg(
            self.locale, "body",
            action=_massrole_action(self.locale, self.action),
            targets=_massrole_target(self.locale, self.target_type),
            roles=role_text,
        )
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=_massmsg(self.locale, "title")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
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
        await interaction.response.edit_message(view=self, allowed_mentions=discord.AllowedMentions.none())

    def _plan(self) -> tuple[list[tuple[discord.Member, tuple[discord.Role, ...]]], int, str | None]:
        if not self.selected_roles:
            return [], 0, _massmsg(self.locale, "select_role_first")

        invalid_roles = [
            role for role in self.selected_roles
            if role.is_default() or role.managed or role >= self.bot_member.top_role
        ]
        if invalid_roles:
            names = ", ".join(f"`{role.name}`" for role in invalid_roles[:5])
            suffix = "…" if len(invalid_roles) > 5 else ""
            return [], 0, _massmsg(
                self.locale, "cannot_manage", names=names, suffix=suffix
            )

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
                view=_massrole_status_view(f"{get_emoji('cross')} {error}", discord.Colour.red())
            )

        self._running = True
        count = len(operations)
        estimate = _massrole_estimate_seconds(count)
        action_label = _massrole_action(interaction, self.action)
        target_label = _massrole_target(interaction, self.target_type)
        await interaction.response.edit_message(view=_massrole_status_view(
            _massmsg(
                interaction, "applying",
                action=action_label,
                targets=target_label,
                count=f"{count:,}",
                estimate=estimate,
            ),
            discord.Colour.orange(),
        ), allowed_mentions=discord.AllowedMentions.none())
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

        skipped_text = (
            _massmsg(interaction, "skipped", count=f"{skipped:,}") if skipped else ""
        )
        failed_text = (
            _massmsg(interaction, "failed", count=f"{failed:,}") if failed else ""
        )
        await interaction.message.edit(view=_massrole_status_view(
            _massmsg(
                interaction, "done",
                emoji=get_emoji("tick") if not failed else get_emoji("warning"),
                updated=f"{updated:,}",
                failed=failed_text,
                skipped=skipped_text,
            ),
            discord.Colour.green() if not failed else discord.Colour.orange(),
        ), allowed_mentions=discord.AllowedMentions.none())


class MembersMixin:
    """Kick, ban, unban, warn, mute/unmute/tempmute commands."""

    # ── KICK ────────────────────────────────────────────────────────────────
    @commands.hybrid_command(description=CMDS.text("kick.description"),
                             help=CMDS.help("kick"))
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        member: discord.Member = commands.parameter(default=None, description=CMDS.arg("kick", "member")),
        *,
        reason: str = commands.parameter(default="No reason provided", description=CMDS.arg("kick", "reason")),
    ):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="kick"))

        confirm_view = _ModConfirmView(
            msg(ctx, "confirm_kick", member=member, id=member.id, reason=reason),
            invoker_id=ctx.author.id,
            cancelled_text=msg(ctx, "cancelled"),
            timeout_text=msg(ctx, "timed_out"),
            invoker_text=msg(ctx, "invoker_only"),
            confirm_label=msg(ctx, "btn_confirm"),
            cancel_label=msg(ctx, "btn_cancel"),
        )
        confirm_msg = await ctx.send(view=confirm_view)

        if not await confirm_view.wait_for_response():
            return

        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_kick")))
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)))

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
    @commands.hybrid_command(description=CMDS.text("ban.description"),
                             help=CMDS.help("ban"))
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        member: discord.User = commands.parameter(default=None, description=CMDS.arg("ban", "member")),
        delete_days: int = commands.parameter(default=7, description=CMDS.arg("ban", "delete_days")),
        *,
        reason: str = commands.parameter(default="No reason provided", description=CMDS.arg("ban", "reason")),
    ):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="ban"))
        # Discord accepts 0–7 days. Clamping keeps a typo from failing the ban,
        # and the confirmation below always states what will be deleted.
        delete_days = max(0, min(int(delete_days if delete_days is not None else 7), 7))

        confirm_view = _ModConfirmView(
            msg(ctx, "confirm_ban", user=member, id=member.id, reason=reason, days=delete_days),
            invoker_id=ctx.author.id,
            cancelled_text=msg(ctx, "cancelled"),
            timeout_text=msg(ctx, "timed_out"),
            invoker_text=msg(ctx, "invoker_only"),
            confirm_label=msg(ctx, "btn_confirm"),
            cancel_label=msg(ctx, "btn_cancel"),
        )
        confirm_msg = await ctx.send(view=confirm_view)

        if not await confirm_view.wait_for_response():
            return

        try:
            await ctx.guild.ban(member, reason=reason, delete_message_days=delete_days)
        except discord.Forbidden:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_ban")))
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)))

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
    @commands.hybrid_command(description=CMDS.text("unban.description"), aliases=["pardon"],
                             help=CMDS.help("unban"))
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        ctx,
        user_id: str = commands.parameter(default=None, description=CMDS.arg("unban", "user_id")),
        *,
        reason: str = commands.parameter(default="No reason provided", description=CMDS.arg("unban", "reason")),
    ):
        """Unban by id — the user is not in the guild, so no Member converter."""
        if not user_id:
            return await ctx.send(msg(ctx, "no_user_id"))
        raw = str(user_id).strip()
        if raw.startswith("<@") and raw.endswith(">"):
            raw = raw.strip("<@!>")
        if not raw.isdigit():
            return await ctx.send(msg(ctx, "bad_user_id", value=user_id))

        try:
            user = await self.bot.fetch_user(int(raw))
        except discord.NotFound:
            return await ctx.send(view=_cv2(msg(ctx, "no_user_found")))
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)))

        try:
            # The reason goes to Discord as well as to Niko's log: kick and ban
            # both pass it, and without it the audit-log entry says nothing.
            await ctx.guild.unban(user, reason=reason)
        except discord.NotFound:
            return await ctx.send(view=_cv2(msg(ctx, "not_banned", user=user)))
        except discord.Forbidden:
            return await ctx.send(view=_cv2(msg(ctx, "cannot_unban")))
        except discord.HTTPException as e:
            return await ctx.send(view=_cv2(msg(ctx, "action_failed", error=e)))

        await ctx.send(view=_cv2(msg(ctx, "unbanned", user=user)))
        body = (
            f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n"
            f"**Action:** Unban\n**Reason:** {reason}\n"
            f"**Moderator:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Unban", body, target_id=user.id, action_key="Unban")

    # ── WARN ─────────────────────────────────────────────────────────────────
    @commands.hybrid_command(description=CMDS.text("warn.description"),
                             help=CMDS.help("warn"))
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def warn(
        self,
        ctx,
        member: discord.Member = commands.parameter(default=None, description=CMDS.arg("warn", "member")),
        *,
        reason: str = commands.parameter(default="No reason provided", description=CMDS.arg("warn", "reason")),
    ):
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

    @commands.hybrid_command(name="warnings", aliases=["warns"],
                             description=CMDS.text("warnings.description"),
                             help=CMDS.help("warnings"))
    @commands.guild_only()
    async def warnings(self, ctx, member: discord.Member = commands.parameter(default=None, description=CMDS.arg("warnings", "member"))):
        if not _can_view_warnings(ctx):
            return await ctx.send(view=_cv2(msg(ctx, "warnings_perms")))
        utils = self.utils()
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="view warnings for"))
        warns = await utils.get_warnings(ctx.guild.id, member.id)
        if not warns:
            return await ctx.send(msg(ctx, "no_warnings", member=member))
        lines = msg(ctx, "warnings_title", member=member)
        for index, warn in enumerate(warns, start=1):
            moderator = ctx.guild.get_member(warn["mod"])
            by = moderator.mention if moderator else f"ID `{warn['mod']}`"
            lines += (
                f"**#{index}** by {by}\n"
                f"Reason: {warn['reason']}\n"
                f"Time: {_relative_time(warn['time'])}\n\n"
            )
        await ctx.send(view=_cv2(lines))

    @commands.hybrid_command(name="clearwarnings", aliases=["clearwarns"],
                             description=CMDS.text("clearwarnings.description"),
                             help=CMDS.help("clearwarnings"))
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def clearwarnings(self, ctx, member: discord.Member = commands.parameter(default=None, description=CMDS.arg("clearwarnings", "member"))):
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
    @commands.hybrid_command(description=CMDS.text("mute.description"),
                             help=CMDS.help("mute"))
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def mute(
        self,
        ctx,
        member: discord.Member = commands.parameter(default=None, description=CMDS.arg("mute", "member")),
        *,
        reason: str = commands.parameter(default="No reason provided", description=CMDS.arg("mute", "reason")),
    ):
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

    @commands.hybrid_command(description=CMDS.text("tempmute.description"),
                             help=CMDS.help("tempmute"))
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def tempmute(
        self,
        ctx,
        member: discord.Member = commands.parameter(default=None, description=CMDS.arg("tempmute", "member")),
        duration=commands.parameter(default=None, description=CMDS.arg("tempmute", "duration")),
        *,
        reason: str = commands.parameter(default="No reason provided", description=CMDS.arg("tempmute", "reason")),
    ):
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

    @commands.hybrid_command(description=CMDS.text("unmute.description"),
                             help=CMDS.help("unmute"))
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member = commands.parameter(default=None, description=CMDS.arg("unmute", "member"))):
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
    @commands.hybrid_command(description=CMDS.text("nick.description"),
                             help=CMDS.help("nick"))
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def nick(
        self,
        ctx,
        member: discord.Member = commands.parameter(default=None, description=CMDS.arg("nick", "member")),
        *,
        nickname=commands.parameter(default=None, description=CMDS.arg("nick", "nickname")),
    ):
        if not member:
            return await ctx.send(msg(ctx, "no_member", action="rename"))
        if not nickname:
            return await ctx.send(msg(ctx, "no_nickname"))
        try:
            await member.edit(nick=nickname)
        except discord.Forbidden:
            return await ctx.send(msg(ctx, "nick_failed"))
        except discord.HTTPException as e:
            return await ctx.send(msg(ctx, "action_failed", error=e))
        await ctx.send(msg(ctx, "nick_changed", member=member, nickname=nickname))
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**New Nickname:** `{nickname}`\n**Changed By:** {ctx.author.mention}"
        )
        await self.logger().log_event(ctx.guild, "moderation", "Nickname Changed", body, target_id=member.id)

    # ── MASSROLE ─────────────────────────────────────────────────────────────
    @commands.hybrid_command(
        name="massrole",
        description=CMDS.text("massrole.description"),
        help=CMDS.help("massrole"),
    )
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def massrole(self, ctx):
        """Open the no-argument mass role management panel."""
        bot_member = ctx.guild.me or ctx.guild.get_member(self.bot.user.id)
        if bot_member is None or not bot_member.guild_permissions.manage_roles:
            return await ctx.send(_massmsg(ctx, "need_bot_permission"))
        await ctx.send(
            view=MassRolePanel(ctx.guild, ctx.author.id, bot_member, ctx),
            allowed_mentions=discord.AllowedMentions.none(),
        )
