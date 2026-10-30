"""Info — shared message catalogue and the card builders every info command uses."""

import discord

from utils.i18n import make_flat_msg
from utils.locales import load_locales

MESSAGES = load_locales("cogs.info", "messages")

msg = make_flat_msg(MESSAGES)


# ===================================================
#  SHARED CARD HELPERS
# ===================================================

# The permissions worth naming on the user and role cards, in the order they
# read best. Anyone without them gets no permissions line at all, so an
# ordinary member or role does not carry a row of "none".
_KEY_PERMISSIONS = (
    "administrator",
    "manage_guild",
    "manage_roles",
    "manage_channels",
    "kick_members",
    "ban_members",
    "moderate_members",
    "manage_messages",
    "mention_everyone",
)


def key_permission_names(permissions) -> list[str]:
    """The notable permission names held by a member's or a role's permissions.

    Administrator implies every other permission, so it is the only name
    returned when it is set; otherwise the names come in display order.
    """
    if getattr(permissions, "administrator", False):
        return ["Administrator"]
    return [
        name.replace("_", " ").title()
        for name in _KEY_PERMISSIONS
        if getattr(permissions, name, False)
    ]


def cv2_text(text, thumbnail_url=None):
    """Build a LayoutView with a container. Optionally include a thumbnail accessory."""
    view = discord.ui.LayoutView()
    if thumbnail_url:
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=text),
                accessory=discord.ui.Thumbnail(thumbnail_url)
            )
        )
    else:
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=text)
        )
    view.add_item(container)
    return view


def _divider() -> discord.ui.Separator:
    """The thin rule the info cards put between their blocks."""
    return discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)


def cv2_image(text, image_url):
    """Build a LayoutView with text container + MediaGallery image."""
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(
            content=text
        )
    )
    if image_url:
        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(media=image_url)
        ))
    view.add_item(container)
    return view
