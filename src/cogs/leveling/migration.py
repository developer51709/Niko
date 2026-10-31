"""The DM Niko sends the inviter when it joins a server, and the leveling import
it offers there.

Several popular leveling bots publish a guild's leaderboard through a public
HTTP endpoint, which means Niko can read it without the member having to hand
over anything.

* **MEE6** — ``/api/plugins/levels/leaderboard/{guild}``. Unofficial and
  undocumented, and the server has to switch "make my server's leaderboard
  public" on, but no key is involved.
* **Lurkr** — ``/v2/levels/{guild}``. Officially documented as public and
  unauthenticated, 100 entries per page.
* **AmariBot** — ``/guild/leaderboard/{guild}``. The key is issued to AmariBot's
  API applicants rather than to each server, so it is set once for this
  deployment in ``AMARIBOT_API_KEY`` and the import is only offered when that
  key is present.

Tatsu publishes a leaderboard too, but its key is per-application and the
endpoints are not documented well enough to rely on, so it is left out. Bots
without a leaderboard endpoint (Arcane, Dyno, ProBot) only render a web page and
cannot be read this way either.

The import keeps the level the other bot reports and stores the progress the
member had inside that level, because Niko's ``levels`` table stores XP *within*
the current level rather than a lifetime total. A member who is already further
along in Niko is never pushed back.
"""

from __future__ import annotations

import asyncio
import os

import aiohttp
import discord
from discord.ext import commands

from config.emojis import get_emoji
from config.links import WEBSITE
from utils import logging as log
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from .panel import ACCENT_BRAND

MESSAGES = load_locales("cogs.leveling", "migration")

msg = make_flat_msg(MESSAGES, {
    "tick": get_emoji("tick"),
    "cross": get_emoji("cross"),
})

# The invite DM's buttons stay usable for half an hour, which is long enough to
# click through from a notification without keeping a view alive forever.
DM_TIMEOUT_SECONDS = 1800

# Every page request has a short timeout, so a stalled leaderboard fails the
# import instead of leaving the DM waiting on it.
REQUEST_TIMEOUT_SECONDS = 15

#: AmariBot hands its key to the applicant behind the bot, not to each server, so
#: one deployment-wide key covers every guild the bot is in.
AMARIBOT_KEY_ENV = "AMARIBOT_API_KEY"


def _parse_mee6(payload) -> list:
    """``players`` rows from MEE6's leaderboard payload."""
    return [
        (player.get("id"), player.get("level"), player.get("xp"))
        for player in payload.get("players") or []
        if isinstance(player, dict)
    ]


def _parse_amaribot(payload) -> list:
    """``data`` rows from AmariBot's leaderboard payload (XP is called ``exp``)."""
    return [
        (member.get("id"), member.get("level"), member.get("exp"))
        for member in payload.get("data") or []
        if isinstance(member, dict)
    ]


def _parse_lurkr(payload) -> list:
    """``levels`` rows from Lurkr's leaderboard payload."""
    return [
        (entry.get("userId"), entry.get("level"), entry.get("xp"))
        for entry in payload.get("levels") or []
        if isinstance(entry, dict)
    ]


def _amaribot_key() -> str:
    """The AmariBot key this deployment was given, or "" when there is none."""
    return (os.environ.get(AMARIBOT_KEY_ENV) or "").strip()


def _amaribot_headers() -> dict:
    """AmariBot wants the bare key in ``Authorization``, without a scheme."""
    key = _amaribot_key()
    return {"Authorization": key} if key else {}


