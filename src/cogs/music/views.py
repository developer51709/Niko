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
from collections import deque

import discord
import wavelink
from discord import MediaGalleryItem, UnfurledMediaItem

from config.emojis import get_emoji
from utils.music import (
    SOURCE_COLOURS,
    _fmt_dur,
    _progress_bar,
    _source_colour,
    msg,
)
from utils.music.database import MusicDatabase

__all__ = ["_build_np_view"]


# ──────────────────────────────────────────────────
#  CONTROL PANEL BUTTONS
# ──────────────────────────────────────────────────

class _PauseResumeBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int, paused: bool):
        super().__init__(
            label="Resume" if paused else "Pause",
            style=discord.ButtonStyle.success if paused else discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_play") if paused else get_emoji("icon_pause"),
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            await player.pause(not player.paused)
        await self.cog._update_np_message(interaction.guild)


class _SkipBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(label="Skip", style=discord.ButtonStyle.primary, emoji=get_emoji('icon_skip'))
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player and player.playing:
            await player.skip(force=True)
        await self.cog._update_np_message(interaction.guild)


class _StopBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger, emoji=get_emoji("icon_stop"))
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            state = self.cog._state(self.guild_id)
            state["loop"] = False
            self.cog._clear_ghost(self.guild_id)
            player.queue.clear()
            await player.stop()
        await self.cog._update_np_message(interaction.guild)


class _PrevBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int, enabled: bool):
        super().__init__(
            label="Prev",
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_rewind"),
            disabled=not enabled,
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        state = self.cog._state(self.guild_id)
        history: deque = state["history"]
        if not player or not history:
            return
        prev_track = history.pop()
        # put current back at front of queue
        if player.current:
            player.queue.put_at(0, player.current)
        await player.play(prev_track)
        self.cog._schedule_ghost_refill(self.guild_id)
        await self.cog._update_np_message(interaction.guild)


class _LoopBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int, loop: bool):
        super().__init__(
            label="Loop On" if loop else "Loop",
            style=discord.ButtonStyle.success if loop else discord.ButtonStyle.secondary,
            emoji=get_emoji("icon_loop"),
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        state = self.cog._state(self.guild_id)
        state["loop"] = not state["loop"]
        await self.cog._update_np_message(interaction.guild)


class _AutoplayBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int, autoplay: bool, available: bool):
        if not available:
            super().__init__(
                label="Autoplay",
                style=discord.ButtonStyle.secondary,
                emoji="📻",
                disabled=True,
            )
        else:
            super().__init__(
                label="Autoplay On" if autoplay else "Autoplay",
                style=discord.ButtonStyle.success if autoplay else discord.ButtonStyle.secondary,
                emoji="📻",
            )
        self.cog       = cog
        self.guild_id  = guild_id
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

    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(
            label="Like",
            style=discord.ButtonStyle.secondary,
            emoji="♥",
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        player: wavelink.Player = interaction.guild.voice_client
        if not player or not player.current:
            await interaction.followup.send("Nothing is playing to like.", ephemeral=True)
            return
        track = player.current
        db    = MusicDatabase()
        try:
            await db.ensure(self.cog.bot)
            now_liked = await db.toggle_liked(interaction.user.id, track)
        except Exception:
            await interaction.followup.send("Couldn't reach the music database right now.", ephemeral=True)
            return
        title = (track.title or "Unknown")
        if now_liked:
            await interaction.followup.send(f"♥ Liked **{title}**", ephemeral=True)
        else:
            await interaction.followup.send(f"Removed **{title}** from your likes.", ephemeral=True)


class _QueueBtn(discord.ui.Button):
    """Show the queue without typing the /queue command."""

    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(
            label="Queue",
            style=discord.ButtonStyle.secondary,
            emoji="📜",
        )
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        state = self.cog._state(self.guild_id)
        ghost = list(state["ghost_queue"])
        if not player or (player.queue.is_empty and not ghost):
            await interaction.followup.send("The queue is currently empty.", ephemeral=True)
            return
        lines = self.cog._format_queue_lines(player, self.guild_id)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="\n".join(lines)),
            accent_colour=discord.Colour(0x5865F2),
        ))
        await interaction.followup.send(view=view)


