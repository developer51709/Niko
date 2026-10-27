"""Donation webhook helpers, used by the donation and premium routes."""

from utils.donations import confirm_invoice
from . import runtime


def _donation_bot():
    if runtime._discord_bot is None or not getattr(runtime._discord_bot, "cxn", None):
        raise RuntimeError("The bot database is unavailable.")
    return runtime._discord_bot


async def _confirm_donation_from_webhook(track_id: str, payload: dict):
    bot = _donation_bot()
    invoice, newly_confirmed = await confirm_invoice(bot, track_id, payload)
    if invoice is not None and newly_confirmed:
        donation_cog = bot.get_cog("DonationCog")
        if donation_cog is not None:
            await donation_cog._on_payment_confirmed(track_id, dict(invoice))
    return invoice, newly_confirmed
