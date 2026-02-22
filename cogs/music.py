import asyncio
import aiohttp
import wavelink
from discord.ext import commands
import discord
import random

PERSONALITY = "gremlin"

SOFT = [
    "yaaay bestie I got your song queued up ✨🎶",
    "omg the vibes are immaculate already (≧◡≦)",
    "bestie your music taste is so cute I can't 💖",
]

SPICY = [
    "ugh fine I'll play your lil song 💅",
    "okay queen I see you with the taste",
    "this track better not flop like your ex",
]

GREMLIN = [
    "OMG YES LET'S SUMMON THE DEMON OF MUSIC 😭🔥✨",
    "BESTIE THIS SONG IS ABOUT TO GO FERALLLL",
    "I'M BLASTING THIS LIKE A GREMLIN IN A SUBWOOFER 😈🌈",
]

NORMAL = [
    "Playing your track.",
    "Added to queue.",
    "Okay.",
]


def vibe():
    if PERSONALITY == "soft":
        return random.choice(SOFT)
    if PERSONALITY == "spicy":
        return random.choice(SPICY)
    if PERSONALITY == "gremlin":
        return random.choice(GREMLIN)
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
                        print(f"[Lavalink] Failed to fetch AjieBlogs list: {resp.status}")
                        return []
                    data = await resp.json()
                    print(f"[Lavalink] Loaded {len(data)} nodes from AjieBlogs API.")
                    return data
            except Exception as e:
                print(f"[Lavalink] Error fetching AjieBlogs list: {e}")
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

            print(f"[Lavalink] Connected to {host}:{port} (SSL={secure})")
            print("[Personality]", vibe())
            self.connected = True
            return True
        except asyncio.TimeoutError:
            print(f"[Lavalink] Timed out connecting to {node_info['host']}:{node_info['port']}")
            try:
                await wavelink.Pool.close()
            except Exception:
                pass
            return False
        except Exception as e:
            print(f"[Lavalink] Failed node {node_info['host']}:{node_info['port']} SSL={node_info.get('secure', False)} -> {e}")
            try:
                await wavelink.Pool.close()
            except Exception:
                pass
            return False

    async def startup_connect(self):
        await self.bot.wait_until_ready()

        nodes = await self.fetch_nodes()
        if not nodes:
            print("[Lavalink] No nodes available from AjieBlogs API.")
            return

        random.shuffle(nodes)

        for node_info in nodes:
            if await self.try_connect_node(node_info):
                return

        print("[Lavalink] All nodes failed to connect.")

    async def get_player(self, ctx):
        if not ctx.author.voice:
            await ctx.send("bestie you're not even in a voice channel 😭")
            return None

        channel = ctx.author.voice.channel
        player = ctx.voice_client

        if player is None:
            player = await channel.connect(cls=wavelink.Player)

        return player

    @commands.command(name="musicstatus")
    async def music_status(self, ctx):
        """Check if the bot is connected to a music server."""
        if not self.connected:
            msg = (
                "bestie… I'm not connected to ANY music servers rn 😭"
                if PERSONALITY != "normal"
                else "Not connected to any Lavalink nodes."
            )
            return await ctx.send(msg)

        msg = (
            "yaaas I'm connected to a music server and ready to serve ✨🎶"
            if PERSONALITY != "normal"
            else "Connected to a Lavalink node."
        )
        await ctx.send(msg)

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        """Play a song in a voice channel."""
        player = await self.get_player(ctx)
        if not player:
            return

        tracks = await wavelink.Playable.search(search)
        if not tracks:
            await ctx.send("bestie I couldn't find that song 😭")
            return

        track = tracks[0]

        if not player.playing:
            await player.play(track)
            await ctx.send(f"{vibe()} — now playing **{track.title}** 🎧")
        else:
            player.queue.put(track)
            await ctx.send(f"{vibe()} — added **{track.title}** to the queue 💖")

    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pause the currently playing song."""
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send("bestie there's literally nothing playing 😭")

        await player.pause(True)
        await ctx.send(f"{vibe()} — pausing the vibes ✨")

    @commands.command(name="resume")
    async def resume(self, ctx):
        """Resume the currently paused song."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("bestie nothing is paused rn 😭")

        await player.pause(False)
        await ctx.send(f"{vibe()} — the vibes are BACK 🎶✨")

    @commands.command(name="skip")
    async def skip(self, ctx):
        """Skip the currently playing song."""
        player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send("skip what babe… the silence? 😭")

        await player.skip()
        await ctx.send(f"{vibe()} — skipped like a messy breakup 💅")

    @commands.command(name="stop")
    async def stop(self, ctx):
        player = ctx.voice_client
        if not player:
            return await ctx.send("there's nothing to stop bestie 😭")

        await player.stop()
        player.queue.clear()
        await ctx.send(f"{vibe()} — okay fine I stopped EVERYTHING 😭✨")

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        """Show the current queue."""
        player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send("the queue is emptier than my love life 😭")

        msg = "**Current Queue:**\n"
        for i, track in enumerate(player.queue, start=1):
            msg += f"{i}. {track.title}\n"

        await ctx.send(msg)

    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx, vol: int):
        """Adjust the volume of the player."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("bestie nothing is even playing 😭")

        vol = max(0, min(vol, 100))
        await player.set_volume(vol)
        await ctx.send(f"{vibe()} — volume set to **{vol}%** ✨")

    @commands.command(name="disconnect", aliases=["dc", "leave"])
    async def disconnect(self, ctx):
        """Disconnect the bot from the voice channel."""
        player = ctx.voice_client
        if not player:
            return await ctx.send("I'm not even in a VC babe 😭")

        await player.disconnect()
        await ctx.send(f"{vibe()} — fine I left the VC like a dramatic queen 💅")


async def setup(bot):
    await bot.add_cog(MusicSystem(bot))
