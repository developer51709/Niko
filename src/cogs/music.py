import asyncio
import time as _time
import aiohttp
import wavelink
from discord.ext import commands
import discord
import random
from utils import logging as log
from utils.ai_config import get_personality
from config.emojis import get_emoji

MESSAGES = {
    "normal": {
        "en": {
            "not_in_voice": "You need to be in a voice channel first.",
            "get_player_not_in_voice": "You need to be in a voice channel to use music commands.",
            "music_player_status_title": "Music Player Status",
            "music_not_connected": "Not connected to any music servers.",
            "music_connected": "Connected to a music server and ready.",
            "play_not_found": "I couldn't find that track.",
            "play_start": "Now playing **{title}**.",
            "play_queued": "Added **{title}** to the queue.",
            "pause_nothing": "There is nothing playing right now.",
            "pause_ok": "Paused the current track.",
            "resume_nothing": "There is nothing to resume.",
            "resume_ok": "Resumed the current track.",
            "skip_nothing": "There is nothing to skip.",
            "skip_ok": "Skipped the current track.",
            "stop_nothing": "There is nothing to stop.",
            "stop_ok": "Stopped playback and cleared the queue.",
            "queue_empty": "The queue is currently empty.",
            "queue_header": "**Current Queue:**",
            "volume_nothing": "There is no active player.",
            "volume_set": "Volume set to **{vol}%**.",
            "disconnect_nothing": "I am not connected to a voice channel.",
            "disconnect_ok": "Disconnected from the voice channel.",
        },
        "de": {
            "not_in_voice": "Du musst zuerst einem Sprachkanal beitreten.",
            "get_player_not_in_voice": "Du musst in einem Sprachkanal sein, um Musikbefehle zu nutzen.",
            "music_player_status_title": "Musik-Player-Status",
            "music_not_connected": "Mit keinem Musikserver verbunden.",
            "music_connected": "Mit einem Musikserver verbunden und bereit.",
            "play_not_found": "Ich konnte diesen Track nicht finden.",
            "play_start": "Spiele jetzt **{title}**.",
            "play_queued": "**{title}** wurde zur Warteschlange hinzugefügt.",
            "pause_nothing": "Es läuft gerade nichts.",
            "pause_ok": "Der aktuelle Track wurde pausiert.",
            "resume_nothing": "Es gibt nichts zum Fortsetzen.",
            "resume_ok": "Der aktuelle Track wurde fortgesetzt.",
            "skip_nothing": "Es gibt nichts zum Überspringen.",
            "skip_ok": "Der aktuelle Track wurde übersprungen.",
            "stop_nothing": "Es gibt nichts zu stoppen.",
            "stop_ok": "Wiedergabe gestoppt und Warteschlange geleert.",
            "queue_empty": "Die Warteschlange ist derzeit leer.",
            "queue_header": "**Aktuelle Warteschlange:**",
            "volume_nothing": "Es gibt keinen aktiven Player.",
            "volume_set": "Lautstärke auf **{vol}%** gesetzt.",
            "disconnect_nothing": "Ich bin mit keinem Sprachkanal verbunden.",
            "disconnect_ok": "Vom Sprachkanal getrennt.",
        },
    },
    "cafe": {
        "en": {
            "not_in_voice": "hey bestie, you gotta hop into a voice channel first ☕💿",
            "get_player_not_in_voice": "you're not in a voice channel yet, i can't serve music there 😭☕",
            "music_player_status_title": "Café Music Player Status",
            "music_not_connected": "hmm… i'm not connected to any music servers right now, like a café with no music on 😭",
            "music_connected": "yesss, i'm connected and ready to pour some cozy tracks ☕✨",
            "play_not_found": "i couldn't find that song, like a drink that's not on the menu 😭",
            "play_start": "brewing **{title}** for your ears right now ☕🎶",
            "play_queued": "added **{title}** to the queue, it's waiting like a drink order on the counter 🍪✨",
            "pause_nothing": "there's nothing playing to pause, just quiet café air rn 😭",
            "pause_ok": "pausing the cozy vibes for a moment 🌿☕",
            "resume_nothing": "there's nothing paused to resume, the speakers are still empty 😭",
            "resume_ok": "bringing the warm café vibes back on 🎶☕",
            "skip_nothing": "skip what… the silence? the playlist is empty rn 😭",
            "skip_ok": "skipping to the next flavor on the menu 🍰✨",
            "stop_nothing": "there's nothing to stop, the café speakers are already quiet 🌙",
            "stop_ok": "okay okay, stopping everything and clearing the tray ☕💛",
            "queue_empty": "the queue is emptier than a café at closing time 😭",
            "queue_header": "☕ **current cozy queue:**",
            "volume_nothing": "there's no active player to adjust, no music brewing yet 😭",
            "volume_set": "volume set to **{vol}%** — adjusting the café ambiance ✨",
            "disconnect_nothing": "i'm not even in a voice channel, just chilling behind the counter 😭",
            "disconnect_ok": "leaving the vc like a soft barista wave, see you soon ☕🌿",
        },
        "de": {
            "not_in_voice": "hey liebchen, du musst erst in einen Sprachkanal gehen ☕💿",
            "get_player_not_in_voice": "du bist noch in keinem Sprachkanal, ich kann dort keine musik servieren 😭☕",
            "music_player_status_title": "Café-Musik-Player-Status",
            "music_not_connected": "hmm… ich bin gerade mit keinem musikserver verbunden, wie ein café ohne musik 😭",
            "music_connected": "yesss, ich bin verbunden und bereit für cozy tracks ☕✨",
            "play_not_found": "ich konnte den song nicht finden, wie ein drink, der nicht auf der karte steht 😭",
            "play_start": "brühe gerade **{title}** für deine ohren auf ☕🎶",
            "play_queued": "**{title}** wurde zur warteschlange hinzugefügt, wartet wie eine bestellung auf der theke 🍪✨",
            "pause_nothing": "es läuft nichts zum pausieren, nur stille café-luft 😭",
            "pause_ok": "pausiere kurz die cozy vibes 🌿☕",
            "resume_nothing": "es gibt nichts fortzusetzen, die lautsprecher sind noch still 😭",
            "resume_ok": "die warmen café-vibes laufen wieder 🎶☕",
            "skip_nothing": "was soll ich skippen… die stille? die playlist ist leer 😭",
            "skip_ok": "springe zum nächsten geschmack auf der karte 🍰✨",
            "stop_nothing": "es gibt nichts zu stoppen, die café-lautsprecher sind schon ruhig 🌙",
            "stop_ok": "okay okay, ich stoppe alles und leere die warteschlange ☕💛",
            "queue_empty": "die warteschlange ist leerer als ein café nach feierabend 😭",
            "queue_header": "☕ **aktuelle cozy-warteschlange:**",
            "volume_nothing": "es gibt keinen aktiven player zum anpassen, noch keine musik am start 😭",
            "volume_set": "lautstärke auf **{vol}%** gesetzt — café-stimmung angepasst ✨",
            "disconnect_nothing": "ich bin gar nicht im sprachkanal, nur hinterm tresen am chillen 😭",
            "disconnect_ok": "ich verlasse den vc wie ein leiser barista-wink, bis später ☕🌿",
        },
    },
}


