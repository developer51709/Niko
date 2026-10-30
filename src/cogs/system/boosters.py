"""Per-server boost announcements and member-owned booster roles."""

from __future__ import annotations

import asyncio
import logging
import re
from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands

from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

log = logging.getLogger(__name__)

MESSAGES = load_locales(__package__, "boosters")
msg = make_flat_msg(MESSAGES)

DEFAULT_BOOST_MESSAGE = (
    "Thank you {user} for boosting {server}! We now have {boost_count} boosts."
)
DEFAULT_UNBOOST_MESSAGE = (
    "{user} is no longer boosting {server}. We now have {boost_count} boosts."
)
HEX_COLOR = re.compile(r"^#?([0-9a-fA-F]{6})$")


async def get_booster_config(pool, guild_id: int) -> dict:
    row = await pool.fetchrow(
        "SELECT notifications_enabled, roles_enabled, channel_id, "
        "boost_message, unboost_message FROM booster_config WHERE guild_id = $1",
        guild_id,
    )
    if row is None:
        return {
            "notifications_enabled": False,
            "roles_enabled": False,
            "channel_id": None,
            "boost_message": DEFAULT_BOOST_MESSAGE,
            "unboost_message": DEFAULT_UNBOOST_MESSAGE,
        }
    return {
        "notifications_enabled": bool(row.get("notifications_enabled")),
        "roles_enabled": bool(row.get("roles_enabled")),
        "channel_id": row.get("channel_id"),
        "boost_message": row.get("boost_message") or DEFAULT_BOOST_MESSAGE,
        "unboost_message": row.get("unboost_message") or DEFAULT_UNBOOST_MESSAGE,
    }


def _parse_color(value: str) -> discord.Colour | None:
    match = HEX_COLOR.fullmatch(value.strip())
    if not match:
        return None
    return discord.Colour(int(match.group(1), 16))


def _render_template(template: str, member: discord.Member) -> str:
    guild = member.guild
    values = {
        "{user}": member.mention,
        "{name}": discord.utils.escape_markdown(member.display_name),
        "{server}": discord.utils.escape_markdown(guild.name),
        "{boost_count}": str(guild.premium_subscription_count or 0),
        "{boost_level}": str(guild.premium_tier or 0),
    }
    for token, value in values.items():
        template = template.replace(token, value)
    return template[:2000]


def _has_guild_feature(guild: discord.Guild, feature: str) -> bool:
    return feature in getattr(guild, "features", ())


