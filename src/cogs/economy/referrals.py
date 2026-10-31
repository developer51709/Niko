"""Coins for the member whose support-server invite brought somebody in.

The invite and the attribution live with the support server
(``cogs/staff/support_referrals.py``); this module only moves the money, so the
join handler can pay a referrer without reaching into the economy cog. Keeping
the amount and the ledger wording here means the reward is in one place instead
of being spelled out in a member-join listener.
"""

from __future__ import annotations

from utils import logging as log

from .data import _check_achievements, _default_user, _get_user_from_db, _log_tx, _save_user_to_db

#: Paid to the referrer for each member their own link brings in. Deliberately
#: small — an invite is a nudge, not a job — but the badges below stack on top.
REFERRAL_REWARD = 250


async def pay_referral(bot, referrer_id: int, member_id: int) -> dict | None:
    """Credit one referral to *referrer_id*, or ``None`` when it could not be paid.

    The account is read, credited and saved in one pass, so the counter the
    referral badges read and the coins in the wallet always move together. A
    referrer who has never used the economy still gets an account: their link
    worked, and losing the reward because they had not run a command yet would
    read as a bug.
    """
    try:
        data = await _get_user_from_db(bot, referrer_id)
    except Exception as exc:  # never let a payout break the join handler
        log.error("Economy", f"Could not read referrer {referrer_id}: {exc}")
        return None
    if data is None:
        data = _default_user()
        data["user_id"] = int(referrer_id)

    data["balance"] = int(data.get("balance", 0)) + REFERRAL_REWARD
    data["total_earned"] = int(data.get("total_earned", 0)) + REFERRAL_REWARD
    data["referral_count"] = int(data.get("referral_count", 0)) + 1
    _log_tx(data, "referral", REFERRAL_REWARD, f"Referral {member_id}")
    # Badges pay their own reward the moment they unlock, exactly as they do on
    # every other economy action.
    unlocked = _check_achievements(data)
    await _save_user_to_db(bot, referrer_id, data)
    return {
        "reward": REFERRAL_REWARD,
        "balance": int(data["balance"]),
        "referral_count": int(data["referral_count"]),
        "achievements": unlocked,
    }
