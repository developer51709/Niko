import asyncio
from typing import Union

import discord
from discord import ui
from discord.ext import commands

from utils import checks
from utils import converters
from utils import decorators
from utils import logging
import utils.emojis as E
from config.emojis import get_emoji
from config import links
from utils.i18n import get_lang
from .messages import msg, text

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

COLOR_DEFAULT = 0xFFFFFF
COLOR_SUCCESS = 0x00CC66
COLOR_ERROR = 0xFF0000

SUPPORT_URL = links.SUPPORT_SERVER
BOT_NAME = "Niko"

SETUP_CATEGORY_NAME = "Niko | VoiceMaster"
SETUP_HUB_NAME = "Join to Create"

def make_container(text: str, accent: int = COLOR_DEFAULT) -> ui.LayoutView:
    view = ui.LayoutView(timeout=None)
    container = ui.Container(accent_color=accent)
    container.add_item(ui.TextDisplay(text))
    view.add_item(container)
    return view


class DisconnectMemberSelect(discord.ui.Select):
    def __init__(self, members: list, lang: str = "en"):
        options = [
            discord.SelectOption(
                label=member.display_name,
                description=text(lang, "disconnect_option", user=member.display_name),
                value=str(member.id)
            )
            for member in members[:25]
        ]
        super().__init__(
            placeholder=text(lang, "disconnect_placeholder"),
            min_values=1,
            max_values=min(len(options), 25),
            options=options
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        try:
            disconnected, failed = [], []
            for member_id in self.values:
                member = interaction.guild.get_member(int(member_id))
                if member and member.voice and member.voice.channel:
                    try:
                        await member.move_to(None)
                        disconnected.append(member.display_name)
                    except Exception:
                        failed.append(member.display_name)

            parts = []
            if disconnected:
                parts.append(
                    f"{get_emoji('tick')} "
                    f"{text(self.lang, 'disconnect_done', users=', '.join(disconnected))}"
                )
            if failed:
                parts.append(
                    f"{get_emoji('cross')} "
                    f"{text(self.lang, 'disconnect_failed', users=', '.join(failed))}"
                )

            body = "\n".join(parts) or (
                f"{get_emoji('cross')} {text(self.lang, 'disconnect_none')}"
            )
            await interaction.response.edit_message(
                content=None,
                view=make_container(f"-# {body}")
            )
        except Exception as e:
            logging.error("VoiceMaster", f"Disconnect callback error: {e}")
            await interaction.response.edit_message(
                content=None,
                view=make_container(
                    f"-# {get_emoji('cross')} {text(self.lang, 'error_generic')}",
                    accent=COLOR_ERROR,
                )
            )


class DisconnectMemberView(discord.ui.View):
    def __init__(self, members: list, owner: discord.Member, lang: str = "en"):
        super().__init__(timeout=60)
        self.add_item(DisconnectMemberSelect(members, lang))


def _interface_commands(lang: str) -> str:
    """The legend under the panel title.

    Command names stay as written — they are literal commands — while the
    description beside each one follows the guild's language.
    """
    rows = (
        ("lock", "Lock", "interface_lock"),
        ("unlock", "Unlock", "interface_unlock"),
        ("hide", "Hide", "interface_hide"),
        ("unhide", "Reveal", "interface_reveal"),
        ("owner_icon", "Claim", "interface_claim"),
        ("disconnect", "Disconnect", "interface_disconnect"),
        ("question", "View", "interface_view"),
        ("plus", "Increase", "interface_increase"),
        ("minus", "Decrease", "interface_decrease"),
    )
    return "\n".join(
        f"{get_emoji(emoji)} — [`{label}`]({SUPPORT_URL}) {text(lang, key)}"
        for emoji, label, key in rows
    )


async def success(ctx: commands.Context, message: str):
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(
            content=f"{get_emoji('tick')} {message}"
        ),
        accent_colour=discord.Color.green()
    )
    view.add_item(container)
    await ctx.reply(view=view)

async def fail(ctx: commands.Context, message: str):
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(
            content=f"{get_emoji('cross')} {message}"
        ),
        accent_colour=discord.Color.red()
    )
    view.add_item(container)
    await ctx.reply(view=view)


