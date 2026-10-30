"""Per-guild profiles, dashboard configuration, and the Discord panel
refreshes that follow a web change."""

import json
import sqlite3
from . import config, database, discord_api, runtime


def _serialize_onboarding_config(cfg) -> dict:
    """Return onboarding values with exact Discord IDs for the dashboard."""
    from dataclasses import asdict
    serialized = asdict(cfg)
    for field in (
        "welcome_channel", "goodbye_channel", "rules_channel", "rules_role_id",
        "rules_message_id", "captcha_channel_id", "captcha_panel_message_id",
    ):
        if serialized.get(field) is not None:
            serialized[field] = str(serialized[field])
    for field in ("autorole_ids", "bot_autorole_ids", "captcha_add_role_ids", "captcha_remove_role_ids"):
        if serialized.get(field) is not None:
            serialized[field] = [str(value) for value in serialized[field]]
    return serialized


def _serialize_ticket_config(cfg) -> dict:
    """Return the editable ticket settings without internal open-ticket state."""
    guild = runtime._discord_bot.get_guild(int(cfg.guild_id)) if runtime._discord_bot is not None else None
    tickets = []
    for ticket in (cfg.open_tickets or []):
        if not isinstance(ticket, dict):
            continue
        channel_id = str(ticket.get("channel_id", ""))
        channel = runtime._discord_bot.get_channel(int(channel_id)) if runtime._discord_bot is not None and channel_id.isdigit() else None
        opener_id = str(ticket.get("opener_id", ""))
        opener = guild.get_member(int(opener_id)) if guild is not None and opener_id.isdigit() else None
        tickets.append({
            **ticket,
            "channel_id": channel_id,
            "opener_id": opener_id,
            "message_id": str(ticket["message_id"]) if ticket.get("message_id") else None,
            "claimed_by": str(ticket["claimed_by"]) if ticket.get("claimed_by") else None,
            "channel_name": getattr(channel, "name", None),
            "opener_name": getattr(opener, "display_name", None),
        })
    return {
        "panel_title": cfg.panel_title,
        "panel_description": cfg.panel_description,
        "panel_color": cfg.panel_color,
        "panel_image": cfg.panel_image,
        "panel_categories": list(cfg.panel_categories or []),
        "panel_channel_id": str(cfg.panel_channel_id) if cfg.panel_channel_id else None,
        "panel_message_id": str(cfg.panel_message_id) if cfg.panel_message_id else None,
        "support_roles": [str(role_id) for role_id in (cfg.support_roles or [])],
        "open_tickets": tickets,
    }


def _profile_row_to_dict(row) -> dict:
    if not row:
        return {"display_name": None, "bio": None, "avatar_url": None, "banner_url": None, "name_font_id": None, "name_effect_id": 2, "name_colors": []}
    colors = row.get("name_colors")
    try:
        colors = json.loads(colors) if colors else []
    except (TypeError, ValueError):
        colors = []
    return {
        "display_name": row.get("display_name"),
        "bio": row.get("bio"),
        "avatar_url": None,
        "banner_url": None,
        "name_font_id": row.get("name_font_id"),
        "name_effect_id": row.get("name_effect_id") or 2,
        "name_colors": colors,
    }


