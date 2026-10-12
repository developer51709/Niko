"""Owner-operated structure and automation for Niko's official support server."""
from __future__ import annotations

import json

import discord

from config.ids import SUPPORT_GUILD
from utils import logging

ROLE_SPECS = {
    "staff": ("Niko Staff", 0xC8A882, True),
    "head_admin": ("Head Admin", 0xE74C3C, True),
    "moderator": ("Moderator", 0xE67E22, True),
    "head_support": ("Head of Support", 0x3498DB, True),
    "graphic_designer": ("Graphic Designer", 0x9B59B6, True),
    "support": ("Support Team", 0x2ECC71, True),
    "supporter": ("Supporter", 0xF1C40F, False),
    "bugbounty": ("Bug Bounty", 0xE84393, False),
    "partner": ("Partner", 0x1ABC9C, False),
    "member": ("Member", 0x95A5A6, False),
    "announcements_ping": ("Announcements", 0x5865F2, False),
    "events_ping": ("Events", 0x1ABC9C, False),
    "community_ping": ("Community", 0xE91E63, False),
    "polls_ping": ("Polls", 0x9B59B6, False),
}

# Channel blueprint: key -> (category, name, kind, staff_only)
CHANNEL_SPECS = {
    "welcome": ("START HERE", "welcome", "text", False),
    "rules": ("START HERE", "rules", "text", False),
    "announcements": ("START HERE", "announcements", "text", False),
    "roles": ("START HERE", "roles", "text", False),
    "status": ("START HERE", "niko-status", "text", False),
    "introductions": ("COMMUNITY", "introductions", "text", False),
    "general": ("COMMUNITY", "general", "text", False),
    "media": ("COMMUNITY", "share-your-setup", "text", False),
    "memes": ("COMMUNITY", "memes", "text", False),
    "suggestions": ("COMMUNITY", "suggestions", "text", False),
    "events": ("COMMUNITY", "events", "text", False),
    "event_chat": ("COMMUNITY", "event-chat", "text", False),
    "polls": ("COMMUNITY", "polls", "text", False),
    "event_voice": ("COMMUNITY", "Community Stage", "voice", False),
    "help": ("SUPPORT", "community-help", "forum", False),
    "tickets": ("SUPPORT", "create-a-ticket", "text", False),
    "logs": ("STAFF", "server-logs", "text", True),
    "automod_logs": ("STAFF", "automod-logs", "text", True),
    "scam_review": ("STAFF", "scam-review", "text", True),
    "staff_announcements": ("STAFF", "staff-announcements", "text", True),
    "staff_rules": ("STAFF", "staff-guidelines", "text", True),
    "staff_chat": ("STAFF", "staff-chat", "text", True),
    "staff_voice": ("STAFF", "staff-voice", "voice", True),
    "voice_join": ("VOICE MASTER", "Join to Create", "voice", False),
    "voice_panel": ("VOICE MASTER", "voice-master", "text", False),
}

CHANNEL_TOPICS = {
    "welcome": "Welcome new members and point them to the rules, roles, and support resources.",
    "rules": "Official Niko community rules and server information.",
    "announcements": "Official Niko updates. Notification roles are available in #roles.",
    "roles": "Choose optional pings for announcements, events, community news, and polls.",
    "status": "Official Niko service status and incident updates.",
    "introductions": "Introduce yourself to the Niko community.",
    "general": "Community conversation about Niko and beyond.",
    "media": "Share your desk, setup, art, and Niko screenshots.",
    "memes": "Keep memes friendly and within the community rules.",
    "suggestions": "Share ideas and feature suggestions for Niko.",
    "events": "Official event announcements and schedules.",
    "event_chat": "Talk about current and upcoming community events.",
    "polls": "Community polls and voting. Opt into the Polls role for pings.",
    "help": "Public peer-to-peer help forum. Open a private ticket for account or sensitive issues.",
    "tickets": "Open a private support ticket for account help, bugs, safety, or moderation appeals.",
    "staff_announcements": "Internal staff updates and operational notices.",
    "staff_rules": "Private staff guidelines and expectations.",
    "staff_chat": "Private staff coordination and discussion.",
    "logs": "Internal server event and moderation logs.",
    "automod_logs": "Internal automod actions and alerts.",
    "scam_review": "Private review queue for reported scam images.",
    "voice_panel": "Create a temporary voice channel by joining the voice room below.",
}