class VoiceMasterInterface(discord.ui.LayoutView):
    def __init__(self, lang: str = "en"):
        super().__init__(timeout=None)

        btn_lock       = discord.ui.Button(emoji=get_emoji('lock'),       style=discord.ButtonStyle.gray, custom_id="lock")
        btn_unlock     = discord.ui.Button(emoji=get_emoji('unlock'),     style=discord.ButtonStyle.gray, custom_id="unlock")
        btn_ghost      = discord.ui.Button(emoji=get_emoji('hide'),       style=discord.ButtonStyle.gray, custom_id="vm_ghost")
        btn_reveal     = discord.ui.Button(emoji=get_emoji('unhide'),     style=discord.ButtonStyle.gray, custom_id="vm_reveal")
        btn_claim      = discord.ui.Button(emoji=get_emoji('owner_icon'),    style=discord.ButtonStyle.gray, custom_id="vm_claim")

        btn_disconnect = discord.ui.Button(emoji=get_emoji('disconnect'),    style=discord.ButtonStyle.gray, custom_id="vm_disconnect")
        btn_info       = discord.ui.Button(emoji=get_emoji('question'), style=discord.ButtonStyle.gray, custom_id="vm_info")
        btn_increase   = discord.ui.Button(emoji=get_emoji('plus'),     style=discord.ButtonStyle.gray, custom_id="vm_increase")
        btn_decrease   = discord.ui.Button(emoji=get_emoji('minus'),    style=discord.ButtonStyle.gray, custom_id="vm_decrease")

        btn_lock.callback       = self._on_lock
        btn_unlock.callback     = self._on_unlock
        btn_ghost.callback      = self._on_ghost
        btn_reveal.callback     = self._on_reveal
        btn_claim.callback      = self._on_claim
        btn_disconnect.callback = self._on_disconnect
        btn_info.callback       = self._on_info
        btn_increase.callback   = self._on_increase
        btn_decrease.callback   = self._on_decrease

        container = ui.Container()
        container.add_item(ui.TextDisplay(f"## {text(lang, 'interface_title')}"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(_interface_commands(lang)))
        container.add_item(ui.Separator())
        container.add_item(ui.ActionRow(btn_lock, btn_unlock, btn_ghost, btn_reveal, btn_claim))
        container.add_item(ui.ActionRow(btn_disconnect, btn_info, btn_increase, btn_decrease))
        self.add_item(container)

    async def _on_lock(self, interaction: discord.Interaction):
        await self._dispatch(interaction, "lock")

    async def _on_unlock(self, interaction: discord.Interaction):
        await self._dispatch(interaction, "unlock")

    async def _on_ghost(self, interaction: discord.Interaction):
        await self._dispatch(interaction, "ghost")

    async def _on_reveal(self, interaction: discord.Interaction):
        await self._dispatch(interaction, "unghost")

    async def _on_claim(self, interaction: discord.Interaction):
        await self._dispatch(interaction, "claim")

    async def _on_info(self, interaction: discord.Interaction):
        await self._dispatch(interaction, "info")

    async def _on_increase(self, interaction: discord.Interaction):
        await self._dispatch(interaction, "increase_limit")

    async def _on_decrease(self, interaction: discord.Interaction):
        await self._dispatch(interaction, "decrease_limit")

    async def _on_disconnect(self, interaction: discord.Interaction):
        cog, channel, err = await self._resolve(interaction, owner_required=True)
        if err:
            return
        members = [m for m in channel.members if m != interaction.user and not m.bot]
        if not members:
            await interaction.response.send_message(
                view=make_container(
                    f"-# {get_emoji('cross')} "
                    f"{msg(interaction, 'interface_no_members_to_disconnect')}",
                    accent=COLOR_ERROR,
                ),
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            view=DisconnectMemberView(
                members, interaction.user, get_lang(interaction)
            ),
            ephemeral=True
        )

    async def _resolve(self, interaction: discord.Interaction, *, owner_required: bool = True):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                view=make_container(
                    f"-# {get_emoji('cross')} {msg(interaction, 'interface_not_in_voice')}",
                    accent=COLOR_ERROR,
                ),
                ephemeral=True
            )
            return None, None, True

        cog = interaction.client.get_cog("VoiceMaster")
        if not cog:
            await interaction.response.send_message(
                view=make_container(
                    f"-# {get_emoji('cross')} {msg(interaction, 'interface_unavailable')}",
                    accent=COLOR_ERROR,
                ),
                ephemeral=True
            )
            return None, None, True

        channel = interaction.user.voice.channel

        if owner_required and not await cog.is_channel_owner(interaction.user.id, channel.id):
            await interaction.response.send_message(
                view=make_container(
                    f"-# {get_emoji('cross')} {msg(interaction, 'interface_not_owner')}",
                    accent=COLOR_ERROR,
                ),
                ephemeral=True
            )
            return None, None, True

        return cog, channel, False

    async def _dispatch(self, interaction: discord.Interaction, action: str):
        # This panel is seeded in the support server and can be posted in any
        # server with `voicemaster sendinterface`, so it must work everywhere.
        # Ownership is enforced per channel by `is_channel_owner` below.
        owner_required = action not in ("claim", "info")
        cog, channel, err = await self._resolve(interaction, owner_required=owner_required)
        if err:
            return

        try:
            if action == "lock":
                await cog.lock_channel(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(
                        f"-# {get_emoji('lock')} {msg(interaction, 'action_locked')}",
                        accent=COLOR_SUCCESS,
                    ), ephemeral=True
                )
            elif action == "unlock":
                await cog.unlock_channel(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(
                        f"-# {get_emoji('unlock')} {msg(interaction, 'action_unlocked')}",
                        accent=COLOR_SUCCESS,
                    ), ephemeral=True
                )
            elif action == "ghost":
                await cog.ghost_channel(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(
                        f"-# {get_emoji('hide')} {msg(interaction, 'action_hidden')}",
                        accent=COLOR_SUCCESS,
                    ), ephemeral=True
                )
            elif action == "unghost":
                await cog.unghost_channel(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(
                        f"-# {get_emoji('unhide')} {msg(interaction, 'action_revealed')}",
                        accent=COLOR_SUCCESS,
                    ), ephemeral=True
                )
            elif action == "claim":
                if await cog.claim_channel(channel, interaction.user):
                    await interaction.response.send_message(
                        view=make_container(
                            f"-# {get_emoji('owner_icon')} {msg(interaction, 'action_claimed')}",
                            accent=COLOR_SUCCESS,
                        ), ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        view=make_container(
                            f"-# {get_emoji('cross')} {msg(interaction, 'action_claim_failed')}",
                            accent=COLOR_ERROR,
                        ), ephemeral=True
                    )
            elif action == "info":
                await interaction.response.send_message(
                    view=await cog.get_channel_info(channel, interaction), ephemeral=True
                )
            elif action == "increase_limit":
                await cog.increase_limit(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(
                        f"-# {get_emoji('plus')} {msg(interaction, 'action_limit_increased')}",
                        accent=COLOR_SUCCESS,
                    ), ephemeral=True
                )
            elif action == "decrease_limit":
                await cog.decrease_limit(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(
                        f"-# {get_emoji('minus')} {msg(interaction, 'action_limit_decreased')}",
                        accent=COLOR_SUCCESS,
                    ), ephemeral=True
                )
        except Exception as exc:
            logging.error("VoiceMaster", f"Interface action '{action}' error: {exc}")
            await interaction.response.send_message(
                view=make_container(
                    f"-# {get_emoji('cross')} {msg(interaction, 'error_generic')}",
                    accent=COLOR_ERROR,
                ), ephemeral=True
            )