def _discord_guild_profile_assets(guild_id: str) -> dict:
    """Resolve profile images from Discord instead of retaining uploaded copies."""
    guild_int = int(guild_id)
    if config.DISCORD_BOT_TOKEN:
        try:
            response = discord_api.discord_request(
                "GET",
                f"{config.DISCORD_API}/guilds/{guild_int}/members/@me",
                headers={"Authorization": f"Bot {config.DISCORD_BOT_TOKEN}"},
                timeout=8,
            )
            if response.status_code == 200:
                payload = response.json()
                user = payload.get("user") or {}
                bot_id = str(user.get("id") or getattr(getattr(runtime._discord_bot, "user", None), "id", ""))
                avatar_hash = payload.get("avatar")
                banner_hash = payload.get("banner")
                avatar_ext = "gif" if str(avatar_hash or "").startswith("a_") else "png"
                banner_ext = "gif" if str(banner_hash or "").startswith("a_") else "png"
                return {
                    "avatar_url": f"https://cdn.discordapp.com/guilds/{guild_int}/users/{bot_id}/avatars/{avatar_hash}.{avatar_ext}?size=512" if avatar_hash and bot_id else None,
                    "banner_url": f"https://cdn.discordapp.com/guilds/{guild_int}/users/{bot_id}/banners/{banner_hash}.{banner_ext}?size=1024" if banner_hash and bot_id else None,
                }
        except Exception:
            pass

    guild = runtime._discord_bot.get_guild(guild_int) if runtime._discord_bot is not None else None
    member = getattr(guild, "me", None) if guild else None
    avatar = getattr(getattr(member, "guild_avatar", None), "url", None)
    banner = getattr(getattr(member, "guild_banner", None), "url", None)
    return {"avatar_url": str(avatar) if avatar else None, "banner_url": str(banner) if banner else None}


def _global_profile_assets() -> dict:
    """Resolve Niko's global (application-wide) avatar and banner.

    The per-guild profile is what a server sets for itself; until a server sets
    one, the dashboard shows Niko's global identity instead. Each image is
    resolved independently: the live bot user is authoritative, and a REST
    ``/users/@me`` read fills in whichever field the cached user object does not
    carry (the gateway payload only includes a banner when one is set).
    """
    user = getattr(runtime._discord_bot, "user", None) if runtime._discord_bot is not None else None
    avatar_url = None
    banner_url = None
    if user is not None:
        avatar_url = str(getattr(getattr(user, "display_avatar", None), "url", "") or "") or None
        banner_url = str(getattr(getattr(user, "banner", None), "url", "") or "") or None

    if (avatar_url and banner_url) or not config.DISCORD_BOT_TOKEN:
        return {"avatar_url": avatar_url, "banner_url": banner_url}

    try:
        response = discord_api.discord_request(
            "GET",
            f"{config.DISCORD_API}/users/@me",
            headers={"Authorization": f"Bot {config.DISCORD_BOT_TOKEN}"},
            timeout=8,
        )
        if response.status_code == 200:
            payload = response.json()
            user_id = str(payload.get("id") or getattr(user, "id", "") or "")
            avatar_hash = payload.get("avatar")
            banner_hash = payload.get("banner")
            if not avatar_url and avatar_hash and user_id:
                extension = "gif" if str(avatar_hash).startswith("a_") else "png"
                avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{extension}?size=512"
            if not banner_url and banner_hash and user_id:
                extension = "gif" if str(banner_hash).startswith("a_") else "png"
                banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.{extension}?size=1024"
    except Exception:
        pass

    return {"avatar_url": avatar_url, "banner_url": banner_url}


def _get_runtime_guild_profile(guild_id: str) -> dict:
    """Read profile text/style from storage and images directly from Discord."""
    assets = _discord_guild_profile_assets(guild_id)
    async def read_from_bot():
        if runtime._discord_bot is None or not getattr(runtime._discord_bot, "cxn", None):
            return None
        return await runtime._discord_bot.cxn.fetchrow(
            "SELECT display_name, bio, name_font_id, name_effect_id, name_colors "
            "FROM guild_profiles WHERE guild_id = $1",
            int(guild_id),
        )

    if runtime._discord_bot is not None and getattr(runtime._discord_bot, "cxn", None):
        try:
            row = runtime.run_on_bot_loop(read_from_bot())
            if row:
                return {**_profile_row_to_dict(row), **assets}
        except Exception:
            pass

    conn = database.sqlite_connect()
    if conn is not None:
        try:
            row = conn.execute(
                "SELECT display_name, bio, name_font_id, name_effect_id, name_colors "
                "FROM guild_profiles WHERE guild_id = ?",
                (int(guild_id),),
            ).fetchone()
            if row:
                return {**_profile_row_to_dict(dict(zip(
                    ("display_name", "bio", "name_font_id", "name_effect_id", "name_colors"), row
                ))), **assets}
        except sqlite3.Error:
            pass
        finally:
            conn.close()

    guild = runtime._discord_bot.get_guild(int(guild_id)) if runtime._discord_bot is not None else None
    member = getattr(guild, "me", None) if guild is not None else None
    return {
        "display_name": getattr(member, "display_name", None) if member else None,
        "bio": None,
        **assets,
        "name_font_id": None,
        "name_effect_id": 2,
        "name_colors": [],
    }


