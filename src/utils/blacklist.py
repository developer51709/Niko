"""
Blacklist helpers — message-level and interaction-level checks.
Both return True / False (blocked or not).
"""
import discord
from config.emojis import get_emoji
from config.links import WEBSITE
from utils.blacklist_manager import BlacklistManager
from utils.i18n import make_flat_msg
from utils.locales import load_locales

BLACKLIST_APPEAL_URL = f"{WEBSITE}/appeals/blacklist"

MESSAGES = load_locales("utils.notices", "blacklist")
msg = make_flat_msg(MESSAGES, {"danger": get_emoji("danger")})


def _notice_view(source, *, guild_scope: bool, reason: str | None) -> discord.ui.LayoutView:
    """The blacklist card, in the language of the guild (or the user)."""
    key = "guild_body" if guild_scope else "user_body"
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=msg(source, "title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(
            source, key,
            reason=reason or msg(source, "no_reason"),
            url=BLACKLIST_APPEAL_URL,
        )),
        accent_colour=discord.Color.red(),
    ))
    return view


async def check_message_blacklist(msg_obj: discord.Message) -> bool:
    """
    Returns True (and notifies the channel) if the message author or their
    guild is blacklisted.  Call this before processing any command.
    """
    bm = BlacklistManager()
    await bm._ensure_loaded()

    user_entry = bm.get_user_entry(msg_obj.author.id)
    if user_entry:
        await msg_obj.channel.send(view=_notice_view(
            msg_obj.guild or msg_obj.author,
            guild_scope=False,
            reason=user_entry.get("reason"),
        ))
        return True

    if msg_obj.guild:
        guild_entry = bm.get_guild_entry(msg_obj.guild.id)
        if guild_entry:
            await msg_obj.channel.send(view=_notice_view(
                msg_obj.guild,
                guild_scope=True,
                reason=guild_entry.get("reason"),
            ))
            return True

    return False


async def check_interaction_blacklist(interaction: discord.Interaction) -> bool:
    """
    Returns False (and sends an ephemeral notice) if the user or guild is
    blacklisted.  Attach to bot.tree.interaction_check.
    """
    bm = BlacklistManager()
    # Slash interactions can arrive before any command has touched the
    # manager. Load the shared database cache before checking either scope.
    await bm._ensure_loaded()

    user_entry = bm.get_user_entry(interaction.user.id)
    if user_entry:
        view = _notice_view(
            interaction.guild or interaction.user,
            guild_scope=False,
            reason=user_entry.get("reason"),
        )
        try:
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception:
            pass
        return False

    if interaction.guild:
        guild_entry = bm.get_guild_entry(interaction.guild.id)
        if guild_entry:
            view = _notice_view(
                interaction.guild,
                guild_scope=True,
                reason=guild_entry.get("reason"),
            )
            try:
                await interaction.response.send_message(view=view, ephemeral=True)
            except Exception:
                pass
            return False

    return True
