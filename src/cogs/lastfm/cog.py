"""Last.fm — the ``/fm`` listening commands.

Discord only reports Spotify as a rich presence, and only for members who have
connected Spotify to Discord. Last.fm is the other half of that picture: a
member links their handle once and every scrobble counts, from any player, on
any device. This cog is Niko's version of the fmbot command set:

``/fm [member]``        what the member is playing right now
``/fm overview [m]``    library overview (top artists, albums and tracks)
``/fm artist <name>``   one artist, with the member's own playcount
``/fm album <a> - <b>`` one album, same shape
``/fm recent [member]`` now playing and the latest scrobbles
``/fm chart <kind>``    a ranked board for the chosen period
``/fm whoknows <name>`` who in this server listens to an artist
``/fm crowns [member]`` the artists a member holds the server crown for
``/fm taste <member>``  how much two members' libraries overlap
``/fm link``            link an account through last.fm's own approval page
``/fm unlink``          forget it
``/fm update``          index the member's top artists for the server boards

Cards are rendered by :mod:`utils.image.lastfm_card`; the API is behind
:class:`utils.lastfm.LastFmClient`; the account link and the guild artist index
live in :mod:`cogs.lastfm._store`.

Every card answer first puts an animated placeholder from the public site on
screen (``scripts/generate_lastfm_loading_cards.py``) and edits it into the
finished PNG, so a slow artwork download never leaves a bare "thinking" state.
Linking runs through last.fm's own approval flow (``/api/lastfm/link``): the
website proves ownership and stores the handle last.fm names, so a member never
types a username and a session key can never be attached to an account it was
not granted for.

The guild boards read the index rather than scanning every member: Last.fm has
no "who in this server" endpoint, and a Discord server can hold thousands of
members. A member's top artists are indexed whenever they use ``/fm``, and
``/fm update`` indexes a fuller slice in one go, so the boards fill in as the
server uses them.
"""

from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from config import links
from config.emojis import get_emoji
from utils import logging
from utils.command_ids import replace_refs
from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.image import lastfm_card
from utils.image.cards import release_card
from utils.image.economy_card import fetch_avatar_bytes
from utils.lastfm import PERIODS, LastFmClient, LastFmError, period_label
from utils.loading_cards import loading_card_url
from utils.locales import load_locales

from . import _store

CMDS = command_texts(__package__)

MESSAGES = load_locales(__package__, "lastfm")
#: The bot's own status emoji, so a notice reads like the rest of Niko instead of
#: carrying Discord's stock ❌/✅/⚙️/⏳. The catalogues keep the named tokens.
msg = make_flat_msg(MESSAGES, {
    "tick": get_emoji("tick"),
    "cross": get_emoji("cross"),
    "warning": get_emoji("warning"),
    "settings": get_emoji("settings"),
    "loading": get_emoji("loading"),
})

#: Last.fm's red, tuned for the graphite card. Discord's accent bar takes the
#: same colour so the message and its card read as one object.
ACCENT = discord.Colour(0xD8645C)

#: Image attachment names. The card URL in the MediaGallery is built from these,
#: so a re-render can replace the attachment without changing the view shape.
CARD_FILE = "lastfm.png"

#: Chart kinds and how many rows each one shows.
CHART_KINDS = {"artists": 10, "albums": 10, "tracks": 10}

#: The card shape each command waits on, and the generated placeholder it shows,
#: served from the public site. Keeping one per shape (not per command) means a
#: chart, a whoknows board and a taste comparison all wait on the same
#: silhouette — the chart GIF is a ten-row board, so the boards reuse it.
LOADING_CARD_FILES = {
    "nowplaying": "nowplaying.gif",
    "overview": "overview.gif",
    "chart": "chart.gif",
    "board": "chart.gif",
    "recent": "recent.gif",
    "detail": "detail.gif",
}

#: How long the animated placeholder stays up before the finished card may
#: replace it. Discord does not promise that two edits of one message are
#: applied in the order they were sent, so a render that beats this and fires
#: the finished card straight after the placeholder can have the two PATCHes
#: race — the card shows up and the loading placeholder lands on top of it. The
#: placeholder only exists to cover a slow render, so a fast one waits out the
#: remainder and the swap always reads loading → card.
PLACEHOLDER_MIN_SECONDS = 0.4


async def _wait(seconds: float) -> None:
    """Sleep, kept behind a seam so the placeholder timing stays testable."""
    await asyncio.sleep(seconds)


def _placeholder_posted_at(message) -> float | None:
    """When the loading message went up, on this process's monotonic clock.

    The message's ``created_at`` is derived from its snowflake, which runs on
    Discord's clock. The age it yields is clamped to the placeholder's own
    window, so clock skew can neither skip the wait nor stretch it into a
    stall, and a message from another process is no worse than an unknown one.
    """
    created = getattr(message, "created_at", None)
    if not isinstance(created, datetime):
        return None
    try:
        age = (datetime.now(timezone.utc) - created).total_seconds()
    except (TypeError, ValueError, OverflowError):
        return None
    return time.monotonic() - min(max(age, 0.0), PLACEHOLDER_MIN_SECONDS)


async def _hold_placeholder(posted_at: float | None) -> None:
    """Keep the placeholder up for its minimum time before the card replaces it."""
    if posted_at is None:
        return
    remaining = PLACEHOLDER_MIN_SECONDS - (time.monotonic() - posted_at)
    if remaining > 0:
        await _wait(remaining)


def _site_base() -> str:
    """The origin that serves the loading cards and hosts the linking flow."""
    origin = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")
    return origin or links.WEBSITE


