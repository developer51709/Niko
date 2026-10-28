"""
OxaPay merchant API client.
Docs: https://oxapay.com/api
"""

from urllib.parse import quote

import aiohttp

OXAPAY_BASE = "https://api.oxapay.com"
OXAPAY_V1_BASE = "https://api.oxapay.com/v1"
_TIMEOUT = aiohttp.ClientTimeout(total=15)


class OxaPayClient:
    def __init__(self, merchant_key: str):
        self.merchant_key = merchant_key

    async def create_invoice(
        self,
        amount: float,
        currency: str = "USD",
        pay_currency: str | None = None,
        lifetime: int = 60,
        description: str = "Niko Bot Donation",
        callback_url: str | None = None,
        order_id: str | None = None,
    ) -> dict:
        """
        Create a payment invoice.

        Returns:
            {"success": True, "trackId": str, "payLink": str}
            {"success": False, "message": str}
        """
        payload: dict = {
            "merchant": self.merchant_key,
            "amount": amount,
            "currency": currency,
            "lifeTime": lifetime,
            "description": description,
        }
        if pay_currency:
            payload["payCurrency"] = pay_currency
        if callback_url:
            payload["callbackUrl"] = callback_url
        if order_id:
            payload["orderId"] = order_id

        try:
            async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                async with session.post(
                    f"{OXAPAY_BASE}/merchants/request", json=payload
                ) as resp:
                    data = await resp.json(content_type=None)
        except Exception as exc:
            return {"success": False, "message": f"Network error: {exc}"}

        if data.get("result") == 100:
            return {
                "success": True,
                "trackId": str(data.get("trackId", "")),
                "payLink": data.get("payLink", ""),
            }
        return {
            "success": False,
            "message": data.get("message", f"OxaPay error {data.get('result')}"),
        }

    async def create_white_label(
        self,
        *,
        amount: float,
        pay_currency: str,
        description: str,
        order_id: str,
        callback_url: str | None = None,
        currency: str = "USD",
        network: str | None = None,
        lifetime: int = 60,
        fee_paid_by_payer: int = 1,
        under_paid_coverage: int = 10,
        email: str | None = None,
    ) -> dict:
        """Create a white-label payment and return its raw address details.

        Unlike :meth:`create_invoice` this never produces a hosted OxaPay page:
        the caller renders the address, amount, and QR code in its own UI.

        Returns:
            {"success": True, "trackId": str, "data": dict}
            {"success": False, "message": str}
        """
        payload: dict = {
            "amount": float(amount),
            "currency": currency,
            "pay_currency": pay_currency.upper(),
            "lifetime": max(15, min(2880, int(lifetime))),
            "fee_paid_by_payer": 1 if fee_paid_by_payer else 0,
            "under_paid_coverage": max(0, min(60, int(under_paid_coverage))),
            "order_id": order_id,
            "description": description,
        }
        if network:
            payload["network"] = network
        if callback_url:
            payload["callback_url"] = callback_url
        if email:
            payload["email"] = email

        try:
            async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                async with session.post(
                    f"{OXAPAY_V1_BASE}/payment/white-label",
                    json=payload,
                    headers={
                        "merchant_api_key": self.merchant_key,
                        "Content-Type": "application/json",
                    },
                ) as resp:
                    data = await resp.json(content_type=None)
        except Exception as exc:
            return {"success": False, "message": f"Network error: {exc}"}

        details = data.get("data") if isinstance(data, dict) else None
        if isinstance(details, dict) and details.get("track_id"):
            return {
                "success": True,
                "trackId": str(details.get("track_id")),
                "data": details,
            }
        message = ""
        if isinstance(data, dict):
            error = data.get("error")
            if isinstance(error, dict) and error.get("message"):
                message = str(error["message"])
            message = message or str(data.get("message") or "")
        return {"success": False, "message": message or "OxaPay could not start this payment."}

    async def check_white_label(self, track_id: str) -> dict:
        """Status of a payment created through :meth:`create_white_label`.

        White-label payments live under the v1 API, so the legacy merchant
        inquiry cannot see them; it is still used as a fallback for invoices
        created before the white-label checkout existed. Statuses are
        normalised to the legacy capitalised form (``Paid``, ``Waiting``,
        ``Expired``, ``Failed``) so callers only handle one shape.
        """
        if not track_id:
            return {"success": False, "status": "Unknown", "message": "Missing track ID."}
        data = None
        try:
            async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                async with session.get(
                    f"{OXAPAY_V1_BASE}/payment/{quote(str(track_id), safe='')}",
                    headers={
                        "merchant_api_key": self.merchant_key,
                        "Accept": "application/json",
                    },
                ) as resp:
                    if resp.status < 500:
                        data = await resp.json(content_type=None)
        except Exception:
            data = None

        details = data.get("data") if isinstance(data, dict) else None
        if isinstance(details, dict) and details.get("status"):
            return {
                "success": True,
                "status": str(details["status"]).strip().title(),
                "data": details,
            }
        return await self.check_payment(track_id)

    async def check_payment(self, track_id: str) -> dict:
        """
        Query the status of an existing invoice.

        Returns:
            {"success": True, "status": str, "data": dict}
            {"success": False, "status": "Unknown", "message": str}

        Possible statuses: Waiting, Paid, Expired, Failed
        """
        payload = {"merchant": self.merchant_key, "trackId": track_id}
        try:
            async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                async with session.post(
                    f"{OXAPAY_BASE}/merchants/inquiry", json=payload
                ) as resp:
                    data = await resp.json(content_type=None)
        except Exception as exc:
            return {"success": False, "status": "Unknown", "message": f"Network error: {exc}"}

        if data.get("result") == 100:
            return {
                "success": True,
                "status": data.get("status", "Unknown"),
                "data": data,
            }
        return {
            "success": False,
            "status": "Unknown",
            "message": data.get("message", f"OxaPay error {data.get('result')}"),
        }
