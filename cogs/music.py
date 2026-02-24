import asyncio
import aiohttp
import wavelink
from discord.ext import commands
import discord
import random
from utils.logging import info, warning, error

# personality mode: "normal" or "cafe" (future modes can be added easily)
PERSONALITY = "cafe"

MESSAGES = {
    "normal": {
        "en": {
            "not_in_voice": "You need to be in a voice channel first.",
            "get_player_not_in_voice": "You need to be in a voice channel to use music commands.",
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
            "get_player_not_in_voice": "you’re not in a voice channel yet, i can’t serve music there 😭☕",
            "music_not_connected": "hmm… i’m not connected to any music servers right now, like a café with no music on 😭",
            "music_connected": "yesss, i’m connected and ready to pour some cozy tracks ☕✨",
            "play_not_found": "i couldn’t find that song, like a drink that’s not on the menu 😭",
            "play_start": "brewing **{title}** for your ears right now ☕🎶",
            "play_queued": "added **{title}** to the queue, it’s waiting like a drink order on the counter 🍪✨",
            "pause_nothing": "there’s nothing playing to pause, just quiet café air rn 😭",
            "pause_ok": "pausing the cozy vibes for a moment 🌿☕",
            "resume_nothing": "there’s nothing paused to resume, the speakers are still empty 😭",
            "resume_ok": "bringing the warm café vibes back on 🎶☕",
            "skip_nothing": "skip what… the silence? the playlist is empty rn 😭",
            "skip_ok": "skipping to the next flavor on the menu 🍰✨",
            "stop_nothing": "there’s nothing to stop, the café speakers are already quiet 🌙",
            "stop_ok": "okay okay, stopping everything and clearing the tray ☕💛",
            "queue_empty": "the queue is emptier than a café at closing time 😭",
            "queue_header": "☕ **current cozy queue:**",
            "volume_nothing": "there’s no active player to adjust, no music brewing yet 😭",
            "volume_set": "volume set to **{vol}%** — adjusting the café ambiance ✨",
            "disconnect_nothing": "i’m not even in a voice channel, just chilling behind the counter 😭",
            "disconnect_ok": "leaving the vc like a soft barista wave, see you soon ☕🌿",
        },
        "de": {
            "not_in_voice": "hey liebchen, du musst erst in einen Sprachkanal gehen ☕💿",
            "get_player_not_in_voice": "du bist noch in keinem Sprachkanal, ich kann dort keine musik servieren 😭☕",
            "music_not_connected": "hmm… ich bin gerade mit keinem musikserver verbunden, wie ein café ohne musik 😭",
            "music_connected": "yesss, ich bin verbunden und bereit für cozy tracks ☕✨",
            "play_not_found": "ich konnte den song nicht finden, wie ein drink, der nicht auf der karte steht 😭",
            "play_start": "brühe gerade **{title}** für deine ohren auf ☕🎶",
            "play_queued": "**{title}** wurde zur warteschlange hinzugefügt, wartet wie eine bestellung auf der theke 🍪✨",
            "pause_nothing": "es läuft nichts zum pausieren, nur stille café‑luft 😭",
            "pause_ok": "pausiere kurz die cozy vibes 🌿☕",
            "resume_nothing": "es gibt nichts fortzusetzen, die lautsprecher sind noch still 😭",
            "resume_ok": "die warmen café‑vibes laufen wieder 🎶☕",
            "skip_nothing": "was soll ich skippen… die stille? die playlist ist leer 😭",
            "skip_ok": "springe zum nächsten geschmack auf der karte 🍰✨",
            "stop_nothing": "es gibt nichts zu stoppen, die café‑lautsprecher sind schon ruhig 🌙",
            "stop_ok": "okay okay, ich stoppe alles und leere die warteschlange ☕💛",
            "queue_empty": "die warteschlange ist leerer als ein café nach feierabend 😭",
            "queue_header": "☕ **aktuelle cozy‑warteschlange:**",
            "volume_nothing": "es gibt keinen aktiven player zum anpassen, noch keine musik am start 😭",
            "volume_set": "lautstärke auf **{vol}%** gesetzt — café‑stimmung angepasst ✨",
            "disconnect_nothing": "ich bin gar nicht im sprachkanal, nur hinterm tresen am chillen 😭",
            "disconnect_ok": "ich verlasse den vc wie ein leiser barista‑wink, bis später ☕🌿",
        },
    },
    # future personalities can be added here, e.g. "soft", "spicy", "gremlin"
}


def get_lang(ctx: commands.Context) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def get_personality() -> str:
    return PERSONALITY if PERSONALITY in MESSAGES else "normal"


def msg(ctx: commands.Context, key: str, **kwargs) -> str:
    personality = get_personality()
    lang = get_lang(ctx)

    # try personality + lang
    base = MESSAGES.get(personality, {})
    lang_block = base.get(lang, {})
    text = lang_block.get(key)

    # fallback: personality + en
    if text is None:
        text = base.get("en", {}).get(key)

    # fallback: normal + lang
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)

    # fallback: normal + en
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)

    return text.format(**kwargs) if kwargs else text


AJIE_ALL = "https://lavalink-list.ajieblogs.eu.org/All"


