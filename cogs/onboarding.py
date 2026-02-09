import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button, Select

from .onboarding_utils import (
    get_config,
    update_config,
    build_welcome_embed,
    build_rules_embed,
)
from .onboarding_config import OnboardingConfig


# -------------------- UTILITY FUNCTIONS --------------------

def parse_role_from_text(text: str, guild: discord.Guild) -> discord.Role | None:
    text = text.strip()

    # ID
    if text.isdigit():
        return guild.get_role(int(text))

    # Mention
    if text.startswith("<@&") and text.endswith(">"):
        try:
            rid = int(text[3:-1])
            return guild.get_role(rid)
        except ValueError:
            return None

    # Name (fallback)
    return discord.utils.get(guild.roles, name=text)


# -------------------- MODALS --------------------

class WelcomeMessageModal(Modal, title="Set Welcome Message"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        self.title_input = TextInput(label="Title", required=False)
        self.desc_input = TextInput(
            label="Description",
            style=discord.TextStyle.long,
            placeholder="Use {user} for mention, {name} for username.",
            required=False,
        )
        self.image_input = TextInput(label="Image URL", required=False)
        self.color_input = TextInput(label="Color (hex)", required=False)

        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.image_input)
        self.add_item(self.color_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)

        if self.title_input.value:
            cfg.welcome_title = self.title_input.value

        if self.desc_input.value:
            cfg.welcome_description = self.desc_input.value

        cfg.welcome_image = self.image_input.value or None

        if self.color_input.value:
            try:
                cfg.welcome_color = int(self.color_input.value.replace("#", ""), 16)
            except ValueError:
                pass

        update_config(self.guild_id, cfg)
        await interaction.response.send_message("Welcome message updated.", ephemeral=True)


