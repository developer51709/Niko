"""
Economy — lottery commands (info, buy).
"""
from discord.ext import commands
from ..data import (
    _info_view, _fmt_remaining, _save_lottery, get_emoji,
    LOTTERY_TICKET_PRICE,
)


class LotteryMixin:
    """lottery group commands."""

    @commands.hybrid_group(name="lottery", aliases=["lotto"],
                           description="Play the weekly café lottery",
                           help="{ 'en': 'play the weekly café lottery 🎰', 'de': 'spiele die wöchentliche Lotterie', 'es': 'juega la lotería semanal 🎰' }",
                           invoke_without_command=True)
    async def lottery(self, ctx: commands.Context):
        await self._lottery_info(ctx)

    async def _lottery_info(self, ctx: commands.Context):
        import time
        data = self.get_user_economy_data(ctx.author.id)
        now    = int(time.time())
        remain = max(0, int(self.lottery.get("next_draw", now)) - now)
        last   = self.lottery.get("last_winner")
        last_block = ""
        if last:
            user = self.bot.get_user(int(last)) if last.isdigit() else None
            who  = user.display_name if user else last
            last_block = f"\n-# Last winner: **{who}** scooped **{int(self.lottery.get('last_pot', 0)):,}** 🥐"
        body = (
            f"💸 **Pot**: **{int(self.lottery['pot']):,}** 🥐\n"
            f"🕒 **Next draw**: in **{_fmt_remaining(remain)}**\n"
            f"🎟️ **Your tickets**: **{int(data.get('lottery_tickets', 0))}**\n\n"
            f"Tickets cost **{LOTTERY_TICKET_PRICE:,}** 🥐 each. Buy with `lottery buy <count>`.{last_block}"
        )
        await ctx.send(view=_info_view("🎰 Café Lottery", body))

    @lottery.command(name="info", description="Show the current lottery pot, draw time and your tickets")
    async def lottery_info(self, ctx: commands.Context):
        await self._lottery_info(ctx)

    @lottery.command(name="buy", description="Buy lottery tickets")
    async def lottery_buy(self, ctx: commands.Context, count: int = 1):
        if count <= 0:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Count must be at least 1."))
        cost = LOTTERY_TICKET_PRICE * count
        data = self.get_user_economy_data(ctx.author.id)
        if data["balance"] < cost:
            return await ctx.send(view=_info_view("💸 Not enough cash", f"That costs **{cost:,}** 🥐."))

        effects    = data.setdefault("effects", {})
        bonus_mult = 2 if effects.pop("lottery_boost", 0) else 1
        added      = count * bonus_mult

        self._credit(data, -cost, "lottery_buy", f"{count} tickets" + (" (lucky x2)" if bonus_mult > 1 else ""))
        data["lottery_tickets"] = int(data.get("lottery_tickets", 0)) + added
        self.lottery["pot"] = int(self.lottery.get("pot", 0)) + cost
        _save_lottery(self.lottery)
        self.save_economy_data()

        await ctx.send(view=_info_view(
            "🎟️ Tickets bought",
            f"You now hold **{int(data['lottery_tickets'])}** tickets.\n"
            f"• Spent **{cost:,}** 🥐\n"
            f"• Pot is now **{int(self.lottery['pot']):,}** 🥐"
            + (f"\n-# Lucky charm doubled your tickets! 🍀" if bonus_mult > 1 else ""),
        ))