class _VolDownBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(label="Vol -", style=discord.ButtonStyle.secondary, emoji="🔉")
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            new_vol = max(0, player.volume - 10)
            await player.set_volume(new_vol)
        await self.cog._update_np_message(interaction.guild)


class _VolUpBtn(discord.ui.Button):
    def __init__(self, cog: "MusicSystem", guild_id: int):
        super().__init__(label="Vol +", style=discord.ButtonStyle.secondary, emoji="🔊")
        self.cog      = cog
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            new_vol = min(100, player.volume + 10)
            await player.set_volume(new_vol)
        await self.cog._update_np_message(interaction.guild)


# ──────────────────────────────────────────────────
#  NOW-PLAYING CARD BUILDER
# ──────────────────────────────────────────────────

def _build_np_view(
    player:   wavelink.Player,
    guild:    discord.Guild,
    cog:      "MusicSystem",
    is_playing: bool = True,
) -> discord.ui.LayoutView:
    state    = cog._state(guild.id)
    track    = player.current if player else None
    loop     = state.get("loop", False)
    autoplay = state.get("autoplay", False)
    history: deque = state.get("history", deque())
    vol      = player.volume if player else 100

    if not track or not is_playing:
        # Idle / stopped card
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_stop')} Nothing Playing"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"-# Use `.play <song>` to queue something up."),
            accent_colour=discord.Colour(0x5865F2),
        ))
        return view

    # Track meta
    source       = (track.source or "").lower()
    accent_color = _source_colour(track)
    author_name  = track.author or "Unknown Artist"
    duration     = _progress_bar(player.position or 0, track.length or 0)
    uri          = track.uri or ""

    # Source badge
    if "youtube" in source:
        src_badge = f"{get_emoji('youtube')} YouTube"
    elif "soundcloud" in source:
        src_badge = f"{get_emoji('soundcloud')} SoundCloud"
    elif "spotify" in source:
        src_badge = f"{get_emoji('spotify')} Spotify"
    else:
        src_badge = "🎵 Music"

    status_icon = get_emoji("icon_pause") if player.paused else get_emoji("icon_play")

    body = (
        f"### {status_icon} Now Playing\n"
        f"**{track.title}**\n"
        f"by {author_name}\n\n"
        f"{duration}\n\n"
        f"-# {src_badge} · Vol {vol}% · "
        f"{get_emoji('icon_loop') + ' Loop ' if loop else ''}{'📻 Autoplay ' if autoplay else ''}"
    ).rstrip(" · \n")

    # Build container items
    items: list = [
        discord.ui.TextDisplay(content=body),
    ]

    # Artwork thumbnail (if available)
    if track.artwork:
        items.insert(0, discord.ui.MediaGallery(
            MediaGalleryItem(media=UnfurledMediaItem(url=track.artwork))
        ))
        items.insert(1, discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

    items += [
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        # Row 1 — transport + like
        discord.ui.ActionRow(
            _PrevBtn(cog, guild.id, enabled=bool(history)),
            _PauseResumeBtn(cog, guild.id, paused=player.paused),
            _SkipBtn(cog, guild.id),
            _StopBtn(cog, guild.id),
            _LikeBtn(cog, guild.id),
        ),
        # Row 2 — modes, queue peek, volume
        discord.ui.ActionRow(
            _LoopBtn(cog, guild.id, loop=loop),
            _AutoplayBtn(cog, guild.id, autoplay=autoplay, available=bool(cog._lastfm_key)),
            _QueueBtn(cog, guild.id),
            _VolDownBtn(cog, guild.id),
            _VolUpBtn(cog, guild.id),
        ),
    ]

    # Link button (separate ActionRow below the container — not inside)
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items, accent_colour=accent_color))
    if uri:
        view.add_item(discord.ui.ActionRow(
            discord.ui.Button(label="Open Track", style=discord.ButtonStyle.link, url=uri)
        ))
    return view