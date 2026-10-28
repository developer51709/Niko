"""Logging — snapshots and the buttons that undo a deletion or a channel edit.

A log entry's buttons have to keep working after a restart, and the state a
restore needs (a role's permissions, a channel's permission overwrites) is far
too large for a button's custom id. So a revertable entry stores its snapshot
in the database and the button carries only the snapshot id.

Everything here is best effort: a guild without a database, a target that no
longer exists, or a bot that lost the permission answers the click with a
one-line notice instead of an error.
"""

from __future__ import annotations

import json
import secrets
import time
from datetime import datetime, timedelta, timezone

import discord

import database
from config.emojis import get_emoji
from utils import logging

#: A snapshot only has to outlive the log entry that offers its button, so old
#: rows are pruned whenever a new one is written instead of growing forever.
SNAPSHOT_TTL = timedelta(days=30)

#: Pruning scans the table, so it runs at most once an hour in the process
#: rather than on every snapshot a busy server writes.
PRUNE_INTERVAL = 3600.0
_last_prune = 0.0

_ROLE_TEMPLATE = r"log:role-restore:(?P<snapshot>[0-9a-f]{12})"
_CHANNEL_TEMPLATE = r"log:channel-restore:(?P<snapshot>[0-9a-f]{12})"
_CHANNEL_REVERT_TEMPLATE = r"log:channel-revert:(?P<snapshot>[0-9a-f]{12})"


# ── Snapshot storage ──────────────────────────────

def _pool():
    return getattr(database, "_shared_pool", None)


async def save_snapshot(guild_id: int, kind: str, payload: dict) -> str | None:
    """Store a restore payload and return its id.

    None means the snapshot could not be stored, and the caller then posts the
    entry without a restore button: a button that cannot work is worse than no
    button at all.
    """
    pool = _pool()
    if pool is None:
        return None
    snapshot_id = secrets.token_hex(6)
    now = datetime.now(timezone.utc)
    try:
        await pool.execute(
            "INSERT OR REPLACE INTO logging_snapshots "
            "(snapshot_id, guild_id, kind, payload, created_at) "
            "VALUES ($1, $2, $3, $4, $5)",
            snapshot_id, int(guild_id), kind, json.dumps(payload), now.isoformat(),
        )
        await _prune(pool, now)
    except Exception as error:  # noqa: BLE001 - the log entry still has to post
        logging.warning("logging_cog", f"Could not store a '{kind}' snapshot: {error}")
        return None
    return snapshot_id


async def _prune(pool, now: datetime) -> None:
    """Drop snapshots nobody can use any more, at most once per interval."""
    global _last_prune
    if time.monotonic() - _last_prune < PRUNE_INTERVAL:
        return
    _last_prune = time.monotonic()
    await pool.execute(
        "DELETE FROM logging_snapshots WHERE created_at < $1",
        (now - SNAPSHOT_TTL).isoformat(),
    )


