"""
nitro.py — Nitro-adjacent & advanced Discord features for Niko.

Features implemented here are things Discord Nitro users normally access
client-side but that bot accounts can use via the API:

  • Burst/super reactions  — animated burst effect on reactions
  • Voice channel status   — text shown in the VC header (/vcstatus)
  • Message forwarding     — native forward via type=1 reference (/forward)
  • Sticker management     — list, send, and upload guild stickers
  • Stage speaker          — bot can become a speaker on Stage channels
  • Context menus          — right-click "☕ Ask Niko" and "📊 User Profile"

All features degrade gracefully (ephemeral error) when permissions are missing.
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from config.emojis import get_emoji
from utils import logging as log
from utils.discord_extras import forward_message, set_voice_status, stage_become_speaker
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

MESSAGES = load_locales(__package__, "nitro")
msg = make_flat_msg(MESSAGES)


def _cv(text: str, *, colour: discord.Colour | None = None) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    kw: dict = {}
    if colour:
        kw["accent_colour"] = colour
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text), **kw))
    return view


# ── COG ───────────────────────────────────────────────────────────────────────

class NitroFeatures(commands.Cog, name="NitroFeatures"):
    """Nitro-adjacent and advanced Discord features."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        # Context menus must be registered manually for cogs
        self._ctx_ask = app_commands.ContextMenu(
            name="☕ Ask Niko",
            callback=self._ask_niko_ctx,
        )
        self._ctx_profile = app_commands.ContextMenu(
            name="📊 User Profile",
            callback=self._user_profile_ctx,
        )
        self.bot.tree.add_command(self._ctx_ask)
        self.bot.tree.add_command(self._ctx_profile)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self._ctx_ask.name, type=self._ctx_ask.type)
        self.bot.tree.remove_command(self._ctx_profile.name, type=self._ctx_profile.type)

    # ── Context menu: Ask Niko ────────────────────────────────────────────

    async def _ask_niko_ctx(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """Right-click a message → Niko responds to it."""
        await interaction.response.defer(ephemeral=True)

        content = message.content or "[no text content]"
        if len(content) > 500:
            content = content[:500] + "…"

        prompt = f'Someone shared this message with you:\n\n"{content}"\n\nWhat do you think?'

        # Share the same config, memory and sentinel handling as the normal AI
        # path. The old helper gated on OPENAI_API_KEY (which this bot never
        # reads), so the menu answered "not set up" even when AI worked.
        from utils.ai.config import load_config
        from utils.ai.error_views import build_ai_error_view, parse_ai_error
        from utils.ai.reply import generate_reply

        config = await load_config(interaction.guild.id) if interaction.guild else None
        reply = await generate_reply(
            self.bot,
            interaction.user.id,
            interaction.guild,
            prompt,
            interaction.user.display_name,
            config=config,
        )

        if isinstance(reply, str) and reply.startswith("ai_error:"):
            kind, cooldown = parse_ai_error(reply)
            await interaction.followup.send(
                view=build_ai_error_view(kind, cooldown),
                ephemeral=True,
            )
        elif reply == "ai_disabled_global":
            await interaction.followup.send(
                msg(interaction, "ai_disabled_global"), ephemeral=True
            )
        elif reply == "ai_disabled_guild":
            await interaction.followup.send(
                msg(interaction, "ai_disabled_guild"), ephemeral=True
            )
        elif isinstance(reply, str) and reply:
            await interaction.followup.send(
                view=_cv(
                    f"### ☕ {msg(interaction, 'ask_title')}\n{reply}",
                    colour=discord.Colour(0xc8a882),
                ),
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                view=_cv(
                    f"☕ {msg(interaction, 'ask_empty')}",
                    colour=discord.Colour(0xfee75c),
                ),
                ephemeral=True,
            )
        log.info("Nitro", f"Ask Niko reply requested by {interaction.user.id}")

    # ── Context menu: User Profile ────────────────────────────────────────

    async def _user_profile_ctx(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ) -> None:
        """Right-click a user → quick profile card with level + economy stats."""
        await interaction.response.defer(ephemeral=True)

        lines: list[str] = [f"### {get_emoji('user')} {member.display_name}"]

        # Level stats
        try:
            row = await self.bot.cxn.fetchrow(
                "SELECT xp, level FROM user_levels WHERE guild_id = $1 AND user_id = $2",
                interaction.guild_id, member.id,
            )
            if row:
                lines.append(
                    f"**{msg(interaction, 'profile_level')}:** {row['level']}  •  "
                    f"**{msg(interaction, 'profile_xp')}:** {row['xp']}"
                )
        except Exception:
            pass

        # Economy stats
        try:
            eco = await self.bot.cxn.fetchrow(
                "SELECT balance, bank FROM economy WHERE guild_id = $1 AND user_id = $2",
                interaction.guild_id, member.id,
            )
            if eco:
                lines.append(
                    f"**{msg(interaction, 'profile_wallet')}:** {eco['balance']:,} ☕  •  "
                    f"**{msg(interaction, 'profile_bank')}:** {eco['bank']:,} ☕"
                )
        except Exception:
            pass

        # Basic info
        joined = (
            discord.utils.format_dt(member.joined_at, "R")
            if member.joined_at
            else msg(interaction, "profile_unknown")
        )
        lines.append(f"-# {msg(interaction, 'profile_joined')}: {joined}")
        lines.append(
            f"-# {msg(interaction, 'profile_account')}: "
            f"{discord.utils.format_dt(member.created_at, 'R')}"
        )

        # Build a Section with avatar thumbnail (Components v2)
        section = discord.ui.Section(
            discord.ui.TextDisplay(content="\n".join(lines)),
            accessory=discord.ui.Thumbnail(
                discord.ui.UnfurledMediaItem(url=member.display_avatar.url)
            ),
        )
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(section, accent_colour=discord.Colour(0xc8a882)))
        await interaction.followup.send(view=view, ephemeral=True)

    # ── /vcstatus ─────────────────────────────────────────────────────────

    @app_commands.command(
        name="vcstatus",
        description=CMDS.text("vcstatus.description"),
    )
    @app_commands.describe(
        status=CMDS.arg("vcstatus", "status"),
        channel=CMDS.arg("vcstatus", "channel"),
    )
    @app_commands.guild_only()
    async def vcstatus(
        self,
        interaction: discord.Interaction,
        status: str = "",
        channel: discord.VoiceChannel | None = None,
    ) -> None:
        # Resolve channel
        target = channel
        if target is None and interaction.user.voice and interaction.user.voice.channel:  # type: ignore[union-attr]
            target = interaction.user.voice.channel  # type: ignore[union-attr]
        if target is None:
            await interaction.response.send_message(
                view=_cv(f"{get_emoji('cross')} {msg(interaction, 'vc_need_channel')}"),
                ephemeral=True,
            )
            return

        # Permission check
        me = interaction.guild.me
        perms = target.permissions_for(me)
        if not perms.manage_channels:
            await interaction.response.send_message(
                view=_cv(f"{get_emoji('cross')} {msg(interaction, 'vc_need_perms')}"),
                ephemeral=True,
            )
            return

        await set_voice_status(self.bot, target.id, status or None)
        if status:
            await interaction.response.send_message(
                view=_cv(
                    f"### 🎙️ {msg(interaction, 'vc_set_title')}\n{target.mention} → `{status[:100]}`",
                    colour=discord.Colour(0x57f287),
                ),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                view=_cv(
                    f"### 🎙️ {msg(interaction, 'vc_cleared_title')}\n{target.mention}",
                    colour=discord.Colour(0x57f287),
                ),
                ephemeral=True,
            )

    # ── /forward ──────────────────────────────────────────────────────────

    @app_commands.command(
        name="forward",
        description=CMDS.text("forward.description"),
    )
    @app_commands.describe(
        message_id=CMDS.arg("forward", "message_id"),
        source=CMDS.arg("forward", "source"),
        destination=CMDS.arg("forward", "destination"),
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    async def forward(
        self,
        interaction: discord.Interaction,
        message_id: str,
        destination: discord.TextChannel,
        source: discord.TextChannel | None = None,
    ) -> None:
        src = source or interaction.channel
        try:
            mid = int(message_id)
        except ValueError:
            await interaction.response.send_message(
                view=_cv(f"{get_emoji('cross')} {msg(interaction, 'forward_invalid_id')}"),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        result = await forward_message(self.bot, destination.id, src.id, mid)
        if result:
            await interaction.followup.send(
                view=_cv(
                    f"### ↗️ {msg(interaction, 'forward_title')}\n"
                    f"{src.mention} → {destination.mention}",
                    colour=discord.Colour(0x57f287),
                ),
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                view=_cv(f"{get_emoji('cross')} {msg(interaction, 'forward_failed')}"),
                ephemeral=True,
            )

    # ── /sticker ──────────────────────────────────────────────────────────

    sticker_group = app_commands.Group(
        name="sticker",
        description=CMDS.text("sticker.description"),
    )

    @sticker_group.command(name="list", description=CMDS.text("sticker.list.description"))
    @app_commands.guild_only()
    async def sticker_list(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            raw = await self.bot.http.get_all_guild_stickers(interaction.guild_id)
        except Exception as e:
            await interaction.followup.send(view=_cv(f"{get_emoji('cross')} {e}"), ephemeral=True)
            return

        if not raw:
            await interaction.followup.send(
                view=_cv(msg(interaction, "sticker_none")), ephemeral=True
            )
            return

        lines = [
            f"### {get_emoji('star')} "
            + msg(interaction, "sticker_title", server=interaction.guild.name)
        ]
        for s in raw:
            fmt = s.get("format_type", 1)
            fmt_label = {1: "PNG", 2: "APNG", 3: "Lottie", 4: "GIF"}.get(fmt, "?")
            lines.append(f"- **{s['name']}**  `{fmt_label}`  —  *{s.get('description', '')}*")

        await interaction.followup.send(
            view=_cv("\n".join(lines), colour=discord.Colour(0xc8a882)),
            ephemeral=True,
        )

    @sticker_group.command(name="send", description=CMDS.text("sticker.send.description"))
    @app_commands.describe(name=CMDS.arg("sticker.send", "name"))
    @app_commands.guild_only()
    async def sticker_send(self, interaction: discord.Interaction, name: str) -> None:
        await interaction.response.defer()
        try:
            raw = await self.bot.http.get_all_guild_stickers(interaction.guild_id)
        except Exception as e:
            await interaction.followup.send(view=_cv(f"{get_emoji('cross')} {e}"), ephemeral=True)
            return

        match = next((s for s in raw if s["name"].lower() == name.lower()), None)
        if not match:
            await interaction.followup.send(
                view=_cv(f"{get_emoji('cross')} {msg(interaction, 'sticker_not_found', name=name)}"),
                ephemeral=True,
            )
            return

        sticker = await interaction.guild.fetch_sticker(int(match["id"]))
        await interaction.followup.send(stickers=[sticker])

    @sticker_send.autocomplete("name")
    async def sticker_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        try:
            raw = await self.bot.http.get_all_guild_stickers(interaction.guild_id)
            return [
                app_commands.Choice(name=s["name"], value=s["name"])
                for s in raw
                if current.lower() in s["name"].lower()
            ][:25]
        except Exception:
            return []

    # ── /stage speak ──────────────────────────────────────────────────────

    stage_group = app_commands.Group(
        name="stage",
        description=CMDS.text("stage.description"),
    )

    @stage_group.command(name="speak", description=CMDS.text("stage.speak.description"))
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_channels=True)
    async def stage_speak(self, interaction: discord.Interaction) -> None:
        vc = interaction.guild.me.voice
        if not vc or not isinstance(vc.channel, discord.StageChannel):
            await interaction.response.send_message(
                view=_cv(f"{get_emoji('cross')} {msg(interaction, 'stage_not_in_stage')}"),
                ephemeral=True,
            )
            return

        await stage_become_speaker(self.bot, interaction.guild_id, vc.channel.id)
        await interaction.response.send_message(
            view=_cv(
                f"### 🎙️ {msg(interaction, 'stage_speaker')}",
                colour=discord.Colour(0x57f287),
            ),
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NitroFeatures(bot))
