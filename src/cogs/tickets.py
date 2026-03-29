import asyncio
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from utils.ticket_utils import (
    get_ticket_config,
    update_ticket_config,
)
from utils.ticket_config import TicketConfig


# -------------------- UTILITY FUNCTIONS --------------------

def parse_hex_color(text: str) -> int | None:
    text = text.strip().replace("#", "")
    try:
        return int(text, 16)
    except ValueError:
        return None


# -------------------- MODALS --------------------

class TicketPanelModal(Modal, title="Configure Ticket Panel"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        self.title_input = TextInput(label="Panel Title", required=False)
        self.desc_input = TextInput(
            label="Panel Description",
            style=discord.TextStyle.long,
            required=False,
        )
        self.color_input = TextInput(label="Color (hex)", required=False)
        self.categories_input = TextInput(
            label="Categories (comma-separated)",
            required=False
        )
        self.image_input = TextInput(label="Image URL", required=False)

        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.color_input)
        self.add_item(self.categories_input)
        self.add_item(self.image_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)

        if self.title_input.value:
            cfg.panel_title = self.title_input.value

        if self.desc_input.value:
            cfg.panel_description = self.desc_input.value

        if self.color_input.value:
            parsed = parse_hex_color(self.color_input.value)
            if parsed is not None:
                cfg.panel_color = parsed

        if self.categories_input.value:
            cats = [c.strip() for c in self.categories_input.value.split(",") if c.strip()]
            cfg.panel_categories = cats

        cfg.panel_image = self.image_input.value or None

        update_ticket_config(self.guild_id, cfg)
        await interaction.response.send_message("Ticket panel updated.", ephemeral=True)


class TicketCategoryModal(Modal, title="Add Ticket Category"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        self.label_input = TextInput(label="Category Name")
        self.add_item(self.label_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)

        if cfg.panel_categories is None:
            cfg.panel_categories = []

        cfg.panel_categories.append(self.label_input.value.strip())
        update_ticket_config(self.guild_id, cfg)

        await interaction.response.send_message("Category added.", ephemeral=True)


# -------------------- BUTTONS --------------------

class ConfigurePanelBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Configure Ticket Panel", style=discord.ButtonStyle.primary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "Only the command invoker can use this.", ephemeral=True
            )
        await interaction.response.send_modal(TicketPanelModal(self.guild_id))


class AddCategoryBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Add Category", style=discord.ButtonStyle.secondary)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "Only the command invoker can use this.", ephemeral=True
            )
        await interaction.response.send_modal(TicketCategoryModal(self.guild_id))


class PostTicketPanelBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(label="Post Ticket Panel Here", style=discord.ButtonStyle.success)
        self.guild_id = guild_id
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "Only the command invoker can use this.", ephemeral=True
            )

        cfg = get_ticket_config(self.guild_id)

        embed = discord.Embed(
            title=cfg.panel_title or "Open a Ticket",
            description=cfg.panel_description or "Select a category or press the button.",
            color=cfg.panel_color or 0x00FF00
        )

        if cfg.panel_image:
            embed.set_image(url=cfg.panel_image)

        view = TicketPanelView(self.guild_id)
        msg = await interaction.channel.send(embed=embed, view=view)

        cfg.panel_message_id = msg.id
        cfg.panel_channel_id = interaction.channel.id
        update_ticket_config(self.guild_id, cfg)

        await interaction.response.send_message("Ticket panel posted.", ephemeral=True)


# -------------------- USER-FACING PANEL BUTTONS --------------------

class OpenTicketBtn(discord.ui.Button):
    def __init__(self, guild_id: int):
        super().__init__(label="Create Ticket", style=discord.ButtonStyle.green)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)

        if cfg.panel_categories:
            view = CategorySelectView(self.guild_id, cfg.panel_categories)
            return await interaction.response.send_message(
                "Choose a category:", view=view, ephemeral=True
            )

        await create_ticket(interaction, "General")


# -------------------- SELECT MENU --------------------

class CategorySelect(discord.ui.Select):
    def __init__(self, guild_id: int, categories: list[str]):
        self.guild_id = guild_id
        options = [
            discord.SelectOption(label=c, description=f"Open a {c} ticket")
            for c in categories
        ]
        super().__init__(placeholder="Select category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.values[0])


# -------------------- VIEWS --------------------

class TicketSetupView(discord.ui.View):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(timeout=None)
        self.add_item(ConfigurePanelBtn(guild_id, author))
        self.add_item(AddCategoryBtn(guild_id, author))
        self.add_item(PostTicketPanelBtn(guild_id, author))


class TicketPanelView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.add_item(OpenTicketBtn(guild_id))


class CategorySelectView(discord.ui.View):
    def __init__(self, guild_id: int, categories: list[str]):
        super().__init__(timeout=None)
        self.add_item(CategorySelect(guild_id, categories))


# -------------------- TICKET CREATION LOGIC --------------------

async def create_ticket(interaction: discord.Interaction, category: str):
    guild = interaction.guild
    user = interaction.user

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        overwrites=overwrites,
        reason=f"Ticket opened by {user}",
    )

    embed = discord.Embed(
        title=f"{category} Ticket",
        description=f"{user.mention}, thanks for opening a ticket.",
        color=0x00FF00,
    )

    await channel.send(embed=embed)
    await interaction.response.send_message(
        f"Your ticket has been created: {channel.mention}", ephemeral=True
    )


# -------------------- COG --------------------

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticketsetup")
    @commands.has_permissions(administrator=True)
    async def ticketsetup(self, ctx: commands.Context):
        view = TicketSetupView(ctx.guild.id, ctx.author)
        await ctx.send("Ticket system setup:", view=view)


async def setup(bot):
    await bot.add_cog(Tickets(bot))