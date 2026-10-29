"""Flask routes for donation."""

from .. import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

from cogs.donations.oxapay import build_order_id

from utils.donations import (
    CRYPTO_CURRENCIES,
    DONATION_MAX_AMOUNT,
    DONATION_MIN_AMOUNT,
    DONATION_PRESET_AMOUNTS,
    confirm_invoice,
    donation_goal_cents,
    get_donation_totals,
    get_total_donated,
)

@app.route("/api/donations/meta")
def api_donation_meta(token: str | None = None):
    """Everything the donation page needs besides the checkout itself.

    Public totals are deliberately aggregate-only: a donor list with user IDs
    is not needed to show progress, and the last few donations stay private.
    """
    goal_cents = donation_goal_cents()
    totals = {"total_cents": 0, "donation_count": 0, "donor_count": 0}
    your_total_cents = 0
    try:
        bot = _donation_bot()
        totals = run_on_bot_loop(get_donation_totals(bot))
        claims = verify_donation_token(token) if token else None
        if claims is not None:
            your_total_cents = int(round(
                run_on_bot_loop(get_total_donated(bot, int(claims["user_id"]))) * 100
            ))
    except Exception:
        pass

    return jsonify({
        "presets": list(DONATION_PRESET_AMOUNTS),
        "currencies": list(CRYPTO_CURRENCIES),
        "min_amount": DONATION_MIN_AMOUNT,
        "max_amount": DONATION_MAX_AMOUNT,
        "totals": totals,
        "goal_cents": goal_cents,
        "progress": round(totals["total_cents"] / goal_cents, 4) if goal_cents else None,
        "your_total_cents": your_total_cents,
        "configured": bool(OXAPAY_KEY),
    })


@app.route("/api/donations/invoice", methods=["POST"])
def api_create_donation_invoice():
    """Create a white-label OxaPay payment for a signed Discord donation link."""
    body = request.get_json(silent=True) or {}
    claims = verify_donation_token(body.get("token", ""))
    if claims is None:
        return jsonify({"error": "This donation link is invalid or expired."}), 400
    try:
        amount = round(float(body.get("amount", 5)), 2)
    except (TypeError, ValueError):
        return jsonify({"error": "Donation amount must be a number."}), 400
    currency = str(body.get("currency", "USDT")).upper()
    if not DONATION_MIN_AMOUNT <= amount <= DONATION_MAX_AMOUNT:
        return jsonify({
            "error": (
                f"Donation amount must be between ${DONATION_MIN_AMOUNT:,.0f} "
                f"and ${DONATION_MAX_AMOUNT:,.0f}."
            )
        }), 400
    if currency not in CRYPTO_CURRENCIES:
        return jsonify({"error": "That cryptocurrency is not available."}), 400
    if not OXAPAY_KEY:
        return jsonify({"error": "Donations are not configured yet."}), 503

    order_id = build_order_id("donation", claims["user_id"])
    callback_url = f"{public_base_url()}/api/donations/webhook"
    # White-label: the payer receives an address, amount, and QR code from our
    # own page instead of a hosted OxaPay checkout.
    try:
        client = OxaPayClient(OXAPAY_KEY)
        result = run_on_bot_loop(client.create_white_label(
            amount=amount,
            currency="USD",
            pay_currency=currency,
            lifetime=60,
            description=f"Niko Bot Donation - ${amount:.2f} USD",
            callback_url=callback_url,
            order_id=order_id,
        ))
    except Exception as error:
        return jsonify({"error": f"Could not create the invoice: {error}"}), 503
    if not result.get("success"):
        return jsonify({"error": result.get("message", "OxaPay could not create the invoice.")}), 502

    details = result.get("data") or {}
    try:
        save_invoice_result = save_invoice
        run_on_bot_loop(save_invoice_result(
            _discord_bot,
            order_id=order_id,
            track_id=result["trackId"],
            user_id=int(claims["user_id"]),
            amount=amount,
            currency="USD",
            pay_currency=currency,
            pay_link="",
        ))
    except Exception as error:
        return jsonify({"error": f"Invoice created but could not be recorded: {error}"}), 503
    return jsonify({
        "ok": True,
        "order_id": order_id,
        "track_id": result["trackId"],
        "pay_link": "",
        "amount_cents": int(round(amount * 100)),
        "amount_label": f"${amount:,.2f} USD",
        "pay_currency": currency,
        "pay_amount": details.get("pay_amount"),
        "network": details.get("network"),
        "address": details.get("address"),
        "memo": details.get("memo") or None,
        "qr_code": details.get("qr_code"),
        "expires_at": details.get("expired_at"),
        "status_url": f"/api/donations/{quote(order_id, safe='')}",
    })

