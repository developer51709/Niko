"""Public API for rendering Discord text with readable mention names."""

import asyncio
import re

from . import server as _server
from flask import jsonify, request

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

_MAX_FETCHES_PER_TYPE = 25
_MAX_PARALLEL_FETCHES = 5


def _empty_names():
    return {"user": {}, "channel": {}, "role": {}}


async def _fetch_discord_rest_name(kind, item_id, guild_id):
    """Resolve names through Discord's bot API when the library cache misses."""
    token = getattr(_server, "DISCORD_BOT_TOKEN", "")
    if not token:
        return None

    endpoint = f"{_server.DISCORD_API}/{kind}s/{item_id}"
    try:
        response = await asyncio.to_thread(
            _server.req.get,
            endpoint,
            headers={"Authorization": f"Bot {token}"},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    if kind == "user":
        return data.get("global_name") or data.get("username")
    if str(data.get("guild_id", "")) != str(guild_id):
        return None
    return data.get("name")


async def _fetch_discord_text_mentions(guild_id, mention_ids, names):
    """Fetch uncached Discord objects, limiting per-request REST lookups."""
    guild = None
    if guild_id:
        try:
            guild = _discord_bot.get_guild(int(guild_id))
        except (AttributeError, TypeError, ValueError):
            pass
        if guild is None and hasattr(_discord_bot, "fetch_guild"):
            try:
                guild = await _discord_bot.fetch_guild(int(guild_id))
            except Exception:
                pass

    missing_roles = mention_ids["role"] - names["role"].keys()
    if missing_roles and guild is not None and hasattr(guild, "fetch_roles"):
        try:
            for role in await guild.fetch_roles():
                role_id = str(role.id)
                if role_id in missing_roles:
                    names["role"][role_id] = role.name
        except Exception:
            pass
    missing_roles -= names["role"].keys()
    if missing_roles and guild_id and getattr(_server, "DISCORD_BOT_TOKEN", ""):
        try:
            response = await asyncio.to_thread(
                _server.req.get,
                f"{_server.DISCORD_API}/guilds/{guild_id}/roles",
                headers={"Authorization": f"Bot {_server.DISCORD_BOT_TOKEN}"},
                timeout=5,
            )
            response.raise_for_status()
            for role in response.json():
                role_id = str(role.get("id", ""))
                if role_id in missing_roles and role.get("name"):
                    names["role"][role_id] = role["name"]
        except Exception:
            pass

    semaphore = asyncio.Semaphore(_MAX_PARALLEL_FETCHES)

    async def fetch_user_name(user_id):
        user = None
        if guild is not None and hasattr(guild, "fetch_member"):
            try:
                user = await guild.fetch_member(int(user_id))
            except Exception:
                pass
        if user is None and hasattr(_discord_bot, "fetch_user"):
            try:
                user = await _discord_bot.fetch_user(int(user_id))
            except Exception:
                pass
        label = (
            getattr(user, "display_name", None)
            or getattr(user, "global_name", None)
            or getattr(user, "name", None)
            or getattr(user, "username", None)
        ) if user is not None else None
        if not label:
            label = await _fetch_discord_rest_name("user", user_id, guild_id)
        if label:
            names["user"][user_id] = label

    async def fetch_channel_name(channel_id):
        channel = None
        if hasattr(_discord_bot, "fetch_channel"):
            try:
                channel = await _discord_bot.fetch_channel(int(channel_id))
            except Exception:
                pass
        channel_guild = getattr(channel, "guild", None) if channel is not None else None
        if channel_guild is not None and str(getattr(channel_guild, "id", "")) == str(guild_id):
            names["channel"][channel_id] = channel.name
        else:
            label = await _fetch_discord_rest_name("channel", channel_id, guild_id)
            if label:
                names["channel"][channel_id] = label

    missing_users = sorted(mention_ids["user"] - names["user"].keys())[:_MAX_FETCHES_PER_TYPE]
    missing_channels = sorted(mention_ids["channel"] - names["channel"].keys())[:_MAX_FETCHES_PER_TYPE]
    async def bounded_fetch(fetch, item_id):
        async with semaphore:
            await fetch(item_id)

    await asyncio.gather(
        *(bounded_fetch(fetch_user_name, user_id) for user_id in missing_users),
        *(bounded_fetch(fetch_channel_name, channel_id) for channel_id in missing_channels),
    )
    return names


async def _fetch_discord_user_profile(guild_id, user_id):
    """Collect a small public profile payload for transcript mention popovers."""
    guild = None
    if guild_id:
        try:
            guild = _discord_bot.get_guild(int(guild_id))
        except (AttributeError, TypeError, ValueError):
            pass
        if guild is None and hasattr(_discord_bot, "fetch_guild"):
            try:
                guild = await _discord_bot.fetch_guild(int(guild_id))
            except Exception:
                pass
    if guild is None and hasattr(_discord_bot, "guilds"):
        for candidate in _discord_bot.guilds:
            try:
                if candidate.get_member(int(user_id)) is not None:
                    guild = candidate
                    break
            except (AttributeError, TypeError, ValueError):
                continue
    member = None
    if guild is not None and hasattr(guild, "fetch_member"):
        try:
            member = await guild.fetch_member(int(user_id))
        except Exception:
            pass
    user = None
    # fetch_user includes profile-only fields such as banner and accent color
    # that are not consistently present on cached guild member objects.
    if hasattr(_discord_bot, "fetch_user"):
        try:
            user = await _discord_bot.fetch_user(int(user_id))
        except Exception:
            pass
    user = user or getattr(member, "_user", None) or member
    if user is None:
        return None

    avatar = getattr(user, "display_avatar", None) or getattr(user, "avatar", None)
    member_status = getattr(member, "status", None)
    status = getattr(member_status, "name", None) or str(member_status or "offline")
    status = status.rsplit(".", 1)[-1].lower()
    banner = getattr(user, "banner", None)
    # Some Discord API/library versions only expose banner color on the member.
    if banner is None:
        banner = getattr(member, "banner", None)
    accent = getattr(user, "accent_color", None)
    if accent is None:
        accent = getattr(member, "accent_color", None)
    try:
        accent_value = int(getattr(accent, "value", accent)) if accent is not None else None
        banner_color = f"#{accent_value:06x}" if accent_value is not None and 0 <= accent_value <= 0xFFFFFF else None
    except (TypeError, ValueError):
        banner_color = None
    primary_guild = getattr(user, "primary_guild", None) or getattr(member, "primary_guild", None)
    guild_tag = getattr(primary_guild, "tag", None)
    guild_badge = getattr(primary_guild, "badge", None)
    decoration = getattr(user, "avatar_decoration", None)
    if decoration is None:
        decoration = getattr(member, "avatar_decoration", None)
    return {
        "id": str(user_id),
        "username": getattr(user, "name", None) or getattr(user, "username", None) or f"user-{user_id}",
        # The popup represents the Discord user profile, never a server-specific nickname.
        "display_name": getattr(user, "global_name", None) or getattr(user, "name", None) or getattr(user, "username", None) or f"user-{user_id}",
        "avatar_url": str(avatar.url) if avatar is not None else None,
        "status": status,
        "banner_url": str(banner.url) if banner is not None else None,
        "banner_color": banner_color,
        "accent_color": banner_color,
        "bio": None,
        "profile_gradient": [],
        "name_font_id": None,
        "name_colors": [],
        "name_effect_id": None,
        "profile_effect_id": None,
        "profile_effect_url": None,
        "profile_effect_animated_url": None,
        "profile_effect_layers": [],
        "nameplate_url": None,
        "nameplate_animated_url": None,
        "guild_tag": guild_tag,
        "guild_badge_url": str(guild_badge.url) if guild_badge is not None else None,
        "badges": [],
        "nitro_badge": None,
        "booster_badge": None,
        "is_mobile": False,
        "is_streaming": False,
        "legacy_username_badge": False,
        "legacy_username": None,
        "custom_status": None,
        "activities": [],
        "avatar_decoration_url": str(decoration.url) if decoration is not None else None,
        "avatar_decoration_animated_url": (
            str(decoration.with_format("gif").url)
            if decoration is not None and getattr(decoration, "is_animated", lambda: False)()
            else None
        ),
        "avatar_decoration_sku_id": getattr(user, "avatar_decoration_sku_id", None),
        "roles": [],
        "guild_nick": getattr(member, "nick", None),
    }


def resolve_discord_user_profiles(guild_id, text):
    """Fetch bounded public profile data for users mentioned in a transcript."""
    if _discord_bot is None:
        return {}
    user_ids = sorted(set(re.findall(r"<@!?([0-9]+)>", str(text or ""))))[:_MAX_FETCHES_PER_TYPE]
    if not user_ids:
        return {}
    bot_loop = getattr(_discord_bot, "loop", None)
    if bot_loop is None or not bot_loop.is_running():
        return {}

    async def fetch_profiles():
        semaphore = asyncio.Semaphore(_MAX_PARALLEL_FETCHES)
        async def bounded(user_id):
            async with semaphore:
                try:
                    profile = await _fetch_discord_user_profile(guild_id, user_id)
                    return user_id, profile
                except Exception:
                    return user_id, None
        values = await asyncio.gather(*(bounded(user_id) for user_id in user_ids))
        return {user_id: profile for user_id, profile in values if profile}

    try:
        return _server.run_on_bot_loop(fetch_profiles())
    except Exception:
        return {}


def resolve_discord_text_mentions(guild_id, text):
    """Resolve mentions using guild cache first, then Discord REST fetches."""
    names = _empty_names()
    if _discord_bot is None:
        return names

    mention_ids = {"user": set(), "channel": set(), "role": set()}
    for user_id, role_id, channel_id in re.findall(
        r"<@!?(\d+)>|<@&(\d+)>|<#(\d+)>", str(text or "")
    ):
        if user_id:
            mention_ids["user"].add(user_id)
        elif role_id:
            mention_ids["role"].add(role_id)
        elif channel_id:
            mention_ids["channel"].add(channel_id)

    try:
        guild = _discord_bot.get_guild(int(guild_id)) if guild_id else None
    except (AttributeError, TypeError, ValueError):
        guild = None
    if guild is not None:
        for channel_id in mention_ids["channel"]:
            channel = guild.get_channel(int(channel_id))
            if channel is not None:
                names["channel"][channel_id] = channel.name
        for role_id in mention_ids["role"]:
            role = guild.get_role(int(role_id))
            if role is not None:
                names["role"][role_id] = role.name
        for user_id in mention_ids["user"]:
            member = guild.get_member(int(user_id))
            if member is not None:
                label = getattr(member, "display_name", None) or getattr(member, "global_name", None) or getattr(member, "name", None)
                if label:
                    names["user"][user_id] = label

    bot_loop = getattr(_discord_bot, "loop", None)
    if bot_loop is None or not bot_loop.is_running():
        return names
    try:
        return _server.run_on_bot_loop(
            _fetch_discord_text_mentions(guild_id, mention_ids, names)
        )
    except Exception:
        # The API can still render IDs when Discord is disconnected or the
        # request is running without a bot event loop.
        return names


@app.route("/api/discord/users/<user_id>")
def api_get_discord_user_profile(user_id):
    """Fetch a public Discord profile for a transcript mention popover."""
    if not re.fullmatch(r"\d{1,22}", user_id):
        return jsonify({"error": "Invalid Discord user ID."}), 400
    if _discord_bot is None:
        return jsonify({"error": "Discord profile lookup is unavailable."}), 503
    try:
        profile = _server.run_on_bot_loop(_fetch_discord_user_profile(None, user_id))
    except Exception:
        profile = None
    if profile is None:
        return jsonify({"error": "Discord user not found."}), 404
    return jsonify(profile)


@app.route("/api/discord/text", methods=["POST"])
def api_resolve_discord_text():
    """Resolve mentions in arbitrary Discord-formatted text."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "A JSON object is required."}), 400
    text = payload.get("text")
    if not isinstance(text, str):
        return jsonify({"error": "The 'text' field must be a string."}), 400
    if len(text) > 20000:
        return jsonify({"error": "Text must be 20,000 characters or fewer."}), 413
    guild_id = payload.get("guild_id")
    if guild_id is not None and not re.fullmatch(r"\d{1,20}", str(guild_id)):
        return jsonify({"error": "The 'guild_id' field must be a Discord ID."}), 400
    return jsonify({
        "text": text,
        "mention_names": resolve_discord_text_mentions(guild_id, text),
    })
