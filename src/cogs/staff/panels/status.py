"""Realtime status panel: health probes, the layout, and its refresh loop."""

import asyncio
import datetime
import json
import os
import time
from urllib.parse import urlsplit

import aiohttp
import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils import logging

# The refresh cadence lives with the panel so the footer and the loop can never
# disagree about it.
STATUS_PANEL_INTERVAL = 30.0

#: How long before the next edit the next snapshot starts collecting. The
#: database ping and the health probes take a few seconds; starting this far
#: ahead means the snapshot is ready when the interval elapses, while its
#: figures still describe the bot seconds before the panel is redrawn.
STATUS_PANEL_PREFETCH_LEAD = 10.0


def _load_bot_stats_file() -> dict:
    """Read data/bot_stats.json written at startup (best-effort)."""
    try:
        with open("data/bot_stats.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _human_uptime(seconds: float) -> str:
    seconds = int(max(0, seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _command_counts(bot) -> tuple:
    """Return (global slash/context commands, prefix commands)."""
    slash = 0
    prefix = 0
    try:
        slash = len(list(bot.tree.get_commands(guild=None) or []))
    except Exception:
        pass
    try:
        prefix = len(bot.commands)
    except Exception:
        pass
    return slash, prefix


async def _probe_http(url: str) -> bool:
    """GET a URL and confirm it responded healthily."""
    try:
        timeout = aiohttp.ClientTimeout(total=4)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return False
                if url.endswith("/api/health"):
                    try:
                        payload = await resp.json(content_type=None)
                        return bool(payload and payload.get("ok"))
                    except Exception:
                        return False
                return True
    except Exception:
        return False


async def _check_database(bot):
    """Return (backend label, healthy bool|None) for the active pool."""
    cxn = getattr(bot, "cxn", None)
    if cxn is None:
        return "unknown", None
    backend = getattr(cxn, "db_type", "unknown")
    try:
        if backend == "sqlite":
            await cxn.fetchval("SELECT 1")
        else:
            # MongoDB (motor or pymongo-backed) — ping the server.
            result = cxn.client.admin.command("ping")
            if asyncio.iscoroutine(result):
                await result
        return backend, True
    except Exception:
        return backend, False


def _local_api_base() -> str:
    """The API this process is actually serving on.

    ``PORT`` is the supervisor's public port in supervised mode and is removed
    from the child environment; the child's Flask server binds an ephemeral
    loopback port instead.  Asking ``api_server`` for the bound port keeps the
    panel aligned in both modes, and its own fallback still covers the case
    where the API is not serving yet.
    """
    try:
        import api_server

        port = api_server.listening_port()
    except Exception:
        port = int(os.environ.get("PORT", "5000"))
    return f"http://127.0.0.1:{port}"


def _percent(value) -> str:
    """A percentage without a trailing ``.0`` — the panel has no room to waste."""
    text = f"{float(value or 0):.1f}"
    return text[:-2] if text.endswith(".0") else text


def _translation_snapshot() -> dict | None:
    """Coverage figures for the status panel's translation card.

    Read through :mod:`webapp.status`, the module the public /status page and the
    owner's locale page use: it already merges beta's live catalogues into the
    numbers, and the dashboard runs in this same process, so the card cannot
    disagree with them. A panel must never fall over because the API half is
    absent, so every failure here simply drops the card.
    """
    try:
        from webapp import status as site_status

        payload = site_status.locale_status()
    except Exception:
        return None

    bot_rows = {str(row.get("code")): row for row in payload.get("bot") or []}
    site_rows = {str(row.get("code")): row for row in payload.get("website") or []}
    # English is the source copy, so counting it would advertise 100% forever.
    codes = [code for code in payload.get("languages") or [] if code != "en"]

    def share(rows) -> float:
        done = sum(int((rows.get(code) or {}).get("translated") or 0) for code in codes)
        total = sum(int((rows.get(code) or {}).get("total") or 0) for code in codes)
        return round(done / total * 100, 1) if total else 0.0

    languages = []
    for code in codes:
        bot_row = bot_rows.get(code) or {}
        site_row = site_rows.get(code) or {}
        languages.append({
            "label": bot_row.get("label") or site_row.get("label") or str(code).upper(),
            "bot": float(bot_row.get("percent") or 0),
            "site": float(site_row.get("percent") or 0),
        })
    if not languages:
        return None
    languages.sort(key=lambda row: (row["site"], row["bot"]), reverse=True)

    source = payload.get("source") or {}
    return {
        "languages": len(payload.get("languages") or []),
        "bot": share(bot_rows),
        "site": share(site_rows),
        "rows": languages,
        "mode": str(source.get("mode") or "local"),
        "scanned_at": int(payload.get("scanned_at") or time.time()),
    }


async def _collect_status(bot) -> dict:
    """Snapshot every stat the panel shows. Best-effort; never raises."""
    now = time.time()
    status = {
        "checked_at": int(now),
        "guild_count": len(bot.guilds),
        "member_count": sum((g.member_count or 0) for g in bot.guilds),
        "shard_count": getattr(bot, "shard_count", 1),
        "slash_commands": 0,
        "prefix_commands": 0,
        "uptime": "—",
        # Filled from ``data/bot_stats.json`` below; unknown until the bot has
        # written its first snapshot, and left out of the footer until then.
        "version": None,
        "latency_ms": None,
        "gateway_ok": None,
        "music_ok": None,
        "music_nodes": 0,
        "database_backend": "unknown",
        "database_ok": None,
        "website_ok": None,
        "website_note": None,
        "api_ok": None,
        "overall_ok": None,
        "translations": None,
    }

    try:
        slash, prefix = _command_counts(bot)
        status["slash_commands"] = slash
        status["prefix_commands"] = prefix
    except Exception:
        pass

    # Uptime — prefer the startup marker written by events.startup.writers,
    # otherwise fall back to when this panel system first came up.
    try:
        uptime_ts = None
        iso = _load_bot_stats_file().get("uptime_since")
        if iso:
            dt = datetime.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            uptime_ts = dt.timestamp()
        if uptime_ts is None:
            if not hasattr(bot, "_niko_status_started"):
                bot._niko_status_started = now
            uptime_ts = bot._niko_status_started
        status["uptime"] = _human_uptime(now - uptime_ts)
    except Exception:
        pass

    try:
        saved = _load_bot_stats_file()
        if saved.get("version"):
            status["version"] = str(saved["version"])
    except Exception:
        pass

    # Gateway status + latency.
    try:
        if bot.is_closed():
            status["gateway_ok"] = False
        elif bot.is_ready():
            status["gateway_ok"] = True
        if bot.latencies:
            status["latency_ms"] = round(
                sum(lat for _, lat in bot.latencies) / len(bot.latencies) * 1000
            )
        elif bot.latency is not None:
            status["latency_ms"] = round(bot.latency * 1000)
    except Exception:
        pass

    # Music health comes directly from the music cog's live node state. This
    # avoids probing Lavalink again and keeps the panel aligned with playback.
    try:
        music_cog = bot.get_cog("MusicSystem")
        if music_cog is not None:
            node_labels = getattr(music_cog, "_node_labels", ()) or ()
            status["music_nodes"] = len(node_labels)
            status["music_ok"] = bool(getattr(music_cog, "connected", False)) and bool(node_labels)
    except Exception:
        pass

    # Check the database and local API separately from public website exposure.
    try:
        db_backend, db_ok = await _check_database(bot)
        status["database_backend"] = db_backend
        status["database_ok"] = db_ok
    except Exception:
        pass
    local_base = _local_api_base()
    try:
        status["api_ok"] = await _probe_http(f"{local_base}/api/health")
    except Exception:
        status["api_ok"] = False

    # A local frontend response does not prove the configured domain is
    # reachable from outside this process. Probe PUBLIC_URL directly and do
    # not let local API health gate the public website result.
    public_url = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")
    parsed_public_url = urlsplit(public_url)
    if not public_url:
        status["website_ok"] = False
        status["website_note"] = "PUBLIC_URL not configured"
    elif parsed_public_url.scheme not in {"http", "https"} or not parsed_public_url.netloc:
        status["website_ok"] = False
        status["website_note"] = "PUBLIC_URL is invalid"
    else:
        try:
            status["website_ok"] = await _probe_http(f"{public_url}/")
        except Exception:
            status["website_ok"] = False

    # The translation card is an owner switch, and it is the most expensive
    # figure on the panel, so it is only collected while it is switched on.
    try:
        # Imported here, not at the top of the file: an update applies one area
        # at a time, and this module must still load on a deployment that has
        # not received ``utils/panel_settings.py`` yet. ``ensure_loaded`` covers
        # the other direction: the module can arrive after this process booted,
        # in which case the first pass after it does reads its stored flag.
        from utils import panel_settings

        await panel_settings.ensure_loaded(bot)
        if panel_settings.show_translation_card():
            status["translations"] = _translation_snapshot()
    except Exception:
        status["translations"] = None

    # Overall roll-up for the summary row on the panel.
    checks = [
        status.get("database_ok"),
        status.get("website_ok"),
        status.get("api_ok"),
        status.get("gateway_ok"),
        status.get("music_ok"),
    ]
    if any(ok is False for ok in checks):
        status["overall_ok"] = False
    elif all(ok is True for ok in checks):
        status["overall_ok"] = True
    else:
        status["overall_ok"] = None

    return status


def _build_status_panel(bot, status: dict) -> discord.ui.LayoutView:
    """Render the realtime status panel layout from a status snapshot.

    API-safe notes: Discord only allows accessory types 2 (Button) or 11
    (thumbnail/media) on a Section, so every stat here is a plain TextDisplay
    block inside accent-coloured Containers — no TextDisplay accessories.
    """
    tick = get_emoji("tick")
    cross = get_emoji("cross")
    pending = get_emoji("loading")

    def state_of(healthy):
        if healthy is True:
            return "Operational"
        if healthy is False:
            return "Down"
        return "Checking…"

    def state_emoji(healthy):
        if healthy is True:
            return tick
        if healthy is False:
            return cross
        return pending

    def line(content: str) -> discord.ui.TextDisplay:
        """One stat row — a plain TextDisplay (valid in any container)."""
        return discord.ui.TextDisplay(content=content)

    def separator() -> discord.ui.Separator:
        return discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)

    def health_accent() -> int:
        checks = [
            status.get("database_ok"),
            status.get("website_ok"),
            status.get("api_ok"),
            status.get("gateway_ok"),
            status.get("music_ok"),
        ]
        if any(ok is False for ok in checks):
            return 0xED4245  # red — something is down
        if all(ok is True for ok in checks):
            return 0x57F287  # green — all systems nominal
        return 0x5865F2    # blurple — still checking

    # ── Derived values ────────────────────────────────────────────────────────
    guild_count = f"{int(status.get('guild_count') or 0):,}"
    member_count = f"{int(status.get('member_count') or 0):,}"
    slash = int(status.get("slash_commands") or 0)
    prefix = int(status.get("prefix_commands") or 0)
    shards = int(status.get("shard_count") or 1)
    latency = status.get("latency_ms")
    latency_text = f"{latency}ms" if latency is not None else "—"
    db_ok = status.get("database_ok")
    website_ok = status.get("website_ok")
    api_ok = status.get("api_ok")
    gateway_ok = status.get("gateway_ok")
    music_ok = status.get("music_ok")
    music_nodes = int(status.get("music_nodes") or 0)
    overall_ok = status.get("overall_ok")

    db_backend = str(status.get("database_backend") or "unknown")
    if db_backend == "sqlite":
        db_backend = "SQLite"
    elif db_backend == "mongodb":
        db_backend = "MongoDB"

    version = status.get("version")
    version_text = f" · v{version}" if version else ""
    checked_at = f"<t:{int(status.get('checked_at') or time.time())}:R>"
    uptime = status.get("uptime") or "—"

    if overall_ok is True:
        overall_text = "All systems operational"
    elif overall_ok is False:
        overall_text = "Service disruption"
    else:
        overall_text = "Checking…"

    view = discord.ui.LayoutView()

    # ── Identity header ───────────────────────────────────────────────────────
    avatar = None
    bot_name = "Niko"
    try:
        user = getattr(bot, "user", None)
        avatar = getattr(user, "display_avatar", None) or getattr(user, "avatar", None)
        bot_name = user.display_name if user is not None else "Niko"
    except Exception:
        pass

    header_text = discord.ui.TextDisplay(content=(
        f"# ☕ {bot_name} Status\n"
        f"-# Real-time status for the official support server"
    ))
    if avatar is not None:
        header_card = discord.ui.Container(
            discord.ui.Section(
                header_text,
                accessory=discord.ui.Thumbnail(str(avatar.url)),
            ),
            accent_colour=0xC8A882,
        )
    else:
        header_card = discord.ui.Container(header_text, accent_colour=0xC8A882)
    view.add_item(header_card)

    # ── At a glance card ──────────────────────────────────────────────────────
    glance = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('notepad')} At a Glance"),
        separator(),
        line(f"{get_emoji('home')} **Servers** — **{guild_count}**"),
        line(f"{get_emoji('moderation')} **Users** — **{member_count}**"),
        line(f"{get_emoji('message')} **Commands** — **{slash:,}** slash · **{prefix:,}** prefix"),
        line(f"{get_emoji('stats')} **Uptime** — **{uptime}**"),
        accent_colour=0x5865F2,
    )
    view.add_item(glance)

    # ── System health card ────────────────────────────────────────────────────
    website_text = state_of(website_ok)
    if status.get("website_note"):
        website_text = f"{website_text} · {status['website_note']}"

    health = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('cpu')} System Health"),
        separator(),
        line(f"{state_emoji(overall_ok)} **Overall** — {overall_text}"),
        line(f"{state_emoji(db_ok)} **Database** — {db_backend} · {state_of(db_ok)}"),
        line(f"{state_emoji(website_ok)} **Website** — {website_text}"),
        line(f"{state_emoji(api_ok)} **API** — {state_of(api_ok)}"),
        line(f"{state_emoji(gateway_ok)} **Gateway** — {state_of(gateway_ok)} · {latency_text}"),
        line(f"{state_emoji(music_ok)} **Music** — {state_of(music_ok)} · {music_nodes} active node{'s' if music_nodes != 1 else ''}"),
        accent_colour=health_accent(),
    )
    view.add_item(health)

    # ── Translation coverage (owner toggle) ───────────────────────────────────
    # Kept off by default: the panel is the support server's first impression and
    # the card is a display choice, so the owner's locale page owns the switch.
    translations = status.get("translations")
    if translations:
        origin = "live from beta" if translations.get("mode") == "beta" else "from this build"
        marker = get_emoji("stats") or ""
        heading = f"### {marker} Translation Coverage" if marker else "### Translation Coverage"
        contents = [
            discord.ui.TextDisplay(content=heading),
            separator(),
            line(
                f"-# {int(translations.get('languages') or 0)} languages · "
                f"bot **{_percent(translations.get('bot'))}%** · "
                f"website **{_percent(translations.get('site'))}%** translated"
            ),
        ]
        # Every shipped language, most translated first: the summary line counts
        # them, so the card has to list all of them or the reader is left
        # wondering which four the numbers came from.
        for row in translations.get("rows") or []:
            contents.append(line(
                f"**{row['label']}** — website {_percent(row['site'])}% · bot {_percent(row['bot'])}%"
            ))
        # One timestamp only: Discord renders it in the reader's own time zone and
        # keeps it relative, so a second "Ns ago" figure would just disagree with it.
        contents.append(line(f"-# {origin} · scanned <t:{int(translations.get('scanned_at') or time.time())}:R>"))
        view.add_item(discord.ui.Container(*contents, accent_colour=0x2E3440))

    # ── Footer ────────────────────────────────────────────────────────────────
    view.add_item(discord.ui.Container(
        line(
            f"-# Shards {shards}{version_text} · Updated {checked_at} · "
            f"refreshes every {int(STATUS_PANEL_INTERVAL)}s"
        ),
        accent_colour=0x2E3440,
    ))
    return view