def _loading_view(card: str) -> discord.ui.LayoutView | None:
    """The animated card-shaped placeholder for *card*, if one exists.

    The GIF's folder belongs in the URL base, not the file name: the hash is
    looked up from the file the site serves, so ``lastfm/<shape>.gif`` has to
    resolve to a real path or the ``?hash=`` anti-cache suffix is dropped.
    """
    file_name = LOADING_CARD_FILES.get(card)
    if file_name is None:
        return None
    view = discord.ui.LayoutView()
    view.add_item(
        discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=loading_card_url(
                        f"{_site_base()}/assets/loading-cards", f"lastfm/{file_name}"
                    )
                )
            ),
            accent_colour=ACCENT,
        )
    )
    return view

#: How many rows the overview lists per column.
OVERVIEW_ROWS = 5


def _ago(timestamp: float | int | None) -> str:
    """``just now``, ``4m ago``, ``3h ago``, ``6d ago`` for a unix timestamp."""
    try:
        seconds = max(0, int(datetime.now(timezone.utc).timestamp() - float(timestamp or 0)))
    except (TypeError, ValueError):
        return ""
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    if seconds < 86400 * 30:
        return f"{seconds // 86400}d ago"
    if seconds < 86400 * 365:
        return f"{seconds // (86400 * 30)}mo ago"
    return f"{seconds // (86400 * 365)}y ago"


def _month_year(timestamp: float | int | None) -> str:
    try:
        return datetime.fromtimestamp(float(timestamp), tz=timezone.utc).strftime("%B %Y")
    except (TypeError, ValueError, OSError):
        return ""


def _action_row(*items) -> discord.ui.ActionRow:
    """A Components-V2 action row holding the given items."""
    return discord.ui.ActionRow(*items)


class LastfmPeriodSelect(discord.ui.Select):
    """Switches the period a card is rendered for, in place."""

    def __init__(self, cog: "LastfmCog", member: discord.abc.User, kind: str, current: str):
        options = [
            discord.SelectOption(
                label=period_label(period),
                value=period,
                default=period == current,
            )
            for period in PERIODS
        ]
        super().__init__(placeholder="Change the time period", options=options, row=0)
        self.cog = cog
        self.member = member
        self.kind = kind

    async def callback(self, interaction: discord.Interaction):
        period = self.values[0]
        await interaction.response.defer()
        # A period change re-reads the library, which is the slow path this
        # placeholder exists for; the shape stays the same, so it does not jump.
        preview = _loading_view("overview" if self.kind == "overview" else "chart")
        posted_at = time.monotonic()
        if preview is not None:
            try:
                await interaction.edit_original_response(view=preview)
            except Exception:
                posted_at = None
        try:
            view, file = await self.cog.render_card(self.kind, self.member, period)
        except LastFmError as exc:
            await _hold_placeholder(posted_at)
            return await interaction.edit_original_response(
                view=self.cog.error_view(interaction, exc, kind="account"), attachments=[]
            )
        except Exception as exc:  # never leave the member with a dead button
            logging.error("Last.fm", f"Period re-render failed: {exc}")
            await _hold_placeholder(posted_at)
            return await interaction.edit_original_response(
                view=self.cog.error_view(interaction, exc), attachments=[]
            )
        await _hold_placeholder(posted_at)
        try:
            await interaction.edit_original_response(view=view, attachments=[file])
        finally:
            # The re-rendered card is not kept: only the message on Discord is.
            release_card(file)


