import discord
from discord.ext import commands
import random
import time
import asyncio
import os

# Seconds between spins. Kept numeric so the cooldown is compared as a time,
# not as concatenated strings.
slots_cooldown = float(os.getenv("SLOTS_COOLDOWN") or 60)

# Symbol tiers and the weighted pool the machine draws from. The rarer a symbol,
# the more a line of it pays: common 2x, uncommon 3x, rare 5x, jackpot 25x, and
# a board of one symbol pays the 100x full-board jackpot on top of its lines.
COMMON = ["🍒", "🍋", "🍊"]
UNCOMMON = ["🍎", "🍇", "🍐"]
RARE = ["💎", "🔥"]
JACKPOT = ["🪙"]

SYMBOLS = COMMON * 6 + UNCOMMON * 4 + RARE * 2 + JACKPOT * 1

LINE_PAYOUTS = {
    **{symbol: (2, "Common Line (2×)") for symbol in COMMON},
    **{symbol: (3, "Uncommon Line (3×)") for symbol in UNCOMMON},
    **{symbol: (5, "Rare Line (5×)") for symbol in RARE},
    **{symbol: (25, "JACKPOT LINE (25×)") for symbol in JACKPOT},
}

FULL_BOARD_MULTIPLIER = 100


def spin_grid() -> list[list[str]]:
    """Draw a fresh 3x3 grid from the weighted symbol pool."""
    return [[random.choice(SYMBOLS) for _ in range(3)] for _ in range(3)]


def grid_to_text(grid) -> str:
    return "\n".join(" ".join(row) for row in grid)


def evaluate_grid(grid, amount: int) -> tuple[int, list[tuple[str, str]]]:
    """Return ``(returned, hits)`` for a finished grid.

    ``returned`` is everything the machine pays back - the stake plus the profit
    - so the account moves by ``returned - amount``. Keeping the paytable here
    rather than inside the command lets every line and the full-board jackpot be
    tested without spinning.
    """
    lines = [
        grid[1],                               # middle row
        grid[0],                               # top row
        grid[2],                               # bottom row
        [grid[0][0], grid[1][1], grid[2][2]],  # diagonal \
        [grid[0][2], grid[1][1], grid[2][0]],  # diagonal /
    ]

    total = 0
    hits: list[tuple[str, str]] = []

    for line in lines:
        if line[0] == line[1] == line[2]:
            symbol = line[0]
            payout = LINE_PAYOUTS.get(symbol)
            if payout is not None:
                multiplier, label = payout
                total += amount * multiplier
                hits.append((symbol, label))

    # Full board jackpot
    flat = [cell for row in grid for cell in row]
    if len(set(flat)) == 1:
        total += amount * FULL_BOARD_MULTIPLIER
        hits.append((flat[0], "FULL BOARD JACKPOT (100×)"))

    return total, hits


# Prefix resolver (required for dynamic prefixes to work)
async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """
    Resolve the primary prefix for the current context/interaction.

    Supports:
    - Static string prefix
    - Static list/tuple of prefixes
    - Dynamic prefix function: command_prefix(bot, message) -> list[str]
    """
    raw = bot.command_prefix

    # Static prefix (string)
    if isinstance(raw, str):
        return raw

    # Static list/tuple of prefixes
    if isinstance(raw, (list, tuple)):
        return raw[0]

    # Dynamic prefix function
    try:
        # Context: has .message
        msg = getattr(ctx_or_interaction, "message", None)

        # Interaction: use the original message if present
        if msg is None and isinstance(ctx_or_interaction, discord.Interaction):
            msg = ctx_or_interaction.message

        if msg is None:
            return "!"

        prefixes = raw(bot, msg)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass

    # Fallback prefix if everything else fails
    return "."


class Slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="slots",
        description="Play a casino-style 3x3 slot machine",
        help="{ 'en': 'play a casino-style 3×3 slot machine 🎰', 'de': 'spiele ein Casino-Slot-Spiel', 'es': 'juega una tragamoneda de estilo 3×3 estilo casino 🎰' }"
    )
    async def slots(self, ctx):
        if ctx.invoked_subcommand is None:
            prefix = await _resolve_prefix(self.bot, ctx)
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### 🎰 Slots Help"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"**{prefix}slots play <amount>** - Play a game of slots.\n**{prefix}slots payouts** - View the slots payout table."
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    @slots.command(name="play", description="Play a game of slots")
    async def slots_play(self, ctx, amount: int = None):
        """Play a casino‑style 3×3 slot machine."""
        # Economy access
        economy = self.bot.get_cog("EconomyCog")
        user_data = await economy.get_user_economy_data(ctx.author.id)
        balance = user_data["balance"]

        # Cooldown
        if float(user_data.get("last_slots") or 0) + slots_cooldown > time.time():
            return await ctx.send(f"You can only play slots once every {int(slots_cooldown)} seconds.")

        if amount is None or amount <= 0:
            return await ctx.send("You must bet more than 0 coins.")

        if amount > balance:
            return await ctx.send("You don't have enough coins to play slots.")

        # SPIN ANIMATION
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### 🎰 Slots"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"Spinning..."
            )
        )
        view.add_item(container)
        msg = await ctx.send(view=view)

        # Fake spinning animation
        for _ in range(3):
            grid = spin_grid()
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### 🎰 Slots"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"{grid_to_text(grid)}"
                )
            )
            view.add_item(container)
            await msg.edit(view=view)
            await asyncio.sleep(0.5)

        # Final result
        final_grid = spin_grid()
        returned, hits = evaluate_grid(final_grid, amount)

        # `returned` is the stake plus the profit, and the stake is part of the
        # result, so the wallet moves by the net only. record_gamble writes that
        # to the ledger, so slots shows up in the dashboard's recent activity
        # card and counts towards earned/spent and gambling achievements.
        net = returned - amount
        if net:
            note = f"bet {amount:,}" + (f" · {hits[0][1]}" if hits else " · no line")
            economy.record_gamble(user_data, net, "slots_win" if net > 0 else "slots_loss", note)

        user_data["last_slots"] = time.time()
        await economy.save_user_economy_data(ctx.author.id)

        # Build result embed
        result_text = grid_to_text(final_grid)

        if net > 0:
            title = "🎉 You Win!"
            details = "\n".join(f"{sym} — {desc}" for sym, desc in hits)
            description = f"{result_text}\n\n**{details}**\nYou won **{net}** coins."
        else:
            title = "😢 You Lose"
            description = f"{result_text}\n\nYou lost **{amount}** coins."

        result_view = discord.ui.LayoutView()
        result_container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {title}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"{description}"
            )
        )
        result_view.add_item(result_container)
        await msg.edit(view=result_view)

    # payouts subcommand (!slots payouts)
    @slots.command(name="payouts", description="View the slots payout table")
    async def slots_payouts(self, ctx):
        """View the slots payout table."""
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### 🎰 Slots Payouts"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"**Common Symbols (🍒🍋🍊)**\n2× bet\n\n**Uncommon Symbols (🍎🍇🍐)**\n3× bet\n\n**Rare Symbols (💎🔥)**\n5× bet\n\n**Jackpot Symbol (🪙 ✨)**\n25× bet\n\n**Full Board Jackpot**\n100× bet"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"**Paylines:**\n- Middle row\n- Top row\n- Bottom row\n- Diagonal (top-left to bottom-right)"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"-# **Notice:** There may be some issues with the slots game. Please report any bugs to the developers."
            )
        )
        view.add_item(container)
        await ctx.send(view=view)
        

async def setup(bot):
    await bot.add_cog(Slots(bot))
