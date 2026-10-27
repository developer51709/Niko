"""Flask routes for premium subscriptions and billing."""

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

import hmac
import hashlib
import json
import os
import uuid

from flask import jsonify, request, Response, session

from cogs.donations.oxapay import OxaPayClient
from utils import logging
import utils.premium as billing

# Currencies offered by the white-label checkout. OxaPay settles the USD price
# into the chosen asset; the payer sends exactly the quoted amount.
CRYPTO_CURRENCIES = ("USDT", "ETH", "BTC", "BNB", "LTC", "DOGE", "TRX", "XMR")
PAYMENT_LIFETIME_MINUTES = 60
MAX_STAFF_GRANT_MONTHS = 12


def merchant_key() -> str:
    return (os.getenv("OXAPAY_API_KEY") or "").strip()


def payment_configured() -> bool:
    return bool(merchant_key())


def _user_id() -> int | None:
    raw = str(session.get("user", {}).get("id", "")).strip()
    return int(raw) if raw.isdigit() else None


def _display_name() -> str | None:
    user = session.get("user") or {}
    return user.get("global_name") or user.get("username")


def _billing_bot():
    if _discord_bot is None or not getattr(_discord_bot, "cxn", None):
        raise RuntimeError("The bot database is unavailable.")
    return _discord_bot


def _crypto_valid(value: str) -> bool:
    return str(value or "").upper() in CRYPTO_CURRENCIES


def _is_member(guild_id: int, user_id: int) -> bool:
    """Whether *user_id* is a member of *guild_id* according to the gateway."""
    bot = _discord_bot
    if bot is None:
        return False
    guild = bot.get_guild(int(guild_id))
    if guild is None:
        return False

    async def check():
        member = guild.get_member(int(user_id))
        if member is not None:
            return True
        try:
            await guild.fetch_member(int(user_id))
            return True
        except Exception:
            return False

    try:
        return bool(run_on_bot_loop(check()))
    except Exception:
        return False


def _checkout_payload(result: dict, *, order_id: str, amount_cents: int, months: int) -> dict:
    data = result.get("data") or {}
    return {
        "ok": True,
        "order_id": order_id,
        "track_id": result.get("trackId"),
        "amount_cents": amount_cents,
        "amount_label": billing.price_label(amount_cents),
        "months": months,
        "pay_currency": str(data.get("pay_currency") or "").upper() or None,
        "network": data.get("network"),
        "pay_amount": data.get("pay_amount"),
        "address": data.get("address"),
        "memo": data.get("memo") or None,
        "qr_code": data.get("qr_code"),
        "expires_at": data.get("expired_at"),
        "status_url": f"/api/premium/orders/{order_id}",
    }


# ── Public plan information ──────────────────────────────────────────────────

@app.route("/api/premium/plans")
def api_premium_plans():
    return jsonify({
        "plan": billing.PREMIUM_PLAN,
        "title": "Niko Premium",
        "price_cents": billing.PREMIUM_PRICE_CENTS,
        "price_label": billing.price_label(),
        "currency": billing.PREMIUM_CURRENCY,
        "months": 1,
        "perks": billing.PERKS,
        "renewal_notice_days": billing.PREMIUM_REMINDER_DAYS,
        "currencies": list(CRYPTO_CURRENCIES),
        "methods": {
            "crypto": {"enabled": payment_configured()},
            "card": {"enabled": False, "message": "Card payments are coming soon."},
        },
    })


@app.route("/api/premium/gift-targets")
@require_auth
def api_premium_gift_targets():
    """Servers the signed-in member belongs to, with their premium state.

    Gifting only needs membership, not Manage Server, so this reads the
    gateway's member cache instead of the OAuth manage list.
    """
    user_id = _user_id()
    if user_id is None:
        return jsonify({"error": "Not authenticated"}), 401
    if _discord_bot is None:
        return jsonify({"error": "The Discord bot is not available."}), 503

    async def collect():
        bot = _billing_bot()
        rows = []
        for guild in bot.guilds:
            if guild.get_member(user_id) is None:
                continue
            sub = await billing.get_subscription(bot.cxn, guild.id)
            rows.append({
                "id": str(guild.id),
                "name": guild.name,
                "icon_url": str(guild.icon.url) if getattr(guild, "icon", None) else None,
                "member_count": int(getattr(guild, "member_count", 0) or 0),
                "premium": billing.subscription_view(sub),
            })
        rows.sort(key=lambda item: item["name"].casefold())
        return rows

    try:
        return jsonify({"guilds": run_on_bot_loop(collect())})
    except Exception:
        return jsonify({"error": "Your servers could not be loaded right now."}), 503


