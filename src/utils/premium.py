"""
Premium server subscriptions.

A subscription belongs to a guild, renews monthly, and currently unlocks one
perk: AI powered image moderation (see ``utils.nsfw_api``). Payments are stored
separately from the subscription so the owner billing tab keeps a full history
even after a subscription expires or is gifted.

All timestamps are stored as ``YYYY-MM-DD HH:MM:SS`` in UTC, matching
``datetime('now')`` in SQLite, so string comparison and ordering stay correct
on both the SQLite and MongoDB backends.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# ── Plan ─────────────────────────────────────────────────────────────────────

PREMIUM_PLAN = "premium_monthly"
PREMIUM_PRICE_CENTS = 1500          # $15.00 USD, monthly
PREMIUM_CURRENCY = "USD"
PREMIUM_MONTH_DAYS = 30
PREMIUM_REMINDER_DAYS = 3           # DM the owner this long before expiry
PREMIUM_GRACE_DAYS = 0              # expires_at is authoritative

PERKS = [
    {
        "key": "ai_image_moderation",
        "title": "AI image moderation",
        "description": "Every image posted in your server is scored by fal.ai's NSFW model and removed automatically.",
    },
]

STATUS_ACTIVE = "active"
STATUS_EXPIRED = "expired"
STATUS_CANCELLED = "cancelled"

KIND_PURCHASE = "purchase"
KIND_RENEWAL = "renewal"
KIND_GIFT = "gift"
KIND_STAFF = "staff"

PAID_STATUSES = {"paid", "confirmed"}
OPEN_STATUSES = {"waiting", "paying", "confirming"}


# ── Pure date and plan helpers (unit tested without a database) ──────────────

def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_iso(moment: datetime) -> str:
    return moment.replace(microsecond=0).isoformat(sep=" ")


def now_iso() -> str:
    return to_iso(utcnow())


def parse_ts(value) -> datetime | None:
    """Parse a stored timestamp; unreadable values mean "never"."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None) if value.tzinfo else value
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:19], fmt)
        except ValueError:
            continue
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed


def next_expiry(current_expires_at, months: int = 1, now: datetime | None = None) -> str:
    """Extend a live subscription, or start a fresh term once it has lapsed.

    Renewing early must never delete paid days, so the new term starts where the
    old one ends. Renewing a lapsed subscription starts from now.
    """
    moment = now or utcnow()
    months = max(1, int(months))
    current = parse_ts(current_expires_at)
    start = current if current and current > moment else moment
    return to_iso(start + timedelta(days=PREMIUM_MONTH_DAYS * months))


def subscription_is_active(row, now: datetime | None = None) -> bool:
    """True while a subscription row is paid up and inside its term."""
    if not row:
        return False
    if str(row.get("status", "")).lower() != STATUS_ACTIVE:
        return False
    expires = parse_ts(row.get("expires_at"))
    return bool(expires and expires > (now or utcnow()))