async def load_snapshot(snapshot_id: str) -> dict | None:
    """The stored snapshot, or None when it expired or cannot be read."""
    pool = _pool()
    if pool is None:
        return None
    try:
        row = await pool.fetchrow(
            "SELECT guild_id, kind, payload FROM logging_snapshots WHERE snapshot_id = $1",
            snapshot_id,
        )
    except Exception as error:  # noqa: BLE001 - a stale button must not raise
        logging.warning("logging_cog", f"Could not read snapshot {snapshot_id}: {error}")
        return None
    if row is None:
        return None
    try:
        payload = json.loads(row["payload"])
    except (TypeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    return {"guild_id": int(row["guild_id"]), "kind": row["kind"], "payload": payload}


async def drop_snapshot(snapshot_id: str) -> None:
    """Forget a snapshot once it has been used, so a second click is refused."""
    pool = _pool()
    if pool is None:
        return
    try:
        await pool.execute(
            "DELETE FROM logging_snapshots WHERE snapshot_id = $1", snapshot_id)
    except Exception:  # noqa: BLE001 - cleanup is never allowed to fail a click
        pass


# ── Payload builders (used by the cog listeners) ──

def channel_type_name(channel) -> str:
    """The Discord channel type as a plain lowercase name."""
    return str(getattr(getattr(channel, "type", "text"), "name", "text")).lower()


def overwrite_entry(target, overwrite) -> dict:
    """A permission overwrite in a form a snapshot can carry as JSON.

    ``allow`` and ``deny`` hold the raw permission bits, so the entry can be
    replayed as ``PermissionOverwrite.from_pair`` without guessing at
    ``discord.Permissions`` defaults.
    """
    allow, deny = overwrite.pair()
    return {
        "target_type": "role" if isinstance(target, discord.Role) else "member",
        "target_id": int(target.id),
        "allow": allow.value,
        "deny": deny.value,
    }


def removed_overwrite_entry(target) -> dict:
    """An overwrite that has to be deleted, not restored."""
    return {
        "target_type": "role" if isinstance(target, discord.Role) else "member",
        "target_id": int(target.id),
        "allow": None,
        "deny": None,
    }


def role_snapshot(role: discord.Role) -> dict:
    return {
        "name": role.name,
        "colour": role.colour.value,
        "hoist": bool(role.hoist),
        "mentionable": bool(role.mentionable),
        "permissions": role.permissions.value,
        "position": int(role.position),
    }


def channel_snapshot(channel) -> dict:
    """Everything needed to recreate a deleted channel."""
    overwrites = getattr(channel, "overwrites", {}) or {}
    return {
        "name": getattr(channel, "name", str(channel)),
        "type": channel_type_name(channel),
        "category_id": getattr(getattr(channel, "category", None), "id", None),
        "position": int(getattr(channel, "position", 0) or 0),
        "topic": getattr(channel, "topic", None),
        "nsfw": bool(getattr(channel, "nsfw", False)),
        "slowmode_delay": int(getattr(channel, "slowmode_delay", 0) or 0),
        "bitrate": getattr(channel, "bitrate", None),
        "user_limit": int(getattr(channel, "user_limit", 0) or 0),
        "overwrites": [overwrite_entry(target, overwrite)
                       for target, overwrite in overwrites.items()],
    }


def _resolve_overwrite_target(guild: discord.Guild, entry: dict):
    if entry.get("target_type") == "role":
        return guild.get_role(int(entry["target_id"]))
    return guild.get_member(int(entry["target_id"]))


def _overwrite_from(entry: dict) -> discord.PermissionOverwrite:
    return discord.PermissionOverwrite.from_pair(
        discord.Permissions(int(entry.get("allow") or 0)),
        discord.Permissions(int(entry.get("deny") or 0)),
    )


def _create_overwrites(guild: discord.Guild, entries: list[dict]) -> dict:
    """Overwrites for a recreated channel; deletion markers are dropped."""
    mapping = {}
    for entry in entries or []:
        if entry.get("allow") is None and entry.get("deny") is None:
            continue
        target = _resolve_overwrite_target(guild, entry)
        if target is not None:
            mapping[target] = _overwrite_from(entry)
    return mapping


# ── Button plumbing ───────────────────────────────

def _notice(text: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return view


async def _has_permission(interaction: discord.Interaction, attribute: str, label: str) -> bool:
    permissions = getattr(interaction.user, "guild_permissions", None)
    if permissions is not None and getattr(permissions, attribute, False):
        return True
    await interaction.followup.send(
        view=_notice(f"You need **{label}** to use this button."), ephemeral=True)
    return False


async def _snapshot_for(interaction: discord.Interaction, snapshot_id: str,
                        kind: str) -> dict | None:
    """Load a snapshot that belongs to this guild and this action kind."""
    guild = interaction.guild
    state = await load_snapshot(snapshot_id)
    if state is None or state["kind"] != kind or guild is None \
            or state["guild_id"] != guild.id:
        await interaction.followup.send(
            view=_notice(
                "This restore is no longer available — its snapshot expired, "
                "or it belongs to another server."
            ),
            ephemeral=True,
        )
        return None
    return state


async def _announce(interaction: discord.Interaction, category: str, title: str,
                    body: str, **kwargs) -> None:
    """Write the restore itself into the server's own logs."""
    logger = interaction.client.get_cog("ServerLogger")
    if logger is None:
        return
    try:
        await logger.log_event(
            interaction.guild, category, title, body, action_key=title, **kwargs)
    except Exception as error:  # noqa: BLE001 - the click already succeeded
        logging.warning("logging_cog", f"Could not log '{title}': {error}")


async def _fail(interaction: discord.Interaction, error: Exception, what: str) -> None:
    logging.error("logging_cog", f"Quick action '{what}' failed: {error!r}")
    await interaction.followup.send(
        view=_notice(
            f"I couldn't {what}. Check that I still have the permissions and "
            "that the target still exists."
        ),
        ephemeral=True,
    )


# ── Buttons ───────────────────────────────────────

class RestoreRoleButton(discord.ui.DynamicItem[discord.ui.Button], template=_ROLE_TEMPLATE):
    """Recreates a deleted role from the snapshot taken at deletion time."""

    def __init__(self, snapshot_id: str):
        super().__init__(discord.ui.Button(
            label="Restore Role",
            style=discord.ButtonStyle.success,
            emoji=get_emoji("refresh"),
            custom_id=f"log:role-restore:{snapshot_id}",
        ))
        self.snapshot_id = snapshot_id

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(match["snapshot"])

    async def callback(self, interaction: discord.Interaction):
        # The snapshot read and the role creation are both round trips; ack
        # first so a slow one never reads as "This interaction failed".
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            return await interaction.followup.send(
                view=_notice("This button only works inside a server."), ephemeral=True)
        if not await _has_permission(interaction, "manage_roles", "Manage Roles"):
            return
        state = await _snapshot_for(interaction, self.snapshot_id, "role")
        if state is None:
            return
        payload = state["payload"]
        guild = interaction.guild
        reason = f"Restored from a log entry by {interaction.user}"
        try:
            role = await guild.create_role(
                name=payload.get("name") or "Restored role",
                colour=discord.Colour(int(payload.get("colour") or 0)),
                hoist=bool(payload.get("hoist")),
                mentionable=bool(payload.get("mentionable")),
                permissions=discord.Permissions(int(payload.get("permissions") or 0)),
                reason=reason,
            )
        except (discord.Forbidden, discord.HTTPException) as error:
            return await _fail(interaction, error, "restore that role")

        # The old position may no longer exist, so it is a best-effort extra.
        position = int(payload.get("position") or 0)
        if position:
            try:
                await role.edit(position=min(position, max(len(guild.roles) - 1, 1)))
            except (discord.Forbidden, discord.HTTPException):
                pass

        await drop_snapshot(self.snapshot_id)
        granted = sum(1 for _, value in iter(role.permissions) if value)
        await _announce(
            interaction, "roles", "Role Restored",
            (
                f"**Role:** {role.mention} (`{role.name}` — ID: `{role.id}`)\n"
                f"**Restored By:** {interaction.user.mention}\n"
                f"**Colour:** `{role.colour}` · **Permissions:** `{granted}` · "
                f"**Position:** `{role.position}`\n"
                f"-# Members who held the deleted role are not re-added automatically."
            ),
            target_id=role.id,
        )
        await interaction.followup.send(
            view=_notice(
                f"{get_emoji('tick')} Restored {role.mention}. "
                "Members who held it before its deletion need it assigned again."
            ),
            ephemeral=True,
        )


class RestoreChannelButton(discord.ui.DynamicItem[discord.ui.Button], template=_CHANNEL_TEMPLATE):
    """Recreates a deleted channel, including its category and overwrites."""

    def __init__(self, snapshot_id: str):
        super().__init__(discord.ui.Button(
            label="Restore Channel",
            style=discord.ButtonStyle.success,
            emoji=get_emoji("refresh"),
            custom_id=f"log:channel-restore:{snapshot_id}",
        ))
        self.snapshot_id = snapshot_id

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(match["snapshot"])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            return await interaction.followup.send(
                view=_notice("This button only works inside a server."), ephemeral=True)
        if not await _has_permission(interaction, "manage_channels", "Manage Channels"):
            return
        state = await _snapshot_for(interaction, self.snapshot_id, "channel")
        if state is None:
            return
        payload = state["payload"]
        guild = interaction.guild

        category = None
        if payload.get("category_id"):
            parent = guild.get_channel(int(payload["category_id"]))
            if isinstance(parent, discord.CategoryChannel):
                category = parent

        kind = str(payload.get("type") or "text")
        common = {
            "name": payload.get("name") or "restored-channel",
            "overwrites": _create_overwrites(guild, payload.get("overwrites") or []),
            "category": category,
            "reason": f"Restored from a log entry by {interaction.user}",
        }
        try:
            if kind == "category":
                common.pop("category", None)
                channel = await guild.create_category(**common)
            elif kind == "voice":
                channel = await guild.create_voice_channel(
                    bitrate=int(payload.get("bitrate") or 64_000),
                    user_limit=int(payload.get("user_limit") or 0),
                    **common,
                )
            elif kind == "stage":
                channel = await guild.create_stage_channel(
                    topic=payload.get("topic"),
                    bitrate=int(payload.get("bitrate") or 64_000),
                    user_limit=int(payload.get("user_limit") or 0),
                    **common,
                )
            elif kind in ("forum", "media"):
                channel = await guild.create_forum_channel(
                    topic=payload.get("topic"),
                    nsfw=bool(payload.get("nsfw")),
                    slowmode_delay=int(payload.get("slowmode_delay") or 0),
                    **common,
                )
            else:
                channel = await guild.create_text_channel(
                    topic=payload.get("topic"),
                    nsfw=bool(payload.get("nsfw")),
                    slowmode_delay=int(payload.get("slowmode_delay") or 0),
                    **common,
                )
        except (discord.Forbidden, discord.HTTPException) as error:
            return await _fail(interaction, error, "restore that channel")

        # The old position may no longer be free, so it is a best-effort extra.
        position = int(payload.get("position") or 0)
        if position:
            try:
                await channel.edit(position=position)
            except (discord.Forbidden, discord.HTTPException):
                pass

        await drop_snapshot(self.snapshot_id)
        note = "" if kind in ("text", "voice", "category", "stage", "forum", "media") else (
            f"\n-# It was a {kind} channel; Discord only allows it back as text."
        )
        await _announce(
            interaction, "channels", "Channel Restored",
            (
                f"**Channel:** {channel.mention} (`{channel.name}` — ID: `{channel.id}`)\n"
                f"**Type:** {channel_type_name(channel).title()}\n"
                f"**Category:** {category.mention if category else 'None'}\n"
                f"**Restored By:** {interaction.user.mention}"
                f"{note}"
            ),
            channel_id=channel.id,
        )
        await interaction.followup.send(
            view=_notice(f"{get_emoji('tick')} Restored {channel.mention}."),
            ephemeral=True,
        )


class RevertChannelButton(discord.ui.DynamicItem[discord.ui.Button], template=_CHANNEL_REVERT_TEMPLATE):
    """Puts a channel's settings and overwrites back to their before values."""

    def __init__(self, snapshot_id: str):
        super().__init__(discord.ui.Button(
            label="Revert Changes",
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("refresh"),
            custom_id=f"log:channel-revert:{snapshot_id}",
        ))
        self.snapshot_id = snapshot_id

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(match["snapshot"])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            return await interaction.followup.send(
                view=_notice("This button only works inside a server."), ephemeral=True)
        if not await _has_permission(interaction, "manage_channels", "Manage Channels"):
            return
        state = await _snapshot_for(interaction, self.snapshot_id, "channel-update")
        if state is None:
            return
        payload = state["payload"]
        guild = interaction.guild
        channel = guild.get_channel(int(payload.get("channel_id") or 0))
        if channel is None:
            return await interaction.followup.send(
                view=_notice("That channel no longer exists."), ephemeral=True)

        reason = f"Reverted from a log entry by {interaction.user}"
        before = payload.get("before") or {}
        options: dict = {}
        if "name" in before:
            options["name"] = before["name"]
        if "topic" in before:
            options["topic"] = before["topic"]
        if "slowmode_delay" in before:
            options["slowmode_delay"] = int(before["slowmode_delay"] or 0)
        if "nsfw" in before:
            options["nsfw"] = bool(before["nsfw"])
        if "bitrate" in before and before["bitrate"]:
            options["bitrate"] = int(before["bitrate"])
        if "user_limit" in before:
            options["user_limit"] = int(before["user_limit"] or 0)
        if "position" in before:
            options["position"] = int(before["position"] or 0)
        if "category_id" in before:
            parent = guild.get_channel(int(before["category_id"])) \
                if before["category_id"] else None
            options["category"] = parent if isinstance(parent, discord.CategoryChannel) else None

        try:
            if options:
                await channel.edit(reason=reason, **options)
            restored = 0
            for entry in payload.get("overwrites") or []:
                target = _resolve_overwrite_target(guild, entry)
                if target is None:
                    continue
                overwrite = None if entry.get("allow") is None and entry.get("deny") is None \
                    else _overwrite_from(entry)
                await channel.set_permissions(target, overwrite=overwrite, reason=reason)
                restored += 1
        except (discord.Forbidden, discord.HTTPException) as error:
            return await _fail(interaction, error, "revert that channel")

        await drop_snapshot(self.snapshot_id)
        fields = ", ".join(sorted(options)) or "none"
        await _announce(
            interaction, "channels", "Channel Reverted",
            (
                f"**Channel:** {channel.mention} (`{channel.name}`)\n"
                f"**Reverted By:** {interaction.user.mention}\n"
                f"**Fields:** {fields}\n"
                f"**Overwrites Restored:** `{restored}`"
            ),
            channel_id=channel.id,
        )
        await interaction.followup.send(
            view=_notice(
                f"{get_emoji('tick')} Reverted {channel.mention} to its previous settings."
            ),
            ephemeral=True,
        )


def register_persistent_views(bot) -> None:
    """Register the snapshot buttons so entries posted before a restart work.

    Log entries are posted with ``timeout=None``, but a button is only resolved
    after a restart when its custom-id pattern is registered on the client.
    """
    registry = discord.ui.LayoutView(timeout=None)
    registry.add_item(discord.ui.Container(discord.ui.ActionRow(
        RestoreRoleButton("0" * 12),
        RestoreChannelButton("0" * 12),
        RevertChannelButton("0" * 12),
    )))
    bot.add_view(registry)
