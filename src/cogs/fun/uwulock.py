import discord
from discord.ext import commands
import json
import re
import random
from typing import Dict
from utils import logging
from utils.i18n import make_msg


_MAX_RECENT_MESSAGES = 2000

# -----------------------------
# MESSAGE DICTIONARY
# -----------------------------
MESSAGES = {
    "normal": {
        "en": {
            "uwu_locked": "Uwulocked {mention}.",
            "uwu_unlocked": "Un‑uwulocked {mention}.",
            "fetch_fail": "Couldn't process uwu message.",
            "no_permission": "You need administrator permissions.",
        },
        "de": {
            "uwu_locked": "{mention} wurde uwugelockt.",
            "uwu_unlocked": "{mention} wurde ent‑uwugelockt.",
            "fetch_fail": "Konnte die uwu‑Nachricht nicht verarbeiten.",
            "no_permission": "Du benötigst Administratorrechte.",
        },
        "es": {
            "uwu_locked": "{mention} ha sido uwu-bloqueado/a.",
            "uwu_unlocked": "{mention} ha sido des-uwu-bloqueado/a.",
            "fetch_fail": "No pude procesar el mensaje uwu.",
            "no_permission": "Necesitas permisos de administrador.",
        },
    },

    "cafe": {
        "en": {
            "uwu_locked": "okay bestie… {mention} is now uwu‑locked ☕💖",
            "uwu_unlocked": "un‑uwu’d {mention} — they’re free again ☕🌿",
            "fetch_fail": "aww i couldn’t process that uwu message rn 😭☕",
            "no_permission": "you need admin perms for this sweetie ☕💛",
        },
        "de": {
            "uwu_locked": "okay liebchen… {mention} ist jetzt uwu‑gelockt ☕💖",
            "uwu_unlocked": "{mention} wurde ent‑uwu’t — wieder frei ☕🌿",
            "fetch_fail": "aww ich konnte die uwu‑nachricht gerade nicht verarbeiten 😭☕",
            "no_permission": "du brauchst admin‑rechte dafür ☕💛",
        },
        "es": {
            "uwu_locked": "okey amix… {mention} ya está uwu-bloqueado/a ☕💖",
            "uwu_unlocked": "des-uwu-eado a {mention} — vuelve a ser libre ☕🌿",
            "fetch_fail": "ay no pude procesar ese mensajito uwu 😭☕",
            "no_permission": "necesitas perms de admin para esto cariño ☕💛",
        },
    },

    # future personalities can be added here
}

msg = make_msg(MESSAGES)


