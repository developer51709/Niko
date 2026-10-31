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
        "version": "1.0",
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
    port = os.environ.get("PORT", "5000")
    local_base = f"http://127.0.0.1:{port}"
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

    version = status.get("version") or "1.0"
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

    # ── Footer ────────────────────────────────────────────────────────────────
    view.add_item(discord.ui.Container(
        line(
            f"-# Shards {shards} · v{version} · Updated {checked_at} · "
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
    """Re-edit every stored status panel every STATUS_PANEL_INTERVAL seconds."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            cxn = getattr(bot, "cxn", None)
            if cxn is None:
                await asyncio.sleep(STATUS_PANEL_INTERVAL)
                continue
            rows = await cxn.fetch(
                "SELECT channel_id, message_id FROM persistent_status_panels"
            )
            if not rows:
                await asyncio.sleep(STATUS_PANEL_INTERVAL)
                continue

            status = await _collect_status(bot)
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
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logging.warning("StatusPanel", f"Refresh tick failed: {exc}")
        await asyncio.sleep(STATUS_PANEL_INTERVAL)
