"""
Economy — lottery commands (info, buy).
"""
from discord.ext import commands
from ..data import (
    _info_view, _reply, _fmt_remaining, _save_lottery, _check_achievements, locale_t,
    LOTTERY_TICKET_PRICE,
)
from utils.i18n import get_lang
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

T = locale_t(load_locales("cogs.economy", "lottery"))


class LotteryMixin:
    """lottery group commands."""

    @commands.hybrid_group(
        name="lottery", aliases=["lotto"],
        description=CMDS.text("lottery.description"),
        help=CMDS.help("lottery"),
        invoke_without_command=True
    )
    async def lottery(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        await self._lottery_info(ctx)

    async def _lottery_info(self, ctx: commands.Context):
        import time
        lang = get_lang(ctx)
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
            last_block = T(
                lang, "last_winner",
                name=who, pot=f"{int(self.lottery.get('last_pot', 0)):,}",
            )
        body = T(
            lang, "body",
            pot=f"{int(self.lottery['pot']):,}",
            time=_fmt_remaining(remain),
            tickets=int(data.get("lottery_tickets", 0)),
            price=f"{LOTTERY_TICKET_PRICE:,}",
            last=last_block,
        )
        await _reply(ctx, _info_view(T(lang, "title"), body))

    @lottery.command(name="info", description=CMDS.text("lottery.info.description"))
    async def lottery_info(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        await self._lottery_info(ctx)

    @lottery.command(name="buy", description=CMDS.text("lottery.buy.description"))
    async def lottery_buy(self, ctx: commands.Context, count: int = 1):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        if count <= 0:
            return await _reply(ctx, _info_view(
                T(lang, "bad_amount_title"), T(lang, "bad_count_body")))

        cost = LOTTERY_TICKET_PRICE * count
        data = await self.get_user_economy_data(ctx.author.id)
        if data["balance"] < cost:
            return await _reply(ctx, _info_view(
                T(lang, "no_cash_title"), T(lang, "no_cash_body", cost=f"{cost:,}")))

        effects    = data.setdefault("effects", {})
        bonus_mult = 2 if effects.pop("lottery_boost", 0) else 1
        added      = count * bonus_mult

        self._credit(
            data, -cost, "lottery_buy",
            T(lang, "note_buy_lucky" if bonus_mult > 1 else "note_buy", count=count),
        )
        data["lottery_tickets"] = int(data.get("lottery_tickets", 0)) + added
        # The lifetime counter is what the lottery badges read: ``lottery_tickets``
        # is reset by every draw, so it would make a badge unreachable for the
        # next week. Bonus tickets are not charged for, so only the paid count
        # moves the counter.
        data["lottery_tickets_bought"] = int(data.get("lottery_tickets_bought", 0)) + count
        self.lottery["pot"] = int(self.lottery.get("pot", 0)) + cost

        # Buying a ticket can be the action that earns a ticket badge, so the
        # unlock is paid and reported here instead of on the next economy command.
        unlocked = _check_achievements(data, lang=lang)

        # Save to database
        from ..data import _save_lottery_to_db
        await _save_lottery_to_db(self.bot, self.lottery)
        await self.save_user_economy_data(ctx.author.id)

        body = T(
            lang, "bought_body",
            tickets=int(data["lottery_tickets"]),
            cost=f"{cost:,}",
            pot=f"{int(self.lottery['pot']):,}",
        )
        if bonus_mult > 1:
            body += T(lang, "lucky")
        if unlocked:
            body += T(lang, "new_achievements", items=", ".join(unlocked))

        await _reply(ctx, _info_view(T(lang, "bought_title"), body))
