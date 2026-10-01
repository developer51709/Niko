"""
mrbeast_scam.py — Experimental MrBeast image scam detection.

Flow
────
1. Anyone right-clicks a message → "🚩 Report MrBeast Scam".
2. The message's image assets (plus context) are forwarded to the scam
   review channel in the private staff-only server.
3. Niko staff press **Confirm Scam** (adds the image's perceptual hash to
   the detection database) or **Reject** (closes the report).
4. When a confirmed image is later posted in any server, Niko deletes it and
   logs the removal to that server's automod log channel (if configured).
5. Every log entry carries a **Report False Positive** button. Pressing it
   sends the image back to the staff review queue so mis-detections can be
   removed from the filter, improving its accuracy over time.

Similarity is a 64-bit difference hash (dHash) compared by Hamming distance,
so re-encoded / resized / re-compressed variants of a confirmed scam image
are still caught. Hashes are computed with Pillow, which is already a
project dependency.
"""

from __future__ import annotations

import io
import json
import re
from datetime import datetime, timezone

import aiohttp
import discord
from discord import MediaGalleryItem
from discord import app_commands
from discord.ext import commands

from config.ids import OWNER_IDS, SCAM_REVIEW_CHANNEL, SCAM_REVIEW_GUILD
from utils import logging

# ── Constants ─────────────────────────────────────────────────────────────────

# Hamming distance below which an image counts as "similar" to a known scam.
SIMILARITY_THRESHOLD = 10

# Internal report state values.
STATE_PENDING = "pending"
STATE_CONFIRMED = "confirmed"
STATE_REJECTED = "rejected"

_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def _safe_upload_name(name: str, index: int) -> str:
    """Sanitize an attachment filename for use with attachment:// URIs.

    Discord requires ASCII alphanumeric names (plus _ - and .) for CV2
    attachment references, so strip everything else and guarantee uniqueness.
    """
    stem, _, ext = name.rpartition(".")
    ext = re.sub(r"[^A-Za-z0-9]", "", ext)[:5].lower()
    stem = re.sub(r"[^A-Za-z0-9_-]", "_", stem)[:60] or "image"
    return f"{stem}_{index}.{ext or 'png'}"

_ACCENT_WARN = 0xFEE75C
_ACCENT_ERROR = 0xED4245
_ACCENT_OK = 0x57F287
_ACCENT_MUTED = 0x2E3440
_ACCENT_BRAND = 0xC8A882


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _is_image_attachment(attachment: discord.Attachment) -> bool:
    content_type = (attachment.content_type or "").lower()
    if content_type.startswith("image/"):
        return True
    return (attachment.filename or "").lower().endswith(_IMAGE_EXTENSIONS)


async def _get_automod_log_channel(bot: commands.Bot, guild: discord.Guild):
    """Resolve the guild's configured automod log channel (may be None).

    Uses the ServerLogger cog's own config loader, which handles both SQLite
    (JSON ``data`` column) and MongoDB (individual document fields, string
    ``_id``) — a direct SQL lookup silently matches nothing on Mongo.
    """
    from cogs.logging.formatters import _guild_config, _load_log_config

    try:
        data = await _load_log_config()
        cfg = _guild_config(data, guild.id)
    except Exception as exc:
        logging.debug("MrBeastScam", f"Could not load logging config for {guild.name}: {exc}")
        return None
    channel_id = cfg.get("automod")
    if not channel_id:
        logging.debug("MrBeastScam", f"No automod log channel configured in {guild.name}")
        return None
    channel = guild.get_channel(int(channel_id))
    if channel is None:
        logging.debug("MrBeastScam", f"Automod log channel {channel_id} not found in {guild.name}")
    return channel


# ── Perceptual hashing (64-bit dHash) ────────────────────────────────────────

