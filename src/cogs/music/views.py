"""
Music System — Now-Playing control panel.

Interactive component classes only (the panel is the primary interactive
surface of the music feature):

  Row 1: Prev · Pause/Resume · Skip · Stop · Like
  Row 2: Loop · Autoplay · Queue · Vol − · Vol +

All shared utilities (constants, formatting, messages, Spotify, Last.fm,
Lavalink node discovery, the dedicated music database) live in
``utils/music/`` so the cog and this panel stay slim.
"""

import asyncio
import re
from collections import deque

import discord
import wavelink
from discord import MediaGalleryItem, UnfurledMediaItem

from config.emojis import get_emoji
from utils import logging as log
from utils.music import (
    SOURCE_COLOURS,
    _fmt_dur,
    _progress_bar,
    _source_colour,
    msg,
)
from utils.music.database import MusicDatabase

__all__ = ["_build_np_view"]


def _fill(template: str, **values) -> str:
    """Replace ``{token}`` placeholders literally.

    Track titles and artist names are whatever the music service returned, so
    they may contain braces; ``str.format`` would raise on those.
    """
    for name, value in values.items():
        template = template.replace("{" + name + "}", str(value))
    return template


async def _report_failure(interaction: discord.Interaction, exc: BaseException) -> None:
    """Tell the presser that the node rejected the action.

    Panel buttons used to call straight into the player, so a Lavalink 500
    escaped as an unhandled interaction error and the button looked dead.
    """
    log.warning("Music", f"Panel action failed: {exc}")
    try:
        await interaction.followup.send(
            msg(interaction, "panel_action_failed"), ephemeral=True
        )
    except Exception:
        pass


# ──────────────────────────────────────────────────
#  CONTROL PANEL BUTTONS
# ──────────────────────────────────────────────────

class _PauseResumeBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild: discord.Guild, paused: bool):
        super().__init__(
            label=msg(guild, "btn_resume" if paused else "btn_pause"),
            style=discord.ButtonStyle.success if paused else discord.ButtonStyle.secondary,
            emoji=get_emoji("play") if paused else get_emoji("pause"),
        )
        self.cog      = cog
        self.guild_id = guild.id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = self.cog._player_for_guild(interaction.guild)
        if player:
            try:
                await player.pause(not player.paused)
            except Exception as exc:
                await _report_failure(interaction, exc)
        await self.cog._update_np_message(interaction.guild)


class _SkipBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild: discord.Guild):
        super().__init__(
            label=msg(guild, "btn_skip"),
            style=discord.ButtonStyle.primary, emoji=get_emoji('skip'))
        self.cog      = cog
        self.guild_id = guild.id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = self.cog._player_for_guild(interaction.guild)
        if player and player.playing:
            try:
                await player.skip(force=True)
            except Exception as exc:
                await _report_failure(interaction, exc)
        await self.cog._update_np_message(interaction.guild)


class _StopBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild: discord.Guild):
        super().__init__(
            label=msg(guild, "btn_stop"),
            style=discord.ButtonStyle.danger, emoji=get_emoji("stop"))
        self.cog      = cog
        self.guild_id = guild.id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = self.cog._player_for_guild(interaction.guild)
        if player:
            state = self.cog._state(self.guild_id)
            state["loop"] = False
            state["current_track"] = None
            self.cog._clear_ghost(self.guild_id)
            player.queue.clear()
            try:
                await player.stop()
            except Exception as exc:
                await _report_failure(interaction, exc)
        await self.cog._update_np_message(interaction.guild)


class _PrevBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild: discord.Guild, enabled: bool):
        super().__init__(
            label=msg(guild, "btn_prev"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("rewind"),
            disabled=not enabled,
        )
        self.cog      = cog
        self.guild_id = guild.id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = self.cog._player_for_guild(interaction.guild)
        state = self.cog._state(self.guild_id)
        history: deque = state["history"]
        if not player or not history:
            return
        prev_track = history.pop()
        # put current back at front of queue
        if player.current:
            player.queue.put_at(0, player.current)
        try:
            await player.play(prev_track)
        except Exception as exc:
            # Give the entry back so a failed replay does not eat history.
            history.append(prev_track)
            await _report_failure(interaction, exc)
            return
        state["current_track"] = prev_track
        self.cog._schedule_ghost_refill(self.guild_id)
        await self.cog._update_np_message(interaction.guild)


class _LoopBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild: discord.Guild, loop: bool):
        super().__init__(
            label=msg(guild, "btn_loop_on" if loop else "btn_loop"),
            style=discord.ButtonStyle.success if loop else discord.ButtonStyle.secondary,
            emoji=get_emoji("loop"),
        )
        self.cog      = cog
        self.guild_id = guild.id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        state = self.cog._state(self.guild_id)
        state["loop"] = not state["loop"]
        await self.cog._update_np_message(interaction.guild)


