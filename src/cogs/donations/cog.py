"""
Donations cog — OxaPay crypto donation system.

Flow:
  /donate [amount]  →  currency picker  →  invoice link (ephemeral)
  Background loop polls OxaPay every 30 s for payment confirmation.
  On Paid: records in DB, DMs the user, grants supporter role in support server.
  on_member_join: auto-grants supporter role to known donors joining the support server.
"""

import os
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config.emojis import get_emoji
from config.ids import SUPPORT_GUILD, SUPPORTER_ROLE
from utils import logging
from utils.donations import add_donor, get_total_donated, is_supporter
from .oxapay import OxaPayClient

# OxaPay key type: use your MERCHANT API key (Dashboard → Merchant → API Key).
# NOT the Sandbox key (testing only) and NOT the Payout API key (for sending crypto).
OXAPAY_KEY: str = os.getenv("OXAPAY_API_KEY", "")
INVOICE_LIFETIME: int = 60  # minutes

CURRENCIES = [
    ("USDT", "Tether",   f"{get_emoji('crypto_tether_usdt')}"),
    ("ETH",  "Ethereum", f"{get_emoji('crypto_ethereum')}"),
    ("BTC",  "Bitcoin",  f"{get_emoji('crypto_bitcoin')}"),
    ("BNB",  "BNB",      f"{get_emoji('crypto_bnb')}"),
    ("LTC",  "Litecoin", f"{get_emoji('crypto_ltc')}"),
    ("DOGE", "Dogecoin", f"{get_emoji('crypto_dogecoin')}"),
    ("TRX",  "TRON",     f"{get_emoji('crypto_tron')}"),
    ("XMR",  "Monero",   f"{get_emoji('crypto_monero')}"),
]


# ─────────────────── UI helpers ───────────────────

def _currency_select(cog: "DonationCog", amount: float, user_id: int) -> discord.ui.ActionRow:
    """Return a View containing a currency Select for `amount` USD."""
    view = discord.ui.ActionRow()
    options = [
        discord.SelectOption(
            label=f"{label} ({code})",
            value=code,
            emoji=emoji,
            description=f"Pay ${amount:.2f} worth of {code}",
        )
        for code, label, emoji in CURRENCIES
    ]
    sel = discord.ui.Select(placeholder="Choose a cryptocurrency…", options=options)

    async def _cb(interaction: discord.Interaction):
        if interaction.user.id != user_id:
            return await interaction.response.send_message(
                "This isn't your donation menu!", ephemeral=True
            )
        sel.disabled = True
        # await interaction.message.edit(view=view)
        await cog._handle_currency_choice(interaction, amount, user_id, sel.values[0])

    sel.callback = _cb
    view.add_item(sel)
    return view


def _payment_layout(
    amount: float, currency: str, track_id: str, pay_link: str
) -> discord.ui.LayoutView:
    """LayoutView showing invoice details + Pay Now link button."""
    view = discord.ui.LayoutView()
    view.add_item(
        discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {get_emoji('icon_heart')} Donation Invoice Created\n"
                    f"**Amount:** `${amount:.2f} USD` in **{currency}**\n"
                    f"**Track ID:** `{track_id}`\n"
                    f"**Expires in:** `{INVOICE_LIFETIME} minutes`\n\n"
                    f"Once your payment is confirmed on-chain you'll automatically receive "
                    f"the {get_emoji('badge_supporter')} **Supporter** badge."
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Pay Now",
                    style=discord.ButtonStyle.link,
                    url=pay_link,
                    emoji="💳",
                )
            ),
        )
    )
    return view


# ─────────────────── Cog ───────────────────

