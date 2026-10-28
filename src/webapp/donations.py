"""Donation webhook helpers, used by the donation and premium routes."""

from utils.donations import confirm_invoice, get_invoice
from . import runtime


def _donation_bot():
    if runtime._discord_bot is None or not getattr(runtime._discord_bot, "cxn", None):
        raise RuntimeError("The bot database is unavailable.")
    return runtime._discord_bot


async def _confirm_donation_from_webhook(track_id: str, payload: dict):
    """Credit a paid invoice once, through the cog that owns the side effects.

    The cog's handler already guards against duplicate confirmations, so the
    webhook never marks the invoice paid itself; doing both was what kept
    webhook donations from ever reaching the donor table or the DM receipt.
    """
    bot = _donation_bot()
    donation_cog = bot.get_cog("DonationCog")
    if donation_cog is not None:
        confirmed = await donation_cog._on_payment_confirmed(track_id, payload)
        return await get_invoice(bot, track_id=track_id), bool(confirmed)
    invoice, newly_confirmed = await confirm_invoice(bot, track_id, payload)
    return invoice, newly_confirmed