#: Bots whose guild leaderboard Niko can read, and how to read it.
PROVIDERS = {
    "mee6": {
        "name": "MEE6",
        "bot_id": 159985870458322944,
        "url": "https://mee6.xyz/api/plugins/levels/leaderboard/{guild}",
        "parse": _parse_mee6,
        "first_page": 0,
        "page_size": 1000,
        "size_param": "limit",
        "max_pages": 100,
        "delay": 0.5,
        # MEE6 reports lifetime XP; Niko stores progress inside the level.
        "cumulative_xp": True,
    },
    "amaribot": {
        "name": "AmariBot",
        "bot_id": 339254240012664832,
        "url": "https://amaribot.com/api/v1/guild/leaderboard/{guild}",
        "parse": _parse_amaribot,
        "first_page": 1,
        "page_size": 1000,
        "size_param": "limit",
        "max_pages": 100,
        # The API allows 60 requests a minute.
        "delay": 1.0,
        # AmariBot reports lifetime XP, like MEE6 does.
        "cumulative_xp": True,
        "headers": _amaribot_headers,
        # Only offered when this deployment has a key, so the import can run.
        "available": _amaribot_key,
        "keyed": True,
    },
    "lurkr": {
        "name": "Lurkr",
        "bot_id": 506186003816513538,
        "url": "https://api.lurkr.gg/v2/levels/{guild}",
        "parse": _parse_lurkr,
        "first_page": 1,
        "page_size": 100,
        "size_param": None,
        "max_pages": 100,
        "delay": 0.0,
        # Lurkr already reports XP within the current level.
        "cumulative_xp": False,
    },
}

#: Order matters when a server runs more than one: MEE6 data is the most
#: complete and is what people usually mean by "my levels".
PROVIDER_ORDER = ("mee6", "amaribot", "lurkr")


class LeaderboardUnavailable(Exception):
    """The other bot refused the request or has no leaderboard to give."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def settings_url(guild_id) -> str:
    """The dashboard page for a server's leveling settings."""
    return f"{WEBSITE}/dashboard/{int(guild_id)}/leveling"


def detect_provider(guild) -> str | None:
    """Return the first supported leveling bot present in *guild*, if any."""
    if guild is None:
        return None
    for key in PROVIDER_ORDER:
        config = PROVIDERS[key]
        available = config.get("available")
        if available is not None and not available():
            continue
        if guild.get_member(config["bot_id"]) is not None:
            return key
    return None


def _as_int(value) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _clean_rows(raw) -> list:
    """Drop entries that cannot be a real member row."""
    rows = []
    for user_id, level, xp in raw:
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            continue
        rows.append({"user_id": user_id, "level": _as_int(level), "xp": _as_int(xp)})
    return rows


def import_progress(level: int, xp: int, *, cumulative: bool, xp_for_level) -> tuple:
    """Convert another bot's row into the ``(level, xp)`` Niko stores.

    Niko keeps XP *within* the current level and resets it on level-up, so a
    lifetime total (MEE6) has to have the completed levels deducted first. The
    imported level itself is kept as reported: members should not lose a level
    to a different XP curve, and any leftover is clamped to the current level.
    """
    level = max(0, int(level))
    xp = max(0, int(xp))
    if cumulative:
        xp -= sum(xp_for_level(stage) for stage in range(level))
    ceiling = max(1, xp_for_level(level)) - 1
    return level, max(0, min(xp, ceiling))


def imported_wins(level: int, xp: int, existing) -> bool:
    """Whether imported data should replace a member's stored Niko row."""
    if not existing:
        return True
    return (level, xp) > (int(existing[0]), int(existing[1]))


async def fetch_leaderboard(guild_id, provider: str, session) -> list:
    """Read a guild's whole leaderboard, page by page."""
    config = PROVIDERS[provider]
    url = config["url"].format(guild=int(guild_id))
    headers = config["headers"]() if config.get("headers") else None
    rows, page = [], config["first_page"]

    for _ in range(config["max_pages"]):
        params = {"page": page}
        if config["size_param"]:
            params[config["size_param"]] = config["page_size"]
        try:
            async with session.get(
                url, params=params, headers=headers,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS),
            ) as response:
                if response.status != 200:
                    raise LeaderboardUnavailable(
                        f"{config['name']} answered HTTP {response.status}",
                        status=response.status,
                    )
                payload = await response.json(content_type=None)
        except LeaderboardUnavailable:
            raise
        except Exception as error:
            raise LeaderboardUnavailable(str(error)) from error

        batch = _clean_rows(config["parse"](payload or {}))
        rows.extend(batch)
        # Only an empty page means the end: a server that caps a page below the
        # requested size would otherwise silently cut the import short.
        if not batch:
            break
        page += 1
        if config["delay"]:
            await asyncio.sleep(config["delay"])
    return rows


