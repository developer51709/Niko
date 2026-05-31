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

import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands

from config.emojis import get_emoji
from utils.discord_extras import burst_react, forward_message, set_voice_status, stage_become_speaker


def _cv(text: str, *, colour: discord.Colour | None = None) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    kw: dict = {}
    if colour:
        kw["accent_colour"] = colour
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text), **kw))
    return view


# ── AI helper (optional) ──────────────────────────────────────────────────────

def _try_ai_reply(bot: commands.Bot, user_id: int, guild, content: str, username: str) -> str | None:
    """Attempt a synchronous AI reply. Returns None if AI is not configured."""
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            from utils.ai.openai_client import generate_reply_openai
            from utils.ai.config import get_personality
            personality = "cafe"
            SYSTEM = (
                "You are Niko, a cozy café AI companion. You are warm, friendly, and a little playful. "
                "Keep responses short and conversational — this is a Discord context menu reply."
            )
            reply = generate_reply_openai(bot, user_id, guild, content, username, SYSTEM)
            return reply
        except Exception:
            pass

    niko_key = os.environ.get("NIKO_API_KEY") or os.environ.get("NIKOAPI_KEY")
    if niko_key:
        try:
            from utils.ai.nikoapi import generate_reply_nikoapi
            SYSTEM = (
                "You are Niko, a cozy café AI companion. Keep replies short and warm."
            )
            reply = generate_reply_nikoapi(bot, user_id, guild, content, username, SYSTEM)
            return reply
        except Exception:
            pass

    return None


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

        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(
            None,
            lambda: _try_ai_reply(
                self.bot,
                interaction.user.id,
                interaction.guild,
                prompt,
                interaction.user.display_name,
            ),
        )

        if reply:
            await interaction.followup.send(
                view=_cv(f"### ☕ Niko says…\n{reply}", colour=discord.Colour(0xc8a882)),
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                view=_cv(
                    "☕ My AI isn't set up yet — ask an admin to add the `OPENAI_API_KEY` secret!\n"
                    f"-# Message by {message.author.mention}: *{content[:120]}*",
                    colour=discord.Colour(0xfee75c),
                ),
                ephemeral=True,
            )

    # ── Context menu: User Profile ────────────────────────────────────────

    async def _user_profile_ctx(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ) -> None:
        """Right-click a user → quick profile card with level + economy stats."""
        await interaction.response.defer(ephemeral=True)

        lines: list[str] = [f"### {get_emoji('icon_user')} {member.display_name}"]

        # Level stats
        try:
            row = await self.bot.cxn.fetchrow(
                "SELECT xp, level FROM user_levels WHERE guild_id = $1 AND user_id = $2",
                interaction.guild_id, member.id,
            )
            if row:
                lines.append(f"**Level:** {row['level']}  •  **XP:** {row['xp']}")
        except Exception:
            pass

        # Economy stats
        try:
            eco = await self.bot.cxn.fetchrow(
                "SELECT balance, bank FROM economy WHERE guild_id = $1 AND user_id = $2",
                interaction.guild_id, member.id,
            )
            if eco:
                lines.append(f"**Wallet:** {eco['balance']:,} ☕  •  **Bank:** {eco['bank']:,} ☕")
        except Exception:
            pass

        # Basic info
        lines.append(f"-# Joined: {discord.utils.format_dt(member.joined_at, 'R') if member.joined_at else 'unknown'}")
        lines.append(f"-# Account: {discord.utils.format_dt(member.created_at, 'R')}")

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
        description="Set or clear the text status shown in a voice channel.",
    )
    @app_commands.describe(
        status="Text to display (leave blank to clear)",
        channel="Voice channel to update (defaults to the one you're in)",
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
                view=_cv(f"{get_emoji('icon_cross')} Join a voice channel or specify one with the `channel` option."),
                ephemeral=True,
            )
            return

        # Permission check
        me = interaction.guild.me
        perms = target.permissions_for(me)
        if not perms.manage_channels:
            await interaction.response.send_message(
                view=_cv(f"{get_emoji('icon_cross')} I need the **Manage Channels** permission to set voice status."),
                ephemeral=True,
            )
            return

        await set_voice_status(self.bot, target.id, status or None)
        if status:
            await interaction.response.send_message(
                view=_cv(
                    f"### 🎙️ Voice Status Set\n{target.mention} → `{status[:100]}`",
                    colour=discord.Colour(0x57f287),
                ),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                view=_cv(f"### 🎙️ Voice Status Cleared\n{target.mention}", colour=discord.Colour(0x57f287)),
                ephemeral=True,
            )

    # ── /forward ──────────────────────────────────────────────────────────

    @app_commands.command(
        name="forward",
        description="Forward a message (by ID) to another channel.",
    )
    @app_commands.describe(
        message_id="ID of the message to forward",
        source="Channel the message is in (defaults to current)",
        destination="Channel to forward to",
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
                view=_cv("❌ Invalid message ID."), ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        result = await forward_message(self.bot, destination.id, src.id, mid)
        if result:
            await interaction.followup.send(
                view=_cv(
                    f"### ↗️ Message Forwarded\nFrom {src.mention} → {destination.mention}",
                    colour=discord.Colour(0x57f287),
                ),
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                view=_cv("❌ Could not forward that message. Check that I have permission to send in the destination channel and the message exists."),
                ephemeral=True,
            )

    # ── /sticker ──────────────────────────────────────────────────────────

    sticker_group = app_commands.Group(
        name="sticker",
        description="Manage and send guild stickers.",
    )

    @sticker_group.command(name="list", description="List all stickers in this server.")
    @app_commands.guild_only()
    async def sticker_list(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            raw = await self.bot.http.get_all_guild_stickers(interaction.guild_id)
        except Exception as e:
            await interaction.followup.send(view=_cv(f"❌ {e}"), ephemeral=True)
            return

        if not raw:
            await interaction.followup.send(
                view=_cv("This server has no custom stickers yet."), ephemeral=True
            )
            return

        lines = [f"### {get_emoji('icon_star')} Server Stickers — {interaction.guild.name}"]
        for s in raw:
            fmt = s.get("format_type", 1)
            fmt_label = {1: "PNG", 2: "APNG", 3: "Lottie", 4: "GIF"}.get(fmt, "?")
            lines.append(f"- **{s['name']}**  `{fmt_label}`  —  *{s.get('description', '')}*")

        await interaction.followup.send(
            view=_cv("\n".join(lines), colour=discord.Colour(0xc8a882)),
            ephemeral=True,
        )

    @sticker_group.command(name="send", description="Send a server sticker into this channel.")
    @app_commands.describe(name="Name of the sticker to send")
    @app_commands.guild_only()
    async def sticker_send(self, interaction: discord.Interaction, name: str) -> None:
        await interaction.response.defer()
        try:
            raw = await self.bot.http.get_all_guild_stickers(interaction.guild_id)
        except Exception as e:
            await interaction.followup.send(view=_cv(f"❌ {e}"), ephemeral=True)
            return

        match = next((s for s in raw if s["name"].lower() == name.lower()), None)
        if not match:
            await interaction.followup.send(
                view=_cv(f"❌ No sticker named **{name}** found. Use `/sticker list`."),
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

    # ── /burst ────────────────────────────────────────────────────────────

    @app_commands.command(
        name="burst",
        description="Send a Nitro-style burst/super reaction on a message.",
    )
    @app_commands.describe(
        message_id="ID of the message to burst-react on",
        emoji="Emoji to burst-react with (e.g. ⭐ or 🎉)",
    )
    @app_commands.guild_only()
    async def burst(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str = "⭐",
    ) -> None:
        try:
            mid = int(message_id)
        except ValueError:
            await interaction.response.send_message(
                view=_cv("❌ Invalid message ID."), ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        await burst_react(self.bot, interaction.channel_id, mid, emoji)
        await interaction.followup.send(
            view=_cv(f"### {emoji} Burst reaction sent! ✨", colour=discord.Colour(0xfee75c)),
            ephemeral=True,
        )

    # ── /stage speak ──────────────────────────────────────────────────────

    stage_group = app_commands.Group(
        name="stage",
        description="Stage channel controls.",
    )

    @stage_group.command(name="speak", description="Make Niko a speaker on the current Stage channel.")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_channels=True)
    async def stage_speak(self, interaction: discord.Interaction) -> None:
        vc = interaction.guild.me.voice
        if not vc or not isinstance(vc.channel, discord.StageChannel):
            await interaction.response.send_message(
                view=_cv("❌ Niko must be in a Stage channel first."), ephemeral=True
            )
            return

        await stage_become_speaker(self.bot, interaction.guild_id, vc.channel.id)
        await interaction.response.send_message(
            view=_cv("### 🎙️ Niko is now a speaker on Stage! ☕", colour=discord.Colour(0x57f287)),
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NitroFeatures(bot))
