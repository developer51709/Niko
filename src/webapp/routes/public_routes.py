"""Flask routes for public."""

import datetime
import time

from config import links as bot_links
from utils import logging
from .. import leaderboard_cache
from .. import locale_feed
from .. import server as _server
from .. import site_build
from .. import status as status_source
from ..bot_card import render_bot_card
from ..staff_card import avatar_data_url

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})


async def _current_support_invite():
    """Resolve the currently valid invite from the support configuration table."""
    if _discord_bot is None or getattr(_discord_bot, "cxn", None) is None:
        return None
    from cogs.staff.support_server import get_support_invite
    return await get_support_invite(_discord_bot)


def _resolve_leaderboard_identities(user_ids):
    """Resolve Discord identities for ``user_ids``, reusing cached lookups.

    The board re-polls while it is open; without this cache every poll would
    re-fetch the same avatars and display names from Discord.
    """
    if not user_ids or _discord_bot is None:
        return {}
    identities = leaderboard_cache.cached_identities(user_ids)
    missing = {user_id for user_id in user_ids if user_id not in identities}
    if not missing:
        return identities

    async def read_identities():
        found = {}
        for user_id in missing:
            user = _discord_bot.get_user(int(user_id))
            if user is None:
                for guild in _discord_bot.guilds:
                    member = guild.get_member(int(user_id))
                    if member is not None:
                        user = member
                        break
            if user is None:
                try:
                    user = await _discord_bot.fetch_user(int(user_id))
                except Exception:
                    continue
            avatar = getattr(user, "display_avatar", None)
            found[user_id] = {
                "username": getattr(user, "name", None),
                "display_name": getattr(user, "global_name", None) or getattr(user, "display_name", None) or getattr(user, "name", None),
                "avatar_url": str(avatar.url) if avatar is not None else None,
            }
        return found

    try:
        fresh = run_on_bot_loop(read_identities())
    except Exception:
        fresh = {}
    if fresh:
        leaderboard_cache.store_identities(fresh)
    identities.update(fresh)
    return identities