# ── Checkout ────────────────────────────────────────────────────────────────

@app.route("/api/premium/checkout", methods=["POST"])
@require_auth
@require_csrf
def api_premium_checkout():
    """Start a white-label crypto payment for one month of premium."""
    if not payment_configured():
        return jsonify({"error": "Payments are not configured yet."}), 503
    body = request.get_json(silent=True) or {}
    kind = str(body.get("kind") or billing.KIND_PURCHASE).strip().lower()
    if kind not in {billing.KIND_PURCHASE, billing.KIND_GIFT}:
        return jsonify({"error": "Choose a valid premium purchase type."}), 400
    pay_currency = str(body.get("pay_currency") or "").upper()
    if not _crypto_valid(pay_currency):
        return jsonify({"error": "That cryptocurrency is not available."}), 400
    raw_guild = str(body.get("guild_id") or "").strip()
    if not raw_guild.isdigit():
        return jsonify({"error": "Choose a server first."}), 400
    guild_id = int(raw_guild)
    if _discord_bot is None or _discord_bot.get_guild(guild_id) is None:
        return jsonify({"error": "Niko is not in that server."}), 404

    user_id = _user_id()
    if user_id is None:
        return jsonify({"error": "Not authenticated"}), 401

    if kind == billing.KIND_PURCHASE:
        if raw_guild not in managed_guild_ids():
            return jsonify({"error": "You need Manage Server access to upgrade that server."}), 403
    elif not _is_member(guild_id, user_id):
        return jsonify({"error": "You have to be a member of that server to gift it premium."}), 403

    amount_cents = billing.PREMIUM_PRICE_CENTS
    order_id = f"premium_{kind}_{guild_id}_{uuid.uuid4().hex}"
    guild = _discord_bot.get_guild(guild_id)
    description = (
        f"Niko Premium - {guild.name if guild else guild_id} - {billing.price_label(amount_cents)}"
    )
    if kind == billing.KIND_GIFT:
        description += " (gift)"

    try:
        client = OxaPayClient(merchant_key())
        result = run_on_bot_loop(client.create_white_label(
            amount=amount_cents / 100,
            currency=billing.PREMIUM_CURRENCY,
            pay_currency=pay_currency,
            lifetime=PAYMENT_LIFETIME_MINUTES,
            description=description,
            callback_url=f"{public_base_url()}/api/premium/webhook",
            order_id=order_id,
        ))
    except Exception as error:
        return jsonify({"error": f"Could not start the payment: {error}"}), 503
    if not result.get("success"):
        return jsonify({"error": result.get("message", "OxaPay could not start the payment.")}), 502

    data = result.get("data") or {}
    async def store():
        bot = _billing_bot()
        await billing.record_payment(
            bot.cxn,
            order_id=order_id,
            track_id=result["trackId"],
            guild_id=guild_id,
            payer_id=user_id,
            kind=kind,
            months=1,
            amount_cents=amount_cents,
            currency=billing.PREMIUM_CURRENCY,
            pay_currency=pay_currency,
            address=data.get("address"),
            pay_amount=data.get("pay_amount"),
            qr_code=data.get("qr_code"),
            expires_at=data.get("expired_at"),
        )

    try:
        run_on_bot_loop(store())
    except Exception as error:
        return jsonify({"error": f"Payment created but could not be recorded: {error}"}), 503
    return jsonify(_checkout_payload(result, order_id=order_id, amount_cents=amount_cents, months=1))


@app.route("/api/premium/orders/<order_id>")
@require_auth
def api_premium_order(order_id):
    """Poll one checkout: payment status plus the guild's current term."""
    try:
        bot = _billing_bot()
        payment = run_on_bot_loop(billing.get_payment(bot.cxn, order_id=order_id))
        if payment is None:
            return jsonify({"error": "Payment not found."}), 404
        if int(payment["payer_id"]) != (_user_id() or 0) and _current_staff_role() != "owner":
            return jsonify({"error": "Payment not found."}), 404
        subscription = run_on_bot_loop(
            billing.get_subscription(bot.cxn, int(payment["guild_id"]))
        )
    except Exception:
        return jsonify({"error": "Payment status is temporarily unavailable."}), 503

    paid = str(payment.get("status", "")).lower() in billing.PAID_STATUSES
    return jsonify({
        "order_id": payment["order_id"],
        "track_id": payment.get("track_id"),
        "status": payment.get("status"),
        "paid": paid,
        "kind": payment.get("kind"),
        "amount_cents": payment.get("amount_cents"),
        "amount_label": billing.price_label(int(payment.get("amount_cents") or 0)),
        "address": payment.get("address"),
        "pay_amount": payment.get("pay_amount"),
        "pay_currency": payment.get("pay_currency"),
        "qr_code": payment.get("qr_code"),
        "expires_at": payment.get("expires_at"),
        "guild_id": str(payment.get("guild_id")),
        "subscription": billing.subscription_view(subscription),
    })


