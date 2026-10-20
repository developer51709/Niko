"""Flask routes for economy standing, achievements and top.gg vote rewards.

The dashboard needs three things this module provides:

* ``POST /api/topgg/webhook`` — top.gg's delivery target. It is authenticated by
  the shared webhook token (``TOPGG_WEBHOOK_TOKEN``) rather than by a session,
  because the caller is the listing site and not a signed-in member.
* ``GET /api/me/economy`` — the signed-in member's account-wide economy standing.
* ``GET /api/me/achievements`` — every badge with progress, unlock state and the
  reward it paid.

Both are account-scoped rather than guild-scoped: the economy is global per
Discord user, so it carries no server ranking and needs no server selected.
"""

from cogs.economy.data import ACHIEVEMENTS, achievement_progress, _get_lottery_from_db
from cogs.economy.seasons import season_status
from utils.economy_jobs import (
    LOTTERY_BASE_POT,
    LOTTERY_DRAW_INTERVAL,
    LOTTERY_TICKET_PRICE,
    get_job,
)
from cogs.economy.voting import (
    record_vote as _record_vote,
    send_vote_thanks as _send_vote_thanks,
    vote_standing,
)

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

TOPGG_WEBHOOK_TOKEN = os.environ.get("TOPGG_WEBHOOK_TOKEN", "")

#: The listing site's logo, shipped with the dashboard (``web/public/topgg.svg``)
#: so the voting badges render it in the browser instead of as an emoji.
TOPGG_LOGO_URL = "/topgg.svg"

# Reading a raw account keeps the JSON columns (achievements, transactions) and
# the voting counters intact; the dashboard's normalized rows report the number
# of achievements, which is not enough to render progress bars.
_ACCOUNT_COLUMNS = (
    "user_id, balance, bank, level, job, daily_streak, total_earned, total_spent, "
    "times_worked, bank_tier, achievements, transactions, season_progress, "
    "votes, vote_streak, best_vote_streak, last_vote, lottery_tickets, "
    "lottery_tickets_bought, lottery_wins"
)


#: Friendly names for the ledger kinds the bot writes. Every casino result
#: (``blackjack``/``slots``/``roulette``) has its own entry here: the card is
#: what tells a member their gambling activity was recorded, so a raw
#: ``blackjack_loss`` identifier would read as a missing entry rather than a
#: named result.
TRANSACTION_LABELS = {
    "activity": "Activity",
    "achievement": "Achievement",
    "interest": "Bank interest",
    "vote": "top.gg vote",
    "daily": "Daily reward",
    "work": "Work shift",
    "pay": "Payment sent",
    "received": "Payment received",
    "buy": "Shop purchase",
    "sell": "Shop sale",
    "crime": "Crime pays",
    "crime_fine": "Crime fine",
    "rob": "Robbery",
    "robbed": "Robbed",
    "rob_fail": "Robbery caught",
    "rob_apology": "Robbery apology",
    "coinflip_win": "Coinflip won",
    "coinflip_loss": "Coinflip lost",
    "dice_win": "Dice won",
    "dice_loss": "Dice lost",
    "slots_win": "Slots won",
    "slots_loss": "Slots lost",
    "blackjack": "Blackjack push",
    "blackjack_win": "Blackjack won",
    "blackjack_loss": "Blackjack lost",
    "roulette_win": "Roulette won",
    "roulette_loss": "Roulette lost",
    "lottery": "Lottery win",
    "lottery_buy": "Lottery tickets",
}


def transaction_label(kind: str) -> str:
    """The name the recent-activity card prints for a ledger kind."""
    return TRANSACTION_LABELS.get(str(kind), str(kind).replace("_", " ").strip().capitalize())


def _as_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _json_list(value) -> list:
    """Accept a JSON column as a string (SQLite) or a real list (MongoDB)."""
    if isinstance(value, str):
        try:
            value = json.loads(value or "[]")
        except (TypeError, ValueError):
            return []
    return list(value) if isinstance(value, (list, tuple)) else []