@app.route("/api/economy/leaderboard")
def api_economy_leaderboard():
    """Return one ranked page of global economy standings.

    Ranks every economy profile by net worth, keeping each profile's identity
    private unless the viewer is the account owner, an official Niko staff
    member, or someone who shares a mutual server with that profile.
    """
    try:
        page = int(request.args.get("page", "1"))
        if page < 1:
            raise ValueError("page must be positive")
    except (TypeError, ValueError):
        return jsonify({"error": "Page must be a positive integer."}), 400
    page_size = 20
    offset = (page - 1) * page_size
    result = get_runtime_leaderboard_page(offset, page_size)
    if result is None:
        return jsonify({"error": "The economy leaderboard is temporarily unavailable."}), 503
    rows, total = result
    viewer_id = str((session.get("user") or {}).get("id", ""))
    official_staff = False
    if viewer_id:
        official_staff = _current_staff_role() is not None
    private_ids = {row["user_id"] for row in rows if row.get("leaderboard_private")}
    mutual_ids = set()
    if private_ids and viewer_id and not official_staff:
        resolved = get_mutual_leaderboard_identity_ids(private_ids - {viewer_id})
        if resolved is None:
            return jsonify({"error": "Private profile access could not be verified."}), 503
        mutual_ids = resolved
    visible_ids = {
        row["user_id"] for row in rows
        if not row.get("leaderboard_private")
        or row["user_id"] == viewer_id
        or official_staff
        or row["user_id"] in mutual_ids
    }
    identities = _resolve_leaderboard_identities(visible_ids)

    entries = []
    for rank, row in enumerate(rows, start=offset + 1):
        user_id = row["user_id"]
        identity = identities.get(user_id) if user_id in visible_ids else None
        entries.append({
            # Stable across polls, so the browser can animate a row that moves
            # rank. It is a salted digest, never the Discord id itself.
            "key": leaderboard_cache.profile_key(user_id),
            "rank": rank,
            "net_worth": row["net_worth"],
            "private": bool(row.get("leaderboard_private")),
            "username": identity.get("username") if identity else None,
            "display_name": identity.get("display_name") if identity else None,
            "avatar_url": identity.get("avatar_url") if identity else None,
        })
    response = jsonify({"entries": entries, "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size})
    # Polled standings must never be answered from a stale copy; the app-wide
    # after_request hook already marks every /api/ response no-store, so this
    # route only has to stay under that prefix.
    return response


@app.route("/api/levels/<guild_id>")
def api_public_guild_levels(guild_id):
    """Return one live page of a server's leveling standings.

    The page is public: a server's own board is already visible to everyone in
    it, and `/leveling leaderboard` now links here instead of rendering a
    static image. The bot must still be in the guild, so a server Niko has left
    reports its unknown-server state rather than showing stale standings.
    """
    try:
        numeric_guild_id = int(guild_id)
        page = int(request.args.get("page", "1"))
        if page < 1:
            raise ValueError("page must be positive")
    except (TypeError, ValueError):
        return jsonify({"error": "Server and page must be positive integers."}), 400

    guild = None
    if _discord_bot is not None:
        try:
            guild = _discord_bot.get_guild(numeric_guild_id)
        except Exception:
            guild = None
    if guild is None:
        return jsonify({
            "error": "Niko isn't in this server, or it is not available right now.",
            "unknown_guild": True,
        }), 404

    page_size = 25
    result = get_runtime_guild_level_page(guild_id, (page - 1) * page_size, page_size)
    if result is None:
        return jsonify({"error": "This server's leaderboard is temporarily unavailable."}), 503
    rows, total = result

    user_ids = {row["user_id"] for row in rows}
    identities = get_runtime_member_metadata(guild_id, user_ids)
    missing = user_ids - set(identities)
    if missing:
        # Members who left the guild still own their XP, so their identity is
        # resolved from the bot's user cache, which skips the guild member list.
        identities.update(_resolve_leaderboard_identities(missing))

    icon = getattr(guild, "icon", None)
    entries = []
    for rank, row in enumerate(rows, start=(page - 1) * page_size + 1):
        identity = identities.get(row["user_id"]) or {}
        entries.append({
            # Opaque, stable per process so the browser can animate a row that
            # changes rank without the API handing out Discord user ids.
            "key": leaderboard_cache.profile_key(row["user_id"]),
            "rank": rank,
            "level": row["level"],
            "xp": row["xp"],
            "xp_for_next": level_xp_for_next(row["level"]),
            "username": identity.get("username"),
            "display_name": identity.get("display_name"),
            "avatar_url": identity.get("avatar_url"),
        })

    return jsonify({
        "guild": {
            "id": str(guild.id),
            "name": guild.name,
            "icon_url": str(icon.url) if icon is not None else None,
            "member_count": int(
                getattr(guild, "member_count", 0) or len(getattr(guild, "members", []) or [])
            ),
        },
        "leveling_enabled": bool(get_runtime_level_config(guild_id).get("xp_enabled", True)),
        "entries": entries,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    })


@app.route("/api/commands")
def api_commands():
    """Public endpoint — returns public bot commands from the startup registry."""
    raw_commands = load_json("data/commands.json", [])
    valid_types = {"slash", "prefix", "hybrid", "context"}
    internal_names = _live_internal_command_names()
    cmds = []
    for command in raw_commands if isinstance(raw_commands, list) else []:
        if not isinstance(command, dict) or not command.get("name"):
            continue
        if _is_internal_command(command.get("cog"), command.get("module")):
            continue
        command_name = str(command["name"])
        if command_name in internal_names or command_name.lower() in _LEGACY_INTERNAL_COMMAND_NAMES:
            continue
        normalized = {
            "name": str(command["name"]),
            "description": _description_value(command.get("description")),
            "category": str(command.get("category") or "utility"),
            "type": command.get("type") if command.get("type") in valid_types else "slash",
            "aliases": [str(item) for item in command.get("aliases", []) if item],
            "parameters": [
                {
                    "name": str(item.get("name") or ""),
                    "description": _description_value(item.get("description")),
                    "required": bool(item.get("required", False)),
                    "type": str(item.get("type") or "string"),
                }
                for item in command.get("parameters", [])
                if isinstance(item, dict) and item.get("name")
            ],
            "permissions": [str(item) for item in command.get("permissions", []) if item],
            "usage": str(command.get("usage") or ""),
            "subcommands": [str(item) for item in command.get("subcommands", []) if item],
        }
        if command.get("context_type") in {"user", "message"}:
            normalized["context_type"] = command["context_type"]
        cmds.append(normalized)
    category = request.args.get("category", "").strip().lower()
    if category:
        cmds = [c for c in cmds if c.get("category") == category]
    return jsonify(cmds)

@app.route("/api/health")
def api_health():
    return jsonify({"ok": True, "service": "niko-api", "static_build": os.path.exists(os.path.join(WEB_DIST_DIR, "index.html"))})


@app.route("/api/site/build")
def api_site_build():
    """The build the site is serving right now.

    An open tab compares this with the build it was served from and offers to
    reload when they differ, which is only ever true when the frontend itself
    was replaced — a server-only update leaves this name alone.
    """
    return jsonify({"build": site_build.build_id()})


@app.route("/api/locales/source.json")
def api_locales_source():
    """This instance's own translation files, in the feed's manifest shape.

    Beta serves this and production pulls it (``BETA_INSTANCE_URL``), which is what
    lets the live site show translations while they are still being written.
    It only ever describes the files on the machine answering it — never a feed
    of its own — so pointing a feed at itself cannot recurse.
    """
    response = jsonify(locale_feed.local_snapshot())
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/api/locales/index.json")
def api_locales_index():
    """Which pages have which languages, with a content hash per file.

    The website reads this at startup: the picker shows the languages in it, and
    every page asks for the catalogue matching the hash it finds here, so a
    translation written on beta is fetched once and then cached by the browser.
    """
    document = locale_feed.manifest()
    response = jsonify(document)
    response.headers["Cache-Control"] = "public, max-age=15"
    return response


@app.route("/api/locales/<page>/<language>.json")
def api_locale_catalogue(page, language):
    """One page's strings in one language, beta's copy first when it has it."""
    found = locale_feed.catalogue(page, language)
    if not found:
        return jsonify({"error": "No such catalogue."}), 404
    etag = f'"{found["hash"]}"'
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=120",
        "X-Locale-Origin": found["origin"],
    }
    if request.headers.get("If-None-Match") == etag:
        return "", 304, headers
    response = jsonify(found["strings"])
    response.headers.update(headers)
    return response


@app.route("/api/locales/bot/<catalogue>/<language>.json")
def api_locale_bot_catalogue(catalogue, language):
    """One bot catalogue, so a production instance can show beta's wording.

    The bot keeps its strings next to each cog (``src/cogs/music/locales``), not
    in the website's page folders, so it gets its own route and its own entry in
    ``/api/locales/source.json``. Beta answers with its own file only; production
    fetches these and hands them to the running bot as a live overlay.
    """
    found = locale_feed.local_bot_catalogue(catalogue, language)
    if not found:
        return jsonify({"error": "No such catalogue."}), 404
    etag = f'"{found["hash"]}"'
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=120",
        "X-Locale-Origin": found["origin"],
    }
    if request.headers.get("If-None-Match") == etag:
        return "", 304, headers
    response = jsonify(found["strings"])
    response.headers.update(headers)
    return response


