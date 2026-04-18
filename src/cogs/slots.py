import discord
from discord.ext import commands
import random
import time
import asyncio
import os

slots_cooldown = os.getenv("SLOTS_COOLDOWN") or 60

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

    @commands.group(
        name="slots",
        help="{ 'en': 'play a casino-style 3×3 slot machine 🎰', 'de': 'spiele ein Casino-Slot-Spiel' }"
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

    @slots.command(name="play")
    async def slots_play(self, ctx, amount: int = None):
        """Play a casino‑style 3×3 slot machine."""
        # Economy access
        economy = self.bot.get_cog("EconomyCog")
        user_data = economy.get_user_economy_data(ctx.author.id)
        balance = user_data["balance"]

        # Cooldown
        if user_data["last_slots"] + slots_cooldown > time.time():
            return await ctx.send(f"You can only play slots once every {slots_cooldown} seconds.")

        if amount is None or amount <= 0:
            return await ctx.send("You must bet more than 0 coins.")

        if amount > balance:
            return await ctx.send("You don't have enough coins to play slots.")

        # Symbol tiers
        COMMON = ["🍒", "🍋", "🍊"]
        UNCOMMON = ["🍇", "🍉", "🍓"]
        RARE = ["🍀", "💎"]
        JACKPOT = ["⭐"]

        # Weighted symbol pool
        SYMBOLS = (
            COMMON * 6 +
            UNCOMMON * 4 +
            RARE * 2 +
            JACKPOT * 1
        )

        # Helper to generate a 3×3 grid
        def spin_grid():
            return [
                [random.choice(SYMBOLS) for _ in range(3)]
                for _ in range(3)
            ]

        # Helper to format grid
        def grid_to_text(grid):
            return "\n".join(" ".join(row) for row in grid)

        # Helper to evaluate paylines
        def evaluate(grid):
            lines = [
                grid[1],                     # middle row
                grid[0],                     # top row
                grid[2],                     # bottom row
                [grid[0][0], grid[1][1], grid[2][2]],  # diagonal \
                [grid[0][2], grid[1][1], grid[2][0]]   # diagonal /
            ]

            total = 0
            hits = []

            for line in lines:
                if line[0] == line[1] == line[2]:
                    symbol = line[0]

                    if symbol in COMMON:
                        total += amount * 2
                        hits.append((symbol, "Common Line (2×)"))
                    elif symbol in UNCOMMON:
                        total += amount * 3
                        hits.append((symbol, "Uncommon Line (3×)"))
                    elif symbol in RARE:
                        total += amount * 5
                        hits.append((symbol, "Rare Line (5×)"))
                    elif symbol in JACKPOT:
                        total += amount * 25
                        hits.append((symbol, "JACKPOT LINE (25×)"))

            # Full board jackpot
            flat = [c for row in grid for c in row]
            if len(set(flat)) == 1:
                total += amount * 100
                hits.append(("⭐", "FULL BOARD JACKPOT (100×)"))

            return total, hits

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
        winnings, hits = evaluate(final_grid)

        # Update economy
        if winnings > 0:
            user_data["balance"] += winnings
        else:
            user_data["balance"] -= amount

        user_data["last_slots"] = time.time()
        economy = self.bot.get_cog("EconomyCog")
        economy.save_economy_data()

        # Build result embed
        result_text = grid_to_text(final_grid)

        if winnings > 0:
            title = "🎉 You Win!"
            details = "\n".join(f"{sym} — {desc}" for sym, desc in hits)
            description = f"{result_text}\n\n**{details}**\nYou won **{winnings}** coins."
        else:
            title = "💀 You Lose"
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
    @slots.command(name="payouts")
    async def slots_payouts(self, ctx):
        """View the slots payout table."""
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### 🎰 Slots Payouts"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"**Common Symbols (🍒🍋🍊)**\n2× bet\n\n**Uncommon Symbols (🍇🍉🍓)**\n3× bet\n\n**Rare Symbols (🍀💎)**\n5× bet\n\n**Jackpot Symbol (⭐️)**\n25× bet\n\n**Full Board Jackpot**\n100× bet"
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