def get_lang(ctx: commands.Context) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def msg(ctx: commands.Context, key: str, **kwargs) -> str:
    personality = get_personality(ctx)
    lang = get_lang(ctx)
    base = MESSAGES.get(personality, {})
    text = base.get(lang, {}).get(key)
    if text is None:
        text = base.get("en", {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


# ─────────────────────────────────────────────────────────────
#  LAVALINK NODE DISCOVERY
# ─────────────────────────────────────────────────────────────

AJIE_ALL = "https://lavalink-list.ajieblogs.eu.org/All"
PROBE_TIMEOUT = 3.0    # seconds for HTTP health-check
CONNECT_TIMEOUT = 20.0  # seconds for wavelink handshake
MAX_PROBE_WORKERS = 8  # concurrent HTTP probes


async def _fetch_node_list() -> list[dict]:
    """Fetch the node list from AjieBlogs. Returns v4 nodes only."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(AJIE_ALL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json(content_type=None)
                # Only keep Lavalink v4 nodes
                v4 = [n for n in data if n.get("version", "v4") == "v4"]
                return v4
    except Exception:
        return []


async def _probe_node(
    session: aiohttp.ClientSession,
    node: dict,
    sem: asyncio.Semaphore,
) -> tuple[dict, float] | None:
    """
    Silently HTTP-probe a single node at /version.
    Returns (node, latency_ms) if alive, None otherwise.
    No logging — we only report the aggregate outcome.
    """
    host = node["host"]
    port = node["port"]
    secure = node.get("secure", False)
    scheme = "https" if secure else "http"
    url = f"{scheme}://{host}:{port}/version"

    async with sem:
        try:
            t0 = _time.monotonic()
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=PROBE_TIMEOUT),
                ssl=False,
            ) as resp:
                if resp.status == 200:
                    return (node, (_time.monotonic() - t0) * 1000)
        except Exception:
            pass
    return None


async def _find_responsive_nodes(nodes: list[dict]) -> list[dict]:
    """
    Probe all nodes concurrently and return those that replied,
    sorted by ascending latency.  Produces a single summary log line.
    """
    sem = asyncio.Semaphore(MAX_PROBE_WORKERS)
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *[_probe_node(session, n, sem) for n in nodes],
            return_exceptions=True,
        )

    alive = [
        r for r in results
        if r is not None and not isinstance(r, BaseException)
    ]
    alive.sort(key=lambda x: x[1])

    if alive:
        summary = ", ".join(
            f"{n['host']}:{n['port']} ({lat:.0f}ms)"
            for n, lat in alive[:4]
        )
        log.info("Lavalink", f"{len(alive)}/{len(nodes)} nodes responsive — {summary}")
    else:
        log.warning("Lavalink", f"No nodes responded out of {len(nodes)} tried.")

    return [n for n, _ in alive]


# ─────────────────────────────────────────────────────────────
#  MUSIC COG
# ─────────────────────────────────────────────────────────────

class MusicSystem(commands.Cog):
    """Music system — cozy personality-aware responses with smart node selection."""

    def __init__(self, bot):
        self.bot = bot
        self.connected = False
        self._connecting = False
        bot.loop.create_task(self.startup_connect())

    # ─── NODE CONNECTION ─────────────────────────────────────

    async def startup_connect(self, *, retry_delay: float = 0):
        """Fetch nodes, probe them silently, connect to the fastest available one."""
        if self._connecting:
            return
        self._connecting = True

        if retry_delay:
            await asyncio.sleep(retry_delay)

        await self.bot.wait_until_ready()

        raw_nodes = await _fetch_node_list()
        if not raw_nodes:
            log.warning("Lavalink", "Could not fetch node list from AjieBlogs API.")
            self._connecting = False
            return

        responsive = await _find_responsive_nodes(raw_nodes)
        if not responsive:
            log.warning("Lavalink", "No responsive Lavalink nodes found. Music unavailable.")
            self._connecting = False
            return

        # Try each responsive node until one connects
        for node_info in responsive:
            host = node_info["host"]
            port = node_info["port"]
            password = node_info["password"]
            secure = node_info.get("secure", False)
            uri = f"{'https' if secure else 'http'}://{host}:{port}"

            try:
                node = wavelink.Node(uri=uri, password=password)
                await asyncio.wait_for(
                    wavelink.Pool.connect(nodes=[node], client=self.bot),
                    timeout=CONNECT_TIMEOUT,
                )
                log.info("Lavalink", f"Connected to {host}:{port} (SSL={secure})")
                self.connected = True
                self._connecting = False
                return
            except Exception:
                # Quietly try the next node — user already saw the probe summary
                try:
                    await wavelink.Pool.close()
                except Exception:
                    pass

        log.warning("Lavalink", "All responsive nodes failed the wavelink handshake.")
        self._connecting = False

    # ─── NODE EVENTS ─────────────────────────────────────────

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        log.info("Lavalink", f"Node '{payload.node.identifier}' ready (resumed={payload.resumed})")

    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list):
        """Fires when a node's websocket closes. Attempt to reconnect after a short delay."""
        log.warning("Lavalink", f"Node '{node.identifier}' closed. Reconnecting in 10s…")
        self.connected = False
        self.bot.loop.create_task(self.startup_connect(retry_delay=10))

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        """Advance to the next queued track, or disconnect when the queue is empty."""
        player = payload.player
        if player is None:
            return
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)
        else:
            # Auto-disconnect once all tracks have finished
            await asyncio.sleep(300)  # 5 minutes idle grace period
            if player and not player.playing:
                await player.disconnect()

    # ─── PLAYER HELPERS ──────────────────────────────────────

    async def get_player(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send(msg(ctx, "get_player_not_in_voice"))
            return None

        channel = ctx.author.voice.channel
        player = ctx.voice_client

        if player is None:
            player = await channel.connect(cls=wavelink.Player)

        return player

    # ─── COMMANDS ────────────────────────────────────────────

    @commands.command(
        name="musicstatus",
        help="{ 'en': 'check if niko is connected to a music server ☕', 'de': 'prüfe ob niko verbunden ist' }"
    )
    async def music_status(self, ctx: commands.Context):
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {msg(ctx, 'music_player_status_title')}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        if not self.connected:
            container.add_item(discord.ui.TextDisplay(content=msg(ctx, "music_not_connected")))
            container.add_item(discord.ui.TextDisplay(content=f"-# {get_emoji('wavelink')} Powered by Wavelink"))
            view.add_item(container)
            return await ctx.send(view=view)
        container.add_item(discord.ui.TextDisplay(content=msg(ctx, "music_connected")))
        container.add_item(discord.ui.TextDisplay(content=f"-# {get_emoji('wavelink')} Powered by Wavelink"))
        view.add_item(container)
        await ctx.send(view=view)

    @commands.command(
        name="play",
        aliases=["p"],
        help="{ 'en': 'brew a cozy track for your ears ☕🎶', 'de': 'spiele einen track ab' }"
    )
    async def play(self, ctx: commands.Context, *, search: str):
        player = await self.get_player(ctx)
        if not player:
            return

        # Support raw URLs and search queries
        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await ctx.send(msg(ctx, "play_not_found"))

        # If a playlist was returned, use the first track
        track = tracks[0] if isinstance(tracks, list) else tracks

        if not player.playing:
            await player.play(track)
            await ctx.send(msg(ctx, "play_start", title=track.title))
        else:
            player.queue.put(track)
            await ctx.send(msg(ctx, "play_queued", title=track.title))

    @commands.command(
        name="pause",
        help="{ 'en': 'gently pause the current vibes 🌿', 'de': 'pausiert den aktuellen track' }"
    )
    async def pause(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "pause_nothing"))
        await player.pause(True)
        await ctx.send(msg(ctx, "pause_ok"))

    @commands.command(
        name="resume",
        help="{ 'en': 'bring the cozy vibes back ☕🎶', 'de': 'setzt den pausierten track fort' }"
    )
    async def resume(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "resume_nothing"))
        await player.pause(False)
        await ctx.send(msg(ctx, "resume_ok"))

    @commands.command(
        name="skip",
        aliases=["s"],
        help="{ 'en': 'skip to the next flavor on the playlist 🍰', 'de': 'springt zum nächsten track' }"
    )
    async def skip(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "skip_nothing"))
        await player.skip()
        await ctx.send(msg(ctx, "skip_ok"))

    @commands.command(
        name="stop",
        help="{ 'en': 'stop playback and clear the queue ☕', 'de': 'stoppt die wiedergabe' }"
    )
    async def stop(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "stop_nothing"))
        await player.stop()
        player.queue.clear()
        await ctx.send(msg(ctx, "stop_ok"))

    @commands.command(
        name="queue",
        aliases=["q"],
        help="{ 'en': 'see whats on the cozy playlist ☕📜', 'de': 'zeigt die warteschlange' }"
    )
    async def queue(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "queue_empty"))

        lines = [msg(ctx, "queue_header")]
        for i, track in enumerate(player.queue, start=1):
            lines.append(f"{i}. {track.title}")
            if i >= 10:
                remaining = len(player.queue) - 10
                if remaining > 0:
                    lines.append(f"…and {remaining} more")
                break

        await ctx.send("\n".join(lines))

    @commands.command(
        name="nowplaying",
        aliases=["np"],
        help="{ 'en': 'see whats brewing right now ☕🎵', 'de': 'zeigt den aktuellen track' }"
    )
    async def nowplaying(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "pause_nothing"))

        track = player.current
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### ☕🎵 Now Playing\n"
                    f"**{track.title}**\n"
                    f"by {track.author or 'Unknown'}"
                )
            )
        ))
        if track.uri:
            view.add_item(discord.ui.ActionRow(
                discord.ui.Button(
                    label="Open Track",
                    style=discord.ButtonStyle.link,
                    url=track.uri,
                )
            ))
        await ctx.send(view=view)

    @commands.command(
        name="volume",
        aliases=["vol"],
        help="{ 'en': 'adjust the café ambiance volume ✨', 'de': 'passt die lautstärke an' }"
    )
    async def volume(self, ctx: commands.Context, vol: int):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "volume_nothing"))
        vol = max(0, min(vol, 100))
        await player.set_volume(vol)
        await ctx.send(msg(ctx, "volume_set", vol=vol))

    @commands.command(
        name="disconnect",
        aliases=["dc", "leave"],
        help="{ 'en': 'have niko leave the voice channel softly ☕', 'de': 'trennt niko vom sprachkanal' }"
    )
    async def disconnect(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "disconnect_nothing"))
        await player.disconnect()
        await ctx.send(msg(ctx, "disconnect_ok"))


async def setup(bot):
    await bot.add_cog(MusicSystem(bot))