@app.route("/api/status")
def api_status():
    """Everything the website's /status page draws, in one live payload.

    The bot half has to run on the Discord event loop; the host and translation
    halves do not, and the translation scan is cached for a minute inside
    :mod:`webapp.status`. When the bot is not connected the page still gets a
    payload — with ``online: false`` — so it can show host and locale figures and
    say plainly that the bot is down, instead of failing the request.
    """
    loop = getattr(_discord_bot, "loop", None) if _discord_bot is not None else None
    if _discord_bot is not None and loop is not None and loop.is_running():
        try:
            payload = run_on_bot_loop(status_source.bot_status(_discord_bot), timeout=6)
        except Exception as exc:
            logging.warning("Status", f"Could not read live bot status: {exc}")
            payload = status_source.offline_status(f"{type(exc).__name__}: {exc}")
    else:
        payload = status_source.offline_status("The bot is not connected.")
    payload["host"] = status_source.host_stats()
    payload["locales"] = status_source.locale_status()
    payload["generated_at"] = int(time.time())
    return jsonify(payload)

def _server_emoji_sample(guild, emoji):
    """The lab's payload for one guild emoji, or None for an emoji it cannot use.

    Managed emojis belong to another application and an unavailable one no
    longer exists, so neither can stand in for a server's own emoji.
    """
    if getattr(emoji, "managed", False) or not getattr(emoji, "available", True):
        return None
    icon = getattr(guild, "icon", None)
    return {
        "name": emoji.name,
        "id": str(emoji.id),
        "animated": bool(getattr(emoji, "animated", False)),
        "guild_name": guild.name,
        "guild_icon_url": str(icon.with_size(128).url) if icon is not None else None,
    }