async def _allow_setup_interaction(ctx: commands.Context, interaction: discord.Interaction) -> bool:
    """Only the member who started setup may drive its prompt."""
    if interaction.user.id != ctx.author.id:
        await interaction.response.send_message(
            view=make_container(
                f"-# {get_emoji('cross')} "
                f"{msg(interaction, 'setup_only_author', user=ctx.author.mention)}",
                accent=COLOR_ERROR,
            ),
            ephemeral=True,
        )
        return False
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            view=make_container(
                f"-# {get_emoji('cross')} {msg(interaction, 'setup_needs_manage')}",
                accent=COLOR_ERROR,
            ),
            ephemeral=True,
        )
        return False
    return True


def _setup_success_view(join_channel: discord.VoiceChannel, category, prefix: str,
                        context) -> ui.LayoutView:
    view = ui.LayoutView(timeout=None)
    container = ui.Container(accent_color=COLOR_SUCCESS)
    container.add_item(ui.TextDisplay(
        f"## {get_emoji('tick')} {msg(context, 'setup_success_title')}"
    ))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(msg(
        context,
        "setup_success_body",
        channel=join_channel.mention,
        category=category.name if category else msg(context, "setup_no_category"),
        prefix=prefix,
    )))
    view.add_item(container)
    return view


class VoiceMasterChannelSelect(ui.Select):
    def __init__(self, cog, ctx: commands.Context, channels: list[discord.VoiceChannel]):
        options = [
            discord.SelectOption(
                label=channel.name[:100],
                value=str(channel.id),
                description=(msg(ctx, "channel_select_category", category=channel.category.name)
                             if channel.category else msg(ctx, "setup_no_category"))[:100],
            )
            for channel in channels[:25]
        ]
        super().__init__(
            placeholder=msg(ctx, "channel_select_placeholder"),
            min_values=1,
            max_values=1,
            options=options,
        )
        self.cog = cog
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel = interaction.guild.get_channel(int(self.values[0]))
        if not isinstance(channel, discord.VoiceChannel):
            await interaction.edit_original_response(view=make_container(
                f"-# {get_emoji('cross')} {msg(interaction, 'channel_select_unavailable')}",
                accent=COLOR_ERROR,
            ))
            return
        try:
            await self.cog.configure_setup(interaction.guild, channel, channel.category)
        except Exception as exc:
            logging.error("VoiceMaster", f"Existing-channel setup error: {exc}")
            await interaction.edit_original_response(view=make_container(
                f"-# {get_emoji('cross')} {msg(interaction, 'channel_select_save_failed')}",
                accent=COLOR_ERROR,
            ))
            return
        await interaction.edit_original_response(
            view=_setup_success_view(
                channel, channel.category, self.ctx.prefix, self.ctx
            )
        )


class VoiceMasterChannelSelectView(ui.LayoutView):
    def __init__(self, cog, ctx: commands.Context, channels: list[discord.VoiceChannel]):
        super().__init__(timeout=180)
        self.ctx = ctx
        container = ui.Container(
            ui.TextDisplay(
                f"## {BOT_NAME} | {msg(ctx, 'channel_select_title')}"
            ),
            ui.Separator(),
            ui.TextDisplay(msg(ctx, "channel_select_body", prefix=ctx.prefix)),
            ui.Separator(),
            ui.ActionRow(VoiceMasterChannelSelect(cog, ctx, channels)),
            accent_color=COLOR_DEFAULT,
        )
        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await _allow_setup_interaction(self.ctx, interaction)


