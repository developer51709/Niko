"""
Premium server subscriptions.

  /premium status    → current plan, expiry, and what premium unlocks
  /premium upgrade   → white-label crypto checkout link for this server
  /premium gift      → gift 1, 3, 6, or 12 months to a server the user is in

A background loop expires lapsed terms and DMs the server owner a few days
before the term ends, so the server can renew before moderation pauses. The
public billing page and the OxaPay webhook live in ``webapp/premium_routes.py``;
both call the notification helpers at the bottom of this module.
"""

import os
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config.emojis import get_emoji
from utils import logging
from utils.i18n import make_flat_msg
from utils.locales import load_locales
from utils.premium import (
    KIND_GIFT,
    PREMIUM_REMINDER_DAYS,
    expire_lapsed,
    get_subscription,
    is_premium,
    mark_reminder_sent,
    parse_ts,
    price_label,
    subscription_is_active,
    subscriptions_due_for_reminder,
)

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

ACCENT = 0xC8A882

MESSAGES = load_locales(__package__, "cog")
msg = make_flat_msg(MESSAGES)


def _duration(ctx, count: int) -> str:
    """``1 month`` / ``3 months`` in the reader's language."""
    return msg(ctx, "months_one" if count == 1 else "months_many", count=count)


def _days(ctx, count: int) -> str:
    """``1 day`` / ``3 days`` in the reader's language."""
    return msg(ctx, "days_one" if count == 1 else "days_many", count=count)


def site_base() -> str:
    """Public origin used by links sent from Discord."""
    base = os.getenv("PUBLIC_URL")
    if not base and os.getenv("REPLIT_DEV_DOMAIN"):
        base = f"https://{os.getenv('REPLIT_DEV_DOMAIN')}"
    return (base or "https://niko.sryze.cc").rstrip("/")


def billing_url(guild_id: int | str, *, gift: bool = False) -> str:
    """Public checkout for one guild; gifts have their own page."""
    if gift:
        return f"{site_base()}/billing/gift?guild={guild_id}"
    return f"{site_base()}/billing?guild={guild_id}"


def _expiry_label(value, ctx=None) -> str:
    """A Discord date, so every reader sees the expiry in their own locale."""
    moment = parse_ts(value)
    if moment is None:
        return msg(ctx, "unknown_date")
    return f"<t:{int(moment.timestamp())}:D>"


def _status_line(row, ctx=None) -> str:
    if subscription_is_active(row):
        return msg(ctx, "status_active", date=_expiry_label(row.get("expires_at"), ctx))
    if row and row.get("status") == "cancelled":
        return msg(ctx, "status_cancelled")
    if row:
        return msg(ctx, "status_expired", date=_expiry_label(row.get("expires_at"), ctx))
    return msg(ctx, "status_none")


def _premium_view() -> discord.ui.LayoutView:
    return discord.ui.LayoutView(timeout=None)


async def _dm(user: discord.abc.User | None, view: discord.ui.LayoutView) -> bool:
    if user is None:
        return False
    try:
        await user.send(view=view)
        return True
    except discord.Forbidden:
        logging.warning("Premium", f"Could not DM {getattr(user, 'id', 'unknown')} — DMs closed.")
    except Exception as error:
        logging.warning("Premium", f"Could not DM {getattr(user, 'id', 'unknown')}: {error}")
    return False


async def notify_gift(
    bot,
    *,
    guild_id: int,
    gifted_by_id: int | None,
    gifted_by_name: str | None,
    months: int,
    expires_at,
) -> bool:
    """Tell the server owner that somebody gifted their community premium."""
    guild = bot.get_guild(int(guild_id)) if bot is not None else None
    owner = None
    owner_id = getattr(guild, "owner_id", None)
    if guild is not None and getattr(guild, "owner", None) is not None:
        owner = guild.owner
    elif owner_id:
        try:
            owner = bot.get_user(int(owner_id)) or await bot.fetch_user(int(owner_id))
        except Exception:
            owner = None

    gifter = gifted_by_name or (f"<@{gifted_by_id}>" if gifted_by_id else msg(guild, "community_member"))
    server_name = guild.name if guild else f"Server {guild_id}"
    view = _premium_view()
    view.add_item(
        discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {get_emoji('heart')} {msg(guild, 'gift_dm_title')}\n"
                    + msg(
                        guild,
                        "gift_dm_body",
                        server=server_name,
                        duration=_duration(guild, months),
                        gifter=gifter,
                        until=_expiry_label(expires_at, guild),
                    )
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label=msg(guild, "open_dashboard"),
                    style=discord.ButtonStyle.link,
                    url=f"{site_base()}/dashboard/{guild_id}/moderation",
                )
            ),
        )
    )
    delivered = await _dm(owner, view)
    if not delivered and owner is not None:
        logging.info("Premium", f"Gift notice for guild {guild_id} could not be delivered.")
    return delivered