@app.route("/api/donations/<order_id>")
def api_donation_status(order_id):
    """Status of one donation, reconciled with OxaPay while it is still open.

    The page polls this endpoint, so checking the provider here means a payment
    shows up even when the webhook is delayed or was never delivered. The
    webhook (or the bot's poller) still owns crediting the donation.
    """
    try:
        bot = _donation_bot()
        invoice = run_on_bot_loop(get_invoice(bot, order_id=order_id))
    except Exception as error:
        return jsonify({"error": str(error)}), 503
    if invoice is None:
        return jsonify({"error": "Donation invoice not found."}), 404

    status = str(invoice.get("status") or "Unknown")
    track_id = str(invoice.get("track_id") or "")
    if OXAPAY_KEY and track_id and status.lower() != "paid":
        try:
            provider = run_on_bot_loop(OxaPayClient(OXAPAY_KEY).check_white_label(track_id))
            checked = str(provider.get("status") or "")
            if checked == "Paid":
                donation_cog = _discord_bot.get_cog("DonationCog") if _discord_bot else None
                if donation_cog is not None:
                    run_on_bot_loop(donation_cog._on_payment_confirmed(track_id))
                else:
                    run_on_bot_loop(confirm_invoice(bot, track_id))
                status = "Paid"
            elif checked in ("Expired", "Failed"):
                run_on_bot_loop(update_invoice_status(bot, track_id, checked))
                status = checked
        except Exception:
            pass

    return jsonify({
        "order_id": order_id,
        "track_id": track_id or None,
        "status": status,
        "paid": status.lower() == "paid",
        "amount_cents": int(round(float(invoice.get("amount") or 0) * 100)),
        "amount_label": f"${float(invoice.get('amount') or 0):,.2f} USD",
        "pay_currency": invoice.get("pay_currency"),
        "paid_at": str(invoice.get("paid_at") or "") or None,
    })

@app.route("/api/donations/webhook", methods=["POST"])
def api_donation_webhook():
    raw_body = request.get_data()
    signature = request.headers.get("HMAC") or request.headers.get("Hmac") or request.headers.get("X-HMAC")
    if not OXAPAY_KEY or not signature:
        return Response("invalid", status=401, mimetype="text/plain")
    expected = hmac.new(OXAPAY_KEY.encode("utf-8"), raw_body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(signature.strip(), expected):
        return Response("invalid", status=401, mimetype="text/plain")
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return Response("invalid", status=400, mimetype="text/plain")
    status = str(payload.get("status", "")).lower()
    track_id = str(payload.get("trackId") or payload.get("track_id") or "")
    if not track_id:
        return Response("ok", status=200, mimetype="text/plain")
    try:
        if status == "paid":
            run_on_bot_loop(_confirm_donation_from_webhook(track_id, payload))
        elif status in {"waiting", "paying", "confirming", "expired", "failed"}:
            run_on_bot_loop(update_invoice_status(_donation_bot(), track_id, str(payload.get("status"))))
    except Exception:
        return Response("retry", status=503, mimetype="text/plain")
    return Response("ok", status=200, mimetype="text/plain")
