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

from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "messages")
msg = make_flat_msg(MESSAGES)

# ============================
#  CONSTANTS
# ============================

ROULETTE_COOLDOWN = 30

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
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_choose_bet")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton(msg(ctx, "roulette_btn_red_black"), discord.ButtonStyle.red, "color"),
            ChoiceButton(msg(ctx, "roulette_btn_odd_even"), discord.ButtonStyle.blurple, "parity"),
            ChoiceButton(msg(ctx, "roulette_btn_high_low"), discord.ButtonStyle.green, "range"),
        ),
        discord.ui.ActionRow(
            ChoiceButton(msg(ctx, "roulette_btn_dozens"), discord.ButtonStyle.gray, "dozen"),
            ChoiceButton(msg(ctx, "roulette_btn_columns"), discord.ButtonStyle.gray, "column"),
            ChoiceButton(msg(ctx, "roulette_btn_inside"), discord.ButtonStyle.green, "inside"),
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
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_choose_color")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton(msg(ctx, "roulette_red"), discord.ButtonStyle.red, "red"),
            ChoiceButton(msg(ctx, "roulette_black"), discord.ButtonStyle.gray, "black"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_parity_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_choose_parity")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton(msg(ctx, "roulette_odd"), discord.ButtonStyle.blurple, "odd"),
            ChoiceButton(msg(ctx, "roulette_even"), discord.ButtonStyle.blurple, "even"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_range_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_choose_range")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton(msg(ctx, "roulette_low"), discord.ButtonStyle.green, "low"),
            ChoiceButton(msg(ctx, "roulette_high"), discord.ButtonStyle.green, "high"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_dozen_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_choose_dozen")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton(msg(ctx, "roulette_dozen1"), discord.ButtonStyle.gray, "dozen1"),
            ChoiceButton(msg(ctx, "roulette_dozen2"), discord.ButtonStyle.gray, "dozen2"),
            ChoiceButton(msg(ctx, "roulette_dozen3"), discord.ButtonStyle.gray, "dozen3"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_column_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_choose_column")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            ChoiceButton(msg(ctx, "roulette_column1"), discord.ButtonStyle.gray, "column1"),
            ChoiceButton(msg(ctx, "roulette_column2"), discord.ButtonStyle.gray, "column2"),
            ChoiceButton(msg(ctx, "roulette_column3"), discord.ButtonStyle.gray, "column3"),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


# ============================
#  INSIDE BET SELECT
# ============================

class InsideBetSelect(discord.ui.Select):
    def __init__(self, ctx):
        options = [
            discord.SelectOption(label=msg(ctx, "roulette_straight"), value="straight"),
            discord.SelectOption(label=msg(ctx, "roulette_split"), value="split"),
            discord.SelectOption(label=msg(ctx, "roulette_street"), value="street"),
            discord.SelectOption(label=msg(ctx, "roulette_corner"), value="corner"),
            discord.SelectOption(label=msg(ctx, "roulette_line"), value="line"),
        ]
        super().__init__(placeholder=msg(ctx, "roulette_inside_placeholder"), options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.choice = self.values[0]
        self.view.stop()
        await interaction.response.defer()


def build_inside_view(ctx) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx)
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_choose_inside")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(InsideBetSelect(ctx)),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


# ============================
#  NUMBER SELECTION
# ============================

class NumberDropdownLow(discord.ui.Select):
    def __init__(self, ctx, count):
        options = [discord.SelectOption(label=str(i), value=str(i)) for i in range(0, 19)]
        super().__init__(
            placeholder=msg(ctx, "roulette_low_placeholder", count=count),
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
    def __init__(self, ctx, count):
        options = [discord.SelectOption(label=str(i), value=str(i)) for i in range(19, 37)]
        super().__init__(
            placeholder=msg(ctx, "roulette_high_placeholder", count=count),
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
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_select_numbers", count=count)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(NumberDropdownLow(ctx, count)),
        discord.ui.ActionRow(NumberDropdownHigh(ctx, count)),
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
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_choose_chip")),
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

def build_spinning_view(ctx) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, "roulette_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "roulette_spinning")),
        accent_colour=ACCENT_GOLD
    )
    view.add_item(container)
    return view


# ============================
#  RESULT VIEW
# ============================

def _roulette_cooldown_view(ctx, last_spin) -> discord.ui.LayoutView:
    """The shared cooldown notice, used by the command and by Spin Again."""
    return cooldown_view(
        msg(ctx, "roulette_cooldown_action"),
        cooldown_ready_at(last_spin, ROULETTE_COOLDOWN),
        title=msg(ctx, "roulette_cooldown_title"),
        note=msg(ctx, "roulette_cooldown_note", seconds=ROULETTE_COOLDOWN),
        template=msg(ctx, "roulette_cooldown_sentence"),
    )


_SPIN_AGAIN_TEMPLATE = r"casino:roulette:again:(?P<user_id>\d+)"


class SpinAgainButton(discord.ui.DynamicItem[discord.ui.Button], template=_SPIN_AGAIN_TEMPLATE):
    """Persistent "Spin Again" button on a roulette result.

    The player's id lives in the custom id, so a click on an old result starts
    the same flow for the same person after a restart.
    """

    def __init__(self, user_id: int, label: str = "Spin Again"):
        super().__init__(discord.ui.Button(
            label=label,
            style=discord.ButtonStyle.green,
            custom_id=f"casino:roulette:again:{int(user_id)}",
        ))
        self.user_id = int(user_id)

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(
            int(match["user_id"]),
            label=msg(interaction, "roulette_spin_again"),
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                msg(interaction, "roulette_wrong_player"),
                ephemeral=True,
            )
        cog = interaction.client.get_cog("Roulette")
        if cog is None:
            return await interaction.response.send_message(
                msg(interaction, "roulette_unavailable"), ephemeral=True
            )
        economy = interaction.client.get_cog("EconomyCog")
        if economy is not None:
            data = await economy.get_user_economy_data(self.user_id)
            last_spin = float(data["last_roulette"]) if data.get("last_roulette") else 0.0
            if last_spin + ROULETTE_COOLDOWN > time.time():
                # Answer the cooldown privately so a spammed button cannot
                # flood the channel with notices.
                return await interaction.response.send_message(
                    view=_roulette_cooldown_view(interaction, last_spin), ephemeral=True
                )
        await interaction.response.defer()
        await cog.play(InteractionContext(interaction))


def build_result_view(ctx, win: bool, result: int, color_str: str, bet_type: str, amount: int, winnings: int) -> RouletteLayoutView:
    view = RouletteLayoutView(ctx, timeout=None)

    title = msg(ctx, "roulette_win_title") if win else msg(ctx, "roulette_lose_title")
    result_line = msg(ctx, "roulette_result", number=result, color=color_str)
    # `winnings` is the net profit, so the card matches what the wallet gained.
    outcome_line = (
        msg(ctx, "roulette_outcome_win", amount=winnings)
        if win
        else msg(ctx, "roulette_outcome_lose", amount=amount)
    )
    bet_label = msg(ctx, f"roulette_bet_{bet_type}")

    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"{result_line}\n{outcome_line}\n"
                + msg(ctx, "roulette_bet_line", bet=bet_label)
            )
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(SpinAgainButton(ctx.author.id, label=msg(ctx, "roulette_spin_again"))),
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

    @commands.hybrid_command(name="roulette", description=CMDS.text("roulette.description"), help=CMDS.help("roulette"),
    )
    async def roulette(self, ctx):
        """Play interactive European roulette."""
        await self.play(ctx)

    async def play(self, ctx):
        """Run one round; shared by the command and the Spin Again button."""
        economy = self.bot.get_cog("EconomyCog")
        user_data = await economy.get_user_economy_data(ctx.author.id)

        if user_data["last_roulette"] + ROULETTE_COOLDOWN > time.time():
            return await ctx.send(view=_roulette_cooldown_view(ctx, user_data["last_roulette"]))

        # STEP 1 — CHOOSE BET TYPE
        view = build_bet_type_view(ctx)
        message = await ctx.send(view=view)
        await view.wait()

        bet_category = view.choice
        if bet_category is None:
            return await ctx.send(msg(ctx, "roulette_timed_out"))

        # STEP 2 — SPECIFIC BET
        numbers = None

        if bet_category == "color":
            view = build_color_view(ctx)
            await message.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "parity":
            view = build_parity_view(ctx)
            await message.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "range":
            view = build_range_view(ctx)
            await message.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "dozen":
            view = build_dozen_view(ctx)
            await message.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "column":
            view = build_column_view(ctx)
            await message.edit(view=view)
            await view.wait()
            bet_type = view.choice

        elif bet_category == "inside":
            view = build_inside_view(ctx)
            await message.edit(view=view)
            await view.wait()
            inside_type = view.choice
            if inside_type is None:
                return await ctx.send(msg(ctx, "roulette_timed_out"))

            count_map = {"straight": 1, "split": 2, "street": 3, "corner": 4, "line": 6}
            count = count_map[inside_type]

            view = build_number_view(ctx, count)
            await message.edit(view=view)
            await view.wait()

            bet_type = inside_type
            numbers = view.choice
            # An abandoned number pick would otherwise resolve as a loss and
            # quietly take the stake without ever spinning.
            if numbers is None:
                return await ctx.send(msg(ctx, "roulette_timed_out"))

        else:
            return await ctx.send(msg(ctx, "roulette_invalid_bet"))

        # Every sub-step is a 30 second menu. If the player let one expire,
        # `bet_type` is None; ending here keeps the rest of the round from
        # running with no bet and crashing the result card.
        if bet_type is None:
            return await ctx.send(msg(ctx, "roulette_timed_out"))

        # STEP 3 — CHIP AMOUNT
        view = build_chip_view(ctx)
        await message.edit(view=view)
        await view.wait()

        amount = view.amount
        if amount is None:
            return await ctx.send(msg(ctx, "roulette_timed_out"))

        if amount > user_data["balance"]:
            return await ctx.send(msg(ctx, "roulette_not_enough"))

        # STEP 4 — SPIN
        await message.edit(view=build_spinning_view(ctx))
        await asyncio.sleep(1)

        result = random.choice(EUROPEAN_WHEEL)

        if result == 0:
            color_str = msg(ctx, "roulette_color_green")
        elif result in RED_NUMBERS:
            color_str = msg(ctx, "roulette_color_red")
        else:
            color_str = msg(ctx, "roulette_color_black")

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
                f"{msg(ctx, f'roulette_bet_{bet_type}')} · {result} ({color_str})",
            )

        user_data["last_roulette"] = time.time()
        await economy.save_user_economy_data(ctx.author.id)

        # STEP 7 — RESULT
        view = build_result_view(ctx, win, result, color_str, bet_type, amount, net)
        await message.edit(view=view)


# ============================
#  SETUP
# ============================

async def setup(bot):
    await bot.add_cog(Roulette(bot))