class _MigrateButton(discord.ui.Button):
    def __init__(self, cog: "LevelMigration", guild, provider: str):
        super().__init__(
            label=msg(guild, "migrate_button", bot=PROVIDERS[provider]["name"]),
            style=discord.ButtonStyle.success,
        )
        self.cog      = cog
        self.guild    = guild
        self.provider = provider

    async def callback(self, interaction: discord.Interaction):
        await self.cog.migrate(interaction, self.guild, self.provider)


class _DeclineButton(discord.ui.Button):
    def __init__(self, cog: "LevelMigration", guild):
        super().__init__(label=msg(guild, "decline_button"), style=discord.ButtonStyle.secondary)
        self.cog   = cog
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            view=_text_view(msg(self.guild, "declined", url=settings_url(self.guild.id)))
        )


def _text_view(text: str) -> discord.ui.LayoutView:
    """A plain components-v2 message: one container, no interactive parts."""
    view = discord.ui.LayoutView(timeout=DM_TIMEOUT_SECONDS)
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        accent_colour=discord.Colour(ACCENT_BRAND),
    ))
    return view


class LevelMigration(commands.Cog):
    """Offer to carry a server's existing levels over from another bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Guards against a member clicking the import twice in one DM.
        self._running: set = set()

    async def cog_load(self):
        # The public leaderboards are only read on demand, but one shared
        # session keeps the TLS handshake out of every page request.
        self._session = aiohttp.ClientSession(
            headers={"User-Agent": "NikoBot (https://niko.sryze.cc)"}
        )

    async def cog_unload(self):
        session = getattr(self, "_session", None)
        if session is not None and not session.closed:
            await session.close()

    # ── JOIN DM ────────────────────────────────────

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        try:
            provider = detect_provider(guild)
            inviter  = await self._inviter(guild)
            if inviter is None:
                log.info("LevelMigration", f"No inviter found for {guild.name} ({guild.id}); skipping DM.")
                return
            await inviter.send(view=self._welcome_view(guild, provider))
            log.info(
                "LevelMigration",
                f"Sent the welcome DM for {guild.name} ({guild.id}) to {inviter}"
                + (f" with a {PROVIDERS[provider]['name']} import offer." if provider else "."),
            )
        except discord.Forbidden:
            log.info("LevelMigration", f"Could not DM the inviter of {guild.name} ({guild.id}) — DMs closed.")
        except Exception as error:
            log.warning("LevelMigration", f"Welcome DM failed for {guild.id}: {error}")

    async def _inviter(self, guild: discord.Guild):
        """Who added Niko, from the audit log, falling back to the owner.

        The audit entry can land a beat after ``on_guild_join``, so a missing
        entry is retried once before giving up.
        """
        me = self.bot.user
        for attempt in range(2):
            if attempt:
                await asyncio.sleep(1.5)
            try:
                async for entry in guild.audit_logs(
                    limit=6, action=discord.AuditLogAction.bot_add
                ):
                    target = getattr(entry, "target", None)
                    if me is not None and getattr(target, "id", None) == me.id:
                        return entry.user
            except (discord.Forbidden, discord.HTTPException):
                # Without View Audit Log there is still an owner to talk to.
                break
        return guild.owner

    def _welcome_view(self, guild: discord.Guild, provider: str | None) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView(timeout=DM_TIMEOUT_SECONDS)
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=msg(guild, "title", guild=guild.name)),
                discord.ui.TextDisplay(
                    content=msg(guild, "settings", url=settings_url(guild.id))
                ),
                accessory=discord.ui.Thumbnail(self.bot.user.display_avatar.url),
            ),
            accent_colour=discord.Colour(ACCENT_BRAND),
        )

        if provider:
            name = PROVIDERS[provider]["name"]
            container.add_item(discord.ui.Separator(
                visible=True, spacing=discord.SeparatorSpacing.small))
            container.add_item(discord.ui.TextDisplay(content=msg(guild, "detected", bot=name)))
            container.add_item(discord.ui.ActionRow(
                _MigrateButton(self, guild, provider),
                _DeclineButton(self, guild),
            ))

        view.add_item(container)
        return view

    # ── IMPORT ─────────────────────────────────────

    async def migrate(self, interaction: discord.Interaction, guild, provider: str):
        key = (guild.id, provider)
        if key in self._running:
            # Ephemeral replies are not available in DMs, so this lands as a
            # short extra message in the same conversation.
            await interaction.response.send_message(msg(guild, "already_running"))
            return

        name = PROVIDERS[provider]["name"]
        self._running.add(key)
        try:
            # Replace the prompt immediately so the buttons cannot be clicked
            # again while the leaderboard is being read.
            try:
                await interaction.response.edit_message(
                    view=_text_view(msg(guild, "migrating", bot=name)))
            except discord.HTTPException:
                pass

            session = getattr(self, "_session", None)
            if session is None or session.closed:
                session = self._session = aiohttp.ClientSession(
                    headers={"User-Agent": "NikoBot (https://niko.sryze.cc)"})

            try:
                rows = await fetch_leaderboard(guild.id, provider, session)
                imported, skipped = await self._apply_import(
                    guild.id, rows, cumulative=PROVIDERS[provider]["cumulative_xp"])
            except LeaderboardUnavailable as error:
                log.info("LevelMigration", f"{name} leaderboard unavailable for {guild.id}: {error}")
                if PROVIDERS[provider].get("keyed") and error.status in (401, 403):
                    text = msg(guild, "failed_key", bot=name,
                               url=settings_url(guild.id))
                else:
                    text = msg(guild, "failed_unavailable", bot=name,
                               url=settings_url(guild.id))
            except Exception as error:
                log.warning("LevelMigration", f"{name} import failed for {guild.id}: {error}")
                text = msg(guild, "failed", error=str(error)[:300])
            else:
                text = msg(guild, "done", bot=name, imported=imported,
                           skipped=skipped, total=len(rows))
                log.info(
                    "LevelMigration",
                    f"Imported {imported} {name} rows into {guild.id} "
                    f"({skipped} already ahead, {len(rows)} read).",
                )

            try:
                await interaction.edit_original_response(view=_text_view(text))
            except discord.HTTPException:
                pass
        finally:
            self._running.discard(key)

    async def _apply_import(self, guild_id, rows: list, *, cumulative: bool) -> tuple:
        """Write imported rows into the ``levels`` table, keeping the best data."""
        leveling = self.bot.get_cog("Leveling")
        if leveling is None:
            raise RuntimeError("the leveling cog is not loaded")

        existing = {}
        stored = await self.bot.cxn.fetch(
            "SELECT * FROM levels WHERE guild_id = $1", int(guild_id))
        for row in stored or []:
            try:
                existing[int(row["user_id"])] = (int(row["level"]), int(row["xp"]))
            except (KeyError, IndexError, TypeError, ValueError):
                continue

        imported = skipped = 0
        for row in rows:
            level, xp = import_progress(
                row["level"], row["xp"],
                cumulative=cumulative, xp_for_level=leveling.get_xp_for_level,
            )
            if not imported_wins(level, xp, existing.get(row["user_id"])):
                skipped += 1
                continue
            await leveling._save_user_data(guild_id, row["user_id"], xp, level)
            imported += 1
        return imported, skipped


async def setup(bot: commands.Bot):
    await bot.add_cog(LevelMigration(bot))