@app.route("/api/premium/guild/<guild_id>")
@require_auth
@require_guild_access
def api_premium_guild(guild_id):
    try:
        bot = _billing_bot()
        row = run_on_bot_loop(billing.get_subscription(bot.cxn, int(guild_id)))
    except Exception:
        return jsonify({"error": "Premium status is temporarily unavailable."}), 503
    return jsonify({
        "premium": billing.subscription_view(row),
        "perks": billing.PERKS,
        "price_cents": billing.PREMIUM_PRICE_CENTS,
        "price_label": billing.price_label(),
        "payment_configured": payment_configured(),
    })


# ── Payment confirmation ────────────────────────────────────────────────────

async def _confirm_payment(track_id: str):
    """Apply a paid checkout exactly once and notify the people involved."""
    from cogs.premium.cog import notify_purchase

    bot = _billing_bot()
    payment, newly_paid = await billing.confirm_payment(bot.cxn, track_id)
    if payment is None or not newly_paid:
        return payment, False
    guild_id = int(payment["guild_id"])
    guild = bot.get_guild(guild_id)
    subscription = await billing.activate_subscription(
        bot.cxn,
        guild_id=guild_id,
        months=int(payment.get("months") or 1),
        source=payment.get("kind") or billing.KIND_PURCHASE,
        payer_id=int(payment["payer_id"]),
        gifted_by=int(payment["payer_id"]) if payment.get("kind") == billing.KIND_GIFT else None,
        owner_id=int(getattr(guild, "owner_id", 0) or 0) or None,
    )
    await notify_purchase(
        bot,
        guild_id=guild_id,
        payer_id=int(payment["payer_id"]),
        kind=payment.get("kind") or billing.KIND_PURCHASE,
        months=int(payment.get("months") or 1),
        expires_at=subscription.get("expires_at"),
        amount_cents=int(payment.get("amount_cents") or billing.PREMIUM_PRICE_CENTS),
    )
    logging.success(
        "Billing",
        f"Premium {payment.get('kind')} confirmed for guild {guild_id} "
        f"({payment.get('order_id')})",
    )
    return payment, True