def _sample_server_emoji():
    """One real server emoji, for the rendering lab's server-emoji popup.

    The lab needs an emoji that genuinely belongs to a guild, together with the
    guild's name and icon: an application emoji forced into the server layout
    would only fake it. The support server answers first, then any guild the bot
    is in. A guild with nothing cached is asked over REST once, so a cache that
    predates the emoji cannot leave the lab with no sample.
    """
    if _discord_bot is None:
        return None
    from config.ids import SUPPORT_GUILD

    preferred = _discord_bot.get_guild(SUPPORT_GUILD)
    guilds = ([preferred] if preferred is not None else [])
    guilds += [guild for guild in getattr(_discord_bot, "guilds", ()) if guild is not preferred]
    for guild in guilds:
        for emoji in getattr(guild, "emojis", ()):
            sample = _server_emoji_sample(guild, emoji)
            if sample is not None:
                return sample
    for guild in guilds:
        try:
            from ..runtime import run_on_bot_loop
            emojis = run_on_bot_loop(guild.fetch_emojis(), timeout=6) or ()
        except Exception as exc:
            # A guild the bot cannot read is not worth failing the page over.
            app.logger.warning("server emoji sample unavailable: %s", exc)
            continue
        for emoji in emojis:
            sample = _server_emoji_sample(guild, emoji)
            if sample is not None:
                return sample
    return None


@app.route("/api/emojis")
def api_bot_emojis():
    """Every emoji the bot sends, for the website's own emoji rendering.

    Read from the bot's config on each request, with the ids the emoji sync has
    re-uploaded, so the rendering lab and the emoji popups can never drift from
    the bot. They used to read a list generated into the web app, which went
    stale as soon as an emoji was added, renamed, or re-uploaded — and a
    re-upload always changes the id, because Discord cannot replace an emoji's
    art. A short id is a stub the sync has not uploaded yet, which the website
    marks instead of requesting it from the CDN.
    """
    # Imported here so the sync's aiohttp client stays out of the web app's
    # startup path; the catalog itself is one file read.
    from utils.emoji_sync import live_emoji_catalog

    return jsonify({
        "emojis": [
            {
                "name": emoji.discord_name,
                "id": str(emoji.emoji_id),
                "animated": emoji.animated,
                "placeholder": emoji.is_placeholder,
            }
            for emoji in live_emoji_catalog()
        ],
        "server_emoji": _sample_server_emoji(),
    })


