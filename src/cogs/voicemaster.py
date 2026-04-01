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

COLOR_DEFAULT = 0xFFFFFF
COLOR_SUCCESS = 0x00CC66
COLOR_ERROR = 0xFF0000

SUPPORT_URL = "https://dsc.gg/astral-haven"
BOT_NAME = "Niko"

def make_container(text: str, accent: int = COLOR_DEFAULT) -> ui.LayoutView:
    view = ui.LayoutView(timeout=None)
    container = ui.Container(accent_color=accent)
    container.add_item(ui.TextDisplay(text))
    view.add_item(container)
    return view


class DisconnectMemberSelect(discord.ui.Select):
    def __init__(self, members: list):
        options = [
            discord.SelectOption(
                label=member.display_name,
                description=f"Disconnect {member.display_name}",
                value=str(member.id)
            )
            for member in members[:25]
        ]
        super().__init__(
            placeholder="Choose members to disconnect...",
            min_values=1,
            max_values=min(len(options), 25),
            options=options
        )

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
                parts.append(f"{get_emoji('icon_tick')} Disconnected: {', '.join(disconnected)}")
            if failed:
                parts.append(f"{get_emoji('icon_cross')} Failed: {', '.join(failed)}")

            msg = "\n".join(parts) or f"{get_emoji('icon_cross')} No members were disconnected."
            await interaction.response.edit_message(
                content=None,
                view=make_container(f"-# {msg}")
            )
        except Exception as e:
            logging.error("VoiceMaster", f"Disconnect callback error: {e}")
            await interaction.response.edit_message(
                content=None,
                view=make_container(f"-# {get_emoji('icon_cross')} An error occurred.", accent=COLOR_ERROR)
            )


class DisconnectMemberView(discord.ui.View):
    def __init__(self, members: list, owner: discord.Member):
        super().__init__(timeout=60)
        self.add_item(DisconnectMemberSelect(members))


INTERFACE_TITLE = "## VoiceMaster | Interface"

INTERFACE_COMMANDS = (
    f"{get_emoji('vm_lock')} — [`Lock`]({SUPPORT_URL}) the voice channel\n"
    f"{get_emoji('vm_unlock')} — [`Unlock`]({SUPPORT_URL}) the voice channel\n"
    f"{E.GHOST} — [`Hide`]({SUPPORT_URL}) the voice channel\n"
    f"{E.REVEAL} — [`Reveal`]({SUPPORT_URL}) the voice channel\n"
    f"{get_emoji('owner_icon')} — [`Claim`]({SUPPORT_URL}) the voice channel\n"
    f"{E.DISCONNECT} — [`Disconnect`]({SUPPORT_URL}) a member\n"
    f"{E.INFO} — [`View`]({SUPPORT_URL}) channel information\n"
    f"{get_emoji('icon_plus')} — [`Increase`]({SUPPORT_URL}) the user limit\n"
    f"{E.DECREASE} — [`Decrease`]({SUPPORT_URL}) the user limit"
)