async def notify_purchase(
    bot,
    *,
    guild_id: int,
    payer_id: int,
    kind: str,
    months: int,
    expires_at,
    amount_cents: int,
) -> bool:
    """Send the payer a receipt and, for a gift, notify the owner."""
    if bot is None:
        return False
    guild = bot.get_guild(int(guild_id))
    guild_name = guild.name if guild else f"Server {guild_id}"
    try:
        payer = bot.get_user(int(payer_id)) or await bot.fetch_user(int(payer_id))
    except Exception:
        payer = None

    gifted = kind == KIND_GIFT
    view = _premium_view()
    view.add_item(
        discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {get_emoji('tick')} {msg(guild, 'payment_title')}\n"
                    + msg(
                        guild,
                        "payment_body",
                        price=price_label(amount_cents),
                        duration=_duration(guild, months),
                        server=guild_name,
                        until=_expiry_label(expires_at, guild),
                    )
                    + "\n\n"
                    + msg(guild, "payment_gift_note" if gifted else "payment_thanks")
                )
            )
        )
    )
    delivered = await _dm(payer, view)
    if gifted:
        await notify_gift(
            bot,
            guild_id=guild_id,
            gifted_by_id=payer_id,
            gifted_by_name=getattr(payer, "display_name", None) or getattr(payer, "name", None),
            months=months,
            expires_at=expires_at,
        )
    return delivered


