"""
Economy — gambling commands (crime, rob).
"""
import random

import discord
from discord.ext import commands
from ..data import (
    _info_view, _fmt_remaining, _check_achievements,
    COOLDOWN_CRIME, COOLDOWN_ROB,
    get_emoji,
    ACCENT_GOLD, ACCENT_RED,
)


class GamblingMixin:
    """crime and rob commands."""


    @commands.hybrid_command(
        name="crime",
        description="Try to steal some extra treats",
        help="{ 'en': 'try to steal some extra treats 😈', 'de': 'versuch, etwas zu stibitzen', 'es': 'intenta robar unas golosinas extra 😈' }"
    )
    async def crime(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        import time
        data = await self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        if now - int(data.get("last_crime", 0)) < COOLDOWN_CRIME:
            remain = COOLDOWN_CRIME - (now - int(data["last_crime"]))
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(
                    "👮 Lay low",
                    f"The shopkeeper's watching. Try again in **{_fmt_remaining(remain)}**.",
                ))
            else:
                return await ctx.send(view=_info_view(
                    "👮 Lay low",
                    f"The shopkeeper's watching. Try again in **{_fmt_remaining(remain)}**.",
                ))

        effects = data.setdefault("effects", {})
        boost   = 0.25 if effects.pop("crime_boost", 0) else 0.0
        success = random.random() < (0.5 + boost)

        if success:
            reward = random.randint(200, 500)
            if effects.pop("gambling_boost", 0):
                reward = int(reward * 1.5)
            self._credit(data, reward, "crime", "successful heist")
            title, subtitle, amount, accent = ("😈 Got away!", "You swiped from the tip jar.", reward, ACCENT_GOLD)
        else:
            loss = random.randint(100, 300)
            loss = min(loss, int(data.get("balance", 0)))
            self._credit(data, -loss, "crime_fine", "caught and fined")
            title, subtitle, amount, accent = ("👮 Caught!", "You had to pay a fine.", -loss, ACCENT_RED)

        data["last_crime"] = now
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)

        await self._send_reward_card(
            ctx, title=title, subtitle=subtitle, amount=amount, accent=accent,
            footer="Tip: use a lockpick before your next attempt for +25% success.",
        )


    @commands.hybrid_command(
        name="rob",
        description="Try to rob another user",
        help="{ 'en': 'try to rob another user 🔫', 'de': 'rauber jemanden aus', 'es': 'intenta robar a otro 🔫' }"
    )
    async def rob(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        import time
        if member.id == ctx.author.id:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("☕ Really?", "You can't rob yourself, silly!"))
            else:
                return await ctx.send(view=_info_view("☕ Really?", "You can't rob yourself, silly!"))

        if member.bot:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('icon_bot')} No can do", "Bots have nothing in their pockets."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_bot')} No can do", "Bots have nothing in their pockets."))

        data   = await self.get_user_economy_data(ctx.author.id)
        target = await self.get_user_economy_data(member.id)
        now = int(time.time())

        if data["balance"] < 100:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("💸 Broke", "You need at least **100** coins to plan a robbery."))
            else:
                return await ctx.send(view=_info_view("💸 Broke", "You need at least **100** coins to plan a robbery."))

        if target["balance"] < 100:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("🥺 Mercy", "They don't have enough to rob — leave them alone!"))
            else:
                return await ctx.send(view=_info_view("🥺 Mercy", "They don't have enough to rob — leave them alone!"))

        if now - int(data.get("last_rob", 0)) < COOLDOWN_ROB:
            remain = COOLDOWN_ROB - (now - int(data["last_rob"]))
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("🕵️ Lay low", f"Try again in **{_fmt_remaining(remain)}**."))
            else:
                return await ctx.send(view=_info_view("🕵️ Lay low", f"Try again in **{_fmt_remaining(remain)}**."))

        target_effects = target.setdefault("effects", {})
        if target_effects.pop("rob_shield", 0):
            data["last_rob"] = now
            await self.save_user_economy_data(ctx.author.id)
            await self.save_user_economy_data(member.id)
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(
                    "🛡️ Blocked!",
                    f"{member.display_name} had a **Tip Jar Lock** active. The robbery failed and they kept everything.",
                ))
            else:
                return await ctx.send(view=_info_view(
                    "🛡️ Blocked!",
                    f"{member.display_name} had a **Tip Jar Lock** active. The robbery failed and they kept everything.",
                ))

        success = random.random() < 0.4
        effects = data.setdefault("effects", {})
        if success:
            amount = random.randint(10, min(target["balance"], 500))
            if effects.pop("gambling_boost", 0):
                amount = int(amount * 1.5)
            self._credit(data, amount, "rob", f"from {member.display_name}")
            self._credit(target, -amount, "robbed", f"by {ctx.author.display_name}")
            title, subtitle, accent = ("💰 Score!", f"You robbed {member.display_name}.", ACCENT_GOLD)
            shown_amount = amount
        else:
            loss = 150
            loss = min(loss, int(data.get("balance", 0)))
            self._credit(data, -loss, "rob_fail", f"caught by {member.display_name}")
            self._credit(target, loss, "rob_apology", f"from {ctx.author.display_name}")
            title, subtitle, accent = ("👮 Caught!", f"You had to pay {member.display_name} as apology.", ACCENT_RED)
            shown_amount = -loss

        data["last_rob"] = now
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        await self.save_user_economy_data(member.id)
        await self._send_reward_card(ctx, title=title, subtitle=subtitle, amount=shown_amount, accent=accent)


    @commands.hybrid_command(
        name="coinflip", aliases=["flip", "cf"],
        description="Flip a coin — double or nothing",
        help="{ 'en': 'flip a coin for double or nothing 🪙', 'de': 'wirf eine Münze', 'es': 'lanza una moneda 🪙' }"
    )
    async def coinflip(self, ctx: commands.Context, amount: int, call: str = "heads"):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        if amount <= 0:
            return await self._send_err(ctx, f"{get_emoji('icon_cross')} Bad amount", "Bet must be at least **1** 🥐.")

        data = await self.get_user_economy_data(ctx.author.id)
        if int(data.get("balance", 0)) < amount:
            return await self._send_err(ctx, "💸 Not enough cash", f"You need **{amount:,}** 🥐 but only have **{data['balance']:,}**.")

        call = call.lower().strip()
        if call not in ("heads", "h", "tails", "t"):
            return await self._send_err(ctx, f"{get_emoji('icon_cross')} Invalid call", "Pick **heads** or **tails**.")
        call = "heads" if call in ("heads", "h") else "tails"

        effects = data.setdefault("effects", {})
        has_booster = effects.pop("coin_booster", 0)
        # Booster gives 60/40 odds instead of 50/50
        success = random.random() < (0.60 if has_booster else 0.50)
        result = "heads" if random.random() < 0.5 else "tails"
        won = success and result == call

        if won:
            profit = amount
            self._credit(data, profit, "coinflip_win", f"won {call}")
            title, subtitle, accent = (
                "🪙 Heads!" if result == "heads" else "🪙 Tails!",
                f"You called **{call}** and won!",
                ACCENT_GOLD,
            )
            shown = profit
        else:
            self._credit(data, -amount, "coinflip_loss", f"lost — landed {result}")
            title, subtitle, accent = (
                "🪙 Heads!" if result == "heads" else "🪙 Tails!",
                f"You called **{call}** but it landed **{result}**.",
                ACCENT_RED,
            )
            shown = -amount

        footer = ""
        if has_booster:
            footer = "-# 🍀 Coin Booster gave you 60/40 odds!"

        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        await self._send_reward_card(
            ctx, title=title, subtitle=subtitle, amount=shown, accent=accent, footer=footer,
        )

    @commands.hybrid_command(
        name="dice", aliases=["roll"],
        description="Roll a die — pick a number and hope for the best",
        help="{ 'en': 'roll a die and bet on the outcome 🎲', 'de': 'würfle und setze auf eine Zahl', 'es': 'lanza un dado 🎲' }"
    )
    async def dice(self, ctx: commands.Context, amount: int, target: int = 50):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        if amount <= 0:
            return await self._send_err(ctx, f"{get_emoji('icon_cross')} Bad amount", "Bet must be at least **1** 🥐.")

        data = await self.get_user_economy_data(ctx.author.id)
        if int(data.get("balance", 0)) < amount:
            return await self._send_err(ctx, "💸 Not enough cash", f"You need **{amount:,}** 🥐 but only have **{data['balance']:,}**.")

        if not 1 <= target <= 99:
            return await self._send_err(ctx, f"{get_emoji('icon_cross')} Invalid target", "Target must be between **1** and **99**.")

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
            self._credit(data, profit, "dice_win", f"rolled {roll} (target {target}+)")
            title = "🎲 Great roll!"
            subtitle = f"Rolled **{roll}** — needed **{target}+** (×{multiplier:.1f})"
            accent = ACCENT_GOLD
            shown = profit
        else:
            self._credit(data, -amount, "dice_loss", f"rolled {roll} (target {target}+)")
            title = "🎲 Bust!"
            subtitle = f"Rolled **{roll}** — needed **{target}+**. Better luck next time!"
            accent = ACCENT_RED
            shown = -amount

        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        await self._send_reward_card(
            ctx, title=title, subtitle=subtitle, amount=shown, accent=accent,
        )

    async def _send_err(self, ctx, title: str, body: str):
        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view(title, body))
        else:
            await ctx.send(view=_info_view(title, body))
