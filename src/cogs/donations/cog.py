"""
Donations cog — OxaPay crypto donation system.

Flow:
  /donate [amount]  →  link to the white-label page (ephemeral)
  /donationstatus [track_id]  →  provider status, reconciled with the database
  Every 45 s the background loop re-reads unpaid invoices from the database and
  asks OxaPay about them, so a restart or a missed webhook cannot lose a payment.
  On Paid (once per invoice): records the donor, DMs a receipt, grants the
  supporter role in the support server, and thanks the channel it started in.
  on_member_join: auto-grants supporter role to known donors joining the support server.
"""

import os
from urllib.parse import quote

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config.emojis import get_emoji
from config.ids import SUPPORT_GUILD
from cogs.staff.support_server import support_role
from utils import logging
from utils.i18n import make_flat_msg
from utils.locales import load_locales
from utils.donations import (
    DONATION_MAX_AMOUNT,
    DONATION_MIN_AMOUNT,
    DONATION_PRESET_AMOUNTS,
    add_donor,
    confirm_invoice,
    create_donation_token,
    get_invoice,
    get_pending_invoices,
    get_total_donated,
    is_supporter,
    update_invoice_status,
)
from .oxapay import OxaPayClient

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

# OxaPay key type: use your MERCHANT API key (Dashboard → Merchant → API Key).
# NOT the Sandbox key (testing only) and NOT the Payout API key (for sending crypto).
OXAPAY_KEY: str = os.getenv("OXAPAY_API_KEY", "")

MESSAGES = load_locales(__package__, "cog")
msg = make_flat_msg(MESSAGES)

#: OxaPay's status values, shown under their translated label.
_STATE_KEYS = {
    "Paid": "state_paid",
    "Waiting": "state_waiting",
    "Paying": "state_paying",
    "Confirming": "state_confirming",
    "Expired": "state_expired",
    "Failed": "state_failed",
}


def _site_base() -> str:
    """Public origin of the white-label payment page."""
    base = os.getenv("PUBLIC_URL")
    if not base and os.getenv("REPLIT_DEV_DOMAIN"):
        base = f"https://{os.getenv('REPLIT_DEV_DOMAIN')}"
    return (base or "https://niko.sryze.cc").rstrip("/")


def donation_checkout_url(user_id: int, amount: float) -> str:
    """Signed link to the white-label page, prefilled with the amount."""
    token = create_donation_token(user_id)
    return f"{_site_base()}/billing?token={quote(token, safe='')}&amount={amount:.2f}"

# ─────────────────── Cog ───────────────────