API_STEP_DELAY = 0.35

# Discord community servers prevent deleting channels referenced by these
# server-level settings. Repoint them to the new canonical channels first.
COMMUNITY_SYSTEM_CHANNELS = {
    "rules_channel": "rules",
    "public_updates_channel": "announcements",
    "safety_alerts_channel": "automod_logs",
}


def _community_system_channel_ids(guild: discord.Guild) -> set[int]:
    return {
        channel.id
        for attribute in COMMUNITY_SYSTEM_CHANNELS
        if (channel := getattr(guild, attribute, None)) is not None
    }


def _community_system_channels_need_relink(guild: discord.Guild) -> bool:
    for attribute, key in COMMUNITY_SYSTEM_CHANNELS.items():
        channel = getattr(guild, attribute, None)
        if channel is None:
            continue
        category_name, expected_name, kind, _ = CHANNEL_SPECS[key]
        expected_type = discord.ForumChannel if kind == "forum" else discord.TextChannel
        if (not isinstance(channel, expected_type) or channel.name != expected_name
                or getattr(getattr(channel, "category", None), "name", None) != category_name):
            return True
    return False


async def _replace_community_system_channels(guild: discord.Guild, channels: dict[str, int]) -> None:
    """Relink Discord's required community channels, then remove their old channels."""
    old_channels: dict[int, discord.TextChannel] = {}
    updates = {}
    for attribute, key in COMMUNITY_SYSTEM_CHANNELS.items():
        old_channel = getattr(guild, attribute, None)
        channel_id = channels.get(key)
        replacement = guild.get_channel(int(channel_id)) if channel_id else None
        if old_channel is None or replacement is None or old_channel.id == replacement.id:
            continue
        old_channels[old_channel.id] = old_channel
        updates[attribute] = replacement

    if not updates:
        return
    if not guild.me.guild_permissions.manage_guild:
        raise RuntimeError("Niko needs Manage Server to move the community rules, updates, and safety-alert channels safely.")

    await guild.edit(**updates, reason="Move community system channels to the reconciled Niko support structure")
    await _pace()
    for channel in old_channels.values():
        await channel.delete(reason="Replace obsolete Discord community system channel")
        await _pace()


async def _pace():
    import asyncio
    await asyncio.sleep(API_STEP_DELAY)


def _json_object(value) -> dict:
    if isinstance(value, dict):
        return value
    try:
        result = json.loads(value or "{}")
        return result if isinstance(result, dict) else {}
    except (TypeError, ValueError):
        return {}


async def get_support_ids(bot) -> dict:
    pool = getattr(bot, "cxn", None)
    if pool is None:
        return {"roles": {}, "channels": {}}
    row = await pool.fetchrow("SELECT role_ids, channel_ids FROM support_server_config WHERE guild_id = $1", SUPPORT_GUILD)
    if row is None:
        return {"roles": {}, "channels": {}}
    return {"roles": _json_object(row.get("role_ids")), "channels": _json_object(row.get("channel_ids"))}


async def support_role(bot, key: str):
    ids = await get_support_ids(bot)
    guild = bot.get_guild(SUPPORT_GUILD)
    role_id = ids["roles"].get(key)
    return guild.get_role(int(role_id)) if guild and role_id else None


async def persist_support_ids(bot, guild: discord.Guild, roles: dict, channels: dict) -> None:
    if guild.id != SUPPORT_GUILD:
        raise ValueError("Support configuration may only be stored for the configured support guild.")
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The database is not ready; support structure was not saved.")
    await pool.execute(
        "INSERT INTO support_server_config (guild_id, role_ids, channel_ids, updated_at) VALUES ($1, $2, $3, datetime('now')) "
        "ON CONFLICT (guild_id) DO UPDATE SET role_ids = $4, channel_ids = $5, updated_at = datetime('now')",
        guild.id, json.dumps(roles), json.dumps(channels), json.dumps(roles), json.dumps(channels),
    )