def _dhash_bits(image_bytes: bytes) -> list[int] | None:
    """64-bit difference hash (dHash) as a list of 0/1 ints. None on failure."""
    try:
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes)).convert("L").resize((9, 8))
        pixels = list(image.getdata())
        bits: list[int] = []
        for row in range(8):
            row_start = row * 9
            for col in range(8):
                bits.append(1 if pixels[row_start + col] > pixels[row_start + col + 1] else 0)
        return bits
    except Exception:
        return None


def _hash_hex(bits: list[int]) -> str:
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return f"{value:016x}"


def _bits_from_str(value) -> list[int] | None:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "01" for c in value):
        return None
    return [int(c) for c in value]


def _hex_to_bits(hex_hash: str) -> list[int] | None:
    """Inverse of _hash_hex: 16 hex chars → 64 bits, MSB first."""
    if not isinstance(hex_hash, str):
        return None
    hex_hash = hex_hash.strip().lower()
    if len(hex_hash) != 16 or any(c not in "0123456789abcdef" for c in hex_hash):
        return None
    value = int(hex_hash, 16)
    return [(value >> (63 - i)) & 1 for i in range(64)]


def _hamming(bits_a: list[int], bits_b: list[int]) -> int:
    return sum(a != b for a, b in zip(bits_a, bits_b))


def _match_hash(bits: list[int], rows) -> tuple[bool, int, str | None]:
    """Return (matched, distance, matched_hash) against known scam hashes."""
    best_distance = 65
    best_hash = None
    for row in rows:
        known = _bits_from_str(row.get("hash_bits"))
        hash_id = row.get("image_hash")
        if known is None or hash_id is None:
            continue
        distance = _hamming(bits, known)
        if distance < best_distance:
            best_distance = distance
            best_hash = hash_id
    if best_distance <= SIMILARITY_THRESHOLD:
        return True, best_distance, best_hash
    return False, best_distance, None


