import asyncio
import time

import database
from .formatters import *


LOG_WEBHOOK_NAME = "Niko | Server Logs"

#: How long a loaded logging config is reused before it is read again. Every
#: single log event used to re-read the whole table (and on MongoDB iterate the
#: whole collection), because the config was reloaded unconditionally at the
#: top of log_event.
CONFIG_TTL = 30.0

#: Deleted-message attachments are re-uploaded into the log, so they are capped:
#: a mass delete of large files would otherwise download them all again.
MAX_LOG_FILES = 5
MAX_LOG_FILE_BYTES = 2_000_000

class ServerLogger(commands.Cog):
    """Multi-channel server event logging."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Logging config lives in the database (logging_config); loaded on demand
        # and reused for CONFIG_TTL so one event is not one table read.
        self._config: dict = {}
        self._config_at: float = 0.0
        self._config_lock = asyncio.Lock()
        # guild_id → {invite_code: uses_count}
        self._invite_cache: dict[int, dict[str, int]] = {}
        self._webhook_cache: dict[tuple[int, int], discord.Webhook] = {}
        self._webhook_locks: dict[tuple[int, int], asyncio.Lock] = {}
        self._deleted_webhooks: set[int] = set()

    @commands.Cog.listener()
    async def on_ready(self):
        """Populate invite cache for all guilds on startup."""
        for guild in self.bot.guilds:
            try:
                invites = await guild.invites()
                self._invite_cache[guild.id] = {inv.code: inv.uses for inv in invites}
            except (discord.Forbidden, discord.HTTPException):
                pass
            # Cache vanity invite uses separately under __vanity__
            if guild.vanity_url_code:
                try:
                    vanity = await guild.vanity_invite()
                    if vanity and vanity.uses is not None:
                        self._invite_cache.setdefault(guild.id, {})["__vanity__"] = vanity.uses
                except (discord.Forbidden, discord.HTTPException, discord.NotFound):
                    pass

    def _get_cfg(self, guild_id: int) -> dict:
        return _guild_config(self._config, guild_id)

    def invalidate(self) -> None:
        """Drop the cached config so the next event reads it again."""
        self._config_at = 0.0

    async def config(self) -> dict:
        """The loaded logging config, refreshed at most once per CONFIG_TTL.

        A failed read keeps the last good copy: returning `{}` (which is what
        `_load_log_config` does by default) looked like "no category is
        configured" and silently dropped every event for a whole outage.
        """
        if self._config_at and time.monotonic() - self._config_at < CONFIG_TTL:
            return self._config
        async with self._config_lock:
            if self._config_at and time.monotonic() - self._config_at < CONFIG_TTL:
                return self._config
            try:
                fresh = await _load_log_config(raise_on_error=True)
            except Exception as error:
                logging.warning(
                    "logging_cog",
                    f"Could not reload the logging config ({error}); keeping the last copy",
                )
                self._config_at = time.monotonic()
                return self._config
            # An empty result from a bot in thousands of guilds means a failed
            # read, not that every server cleared its channels.
            if fresh or not self._config:
                self._config = fresh
            self._config_at = time.monotonic()
        return self._config

    async def _reload(self):
        """Force a fresh read, for the `/logging` panel and its status view."""
        self.invalidate()
        return await self.config()

    async def save_config(self, guild: discord.Guild, cfg: dict, *, actor=None,
                          summary: str = "", before: dict | None = None) -> None:
        """Persist one guild's logging config, then announce the change.

        The announcement goes to the channels that were configured before the
        change, so redirecting or clearing a category cannot quietly stop the
        logs the people watching that channel rely on.
        """
        await _save_guild_log_config(guild.id, cfg)
        self._config[str(guild.id)] = cfg
        self.invalidate()
        await self._audit_logging_change(guild, before, actor=actor, summary=summary)

    async def _audit_logging_change(self, guild: discord.Guild, before: dict | None,
                                    *, actor=None, summary: str = "") -> None:
        """Record a logging-config change in the channels it affected."""
        if before is None:
            return
        channels = {before.get(key) for key in CATEGORIES if before.get(key)}
        if not channels:
            return
        lines = [f"**Action:** Logging configuration changed"]
        if actor is not None:
            lines.append(f"**Changed by:** {getattr(actor, 'mention', actor)}")
        if summary:
            lines.append(f"**Change:** {summary}")
        for channel_id in list(channels)[:3]:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue
            await self._send_entry(
                guild, channel, "server", "Logging Updated", "\n".join(lines))

    # ── Core logging method ───────────────────────

    async def log_event(
        self,
        guild: discord.Guild,
        category: str,
        title: str,
        body: str,
        target_id: int | None = None,
        action_key: str | None = None,
        channel_id: int | None = None,
        media_urls: list[str] | None = None,
        thumbnail_url: str | None = None,
        files: list[discord.File] | None = None,
    ):
        """Send a structured log entry to the configured channel for the given category.

        media_urls renders image URLs in a MediaGallery inside the log container;
        thumbnail_url renders the body in a Section with a Thumbnail accessory;
        files renders discord.ui.File components inside the log container (the
        bytes are uploaded alongside the message via send(files=...)).
        """
        await self.config()
        cfg = self._get_cfg(guild.id)

        if category in cfg.get("disabled", []):
            return

        log_channel_id = cfg.get(category)
        if not log_channel_id:
            return

        channel = guild.get_channel(log_channel_id)
        if not channel:
            return

        await self._send_entry(
            guild, channel, category, title, body,
            target_id=target_id, action_key=action_key, channel_id=channel_id,
            media_urls=media_urls, thumbnail_url=thumbnail_url, files=files,
        )

    async def _send_entry(
        self,
        guild: discord.Guild,
        channel: discord.abc.Messageable,
        category: str,
        title: str,
        body: str,
        *,
        target_id: int | None = None,
        action_key: str | None = None,
        channel_id: int | None = None,
        media_urls: list[str] | None = None,
        thumbnail_url: str | None = None,
        files: list[discord.File] | None = None,
    ) -> None:
        """Post one log entry to a specific channel.

        Webhooks are preferred (their own rate-limit bucket), but a server that
        has not granted Manage Webhooks, or a channel that cannot own a webhook
        such as a thread, still gets its log: the entry falls back to the bot
        account instead of being dropped.
        """
        view = _build_log_view(
            category=category,
            title=title,
            body=body,
            guild_id=guild.id,
            target_id=target_id,
            action_key=action_key or title,
            channel_id=channel_id,
            media_urls=media_urls,
            thumbnail_url=thumbnail_url,
            files=files,
        )
        try:
            await log_channel_limiter.acquire((guild.id, getattr(channel, "id", 0)))
            webhook = await self._get_log_webhook(channel)
            if webhook is None:
                await self._send_with_bot(channel, view, files)
                return
            try:
                await webhook.send(
                    view=view,
                    files=files or [],
                    username=LOG_WEBHOOK_NAME,
                    avatar_url=self.bot.user.display_avatar.url,
                    allowed_mentions=discord.AllowedMentions.none(),
                    wait=True,
                )
            except discord.NotFound:
                # Remove only this stale webhook under the channel lock. A
                # concurrent event may already have replaced it.
                key = (guild.id, channel.id)
                lock = self._webhook_locks.setdefault(key, asyncio.Lock())
                async with lock:
                    self._deleted_webhooks.add(webhook.id)
                    self._webhook_cache.pop(key, None)
                    pool = getattr(database, "_shared_pool", None)
                    if pool is not None:
                        await pool.execute(
                            "DELETE FROM logging_webhooks WHERE guild_id = $1 AND channel_id = $2",
                            guild.id,
                            channel.id,
                        )
                webhook = await self._get_log_webhook(channel)
                if webhook is None:
                    await self._send_with_bot(channel, view, files)
                    return
                for file in files or []:
                    file.reset(seek=True)
                await webhook.send(
                    view=view,
                    files=files or [],
                    username=LOG_WEBHOOK_NAME,
                    avatar_url=self.bot.user.display_avatar.url,
                    allowed_mentions=discord.AllowedMentions.none(),
                    wait=True,
                )
        except Exception as e:
            logging.error("logging_cog", f"Failed to send log message to {channel} in {guild}: {e}")

    async def _send_with_bot(self, channel: discord.abc.Messageable,
                             view: discord.ui.LayoutView,
                             files: list[discord.File] | None = None) -> None:
        """Send a log entry as the bot itself, the fallback without webhooks."""
        for file in files or []:
            file.reset(seek=True)
        await channel.send(
            view=view,
            files=files or [],
            allowed_mentions=discord.AllowedMentions.none(),
        )

    async def _get_log_webhook(self, channel) -> discord.Webhook | None:
        """Return the persisted log webhook for a channel, replacing it if deleted.

        Only real text channels can own a webhook; threads, announcement
        channels and categories return None so the caller falls back to sending
        the entry as the bot.
        """
        if not isinstance(channel, discord.TextChannel):
            return None
        key = (channel.guild.id, channel.id)
        lock = self._webhook_locks.setdefault(key, asyncio.Lock())
        async with lock:
            webhook = self._webhook_cache.get(key)
            if webhook and webhook.id not in self._deleted_webhooks:
                return webhook
            self._webhook_cache.pop(key, None)

            pool = getattr(database, "_shared_pool", None)
            if pool is None:
                return None
            row = await pool.fetchrow(
                "SELECT webhook_id, token FROM logging_webhooks WHERE guild_id = $1 AND channel_id = $2",
                channel.guild.id,
                channel.id,
            )
            if row:
                try:
                    webhook = discord.Webhook.partial(
                        int(row["webhook_id"]), row["token"], client=self.bot
                    )
                    await webhook.fetch()
                    if webhook.id not in self._deleted_webhooks:
                        self._webhook_cache[key] = webhook
                        return webhook
                except (discord.NotFound, discord.Forbidden):
                    pass
                except discord.HTTPException as exc:
                    if exc.status != 401:
                        raise

            try:
                avatar = await self.bot.user.display_avatar.read()
                webhook = await channel.create_webhook(
                    name=LOG_WEBHOOK_NAME,
                    avatar=avatar,
                    reason="Automatically created for server event logs",
                )
            except discord.Forbidden:
                logging.warning(
                    "logging_cog",
                    f"Cannot create log webhook in {channel} for {channel.guild}: missing Manage Webhooks permission",
                )
                return None
            except discord.HTTPException as error:
                # A thread or an announcement channel cannot own a webhook; the
                # entry is still delivered through the bot account.
                logging.warning(
                    "logging_cog",
                    f"Cannot create log webhook in {channel} ({error}); falling back to a normal message",
                )
                return None

            if not webhook.token:
                logging.error("logging_cog", f"Created log webhook in {channel} without a token; cannot persist it")
                return None
            await pool.execute(
                "INSERT OR REPLACE INTO logging_webhooks (guild_id, channel_id, webhook_id, token) VALUES ($1, $2, $3, $4)",
                channel.guild.id,
                channel.id,
                webhook.id,
                webhook.token,
            )
            self._deleted_webhooks.discard(webhook.id)
            self._webhook_cache[key] = webhook
            return webhook

    #Backward-compat wrapper used by moderation_utils

    async def log_action(
        self,
        guild: discord.Guild,
        title: str,
        description: str,
        target: discord.Member | discord.User | None = None,
        moderator: discord.Member | None = None,
    ):
        """Drop-in replacement for the old ModerationUtils.log_action."""
        # Determine category from title
        category = _TITLE_CATEGORY.get(title)
        if not category:
            if any(s in title for s in _AUTOMOD_SUBSTRINGS):
                category = "automod"
            else:
                category = "moderation"

        body = description
        if moderator and f"{moderator}" not in description:
            body += f"\n**Moderator:** {moderator.mention}"

        target_id = target.id if target else None
        await self.log_event(guild, category, title, body, target_id=target_id, action_key=title)

    # ── Gateway event listeners ───────────────────

    async def _audit_entry(self, guild: discord.Guild, action, target_id: int,
                           *, window: float = 15.0):
        """The audit entry for *this* action on *this* target, or None.

        Every attribution used to take "the first entry in the last few", with
        no target and no recency check, so two moderators acting within a second
        swapped names and a stale entry could blame somebody who did nothing.
        Audit entries arrive newest first, so the first entry older than the
        window ends the search.
        """
        try:
            async for entry in guild.audit_logs(limit=6, action=action):
                target = getattr(entry, "target", None)
                if target is not None and getattr(target, "id", None) != target_id:
                    continue
                age = (discord.utils.utcnow() - entry.created_at).total_seconds()
                if age > window:
                    break
                return entry
        except (discord.Forbidden, discord.HTTPException):
            return None
        return None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        created = member.created_at.strftime("%Y-%m-%d")
        account_age = (datetime.now(timezone.utc) - member.created_at).days
        age_warn = f"\n-# {get_emoji('danger')} New account — only **{account_age}d** old" if account_age < 7 else ""

        # ── Detect which invite was used ──────────
        used_invite = None
        used_vanity = False

        try:
            current_invites = await guild.invites()
            cached = self._invite_cache.get(guild.id, {})
            for inv in current_invites:
                if inv.uses > cached.get(inv.code, 0):
                    used_invite = inv
                    break
            # Rebuild cache but preserve the __vanity__ counter
            new_cache = {inv.code: inv.uses for inv in current_invites}
            if "__vanity__" in cached:
                new_cache["__vanity__"] = cached["__vanity__"]
            self._invite_cache[guild.id] = new_cache
        except (discord.Forbidden, discord.HTTPException):
            pass

        # If no regular invite matched, check the vanity invite
        if not used_invite and guild.vanity_url_code:
            try:
                vanity = await guild.vanity_invite()
                if vanity and vanity.uses is not None:
                    cached_vanity = self._invite_cache.get(guild.id, {}).get("__vanity__", 0)
                    if vanity.uses > cached_vanity:
                        used_vanity = True
                        self._invite_cache.setdefault(guild.id, {})["__vanity__"] = vanity.uses
            except (discord.Forbidden, discord.HTTPException, discord.NotFound):
                pass

        # ── Build join-method label ───────────────
        if used_invite:
            join_method = f"Invite `{used_invite.code}`"
        elif used_vanity:
            join_method = f"Vanity URL (`/{guild.vanity_url_code}`)"
        else:
            join_method = "Unknown — OAuth2, Server Discovery, or deleted invite"

        # ── Log to invites category ───────────────
        if used_invite:
            inv_body = (
                f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Invite Code:** `{used_invite.code}`\n"
                f"**Created By:** {used_invite.inviter.mention if used_invite.inviter else 'Unknown'}\n"
                f"**Total Uses:** {used_invite.uses}"
            )
            await self.log_event(
                guild, "invites", "Invite Used", inv_body,
                target_id=member.id
            )
        elif used_vanity:
            vanity_body = (
                f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Join Method:** Vanity URL (`/{guild.vanity_url_code}`)"
            )
            await self.log_event(
                guild, "invites", "Vanity Invite Used", vanity_body,
                target_id=member.id
            )
        else:
            unknown_body = (
                f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Join Method:** Unknown — likely OAuth2 authorization, Server Discovery, or a deleted invite"
            )
            await self.log_event(
                guild, "invites", "Unknown Join Method", unknown_body,
                target_id=member.id
            )

        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Account Created:** {created} ({account_age} days ago){age_warn}\n"
            f"**Join Method:** {join_method}"
        )
        await self.log_event(
            guild, "members", "Member Joined", body,
            target_id=member.id, action_key="member_join"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild

        # ── Was this a kick or a ban rather than a plain leave? ──
        # Only kicks used to be checked, so a banned member also appeared as
        # "Member Left" with no reason on top of the Ban entry.
        kick = await self._audit_entry(
            guild, discord.AuditLogAction.kick, member.id)
        if kick is not None and kick.user != self.bot.user:
            body = (
                f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Action:** Kick\n"
                f"**Reason:** {kick.reason or 'No reason provided'}\n"
                f"**Moderator:** {kick.user.mention if kick.user else 'Unknown'}"
            )
            await self.log_event(
                guild, "moderation", "Kick", body,
                target_id=member.id, action_key="Kick"
            )
            return

        # A ban already has its own listener; the member must not also show up
        # as having left on their own.
        if await self._audit_entry(guild, discord.AuditLogAction.ban, member.id) is not None:
            return

        roles = [r.mention for r in member.roles if r != guild.default_role]
        roles_text = ", ".join(roles) if roles else "None"
        joined_at = getattr(member, "joined_at", None)
        tenure = (
            f"\n**Joined:** <t:{int(joined_at.timestamp())}:R>" if joined_at else ""
        )
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Roles:** {roles_text}{tenure}"
        )
        await self.log_event(
            guild, "members", "Member Left", body,
            target_id=member.id,
            thumbnail_url=self._avatar_url(member),
        )

    @staticmethod
    def _avatar_url(user) -> str | None:
        """A member-scoped entry shows the avatar as a thumbnail."""
        try:
            return user.display_avatar.url
        except Exception:
            return None

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild = after.guild

        # ── Avatar change (global or server avatar) ──
        def _asset_url(asset) -> str | None:
            return asset.url if asset else None

        avatar_changed = (
            _asset_url(before.avatar) != _asset_url(after.avatar)
            or _asset_url(before.guild_avatar) != _asset_url(after.guild_avatar)
        )
        if avatar_changed:
            old_avatar = (
                _asset_url(before.guild_avatar)
                or _asset_url(before.avatar)
                or before.display_avatar.url
            )
            new_avatar = after.display_avatar.url
            avatar_body = (
                f"**Member:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                f"**Avatar Updated**\n"
                f"[Old avatar]({old_avatar}) → [New avatar]({new_avatar})"
            )
            await self.log_event(
                guild, "members", "Avatar Updated", avatar_body,
                target_id=after.id, thumbnail_url=new_avatar,
            )

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added = after_roles - before_roles
        removed = before_roles - after_roles

        changes = []
        if added:
            changes.append(f"**Roles Added:** {', '.join(r.mention for r in added)}")
        if removed:
            changes.append(f"**Roles Removed:** {', '.join(r.mention for r in removed)}")

        # ── Boost / unboost ───────────────────────
        before_boost = getattr(before, "premium_since", None)
        after_boost = getattr(after, "premium_since", None)
        if before_boost != after_boost and (before_boost is None or after_boost is None):
            if after_boost is not None:
                boost_title, boost_line = "Server Boosted", "started boosting"
            else:
                boost_title, boost_line = "Boost Removed", "stopped boosting"
            boost_body = (
                f"**Member:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                f"**Action:** {boost_line}\n"
                f"**Boosts:** `{guild.premium_subscription_count}` (Tier {guild.premium_tier})"
            )
            await self.log_event(
                guild, "members", boost_title, boost_body,
                target_id=after.id, thumbnail_url=self._avatar_url(after),
            )

        # ── Nick change — attribute to moderator via audit log ──
        if before.nick != after.nick:
            nick_entry = await self._audit_entry(
                guild, discord.AuditLogAction.member_update, after.id)
            nick_moderator = nick_entry.user if nick_entry else None

            if nick_moderator and nick_moderator != self.bot.user:
                nick_body = (
                    f"**Member:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                    f"**Old Nickname:** `{before.nick or before.name}`\n"
                    f"**New Nickname:** `{after.nick or after.name}`\n"
                    f"**Changed By:** {nick_moderator.mention}"
                )
                if nick_entry.reason:
                    nick_body += f"\n**Reason:** {nick_entry.reason}"
                await self.log_event(
                    guild, "moderation", "Nickname Changed", nick_body,
                    target_id=after.id
                )

            changes.append(f"**Nickname:** `{before.nick or before.name}` → `{after.nick or after.name}`")

        # ── Discord native timeout detection ──────
        before_timeout = getattr(before, "timed_out_until", None)
        after_timeout = getattr(after, "timed_out_until", None)
        if before_timeout != after_timeout:
            timeout_entry = await self._audit_entry(
                guild, discord.AuditLogAction.member_update, after.id)
            timeout_mod = timeout_entry.user if timeout_entry else None

            if timeout_mod and timeout_mod != self.bot.user:
                if after_timeout:
                    timeout_body = (
                        f"**User:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                        f"**Action:** Timeout applied\n"
                        f"**Until:** <t:{int(after_timeout.timestamp())}:F> (<t:{int(after_timeout.timestamp())}:R>)\n"
                        f"**Moderator:** {timeout_mod.mention}"
                    )
                    if timeout_entry.reason:
                        timeout_body += f"\n**Reason:** {timeout_entry.reason}"
                    await self.log_event(
                        guild, "moderation", "Timeout", timeout_body,
                        target_id=after.id, action_key="Timeout"
                    )
                else:
                    timeout_body = (
                        f"**User:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                        f"**Action:** Timeout removed\n"
                        f"**Moderator:** {timeout_mod.mention}"
                    )
                    await self.log_event(
                        guild, "moderation", "Timeout Removed", timeout_body,
                        target_id=after.id
                    )

        if not changes:
            return

        body = f"**Member:** {after.mention} (`{after}`)\n" + "\n".join(changes)
        await self.log_event(guild, "members", "Member Updated", body, target_id=after.id)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        content = message.content or "*No text content*"
        if len(content) > 900:
            content = content[:900] + "…"

        attachment_note = ""
        image_urls = []
        files = []
        if message.attachments:
            names = ", ".join(f"`{a.filename}`" for a in message.attachments)
            attachment_note = f"\n**Attachments ({len(message.attachments)}):** {names}"
            import aiohttp
            import io
            async with aiohttp.ClientSession() as session:
                for att in message.attachments:
                    is_image = (
                        att.content_type.startswith("image/")
                        if att.content_type
                        else (att.filename or "").lower().endswith(
                            (".png", ".jpg", ".jpeg", ".gif", ".webp")
                        )
                    )
                    if is_image:
                        # Image attachments render inline in the log container's gallery.
                        image_urls.append(att.proxy_url)
                        continue
                    # Non-image attachments render as discord.ui.File components
                    # inside the log container, so no separate re-upload message.
                    try:
                        async with session.get(att.proxy_url) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                files.append(discord.File(io.BytesIO(data), filename=att.filename))
                    except Exception:
                        pass

        body = (
            f"**Author:** {message.author.mention} (`{message.author}`)\n"
            f"**Channel:** {message.channel.mention}\n"
            f"**Content:**\n{content}"
            f"{attachment_note}"
        )
        await self.log_event(
            message.guild, "messages", "Message Deleted", body,
            target_id=message.author.id, media_urls=image_urls or None,
            files=files or None,
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not after.guild or after.author.bot:
            return
        if before.content == after.content:
            return
        before_content = before.content or "*empty*"
        after_content = after.content or "*empty*"
        if len(before_content) > 450:
            before_content = before_content[:450] + "…"
        if len(after_content) > 450:
            after_content = after_content[:450] + "…"
        body = (
            f"**Author:** {after.author.mention} (`{after.author}`)\n"
            f"**Channel:** {after.channel.mention}\n"
            f"**Before:**\n{before_content}\n"
            f"**After:**\n{after_content}\n"
            f"-# [Jump to message]({after.jump_url})"
        )
        await self.log_event(after.guild, "messages", "Message Edited", body, target_id=after.author.id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Cache invites when the bot joins a new guild."""
        try:
            invites = await guild.invites()
            self._invite_cache[guild.id] = {inv.code: inv.uses for inv in invites}
        except (discord.Forbidden, discord.HTTPException):
            pass
        if guild.vanity_url_code:
            try:
                vanity = await guild.vanity_invite()
                if vanity and vanity.uses is not None:
                    self._invite_cache.setdefault(guild.id, {})["__vanity__"] = vanity.uses
            except (discord.Forbidden, discord.HTTPException, discord.NotFound):
                pass

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        guild = invite.guild
        if not guild:
            return
        # Update cache
        cached = self._invite_cache.setdefault(guild.id, {})
        cached[invite.code] = invite.uses

        expires_text = (
            f"<t:{int(invite.expires_at.timestamp())}:R>" if invite.expires_at else "Never"
        )
        max_uses_text = str(invite.max_uses) if invite.max_uses else "Unlimited"
        body = (
            f"**Invite Code:** `{invite.code}`\n"
            f"**Created By:** {invite.inviter.mention if invite.inviter else 'Unknown'}\n"
            f"**Channel:** {invite.channel.mention if invite.channel else 'Unknown'}\n"
            f"**Max Uses:** {max_uses_text}\n"
            f"**Expires:** {expires_text}"
        )
        await self.log_event(guild, "invites", "Invite Created", body)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        guild = invite.guild
        if not guild:
            return
        # Remove from cache
        cached = self._invite_cache.get(guild.id, {})
        cached.pop(invite.code, None)

        body = (
            f"**Invite Code:** `{invite.code}`\n"
            f"**Channel:** {invite.channel.mention if invite.channel else 'Unknown'}"
        )
        await self.log_event(guild, "invites", "Invite Deleted", body)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        entry = await self._audit_entry(
            channel.guild, discord.AuditLogAction.channel_create, channel.id)
        responsible = entry.user if entry else None

        body = (
            f"**Channel:** {channel.mention} (`{channel.name}`)\n"
            f"**Type:** {str(channel.type).replace('_', ' ').title()}\n"
            f"**Created By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(channel.guild, "channels", "Channel Created", body)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        entry = await self._audit_entry(
            channel.guild, discord.AuditLogAction.channel_delete, channel.id)
        responsible = entry.user if entry else None

        body = (
            f"**Channel:** `#{channel.name}`\n"
            f"**Type:** {str(channel.type).replace('_', ' ').title()}\n"
            f"**Deleted By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(channel.guild, "channels", "Channel Deleted", body)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        changes = []

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")

        if isinstance(after, discord.TextChannel) or isinstance(after, discord.ForumChannel):
            if getattr(before, "topic", None) != getattr(after, "topic", None):
                b_topic = getattr(before, "topic", None) or "*None*"
                a_topic = getattr(after, "topic", None) or "*None*"
                changes.append(f"**Topic:** {b_topic} → {a_topic}")
            if getattr(before, "slowmode_delay", 0) != getattr(after, "slowmode_delay", 0):
                changes.append(f"**Slowmode:** `{getattr(before, 'slowmode_delay', 0)}s` → `{getattr(after, 'slowmode_delay', 0)}s`")
            if getattr(before, "nsfw", False) != getattr(after, "nsfw", False):
                changes.append(f"**NSFW:** `{getattr(before, 'nsfw', False)}` → `{getattr(after, 'nsfw', False)}`")

        if isinstance(after, discord.VoiceChannel):
            if getattr(before, "bitrate", None) != getattr(after, "bitrate", None):
                changes.append(f"**Bitrate:** `{getattr(before, 'bitrate', 0) // 1000}kbps` → `{getattr(after, 'bitrate', 0) // 1000}kbps`")
            if getattr(before, "user_limit", 0) != getattr(after, "user_limit", 0):
                b_lim = getattr(before, "user_limit", 0) or "Unlimited"
                a_lim = getattr(after, "user_limit", 0) or "Unlimited"
                changes.append(f"**User Limit:** `{b_lim}` → `{a_lim}`")

        # ── Permission overwrites ────────────────
        # Granting or revoking a member/role overwrite is the most consequential
        # channel edit and used to be silent unless the category was logged by
        # the role or member listener.
        before_overwrites = getattr(before, "overwrites", {})
        after_overwrites = getattr(after, "overwrites", {})
        for target, overwrite in after_overwrites.items():
            old = before_overwrites.get(target)
            label = getattr(target, "mention", None) or getattr(target, "name", str(target))
            if old is None:
                granted = [p for p, v in iter(overwrite) if v]
                denied = [p for p, v in iter(overwrite) if not v]
                parts = []
                if granted:
                    parts.append("allow " + ", ".join(f"`{p.replace('_', ' ')}`" for p in granted))
                if denied:
                    parts.append("deny " + ", ".join(f"`{p.replace('_', ' ')}`" for p in denied))
                changes.append(f"**Overwrite Added** for {label}: " + ("; ".join(parts) or "none"))
            elif old != overwrite:
                granted = [p for p, v in iter(overwrite) if v and not getattr(old, p)]
                denied = [p for p, v in iter(overwrite) if not v and getattr(old, p)]
                parts = []
                if granted:
                    parts.append("allow " + ", ".join(f"`{p}`" for p in granted))
                if denied:
                    parts.append("deny " + ", ".join(f"`{p}`" for p in denied))
                if parts:
                    changes.append(f"**Overwrite Changed** for {label}: " + "; ".join(parts))
        for target in before_overwrites:
            if target not in after_overwrites:
                label = getattr(target, "mention", None) or getattr(target, "name", str(target))
                changes.append(f"**Overwrite Removed** for {label}")

        if not changes:
            return

        entry = await self._audit_entry(
            after.guild, discord.AuditLogAction.channel_update, after.id)
        responsible = entry.user if entry else None

        body = (
            f"**Channel:** {after.mention} (`{after.name}`)\n"
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after.guild, "channels", "Channel Updated", body)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        entry = await self._audit_entry(
            role.guild, discord.AuditLogAction.role_create, role.id)
        responsible = entry.user if entry else None

        color_text = str(role.color) if role.color.value else "Default"
        body = (
            f"**Role:** {role.mention} (`{role.name}`)\n"
            f"**Color:** `{color_text}`\n"
            f"**Hoisted:** `{role.hoist}` | **Mentionable:** `{role.mentionable}`\n"
            f"**Created By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(role.guild, "roles", "Role Created", body)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        entry = await self._audit_entry(
            role.guild, discord.AuditLogAction.role_delete, role.id)
        responsible = entry.user if entry else None

        body = (
            f"**Role:** `{role.name}` (ID: `{role.id}`)\n"
            f"**Deleted By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(role.guild, "roles", "Role Deleted", body)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        changes = []

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")
        if before.color != after.color:
            changes.append(f"**Color:** `{before.color}` → `{after.color}`")
        if before.hoist != after.hoist:
            changes.append(f"**Hoisted:** `{before.hoist}` → `{after.hoist}`")
        if before.mentionable != after.mentionable:
            changes.append(f"**Mentionable:** `{before.mentionable}` → `{after.mentionable}`")
        if before.permissions != after.permissions:
            perm_changes = []
            for perm, value in iter(after.permissions):
                if getattr(before.permissions, perm) != value:
                    symbol = get_emoji('tick') if value else get_emoji('cross')
                    perm_changes.append(f"{symbol} `{perm.replace('_', ' ').title()}`")
            if perm_changes:
                changes.append("**Permissions Changed:**\n" + " ".join(perm_changes))

        if not changes:
            return

        entry = await self._audit_entry(
            after.guild, discord.AuditLogAction.role_update, after.id)
        responsible = entry.user if entry else None

        body = (
            f"**Role:** {after.mention} (`{after.name}`)\n"
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after.guild, "roles", "Role Updated", body)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        changes = []

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")
        if before.description != after.description:
            b_desc = before.description or "*None*"
            a_desc = after.description or "*None*"
            changes.append(f"**Description:** {b_desc} → {a_desc}")
        if before.verification_level != after.verification_level:
            changes.append(f"**Verification Level:** `{before.verification_level}` → `{after.verification_level}`")
        if before.explicit_content_filter != after.explicit_content_filter:
            changes.append(f"**Explicit Content Filter:** `{before.explicit_content_filter}` → `{after.explicit_content_filter}`")
        if before.default_notifications != after.default_notifications:
            changes.append(f"**Default Notifications:** `{before.default_notifications}` → `{after.default_notifications}`")
        if before.afk_channel != after.afk_channel:
            b_afk = before.afk_channel.name if before.afk_channel else "None"
            a_afk = after.afk_channel.name if after.afk_channel else "None"
            changes.append(f"**AFK Channel:** `{b_afk}` → `{a_afk}`")
        if before.icon != after.icon:
            changes.append("**Server Icon:** changed")
        if before.banner != after.banner:
            changes.append("**Server Banner:** changed")

        if not changes:
            return

        entry = await self._audit_entry(
            after, discord.AuditLogAction.guild_update, after.id)
        responsible = entry.user if entry else None

        body = (
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after, "server", "Server Updated", body)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: discord.Guild, before: list, after: list):
        before_ids = {e.id for e in before}
        after_ids = {e.id for e in after}

        added = [e for e in after if e.id not in before_ids]
        removed = [e for e in before if e.id not in after_ids]

        if not added and not removed:
            return

        lines = []
        if added:
            lines.append("**Added:** " + ", ".join(f"`:{e.name}:`" for e in added))
        if removed:
            lines.append("**Removed:** " + ", ".join(f"`:{e.name}:`" for e in removed))

        responsible = None
        try:
            action = discord.AuditLogAction.emoji_create if added else discord.AuditLogAction.emoji_delete
            for emoji in (added or removed):
                entry = await self._audit_entry(guild, action, emoji.id)
                if entry is not None:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            responsible = None

        body = (
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(lines)
        )
        await self.log_event(guild, "server", "Emoji Updated", body)

    @commands.Cog.listener()
    async def on_guild_stickers_update(self, guild: discord.Guild, before: list, after: list):
        before_ids = {s.id for s in before}
        after_ids = {s.id for s in after}

        added = [s for s in after if s.id not in before_ids]
        removed = [s for s in before if s.id not in after_ids]

        if not added and not removed:
            return

        lines = []
        if added:
            lines.append("**Added:** " + ", ".join(f"`{s.name}`" for s in added))
        if removed:
            lines.append("**Removed:** " + ", ".join(f"`{s.name}`" for s in removed))

        body = "\n".join(lines)
        await self.log_event(guild, "server", "Sticker Updated", body)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        if before.channel is None and after.channel is not None:
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Joined:** {after.channel.mention}"
            )
            await self.log_event(guild, "voice", "Voice Join", body, target_id=member.id)

        elif before.channel is not None and after.channel is None:
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Left:** {before.channel.mention}"
            )
            await self.log_event(guild, "voice", "Voice Leave", body, target_id=member.id)

        elif (
            before.channel is not None
            and after.channel is not None
            and before.channel.id != after.channel.id
        ):
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**From:** {before.channel.mention}\n"
                f"**To:** {after.channel.mention}"
            )
            await self.log_event(guild, "voice", "Voice Move", body, target_id=member.id)

    @commands.Cog.listener()
    # discord.py does not pass the moderator, so the audit log is the only source.
    async def on_member_ban(self, guild: discord.Guild, user: discord.User, reason: str | None = None):
        entry = await self._audit_entry(guild, discord.AuditLogAction.ban, user.id)
        moderator = entry.user if entry else None
        if moderator == self.bot.user:
            return
        reason = reason or (entry.reason if entry else None)
        body = (
            f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n"
            f"**Action:** Ban\n"
            f"**Reason:** {reason or 'No reason provided'}\n"
            f"**Moderator:** {moderator.mention if moderator else 'Unknown'}"
        )
        await self.log_event(
            guild, "moderation", "Ban", body, 
            target_id=user.id, action_key="Ban"
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User, reason: str | None = None):
        entry = await self._audit_entry(guild, discord.AuditLogAction.unban, user.id)
        moderator = entry.user if entry else None
        if moderator == self.bot.user:
            return
        reason = reason or (entry.reason if entry else None)
        body = (
            f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n"
            f"**Action:** Unban\n"
            f"**Reason:** {reason or 'No reason provided'}\n"
            f"**Moderator:** {moderator.mention if moderator else 'Unknown'}"
        )
        await self.log_event(
            guild, "moderation", "Unban", body,
            target_id=user.id, action_key="Unban"
        )

    # ── Events that used to be unlogged ──────────

    async def _audit_latest(self, guild: discord.Guild, action, *, window: float = 15.0):
        """The newest audit entry for *action*, if it is recent enough."""
        try:
            async for entry in guild.audit_logs(limit=1, action=action):
                if (discord.utils.utcnow() - entry.created_at).total_seconds() > window:
                    return None
                return entry
        except (discord.Forbidden, discord.HTTPException):
            return None
        return None

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        """A purge: Discord does not fire on_message_delete for each message."""
        if not messages or messages[0].guild is None:
            return
        guild = messages[0].guild
        channel = messages[0].channel
        counts: dict[str, int] = {}
        for message in messages:
            label = f"{message.author.mention}"
            counts[label] = counts.get(label, 0) + 1
        top = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:5]
        entry = await self._audit_latest(guild, discord.AuditLogAction.message_bulk_delete)
        body = (
            f"**Channel:** {channel.mention}\n"
            f"**Messages Deleted:** `{len(messages)}`\n"
            f"**Top Authors:**\n" + "\n".join(f"{who} — `{count}`" for who, count in top)
        )
        if entry is not None:
            body += f"\n**Deleted By:** {entry.user.mention if entry.user else 'Unknown'}"
        await self.log_event(
            guild, "messages", "Messages Bulk Deleted", body,
            channel_id=channel.id,
        )

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        guild = thread.guild
        entry = await self._audit_entry(
            guild, discord.AuditLogAction.thread_create, thread.id)
        body = (
            f"**Thread:** {thread.mention} (`{thread.name}`)\n"
            f"**Parent:** {thread.parent.mention if thread.parent else 'Unknown'}\n"
            f"**Created By:** {thread.owner.mention if thread.owner else 'Unknown'}"
        )
        if entry is not None and entry.user:
            body += f"\n-# Created via {entry.user.mention}"
        await self.log_event(guild, "channels", "Thread Created", body,
                             channel_id=thread.parent_id)

    @commands.Cog.listener()
    async def on_thread_delete(self, thread: discord.Thread):
        guild = thread.guild
        entry = await self._audit_entry(
            guild, discord.AuditLogAction.thread_delete, thread.id)
        body = (
            f"**Thread:** `{thread.name}` (ID: `{thread.id}`)\n"
            f"**Parent:** {thread.parent.mention if thread.parent else 'Unknown'}\n"
            f"**Deleted By:** {entry.user.mention if entry and entry.user else 'Unknown'}"
        )
        await self.log_event(guild, "channels", "Thread Deleted", body)

    @commands.Cog.listener()
    async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
        changes = []
        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")
        if before.archived != after.archived:
            changes.append(f"**Archived:** `{before.archived}` → `{after.archived}`")
        if before.locked != after.locked:
            changes.append(f"**Locked:** `{before.locked}` → `{after.locked}`")
        if getattr(before, "slowmode_delay", 0) != getattr(after, "slowmode_delay", 0):
            changes.append(
                f"**Slowmode:** `{before.slowmode_delay}s` → `{after.slowmode_delay}s`")
        if not changes:
            return
        body = (
            f"**Thread:** {after.mention} (`{after.name}`)\n"
            f"**Parent:** {after.parent.mention if after.parent else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after.guild, "channels", "Thread Updated", body)

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel: discord.abc.GuildChannel):
        guild = channel.guild
        for action, title in (
            (discord.AuditLogAction.webhook_create, "Webhook Created"),
            (discord.AuditLogAction.webhook_delete, "Webhook Deleted"),
            (discord.AuditLogAction.webhook_update, "Webhook Updated"),
        ):
            entry = await self._audit_latest(guild, action)
            if entry is None:
                continue
            target = getattr(entry, "target", None)
            if getattr(target, "channel", None) is not None and target.channel.id != channel.id:
                continue
            name = getattr(target, "name", None) or "unknown"
            body = (
                f"**Channel:** {channel.mention}\n"
                f"**Webhook:** `{name}`\n"
                f"**By:** {entry.user.mention if entry.user else 'Unknown'}"
            )
            await self.log_event(guild, "channels", title, body, channel_id=channel.id)
            return

    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild: discord.Guild):
        entry = await self._audit_latest(guild, discord.AuditLogAction.integration_create) \
            or await self._audit_latest(guild, discord.AuditLogAction.integration_delete) \
            or await self._audit_latest(guild, discord.AuditLogAction.integration_update)
        if entry is None:
            return
        body = (
            f"**Integration:** `{getattr(entry.target, 'name', 'unknown')}`\n"
            f"**By:** {entry.user.mention if entry.user else 'Unknown'}"
        )
        await self.log_event(guild, "server", "Integrations Updated", body)

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction):
        """A rule managed in Discord's own AutoMod settings fired."""
        guild = execution.guild
        if guild is None:
            return
        member = execution.member

        # The action payload only carries the rule id, so the name needs a
        # fetch — and a missing Manage Server permission must not lose the entry.
        rule_name = f"rule {execution.rule_id}"
        try:
            rule = await execution.fetch_rule()
            rule_name = f"{rule.name} ({execution.rule_id})"
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

        action_type = getattr(execution.action, "type", None)
        action_text = str(getattr(action_type, "name", action_type) or "blocked").replace("_", " ")
        body = (
            f"**Rule:** `{rule_name}` ({str(execution.rule_trigger_type).replace('_', ' ')})\n"
            f"**Action:** {action_text.title()}"
        )
        if member is not None:
            body = f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n" + body
        if execution.channel_id:
            body += f"\n**Channel:** <#{execution.channel_id}>"
        matched = execution.matched_keyword or execution.matched_content or execution.content
        if matched:
            body += f"\n**Matched:** `{matched[:200]}`"
        await self.log_event(
            guild, "automod", "AutoMod Rule Triggered", body,
            target_id=member.id if member else None,
        )

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        """A pin or unpin: the audit log knows which and by whom."""
        guild = getattr(channel, "guild", None)
        if guild is None:
            return
        for action, title in (
            (discord.AuditLogAction.message_pin, "Message Pinned"),
            (discord.AuditLogAction.message_unpin, "Message Unpinned"),
        ):
            entry = await self._audit_latest(guild, action)
            if entry is None:
                continue
            target = getattr(entry, "target", None)
            target_channel = getattr(target, "channel", None)
            if target_channel is not None and target_channel.id != channel.id:
                continue
            body = (
                f"**Channel:** {channel.mention}\n"
                f"**By:** {entry.user.mention if entry.user else 'Unknown'}"
            )
            jump = getattr(target, "jump_url", None)
            if jump:
                body += f"\n-# [Jump to message]({jump})"
            await self.log_event(guild, "channels", title, body, channel_id=channel.id)
            return

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event: discord.ScheduledEvent):
        body = (
            f"**Event:** {event.name}\n"
            f"**Starts:** <t:{int(event.start_time.timestamp())}:F>\n"
            f"**Location:** {event.location or 'Unknown'}\n"
            f"**Created By:** {event.creator.mention if event.creator else 'Unknown'}"
        )
        await self.log_event(event.guild, "server", "Event Created", body)

    @commands.Cog.listener()
    async def on_scheduled_event_delete(self, event: discord.ScheduledEvent):
        entry = await self._audit_entry(
            event.guild, discord.AuditLogAction.scheduled_event_delete, event.id)
        body = (
            f"**Event:** {event.name}\n"
            f"**Deleted By:** {entry.user.mention if entry and entry.user else 'Unknown'}"
        )
        await self.log_event(event.guild, "server", "Event Deleted", body)

    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before: discord.ScheduledEvent, after: discord.ScheduledEvent):
        changes = []
        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")
        if before.status != after.status:
            changes.append(f"**Status:** `{before.status}` → `{after.status}`")
        if before.start_time != after.start_time:
            changes.append(
                f"**Start:** <t:{int(before.start_time.timestamp())}:f> → "
                f"<t:{int(after.start_time.timestamp())}:f>"
            )
        if not changes:
            return
        body = f"**Event:** {after.name}\n" + "\n".join(changes)
        await self.log_event(after.guild, "server", "Event Updated", body)

    # ── Commands ──────────────────────────────────

    @commands.group(name="logging", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def logging_cmd(self, ctx: commands.Context):
        """Open the server logging configuration panel."""
        # Pass the loaded config as data=; the third positional arg is category.
        await ctx.send(
            view=LoggingSetupView(ctx.guild.id, ctx.author, data=await _load_log_config())
        )

    @logging_cmd.command(name="status")
    @commands.has_permissions(manage_guild=True)
    async def logging_status(self, ctx: commands.Context):
        """Show the current logging configuration."""
        await self._reload()
        cfg = self._get_cfg(ctx.guild.id)
        icon = get_emoji("settings")

        lines = []
        for key, info in CATEGORIES.items():
            ch_id = cfg.get(key)
            ch_text = f"<#{ch_id}>" if ch_id else "`Not set`"
            disabled = key in cfg.get("disabled", [])
            status = get_emoji("disabled") if disabled else get_emoji("enabled")
            lines.append(f"{status} **{info['label']}** — {ch_text}")

        body = "\n".join(lines)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {icon} Logging Status"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=body),
            accent_colour=discord.Colour(0x5865F2),
        ))
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLogger(bot))