class VoiceMasterInterface(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        btn_lock       = discord.ui.Button(emoji=get_emoji('vm_lock'),       style=discord.ButtonStyle.gray, custom_id="vm_lock")
        btn_unlock     = discord.ui.Button(emoji=get_emoji('vm_unlock'),     style=discord.ButtonStyle.gray, custom_id="vm_unlock")
        btn_ghost      = discord.ui.Button(emoji=E.GHOST,      style=discord.ButtonStyle.gray, custom_id="vm_ghost")
        btn_reveal     = discord.ui.Button(emoji=E.REVEAL,     style=discord.ButtonStyle.gray, custom_id="vm_reveal")
        btn_claim      = discord.ui.Button(emoji=get_emoji('owner_icon'),      style=discord.ButtonStyle.gray, custom_id="vm_claim")

        btn_disconnect = discord.ui.Button(emoji=E.DISCONNECT, style=discord.ButtonStyle.gray, custom_id="vm_disconnect")
        btn_info       = discord.ui.Button(emoji=E.INFO,       style=discord.ButtonStyle.gray, custom_id="vm_info")
        btn_increase   = discord.ui.Button(emoji=get_emoji('icon_plus'),   style=discord.ButtonStyle.gray, custom_id="vm_increase")
        btn_decrease   = discord.ui.Button(emoji=E.DECREASE,   style=discord.ButtonStyle.gray, custom_id="vm_decrease")

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
        container.add_item(ui.TextDisplay(INTERFACE_TITLE))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(INTERFACE_COMMANDS))
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
                view=make_container(f"-# {get_emoji('icon_cross')} No members to disconnect.", accent=COLOR_ERROR),
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            view=DisconnectMemberView(members, interaction.user),
            ephemeral=True
        )

    async def _resolve(self, interaction: discord.Interaction, *, owner_required: bool = True):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                view=make_container(f"-# {get_emoji('icon_cross')} You must be in a voice channel.", accent=COLOR_ERROR),
                ephemeral=True
            )
            return None, None, True

        cog = interaction.client.get_cog("VoiceMaster")
        if not cog:
            await interaction.response.send_message(
                view=make_container(f"-# {get_emoji('icon_cross')} VoiceMaster is not available.", accent=COLOR_ERROR),
                ephemeral=True
            )
            return None, None, True

        channel = interaction.user.voice.channel

        if owner_required and not await cog.is_channel_owner(interaction.user.id, channel.id):
            await interaction.response.send_message(
                view=make_container(f"-# {get_emoji('icon_cross')} You don't own this voice channel.", accent=COLOR_ERROR),
                ephemeral=True
            )
            return None, None, True

        return cog, channel, False

    async def _dispatch(self, interaction: discord.Interaction, action: str):
        owner_required = action not in ("claim", "info")
        cog, channel, err = await self._resolve(interaction, owner_required=owner_required)
        if err:
            return

        try:
            if action == "lock":
                await cog.lock_channel(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(f"-# {get_emoji('vm_lock')} Voice channel locked.", accent=COLOR_SUCCESS), ephemeral=True
                )
            elif action == "unlock":
                await cog.unlock_channel(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(f"-# {get_emoji('vm_unlock')} Voice channel unlocked.", accent=COLOR_SUCCESS), ephemeral=True
                )
            elif action == "ghost":
                await cog.ghost_channel(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(f"-# {E.GHOST} Voice channel hidden.", accent=COLOR_SUCCESS), ephemeral=True
                )
            elif action == "unghost":
                await cog.unghost_channel(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(f"-# {E.REVEAL} Voice channel revealed.", accent=COLOR_SUCCESS), ephemeral=True
                )
            elif action == "claim":
                if await cog.claim_channel(channel, interaction.user):
                    await interaction.response.send_message(
                        view=make_container(f"-# {get_emoji('owner_icon')} Voice channel claimed.", accent=COLOR_SUCCESS), ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        view=make_container(f"-# {get_emoji('icon_cross')} Cannot claim this channel.", accent=COLOR_ERROR), ephemeral=True
                    )
            elif action == "info":
                await interaction.response.send_message(
                    view=await cog.get_channel_info(channel), ephemeral=True
                )
            elif action == "increase_limit":
                await cog.increase_limit(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(f"-# {get_emoji('icon_plus')} User limit increased.", accent=COLOR_SUCCESS), ephemeral=True
                )
            elif action == "decrease_limit":
                await cog.decrease_limit(channel, interaction.user)
                await interaction.response.send_message(
                    view=make_container(f"-# {E.DECREASE} User limit decreased.", accent=COLOR_SUCCESS), ephemeral=True
                )
        except Exception as exc:
            logging.error("VoiceMaster", f"Interface action '{action}' error: {exc}")
            await interaction.response.send_message(
                view=make_container(f"-# {get_emoji('icon_cross')} An error occurred.", accent=COLOR_ERROR), ephemeral=True
            )


