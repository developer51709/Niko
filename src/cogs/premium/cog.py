"""
Premium server subscriptions.

  /premium status    → current plan, expiry, and what premium unlocks
  /premium upgrade   → white-label crypto checkout link for this server
  /premium gift      → gift a month of premium to a server the user is in

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

ACCENT = 0xC8A882


def site_base() -> str:
    """Public origin used by links sent from Discord."""
    base = os.getenv("PUBLIC_URL") or os.getenv("DONATION_SITE_URL")
    if not base and os.getenv("REPLIT_DEV_DOMAIN"):
        base = f"https://{os.getenv('REPLIT_DEV_DOMAIN')}"
    return (base or "https://niko.sryze.cc").rstrip("/")


def billing_url(guild_id: int | str, *, gift: bool = False) -> str:
    """Public billing page for one guild (gift mode prefills the intent)."""
    url = f"{site_base()}/billing?guild={guild_id}"
    return f"{url}&gift=1" if gift else url


def _expiry_label(value) -> str:
    moment = parse_ts(value)
    if moment is None:
        return "unknown"
    return moment.strftime("%d %b %Y")


def _status_line(row) -> str:
    if subscription_is_active(row):
        return f"Active · renews by **{_expiry_label(row.get('expires_at'))}**"
    if row and row.get("status") == "cancelled":
        return "Cancelled · premium perks are paused"
    if row:
        return f"Expired on **{_expiry_label(row.get('expires_at'))}**"
    return "No subscription"


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

    gifter = gifted_by_name or f"<@{gifted_by_id}>" if gifted_by_id else "A community member"
    view = _premium_view()
    view.add_item(
        discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {get_emoji('heart')} Your server was gifted premium\n"
                    f"**{guild.name if guild else f'Server {guild_id}'}** now has Niko Premium "
                    f"for **{months} month{'s' if months != 1 else ''}**.\n\n"
                    f"**Gifted by:** {gifter}\n"
                    f"**Active until:** **{_expiry_label(expires_at)}**\n\n"
                    f"Premium includes AI image moderation, powered by fal.ai. "
                    f"You can turn it on in the dashboard under Moderation."
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Open server dashboard",
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
                    f"### {get_emoji('tick')} Payment confirmed\n"
                    f"**{price_label(amount_cents)}** for **{months} month{'s' if months != 1 else ''}** "
                    f"of Niko Premium.\n"
                    f"**Server:** {guild_name}\n"
                    f"**Active until:** **{_expiry_label(expires_at)}**\n\n"
                    + (
                        "The server owner has been notified about your gift."
                        if gifted
                        else "Thanks for supporting Niko — this pays for the moderation API, "
                             "hosting, and the upcoming domain."
                    )
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
        view = _premium_view()
        view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('loading')} Premium expires soon\n"
                        f"**{guild.name if guild else f'Server {guild_id}'}**'s Niko Premium ends "
                        f"**{_expiry_label(row.get('expires_at'))}** "
                        f"(in {max(1, days_left)} day{'s' if days_left != 1 else ''}).\n\n"
                        f"Renewing keeps AI image moderation running without a gap. "
                        f"The monthly plan is **{price_label(int(row.get('price_cents') or 1500))}**."
                    )
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label="Renew premium",
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
    # A pure application-command group: `cogs.staff.owner` already owns the
    # `.premium` prefix group for user grants, so a hybrid command here would
    # replace that prefix handler depending on cog load order.

    premium = app_commands.Group(name="premium", description="Manage Niko Premium for a server")

    @premium.command(name="status", description="Show this server's premium subscription")
    async def premium_status(self, interaction: discord.Interaction):
        if interaction.guild is None:
            return await interaction.response.send_message(
                f"{get_emoji('danger')} Use this command inside a server.", ephemeral=True
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
                    f"### {get_emoji('heart')} Niko Premium\n"
                    f"**Server:** {interaction.guild.name}\n"
                    f"**Status:** {_status_line(row)}\n"
                    f"**Plan:** {price_label(int((row or {}).get('price_cents') or 1500))} / month\n"
                    f"**AI image moderation:** {'enabled with premium' if subscription_is_active(row) else 'paused'}"
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    "Premium is per server and renews monthly. It pays for the fal.ai "
                    "moderation credits, bot hosting, and the upcoming niko domain."
                )
            ),
            accent_colour=discord.Colour(ACCENT),
        )
        if not subscription_is_active(row):
            container.add_item(
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label="Upgrade this server",
                        style=discord.ButtonStyle.link,
                        url=billing_url(interaction.guild.id),
                    )
                )
            )
        view.add_item(container)
        await interaction.followup.send(view=view, ephemeral=True)

    @premium.command(name="upgrade", description="Get the checkout link for this server")
    @app_commands.default_permissions(manage_guild=True)
    async def premium_upgrade(self, interaction: discord.Interaction):
        if interaction.guild is None:
            return await interaction.response.send_message(
                f"{get_emoji('danger')} Use this command inside a server.", ephemeral=True
            )
        permissions = interaction.permissions
        if not (permissions.manage_guild or permissions.administrator):
            return await interaction.response.send_message(
                f"{get_emoji('danger')} Only members who can manage this server can upgrade it.",
                ephemeral=True,
            )
        await interaction.response.defer(ephemeral=True)
        view = _premium_view()
        view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('heart')} Upgrade {interaction.guild.name}\n"
                        f"**{price_label()} / month** — cancel by simply not renewing.\n\n"
                        f"Checkout opens our white-label payment page: choose a cryptocurrency, "
                        f"send it to the address shown, and premium activates the moment the "
                        f"transaction confirms.\n\n"
                        f"-# Card payments are coming soon."
                    )
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label="Open checkout",
                        style=discord.ButtonStyle.link,
                        url=billing_url(interaction.guild.id),
                    )
                ),
                accent_colour=discord.Colour(ACCENT),
            )
        )
        await interaction.followup.send(view=view, ephemeral=True)

    @premium.command(name="gift", description="Gift a month of premium to a server you are in")
    @app_commands.describe(server_id="Server ID to gift (defaults to this server)")
    async def premium_gift(self, interaction: discord.Interaction, server_id: str | None = None):
        await interaction.response.defer(ephemeral=True)
        target = interaction.guild
        if server_id:
            if not server_id.strip().isdigit():
                return await interaction.followup.send(
                    f"{get_emoji('danger')} That is not a valid server ID.", ephemeral=True
                )
            target = self.bot.get_guild(int(server_id.strip()))
        if target is None:
            return await interaction.followup.send(
                f"{get_emoji('danger')} Choose a server Niko is in to gift premium to.",
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
                f"{get_emoji('danger')} You have to be a member of **{target.name}** to gift it premium.",
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
                        f"### {get_emoji('heart')} Gift premium\n"
                        f"**{target.name}**\n"
                        f"**{price_label()} / month**"
                        + ("\n\n-# This adds another month on top of the current subscription." if already else "")
                        + "\n\nYour gift stays active even if you leave the server. "
                        "The owner is told who gifted it."
                    )
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label="Continue to payment",
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