class StatusPanelCog(commands.Cog):
    """Internal cog that owns the persistent status-panel refresh loop."""

    def __init__(self, bot):
        self.bot = bot
        self._refresh_task = None

    async def cog_load(self):
        self._refresh_task = asyncio.create_task(_status_refresh_loop(self.bot))

    async def cog_unload(self):
        if self._refresh_task is not None:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass


async def _status_refresh_loop(bot):
    """Re-edit every stored status panel every STATUS_PANEL_INTERVAL seconds.

    Collecting a snapshot is the slow part of a tick — the guild and member
    counts, the command totals, the database ping and the two health probes
    take a few seconds. The next snapshot therefore starts collecting
    ``STATUS_PANEL_PREFETCH_LEAD`` seconds before the next tick, so its work
    happens between edits and the edit lands on the interval instead of a few
    seconds after it, with figures that are still only seconds old.
    """
    await bot.wait_until_ready()
    prefetch = None
    try:
        while not bot.is_closed():
            started = time.monotonic()
            rows = []
            try:
                cxn = getattr(bot, "cxn", None)
                if cxn is not None:
                    rows = await cxn.fetch(
                        "SELECT channel_id, message_id FROM persistent_status_panels"
                    )
                if rows:
                    # A first pass (or one whose prefetch never finished) still
                    # collects inline, so a panel is never left unrendered.
                    status = await prefetch if prefetch is not None else await _collect_status(bot)
                    prefetch = None
                    # The snapshot was collected ahead of time; stamp the edit
                    # itself so the footer's "Updated … ago" never carries the
                    # prefetch lead (which made a 30s refresh read as 40s).
                    status["checked_at"] = int(time.time())
                    panel_view = _build_status_panel(bot, status)
                    for row in rows:
                        try:
                            channel = bot.get_channel(int(row["channel_id"]))
                            if channel is None:
                                continue
                            message = channel.get_partial_message(int(row["message_id"]))
                            await message.edit(view=panel_view)
                        except discord.HTTPException:
                            # Deleted panel, missing permissions, etc. — skip this row.
                            continue
                        except Exception:
                            continue
                elif prefetch is not None:
                    # The panels are gone; stop paying for a snapshot nobody
                    # is going to render.
                    prefetch.cancel()
                    prefetch = None
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logging.warning("StatusPanel", f"Refresh tick failed: {exc}")

            # Keep the cadence anchored to the start of this tick, and gather
            # the next snapshot ahead of the next one: the collection then runs
            # between edits instead of pushing the edit that triggered it back.
            deadline = started + STATUS_PANEL_INTERVAL
            if rows:
                start_at = deadline - STATUS_PANEL_PREFETCH_LEAD
                now = time.monotonic()
                if start_at > now:
                    await asyncio.sleep(start_at - now)
                prefetch = asyncio.create_task(_collect_status(bot))
            await asyncio.sleep(max(0.0, deadline - time.monotonic()))
    finally:
        if prefetch is not None:
            prefetch.cancel()