class RulesModal(Modal, title="Set Rules Text"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        self.rules_input = TextInput(
            label="Rules",
            style=discord.TextStyle.long,
        )
        self.add_item(self.rules_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        cfg.rules_text = self.rules_input.value
        update_config(self.guild_id, cfg)

        await interaction.response.send_message("Rules updated.", ephemeral=True)


class RoleMenuOptionModal(Modal, title="Add Role Menu Option"):
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id

        self.role_input = TextInput(label="Role ID or @mention")
        self.label_input = TextInput(label="Label")
        self.desc_input = TextInput(label="Description", required=False)
        self.emoji_input = TextInput(label="Emoji", required=False)

        self.add_item(self.role_input)
        self.add_item(self.label_input)
        self.add_item(self.desc_input)
        self.add_item(self.emoji_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)

        raw_role = self.role_input.value.strip()
        label = self.label_input.value.strip()
        desc = self.desc_input.value.strip()
        emoji = self.emoji_input.value.strip()

        role_id = None
        if raw_role.isdigit():
            role_id = int(raw_role)
        elif raw_role.startswith("<@&") and raw_role.endswith(">"):
            try:
                role_id = int(raw_role[3:-1])
            except ValueError:
                pass

        if role_id is None:
            await interaction.response.send_message("Invalid role.", ephemeral=True)
            return

        if cfg.role_menu_options is None:
            cfg.role_menu_options = []

        cfg.role_menu_options.append({
            "role_id": role_id,
            "label": label,
            "description": desc or None,
            "emoji": emoji or None,
        })

        update_config(self.guild_id, cfg)
        await interaction.response.send_message("Role option added.", ephemeral=True)


# -------------------- VIEWS --------------------

class RulesAcknowledgeView(View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="I Agree", style=discord.ButtonStyle.success)
    async def agree(self, interaction: discord.Interaction, button: Button):
        cfg = get_config(self.guild_id)

        if not cfg.rules_role_id:
            await interaction.response.send_message("No role configured.", ephemeral=True)
            return

        role = interaction.guild.get_role(cfg.rules_role_id)
        if not role:
            await interaction.response.send_message("Configured role no longer exists.", ephemeral=True)
            return

        await interaction.user.add_roles(role, reason="Acknowledged rules")
        await interaction.response.send_message("You have acknowledged the rules.", ephemeral=True)


class RoleMenuSelect(Select):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        cfg = get_config(guild_id)

        options = []
        if cfg.role_menu_options:
            for opt in cfg.role_menu_options:
                options.append(
                    discord.SelectOption(
                        label=opt["label"],
                        description=opt.get("description"),
                        emoji=opt.get("emoji"),
                        value=str(opt["role_id"]),
                    )
                )

        super().__init__(
            placeholder="Select roles...",
            min_values=0,
            max_values=len(options) if options else 1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        cfg = get_config(self.guild_id)
        member = interaction.user

        selected = {int(v) for v in self.values}
        all_roles = {int(opt["role_id"]) for opt in (cfg.role_menu_options or [])}

        to_add = []
        to_remove = []

        for rid in all_roles:
            role = interaction.guild.get_role(rid)
            if not role:
                continue

            if rid in selected and role not in member.roles:
                to_add.append(role)
            if rid not in selected and role in member.roles:
                to_remove.append(role)

        if to_add:
            await member.add_roles(*to_add)
        if to_remove:
            await member.remove_roles(*to_remove)

        await interaction.response.send_message("Roles updated.", ephemeral=True)


class RoleMenuView(View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.add_item(RoleMenuSelect(guild_id))


class OnboardingSetupView(View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="Set Welcome Message", style=discord.ButtonStyle.primary)
    async def welcome_msg(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(WelcomeMessageModal(self.guild_id))

    @discord.ui.button(label="Set Welcome Channel", style=discord.ButtonStyle.secondary)
    async def welcome_channel(self, interaction: discord.Interaction, button: Button):
        cfg = get_config(self.guild_id)
        cfg.welcome_channel = interaction.channel.id
        update_config(self.guild_id, cfg)
        await interaction.response.send_message(
            f"Welcome channel set to {interaction.channel.mention}.", ephemeral=True
        )

    @discord.ui.button(label="Set Rules Text", style=discord.ButtonStyle.primary)
    async def rules_text(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RulesModal(self.guild_id))

    @discord.ui.button(label="Post Rules Message Here", style=discord.ButtonStyle.secondary)
    async def post_rules(self, interaction: discord.Interaction, button: Button):
        cfg = get_config(self.guild_id)
        cfg.rules_channel = interaction.channel.id

        embed = build_rules_embed(cfg)
        view = RulesAcknowledgeView(self.guild_id)
        msg = await interaction.channel.send(embed=embed, view=view)

        cfg.rules_message_id = msg.id
        update_config(self.guild_id, cfg)

        await interaction.response.send_message("Rules message posted.", ephemeral=True)

    @discord.ui.button(label="Set Rules Role (reply with role)", style=discord.ButtonStyle.secondary)
    async def rules_role(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "Reply in this channel with a role mention, ID, or name within 60 seconds.",
            ephemeral=True
        )

        def check(msg: discord.Message) -> bool:
            return (
                msg.author == interaction.user
                and msg.channel == interaction.channel
            )

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out waiting for a reply. Try again.", ephemeral=True
            )
            return

        if not interaction.guild:
            await interaction.followup.send(
                "This must be used in a server.", ephemeral=True
            )
            return

        role = parse_role_from_text(msg.content, interaction.guild)
        if role is None:
            await interaction.followup.send(
                "Could not find that role. Make sure it's a valid mention, ID, or name.",
                ephemeral=True
            )
            return

        cfg = get_config(interaction.guild.id)
        cfg.rules_role_id = role.id
        update_config(interaction.guild.id, cfg)

        await interaction.followup.send(
            f"Rules role set to {role.mention}.", ephemeral=True
        )


class RoleMenuSetupView(View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="Add Role Option", style=discord.ButtonStyle.primary)
    async def add_option(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RoleMenuOptionModal(self.guild_id))

    @discord.ui.button(label="Post Role Menu Here", style=discord.ButtonStyle.secondary)
    async def post_menu(self, interaction: discord.Interaction, button: Button):
        cfg = get_config(self.guild_id)

        if not cfg.role_menu_options:
            await interaction.response.send_message("No role options configured.", ephemeral=True)
            return

        cfg.role_menu_channel = interaction.channel.id

        embed = discord.Embed(
            title="Role Selection",
            description="Choose your roles below.",
            color=0x57F287,
        )
        view = RoleMenuView(self.guild_id)
        msg = await interaction.channel.send(embed=embed, view=view)

        cfg.role_menu_message_id = msg.id
        update_config(self.guild_id, cfg)

        await interaction.response.send_message("Role menu posted.", ephemeral=True)


# -------------------- PREFIX COMMAND COG --------------------

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="onboarding_setup")
    @commands.has_permissions(administrator=True)
    async def onboarding_setup(self, ctx: commands.Context):
        """Setup onboarding for the server."""
        embed = discord.Embed(
            title="Onboarding Setup",
            description="Use the buttons below to configure onboarding.",
            color=0x5865F2,
        )
        await ctx.send(
            embed=embed,
            view=OnboardingSetupView(ctx.guild.id)
        )

    @commands.command(name="onboarding_role_menu")
    @commands.has_permissions(administrator=True)
    async def onboarding_role_menu(self, ctx: commands.Context):
        """Setup role menu for the server."""
        embed = discord.Embed(
            title="Role Menu Setup",
            description="Add role options and post the menu.",
            color=0x57F287,
        )
        await ctx.send(
            embed=embed,
            view=RoleMenuSetupView(ctx.guild.id)
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        cfg = get_config(member.guild.id)
        if not cfg.welcome_channel:
            return

        channel = member.guild.get_channel(cfg.welcome_channel)
        if not channel:
            return

        embed = build_welcome_embed(cfg, member)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            cfg = get_config(guild.id)

            if cfg.rules_channel and cfg.rules_message_id:
                self.bot.add_view(RulesAcknowledgeView(guild.id))

            if cfg.role_menu_channel and cfg.role_menu_message_id:
                self.bot.add_view(RoleMenuView(guild.id))


async def setup(bot):
    await bot.add_cog(Onboarding(bot))