def days_remaining(row, now: datetime | None = None) -> int:
    """Whole days left in the current term (0 when expired)."""
    expires = parse_ts((row or {}).get("expires_at"))
    if expires is None:
        return 0
    delta = expires - (now or utcnow())
    return max(0, int(delta.total_seconds() // 86400))


def reminder_due(row, now: datetime | None = None, days: int = PREMIUM_REMINDER_DAYS) -> bool:
    """True when the owner should be warned before the term runs out.

    A reminder is sent once per term: ``reminder_sent_at`` is cleared whenever
    the subscription is renewed or granted again.
    """
    if not subscription_is_active(row, now):
        return False
    if (row or {}).get("reminder_sent_at"):
        return False
    expires = parse_ts((row or {}).get("expires_at"))
    if expires is None:
        return False
    return expires - (now or utcnow()) <= timedelta(days=days)


def price_label(cents: int = PREMIUM_PRICE_CENTS, currency: str = PREMIUM_CURRENCY) -> str:
    return f"${cents / 100:,.2f} {currency}"


def subscription_view(row) -> dict | None:
    """Shape a subscription row for the dashboard and bot embeds."""
    if not row:
        return None
    active = subscription_is_active(row)
    return {
        "guild_id": str(row.get("guild_id", "")),
        "plan": row.get("plan", PREMIUM_PLAN),
        "status": STATUS_ACTIVE if active else str(row.get("status", STATUS_EXPIRED)),
        "active": active,
        "price_cents": int(row.get("price_cents", PREMIUM_PRICE_CENTS) or 0),
        "currency": row.get("currency", PREMIUM_CURRENCY),
        "started_at": row.get("started_at"),
        "expires_at": row.get("expires_at"),
        "days_remaining": days_remaining(row),
        "source": row.get("source", KIND_PURCHASE),
        "gifted_by": str(row["gifted_by"]) if row.get("gifted_by") else None,
        "gifted_by_name": row.get("gifted_by_name"),
        "auto_renew": bool(row.get("auto_renew", 1)),
    }


# ── Database helpers ─────────────────────────────────────────────────────────

def _require_pool(pool):
    if pool is None:
        raise RuntimeError("The primary database is not available")
    return pool


async def get_subscription(pool, guild_id: int) -> dict | None:
    pool = _require_pool(pool)
    row = await pool.fetchrow(
        "SELECT guild_id, plan, status, price_cents, currency, started_at, expires_at, "
        "auto_renew, source, gifted_by, gifted_by_name, owner_id, reminder_sent_at, updated_at "
        "FROM premium_subscriptions WHERE guild_id = $1",
        int(guild_id),
    )
    return dict(row) if row else None


async def is_premium(pool, guild_id: int) -> bool:
    """Whether a guild may use premium perks right now."""
    try:
        return subscription_is_active(await get_subscription(pool, guild_id))
    except Exception:
        return False


async def activate_subscription(
    pool,
    *,
    guild_id: int,
    months: int = 1,
    source: str = KIND_PURCHASE,
    payer_id: int | None = None,
    gifted_by: int | None = None,
    gifted_by_name: str | None = None,
    owner_id: int | None = None,
    now: datetime | None = None,
) -> dict:
    """Grant or extend premium for a guild and return the stored row."""
    pool = _require_pool(pool)
    guild_id = int(guild_id)
    current = await get_subscription(pool, guild_id)
    moment = now or utcnow()
    expires_at = next_expiry((current or {}).get("expires_at"), months, now=moment)
    started_at = (current or {}).get("started_at") or to_iso(moment)

    # Mongo omits SQL expressions in SET clauses, so merge the carried-over
    # fields here instead of relying on COALESCE.
    keep_gifted_by = (current or {}).get("gifted_by")
    keep_gifted_by_name = (current or {}).get("gifted_by_name")
    keep_owner = (current or {}).get("owner_id")
    if payer_id is not None and source in {KIND_PURCHASE, KIND_RENEWAL}:
        # The latest payer is the fallback the renewal reminder reaches back to
        # if the server has no recorded owner.
        keep_owner = keep_owner or int(payer_id)

    if current is None:
        await pool.execute(
            "INSERT INTO premium_subscriptions "
            "(guild_id, plan, status, price_cents, currency, started_at, expires_at, "
            " auto_renew, source, gifted_by, gifted_by_name, owner_id, reminder_sent_at, updated_at) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, 1, $8, $9, $10, $11, NULL, $12)",
            guild_id, PREMIUM_PLAN, STATUS_ACTIVE, PREMIUM_PRICE_CENTS, PREMIUM_CURRENCY,
            started_at, expires_at, source, gifted_by, gifted_by_name,
            owner_id if owner_id is not None else keep_owner, to_iso(moment),
        )
    else:
        await pool.execute(
            "UPDATE premium_subscriptions SET status = $1, expires_at = $2, source = $3, "
            "gifted_by = $4, gifted_by_name = $5, owner_id = $6, reminder_sent_at = NULL, "
            "updated_at = $7 WHERE guild_id = $8",
            STATUS_ACTIVE, expires_at, source,
            gifted_by if gifted_by is not None else keep_gifted_by,
            gifted_by_name if gifted_by_name is not None else keep_gifted_by_name,
            owner_id if owner_id is not None else keep_owner,
            to_iso(moment), guild_id,
        )

    return await get_subscription(pool, guild_id) or {}


async def set_subscription_status(pool, guild_id: int, status: str, now: datetime | None = None) -> bool:
    pool = _require_pool(pool)
    await pool.execute(
        "UPDATE premium_subscriptions SET status = $1, updated_at = $2 WHERE guild_id = $3",
        status, to_iso(now or utcnow()), int(guild_id),
    )
    return True


async def expire_lapsed(pool, now: datetime | None = None) -> list[dict]:
    """Mark subscriptions past their term as expired; return those that changed."""
    pool = _require_pool(pool)
    moment = now or utcnow()
    rows = await pool.fetch(
        "SELECT guild_id, expires_at FROM premium_subscriptions WHERE status = $1",
        STATUS_ACTIVE,
    )
    changed = []
    for row in rows:
        expires = parse_ts(row.get("expires_at"))
        if expires is not None and expires <= moment:
            await pool.execute(
                "UPDATE premium_subscriptions SET status = $1, updated_at = $2 WHERE guild_id = $3",
                STATUS_EXPIRED, to_iso(moment), int(row["guild_id"]),
            )
            changed.append(dict(row))
    return changed


async def subscriptions_due_for_reminder(pool, now: datetime | None = None, days: int = PREMIUM_REMINDER_DAYS) -> list[dict]:
    pool = _require_pool(pool)
    rows = await pool.fetch(
        "SELECT guild_id, plan, status, expires_at, owner_id, reminder_sent_at, source, "
        "gifted_by, gifted_by_name, price_cents, currency FROM premium_subscriptions "
        "WHERE status = $1",
        STATUS_ACTIVE,
    )
    return [dict(row) for row in rows if reminder_due(dict(row), now=now, days=days)]


async def mark_reminder_sent(pool, guild_id: int, now: datetime | None = None) -> None:
    pool = _require_pool(pool)
    await pool.execute(
        "UPDATE premium_subscriptions SET reminder_sent_at = $1 WHERE guild_id = $2",
        to_iso(now or utcnow()), int(guild_id),
    )


async def record_payment(
    pool,
    *,
    order_id: str,
    track_id: str,
    guild_id: int,
    payer_id: int,
    kind: str = KIND_PURCHASE,
    months: int = 1,
    amount_cents: int = PREMIUM_PRICE_CENTS,
    currency: str = PREMIUM_CURRENCY,
    pay_currency: str | None = None,
    address: str | None = None,
    pay_amount: float | None = None,
    qr_code: str | None = None,
    expires_at: int | None = None,
    status: str = "Waiting",
) -> None:
    """Persist a checkout before the payer is sent to their wallet."""
    pool = _require_pool(pool)
    await pool.execute(
        "INSERT INTO premium_payments "
        "(order_id, track_id, guild_id, payer_id, kind, months, amount_cents, currency, "
        " pay_currency, address, pay_amount, qr_code, status, created_at, expires_at) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)",
        str(order_id), str(track_id), int(guild_id), int(payer_id), kind, int(months),
        int(amount_cents), currency, pay_currency, address, pay_amount, qr_code,
        status, now_iso(), expires_at,
    )


async def get_payment(pool, *, order_id: str | None = None, track_id: str | None = None) -> dict | None:
    pool = _require_pool(pool)
    if order_id:
        row = await pool.fetchrow(
            "SELECT * FROM premium_payments WHERE order_id = $1", str(order_id)
        )
    elif track_id:
        row = await pool.fetchrow(
            "SELECT * FROM premium_payments WHERE track_id = $1", str(track_id)
        )
    else:
        return None
    return dict(row) if row else None


async def update_payment_status(pool, track_id: str, status: str) -> None:
    pool = _require_pool(pool)
    await pool.execute(
        "UPDATE premium_payments SET status = $1 WHERE track_id = $2",
        status, str(track_id),
    )


async def confirm_payment(pool, track_id: str) -> tuple[dict | None, bool]:
    """Mark a premium payment paid exactly once.

    ``newly_paid`` gates the subscription grant and the notification DMs, so a
    provider that retries its callback cannot extend a term twice.
    """
    pool = _require_pool(pool)
    payment = await get_payment(pool, track_id=track_id)
    if payment is None:
        return None, False
    if str(payment.get("status", "")).lower() in PAID_STATUSES:
        return payment, False
    await pool.execute(
        "UPDATE premium_payments SET status = 'Paid', paid_at = $1 WHERE track_id = $2",
        now_iso(), str(track_id),
    )
    refreshed = await get_payment(pool, track_id=track_id) or payment
    return refreshed, True


async def recent_payments(pool, limit: int = 50) -> list[dict]:
    pool = _require_pool(pool)
    rows = await pool.fetch(
        "SELECT order_id, track_id, guild_id, payer_id, kind, months, amount_cents, currency, "
        "pay_currency, address, pay_amount, status, issue_status, issue_note, resolved_by, "
        "resolved_at, created_at, paid_at, expires_at FROM premium_payments "
        "ORDER BY created_at DESC, order_id DESC LIMIT $1",
        int(limit),
    )
    return [dict(row) for row in rows]


async def resolve_payment(
    pool,
    *,
    order_id: str,
    status: str,
    note: str = "",
    staff_id: int | None = None,
) -> bool:
    """Record a billing decision (open/resolved) without touching payment state."""
    pool = _require_pool(pool)
    await pool.execute(
        "UPDATE premium_payments SET issue_status = $1, issue_note = $2, resolved_by = $3, "
        "resolved_at = $4 WHERE order_id = $5",
        status, note, staff_id, now_iso(), str(order_id),
    )
    return True


async def list_subscriptions(pool, limit: int = 100) -> list[dict]:
    pool = _require_pool(pool)
    rows = await pool.fetch(
        "SELECT guild_id, plan, status, price_cents, currency, started_at, expires_at, "
        "auto_renew, source, gifted_by, gifted_by_name, owner_id, reminder_sent_at, updated_at "
        "FROM premium_subscriptions ORDER BY expires_at DESC LIMIT $1",
        int(limit),
    )
    return [dict(row) for row in rows]


async def billing_totals(pool) -> dict:
    """Small revenue summary for the owner billing tab."""
    pool = _require_pool(pool)
    rows = await pool.fetch("SELECT amount_cents FROM premium_payments WHERE paid_at IS NOT NULL")
    total = sum(int(row.get("amount_cents", 0) or 0) for row in rows)
    return {"paid_count": len(rows), "paid_cents": total}
