import asyncio
import io
import re
import time

import database
from .formatters import *
from .revert import (
    channel_snapshot,
    overwrite_entry,
    register_persistent_views,
    removed_overwrite_entry,
    role_snapshot,
    save_snapshot,
)


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

#: Discord expires the CDN URL of a replaced avatar a day or two after the
#: change, so both pictures are downloaded and uploaded with the log entry
#: instead of linked. The cap keeps a large animated asset from turning one
#: profile edit into a big upload.
MAX_ARCHIVED_AVATAR_BYTES = 4_000_000

#: Global profile changes arrive once per shared server, so the last logged
#: profile of each user is remembered to drop the repeats. The cap keeps a big
#: bot from holding an entry for every user it has ever seen change a picture.
MAX_TRACKED_PROFILES = 20_000

#: How long one entry stays open for further changes. A member update is
#: posted once and then edited for this long, so a role menu that toggles six
#: roles produces one entry rather than six.
ENTRY_RETENTION_SECONDS = 30.0

#: Titles whose entries describe an ongoing change to one member, and so are
#: merged inside the retention window. Picture changes are left out: an edit
#: cannot attach the before/after files, and each picture change is a finished
#: event rather than one step of a sequence.
COALESCED_TITLES = frozenset({"Member Updated", "Nickname Changed"})

#: Details that accumulate across the window instead of replacing each other —
#: the second role a member gains is added to the list, not swapped in for the
#: first.
_ACCUMULATED_DETAILS = frozenset({"Roles Added", "Roles Removed"})

#: The line that cancels a given accumulated line out.
_OPPOSITE_DETAILS = {"Roles Added": "Roles Removed", "Roles Removed": "Roles Added"}

#: A ``**Label:** value`` detail line of a log body.
_DETAIL_LINE = re.compile(r"^\*\*(?P<label>[^*]+):\*\*\s*(?P<value>.*)$")

COALESCED_NOTE = (
    "-# Changes made within 30 seconds of each other are merged into this entry."
)

#: Open entries and their locks are dropped lazily, but a very busy bot should
#: not hold one per member it has ever logged.
MAX_PENDING_ENTRIES = 512

_IMAGE_EXTENSIONS = ("png", "jpg", "jpeg", "webp", "gif")


def _asset_url(asset) -> str | None:
    """The URL of an asset, or None for a missing one."""
    try:
        return asset.url if asset else None
    except Exception:  # noqa: BLE001 - a broken asset is simply "no picture"
        return None


def _asset_extension(asset) -> str:
    """The image format from the asset URL, for the archived file's name."""
    tail = (_asset_url(asset) or "").split("?", 1)[0].rsplit(".", 1)[-1].lower()
    return tail if tail in _IMAGE_EXTENSIONS else "png"


def _channel_kind(channel) -> str:
    """A channel's type as its plain name (text, voice, forum …)."""
    return str(getattr(getattr(channel, "type", "text"), "name", "text")).lower()


def _permission_list(permissions, *, limit: int = 8) -> str:
    """The granted names of a Permissions object, for a detail line."""
    names = [name.replace("_", " ") for name, value in iter(permissions) if value]
    if not names:
        return "none"
    shown = names[:limit]
    if len(names) > limit:
        shown.append(f"+{len(names) - limit} more")
    return ", ".join(shown)

def _split_entry_body(body: str) -> tuple[str, list[tuple[str, str]]]:
    """Split a log body into its heading line(s) and labelled detail lines.

    ``**Member:** @someone`` (the first line) stays the heading; the change
    lines below it — ``**Roles Added:** @mod`` — become mergeable details, so
    two member updates can be folded together without their headers piling up.
    """
    heading: list[str] = []
    details: list[tuple[str, str]] = []
    for line in body.splitlines():
        match = _DETAIL_LINE.match(line)
        if not match or not heading:
            heading.append(line)
            continue
        details.append((match.group("label").strip(), match.group("value").strip()))
    return "\n".join(heading), details