def _cv(text: str, *, colour: int = _ACCENT_BRAND) -> discord.ui.LayoutView:
    """Small CV2 status card — matches the single-message helper in nitro.py."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        accent_colour=discord.Colour(colour),
    ))
    return view


# ── COG ───────────────────────────────────────────────────────────────────────

class MrBeastScam(commands.Cog, name="MrBeastScam"):
    """Experimental MrBeast image scam detection (context-menu reported)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._ctx_report = app_commands.ContextMenu(
            name="🚩 Report MrBeast Scam",
            callback=self._report_context_menu,
        )
        self.bot.tree.add_command(self._ctx_report)

        # Persistent review / false-positive buttons survive restarts.
        self.bot.add_dynamic_items(
            _ReviewConfirmButton, _ReviewRejectButton, _FalsePositiveButton, _RemoveScamButton
        )

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self._ctx_report.name, type=self._ctx_report.type)
        self.bot.remove_dynamic_items(
            _ReviewConfirmButton, _ReviewRejectButton, _FalsePositiveButton, _RemoveScamButton
        )

    # ── helpers ───────────────────────────────────────────────────────────

    def _review_guild(self) -> discord.Guild | None:
        if not SCAM_REVIEW_GUILD or not SCAM_REVIEW_CHANNEL:
            return None
        return self.bot.get_guild(SCAM_REVIEW_GUILD)

    def _review_channel(self) -> discord.abc.Messageable | None:
        guild = self._review_guild()
        if guild is None:
            return None
        channel = guild.get_channel(SCAM_REVIEW_CHANNEL)
        return channel if isinstance(channel, discord.TextChannel) else None

    def _is_staff_reviewer(self, user: discord.abc.User) -> bool:
        if user.id in OWNER_IDS:
            return True
        guild = self._review_guild()
        if guild is None:
            return False
        member = guild.get_member(user.id)
        if member is None:
            return False
        return member.guild_permissions.manage_guild or member.guild_permissions.administrator

    async def _store_bits(self, bits: list[int], *, preview_url: str | None,
                          confirmed_by: int,
                          fallback_preview_url: str | None = None) -> str:
        """Add (or refresh) a confirmed scam hash, preserving its counters.

        ``preview_url`` should be a review-channel attachment URL (stable).
        Expiring reporter CDN links are only used as a fallback when no
        durable preview exists, so the false-positive report keeps working.
        """
        hex_hash = _hash_hex(bits)
        existing = await self.bot.cxn.fetchrow(
            "SELECT times_deleted, false_positives FROM mrbeast_scams WHERE image_hash = $1",
            hex_hash,
        )
        times_deleted = existing["times_deleted"] if existing else 0
        false_positives = existing["false_positives"] if existing else 0
        if preview_url is None:
            preview_url = fallback_preview_url

        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO mrbeast_scams "
            "(image_hash, hash_bits, preview_url, confirmed_by, confirmed_at, times_deleted, false_positives) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7)",
            hex_hash, "".join(map(str, bits)), preview_url, str(confirmed_by),
            _utcnow(), times_deleted, false_positives,
        )
        return hex_hash

    async def _known_hashes(self):
        return await self.bot.cxn.fetch("SELECT image_hash, hash_bits FROM mrbeast_scams")

    # ── 1. context menu report ────────────────────────────────────────────

    async def _report_context_menu(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """Right-click a message → send its image assets to staff review."""
        await interaction.response.defer(ephemeral=True)

        images = [a for a in message.attachments if _is_image_attachment(a)]
        if not images:
            await interaction.followup.send(
                view=_cv("🚩 That message has no image attachments to review.", colour=_ACCENT_WARN),
                ephemeral=True,
            )
            return

        review_channel = self._review_channel()
        if review_channel is None:
            await interaction.followup.send(
                view=_cv(
                    "🚩 Scam review is not configured yet — an admin needs to set `SCAM_REVIEW_CHANNEL`.",
                    colour=_ACCENT_WARN,
                ),
                ephemeral=True,
            )
            return

        # Download assets once so they can be re-uploaded to the private server.
        blobs: list[tuple[str, bytes]] = []
        async with aiohttp.ClientSession() as session:
            for attachment in images[:4]:
                try:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            blobs.append((attachment.filename or "image.png", data))
                except Exception:
                    continue

        # Hash EVERY image now — confirmation then works offline and each
        # image in a multi-image report joins the filter (attachment URLs
        # are signed and expire, so hashing later is unreliable).
        report_hashes: list[str] = []
        for _, data in blobs:
            bits = _dhash_bits(data)
            if bits is not None:
                report_hashes.append(_hash_hex(bits))

        content = message.content or ""
        body = (
            f"**Reported by:** {interaction.user.mention} (`{interaction.user.id}`)\n"
            f"**Author:** {message.author.mention} (`{message.author.id}`)\n"
            f"**Server:** {message.guild.name} (`{message.guild.id}`)\n"
            f"**Channel:** #{message.channel.name} · [jump to message]({message.jump_url})"
            + (f"\n\n**Content:** {content[:500]}" if content else "")
        )

        files = [
            discord.File(io.BytesIO(data), filename=_safe_upload_name(name, i))
            for i, (name, data) in enumerate(blobs)
        ]
        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### 🚩 MrBeast Scam Report"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=body),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )
        if files:
            gallery = discord.ui.MediaGallery()
            for file in files:
                gallery.add_item(media=file)
            container.add_item(gallery)
            container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        row = discord.ui.ActionRow()
        row.add_item(_ReviewConfirmButton("open"))
        row.add_item(_ReviewRejectButton("open"))
        container.add_item(row)
        view = discord.ui.LayoutView()
        view.add_item(container)

        try:
            review_message = await review_channel.send(view=view, files=files)
        except discord.HTTPException as exc:
            logging.error("MrBeastScam", f"Could not deliver report to review channel: {exc}")
            await interaction.followup.send(
                view=_cv("🚩 Could not reach the review channel — try again later.", colour=_ACCENT_ERROR),
                ephemeral=True,
            )
            return

        report_id = f"{message.id}-{interaction.user.id}"
        try:
            await self.bot.cxn.execute(
                "INSERT OR REPLACE INTO mrbeast_scam_reports "
                "(report_id, message_id, guild_id, channel_id, reporter_id, author_id, content, attachments, image_hash, status, review_message_id, created_at) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)",
                report_id, message.id, message.guild.id, message.channel.id,
                interaction.user.id, message.author.id, content,
                [a.url for a in images], report_hashes,
                STATE_PENDING, review_message.id, _utcnow(),
            )
        except Exception as exc:
            logging.error("MrBeastScam", f"Could not persist scam report: {exc}")

        await interaction.followup.send(
            view=_cv("🚩 Thanks! The image was sent to the scam review team.", colour=_ACCENT_OK),
            ephemeral=True,
        )

    # ── 2. review resolution ──────────────────────────────────────────────

    async def _handle_review(self, interaction: discord.Interaction, decision: str) -> None:
        if not self._is_staff_reviewer(interaction.user):
            await interaction.response.send_message(
                view=_cv("🔒 Only Niko staff can review scam reports.", colour=_ACCENT_ERROR),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        message = interaction.message
        if message is None:
            await interaction.followup.send(view=_cv("Review message unavailable.", colour=_ACCENT_ERROR))
            return

        # Find the matching pending report by review message id.
        row = await self.bot.cxn.fetchrow(
            "SELECT report_id FROM mrbeast_scam_reports "
            "WHERE review_message_id = $1 AND status = $2",
            message.id, STATE_PENDING,
        )
        if row is None:
            await interaction.message.edit(
                view=_cv("🚩 Scam Review — already resolved", colour=_ACCENT_MUTED)
            )
            return

        if decision == "confirm":
            await self._confirm_report(interaction, row["report_id"], message)
        else:
            await self._reject_report(interaction, row["report_id"], message)

    async def _confirm_report(
        self,
        interaction: discord.Interaction,
        report_id: str,
        review_message: discord.Message,
    ) -> None:
        report = await self.bot.cxn.fetchrow(
            "SELECT image_hash, attachments FROM mrbeast_scam_reports WHERE report_id = $1",
            report_id,
        )

        # Stored hashes may be a JSON list (one per reported image) or a legacy
        # single value; normalise to a list of 64-char bit strings.
        stored = report.get("image_hash") if report else None
        if isinstance(stored, str):
            try:
                parsed = json.loads(stored)
            except Exception:
                parsed = [stored]
            if not isinstance(parsed, list):
                parsed = [stored]
            stored = parsed
        if not isinstance(stored, list):
            stored = []

        hash_bits_list: list[list[int]] = []
        for item in stored:
            bits_item = _bits_from_str(item) or _hex_to_bits(item)
            if bits_item is not None:
                hash_bits_list.append(bits_item)

        # A review-channel attachment URL is the only durable preview: the
        # reporter's original CDN links expire (webp first). Capture it from
        # the review message at confirm time; the reporter link stays as a
        # fallback for hashes stored before this existed.
        review_preview_url = None
        for attachment in review_message.attachments:
            if _is_image_attachment(attachment):
                review_preview_url = attachment.url
                break

        preview_url = None
        attachment_urls = report.get("attachments") if report else None
        if isinstance(attachment_urls, str):
            try:
                attachment_urls = json.loads(attachment_urls)
            except Exception:
                attachment_urls = []
        if isinstance(attachment_urls, list) and attachment_urls:
            preview_url = attachment_urls[0]

        # Fallback for old reports saved before hash-at-report-time.
        if not hash_bits_list and preview_url:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(preview_url) as resp:
                        if resp.status == 200:
                            bits_fallback = _dhash_bits(await resp.read())
                            if bits_fallback is not None:
                                hash_bits_list.append(bits_fallback)
                except Exception:
                    pass

        if not hash_bits_list:
            await interaction.followup.send(
                view=_cv("⚠️ Could not recover the reported image — reject this report and re-report it.", colour=_ACCENT_WARN),
                ephemeral=True,
            )
            return

        # Store EVERY reported image so multi-image reports join the filter
        # in full, not just the first attachment.
        stored_hashes: list[str] = []
        for bits in hash_bits_list:
            hex_hash = await self._store_bits(
                bits,
                preview_url=review_preview_url,
                fallback_preview_url=preview_url,
                confirmed_by=interaction.user.id,
            )
            stored_hashes.append(hex_hash)

        await self.bot.cxn.execute(
            "UPDATE mrbeast_scam_reports SET status = $1, resolved_by = $2, resolved_at = $3 WHERE report_id = $4",
            STATE_CONFIRMED, str(interaction.user.id), _utcnow(), report_id,
        )

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### ✅ Scam Confirmed"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"{len(stored_hashes)} image hash(es) `{', '.join(h[:12] + '…' for h in stored_hashes)}` "
                    f"were added to the detection database by {interaction.user.mention}."
                )
            ),
            accent_colour=discord.Colour(_ACCENT_OK),
        ))
        await review_message.edit(view=view)

    async def _reject_report(
        self,
        interaction: discord.Interaction,
        report_id: str,
        review_message: discord.Message,
    ) -> None:
        await self.bot.cxn.execute(
            "UPDATE mrbeast_scam_reports SET status = $1, resolved_by = $2, resolved_at = $3 WHERE report_id = $4",
            STATE_REJECTED, str(interaction.user.id), _utcnow(), report_id,
        )
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### 🚫 Scam Report Rejected"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"Rejected by {interaction.user.mention} — nothing was added to the filter."),
            accent_colour=discord.Colour(_ACCENT_MUTED),
        ))
        await review_message.edit(view=view)

    # ── 3. automatic detection ────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return
        # Skip ONLY the review queue channel — evidence images posted there by
        # the report flow must never be deleted. (Skipping the whole review
        # GUILD would disable detection everywhere staff test it, since the
        # review server is the staff/support server.)
        if message.channel.id == SCAM_REVIEW_CHANNEL:
            return
        pool = self.bot.cxn
        if pool is None:
            return

        # Per-guild opt-in: the filter only runs where it is enabled in the
        # automod settings (command panel or dashboard).
        utils = self.bot.get_cog("ModerationUtils")
        if utils is None:
            logging.debug("MrBeastScam", "ModerationUtils unavailable — filter skipped")
            return
        try:
            enabled = utils.get_guild_config(message.guild.id)["automod"].get("scam_image_filter", False)
        except Exception as exc:
            logging.debug("MrBeastScam", f"Could not read automod config: {exc}")
            return
        if not enabled:
            return
        images = [a for a in message.attachments if _is_image_attachment(a)]
        if not images:
            return

        try:
            rows = await self._known_hashes()
        except Exception as exc:
            logging.error("MrBeastScam", f"Could not load scam hashes: {exc}")
            return
        if not rows:
            logging.debug("MrBeastScam", "Detection skipped — no confirmed hashes in the database yet")
            return

        # Keep the bytes of every image we read: attachment URLs are signed
        # and stop resolving (webp first) as soon as the message is deleted,
        # so the deletion log must re-upload the actual image data instead of
        # linking the CDN.
        blobs: list[tuple[str, bytes]] = []
        for attachment in images:
            try:
                data = await attachment.read()
            except Exception as exc:
                logging.debug("MrBeastScam", f"Could not read attachment {attachment.filename}: {exc}")
                continue
            blobs.append((attachment.filename or "image.png", data))
            bits = _dhash_bits(data)
            if bits is None:
                continue
            matched, distance, matched_hash = _match_hash(bits, rows)
            if not matched:
                continue

            logging.info(
                "MrBeastScam",
                f"Scam image matched in #{message.channel} ({message.guild.name}) — "
                f"hash {matched_hash[:12]}… distance {distance}; deleting.",
            )
            await self._delete_and_log(message, matched_hash, distance, blobs)
            return

    async def _delete_and_log(
        self,
        message: discord.Message,
        matched_hash: str,
        distance: int,
        blobs: list[tuple[str, bytes]] | None = None,
    ) -> None:
        deleted = False
        try:
            await message.delete()
            deleted = True
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass

        try:
            await self.bot.cxn.execute(
                "UPDATE mrbeast_scams SET times_deleted = times_deleted + 1 WHERE image_hash = $1",
                matched_hash,
            )
        except Exception:
            pass

        guild = message.guild
        if guild is None:
            return

        body = (
            f"**Author:** {message.author.mention} (`{message.author.id}`)\n"
            f"**Channel:** {getattr(message.channel, 'mention', message.channel.id)}\n"
            f"**Reason:** MrBeast scam image detected "
            f"(hash `{matched_hash[:12]}…`, distance {distance})\n"
            f"**Action:** {'Message deleted' if deleted else 'Delete failed — missing permissions'}"
        )

        log_channel = await _get_automod_log_channel(self.bot, guild)
        if log_channel is None:
            return

        image_urls = [a.url for a in message.attachments if _is_image_attachment(a)][:4]

        def build_log_view(with_images: bool) -> tuple[discord.ui.LayoutView, list[discord.File]]:
            built: list[discord.File] = []
            if with_images:
                # Re-upload the actual image bytes: the deleted message's CDN
                # URLs are signed and stop resolving (webp first) once the
                # message is gone, so linking attachment.url leaves the log
                # with dead images.
                for i, (name, data) in enumerate((blobs or [])[:4]):
                    if not data:
                        continue
                    built.append(discord.File(io.BytesIO(data), filename=_safe_upload_name(name, i)))

            kids: list[discord.ui.Item] = [
                discord.ui.TextDisplay(content="### 🚩 MrBeast Scam Removed"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=body),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            ]
            if built:
                gallery = discord.ui.MediaGallery()
                for file in built:
                    gallery.add_item(media=file)
                kids.append(gallery)
                kids.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            elif image_urls:
                # No bytes available — fall back to CDN links (these expire).
                kids.append(discord.ui.MediaGallery(*[
                    MediaGalleryItem(media=url) for url in image_urls
                ]))
                kids.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            row = discord.ui.ActionRow()
            row.add_item(_FalsePositiveButton(matched_hash))
            kids.append(row)
            built_view = discord.ui.LayoutView()
            built_view.add_item(discord.ui.Container(*kids, accent_colour=discord.Colour(_ACCENT_WARN)))
            return built_view, built

        try:
            view, files = build_log_view(with_images=True)
            await log_channel.send(
                view=view,
                files=files or None,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except discord.HTTPException as exc:
            # Oversized or otherwise unuploadable images must not cost us the
            # log entry itself — retry once without them. (The File streams
            # were consumed by the failed multipart upload, so rebuild.)
            logging.info(
                "MrBeastScam",
                f"Image upload failed for scam deletion log in {guild}: {exc} — retrying without images",
            )
            try:
                view, _ = build_log_view(with_images=False)
                await log_channel.send(view=view, allowed_mentions=discord.AllowedMentions.none())
            except discord.HTTPException as exc2:
                logging.error("MrBeastScam", f"Could not log scam deletion in {guild}: {exc2}")

    # ── 4. false positive reporting ───────────────────────────────────────

    async def _handle_false_positive(self, interaction: discord.Interaction, image_hash: str) -> None:
        if not interaction.guild:
            return
        await interaction.response.defer(ephemeral=True)

        review_channel = self._review_channel()
        if review_channel is None:
            await interaction.followup.send(
                view=_cv("🚩 Scam review is not configured — cannot submit this false positive.", colour=_ACCENT_WARN),
                ephemeral=True,
            )
            return

        # Pull the stored preview so staff can see what was flagged.
        scam = await self.bot.cxn.fetchrow(
            "SELECT preview_url, times_deleted, false_positives FROM mrbeast_scams WHERE image_hash = $1",
            image_hash,
        )
        preview_url = scam.get("preview_url") if scam else None

        # Preview links can rot (reporter CDN URLs are signed and expire, webp
        # first), so re-upload the actual bytes and only fall back to links.
        preview_bytes: bytes | None = None
        candidate_urls: list[str] = []
        if preview_url:
            candidate_urls.append(preview_url)
        # Best effort: legacy reports stored a single hash and can be matched;
        # newer rows keep a JSON list, which plain equality never matches.
        try:
            pending = await self.bot.cxn.fetch(
                "SELECT attachments FROM mrbeast_scam_reports "
                "WHERE image_hash = $1 AND status = $2 LIMIT 3",
                image_hash, STATE_PENDING,
            )
        except Exception:
            pending = []
        for pending_row in pending or []:
            urls = pending_row.get("attachments") if pending_row else None
            if isinstance(urls, str):
                try:
                    urls = json.loads(urls)
                except Exception:
                    urls = []
            if isinstance(urls, list):
                for url in urls:
                    if isinstance(url, str) and url not in candidate_urls:
                        candidate_urls.append(url)
        async with aiohttp.ClientSession() as session:
            for url in candidate_urls[:4]:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            preview_bytes = await resp.read()
                            break
                except Exception:
                    continue

        body = (
            f"**Flagged as false positive in:** {interaction.guild.name} (`{interaction.guild.id}`)\n"
            f"**By:** {interaction.user.mention} (`{interaction.user.id}`)\n"
            f"**Hash:** `{image_hash}`\n"
            f"**Deletions so far:** {scam['times_deleted'] if scam else 0}\n"
        )
        if preview_url:
            body += f"\n[stored preview]({preview_url})"

        row = discord.ui.ActionRow()
        row.add_item(_RemoveScamButton(image_hash))

        def build_fp_view(with_image: bool) -> tuple[discord.ui.LayoutView, list[discord.File]]:
            files: list[discord.File] = []
            kids: list[discord.ui.Item] = [
                discord.ui.TextDisplay(content="### 🧪 False Positive Report"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=body),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            ]
            if with_image:
                if preview_bytes:
                    file = discord.File(
                        io.BytesIO(preview_bytes),
                        filename=_safe_upload_name("false_positive_preview.png", 0),
                    )
                    gallery = discord.ui.MediaGallery()
                    gallery.add_item(media=file)
                    kids.append(gallery)
                    kids.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
                    files.append(file)
                elif preview_url:
                    # Bytes unreachable — last resort is the (possibly dead) URL.
                    kids.append(discord.ui.MediaGallery(MediaGalleryItem(media=preview_url)))
                    kids.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            kids.append(row)
            built_view = discord.ui.LayoutView()
            built_view.add_item(discord.ui.Container(*kids, accent_colour=discord.Colour(_ACCENT_WARN)))
            return built_view, files

        async def deliver_fp(view_to_send: discord.ui.LayoutView,
                             files_to_send: list[discord.File]) -> tuple[bool, Exception | None]:
            try:
                await review_channel.send(view=view_to_send, files=files_to_send or None)
                return True, None
            except discord.HTTPException as exc:
                return False, exc

        ok, first_exc = await deliver_fp(*build_fp_view(with_image=True))
        if not ok:
            logging.info(
                "MrBeastScam",
                f"Image upload failed for false positive report: {first_exc} — retrying without image",
            )
            ok, retry_exc = await deliver_fp(*build_fp_view(with_image=False))
        if not ok:
            logging.error("MrBeastScam", f"Could not forward false positive: {retry_exc}")
            await interaction.followup.send(
                view=_cv("🚩 Could not reach the review channel — try again later.", colour=_ACCENT_ERROR),
                ephemeral=True,
            )
            return

        try:
            await self.bot.cxn.execute(
                "UPDATE mrbeast_scams SET false_positives = false_positives + 1 WHERE image_hash = $1",
                image_hash,
            )
        except Exception:
            pass

        await interaction.followup.send(
            view=_cv("🧪 Thanks! The false positive was sent to the scam review team.", colour=_ACCENT_OK),
            ephemeral=True,
        )

    async def _remove_scam_hash(self, interaction: discord.Interaction, image_hash: str) -> None:
        if not self._is_staff_reviewer(interaction.user):
            await interaction.response.send_message(
                view=_cv("🔒 Only Niko staff can remove hashes.", colour=_ACCENT_ERROR),
                ephemeral=True,
            )
            return
        await interaction.response.defer()
        try:
            await self.bot.cxn.execute("DELETE FROM mrbeast_scams WHERE image_hash = $1", image_hash)
        except Exception as exc:
            logging.error("MrBeastScam", f"Could not remove hash {image_hash}: {exc}")
            await interaction.followup.send(view=_cv("⚠️ Could not remove that hash.", colour=_ACCENT_ERROR))
            return
        if interaction.message is not None:
            try:
                await interaction.message.edit(
                    view=_cv(f"🧹 Hash `{image_hash[:12]}…` removed from the filter", colour=_ACCENT_MUTED)
                )
            except discord.HTTPException:
                pass


# ── Persistent buttons (DynamicItem) ─────────────────────────────────────────

class _ReviewConfirmButton(discord.ui.DynamicItem[discord.ui.Button], template=r"mrbeast:confirm:[a-z0-9]+"):
    def __init__(self, state: str) -> None:
        super().__init__(discord.ui.Button(
            label="Confirm Scam",
            style=discord.ButtonStyle.danger,
            custom_id=f"mrbeast:confirm:{state}",
        ))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls("open")

    async def callback(self, interaction: discord.Interaction) -> None:
        cog = interaction.client.get_cog("MrBeastScam")
        if cog is None:
            await interaction.response.send_message("Scam filter is unavailable.", ephemeral=True)
            return
        await cog._handle_review(interaction, "confirm")  # type: ignore[attr-defined]


class _ReviewRejectButton(discord.ui.DynamicItem[discord.ui.Button], template=r"mrbeast:reject:[a-z0-9]+"):
    def __init__(self, state: str) -> None:
        super().__init__(discord.ui.Button(
            label="Reject",
            style=discord.ButtonStyle.secondary,
            custom_id=f"mrbeast:reject:{state}",
        ))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls("open")

    async def callback(self, interaction: discord.Interaction) -> None:
        cog = interaction.client.get_cog("MrBeastScam")
        if cog is None:
            await interaction.response.send_message("Scam filter is unavailable.", ephemeral=True)
            return
        await cog._handle_review(interaction, "reject")  # type: ignore[attr-defined]


class _FalsePositiveButton(discord.ui.DynamicItem[discord.ui.Button], template=r"mrbeast:fp:([a-f0-9]+)"):
    def __init__(self, image_hash: str) -> None:
        super().__init__(discord.ui.Button(
            label="Report False Positive",
            style=discord.ButtonStyle.secondary,
            custom_id=f"mrbeast:fp:{image_hash}",
        ))
        self.image_hash = image_hash

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match.group(1))

    async def callback(self, interaction: discord.Interaction) -> None:
        cog = interaction.client.get_cog("MrBeastScam")
        if cog is None:
            await interaction.response.send_message("Scam filter is unavailable.", ephemeral=True)
            return
        await cog._handle_false_positive(interaction, self.image_hash)  # type: ignore[attr-defined]


class _RemoveScamButton(discord.ui.DynamicItem[discord.ui.Button], template=r"mrbeast:remove:([a-f0-9]+)"):
    def __init__(self, image_hash: str) -> None:
        super().__init__(discord.ui.Button(
            label="Remove From Filter",
            style=discord.ButtonStyle.danger,
            custom_id=f"mrbeast:remove:{image_hash}",
        ))
        self.image_hash = image_hash

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match.group(1))

    async def callback(self, interaction: discord.Interaction) -> None:
        cog = interaction.client.get_cog("MrBeastScam")
        if cog is None:
            await interaction.response.send_message("Scam filter is unavailable.", ephemeral=True)
            return
        await cog._remove_scam_hash(interaction, self.image_hash)  # type: ignore[attr-defined]


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MrBeastScam(bot))
