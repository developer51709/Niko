import discord
from utils.onboarding_config import load_config, save_config, OnboardingConfig


def get_config(guild_id: int) -> OnboardingConfig:
    return load_config(guild_id)


def update_config(guild_id: int, cfg: OnboardingConfig):
    save_config(guild_id, cfg)


def build_welcome_embed(cfg: OnboardingConfig, member: discord.Member | None = None) -> discord.Embed:
    desc = cfg.welcome_description or "Welcome to the server!"
    if member:
        desc = desc.replace("{user}", member.mention).replace("{name}", member.name)

    embed = discord.Embed(
        title=cfg.welcome_title or "Welcome!",
        description=desc,
        color=cfg.welcome_color or 0x5865F2
    )
    if cfg.welcome_image:
        embed.set_image(url=cfg.welcome_image)
    return embed


def build_rules_embed(cfg: OnboardingConfig) -> discord.Embed:
    embed = discord.Embed(
        title="Server Rules",
        description=cfg.rules_text or "No rules have been set yet.",
        color=0xED4245
    )
    embed.set_footer(text="Click the button below to acknowledge the rules.")
    return embed