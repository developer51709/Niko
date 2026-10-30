import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument, EmojiNotFound
import io
import os
import re
import shutil
import tempfile
import time
import zipfile
from urllib.parse import unquote, urlparse
import aiohttp
import asyncio
from typing import Optional
from config.emojis import get_emoji
from utils import logging as log
from utils.archive_safety import scan_zip
from utils.i18n import make_flat_msg
from utils.prefix_manager import resolve_prefix
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

MESSAGES = load_locales("cogs.admin", "emoji")

msg = make_flat_msg(MESSAGES)

EMOJI_REGEX = re.compile(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]+):(?P<id>[0-9]+)>")

# Discord's emoji endpoints are strict and the bucket is easy to overshoot, so
# bulk uploads are paced instead of fired off back to back.
EMOJI_UPLOAD_INTERVAL = 1.5
EMOJI_MAX_BYTES = 256 * 1024
MAX_DOWNLOAD_BYTES = 40 * 1024 * 1024
MAX_JOBS = 250
IMAGE_EXTENSIONS = (".png", ".gif", ".jpg", ".jpeg")
# discord.py retries 429s internally without telling anyone. When an upload
# takes noticeably longer than expected we surface the throttle to the user.
THROTTLE_NOTICE_SECONDS = 2.5

# How a refused archive is explained to the user. ``scan_zip`` reports a
# machine-readable code; every code has to map to a localized reason.
ZIP_SCAN_REASONS = {
    "invalid": "reason_zip_invalid",
    "encrypted": "reason_zip_invalid",
    "too_many_entries": "reason_too_many",
    "entry_too_large": "reason_zip_bomb",
    "too_large": "reason_zip_bomb",
    "compression_ratio": "reason_zip_bomb",
    "nested_archive": "reason_zip_bomb",
}


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _normalise_name(raw: str) -> str:
    """Turn a filename or emoji name into a valid Discord emoji name."""
    base = unquote(raw).replace("\\", "/").rsplit("/", 1)[-1]
    base = os.path.splitext(base)[0]
    base = re.sub(r"[^A-Za-z0-9_]+", "_", base).strip("_")
    if len(base) > 32:
        base = base[:32].rstrip("_")
    if len(base) < 2:
        base = f"{base}_emoji"[:32] if base else "emoji"
    return base


def _unique_name(name: str, used: set) -> str:
    candidate = name
    index = 2
    while candidate.lower() in used:
        suffix = f"_{index}"
        candidate = f"{name[:32 - len(suffix)]}{suffix}"
        index += 1
    used.add(candidate.lower())
    return candidate


def _is_animated_image(data: bytes) -> bool:
    return data[:6] in (b"GIF87a", b"GIF89a")


def _names_preview(names, limit: int = 6) -> str:
    shown = ", ".join(f"`{name}`" for name in names[:limit])
    if len(names) > limit:
        shown += f" +{len(names) - limit}"
    return shown


def _group_reasons(items) -> dict:
    grouped: dict[str, list[str]] = {}
    for name, reason in items:
        grouped.setdefault(reason, []).append(name)
    return grouped


# ─────────────────────────────────────────
#  Bulk upload cards (CV2)
# ─────────────────────────────────────────

STEAL_ACCENT = discord.Colour(0xC8A882)
STEAL_ACCENT_OK = discord.Colour(0x57F287)
STEAL_ACCENT_WARN = discord.Colour(0xFEE75C)
STEAL_ACCENT_ERROR = discord.Colour(0xED4245)


