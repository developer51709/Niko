from .views import *

class MusicSystem(commands.Cog):
    """Music system — artwork cards, control panel, multi-source, autoplay."""

    def __init__(self, bot: commands.Bot):
        self.bot        = bot
        self.connected  = False
        self._connecting = False

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
                "loop":       False,
                "autoplay":   False,
                "history":    deque(maxlen=HISTORY_LEN),
                "np_message": None,
                "last_track": None,
            }
        return self._guild_states[guild_id]

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
        if self._connecting:
            return
        self._connecting = True
        if retry_delay:
            await asyncio.sleep(retry_delay)
        await self.bot.wait_until_ready()

        raw_nodes = await _fetch_node_list()
        if not raw_nodes:
            log.warning("Lavalink", "Could not fetch node list.")
            self._connecting = False
            return

        responsive = await _find_responsive_nodes(raw_nodes)
        if not responsive:
            log.warning("Lavalink", "No responsive nodes found. Music unavailable.")
            self._connecting = False
            return

        for node_info in responsive:
            host     = node_info["host"]
            port     = node_info["port"]
            password = node_info["password"]
            secure   = node_info.get("secure", False)
            uri      = f"{'https' if secure else 'http'}://{host}:{port}"
            try:
                node = wavelink.Node(uri=uri, password=password)
                await asyncio.wait_for(
                    wavelink.Pool.connect(nodes=[node], client=self.bot),
                    timeout=_CONNECT_TIMEOUT,
                )
                log.info("Lavalink", f"Connected to {host}:{port} (SSL={secure})")
                self.connected   = True
                self._connecting = False
                return
            except Exception:
                try:
                    await wavelink.Pool.close()
                except Exception:
                    pass

        log.warning("Lavalink", "All responsive nodes failed the wavelink handshake.")
        self._connecting = False

    # ─── WAVELINK EVENTS ──────────────────────────

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        log.info("Lavalink", f"Node '{payload.node.identifier}' ready (resumed={payload.resumed})")

    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list):
        log.warning("Lavalink", f"Node '{node.identifier}' closed. Reconnecting in 10s…")
        self.connected = False
        self.bot.loop.create_task(self.startup_connect(retry_delay=10))

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

        # Queue has more tracks
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)
            await self._update_np_message(player.guild)
            return

        # Queue exhausted — try autoplay via Last.fm
        if state.get("autoplay") and self._lastfm_key and payload.track:
            track      = payload.track
            artist_raw = track.author or ""
            title_raw  = track.title  or ""
            similars   = await _lastfm_similar(self._lastfm_key, artist_raw, title_raw)

            for similar_artist, similar_title in similars:
                query   = f"ytsearch:{similar_artist} - {similar_title}"
                results = await wavelink.Playable.search(query)
                if results:
                    nxt = results[0] if isinstance(results, list) else results
                    await player.play(nxt)
                    await self._update_np_message(player.guild)
                    return

        # Nothing more to play — idle grace period then disconnect
        await asyncio.sleep(IDLE_TIMEOUT)
        if player and not player.playing:
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
        if "open.spotify.com" in q:
            if not self._spotify:
                return None

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
        is_spotify = "open.spotify.com" in search
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
        key = "autoplay_on" if state["autoplay"] else "autoplay_off"
        await ctx.send(msg(ctx, key))
        await self._update_np_message(ctx.guild)

    @commands.command(
        name="queue", aliases=["q"],
        help="{ 'en': 'show the current queue ☕📜', 'de': 'zeigt die warteschlange' }"
    )
    async def queue(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "queue_empty"))

        lines = [msg(ctx, "queue_header")]
        for i, track in enumerate(player.queue, start=1):
            dur = _fmt_dur(track.length) if track.length else "?"
            lines.append(f"{i}. **{track.title}** — {track.author or 'Unknown'} `[{dur}]`")
            if i >= MAX_QUEUE_SHOW:
                remaining = len(player.queue) - MAX_QUEUE_SHOW
                if remaining > 0:
                    lines.append(f"\n*…and {remaining} more track{'s' if remaining > 1 else ''}*")
                break

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="\n".join(lines)),
            accent_colour=discord.Colour(0x5865F2),
        ))
        await ctx.send(view=view)

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
