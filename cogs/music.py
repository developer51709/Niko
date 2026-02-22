import aiohttp
import wavelink
from discord.ext import commands
import discord
import random

# ===================================
# PERSONALITY TOGGLE
# ===================================
# Options:
#   "soft"    = soft gay chaos
#   "spicy"   = spicy gay chaos
#   "gremlin" = unhinged gremlin gay chaos
#   "normal"  = boring mode for boring people
#
# Self-hosters can change this to whatever they want.
# ===================================

PERSONALITY = "gremlin"


# ===================================
# PERSONALITY RESPONSE POOLS
# ===================================

SOFT = [
    "yaaay bestie I got your song queued up ✨🎶",
    "omg the vibes are immaculate already (≧◡≦)",
    "bestie your music taste is so cute I can’t 💖",
]

SPICY = [
    "ugh fine I’ll play your lil song 💅",
    "okay queen I see you with the taste",
    "this track better not flop like your ex",
]

GREMLIN = [
    "OMG YES LET’S SUMMON THE DEMON OF MUSIC 😭🔥✨",
    "BESTIE THIS SONG IS ABOUT TO GO FERALLLL",
    "I’M BLASTING THIS LIKE A GREMLIN IN A SUBWOOFER 😈🌈",
]

NORMAL = [
    "Playing your track.",
    "Added to queue.",
    "Okay.",
]


def vibe():
    """Return a personality‑appropriate message."""
    if PERSONALITY == "soft":
        return random.choice(SOFT)
    if PERSONALITY == "spicy":
        return random.choice(SPICY)
    if PERSONALITY == "gremlin":
        return random.choice(GREMLIN)
    return random.choice(NORMAL)


# ===================================
# PUBLIC LAVALINK NODE SOURCES
# ===================================
# These URLs should point to JSON lists of public Lavalink nodes.
# You can add multiple sources for redundancy.
# ===================================

PUBLIC_NODE_LISTS = [
    "https://lavalink-list.example/api/nodes.json",   # placeholder
    "https://another-source.example/nodes.json",      # placeholder
]


# ===================================
# MAIN COG
# ===================================