def _steal_view(*items, accent: discord.Colour) -> discord.ui.LayoutView:
    """Wrap bulk-upload card items in one accented cv2 container."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items, accent_colour=accent))
    return view


def _progress_bar(done: int, total: int, width: int = 14) -> str:
    """Discord has no progress component, so the bar is drawn with blocks."""
    ratio = 0.0 if total <= 0 else min(1.0, done / total)
    filled = int(round(ratio * width))
    return "▰" * filled + "▱" * (width - filled)


def _steal_progress_view(ctx, *, done, total, added, skipped, failed, notice) -> discord.ui.LayoutView:
    """The live card shown while a bulk upload is running."""
    percent = 0 if total <= 0 else min(100, round(done / total * 100))
    items = [
        discord.ui.TextDisplay(
            content=f"### {get_emoji('paint')} {msg(ctx, 'stealing_title')}"
        ),
        discord.ui.TextDisplay(
            content=msg(ctx, "steal_progress_count", done=done, total=total)
        ),
        discord.ui.TextDisplay(content=f"{_progress_bar(done, total)}  `{percent}%`"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=msg(ctx, "steal_progress_tally", added=added, skipped=skipped, failed=failed)
        ),
    ]
    if notice:
        items.append(discord.ui.TextDisplay(content=f"-# {notice}"))
    return _steal_view(*items, accent=STEAL_ACCENT)


def _steal_overview_view(ctx, *, checked, added, skipped, failed, notice,
                         slots, limit, aborted, thumbnail_url) -> discord.ui.LayoutView:
    """The final card: what was uploaded and everything that was refused."""
    success = bool(added)
    heading = [
        discord.ui.TextDisplay(
            content=f"### {get_emoji('tick') if success else get_emoji('warning')} "
                    f"{msg(ctx, 'steal_overview_title')}"
        ),
        discord.ui.TextDisplay(
            content=f"-# {msg(ctx, 'steal_overview_subtitle', guild=getattr(ctx.guild, 'name', 'this server'), checked=checked)}"
        ),
    ]
    items = []
    if thumbnail_url:
        items.append(discord.ui.Section(*heading, accessory=discord.ui.Thumbnail(thumbnail_url)))
    else:
        items.extend(heading)
    summary = msg(ctx, "steal_overview_added", count=len(added)) if success else msg(ctx, "steal_none_added")
    if aborted:
        summary += f"\n-# {msg(ctx, 'steal_aborted')}"
    items.extend([
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=summary),
        discord.ui.TextDisplay(
            content=f"-# {msg(ctx, 'steal_overview_slots', static=slots[False], animated=slots[True], limit=limit)}"
        ),
    ])

    for group, key in ((skipped, "steal_skip_line"), (failed, "steal_fail_line")):
        lines = [
            msg(ctx, key, count=len(names), reason=reason, names=_names_preview(names))
            for reason, names in _group_reasons(group).items()
        ]
        if lines:
            items.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            items.append(discord.ui.TextDisplay(content="\n".join(lines)))

    if notice:
        items.append(discord.ui.TextDisplay(content=f"-# {notice}"))
    return _steal_view(*items, accent=STEAL_ACCENT_OK if success else STEAL_ACCENT_WARN)


def _retry_after_seconds(exc: Exception) -> float:
    """Best-effort extraction of the wait time from a 429."""
    retry_after = getattr(exc, "retry_after", None)
    if isinstance(retry_after, (int, float)):
        return max(0.0, float(retry_after))

    headers = getattr(getattr(exc, "response", None), "headers", None)
    if headers:
        for header in ("Retry-After", "X-RateLimit-Reset-After"):
            raw = headers.get(header)
            if raw:
                try:
                    return max(0.0, float(raw))
                except (TypeError, ValueError):
                    pass

    match = re.search(r'"retry_after"\s*:\s*([0-9.]+)', getattr(exc, "text", "") or "")
    if match:
        return max(0.0, float(match.group(1)))
    return 5.0


def _safe_member_path(root: str, filename: str) -> Optional[str]:
    """Resolve a zip member inside *root*, refusing path traversal."""
    parts = [part for part in filename.replace("\\", "/").split("/") if part not in ("", ".", "..")]
    if not parts:
        return None
    candidate = os.path.join(root, *parts)
    try:
        if os.path.commonpath([os.path.realpath(root), os.path.realpath(candidate)]) != os.path.realpath(root):
            return None
    except ValueError:
        return None
    return candidate


def _extract_zip_images(data: bytes, target_dir: str):
    """Extract supported images from a zip into *target_dir*.

    Returns ``(extracted, skipped)`` where *extracted* is a list of
    ``(filename, path)`` pairs (sorted so packs upload in a stable order) and
    *skipped* is a list of ``(filename, reason)``.
    """
    extracted = []
    skipped = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            name = member.filename.replace("\\", "/")
            base = name.rsplit("/", 1)[-1]
            if name.startswith("__MACOSX/") or base.startswith("."):
                continue
            if not name.lower().endswith(IMAGE_EXTENSIONS):
                continue
            if len(extracted) >= MAX_JOBS:
                skipped.append((base, "reason_too_many"))
                continue
            if member.file_size > EMOJI_MAX_BYTES:
                skipped.append((base, "reason_too_large"))
                continue
            path = _safe_member_path(target_dir, name)
            if path is None:
                continue
            os.makedirs(os.path.dirname(path), exist_ok=True)
            written = 0
            oversized = False
            with archive.open(member) as source, open(path, "wb") as destination:
                while True:
                    chunk = source.read(64 * 1024)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > EMOJI_MAX_BYTES:
                        # The header can lie about the size; never trust it.
                        oversized = True
                        break
                    destination.write(chunk)
            if oversized:
                os.remove(path)
                skipped.append((base, "reason_too_large"))
                continue
            extracted.append((base, path))
    extracted.sort(key=lambda item: item[0].lower())
    return extracted, skipped


def _remaining_slots(guild) -> dict:
    """Remaining emoji slots per animated flag.

    Discord keeps separate buckets for static and animated emojis, so both are
    tracked independently.
    """
    limit = getattr(guild, "emoji_limit", None) or 50
    static = sum(1 for emoji in guild.emojis if not emoji.animated)
    animated = sum(1 for emoji in guild.emojis if emoji.animated)
    return {False: limit - static, True: limit - animated}


# Prefix resolver (required for dynamic prefixes to work)
async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await resolve_prefix(bot, ctx_or_interaction)


class EmojiManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        await self.session.close()

    async def _get_emoji_info(self, emoji_string: str):
        match = EMOJI_REGEX.match(emoji_string)
        if not match:
            return None, None, None, None 

        emoji_id = match.group("id")
        emoji_name = match.group("name")
        animated = bool(match.group("animated"))
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if animated else 'png'}"

        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    return emoji_name, image_data, animated, url
        except Exception:
            pass
        return emoji_name, None, animated, None

    async def _download(self, url: str):
        """Download *url*. Returns ``(data, error)`` with exactly one set."""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status != 200:
                    return None, "failed"
                if resp.content_length and resp.content_length > MAX_DOWNLOAD_BYTES:
                    return None, "too_large"
                data = await resp.read()
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            return None, "failed"
        if len(data) > MAX_DOWNLOAD_BYTES:
            return None, "too_large"
        return data, None

    async def _create_emoji(self, guild, name: str, image: bytes, on_throttle):
        """Create one emoji, retrying politely when Discord rate limits us.

        Returns ``(emoji, None)`` on success and ``(None, reason)`` otherwise.
        """
        for _ in range(6):
            started = time.monotonic()
            try:
                emoji = await guild.create_custom_emoji(name=name, image=image)
            except discord.RateLimited as exc:
                wait = max(0.0, float(exc.retry_after))
                await on_throttle(wait)
                await asyncio.sleep(wait + 0.25)
                continue
            except discord.Forbidden:
                return None, "forbidden"
            except discord.HTTPException as exc:
                if exc.status == 429:
                    wait = _retry_after_seconds(exc)
                    await on_throttle(wait)
                    await asyncio.sleep(wait + 0.25)
                    continue
                if exc.status == 403:
                    return None, "forbidden"
                return None, f"HTTP {exc.status}"
            if time.monotonic() - started >= THROTTLE_NOTICE_SECONDS:
                # discord.py sat on a rate limit internally; let the user know.
                await on_throttle(None)
            return emoji, None
        return None, "HTTP 429"

    async def _collect_jobs(self, ctx, items, attachment_zips, temp_dirs):
        """Resolve command arguments into ``(name_hint, payload)`` upload jobs.

        ``payload`` is either raw image bytes or a path to an extracted file.
        """
        jobs = []
        skipped = []

        async def add_zip(data: bytes, label: str):
            if len(data) > MAX_DOWNLOAD_BYTES:
                skipped.append((label, msg(ctx, "reason_zip_too_large")))
                return
            # Screen the archive before opening it: a zip bomb is refused here,
            # while it is still a few kilobytes of metadata.
            report = await asyncio.to_thread(scan_zip, data)
            if not report.ok:
                log.warning("emoji", f"Refused archive {label!r} ({report.code}): {report.detail}")
                skipped.append((label, msg(ctx, ZIP_SCAN_REASONS.get(report.code, "reason_zip_bomb"))))
                return
            target_dir = tempfile.mkdtemp(prefix="niko-emojis-")
            temp_dirs.append(target_dir)
            try:
                extracted, refused = await asyncio.to_thread(_extract_zip_images, data, target_dir)
            except zipfile.BadZipFile:
                skipped.append((label, msg(ctx, "reason_zip_invalid")))
                return
            except (OSError, RuntimeError):
                skipped.append((label, msg(ctx, "reason_download")))
                return
            skipped.extend((name, msg(ctx, reason)) for name, reason in refused)
            if not extracted:
                skipped.append((label, msg(ctx, "reason_zip_empty")))
                return
            jobs.extend(extracted)

        for item in items:
            cleaned = item.strip()
            if EMOJI_REGEX.fullmatch(cleaned):
                name, data, _animated, _url = await self._get_emoji_info(cleaned)
                if data:
                    jobs.append((name or cleaned, data))
                else:
                    skipped.append((name or cleaned, msg(ctx, "reason_download")))
                continue
            if not _is_http_url(cleaned):
                skipped.append((cleaned[:32], msg(ctx, "reason_invalid")))
                continue
            data, error = await self._download(cleaned)
            if error:
                reason = "reason_zip_too_large" if error == "too_large" else "reason_download"
                skipped.append((_normalise_name(cleaned), msg(ctx, reason)))
                continue
            if data[:4] == b"PK\x03\x04" or urlparse(cleaned).path.lower().endswith(".zip"):
                await add_zip(data, _normalise_name(cleaned))
            else:
                jobs.append((_normalise_name(cleaned), data))

        for attachment in attachment_zips:
            if attachment.size and attachment.size > MAX_DOWNLOAD_BYTES:
                skipped.append((attachment.filename, msg(ctx, "reason_zip_too_large")))
                continue
            try:
                data = await attachment.read()
            except discord.HTTPException:
                skipped.append((attachment.filename, msg(ctx, "reason_download")))
                continue
            await add_zip(data, _normalise_name(attachment.filename))

        return jobs[:MAX_JOBS], skipped

    async def _steal(self, ctx, items, attachment_zips=(), override_name: Optional[str] = None):
        """Shared steal pipeline for emoji strings, links and zip packs."""
        guild = ctx.guild
        temp_dirs = []
        try:
            jobs, skipped = await self._collect_jobs(ctx, items, attachment_zips, temp_dirs)
            if override_name and jobs:
                jobs = [(override_name, jobs[0][1])]

            if not jobs:
                return await ctx.send(view=self._no_jobs_view(ctx, skipped))

            limit = getattr(guild, "emoji_limit", 50)
            remaining = _remaining_slots(guild)
            if remaining[False] <= 0 and remaining[True] <= 0:
                return await ctx.send(view=_steal_view(
                    discord.ui.TextDisplay(
                        content=f"### {get_emoji('warning')} {msg(ctx, 'steal_full_title')}"
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(content=msg(ctx, "server_full", limit=limit)),
                    accent=STEAL_ACCENT_ERROR,
                ))

            total = len(jobs)
            state = {
                "done": 0,
                "notice": "",
                "added": 0,
                "skipped": len(skipped),
                "failed": 0,
            }
            progress = await ctx.send(view=_steal_progress_view(
                ctx, done=0, total=total,
                added=0, skipped=state["skipped"], failed=0, notice="",
            ))
            last_edit = 0.0

            async def show(force: bool = False):
                nonlocal last_edit
                now = time.monotonic()
                if not force and now - last_edit < 2.0:
                    return
                last_edit = now
                try:
                    await progress.edit(view=_steal_progress_view(
                        ctx,
                        done=state["done"],
                        total=total,
                        added=state["added"],
                        skipped=state["skipped"],
                        failed=state["failed"],
                        notice=state["notice"],
                    ))
                except discord.HTTPException:
                    pass

            async def on_throttle(wait):
                if wait is None:
                    notice = msg(ctx, "rate_limited")
                else:
                    notice = msg(ctx, "rate_limited_wait", seconds=max(1, round(wait)))
                if notice != state["notice"]:
                    state["notice"] = notice
                    await show(force=True)

            used = {emoji.name.lower() for emoji in guild.emojis}
            added, failed = [], []
            aborted = False

            for position, (name_hint, payload) in enumerate(jobs, start=1):
                if isinstance(payload, str):
                    try:
                        with open(payload, "rb") as handle:
                            data = handle.read()
                    except OSError:
                        failed.append((name_hint, msg(ctx, "reason_download")))
                        state["failed"] += 1
                        state["done"] = position
                        await show()
                        continue
                else:
                    data = payload

                animated = _is_animated_image(data)
                if len(data) > EMOJI_MAX_BYTES:
                    skipped.append((name_hint, msg(ctx, "reason_too_large")))
                    state["skipped"] += 1
                    state["done"] = position
                    await show()
                    continue
                if remaining[animated] <= 0:
                    skipped.append((name_hint, msg(ctx, "reason_no_slots")))
                    state["skipped"] += 1
                    state["done"] = position
                    await show()
                    continue

                name = _unique_name(_normalise_name(name_hint), used)
                emoji, error = await self._create_emoji(guild, name, data, on_throttle)
                state["done"] = position

                if emoji is None:
                    failed.append((name_hint, msg(ctx, "no_perms") if error == "forbidden" else error))
                    state["failed"] += 1
                    if error == "forbidden":
                        aborted = True
                        break
                else:
                    added.append(emoji.name)
                    state["added"] += 1
                    remaining[animated] -= 1

                await show()
                if position < total:
                    await asyncio.sleep(EMOJI_UPLOAD_INTERVAL)

            if aborted:
                skipped.extend((hint, msg(ctx, "no_perms")) for hint, _payload in jobs[position:])
                state["skipped"] += len(jobs) - position

            overview = _steal_overview_view(
                ctx,
                checked=state["done"],
                added=added,
                skipped=skipped,
                failed=failed,
                notice=state["notice"],
                slots=remaining,
                limit=limit,
                aborted=aborted,
                thumbnail_url=guild.icon.url if guild.icon else self.bot.user.display_avatar.url,
            )
            try:
                await progress.edit(view=overview)
            except discord.HTTPException:
                await ctx.send(view=overview)

            if added:
                log.success("Emoji", f"Stole {len(added)} emojis in {guild.name}")
        finally:
            for directory in temp_dirs:
                shutil.rmtree(directory, ignore_errors=True)

    @staticmethod
    def _no_jobs_view(ctx, skipped) -> discord.ui.LayoutView:
        """The card shown when nothing usable was collected from the message."""
        if not skipped:
            return _steal_view(
                discord.ui.TextDisplay(content=msg(ctx, "not_found")),
                accent=STEAL_ACCENT_ERROR,
            )
        lines = [
            msg(ctx, "steal_skip_line", count=len(names), reason=reason, names=_names_preview(names))
            for reason, names in _group_reasons(skipped).items()
        ]
        return _steal_view(
            discord.ui.TextDisplay(
                content=f"### {get_emoji('warning')} {msg(ctx, 'steal_nothing_title')}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="\n".join(lines)),
            accent=STEAL_ACCENT_WARN,
        )

    @commands.command(name="emojimanager", aliases=["em"], help=CMDS.help("emojimanager"),
    )
    async def emojimanager_help(self, ctx):
        prefix = await _resolve_prefix(self.bot, ctx)
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"### {msg(ctx, 'emojimanager_title')}"
                ),
                discord.ui.TextDisplay(
                    content=f"-# {msg(ctx, 'emojimanager_description')}"
                ),
                accessory=discord.ui.Thumbnail(self.bot.user.avatar.url)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        
        commands_list = [
            (f"{prefix}steal <emoji | link | .zip> [...]", f"{msg(ctx, 'steal_description')}"),
            (f"{prefix}surl <url> [name]", f"{msg(ctx, 'surl_description')}"),
            (f"{prefix}enlarge <emoji>", f"{msg(ctx, 'enlarge_description')}"),
            (f"{prefix}emojistats", f"{msg(ctx, 'emojistats_description')}"),
            (f"{prefix}re <emoji>", f"{msg(ctx, 're_description')}")
        ]
        for cmd, desc in commands_list:
            container.add_item(
                discord.ui.TextDisplay(
                    content=f"**`{cmd}`**\n{desc}"
                )
            )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.command(
        name="steal",
        aliases=["sm", "stealall", "steal-multiple"],
        help=CMDS.help("steal"))
    @has_permissions(manage_guild=True)
    async def steal_emoji(self, ctx, *items: str):
        """Steal one emoji, several emojis, image links or a whole zip pack."""
        attachment_zips = [
            attachment
            for attachment in getattr(ctx.message, "attachments", []) or []
            if attachment.filename.lower().endswith(".zip")
        ]
        if not items and not attachment_zips:
            prefix = await _resolve_prefix(self.bot, ctx)
            return await ctx.send(view=_steal_view(
                discord.ui.TextDisplay(content=f"### {get_emoji('paint')} {msg(ctx, 'stealing_title')}"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=msg(ctx, "steal_usage", prefix=prefix)),
                accent=STEAL_ACCENT,
            ))
        await ctx.typing()
        await self._steal(ctx, list(items), attachment_zips)

    @commands.command(name="steal-from-url", aliases=["surl"], help=CMDS.help("steal-from-url"),
    )
    @has_permissions(manage_guild=True)
    async def steal_from_url(self, ctx, url: str, name: Optional[str] = None):
        if not _is_http_url(url):
            return await ctx.send(msg(ctx, "error", error=msg(ctx, "invalid_url")))
        await ctx.typing()
        await self._steal(ctx, [url], override_name=name)

    @commands.command(name="enlarge", help=CMDS.help("enlarge"),
    )
    async def enlarge_emoji(self, ctx, emoji_string: str):
        name, data, _, url = await self._get_emoji_info(emoji_string)
        if not url:
            return await ctx.send(msg(ctx, "not_found"))
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### 🔍 :{name}:"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=url
                )
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.command(name="emojistats", help=CMDS.help("emojistats"),
    )
    async def emoji_stats(self, ctx):
        guild = ctx.guild
        static = len([e for e in guild.emojis if not e.animated])
        animated = len([e for e in guild.emojis if e.animated])
        limit = guild.emoji_limit
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(ctx, "emoji_stats_title")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=msg(ctx, "emoji_stats_body", static=static, animated=animated, limit=limit)
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    @commands.command(name="remove-emoji", aliases=["re"], help=CMDS.help("remove-emoji"),
    )
    @has_permissions(manage_guild=True)
    async def remove_emoji(self, ctx, emoji: discord.Emoji):
        try:
            name = emoji.name
            await emoji.delete()
            await ctx.send(msg(ctx, "emoji_removed", name=name))
        except Exception:
            await ctx.send(msg(ctx, "no_perms"))


async def setup(bot):
    await bot.add_cog(EmojiManagerCog(bot))