class PremiumCog(commands.Cog, name="Premium"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._lifecycle_loop.start()

    def cog_unload(self):
        self._lifecycle_loop.cancel()

    @tasks.loop(hours=6)
    async def _lifecycle_loop(self):
        """Expire lapsed terms and remind owners before they run out."""
        if not getattr(self.bot, "cxn", None):
            return
        try:
            expired = await expire_lapsed(self.bot.cxn)
            for row in expired:
                logging.info("Premium", f"Subscription for guild {row.get('guild_id')} expired.")
            for row in await subscriptions_due_for_reminder(self.bot.cxn):
                await self._send_renewal_reminder(row)
        except Exception as error:
            logging.warning("Premium", f"Subscription lifecycle check failed: {error}")

    @_lifecycle_loop.before_loop
    async def _before_lifecycle(self):
        await self.bot.wait_until_ready()

    async def _send_renewal_reminder(self, row: dict) -> None:
        guild_id = int(row["guild_id"])
        guild = self.bot.get_guild(guild_id)
        owner = None
        if guild is not None:
            owner = getattr(guild, "owner", None)
            if owner is None:
                try:
                    owner = self.bot.get_user(int(guild.owner_id)) or await self.bot.fetch_user(int(guild.owner_id))
                except Exception:
                    owner = None
        if owner is None and row.get("owner_id"):
            try:
                owner = self.bot.get_user(int(row["owner_id"])) or await self.bot.fetch_user(int(row["owner_id"]))
            except Exception:
                owner = None

        expires = parse_ts(row.get("expires_at"))
        days_left = max(0, (expires - datetime.utcnow()).days) if expires else PREMIUM_REMINDER_DAYS
        ctx = guild or owner
        view = _premium_view()
        view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('loading')} {msg(ctx, 'reminder_title')}\n"
                        + msg(
                            ctx,
                            "reminder_body",
                            server=guild.name if guild else f"Server {guild_id}",
                            until=_expiry_label(row.get("expires_at"), ctx),
                            duration=_days(ctx, max(1, days_left)),
                            price=price_label(int(row.get("price_cents") or 1500)),
                        )
                    )
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label=msg(ctx, "renew_button"),
                        style=discord.ButtonStyle.link,
                        url=billing_url(guild_id),
                    )
                ),
            )
        )
        if await _dm(owner, view):
            logging.success("Premium", f"Renewal reminder sent for guild {guild_id}.")
        # Mark it either way: a closed DM is not fixed by retrying every loop.
        try:
            await mark_reminder_sent(self.bot.cxn, guild_id)
        except Exception as error:
            logging.warning("Premium", f"Could not mark reminder sent for {guild_id}: {error}")

    # ── Commands ──────────────────────────────────
    # A pure application-command group: `cogs.staff.commands.moderation`
    # already owns the `.staff premium` prefix group for user grants, so a
    # hybrid command here would collide with that prefix handler depending on
    # cog load order.

    premium = app_commands.Group(
        name="premium",
        description=CMDS.text("premium.description"),
    )

    @premium.command(name="status", description=CMDS.text("premium.status.description"))
    async def premium_status(self, interaction: discord.Interaction):
        if interaction.guild is None:
            return await interaction.response.send_message(
                f"{get_emoji('danger')} {msg(interaction, 'guild_only')}", ephemeral=True
            )
        await interaction.response.defer(ephemeral=True)
        row = None
        if getattr(self.bot, "cxn", None):
            try:
                row = await get_subscription(self.bot.cxn, interaction.guild.id)
            except Exception as error:
                logging.warning("Premium", f"Could not read subscription: {error}")
        view = _premium_view()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {get_emoji('heart')} {msg(interaction, 'status_title')}\n"
                    f"**{msg(interaction, 'status_server')}:** {interaction.guild.name}\n"
                    f"**{msg(interaction, 'status_status')}:** {_status_line(row, interaction)}\n"
                    f"**{msg(interaction, 'status_plan')}:** "
                    f"{msg(interaction, 'plan_price', price=price_label(int((row or {}).get('price_cents') or 1500)))}\n"
                    f"**{msg(interaction, 'status_ai_moderation')}:** "
                    f"{msg(interaction, 'status_enabled' if subscription_is_active(row) else 'status_paused')}"
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg(interaction, "status_blurb")),
            accent_colour=discord.Colour(ACCENT),
        )
        if not subscription_is_active(row):
            container.add_item(
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label=msg(interaction, "upgrade_button"),
                        style=discord.ButtonStyle.link,
                        url=billing_url(interaction.guild.id),
                    )
                )
            )
        view.add_item(container)
        await interaction.followup.send(view=view, ephemeral=True)

    @premium.command(name="upgrade", description=CMDS.text("premium.upgrade.description"))
    @app_commands.default_permissions(manage_guild=True)
    async def premium_upgrade(self, interaction: discord.Interaction):
        if interaction.guild is None:
            return await interaction.response.send_message(
                f"{get_emoji('danger')} {msg(interaction, 'guild_only')}", ephemeral=True
            )
        permissions = interaction.permissions
        if not (permissions.manage_guild or permissions.administrator):
            return await interaction.response.send_message(
                f"{get_emoji('danger')} {msg(interaction, 'manage_only')}",
                ephemeral=True,
            )
        await interaction.response.defer(ephemeral=True)
        view = _premium_view()
        view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('heart')} "
                        + msg(interaction, "upgrade_title", server=interaction.guild.name)
                        + "\n"
                        + msg(interaction, "upgrade_price", price=price_label())
                        + "\n\n"
                        + msg(interaction, "upgrade_blurb")
                        + "\n\n"
                        + msg(interaction, "upgrade_cards_note")
                    )
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label=msg(interaction, "open_checkout"),
                        style=discord.ButtonStyle.link,
                        url=billing_url(interaction.guild.id),
                    )
                ),
                accent_colour=discord.Colour(ACCENT),
            )
        )
        await interaction.followup.send(view=view, ephemeral=True)

    @premium.command(name="gift", description=CMDS.text("premium.gift.description"))
    @app_commands.describe(server_id=CMDS.arg("premium.gift", "server_id"))
    async def premium_gift(self, interaction: discord.Interaction, server_id: str | None = None):
        await interaction.response.defer(ephemeral=True)
        target = interaction.guild
        if server_id:
            if not server_id.strip().isdigit():
                return await interaction.followup.send(
                    f"{get_emoji('danger')} {msg(interaction, 'invalid_server_id')}", ephemeral=True
                )
            target = self.bot.get_guild(int(server_id.strip()))
        if target is None:
            return await interaction.followup.send(
                f"{get_emoji('danger')} {msg(interaction, 'choose_server')}",
                ephemeral=True,
            )
        member = target.get_member(interaction.user.id)
        if member is None:
            try:
                member = await target.fetch_member(interaction.user.id)
            except Exception:
                member = None
        if member is None:
            return await interaction.followup.send(
                f"{get_emoji('danger')} {msg(interaction, 'not_member', server=target.name)}",
                ephemeral=True,
            )

        already = False
        if getattr(self.bot, "cxn", None):
            try:
                already = await is_premium(self.bot.cxn, target.id)
            except Exception:
                already = False
        view = _premium_view()
        view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('heart')} {msg(interaction, 'gift_title')}\n"
                        f"**{target.name}**\n"
                        + msg(interaction, "plan_price", price=price_label())
                        + ("\n\n" + msg(interaction, "gift_active_note") if already else "")
                        + "\n\n"
                        + msg(interaction, "gift_blurb")
                    )
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label=msg(interaction, "continue_payment"),
                        style=discord.ButtonStyle.link,
                        url=billing_url(target.id, gift=True),
                    )
                ),
                accent_colour=discord.Colour(ACCENT),
            )
        )
        await interaction.followup.send(view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        """Expire lapsed terms as soon as the bot is up, not only after six hours."""
        if not getattr(self.bot, "cxn", None):
            return
        try:
            await expire_lapsed(self.bot.cxn)
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(PremiumCog(bot))
