import discord
from discord.ext import commands

# ============================
#  DROPDOWN SELECT MENU
# ============================

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot

        options = [
            discord.SelectOption(label="General", description="General bot information"),
            discord.SelectOption(label="Gambling", description="Blackjack, Slots, Roulette"),
            discord.SelectOption(label="Economy", description="Balance, daily, work, etc"),
            discord.SelectOption(label="Roleplay", description="RP commands"),
            discord.SelectOption(label="Info", description="User/server info commands"),
            discord.SelectOption(label="Utility", description="Misc tools and utilities"),
            discord.SelectOption(label="AI", description="AI commands"),
        ]

        super().__init__(
            placeholder="Select a help category",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = discord.Embed(
            title=f"📘 {category} Help",
            color=discord.Color.blue()
        )

        # ===========================
        #  GAMBLING CATEGORY
        # ===========================
        if category == "Gambling":
            embed.description = "🎰 **Casino Commands**\nBlackjack, Slots, Roulette"

            # Collect commands from gambling cogs
            gambling_cogs = ["Blackjack", "Roulette", "Slots", "GamblingCog"]
            for cog_name in gambling_cogs:
                cog = self.bot.get_cog(cog_name)
                if cog:
                    for cmd in cog.get_commands():
                        embed.add_field(
                            name=f"`{cmd.name}`",
                            value=cmd.help or "No description",
                            inline=False
                        )

        # ===========================
        #  ECONOMY CATEGORY
        # ===========================
        elif category == "Economy":
            embed.description = "💰 **Economy Commands**"
            cog = self.bot.get_cog("EconomyCog")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  ROLEPLAY CATEGORY
        # ===========================
        elif category == "Roleplay":
            embed.description = "🎭 **Roleplay Commands**"
            cog = self.bot.get_cog("RolePlayCog")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  INFO CATEGORY
        # ===========================
        elif category == "Info":
            embed.description = "ℹ️ **Information Commands**"
            cog = self.bot.get_cog("InfoCog")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  UTILITY CATEGORY
        # ===========================
        elif category == "Utility":
            embed.description = "🛠️ **Utility Commands**"
            cog = self.bot.get_cog("UtilityCog")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  UTILITY CATEGORY
        # ===========================
        elif category == "AI":
            embed.description = "🤖 **AI Commands**"
            cog = self.bot.get_cog("AICog")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  GENERAL CATEGORY
        # ===========================
        else:
            embed.description = (
                "Welcome to the help menu.\n"
                "Use the dropdown below to browse categories."
            )

        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(HelpDropdown(bot))


# ============================
#  HELP COG
# ============================

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx):
        """Shows the help menu."""
        embed = discord.Embed(
            title="📘 Help Menu",
            description="Use the dropdown below to select a category.",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed, view=HelpView(self.bot))


async def setup(bot):
    await bot.add_cog(HelpCog(bot))