def _json_map(value) -> dict:
    """Accept a JSON object column as a string (SQLite) or a mapping (MongoDB)."""
    if isinstance(value, str):
        try:
            value = json.loads(value or "{}")
        except (TypeError, ValueError):
            return {}
    return dict(value) if isinstance(value, dict) else {}


def _read_account(user_id: str) -> dict | None:
    """Read one account's raw economy record, preferring the live bot."""
    account_id = int(user_id)
    if _discord_bot is not None:
        cog = _discord_bot.get_cog("EconomyCog")
        if cog is not None:
            try:
                return dict(run_on_bot_loop(cog.get_user_economy_data(account_id)))
            except Exception:
                pass
        pool = getattr(_discord_bot, "cxn", None)
        if pool is not None:
            async def read_row():
                return await pool.fetchrow(
                    f"SELECT {_ACCOUNT_COLUMNS} FROM economy_users WHERE user_id = ?", account_id
                )
            try:
                row = run_on_bot_loop(read_row())
                if row is not None:
                    return dict(row)
            except Exception:
                pass

    conn = sqlite_connect()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT {_ACCOUNT_COLUMNS} FROM economy_users WHERE user_id = ?", (account_id,)
        )
        columns = [description[0] for description in cursor.description]
        raw = cursor.fetchone()
        return dict(zip(columns, raw)) if raw else None
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def _global_rank(net_worth: int) -> int | None:
    """Rank by net worth with two counts instead of loading every account."""
    ledger = getattr(_discord_bot, "cxn", None) if _discord_bot is not None else None
    if ledger is None:
        return None

    async def read_rank():
        higher = await ledger.fetchval(
            "SELECT COUNT(*) FROM economy_users WHERE net_worth > ?", int(net_worth)
        )
        return int(higher or 0) + 1

    try:
        return run_on_bot_loop(read_rank())
    except Exception:
        return None


def _account_count() -> int | None:
    ledger = getattr(_discord_bot, "cxn", None) if _discord_bot is not None else None
    if ledger is None:
        return None
    try:
        return int(run_on_bot_loop(ledger.fetchval("SELECT COUNT(*) FROM economy_users")) or 0)
    except Exception:
        return None


def _recent_transactions(account: dict, limit: int = 8) -> list[dict]:
    """Shape the stored transaction log for the dashboard."""
    entries = []
    for entry in _json_list(account.get("transactions"))[:limit]:
        if not isinstance(entry, dict):
            continue
        kind = str(entry.get("kind") or "activity")
        entries.append({
            "kind": kind,
            "label": transaction_label(kind),
            "amount": _as_int(entry.get("amount")),
            "note": str(entry.get("note") or ""),
            "ts": _as_int(entry.get("ts")),
        })
    return entries


def _winner_name(winner_id: str | None) -> str | None:
    """The last winner's display name, when the live bot still knows the user."""
    if not winner_id or not str(winner_id).isdigit() or _discord_bot is None:
        return None
    user = _discord_bot.get_user(int(winner_id))
    return getattr(user, "display_name", None) if user else None


