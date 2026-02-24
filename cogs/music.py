import asyncio
import aiohttp
import wavelink
from discord.ext import commands
import discord
import random
from utils.logging import info, warning, error

# Set to either "cafe" or "normal"
PERSONALITY = "cafe"  # soft café‑vibe default

CAFE_SOFT = [
    "okay bestie, your song is brewing ☕✨",
    "aww this track feels like warm sunlight through a café window (≧◡≦)🌿",
    "your music taste is like… cinnamon‑sweet?? i love it sm 🍪💛",
]

CAFE_GERMAN = [
    "alles klar liebchen, dein song läuft gleich ☕✨",
    "ohhh das fühlt sich an wie ein ruhiger morgen im café (˘͈ᵕ ˘͈♡)🌿",
    "dein musikgeschmack ist so cozy ich kann nicht 🍪💛",
]

CAFE_PLAYFUL = [
    "one cozy track coming right up, like a lil latte for your ears ☕🎶",
    "okay okay, i see you ordering the *fancy* vibes today ✨",
    "this song is giving soft lo‑fi café energy and i’m here for it 🌿",
]

NORMAL = [
    "Playing your track.",
    "Added to queue.",
    "Okay.",
]


def vibe(ctx=None):
    lang = "de" if ctx and ctx.guild and ctx.guild.preferred_locale.startswith("de") else "en"

    if PERSONALITY == "cafe":
        if lang == "de":
            return random.choice(CAFE_GERMAN)
        return random.choice(CAFE_SOFT + CAFE_PLAYFUL)

    return random.choice(NORMAL)


AJIE_ALL = "https://lavalink-list.ajieblogs.eu.org/All"


class MusicSystem(commands.Cog):

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

    async def get_player(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("uhh bestie… du bist nicht mal im voice channel 😭☕")

        channel = ctx.author.voice.channel
        player = ctx.voice_client

        if player is None:
            player = await channel.connect(cls=wavelink.Player)

        return player

    @commands.command(name="musicstatus")
    async def music_status(self, ctx):
        if not self.connected:
            return await ctx.send("hmm… ich bin grad mit keinem musikserver verbunden 😭☕")

        await ctx.send("yesss, i’m connected + ready to play cozy café vibes ✨🎶")

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        player = await self.get_player(ctx)
        if not player:
            return

        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await ctx.send("konnte den song nicht finden liebchen 😭🌿")

        track = tracks[0]

        if not player.playing:
            await player.play(track)
            await ctx.send(f"{vibe(ctx)} — now playing **{track.title}** 🎧☕")
        else:
            player.queue.put(track)
            await ctx.send(f"{vibe(ctx)} — added **{track.title}** to the queue 🍪✨")

    @commands.command(name="pause")
    async def pause(self, ctx):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send("there’s nothing playing rn babe 😭☕")

        await player.pause(True)
        await ctx.send(f"{vibe(ctx)} — pausing the cozy vibes 🌿")

    @commands.command(name="resume")
    async def resume(self, ctx):
        player = ctx.voice_client
        if not player:
            return await ctx.send("nichts zum fortsetzen da 😭")

        await player.pause(False)
        await ctx.send(f"{vibe(ctx)} — vibes resumed ✨🎶")

    @commands.command(name="skip")
    async def skip(self, ctx):
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send("skip what… the silence? 😭☕")

        await player.skip()
        await ctx.send(f"{vibe(ctx)} — skipped like turning a café page 🍂")

    @commands.command(name="stop")
    async def stop(self, ctx):
        player = ctx.voice_client
        if not player:
            return await ctx.send("there’s nothing to stop babe 😭")

        await player.stop()
        player.queue.clear()
        await ctx.send(f"{vibe(ctx)} — okay okay, stopping everything ☕💛")

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send("the queue is emptier than a café at closing time 😭")

        msg = "**current queue:**\n"
        for i, track in enumerate(player.queue, start=1):
            msg += f"{i}. {track.title}\n"

        await ctx.send(msg)

    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx, vol: int):
        player = ctx.voice_client
        if not player:
            return await ctx.send("nothing is playing rn 😭")

        vol = max(0, min(vol, 100))
        await player.set_volume(vol)
        await ctx.send(f"{vibe(ctx)} — volume set to **{vol}%** ☕✨")

    @commands.command(name="disconnect", aliases=["dc", "leave"])
    async def disconnect(self, ctx):
        player = ctx.voice_client
        if not player:
            return await ctx.send("i’m not even in vc babe 😭")

        await player.disconnect()
        await ctx.send(f"{vibe(ctx)} — leaving the vc like a soft lil barista wave 🌿☕")


async def setup(bot):
    await bot.add_cog(MusicSystem(bot))