class _AutoplayBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild: discord.Guild,
                 autoplay: bool, available: bool):
        if not available:
            super().__init__(
                label=msg(guild, "btn_autoplay"),
                style=discord.ButtonStyle.secondary,
                emoji=get_emoji("autoplay"),
                disabled=True,
            )
        else:
            super().__init__(
                label=msg(guild, "btn_autoplay_on" if autoplay else "btn_autoplay"),
                style=discord.ButtonStyle.success if autoplay else discord.ButtonStyle.secondary,
                emoji=get_emoji("autoplay"),
            )
        self.cog       = cog
        self.guild_id  = guild.id
        self.available = available

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.available:
            return
        state = self.cog._state(self.guild_id)
        state["autoplay"] = not state["autoplay"]
        if state["autoplay"]:
            self.cog._schedule_ghost_refill(self.guild_id)
        else:
            self.cog._clear_ghost(self.guild_id)
        await self.cog._update_np_message(interaction.guild)


class _LikeBtn(discord.ui.Button):
    """Save / unsave the current track in the user's liked-songs library."""

    def __init__(self, cog: "MusicSystem", guild: discord.Guild):
        super().__init__(
            label=msg(guild, "btn_like"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("heart"),
        )
        self.cog      = cog
        self.guild_id = guild.id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        player = self.cog._player_for_guild(interaction.guild)
        if not player or not player.current:
            await interaction.followup.send(msg(interaction, "like_nothing"), ephemeral=True)
            return
        track = player.current
        db    = MusicDatabase()
        try:
            await db.ensure(self.cog.bot)
            now_liked = await db.toggle_liked(interaction.user.id, track)
        except Exception as exc:
            log.warning("Music", f"Panel like failed for {interaction.user.id}: {exc}")
            await interaction.followup.send(msg(interaction, "music_db_error"), ephemeral=True)
            return
        title = (track.title or msg(interaction, "np_unknown_track"))
        key = "like_on" if now_liked else "like_off"
        await interaction.followup.send(msg(interaction, key, title=title), ephemeral=True)


class _QueueBtn(discord.ui.Button):
    """Show the queue without typing the /queue command."""

    def __init__(self, cog: "MusicSystem", guild: discord.Guild):
        super().__init__(
            label=msg(guild, "btn_queue"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("queue"),
        )
        self.cog      = cog
        self.guild_id = guild.id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = self.cog._player_for_guild(interaction.guild)
        state = self.cog._state(self.guild_id)
        ghost = list(state["ghost_queue"])
        if not player or (player.queue.is_empty and not ghost):
            await interaction.followup.send(msg(interaction, "queue_empty"), ephemeral=True)
            return
        lines = self.cog._format_queue_lines(
            player, self.guild_id, msg(interaction, "queue_header"), interaction
        )
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="\n".join(lines)),
            accent_colour=discord.Colour(0x5865F2),
        ))
        await interaction.followup.send(view=view)


class _VolDownBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild: discord.Guild):
        super().__init__(
            label=msg(guild, "btn_vol_down"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("volume_down"),
        )
        self.cog      = cog
        self.guild_id = guild.id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = self.cog._player_for_guild(interaction.guild)
        if player:
            new_vol = max(0, player.volume - 10)
            try:
                await player.set_volume(new_vol)
            except Exception as exc:
                await _report_failure(interaction, exc)
        await self.cog._update_np_message(interaction.guild)


class _VolUpBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild: discord.Guild):
        super().__init__(
            label=msg(guild, "btn_vol_up"),
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("volume_up"),
        )
        self.cog      = cog
        self.guild_id = guild.id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = self.cog._player_for_guild(interaction.guild)
        if player:
            new_vol = min(100, player.volume + 10)
            try:
                await player.set_volume(new_vol)
            except Exception as exc:
                await _report_failure(interaction, exc)
        await self.cog._update_np_message(interaction.guild)


# ──────────────────────────────────────────────────
#  NOW-PLAYING CARD BUILDER
# ──────────────────────────────────────────────────

_YT_ID_RE = re.compile(r"(?:[?&]v=|youtu\.be/|/shorts/|/embed/)([\w-]{6,})")


