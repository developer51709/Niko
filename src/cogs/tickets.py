import asyncio
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

from utils.ticket_utils import (
    get_ticket_config,
    update_ticket_config,
    get_all_ticket_configs,
)
from utils.ticket_config import TicketConfig


# -------------------- UTILITY FUNCTIONS --------------------

def parse_hex_color(text: str) -> int | None:
    text = text.strip().replace("#", "")
    try:
        return int(text, 16)
    except ValueError:
        return None


def color_to_markdown(color: int | None) -> str:
    if color is None:
        return ""
    return f"`#{color:06X}`"


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


# -------------------- ADMIN SETUP BUTTONS --------------------

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

        view = TicketPanelView(self.guild_id, cfg)
        msg = await interaction.channel.send(view=view)

        cfg.panel_message_id = msg.id
        cfg.panel_channel_id = interaction.channel.id
        update_ticket_config(self.guild_id, cfg)

        await interaction.response.send_message("Ticket panel posted.", ephemeral=True)


# -------------------- USER-FACING PANEL BUTTONS --------------------

class OpenTicketBtn(discord.ui.Button):
    def __init__(self, guild_id: int):
        super().__init__(
            label="Create Ticket",
            style=discord.ButtonStyle.green,
            custom_id=f"open_ticket_{guild_id}",
        )
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        cfg = get_ticket_config(self.guild_id)

        if cfg.panel_categories:
            view = CategorySelectView(self.guild_id, cfg.panel_categories)
            return await interaction.response.send_message(
                "Choose a category:", view=view, ephemeral=True
            )

        await create_ticket(interaction, "General")


# -------------------- ADMIN CONTROLS INSIDE TICKET --------------------

class CloseTicketBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Close Ticket",
            style=discord.ButtonStyle.danger,
            custom_id="ticket_close",
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message(
                "You don't have permission to close tickets.", ephemeral=True
            )

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.response.send_message(
                "This can only be used in a ticket channel.", ephemeral=True
            )

        await interaction.response.send_message("Closing ticket...", ephemeral=True)

        overwrites = channel.overwrites
        for target, perms in list(overwrites.items()):
            if isinstance(target, discord.Role) and target.is_default():
                perms.send_messages = False
                perms.view_channel = False
                overwrites[target] = perms

        await channel.edit(overwrites=overwrites, name=f"closed-{channel.name}")
        await channel.send("This ticket has been closed by staff.")


class DeleteTicketBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Delete Ticket",
            style=discord.ButtonStyle.secondary,
            custom_id="ticket_delete",
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message(
                "You don't have permission to delete tickets.", ephemeral=True
            )

        await interaction.response.send_message("Deleting ticket in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Ticket deleted by {interaction.user}")


class TicketControlRow(discord.ui.ActionRow):
    def __init__(self):
        super().__init__()
        self.add_item(CloseTicketBtn())
        self.add_item(DeleteTicketBtn())


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

class TicketSetupRow(discord.ui.ActionRow):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__()
        self.add_item(ConfigurePanelBtn(guild_id, author))
        self.add_item(AddCategoryBtn(guild_id, author))
        self.add_item(PostTicketPanelBtn(guild_id, author))


class TicketPanelView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, cfg: TicketConfig | None = None):
        super().__init__(timeout=None)
        cfg = cfg or get_ticket_config(guild_id)

        title = cfg.panel_title or "Open a Ticket"
        desc = cfg.panel_description or "Select a category or press the button."
        color_md = color_to_markdown(cfg.panel_color)

        header = f"### 🎫 {title}"
        if color_md:
            header += f" {color_md}"

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=header),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=desc),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )

        if cfg.panel_image:
            container.add_item(
                discord.ui.TextDisplay(content=f"![panel-image]({cfg.panel_image})")
            )

        # row with the "Create Ticket" button
        container.add_item(
            discord.ui.ActionRow(
                OpenTicketBtn(guild_id)
            )
        )

        self.add_item(container)


class CategorySelectView(discord.ui.View):
    def __init__(self, guild_id: int, categories: list[str]):
        super().__init__(timeout=None)
        self.add_item(CategorySelect(guild_id, categories))


class TicketSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member):
        super().__init__(timeout=None)
        self.container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Ticket System Setup"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="Configure your ticket system below."),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        self.container.add_item(TicketSetupRow(guild_id, author))
        self.add_item(self.container)


class TicketView(discord.ui.LayoutView):
    def __init__(self, category: str, user: discord.Member | None = None):
        super().__init__(timeout=None)
        mention = user.mention if user else "a member"
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### 🎫 {category} Ticket"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"Welcome to your ticket {mention}! A staff member will be with you shortly."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        container.add_item(TicketControlRow())
        self.add_item(container)


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

    view = TicketView(category, user)
    msg = await channel.send(view=view)

    cfg = get_ticket_config(guild.id)
    cfg.open_tickets.append({
        "channel_id": channel.id,
        "message_id": msg.id,
        "category": category,
        "opener_id": user.id,
        "status": "open"
    })
    update_ticket_config(guild.id, cfg)

    if interaction.response.is_done():
        await interaction.followup.send(
            f"Your ticket has been created: {channel.mention}", ephemeral=True
        )
    else:
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
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(Tickets(bot))

    # reattach persistent ticket panels
    for cfg in get_all_ticket_configs():
        if cfg.panel_message_id:
            bot.add_view(
                TicketPanelView(cfg.guild_id, cfg),
                message_id=cfg.panel_message_id
            )

        # reattach open ticket views
        for t in cfg.open_tickets:
            if t.get("message_id"):
                bot.add_view(
                    TicketView(
                        t["category"],
                        user=bot.get_user(t["opener_id"]),
                    ),
                    message_id=t["message_id"],
                )