class DonationCog(commands.Cog, name="DonationCog"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # track_id → {user_id, amount, currency, channel_id}
        self._pending: dict[str, dict] = {}
        self._poll_loop.start()

    def cog_unload(self):
        self._poll_loop.cancel()

    # ── Background payment poller ──────────────────

    @tasks.loop(seconds=30)
    async def _poll_loop(self):
        if not self._pending or not OXAPAY_KEY:
            return
        client = OxaPayClient(OXAPAY_KEY)
        completed: list[str] = []
        for track_id, data in list(self._pending.items()):
            try:
                result = await client.check_payment(track_id)
                status = result.get("status", "")
                if status == "Paid":
                    await self._on_payment_confirmed(track_id, data)
                    completed.append(track_id)
                elif status in ("Expired", "Failed"):
                    completed.append(track_id)
            except Exception as exc:
                logging.warning("Donations", f"Poll error for {track_id}: {exc}")
        for tid in completed:
            self._pending.pop(tid, None)

    @_poll_loop.before_loop
    async def _before_poll(self):
        await self.bot.wait_until_ready()

    # ── Payment confirmed handler ──────────────────

    async def _on_payment_confirmed(self, track_id: str, data: dict):
        user_id: int = data["user_id"]
        amount: float = data["amount"]
        currency: str = data["currency"]
        channel_id: int | None = data.get("channel_id")

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
                            f"### {get_emoji('icon_heart')} Thank you for donating!\n"
                            f"Your donation of **${amount:.2f} USD** in **{currency}** "
                            f"has been confirmed. You've been granted the "
                            f"{get_emoji('badge_supporter')} **Supporter** badge!\n\n"
                            f"-# Track ID: `{track_id}`"
                        )
                    )
                )
            )
            await user.send(view=dm_view)
        except Exception:
            pass

        # Public thank-you in the originating channel
        if channel_id:
            try:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    pub_view = discord.ui.LayoutView()
                    pub_view.add_item(
                        discord.ui.Container(
                            discord.ui.TextDisplay(
                                content=(
                                    f"### {get_emoji('icon_heart')} New Supporter!\n"
                                    f"<@{user_id}> just donated **${amount:.2f} USD** in **{currency}**! "
                                    f"Thank you for supporting Niko! {get_emoji('badge_supporter')}"
                                )
                            )
                        )
                    )
                    await channel.send(view=pub_view)
            except Exception:
                pass

    # ── Role helpers ──────────────────────────────

    async def _grant_supporter_role(self, user_id: int):
        """Grant SUPPORTER_ROLE in the support server, silently if user isn't there."""
        if not SUPPORTER_ROLE:
            return
        support_guild = self.bot.get_guild(SUPPORT_GUILD)
        if not support_guild:
            return
        try:
            member = support_guild.get_member(user_id) or await support_guild.fetch_member(user_id)
            role = support_guild.get_role(SUPPORTER_ROLE)
            if role and role not in member.roles:
                await member.add_roles(role, reason="Crypto donation confirmed via OxaPay")
                logging.success("Donations", f"Granted supporter role to {member} ({user_id})")
        except discord.NotFound:
            pass
        except Exception as exc:
            logging.warning("Donations", f"Could not grant supporter role to {user_id}: {exc}")

    # ── Currency-select callback ──────────────────

    async def _handle_currency_choice(
        self,
        interaction: discord.Interaction,
        amount: float,
        user_id: int,
        currency: str,
    ):
        await interaction.response.defer(ephemeral=True)

        if not OXAPAY_KEY:
            return await interaction.followup.send(
                f"{get_emoji('icon_danger')} Donations are not configured yet. "
                "Please try again later.",
                ephemeral=True,
            )

        client = OxaPayClient(OXAPAY_KEY)
        result = await client.create_invoice(
            amount=amount,
            currency="USD",
            pay_currency=currency,
            lifetime=INVOICE_LIFETIME,
            description=f"Niko Bot Donation — ${amount:.2f} USD",
            order_id=f"{user_id}_{int(datetime.utcnow().timestamp())}",
        )

        if not result["success"]:
            return await interaction.followup.send(
                f"{get_emoji('icon_danger')} Could not create invoice: "
                f"{result.get('message', 'Unknown error')}",
                ephemeral=True,
            )

        track_id: str = result["trackId"]
        pay_link: str = result["payLink"]

        self._pending[track_id] = {
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "channel_id": interaction.channel_id,
        }

        await interaction.followup.send(
            view=_payment_layout(amount, currency, track_id, pay_link),
            ephemeral=True,
        )

    # ── Commands ──────────────────────────────────

    @commands.hybrid_command(
        name="donate",
        description="Support Niko with a crypto donation",
        help="{ 'en': 'support niko with crypto ☕', 'de': 'unterstütze niko mit krypto', 'es': 'apoya a niko con cripto' }",
    )
    @app_commands.describe(amount="Amount in USD to donate (e.g. 5.00, minimum $1)")
    async def donate(self, ctx: commands.Context, amount: float = 5.0):
        if ctx.interaction:
            await ctx.defer(ephemeral=True)

        if amount < 1.0:
            return await ctx.send(
                f"{get_emoji('icon_danger')} Minimum donation is `$1.00 USD`.",
                ephemeral=bool(ctx.interaction),
            )
        if amount > 10_000.0:
            return await ctx.send(
                f"{get_emoji('icon_danger')} Maximum single donation is `$10,000.00 USD`.",
                ephemeral=bool(ctx.interaction),
            )

        intro_view = discord.ui.LayoutView()
        intro_view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('icon_heart')} Donate to Niko\n"
                        f"**Amount:** `${amount:.2f} USD`\n\n"
                        f"Your donation helps cover hosting costs and keeps Niko running! "
                        f"As a thank-you you'll receive the "
                        f"{get_emoji('badge_supporter')} **Supporter** badge "
                        f"and role in the support server.\n\n"
                        f"Select a cryptocurrency below to proceed:"
                    )
                ),
                _currency_select(self, amount, ctx.author.id)
            )
        )

        # currency_sel = _currency_view(self, amount, ctx.author.id)

        if ctx.interaction:
            await ctx.interaction.followup.send(view=intro_view, ephemeral=True)
            # await ctx.interaction.followup.send(view=currency_sel, ephemeral=True)
        else:
            await ctx.send(view=intro_view)
            # await ctx.send(view=currency_sel)

    @commands.hybrid_command(
        name="donationstatus",
        description="Check the status of a pending donation by Track ID",
        help="{ 'en': 'check donation status', 'de': 'spendenstatus prüfen', 'es': 'ver estado de donación' }",
    )
    @app_commands.describe(track_id="The Track ID shown on your invoice")
    async def donationstatus(self, ctx: commands.Context, track_id: str):
        if ctx.interaction:
            await ctx.defer(ephemeral=True)

        if not OXAPAY_KEY:
            return await ctx.send(
                f"{get_emoji('icon_danger')} Donations are not configured.",
                ephemeral=bool(ctx.interaction),
            )

        client = OxaPayClient(OXAPAY_KEY)
        result = await client.check_payment(track_id)
        status = result.get("status", "Unknown")

        icons = {
            "Paid":    get_emoji("icon_tick"),
            "Waiting": get_emoji("icon_loading"),
            "Expired": get_emoji("icon_cross"),
            "Failed":  get_emoji("icon_danger"),
        }
        icon = icons.get(status, "❓")

        view = discord.ui.LayoutView()
        view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('icon_heart')} Donation Status\n"
                        f"**Track ID:** `{track_id}`\n"
                        f"**Status:** {icon} `{status}`"
                    )
                )
            )
        )
        await ctx.send(view=view, ephemeral=bool(ctx.interaction))

    @commands.hybrid_command(
        name="donorinfo",
        description="Check donor/supporter status for a user",
        help="{ 'en': 'check supporter status', 'de': 'spenderstatus', 'es': 'estado de donador' }",
    )
    async def donorinfo(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.interaction:
            await ctx.defer(ephemeral=True)
        target = member or ctx.author
        total = await get_total_donated(self.bot, target.id)
        supporter = await is_supporter(self.bot, target.id)
        badge_line = (
            f"{get_emoji('badge_supporter')} Supporter" if supporter else "None"
        )
        view = discord.ui.LayoutView()
        view.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"### {get_emoji('icon_heart')} Donor Info — {target.display_name}\n"
                        f"**Total Donated:** `${total:.2f} USD`\n"
                        f"**Badge:** {badge_line}"
                    )
                )
            )
        )
        await ctx.send(view=view, ephemeral=bool(ctx.interaction))

    # ── Events ───────────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Auto-grant supporter role when a known donor joins the support server."""
        if member.guild.id != SUPPORT_GUILD or not SUPPORTER_ROLE:
            return
        try:
            if await is_supporter(self.bot, member.id):
                role = member.guild.get_role(SUPPORTER_ROLE)
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