class DonationCog(commands.Cog, name="DonationCog"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._poll_loop.start()

    def cog_unload(self):
        self._poll_loop.cancel()

    # ── Background payment poller ──────────────────

    @tasks.loop(seconds=45)
    async def _poll_loop(self):
        """Reconcile unpaid invoices straight from the database.

        Reading the pending set from storage instead of memory means a restart
        between "address shown" and "network settled" no longer loses the
        donation, and the webhook and this loop cannot both credit a payment
        because both go through :meth:`_on_payment_confirmed`.
        """
        if not OXAPAY_KEY:
            return
        try:
            invoices = await get_pending_invoices(self.bot)
        except Exception as exc:
            logging.warning("Donations", f"Could not read pending invoices: {exc}")
            return
        if not invoices:
            return
        client = OxaPayClient(OXAPAY_KEY)
        for invoice in invoices:
            track_id = str(invoice["track_id"] or "")
            if not track_id:
                continue
            try:
                result = await client.check_white_label(track_id)
            except Exception as exc:
                logging.warning("Donations", f"Poll error for {track_id}: {exc}")
                continue
            status = str(result.get("status") or "")
            if status == "Paid":
                await self._on_payment_confirmed(track_id)
            elif status in ("Expired", "Failed"):
                await update_invoice_status(self.bot, track_id, status)

    @_poll_loop.before_loop
    async def _before_poll(self):
        await self.bot.wait_until_ready()

    # ── Payment confirmed handler ──────────────────

    async def _on_payment_confirmed(self, track_id: str, data: dict | None = None) -> bool:
        """Credit a confirmed donation exactly once and thank the donor.

        Returns True only for the call that flipped the invoice to paid, so a
        retried webhook, a duplicate callback, or the poller catching up on the
        same payment never credits the donor twice.
        """
        invoice, newly_confirmed = await confirm_invoice(self.bot, track_id, data)
        if invoice is None:
            logging.warning("Donations", f"Paid invoice {track_id} is not in the database.")
            return False
        if not newly_confirmed:
            return False

        user_id = int(invoice["user_id"])
        amount = float(invoice["amount"])
        currency = str(invoice.get("pay_currency") or invoice.get("currency") or "USD")
        channel_id = invoice.get("channel_id")
        channel = self.bot.get_channel(channel_id) if channel_id else None
        # The thank-you follows the language of the server the donation started
        # in; a DM has no guild of its own.
        ctx = getattr(channel, "guild", None)
        amount_label = f"${amount:.2f} USD"

        try:
            await add_donor(self.bot, user_id, amount, currency, track_id)
        except Exception as exc:
            logging.error("Donations", f"DB error recording donation: {exc}")

        await self._grant_supporter_role(user_id)

        # DM the donor
        try:
            user = await self.bot.fetch_user(user_id)
            dm_view = discord.ui.LayoutView()
            dm_view.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=(
                            f"### {get_emoji('heart')} {msg(ctx, 'dm_title')}\n"
                            + msg(
                                ctx,
                                "dm_body",
                                amount=amount_label,
                                currency=currency,
                                badge=get_emoji("badge_supporter_role"),
                                track=track_id,
                            )
                        )
                    )
                )
            )
            await user.send(view=dm_view)
        except Exception:
            pass

        # Public thank-you in the originating channel
        if channel:
            try:
                pub_view = discord.ui.LayoutView()
                pub_view.add_item(
                    discord.ui.Container(
                        discord.ui.TextDisplay(
                            content=(
                                f"### {get_emoji('heart')} {msg(ctx, 'public_title')}\n"
                                + msg(
                                    ctx,
                                    "public_body",
                                    user=user_id,
                                    amount=amount_label,
                                    currency=currency,
                                    badge=get_emoji("badge_supporter_role"),
                                )
                            )
                        )
                    )
                )
                await channel.send(view=pub_view)
            except Exception:
                pass

        logging.success(
            "Donations", f"Confirmed ${amount:.2f} donation from {user_id} ({track_id})"
        )
        return True

    # ── Role helpers ──────────────────────────────

    async def _grant_supporter_role(self, user_id: int):
        """Grant the database-configured supporter role in the support server."""
        support_guild = self.bot.get_guild(SUPPORT_GUILD)
        if not support_guild:
            return
        try:
            member = support_guild.get_member(user_id) or await support_guild.fetch_member(user_id)
            role = await support_role(self.bot, "supporter")
            if role and role not in member.roles:
                await member.add_roles(role, reason="Crypto donation confirmed via OxaPay")
                logging.success("Donations", f"Granted supporter role to {member} ({user_id})")
        except discord.NotFound:
            pass
        except Exception as exc:
            logging.warning("Donations", f"Could not grant supporter role to {user_id}: {exc}")

    # ── Commands ──────────────────────────────────

    @commands.hybrid_command(
        name="donate",
        description=CMDS.text("donate.description"),
        help=CMDS.help("donate"),
    )
    @app_commands.describe(amount=CMDS.arg("donate", "amount"))
    async def donate(self, ctx: commands.Context, amount: float = 5.0):
        if ctx.interaction:
            await ctx.defer(ephemeral=True)

        if amount < 1.0:
            return await ctx.send(
                f"{get_emoji('danger')} {msg(ctx, 'min_donation', min='$1.00 USD')}",
                ephemeral=bool(ctx.interaction),
            )
        if amount > 10_000.0:
            return await ctx.send(
                f"{get_emoji('danger')} {msg(ctx, 'max_donation', max='$10,000.00 USD')}",
                ephemeral=bool(ctx.interaction),
            )

        # Every checkout happens on the white-label page so crypto and (later)
        # card share one interface, the same one premium uses.
        intro_view = discord.ui.LayoutView()
        intro_view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('heart')} {msg(ctx, 'donate_title')}\n"
                        + msg(
                            ctx,
                            "donate_body",
                            amount=f"${amount:.2f} USD",
                            badge=get_emoji("badge_supporter_role"),
                        )
                    )
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label=msg(ctx, "open_checkout"),
                        style=discord.ButtonStyle.link,
                        url=donation_checkout_url(ctx.author.id, amount),
                        emoji=get_emoji("oxapay"),
                    )
                ),
                # One click for the usual amounts; /donate amount still takes
                # anything between the minimum and the maximum.
                discord.ui.ActionRow(*[
                    discord.ui.Button(
                        label=f"${preset}",
                        style=discord.ButtonStyle.link,
                        url=donation_checkout_url(ctx.author.id, preset),
                    )
                    for preset in DONATION_PRESET_AMOUNTS
                ]),
                discord.ui.TextDisplay(
                    content=(
                        msg(
                            ctx,
                            "limits_note",
                            min=f"${DONATION_MIN_AMOUNT:,.0f}",
                            max=f"${DONATION_MAX_AMOUNT:,.0f}",
                        )
                        + "\n"
                        + msg(ctx, "powered_by", oxapay=get_emoji("oxapay"))
                    )
                )
            )
        )

        if ctx.interaction:
            await ctx.interaction.followup.send(view=intro_view, ephemeral=True)
        else:
            await ctx.send(view=intro_view)

    @commands.hybrid_command(
        name="donationstatus",
        description=CMDS.text("donationstatus.description"),
        help=CMDS.help("donationstatus"),
    )
    @app_commands.describe(track_id=CMDS.arg("donationstatus", "track_id"))
    async def donationstatus(self, ctx: commands.Context, track_id: str):
        if ctx.interaction:
            await ctx.defer(ephemeral=True)

        invoice = await get_invoice(self.bot, track_id=track_id)
        if invoice is not None and str(invoice["user_id"]) != str(ctx.author.id):
            return await ctx.send(
                f"{get_emoji('danger')} {msg(ctx, 'invalid_track')}",
                ephemeral=bool(ctx.interaction),
            )

        status = str(invoice.get("status")) if invoice is not None else "Unknown"
        if OXAPAY_KEY:
            result = await OxaPayClient(OXAPAY_KEY).check_white_label(track_id)
            status = str(result.get("status") or status)
            # Keep the stored copy current so the website and the poller agree.
            if invoice is not None and status in ("Expired", "Failed"):
                await update_invoice_status(self.bot, track_id, status)
        elif invoice is None:
            return await ctx.send(
                f"{get_emoji('danger')} {msg(ctx, 'not_configured')}",
                ephemeral=bool(ctx.interaction),
            )

        icons = {
            "Paid":    get_emoji("tick"),
            "Waiting": get_emoji("loading"),
            "Paying":  get_emoji("loading"),
            "Confirming": get_emoji("loading"),
            "Expired": get_emoji("cross"),
            "Failed":  get_emoji("danger"),
        }
        icon = icons.get(status, "❓")
        status_label = msg(ctx, _STATE_KEYS[status]) if status in _STATE_KEYS else status
        details = ""
        if invoice is not None:
            pay_currency = invoice.get("pay_currency") or "USD"
            details = msg(
                ctx,
                "status_amount_line",
                amount=f"${float(invoice['amount']):.2f} USD",
                currency=pay_currency,
            )
            created = invoice.get("created_at")
            if hasattr(created, "timestamp"):
                details += msg(ctx, "status_created_line", when=f"<t:{int(created.timestamp())}:R>")

        view = discord.ui.LayoutView()
        view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('heart')} {msg(ctx, 'status_title')}\n"
                        f"**{msg(ctx, 'status_track')}:** `{track_id}`\n"
                        f"**{msg(ctx, 'status_status')}:** {icon} `{status_label}`{details}"
                    )
                )
            )
        )
        await ctx.send(view=view, ephemeral=bool(ctx.interaction))

    @commands.hybrid_command(
        name="donorinfo",
        description=CMDS.text("donorinfo.description"),
        help=CMDS.help("donorinfo"),
    )
    async def donorinfo(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.interaction:
            await ctx.defer(ephemeral=True)
        target = member or ctx.author
        total = await get_total_donated(self.bot, target.id)
        supporter = await is_supporter(self.bot, target.id)
        badge_line = (
            f"{get_emoji('badge_supporter_role')} {msg(ctx, 'supporter')}"
            if supporter
            else msg(ctx, "none")
        )
        view = discord.ui.LayoutView()
        view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('heart')} "
                        + msg(ctx, "donor_title", user=target.display_name)
                        + f"\n**{msg(ctx, 'donor_total')}:** `${total:.2f} USD`"
                        + f"\n**{msg(ctx, 'donor_badge')}:** {badge_line}"
                    )
                )
            )
        )
        await ctx.send(view=view, ephemeral=bool(ctx.interaction))

    # ── Events ───────────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Auto-grant supporter role when a known donor joins the support server."""
        if member.guild.id != SUPPORT_GUILD:
            return
        try:
            if await is_supporter(self.bot, member.id):
                role = await support_role(self.bot, "supporter")
                if role and role not in member.roles:
                    await member.add_roles(
                        role, reason="Auto-granted: existing donor joining support server"
                    )
                    logging.success(
                        "Donations",
                        f"Auto-granted supporter role to {member} ({member.id}) on join",
                    )
        except Exception as exc:
            logging.warning("Donations", f"on_member_join error for {member.id}: {exc}")


async def setup(bot: commands.Bot):
    await bot.add_cog(DonationCog(bot))
