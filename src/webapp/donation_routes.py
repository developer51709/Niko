"""Flask routes for donation."""

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

@app.route("/api/donations/invoice", methods=["POST"])
def api_create_donation_invoice():
    """Create a hosted OxaPay invoice for a signed Discord donation link."""
    body = request.get_json(silent=True) or {}
    claims = verify_donation_token(body.get("token", ""))
    if claims is None:
        return jsonify({"error": "This donation link is invalid or expired."}), 400
    try:
        amount = float(body.get("amount", 5))
    except (TypeError, ValueError):
        return jsonify({"error": "Donation amount must be a number."}), 400
    currency = str(body.get("currency", "USDT")).upper()
    if not 1 <= amount <= 10000:
        return jsonify({"error": "Donation amount must be between $1 and $10,000."}), 400
    if currency not in {"USDT", "ETH", "BTC", "BNB", "LTC", "DOGE", "TRX", "XMR"}:
        return jsonify({"error": "That cryptocurrency is not available."}), 400
    if not OXAPAY_KEY:
        return jsonify({"error": "Donations are not configured yet."}), 503

    order_id = f"donation_{claims['user_id']}_{uuid.uuid4().hex}"
    callback_url = f"{public_base_url()}/api/donations/webhook"
    try:
        client = OxaPayClient(OXAPAY_KEY)
        result = run_on_bot_loop(client.create_invoice(
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
            pay_link=result["payLink"],
        ))
    except Exception as error:
        return jsonify({"error": f"Invoice created but could not be recorded: {error}"}), 503
    return jsonify({
        "ok": True,
        "order_id": order_id,
        "track_id": result["trackId"],
        "pay_link": result["payLink"],
        "status_url": f"/api/donations/{quote(order_id, safe='')}",
    })

@app.route("/api/donations/<order_id>")
def api_donation_status(order_id):
    try:
        invoice = run_on_bot_loop(get_invoice(_donation_bot(), order_id=order_id))
    except Exception as error:
        return jsonify({"error": str(error)}), 503
    if invoice is None:
        return jsonify({"error": "Donation invoice not found."}), 404
    return jsonify({"status": invoice.get("status", "Unknown"), "paid": str(invoice.get("status", "")).lower() == "paid"})

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
