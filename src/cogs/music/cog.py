import asyncio
import os
import re
import time as _time
from collections import deque

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

from config.emojis import get_emoji
from utils import logging as log
from utils.discord_extras import set_voice_status
from utils.music import (
    GHOST_QUEUE_LEN,
    HISTORY_LEN,
    IDLE_TIMEOUT,
    MAX_QUEUE_SHOW,
    SOURCE_COLOURS,
    _CONNECT_TIMEOUT,
    _MAX_CONNECT_NODES,
    _SPOTIFY_ALBUM_RE,
    _SPOTIFY_PLAYLIST_RE,
    _SPOTIFY_TRACK_RE,
    _SpotifyClient,
    _fetch_node_list,
    _find_responsive_nodes,
    _fmt_dur,
    _lastfm_similar,
    _normalize_spotify_reference,
    _source_colour,
    msg,
)
from utils.music.database import MusicDatabase
from cogs.music.views import _build_np_view

class MusicSystem(commands.Cog):
    """Music system — artwork cards, control panel, multi-source, autoplay."""

    def __init__(self, bot: commands.Bot):
        self.bot        = bot
        self.connected  = False
        self._connecting = False
        # Labels of Lavalink nodes currently in the pool (host:port).
        self._node_labels: list[str] = []

        # { guild_id: { loop, autoplay, history, np_message, last_track } }
        self._guild_states: dict[int, dict] = {}

        # YouTube autocomplete cache: { lower_query: (monotonic_ts, [Choice, ...]) }
        self._autocomplete_cache: dict[str, tuple[float, list]] = {}

        # Optional integrations — silently disabled if env vars are absent
        sp_id     = os.environ.get("SPOTIFY_CLIENT_ID")
        sp_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        self._spotify: _SpotifyClient | None = (
            _SpotifyClient(sp_id, sp_secret) if sp_id and sp_secret else None
        )
        if self._spotify:
            log.debug("Music", "Spotify URL support enabled.")

        self._lastfm_key: str | None = os.environ.get("LASTFM_API_KEY")
        if self._lastfm_key:
            log.debug("Music", "Last.fm autoplay enabled.")

        # Wire the slash autocomplete callback to the /play search parameter
        try:
            self.play.autocomplete("search")(self._play_autocomplete)
        except Exception as exc:
            log.warning("Music", f"Could not attach play autocomplete: {exc}")

        bot.loop.create_task(self.startup_connect())

    def _state(self, guild_id: int) -> dict:
        if guild_id not in self._guild_states:
            self._guild_states[guild_id] = {
                "loop":        False,
                "autoplay":    False,
                "history":     deque(maxlen=HISTORY_LEN),
                "np_message":  None,
                "last_track":  None,
                # Autoplay "ghost queue": pre-resolved Last.fm suggestions
                # that play only when the manual queue runs dry. It never
                # feeds tracks into player.queue, so manual queue changes
                # are never disturbed by autoplay.
                "ghost_queue": deque(maxlen=GHOST_QUEUE_LEN),
                "ghost_seed":  None,   # (artist, title) it was seeded from
                "ghost_task":  None,   # pending background refill task
            }
        return self._guild_states[guild_id]

    # ─── AUTOPLAY GHOST QUEUE ────────────────────

    def _clear_ghost(self, guild_id: int):
        """Drop all autoplay suggestions and cancel any pending refill.

        Called on /stop, disconnect, and when autoplay is toggled off, so a
        stale ghost queue can never leak into a fresh listening session.
        """
        state = self._guild_states.get(guild_id)
        if not state:
            return
        task = state.get("ghost_task")
        if task and not task.done():
            task.cancel()
        state["ghost_task"] = None
        state["ghost_queue"].clear()
        state["ghost_seed"] = None

    def _ghost_seed_from_player(self, player, fallback=None):
        """Pick the track the next ghost-queue refill should follow.

        Priority: the last manually queued track (the queue tail, i.e. what
        will be playing when the manual queue finally drains) → the currently
        playing track → the caller-provided fallback.
        """
        if player is not None:
            try:
                if not player.queue.is_empty:
                    return player.queue[-1]
            except Exception:
                pass
            if getattr(player, "current", None):
                return player.current
        return fallback

    def _schedule_ghost_refill(
        self,
        guild_id: int,
        seed_track=None,
        delay: float = 1.0,
    ):
        """Queue a background refill of the autoplay ghost queue.

        Coalesced per guild: scheduling a new refill cancels any pending one,
        so a burst of manual /play adds only triggers one Last.fm round trip.
        """
        state = self._state(guild_id)
        if not (self._lastfm_key and state.get("autoplay")):
            return
        task = state.get("ghost_task")
        if task and not task.done():
            task.cancel()
        state["ghost_task"] = asyncio.create_task(
            self._ghost_refill_task(guild_id, seed_track, delay)
        )

    async def _ghost_refill_task(self, guild_id: int, seed_track, delay: float):
        """Background refill: resolve similar tracks for the current seed and
        replace the ghost queue with them (deduped against history)."""
        try:
            await asyncio.sleep(delay)
            state = self._state(guild_id)
            if not (self._lastfm_key and state.get("autoplay")):
                return

            guild  = self.bot.get_guild(guild_id)
            player = guild.voice_client if guild else None
            seed   = self._ghost_seed_from_player(player, seed_track)
            if seed is None:
                return
            seed_key = ((seed.author or "").lower(), (seed.title or "").lower())
            if seed_key == ("", ""):
                return

            # Nothing changed since the last fill — don't burn a Last.fm call.
            if state.get("ghost_seed") == seed_key and state.get("ghost_queue"):
                return

            candidates = await self._fetch_ghost_candidates(guild_id, seed)
            if not candidates:
                return
            state["ghost_queue"].clear()
            state["ghost_queue"].extend(candidates)
            state["ghost_seed"] = seed_key
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            log.error("Music", f"Ghost queue refill failed: {exc}")
        finally:
            state = self._guild_states.get(guild_id)
            if state:
                state["ghost_task"] = None

    async def _fetch_ghost_candidates(self, guild_id: int, seed) -> list:
        """Resolve up to GHOST_QUEUE_LEN Last.fm-similar tracks for the seed,
        skipping anything already played or already suggested."""
        artist_raw = (seed.author or "").strip()
        title_raw  = (seed.title  or "").strip()
        if not artist_raw and not title_raw:
            return []

        state = self._state(guild_id)
        played: set[tuple[str, str]] = set()
        for item in state["history"]:
            key = ((item.author or "").lower(), (item.title or "").lower())
            if key != ("", ""):
                played.add(key)
        if state.get("last_track"):
            played.add((
                (state["last_track"].author or "").lower(),
                (state["last_track"].title  or "").lower(),
            ))
        for item in state.get("ghost_queue", ()):
            played.add(((item.author or "").lower(), (item.title or "").lower()))
        played.add((artist_raw.lower(), title_raw.lower()))

        similars = await _lastfm_similar(self._lastfm_key, artist_raw, title_raw)
        found: list = []
        for similar_artist, similar_title in similars:
            if (similar_artist.lower(), similar_title.lower()) in played:
                continue
            try:
                results = await wavelink.Playable.search(
                    f"ytsearch:{similar_artist} - {similar_title}"
                )
            except Exception:
                continue
            if not results:
                continue
            track = results[0] if isinstance(results, list) else results
            found.append(track)
            played.add((similar_artist.lower(), similar_title.lower()))
            if len(found) >= GHOST_QUEUE_LEN:
                break
        return found

    # ─── NP MESSAGE UPDATE ────────────────────────

    async def _update_np_message(self, guild: discord.Guild):
        state   = self._state(guild.id)
        message: discord.Message | None = state.get("np_message")
        if not message:
            return
        player: wavelink.Player = guild.voice_client
        if not player:
            return
        view = _build_np_view(player, guild, self, is_playing=player.playing or player.paused)
        try:
            await message.edit(view=view)
        except discord.NotFound:
            state["np_message"] = None
        except Exception:
            pass

    async def _send_np(self, ctx: commands.Context, player: wavelink.Player):
        """Send (or update) the now-playing control panel."""
        state  = self._state(ctx.guild.id)
        old_msg: discord.Message | None = state.get("np_message")

        view = _build_np_view(player, ctx.guild, self)
        new_msg = await ctx.send(view=view)
        state["np_message"] = new_msg

        # Clean up the previous control panel quietly
        if old_msg:
            try:
                await old_msg.delete()
            except Exception:
                pass

    # ─── LAVALINK CONNECTION ──────────────────────

    async def startup_connect(self, *, retry_delay: float = 0):
        """Connect the bot to several responsive Lavalink nodes at once.

        wavelink registers every node that accepts the handshake and then
        load-balances players across them, so a single node going down no
        longer kills music for every guild.
        """
        if self._connecting:
            return
        self._connecting = True
        try:
            if retry_delay:
                await asyncio.sleep(retry_delay)
            await self.bot.wait_until_ready()

            raw_nodes = await _fetch_node_list()
            if not raw_nodes:
                log.warning("Lavalink", "Could not fetch node list.")
                return

            responsive = await _find_responsive_nodes(raw_nodes)
            if not responsive:
                log.warning("Lavalink", "No responsive nodes found. Music unavailable.")
                return

            # Eject dead nodes from a previous pool epoch so their identifiers
            # can be registered again. Healthy nodes are left untouched.
            await self._eject_stale_nodes()

            # Connect several nodes in one Pool.connect call — wavelink keeps
            # whichever succeed.
            targets: list[wavelink.Node] = []
            for node_info in responsive[: int(_MAX_CONNECT_NODES)]:
                host     = node_info["host"]
                port     = node_info["port"]
                password = node_info["password"]
                secure   = node_info.get("secure", False)
                uri      = f"{'https' if secure else 'http'}://{host}:{port}"
                targets.append(wavelink.Node(
                    uri=uri,
                    password=password,
                    identifier=f"{host}:{port}",
                    retries=3,
                ))

            try:
                await asyncio.wait_for(
                    wavelink.Pool.connect(nodes=targets, client=self.bot),
                    timeout=_CONNECT_TIMEOUT + 10,
                )
            except Exception as exc:
                log.warning(
                    "Lavalink",
                    f"Multi-node connect failed ({exc}); retrying the fastest node alone.",
                )
                await self._eject_stale_nodes()
                try:
                    await asyncio.wait_for(
                        wavelink.Pool.connect(nodes=targets[:1], client=self.bot),
                        timeout=_CONNECT_TIMEOUT,
                    )
                except Exception as exc2:
                    log.warning("Lavalink", f"Single-node fallback failed too: {exc2}")

            # wavelink registers a node as soon as its websocket opens, but the
            # Lavalink 'ready' handshake completes a beat later on the node's
            # background task. Poll for the CONNECTED status instead of trusting
            # an instant snapshot, otherwise a healthy connect can be reported
            # as failed (ready events arriving just after the check).
            target_ids = {node.identifier for node in targets}
            connected  = await self._wait_for_connected_nodes(target_ids)
            if connected:
                self._node_labels = sorted(node.identifier for node in connected)
                self.connected    = True
                log.info(
                    "Lavalink",
                    f"Connected to {len(connected)} Lavalink node(s): "
                    + ", ".join(self._node_labels),
                )
            else:
                self._node_labels = []
                self.connected    = False
                log.warning(
                    "Lavalink",
                    "No Lavalink node completed the wavelink handshake.",
                )
        finally:
            self._connecting = False

    async def _eject_stale_nodes(self):
        """Remove disconnected nodes from the wavelink pool so their
        identifiers can be re-registered on the next connect attempt."""
        for node in list(wavelink.Pool.nodes.values()):
            if node.status is not wavelink.NodeStatus.CONNECTED:
                try:
                    await node.close(eject=True)
                except Exception:
                    pass

    async def _wait_for_connected_nodes(
        self, identifiers: set[str], timeout: float = 8.0
    ) -> list:
        """Poll the pool until any of the given nodes report CONNECTED.

        wavelink registers a node as soon as its websocket opens; the actual
        Lavalink 'ready' opcode is handled by the node's background task a
        moment later. Polling avoids declaring a failed connect from a status
        snapshot taken before the handshake lands.
        """
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            connected = [
                n for n in wavelink.Pool.nodes.values()
                if n.identifier in identifiers
                and n.status is wavelink.NodeStatus.CONNECTED
            ]
            if connected or loop.time() >= deadline:
                return connected
            await asyncio.sleep(0.2)

    # ─── WAVELINK EVENTS ──────────────────────────

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        node_id = payload.node.identifier
        log.info("Lavalink", f"Node '{node_id}' ready (resumed={payload.resumed})")

        # Ready events can land after startup_connect's decision window (the
        # handshake completes on the node's background task), so keep the cog's
        # state in sync with nodes that are genuinely up.
        if node_id not in self._node_labels:
            self._node_labels = sorted(set(self._node_labels) | {node_id})
        if not self.connected:
            self.connected = True
            log.info("Lavalink", f"Node '{node_id}' ready — Lavalink back online.")

    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list):
        """Handle node loss: keep playing while other nodes remain; only
        re-run the full connect cycle when every node is gone."""
        try:
            remaining = [
                n for n in wavelink.Pool.nodes.values()
                if n is not node and n.status is wavelink.NodeStatus.CONNECTED
            ]
        except Exception:
            remaining = []

        if remaining:
            self._node_labels = sorted(n.identifier for n in remaining)
            self.connected    = True
            log.warning(
                "Lavalink",
                f"Node '{node.identifier}' closed — {len(remaining)} node(s) still "
                "connected, continuing playback.",
            )
            return

        self._node_labels = []
        self.connected    = False
        if self._connecting:
            return  # a reconnect cycle is already running
        log.warning(
            "Lavalink",
            f"Node '{node.identifier}' closed — no nodes left. Reconnecting in 10s…",
        )
        self.bot.loop.create_task(self.startup_connect(retry_delay=10))

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        """Auto-set voice channel status to the current track title when a song starts."""
        player = payload.player
        if player is None or not getattr(player, "channel", None):
            return
        track = payload.track
        if not track:
            return
        title  = (track.title  or "Unknown")[:80]
        artist = (track.author or "")[:40]
        status = f"🎵 {title}" + (f" · {artist}" if artist else "")
        asyncio.create_task(set_voice_status(self.bot, player.channel.id, status))

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        if player is None:
            return

        guild_id = player.guild.id
        state    = self._state(guild_id)

        # Push finished track to history
        if payload.track:
            state["history"].append(payload.track)
            state["last_track"] = payload.track

        # Loop mode — replay the same track
        if state.get("loop") and payload.track:
            await player.play(payload.track)
            await self._update_np_message(player.guild)
            return

        reason  = str(getattr(payload, "reason", "") or "")
        natural = reason in ("finished", "replaced")

        # Queue has more tracks — manual queue always wins over autoplay.
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)
            await self._update_np_message(player.guild)
            # Near the end of a manual queue, keep the autoplay suggestions
            # following the new queue tail (coalesced background refill).
            try:
                if len(player.queue) <= GHOST_QUEUE_LEN:
                    self._schedule_ghost_refill(guild_id)
            except Exception:
                pass
            return

        # Queue exhausted — continue via the autoplay ghost queue (Last.fm
        # suggestions pre-resolved in the background, never mixed into the
        # manual queue). Only continue when the previous track ended naturally
        # or was skipped forward; never after /stop or a channel cleanup,
        # which fire 'stopped'/'cleanup' reasons.
        if natural and state.get("autoplay") and self._lastfm_key and payload.track:
            ghost = state.get("ghost_queue")
            if ghost:
                # Instant pop — no network in the hot path.
                nxt = ghost.popleft()
                # Force a re-seed so the top-up refill below actually runs.
                state["ghost_seed"] = None
                try:
                    await player.play(nxt)
                    await self._update_np_message(player.guild)
                    self._schedule_ghost_refill(guild_id, seed_track=nxt, delay=0.5)
                    return
                except Exception as exc:
                    log.error("Music", f"Autoplay ghost play failed: {exc}")

            # No suggestions ready yet (e.g. autoplay was just switched on) —
            # fall back to a direct fetch so playback never dead-airs.
            try:
                track      = payload.track
                artist_raw = track.author or ""
                title_raw  = track.title  or ""
                similars   = await _lastfm_similar(self._lastfm_key, artist_raw, title_raw)

                # Skip candidates we have just played — Last.fm "similar" lists
                # frequently include the source track, which would otherwise
                # loop two songs forever.
                played = set()
                for item in state["history"]:
                    key = ((item.author or "").lower(), (item.title or "").lower())
                    if key != ("", ""):
                        played.add(key)
                played.add((artist_raw.lower(), title_raw.lower()))

                for similar_artist, similar_title in similars:
                    if (similar_artist.lower(), similar_title.lower()) in played:
                        continue
                    query   = f"ytsearch:{similar_artist} - {similar_title}"
                    results = await wavelink.Playable.search(query)
                    if not results:
                        continue
                    nxt = results[0] if isinstance(results, list) else results
                    await player.play(nxt)
                    await self._update_np_message(player.guild)
                    return
            except Exception as exc:
                log.error("Music", f"Autoplay failed: {exc}")
        else:
            # Stopped/cleanup, or autoplay off — drop pending suggestions so
            # they can't leak into the next listening session.
            self._clear_ghost(guild_id)

        # Nothing more to play — idle grace period then disconnect
        await asyncio.sleep(IDLE_TIMEOUT)
        if player and not player.playing:
            if getattr(player, "channel", None):
                await set_voice_status(self.bot, player.channel.id, None)
            try:
                await player.disconnect()
            except Exception:
                pass
            state["np_message"] = None

    # ─── SOURCE RESOLUTION ────────────────────────

    async def _resolve_query(self, query: str) -> list[str] | None:
        """
        Returns a list of wavelink-ready search strings.
        Handles Spotify URLs (single track → 1 item; album/playlist → multiple).
        Returns None on unrecoverable failure.
        """
        q = query.strip()

        # ── Spotify ───────────────────────────────
        if "open.spotify.com" in q or q.startswith("spotify:"):
            if not self._spotify:
                return None
            normalized = _normalize_spotify_reference(q)
            if not normalized:
                return None
            q = normalized

            m_track = _SPOTIFY_TRACK_RE.search(q)
            if m_track:
                search = await self._spotify.resolve_track(m_track.group(1))
                return [f"ytsearch:{search}"] if search else None

            m_album = _SPOTIFY_ALBUM_RE.search(q)
            if m_album:
                queries = await self._spotify.resolve_album(m_album.group(1))
                return [f"ytsearch:{s}" for s in queries] if queries else None

            m_playlist = _SPOTIFY_PLAYLIST_RE.search(q)
            if m_playlist:
                queries = await self._spotify.resolve_playlist(m_playlist.group(1))
                return [f"ytsearch:{s}" for s in queries] if queries else None

            return None

        # ── SoundCloud prefix ─────────────────────
        if q.lower().startswith("sc:"):
            return [f"scsearch:{q[3:].strip()}"]

        # ── YouTube prefix ────────────────────────
        if q.lower().startswith("yt:"):
            return [f"ytsearch:{q[3:].strip()}"]

        # ── Raw URL (YouTube, SoundCloud, etc.) ───
        if q.startswith("http://") or q.startswith("https://"):
            return [q]

        # ── Default: YouTube text search ──────────
        return [f"ytsearch:{q}"]

    # ─── PLAYER HELPER ────────────────────────────

    async def get_player(self, ctx: commands.Context) -> wavelink.Player | None:
        if not ctx.author.voice:
            await ctx.send(msg(ctx, "get_player_not_in_voice"))
            return None
        channel = ctx.author.voice.channel
        player  = ctx.voice_client
        if player is None:
            player = await channel.connect(cls=wavelink.Player)
        return player

    # ─── COMMANDS ─────────────────────────────────

    async def _play_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Live YouTube search suggestions for the slash version of /play."""
        current = (current or "").strip()
        if len(current) < 2:
            return []
        # If the user already pasted a URL, just echo it back so they can submit.
        if current.startswith(("http://", "https://")):
            return [app_commands.Choice(name=current[:100], value=current[:100])]

        # Cheap in-memory cache to avoid hammering Lavalink for every keystroke.
        cache_key = current.lower()
        cached = self._autocomplete_cache.get(cache_key)
        now = _time.monotonic()
        if cached and now - cached[0] < 30:
            return cached[1]

        try:
            results = await asyncio.wait_for(
                wavelink.Playable.search(f"ytsearch:{current}"),
                timeout=2.5,
            )
        except (asyncio.TimeoutError, Exception):
            return []

        if not results:
            return []

        choices: list[app_commands.Choice[str]] = []
        for track in (results if isinstance(results, list) else [results])[:25]:
            label = track.title
            if getattr(track, "author", None):
                label = f"{track.title} — {track.author}"
            label = label[:100]
            value = (getattr(track, "uri", None) or track.title)[:100]
            choices.append(app_commands.Choice(name=label, value=value))

        self._autocomplete_cache[cache_key] = (now, choices)
        return choices

    @commands.hybrid_command(
        name="play", aliases=["p"],
        description="Play a song or add it to the queue",
        help="{ 'en': 'play a song or queue it up ☕🎶', 'de': 'spiele einen track ab', 'es': 'reproduce una canción o agrégala a la cola ☕🎶' }"
    )
    @app_commands.describe(search="Song name, YouTube/SoundCloud/Spotify URL, or sc:<query>")
    async def play(self, ctx: commands.Context, *, search: str):
        # Slash invocations need to defer because resolution can take >3s
        if ctx.interaction and not ctx.interaction.response.is_done():
            try:
                await ctx.defer()
            except Exception:
                pass
        player = await self.get_player(ctx)
        if not player:
            return

        # Handle Spotify URL feedback before long resolution
        is_spotify = "open.spotify.com" in search or search.startswith("spotify:")
        if is_spotify and not self._spotify:
            return await ctx.send(msg(ctx, "spotify_disabled"))

        if is_spotify:
            resolving = discord.ui.LayoutView()
            resolving.add_item(discord.ui.Container(
                discord.ui.TextDisplay(content=f"### ☕ {msg(ctx, 'spotify_resolving')}"),
                accent_colour=SOURCE_COLOURS["spotify"],
            ))
            status_msg = await ctx.send(view=resolving)
        else:
            status_msg = None

        # Resolve to wavelink search strings
        searches = await self._resolve_query(search)

        if status_msg:
            try:
                await status_msg.delete()
            except Exception:
                pass

        if not searches:
            return await ctx.send(msg(ctx, "play_not_found" if not is_spotify else "spotify_fail"))

        queued_count = 0
        first_track  = None

        for i, query in enumerate(searches):
            results = await wavelink.Playable.search(query)
            if not results:
                continue

            track = results[0] if isinstance(results, list) else results
            if not player.playing and first_track is None:
                await player.play(track)
                first_track = track
            else:
                player.queue.put(track)
                queued_count += 1

        if first_track is None and queued_count == 0:
            return await ctx.send(msg(ctx, "play_not_found"))

        # Manual tracks were added — re-seed the autoplay suggestions so they
        # follow the newest additions (background, coalesced; never touches the
        # manual queue itself).
        self._schedule_ghost_refill(ctx.guild.id)

        if queued_count:
            if not first_track:
                first_track = player.current
            # Multiple tracks added (album / playlist)
            multi = discord.ui.LayoutView()
            multi.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### ☕ Added {queued_count + 1} track{'s' if queued_count else ''} to the queue\n"
                        f"Now playing **{first_track.title}** + {queued_count} more queued."
                    )
                ),
                accent_colour=_source_colour(first_track),
            ))
            await ctx.send(view=multi)

        # Send / replace now-playing control panel
        if first_track and not queued_count:
            await self._send_np(ctx, player)

    @commands.command(
        name="pause",
        help="{ 'en': 'pause the current track 🌿', 'de': 'pausiert den aktuellen track' }"
    )
    async def pause(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "pause_nothing"))
        await player.pause(True)
        await ctx.send(msg(ctx, "pause_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="resume",
        help="{ 'en': 'resume the paused track ☕🎶', 'de': 'setzt den pausierten track fort' }"
    )
    async def resume(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "resume_nothing"))
        await player.pause(False)
        await ctx.send(msg(ctx, "resume_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="skip", aliases=["sk"],
        help="{ 'en': 'skip to the next track 🍰', 'de': 'springt zum nächsten track' }"
    )
    async def skip(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "skip_nothing"))
        await player.skip(force=True)
        await ctx.send(msg(ctx, "skip_ok"))

    @commands.command(
        name="stop",
        help="{ 'en': 'stop and clear the queue ☕', 'de': 'stoppt die wiedergabe' }"
    )
    async def stop(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "stop_nothing"))
        self._state(ctx.guild.id)["loop"] = False
        self._clear_ghost(ctx.guild.id)
        player.queue.clear()
        await player.stop()
        await ctx.send(msg(ctx, "stop_ok"))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="loop", aliases=["repeat"],
        help="{ 'en': 'toggle loop for the current track 🔁', 'de': 'wiederholt den aktuellen track' }"
    )
    async def loop(self, ctx: commands.Context):
        state = self._state(ctx.guild.id)
        state["loop"] = not state["loop"]
        key = "loop_on" if state["loop"] else "loop_off"
        await ctx.send(msg(ctx, key))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="autoplay", aliases=["ap"],
        help="{ 'en': 'toggle Last.fm autoplay 📻', 'de': 'schaltet Last.fm-Autoplay um' }"
    )
    async def autoplay(self, ctx: commands.Context):
        if not self._lastfm_key:
            return await ctx.send(msg(ctx, "autoplay_unavailable"))
        state = self._state(ctx.guild.id)
        state["autoplay"] = not state["autoplay"]
        if state["autoplay"]:
            self._schedule_ghost_refill(ctx.guild.id)
        else:
            self._clear_ghost(ctx.guild.id)
        key = "autoplay_on" if state["autoplay"] else "autoplay_off"
        await ctx.send(msg(ctx, key))
        await self._update_np_message(ctx.guild)

    def _format_queue_lines(
        self,
        player: wavelink.Player,
        guild_id: int,
        header: str = "**Current Queue:**",
    ) -> list[str]:
        """Shared queue display — used by the /queue command and the Queue
        button on the now-playing panel."""
        state = self._state(guild_id)
        ghost = list(state["ghost_queue"])
        lines = [header]
        for i, track in enumerate(player.queue, start=1):
            dur = _fmt_dur(track.length) if track.length else "?"
            lines.append(f"{i}. **{track.title}** — {track.author or 'Unknown'} `[{dur}]`")
            if i >= MAX_QUEUE_SHOW:
                remaining = len(player.queue) - MAX_QUEUE_SHOW
                if remaining > 0:
                    lines.append(f"\n*…and {remaining} more track{'s' if remaining > 1 else ''}*")
                break

        # Show the autoplay suggestions separately — they are NOT part of the
        # manual queue and only play when it runs dry.
        if ghost:
            lines.append("")
            lines.append("-# 📻 **Autoplay suggestions** (play when the queue runs dry):")
            for i, track in enumerate(ghost[:3], start=1):
                dur = _fmt_dur(track.length) if track.length else "?"
                lines.append(f"   📻 {i}. **{track.title}** — {track.author or 'Unknown'} `[{dur}]`")
        return lines

    @commands.command(
        name="queue", aliases=["q"],
        help="{ 'en': 'show the current queue ☕📜', 'de': 'zeigt die warteschlange' }"
    )
    async def queue(self, ctx: commands.Context):
        player = ctx.voice_client
        state  = self._state(ctx.guild.id) if ctx.guild else None
        ghost  = list(state["ghost_queue"]) if state else []
        if not player or (player.queue.is_empty and not ghost):
            return await ctx.send(msg(ctx, "queue_empty"))

        lines = self._format_queue_lines(player, ctx.guild.id, msg(ctx, "queue_header"))
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="\n".join(lines)),
            accent_colour=discord.Colour(0x5865F2),
        ))
        await ctx.send(view=view)

    # ─── LIKED SONGS (dedicated music database) ─────

    @commands.command(
        name="like",
        help="{ 'en': 'like the current track ♥', 'de': 'liked den aktuellen track' }"
    )
    async def like(self, ctx: commands.Context):
        """Like (or unlike) the currently playing track. Saved in the music
        database, so likes survive restarts and work in every server."""
        player = ctx.voice_client
        if not player or not player.current:
            return await ctx.send(msg(ctx, "like_nothing"))
        track = player.current
        try:
            db = MusicDatabase()
            await db.ensure(self.bot)
            now_liked = await db.toggle_liked(ctx.author.id, track)
        except Exception as exc:
            log.error("Music", f"Like failed for {ctx.author.id}: {exc}")
            return await ctx.send(msg(ctx, "play_not_found"))
        key = "like_on" if now_liked else "like_off"
        await ctx.send(msg(ctx, key, title=track.title or "Unknown"))

    @commands.command(
        name="liked", aliases=["likes"],
        help="{ 'en': 'show your liked songs ☕♥', 'de': 'zeigt deine gelikten songs' }"
    )
    async def liked(self, ctx: commands.Context):
        """List your liked songs (newest first). Use `.unlike <number>` to
        remove one, or `.unlike all` to clear the whole library."""
        try:
            db = MusicDatabase()
            await db.ensure(self.bot)
            rows  = await db.get_liked(ctx.author.id, limit=10)
            total = await db.count_liked(ctx.author.id)
        except Exception as exc:
            log.error("Music", f"Liked list failed for {ctx.author.id}: {exc}")
            return await ctx.send(msg(ctx, "play_not_found"))

        if not rows:
            return await ctx.send(msg(ctx, "liked_empty"))

        lines = [msg(ctx, "liked_header")]
        for i, row in enumerate(rows, start=1):
            dur  = _fmt_dur(row["length_ms"]) if row.get("length_ms") else "?"
            link = (row.get("uri") or "")[:60]
            lines.append(f"{i}. **{row['title']}** — {row.get('author') or 'Unknown'} `[{dur}]`")
            if link:
                lines.append(f"   -# {link}")
        if total > len(rows):
            lines.append(f"\n*…and {total - len(rows)} more — use `.unlike <number>` to remove*")

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="\n".join(lines)),
            accent_colour=discord.Colour(0xE91E63),
        ))
        await ctx.send(view=view)

    @commands.command(
        name="unlike",
        help="{ 'en': 'remove a liked song (use number from .liked)', 'de': 'entfernt einen gelikten song' }"
    )
    async def unlike(self, ctx: commands.Context, index: str = None):
        """Remove a liked song by its `.liked` number, or pass `all` to clear."""
        db = MusicDatabase()
        try:
            await db.ensure(self.bot)
            if index is not None and index.lower() in ("all", "*"):
                count = await db.clear_liked(ctx.author.id)
                return await ctx.send(msg(ctx, "likes_cleared", count=count))

            try:
                idx = int(index)
            except (TypeError, ValueError):
                return await ctx.send(msg(ctx, "unlike_invalid"))

            rows = await db.get_liked(ctx.author.id, limit=100)
            if not rows:
                return await ctx.send(msg(ctx, "unlike_nothing"))
            if idx < 1 or idx > len(rows):
                return await ctx.send(msg(ctx, "unlike_invalid"))

            target = rows[idx - 1]
            await db.remove_liked(ctx.author.id, target["track_key"])
            await ctx.send(msg(ctx, "unlike_ok", title=target["title"]))
        except Exception as exc:
            log.error("Music", f"Unlike failed for {ctx.author.id}: {exc}")
            await ctx.send(msg(ctx, "play_not_found"))

    @commands.command(
        name="nowplaying", aliases=["np"],
        help="{ 'en': 'see whats brewing right now ☕🎵', 'de': 'zeigt den aktuellen track' }"
    )
    async def nowplaying(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or (not player.playing and not player.paused):
            return await ctx.send(msg(ctx, "pause_nothing"))
        await self._send_np(ctx, player)

    @commands.command(
        name="volume", aliases=["vol"],
        help="{ 'en': 'set the playback volume ✨', 'de': 'passt die lautstärke an' }"
    )
    async def volume(self, ctx: commands.Context, vol: int):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "volume_nothing"))
        vol = max(0, min(vol, 100))
        await player.set_volume(vol)
        await ctx.send(msg(ctx, "volume_set", vol=vol))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="disconnect", aliases=["dc", "leave"],
        help="{ 'en': 'have niko leave the voice channel ☕', 'de': 'trennt niko vom sprachkanal' }"
    )
    async def disconnect(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "disconnect_nothing"))
        state = self._state(ctx.guild.id)
        state["np_message"] = None
        self._clear_ghost(ctx.guild.id)
        if getattr(player, "channel", None):
            asyncio.create_task(set_voice_status(self.bot, player.channel.id, None))
        await player.disconnect()
        await ctx.send(msg(ctx, "disconnect_ok"))

    @commands.command(
        name="musicstatus",
        help="{ 'en': 'check if niko is connected to a music server ☕', 'de': 'prüfe ob niko verbunden ist' }"
    )
    async def music_status(self, ctx: commands.Context):
        sp_line = ""
        if self._spotify:
            sp_line = "\n-# 🎧 Spotify URL support enabled"
        if self._lastfm_key:
            sp_line += "\n-# 📻 Last.fm autoplay available"
        if self.connected and self._node_labels:
            sp_line += (
                "\n-# 🎛 "
                + str(len(self._node_labels))
                + " node(s): "
                + ", ".join(self._node_labels)
            )

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {msg(ctx, 'music_player_status_title')}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    msg(ctx, "music_connected" if self.connected else "music_not_connected")
                    + sp_line
                    + f"\n-# {get_emoji('wavelink')} Powered by Wavelink"
                )
            ),
            accent_colour=discord.Colour(0x57F287) if self.connected else discord.Colour(0xED4245),
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicSystem(bot))