async def _ensure_role(guild: discord.Guild, key: str) -> discord.Role:
    name, colour, hoist = ROLE_SPECS[key]
    role = discord.utils.get(guild.roles, name=name)
    if role is None:
        role = await guild.create_role(name=name, colour=discord.Colour(colour), hoist=hoist, mentionable=key.endswith("_ping"), reason="Niko support server structure")
        await _pace()
    elif role.colour.value != colour or role.hoist != hoist or role.mentionable != key.endswith("_ping"):
        await role.edit(colour=discord.Colour(colour), hoist=hoist, mentionable=key.endswith("_ping"), reason="Reconcile Niko support server role")
        await _pace()
    return role


async def reconcile_structure(guild: discord.Guild, *, destructive: bool = False) -> tuple[dict, dict]:
    """Create/repair canonical roles, channels, and category-based permissions."""
    if guild.id != SUPPORT_GUILD:
        raise ValueError("This operation is restricted to the configured support guild.")
    bot_member = guild.me
    if bot_member is None or not bot_member.guild_permissions.manage_channels or not bot_member.guild_permissions.manage_roles:
        raise RuntimeError("Niko needs Manage Channels and Manage Roles in the support server.")
    if destructive and not bot_member.guild_permissions.administrator:
        raise RuntimeError("Niko needs Administrator for the destructive setup to avoid partially deleting channels it cannot manage.")
    if (not bot_member.guild_permissions.manage_guild
            and (destructive or _community_system_channels_need_relink(guild))):
        raise RuntimeError("Niko needs Manage Server to repoint the community rules, updates, and safety-alert channels before replacing them.")

    protected_system_channel_ids = _community_system_channel_ids(guild)
    if destructive:
        # Discord rejects deleting channels configured as community system
        # channels. Keep them until their settings point at replacements.
        for channel in list(guild.channels):
            if channel.id in protected_system_channel_ids:
                continue
            await channel.delete(reason="Owner-confirmed Niko support server rebuild")
            await _pace()
        for role in list(guild.roles):
            if role.is_default() or role.managed or role == bot_member.top_role or role >= bot_member.top_role:
                continue
            try:
                await role.delete(reason="Owner-confirmed Niko support server rebuild")
                await _pace()
            except discord.Forbidden:
                logging.warning("SupportServer", f"Could not delete role {role.name}; it is above Niko's role.")

    roles: dict[str, int] = {}
    for key in ROLE_SPECS:
        roles[key] = (await _ensure_role(guild, key)).id

    bot_member = guild.me
    everyone = guild.default_role
    staff_role = guild.get_role(roles["staff"])
    categories: dict[str, discord.CategoryChannel] = {}
    for category_name in dict.fromkeys(spec[0] for spec in CHANNEL_SPECS.values()):
        category = discord.utils.get(guild.categories, name=category_name)
        staff_only = category_name == "STAFF"
        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=not staff_only),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True),
            bot_member: discord.PermissionOverwrite(view_channel=True, manage_channels=True, manage_permissions=True, send_messages=True, read_message_history=True, connect=True, speak=True),
        }
        if category is None:
            category = await guild.create_category(category_name, overwrites=overwrites, reason="Niko support server structure")
            await _pace()
        else:
            await category.edit(overwrites=overwrites, reason="Reconcile Niko support category permissions")
            await _pace()
        categories[category_name] = category

    channels: dict[str, int] = {}
    for key, (category_name, name, kind, staff_only) in CHANNEL_SPECS.items():
        category = categories[category_name]
        channel = discord.utils.get(category.channels, name=name)
        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=not staff_only, send_messages=not (key in {"rules", "announcements", "status", "staff_announcements", "staff_rules"}), read_message_history=True, connect=not staff_only, speak=not staff_only),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True),
            bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True, connect=True, speak=True),
        }
        # Staff application role tiers are allowed in internal staff spaces too.
        for staff_key in ("head_admin", "moderator", "head_support", "graphic_designer", "support"):
            staff_id = roles.get(staff_key)
            staff_specific_role = guild.get_role(int(staff_id)) if staff_id else None
            if staff_specific_role:
                overwrites[staff_specific_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
        expected_type = {"voice": discord.VoiceChannel, "forum": discord.ForumChannel}.get(kind, discord.TextChannel)
        if channel is not None and not isinstance(channel, expected_type):
            if channel.id not in protected_system_channel_ids:
                await channel.delete(reason="Replace support channel with canonical channel type")
                await _pace()
            channel = None
        topic = CHANNEL_TOPICS.get(key, "")
        if channel is None:
            if kind == "voice":
                channel = await guild.create_voice_channel(name, category=category, overwrites=overwrites, reason="Niko support server structure")
            elif kind == "forum":
                channel = await guild.create_forum(name, topic=topic, category=category, overwrites=overwrites, slowmode_delay=5, default_thread_slowmode_delay=5, reason="Niko support server structure")
            else:
                channel = await guild.create_text_channel(name, category=category, topic=topic, overwrites=overwrites, slowmode_delay=2, reason="Niko support server structure")
            await _pace()
        else:
            edit_kwargs = {"category": category, "overwrites": overwrites}
            if kind != "voice":
                edit_kwargs.update(topic=topic, slowmode_delay=5 if kind == "forum" else 2)
            await channel.edit(**edit_kwargs, reason="Reconcile Niko support channel permissions")
            await _pace()
        channels[key] = channel.id

    await _replace_community_system_channels(guild, channels)
    return roles, channels


async def create_support_invite(bot, guild: discord.Guild, channels: dict) -> str:
    """Create a never-expiring invite and persist it with the support config."""
    if guild.id != SUPPORT_GUILD:
        raise ValueError("The support invite may only be created for the configured support guild.")
    channel = guild.get_channel(int(channels["welcome"])) or guild.get_channel(int(channels["general"]))
    if channel is None:
        raise RuntimeError("Could not locate a public channel for the support invite.")
    invite = await channel.create_invite(max_age=0, max_uses=0, unique=True, reason="Refresh official Niko support server invite")
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The database is not ready; support invite was not saved.")
    row = await pool.fetchrow(
        "SELECT role_ids, channel_ids FROM support_server_config WHERE guild_id = $1",
        guild.id,
    )
    role_ids = _json_object(row.get("role_ids")) if row else {}
    channel_ids = _json_object(row.get("channel_ids")) if row else {}
    channel_ids["welcome"] = int(channels["welcome"])
    channel_ids["general"] = int(channels["general"])
    await pool.execute(
        "INSERT INTO support_server_config (guild_id, role_ids, channel_ids, invite_url, updated_at) "
        "VALUES ($1, $2, $3, $4, datetime('now')) ON CONFLICT (guild_id) DO UPDATE SET invite_url = $5, updated_at = datetime('now')",
        guild.id, json.dumps(role_ids), json.dumps(channel_ids), invite.url, invite.url,
    )
    return invite.url


async def get_support_invite(bot) -> str | None:
    pool = getattr(bot, "cxn", None)
    if pool is None:
        return None
    row = await pool.fetchrow("SELECT invite_url FROM support_server_config WHERE guild_id = $1", SUPPORT_GUILD)
    invite = row.get("invite_url") if row else None
    return str(invite) if invite else None


async def assign_join_roles(bot, member: discord.Member, roles: dict) -> None:
    """Assign default, staff, and donor roles to an arriving support member."""
    if member.guild.id != SUPPORT_GUILD:
        return
    additions = member_join_roles(member, roles)
    from utils.donations import is_supporter
    supporter = member.guild.get_role(int(roles["supporter"])) if roles.get("supporter") else None
    if supporter and supporter not in member.roles and await is_supporter(bot, member.id):
        additions.append(supporter)
    pool = getattr(bot, "cxn", None)
    if pool:
        row = await pool.fetchrow("SELECT role FROM staff_members WHERE user_id = $1", member.id)
        staff_key = str(row["role"]) if row else None
        if staff_key in {"head_admin", "moderator", "head_support", "graphic_designer", "support"}:
            if roles.get("staff"):
                shared = member.guild.get_role(int(roles["staff"]))
                if shared and shared not in member.roles:
                    additions.append(shared)
            specific = member.guild.get_role(int(roles[staff_key])) if roles.get(staff_key) else None
            if specific and specific not in member.roles:
                additions.append(specific)
    if additions:
        await member.add_roles(*additions, reason="Niko support server join roles")


async def assign_support_roles(bot, guild: discord.Guild, roles: dict) -> None:
    """Bring current members in sync with saved staff records and base roles."""
    pool = getattr(bot, "cxn", None)
    if pool is None:
        return
    member_role = guild.get_role(int(roles["member"]))
    shared_staff = guild.get_role(int(roles["staff"]))
    staff_rows = await pool.fetch("SELECT user_id, role FROM staff_members")
    staff_by_user = {int(row["user_id"]): str(row["role"]) for row in staff_rows}
    from config.ids import OWNER_IDS
    for owner_id in OWNER_IDS:
        staff_by_user.setdefault(int(owner_id), "head_admin")
    try:
        members = [member async for member in guild.fetch_members(limit=None)]
    except (discord.Forbidden, discord.HTTPException):
        members = list(guild.members)
    from utils.donations import is_supporter
    for member in members:
        if member.id == getattr(bot.user, "id", None):
            continue
        add = []
        if member_role and member_role not in member.roles:
            add.append(member_role)
        supporter = guild.get_role(int(roles["supporter"])) if roles.get("supporter") else None
        if supporter and await is_supporter(bot, member.id) and supporter not in member.roles:
            add.append(supporter)
        if shared_staff and member.id in staff_by_user and shared_staff not in member.roles:
            add.append(shared_staff)
        staff_key = staff_by_user.get(member.id)
        if staff_key not in {"head_admin", "moderator", "head_support", "graphic_designer", "support"}:
            staff_key = None
        if staff_key and roles.get(staff_key):
            specific = guild.get_role(int(roles[staff_key]))
            if specific and specific not in member.roles:
                add.append(specific)
        if add:
            await member.add_roles(*add, reason="Synchronize Niko support server roles")
        if staff_key:
            specific = guild.get_role(int(roles[staff_key])) if roles.get(staff_key) else None
            stale = [guild.get_role(int(roles[key])) for key in ("head_admin", "moderator", "head_support", "graphic_designer", "support") if key != staff_key and roles.get(key)]
            stale = [role for role in stale if role and role in member.roles]
            if specific and specific not in member.roles:
                await member.add_roles(specific, reason="Synchronize Niko staff assignment")
            if stale:
                await member.remove_roles(*stale, reason="Remove obsolete Niko staff assignment")


class SupportPingPanel(discord.ui.LayoutView):
    """Persistent member-managed notification roles panel."""
    def __init__(self):
        super().__init__(timeout=None)
        row = discord.ui.ActionRow()
        for key, label, emoji in (("announcements_ping", "Announcements", "📣"), ("events_ping", "Events", "🎉"), ("community_ping", "Community", "💬"), ("polls_ping", "Polls", "📊")):
            button = discord.ui.Button(label=label, emoji=emoji, style=discord.ButtonStyle.secondary, custom_id=f"niko:support:role:{key}")
            button.callback = self._toggle_role
            row.add_item(button)
        self.add_item(discord.ui.Container(discord.ui.TextDisplay(content="## Choose your notifications\nGet only the updates you care about. Tap again to remove a role."), discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small), row, accent_colour=0xC8A882))

    async def _toggle_role(self, interaction: discord.Interaction):
        if not interaction.guild or interaction.guild.id != SUPPORT_GUILD or not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("This panel only works in the official support server.", ephemeral=True)
        key = interaction.data.get("custom_id", "").rsplit(":", 1)[-1]
        role = await support_role(interaction.client, key)
        if role is None:
            return await interaction.response.send_message("This role is not configured yet. Please contact staff.", ephemeral=True)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role, reason="Support notification role preference")
            message = f"Removed **{role.name}**."
        else:
            await interaction.user.add_roles(role, reason="Support notification role preference")
            message = f"Added **{role.name}**."
        await interaction.response.send_message(message, ephemeral=True)


def support_rules_text() -> str:
    return ("## Staff guidelines\n- Protect private information and keep staff discussions confidential.\n"
            "- Be calm, fair, and consistent; explain moderation decisions respectfully.\n"
            "- Escalate safety concerns and serious incidents to the owner promptly.\n"
            "- Do not promise features, uptime, or outcomes on behalf of the project.\n"
            "- Keep support conversations in the right channel and document important decisions.")


def member_join_roles(member: discord.Member, roles: dict) -> list[discord.Role]:
    role = member.guild.get_role(int(roles.get("member", 0))) if roles.get("member") else None
    return [role] if role and role not in member.roles else []
