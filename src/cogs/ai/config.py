# this cog will allow server admins to configure the AI settings for their server or even disable the AI features.

import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils import logging
from utils.ai.config import (
    MIN_AI_NAME_LENGTH,
    load_config,
    preload_all,
    save_config,
)
from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "config")
msg = make_flat_msg(MESSAGES, {
    "ai": get_emoji("ai"),
    "danger": get_emoji("danger"),
    "tick": get_emoji("tick"),
    "cross": get_emoji("cross"),
})


def _error_view(ctx, key: str = "error_permission") -> discord.ui.LayoutView:
    """The yellow card every manage_guild gate answers with."""
    return _card_view(ctx, "error_heading", key, discord.Color.yellow())


def _card_view(ctx, heading_key: str, body_key: str, colour, **kwargs) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, heading_key)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, body_key, **kwargs)),
        accent_colour=colour,
    ))
    return view


# exeriments view
# this is where users can learn about the experimental features and toggle them on or off
class ExperimentsView(discord.ui.LayoutView):
    def __init__(self, bot: commands.Bot, ctx, config: dict):
        self.bot = bot
        self.ctx = ctx
        super().__init__()
        self.container = discord.ui.Container()
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "experiments_heading")))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "experiments_note")))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "ai_actions_title")))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "ai_actions_description")))
        self.container.add_item(discord.ui.ActionRow(
            ExperimentToggle(self.bot, "ai_actions", ctx, config),
            ExperimentAboutButton(self.bot, "ai_actions", ctx)
        ))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "better_context_title")))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "better_context_description")))
        self.container.add_item(discord.ui.ActionRow(
            ExperimentToggle(self.bot, "better_context", ctx, config),
            ExperimentAboutButton(self.bot, "better_context", ctx)
        ))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "multimodal_title")))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "multimodal_description")))
        self.container.add_item(discord.ui.ActionRow(
            ExperimentToggle(self.bot, "multimodal", ctx, config),
            ExperimentAboutButton(self.bot, "multimodal", ctx)
        ))
        self.add_item(self.container)

    @classmethod
    async def create(cls, bot: commands.Bot, ctx) -> "ExperimentsView":
        return cls(bot, ctx, await load_config(ctx.guild.id, fresh=True))

class ExperimentAboutButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot, experiment: str, ctx):
        self.bot = bot
        self.experiment = experiment
        self.ctx = ctx
        super().__init__(label=msg(ctx, "button_about"), style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        ctx = interaction
        if self.experiment == "ai_actions":
            view = AIActionsExperimentAbout(self.bot, ctx)
        elif self.experiment == "better_context":
            view = BetterContextExperimentAbout(self.bot, ctx)
        elif self.experiment == "multimodal":
            view = MultimodalExperimentAbout(self.bot, ctx)
        else:
            view = _card_view(
                ctx, "unknown_experiment_heading", "unknown_experiment_body",
                discord.Color.yellow(),
            )
        await interaction.response.send_message(view=view, ephemeral=True)

class ExperimentToggle(discord.ui.Button):
    def __init__(self, bot: commands.Bot, experiment: str, ctx, config: dict):
        self.bot = bot
        self.experiment = experiment
        self.ctx = ctx
        if str(config.get(f"{experiment}_experiment")) == "True":
            emoji = get_emoji("tick")
            label = msg(ctx, "toggle_enabled")
            style = discord.ButtonStyle.green
        else:
            emoji = get_emoji("cross")
            label = msg(ctx, "toggle_disabled")
            style = discord.ButtonStyle.red
        super().__init__(label=label, style=style, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                view=_error_view(interaction), ephemeral=True
            )
        guild_id = interaction.guild.id
        config = await load_config(guild_id, fresh=True)
        enabled = str(config.get(f"{self.experiment}_experiment")) == "True"
        try:
            await save_config(
                guild_id, f"{self.experiment}_experiment", "False" if enabled else "True"
            )
        except Exception as error:  # noqa: BLE001
            return await interaction.response.send_message(
                msg(interaction, "save_experiment_error", error=error), ephemeral=True
            )
        if enabled:
            self.emoji = get_emoji("cross")
            self.label = msg(interaction, "toggle_disabled")
            self.style = discord.ButtonStyle.red
        else:
            self.emoji = get_emoji("tick")
            self.label = msg(interaction, "toggle_enabled")
            self.style = discord.ButtonStyle.green
        await interaction.response.edit_message(view=self.view)

class AIActionsExperimentAbout(discord.ui.LayoutView):
    def __init__(self, bot: commands.Bot, ctx):
        super().__init__()
        self.bot = bot
        self.container = discord.ui.Container()
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "actions_heading")))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "actions_intro")))
        self.container.add_item(discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "actions_capabilities")))
        self.container.add_item(discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "actions_how")))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "actions_permissions")))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "actions_note")))
        self.add_item(self.container)

class BetterContextExperimentAbout(discord.ui.LayoutView):
    def __init__(self, bot: commands.Bot, ctx):
        super().__init__()
        self.bot = bot
        self.container = discord.ui.Container()
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "context_heading")))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "context_intro")))
        self.container.add_item(discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "context_adds")))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "context_note")))
        self.add_item(self.container)


class MultimodalExperimentAbout(discord.ui.LayoutView):
    def __init__(self, bot: commands.Bot, ctx):
        super().__init__()
        self.bot = bot
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "multimodal_heading")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(ctx, "multimodal_body")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(ctx, "multimodal_footnote")),
        )
        self.add_item(container)


class ExperimentsButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot, ctx):
        super().__init__(
            label=msg(ctx, "button_experiments"),
            style=discord.ButtonStyle.secondary
        )
        self.bot = bot
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        # require manage guild perm
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                view=_error_view(interaction), ephemeral=True
            )
        view = await ExperimentsView.create(self.bot, interaction)
        await interaction.response.send_message(view=view, ephemeral=True)


class BotPersonalitySelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, ctx):
        super().__init__(
            placeholder=msg(ctx, "personality_placeholder"),
            options=[
                discord.SelectOption(label=msg(ctx, "personality_normal"), value="normal"),
                discord.SelectOption(label=msg(ctx, "personality_cafe"), value="cafe"),
            ],
        )
        self.bot = bot
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        personality = self.values[0]
        try:
            await save_config(interaction.guild.id, "personality", personality)
        except Exception as error:  # noqa: BLE001
            return await interaction.response.send_message(
                msg(interaction, "personality_save_error", error=error), ephemeral=True
            )
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "personality_heading")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(
                interaction, "personality_set",
                personality=msg(interaction, f"personality_{personality}"),
            )),
            accent_colour=discord.Color.green(),
        )
        view.add_item(container)
        await interaction.response.edit_message(view=view)


class BotPersonalityButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot, ctx):
        super().__init__(label=msg(ctx, "button_personality"), style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                msg(interaction, "error_permission"), ephemeral=True
            )
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "personality_heading")),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(interaction, "personality_prompt")),
            discord.ui.ActionRow(BotPersonalitySelect(self.bot, interaction)),
            discord.ui.TextDisplay(content=msg(interaction, "personality_note")),
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


class AINameModal(discord.ui.Modal):
    def __init__(self, ctx):
        super().__init__(title=msg(ctx, "name_modal_title"))
        self.ctx = ctx
        self.name_input = discord.ui.TextInput(
            label=msg(ctx, "name_label"),
            placeholder=msg(ctx, "name_placeholder"),
            # Short names would make the AI answer nearly every message.
            min_length=MIN_AI_NAME_LENGTH,
            max_length=32,
            required=True,
        )
        self.add_item(self.name_input)

    async def on_submit(self, interaction: discord.Interaction):
        value = str(self.name_input).strip()
        if len(value) < MIN_AI_NAME_LENGTH:
            return await interaction.response.send_message(
                msg(interaction, "name_too_short", min=MIN_AI_NAME_LENGTH),
                ephemeral=True,
            )
        try:
            await save_config(interaction.guild.id, "ai_name", value)
        except Exception as error:  # noqa: BLE001
            return await interaction.response.send_message(
                msg(interaction, "name_save_error", error=error), ephemeral=True
            )
        await interaction.response.send_message(
            msg(interaction, "name_saved", name=value), ephemeral=True
        )


class AINameButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot, ctx):
        super().__init__(label=msg(ctx, "button_name"), style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                msg(interaction, "error_permission"), ephemeral=True
            )
        await interaction.response.send_modal(AINameModal(interaction))


class ToggleAIButton(discord.ui.Button):
    def __init__(self, bot: commands.Bot, ctx):
        super().__init__(
            label=msg(ctx, "button_toggle"),
            style=discord.ButtonStyle.secondary
        )
        self.bot = bot
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        # require manage guild perm
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                view=_error_view(interaction), ephemeral=True
            )
        guild_id = interaction.guild.id
        config = await load_config(guild_id, fresh=True)
        enabled = str(config.get("enabled")) == "True"
        try:
            await save_config(guild_id, "enabled", "False" if enabled else "True")
        except Exception as error:  # noqa: BLE001
            return await interaction.response.send_message(
                msg(interaction, "toggle_save_error", error=error), ephemeral=True
            )
        return await interaction.response.send_message(
            msg(interaction, "ai_disabled" if enabled else "ai_enabled"),
            ephemeral=True,
        )


class MainPanelButtons(discord.ui.ActionRow):
    def __init__(self, bot: commands.Bot, ctx):
        super().__init__()
        self.bot = bot
        self.add_item(ToggleAIButton(self.bot, ctx))
        self.add_item(AINameButton(self.bot, ctx))
        self.add_item(BotPersonalityButton(self.bot, ctx))
        self.add_item(ExperimentsButton(self.bot, ctx))


class AIConfigPanel(discord.ui.LayoutView):
    def __init__(self, ctx, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.container = discord.ui.Container()
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "panel_heading")))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(discord.ui.TextDisplay(content=msg(ctx, "panel_description")))
        self.container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        self.container.add_item(MainPanelButtons(self.bot, ctx))
        self.add_item(self.container)


class AIConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Warm the config cache for every guild, so the sync personality lookup
        # used by roleplay flavour text and the panel buttons is accurate.
        # A cache warm-up must never be able to fail the whole cog: that took
        # every AI command offline over a single unreadable guild row.
        try:
            await preload_all()
        except Exception as error:  # noqa: BLE001
            logging.warning("ai_config", f"Could not warm the AI config cache: {error}")

    @commands.hybrid_command(
        name="ai-config",
        description=CMDS.text("ai-config.description"),
        help=CMDS.help("ai-config"),
    )
    @commands.has_permissions(manage_guild=True)
    async def ai_config(self, ctx: commands.Context):
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=False)
        await load_config(ctx.guild.id, fresh=True)
        view = AIConfigPanel(ctx, self.bot)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AIConfig(bot))
