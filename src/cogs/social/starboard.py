"""
Starboard — repost popular messages to a starboard channel based on ⭐ reactions.

Commands (single `starboard` group, manage_guild required):
    starboard channel <channel>  — set the starboard channel
    starboard threshold <n>      — set the star threshold (default 3)
    starboard emoji <emoji>      — set the trigger emoji (default ⭐)
    starboard ignore <channel>   — ignore a channel (no starring from it)
    starboard unignore <channel> — stop ignoring a channel
    starboard disable            — turn the starboard off
    starboard config             — show current config
"""

from __future__ import annotations

import json

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.blacklist_manager import BlacklistManager
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

DEFAULT_THRESHOLD = 3
DEFAULT_EMOJI = "⭐"


MESSAGES = load_locales("cogs.social", "starboard")


msg = make_flat_msg(MESSAGES)


def cv2(text: str) -> discord.ui.LayoutView:
    v = discord.ui.LayoutView()
    v.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return v


class Starboard(commands.Cog):
    """Star-based highlight wall for popular messages."""

    def __init__(self, bot):
        self.bot = bot
        self.data = {"guilds": {}, "starred": {}}

    async def cog_load(self):
        """Load settings and active post IDs from the primary database."""
        configs = await self.bot.cxn.fetch(
            "SELECT guild_id, channel_id, threshold, emoji, ignored_channels "
            "FROM starboard_config"
        )
        for row in configs:
            try:
                ignored = json.loads(row["ignored_channels"] or "[]")
            except (TypeError, ValueError):
                ignored = []
            self.data["guilds"][str(row["guild_id"])] = {
                "channel_id": row["channel_id"],
                "threshold": row["threshold"],
                "emoji": row["emoji"],
                "ignored_channels": ignored if isinstance(ignored, list) else [],
            }

        posts = await self.bot.cxn.fetch(
            "SELECT guild_id, message_id, starboard_message_id FROM starboard_messages"
        )
        for row in posts:
            self.data["starred"].setdefault(str(row["guild_id"]), {})[
                str(row["message_id"])
            ] = row["starboard_message_id"]

    async def _save_config(self, guild_id: int):
        config = self._g(guild_id)
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO starboard_config "
            "(guild_id, channel_id, threshold, emoji, ignored_channels) "
            "VALUES ($1, $2, $3, $4, $5)",
            guild_id,
            config["channel_id"],
            config["threshold"],
            config["emoji"],
            json.dumps(config["ignored_channels"]),
        )

    async def _save_starred(self, guild_id: int, message_id: int, starboard_message_id: int):
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO starboard_messages "
            "(guild_id, message_id, starboard_message_id) VALUES ($1, $2, $3)",
            guild_id, message_id, starboard_message_id,
        )

    async def _delete_starred(self, guild_id: int, message_id: int):
        await self.bot.cxn.execute(
            "DELETE FROM starboard_messages WHERE guild_id = $1 AND message_id = $2",
            guild_id, message_id,
        )

    def _g(self, gid: int) -> dict:
        return self.data["guilds"].setdefault(str(gid), {
            "channel_id": None,
            "threshold": DEFAULT_THRESHOLD,
            "emoji": DEFAULT_EMOJI,
            "ignored_channels": [],
        })

    @commands.hybrid_group(
        name="starboard",
        description=CMDS.text("starboard.description"),
        help=CMDS.help("starboard"),
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def starboard(self, ctx: commands.Context):
        help_cmd = self.bot.get_command("help")
        if help_cmd is None:
            return await ctx.send_help(self.starboard)
        await ctx.invoke(help_cmd, command_name="starboard")

    @starboard.command(
        name="channel",
        description=CMDS.text("starboard.channel.description"),
        help=CMDS.help("starboard.channel"),
    )
    async def starboard_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        g = self._g(ctx.guild.id)
        g["channel_id"] = channel.id
        await self._save_config(ctx.guild.id)
        await ctx.send(view=cv2(msg(ctx, "channel_set", channel=channel.mention)))

    @starboard.command(
        name="threshold",
        description=CMDS.text("starboard.threshold.description"),
        help=CMDS.help("starboard.threshold"),
    )
    async def starboard_threshold(self, ctx: commands.Context, count: int):
        count = max(1, min(50, count))
        g = self._g(ctx.guild.id)
        g["threshold"] = count
        await self._save_config(ctx.guild.id)
        await ctx.send(view=cv2(msg(ctx, "threshold_set", n=count)))

    @starboard.command(
        name="emoji",
        description=CMDS.text("starboard.emoji.description"),
        help=CMDS.help("starboard.emoji"))
    async def starboard_emoji(self, ctx: commands.Context, emoji: str):
        g = self._g(ctx.guild.id)
        g["emoji"] = emoji
        await self._save_config(ctx.guild.id)
        await ctx.send(view=cv2(msg(ctx, "emoji_set", emoji=emoji)))

    @starboard.command(
        name="ignore",
        description=CMDS.text("starboard.ignore.description"),
        help=CMDS.help("starboard.ignore"),
    )
    async def starboard_ignore(self, ctx: commands.Context, channel: discord.TextChannel):
        g = self._g(ctx.guild.id)
        if channel.id not in g["ignored_channels"]:
            g["ignored_channels"].append(channel.id)
            await self._save_config(ctx.guild.id)
        await ctx.send(view=cv2(msg(ctx, "ignored", channel=channel.mention)))

    @starboard.command(
        name="unignore",
        description=CMDS.text("starboard.unignore.description"),
        help=CMDS.help("starboard.unignore"),
    )
    async def starboard_unignore(self, ctx: commands.Context, channel: discord.TextChannel):
        g = self._g(ctx.guild.id)
        if channel.id in g["ignored_channels"]:
            g["ignored_channels"].remove(channel.id)
            await self._save_config(ctx.guild.id)
        await ctx.send(view=cv2(msg(ctx, "unignored", channel=channel.mention)))

    @starboard.command(
        name="disable",
        description=CMDS.text("starboard.disable.description"),
        help=CMDS.help("starboard.disable"),
    )
    async def starboard_disable(self, ctx: commands.Context):
        g = self._g(ctx.guild.id)
        g["channel_id"] = None
        await self._save_config(ctx.guild.id)
        await ctx.send(view=cv2(msg(ctx, "disabled")))

    @starboard.command(
        name="config",
        description=CMDS.text("starboard.config.description"),
        help=CMDS.help("starboard.config"),
    )
    async def starboard_config(self, ctx: commands.Context):
        g = self._g(ctx.guild.id)
        ch = ctx.guild.get_channel(g["channel_id"]) if g.get("channel_id") else None
        ignored = ", ".join(f"<#{c}>" for c in g["ignored_channels"]) or "—"
        body = msg(ctx, "config_title", icon=get_emoji("settings")) + "\n" + msg(
            ctx, "config_body",
            channel=ch.mention if ch else "—",
            threshold=g["threshold"],
            emoji=g["emoji"],
            ignored=ignored,
        )
        await ctx.send(view=cv2(body))

    # ───── reaction handler ───────────────────────

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self._on_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self._on_reaction(payload)

    async def _on_reaction(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id:
            return
        # Blacklisting a server clears its saved starboard channel, so the guild
        # is already inert here; the explicit check covers the moment between the
        # blacklist write and that step, and any guild locked before a restart.
        if BlacklistManager().is_guild_blacklisted(int(payload.guild_id)):
            return
        g = self.data["guilds"].get(str(payload.guild_id))
        if not g or not g.get("channel_id"):
            return
        emoji_str = str(payload.emoji)
        if emoji_str != g.get("emoji", DEFAULT_EMOJI):
            return
        if payload.channel_id in g.get("ignored_channels", []):
            return
        if payload.channel_id == g["channel_id"]:
            return  # ignore reactions on the starboard itself

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return
        # Webhook reposts need source-author attribution before the normal bot
        # message filter is applied; regular member messages need no DB lookup.
        uwu_attribution = None
        if message.author.bot or message.webhook_id:
            uwu_attribution = await self.bot.cxn.fetchrow(
                "SELECT author_id, author_name, author_avatar_url, original_created_at "
                "FROM uwulock_messages WHERE message_id = $1",
                message.id,
            )
        if message.author.bot and not uwu_attribution:
            return

        # count the trigger reaction
        count = 0
        for r in message.reactions:
            if str(r.emoji) == g["emoji"]:
                count = r.count
                break

        starboard_ch = guild.get_channel(g["channel_id"])
        if not starboard_ch:
            return

        starred = self.data["starred"].setdefault(str(payload.guild_id), {})
        existing_id = starred.get(str(message.id))

        if count >= g["threshold"]:
            view = self._build_starred_view(message, count, g, uwu_attribution)
            if existing_id:
                try:
                    m = await starboard_ch.fetch_message(int(existing_id))
                    await m.edit(
                        view=view,
                        allowed_mentions=discord.AllowedMentions.none(),
                    )
                    return
                except Exception:
                    pass
            try:
                sent = await starboard_ch.send(
                    view=view,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
                starred[str(message.id)] = sent.id
                await self._save_starred(payload.guild_id, message.id, sent.id)
                self.bot.dispatch("sticky_feature_message", payload.guild_id, starboard_ch.id)
            except Exception:
                pass
        else:
            # below threshold — remove if present
            if existing_id:
                try:
                    m = await starboard_ch.fetch_message(int(existing_id))
                    await m.delete()
                except Exception:
                    pass
                starred.pop(str(message.id), None)
                await self._delete_starred(payload.guild_id, message.id)

    def _build_starred_view(
        self,
        message: discord.Message,
        count: int,
        g: dict,
        uwu_attribution=None,
    ) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView(timeout=None)

        header = msg(message.guild, "starred",
                     emoji=g.get("emoji", DEFAULT_EMOJI),
                     count=count,
                     channel=message.channel.mention)

        if uwu_attribution:
            author_name = uwu_attribution["author_name"]
            author_id = int(uwu_attribution["author_id"])
            created_at = int(uwu_attribution["original_created_at"])
            # The source message is replaced by this webhook post; link to
            # the live transformed copy rather than the deleted original.
            jump_url = message.jump_url
            author_line = (
                f"**{discord.utils.escape_markdown(author_name)}** (<@{author_id}>) · "
                f"<t:{created_at}:R> · UwU-locked message"
            )
            author_avatar_url = uwu_attribution.get("author_avatar_url")
            author_display = (
                discord.ui.Section(
                    discord.ui.TextDisplay(content=author_line),
                    accessory=discord.ui.Thumbnail(author_avatar_url),
                )
                if author_avatar_url
                else discord.ui.TextDisplay(content=author_line)
            )
        else:
            author_line = (
                f"**{message.author.display_name}** · "
                f"<t:{int(message.created_at.timestamp())}:R>"
            )
            jump_url = message.jump_url

        body_parts = [f"### {header}"]
        if message.content:
            txt = message.content
            if len(txt) > 1500:
                txt = txt[:1500] + "…"
            body_parts.append(txt)

        body_parts.append(f"[Jump to message]({jump_url})")

        if uwu_attribution:
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=body_parts[0]),
                author_display,
                *[discord.ui.TextDisplay(content=part) for part in body_parts[1:]],
            )
        else:
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content="\n\n".join([*body_parts[:1], author_line, *body_parts[1:]])
                ),
            )

        # Embed first attachment as media if it's an image
        att_image = None
        for att in message.attachments:
            if (att.content_type or "").startswith("image/") or att.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
                att_image = att.url
                break
        if att_image:
            container.add_item(
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=att_image))
            )

        view.add_item(container)
        return view


async def setup(bot):
    await bot.add_cog(Starboard(bot))