def _lottery_state() -> dict:
    """Read the current round: prize, entrants and their tickets.

    The pot lives in ``economy_lottery`` and the entrants are counted from
    ``economy_users``, so the count is the number of *members* holding a ticket
    rather than the number of tickets. The live bot is preferred; a deployment
    without it reads the same SQLite file the site is served from.
    """
    if _discord_bot is not None:
        async def read_state():
            state = dict(await _get_lottery_from_db(_discord_bot))
            row = await _discord_bot.cxn.fetchrow(
                "SELECT COUNT(*) AS participants, COALESCE(SUM(lottery_tickets), 0) AS tickets "
                "FROM economy_users WHERE lottery_tickets > 0"
            )
            state["participants"] = _as_int(row.get("participants")) if row else 0
            state["tickets"] = _as_int(row.get("tickets")) if row else 0
            return state

        try:
            state = run_on_bot_loop(read_state())
        except Exception:
            state = None
        if state is not None:
            state["last_winner_name"] = _winner_name(str(state.get("last_winner") or ""))
            return state

    # The same seed the bot's own ``_get_lottery_from_db`` falls back to, so a
    # deployment without the live bot still describes the first round instead of
    # reporting an empty, closed lottery the bot would never draw from.
    state = {"pot": LOTTERY_BASE_POT, "next_draw": int(time.time()) + LOTTERY_DRAW_INTERVAL,
             "last_winner": None, "last_pot": 0, "participants": 0, "tickets": 0}
    conn = sqlite_connect()
    if conn is None:
        return state
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT pot, next_draw, last_winner, last_pot FROM economy_lottery WHERE id = 1")
        row = cursor.fetchone()
        if row:
            state.update({"pot": _as_int(row[0]), "next_draw": _as_int(row[1]),
                          "last_winner": row[2], "last_pot": _as_int(row[3])})
        cursor.execute(
            "SELECT COUNT(*), COALESCE(SUM(lottery_tickets), 0) FROM economy_users "
            "WHERE lottery_tickets > 0"
        )
        counts = cursor.fetchone()
        if counts:
            state["participants"] = _as_int(counts[0])
            state["tickets"] = _as_int(counts[1])
    except sqlite3.Error:
        pass
    finally:
        conn.close()
    state["last_winner_name"] = None
    return state


def lottery_standing(account: dict | None) -> dict:
    """The lottery card the economy tab renders: prize, entrants, your tickets."""
    state = _lottery_state()
    pot = _as_int(state.get("pot"))
    return {
        "pot": pot,
        "participants": _as_int(state.get("participants")),
        "tickets": _as_int(state.get("tickets")),
        "your_tickets": _as_int((account or {}).get("lottery_tickets")),
        "ticket_price": LOTTERY_TICKET_PRICE,
        "next_draw": _as_int(state.get("next_draw")),
        "last_winner": state.get("last_winner_name"),
        "last_pot": _as_int(state.get("last_pot")),
        "open": pot > 0,
    }


def economy_summary(
    account: dict | None,
    *,
    global_rank: int | None = None,
    account_count: int | None = None,
    lottery: dict | None = None,
) -> dict:
    """Build the personal economy tab payload for one account."""
    account = account or {}
    balance = _as_int(account.get("balance"))
    bank = _as_int(account.get("bank"))
    unlocked = [name for name in _json_list(account.get("achievements")) if name in ACHIEVEMENTS]
    return {
        "user_id": str(account.get("user_id") or "") or None,
        "balance": balance,
        "bank": bank,
        "net_worth": balance + bank,
        "level": _as_int(account.get("level")),
        "job": account.get("job") or "barista",
        # The job column stores an id; the dashboard shows the display name so
        # the career never renders as a raw internal value.
        "job_name": get_job(account.get("job"))["name"],
        "bank_tier": _as_int(account.get("bank_tier")),
        "daily_streak": _as_int(account.get("daily_streak")),
        "total_earned": _as_int(account.get("total_earned")),
        "total_spent": _as_int(account.get("total_spent")),
        "times_worked": _as_int(account.get("times_worked")),
        "achievements_unlocked": len(unlocked),
        "achievements_total": len(ACHIEVEMENTS),
        "achievement_coins": sum(int(ACHIEVEMENTS[name].get("reward", 0)) for name in unlocked),
        "global_rank": global_rank,
        "account_count": account_count,
        "transactions": _recent_transactions(account),
        "lottery": lottery if lottery is not None else lottery_standing(account),
        "vote": vote_standing(account),
    }


