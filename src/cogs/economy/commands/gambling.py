"""
Economy — gambling commands (crime, rob).
"""
import random

import discord
from discord.ext import commands
from ..data import (
    _info_view, _reply, _check_achievements, locale_t,
    COOLDOWN_CRIME, COOLDOWN_ROB,
    get_emoji,
    ACCENT_GOLD, ACCENT_RED,
)
from utils.cooldown import cooldown_ready_at, cooldown_view
from utils.i18n import get_lang
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

T = locale_t(load_locales("cogs.economy", "gambling"))


class GamblingMixin:
    """crime and rob commands."""


    @commands.hybrid_command(
        name="crime",
        description=CMDS.text("crime.description"),
        help=CMDS.help("crime"),
    )
    async def crime(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        import time
        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        if now - int(data.get("last_crime", 0)) < COOLDOWN_CRIME:
            view = cooldown_view(
                T(lang, "crime_cd_action"),
                cooldown_ready_at(data.get("last_crime"), COOLDOWN_CRIME),
                title=T(lang, "crime_cd_title"),
                note=T(lang, "crime_cd_note"),
            )
            return await _reply(ctx, view)

        effects = data.setdefault("effects", {})
        boost   = 0.25 if effects.pop("crime_boost", 0) else 0.0
        success = random.random() < (0.5 + boost)

        if success:
            reward = random.randint(200, 500)
            if effects.pop("gambling_boost", 0):
                reward = int(reward * 1.5)
            self._credit(data, reward, "crime", T(lang, "note_crime_win"))
            title, subtitle, amount, accent = (
                T(lang, "crime_win_title"), T(lang, "crime_win_sub"), reward, ACCENT_GOLD)
        else:
            loss = random.randint(100, 300)
            loss = min(loss, int(data.get("balance", 0)))
            self._credit(data, -loss, "crime_fine", T(lang, "note_crime_loss"))
            title, subtitle, amount, accent = (
                T(lang, "crime_loss_title"), T(lang, "crime_loss_sub"), -loss, ACCENT_RED)

        data["last_crime"] = now
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)

        await self._send_reward_card(
            ctx, title=title, subtitle=subtitle, amount=amount, accent=accent,
            footer=T(lang, "crime_tip"),
        )


    @commands.hybrid_command(
        name="rob",
        description=CMDS.text("rob.description"),
        help=CMDS.help("rob"),
    )
    async def rob(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        import time
        lang = get_lang(ctx)
        if member.id == ctx.author.id:
            return await _reply(ctx, _info_view(
                T(lang, "rob_self_title"), T(lang, "rob_self_body")))

        if member.bot:
            return await _reply(ctx, _info_view(
                T(lang, "rob_bot_title", bot=get_emoji("bot")),
                T(lang, "rob_bot_body")))

        data   = await self.get_user_economy_data(ctx.author.id)
        target = await self.get_user_economy_data(member.id)
        now = int(time.time())

        if data["balance"] < 100:
            return await _reply(ctx, _info_view(
                T(lang, "rob_broke_title"), T(lang, "rob_broke_body")))

        if target["balance"] < 100:
            return await _reply(ctx, _info_view(
                T(lang, "rob_mercy_title"), T(lang, "rob_mercy_body")))

        if now - int(data.get("last_rob", 0)) < COOLDOWN_ROB:
            view = cooldown_view(
                T(lang, "rob_cd_action"),
                cooldown_ready_at(data.get("last_rob"), COOLDOWN_ROB),
                title=T(lang, "rob_cd_title"),
            )
            return await _reply(ctx, view)

        target_effects = target.setdefault("effects", {})
        if target_effects.pop("rob_shield", 0):
            data["last_rob"] = now
            await self.save_user_economy_data(ctx.author.id)
            await self.save_user_economy_data(member.id)
            return await _reply(ctx, _info_view(
                T(lang, "rob_shield_title"),
                T(lang, "rob_shield_body", name=member.display_name),
            ))

        success = random.random() < 0.4
        effects = data.setdefault("effects", {})
        if success:
            amount = random.randint(10, min(target["balance"], 500))
            if effects.pop("gambling_boost", 0):
                amount = int(amount * 1.5)
            self._credit(data, amount, "rob",
                         T(lang, "note_rob_win", name=member.display_name))
            self._credit(target, -amount, "robbed",
                         T(lang, "note_robbed", name=ctx.author.display_name))
            title, subtitle, accent = (
                T(lang, "rob_win_title"),
                T(lang, "rob_win_sub", name=member.display_name),
                ACCENT_GOLD,
            )
            shown_amount = amount
        else:
            loss = 150
            loss = min(loss, int(data.get("balance", 0)))
            self._credit(data, -loss, "rob_fail",
                         T(lang, "note_rob_fail", name=member.display_name))
            self._credit(target, loss, "rob_apology",
                         T(lang, "note_rob_apology", name=ctx.author.display_name))
            title, subtitle, accent = (
                T(lang, "rob_fail_title"),
                T(lang, "rob_fail_sub", name=member.display_name),
                ACCENT_RED,
            )
            shown_amount = -loss

        data["last_rob"] = now
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        await self.save_user_economy_data(member.id)
        await self._send_reward_card(ctx, title=title, subtitle=subtitle, amount=shown_amount, accent=accent)


    @commands.hybrid_command(
        name="coinflip", aliases=["cf"],
        description=CMDS.text("coinflip.description"),
        help=CMDS.help("coinflip"),
    )
    async def coinflip(self, ctx: commands.Context, amount: int, call: str = "heads"):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        if amount <= 0:
            return await self._send_err(ctx, T(lang, "bad_amount_title"), T(lang, "bad_bet_body"))

        data = await self.get_user_economy_data(ctx.author.id)
        if int(data.get("balance", 0)) < amount:
            return await self._send_err(
                ctx, T(lang, "no_cash_title"),
                T(lang, "no_cash_body", amount=f"{amount:,}", balance=f"{data['balance']:,}"))

        call = call.lower().strip()
        if call not in ("heads", "h", "tails", "t"):
            return await self._send_err(
                ctx, T(lang, "cf_bad_call_title"), T(lang, "cf_bad_call_body"))
        call = "heads" if call in ("heads", "h") else "tails"
        call_name = T(lang, "cf_heads" if call == "heads" else "cf_tails")

        effects = data.setdefault("effects", {})
        has_booster = effects.pop("coin_booster", 0)
        # Booster gives 60/40 odds instead of 50/50
        success = random.random() < (0.60 if has_booster else 0.50)
        result = "heads" if random.random() < 0.5 else "tails"
        result_name = T(lang, "cf_heads" if result == "heads" else "cf_tails")
        won = success and result == call

        if won:
            profit = amount
            self._credit(data, profit, "coinflip_win",
                         T(lang, "note_cf_win", call=call_name))
            title = T(lang, "cf_heads_title" if result == "heads" else "cf_tails_title")
            subtitle, accent, shown = (
                T(lang, "cf_win_sub", call=call_name), ACCENT_GOLD, profit)
        else:
            self._credit(data, -amount, "coinflip_loss",
                         T(lang, "note_cf_loss", result=result_name))
            title = T(lang, "cf_heads_title" if result == "heads" else "cf_tails_title")
            subtitle, accent, shown = (
                T(lang, "cf_loss_sub", call=call_name, result=result_name),
                ACCENT_RED, -amount)

        footer = T(lang, "cf_booster") if has_booster else ""

        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        await self._send_reward_card(
            ctx, title=title, subtitle=subtitle, amount=shown, accent=accent, footer=footer,
        )

    @commands.hybrid_command(
        name="dice", aliases=["roll"],
        description=CMDS.text("dice.description"),
        help=CMDS.help("dice"),
    )
    async def dice(self, ctx: commands.Context, amount: int, target: int = 50):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        if amount <= 0:
            return await self._send_err(ctx, T(lang, "bad_amount_title"), T(lang, "bad_bet_body"))

        data = await self.get_user_economy_data(ctx.author.id)
        if int(data.get("balance", 0)) < amount:
            return await self._send_err(
                ctx, T(lang, "no_cash_title"),
                T(lang, "no_cash_body", amount=f"{amount:,}", balance=f"{data['balance']:,}"))

        if not 1 <= target <= 99:
            return await self._send_err(
                ctx, T(lang, "dice_bad_target_title"), T(lang, "dice_bad_target_body"))

        roll = random.randint(1, 100)
        won = roll >= target

        # Payout scales inversely with target difficulty
        multiplier = round(100 / max(target, 1), 2)
        multiplier = max(1.01, min(multiplier, 50.0))  # cap payout at 50x

        effects = data.setdefault("effects", {})
        if won:
            profit = int(amount * multiplier)
            if effects.pop("gambling_boost", 0):
                profit = int(profit * 1.5)
            self._credit(data, profit, "dice_win", T(lang, "note_dice", roll=roll, target=target))
            title = T(lang, "dice_win_title")
            subtitle = T(lang, "dice_win_sub", roll=roll, target=target, mult=f"{multiplier:.1f}")
            accent = ACCENT_GOLD
            shown = profit
        else:
            self._credit(data, -amount, "dice_loss", T(lang, "note_dice", roll=roll, target=target))
            title = T(lang, "dice_loss_title")
            subtitle = T(lang, "dice_loss_sub", roll=roll, target=target)
            accent = ACCENT_RED
            shown = -amount

        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        await self._send_reward_card(
            ctx, title=title, subtitle=subtitle, amount=shown, accent=accent,
        )

    async def _send_err(self, ctx, title: str, body: str):
        await _reply(ctx, _info_view(title, body))
