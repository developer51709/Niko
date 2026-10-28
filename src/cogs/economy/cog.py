from config.ids import SUPPORT_GUILD

from .data import *
from .commands.currency import CurrencyMixin
from .commands.jobs import JobsMixin
from .commands.gambling import GamblingMixin
from .commands.leaderboard import LeaderboardMixin
from .commands.shop import ShopMixin, _ShopActionView
from .commands.bank import BankMixin
from .commands.lottery import LotteryMixin
from .voting import VoteMixin


class EconomyCog(
    CurrencyMixin,
    JobsMixin,
    GamblingMixin,
    LeaderboardMixin,
    ShopMixin,
    BankMixin,
    LotteryMixin,
    VoteMixin,
    commands.Cog,
):
    """Premium economy with image cards, jobs, banking, a lottery and voting."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        if not os.path.exists("data/economy_data"):
            log.info("Economy", "economy_data directory not found. Creating directory…")
            os.makedirs("data/economy_data")
            log.success("Economy", "economy_data directory created. Continuing…")

        # Use database instead of JSON files
        self.economy_data: dict[str, dict] = {}  # Cache for performance
        self.lottery: dict = {}  # Will be loaded from database in setup
        
        self._tick_task.start()

    async def cog_load(self):
        # The shop card's Buy/Sell buttons have stable custom ids and need no
        # per-message state, so a single registration covers every shop message
        # and they keep working after a restart.
        self.bot.add_view(_ShopActionView(self, timeout=None))

    def cog_unload(self):
        try:
            self._tick_task.cancel()
        except Exception:
            pass

    # ── Persistence ──────────────────────────────────────────────────────────
    def _load_all(self) -> dict[str, dict]:
        """Legacy method - now uses database."""
        return {}

    def load_economy_data(self) -> dict[str, dict]:
        """Alias kept for backward-compat with other cogs."""
        return {}

    def save_economy_data(self) -> None:
        """Now uses database - this is a no-op for compatibility."""
        pass

    async def get_user_economy_data(self, user_id) -> dict:
        """Get user economy data from database with caching."""
        # Guard against non-integer user IDs
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            log.warning("Economy", f"Rejected non-integer user_id: {user_id!r}")
            return _migrate_user(_default_user())
        uid = str(user_id)

        # Check cache first
        if uid in self.economy_data:
            data = self.economy_data[uid]
        else:
            # Try to load from database
            data = await _get_user_from_db(self.bot, user_id)
            if data:
                self.economy_data[uid] = data
            else:
                # Create new user
                data = _default_user()
                self.economy_data[uid] = data
                await _save_user_to_db(self.bot, user_id, data)

        # The account is handed to the command now and the command is what will
        # move the counters, so this is the last moment a seasonal badge's
        # window baseline can still be the value the window opened with.
        ensure_season_baselines(data)
        return _migrate_user(data)

    async def save_user_economy_data(self, user_id) -> None:
        """Save a single user's data to database."""
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return
        uid = str(user_id)
        if uid in self.economy_data:
            await _save_user_to_db(self.bot, user_id, self.economy_data[uid])

    async def prime_cache(self) -> None:
        """Load every economy user from the database into the in-memory cache.

        ``self.economy_data`` is normally populated lazily as members interact
        with economy commands, so the leaderboard would only reflect users who
        have been active since the last restart. Warming the cache at startup
        means every member with saved data — including those who have not used
        an economy command since the last restart — is ranked immediately.
        """
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            log.warning("Economy", "Database not ready; skipping economy cache warm-up.")
            return
        try:
            rows = await cxn.fetch("SELECT user_id FROM economy_users")
        except Exception as exc:
            log.error("Economy", f"Could not query economy users for cache warm-up: {exc}")
            return

        loaded = 0
        for row in rows:
            uid = str(row["user_id"])
            if uid in self.economy_data:
                continue
            data = await _get_user_from_db(self.bot, int(row["user_id"]))
            if data:
                self.economy_data[uid] = data
                loaded += 1

        if loaded:
            log.info("Economy", f"Warmed up cache with {loaded} economy users.")

    # ── Internal helpers ─────────────────────────────────────────────────────
    def _credit(self, data: dict, amount: int, kind: str, note: str = ""):
        amount = int(amount)
        data["balance"] = int(data.get("balance", 0)) + amount
        if amount > 0:
            data["total_earned"] = int(data.get("total_earned", 0)) + amount
        else:
            data["total_spent"] = int(data.get("total_spent", 0)) + abs(amount)
        _log_tx(data, kind, amount, note)

    def record_gamble(self, data: dict, amount: int, kind: str, note: str = "") -> list[str]:
        """Apply a casino result to an account and write it to the ledger.

        The casino cogs (blackjack, slots, roulette) live outside the economy
        mixins and used to move ``data["balance"]`` directly. That left their
        wins and losses out of ``total_earned``/``total_spent`` and, more
        visibly, out of the recent activity card on the dashboard. Every casino
        payout now goes through here so it is recorded the same way as crime,
        rob, coinflip and dice, and so gambling achievements still unlock.

        Returns the display labels of any badges the result unlocked.
        """
        amount = int(amount)
        if amount:
            self._credit(data, amount, kind, note)
        return _check_achievements(data)

    async def _net_rank(self, uid: str) -> int | None:
        # Get all users from database for ranking
        all_users = await _get_all_users_from_db(self.bot)
        
        # Include current user from cache if not in database yet
        if uid in self.economy_data and uid not in all_users:
            data = self.economy_data[uid]
            all_users[uid] = {"balance": data.get("balance", 0), "bank": data.get("bank", 0)}
        
        sorted_users = sorted(
            ((u, d.get("balance", 0) + d.get("bank", 0)) for u, d in all_users.items()),
            key=lambda x: x[1], reverse=True,
        )
        for i, (u, _) in enumerate(sorted_users, start=1):
            if u == uid:
                return i
        return None

    async def _show_loading_card(self, ctx, card_type: str, **kwargs):
        """Show the matching animated loading card while a render is in flight.

        The public GIF is sent first and then edited into the finished PNG card,
        so a slow avatar fetch never leaves the member with a bare "thinking"
        state. Prefix commands get a new message; slash commands reuse the
        deferred response, so neither path leaves a duplicate card behind.

        ``**kwargs`` reach :func:`_loading_card_view` — the shop passes its row
        count and disabled controls so the placeholder matches the final card.
        """
        view = _loading_card_view(card_type, **kwargs)
        if ctx.interaction:
            return await ctx.interaction.edit_original_response(view=view)
        return await ctx.send(view=view)

    async def _send_balance_card(self, ctx, target: discord.Member, *, title: str = "Wallet"):
        message = await self._show_loading_card(ctx, "balance")
        data = await self.get_user_economy_data(target.id)
        avatar_bytes = await fetch_avatar_bytes(str(target.display_avatar.replace(size=256, format="png")), size=256)

        lvl      = int(data.get("level", 0))
        in_lvl   = int(data.get("xp", 0)) - total_xp_for_level(lvl)
        nxt      = xp_to_next(lvl)
        job      = get_job(data.get("job"))
        cap      = bank_cap(int(data.get("bank_tier", 0)))
        tier_name = bank_name(int(data.get("bank_tier", 0)))
        rank     = await self._net_rank(str(target.id))

        buf = await render_balance_card(
            avatar_bytes=avatar_bytes,
            name=target.display_name,
            cash=int(data.get("balance", 0)),
            bank=int(data.get("bank", 0)),
            bank_cap_v=cap,
            bank_tier_name=tier_name,
            net_worth=int(data.get("balance", 0)) + int(data.get("bank", 0)),
            level=lvl,
            xp_in_level=max(0, in_lvl),
            xp_for_next=nxt,
            job_name=job["name"],
            job_emoji="",
            daily_streak=int(data.get("daily_streak", 0)),
            rank=rank,
            title=title,
        )
        prefix = await _resolve_prefix(self.bot, ctx)
        view = _card_view(
            title=f"{get_emoji('credit_card')} {title}",
            image_name="balance.png",
            footer_lines=[
                f"-# Use `{prefix}deposit` / `{prefix}withdraw` to manage your vault.",
                f"-# `{prefix}work` to earn, `{prefix}daily` for your daily reward, `{prefix}shop` to spend.",
            ],
        )
        await message.edit(view=view, attachments=[discord.File(buf, "balance.png")])

    async def _send_reward_card(
        self,
        ctx,
        *,
        title: str,
        subtitle: str,
        amount: int,
        accent,
        footer: str = "",
        announce: str | None = None,
    ):
        message = await self._show_loading_card(ctx, "reward")
        data = await self.get_user_economy_data(ctx.author.id)
        avatar_bytes = await fetch_avatar_bytes(
            str(ctx.author.display_avatar.replace(size=256, format="png")), size=256
        )
        new_balance = int(data.get("balance", 0))
        buf = await render_reward_card(
            avatar_bytes=avatar_bytes,
            name=ctx.author.display_name,
            title=title,
            subtitle=subtitle,
            amount=amount,
            new_balance=new_balance,
            accent=accent,
            footer=footer,
        )
        view = _card_view(
            title=f"### {title}".replace("###", "").strip() or title,
            image_name="reward.png",
            footer_lines=[announce] if announce else [],
        )
        await message.edit(view=view, attachments=[discord.File(buf, "reward.png")])

    # ── Lottery announcements ────────────────────────────────────────────────
    async def _lottery_channel(self):
        """The support server's #lottery channel, or None when it is not set up.

        The channel id comes from the same `support_server_config` row the
        `.staff supportsetup` command writes, so nothing is hardcoded and the
        announcement stays optional: a deployment without the support server
        simply draws the lottery silently.
        """
        cached = getattr(self, "_lottery_channel_cache", None)
        if cached is not None:
            return cached
        pool = getattr(self.bot, "cxn", None)
        if pool is None:
            return None
        try:
            row = await pool.fetchrow(
                "SELECT channel_ids FROM support_server_config WHERE guild_id = $1",
                SUPPORT_GUILD,
            )
        except Exception as exc:
            log.error("Economy", f"Could not read the support server channels: {exc}")
            return None
        channel_ids = row.get("channel_ids") if row else None
        if isinstance(channel_ids, str):
            try:
                channel_ids = json.loads(channel_ids or "{}")
            except (TypeError, ValueError):
                channel_ids = None
        channel_id = channel_ids.get("lottery") if isinstance(channel_ids, dict) else None
        if not channel_id:
            return None
        channel = self.bot.get_channel(int(channel_id))
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(int(channel_id))
            except Exception:
                return None
        self._lottery_channel_cache = channel
        return channel

    async def _announce_lottery_draw(
        self, *, winner_name: str | None, payout: int, tickets: int, entrants: int,
        unlocked: list[str] | None = None,
    ) -> None:
        """Post the weekly draw to #lottery. Best effort: never fail the draw."""
        try:
            channel = await self._lottery_channel()
            if channel is None:
                return
            remaining = max(0, int(self.lottery.get("next_draw", 0)) - int(time.time()))
            if winner_name:
                title = "🎰 Lottery drawn"
                body = (
                    f"**{winner_name}** won **{payout:,}** 🪙 this week.\n"
                    f"• Tickets in play: **{tickets:,}** from **{entrants:,}** "
                    f"member{'s' if entrants != 1 else ''}\n"
                    f"• Next pot starts at **{int(self.lottery.get('pot', 0)):,}** 🪙\n\n"
                    f"Next draw in **{_fmt_remaining(remaining)}** — buy tickets with `/lottery buy`."
                )
                if unlocked:
                    body += "\n\n**New achievements** " + ", ".join(unlocked)
            else:
                title = "🎰 No lottery winner this week"
                body = (
                    "Nobody held a ticket when the draw came up, so the pot rolls over.\n\n"
                    f"Next draw in **{_fmt_remaining(remaining)}** — buy tickets with `/lottery buy`."
                )
            await channel.send(view=_info_view(title, body))
        except Exception as exc:
            log.error("Economy", f"Could not announce the lottery draw: {exc}")

    async def _winner_name(self, winner_id: str | None) -> str | None:
        """The winner's display name for the announcement, or None if unknown."""
        if not winner_id:
            return None
        try:
            user = self.bot.get_user(int(winner_id))
            if user is None:
                user = await self.bot.fetch_user(int(winner_id))
            return getattr(user, "display_name", None) or getattr(user, "name", None)
        except Exception:
            return None

    # ── Background tick: bank interest + lottery draw ────────────────────────
    @tasks.loop(minutes=30)
    async def _tick_task(self):
        try:
            await self._apply_bank_interest()
            await self._maybe_draw_lottery()
        except Exception as exc:
            log.error("Economy", f"Tick task failed: {exc}")

    @_tick_task.before_loop
    async def _before_tick(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(20)

    async def _apply_bank_interest(self):
        now = int(time.time())
        today_utc = datetime.datetime.utcfromtimestamp(now).strftime("%Y-%m-%d")
        changed = 0
        
        # Get all users from database
        rows = await self.bot.cxn.fetch("SELECT user_id, bank, bank_tier, total_earned, last_interest_day FROM economy_users")
        
        for row in rows:
            user_id = row["user_id"]
            
            # ── Skip fake / malformed records (non-integer user IDs) ──────
            try:
                uid_int = int(user_id)
            except (TypeError, ValueError):
                log.warning("Economy", f"Skipping malformed economy record with non-integer user_id: {user_id!r}")
                await self.bot.cxn.execute(
                    "DELETE FROM economy_users WHERE user_id = ?",
                    user_id
                )
                continue
            
            # ── Compare last_interest_day safely ──────────────────────
            # MongoDB stores dates as datetime objects; convert to string
            # before comparing with the YYYY-MM-DD string.
            last_day = row.get("last_interest_day")
            if last_day is not None:
                last_day_str = str(last_day)[:10]  # handles datetime → "2026-09-02 ..."
            else:
                last_day_str = None
            
            if last_day_str == today_utc:
                continue
            
            tier = int(row.get("bank_tier", 0))
            cap  = bank_cap(tier)
            rate = bank_rate(tier)
            bank = int(row.get("bank", 0))
            
            if bank <= 0:
                await self.bot.cxn.execute(
                    "UPDATE economy_users SET last_interest_day = ? WHERE user_id = ?",
                    today_utc, uid_int
                )
                continue
            
            principal = min(bank, cap)
            interest  = int(principal * rate)
            
            if interest <= 0:
                await self.bot.cxn.execute(
                    "UPDATE economy_users SET last_interest_day = ? WHERE user_id = ?",
                    today_utc, uid_int
                )
                continue
            
            new_bank = bank + interest
            new_total_earned = int(row.get("total_earned", 0)) + interest
            
            await self.bot.cxn.execute(
                "UPDATE economy_users SET bank = ?, total_earned = ?, last_interest_day = ? WHERE user_id = ?",
                new_bank, new_total_earned, today_utc, uid_int
            )
            
            # Update cache if user is in memory
            uid = str(uid_int)
            if uid in self.economy_data:
                self.economy_data[uid]["bank"] = new_bank
                self.economy_data[uid]["total_earned"] = new_total_earned
                self.economy_data[uid]["last_interest_day"] = today_utc
                _log_tx(self.economy_data[uid], "interest", interest, f"daily {bank_name(tier)} interest")
            
            changed += 1
        
        if changed:
            log.info("Economy", f"Applied bank interest to {changed} accounts.")

    async def _maybe_draw_lottery(self):
        now = int(time.time())
        
        # Load lottery state from database
        lottery_state = await _get_lottery_from_db(self.bot)
        self.lottery = lottery_state
        
        if now < int(self.lottery.get("next_draw", 0)):
            return
        
        entrants: list[tuple[str, int]] = []
        total_tickets = 0
        
        # Get all users with lottery tickets from database
        rows = await self.bot.cxn.fetch("SELECT user_id, lottery_tickets FROM economy_users WHERE lottery_tickets > 0")
        
        for row in rows:
            uid = str(row["user_id"])
            tix = int(row["lottery_tickets"])
            if tix > 0:
                entrants.append((uid, tix))
                total_tickets += tix

        pot = int(self.lottery.get("pot", LOTTERY_BASE_POT))
        if not entrants or total_tickets <= 0 or pot <= 0:
            # Nothing to pay out, but the draw still happened: the channel post
            # tells members the pot rolled over and when the next draw runs.
            self.lottery["next_draw"] = now + LOTTERY_DRAW_INTERVAL
            await _save_lottery_to_db(self.bot, self.lottery)
            await self._announce_lottery_draw(
                winner_name=None, payout=0, tickets=0, entrants=0,
            )
            return

        roll = random.randint(1, total_tickets)
        cur  = 0
        winner_id = entrants[-1][0]
        for uid, tix in entrants:
            cur += tix
            if roll <= cur:
                winner_id = uid
                break

        rake   = int(pot * LOTTERY_HOUSE_RAKE)
        payout = pot - rake

        winner_data = await self.get_user_economy_data(int(winner_id))
        self._credit(winner_data, payout, "lottery", f"weekly draw winner ({total_tickets} tickets)")
        # Winning a draw is its own milestone, and the badge rewards are paid on
        # the same save as the payout.
        winner_data["lottery_wins"] = int(winner_data.get("lottery_wins", 0)) + 1
        unlocked = _check_achievements(winner_data)
        await self.save_user_economy_data(int(winner_id))

        # Reset lottery tickets for all entrants
        for uid, _ in entrants:
            await self.bot.cxn.execute(
                "UPDATE economy_users SET lottery_tickets = 0 WHERE user_id = ?",
                int(uid)
            )
            # Update cache if user is in memory
            if uid in self.economy_data:
                self.economy_data[uid]["lottery_tickets"] = 0

        self.lottery = {
            "pot":         max(LOTTERY_BASE_POT, rake),
            "next_draw":   now + LOTTERY_DRAW_INTERVAL,
            "last_winner": winner_id,
            "last_pot":    payout,
        }
        await _save_lottery_to_db(self.bot, self.lottery)
        log.info("Economy", f"Lottery: paid {payout:,} coins to {winner_id} (next pot starts at {self.lottery['pot']:,}).")
        await self._announce_lottery_draw(
            winner_name=await self._winner_name(winner_id),
            payout=payout,
            tickets=total_tickets,
            entrants=len(entrants),
            unlocked=unlocked,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