def achievement_entries(account: dict | None, now=None) -> list[dict]:
    """Build the achievement list: unlock state, progress and reward.

    Unearned badges come first, closest to completion at the top, so the tab
    opens on what the member can still win. A seasonal badge also carries its
    window, which is how the tab explains a badge that is out of reach today.
    """
    # A raw SQLite row keeps the JSON columns as strings, and the seasonal
    # baselines have to be a mapping for the window measurements below.
    account = {**(account or {}), "season_progress": _json_map((account or {}).get("season_progress"))}
    unlocked = set(_json_list(account.get("achievements")))
    entries = []
    for achievement_id, meta in ACHIEVEMENTS.items():
        # ``achievement_id`` + ``now`` keep a seasonal badge's bar measured the
        # same way the bot measures it: inside its own window only.
        current, target = achievement_progress(
            meta, account, now=now, achievement_id=achievement_id
        )
        entries.append({
            "id": achievement_id,
            "name": meta["name"],
            "emoji": meta["emoji"],
            # Voting badges carry the site logo; every other badge keeps its emoji.
            "icon_url": TOPGG_LOGO_URL if meta.get("icon") == "topgg" else None,
            # ``None`` for a badge that is available all year round.
            "season": season_status(meta, now),
            "description": meta.get("description") or "",
            "reward": int(meta.get("reward", 0)),
            "unlocked": achievement_id in unlocked,
            "progress": {
                "current": current,
                "target": target,
                "percent": int(round(current / target * 100)),
            },
        })
    entries.sort(key=lambda entry: (entry["unlocked"], -entry["progress"]["percent"], entry["name"]))
    return entries


@app.route("/api/me/economy")
@require_auth
def api_me_economy():
    """The signed-in member's account-wide economy standing."""
    user_id = str(session["user"].get("id", ""))
    try:
        account = _read_account(user_id) or {}
    except Exception:
        return jsonify({"error": "Your economy standing is temporarily unavailable."}), 503

    return jsonify(economy_summary(
        account,
        global_rank=_global_rank(_as_int(account.get("balance")) + _as_int(account.get("bank"))),
        account_count=_account_count(),
        lottery=lottery_standing(account),
    ))


@app.route("/api/me/achievements")
@require_auth
def api_me_achievements():
    """Every badge with progress, unlock state and the coins it paid."""
    user_id = str(session["user"].get("id", ""))
    try:
        account = _read_account(user_id) or {}
    except Exception:
        return jsonify({"error": "Achievements are temporarily unavailable."}), 503

    entries = achievement_entries(account)
    earned = [entry for entry in entries if entry["unlocked"]]
    return jsonify({
        "achievements": entries,
        "unlocked": len(earned),
        "total": len(entries),
        "coins_earned": sum(entry["reward"] for entry in earned),
        "coins_available": sum(entry["reward"] for entry in entries if not entry["unlocked"]),
    })


@app.route("/api/topgg/webhook", methods=["POST"])
def api_topgg_webhook():
    """Receive a top.gg vote and pay it out.

    top.gg authenticates the delivery with the authorization token configured on
    the listing, so the header check below is the only guard: without a
    configured token the endpoint stays closed rather than trusting anyone.
    """
    raw_body = request.get_data()
    token = (request.headers.get("Authorization") or "").strip()
    if not TOPGG_WEBHOOK_TOKEN or not token or not hmac.compare_digest(token, TOPGG_WEBHOOK_TOKEN):
        return Response("invalid", status=401, mimetype="text/plain")
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return Response("invalid", status=400, mimetype="text/plain")
    if not isinstance(payload, dict):
        return Response("invalid", status=400, mimetype="text/plain")

    # top.gg sends a "test" event when the webhook is first configured; it
    # proves the token works and must not pay anybody out.
    if str(payload.get("type", "upvote")).lower() in {"test", "webhook_test"}:
        return Response("ok", status=200, mimetype="text/plain")

    user_id = str(payload.get("user") or payload.get("user_id") or "")
    if not user_id.isdigit():
        return Response("invalid", status=400, mimetype="text/plain")
    weekend = bool(payload.get("isWeekend") or payload.get("weekend"))

    try:
        result = run_on_bot_loop(_record_vote(_discord_bot, user_id, weekend=weekend))
    except Exception:
        # A 503 tells top.gg to retry, and a retried vote is deduplicated by
        # the 12-hour cooldown inside record_vote.
        return Response("retry", status=503, mimetype="text/plain")

    if result.get("status") == "recorded":
        try:
            run_on_bot_loop(_send_vote_thanks(_discord_bot, user_id, result))
        except Exception:
            pass  # the reward is already banked; a failed DM must not undo it
    return Response("ok", status=200, mimetype="text/plain")
