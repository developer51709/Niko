# ============================
#  IMPORTS
# ============================

import discord
from discord.ext import commands
import random
import time
import asyncio

# ============================
#  CONSTANTS
# ============================

ROULETTE_COOLDOWN = 60  # or use env var if you prefer

# European wheel layout (single zero)
EUROPEAN_WHEEL = [
    0,
    32, 15, 19, 4, 21, 2, 25, 17, 34, 6,
    27, 13, 36, 11, 30, 8, 23, 10, 5, 24,
    16, 33, 1, 20, 14, 31, 9, 22, 18, 29,
    7, 28, 12, 35, 3, 26
]

RED_NUMBERS = {
    1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
}

BLACK_NUMBERS = {
    2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35
}

# ============================
#  BET TYPES
# ============================

BET_TYPES = {
    "red": "Red",
    "black": "Black",
    "odd": "Odd",
    "even": "Even",
    "high": "High (19–36)",
    "low": "Low (1–18)",
    "dozen1": "1st Dozen (1–12)",
    "dozen2": "2nd Dozen (13–24)",
    "dozen3": "3rd Dozen (25–36)",
    "column1": "Column 1",
    "column2": "Column 2",
    "column3": "Column 3",
    "straight": "Straight (Single Number)",
    "split": "Split (2 Numbers)",
    "street": "Street (3 Numbers)",
    "corner": "Corner (4 Numbers)",
    "line": "Line (6 Numbers)"
}

# ============================
#  UI COMPONENTS
# ============================

class BetTypeView(discord.ui.View):
    def __init__(self, ctx, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Red / Black", style=discord.ButtonStyle.red)
    async def rb(self, interaction, button):
        self.choice = "color"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Odd / Even", style=discord.ButtonStyle.blurple)
    async def oe(self, interaction, button):
        self.choice = "parity"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="High / Low", style=discord.ButtonStyle.green)
    async def hl(self, interaction, button):
        self.choice = "range"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Dozens", style=discord.ButtonStyle.gray)
    async def doz(self, interaction, button):
        self.choice = "dozen"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Columns", style=discord.ButtonStyle.gray)
    async def col(self, interaction, button):
        self.choice = "column"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Inside Bets", style=discord.ButtonStyle.green)
    async def inside(self, interaction, button):
        self.choice = "inside"
        self.stop()
        await interaction.response.defer()


class ColorChoiceView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Red", style=discord.ButtonStyle.red)
    async def red(self, interaction, button):
        self.choice = "red"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Black", style=discord.ButtonStyle.gray)
    async def black(self, interaction, button):
        self.choice = "black"
        self.stop()
        await interaction.response.defer()


class ParityChoiceView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Odd", style=discord.ButtonStyle.blurple)
    async def odd(self, interaction, button):
        self.choice = "odd"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Even", style=discord.ButtonStyle.blurple)
    async def even(self, interaction, button):
        self.choice = "even"
        self.stop()
        await interaction.response.defer()


class RangeChoiceView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Low (1–18)", style=discord.ButtonStyle.green)
    async def low(self, interaction, button):
        self.choice = "low"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="High (19–36)", style=discord.ButtonStyle.green)
    async def high(self, interaction, button):
        self.choice = "high"
        self.stop()
        await interaction.response.defer()


class DozenChoiceView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="1st Dozen", style=discord.ButtonStyle.gray)
    async def d1(self, interaction, button):
        self.choice = "dozen1"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="2nd Dozen", style=discord.ButtonStyle.gray)
    async def d2(self, interaction, button):
        self.choice = "dozen2"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="3rd Dozen", style=discord.ButtonStyle.gray)
    async def d3(self, interaction, button):
        self.choice = "dozen3"
        self.stop()
        await interaction.response.defer()


class ColumnChoiceView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Column 1", style=discord.ButtonStyle.gray)
    async def c1(self, interaction, button):
        self.choice = "column1"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Column 2", style=discord.ButtonStyle.gray)
    async def c2(self, interaction, button):
        self.choice = "column2"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Column 3", style=discord.ButtonStyle.gray)
    async def c3(self, interaction, button):
        self.choice = "column3"
        self.stop()
        await interaction.response.defer()


class InsideBetDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Straight (Single Number)", value="straight"),
            discord.SelectOption(label="Split (2 Numbers)", value="split"),
            discord.SelectOption(label="Street (3 Numbers)", value="street"),
            discord.SelectOption(label="Corner (4 Numbers)", value="corner"),
            discord.SelectOption(label="Line (6 Numbers)", value="line"),
        ]
        super().__init__(placeholder="Choose inside bet type", options=options)

    async def callback(self, interaction):
        self.view.choice = self.values[0]
        self.view.stop()
        await interaction.response.defer()


class InsideBetView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.choice = None
        self.add_item(InsideBetDropdown())

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id

# ============================
#  NUMBER SELECTION DROPDOWNS
# ============================

class NumberDropdown(discord.ui.Select):
    def __init__(self, count):
        options = [
            discord.SelectOption(label=str(i), value=str(i))
            for i in range(37)
        ]
        super().__init__(
            placeholder=f"Select {count} number(s)",
            min_values=count,
            max_values=count,
            options=options
        )

    async def callback(self, interaction):
        self.view.choice = [int(v) for v in self.values]
        self.view.stop()
        await interaction.response.defer()


class NumberSelectView(discord.ui.View):
    def __init__(self, ctx, count):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.choice = None
        self.add_item(NumberDropdown(count))

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id


# ============================
#  CHIP AMOUNT BUTTONS
# ============================

class ChipView(discord.ui.View):
    def __init__(self, ctx, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.amount = None

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="10", style=discord.ButtonStyle.green)
    async def c10(self, interaction, button):
        self.amount = 10
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="50", style=discord.ButtonStyle.green)
    async def c50(self, interaction, button):
        self.amount = 50
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="100", style=discord.ButtonStyle.green)
    async def c100(self, interaction, button):
        self.amount = 100
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="500", style=discord.ButtonStyle.green)
    async def c500(self, interaction, button):
        self.amount = 500
        self.stop()
        await interaction.response.defer()


# ============================
#  SPIN AGAIN BUTTON
# ============================

