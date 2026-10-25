# ============================
#  IMPORTS
# ============================

import discord
from discord.ext import commands
import random
import time
import asyncio

from cogs.casino.replay import InteractionContext
from utils.cooldown import cooldown_ready_at, cooldown_view

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

# Bet type -> (winning-number test, total return multiplier). A European wheel
# pays even money as 2x the stake back, a dozen or column as 3x, and the inside
# bets as the usual 35/17/11/8/5x. The green zero loses every outside bet.
OUTSIDE_PAYOUTS = {
    "red": (lambda n: n in RED_NUMBERS, 2),
    "black": (lambda n: n in BLACK_NUMBERS, 2),
    "odd": (lambda n: n != 0 and n % 2 == 1, 2),
    "even": (lambda n: n != 0 and n % 2 == 0, 2),
    "low": (lambda n: 1 <= n <= 18, 2),
    "high": (lambda n: 19 <= n <= 36, 2),
    "dozen1": (lambda n: 1 <= n <= 12, 3),
    "dozen2": (lambda n: 13 <= n <= 24, 3),
    "dozen3": (lambda n: 25 <= n <= 36, 3),
    "column1": (lambda n: n % 3 == 1, 3),
    "column2": (lambda n: n % 3 == 2, 3),
    "column3": (lambda n: n != 0 and n % 3 == 0, 3),
}
INSIDE_PAYOUTS = {"straight": 35, "split": 17, "street": 11, "corner": 8, "line": 5}


def resolve_bet(bet_type: str, numbers, result: int, amount: int) -> tuple[bool, int]:
    """Return ``(win, returned)`` for one spin.

    ``returned`` is everything the table pays back on a win - the stake plus the
    profit - so the account is settled with ``returned - amount`` on a win and
    ``-amount`` on a loss. Keeping the whole table in one pure function means
    every bet type is testable without driving the interactive views.
    """
    outside = OUTSIDE_PAYOUTS.get(bet_type)
    if outside is not None:
        wins, multiplier = outside
        return (True, amount * multiplier) if wins(result) else (False, 0)

    multiplier = INSIDE_PAYOUTS.get(bet_type)
    if multiplier is not None and numbers and result in numbers:
        return True, amount * multiplier

    return False, 0

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

def _roulette_cooldown_view(last_spin) -> discord.ui.LayoutView:
    """The shared cooldown notice, used by the command and by Spin Again."""
    return cooldown_view(
        "spin the wheel",
        cooldown_ready_at(last_spin, ROULETTE_COOLDOWN),
        title="🎡 Slow down",
        note=f"Roulette allows one spin every **{ROULETTE_COOLDOWN}** seconds.",
    )


_SPIN_AGAIN_TEMPLATE = r"casino:roulette:again:(?P<user_id>\d+)"


class SpinAgainButton(discord.ui.DynamicItem[discord.ui.Button], template=_SPIN_AGAIN_TEMPLATE):
    """Persistent "Spin Again" button on a roulette result.

    The player's id lives in the custom id, so a click on an old result starts
    the same flow for the same person after a restart.
    """

    def __init__(self, user_id: int):
        super().__init__(discord.ui.Button(
            label="Spin Again",
            style=discord.ButtonStyle.green,
            custom_id=f"casino:roulette:again:{int(user_id)}",
        ))
        self.user_id = int(user_id)

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(int(match["user_id"]))

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                "This wheel belongs to someone else. Start your own with `/roulette`.",
                ephemeral=True,
            )
        cog = interaction.client.get_cog("Roulette")
        if cog is None:
            return await interaction.response.send_message(
                "Roulette is unavailable right now.", ephemeral=True
            )
        economy = interaction.client.get_cog("EconomyCog")
        if economy is not None:
            data = await economy.get_user_economy_data(self.user_id)
            last_spin = float(data["last_roulette"]) if data.get("last_roulette") else 0.0
            if last_spin + ROULETTE_COOLDOWN > time.time():
                # Answer the cooldown privately so a spammed button cannot
                # flood the channel with notices.
                return await interaction.response.send_message(
                    view=_roulette_cooldown_view(last_spin), ephemeral=True
                )
        await interaction.response.defer()
        await cog.play(InteractionContext(interaction))


def build_result_view(ctx, win: bool, result: int, color_str: str, bet_type: str, amount: int, winnings: int) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx, timeout=None)

    title = "🎉 You Win!" if win else "💀 You Lose"
    result_line = f"**Result:** {result} ({color_str})"
    # `winnings` is the net profit, so the card matches what the wallet gained.
    outcome_line = f"You won **{winnings}** coins." if win else f"You lost **{amount}** coins."
    bet_label = bet_type.replace("dozen", "Dozen ").replace("column", "Column ").title()

    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=f"{result_line}\n{outcome_line}\n**Bet:** {bet_label}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(SpinAgainButton(ctx.author.id)),
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

    async def cog_load(self):
        # One registration covers every roulette result ever posted: the button
        # rebuilds itself from its custom id.
        registry = discord.ui.LayoutView(timeout=None)
        registry.add_item(discord.ui.Container(discord.ui.ActionRow(SpinAgainButton(0))))
        self.bot.add_view(registry)

    @commands.hybrid_command(name="roulette", description="Play interactive European roulette", help="{ 'en': 'play interactive European roulette 🎡', 'de': 'spiele interaktives europäisches Roulette 🎡', 'es': 'juega ruleta europea interactiva 🎡' }")
    async def roulette(self, ctx):
        """Play interactive European roulette."""
        await self.play(ctx)

    async def play(self, ctx):
        """Run one round; shared by the command and the Spin Again button."""
        economy = self.bot.get_cog("EconomyCog")
        user_data = await economy.get_user_economy_data(ctx.author.id)

        if user_data["last_roulette"] + ROULETTE_COOLDOWN > time.time():
            return await ctx.send(view=_roulette_cooldown_view(user_data["last_roulette"]))

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
        win, returned = resolve_bet(bet_type, numbers, result, amount)

        # STEP 6 — UPDATE ECONOMY
        # The stake is part of the result: a win pays the stake back with the
        # profit, a loss costs the stake. `returned` is the total, so the account
        # moves by the net only — crediting the total without ever debiting the
        # stake paid every winner one extra stake. record_gamble writes the net
        # to the ledger, so roulette also shows up in the dashboard's recent
        # activity card and counts towards the gambling badges.
        net = returned - amount if win else -amount
        if net:
            economy.record_gamble(
                user_data, net,
                "roulette_win" if net > 0 else "roulette_loss",
                f"{bet_type} · {result} ({color_str})",
            )

        user_data["last_roulette"] = time.time()
        await economy.save_user_economy_data(ctx.author.id)

        # STEP 7 — RESULT
        view = build_result_view(ctx, win, result, color_str, bet_type, amount, net)
        await msg.edit(view=view)


# ============================
#  SETUP
# ============================

async def setup(bot):
    await bot.add_cog(Roulette(bot))
