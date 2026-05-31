from .views import *
from utils.discord_extras import burst_react

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    async def cog_load(self):
        await self.bot.cxn.execute("""
            CREATE TABLE IF NOT EXISTS giveaways (
                message_id    INTEGER PRIMARY KEY,
                channel_id    INTEGER,
                guild_id      INTEGER,
                prize         TEXT,
                winners_count INTEGER,
                end_time      TEXT,
                ended         BOOLEAN DEFAULT 0,
                host_id       INTEGER,
                requirements  TEXT
            )
        """)
        await self.bot.cxn.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                message_id INTEGER,
                user_id    INTEGER,
                PRIMARY KEY (message_id, user_id)
            )
        """)
        # Migrate older databases: add the requirements column if missing.
        try:
            await self.bot.cxn.execute("ALTER TABLE giveaways ADD COLUMN requirements TEXT")
        except Exception:
            pass

        # Sanitise rows with unparseable end_time
        await self.bot.cxn.execute(
            "UPDATE giveaways SET ended = 1 WHERE ended = 0 AND end_time NOT LIKE '____-%'"
        )

        # Re-register a unique persistent view for every active giveaway so that
        # button interactions survive restarts and never bleed between messages.
        active = await self.bot.cxn.fetch(
            "SELECT message_id FROM giveaways WHERE ended = 0"
        )
        for row in active:
            mid  = row["message_id"]
            view = _make_persistent_view(self.bot, mid)
            self.bot.add_view(view, message_id=mid)

    async def cog_unload(self):
        self.check_giveaways.cancel()

    # ─── HELPERS ─────────────────────────────────────────────

    def parse_duration(self, duration_str: str) -> int:
        m = re.match(r"([\d\.]+)([smhd])", duration_str.lower())
        if not m:
            return -1
        try:
            value = float(m.group(1))
            unit  = m.group(2)
            return int(value * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit])
        except ValueError:
            return -1

    # ─── COMMANDS ─────────────────────────────────────────────

    @commands.group(name="giveaway", aliases=["g"], invoke_without_command=True)
    async def giveaway(self, ctx):
        """Manage giveaways."""
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('icon_giveaway')} Giveaway Commands"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"Use `{ctx.clean_prefix}giveaway start <duration> <winners> <prize>` to start a new giveaway."
            ),
            accent_colour=discord.Color.purple()
        )
        view.add_item(container)
        await ctx.send(view=view)

    @giveaway.command(name="start")
    @commands.has_permissions(manage_guild=True)
    async def start(self, ctx, *, _ignored: str = ""):
        """Open the interactive giveaway setup panel.

        All settings — prize, duration, winners, channel, and join requirements
        (account age, time in server, required roles, booster-only) — are
        configured through the buttons on the panel that this command sends.
        """
        state = _SetupState(channel_id=ctx.channel.id)
        view  = _build_setup_view(self.bot, ctx, state, ctx.author.id)
        sent  = await ctx.send(view=view)
        view.message = sent

    @giveaway.command(name="reroll")
    @commands.has_permissions(manage_guild=True)
    async def reroll(self, ctx, message_id: int):
        """Reroll a finished giveaway to pick a new winner."""
        giveaway = await self.bot.cxn.fetchrow(
            "SELECT prize, winners_count, ended FROM giveaways WHERE message_id = $1", message_id
        )
        if not giveaway:
            return await ctx.send(msg(ctx, "reroll_not_found"))
        if not giveaway["ended"]:
            return await ctx.send(msg(ctx, "reroll_not_ended"))

        rows = await self.bot.cxn.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", message_id
        )
        participants = [row["user_id"] for row in rows]
        if not participants:
            return await ctx.send(msg(ctx, "reroll_no_participants"))

        new_winners     = random.sample(participants, 1)
        winner_mentions = ", ".join(f"<@{w}>" for w in new_winners)
        await ctx.send(msg(ctx, "reroll_announce", prize=giveaway["prize"], mentions=winner_mentions))

    # ─── BACKGROUND TASK ─────────────────────────────────────

    @tasks.loop(seconds=15)
    async def check_giveaways(self):
        try:
            now  = datetime.datetime.now(datetime.timezone.utc)
            rows = await self.bot.cxn.fetch(
                "SELECT message_id, channel_id, guild_id, prize, winners_count, end_time, host_id "
                "FROM giveaways WHERE ended = 0"
            )
            for row in rows:
                message_id   = row["message_id"]
                end_time_str = row["end_time"]
                try:
                    end_time = datetime.datetime.fromisoformat(str(end_time_str))
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=datetime.timezone.utc)
                except (TypeError, ValueError):
                    await self.bot.cxn.execute(
                        "UPDATE giveaways SET ended = 1 WHERE message_id = $1", message_id
                    )
                    continue

                if now >= end_time:
                    await self.end_giveaway(
                        message_id, row["channel_id"], row["guild_id"],
                        row["prize"], row["winners_count"], row["host_id"],
                    )
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[Giveaway Task Error] {e}")

    # ─── END GIVEAWAY ─────────────────────────────────────────

    async def end_giveaway(self, message_id, channel_id, guild_id, prize, winners_count, host_id):
        await self.bot.cxn.execute(
            "UPDATE giveaways SET ended = 1 WHERE message_id = $1", message_id
        )

        channel = self.bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception:
                return

        guild = self.bot.get_guild(guild_id) or getattr(channel, "guild", None)

        try:
            giveaway_msg = await channel.fetch_message(message_id)
        except Exception:
            giveaway_msg = None

        rows         = await self.bot.cxn.fetch(
            "SELECT user_id FROM participants WHERE message_id = $1", message_id
        )
        participants = [row["user_id"] for row in rows]
        msg_url      = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"

        if not participants:
            ended_view = _build_ended_view(guild, prize, host_id, winners=None)
            if giveaway_msg:
                try:
                    await giveaway_msg.edit(view=ended_view)
                except Exception:
                    pass
            await channel.send(_guild_msg(guild, "no_participants_msg", prize=prize))
            return

        winner_count    = min(winners_count, len(participants))
        winners         = random.sample(participants, winner_count)
        winner_mentions = ", ".join(f"<@{w}>" for w in winners)

        ended_view = _build_ended_view(guild, prize, host_id, winners=winners)
        if giveaway_msg:
            try:
                await giveaway_msg.edit(view=ended_view)
            except Exception:
                pass

        win_msg = await channel.send(
            _guild_msg(guild, "winner_announce", mentions=winner_mentions, prize=prize, url=msg_url)
        )
        # Burst-react on both the original giveaway message and the winner announcement
        if giveaway_msg:
            asyncio.create_task(burst_react(self.bot, channel_id, giveaway_msg.id, "⭐"))
        asyncio.create_task(burst_react(self.bot, channel_id, win_msg.id, "🎉"))

    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