def _detail_values(details: list[tuple[str, str]], label: str) -> list[str]:
    """The comma-separated values of one detail line."""
    for name, value in details:
        if name == label:
            return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _set_detail(details: list[tuple[str, str]], label: str,
                values: list[str]) -> None:
    """Write a detail line's values, removing the line when none are left."""
    for index, (name, _) in enumerate(details):
        if name == label:
            if values:
                details[index] = (label, ", ".join(values))
            else:
                details.pop(index)
            return
    if values:
        details.append((label, ", ".join(values)))


def _merge_entry_details(current: list[tuple[str, str]],
                        incoming: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Fold a new change into the details already collected.

    Role lists grow and cancel out — a role granted and taken back inside the
    window leaves no line, which is what a self-assign menu toggled twice
    means — while a single-valued line (a nickname, the moderator who made the
    change) takes the newest value. The entry describes the member's current
    state rather than replaying every intermediate click.
    """
    merged = list(current)
    for label, value in incoming:
        if label in _ACCUMULATED_DETAILS:
            opposite = _OPPOSITE_DETAILS[label]
            additions: list[str] = []
            for item in (part.strip() for part in value.split(",")):
                if not item:
                    continue
                if item in _detail_values(merged, opposite):
                    # Toggled back inside the window: the role ends where it
                    # started, so neither line should mention it.
                    _set_detail(merged, opposite, [
                        other for other in _detail_values(merged, opposite)
                        if other != item
                    ])
                elif item not in _detail_values(merged, label) and item not in additions:
                    additions.append(item)
            if additions:
                _set_detail(merged, label, _detail_values(merged, label) + additions)
            continue
        for index, (name, _) in enumerate(merged):
            if name == label:
                merged[index] = (label, value)
                break
        else:
            merged.append((label, value))
    return merged


def _render_entry_body(heading: str, details: list[tuple[str, str]],
                       *, note: bool = False) -> str:
    """Rebuild a body from its heading and details, for the edited entry."""
    lines = [heading] if heading else []
    lines.extend(f"**{label}:** {value}" for label, value in details)
    if note:
        lines.append(COALESCED_NOTE)
    return "\n".join(lines)


class _PendingEntry:
    """The entry a target's changes are collected into while it is open."""

    __slots__ = ("message", "channel_id", "heading", "details", "expires_at")

    def __init__(self, message, channel_id: int, heading: str,
                 details: list[tuple[str, str]], expires_at: float):
        self.message = message
        self.channel_id = channel_id
        self.heading = heading
        self.details = details
        self.expires_at = expires_at


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
        # user id → the global profile fields last logged, so one profile edit
        # (dispatched once per shared server) is logged once, not once per guild.
        self._global_profile_seen: dict[int, tuple] = {}
        # (guild, category, title, target) → the entry still inside its
        # retention window, so rapid changes to one member edit that entry.
        self._pending_entries: dict[tuple, _PendingEntry] = {}
        self._pending_locks: dict[tuple, asyncio.Lock] = {}

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

    async def cog_load(self):
        """Register the restore/revert buttons for entries posted before this run."""
        register_persistent_views(self.bot)

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
        media_urls: list | None = None,
        thumbnail_url: str | None = None,
        files: list[discord.File] | None = None,
        file_components: bool = True,
        revert: tuple[str, str] | None = None,
    ):
        """Send a structured log entry to the configured channel for the given category.

        media_urls renders images in a MediaGallery inside the log container (a
        ``(uri, caption)`` pair labels its item); thumbnail_url renders the body
        in a Section with a Thumbnail accessory; files uploads the bytes
        alongside the message and renders them as discord.ui.File components
        unless ``file_components`` is False, which is what an asset-archiving
        entry wants: its bytes belong in the gallery, not in a file chip.

        ``revert`` is a ``(kind, snapshot_id)`` pair; it adds the restore/revert
        button that undoes the logged change.
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
            file_components=file_components, revert=revert,
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
        media_urls: list | None = None,
        thumbnail_url: str | None = None,
        files: list[discord.File] | None = None,
        file_components: bool = True,
        revert: tuple[str, str] | None = None,
    ) -> None:
        """Post one log entry to a specific channel.

        Webhooks are preferred (their own rate-limit bucket), but a server that
        has not granted Manage Webhooks, or a channel that cannot own a webhook
        such as a thread, still gets its log: the entry falls back to the bot
        account instead of being dropped.

        An entry about a member is kept open for ``ENTRY_RETENTION_SECONDS``:
        a change that lands inside that window is merged into the entry already
        posted and the message is edited, so a role menu that toggles several
        roles — or a moderator making a run of changes — leaves one entry
        behind instead of one per click.
        """
        retention_key = self._retention_key(
            guild, category, title, target_id, files, media_urls, revert)
        if retention_key is None:
            await self._post_entry(
                guild, channel, category, title, body,
                target_id=target_id, action_key=action_key, channel_id=channel_id,
                media_urls=media_urls, thumbnail_url=thumbnail_url, files=files,
                file_components=file_components, revert=revert,
            )
            return

        lock = self._pending_locks.setdefault(retention_key, asyncio.Lock())
        async with lock:
            self._prune_pending()
            pending = self._open_entry(retention_key, channel)
            if pending is not None and await self._extend_entry(
                retention_key, guild, channel, category, title, body, pending,
                target_id=target_id, action_key=action_key,
                channel_id=channel_id, thumbnail_url=thumbnail_url,
            ):
                return
            self._pending_entries.pop(retention_key, None)
            message = await self._post_entry(
                guild, channel, category, title, body,
                target_id=target_id, action_key=action_key, channel_id=channel_id,
                media_urls=media_urls, thumbnail_url=thumbnail_url, files=files,
                file_components=file_components, revert=revert,
            )
            if message is None:
                return
            heading, details = _split_entry_body(body)
            self._pending_entries[retention_key] = _PendingEntry(
                message,
                getattr(channel, "id", 0),
                heading,
                details,
                time.monotonic() + ENTRY_RETENTION_SECONDS,
            )

        # A lock is only worth keeping while its entry is open; dropping it
        # stops the map from holding one per member the bot has ever logged.
        if retention_key not in self._pending_entries and not lock.locked():
            self._pending_locks.pop(retention_key, None)

    def _retention_key(self, guild, category: str, title: str,
                       target_id: int | None, files, media_urls,
                       revert) -> tuple | None:
        """The key whose entry this change belongs to, or None to send fresh.

        Only a finished, text-only entry about one member can be extended: an
        edit cannot attach the files a picture change carries.
        """
        if title not in COALESCED_TITLES or target_id is None:
            return None
        if files or media_urls or revert:
            return None
        return (guild.id, category, title, target_id)

    def _open_entry(self, key: tuple, channel) -> _PendingEntry | None:
        """The entry still inside its window, forgetting it once it has closed."""
        pending = self._pending_entries.get(key)
        if pending is None:
            return None
        if (pending.channel_id != getattr(channel, "id", 0)
                or time.monotonic() >= pending.expires_at):
            self._pending_entries.pop(key, None)
            return None
        return pending

    async def _extend_entry(self, key: tuple, guild, channel, category: str,
                            title: str, body: str, pending: _PendingEntry, *,
                            target_id=None, action_key: str | None = None,
                            channel_id: int | None = None,
                            thumbnail_url: str | None = None) -> bool:
        """Fold a change into the open entry and edit its message.

        Returns False when the entry could not be edited (the message was
        deleted, or the edit failed), so the caller posts a fresh entry.
        """
        _, details = _split_entry_body(body)
        merged = _merge_entry_details(pending.details, details)
        if not merged:
            # Every change cancelled out inside the window — a role menu toggled
            # on and then off — so the entry has nothing left to say and goes.
            self._pending_entries.pop(key, None)
            try:
                await pending.message.delete()
            except Exception as e:
                logging.warning(
                    "logging_cog",
                    f"Could not remove the emptied log entry in {channel}: {e}",
                )
            return True
        view = _build_log_view(
            category=category,
            title=title,
            body=_render_entry_body(pending.heading, merged, note=True),
            guild_id=guild.id,
            target_id=target_id,
            action_key=action_key or title,
            channel_id=channel_id,
            thumbnail_url=thumbnail_url,
        )
        try:
            await log_channel_limiter.acquire((guild.id, pending.channel_id))
            # An edit defaults to allowing every mention in the new render, and
            # the merged body names roles and members. Without this the bot
            # pings every role the entry mentions, once per merged change.
            await pending.message.edit(
                view=view, allowed_mentions=discord.AllowedMentions.none()
            )
        except Exception as e:
            logging.warning(
                "logging_cog",
                f"Could not extend the log entry in {channel}: {e}",
            )
            return False
        pending.details = merged
        return True

    def _prune_pending(self) -> None:
        """Forget entries whose window has closed, and their locks with them.

        Called on every coalescable entry instead of from a timer: nothing has
        to keep running for the window to expire, and a key that is never seen
        again is dropped the next time any other member entry is logged.
        """
        now = time.monotonic()
        for key, pending in list(self._pending_entries.items()):
            if pending.expires_at <= now:
                self._pending_entries.pop(key, None)
                # The current event's own lock is held while this runs.
                lock = self._pending_locks.get(key)
                if lock is None or not lock.locked():
                    self._pending_locks.pop(key, None)
        if len(self._pending_locks) <= MAX_PENDING_ENTRIES:
            return
        # A lock is only needed while its entry is open. A held lock is left
        # alone: another event is using it right now.
        for key, lock in list(self._pending_locks.items()):
            if key not in self._pending_entries and not lock.locked():
                self._pending_locks.pop(key, None)

    async def _post_entry(
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
        media_urls: list | None = None,
        thumbnail_url: str | None = None,
        files: list[discord.File] | None = None,
        file_components: bool = True,
        revert: tuple[str, str] | None = None,
    ):
        """Send one entry and return the message, so it can be extended later."""
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
            file_components=file_components,
            revert=revert,
        )
        try:
            await log_channel_limiter.acquire((guild.id, getattr(channel, "id", 0)))
            webhook = await self._get_log_webhook(channel)
            if webhook is None:
                return await self._send_with_bot(channel, view, files)
            try:
                return await webhook.send(
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
                    return await self._send_with_bot(channel, view, files)
                for file in files or []:
                    file.reset(seek=True)
                return await webhook.send(
                    view=view,
                    files=files or [],
                    username=LOG_WEBHOOK_NAME,
                    avatar_url=self.bot.user.display_avatar.url,
                    allowed_mentions=discord.AllowedMentions.none(),
                    wait=True,
                )
        except Exception as e:
            logging.error("logging_cog", f"Failed to send log message to {channel} in {guild}: {e}")
            return None

    async def _send_with_bot(self, channel: discord.abc.Messageable,
                             view: discord.ui.LayoutView,
                             files: list[discord.File] | None = None):
        """Send a log entry as the bot itself, the fallback without webhooks."""
        for file in files or []:
            file.reset(seek=True)
        return await channel.send(
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

        member_count = getattr(guild, "member_count", None)
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Account Created:** {created} ({account_age} days ago){age_warn}\n"
            f"**Join Method:** {join_method}"
            + (f"\n**Member Count:** `{member_count:,}`" if member_count else "")
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
        created_at = getattr(member, "created_at", None)
        account = (
            f"\n**Account Created:** <t:{int(created_at.timestamp())}:R>"
            if created_at else ""
        )
        member_count = getattr(guild, "member_count", None)
        remaining = (
            f"\n**Member Count:** `{member_count:,}`" if member_count else ""
        )
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Roles ({len(roles)}):** {roles_text}{tenure}{account}{remaining}"
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

    async def _archive_asset(self, asset, filename: str) -> discord.File | None:
        """Download an asset so the log keeps it after its CDN URL expires.

        Discord invalidates the URL of a replaced avatar a day or two after the
        change, so linking the old picture produced an entry that went dead. The
        bytes are uploaded with the entry instead.
        """
        if asset is None:
            return None
        try:
            data = await asset.read()
        except (discord.HTTPException, discord.NotFound, OSError, AttributeError):
            return None
        if not data or len(data) > MAX_ARCHIVED_AVATAR_BYTES:
            return None
        return discord.File(io.BytesIO(data), filename=filename)

    async def _log_picture_change(self, before, after, *, attribute: str, title: str,
                                  label: str, slug: str, guild) -> bool:
        """Log one picture change with both pictures archived as attachments.

        The global profile picture, the global banner and the per-server
        picture are separate fields, so a member who changes several of them
        gets an entry for each rather than one entry that hides half of what
        happened. ``guild`` is explicit because a global change arrives as a
        :class:`discord.User`, which has no guild of its own.
        """
        old_asset = getattr(before, attribute, None)
        new_asset = getattr(after, attribute, None)
        old_url = _asset_url(old_asset)
        new_url = _asset_url(new_asset)
        if old_url == new_url:
            return False

        lines = [
            f"**Member:** {after.mention} (`{after}` — ID: `{after.id}`)",
            f"**Changed:** {label}",
        ]
        media: list = []
        files: list[discord.File] = []
        linked: list[str] = []
        pictures = ((old_asset, "before", old_url), (new_asset, "after", new_url))
        present = sum(1 for _asset, _side, url in pictures if url)
        for asset, side, url in pictures:
            filename = f"{slug}-{side}.{_asset_extension(asset)}"
            archived = await self._archive_asset(asset, filename)
            if archived is not None:
                files.append(archived)
                media.append((f"attachment://{filename}", f"{side.title()} — {label}"))
            elif url:
                # The download failed or the file is too large to re-upload, so
                # the entry keeps the link it has — with the caveat that the old
                # one stops working once Discord expires it.
                media.append(url)
                linked.append(f"**{side.title()}:** {url}")

        if len(files) == present and present:
            lines.append(
                "-# The pictures are attached to this entry, so it still shows "
                "them after Discord expires their old links."
            )
        elif files and linked:
            lines.append(
                "-# One picture could not be archived and is linked instead; "
                "Discord expires such a link once the picture changes again."
            )
        lines.extend(linked)
        if not files and not linked:
            lines.append("**Before:** *none*\n**After:** *none*")

        await self.log_event(
            guild=guild,
            category="members",
            title=title,
            body="\n".join(lines),
            target_id=after.id,
            action_key=title,
            media_urls=media or None,
            files=files or None,
            file_components=False,
        )
        return True

    def _shared_guilds(self, user) -> list:
        """The guilds where this user and the bot are both members."""
        guilds = getattr(user, "mutual_guilds", None)
        if guilds is None:
            single = getattr(user, "guild", None)
            return [single] if single is not None else []
        return list(guilds)

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        """Log a change to a member's *global* Discord profile.

        The global picture, display name, username and banner are visible in
        every server the user is in (a member without a per-server picture
        shows the global one), so they belong in each server's member logs.

        These arrive as ``on_user_update``: Discord sends the changed user
        once per shared server, and the member in ``on_member_update`` shares
        its user object with the updated one, so comparing two members can
        never show a global change.
        """
        if getattr(after, "bot", False):
            return

        signature = (
            getattr(after, "name", None),
            getattr(after, "global_name", None),
            _asset_url(getattr(after, "avatar", None)),
            _asset_url(getattr(after, "banner", None)),
        )
        if self._global_profile_seen.get(after.id) == signature:
            # The same edit is dispatched once per shared server (and again from
            # the member update), so the first dispatch logs it to all of them
            # and the repeats are dropped.
            return
        self._global_profile_seen[after.id] = signature
        if len(self._global_profile_seen) > MAX_TRACKED_PROFILES:
            # Oldest first: a dict keeps insertion order.
            self._global_profile_seen.pop(next(iter(self._global_profile_seen)))

        names: list[str] = []
        if before.name != after.name:
            names.append(f"**Username:** `{before.name}` → `{after.name}`")
        if before.global_name != after.global_name:
            names.append(
                f"**Display Name:** `{before.global_name or 'none'}` → "
                f"`{after.global_name or 'none'}`"
            )

        for guild in self._shared_guilds(after):
            member = guild.get_member(after.id) or after
            await self._log_picture_change(
                before, after,
                guild=guild,
                attribute="avatar",
                title="Avatar Updated",
                label="Global profile picture",
                slug="profile-picture",
            )
            await self._log_picture_change(
                before, after,
                guild=guild,
                attribute="banner",
                title="Profile Banner Updated",
                label="Profile banner",
                slug="profile-banner",
            )
            if names:
                body = (
                    f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                    f"**Changed:** Global profile\n"
                    + "\n".join(names)
                )
                await self.log_event(
                    guild, "members", "Username Updated", body,
                    target_id=after.id,
                    thumbnail_url=self._avatar_url(member),
                )

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild = after.guild

        # ── Picture: only the per-server one reaches this event ──
        # A global picture change is logged by on_user_update instead: Discord
        # updates the shared user object in place before this listener runs, so
        # `before` and `after` always agree on the global picture.
        await self._log_picture_change(
            before, after,
            guild=guild,
            attribute="guild_avatar",
            title="Server Avatar Updated",
            label="Server profile picture",
            slug="server-profile-picture",
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
        if added or removed:
            # A role change is usually somebody else's doing; the gateway event
            # only says the roles changed, so the audit log names the actor.
            role_entry = await self._audit_entry(
                guild, discord.AuditLogAction.member_role_update, after.id)
            role_actor = role_entry.user if role_entry else None
            if role_actor is not None and role_actor != self.bot.user:
                changes.append(f"**Roles Changed By:** {role_actor.mention}")
                if role_entry.reason:
                    changes.append(f"**Reason:** {role_entry.reason}")

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
            f"**Channel:** {channel.mention} (`{channel.name}` — ID: `{channel.id}`)\n"
            f"**Type:** {_channel_kind(channel).title()}\n"
            f"**Category:** {self._category_text(channel)}\n"
            f"**Position:** `{getattr(channel, 'position', 0)}`\n"
            + self._channel_detail_lines(channel)
            + f"**Created By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(channel.guild, "channels", "Channel Created", body,
                             channel_id=channel.id)

    @staticmethod
    def _category_text(channel) -> str:
        category = getattr(channel, "category", None)
        return category.mention if category else "None"

    @staticmethod
    def _channel_detail_lines(channel) -> str:
        """The settings worth naming for whichever channel type this is."""
        lines = ""
        if _channel_kind(channel) in ("text", "news", "forum", "media", "stage"):
            topic = getattr(channel, "topic", None)
            if topic:
                lines += f"**Topic:** {topic[:200]}\n"
            slowmode = getattr(channel, "slowmode_delay", 0) or 0
            if slowmode:
                lines += f"**Slowmode:** `{slowmode}s`\n"
            if getattr(channel, "nsfw", False):
                lines += "**NSFW:** `True`\n"
        if _channel_kind(channel) in ("voice", "stage"):
            bitrate = getattr(channel, "bitrate", 0) or 0
            limit = getattr(channel, "user_limit", 0) or 0
            lines += f"**Bitrate:** `{bitrate // 1000}kbps` · **User Limit:** `{limit or 'Unlimited'}`\n"
        overwrites = getattr(channel, "overwrites", {}) or {}
        if overwrites:
            lines += f"**Permission Overwrites:** `{len(overwrites)}`\n"
        return lines

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        entry = await self._audit_entry(
            channel.guild, discord.AuditLogAction.channel_delete, channel.id)
        responsible = entry.user if entry else None

        # The channel is gone, so its settings are snapshotted now: the restore
        # button can only put back what it knows about.
        snapshot = await save_snapshot(channel.guild.id, "channel", channel_snapshot(channel))

        body = (
            f"**Channel:** `#{channel.name}` (ID: `{channel.id}`)\n"
            f"**Type:** {_channel_kind(channel).title()}\n"
            f"**Category:** {self._category_text(channel)}\n"
            f"**Position:** `{getattr(channel, 'position', 0)}`\n"
            + self._channel_detail_lines(channel)
            + f"**Deleted By:** {responsible.mention if responsible else 'Unknown'}"
        )
        if snapshot:
            body += "\n-# Press **Restore Channel** to recreate it with the same settings."
        await self.log_event(
            channel.guild, "channels", "Channel Deleted", body,
            target_id=channel.id,
            revert=("channel", snapshot) if snapshot else None,
        )

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        changes = []
        # What the Revert button puts back, keyed by the edit option it maps to.
        # Only fields that actually changed are stored, so a revert never
        # overwrites a setting nobody touched.
        revert_before: dict = {}

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")
            revert_before["name"] = before.name

        if self._category_text(before) != self._category_text(after):
            changes.append(
                f"**Category:** {self._category_text(before)} → {self._category_text(after)}")
            revert_before["category_id"] = getattr(
                getattr(before, "category", None), "id", None)

        if isinstance(after, discord.TextChannel) or isinstance(after, discord.ForumChannel):
            if getattr(before, "topic", None) != getattr(after, "topic", None):
                b_topic = getattr(before, "topic", None) or "*None*"
                a_topic = getattr(after, "topic", None) or "*None*"
                changes.append(f"**Topic:** {b_topic} → {a_topic}")
                revert_before["topic"] = getattr(before, "topic", None)
            if getattr(before, "slowmode_delay", 0) != getattr(after, "slowmode_delay", 0):
                changes.append(f"**Slowmode:** `{getattr(before, 'slowmode_delay', 0)}s` → `{getattr(after, 'slowmode_delay', 0)}s`")
                revert_before["slowmode_delay"] = int(
                    getattr(before, "slowmode_delay", 0) or 0)
            if getattr(before, "nsfw", False) != getattr(after, "nsfw", False):
                changes.append(f"**NSFW:** `{getattr(before, 'nsfw', False)}` → `{getattr(after, 'nsfw', False)}`")
                revert_before["nsfw"] = bool(getattr(before, "nsfw", False))

        if isinstance(after, (discord.VoiceChannel, discord.StageChannel)):
            if getattr(before, "bitrate", None) != getattr(after, "bitrate", None):
                changes.append(f"**Bitrate:** `{getattr(before, 'bitrate', 0) // 1000}kbps` → `{getattr(after, 'bitrate', 0) // 1000}kbps`")
                revert_before["bitrate"] = int(getattr(before, "bitrate", 0) or 0)
            if getattr(before, "user_limit", 0) != getattr(after, "user_limit", 0):
                b_lim = getattr(before, "user_limit", 0) or "Unlimited"
                a_lim = getattr(after, "user_limit", 0) or "Unlimited"
                changes.append(f"**User Limit:** `{b_lim}` → `{a_lim}`")
                revert_before["user_limit"] = int(getattr(before, "user_limit", 0) or 0)

        # ── Permission overwrites ────────────────
        # Granting or revoking a member/role overwrite is the most consequential
        # channel edit and used to be silent unless the category was logged by
        # the role or member listener.
        before_overwrites = getattr(before, "overwrites", {})
        after_overwrites = getattr(after, "overwrites", {})
        overwrite_restore: list[dict] = []
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
                # The overwrite did not exist before, so a revert removes it.
                overwrite_restore.append(removed_overwrite_entry(target))
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
                    overwrite_restore.append(overwrite_entry(target, old))
        for target in before_overwrites:
            if target not in after_overwrites:
                label = getattr(target, "mention", None) or getattr(target, "name", str(target))
                changes.append(f"**Overwrite Removed** for {label}")
                overwrite_restore.append(overwrite_entry(target, before_overwrites[target]))

        if not changes:
            return

        entry = await self._audit_entry(
            after.guild, discord.AuditLogAction.channel_update, after.id)
        responsible = entry.user if entry else None

        snapshot = None
        if revert_before or overwrite_restore:
            snapshot = await save_snapshot(
                after.guild.id, "channel-update",
                {"channel_id": after.id, "before": revert_before,
                 "overwrites": overwrite_restore},
            )

        body = (
            f"**Channel:** {after.mention} (`{after.name}` — ID: `{after.id}`)\n"
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        if snapshot:
            body += "\n-# Press **Revert Changes** to put these settings back."
        await self.log_event(
            after.guild, "channels", "Channel Updated", body,
            channel_id=after.id,
            revert=("channel-update", snapshot) if snapshot else None,
        )

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        entry = await self._audit_entry(
            role.guild, discord.AuditLogAction.role_create, role.id)
        responsible = entry.user if entry else None

        color_text = str(role.color) if role.color.value else "Default"
        body = (
            f"**Role:** {role.mention} (`{role.name}` — ID: `{role.id}`)\n"
            f"**Color:** `{color_text}` · **Hoisted:** `{role.hoist}` · **Mentionable:** `{role.mentionable}`\n"
            f"**Position:** `{role.position}` · **Members:** `{len(role.members)}`\n"
            f"**Permissions:** {_permission_list(role.permissions)}\n"
            f"**Created By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(role.guild, "roles", "Role Created", body, target_id=role.id)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        entry = await self._audit_entry(
            role.guild, discord.AuditLogAction.role_delete, role.id)
        responsible = entry.user if entry else None

        # The role is gone, so its settings are snapshotted now: the restore
        # button can only recreate what it knows about.
        snapshot = await save_snapshot(role.guild.id, "role", role_snapshot(role))

        body = (
            f"**Role:** `{role.name}` (ID: `{role.id}`)\n"
            f"**Color:** `{role.colour}` · **Hoisted:** `{role.hoist}` · **Mentionable:** `{role.mentionable}`\n"
            f"**Position:** `{role.position}`\n"
            f"**Permissions:** {_permission_list(role.permissions)}\n"
            f"**Deleted By:** {responsible.mention if responsible else 'Unknown'}"
        )
        if snapshot:
            body += "\n-# Press **Restore Role** to recreate it with the same settings."
        await self.log_event(
            role.guild, "roles", "Role Deleted", body,
            target_id=role.id,
            revert=("role", snapshot) if snapshot else None,
        )

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
            f"**Role:** {after.mention} (`{after.name}` — ID: `{after.id}`)\n"
            f"**Members:** `{len(after.members)}` · **Position:** `{after.position}`\n"
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after.guild, "roles", "Role Updated", body, target_id=after.id)

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

        else:
            # Same channel: the category promises mute/deafen changes too, and
            # they used to be silent. self_stream and self_video are only sent
            # for some guilds, so a missing attribute changes nothing.
            states = []
            for attribute, label, on_text, off_text in (
                ("self_mute", "Self Mute", "muted", "unmuted"),
                ("self_deaf", "Self Deafen", "deafened", "undeafened"),
                ("self_stream", "Stream", "started streaming", "stopped streaming"),
                ("self_video", "Camera", "camera on", "camera off"),
                ("mute", "Server Mute", "server-muted", "server-unmuted"),
                ("deaf", "Server Deafen", "server-deafened", "server-undeafened"),
            ):
                was = getattr(before, attribute, None)
                now = getattr(after, attribute, None)
                if was is None or now is None or was == now:
                    continue
                states.append(f"**{label}:** `{on_text if now else off_text}`")
            if not states:
                return
            channel = after.channel or before.channel
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Channel:** {channel.mention if channel else 'Unknown'}\n"
                + "\n".join(states)
            )
            await self.log_event(
                guild, "voice", "Voice State Updated", body, target_id=member.id)

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