class MusicSystem(commands.Cog):
    """Music system with cozy personality‑aware responses."""

    def __init__(self, bot):
        self.bot = bot
        self.connected = False
        bot.loop.create_task(self.startup_connect())

    async def fetch_nodes(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(AJIE_ALL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        error("Lavalink", f"Failed to fetch AjieBlogs list: {resp.status}")
                        return []
                    data = await resp.json()
                    info("Lavalink", f"Loaded {len(data)} nodes from AjieBlogs API.")
                    return data
            except Exception as e:
                error("Lavalink", f"Error fetching AjieBlogs list: {e}")
                return []

    async def try_connect_node(self, node_info):
        try:
            host = node_info["host"]
            port = node_info["port"]
            password = node_info["password"]
            secure = node_info.get("secure", False)

            uri = f"{'https' if secure else 'http'}://{host}:{port}"

            node = wavelink.Node(uri=uri, password=password)
            await asyncio.wait_for(
                wavelink.Pool.connect(nodes=[node], client=self.bot),
                timeout=8
            )

            info("Lavalink", f"Connected to {host}:{port} (SSL={secure})")
            self.connected = True
            return True
        except asyncio.TimeoutError:
            warning("Lavalink", f"Timed out connecting to {node_info['host']}:{node_info['port']}")
            try:
                await wavelink.Pool.close()
            except Exception:
                error("Lavalink", f"Failed to close connection to {node_info['host']}:{node_info['port']}")
            return False
        except Exception as e:
            error("Lavalink", f"Failed node {node_info['host']}:{node_info['port']} SSL={node_info.get('secure', False)} -> {e}")
            try:
                await wavelink.Pool.close()
            except Exception:
                error("Lavalink", f"Failed to close connection to {node_info['host']}:{node_info['port']}")
            return False

    async def startup_connect(self):
        await self.bot.wait_until_ready()

        nodes = await self.fetch_nodes()
        if not nodes:
            warning("Lavalink", "No nodes available from AjieBlogs API.")
            return

        random.shuffle(nodes)

        for node_info in nodes:
            if await self.try_connect_node(node_info):
                return

        error("Lavalink", "All nodes failed to connect.")

    async def get_player(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send(msg(ctx, "get_player_not_in_voice"))
            return None

        channel = ctx.author.voice.channel
        player = ctx.voice_client

        if player is None:
            player = await channel.connect(cls=wavelink.Player)

        return player

    @commands.command(
        name="musicstatus",
        help="check if niko is connected to a music server ☕ | prüfe, ob niko mit einem musikserver verbunden ist"
    )
    async def music_status(self, ctx: commands.Context):
        """Check if the bot is connected to a music server."""
        if not self.connected:
            return await ctx.send(msg(ctx, "music_not_connected"))

        await ctx.send(msg(ctx, "music_connected"))

    @commands.command(
        name="play",
        aliases=["p"],
        help="brew a cozy track for your ears ☕🎶 | spiele einen gemütlichen track ab"
    )
    async def play(self, ctx: commands.Context, *, search: str):
        """Play a song in a voice channel."""
        player = await self.get_player(ctx)
        if not player:
            return

        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await ctx.send(msg(ctx, "play_not_found"))

        track = tracks[0]

        if not player.playing:
            await player.play(track)
            await ctx.send(msg(ctx, "play_start", title=track.title))
        else:
            player.queue.put(track)
            await ctx.send(msg(ctx, "play_queued", title=track.title))

    @commands.command(
        name="pause",
        help="gently pause the current vibes 🌿 | pausiert den aktuellen track"
    )
    async def pause(self, ctx: commands.Context):
        """Pause the currently playing song."""
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "pause_nothing"))

        await player.pause(True)
        await ctx.send(msg(ctx, "pause_ok"))

    @commands.command(
        name="resume",
        help="bring the cozy vibes back ☕🎶 | setzt den pausierten track fort"
    )
    async def resume(self, ctx: commands.Context):
        """Resume the currently paused song."""
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "resume_nothing"))

        await player.pause(False)
        await ctx.send(msg(ctx, "resume_ok"))

    @commands.command(
        name="skip",
        help="skip to the next flavor on the playlist 🍰 | springt zum nächsten track"
    )
    async def skip(self, ctx: commands.Context):
        """Skip the currently playing song."""
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(msg(ctx, "skip_nothing"))

        await player.skip()
        await ctx.send(msg(ctx, "skip_ok"))

    @commands.command(
        name="stop",
        help="stop playback and clear the queue ☕ | stoppt die wiedergabe und leert die warteschlange"
    )
    async def stop(self, ctx: commands.Context):
        """Stop the player and clear the queue."""
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "stop_nothing"))

        await player.stop()
        player.queue.clear()
        await ctx.send(msg(ctx, "stop_ok"))

    @commands.command(
        name="queue",
        aliases=["q"],
        help="see what’s on the cozy playlist ☕📜 | zeigt die aktuelle warteschlange"
    )
    async def queue(self, ctx: commands.Context):
        """Show the current queue."""
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(msg(ctx, "queue_empty"))

        header = msg(ctx, "queue_header")
        lines = [header]
        for i, track in enumerate(player.queue, start=1):
            lines.append(f"{i}. {track.title}")

        await ctx.send("\n".join(lines))

    @commands.command(
        name="volume",
        aliases=["vol"],
        help="adjust the café ambiance volume ✨ | passt die lautstärke an"
    )
    async def volume(self, ctx: commands.Context, vol: int):
        """Adjust the volume of the player."""
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "volume_nothing"))

        vol = max(0, min(vol, 100))
        await player.set_volume(vol)
        await ctx.send(msg(ctx, "volume_set", vol=vol))

    @commands.command(
        name="disconnect",
        aliases=["dc", "leave"],
        help="have niko leave the voice channel softly ☕ | trennt niko vom sprachkanal"
    )
    async def disconnect(self, ctx: commands.Context):
        """Disconnect the bot from the voice channel."""
        player = ctx.voice_client
        if not player:
            return await ctx.send(msg(ctx, "disconnect_nothing"))

        await player.disconnect()
        await ctx.send(msg(ctx, "disconnect_ok"))


async def setup(bot):
    await bot.add_cog(MusicSystem(bot))