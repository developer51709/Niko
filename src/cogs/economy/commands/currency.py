"""
Economy — currency commands: balance, profile, daily, work, pay, transactions, networth.
"""
import discord
from discord.ext import commands
from ..data import (
    msg, _info_view, _card_view, _fmt_remaining,
    _check_achievements, _resolve_prefix,
    COOLDOWN_DAILY, COOLDOWN_WORK,
    get_job, get_emoji,
    total_xp_for_level, xp_to_next, bank_name,
    add_xp,
    ACCENT_GOLD, ACCENT_GREEN,
)
import random
import datetime


class CurrencyMixin:
    """balance, profile, daily, work, pay, transactions, networth."""

    # ── balance / profile ────────────────────────────────────────────────────
    @commands.hybrid_command(name="balance", aliases=["bal", "wallet"],
                             description="Check your premium café wallet card",
                             help="{ 'en': 'check your pastry bag balance 🥐✨', 'de': 'sieh dein Wallet als Karte', 'es': 'consulta tu wallet 🥐✨' }")
    async def balance(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        await self._send_balance_card(ctx, target, title="Wallet")

    @commands.hybrid_command(name="profile", aliases=["prof", "stats"],
                             description="Full café profile card",
                             help="{ 'en': 'view a full café profile card 📜✨', 'de': 'sieh dein volles Profil', 'es': 'mira tu perfil completo 📜✨' }")
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        from ..data import ACHIEVEMENTS
        target = member or ctx.author
        await self._send_balance_card(ctx, target, title="Profile")
        data = self.get_user_economy_data(target.id)
        ach = data.get("achievements", [])
        ach_line = (
            ", ".join(f"{ACHIEVEMENTS[a]['emoji']} {ACHIEVEMENTS[a]['name']}" for a in ach if a in ACHIEVEMENTS)
            or "*no badges yet — go earn some!*"
        )
        txs = data.get("transactions", [])[:5]
        if txs:
            lines = []
            for t in txs:
                sign = "+" if t["amount"] >= 0 else "−"
                lines.append(f"`{t['kind'][:10]:<10}` {sign}{abs(t['amount']):,}  ·  {t.get('note','')}")
            tx_block = "\n".join(lines)
        else:
            tx_block = "*no transactions yet*"
        view = _info_view(
            f"📜 {target.display_name}'s Extras",
            f"**Badges**\n{ach_line}\n\n**Recent activity**\n{tx_block}",
        )
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # ── daily ────────────────────────────────────────────────────────────────
    @commands.hybrid_command(name="daily",
                             description="Claim your daily treats with streak bonus",
                             help="{ 'en': 'claim your daily treats 🍬✨', 'de': 'hol dir deine täglichen Belohnungen', 'es': 'reclama tus golosinas diarias 🍬✨' }")
    async def daily(self, ctx: commands.Context):
        import time
        data = self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        elapsed = now - int(data.get("last_daily", 0))

        if elapsed < COOLDOWN_DAILY:
            remain = COOLDOWN_DAILY - elapsed
            return await ctx.send(view=_info_view(
                "⏳ Daily on cooldown",
                f"Patience! Your treats are still baking.\nCome back in **{_fmt_remaining(remain)}**. ☕🍰",
            ))

        streak = int(data.get("daily_streak", 0))
        if elapsed > 2 * COOLDOWN_DAILY:
            streak = 1
        else:
            streak += 1
        multiplier = 1 + min(streak, 7) * 0.2
        base = 1000
        reward = int(base * multiplier)

        self._credit(data, reward, "daily", f"day {streak} • x{multiplier:.1f}")
        data["daily_streak"] = streak
        data["last_daily"] = now
        _check_achievements(data)
        self.save_economy_data()

        await self._send_reward_card(
            ctx,
            title="🍬 Daily Treats",
            subtitle=f"Streak day {streak} 🔥  •  multiplier x{multiplier:.1f}",
            amount=reward,
            accent=ACCENT_GOLD,
            footer=msg(ctx, "daily_success", reward=reward),
        )

    # ── work ─────────────────────────────────────────────────────────────────
    @commands.hybrid_command(name="work",
                             description="Work a shift at your current café job",
                             help="{ 'en': 'work a shift at your current café job ☕', 'de': 'arbeite eine Schicht', 'es': 'trabaja un turno en el café ☕' }")
    async def work(self, ctx: commands.Context):
        import time
        data = self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        job = get_job(data.get("job"))
        cd = int(job.get("cooldown", COOLDOWN_WORK))

        effects = data.setdefault("effects", {})
        if effects.get("work_cooldown_half"):
            cd = cd // 2

        elapsed = now - int(data.get("last_work", 0))
        if elapsed < cd:
            return await ctx.send(view=_info_view(
                "⏳ On a coffee break",
                f"You're resting after your last shift.\nBack to work in **{_fmt_remaining(cd - elapsed)}**. ☕💤",
            ))

        if effects.get("work_cooldown_half"):
            effects.pop("work_cooldown_half", None)

        reward = random.randint(int(job["min_pay"]), int(job["max_pay"]))
        self._credit(data, reward, "work", f"{job['name']} shift")
        data["last_work"] = now
        data["times_worked"] = int(data.get("times_worked", 0)) + 1

        new_lvl, gained_levels, leveled = add_xp(data, int(job.get("xp_per_shift", 10)))
        announce = msg(ctx, "level_up", level=new_lvl) if leveled else None

        newly = _check_achievements(data)
        self.save_economy_data()

        subtitle = f"{job['emoji']} {job['name']} shift  •  +{job.get('xp_per_shift', 10)} XP"
        footer = msg(ctx, "work_success", reward=reward)
        if newly:
            footer += "  •  unlocked: " + ", ".join(newly)
        await self._send_reward_card(
            ctx, title="🍯 Shift complete", subtitle=subtitle, amount=reward,
            accent=ACCENT_GREEN, footer=footer, announce=announce,
        )

    # ── pay ───────────────────────────────────────────────────────────────────
    @commands.hybrid_command(name="pay", aliases=["give"],
                             description="Send coins to another user",
                             help="{ 'en': 'send coins to another user 💸🥐', 'de': 'sende Münzen an jemanden', 'es': 'envía monedas a alguien 💸🥐' }")
    async def pay(self, ctx: commands.Context, member: discord.Member, amount: int):
        if not member or member.bot or member.id == ctx.author.id:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad target", "Pick a real person other than yourself."))
        if amount <= 0:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Amount must be positive."))
        data   = self.get_user_economy_data(ctx.author.id)
        target = self.get_user_economy_data(member.id)
        if data["balance"] < amount:
            return await ctx.send(view=_info_view("💸 Not enough cash", "Your pastry bag is too light for that."))
        self._credit(data, -amount, "pay", f"to {member.display_name}")
        self._credit(target, amount, "received", f"from {ctx.author.display_name}")
        self.save_economy_data()
        await ctx.send(view=_info_view(
            "💸 Transfer complete",
            f"You sent **{amount:,}** 🥐 to {member.mention}.\n-# New balance: **{data['balance']:,}** 🥐",
        ), allowed_mentions=discord.AllowedMentions.none())

    # ── transactions ──────────────────────────────────────────────────────────
    @commands.hybrid_command(name="transactions", aliases=["tx", "history"],
                             description="See your recent transactions",
                             help="{ 'en': 'see your last transactions 📜', 'de': 'sieh deine letzten Transaktionen', 'es': 'mira tus últimas transacciones 📜' }")
    async def transactions(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        txs = data.get("transactions", [])
        if not txs:
            return await ctx.send(view=_info_view("📜 No history", "No transactions yet."))
        lines = []
        for t in txs[:25]:
            sign = "+" if t["amount"] >= 0 else "−"
            ts = datetime.datetime.utcfromtimestamp(int(t["ts"])).strftime("%m-%d %H:%M")
            lines.append(f"`{ts}` `{t['kind'][:10]:<10}` **{sign}{abs(int(t['amount'])):,}** 🥐  ·  {t.get('note','')}")
        await ctx.send(view=_info_view(f"📜 {ctx.author.display_name}'s Recent Activity", "\n".join(lines)))

    # ── networth ──────────────────────────────────────────────────────────────
    @commands.hybrid_command(name="networth", aliases=["nw"],
                             description="Quick net worth summary",
                             help="{ 'en': 'calculate your total café fortune 📊🥐', 'de': 'berechne dein gesamtes Vermögen', 'es': 'calcula tu fortuna 📊🥐' }")
    async def networth(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        data = self.get_user_economy_data(target.id)
        nw = int(data["balance"]) + int(data["bank"])
        rank = self._net_rank(str(target.id))
        body = (
            f"💼 **{target.display_name}** is worth **{nw:,}** 🥐\n"
            f"• Cash: **{int(data['balance']):,}**\n"
            f"• Bank: **{int(data['bank']):,}** ({bank_name(int(data.get('bank_tier', 0)))})\n"
            f"• Rank: **#{rank}**" if rank else ""
        )
        await ctx.send(view=_info_view("📊 Net Worth", body))