@app.route("/api/config")
def api_public_config():
    bot_avatar_url = None
    bot_name = None
    bot_display_name = None
    bot_discriminator = None
    bot_verified = False
    user = getattr(_discord_bot, "user", None) if _discord_bot is not None else None
    if user is not None:
        try:
            bot_avatar_url = str(user.display_avatar.url)
        except Exception:
            bot_avatar_url = None
        # The identity Discord prints above the bot's messages: the global
        # display name when it has one, otherwise the username.
        bot_name = str(getattr(user, "name", "") or "") or None
        bot_display_name = str(getattr(user, "display_name", "") or "") or bot_name
        # Older accounts carry a four-digit tag; migrated ones report "0" and
        # Discord shows no discriminator at all.
        bot_discriminator = str(getattr(user, "discriminator", "") or "") or None
        # Bit 16 of a user's public flags is Discord's verified-bot check — the
        # tick Discord draws inside the APP tag beside a verified bot's name.
        flags = getattr(user, "public_flags", None)
        try:
            flag_value = int(getattr(flags, "value", flags) or 0)
        except (TypeError, ValueError):
            flag_value = 0
        bot_verified = bool(flag_value & (1 << 16))
    config = {
        "application_id": DISCORD_CLIENT_ID,
        "bot_avatar_url": bot_avatar_url,
        "bot_name": bot_name,
        "bot_display_name": bot_display_name,
        "bot_discriminator": bot_discriminator,
        "bot_verified": bot_verified,
        "invite_url": (
            f"https://discord.com/oauth2/authorize?"
            f"{urlencode({'client_id': DISCORD_CLIENT_ID, 'permissions': '8', 'scope': 'bot applications.commands'})}"
        ),
        "oauth_available": oauth_enabled(),
    }
    if _discord_bot is not None and getattr(_discord_bot, "loop", None) is not None and _discord_bot.loop.is_running():
        try:
            config["support_server_url"] = run_on_bot_loop(_current_support_invite())
        except Exception as exc:
            logging.warning("PublicConfig", f"Could not load current support invite: {exc}")
            config["support_server_url"] = None
    else:
        config["support_server_url"] = None
    return jsonify(config)

@app.route("/api/botstats")
def api_botstats():
    # Prefer live values from the running bot so the numbers are realtime
    # instead of the startup snapshot in data/bot_stats.json.
    if _discord_bot is not None and getattr(_discord_bot, "loop", None) is not None:
        try:
            live = run_on_bot_loop(_live_bot_stats(), timeout=5)
            if live:
                return jsonify(live)
        except Exception:
            pass

    stats = load_json(BOT_STATS, {})
    econ_count = len(glob.glob(os.path.join(ECONOMY_DIR, "[0-9]*.json")))
    return jsonify({
        "guild_count":   stats.get("guild_count", 0),
        "user_count":    stats.get("user_count", 0),
        "command_count": stats.get("command_count", 76),
        "uptime_since":  stats.get("uptime_since", None),
        "version":       stats.get("version"),
        "economy_users": econ_count,
    })


