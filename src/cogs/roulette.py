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

ROULETTE_COOLDOWN = 60

EUROPEAN_WHEEL = [
    0,
    32, 15, 19, 4, 21, 2, 25, 17, 34, 6,
    27, 13, 36, 11, 30, 8, 23, 10, 5, 24,
    16, 33, 1, 20, 14, 31, 9, 22, 18, 29,
    7, 28, 12, 35, 3, 26
]

RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

ACCENT_GREEN = discord.Colour(0x57F287)
ACCENT_RED = discord.Colour(0xED4245)
ACCENT_GOLD = discord.Colour(0xFEE75C)

# ============================
#  BASE LAYOUT VIEW
# ============================

class RouletteLayoutView(discord.ui.LayoutView):
    """Base LayoutView that restricts interactions to the command author."""
    def __init__(self, ctx, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id


# ============================
#  GENERIC BUTTON CLASS
# ============================

class ChoiceButton(discord.ui.Button):
    """A button that sets view.choice and stops the view."""
    def __init__(self, label: str, style: discord.ButtonStyle, value: str):
        super().__init__(label=label, style=style)
        self.value = value

    async def callback(self, interaction: discord.Interaction):
        self.view.choice = self.value
        self.view.stop()
        await interaction.response.defer()


# ============================
#  BET TYPE VIEW
# ============================

def build_bet_type_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Choose your bet type."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton("Red / Black", discord.ButtonStyle.red, "color"),
            ChoiceButton("Odd / Even", discord.ButtonStyle.blurple, "parity"),
            ChoiceButton("High / Low", discord.ButtonStyle.green, "range"),
        ),
        discord.ui.ActionRow(
            ChoiceButton("Dozens", discord.ButtonStyle.gray, "dozen"),
            ChoiceButton("Columns", discord.ButtonStyle.gray, "column"),
            ChoiceButton("Inside Bets", discord.ButtonStyle.green, "inside"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


# ============================
#  COLOR / PARITY / RANGE VIEWS
# ============================

def build_color_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Choose Red or Black."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton("Red", discord.ButtonStyle.red, "red"),
            ChoiceButton("Black", discord.ButtonStyle.gray, "black"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_parity_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Choose Odd or Even."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton("Odd", discord.ButtonStyle.blurple, "odd"),
            ChoiceButton("Even", discord.ButtonStyle.blurple, "even"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_range_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Choose High (19–36) or Low (1–18)."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton("Low (1–18)", discord.ButtonStyle.green, "low"),
            ChoiceButton("High (19–36)", discord.ButtonStyle.green, "high"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_dozen_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Choose a dozen."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton("1st Dozen (1–12)", discord.ButtonStyle.gray, "dozen1"),
            ChoiceButton("2nd Dozen (13–24)", discord.ButtonStyle.gray, "dozen2"),
            ChoiceButton("3rd Dozen (25–36)", discord.ButtonStyle.gray, "dozen3"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_column_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Choose a column."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton("Column 1", discord.ButtonStyle.gray, "column1"),
            ChoiceButton("Column 2", discord.ButtonStyle.gray, "column2"),
            ChoiceButton("Column 3", discord.ButtonStyle.gray, "column3"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


# ============================
#  INSIDE BET SELECT
# ============================

class InsideBetSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Straight (Single Number)", value="straight"),
            discord.SelectOption(label="Split (2 Numbers)", value="split"),
            discord.SelectOption(label="Street (3 Numbers)", value="street"),
            discord.SelectOption(label="Corner (4 Numbers)", value="corner"),
            discord.SelectOption(label="Line (6 Numbers)", value="line"),
        ]
        super().__init__(placeholder="Choose inside bet type", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.choice = self.values[0]
        self.view.stop()
        await interaction.response.defer()


def build_inside_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Choose an inside bet type."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(InsideBetSelect()),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


# ============================
#  NUMBER SELECTION
# ============================

class NumberDropdownLow(discord.ui.Select):
    def __init__(self, count):
        options = [discord.SelectOption(label=str(i), value=str(i)) for i in range(0, 19)]
        super().__init__(
            placeholder=f"Numbers 0–18 (pick up to {count})",
            min_values=0,
            max_values=count,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_low = [int(v) for v in self.values]
        total = self.view.selected_low + self.view.selected_high
        if len(total) == self.view.count:
            self.view.choice = total
            self.view.stop()
        await interaction.response.defer()


class NumberDropdownHigh(discord.ui.Select):
    def __init__(self, count):
        options = [discord.SelectOption(label=str(i), value=str(i)) for i in range(19, 37)]
        super().__init__(
            placeholder=f"Numbers 19–36 (pick up to {count})",
            min_values=0,
            max_values=count,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_high = [int(v) for v in self.values]
        total = self.view.selected_low + self.view.selected_high
        if len(total) == self.view.count:
            self.view.choice = total
            self.view.stop()
        await interaction.response.defer()


def build_number_view(ctx, count: int) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    view.count = count
    view.selected_low = []
    view.selected_high = []
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=f"Select **{count}** number(s). Use both dropdowns if needed."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(NumberDropdownLow(count)),
        discord.ui.ActionRow(NumberDropdownHigh(count)),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


# ============================
#  CHIP AMOUNT VIEW
# ============================

def build_chip_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    view.amount = None

    class ChipBtn(discord.ui.Button):
        def __init__(self_, label, value):
            super().__init__(label=label, style=discord.ButtonStyle.green)
            self_.value = value
        async def callback(self_, interaction):
            view.amount = self_.value
            view.stop()
            await interaction.response.defer()

    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Choose your chip amount."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChipBtn("10", 10),
            ChipBtn("50", 50),
            ChipBtn("100", 100),
            ChipBtn("500", 500),
        ),
        accent_colour=ACCENT_GOLD
    )
    view.add_item(container)
    return view


# ============================
#  SPINNING VIEW (no buttons)
# ============================

def build_spinning_view() -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Roulette"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Spinning the wheel..."),
        accent_colour=ACCENT_GOLD
    )
    view.add_item(container)
    return view


# ============================
#  RESULT VIEW
# ============================

def build_result_view(ctx, win: bool, result: int, color_str: str, bet_type: str, amount: int, payout: int) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)

    title = "🎉 You Win!" if win else "💀 You Lose"
    result_line = f"**Result:** {result} ({color_str})"
    outcome_line = f"You won **{payout}** coins." if win else f"You lost **{amount}** coins."
    bet_label = bet_type.replace("dozen", "Dozen ").replace("column", "Column ").title()

    class SpinAgainBtn(discord.ui.Button):
        def __init__(self_):
            super().__init__(label="Spin Again", style=discord.ButtonStyle.green)
        async def callback(self_, interaction):
            view.choice = "spin"
            view.stop()
            await interaction.response.defer()

    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=f"{result_line}\n{outcome_line}\n**Bet:** {bet_label}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(SpinAgainBtn()),
        accent_colour=ACCENT_GREEN if win else ACCENT_RED
    )
    view.add_item(container)
    return view


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

        if user_data["last_roulette"] + ROULETTE_COOLDOWN > time.time():
            return await ctx.send(f"You can only play roulette once every {ROULETTE_COOLDOWN} seconds.")

        # STEP 1 — CHOOSE BET TYPE
        view = build_bet_type_view(ctx)
        msg = await ctx.send(view=view)
        await view.wait()

        bet_category = view.choice
        if bet_category is None:
            return await ctx.send("Timed out.")

        # STEP 2 — SPECIFIC BET
        numbers = None

        if bet_category == "color":
            view = build_color_view(ctx)
            await msg.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "parity":
            view = build_parity_view(ctx)
            await msg.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "range":
            view = build_range_view(ctx)
            await msg.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "dozen":
            view = build_dozen_view(ctx)
            await msg.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "column":
            view = build_column_view(ctx)
            await msg.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "inside":
            view = build_inside_view(ctx)
            await msg.edit(view=view)
            await view.wait()
            inside_type = view.choice

            count_map = {"straight": 1, "split": 2, "street": 3, "corner": 4, "line": 6}
            count = count_map[inside_type]

            view = build_number_view(ctx, count)
            await msg.edit(view=view)
            await view.wait()

            bet_type = inside_type
            numbers = view.choice

        else:
            return await ctx.send("Invalid bet type.")

        # STEP 3 — CHIP AMOUNT
        view = build_chip_view(ctx)
        await msg.edit(view=view)
        await view.wait()

        amount = view.amount
        if amount is None:
            return await ctx.send("Timed out.")

        if amount > user_data["balance"]:
            return await ctx.send("You don't have enough coins.")

        # STEP 4 — SPIN
        await msg.edit(view=build_spinning_view())
        await asyncio.sleep(1)

        result = random.choice(EUROPEAN_WHEEL)

        if result == 0:
            color_str = "🟢 Green"
        elif result in RED_NUMBERS:
            color_str = "🔴 Red"
        else:
            color_str = "⚫ Black"

        # STEP 5 — PAYOUT LOGIC
        win = False
        payout = 0

        if bet_type == "red" and result in RED_NUMBERS:
            win, payout = True, amount * 2
        elif bet_type == "black" and result in BLACK_NUMBERS:
            win, payout = True, amount * 2
        elif bet_type == "odd" and result != 0 and result % 2 == 1:
            win, payout = True, amount * 2
        elif bet_type == "even" and result != 0 and result % 2 == 0:
            win, payout = True, amount * 2
        elif bet_type == "low" and 1 <= result <= 18:
            win, payout = True, amount * 2
        elif bet_type == "high" and 19 <= result <= 36:
            win, payout = True, amount * 2
        elif bet_type == "dozen1" and 1 <= result <= 12:
            win, payout = True, amount * 3
        elif bet_type == "dozen2" and 13 <= result <= 24:
            win, payout = True, amount * 3
        elif bet_type == "dozen3" and 25 <= result <= 36:
            win, payout = True, amount * 3
        elif bet_type == "column1" and result % 3 == 1:
            win, payout = True, amount * 3
        elif bet_type == "column2" and result % 3 == 2:
            win, payout = True, amount * 3
        elif bet_type == "column3" and result % 3 == 0:
            win, payout = True, amount * 3
        elif bet_type == "straight" and numbers and result == numbers[0]:
            win, payout = True, amount * 35
        elif bet_type == "split" and numbers and result in numbers:
            win, payout = True, amount * 17
        elif bet_type == "street" and numbers and result in numbers:
            win, payout = True, amount * 11
        elif bet_type == "corner" and numbers and result in numbers:
            win, payout = True, amount * 8
        elif bet_type == "line" and numbers and result in numbers:
            win, payout = True, amount * 5

        # STEP 6 — UPDATE ECONOMY
        if win:
            user_data["balance"] += payout
        else:
            user_data["balance"] -= amount

        user_data["last_roulette"] = time.time()
        economy.save_economy_data()

        # STEP 7 — RESULT
        view = build_result_view(ctx, win, result, color_str, bet_type, amount, payout)
        await msg.edit(view=view)
        await view.wait()

        if view.choice == "spin":
            return await self.roulette(ctx)


# ============================
#  SETUP
# ============================

async def setup(bot):
    await bot.add_cog(Roulette(bot))
