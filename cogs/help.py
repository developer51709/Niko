import discord
from discord.ext import commands

# ============================
#  DROPDOWN SELECT MENU
# ============================

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot

        options = [
            discord.SelectOption(
                label="General", 
                description="General bot information"
            ),
            discord.SelectOption(
                label="Fun", 
                description="Fun commands"
            ),
            discord.SelectOption(
                label="Gambling", 
                description="Blackjack, Slots, Roulette"
            ),
            discord.SelectOption(
                label="Economy", 
                description="Balance, daily, work, etc"
            ),
            discord.SelectOption(
                label="Roleplay", 
                description="RP commands"
            ),
            discord.SelectOption(
                label="Info", 
                description="User/server info commands"
            ),
            discord.SelectOption(
                label="Utility", 
                description="Misc tools and utilities"
            ),
            discord.SelectOption(
                label="AI", 
                description="AI commands"
            ),
            discord.SelectOption(
                label="Moderation", 
                description="Moderation commands"
            ),
            discord.SelectOption(
                label="AutoMod", 
                description="AutoMod commands"
            ),
            discord.SelectOption(
                label="EmojiManager", 
                description="EmojiManager commands"
            ),
            discord.SelectOption(
                label="Onboarding", 
                description="Onboarding commands"
            ),
            discord.SelectOption(
                label="NSFW", 
                description="NSFW commands"
            ),
            discord.SelectOption(
                label="Music", 
                description="Music commands"
            ),
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
        #  FUN CATEGORY
        # ===========================
        elif category == "Fun":
            embed.description = "🎉 **Fun Commands**"
            # Collect commands from fun cogs
            fun_cogs = ["UwULock", "Meme", "tictactoe", "CuteAnimals"]
            for cog_name in fun_cogs:
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
        #  AI CATEGORY
        # ===========================
        elif category == "AI":
            embed.description = "🤖 **AI Commands**"
            embed.add_field(
                name="`ai`",
                value="Talk to Niko",
                inline=False
            )
            cog = self.bot.get_cog("AICog")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  MODERATION CATEGORY
        # ===========================
        elif category == "Moderation":
            embed.description = "🛡 **Moderation Commands**"
            cog = self.bot.get_cog("Moderation")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  AUTOMOD CATEGORY
        # ===========================
        elif category == "AutoMod":
            embed.description = "⚔️ **AutoMod Commands**"
            cog = self.bot.get_cog("AutoMod")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  EMOJIMANAGER CATEGORY
        # ===========================
        elif category == "EmojiManager":
            embed.description = "😂 **EmojiManager Commands**"
            cog = self.bot.get_cog("EmojiManagerCog")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  ONBOARDING CATEGORY
        # ===========================
        elif category == "Onboarding":
            embed.description = "🎉 **Onboarding Commands**"
            cog = self.bot.get_cog("Onboarding")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  NSFW CATEGORY
        # ===========================
        elif category == "NSFW":
            embed.description = "🔞 **NSFW Commands**\n> NOTICE: These commands are only allowed in nsfw channels and will not work elsewhere."
            cog = self.bot.get_cog("NSFW")
            if cog:
                for cmd in cog.get_commands():
                    embed.add_field(
                        name=f"`{cmd.name}`",
                        value=cmd.help or "No description",
                        inline=False
                    )

        # ===========================
        #  MUSIC CATEGORY
        # ===========================
        elif category == "Music":
            embed.description = "🎵 **Music Commands**"
            cog = self.bot.get_cog("MusicSystem")
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
                "> Use the dropdown below to browse categories."
            )
            embed.add_field(
                name="🤖 About Niko",
                value="Niko is a simple, lightweight, open-source AI powered Discord bot made to provide Discord servers with a fun, interactive, and engaging experience.",
                inline=False
            )
            embed.add_field(
                name="🔗 Links",
                value=f"[GitHub](https://github.com/developer51709/Niko) | [invite](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8)",
                inline=False
            )
            embed.set_footer(text="Made with ❤️ by Nyxen")

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
    async def help(self, ctx, *, command_name=None):
        """Shows the help menu or info about a specific command."""

    # -------------------------------
    # INDIVIDUAL COMMAND HELP
    # -------------------------------
        if command_name:
            cmd = self.bot.get_command(command_name)

            if not cmd:
                embed = discord.Embed(
                    title="❌ Command Not Found",
                    description=f"No command named `{command_name}` exists.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)

            embed = discord.Embed(
                title=f"📘 Help: `{cmd.name}`",
                color=discord.Color.blue()
            )

            # Description / docstring
            embed.add_field(
                name="Description",
                value=cmd.help or "No description provided.",
                inline=False
            )

            # Aliases
            if cmd.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join(f"`{a}`" for a in cmd.aliases),
                    inline=False
                )

            # Usage (auto-generated)
            signature = cmd.signature or ""
            embed.add_field(
                name="Usage",
                value=f"`{self.bot.command_prefix}{cmd.name} {signature}`",
                inline=False
            )

            # Cog name
            if cmd.cog_name:
                embed.add_field(
                    name="Category",
                    value=cmd.cog_name,
                    inline=False
                )

            embed.set_footer(text=f"Requested by {ctx.author}")
            return await ctx.send(embed=embed)

    # -------------------------------
    # DEFAULT HELP MENU (dropdown)
    # -------------------------------
        embed = discord.Embed(
            title="📘 Help Menu",
            description="> Use the dropdown below to select a category.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🤖 About Niko",
            value="Niko is a simple, lightweight, open-source AI powered Discord bot made to provide Discord servers with a fun, interactive, and engaging experience.",
            inline=False
        )
        embed.add_field(
            name="🔗 Links",
            value=f"[GitHub](https://github.com/developer51709/Niko) | [invite](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8)",
            inline=False
        )
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed, view=HelpView(self.bot))


async def setup(bot):
    await bot.add_cog(HelpCog(bot))