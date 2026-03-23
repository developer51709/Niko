import discord
from utils.onboarding_config import load_config, save_config, OnboardingConfig


def get_config(guild_id: int) -> OnboardingConfig:
    return load_config(guild_id)


def update_config(guild_id: int, cfg: OnboardingConfig):
    save_config(guild_id, cfg)


def build_welcome_view(cfg: OnboardingConfig, member: discord.Member | None = None) -> discord.ui.LayoutView:
    desc = cfg.welcome_description or "Welcome to the server!"
    if member:
        desc = desc.replace("{user}", member.mention).replace("{name}", member.name)

    title = cfg.welcome_title or "Welcome!"
    color = discord.Colour(cfg.welcome_color) if cfg.welcome_color else discord.Colour(0x5865F2)

    if cfg.welcome_image and member:
        section = discord.ui.Section(
            discord.ui.TextDisplay(content=f"### {title}"),
            discord.ui.TextDisplay(content=desc),
            accessory=discord.ui.Thumbnail(cfg.welcome_image)
        )
    elif member:
        section = discord.ui.Section(
            discord.ui.TextDisplay(content=f"### {title}"),
            discord.ui.TextDisplay(content=desc),
            accessory=discord.ui.Thumbnail(member.display_avatar.url)
        )
    else:
        section = discord.ui.Section(
            discord.ui.TextDisplay(content=f"### {title}"),
            discord.ui.TextDisplay(content=desc),
        )

    container = discord.ui.Container(
        section,
        accent_colour=color
    )
    view = discord.ui.LayoutView()
    view.add_item(container)
    return view


def build_rules_view(cfg: OnboardingConfig) -> discord.ui.LayoutView:
    rules_text = cfg.rules_text or "No rules have been set yet."
    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### Server Rules"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=rules_text),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="-# Click the button below to acknowledge the rules."),
        accent_colour=discord.Colour(0xED4245)
    )
    view = discord.ui.LayoutView()
    view.add_item(container)
    return view
