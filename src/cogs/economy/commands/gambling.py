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

    @commands.hybrid_command(name="crime",
                             description="Try to steal some extra treats",
                             help="{ 'en': 'try to steal some extra treats 😈', 'de': 'versuch, etwas zu stibitzen', 'es': 'intenta robar unas golosinas extra 😈' }")
    async def crime(self, ctx: commands.Context):
        import time
        data = self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        if now - int(data.get("last_crime", 0)) < COOLDOWN_CRIME:
            remain = COOLDOWN_CRIME - (now - int(data["last_crime"]))
            return await ctx.send(view=_info_view(
                "👮 Lay low",
                f"The shopkeeper's watching. Try again in **{_fmt_remaining(remain)}**.",
            ))

        effects = data.setdefault("effects", {})
        boost   = 0.25 if effects.pop("crime_boost", 0) else 0.0
        success = random.random() < (0.5 + boost)

        if success:
            reward = random.randint(200, 500)
            self._credit(data, reward, "crime", "successful heist")
            title, subtitle, amount, accent = ("😈 Got away!", "You swiped from the tip jar.", reward, ACCENT_GOLD)
        else:
            loss = random.randint(100, 300)
            loss = min(loss, int(data.get("balance", 0)))
            self._credit(data, -loss, "crime_fine", "caught and fined")
            title, subtitle, amount, accent = ("👮 Caught!", "You had to pay a fine.", -loss, ACCENT_RED)

        data["last_crime"] = now
        _check_achievements(data)
        self.save_economy_data()

        await self._send_reward_card(
            ctx, title=title, subtitle=subtitle, amount=amount, accent=accent,
            footer="Tip: use a lockpick before your next attempt for +25% success.",
        )

    @commands.hybrid_command(name="rob",
                             description="Try to rob another user",
                             help="{ 'en': 'try to rob another user 🔫', 'de': 'rauber jemanden aus', 'es': 'intenta robar a otro 🔫' }")
    async def rob(self, ctx: commands.Context, member: discord.Member):
        import time
        if member.id == ctx.author.id:
            return await ctx.send(view=_info_view("☕ Really?", "You can't rob yourself, silly!"))
        if member.bot:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_bot')} No can do", "Bots have nothing in their pockets."))

        data   = self.get_user_economy_data(ctx.author.id)
        target = self.get_user_economy_data(member.id)
        now = int(time.time())

        if data["balance"] < 100:
            return await ctx.send(view=_info_view("💸 Broke", "You need at least **100** coins to plan a robbery."))
        if target["balance"] < 100:
            return await ctx.send(view=_info_view("🥺 Mercy", "They don't have enough to rob — leave them alone!"))
        if now - int(data.get("last_rob", 0)) < COOLDOWN_ROB:
            remain = COOLDOWN_ROB - (now - int(data["last_rob"]))
            return await ctx.send(view=_info_view("🕵️ Lay low", f"Try again in **{_fmt_remaining(remain)}**."))

        target_effects = target.setdefault("effects", {})
        if target_effects.pop("rob_shield", 0):
            data["last_rob"] = now
            self.save_economy_data()
            return await ctx.send(view=_info_view(
                "🛡️ Blocked!",
                f"{member.display_name} had a **Tip Jar Lock** active. The robbery failed and they kept everything.",
            ))

        success = random.random() < 0.4
        if success:
            amount = random.randint(10, min(target["balance"], 500))
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
        self.save_economy_data()
        await self._send_reward_card(ctx, title=title, subtitle=subtitle, amount=shown_amount, accent=accent)