class VoiceMaster(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(VoiceMasterInterface())
        self._settings_cache: dict = {}

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

            await asyncio.gather(
                member.move_to(channel),
                self.bot.cxn.execute(
                    "INSERT INTO voicemaster_channels (channel_id, owner_id, guild_id, created_at) "
                    "VALUES ($1, $2, $3, datetime('now'))",
                    channel.id, member.id, member.guild.id
                ),
                return_exceptions=True
            )
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
                await asyncio.gather(
                    channel.delete(reason="VoiceMaster: Empty temporary channel"),
                    self.bot.cxn.execute(
                        "DELETE FROM voicemaster_channels WHERE channel_id = $1", channel.id
                    ),
                    return_exceptions=True
                )
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

    async def get_channel_info(self, channel: discord.VoiceChannel) -> ui.LayoutView:
        owner_id = await self.bot.cxn.fetchval(
            "SELECT owner_id FROM voicemaster_channels WHERE channel_id = $1", channel.id
        )
        owner = channel.guild.get_member(owner_id) if owner_id else None

        perms = channel.overwrites_for(channel.guild.default_role)
        status_parts = []
        if perms.connect is False:
            status_parts.append("Locked")
        if perms.view_channel is False:
            status_parts.append("Hidden")
        ch_status = " · ".join(status_parts) if status_parts else "Open"

        details = []
        if owner:
            details.append(f"> - **Owner:** {owner.mention}")
        details.append(f"> - **Members:** {len(channel.members)}")
        details.append(f"> - **Limit:** {channel.user_limit if channel.user_limit else 'No limit'}")
        details.append(f"> - **Bitrate:** {channel.bitrate // 1000} kbps")
        details.append(f"> - **Region:** {str(channel.rtc_region).title() if channel.rtc_region else 'Automatic'}")
        details.append(f"> - **Status:** {ch_status}")

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
        brief="Make temporary voice channels in your server",
    )
    @checks.cooldown()
    async def _voicemaster(self, ctx):
        if not ctx.invoked_subcommand:
            view = ui.LayoutView(timeout=None)
            container = ui.Container()
            container.add_item(ui.TextDisplay(f"## {BOT_NAME} | VoiceMaster"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(
                "Create and manage temporary voice channels in your server.\n\n"
                "**Getting Started**\n"
                f"-# Use `voicemaster setup` to configure VoiceMaster for your server\n\n"
                "**Popular Commands**\n"
                f"-# `voicemaster lock` — Lock your channel\n"
                f"-# `voicemaster claim` — Claim an inactive channel\n"
                f"-# `voicemaster limit <number>` — Set user limit"
            ))
            container.add_item(ui.Separator())
            container.add_item(ui.ActionRow(
                ui.Button(label="Support", style=discord.ButtonStyle.link, url=SUPPORT_URL),
            ))
            view.add_item(container)
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    @_voicemaster.command(brief="Configure VoiceMaster for your server")
    @checks.has_perms(manage_guild=True)
    async def setup(self, ctx):
        try:
            category = await ctx.guild.create_category("Niko | VoiceMaster")
            join_channel = await ctx.guild.create_voice_channel("Join to Create", category=category)

            await self.bot.cxn.execute(
                """
                INSERT INTO voicemaster_settings
                    (guild_id, join_channel_id, category_id, default_name, default_limit, default_bitrate)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (guild_id)
                DO UPDATE SET
                    join_channel_id = excluded.join_channel_id,
                    category_id     = excluded.category_id
                """,
                ctx.guild.id, join_channel.id, category.id, "{user}'s Channel", 0, 64000
            )
            self._bust_cache(ctx.guild.id)

            view = ui.LayoutView(timeout=None)
            container = ui.Container(accent_color=COLOR_SUCCESS)
            container.add_item(ui.TextDisplay(f"## {get_emoji('icon_tick')} VoiceMaster Setup Complete"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(
                f"**Join Channel:** {join_channel.mention}\n"
                f"**Category:** {category.name}\n\n"
                f"-# Use `{ctx.prefix}voicemaster sendinterface` to send the control panel."
            ))
            view.add_item(container)
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

        except Exception as e:
            logging.error("VoiceMaster", f"Setup error: {e}")
            await ctx.fail("Failed to set up VoiceMaster. Please check my permissions.")

    @_voicemaster.command(brief="Send the VoiceMaster control panel")
    @checks.has_perms(manage_guild=True)
    async def sendinterface(self, ctx):
        await ctx.send(view=VoiceMasterInterface())

    @_voicemaster.command(brief="Reset VoiceMaster configuration for this server")
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
                    if jc:
                        await jc.delete(reason="VoiceMaster reset")
                if settings.get('category_id'):
                    cat = ctx.guild.get_channel(settings['category_id'])
                    if cat and len(cat.channels) == 0:
                        await cat.delete(reason="VoiceMaster reset")

            await self.bot.cxn.execute("DELETE FROM voicemaster_channels WHERE guild_id = $1", ctx.guild.id)
            await self.bot.cxn.execute("DELETE FROM voicemaster_settings WHERE guild_id = $1", ctx.guild.id)
            self._bust_cache(ctx.guild.id)

            await ctx.success(f"{E.TRANSFER} VoiceMaster has been reset.")
        except Exception as e:
            logging.error("VoiceMaster", f"Reset error: {e}")
            await ctx.fail("Failed to reset VoiceMaster.")

    @_voicemaster.command(brief="Set the category for temporary voice channels")
    @checks.has_perms(manage_guild=True)
    async def category(self, ctx, cat: discord.CategoryChannel = None):
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET category_id = $1 WHERE guild_id = $2",
                cat.id if cat else None, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            msg = f"{get_emoji('icon_categories')} Voice channels will be created in: **{cat.name}**" if cat \
                else f"{get_emoji('icon_categories')} Voice channels will be created without a specific category."
            await ctx.success(msg)
        except Exception as e:
            logging.error("VoiceMaster", f"Category error: {e}")
            await ctx.fail("Failed to set category.")

    @_voicemaster.group(brief="Configure default settings for new voice channels")
    @checks.has_perms(manage_guild=True)
    async def default(self, ctx):
        if not ctx.invoked_subcommand:
            settings = await self.get_guild_settings(ctx.guild.id)
            if not settings:
                await ctx.fail("VoiceMaster is not set up. Use `voicemaster setup` first.")
                return

            default_limit   = settings.get('default_limit', 0)
            default_bitrate = (settings.get('default_bitrate', 64000) or 64000) // 1000
            default_name    = settings.get('default_name') or "{user}'s Channel"

            view = ui.LayoutView(timeout=None)
            container = ui.Container(accent_color=COLOR_DEFAULT)
            container.add_item(ui.TextDisplay(f"## {BOT_NAME} | Default Settings"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(
                f"**{get_emoji('icon_edit')} Default Name:** {default_name}\n"
                f"**{E.LIMIT} Default Limit:** {default_limit or 'No limit'}\n"
                f"**{E.BITRATE} Default Bitrate:** {default_bitrate} kbps"
            ))
            view.add_item(container)
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    @default.command(name="name", brief="Set default name for new voice channels")
    @checks.has_perms(manage_guild=True)
    async def default_name(self, ctx, *, name: str):
        if len(name) > 100:
            await ctx.fail("Default name must be 100 characters or less.")
            return
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET default_name = $1 WHERE guild_id = $2", name, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            await ctx.success(f"{get_emoji('icon_edit')} Default channel name set to: **{name}**")
        except Exception as e:
            logging.error("VM", f"Default name error: {e}")
            await ctx.fail("Failed to set default name.")

    @default.command(name="limit", brief="Set default user limit for new voice channels")
    @checks.has_perms(manage_guild=True)
    async def default_limit(self, ctx, limit: int):
        if limit < 0 or limit > 99:
            await ctx.fail("Limit must be between 0 and 99.")
            return
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET default_limit = $1 WHERE guild_id = $2", limit, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            msg = f"{E.LIMIT} Default user limit set to: **No limit**" if limit == 0 \
                else f"{E.LIMIT} Default user limit set to: **{limit}**"
            await ctx.success(msg)
        except Exception as e:
            logging.error("VoiceMaster", f"Default limit error: {e}")
            await ctx.fail("Failed to set default limit.")

    @default.command(name="bitrate", brief="Set default bitrate for new voice channels")
    @checks.has_perms(manage_guild=True)
    async def default_bitrate(self, ctx, bitrate: int):
        if bitrate < 8 or bitrate > 384:
            await ctx.fail("Bitrate must be between 8 and 384 kbps.")
            return
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET default_bitrate = $1 WHERE guild_id = $2",
                bitrate * 1000, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            await ctx.success(f"{E.BITRATE} Default bitrate set to: **{bitrate} kbps**")
        except Exception as e:
            logging.error("VM", f"Default bitrate error: {e}")
            await ctx.fail("Failed to set default bitrate.")

    @default.command(name="region", brief="Set default region for new voice channels")
    @checks.has_perms(manage_guild=True)
    async def default_region(self, ctx, region: str = None):
        valid_regions = [
            'us-west', 'us-east', 'us-central', 'us-south',
            'singapore', 'southafrica', 'sydney', 'europe',
            'brazil', 'hongkong', 'russia', 'japan', 'india',
        ]
        if region and region.lower() not in valid_regions:
            await ctx.fail(f"Invalid region. Valid options: {', '.join(valid_regions)}")
            return
        try:
            await self.bot.cxn.execute(
                "UPDATE voicemaster_settings SET default_region = $1 WHERE guild_id = $2",
                region.lower() if region else None, ctx.guild.id
            )
            self._bust_cache(ctx.guild.id)
            msg = f"{E.REGION} Default region set to: **{region.title()}**" if region \
                else f"{E.REGION} Default region set to: **Automatic**"
            await ctx.success(msg)
        except Exception as e:
            logging.error("VM", f"Default region error: {e}")
            await ctx.fail("Failed to set default region.")

    @_voicemaster.command(brief="View current voice channel configuration")
    async def configuration(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        await ctx.send(view=await self.get_channel_info(channel), allowed_mentions=discord.AllowedMentions.none())

    @_voicemaster.command(brief="Lock your voice channel")
    async def lock(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await self.lock_channel(channel, ctx.author)
            await ctx.success(f"{get_emoji('vm_lock')} Voice channel locked.")
        except Exception as e:
            logging.error("VM", f"Lock error: {e}")
            await ctx.fail("Failed to lock the voice channel.")

    @_voicemaster.command(brief="Unlock your voice channel")
    async def unlock(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await self.unlock_channel(channel, ctx.author)
            await ctx.success(f"{get_emoji('vm_unlock')} Voice channel unlocked.")
        except Exception as e:
            logging.error("VoiceMaster", f"Unlock error: {e}")
            await ctx.fail("Failed to unlock the voice channel.")

    @_voicemaster.command(brief="Hide your voice channel")
    async def ghost(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await self.ghost_channel(channel, ctx.author)
            await ctx.success(f"{E.GHOST} Voice channel hidden.")
        except Exception as e:
            logging.error("VoiceMaster", f"Ghost error: {e}")
            await ctx.fail("Failed to hide the voice channel.")

    @_voicemaster.command(brief="Unhide your voice channel")
    async def unghost(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await self.unghost_channel(channel, ctx.author)
            await ctx.success(f"{E.REVEAL} Voice channel revealed.")
        except Exception as e:
            logging.error("VoiceMaster", f"Unghost error: {e}")
            await ctx.fail("Failed to reveal the voice channel.")

    @_voicemaster.command(brief="Claim an inactive voice channel")
    async def claim(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        if await self.claim_channel(ctx.author.voice.channel, ctx.author):
            await ctx.success(f"{get_emoji('owner_icon')} Voice channel claimed.")
        else:
            await ctx.fail("Cannot claim this channel. The owner may still be present.")

    @_voicemaster.command(brief="Set a user limit on your voice channel")
    async def limit(self, ctx, limit: int):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        if limit < 0 or limit > 99:
            await ctx.fail("Limit must be between 0 and 99.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await channel.edit(user_limit=limit)
            msg = f"{E.LIMIT} User limit removed." if limit == 0 else f"{E.LIMIT} User limit set to {limit}."
            await ctx.success(msg)
        except Exception as e:
            logging.error("VoiceMaster", f"Limit error: {e}")
            await ctx.fail("Failed to set user limit.")

    @_voicemaster.command(brief="Rename your voice channel")
    async def name(self, ctx, *, name: str):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        if len(name) > 100:
            await ctx.fail("Channel name must be 100 characters or less.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await channel.edit(name=name)
            await ctx.success(f"{get_emoji('icon_edit')} Channel renamed to **{name}**.")
        except Exception as e:
            logging.error("VoiceMaster", f"Rename error: {e}")
            await ctx.fail("Failed to rename the voice channel.")

    @_voicemaster.command(brief="Set bitrate of your voice channel")
    async def bitrate(self, ctx, bitrate: int):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        if bitrate < 8 or bitrate > 384:
            await ctx.fail("Bitrate must be between 8 and 384 kbps.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await channel.edit(bitrate=bitrate * 1000)
            await ctx.success(f"{E.BITRATE} Bitrate set to {bitrate} kbps.")
        except Exception as e:
            logging.error("VoiceMaster", f"Bitrate error: {e}")
            await ctx.fail("Failed to set bitrate.")

    @_voicemaster.command(brief="Transfer ownership of your channel")
    async def transfer(self, ctx, member: discord.Member):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        if member == ctx.author:
            await ctx.fail("You cannot transfer ownership to yourself.")
            return
        if not member.voice or member.voice.channel != ctx.author.voice.channel:
            await ctx.fail("That member must be in your voice channel.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
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
            await ctx.success(f"{get_emoji('owner_icon')} Ownership transferred to **{member.display_name}**.")
        except Exception as e:
            logging.error("VoiceMaster", f"Transfer error: {e}")
            await ctx.fail("Failed to transfer ownership.")

    @_voicemaster.command(brief="Allow a member or role to join your VC")
    async def permit(self, ctx, target: Union[converters.DiscordMember, discord.Role]):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await channel.set_permissions(target, connect=True)
            target_name = target.display_name if isinstance(target, discord.Member) else "Members with this role"
            await ctx.success(f"{get_emoji('icon_tick')} **{target_name}** can now join your voice channel.")
        except Exception as e:
            logging.error("VoiceMaster", f"Permit error: {e}")
            await ctx.fail("Failed to permit access.")

    @_voicemaster.command(brief="Block a member or role from joining your VC")
    async def reject(self, ctx, target: Union[converters.DiscordMember, discord.Role]):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await channel.set_permissions(target, connect=False)
            if isinstance(target, discord.Member) and target.voice and target.voice.channel == channel:
                await target.move_to(None)
            target_name = target.display_name if isinstance(target, discord.Member) else "Members with this role"
            await ctx.success(f"{get_emoji('icon_cross')} **{target_name}** can no longer join your voice channel.")
        except Exception as e:
            logging.error("VoiceMaster", f"Reject error: {e}")
            await ctx.fail("Failed to reject access.")

    @_voicemaster.command(brief="Set a status message for your voice channel")
    async def status(self, ctx, *, status: str = None):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        try:
            await channel.edit(status=status)
            msg = f"{E.STATUS} Channel status set to: **{status}**" if status \
                else f"{E.STATUS} Channel status cleared."
            await ctx.success(msg)
        except Exception as e:
            logging.error("VoiceMaster", f"Status error: {e}")
            await ctx.fail("Failed to set channel status.")

    @_voicemaster.command(brief="Disconnect a member from your voice channel", hidden=True)
    async def disconnect(self, ctx, member: converters.DiscordMember):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        if not member.voice or member.voice.channel != channel:
            await ctx.fail("That member is not in your voice channel.")
            return
        try:
            await member.move_to(None)
            await ctx.success(f"{E.DISCONNECT} **{member.display_name}** has been disconnected.")
        except Exception as e:
            logging.error("VoiceMaster", f"Disconnect error: {e}")
            await ctx.fail("Failed to disconnect the member.")

    @_voicemaster.command(brief="Configure a role for your voice channel members")
    async def role(self, ctx, role: discord.Role):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.fail("You must be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        if not await self.is_channel_owner(ctx.author.id, channel.id):
            await ctx.fail("You don't own this voice channel.")
            return
        await ctx.success(f"{E.ROLE} Role management for **{role.name}** configured.")


async def setup(bot):
    await bot.add_cog(VoiceMaster(bot))