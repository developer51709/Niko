"""
Economy — lottery commands (info, buy).
"""
from discord.ext import commands
from ..data import (
    _info_view, _fmt_remaining, _save_lottery, _check_achievements, get_emoji,
    LOTTERY_TICKET_PRICE,
)


class LotteryMixin:
    """lottery group commands."""

    @commands.hybrid_group(
        name="lottery", aliases=["lotto"],
        description="Play the weekly lottery",
        help="{ 'en': 'play the weekly lottery 🎰', 'de': 'spiele die wöchentliche Lotterie', 'es': 'juega la lotería semanal 🎰' }",
        invoke_without_command=True
    )
    async def lottery(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        await self._lottery_info(ctx)

    async def _lottery_info(self, ctx: commands.Context):
        import time
        data = await self.get_user_economy_data(ctx.author.id)
        now    = int(time.time())
        
        # Load lottery state from database
        from ..data import _get_lottery_from_db
        self.lottery = await _get_lottery_from_db(self.bot)
        
        remain = max(0, int(self.lottery.get("next_draw", now)) - now)
        last   = self.lottery.get("last_winner")
        last_block = ""
        if last:
            user = self.bot.get_user(int(last)) if last.isdigit() else None
            who  = user.display_name if user else last
            last_block = f"\n-# Last winner: **{who}** scooped **{int(self.lottery.get('last_pot', 0)):,}** 🪙"
        body = (
            f"💸 **Pot**: **{int(self.lottery['pot']):,}** 🪙\n"
            f"🕒 **Next draw**: in **{_fmt_remaining(remain)}**\n"
            f"🎟️ **Your tickets**: **{int(data.get('lottery_tickets', 0))}**\n\n"
            f"Tickets cost **{LOTTERY_TICKET_PRICE:,}** 🪙 each. Buy with `lottery buy <count>`.{last_block}"
        )
        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view("🎰 Lottery", body))
        else:
            await ctx.send(view=_info_view("🎰 Lottery", body))

    @lottery.command(name="info", description="Show the current lottery pot, draw time and your tickets")
    async def lottery_info(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        await self._lottery_info(ctx)

    @lottery.command(name="buy", description="Buy lottery tickets")
    async def lottery_buy(self, ctx: commands.Context, count: int = 1):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        if count <= 0:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('cross')} Bad amount", "Count must be at least 1."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('cross')} Bad amount", "Count must be at least 1."))

        cost = LOTTERY_TICKET_PRICE * count
        data = await self.get_user_economy_data(ctx.author.id)
        if data["balance"] < cost:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("💸 Not enough cash", f"That costs **{cost:,}** 🪙."))
            else:
                return await ctx.send(view=_info_view("💸 Not enough cash", f"That costs **{cost:,}** 🪙."))

        effects    = data.setdefault("effects", {})
        bonus_mult = 2 if effects.pop("lottery_boost", 0) else 1
        added      = count * bonus_mult

        self._credit(data, -cost, "lottery_buy", f"{count} tickets" + (" (lucky x2)" if bonus_mult > 1 else ""))
        data["lottery_tickets"] = int(data.get("lottery_tickets", 0)) + added
        # The lifetime counter is what the lottery badges read: ``lottery_tickets``
        # is reset by every draw, so it would make a badge unreachable for the
        # next week. Bonus tickets are not charged for, so only the paid count
        # moves the counter.
        data["lottery_tickets_bought"] = int(data.get("lottery_tickets_bought", 0)) + count
        self.lottery["pot"] = int(self.lottery.get("pot", 0)) + cost

        # Buying a ticket can be the action that earns a ticket badge, so the
        # unlock is paid and reported here instead of on the next economy command.
        unlocked = _check_achievements(data)

        # Save to database
        from ..data import _save_lottery_to_db
        await _save_lottery_to_db(self.bot, self.lottery)
        await self.save_user_economy_data(ctx.author.id)

        body = (
            f"You now hold **{int(data['lottery_tickets'])}** tickets.\n"
            f"• Spent **{cost:,}** 🪙\n"
            f"• Pot is now **{int(self.lottery['pot']):,}** 🪙"
            + (f"\n-# Lucky charm doubled your tickets! 🍀" if bonus_mult > 1 else "")
        )
        if unlocked:
            body += "\n\n**New achievements** " + ", ".join(unlocked)

        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view("🎟️ Tickets bought", body))
        else:
            await ctx.send(view=_info_view("🎟️ Tickets bought", body))