class BoosterRoles(commands.Cog):
    """Manage boost notifications and personal booster roles."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._member_locks: dict[tuple[int, int], asyncio.Lock] = defaultdict(asyncio.Lock)
        self._syncing_guilds: set[int] = set()
        self._sync_again: set[int] = set()

    async def _config(self, guild_id: int) -> dict:
        if self.bot.cxn is None:
            raise RuntimeError("The bot database is unavailable.")
        return await get_booster_config(self.bot.cxn, guild_id)

    def _bot_member(self, guild: discord.Guild) -> discord.Member | None:
        if self.bot.user is None:
            return None
        return guild.get_member(self.bot.user.id)

    def _can_manage_roles(self, guild: discord.Guild) -> bool:
        me = self._bot_member(guild)
        return bool(me and me.guild_permissions.manage_roles)

    async def _ensure_role(self, member: discord.Member) -> discord.Role | None:
        config = await self._config(member.guild.id)
        if not config["roles_enabled"] or member.premium_since is None:
            return None
        if not self._can_manage_roles(member.guild):
            raise PermissionError("Niko needs Manage Roles to create booster roles.")

        key = (member.guild.id, member.id)
        async with self._member_locks[key]:
            row = await self.bot.cxn.fetchrow(
                "SELECT role_id FROM booster_roles WHERE guild_id = $1 AND user_id = $2",
                member.guild.id,
                member.id,
            )
            role = member.guild.get_role(int(row["role_id"])) if row else None
            if row and role is None:
                await self.bot.cxn.execute(
                    "DELETE FROM booster_roles WHERE guild_id = $1 AND user_id = $2",
                    member.guild.id,
                    member.id,
                )
            if role is not None:
                if role not in member.roles:
                    await member.add_roles(role, reason="Restore the member's booster role")
                return role

            role = await member.guild.create_role(
                name=f"{member.display_name[:80]}'s Booster Role",
                permissions=discord.Permissions.none(),
                mentionable=False,
                hoist=False,
                reason="Create a personal role for an active server booster",
            )
            try:
                await member.add_roles(role, reason="Assign the member's booster role")
                await self.bot.cxn.execute(
                    "INSERT OR REPLACE INTO booster_roles (guild_id, user_id, role_id) "
                    "VALUES ($1, $2, $3)",
                    member.guild.id,
                    member.id,
                    role.id,
                )
            except Exception:
                try:
                    await role.delete(reason="Clean up an unrecorded booster role")
                except discord.HTTPException:
                    log.exception("Could not clean up unrecorded booster role %s", role.id)
                raise
            return role

    async def _remove_role(self, guild: discord.Guild, user_id: int) -> None:
        row = await self.bot.cxn.fetchrow(
            "SELECT role_id FROM booster_roles WHERE guild_id = $1 AND user_id = $2",
            guild.id,
            user_id,
        )
        if row is None:
            return
        role = guild.get_role(int(row["role_id"]))
        if role is not None:
            try:
                await role.delete(reason="The role owner's server boost ended")
            except discord.NotFound:
                pass
            except discord.HTTPException:
                log.exception("Could not delete booster role %s in guild %s", role.id, guild.id)
                return
        await self.bot.cxn.execute(
            "DELETE FROM booster_roles WHERE guild_id = $1 AND user_id = $2",
            guild.id,
            user_id,
        )

    async def sync_guild(self, guild: discord.Guild) -> None:
        """Apply the current role switch to cached boosters and saved roles."""
        if self.bot.cxn is None:
            return
        if guild.id in self._syncing_guilds:
            self._sync_again.add(guild.id)
            return
        self._syncing_guilds.add(guild.id)
        try:
            config = await self._config(guild.id)
            rows = await self.bot.cxn.fetch(
                "SELECT user_id FROM booster_roles WHERE guild_id = $1", guild.id
            )
            if not config["roles_enabled"]:
                for row in rows:
                    await self._remove_role(guild, int(row["user_id"]))
                return
            if not self._can_manage_roles(guild):
                log.warning(
                    "Booster roles are enabled but the bot lacks Manage Roles in guild %s",
                    guild.id,
                )
                return

            cached_members = {member.id: member for member in guild.members}
            for row in rows:
                member = cached_members.get(int(row["user_id"]))
                if member is not None and member.premium_since is None:
                    await self._remove_role(guild, member.id)
            for member in cached_members.values():
                if member.premium_since is not None:
                    try:
                        await self._ensure_role(member)
                    except (discord.HTTPException, PermissionError):
                        log.exception(
                            "Could not provision booster role for %s in guild %s",
                            member.id,
                            guild.id,
                        )
        except Exception:
            log.exception("Could not sync booster roles in guild %s", guild.id)
        finally:
            self._syncing_guilds.discard(guild.id)
            if guild.id in self._sync_again:
                self._sync_again.discard(guild.id)
                asyncio.create_task(self.sync_guild(guild))

    async def _send_boost_notification(
        self, member: discord.Member, *, is_boosting: bool, config: dict
    ) -> None:
        if not config["notifications_enabled"] or not config["channel_id"]:
            return
        channel = member.guild.get_channel(int(config["channel_id"]))
        if not isinstance(channel, discord.TextChannel):
            log.warning(
                "Configured boost announcement channel %s is unavailable in guild %s",
                config["channel_id"],
                member.guild.id,
            )
            return
        template = config["boost_message"] if is_boosting else config["unboost_message"]
        try:
            await channel.send(
                _render_template(template, member),
                allowed_mentions=discord.AllowedMentions(
                    users=[member], roles=False, everyone=False, replied_user=False
                ),
            )
        except discord.HTTPException:
            log.exception("Could not send boost notification in guild %s", member.guild.id)

    async def _interaction_role(
        self, interaction: discord.Interaction
    ) -> discord.Role | None:
        member = interaction.user
        if not isinstance(member, discord.Member) or interaction.guild is None:
            await interaction.followup.send(msg(interaction, "guild_only"), ephemeral=True)
            return None
        try:
            config = await self._config(interaction.guild.id)
        except Exception:
            log.exception("Could not load booster settings for guild %s", interaction.guild.id)
            await interaction.followup.send(msg(interaction, "settings_failed"), ephemeral=True)
            return None
        if not config["roles_enabled"]:
            await interaction.followup.send(msg(interaction, "roles_disabled"), ephemeral=True)
            return None
        if member.premium_since is None:
            await interaction.followup.send(msg(interaction, "not_boosting"), ephemeral=True)
            return None
        try:
            role = await self._ensure_role(member)
        except PermissionError:
            await interaction.followup.send(msg(interaction, "need_manage_roles"), ephemeral=True)
            return None
        except discord.HTTPException:
            log.exception("Could not provision booster role for member %s", member.id)
            await interaction.followup.send(msg(interaction, "role_create_failed"), ephemeral=True)
            return None
        except Exception:
            log.exception("Could not load booster role for member %s", member.id)
            await interaction.followup.send(msg(interaction, "role_load_failed"), ephemeral=True)
            return None
        if role is None:
            await interaction.followup.send(msg(interaction, "role_missing"), ephemeral=True)
        return role

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        for guild in self.bot.guilds:
            asyncio.create_task(self.sync_guild(guild))

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        if (before.premium_since is None) == (after.premium_since is None):
            return
        try:
            config = await self._config(after.guild.id)
            is_boosting = after.premium_since is not None
            if is_boosting and config["roles_enabled"]:
                try:
                    await self._ensure_role(after)
                except discord.HTTPException:
                    log.exception(
                        "Could not provision booster role for %s in guild %s",
                        after.id,
                        after.guild.id,
                    )
            elif not is_boosting:
                await self._remove_role(after.guild, after.id)
            await self._send_boost_notification(
                after, is_boosting=is_boosting, config=config
            )
        except Exception:
            log.exception("Could not process boost change for member %s", after.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        try:
            await self._remove_role(member.guild, member.id)
        except Exception:
            log.exception("Could not clean up booster role for departing member %s", member.id)

    boosterrole = app_commands.Group(
        name="boosterrole",
        description=CMDS.text("boosterrole.description"),
    )

    @boosterrole.command(name="rename", description=CMDS.text("boosterrole.rename.description"))
    @app_commands.describe(name=CMDS.arg("boosterrole.rename", "name"))
    async def boosterrole_rename(
        self, interaction: discord.Interaction, name: str
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        name = name.strip()
        if not name or len(name) > 100:
            await interaction.followup.send(msg(interaction, "role_name_invalid"), ephemeral=True)
            return
        role = await self._interaction_role(interaction)
        if role is None:
            return
        try:
            await role.edit(name=name, reason="Booster customized their role")
            await interaction.followup.send(
                msg(interaction, "role_renamed", name=discord.utils.escape_markdown(name)),
                ephemeral=True,
            )
        except discord.HTTPException:
            await interaction.followup.send(msg(interaction, "role_rename_failed"), ephemeral=True)

    @boosterrole.command(name="color", description=CMDS.text("boosterrole.color.description"))
    @app_commands.describe(hex_color=CMDS.arg("boosterrole.color", "hex_color"))
    async def boosterrole_color(
        self, interaction: discord.Interaction, hex_color: str
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        color = _parse_color(hex_color)
        if color is None:
            await interaction.followup.send(msg(interaction, "colour_invalid"), ephemeral=True)
            return
        role = await self._interaction_role(interaction)
        if role is None:
            return
        try:
            await role.edit(
                colour=color,
                secondary_colour=None,
                secondary_color=None,
                tertiary_colour=None,
                tertiary_color=None,
                reason="Booster customized their role color",
            )
            await interaction.followup.send(msg(interaction, "colour_updated"), ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send(msg(interaction, "colour_failed"), ephemeral=True)

    @boosterrole.command(name="gradient", description=CMDS.text("boosterrole.gradient.description"))
    @app_commands.describe(
        first=CMDS.arg("boosterrole.gradient", "first"),
        second=CMDS.arg("boosterrole.gradient", "second"),
    )
    async def boosterrole_gradient(
        self,
        interaction: discord.Interaction,
        first: str,
        second: str,
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        if guild is None or not _has_guild_feature(guild, "ENHANCED_ROLE_COLORS"):
            await interaction.followup.send(msg(interaction, "gradient_unavailable"), ephemeral=True)
            return
        colors = [_parse_color(value) for value in (first, second)]
        if any(color is None for color in colors):
            await interaction.followup.send(msg(interaction, "hex_invalid"), ephemeral=True)
            return
        role = await self._interaction_role(interaction)
        if role is None:
            return
        try:
            await role.edit(
                colour=colors[0],
                secondary_colour=colors[1],
                secondary_color=colors[1],
                tertiary_colour=None,
                tertiary_color=None,
                reason="Booster customized their role gradient",
            )
            await interaction.followup.send(msg(interaction, "gradient_updated"), ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send(msg(interaction, "gradient_failed"), ephemeral=True)

    @boosterrole.command(name="icon", description=CMDS.text("boosterrole.icon.description"))
    @app_commands.describe(image=CMDS.arg("boosterrole.icon", "image"))
    async def boosterrole_icon(
        self, interaction: discord.Interaction, image: discord.Attachment
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        if guild is None or not _has_guild_feature(guild, "ROLE_ICONS"):
            await interaction.followup.send(msg(interaction, "icon_unavailable"), ephemeral=True)
            return
        if image.content_type not in {"image/png", "image/jpeg"}:
            await interaction.followup.send(msg(interaction, "icon_type"), ephemeral=True)
            return
        if image.size > 256 * 1024:
            await interaction.followup.send(msg(interaction, "icon_too_large"), ephemeral=True)
            return
        role = await self._interaction_role(interaction)
        if role is None:
            return
        try:
            await role.edit(
                display_icon=await image.read(),
                reason="Booster customized their role icon",
            )
            await interaction.followup.send(msg(interaction, "icon_updated"), ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send(msg(interaction, "icon_failed"), ephemeral=True)

    @boosterrole.command(name="clear-icon", description=CMDS.text("boosterrole.clear-icon.description"))
    async def boosterrole_clear_icon(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        role = await self._interaction_role(interaction)
        if role is None:
            return
        try:
            await role.edit(display_icon=None, reason="Booster cleared their role icon")
            await interaction.followup.send(msg(interaction, "icon_removed"), ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send(msg(interaction, "icon_remove_failed"), ephemeral=True)

    @boosterrole.command(name="share", description=CMDS.text("boosterrole.share.description"))
    @app_commands.describe(member=CMDS.arg("boosterrole.share", "member"))
    async def boosterrole_share(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        role = await self._interaction_role(interaction)
        if role is None:
            return
        if member.id == interaction.user.id:
            await interaction.followup.send(msg(interaction, "share_self"), ephemeral=True)
            return
        if role in member.roles:
            await interaction.followup.send(
                msg(interaction, "share_already", member=member.mention), ephemeral=True
            )
            return
        try:
            await member.add_roles(role, reason="Booster shared their personal role")
            await interaction.followup.send(
                msg(interaction, "share_ok", role=role.mention, member=member.mention),
                ephemeral=True,
            )
        except discord.HTTPException:
            await interaction.followup.send(msg(interaction, "share_failed"), ephemeral=True)

    @boosterrole.command(name="unshare", description=CMDS.text("boosterrole.unshare.description"))
    @app_commands.describe(member=CMDS.arg("boosterrole.unshare", "member"))
    async def boosterrole_unshare(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        role = await self._interaction_role(interaction)
        if role is None:
            return
        if member.id == interaction.user.id:
            await interaction.followup.send(msg(interaction, "unshare_self"), ephemeral=True)
            return
        if role not in member.roles:
            await interaction.followup.send(
                msg(interaction, "unshare_missing", member=member.mention), ephemeral=True
            )
            return
        try:
            await member.remove_roles(role, reason="Booster stopped sharing their personal role")
            await interaction.followup.send(
                msg(interaction, "unshare_ok", member=member.mention), ephemeral=True
            )
        except discord.HTTPException:
            await interaction.followup.send(msg(interaction, "unshare_failed"), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BoosterRoles(bot))