@app.route("/api/premium/webhook", methods=["POST"])
def api_premium_webhook():
    """OxaPay white-label callback, signed with the merchant API key."""
    raw_body = request.get_data()
    signature = (
        request.headers.get("HMAC")
        or request.headers.get("Hmac")
        or request.headers.get("X-HMAC")
    )
    key = merchant_key()
    if not key or not signature:
        return Response("invalid", status=401, mimetype="text/plain")
    expected = hmac.new(key.encode("utf-8"), raw_body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(signature.strip(), expected):
        return Response("invalid", status=401, mimetype="text/plain")
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return Response("invalid", status=400, mimetype="text/plain")

    status = str(payload.get("status", "")).lower()
    track_id = str(payload.get("track_id") or payload.get("trackId") or "")
    if not track_id:
        return Response("ok", status=200, mimetype="text/plain")
    try:
        if status == "paid":
            run_on_bot_loop(_confirm_payment(track_id))
        else:
            run_on_bot_loop(billing.update_payment_status(
                _billing_bot().cxn, track_id, str(payload.get("status") or "Waiting")
            ))
    except Exception as error:
        logging.warning("Billing", f"OxaPay callback for {track_id} failed: {error}")
        return Response("retry", status=503, mimetype="text/plain")
    return Response("ok", status=200, mimetype="text/plain")


# ── Owner billing tab ───────────────────────────────────────────────────────

def _require_owner():
    if _current_staff_role() != "owner":
        return jsonify({"error": "Billing is restricted to the bot owner."}), 403
    return None


def _guild_label(guild_id) -> str | None:
    guild = _discord_bot.get_guild(int(guild_id)) if _discord_bot is not None else None
    return guild.name if guild else None


@app.route("/api/staff/billing")
@require_auth
def api_staff_billing():
    error = _require_owner()
    if error:
        return error
    try:
        bot = _billing_bot()
        payments = run_on_bot_loop(billing.recent_payments(bot.cxn, limit=60))
        subscriptions = run_on_bot_loop(billing.list_subscriptions(bot.cxn, limit=100))
        totals = run_on_bot_loop(billing.billing_totals(bot.cxn))
    except Exception:
        return jsonify({"error": "Billing data is temporarily unavailable."}), 503

    for payment in payments:
        payment["guild_name"] = _guild_label(payment.get("guild_id"))
        payment["amount_label"] = billing.price_label(int(payment.get("amount_cents") or 0))
        user = _discord_bot.get_user(int(payment["payer_id"])) if _discord_bot else None
        payment["payer_name"] = (
            getattr(user, "global_name", None) or getattr(user, "name", None) if user else None
        )
        payment["paid"] = str(payment.get("status", "")).lower() in billing.PAID_STATUSES

    views = []
    for row in subscriptions:
        view = billing.subscription_view(row) or {}
        view["owner_id"] = str(row["owner_id"]) if row.get("owner_id") else None
        view["guild_name"] = _guild_label(row.get("guild_id"))
        views.append(view)

    return jsonify({
        "payments": payments,
        "subscriptions": views,
        "totals": {
            **totals,
            "paid_label": billing.price_label(int(totals.get("paid_cents") or 0)),
            "active_count": sum(1 for view in views if view.get("active")),
            "expiring_soon": sum(
                1 for view in views if view.get("active") and int(view.get("days_remaining") or 0) <= billing.PREMIUM_REMINDER_DAYS
            ),
        },
        "gateway": {
            "configured": payment_configured(),
            "model": "fal-ai/imageutils/nsfw",
        },
    })


@app.route("/api/staff/billing/payments/<order_id>/resolve", methods=["POST"])
@require_auth
@require_csrf
def api_staff_resolve_payment(order_id):
    error = _require_owner()
    if error:
        return error
    body = request.get_json(silent=True) or {}
    status = str(body.get("status") or "resolved").strip().lower()
    if status not in {"open", "resolved"}:
        return jsonify({"error": "Choose open or resolved."}), 400
    note = str(body.get("note") or "").strip()[:1000]
    try:
        bot = _billing_bot()
        payment = run_on_bot_loop(billing.get_payment(bot.cxn, order_id=order_id))
        if payment is None:
            return jsonify({"error": "Payment not found."}), 404
        run_on_bot_loop(billing.resolve_payment(
            bot.cxn,
            order_id=order_id,
            status=status,
            note=note,
            staff_id=_user_id(),
        ))
    except Exception:
        return jsonify({"error": "The billing note could not be saved."}), 503
    logging.info("Billing", f"{order_id} marked {status} by staff {_user_id()}")
    return jsonify({"ok": True, "issue_status": status})


@app.route("/api/staff/billing/subscriptions/<guild_id>", methods=["POST"])
@require_auth
@require_csrf
def api_staff_subscription(guild_id):
    error = _require_owner()
    if error:
        return error
    if not str(guild_id).isdigit():
        return jsonify({"error": "Invalid guild ID."}), 400
    body = request.get_json(silent=True) or {}
    action = str(body.get("action") or "grant").strip().lower()
    try:
        bot = _billing_bot()
        if action == "cancel":
            run_on_bot_loop(billing.set_subscription_status(bot.cxn, int(guild_id), billing.STATUS_CANCELLED))
            row = run_on_bot_loop(billing.get_subscription(bot.cxn, int(guild_id)))
        elif action in {"grant", "extend"}:
            try:
                months = max(1, min(MAX_STAFF_GRANT_MONTHS, int(body.get("months") or 1)))
            except (TypeError, ValueError):
                return jsonify({"error": "Months must be a number."}), 400
            guild = _discord_bot.get_guild(int(guild_id))
            row = run_on_bot_loop(billing.activate_subscription(
                bot.cxn,
                guild_id=int(guild_id),
                months=months,
                source=billing.KIND_STAFF,
                owner_id=int(getattr(guild, "owner_id", 0) or 0) or None,
            ))
        else:
            return jsonify({"error": "Choose grant or cancel."}), 400
    except Exception:
        return jsonify({"error": "The subscription could not be changed."}), 503
    logging.info("Billing", f"Staff {_user_id()} set {guild_id} to {action}")
    return jsonify({"ok": True, "premium": billing.subscription_view(row)})