class VoiceMasterSetupView(ui.LayoutView):
    """Interactive prompt asking whether to create a hub or use an existing channel."""

    def __init__(self, cog, ctx: commands.Context, current_hub: discord.VoiceChannel | None = None):
        super().__init__(timeout=180)
        self.cog = cog
        self.ctx = ctx

        btn_create = ui.Button(
            label=msg(ctx, "setup_create_channel"),
            style=discord.ButtonStyle.success,
            custom_id="vm_setup_create",
        )
        btn_existing = ui.Button(
            label=msg(ctx, "setup_use_existing"),
            style=discord.ButtonStyle.secondary,
            custom_id="vm_setup_existing",
        )
        btn_create.callback = self._create_new_channel
        btn_existing.callback = self._choose_existing_channel

        body = msg(ctx, "setup_body")
        if current_hub is not None:
            body += "\n\n-# " + msg(ctx, "setup_current_hub", channel=current_hub.mention)

        container = ui.Container(
            ui.TextDisplay(f"## {BOT_NAME} | {msg(ctx, 'setup_title')}"),
            ui.Separator(),
            ui.TextDisplay(body),
            ui.Separator(),
            ui.ActionRow(btn_create, btn_existing),
            accent_color=COLOR_DEFAULT,
        )
        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await _allow_setup_interaction(self.ctx, interaction)

    async def _create_new_channel(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            category = await interaction.guild.create_category(SETUP_CATEGORY_NAME)
            channel = await interaction.guild.create_voice_channel(SETUP_HUB_NAME, category=category)
            await self.cog.configure_setup(interaction.guild, channel, category)
        except Exception as exc:
            logging.error("VoiceMaster", f"Setup error: {exc}")
            await interaction.edit_original_response(view=make_container(
                f"-# {get_emoji('cross')} {msg(interaction, 'setup_failed')}",
                accent=COLOR_ERROR,
            ))
            return
        await interaction.edit_original_response(
            view=_setup_success_view(channel, category, self.ctx.prefix, self.ctx)
        )

    async def _choose_existing_channel(self, interaction: discord.Interaction):
        channels = interaction.guild.voice_channels
        if not channels:
            await interaction.response.send_message(
                view=make_container(
                    f"-# {get_emoji('cross')} {msg(interaction, 'setup_no_voice_channels')}",
                    accent=COLOR_ERROR,
                ),
                ephemeral=True,
            )
            return
        await interaction.response.edit_message(
            view=VoiceMasterChannelSelectView(self.cog, self.ctx, channels)
        )


class VoiceMaster(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(VoiceMasterInterface())
        self._settings_cache: dict = {}

    async def configure_setup(self, guild: discord.Guild, join_channel: discord.VoiceChannel, category) -> None:
        """Save a hub channel (new or pre-existing) as this guild's VoiceMaster setup."""
        category_id = category.id if category else None
        await self.bot.cxn.execute(
            """
            INSERT INTO voicemaster_settings
                (guild_id, join_channel_id, category_id, default_name, default_limit, default_bitrate)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (guild_id)
            DO UPDATE SET
                join_channel_id = $7,
                category_id     = $8
            """,
            guild.id, join_channel.id, category_id, "{user}'s Channel", 0, 64000,
            join_channel.id, category_id
        )
        self._bust_cache(guild.id)

    async def is_channel_owner(self, user_id: int, channel_id: int) -> bool:
        try:
            owner = await self.bot.cxn.fetchval(
                "SELECT owner_id FROM voicemaster_channels WHERE channel_id = $1", channel_id
            )
            return owner == user_id
        except Exception:
            return False

    async def get_guild_settings(self, guild_id: int):
        if guild_id in self._settings_cache:
            return self._settings_cache[guild_id]
        try:
            settings = await self.bot.cxn.fetchrow(
                "SELECT * FROM voicemaster_settings WHERE guild_id = $1", guild_id
            )
            self._settings_cache[guild_id] = settings
            asyncio.create_task(self._expire_cache(guild_id, delay=300))
            return settings
        except Exception:
            return None

    async def _expire_cache(self, guild_id: int, delay: int):
        await asyncio.sleep(delay)
        self._settings_cache.pop(guild_id, None)

    def _bust_cache(self, guild_id: int):
        self._settings_cache.pop(guild_id, None)

    async def _create_temp_channel(self, member: discord.Member, category: discord.CategoryChannel = None):
        try:
            settings = await self.get_guild_settings(member.guild.id)
            if not settings:
                return None

            name    = settings.get('default_name', "{user}'s Channel").replace("{user}", member.display_name)
            limit   = settings.get('default_limit', 0)
            bitrate = settings.get('default_bitrate', 64000)

            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(connect=True),
                member: discord.PermissionOverwrite(
                    manage_channels=True,
                    manage_permissions=True,
                    move_members=True,
                    mute_members=True,
                    deafen_members=True,
                )
            }

            channel = await member.guild.create_voice_channel(
                name=name, category=category,
                user_limit=limit, bitrate=bitrate,
                overwrites=overwrites
            )

            # DB insert first so the channel is tracked even if move_to fails.
            await self.bot.cxn.execute(
                "INSERT INTO voicemaster_channels (channel_id, owner_id, guild_id, created_at) "
                "VALUES ($1, $2, $3, datetime('now'))",
                channel.id, member.id, member.guild.id
            )
            try:
                await member.move_to(channel)
            except Exception:
                logging.warning("VoiceMaster", f"Failed to move member {member.id} to channel {channel.id}")
            return channel
        except Exception as e:
            logging.error("VoiceMaster", f"Create temp channel error: {e}")
            return None

    async def _cleanup_empty_channel(self, channel: discord.VoiceChannel):
        try:
            owner_id = await self.bot.cxn.fetchval(
                "SELECT owner_id FROM voicemaster_channels WHERE channel_id = $1", channel.id
            )
            if owner_id:
                # Delete from DB first so stale records don't linger if channel.delete fails.
                await self.bot.cxn.execute(
                    "DELETE FROM voicemaster_channels WHERE channel_id = $1", channel.id
                )
                try:
                    await channel.delete(reason="VoiceMaster: Empty temporary channel")
                except Exception:
                    logging.warning("VoiceMaster", f"Failed to delete empty channel {channel.id}")
        except Exception as e:
            logging.error("VoiceMaster", f"Cleanup channel {channel.id} error: {e}")

    async def lock_channel(self, channel: discord.VoiceChannel, _: discord.Member):
        await channel.set_permissions(channel.guild.default_role, connect=False)

    async def unlock_channel(self, channel: discord.VoiceChannel, _: discord.Member):
        await channel.set_permissions(channel.guild.default_role, connect=True)

    async def ghost_channel(self, channel: discord.VoiceChannel, _: discord.Member):
        await channel.set_permissions(channel.guild.default_role, view_channel=False)

    async def unghost_channel(self, channel: discord.VoiceChannel, _: discord.Member):
        await channel.set_permissions(channel.guild.default_role, view_channel=True)

    async def claim_channel(self, channel: discord.VoiceChannel, member: discord.Member) -> bool:
        try:
            current_owner_id = await self.bot.cxn.fetchval(
                "SELECT owner_id FROM voicemaster_channels WHERE channel_id = $1", channel.id
            )
            if not current_owner_id:
                return False
            current_owner = channel.guild.get_member(current_owner_id)
            if current_owner and current_owner.voice and current_owner.voice.channel == channel:
                return False
            await self.bot.cxn.execute(
                "UPDATE voicemaster_channels SET owner_id = $1 WHERE channel_id = $2", member.id, channel.id
            )
            if current_owner:
                await channel.set_permissions(current_owner, overwrite=None)
            await channel.set_permissions(
                member, manage_channels=True, manage_permissions=True,
                move_members=True, mute_members=True, deafen_members=True
            )
            return True
        except Exception as exc:
            logging.error("VoiceMaster", f"Claim channel error: {exc}")
            return False

    async def increase_limit(self, channel: discord.VoiceChannel, _: discord.Member):
        current = channel.user_limit
        await channel.edit(user_limit=min(current + 1 if current > 0 else 2, 99))

    async def decrease_limit(self, channel: discord.VoiceChannel, _: discord.Member):
        current = channel.user_limit
        await channel.edit(user_limit=0 if current <= 1 else current - 1)

    async def get_channel_info(self, channel: discord.VoiceChannel,
                               context=None) -> ui.LayoutView:
        """The channel card, in the language of whoever asked for it."""
        owner_id = await self.bot.cxn.fetchval(
            "SELECT owner_id FROM voicemaster_channels WHERE channel_id = $1", channel.id
        )
        owner = channel.guild.get_member(owner_id) if owner_id else None

        perms = channel.overwrites_for(channel.guild.default_role)
        status_parts = []
        if perms.connect is False:
            status_parts.append(msg(context, "info_locked"))
        if perms.view_channel is False:
            status_parts.append(msg(context, "info_hidden"))
        ch_status = " · ".join(status_parts) if status_parts else msg(context, "info_open")

        limit = str(channel.user_limit) if channel.user_limit else msg(context, "info_no_limit")
        region = (
            str(channel.rtc_region).title() if channel.rtc_region
            else msg(context, "info_automatic")
        )

        details = []
        if owner:
            details.append(f"> - **{msg(context, 'info_owner')}:** {owner.mention}")
        details.append(
            f"> - **{msg(context, 'info_members')}:** {len(channel.members)}"
        )
        details.append(f"> - **{msg(context, 'info_limit')}:** {limit}")
        details.append(
            f"> - **{msg(context, 'info_bitrate')}:** {channel.bitrate // 1000} kbps"
        )
        details.append(f"> - **{msg(context, 'info_region')}:** {region}")
        details.append(f"> - **{msg(context, 'info_status')}:** {ch_status}")

        view = ui.LayoutView(timeout=None)
        container = ui.Container(accent_color=COLOR_DEFAULT)
        container.add_item(ui.TextDisplay(f"## {channel.name}"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay("\n".join(details)))
        view.add_item(container)
        return view

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            if after.channel:
                settings = await self.get_guild_settings(member.guild.id)
                if settings and after.channel.id == settings.get('join_channel_id'):
                    category = None
                    if settings.get('category_id'):
                        category = member.guild.get_channel(settings['category_id'])
                    await self._create_temp_channel(member, category)

            if before.channel and len(before.channel.members) == 0:
                asyncio.create_task(self._cleanup_empty_channel(before.channel))
        except Exception as e:
            logging.error("VoiceMaster", f"Voice state update error: {e}")

    @decorators.group(
        name="voicemaster",
        aliases=["j2c", "vm", "join2create"],
        help=CMDS.help("voicemaster"),
    )
    @checks.cooldown()
    async def _voicemaster(self, ctx):
        if not ctx.invoked_subcommand:
            view = ui.LayoutView(timeout=None)
            container = ui.Container()
            container.add_item(ui.TextDisplay(f"## {BOT_NAME} | VoiceMaster"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(msg(ctx, "help_body")))
            container.add_item(ui.Separator())
            container.add_item(ui.ActionRow(
                ui.Button(
                    label=msg(ctx, "help_support_button"),
                    style=discord.ButtonStyle.link,
                    url=SUPPORT_URL,
                ),
            ))
            view.add_item(container)
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    @_voicemaster.command(help=CMDS.help("voicemaster.setup"))
    @checks.has_perms(manage_guild=True)
    async def setup(self, ctx):
        current_hub = None
        settings = await self.get_guild_settings(ctx.guild.id)
        if settings and settings.get('join_channel_id'):
            current_hub = ctx.guild.get_channel(settings['join_channel_id'])
        await ctx.send(
            view=VoiceMasterSetupView(self, ctx, current_hub),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @_voicemaster.command(help=CMDS.help("voicemaster.sendinterface"))
    @checks.has_perms(manage_guild=True)
    async def sendinterface(self, ctx):
        await ctx.send(view=VoiceMasterInterface(get_lang(ctx)))

    @_voicemaster.command(help=CMDS.help("voicemaster.reset"))
    @checks.has_perms(manage_guild=True)
    async def reset(self, ctx):
        try:
            settings   = await self.get_guild_settings(ctx.guild.id)
            channel_ids = await self.bot.cxn.fetch(
                "SELECT channel_id FROM voicemaster_channels WHERE guild_id = $1", ctx.guild.id
            )

            for record in channel_ids:
                ch = ctx.guild.get_channel(record['channel_id'])
                if ch:
                    await ch.delete(reason="VoiceMaster reset")

            if settings:
                if settings.get('join_channel_id'):
                    jc = ctx.guild.get_channel(settings['join_channel_id'])
                    # Setup can point at a hub the admin already owned, so only
                    # remove the channel Niko created itself.
                    if jc and jc.name == SETUP_HUB_NAME:
                        await jc.delete(reason="VoiceMaster reset")
                if settings.get('category_id'):
                    cat = ctx.guild.get_channel(settings['category_id'])
                    if cat and len(cat.channels) == 0:
                        await cat.delete(reason="VoiceMaster reset")

            await self.bot.cxn.execute("DELETE FROM voicemaster_channels WHERE guild_id = $1", ctx.guild.id)
            await self.bot.cxn.execute("DELETE FROM voicemaster_settings WHERE guild_id = $1", ctx.guild.id)
            self._bust_cache(ctx.guild.id)

            await success(ctx, f"{get_emoji('refresh')} {msg(ctx, 'reset_success')}")
        except Exception as e:
            logging.error("VoiceMaster", f"Reset error: {e}")
            await fail(ctx, msg(ctx, "reset_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.category"))
    @checks.has_perms(manage_guild=True)
    async def category(
        self,
        ctx,
        cat: discord.CategoryChannel = commands.parameter(
            default=None,
            description=CMDS.arg("voicemaster.category", "cat"),
        ),
    ):
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET category_id = $1 WHERE guild_id = $2",
                cat.id if cat else None, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            line = (
                f"{get_emoji('categories')} "
                f"{msg(ctx, 'category_set', category=cat.name)}"
                if cat else
                f"{get_emoji('categories')} {msg(ctx, 'category_cleared')}"
            )
            await success(ctx, line)
        except Exception as e:
            logging.error("VoiceMaster", f"Category error: {e}")
            await fail(ctx, msg(ctx, "category_failed"))

    @_voicemaster.group(help=CMDS.help("voicemaster.default"))
    @checks.has_perms(manage_guild=True)
    async def default(self, ctx):
        if not ctx.invoked_subcommand:
            settings = await self.get_guild_settings(ctx.guild.id)
            if not settings:
                await fail(ctx, msg(ctx, "default_not_set_up"))
                return

            default_limit   = settings.get('default_limit', 0)
            default_bitrate = (settings.get('default_bitrate', 64000) or 64000) // 1000
            default_name    = settings.get('default_name') or "{user}'s Channel"

            view = ui.LayoutView(timeout=None)
            container = ui.Container(accent_color=COLOR_DEFAULT)
            container.add_item(ui.TextDisplay(
                f"## {BOT_NAME} | {msg(ctx, 'defaults_title')}"
            ))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(
                f"**{get_emoji('edit')} {msg(ctx, 'defaults_name')}:** {default_name}\n"
                f"**{E.LIMIT} {msg(ctx, 'defaults_limit')}:** "
                f"{default_limit or msg(ctx, 'no_limit')}\n"
                f"**{E.BITRATE} {msg(ctx, 'defaults_bitrate')}:** {default_bitrate} kbps"
            ))
            view.add_item(container)
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    @default.command(name="name", help=CMDS.help("voicemaster.default.name"))
    @checks.has_perms(manage_guild=True)
    async def default_name(
        self,
        ctx,
        *,
        name: str = commands.parameter(
            description=CMDS.arg("voicemaster.default.name", "name"),
        ),
    ):
        if len(name) > 100:
            await fail(ctx, msg(ctx, "default_name_too_long"))
            return
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET default_name = $1 WHERE guild_id = $2", name, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            await success(
                ctx,
                f"{get_emoji('edit')} {msg(ctx, 'default_name_set', name=name)}",
            )
        except Exception as e:
            logging.error("VM", f"Default name error: {e}")
            await fail(ctx, msg(ctx, "default_name_failed"))

    @default.command(name="limit", help=CMDS.help("voicemaster.default.limit"))
    @checks.has_perms(manage_guild=True)
    async def default_limit(
        self,
        ctx,
        limit: int = commands.parameter(
            description=CMDS.arg("voicemaster.default.limit", "limit"),
        ),
    ):
        if limit < 0 or limit > 99:
            await fail(ctx, msg(ctx, "default_limit_invalid"))
            return
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET default_limit = $1 WHERE guild_id = $2", limit, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            value = msg(ctx, "no_limit") if limit == 0 else str(limit)
            await success(
                ctx,
                f"{E.LIMIT} {msg(ctx, 'default_limit_set', value=value)}",
            )
        except Exception as e:
            logging.error("VoiceMaster", f"Default limit error: {e}")
            await fail(ctx, msg(ctx, "default_limit_failed"))

    @default.command(name="bitrate", help=CMDS.help("voicemaster.default.bitrate"))
    @checks.has_perms(manage_guild=True)
    async def default_bitrate(
        self,
        ctx,
        bitrate: int = commands.parameter(
            description=CMDS.arg("voicemaster.default.bitrate", "bitrate"),
        ),
    ):
        if bitrate < 8 or bitrate > 384:
            await fail(ctx, msg(ctx, "default_bitrate_invalid"))
            return
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET default_bitrate = $1 WHERE guild_id = $2",
                bitrate * 1000, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            await success(
                ctx,
                f"{E.BITRATE} {msg(ctx, 'default_bitrate_set', value=bitrate)}",
            )
        except Exception as e:
            logging.error("VM", f"Default bitrate error: {e}")
            await fail(ctx, msg(ctx, "default_bitrate_failed"))

    @default.command(name="region", help=CMDS.help("voicemaster.default.region"))
    @checks.has_perms(manage_guild=True)
    async def default_region(
        self,
        ctx,
        region: str = commands.parameter(
            default=None,
            description=CMDS.arg("voicemaster.default.region", "region"),
        ),
    ):
        valid_regions = [
            'us-west', 'us-east', 'us-central', 'us-south',
            'singapore', 'southafrica', 'sydney', 'europe',
            'brazil', 'hongkong', 'russia', 'japan', 'india',
        ]
        if region and region.lower() not in valid_regions:
            await fail(
                ctx,
                msg(ctx, "default_region_invalid", regions=", ".join(valid_regions)),
            )
            return
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET default_region = $1 WHERE guild_id = $2",
                region.lower() if region else None, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            value = region.title() if region else msg(ctx, "info_automatic")
            await success(
                ctx,
                f"{E.REGION} {msg(ctx, 'default_region_set', value=value)}",
            )
        except Exception as e:
            logging.error("VM", f"Default region error: {e}")
            await fail(ctx, msg(ctx, "default_region_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.configuration"))
    async def configuration(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        await ctx.send(
            view=await self.get_channel_info(channel, ctx),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @_voicemaster.command(help=CMDS.help("voicemaster.lock"))
    async def lock(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await self.lock_channel(channel, ctx.author)
            await success(ctx, f"{get_emoji('lock')} {msg(ctx, 'locked')}")
        except Exception as e:
            logging.error("VM", f"Lock error: {e}")
            await fail(ctx, msg(ctx, "lock_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.unlock"))
    async def unlock(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await self.unlock_channel(channel, ctx.author)
            await success(ctx, f"{get_emoji('unlock')} {msg(ctx, 'unlocked')}")
        except Exception as e:
            logging.error("VoiceMaster", f"Unlock error: {e}")
            await fail(ctx, msg(ctx, "unlock_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.ghost"))
    async def ghost(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await self.ghost_channel(channel, ctx.author)
            await success(ctx, f"{get_emoji('hide')} {msg(ctx, 'hidden')}")
        except Exception as e:
            logging.error("VoiceMaster", f"Ghost error: {e}")
            await fail(ctx, msg(ctx, "ghost_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.unghost"))
    async def unghost(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await self.unghost_channel(channel, ctx.author)
            await success(ctx, f"{get_emoji('unhide')} {msg(ctx, 'revealed')}")
        except Exception as e:
            logging.error("VoiceMaster", f"Unghost error: {e}")
            await fail(ctx, msg(ctx, "unghost_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.claim"))
    async def claim(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        if await self.claim_channel(ctx.author.voice.channel, ctx.author):
            await success(ctx, f"{get_emoji('owner_icon')} {msg(ctx, 'claimed')}")
        else:
            await fail(ctx, msg(ctx, "claim_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.limit"))
    async def limit(
        self,
        ctx,
        limit: int = commands.parameter(
            description=CMDS.arg("voicemaster.limit", "limit"),
        ),
    ):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        if limit < 0 or limit > 99:
            await fail(ctx, msg(ctx, "limit_invalid"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await channel.edit(user_limit=limit)
            line = (
                f"{E.LIMIT} {msg(ctx, 'limit_removed')}" if limit == 0
                else f"{E.LIMIT} {msg(ctx, 'limit_set', limit=limit)}"
            )
            await success(ctx, line)
        except Exception as e:
            logging.error("VoiceMaster", f"Limit error: {e}")
            await fail(ctx, msg(ctx, "limit_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.name"))
    async def name(
        self,
        ctx,
        *,
        name: str = commands.parameter(
            description=CMDS.arg("voicemaster.name", "name"),
        ),
    ):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        if len(name) > 100:
            await fail(ctx, msg(ctx, "name_too_long"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await channel.edit(name=name)
            await success(ctx, f"{get_emoji('edit')} {msg(ctx, 'renamed', name=name)}")
        except Exception as e:
            logging.error("VoiceMaster", f"Rename error: {e}")
            await fail(ctx, msg(ctx, "rename_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.bitrate"))
    async def bitrate(
        self,
        ctx,
        bitrate: int = commands.parameter(
            description=CMDS.arg("voicemaster.bitrate", "bitrate"),
        ),
    ):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        if bitrate < 8 or bitrate > 384:
            await fail(ctx, msg(ctx, "bitrate_invalid"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await channel.edit(bitrate=bitrate * 1000)
            await success(
                ctx, f"{E.BITRATE} {msg(ctx, 'bitrate_set', value=bitrate)}"
            )
        except Exception as e:
            logging.error("VoiceMaster", f"Bitrate error: {e}")
            await fail(ctx, msg(ctx, "bitrate_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.transfer"))
    async def transfer(
        self,
        ctx,
        member: discord.Member = commands.parameter(
            description=CMDS.arg("voicemaster.transfer", "member"),
        ),
    ):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        if member == ctx.author:
            await fail(ctx, msg(ctx, "transfer_self"))
            return
        if not member.voice or member.voice.channel != ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "transfer_not_in_channel"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_channels SET owner_id = $1 WHERE channel_id = $2", member.id, channel.id
            )
            await channel.set_permissions(ctx.author, overwrite=None)
            await channel.set_permissions(
                member, manage_channels=True, manage_permissions=True,
                move_members=True, mute_members=True, deafen_members=True
            )
            await success(
                ctx,
                f"{get_emoji('owner_icon')} "
                f"{msg(ctx, 'transferred', user=member.display_name)}",
            )
        except Exception as e:
            logging.error("VoiceMaster", f"Transfer error: {e}")
            await fail(ctx, msg(ctx, "transfer_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.permit"))
    async def permit(
        self,
        ctx,
        target: Union[converters.DiscordMember, discord.Role] = commands.parameter(
            description=CMDS.arg("voicemaster.permit", "target"),
        ),
    ):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await channel.set_permissions(target, connect=True)
            target_name = (
                target.display_name if isinstance(target, discord.Member)
                else msg(ctx, "permit_role")
            )
            await success(
                ctx,
                f"{get_emoji('tick')} {msg(ctx, 'permitted', target=target_name)}",
            )
        except Exception as e:
            logging.error("VoiceMaster", f"Permit error: {e}")
            await fail(ctx, msg(ctx, "permit_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.reject"))
    async def reject(
        self,
        ctx,
        target: Union[converters.DiscordMember, discord.Role] = commands.parameter(
            description=CMDS.arg("voicemaster.reject", "target"),
        ),
    ):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await channel.set_permissions(target, connect=False)
            if isinstance(target, discord.Member) and target.voice and target.voice.channel == channel:
                await target.move_to(None)
            target_name = (
                target.display_name if isinstance(target, discord.Member)
                else msg(ctx, "permit_role")
            )
            await success(
                ctx,
                f"{get_emoji('cross')} {msg(ctx, 'rejected', target=target_name)}",
            )
        except Exception as e:
            logging.error("VoiceMaster", f"Reject error: {e}")
            await fail(ctx, msg(ctx, "reject_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.status"))
    async def status(
        self,
        ctx,
        *,
        status: str = commands.parameter(
            default=None,
            description=CMDS.arg("voicemaster.status", "status"),
        ),
    ):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        try:
            await channel.edit(status=status)
            line = (
                f"{E.STATUS} {msg(ctx, 'status_set', status=status)}" if status
                else f"{E.STATUS} {msg(ctx, 'status_cleared')}"
            )
            await success(ctx, line)
        except Exception as e:
            logging.error("VoiceMaster", f"Status error: {e}")
            await fail(ctx, msg(ctx, "status_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.disconnect"), hidden=True)
    async def disconnect(
        self,
        ctx,
        member: converters.DiscordMember = commands.parameter(
            description=CMDS.arg("voicemaster.disconnect", "member"),
        ),
    ):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        if not member.voice or member.voice.channel != channel:
            await fail(ctx, msg(ctx, "disconnect_not_in_channel"))
            return
        try:
            await member.move_to(None)
            await success(
                ctx,
                f"{get_emoji('disconnect')} "
                f"{msg(ctx, 'disconnected', user=member.display_name)}",
            )
        except Exception as e:
            logging.error("VoiceMaster", f"Disconnect error: {e}")
            await fail(ctx, msg(ctx, "disconnect_member_failed"))

    @_voicemaster.command(help=CMDS.help("voicemaster.role"))
    async def role(
        self,
        ctx,
        role: discord.Role = commands.parameter(
            description=CMDS.arg("voicemaster.role", "role"),
        ),
    ):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await fail(ctx, msg(ctx, "not_in_voice"))
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await fail(ctx, msg(ctx, "not_owner"))
            return
        await success(ctx, f"{E.ROLE} {msg(ctx, 'role_configured', role=role.name)}")


async def setup(bot):
    await bot.add_cog(VoiceMaster(bot))
