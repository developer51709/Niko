import discord
from discord.ext import commands
import random
import time
import asyncio
import os

slots_cooldown = os.getenv("SLOTS_COOLDOWN") or 60

class SpinAgainView(discord.ui.View):
    def __init__(self, ctx, amount, timeout=None):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.amount = amount
        self.choice = None

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Spin Again", style=discord.ButtonStyle.green)
    async def spin_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.choice = "spin"
        self.stop()
        await interaction.response.defer()


class Slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="slots")
    async def slots(self, ctx, amount: int = None):
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
        embed = discord.Embed(
            title="🎰 Slots",
            description="Spinning...",
            color=discord.Color.gold()
        )
        msg = await ctx.send(embed=embed)

        # Fake spinning animation
        for _ in range(3):
            grid = spin_grid()
            embed.description = grid_to_text(grid)
            await msg.edit(embed=embed)
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
            color = discord.Color.green()
            details = "\n".join(f"{sym} — {desc}" for sym, desc in hits)
            description = f"{result_text}\n\n**{details}**\nYou won **{winnings}** coins."
        else:
            title = "💀 You Lose"
            color = discord.Color.red()
            description = f"{result_text}\n\nYou lost **{amount}** coins."

        result_embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )

        # Spin Again button
        view = SpinAgainView(ctx, amount)
        await msg.edit(embed=result_embed, view=view)

        await view.wait()

        if view.choice == "spin":
            return await self.slots(ctx, amount)

async def setup(bot):
    await bot.add_cog(Slots(bot))