class LastfmCog(commands.Cog):
    """Last.fm listening, cards and per-server leaderboards."""

    def __init__(self, bot):
        self.bot = bot
        self.client = LastFmClient(
            os.environ.get("LASTFM_API_KEY", ""),
            # The shared secret is only needed to exchange a web-auth approval for
            # a session key; every read command works without it.
            api_secret=os.environ.get("LASTFM_API_SECRET", ""),
        )

    async def cog_unload(self):
        await self.client.close()

    # ── shared plumbing ───────────────────────────────────────────────

    def _layout(self, *rows, accent: discord.Colour = ACCENT) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView(timeout=300)
        view.add_item(discord.ui.Container(*rows, accent_colour=accent))
        return view

    def notice_view(self, text: str, *, accent: discord.Colour = ACCENT) -> discord.ui.LayoutView:
        """A notice in the member's language, with command references as chips.

        The catalogues keep writing ``/fm chart`` because a translator should
        see a command name, not a snowflake; this is where that turns into a
        clickable ``</fm chart:id>``. Anything the member reads in a card is
        drawn into a PNG and never comes through here.
        """
        return self._layout(discord.ui.TextDisplay(content=replace_refs(text)), accent=accent)

    #: Last.fm answers "unknown" (code 6) for a bad handle and for a bad artist
    #: or album name alike, so the copy follows what the member actually asked
    #: for — the way to fix each one is different.
    _UNKNOWN_KEYS = {
        "account": "err_unknown_account",
        "artist": "err_unknown_artist",
        "album": "err_unknown_album",
    }

    def error_view(
        self, ctx, exc: Exception, *, kind: str = ""
    ) -> discord.ui.LayoutView:
        """A readable notice for a Last.fm failure, in the member's language.

        ``kind`` names what was asked for (``account``, ``artist``, ``album``) so
        an unknown answer can point at the one thing that fixes it. Last.fm's own
        reply is logged rather than printed: a member cannot act on a status code
        and a socket error reads as the bot's fault, while the log is the only
        place either detail would otherwise survive.
        """
        if not isinstance(exc, LastFmError):
            logging.error("Last.fm", f"Unexpected failure: {exc!r}")
            key = "err_unexpected"
        elif not self.client.has_key:
            key = "err_not_configured"
        elif exc.bad_key:
            key = "err_key"
            logging.warning("Last.fm", f"API key rejected: {exc.message}")
        elif exc.rate_limited:
            key = "err_busy"
        elif exc.unknown_user:
            key = self._UNKNOWN_KEYS.get(kind, "err_unknown")
        elif exc.code is None:
            # No code means the request never got an answer: a socket error, a
            # 5xx, or a body Last.fm did not mean to send. All worth a retry.
            key = "err_unreachable"
            logging.warning("Last.fm", f"No answer: {exc.message}")
        else:
            key = "err_generic"
            logging.warning("Last.fm", f"Refused (code {exc.code}): {exc.message}")
        return self.notice_view(msg(ctx, key), accent=discord.Colour(0xB4544C))

    async def _start(self, ctx, card: str | None = None):
        """Defer a slash command and put the animated placeholder on screen.

        Returns the placeholder message (a prefix command edits it into the
        finished card); a slash command has no message to hand back because
        ``edit_original_response`` already targets the deferred reply.
        """
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.interaction.response.defer()
        if not card:
            return None
        view = _loading_view(card)
        if view is None:
            return None
        try:
            if ctx.interaction:
                return await ctx.interaction.edit_original_response(view=view)
            return await ctx.send(view=view)
        except Exception as exc:  # never block the real card on a placeholder
            logging.warning("Last.fm", f"Loading card failed: {exc}")
            return None

    async def _reply(
        self,
        ctx,
        view: discord.ui.LayoutView,
        file: discord.File | None = None,
        *,
        message=None,
    ):
        """Deliver a card, editing the placeholder when there is one.

        A slash command edits its original response for both halves of the swap.
        Editing the placeholder message by id and then the card through
        ``edit_original_response`` would be two different routes into the same
        message, and the older of the two can be applied last; one route keeps
        the swap in order.

        The card's PNG is released once Discord has it: every listing is drawn
        for one reply, and a 980px card is several megabytes to keep alive until
        a garbage collection happens to run.
        """
        try:
            if message is not None:
                # The placeholder has to be on screen before the card may replace
                # it; see PLACEHOLDER_MIN_SECONDS for why the two edits cannot be
                # fired back to back.
                await _hold_placeholder(_placeholder_posted_at(message))
            if ctx.interaction is not None:
                if not ctx.interaction.response.is_done():
                    await ctx.interaction.response.defer()
                kwargs = {"view": view}
                if file is not None:
                    kwargs["attachments"] = [file]
                return await ctx.interaction.edit_original_response(**kwargs)
            if message is not None:
                return await message.edit(
                    view=view, attachments=[file] if file is not None else []
                )
            kwargs = {"view": view}
            if file is not None:
                kwargs["file"] = file
            return await ctx.send(**kwargs)
        finally:
            release_card(file)

    async def _progress(self, ctx, text: str):
        """Put a text notice on screen now and hand it back for editing.

        ``/fm update`` reads two pages of Last.fm before it can answer anything,
        so the notice goes up the moment the command is pressed and that same
        message becomes the result. A slash command answers with the notice
        rather than deferring, because a deferral leaves the reply blank until
        the crawl is already over — the member sees nothing happen.
        """
        view = self.notice_view(text)
        try:
            if ctx.interaction is not None:
                if ctx.interaction.response.is_done():
                    return await ctx.interaction.edit_original_response(view=view)
                return await ctx.interaction.response.send_message(view=view)
            return await ctx.send(view=view)
        except Exception as exc:  # a missing notice must never stop the update
            logging.warning("Last.fm", f"Progress notice failed: {exc}")
            return None

    async def _fetch_art(self, urls: list[str | None]) -> list[bytes | None]:
        """Download several artworks at once; failures become ``None``."""
        return list(await asyncio.gather(*(fetch_avatar_bytes(url, size=300) for url in urls)))

    def _period_select(self, member, kind: str, period: str) -> LastfmPeriodSelect:
        return LastfmPeriodSelect(self, member, kind, period)

    def _link_view(self, ctx, handle: str | None = None) -> discord.ui.LayoutView:
        """The offer to link through last.fm's own approval page.

        Needs the application's shared secret, which is what lets the website
        exchange the approval for a session key; without it there is no way to
        prove a handle, so the member is told linking is unavailable.

        ``handle`` is the account already linked, if any: the same button then
        reads as a reconnect and the message says which account it would replace,
        so nobody has to guess whether they are linked or press to find out.
        """
        if not self.client.has_secret:
            return self.notice_view(msg(ctx, "link_unavailable"))
        linked = bool(handle)
        title = msg(ctx, "link_linked_title" if linked else "link_title")
        body = (
            msg(ctx, "link_linked", handle=handle)
            if linked
            else msg(ctx, "link_prompt")
        )
        return self._layout(
            discord.ui.TextDisplay(content=title),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=replace_refs(body)),
            _action_row(
                discord.ui.Button(
                    label=msg(ctx, "reconnect_button" if linked else "connect_button"),
                    style=discord.ButtonStyle.link,
                    url=f"{_site_base()}/api/lastfm/link",
                    emoji=get_emoji("lastfm"),
                )
            ),
        )

    # ── card renderers ────────────────────────────────────────────────

    async def render_card(self, kind: str, member, period: str = "overall"):
        """Render the overview or a chart for *member* and *period*.

        Returns ``(view, file)`` so both the first reply and the period picker
        deliver the card the same way.
        """
        if not self.client.has_key:
            raise LastFmError("Last.fm is not configured on this bot.")
        handle = await _store.get_account(self.bot.cxn, member.id)
        if not handle:
            raise LastFmError("That member has not linked a Last.fm account.", code=6)

        if kind == "overview":
            return await self._overview(member, handle, period)
        if kind in CHART_KINDS:
            return await self._chart(member, handle, kind, period)
        raise ValueError(f"Unknown Last.fm card kind: {kind!r}")

    async def _overview(self, member, handle: str, period: str):
        info, recent = await asyncio.gather(
            self.client.user_info(handle),
            self.client.recent_tracks(handle, limit=1),
        )
        artists, albums, tracks = await asyncio.gather(
            self.client.top_artists(handle, period=period, limit=OVERVIEW_ROWS),
            self.client.top_albums(handle, period=period, limit=OVERVIEW_ROWS),
            self.client.top_tracks(handle, period=period, limit=OVERVIEW_ROWS),
        )

        # The visible top artists are the cheapest, most honest index update
        # there is: the member already paid for this request.
        await self._index(member, artists)
        await self._maybe_refresh_account(member.id, handle, info)

        avatar = await fetch_avatar_bytes(member.display_avatar.url, size=256)
        buf = await lastfm_card.render_overview_card(
            avatar_bytes=avatar,
            display_name=member.display_name,
            handle=f"@{info['username']}",
            period=period_label(period),
            scrobbles=info["playcount"],
            artists=[
                {"rank": index + 1, "name": row["name"], "value": _compact(row["playcount"])}
                for index, row in enumerate(artists)
            ],
            albums=[
                {"rank": index + 1, "name": row["name"], "subtitle": row["artist"], "value": _compact(row["playcount"])}
                for index, row in enumerate(albums)
            ],
            tracks=[
                {"rank": index + 1, "name": row["name"], "subtitle": row["artist"], "value": _compact(row["playcount"])}
                for index, row in enumerate(tracks)
            ],
            member_since=(
                f"member since {_month_year(info['registered'])}" if info["registered"] else ""
            ),
            now_playing=recent.get("now_playing"),
            footer=f"{info['artist_count']:,} artists · {info['track_count']:,} tracks · last.fm/user/{info['username']}",
            empty_text="No scrobbles in this period.",
        )

        buttons = []
        if info.get("url"):
            buttons.append(
                discord.ui.Button(
                    label=msg(None, "open_profile"),
                    style=discord.ButtonStyle.link,
                    url=info["url"],
                )
            )
        # A select has to be alone in its action row, so the period picker and
        # the profile button are separate rows.
        rows = [
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=f"attachment://{CARD_FILE}")
            ),
            discord.ui.Separator(visible=True),
            _action_row(self._period_select(member, "overview", period)),
        ]
        if buttons:
            rows.append(_action_row(*buttons))
        return self._layout(*rows), discord.File(buf, CARD_FILE)

    async def _chart(self, member, handle: str, kind: str, period: str):
        limit = CHART_KINDS[kind]
        if kind == "artists":
            rows = await self.client.top_artists(handle, period=period, limit=limit)
            await self._index(member, rows)
        elif kind == "albums":
            rows = await self.client.top_albums(handle, period=period, limit=limit)
        else:
            rows = await self.client.top_tracks(handle, period=period, limit=limit)

        images = await self._fetch_art([row.get("image") for row in rows])
        entries = []
        for index, row in enumerate(rows):
            subtitle = row.get("artist") or ""
            entries.append({
                "rank": index + 1,
                "name": row["name"],
                "subtitle": subtitle,
                "value": _compact(row["playcount"]),
                "bar": row["playcount"],
                "image": images[index] if index < len(images) else None,
            })

        title = {
            "artists": msg(None, "chart_artists"),
            "albums": msg(None, "chart_albums"),
            "tracks": msg(None, "chart_tracks"),
        }[kind]
        buf = await lastfm_card.render_board_card(
            title=f"{member.display_name} — {title}",
            subtitle=period_label(period),
            entries=entries,
            footer=msg(None, "index_hint"),
            empty_text=msg(None, "chart_empty"),
            value_label=msg(None, "plays_label"),
            show_images=True,
        )
        rows_view = [
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=f"attachment://{CARD_FILE}")
            ),
            discord.ui.Separator(visible=True),
            _action_row(self._period_select(member, kind, period)),
        ]
        return self._layout(*rows_view), discord.File(buf, CARD_FILE)

    # ── index maintenance ─────────────────────────────────────────────

    async def _index(self, member, rows: list[dict], *, limit: int = _store.INDEX_BATCH) -> None:
        """Record a member's artist playcounts for this server's boards."""
        guild = getattr(member, "guild", None)
        if guild is None or not rows:
            return
        try:
            await _store.index_artists(
                self.bot.cxn,
                guild.id,
                member.id,
                [(row["name"], row.get("playcount") or 0) for row in rows if row.get("name")],
                limit=limit,
            )
        except Exception as exc:
            # The card in front of the member does not depend on the index.
            logging.warning("Last.fm", f"Artist index write failed: {exc}")

    async def _maybe_refresh_account(self, user_id: int, handle: str, info: dict) -> None:
        """Note that a linked handle still resolves, at most once a day."""
        try:
            row = await _store.get_account_row(self.bot.cxn, user_id)
            if row and info and (row.get("checked_at") or 0) > _store.now() - 86400:
                return
            await _store.touch_account(self.bot.cxn, user_id)
        except Exception as exc:
            logging.warning("Last.fm", f"Account touch failed: {exc}")

    # ── commands ──────────────────────────────────────────────────────

    @commands.hybrid_group(
        name="fm",
        description=CMDS.text("fm.description"),
        help=CMDS.help("fm"),
        invoke_without_command=True,
    )
    @app_commands.describe(member=CMDS.arg("fm", "member"))
    async def fm(self, ctx, member: discord.Member = None):
        """What you are playing on Last.fm right now."""
        # Discord does not register a group that has subcommands as a slash
        # command, so this body is the prefix ``.fm``; ``/fm nowplaying`` is the
        # same card for everyone who only uses slash commands.
        await self._now_playing(ctx, member or ctx.author)

    @fm.command(name="nowplaying", description=CMDS.text("fm.nowplaying.description"))
    @app_commands.describe(member=CMDS.arg("fm.nowplaying", "member"))
    async def fm_nowplaying(self, ctx, member: discord.Member = None):
        """What a member is playing on Last.fm right now."""
        await self._now_playing(ctx, member or ctx.author)

    @fm.command(name="overview", description=CMDS.text("fm.overview.description"))
    @app_commands.describe(member=CMDS.arg("fm.overview", "member"))
    async def fm_overview(self, ctx, member: discord.Member = None):
        """Your library at a glance — top artists, albums and tracks."""
        target = member or ctx.author
        loading = await self._start(ctx, "overview")

        if not self.client.has_key:
            return await self._reply(
                ctx, self.error_view(ctx, LastFmError("missing key")), message=loading
            )
        handle = await _store.get_account(self.bot.cxn, target.id)
        if not handle:
            return await self._reply(
                ctx,
                self.notice_view(msg(ctx, "not_linked", user=target.display_name, cmd=msg(ctx, "fm_link_usage"))),
                message=loading,
            )
        try:
            view, file = await self.render_card("overview", target, "overall")
        except LastFmError as exc:
            return await self._reply(
                ctx, self.error_view(ctx, exc, kind="account"), message=loading
            )
        await self._reply(ctx, view, file, message=loading)

    async def _now_playing(self, ctx, target) -> None:
        """The large now-playing card, falling back to the last scrobble."""
        loading = await self._start(ctx, "nowplaying")
        if not self.client.has_key:
            return await self._reply(
                ctx, self.error_view(ctx, LastFmError("missing key")), message=loading
            )
        handle = await _store.get_account(self.bot.cxn, target.id)
        if not handle:
            return await self._reply(
                ctx,
                self.notice_view(msg(ctx, "not_linked", user=target.display_name, cmd=msg(ctx, "fm_link_usage"))),
                message=loading,
            )
        try:
            data = await self.client.recent_tracks(handle, limit=1)
        except LastFmError as exc:
            return await self._reply(
                ctx, self.error_view(ctx, exc, kind="account"), message=loading
            )

        live = bool(data.get("now_playing"))
        track = data.get("now_playing") or (data["tracks"][0] if data["tracks"] else None)
        image = await fetch_avatar_bytes(track.get("image"), size=420) if track else None

        if track is None:
            footer = msg(ctx, "nowplaying_footer", name=target.display_name, handle=handle)
        elif live:
            footer = msg(ctx, "nowplaying_live", name=target.display_name, handle=handle)
        else:
            footer = msg(
                ctx,
                "nowplaying_last",
                name=target.display_name,
                when=_ago(track.get("played_at")),
            )
        buf = await lastfm_card.render_now_playing_card(
            image_bytes=image,
            title=track["title"] if track else "",
            artist=track.get("artist", "") if track else "",
            album=track.get("album", "") if track else "",
            live=live,
            handle=handle,
            footer=footer,
            empty_text=msg(None, "nowplaying_empty"),
            now_label=msg(None, "now_playing"),
            last_label=msg(None, "last_played"),
        )
        rows = [
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=f"attachment://{CARD_FILE}")
            )
        ]
        if track and track.get("url"):
            rows.extend(
                [
                    discord.ui.Separator(visible=True),
                    _action_row(
                        discord.ui.Button(
                            label=msg(None, "open_track"),
                            style=discord.ButtonStyle.link,
                            url=track["url"],
                        )
                    ),
                ]
            )
        await self._reply(
            ctx, self._layout(*rows), discord.File(buf, CARD_FILE), message=loading
        )

    @fm.command(name="artist", description=CMDS.text("fm.artist.description"))
    @app_commands.describe(artist=CMDS.arg("fm.artist", "artist"))
    async def fm_artist(self, ctx, *, artist: str = None):
        """One artist on Last.fm, with your own playcount."""
        loading = await self._start(ctx, "detail")
        if not artist:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_artist")), message=loading)
        handle = await _store.get_account(self.bot.cxn, ctx.author.id)
        if not handle:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_link_self", cmd=msg(ctx, "fm_link_usage"))), message=loading)
        try:
            info = await self.client.artist_info(artist, handle)
        except LastFmError as exc:
            return await self._reply(
                ctx, self.error_view(ctx, exc, kind="artist"), message=loading
            )

        if ctx.guild is not None and info.get("user_playcount") is not None:
            try:
                await _store.index_artists(
                    self.bot.cxn, ctx.guild.id, ctx.author.id,
                    [(info["name"], int(info["user_playcount"]))],
                )
            except Exception as exc:
                logging.warning("Last.fm", f"Artist index write failed: {exc}")

        art = await fetch_avatar_bytes(info.get("image"), size=420)
        buf = await lastfm_card.render_detail_card(
            image_bytes=art,
            kind="Artist",
            title=info["name"],
            subtitle=", ".join(info.get("tags") or []) or "artist",
            playcount=info.get("user_playcount"),
            chips=[
                ("listeners", _compact(info.get("listeners") or 0)),
                ("scrobbles", _compact(info.get("playcount") or 0)),
            ],
            footer=(
                f"your plays · last.fm/music/{info['name'].replace(' ', '+')}"
                if info.get("user_playcount") is not None
                else "last.fm"
            ),
            plays_label=msg(None, "plays_label"),
        )
        buttons = []
        if info.get("url"):
            buttons.append(
                discord.ui.Button(
                    label=msg(None, "open_artist"),
                    style=discord.ButtonStyle.link,
                    url=info["url"],
                )
            )
        view = self._layout(
            discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://{CARD_FILE}")),
            discord.ui.Separator(visible=True),
            _action_row(*buttons) if buttons else discord.ui.TextDisplay(content="-# last.fm"),
        )
        await self._reply(ctx, view, discord.File(buf, CARD_FILE), message=loading)

    @fm.command(name="album", description=CMDS.text("fm.album.description"))
    @app_commands.describe(album=CMDS.arg("fm.album", "album"))
    async def fm_album(self, ctx, *, album: str = None):
        """One album on Last.fm, with your own playcount. Use `Artist - Album`."""
        loading = await self._start(ctx, "detail")
        if not album or " - " not in album:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_album")), message=loading)
        artist, name = (part.strip() for part in album.split(" - ", 1))
        handle = await _store.get_account(self.bot.cxn, ctx.author.id)
        if not handle:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_link_self", cmd=msg(ctx, "fm_link_usage"))), message=loading)
        try:
            info = await self.client.album_info(artist, name, handle)
        except LastFmError as exc:
            return await self._reply(
                ctx, self.error_view(ctx, exc, kind="album"), message=loading
            )

        art = await fetch_avatar_bytes(info.get("image"), size=420)
        chips = [("listeners", _compact(info.get("listeners") or 0))]
        if info.get("track_count"):
            chips.append(("tracks", str(info["track_count"])))
        buf = await lastfm_card.render_detail_card(
            image_bytes=art,
            kind="Album",
            title=info["name"],
            subtitle=info.get("artist") or artist,
            playcount=info.get("user_playcount"),
            chips=chips,
            footer=f"your plays · album by {info.get('artist') or artist}",
            plays_label=msg(None, "plays_label"),
        )
        buttons = []
        if info.get("url"):
            buttons.append(
                discord.ui.Button(
                    label=msg(None, "open_album"),
                    style=discord.ButtonStyle.link,
                    url=info["url"],
                )
            )
        view = self._layout(
            discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://{CARD_FILE}")),
            discord.ui.Separator(visible=True),
            _action_row(*buttons) if buttons else discord.ui.TextDisplay(content="-# last.fm"),
        )
        await self._reply(ctx, view, discord.File(buf, CARD_FILE), message=loading)

    @fm.command(name="recent", description=CMDS.text("fm.recent.description"))
    @app_commands.describe(member=CMDS.arg("fm.recent", "member"))
    async def fm_recent(self, ctx, member: discord.Member = None):
        """What a member is playing right now, and their last scrobbles."""
        loading = await self._start(ctx, "recent")
        target = member or ctx.author
        handle = await _store.get_account(self.bot.cxn, target.id)
        if not handle:
            return await self._reply(
                ctx,
                self.notice_view(msg(ctx, "not_linked", user=target.display_name, cmd=msg(ctx, "fm_link_usage"))),
                message=loading,
            )
        try:
            data = await self.client.recent_tracks(handle, limit=10)
        except LastFmError as exc:
            return await self._reply(
                ctx, self.error_view(ctx, exc, kind="account"), message=loading
            )

        entries = []
        if data.get("now_playing"):
            entries.append({
                "title": data["now_playing"]["title"],
                "subtitle": data["now_playing"]["artist"],
                "when": "now",
                "now_playing": True,
                "image": data["now_playing"].get("image"),
            })
        for row in data["tracks"]:
            entries.append({
                "title": row["title"],
                "subtitle": row["artist"],
                "when": _ago(row["played_at"]),
                "image": row.get("image"),
            })

        # A scrobble list without sleeves is just a list of names, so the
        # artwork is downloaded before the card is drawn — the same way the
        # charts fetch theirs.
        entries = entries[:11]
        images = await self._fetch_art([entry.pop("image", None) for entry in entries])
        for entry, artwork in zip(entries, images):
            entry["image"] = artwork

        avatar = await fetch_avatar_bytes(target.display_avatar.url, size=256)
        buf = await lastfm_card.render_recent_card(
            avatar_bytes=avatar,
            display_name=target.display_name,
            handle=f"@{handle}",
            entries=entries,
            footer=f"last.fm/user/{handle} · {data.get('total', 0):,} scrobbles",
            empty_text=msg(None, "recent_empty"),
            now_label=msg(None, "now_playing"),
        )
        view = self._layout(
            discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://{CARD_FILE}")),
            accent=ACCENT,
        )
        await self._reply(ctx, view, discord.File(buf, CARD_FILE), message=loading)

    @fm.command(name="chart", description=CMDS.text("fm.chart.description"))
    @app_commands.describe(
        kind=CMDS.arg("fm.chart", "kind"),
        member=CMDS.arg("fm.chart", "member"),
    )
    async def fm_chart(self, ctx, kind: str = "artists", member: discord.Member = None):
        """Your top artists, albums or tracks for the chosen period."""
        loading = await self._start(ctx, "chart")
        kind = (kind or "artists").strip().lower().rstrip("s") + "s"
        if kind not in CHART_KINDS:
            return await self._reply(
                ctx, self.notice_view(msg(ctx, "chart_usage")), message=loading
            )
        target = member or ctx.author
        handle = await _store.get_account(self.bot.cxn, target.id)
        if not handle:
            return await self._reply(
                ctx,
                self.notice_view(msg(ctx, "not_linked", user=target.display_name, cmd=msg(ctx, "fm_link_usage"))),
                message=loading,
            )
        try:
            view, file = await self.render_card(kind, target, "overall")
        except LastFmError as exc:
            return await self._reply(
                ctx, self.error_view(ctx, exc, kind="account"), message=loading
            )
        await self._reply(ctx, view, file, message=loading)

    @fm.command(name="whoknows", description=CMDS.text("fm.whoknows.description"))
    @app_commands.describe(artist=CMDS.arg("fm.whoknows", "artist"))
    async def fm_whoknows(self, ctx, *, artist: str = None):
        """Who in this server listens to an artist, and how much."""
        loading = await self._start(ctx, "board")
        if not artist:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_artist")), message=loading)
        if ctx.guild is None:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_guild")), message=loading)

        # The member's own number is refreshed first: they are the one asking,
        # and their row is the one most likely to be missing.
        handle = await _store.get_account(self.bot.cxn, ctx.author.id)
        if handle:
            try:
                info = await self.client.artist_info(artist, handle)
                await _store.index_artists(
                    self.bot.cxn, ctx.guild.id, ctx.author.id,
                    [(info["name"], int(info.get("user_playcount") or 0))],
                )
                artist = info["name"] or artist
            except LastFmError:
                pass  # the board below still answers from the index

        rows = await _store.artist_listeners(self.bot.cxn, ctx.guild.id, artist)
        members = []
        for row in rows:
            member = ctx.guild.get_member(int(row["user_id"]))
            members.append((member, row))

        avatars = await asyncio.gather(
            *(
                fetch_avatar_bytes(member.display_avatar.url, size=128) if member else _no_avatar()
                for member, _ in members
            )
        )
        entries = []
        for index, ((member, row), avatar) in enumerate(zip(members, avatars)):
            entries.append({
                "rank": index + 1,
                "name": member.display_name if member else f"member {row['user_id']}",
                "subtitle": f"{_ago(row.get('updated_at'))}",
                "value": _compact(row["playcount"]),
                "bar": row["playcount"],
                "avatar": avatar,
            })

        buf = await lastfm_card.render_board_card(
            title=msg(None, "whoknows_title", artist=artist),
            subtitle=msg(None, "whoknows_subtitle", count=len(entries)),
            entries=entries,
            footer=msg(None, "whoknows_footer"),
            empty_text=msg(None, "whoknows_empty"),
            value_label=msg(None, "plays_label"),
            show_images=False,
        )
        view = self._layout(
            discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://{CARD_FILE}")),
        )
        await self._reply(ctx, view, discord.File(buf, CARD_FILE), message=loading)

    @fm.command(name="crowns", description=CMDS.text("fm.crowns.description"))
    @app_commands.describe(member=CMDS.arg("fm.crowns", "member"))
    async def fm_crowns(self, ctx, member: discord.Member = None):
        """The artists a member listens to more than anyone else here."""
        loading = await self._start(ctx, "board")
        if ctx.guild is None:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_guild")), message=loading)
        target = member or ctx.author

        rows = await _store.guild_index(self.bot.cxn, ctx.guild.id)
        held = _store.crowns(rows)
        crowns = held.get(target.id, [])
        entries = []
        for index, crown in enumerate(crowns[:12]):
            rival = ctx.guild.get_member(crown["runner_up_id"])
            entries.append({
                "rank": index + 1,
                "name": crown["artist"],
                "subtitle": msg(
                    None,
                    "crowns_subtitle",
                    rival=rival.display_name if rival else "someone",
                    gap=crown["lead"],
                ),
                "value": _compact(crown["plays"]),
                "bar": crown["plays"],
            })

        buf = await lastfm_card.render_board_card(
            title=msg(None, "crowns_title", user=target.display_name, count=len(crowns)),
            subtitle=msg(None, "crowns_subtitle_line", ranked=len(held)),
            entries=entries,
            footer=msg(None, "index_hint"),
            empty_text=msg(None, "crowns_empty"),
            value_label=msg(None, "plays_label"),
            show_images=False,
        )
        view = self._layout(
            discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://{CARD_FILE}")),
        )
        await self._reply(ctx, view, discord.File(buf, CARD_FILE), message=loading)

    @fm.command(name="taste", description=CMDS.text("fm.taste.description"))
    @app_commands.describe(member=CMDS.arg("fm.taste", "member"))
    async def fm_taste(self, ctx, member: discord.Member = None):
        """How closely two members' listening overlaps."""
        loading = await self._start(ctx, "board")
        target = member or ctx.author
        if target.id == ctx.author.id:
            return await self._reply(ctx, self.notice_view(msg(ctx, "taste_self")), message=loading)
        mine = await _store.get_account(self.bot.cxn, ctx.author.id)
        theirs = await _store.get_account(self.bot.cxn, target.id)
        if not mine:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_link_self", cmd=msg(ctx, "fm_link_usage"))), message=loading)
        if not theirs:
            return await self._reply(
                ctx, self.notice_view(msg(ctx, "not_linked", user=target.display_name, cmd=msg(ctx, "fm_link_usage"))), message=loading,
            )

        try:
            my_artists, their_artists = await asyncio.gather(
                self.client.top_artists(mine, period="overall", limit=50),
                self.client.top_artists(theirs, period="overall", limit=50),
            )
        except LastFmError as exc:
            return await self._reply(
                ctx, self.error_view(ctx, exc, kind="account"), message=loading
            )

        my_counts = {_store.artist_key(row["name"]): row["playcount"] for row in my_artists}
        their_counts = {_store.artist_key(row["name"]): row["playcount"] for row in their_artists}
        shared = set(my_counts) & set(their_counts)
        union = set(my_counts) | set(their_counts)
        overlap = (
            sum(min(my_counts[key], their_counts[key]) for key in union) / max(1, sum(max(my_counts.get(key, 0), their_counts.get(key, 0)) for key in union))
        )
        score = int(round(overlap * 100))

        rows = [
            {
                "name": row["name"],
                "plays": my_counts.get(_store.artist_key(row["name"]), 0),
                "their_plays": their_counts[_store.artist_key(row["name"])],
            }
            for row in my_artists
            if _store.artist_key(row["name"]) in shared
        ]
        rows.sort(key=lambda item: -(item["plays"] + item["their_plays"]))
        entries = [
            {
                "rank": index + 1,
                "name": item["name"],
                "subtitle": msg(
                    None, "taste_row", you=item["plays"], them=item["their_plays"]
                ),
                "value": f"{item['plays']}/{item['their_plays']}",
                "bar": item["plays"] + item["their_plays"],
            }
            for index, item in enumerate(rows[:10])
        ]

        buf = await lastfm_card.render_board_card(
            title=msg(None, "taste_title", score=score, user=target.display_name),
            subtitle=msg(None, "taste_subtitle", mine=ctx.author.display_name, theirs=target.display_name),
            entries=entries,
            footer=msg(None, "taste_footer", count=len(shared)),
            empty_text=msg(None, "taste_empty"),
            value_label="you / them",
            show_images=False,
        )
        view = self._layout(
            discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://{CARD_FILE}")),
        )
        await self._reply(ctx, view, discord.File(buf, CARD_FILE), message=loading)

    @fm.command(name="link", description=CMDS.text("fm.link.description"))
    async def fm_link(self, ctx):
        """Link your Last.fm account so the listening commands work.

        Last.fm asks the member to approve the application, so the handle is
        proven rather than typed — which is also why this takes no username.
        """
        await self._start(ctx)
        handle = await _store.get_account(self.bot.cxn, ctx.author.id)
        await self._reply(ctx, self._link_view(ctx, handle))

    @fm.command(name="unlink", description=CMDS.text("fm.unlink.description"))
    async def fm_unlink(self, ctx):
        """Unlink your Last.fm account from Niko."""
        await self._start(ctx)
        handle = await _store.get_account(self.bot.cxn, ctx.author.id)
        if not handle:
            # Nothing to delete: answering "unlinked" would claim a change that
            # never happened, and the member would have no idea why the cards
            # still say they are not linked.
            return await self._reply(
                ctx, self.notice_view(msg(ctx, "no_account_to_unlink"))
            )
        await _store.remove_account(self.bot.cxn, ctx.author.id)
        await self._reply(ctx, self.notice_view(msg(ctx, "unlinked", handle=handle)))

    @fm.command(name="update", description=CMDS.text("fm.update.description"))
    async def fm_update(self, ctx):
        """Index more of your library so the server leaderboards include you."""
        # The two cheap checks happen before anything is drawn: a member who
        # cannot run the crawl should not see an "indexing" notice at all.
        if ctx.guild is None:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_guild")))
        handle = await _store.get_account(self.bot.cxn, ctx.author.id)
        if not handle:
            return await self._reply(ctx, self.notice_view(msg(ctx, "need_link_self", cmd=msg(ctx, "fm_link_usage"))))

        # Two pages of a hundred artists is a Last.fm round trip each, so the
        # notice goes up first and the same message is edited into the result.
        progress = await self._progress(ctx, msg(ctx, "indexing"))
        indexed = 0
        checked = 0
        try:
            for page in (1, 2):
                rows = await self.client.top_artists(handle, period="overall", limit=100, page=page)
                if not rows:
                    break
                checked += len(rows)
                indexed += await _store.index_artists(
                    self.bot.cxn,
                    ctx.guild.id,
                    ctx.author.id,
                    [(row["name"], row["playcount"]) for row in rows],
                    limit=100,
                )
        except LastFmError as exc:
            # A half-finished crawl keeps the rows it already wrote; the log says
            # how far it got, and the notice is the ordinary readable error.
            if indexed:
                logging.warning("Last.fm", f"Update stopped after {indexed} artists: {exc.message}")
            return await self._reply(
                ctx, self.error_view(ctx, exc, kind="account"), message=progress
            )

        # ``indexed`` counts rows written, which is zero on a repeat run because
        # the index only ever rises. "Indexed 0 artists" read as a failure, so
        # the three answers say which of the three things actually happened:
        # nothing to read, nothing new, or this many rows raised.
        if not checked:
            text = msg(ctx, "indexed_empty", handle=handle)
        elif indexed:
            text = msg(ctx, "indexed", count=indexed, handle=handle)
        else:
            text = msg(ctx, "indexed_uptodate", count=checked, handle=handle)
        await self._reply(ctx, self.notice_view(text), message=progress)


async def _no_avatar() -> None:
    return None


def _compact(value) -> str:
    """A short number for a card column (``1.2K``, ``3.45M``)."""
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        return "0"
    if abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    if abs(number) >= 10_000:
        return f"{number / 1_000:.0f}K"
    return f"{number:,}"


async def setup(bot):
    await bot.add_cog(LastfmCog(bot))