def _save_runtime_guild_profile(guild_id: int, profile: dict) -> None:
    """Write a complete profile row through whichever database is active."""
    async def save_to_bot():
        await runtime._discord_bot.cxn.execute(
            "INSERT OR REPLACE INTO guild_profiles "
            "(guild_id, display_name, bio, name_font_id, name_effect_id, name_colors, updated_at) "
            "VALUES ($1, $2, $3, $4, $5, $6, datetime('now'))",
            guild_id,
            profile.get("display_name"),
            profile.get("bio"),
            profile.get("name_font_id"),
            profile.get("name_effect_id"),
            json.dumps(profile.get("name_colors") or []),
        )

    if runtime._discord_bot is not None and getattr(runtime._discord_bot, "cxn", None):
        runtime.run_on_bot_loop(save_to_bot())
        return

    conn = database.sqlite_connect()
    if conn is None:
        raise RuntimeError("The bot database is unavailable.")
    try:
        conn.execute(
            "INSERT OR REPLACE INTO guild_profiles "
            "(guild_id, display_name, bio, name_font_id, name_effect_id, name_colors, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                guild_id,
                profile.get("display_name"),
                profile.get("bio"),
                profile.get("name_font_id"),
                profile.get("name_effect_id"),
                json.dumps(profile.get("name_colors") or []),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _serialize_logging_categories() -> list[dict]:
    """The log categories the bot knows about, for the dashboard's pickers."""
    from cogs.logging.formatters import CATEGORIES

    return [
        {"key": key, "label": info["label"], "description": info.get("description", "")}
        for key, info in CATEGORIES.items()
    ]


def _get_runtime_server_config(guild_id: str) -> dict:
    """Read all server-management settings from their existing owners."""
    from utils.prefix_manager import DEFAULT_PREFIX, PREFIX_OVERRIDE, get_prefixes
    from config.status import DEVELOPMENT
    from utils.guild_privacy import get_guild_privacy
    from utils.onboarding.config import load_config
    from cogs.logging.formatters import _load_log_config, _guild_config
    from utils.tickets.utils import get_ticket_config

    onboarding = runtime.run_on_bot_loop(load_config(int(guild_id)))
    logging_data = runtime.run_on_bot_loop(_load_log_config())
    logging_config = _guild_config(logging_data, int(guild_id))
    for category, channel_id in logging_config.items():
        if category != "disabled" and channel_id is not None:
            logging_config[category] = str(channel_id)
    return {
        "prefixes": runtime.run_on_bot_loop(
            get_prefixes(int(guild_id), getattr(runtime._discord_bot, "cxn", None))
        ),
        "development": DEVELOPMENT,
        "default_prefix": DEFAULT_PREFIX,
        "prefix_override": PREFIX_OVERRIDE,
        "onboarding": _serialize_onboarding_config(onboarding),
        "logging": logging_config,
        # The bot's own category list, so the dashboard can never drift from the
        # events the bot actually logs.
        "logging_categories": _serialize_logging_categories(),
        "tickets": _serialize_ticket_config(get_ticket_config(int(guild_id))),
        "profile": _get_runtime_guild_profile(guild_id),
        # Whether the server tag popups in transcripts hide this server.
        "privacy": runtime.run_on_bot_loop(
            get_guild_privacy(int(guild_id), getattr(runtime._discord_bot, "cxn", None))
        ),
        # Niko's own identity, so the customization tab can show what a server
        # inherits until it uploads its own avatar or banner.
        "global_profile": _global_profile_assets(),
    }


def _guild_resource_ids(guild_id: int) -> tuple[set[str] | None, set[str] | None]:
    """Return valid channel and role IDs from the live Discord guild."""
    if runtime._discord_bot is None:
        return None, None
    guild = runtime._discord_bot.get_guild(guild_id)
    if guild is None:
        return set(), set()
    return (
        {str(channel.id) for channel in guild.text_channels},
        {str(role.id) for role in guild.roles if not role.is_default()},
    )


async def _refresh_ticket_panel(guild_id: int) -> None:
    """Refresh a configured ticket panel after dashboard edits."""
    from utils.tickets.utils import get_ticket_config
    from cogs.tickets.views import TicketPanelView

    guild = runtime._discord_bot.get_guild(guild_id) if runtime._discord_bot is not None else None
    cfg = get_ticket_config(guild_id)
    if guild is None or not cfg.panel_channel_id or not cfg.panel_message_id:
        return
    channel = guild.get_channel(cfg.panel_channel_id)
    if channel is None:
        return
    try:
        message = await channel.fetch_message(cfg.panel_message_id)
        await message.edit(view=TicketPanelView(guild_id, cfg))
    except Exception:
        pass


async def _refresh_captcha_panel(
    guild_id: int,
    previous_channel_id: int | None = None,
    previous_message_id: int | None = None,
) -> None:
    """Post or update the public Verify panel in its configured channel."""
    from utils.onboarding.config import load_config, save_config
    from cogs.onboarding.views import CaptchaPanelView

    guild = runtime._discord_bot.get_guild(guild_id) if runtime._discord_bot is not None else None
    cfg = await load_config(guild_id)
    if guild is None:
        raise RuntimeError("The selected server is not available to the bot.")
    if not cfg.captcha_channel_id:
        if previous_channel_id and previous_message_id:
            previous_channel = guild.get_channel(previous_channel_id)
            if previous_channel is not None:
                try:
                    previous_message = await previous_channel.fetch_message(previous_message_id)
                    await previous_message.delete()
                except Exception:
                    pass
        cfg.captcha_panel_message_id = None
        await save_config(guild_id, cfg)
        return
    channel = guild.get_channel(cfg.captcha_channel_id)
    if channel is None:
        raise RuntimeError("The configured verification panel channel is unavailable.")

    panel_view = CaptchaPanelView(guild_id, mode=cfg.captcha_mode, locale=guild)
    message = None
    if previous_channel_id == cfg.captcha_channel_id and previous_message_id:
        try:
            message = await channel.fetch_message(previous_message_id)
            await message.edit(view=panel_view)
        except Exception:
            message = None
    if message is None:
        message = await channel.send(view=panel_view)
        if previous_channel_id and previous_message_id and previous_channel_id != channel.id:
            previous_channel = guild.get_channel(previous_channel_id)
            if previous_channel is not None:
                try:
                    previous_message = await previous_channel.fetch_message(previous_message_id)
                    await previous_message.delete()
                except Exception:
                    pass

    cfg.captcha_channel_id = channel.id
    cfg.captcha_panel_message_id = message.id
    await save_config(guild_id, cfg)
    runtime._discord_bot.add_view(panel_view, message_id=message.id)


def _read_moderation_config_sync(guild_id: str) -> dict:
    """Read moderation config from the bot's database file (SQLite only).

    Used only when the live bot object is unavailable; MongoDB deployments
    always resolve through the running bot instead.
    """
    conn = database.sqlite_connect()
    if conn is None:
        return {}
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT data FROM moderation_config WHERE guild_id = ?",
            (int(guild_id),),
        )
        row = cur.fetchone()
        if row and row[0]:
            try:
                data = json.loads(row[0])
                if isinstance(data, dict):
                    return data
            except (TypeError, ValueError):
                pass
        return {}
    except sqlite3.Error:
        return {}
    finally:
        conn.close()


def get_runtime_moderation_config(guild_id: str) -> dict:
    """Read the live ModerationUtils config so the dashboard and cog agree."""
    if runtime._discord_bot is not None:
        moderation = runtime._discord_bot.get_cog("ModerationUtils")
        if moderation is not None:
            return moderation.get_guild_config(int(guild_id))
    return _read_moderation_config_sync(guild_id)