def _bot_card_profile() -> dict:
    """The figures Niko's own README card draws, read from the running bot.

    Counts come from the same live snapshot ``/api/botstats`` uses, so the card
    and the website can never disagree. Latency and uptime are read straight
    from the bot object, which is safe from the Flask thread because neither
    awaits anything. When the gateway is down the startup snapshot still fills
    the tiles and the card shows the offline presence instead of breaking.
    """
    bot = _discord_bot
    snapshot = load_json(BOT_STATS, {})

    stats = None
    coro = _live_bot_stats()
    try:
        live = run_on_bot_loop(coro, timeout=3)
        stats = dict(live) if live else None
    except Exception:
        # Nothing was scheduled (no bot loop, or the future raised), so close
        # the coroutine instead of leaving it un-awaited.
        coro.close()
        stats = None

    stats = stats or {
        "guild_count": snapshot.get("guild_count", 0),
        "user_count": snapshot.get("user_count", 0),
        "command_count": snapshot.get("command_count", 0),
        "version": snapshot.get("version"),
    }

    user = getattr(bot, "user", None) if bot is not None else None
    online = bool(user is not None and getattr(bot, "is_ready", lambda: False)())

    avatar_url = None
    if user is not None:
        try:
            avatar_url = str(user.display_avatar.url)
        except Exception:
            avatar_url = None

    latency_ms = None
    if online:
        try:
            latency_ms = round(float(bot.latency) * 1000)
        except Exception:
            latency_ms = None

    uptime_seconds = None
    start_time = getattr(bot, "start_time", None) if bot is not None else None
    if isinstance(start_time, (int, float)) and start_time > 0:
        uptime_seconds = max(0, time.time() - start_time)
    else:
        since = snapshot.get("uptime_since")
        if since:
            try:
                uptime_seconds = max(0, time.time() - datetime.datetime.fromisoformat(since).timestamp())
            except (TypeError, ValueError):
                uptime_seconds = None

    return {
        "name": getattr(user, "display_name", None) or getattr(user, "name", None) or "Niko",
        "handle": getattr(user, "name", None) or "niko",
        "avatar_url": avatar_url,
        "online": online,
        "guild_count": stats.get("guild_count", 0),
        "user_count": stats.get("user_count", 0),
        "command_count": stats.get("command_count", 0),
        "latency_ms": latency_ms,
        "uptime_seconds": uptime_seconds,
        "version": str(stats.get("version") or ""),
    }


@app.route("/bot/card.svg")
def api_bot_card():
    """Niko's live profile card, for the README and any other README.

    GitHub fetches this through its image proxy inside an ``<img>``, so the
    document must stand on its own: the avatar is inlined as a data URI and the
    markup uses presentation attributes instead of an external stylesheet.
    """
    profile = _bot_card_profile()
    svg = render_bot_card(
        profile,
        theme=request.args.get("theme"),
        accent=request.args.get("accent"),
        avatar_data_url=avatar_data_url(profile.get("avatar_url")),
    )
    response = Response(svg, mimetype="image/svg+xml")
    # The figures are live, so no layer may reuse a rendered card. GitHub's
    # image proxy and the browser both honour this and revalidate instead of
    # serving the counts the bot had when the image was first requested.
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


async def _live_bot_stats():
    """Collect stats directly from the connected bot (runs on the bot loop)."""
    bot = _discord_bot
    if bot is None or not getattr(bot, "is_ready", lambda: False)():
        return None
    guilds = list(bot.guilds)
    user_count = sum(g.member_count or 0 for g in guilds)
    command_count = getattr(bot, "_status_command_count", None)
    if command_count is None:
        # The public registry uses the same filtering and deduplication as the
        # commands page, including nested slash commands and context menus.
        command_registry = load_json("data/commands.json", None)
        if isinstance(command_registry, list):
            command_count = sum(
                1 for command in command_registry
                if isinstance(command, dict)
                and command.get("name")
                and not _is_internal_command(command.get("cog"), command.get("module"))
                and str(command["name"]).lower() not in _LEGACY_INTERNAL_COMMAND_NAMES
                and str(command["name"]) not in _live_internal_command_names()
            )
        else:
            command_count = load_json(BOT_STATS, {}).get("command_count", 76)
    if not command_count:
        command_count = load_json(BOT_STATS, {}).get("command_count", 76)
    return {
        "guild_count":   len(guilds),
        "user_count":    user_count,
        "command_count": command_count,
        "uptime_since":  load_json(BOT_STATS, {}).get("uptime_since"),
        "version":       load_json(BOT_STATS, {}).get("version"),
        "economy_users": len(glob.glob(os.path.join(ECONOMY_DIR, "[0-9]*.json"))),
    }
