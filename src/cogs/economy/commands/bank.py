"""
Economy — bank commands (deposit, withdraw, upgrade).
"""
from discord.ext import commands
from ..data import (
    _info_view, _reply, _check_achievements, _log_tx, locale_t,
    BANK_TIERS, bank_info, bank_cap, bank_name, bank_rate, max_bank_tier,
)
from utils.i18n import get_lang
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

T = locale_t(load_locales("cogs.economy", "bank"))


class BankMixin:
    """bank group commands."""


    @commands.hybrid_group(
        name="bank",
        description=CMDS.text("bank.description"),
        help=CMDS.help("bank"),
        invoke_without_command=True
    )
    async def bank(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        tier = int(data.get("bank_tier", 0))
        cap  = bank_cap(tier)
        rate = bank_rate(tier)
        body = T(
            lang, "body",
            tier=bank_name(tier), n=tier + 1, total=len(BANK_TIERS),
            stored=f"{int(data['bank']):,}", cap=f"{cap:,}", rate=f"{rate*100:.2f}",
        )
        await _reply(ctx, _info_view(T(lang, "title"), body))


    @bank.command(name="deposit", description=CMDS.text("bank.deposit.description"))
    async def bank_deposit(self, ctx: commands.Context, amount: str):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        cap  = bank_cap(int(data.get("bank_tier", 0)))
        free = max(0, cap - int(data["bank"]))

        if amount.lower() == "all":
            amt = min(int(data["balance"]), free)
        else:
            try:
                amt = int(amount)
            except ValueError:
                return await _reply(ctx, _info_view(
                    T(lang, "bad_amount_title"), T(lang, "bad_amount_body")))

        if amt <= 0:
            return await _reply(ctx, _info_view(
                T(lang, "nothing_deposit_title"), T(lang, "nothing_deposit_body")))

        if amt > data["balance"]:
            return await _reply(ctx, _info_view(
                T(lang, "no_cash_title"), T(lang, "no_cash_body")))

        if amt > free:
            return await _reply(ctx, _info_view(
                T(lang, "vault_full_title"),
                T(lang, "vault_full_body",
                  free=f"{free:,}", tier=bank_name(data["bank_tier"])),
            ))

        data["balance"] -= amt
        data["bank"]    += amt
        _log_tx(data, "deposit", amt, T(lang, "note_deposit"))
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        await _reply(ctx, _info_view(
            T(lang, "deposited_title"),
            T(lang, "deposited_body",
              amount=f"{amt:,}", vault=f"{data['bank']:,}", cap=f"{cap:,}"),
        ))


    @bank.command(name="withdraw", description=CMDS.text("bank.withdraw.description"))
    async def bank_withdraw(self, ctx: commands.Context, amount: str):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        if amount.lower() == "all":
            amt = int(data["bank"])
        else:
            try:
                amt = int(amount)
            except ValueError:
                return await _reply(ctx, _info_view(
                    T(lang, "bad_amount_title"), T(lang, "bad_amount_body")))

        if amt <= 0:
            return await _reply(ctx, _info_view(
                T(lang, "nothing_withdraw_title"), T(lang, "nothing_withdraw_body")))

        if amt > data["bank"]:
            return await _reply(ctx, _info_view(
                T(lang, "vault_low_title"), T(lang, "vault_low_body")))

        data["bank"]    -= amt
        data["balance"] += amt
        _log_tx(data, "withdraw", amt, T(lang, "note_withdraw"))
        await self.save_user_economy_data(ctx.author.id)
        await _reply(ctx, _info_view(
            T(lang, "withdrawn_title"),
            T(lang, "withdrawn_body", amount=f"{amt:,}", wallet=f"{data['balance']:,}"),
        ))


    @bank.command(name="upgrade", description=CMDS.text("bank.upgrade.description"))
    async def bank_upgrade(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        cur  = int(data.get("bank_tier", 0))
        if cur >= max_bank_tier():
            return await _reply(ctx, _info_view(
                T(lang, "maxed_title"), T(lang, "maxed_body")))

        next_tier = cur + 1
        cost = bank_cap(next_tier) // 2
        if data["balance"] + data["bank"] < cost:
            return await _reply(ctx, _info_view(
                T(lang, "no_worth_title"),
                T(lang, "no_worth_body",
                  tier=bank_name(next_tier), cost=f"{cost:,}"),
            ))

        from_wallet = min(int(data["balance"]), cost)
        from_bank   = cost - from_wallet
        data["balance"] -= from_wallet
        data["bank"]    -= from_bank
        data["bank_tier"] = next_tier
        _log_tx(data, "upgrade", -cost, T(lang, "note_upgrade", tier=bank_name(next_tier)))
        await self.save_user_economy_data(ctx.author.id)
        await _reply(ctx, _info_view(
            T(lang, "upgraded_title"),
            T(lang, "upgraded_body",
              tier=bank_name(next_tier),
              cap=f"{bank_cap(next_tier):,}",
              rate=f"{bank_rate(next_tier)*100:.2f}"),
        ))