def _track_artwork(track) -> str | None:
    """Best-effort artwork URL for the now-playing card.

    Not every public Lavalink node populates ``artworkUrl`` on its track
    info, which left the panel without a thumbnail.  Fall back to the stock
    YouTube thumbnail whenever the track points at a YouTube video.
    """
    artwork = (
        getattr(track, "artwork", None)
        or getattr(track, "artwork_url", None)
        or (getattr(track, "raw_data", {}) or {}).get("info", {}).get("artworkUrl")
    )
    if artwork:
        return artwork

    uri = getattr(track, "uri", None) or ""
    source = (getattr(track, "source", None) or "").lower()
    identifier = getattr(track, "identifier", None) or ""
    if "youtu" in uri or source in {"youtube", "youtube music", "youtube_music"}:
        match = _YT_ID_RE.search(uri) or re.fullmatch(r"[\w-]{6,}", identifier)
        if match:
            video_id = match.group(1) if hasattr(match, "group") and match.lastindex else match.group(0)
            return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    return None


def _build_np_view(
    player:   wavelink.Player,
    guild:    discord.Guild,
    cog:      "MusicSystem",
    is_playing: bool = True,
    prefix:   str = ".",
) -> discord.ui.LayoutView:
    state    = cog._state(guild.id)
    track    = (
        (player.current if player else None)
        or state.get("current_track")
    )
    loop     = state.get("loop", False)
    autoplay = state.get("autoplay", False)
    history: deque = state.get("history", deque())
    vol      = player.volume if player else 100

    if not track or not is_playing:
        # Idle / stopped card
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(guild, "np_idle_title", stop=get_emoji("stop"))),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=msg(guild, "np_idle_hint", prefix=prefix)),
            accent_colour=discord.Colour(0x5865F2),
        ))
        return view

    # Track meta
    source       = (track.source or "").lower()
    accent_color = _source_colour(track)
    author_name  = track.author or msg(guild, "np_unknown_artist")
    # Streams report length 0; a progress bar would render as permanently full.
    if not track.length:
        duration = msg(
            guild, "np_live",
            time=_fmt_dur(player.position or 0),
        )
    else:
        duration = _progress_bar(player.position or 0, track.length)
    uri          = track.uri or ""

    # Source badge
    if "youtube" in source:
        src_badge = f"{get_emoji('youtube')} YouTube"
    elif "soundcloud" in source:
        src_badge = f"{get_emoji('soundcloud')} SoundCloud"
    elif "spotify" in source:
        src_badge = f"{get_emoji('spotify')} Spotify"
    else:
        src_badge = msg(guild, "np_source_music")

    status_icon = get_emoji("pause") if player.paused else get_emoji("play")

    badges = []
    if loop:
        badges.append(msg(guild, "np_loop_badge", emoji=get_emoji("loop")))
    if autoplay:
        badges.append(msg(guild, "np_autoplay_badge", emoji=get_emoji("autoplay")))

    meta = msg(guild, "np_meta", source=src_badge, vol=vol)
    if badges:
        meta = f"{meta} · " + " · ".join(badges)

    body = (
        f"{msg(guild, 'np_heading', status=status_icon)}\n"
        f"**{track.title}**\n"
        f"{msg(guild, 'np_byline', author=author_name)}\n\n"
        f"{duration}\n\n"
        f"{meta}"
    )

    # Build container items
    items: list = [
        discord.ui.TextDisplay(content=body),
    ]

    # Artwork thumbnail (if available)
    artwork = _track_artwork(track)
    if artwork:
        items.insert(0, discord.ui.MediaGallery(
            MediaGalleryItem(media=UnfurledMediaItem(url=artwork))
        ))
        items.insert(1, discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

    items += [
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        # Row 1 — transport + like
        discord.ui.ActionRow(
            _PrevBtn(cog, guild, enabled=bool(history)),
            _PauseResumeBtn(cog, guild, paused=player.paused),
            _SkipBtn(cog, guild),
            _StopBtn(cog, guild),
            _LikeBtn(cog, guild),
        ),
        # Row 2 — modes, queue peek, volume
        discord.ui.ActionRow(
            _LoopBtn(cog, guild, loop=loop),
            _AutoplayBtn(cog, guild, autoplay=autoplay, available=bool(cog._lastfm_key)),
            _QueueBtn(cog, guild),
            _VolDownBtn(cog, guild),
            _VolUpBtn(cog, guild),
        ),
    ]

    # Link button (separate ActionRow below the container — not inside)
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items, accent_colour=accent_color))
    if uri:
        view.add_item(discord.ui.ActionRow(
            discord.ui.Button(
                label=msg(guild, "btn_open_track"),
                style=discord.ButtonStyle.link, url=uri)
        ))
    return view
