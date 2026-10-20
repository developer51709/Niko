from .views import *
from utils import logging
from utils.blacklist_manager import BlacklistManager
from utils.prefix_manager import get_prefixes


# SQLite accepts 0 and FALSE interchangeably, while MongoDB keeps booleans
# distinct from numbers. Query both representations so old and new rows are
# discovered regardless of which backend wrote them.
_ACTIVE_GIVEAWAY_FILTER = "(ended = 0 OR ended = FALSE)"


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
        # Giveaway bans are per server and outlive the giveaway they were set
        # in, so they belong to the schema rather than to one giveaway row.
        await self.bot.cxn.execute("""
            CREATE TABLE IF NOT EXISTS giveaway_bans (
                guild_id   INTEGER,
                user_id    INTEGER,
                banned_by  INTEGER,
                created_at TEXT,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        # Migrate older databases: add the requirements column if missing.
        try:
            await self.bot.cxn.execute("ALTER TABLE giveaways ADD COLUMN requirements TEXT")
        except Exception:
            pass
        # Giveaways locked by a blacklist lockdown must stay locked after a
        # restart, so the column belongs to the schema and not just to memory.
        try:
            await self.bot.cxn.execute("ALTER TABLE giveaways ADD COLUMN locked INTEGER DEFAULT 0")
        except Exception:
            pass

        # Sanitise rows with unparseable end_time
        await self.bot.cxn.execute(
            "UPDATE giveaways SET ended = 1 WHERE "
            f"{_ACTIVE_GIVEAWAY_FILTER} AND end_time NOT LIKE '____-%'"
        )

        await self.register_persistent_views()

    async def register_persistent_views(self) -> int:
        """Register the buttons for every active stored giveaway at startup."""
        active = await self.bot.cxn.fetch(
            "SELECT message_id FROM giveaways WHERE "
            f"{_ACTIVE_GIVEAWAY_FILTER}"
        )
        registered = 0
        for row in active:
            message_id = row["message_id"]
            try:
                view = _make_persistent_view(self.bot, message_id)
                self.bot.add_view(view, message_id=message_id)
                registered += 1
            except Exception as exc:
                logging.error(
                    "Giveaway",
                    f"Could not register persistent buttons for giveaway {message_id}: {exc}",
                )

        logging.info(
            "Giveaway",
            f"Registered persistent buttons for {registered}/{len(active)} active giveaway(s)",
        )
        return registered

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
                content=f"### {get_emoji('giveaway')} Giveaway Commands"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"Use `{ctx.clean_prefix}giveaway start` to start a new giveaway.\n"
                    f"Use `{ctx.clean_prefix}giveaway ban <member>` to keep a member out of every "
                    f"giveaway in this server, and `{ctx.clean_prefix}giveaway unban <member>` to let "
                    f"them back in."
                )
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
        banned = await self._banned_user_ids(ctx.guild.id if ctx.guild else None)
        participants = [uid for uid in participants if int(uid) not in banned]
        if not participants:
            return await ctx.send(msg(ctx, "reroll_no_participants"))

        new_winners     = random.sample(participants, 1)
        winner_mentions = ", ".join(f"<@{w}>" for w in new_winners)
        await ctx.send(msg(ctx, "reroll_announce", prize=giveaway["prize"], mentions=winner_mentions))

    # ─── GIVEAWAY BANS ────────────────────────────────────────

    async def _banned_user_ids(self, guild_id) -> set[int]:
        """Every member banned from this server's giveaways.

        The draw reads this set instead of trusting that a ban only ever lands
        before entries are cleared: an entry recorded while a giveaway was
        ending must never be able to win.
        """
        if guild_id is None:
            return set()
        rows = await self.bot.cxn.fetch(
            "SELECT user_id FROM giveaway_bans WHERE guild_id = $1", guild_id
        )
        return {int(row["user_id"]) for row in rows}

    async def _clear_entries(self, guild_id, user_id) -> int:
        """Remove the entries a banned member still holds in active giveaways."""
        active = await self.bot.cxn.fetch(
            "SELECT message_id FROM giveaways WHERE guild_id = $1 AND "
            f"{_ACTIVE_GIVEAWAY_FILTER}",
            guild_id,
        )
        cleared = 0
        for row in active:
            message_id = row["message_id"]
            held = await self.bot.cxn.fetchval(
                "SELECT 1 FROM participants WHERE message_id = $1 AND user_id = $2",
                message_id, user_id,
            )
            if held is None:
                continue
            await self.bot.cxn.execute(
                "DELETE FROM participants WHERE message_id = $1 AND user_id = $2",
                message_id, user_id,
            )
            cleared += 1
        return cleared

    @giveaway.command(name="ban")
    @commands.has_permissions(manage_guild=True)
    async def ban(self, ctx, member: discord.Member):
        """Ban a member from joining giveaways in this server."""
        if member.bot:
            return await ctx.send(f"{get_emoji('cross')} {msg(ctx, 'join_bot')}")

        guild_id = ctx.guild.id
        existing = await self.bot.cxn.fetchval(
            "SELECT 1 FROM giveaway_bans WHERE guild_id = $1 AND user_id = $2",
            guild_id, member.id,
        )
        if existing is not None:
            return await ctx.send(
                f"{get_emoji('cross')} {msg(ctx, 'ban_already', user=member.display_name)}"
            )

        await self.bot.cxn.execute(
            "INSERT INTO giveaway_bans (guild_id, user_id, banned_by, created_at) "
            "VALUES ($1, $2, $3, $4)",
            guild_id, member.id, ctx.author.id,
            datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        )
        # Existing entries would still be eligible at the draw, so a ban also
        # removes what the member already holds.
        cleared = await self._clear_entries(guild_id, member.id)
        await ctx.send(
            f"{get_emoji('check')} {msg(ctx, 'ban_success', user=member.display_name, count=cleared)}"
        )

    @giveaway.command(name="unban")
    @commands.has_permissions(manage_guild=True)
    async def unban(self, ctx, member: discord.Member):
        """Lift a giveaway ban so the member can enter again."""
        guild_id = ctx.guild.id
        existing = await self.bot.cxn.fetchval(
            "SELECT 1 FROM giveaway_bans WHERE guild_id = $1 AND user_id = $2",
            guild_id, member.id,
        )
        if existing is None:
            return await ctx.send(
                f"{get_emoji('cross')} {msg(ctx, 'unban_not_banned', user=member.display_name)}"
            )

        await self.bot.cxn.execute(
            "DELETE FROM giveaway_bans WHERE guild_id = $1 AND user_id = $2",
            guild_id, member.id,
        )
        await ctx.send(
            f"{get_emoji('check')} {msg(ctx, 'unban_success', user=member.display_name)}"
        )

    # ─── BACKGROUND TASK ─────────────────────────────────────

    @tasks.loop(seconds=15)
    async def check_giveaways(self):
        try:
            now  = datetime.datetime.now(datetime.timezone.utc)
            rows = await self.bot.cxn.fetch(
                "SELECT message_id, channel_id, guild_id, prize, winners_count, end_time, host_id, locked "
                "FROM giveaways WHERE "
                f"{_ACTIVE_GIVEAWAY_FILTER}"
            )
            blacklist = BlacklistManager()
            for row in rows:
                message_id   = row["message_id"]
                # A giveaway of a blacklisted server is frozen, not ended: it keeps
                # its entries and end time so an approved appeal resumes it.
                if row.get("locked") or blacklist.is_guild_blacklisted(int(row["guild_id"])):
                    continue
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

    async def _command_prefix(self, guild_id) -> str:
        """The prefix the copy-ready `.giveaway ...` hint should use here.

        Prefixes are per server, so a hint with the wrong one would be just as
        useless as no hint. A prefix lookup failure falls back to the default
        rather than holding up the draw announcement.
        """
        try:
            prefixes = await get_prefixes(int(guild_id), self.bot.cxn)
        except Exception as exc:
            logging.error("Giveaway", f"Could not read the prefix for guild {guild_id}: {exc}")
            prefixes = []
        return (prefixes or ["."])[0]

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
        # A ban is authoritative at the draw: a member banned mid-giveaway must
        # not win even if their entry outlived the ban that cleared it.
        banned = await self._banned_user_ids(guild_id)
        participants = [uid for uid in participants if int(uid) not in banned]
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

        # Most members do not know how to copy a message id, so the end message
        # spells out the reroll command with this giveaway's id in it and the
        # server's own prefix. The host can copy the whole line unchanged.
        reroll_hint = _guild_msg(
            guild, "reroll_hint",
            command=f"{await self._command_prefix(guild_id)}giveaway reroll {message_id}",
        )
        await channel.send(
            _guild_msg(guild, "winner_announce", mentions=winner_mentions, prize=prize, url=msg_url)
            + "\n" + reroll_hint
        )

    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