class MusicSystem(commands.Cog):
    """Unified Lavalink auto-connect + full music command system."""

    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.startup_connect())

    # -------------------------------
    # FETCH PUBLIC LAVALINK NODES
    # -------------------------------
    async def fetch_public_nodes(self):
        """Fetch node lists from multiple public sources."""
        nodes = []

        async with aiohttp.ClientSession() as session:
            for url in PUBLIC_NODE_LISTS:
                try:
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            nodes.extend(data)
                except:
                    continue

        return nodes

    # -------------------------------
    # CONNECT TO A NODE
    # -------------------------------
    async def connect_to_node(self, node):
        """Try connecting to a single Lavalink node."""
        try:
            await wavelink.NodePool.create_node(
                bot=self.bot,
                host=node["host"],
                port=node["port"],
                password=node["password"],
                https=node.get("secure", False)
            )
            print(f"[Lavalink] Connected to {node['host']}")
            print("[Personality]", vibe())
            return True
        except Exception as e:
            print(f"[Lavalink] Failed node {node['host']}: {e}")
            return False

    # -------------------------------
    # STARTUP CONNECTION LOGIC
    # -------------------------------
    async def startup_connect(self):
        """Runs at bot startup: fetch nodes, test them, connect to one."""
        await self.bot.wait_until_ready()

        nodes = await self.fetch_public_nodes()

        if not nodes:
            print("[Lavalink] No public nodes found.")
            return

        random.shuffle(nodes)

        for node in nodes:
            if await self.connect_to_node(node):
                return

        print("[Lavalink] All public nodes failed.")

    # -------------------------------
    # AUTO-FAILOVER
    # -------------------------------
    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node, reason):
        """If a node dies, try to reconnect to another one."""
        print(f"[Lavalink] Node died: {reason}")
        print("[Personality]", vibe())
        await self.startup_connect()

    # -------------------------------
    # HELPER: GET OR CREATE PLAYER
    # -------------------------------
    async def get_player(self, ctx):
        """Returns the guild's music player, connecting if needed."""
        if not ctx.author.voice:
            await ctx.send("bestie you’re not even in a voice channel 😭")
            return None

        channel = ctx.author.voice.channel

        # If player exists, return it
        if ctx.guild.id in self.bot.wavelink.players:
            return self.bot.wavelink.players[ctx.guild.id]

        # Otherwise create a new player
        player = await channel.connect(cls=wavelink.Player)
        return player

    # -------------------------------
    # !play
    # -------------------------------
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        """Play a song or add it to the queue."""
        player = await self.get_player(ctx)
        if not player:
            return

        tracks = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.send("bestie I couldn’t find that song 😭")
            return

        track = tracks[0]

        if not player.is_playing():
            await player.play(track)
            await ctx.send(f"{vibe()} — now playing **{track.title}** 🎧")
        else:
            player.queue.put(track)
            await ctx.send(f"{vibe()} — added **{track.title}** to the queue 💖")

    # -------------------------------
    # !pause
    # -------------------------------
    @commands.command(name="pause")
    async def pause(self, ctx):
        player = self.bot.wavelink.players.get(ctx.guild.id)
        if not player or not player.is_playing():
            return await ctx.send("bestie there’s literally nothing playing 😭")

        await player.pause()
        await ctx.send(f"{vibe()} — pausing the vibes ✨")

    # -------------------------------
    # !resume
    # -------------------------------
    @commands.command(name="resume")
    async def resume(self, ctx):
        player = self.bot.wavelink.players.get(ctx.guild.id)
        if not player:
            return await ctx.send("bestie nothing is paused rn 😭")

        await player.resume()
        await ctx.send(f"{vibe()} — the vibes are BACK 🎶✨")

    # -------------------------------
    # !skip
    # -------------------------------
    @commands.command(name="skip")
    async def skip(self, ctx):
        player = self.bot.wavelink.players.get(ctx.guild.id)
        if not player or not player.is_playing():
            return await ctx.send("skip what babe… the silence? 😭")

        await player.stop()
        await ctx.send(f"{vibe()} — skipped like a messy breakup 💅")

    # -------------------------------
    # !stop
    # -------------------------------
    @commands.command(name="stop")
    async def stop(self, ctx):
        player = self.bot.wavelink.players.get(ctx.guild.id)
        if not player:
            return await ctx.send("there’s nothing to stop bestie 😭")

        await player.stop()
        player.queue.clear()
        await ctx.send(f"{vibe()} — okay fine I stopped EVERYTHING 😭✨")

    # -------------------------------
    # !queue
    # -------------------------------
    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        player = self.bot.wavelink.players.get(ctx.guild.id)
        if not player or player.queue.is_empty:
            return await ctx.send("the queue is emptier than my love life 😭")

        msg = "**Current Queue:**\n"
        for i, track in enumerate(player.queue, start=1):
            msg += f"{i}. {track.title}\n"

        await ctx.send(msg)

    # -------------------------------
    # !volume
    # -------------------------------
    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx, vol: int):
        player = self.bot.wavelink.players.get(ctx.guild.id)
        if not player:
            return await ctx.send("bestie nothing is even playing 😭")

        vol = max(0, min(vol, 100))
        await player.set_volume(vol)
        await ctx.send(f"{vibe()} — volume set to **{vol}%** ✨")

    # -------------------------------
    # !disconnect
    # -------------------------------
    @commands.command(name="disconnect", aliases=["dc", "leave"])
    async def disconnect(self, ctx):
        player = self.bot.wavelink.players.get(ctx.guild.id)
        if not player:
            return await ctx.send("I’m not even in a VC babe 😭")

        await player.disconnect()
        await ctx.send(f"{vibe()} — fine I left the VC like a dramatic queen 💅")


# ===================================
# SETUP
# ===================================

async def setup(bot):
    await bot.add_cog(MusicSystem(bot))