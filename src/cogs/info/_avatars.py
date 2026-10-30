"""Info — the persistent avatar / banner buttons and the panels that carry them.

Every button encodes the target's user id in its custom id, so a panel posted
before a restart still resolves the right person after it.
"""

import discord

from ._messages import msg

# The avatar panel's buttons carry the target's user id in their custom id, so
# they resolve the right person after a restart without any message state.
_AVATAR_SERVER_TEMPLATE = r"avatar:server:(?P<user_id>\d+)"
_AVATAR_USER_TEMPLATE = r"avatar:user:(?P<user_id>\d+)"
_AVATAR_BANNER_TEMPLATE = r"avatar:banner:(?P<user_id>\d+)"


def _avatar_image_view(title: str, image_url: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.MediaGallery(discord.MediaGalleryItem(media=image_url)),
    ))
    return view


async def _avatar_member(interaction: discord.Interaction, user_id: int):
    """Resolve the target as a member, wherever the interaction happens."""
    guild = interaction.guild
    if guild is not None:
        member = guild.get_member(user_id)
        if member is not None:
            return member
        try:
            return await guild.fetch_member(user_id)
        except discord.HTTPException:
            return None
    # DMs have no guild of their own, so fall back to a cached server avatar.
    fallback = None
    for shared in interaction.client.guilds:
        member = shared.get_member(user_id)
        if member is None:
            continue
        if member.guild_avatar:
            return member
        fallback = fallback or member
    return fallback


class _ServerAvatarButton(discord.ui.DynamicItem[discord.ui.Button], template=_AVATAR_SERVER_TEMPLATE):
    def __init__(self, user_id: int, ctx=None):
        super().__init__(discord.ui.Button(
            label=msg(ctx, "avatar_server_button"),
            style=discord.ButtonStyle.success,
            custom_id=f"avatar:server:{int(user_id)}",
        ))
        self.user_id = int(user_id)

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(int(match["user_id"]), interaction)

    async def callback(self, interaction: discord.Interaction):
        # Acknowledge before anything else: resolving the member and the user is
        # a Discord round trip, and the panel must not greet a slow one with
        # "This interaction failed".
        await interaction.response.defer(ephemeral=True)
        member = await _avatar_member(interaction, self.user_id)
        if member is None:
            return await interaction.followup.send(
                msg(interaction, "avatar_member_gone"), ephemeral=True
            )
        if not member.guild_avatar:
            return await interaction.followup.send(
                msg(interaction, "avatar_no_server_avatar"), ephemeral=True
            )
        await interaction.followup.send(
            view=_avatar_image_view(
                msg(interaction, "avatar_server_button"), member.guild_avatar.url),
            ephemeral=True,
        )


class _UserAvatarButton(discord.ui.DynamicItem[discord.ui.Button], template=_AVATAR_USER_TEMPLATE):
    def __init__(self, user_id: int, ctx=None):
        super().__init__(discord.ui.Button(
            label=msg(ctx, "avatar_user_button"),
            style=discord.ButtonStyle.secondary,
            custom_id=f"avatar:user:{int(user_id)}",
        ))
        self.user_id = int(user_id)

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(int(match["user_id"]), interaction)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.client.get_user(self.user_id)
        if user is None:
            try:
                user = await interaction.client.fetch_user(self.user_id)
            except discord.HTTPException:
                user = None
        if user is None:
            return await interaction.followup.send(
                msg(interaction, "avatar_user_gone"), ephemeral=True
            )
        # display_avatar is never empty, so a user without an uploaded picture
        # still gets the default avatar Discord draws for them.
        await interaction.followup.send(
            view=_avatar_image_view(
                msg(interaction, "avatar_user_button"), user.display_avatar.url),
            ephemeral=True,
        )


class _UserBannerButton(discord.ui.DynamicItem[discord.ui.Button], template=_AVATAR_BANNER_TEMPLATE):
    def __init__(self, user_id: int, style: discord.ButtonStyle = discord.ButtonStyle.success,
                 ctx=None):
        # The /avatar panel posts its controls green and keeps the default; the
        # userinfo card passes the secondary style. The style only matters when
        # the panel is sent: an item rebuilt from a custom id handles the click
        # on a message that already carries the colours it was posted with.
        super().__init__(discord.ui.Button(
            label=msg(ctx, "avatar_banner_button"),
            style=style,
            custom_id=f"avatar:banner:{int(user_id)}",
        ))
        self.user_id = int(user_id)

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item, match, /):
        return cls(int(match["user_id"]), ctx=interaction)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.client.get_user(self.user_id)
        if user is None:
            try:
                user = await interaction.client.fetch_user(self.user_id)
            except discord.HTTPException:
                user = None
        if user is None:
            return await interaction.followup.send(
                msg(interaction, "avatar_user_gone"), ephemeral=True
            )
        if not user.banner:
            return await interaction.followup.send(
                msg(interaction, "avatar_no_banner"), ephemeral=True
            )
        await interaction.followup.send(
            view=_avatar_image_view(
                msg(interaction, "avatar_banner_button"), user.banner.url),
            ephemeral=True,
        )


class AvatarButtons(discord.ui.ActionRow):
    """Avatar panel controls, keyed to the user the panel is showing."""

    def __init__(self, user_id: int, ctx=None):
        super().__init__()
        self.user_id = int(user_id)
        self.add_item(_ServerAvatarButton(self.user_id, ctx))
        self.add_item(_UserBannerButton(self.user_id, ctx=ctx))


class UserInfoButtons(discord.ui.ActionRow):
    """Userinfo card controls: the profile picture and the banner of the user
    the card is showing, keyed to them so they survive a restart."""

    def __init__(self, user_id: int, ctx=None):
        super().__init__()
        self.user_id = int(user_id)
        self.add_item(_UserAvatarButton(self.user_id, ctx))
        self.add_item(_UserBannerButton(
            self.user_id, style=discord.ButtonStyle.secondary, ctx=ctx))


def register_avatar_persistent_views(bot) -> None:
    """Register every avatar custom-id pattern so the buttons keep responding
    after a restart for panels posted before it."""
    registry = discord.ui.LayoutView(timeout=None)
    registry.add_item(discord.ui.Container(discord.ui.ActionRow(
        _ServerAvatarButton(0),
        _UserAvatarButton(0),
        _UserBannerButton(0),
    )))
    bot.add_view(registry)
