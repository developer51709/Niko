"""``.staff blacklist`` and ``.staff premium``: the two owner moderation groups."""

import discord
from discord.ext import commands

from config import links
from config.emojis import get_emoji
from cogs.staff.base import CMDS, StaffCommands, _resolve_prefix
from utils.blacklist_manager import BlacklistManager
from utils.paginator import PaginatedView, paginate
from utils.premium_manager import PremiumManager


class ModerationCommands:
    """Blacklist and premium management."""

    # -------------------------------
    # Blacklist commands
    # -------------------------------
    @StaffCommands.staff.group(
        name="blacklist",
        help=CMDS.help("blacklist"),
        invoke_without_command=True,
        hidden=True,
    )
    async def blacklist(self, ctx):
        """Show the current blacklist with reasons and dates."""
        blacklist_manager = BlacklistManager()
        user_entries  = blacklist_manager.get_user_entries()
        guild_entries = blacklist_manager.get_guild_entries()

        def _fmt(entry, kind):
            ts = entry.get("timestamp")
            date_str = f"<t:{int(ts)}:d>" if ts else "—"
            reason = entry.get("reason") or "*no reason given*"
            added_by = entry.get("added_by")
            added_by_str = f"<@{added_by}>" if added_by else "—"
            return (
                f"**{kind}:** `{entry['id']}`\n"
                f"-# Reason: {reason}\n"
                f"-# Added: {date_str} · By: {added_by_str}"
            )

        user_lines  = [_fmt(e, "User")  for e in user_entries]
        guild_lines = [_fmt(e, "Guild") for e in guild_entries]
        lines = user_lines + guild_lines

        if not lines:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('important')} The blacklist is currently empty."
                ),
                accent_colour=discord.Color.blurple()
            )
            view.add_item(container)
            return await ctx.send(view=view)

        pages = paginate(lines, per_page=5)
        view = PaginatedView(
            title=f"🔨 Blacklist\n-# Users: {len(user_lines)} · Guilds: {len(guild_lines)}",
            pages=pages
        )
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # -------------------------------
    # INFO — look up a single entry
    # -------------------------------
    @blacklist.command(
        name="info",
        help=CMDS.help("blacklist.info"),
    )
    async def blacklist_info(self, ctx, type: str, id_or_mention: str):
        bm = BlacklistManager()
        type = type.lower()
        try:
            target_id = int(id_or_mention.strip("<@!>"))
        except ValueError:
            return await ctx.send(f"{get_emoji('cross')} Invalid ID.")

        entry = bm.get_user_entry(target_id) if type == "user" else bm.get_guild_entry(target_id)
        if not entry:
            return await ctx.send(f"{get_emoji('cross')} `{target_id}` is not blacklisted.")

        ts = entry.get("timestamp")
        date_str = f"<t:{int(ts)}:F> (<t:{int(ts)}:R>)" if ts else "Unknown"
        reason = entry.get("reason") or "*no reason given*"
        added_by = entry.get("added_by")
        added_by_str = f"<@{added_by}> (`{added_by}`)" if added_by else "Unknown"

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### 🔨 Blacklist Entry — {type.title()} `{target_id}`"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"**Reason:** {reason}\n**Added:** {date_str}\n**Added by:** {added_by_str}"),
            accent_colour=discord.Color.red(),
        ))
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # -------------------------------
    # REASON — update reason on an existing entry
    # -------------------------------
    @blacklist.command(
        name="reason",
        help=CMDS.help("blacklist.reason"),
    )
    async def blacklist_reason(self, ctx, type: str, id_or_mention: str, *, reason: str):
        bm = BlacklistManager()
        type = type.lower()
        try:
            target_id = int(id_or_mention.strip("<@!>"))
        except ValueError:
            return await ctx.send(f"{get_emoji('cross')} Invalid ID.")

        ok = await (bm.update_user_reason(target_id, reason) if type == "user" else bm.update_guild_reason(target_id, reason))
        if ok:
            await ctx.send(f"{get_emoji('tick')} Reason for `{target_id}` updated.")
        else:
            await ctx.send(f"{get_emoji('cross')} `{target_id}` is not blacklisted.")

    # -------------------------------
    # ADD
    # -------------------------------
    @blacklist.command(
        name="add",
        help=CMDS.help("blacklist.add"),
    )
    async def blacklist_add(self, ctx, type: str, id_or_mention: str, send_message: bool = False, *, reason: str = None):
        """Add a user or guild to the blacklist with an optional reason."""
        blacklist_manager = BlacklistManager()
        type = type.lower()

        # -------------------------------
        # USER ADD
        # -------------------------------
        if type == "user":
            try:
                user_id = int(id_or_mention.strip("<@!>"))
            except ValueError:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Invalid user ID or mention."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if await blacklist_manager.add_user(user_id, reason=reason, added_by=ctx.author.id):
                # Success message
                reason_line = f"\n-# Reason: {reason}" if reason else ""
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} User `{user_id}` added to blacklist.{reason_line}"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)

                # Optional DM
                if send_message:
                    try:
                        user = self.bot.get_user(user_id)
                        if user:
                            view = discord.ui.LayoutView()
                            container = discord.ui.Container(
                                discord.ui.TextDisplay(
                                    content=f"### {get_emoji('danger')} You have been blacklisted from using this bot."
                                ),
                                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                                discord.ui.TextDisplay(
                                    content="This is likely due to repeated violations of the bot's terms of service or abuse of the bot's features."
                                ),
                                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                                discord.ui.TextDisplay(
                                    content=f"-# If you believe this is a mistake, submit a blacklist appeal at {links.WEBSITE}/appeals/blacklist."
                                ),
                                accent_colour=discord.Color.red()
                            )
                            await user.send(view=view)
                    except Exception:
                        view = discord.ui.LayoutView()
                        container = discord.ui.Container(
                            discord.ui.TextDisplay(
                                content=f"{get_emoji('cross')} Failed to send message to user `{user_id}`."
                            ),
                            accent_colour=discord.Color.red()
                        )
                        view.add_item(container)
                        await ctx.send(view=view)

            else:
                # Already blacklisted
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} User `{user_id}` is already blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        # -------------------------------
        # GUILD ADD
        # -------------------------------
        elif type == "guild":
            try:
                guild_id = int(id_or_mention)
            except ValueError:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Invalid guild ID."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if await blacklist_manager.add_guild(guild_id, reason=reason, added_by=ctx.author.id, bot=ctx.bot):
                reason_line = f"\n-# Reason: {reason}" if reason else ""
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} Guild `{guild_id}` added to blacklist.{reason_line}"
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)
            else:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Guild `{guild_id}` is already blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} Invalid type. Use `user` or `guild`."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await ctx.send(view=view)

    # -------------------------------
    # REMOVE
    # -------------------------------
    @blacklist.command(
        name="remove",
        help=CMDS.help("blacklist.remove"),
    )
    async def blacklist_remove(self, ctx, type: str, id_or_mention: str):
        """Remove a user or guild from the blacklist."""
        blacklist_manager = BlacklistManager()
        type = type.lower()

        # -------------------------------
        # USER REMOVE
        # -------------------------------
        if type == "user":
            try:
                user_id = int(id_or_mention.strip("<@!>"))
            except ValueError:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Invalid user ID or mention."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if await blacklist_manager.remove_user(user_id):
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} User `{user_id}` removed from blacklist."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)
            else:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} User `{user_id}` is not blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        # -------------------------------
        # GUILD REMOVE
        # -------------------------------
        elif type == "guild":
            try:
                guild_id = int(id_or_mention)
            except ValueError:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Invalid guild ID."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                return await ctx.send(view=view)

            if await blacklist_manager.remove_guild(guild_id, bot=ctx.bot):
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('tick')} Guild `{guild_id}` removed from blacklist."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                await ctx.send(view=view)
            else:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('cross')} Guild `{guild_id}` is not blacklisted."
                    ),
                    accent_colour=discord.Color.red()
                )
                view.add_item(container)
                await ctx.send(view=view)

        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} Invalid type. Use `user` or `guild`."
                ),
                accent_colour=discord.Color.red()
            )
            view.add_item(container)
            await ctx.send(view=view)

    # -------------------------------
    # Premium management commands
    # -------------------------------
    @StaffCommands.staff.group(
        name="premium",
        help=CMDS.help("premium"),
        invoke_without_command=True,
        hidden=True,
    )
    async def premium(self, ctx):
        """Shows premium subcommand usage."""
        prefix = await _resolve_prefix(self.bot, ctx)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {get_emoji('badge_owner')} Premium Management\n"
                    f"`{prefix}premium add <user>` — grant premium\n"
                    f"`{prefix}premium remove <user>` — revoke premium\n"
                    f"`{prefix}premium list` — list all premium users"
                )
            ),
            accent_colour=discord.Color.gold(),
        ))
        await ctx.send(view=view)

    @premium.command(name="add", help=CMDS.help("premium.add"))
    async def premium_add(self, ctx, user: discord.User):
        added = await PremiumManager.add(self.bot.cxn, user.id)
        if added:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} **{user}** (`{user.id}`) has been granted premium."
                ),
                accent_colour=discord.Color.green(),
            ))
        else:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('important')} **{user}** already has premium."
                ),
                accent_colour=discord.Color.blurple(),
            ))
        await ctx.send(view=view)

    @premium.command(name="remove", help=CMDS.help("premium.remove"))
    async def premium_remove(self, ctx, user: discord.User):
        removed = await PremiumManager.remove(self.bot.cxn, user.id)
        if removed:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('tick')} Premium revoked from **{user}** (`{user.id}`)."
                ),
                accent_colour=discord.Color.green(),
            ))
        else:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('cross')} **{user}** does not have premium."
                ),
                accent_colour=discord.Color.red(),
            ))
        await ctx.send(view=view)

    @premium.command(name="list", help=CMDS.help("premium.list"))
    async def premium_list(self, ctx):
        user_ids = await PremiumManager.list_users(self.bot.cxn)
        if not user_ids:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"{get_emoji('important')} No premium users yet."
                ),
                accent_colour=discord.Color.blurple(),
            ))
            return await ctx.send(view=view)

        lines = []
        for uid in user_ids:
            user = self.bot.get_user(uid)
            if not user:
                try:
                    user = await self.bot.fetch_user(uid)
                except discord.NotFound:
                    user = None
            label = f"**{user}** (`{uid}`)" if user else f"`{uid}`"
            lines.append(f"• {label}")

        pages = paginate(lines, per_page=10)
        view = PaginatedView(
            title=f"⭐ Premium Users — {len(user_ids)} total",
            pages=pages,
        )
        await ctx.send(view=view)
