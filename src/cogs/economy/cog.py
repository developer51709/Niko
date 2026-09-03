from .data import *
from .commands.currency import CurrencyMixin
from .commands.jobs import JobsMixin
from .commands.gambling import GamblingMixin
from .commands.leaderboard import LeaderboardMixin
from .commands.shop import ShopMixin
from .commands.bank import BankMixin
from .commands.lottery import LotteryMixin


class EconomyCog(
    CurrencyMixin,
    JobsMixin,
    GamblingMixin,
    LeaderboardMixin,
    ShopMixin,
    BankMixin,
    LotteryMixin,
    commands.Cog,
):
    """Premium café economy with image cards, jobs, banking and a lottery."""

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
            return _migrate_user(self.economy_data[uid])
        
        # Try to load from database
        data = await _get_user_from_db(self.bot, user_id)
        if data:
            self.economy_data[uid] = data
            return _migrate_user(data)
        
        # Create new user
        default = _default_user()
        self.economy_data[uid] = default
        await _save_user_to_db(self.bot, user_id, default)
        return _migrate_user(default)

    async def save_user_economy_data(self, user_id) -> None:
        """Save a single user's data to database."""
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return
        uid = str(user_id)
        if uid in self.economy_data:
            await _save_user_to_db(self.bot, user_id, self.economy_data[uid])

    # ── Internal helpers ─────────────────────────────────────────────────────
    def _credit(self, data: dict, amount: int, kind: str, note: str = ""):
        amount = int(amount)
        data["balance"] = int(data.get("balance", 0)) + amount
        if amount > 0:
            data["total_earned"] = int(data.get("total_earned", 0)) + amount
        else:
            data["total_spent"] = int(data.get("total_spent", 0)) + abs(amount)
        _log_tx(data, kind, amount, note)

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

    async def _send_balance_card(self, ctx, target: discord.Member, *, title: str = "Wallet"):
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
                f"-# `{prefix}work` to earn, `{prefix}daily` for treats, `{prefix}shop` to spend.",
            ],
        )
        if ctx.interaction:
            await ctx.interaction.followup.send(view=view, file=discord.File(buf, "balance.png"))
        else:
            await ctx.send(view=view, file=discord.File(buf, "balance.png"))

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
        if ctx.interaction:
            await ctx.interaction.followup.send(view=view, file=discord.File(buf, "reward.png"))
        else:
            await ctx.send(view=view, file=discord.File(buf, "reward.png"))

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
            self.lottery["next_draw"] = now + LOTTERY_DRAW_INTERVAL
            await _save_lottery_to_db(self.bot, self.lottery)
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


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