class SpinAgainView(discord.ui.View):
    def __init__(self, ctx, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Spin Again", style=discord.ButtonStyle.green)
    async def spin(self, interaction, button):
        self.choice = "spin"
        self.stop()
        await interaction.response.defer()


# ============================
#  ROULETTE COG
# ============================

class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roulette")
    async def roulette(self, ctx):
        """Play interactive European roulette."""

        economy = self.bot.get_cog("EconomyCog")
        user_data = economy.get_user_economy_data(ctx.author.id)

        # Cooldown check
        if user_data["last_roulette"] + ROULETTE_COOLDOWN > time.time():
            return await ctx.send(f"You can only play roulette once every {ROULETTE_COOLDOWN} seconds.")

        # ===========================
        #  STEP 1 — CHOOSE BET TYPE
        # ===========================

        embed = discord.Embed(
            title="🎰 Roulette",
            description="Choose your bet type.",
            color=discord.Color.green()
        )
        view = BetTypeView(ctx)
        msg = await ctx.send(embed=embed, view=view)
        await view.wait()
        await msg.edit(view=None)

        bet_category = view.choice
        if bet_category is None:
            return await ctx.send("Timed out.")

        # ===========================
        #  STEP 2 — SPECIFIC BET SELECTION
        # ===========================

        # COLOR
        if bet_category == "color":
            embed.description = "Choose Red or Black."
            view = ColorChoiceView(ctx)
            await msg.edit(embed=embed, view=view)
            await view.wait()
            await msg.edit(view=None)
            bet_type = view.choice

        # ODD/EVEN
        elif bet_category == "parity":
            embed.description = "Choose Odd or Even."
            view = ParityChoiceView(ctx)
            await msg.edit(embed=embed, view=view)
            await view.wait()
            await msg.edit(view=None)
            bet_type = view.choice

        # HIGH/LOW
        elif bet_category == "range":
            embed.description = "Choose High or Low."
            view = RangeChoiceView(ctx)
            await msg.edit(embed=embed, view=view)
            await view.wait()
            await msg.edit(view=None)
            bet_type = view.choice

        # DOZENS
        elif bet_category == "dozen":
            embed.description = "Choose a dozen."
            view = DozenChoiceView(ctx)
            await msg.edit(embed=embed, view=view)
            await view.wait()
            await msg.edit(view=None)
            bet_type = view.choice

        # COLUMNS
        elif bet_category == "column":
            embed.description = "Choose a column."
            view = ColumnChoiceView(ctx)
            await msg.edit(embed=embed, view=view)
            await view.wait()
            await msg.edit(view=None)
            bet_type = view.choice

        # INSIDE BETS
        elif bet_category == "inside":
            embed.description = "Choose inside bet type."
            view = InsideBetView(ctx)
            await msg.edit(embed=embed, view=view)
            await view.wait()
            await msg.edit(view=None)
            inside_type = view.choice

            # Determine number count
            count_map = {
                "straight": 1,
                "split": 2,
                "street": 3,
                "corner": 4,
                "line": 6
            }
            count = count_map[inside_type]

            embed.description = f"Select {count} number(s)."
            view = NumberSelectView(ctx, count)
            await msg.edit(embed=embed, view=view)
            await view.wait()
            await msg.edit(view=None)

            bet_type = inside_type
            numbers = view.choice

        else:
            return await ctx.send("Invalid bet type.")

        # ===========================
        #  STEP 3 — BET AMOUNT
        # ===========================

        embed.description = "Choose your chip amount."
        view = ChipView(ctx)
        await msg.edit(embed=embed, view=view)
        await view.wait()
        await msg.edit(view=None)

        amount = view.amount
        if amount is None:
            return await ctx.send("Timed out.")

        if amount > user_data["balance"]:
            return await ctx.send("You don't have enough coins.")

        # ===========================
        #  STEP 4 — SPIN THE WHEEL
        # ===========================

        embed.description = "Spinning the wheel..."
        await msg.edit(embed=embed)

        await asyncio.sleep(1)

        result = random.choice(EUROPEAN_WHEEL)

        # Determine color
        if result == 0:
            color = "🟢 Green"
        elif result in RED_NUMBERS:
            color = "🔴 Red"
        else:
            color = "⚫ Black"

        # ===========================
        #  STEP 5 — PAYOUT LOGIC
        # ===========================

        win = False
        payout = 0

        # Even-money bets
        if bet_type == "red" and result in RED_NUMBERS:
            win = True
            payout = amount * 2
        elif bet_type == "black" and result in BLACK_NUMBERS:
            win = True
            payout = amount * 2
        elif bet_type == "odd" and result != 0 and result % 2 == 1:
            win = True
            payout = amount * 2
        elif bet_type == "even" and result != 0 and result % 2 == 0:
            win = True
            payout = amount * 2
        elif bet_type == "low" and 1 <= result <= 18:
            win = True
            payout = amount * 2
        elif bet_type == "high" and 19 <= result <= 36:
            win = True
            payout = amount * 2

        # Dozens
        elif bet_type == "dozen1" and 1 <= result <= 12:
            win = True
            payout = amount * 3
        elif bet_type == "dozen2" and 13 <= result <= 24:
            win = True
            payout = amount * 3
        elif bet_type == "dozen3" and 25 <= result <= 36:
            win = True
            payout = amount * 3

        # Columns
        elif bet_type == "column1" and result % 3 == 1:
            win = True
            payout = amount * 3
        elif bet_type == "column2" and result % 3 == 2:
            win = True
            payout = amount * 3
        elif bet_type == "column3" and result % 3 == 0:
            win = True
            payout = amount * 3

        # Inside bets
        elif bet_type == "straight" and result == numbers[0]:
            win = True
            payout = amount * 35
        elif bet_type == "split" and result in numbers:
            win = True
            payout = amount * 17
        elif bet_type == "street" and result in numbers:
            win = True
            payout = amount * 11
        elif bet_type == "corner" and result in numbers:
            win = True
            payout = amount * 8
        elif bet_type == "line" and result in numbers:
            win = True
            payout = amount * 5

        # ===========================
        #  STEP 6 — UPDATE ECONOMY
        # ===========================

        if win:
            user_data["balance"] += payout
        else:
            user_data["balance"] -= amount

        user_data["last_roulette"] = time.time()
        economy.save_economy_data()

        # ===========================
        #  STEP 7 — RESULT EMBED
        # ===========================

        title = "🎉 You Win!" if win else "💀 You Lose"
        result_text = f"**Result:** {result} ({color})"

        if win:
            desc = f"{result_text}\nYou won **{payout}** coins."
        else:
            desc = f"{result_text}\nYou lost **{amount}** coins."

        embed = discord.Embed(
            title=title,
            description=desc,
            color=discord.Color.green() if win else discord.Color.red()
        )

        view = SpinAgainView(ctx)
        await msg.edit(embed=embed, view=view)

        await view.wait()

        if view.choice == "spin":
            return await self.roulette(ctx)


# ============================
#  SETUP
# ============================

async def setup(bot):
    await bot.add_cog(Roulette(bot))