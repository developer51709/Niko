import discord
from utils.i18n import make_flat_msg
from utils.locales import load_locales
from utils.onboarding.config import load_config, save_config, OnboardingConfig

MESSAGES = load_locales(__package__, "messages")
msg = make_flat_msg(MESSAGES)


async def get_config(guild_id: int) -> OnboardingConfig:
    """Async replacement for the old synchronous JSON-backed get_config."""
    return await load_config(guild_id)


async def update_config(guild_id: int, cfg: OnboardingConfig):
    """Async replacement for the old synchronous save_config wrapper."""
    await save_config(guild_id, cfg)


def fill_greeting_placeholders(
    text: str,
    member: discord.Member | None = None,
    guild: discord.Guild | None = None,
) -> str:
    """Replace the documented ``{user}``, ``{name}`` and ``{guild}`` tokens.

    Welcome and goodbye messages share this so an admin only has to learn one
    set of placeholders.
    """
    if member is not None:
        text = text.replace("{user}", member.mention).replace("{name}", member.name)
    guild = guild or getattr(member, "guild", None)
    if guild is not None:
        text = text.replace("{guild}", guild.name)
    return text


def _build_greeting_view(
    title: str,
    description: str,
    color: int | None,
    image: str | None,
) -> discord.ui.LayoutView:
    """The shared card shape used by both the welcome and goodbye messages."""
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(
            content=f"### {title}"
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=description
        )
    )
    if image:
        container.add_item(
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
        )
        container.add_item(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=image
                )
            )
        )
    if color:
        container.accent_colour = discord.Colour(color)

    view.add_item(container)
    return view


def build_welcome_view(
    cfg: OnboardingConfig,
    member: discord.Member | None = None,
    guild: discord.Guild | None = None,
) -> discord.ui.LayoutView:
    source = guild or member
    desc = fill_greeting_placeholders(
        cfg.welcome_description or msg(source, "welcome_default_body"), member, guild
    )
    return _build_greeting_view(
        cfg.welcome_title or msg(source, "welcome_default_title"),
        desc,
        cfg.welcome_color,
        cfg.welcome_image,
    )


def build_goodbye_view(
    cfg: OnboardingConfig,
    member: discord.Member | None = None,
    guild: discord.Guild | None = None,
) -> discord.ui.LayoutView:
    """The leave message, styled with the guild's own goodbye settings.

    Only sent when a goodbye channel is configured, so servers that have not
    opted in keep posting nothing when a member leaves.
    """
    source = guild or member
    desc = fill_greeting_placeholders(
        cfg.goodbye_description or msg(source, "goodbye_default_body"), member, guild
    )
    return _build_greeting_view(
        cfg.goodbye_title or msg(source, "goodbye_default_title"),
        desc,
        cfg.goodbye_color,
        cfg.goodbye_image,
    )


def build_rules_view(
    cfg: OnboardingConfig,
    guild: discord.Guild | None = None,
) -> discord.ui.LayoutView:
    rules_text = cfg.rules_text or msg(guild, "rules_default")
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=msg(guild, "rules_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=rules_text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(guild, "rules_hint")),
        accent_colour=discord.Colour(0xED4245)
    )
    view = discord.ui.LayoutView()
    view.add_item(container)
    return view
