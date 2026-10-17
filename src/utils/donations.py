"""
Donation database and payment-link helpers.
Used by the donations cog, website webhook, and supporter badge lookup.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from urllib.parse import quote


def _signing_secret() -> bytes:
    """Use a stable deployment secret without exposing it to the browser."""
    secret = (
        os.getenv("DONATION_TOKEN_SECRET")
        or os.getenv("SESSION_SECRET")
        or os.getenv("DISCORD_BOT_TOKEN")
    )
    if not secret:
        raise RuntimeError("Donation links require DONATION_TOKEN_SECRET or SESSION_SECRET.")
    return secret.encode("utf-8")


def create_donation_token(user_id: int, lifetime: int = 3600) -> str:
    """Create a short-lived signed token binding a website flow to a Discord user."""
    payload = {
        "user_id": str(user_id),
        "expires": int(time.time()) + lifetime,
        "nonce": secrets.token_urlsafe(8),
    }
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ).decode("ascii").rstrip("=")
    signature = hmac.new(_signing_secret(), encoded.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def verify_donation_token(token: str) -> dict | None:
    """Validate a signed donation token and return its claims when it is current."""
    if not isinstance(token, str) or "." not in token:
        return None
    encoded, signature = token.rsplit(".", 1)
    try:
        expected = hmac.new(_signing_secret(), encoded.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        padded = encoded + "=" * (-len(encoded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
        if int(payload.get("expires", 0)) < int(time.time()):
            return None
        if not str(payload.get("user_id", "")).isdigit():
            return None
        return payload
    except (ValueError, TypeError, KeyError, json.JSONDecodeError, RuntimeError):
        return None


def donation_link(base_url: str, user_id: int) -> str:
    """Build the website donation URL for a Discord user."""
    token = create_donation_token(user_id)
    return f"{base_url.rstrip('/')}/donate?token={quote(token, safe='')}"


async def is_supporter(bot, user_id: int) -> bool:
    """Return True if user_id has at least one confirmed donation."""
    if not getattr(bot, "cxn", None):
        return False
    try:
        row = await bot.cxn.fetchrow(
            "SELECT 1 FROM donors WHERE user_id = $1", user_id
        )
        return row is not None
    except Exception:
        return False


async def add_donor(bot, user_id: int, amount: float, currency: str, track_id: str) -> None:
    """Insert or update a donor record after a confirmed payment."""
    if not getattr(bot, "cxn", None):
        return
    await bot.cxn.execute(
        """
        INSERT INTO donors (user_id, total_donated, last_donation, last_track_id)
        VALUES ($1, $2, datetime('now'), $3)
        ON CONFLICT(user_id) DO UPDATE SET
            total_donated = total_donated + $4,
            last_donation  = datetime('now'),
            last_track_id  = $5
        """,
        user_id, amount, track_id, amount, track_id,
    )


async def save_invoice(
    bot,
    *,
    order_id: str,
    track_id: str,
    user_id: int,
    amount: float,
    currency: str,
    pay_currency: str,
    pay_link: str,
    channel_id: int | None = None,
) -> None:
    """Persist an OxaPay invoice so it survives bot restarts."""
    if not getattr(bot, "cxn", None):
        raise RuntimeError("The bot database is unavailable.")
    await bot.cxn.execute(
        """
        INSERT INTO donation_invoices
            (order_id, track_id, user_id, amount, currency, pay_currency, pay_link, status, channel_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'Waiting', $8)
        ON CONFLICT(order_id) DO UPDATE SET
            track_id = $9, user_id = $10, amount = $11, currency = $12,
            pay_currency = $13, pay_link = $14, channel_id = $15
        """,
        order_id, track_id, user_id, amount, currency, pay_currency, pay_link, channel_id,
        track_id, user_id, amount, currency, pay_currency, pay_link, channel_id,
    )


async def get_invoice(bot, *, order_id: str | None = None, track_id: str | None = None):
    """Return one persisted invoice by its website order or OxaPay track ID."""
    if not getattr(bot, "cxn", None):
        return None
    if order_id:
        return await bot.cxn.fetchrow(
            "SELECT order_id, track_id, user_id, amount, currency, pay_currency, pay_link, status, channel_id, created_at, paid_at "
            "FROM donation_invoices WHERE order_id = $1", order_id
        )
    if track_id:
        return await bot.cxn.fetchrow(
            "SELECT order_id, track_id, user_id, amount, currency, pay_currency, pay_link, status, channel_id, created_at, paid_at "
            "FROM donation_invoices WHERE track_id = $1", track_id
        )
    return None


async def get_pending_invoices(bot) -> list:
    """Return invoices still eligible for a provider status check."""
    if not getattr(bot, "cxn", None):
        return []
    return await bot.cxn.fetch(
        "SELECT order_id, track_id, user_id, amount, currency, pay_currency, pay_link, status, channel_id "
        "FROM donation_invoices WHERE status IN ('Waiting', 'Paying', 'Confirming')"
    )


async def update_invoice_status(bot, track_id: str, status: str) -> None:
    """Store a non-terminal provider status."""
    if not getattr(bot, "cxn", None):
        return
    await bot.cxn.execute(
        "UPDATE donation_invoices SET status = $1 WHERE track_id = $2",
        status, track_id,
    )


async def confirm_invoice(bot, track_id: str, provider_data: dict | None = None) -> tuple[dict | None, bool]:
    """Mark an invoice paid once and return ``(invoice, newly_confirmed)``.

    The read/update guard makes repeated OxaPay callbacks harmless. The donor
    side effect is only called by the caller when ``newly_confirmed`` is true.
    """
    invoice = await get_invoice(bot, track_id=track_id)
    if invoice is None or str(invoice.get("status", "")).lower() == "paid":
        return invoice, False
    await bot.cxn.execute(
        "UPDATE donation_invoices SET status = 'Paid', paid_at = datetime('now') WHERE track_id = $1",
        track_id,
    )
    refreshed = await get_invoice(bot, track_id=track_id) or invoice
    return refreshed, True


async def get_total_donated(bot, user_id: int) -> float:
    """Return the total USD donated by user_id, or 0.0."""
    if not getattr(bot, "cxn", None):
        return 0.0
    try:
        row = await bot.cxn.fetchrow(
            "SELECT total_donated FROM donors WHERE user_id = $1", user_id
        )
        return float(row["total_donated"]) if row else 0.0
    except Exception:
        return 0.0