# -----------------------------
# UWU LOCK COG
# -----------------------------
class UwULock(commands.Cog):
    """UwU‑lock system with cozy café personality + bilingual support."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data: Dict[int, Dict[int, Dict[int, dict]]] = {}
        # Guards against double processing when both the explicit hook from
        # events.on_message and the fallback listener see the same message.
        self._recent: list[int] = []

    async def cog_load(self):
        """Load active lock rules from the primary database."""
        rows = await self.bot.cxn.fetch(
            "SELECT guild_id, channel_id, user_id, webhook_url FROM uwulock_config"
        )
        for row in rows:
            self.data.setdefault(int(row["guild_id"]), {}).setdefault(
                int(row["channel_id"]), {}
            )[int(row["user_id"])] = {"webhook": row["webhook_url"]}

    # -----------------------------
    # uwulock command
    # -----------------------------
    @commands.command(
        name="uwulock",
        help="{ 'en': 'uwu‑lock a user so their messages become uwu‑ified ☕', 'de': 'uwu‑lockt einen nutzer' }"
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_webhooks=True, manage_messages=True)
    @commands.has_permissions(administrator=True)
    async def uwulock(self, ctx: commands.Context, *, user: discord.Member):
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        user_id = user.id
        existing = self.data.get(guild_id, {}).get(channel_id, {}).get(user_id)

        if existing:
            shared_webhook = any(
                member_id != user_id and entry["webhook"] == existing["webhook"]
                for member_id, entry in self.data[guild_id][channel_id].items()
            )
            if not shared_webhook:
                try:
                    webhook = discord.Webhook.from_url(existing["webhook"], client=self.bot)
                    await webhook.delete(reason=f"UwU lock removed by {ctx.author}")
                except discord.NotFound:
                    pass
                except discord.HTTPException as exc:
                    logging.warning("UwULock", f"Could not delete webhook for {channel_id}: {exc}")
                    return await ctx.send(msg(ctx, "fetch_fail"))

            await self.bot.cxn.execute(
                "DELETE FROM uwulock_config WHERE guild_id = $1 AND channel_id = $2 AND user_id = $3",
                guild_id, channel_id, user_id,
            )
            del self.data[guild_id][channel_id][user_id]
            if not self.data[guild_id][channel_id]:
                del self.data[guild_id][channel_id]
            if not self.data[guild_id]:
                del self.data[guild_id]
            return await ctx.send(msg(ctx, "uwu_unlocked", mention=user.mention))

        webhook_channel = (
            ctx.channel.parent
            if isinstance(ctx.channel, discord.Thread)
            else ctx.channel
        )
        if webhook_channel is None or not hasattr(webhook_channel, "create_webhook"):
            return await ctx.send(msg(ctx, "fetch_fail"))

        channel_rules = self.data.get(guild_id, {}).get(channel_id, {})
        webhook_url = next(
            (entry["webhook"] for entry in channel_rules.values()), None
        )
        stale_webhook_url = None
        webhook = None
        if webhook_url:
            try:
                webhook = discord.Webhook.from_url(webhook_url, client=self.bot)
                await webhook.fetch()
            except discord.NotFound:
                stale_webhook_url = webhook_url
                webhook = None
            except discord.HTTPException as exc:
                logging.warning("UwULock", f"Could not verify webhook in {channel_id}: {exc}")
                return await ctx.send(msg(ctx, "fetch_fail"))

        if webhook is None:
            try:
                webhook = await webhook_channel.create_webhook(
                    name="UwU Lock",
                    reason=f"UwU lock enabled by {ctx.author}",
                )
            except discord.HTTPException as exc:
                logging.warning("UwULock", f"Could not create webhook in {channel_id}: {exc}")
                return await ctx.send(msg(ctx, "fetch_fail"))

        if stale_webhook_url:
            await self.bot.cxn.execute(
                "UPDATE uwulock_config SET webhook_url = $1 "
                "WHERE guild_id = $2 AND channel_id = $3 AND webhook_url = $4",
                webhook.url, guild_id, channel_id, stale_webhook_url,
            )
            for entry in channel_rules.values():
                if entry["webhook"] == stale_webhook_url:
                    entry["webhook"] = webhook.url

        try:
            await self.bot.cxn.execute(
                "INSERT INTO uwulock_config (guild_id, channel_id, user_id, webhook_url) "
                "VALUES ($1, $2, $3, $4)",
                guild_id, channel_id, user_id, webhook.url,
            )
        except Exception:
            try:
                await webhook.delete(reason="UwU lock setup could not be saved")
            except discord.HTTPException:
                pass
            raise

        self.data.setdefault(guild_id, {}).setdefault(channel_id, {})[user_id] = {
            "webhook": webhook.url,
        }
        return await ctx.send(msg(ctx, "uwu_locked", mention=user.mention))

    # -----------------------------
    # Message transformation
    # -----------------------------
    async def process_message(self, message: discord.Message) -> bool:
        """Transform a locked message; return whether it was handled.

        Called explicitly from ``events.on_message`` so locked messages are
        handled before AI triggers, and also from the listener below as a
        fallback.  The ``_recent`` guard keeps the two paths from double
        processing the same message.
        """
        if message.author.bot or not message.guild:
            return False

        entry = self.data.get(message.guild.id, {}).get(message.channel.id, {}).get(message.author.id)
        if not entry:
            return False

        if message.id in self._recent:
            return True
        self._recent.append(message.id)
        if len(self._recent) > _MAX_RECENT_MESSAGES:
            del self._recent[: len(self._recent) - _MAX_RECENT_MESSAGES]

        logging.info(
            "UwULock",
            f"Detected locked message {message.id} from {message.author.id} in {message.channel.id}",
        )

        bot_member = message.guild.me
        if bot_member is None:
            logging.warning("UwULock", "Bot member is unavailable; cannot check permissions.")
            return True
        permissions = message.channel.permissions_for(bot_member)
        if not permissions.manage_messages:
            logging.warning(
                "UwULock",
                f"Missing Manage Messages in channel {message.channel.id}; skipping transform.",
            )
            return True

        files = []
        repost = None
        try:
            for attachment in message.attachments[:10]:
                files.append(await attachment.to_file())

            text = self.uwuify(message.content)
            if message.stickers:
                sticker_names = ", ".join(sticker.name for sticker in message.stickers)
                text = f"{text}\n[Sticker: {sticker_names}]" if text else f"[Sticker: {sticker_names}]"
            if len(text) > 2000:
                text = text[:1999] + "…"
            if not text and not files and not message.embeds:
                text = "‎"

            webhook = discord.Webhook.from_url(entry["webhook"], client=self.bot)
            send_options = {}
            if isinstance(message.channel, discord.Thread):
                send_options["thread"] = message.channel
            send_kwargs = {
                "content": text or None,
                "username": message.author.display_name[:80],
                "avatar_url": message.author.display_avatar.url,
                "allowed_mentions": discord.AllowedMentions.none(),
                "wait": True,
                **send_options,
            }
            try:
                repost = await webhook.send(
                    files=files or None,
                    embeds=message.embeds or None,
                    **send_kwargs,
                )
            except Exception as exc:
                # Attachments/embeds can be rejected by Discord (size limits,
                # unsupported embed types). Fall back to the transformed text
                # so the message is still visibly uwu-ified.
                logging.warning(
                    "UwULock",
                    f"Full repost failed for message {message.id} ({exc}); retrying text only",
                )
                repost = await webhook.send(**send_kwargs)

            try:
                await self.bot.cxn.execute(
                    "INSERT INTO uwulock_messages "
                    "(message_id, guild_id, channel_id, original_message_id, author_id, "
                    "author_name, author_avatar_url, original_created_at) "
                    "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
                    repost.id,
                    message.guild.id,
                    message.channel.id,
                    message.id,
                    message.author.id,
                    message.author.display_name,
                    message.author.display_avatar.url,
                    message.created_at.timestamp(),
                )
            except Exception as exc:
                # Starboard attribution is a bonus; never let a DB hiccup hide
                # the reposted message from the channel.
                logging.warning(
                    "UwULock",
                    f"Could not store attribution for message {message.id}: {exc}",
                )
        except Exception as exc:
            if repost is not None:
                try:
                    await repost.delete()
                except discord.HTTPException:
                    pass
            logging.warning("UwULock", f"Could not repost message {message.id}: {exc}")
            return True
        finally:
            for file in files:
                file.close()

        try:
            await message.delete()
            logging.info("UwULock", f"Reposted and removed original message {message.id}")
        except discord.HTTPException as exc:
            # Keep the repost visible even if the original could not be deleted;
            # a visible duplicate is better than silently doing nothing.
            logging.warning(
                "UwULock",
                f"Could not delete original message {message.id}: {exc}",
            )

        return True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Fallback listener alongside the explicit hook in events.on_message."""
        await self.process_message(message)

    # -----------------------------
    # uwuify helper
    # -----------------------------
    def uwuify(self, text: str) -> str:
        try:
            with open("blocked_words.json", "r") as f:
                filters = json.load(f)
        except Exception:
            filters = {"slurs": [], "threats": []}

        slur_replacements = ["sweetie", "snugglebun", "fluffball", "cutie‑pie", "honeybee"]
        threat_replacements = [
            "I need a hug…",
            "I should calm down…",
            "I’m feeling spicy but harmless…",
            "deep breaths…"
        ]

        for bad in filters.get("slurs", []):
            pattern = re.compile(rf"\b{re.escape(bad)}\b", re.IGNORECASE)
            text = pattern.sub(random.choice(slur_replacements), text)

        for bad in filters.get("threats", []):
            pattern = re.compile(rf"\b{re.escape(bad)}\b", re.IGNORECASE)
            text = pattern.sub(random.choice(threat_replacements), text)

        text = text.replace("r", "w").replace("l", "w")
        text = text.replace("R", "W").replace("L", "W")

        interjections = [
            "owo", "uwu", "x3", ">w<", "^w^", "rawr~",
            "nya~", "teehee~", "(≧◡≦)", "(⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
            "(｡♥‿♥｡)", "(ᵘʷᵘ)", "(๑˃ᴗ˂)ﻭ"
        ]

        prefixes = ["uhh", "umm", "ahh", "oh~", "hehe", "teehee", "h‑hewwo"]

        emojis = ["✨", "💖", "🥺", "👉👈", "🌸", "💞", "😳", "😼", "💗", "🌟"]

        words = text.split()
        uwu_words = []

        if random.random() < 0.35:
            uwu_words.append(random.choice(interjections))

        for w in words:
            base = w.lower()

            if random.random() < 0.20:
                uwu_words.append(random.choice(prefixes))

            if random.random() < 0.40:
                w = f"{w[0]}-{w}"

            if base in ["i", "to", "my", "we", "you"] and random.random() < 0.65:
                w = f"{w[0]}-{w}"

            if base == "to" and random.random() < 0.45:
                w = f"{w[0]}-{w[0]}-{w}"

            w = w.replace("no", "nyo")
            w = w.replace("has", "haz")
            w = w.replace("have", "haz")
            w = w.replace("you", "uu")
            w = w.replace("love", "wuv")

            uwu_words.append(w)

            if random.random() < 0.25:
                uwu_words.append(random.choice(interjections))

            if random.random() < 0.20:
                uwu_words.append(random.choice(emojis))

        return " ".join(uwu_words)

async def setup(bot: commands.Bot):
    await bot.add_cog(UwULock(bot))
