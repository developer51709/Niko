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

        self.economy_data: dict[str, dict] = self._load_all()
        self.lottery: dict = _load_lottery()

        self._tick_task.start()

    def cog_unload(self):
        try:
            self._tick_task.cancel()
        except Exception:
            pass

    # ── Persistence ──────────────────────────────────────────────────────────
    def _load_all(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        if not os.path.exists("data/economy_data"):
            return out
        for filename in os.listdir("data/economy_data"):
            if not filename.endswith(".json") or filename.startswith("_"):
                continue
            try:
                with open(os.path.join("data/economy_data", filename), "r") as f:
                    uid = filename[:-5]
                    raw = json.load(f)
                    out[uid] = _migrate_user(raw)
            except Exception as e:
                log.error("Economy", f"Error loading {filename}: {e}")
        return out

    def load_economy_data(self) -> dict[str, dict]:
        """Alias kept for backward-compat with other cogs."""
        return self._load_all()

    def save_economy_data(self) -> None:
        if not os.path.exists("data/economy_data"):
            os.makedirs("data/economy_data")
        for uid, data in self.economy_data.items():
            try:
                _migrate_user(data)
                with open(os.path.join("data/economy_data", f"{uid}.json"), "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as exc:
                log.error("Economy", f"Could not save {uid}: {exc}")

    def get_user_economy_data(self, user_id) -> dict:
        uid = str(user_id)
        if uid not in self.economy_data:
            self.economy_data[uid] = _default_user()
        return _migrate_user(self.economy_data[uid])

    # ── Internal helpers ─────────────────────────────────────────────────────
    def _credit(self, data: dict, amount: int, kind: str, note: str = ""):
        amount = int(amount)
        data["balance"] = int(data.get("balance", 0)) + amount
        if amount > 0:
            data["total_earned"] = int(data.get("total_earned", 0)) + amount
        else:
            data["total_spent"] = int(data.get("total_spent", 0)) + abs(amount)
        _log_tx(data, kind, amount, note)

    def _net_rank(self, uid: str) -> int | None:
        sorted_users = sorted(
            ((u, d.get("balance", 0) + d.get("bank", 0)) for u, d in self.economy_data.items()),
            key=lambda x: x[1], reverse=True,
        )
        for i, (u, _) in enumerate(sorted_users, start=1):
            if u == uid:
                return i
        return None

    async def _send_balance_card(self, ctx, target: discord.Member, *, title: str = "Wallet"):
        data = self.get_user_economy_data(target.id)
        avatar_bytes = await fetch_avatar_bytes(str(target.display_avatar.replace(size=256, format="png")), size=256)

        lvl      = int(data.get("level", 0))
        in_lvl   = int(data.get("xp", 0)) - total_xp_for_level(lvl)
        nxt      = xp_to_next(lvl)
        job      = get_job(data.get("job"))
        cap      = bank_cap(int(data.get("bank_tier", 0)))
        tier_name = bank_name(int(data.get("bank_tier", 0)))
        rank     = self._net_rank(str(target.id))

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
        data = self.get_user_economy_data(ctx.author.id)
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
        for uid, data in self.economy_data.items():
            if data.get("last_interest_day") == today_utc:
                continue
            tier = int(data.get("bank_tier", 0))
            cap  = bank_cap(tier)
            rate = bank_rate(tier)
            bank = int(data.get("bank", 0))
            if bank <= 0:
                data["last_interest_day"] = today_utc
                continue
            principal = min(bank, cap)
            interest  = int(principal * rate)
            if interest <= 0:
                data["last_interest_day"] = today_utc
                continue
            data["bank"]         = bank + interest
            data["total_earned"] = int(data.get("total_earned", 0)) + interest
            data["last_interest_day"] = today_utc
            _log_tx(data, "interest", interest, f"daily {bank_name(tier)} interest")
            changed += 1
        if changed:
            self.save_economy_data()
            log.info("Economy", f"Applied bank interest to {changed} accounts.")

    async def _maybe_draw_lottery(self):
        now = int(time.time())
        if now < int(self.lottery.get("next_draw", 0)):
            return
        entrants: list[tuple[str, int]] = []
        total_tickets = 0
        for uid, data in self.economy_data.items():
            tix = int(data.get("lottery_tickets", 0))
            if tix > 0:
                entrants.append((uid, tix))
                total_tickets += tix

        pot = int(self.lottery.get("pot", LOTTERY_BASE_POT))
        if not entrants or total_tickets <= 0 or pot <= 0:
            self.lottery["next_draw"] = now + LOTTERY_DRAW_INTERVAL
            _save_lottery(self.lottery)
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

        winner_data = self.get_user_economy_data(winner_id)
        self._credit(winner_data, payout, "lottery", f"weekly draw winner ({total_tickets} tickets)")

        for uid, _ in entrants:
            d = self.economy_data.get(uid)
            if d is not None:
                d["lottery_tickets"] = 0

        self.lottery = {
            "pot":         max(LOTTERY_BASE_POT, rake),
            "next_draw":   now + LOTTERY_DRAW_INTERVAL,
            "last_winner": winner_id,
            "last_pot":    payout,
        }
        _save_lottery(self.lottery)
        self.save_economy_data()
        log.info("Economy", f"Lottery: paid {payout:,} coins to {winner_id} (next pot starts at {self.lottery['pot']:,}).")


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
