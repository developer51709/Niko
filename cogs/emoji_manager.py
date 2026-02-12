import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument, EmojiNotFound
import io
import aiohttp
import pathlib
import re
from typing import Optional
import zipfile
import asyncio

DATA_DIR = pathlib.Path("data/emojimanager/")

EMOJI_REGEX = re.compile(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]+):(?P<id>[0-9]+)>")
URL_REGEX = re.compile(r"https?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

class EmojiManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def get_prefix(self, ctx):
        if isinstance(self.bot.command_prefix, list):
            return self.bot.command_prefix[0]
        return self.bot.command_prefix

    async def _get_emoji_info(self, emoji_string: str):
        """
        Parses an emoji string (<:name:id> or <a:name:id>) and fetches its image data.
        Returns: name, image_data, animated, url
        """
        match = EMOJI_REGEX.match(emoji_string)
        if not match:
            return None, None, None, None 

        emoji_id = match.group("id")
        emoji_name = match.group("name")
        animated = bool(match.group("animated"))
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if animated else 'png'}"

        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    return emoji_name, image_data, animated, url
                else:
                    return emoji_name, None, animated, None
        except aiohttp.ClientError:
            
            return emoji_name, None, animated, None

    async def _add_emoji(self, ctx, name, image_data):
        """
        Helper function to add an emoji to the guild.
        Returns True on success, False on failure.
        """
        try:
            guild = ctx.guild
            if guild.emoji_limit <= len(guild.emojis):
                embed = discord.Embed(
                    title="Server Full",
                    description=f"This server has reached its maximum emoji limit of {guild.emoji_limit}.",
                    color=discord.Color.red()
                )
                embed.set_footer(text="Made By Nyxen")
                await ctx.send(embed=embed)
                return False

            new_emoji = await guild.create_custom_emoji(name=name, image=image_data)
            
            embed = discord.Embed(
                title="Emoji Added",
                description=f"Successfully added emoji: {new_emoji} (`:{new_emoji.name}:`)",
                color=discord.Color.green()
            )
            embed.set_footer(text="Made By Nyxen")
            await ctx.send(embed=embed)
            return True
        except discord.Forbidden:
            await ctx.send("I don't have the permissions to add emojis.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
        return False

    @commands.command(name="emojimanager", aliases=["em"])
    async def emojimanager_help(self, ctx):
        """Displays the help menu for the Emoji Manager cog."""
        prefix = self.get_prefix(ctx)
        
        embed = discord.Embed(
            title="Emoji Manager Commands",
            description="Here is a list of all commands for managing emojis. All commands require `Manage Guild` or `Administrator` permissions.",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name=f"`{prefix}steal <emoji_string>`",
            value="Steals a single custom emoji from any server and adds it to the current one. **Provide the full emoji string like `<:name:id>` or `<a:name:id>`.** The bot does not need to be in the origin server.",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}steal-multiple <emoji_strings...>`",
            value="Steals multiple custom emojis in one command. Provide a space-separated list of full emoji strings.",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}steal-from-url <URL> [name]`",
            value="Adds a new emoji by providing a direct image URL. You can optionally specify a name for the emoji.",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}stickersteal`",
            value="Steals a sticker by prompting you to send one in the chat. The bot will then ask for a name to add it as a custom emoji.",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}enlarge <emoji_string>`",
            value="Displays a larger PNG/GIF version of a given custom emoji. **Provide the full emoji string like `<:name:id>` or `<a:name:id>`.**",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}emojistats`",
            value="Displays a detailed breakdown of the server's emoji usage and available slots.",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}list-emojis`",
            value="Provides a list of all custom emojis in the server with their names and animated status.",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}extract-emoji <emoji_string>`",
            value="Sends the image file for a given custom emoji. **Provide the full emoji string like `<:name:id>` or `<a:name:id>`.**",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}emdownloadserver`",
            value="Downloads all custom emojis from the server and sends them as a zip file.",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}emdownload <<emoji_string>/sticker>`",
            value=f"Downloads a specific custom emoji or sticker and puts it in a zip file.\n If you want to download the sticker execute: {prefix}emdownload sticker (just say 'sticker' when you execute it like that, it will ask you to send the sticker then it puts it in a zip)\n If you want to download an emoji do {prefix}emdownload `<:emoji:id>`",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}remove-emoji <emoji>`",
            value="Removes a single custom emoji from the server.",
            inline=False
        )
        embed.add_field(
            name=f"`{prefix}remove-all-emojis`",
            value="Removes all custom emojis from the server with a confirmation button.",
            inline=False
        )
        
        embed.set_footer(text="Made By Nyxen")
        
        await ctx.send(embed=embed)

    @commands.command(name="steal")
    @has_permissions(manage_guild=True)
    async def steal_emoji(self, ctx, emoji_string: str):
        """Steals a single custom emoji from any server and adds it to the current one."""
        await ctx.typing()
        
        name, image_data, animated, url = await self._get_emoji_info(emoji_string)
        
        if not image_data:
            embed = discord.Embed(
                title="Error Stealing Emoji",
                description="Could not find or download the emoji. Please ensure you provided the full emoji string (e.g., `<:name:id>`).",
                color=discord.Color.red()
            )
            embed.set_footer(text="Made By Nyxen")
            await ctx.send(embed=embed)
            return
        
        await self._add_emoji(ctx, name, image_data)

    @commands.command(name="steal-multiple", aliases=["sm", "stealall"])
    @has_permissions(manage_guild=True)
    async def steal_multiple_emojis(self, ctx, *emoji_strings: str):
        """Steals multiple custom emojis in one command."""
        await ctx.typing()

        added_emojis = []
        failed_emojis = []

        if not emoji_strings:
            embed = discord.Embed(
                title="Missing Emojis",
                description="Please provide one or more full emoji strings (e.g., `<:name:id>`) to steal.",
                color=discord.Color.red()
            )
            embed.set_footer(text="Made By Nyxen")
            await ctx.send(embed=embed)
            return

        for emoji_string in emoji_strings:
            name, image_data, animated, url = await self._get_emoji_info(emoji_string)
            
            if image_data:
                success = await self._add_emoji(ctx, name, image_data)
                if success:
                    added_emojis.append(name)
                else:
                    failed_emojis.append(f"Failed to add: `{name}` (server limit or permissions)")
            else:
                failed_emojis.append(f"Failed to find or download: `{emoji_string}` (invalid format or URL)")

        embed = discord.Embed(
            title="Multi-Emoji Steal Summary",
            color=discord.Color.blue()
        )
        if added_emojis:
            embed.add_field(name="✅ Added Emojis", value="\n".join([f":{name}:" for name in added_emojis]), inline=False)
        if failed_emojis:
            embed.add_field(name="❌ Failed Emojis", value="\n".join(failed_emojis), inline=False)
        else:
            embed.description = "All specified emojis were processed successfully!"

        embed.set_footer(text="Made By Nyxen")
        await ctx.send(embed=embed)

    @commands.command(name="steal-from-url", aliases=["surl"])
    @has_permissions(manage_guild=True)
    async def steal_from_url(self, ctx, url: str, name: Optional[str] = None):
        """Adds a new emoji by providing a direct image URL."""
        await ctx.typing()

        if not URL_REGEX.match(url):
            return await ctx.send("The provided URL is invalid.")

        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send("Could not download the image from that URL.")
                
                image_data = await resp.read()
                
                if name is None:
                    file_name = url.split('/')[-1]
                    name = file_name.split('.')[0] if '.' in file_name else "new_emoji"
                
                await self._add_emoji(ctx, name, image_data)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(name="stickersteal", aliases=["ss"])
    @has_permissions(manage_guild=True)
    async def stickersteal(self, ctx):
        """Steals a sticker by prompting the user to send one in the chat."""
        await ctx.send("Please send the sticker you want to steal within the next 30 seconds.")
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.stickers

        try:
            sticker_message = await self.bot.wait_for('message', check=check, timeout=30.0)
            sticker = sticker_message.stickers[0]
            
            await ctx.send("What would you like to name this new emoji? Respond within 30 seconds.")

            def name_check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content

            try:
                name_message = await self.bot.wait_for('message', check=name_check, timeout=30.0)
                name = name_message.content
                
                if not name.isalnum() or not 2 <= len(name) <= 32:
                    return await ctx.send("Invalid name. Please use alphanumeric characters and ensure the name is between 2 and 32 characters long.")

                url = sticker.url
                await ctx.typing()
                
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        return await ctx.send("Could not download the sticker image.")
                    
                    image_data = await resp.read()
                    await self._add_emoji(ctx, name, image_data)
            
            except asyncio.TimeoutError:
                await ctx.send("You took too long to provide a name. Operation cancelled.")
            
        except asyncio.TimeoutError:
            await ctx.send("You took too long to send a sticker. Operation cancelled.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(name="enlarge")
    async def enlarge_emoji(self, ctx, emoji_string: str):
        """Displays a larger PNG/GIF version of a given custom emoji."""
        await ctx.typing()
        
        name, image_data, animated, url = await self._get_emoji_info(emoji_string)

        if not image_data:
            embed = discord.Embed(
                title="Error Enlarging Emoji",
                description="Could not find or download the emoji. Please ensure you provided the full emoji string (e.g., `<:name:id>`).",
                color=discord.Color.red()
            )
            embed.set_footer(text="Made By Nyxen")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title=f"Enlarged Emoji: :{name}:", color=discord.Color.blue())
        embed.set_image(url=url)
        embed.set_footer(text="Made By Nyxen")
        await ctx.send(embed=embed)

    @commands.command(name="emojistats")
    @has_permissions(manage_guild=True)
    async def emoji_stats(self, ctx):
        """Displays a detailed breakdown of the server's emoji usage and available slots."""
        guild = ctx.guild
        static_emojis = [e for e in guild.emojis if not e.animated]
        animated_emojis = [e for e in guild.emojis if e.animated]
        
        static_count = len(static_emojis)
        animated_count = len(animated_emojis)
        
        static_limit = guild.emoji_limit
        animated_limit = guild.emoji_limit

        static_used_percentage = (static_count / static_limit) * 100 if static_limit > 0 else 0
        animated_used_percentage = (animated_count / animated_limit) * 100 if animated_limit > 0 else 0

        static_progress = "█" * int(static_used_percentage / 10) + " " * (10 - int(static_used_percentage / 10))
        animated_progress = "█" * int(animated_used_percentage / 10) + " " * (10 - int(animated_used_percentage / 10))

        embed = discord.Embed(
            title=f"Emoji Stats for {guild.name}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Static Emojis",
            value=(
                f"Used: **{static_count}/{static_limit}**\n"
                f"Progress: `[{static_progress}]`\n"
                f"Remaining: **{static_limit - static_count}**"
            ),
            inline=False
        )
        embed.add_field(
            name="Animated Emojis",
            value=(
                f"Used: **{animated_count}/{animated_limit}**\n"
                f"Progress: `[{animated_progress}]`\n"
                f"Remaining: **{animated_limit - animated_count}**"
            ),
            inline=False
        )
        
        embed.set_footer(text="Made By Nyxen")
        await ctx.send(embed=embed)

    @commands.command(name="list-emojis", aliases=["le"])
    @has_permissions(manage_guild=True)
    async def list_emojis(self, ctx):
        """Provides a list of all custom emojis in the server with their names and animated status."""
        guild = ctx.guild
        emojis_list = sorted(guild.emojis, key=lambda e: e.name)

        if not emojis_list:
            return await ctx.send("This server has no custom emojis.")

        static_emojis = [f":{e.name}: (`:{e.name}:`)" for e in emojis_list if not e.animated]
        animated_emojis = [f":{e.name}: (`:{e.name}:`)" for e in emojis_list if e.animated]

        embed = discord.Embed(
            title=f"Custom Emojis in {guild.name}",
            color=discord.Color.blue()
        )
        
        static_field = "\n".join(static_emojis) if static_emojis else "No static emojis."
        animated_field = "\n".join(animated_emojis) if animated_emojis else "No animated emojis."
        
        embed.add_field(name="Static Emojis", value=static_field, inline=False)
        embed.add_field(name="Animated Emojis", value=animated_field, inline=False)
        embed.set_footer(text="Made By Nyxen")

        await ctx.send(embed=embed)

    @commands.command(name="extract-emoji", aliases=["ee"])
    @has_permissions(manage_guild=True)
    async def extract_emoji(self, ctx, emoji_string: str):
        """Sends the image file for a given custom emoji."""
        await ctx.typing()
        
        name, image_data, animated, url = await self._get_emoji_info(emoji_string)

        if not image_data:
            embed = discord.Embed(
                title="Error Extracting Emoji",
                description="Could not find or download the emoji. Please ensure you provided the full emoji string (e.g., `<:name:id>`).",
                color=discord.Color.red()
            )
            embed.set_footer(text="Made By Nyxen")
            await ctx.send(embed=embed)
            return

        file_extension = "gif" if animated else "png"
        file_name = f"{name}.{file_extension}"
        file = discord.File(io.BytesIO(image_data), filename=file_name)
        
        embed = discord.Embed(
            title=f"Extracted Emoji: `{name}`",
            description=f"Here is the `{name}` emoji as a file.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Made By Nyxen")
        
        await ctx.send(embed=embed, file=file)

    @commands.command(name="emdownloadserver")
    @has_permissions(manage_guild=True)
    async def emdownloadserver(self, ctx):
        """Downloads all custom emojis from the server and sends them as a zip file."""
        await ctx.typing()
        
        guild = ctx.guild
        emojis = guild.emojis
        
        if not emojis:
            return await ctx.send("This server has no custom emojis to download.")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for emoji in emojis:
                try:
                    async with self.session.get(emoji.url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            file_extension = "gif" if emoji.animated else "png"
                            zip_file.writestr(f"{emoji.name}.{file_extension}", image_data)
                except Exception as e:
                    print(f"Failed to download emoji {emoji.name}: {e}")
        
        buffer.seek(0)
        
        file = discord.File(buffer, filename=f"{guild.name}_emojis.zip")
        await ctx.send(f"Here are all {len(emojis)} custom emojis from **{guild.name}** in a zip file.", file=file)

    @commands.command(name="emdownload")
    @has_permissions(manage_guild=True)
    async def emdownload(self, ctx, item: str):
        """Downloads a specific custom emoji or sticker and puts it in a zip file."""
        await ctx.typing()
        
        if item.lower() == "sticker":
            await ctx.send("Please send the sticker you want to download within the next 30 seconds.")
            
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.stickers

            try:
                sticker_message = await self.bot.wait_for('message', check=check, timeout=30.0)
                sticker = sticker_message.stickers[0]
                
                url = sticker.url
                name = sticker.name
                
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    async with self.session.get(url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            zip_file.writestr(f"{name}.png", image_data)
                        else:
                            return await ctx.send("Failed to download the sticker image.")
                
                buffer.seek(0)
                file = discord.File(buffer, filename=f"{name}.zip")
                await ctx.send("Here is your requested sticker in a zip file.", file=file)
                
            except asyncio.TimeoutError:
                await ctx.send("You took too long to send a sticker. Operation cancelled.")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
        else:
            # Assume it's an emoji string
            name, image_data, animated, url = await self._get_emoji_info(item)

            if not image_data:
                await ctx.send("The provided item is not a valid custom emoji or sticker. Please ensure you provided the full emoji string (e.g., `<:name:id>`) or 'sticker'.")
                return

            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                file_extension = "gif" if animated else "png"
                zip_file.writestr(f"{name}.{file_extension}", image_data)

            buffer.seek(0)
            file = discord.File(buffer, filename=f"{name}.zip")
            await ctx.send("Here is your requested emoji in a zip file.", file=file)


    @commands.command(name="remove-emoji", aliases=["re"])
    @has_permissions(manage_guild=True)
    async def remove_emoji(self, ctx, emoji: discord.Emoji):
        """Removes a single custom emoji from the server."""
        await ctx.typing()

        try:
            await emoji.delete()
            embed = discord.Embed(
                title="Emoji Removed",
                description=f"Successfully removed the emoji: `{emoji.name}`",
                color=discord.Color.green()
            )
            embed.set_footer(text="Made By Nyxen")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I don't have the permissions to remove emojis.")
        except Exception as e:
            await ctx.send(f"An error occurred while removing the emoji: {e}")

    @commands.command(name="remove-all-emojis", aliases=["rae"])
    @has_permissions(manage_guild=True)
    async def remove_all_emojis(self, ctx):
        """Removes all custom emojis from the server with a confirmation button."""
        
        class ConfirmView(discord.ui.View):
            def __init__(self, bot, author_id):
                super().__init__(timeout=60)
                self.bot = bot
                self.author_id = author_id
                self.confirmed = False

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
            async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != self.author_id:
                    await interaction.response.send_message("You are not the command author!", ephemeral=True)
                    return
                self.confirmed = True
                self.stop()
                await interaction.response.edit_message(content="Confirmation received. Removing all emojis...", view=None)

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != self.author_id:
                    await interaction.response.send_message("You are not the command author!", ephemeral=True)
                    return
                self.confirmed = False
                self.stop()
                await interaction.response.edit_message(content="Operation cancelled.", view=None)

            async def on_timeout(self):
                if not self.confirmed:
                    await self.message.edit(content="Timed out. Operation cancelled.", view=None)
        
        embed = discord.Embed(
            title="⚠️ Warning: Remove All Emojis",
            description="Are you sure you want to remove ALL custom emojis from this server? This action is irreversible.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Made By Nyxen")
        view = ConfirmView(self.bot, ctx.author.id)
        
        message = await ctx.send(embed=embed, view=view)
        view.message = message

        await view.wait()

        if view.confirmed:
            await ctx.typing()
            emojis = ctx.guild.emojis
            if not emojis:
                return await ctx.send("This server has no custom emojis to remove.")

            failed_deletions = []
            for emoji in emojis:
                try:
                    await emoji.delete()
                except discord.Forbidden:
                    failed_deletions.append(f"`:{emoji.name}:` (Forbidden)")
                except Exception as e:
                    failed_deletions.append(f"`:{emoji.name}:` ({e})")
            
            if failed_deletions:
                summary_embed = discord.Embed(
                    title="Bulk Removal Complete",
                    description=f"Successfully removed {len(emojis) - len(failed_deletions)}/{len(emojis)} emojis.",
                    color=discord.Color.orange()
                )
                summary_embed.add_field(name="Failed to Remove", value="\n".join(failed_deletions), inline=False)
                summary_embed.set_footer(text="Made By Nyxen")
                await ctx.send(embed=summary_embed)
            else:
                summary_embed = discord.Embed(
                    title="Bulk Removal Complete",
                    description=f"Successfully removed all {len(emojis)} custom emojis.",
                    color=discord.Color.green()
                )
                summary_embed.set_footer(text="Made By Nyxen")
                await ctx.send(embed=summary_embed)
        else:
            pass

async def setup(bot):
    await bot.add_cog(EmojiManagerCog(bot))