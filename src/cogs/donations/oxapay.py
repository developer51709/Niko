"""
OxaPay merchant API client.
Docs: https://oxapay.com/api
"""

import aiohttp

OXAPAY_BASE = "https://api.oxapay.com"
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
