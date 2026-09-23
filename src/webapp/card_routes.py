"""Flask routes for card."""

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

@app.route("/api/cards/rank")
def card_rank():
    """Rank / level card (820x340). Queries levels + level_config from DB."""
    guild_id = _int_param(request.args.get("guild"))
    user_id = _int_param(request.args.get("user"))
    accent, bg_top, bg_bot = _get_guild_card_colors(guild_id)

    row = _db_fetchone(
        "SELECT xp, level FROM levels WHERE guild_id = ? AND user_id = ?",
        (guild_id, user_id),
    )
    xp = row["xp"] if row else 0
    level = row["level"] if row else 0

    # Compute rank
    rank_row = _db_fetchone(
        "SELECT COUNT(*) as r FROM levels WHERE guild_id = ? AND xp > ?",
        (guild_id, xp),
    )
    rank = (rank_row["r"] + 1) if rank_row else 1

    # XP for next level (simplified formula: level * 100 + 100)
    xp_for_next = level * 100 + 100
    xp_in_level = xp
    for lvl in range(level):
        xp_in_level -= lvl * 100 + 100
    xp_in_level = max(0, xp_in_level)

    # Try to get display name from Discord cache via bot
    name = f"User {user_id}"
    try:
        if _discord_bot:
            member = _discord_bot.get_guild(guild_id) and _discord_bot.get_guild(guild_id).get_member(user_id)
            if member:
                name = member.display_name
    except Exception:
        pass

    W, H = 820, 340
    bar_w = W - 120
    progress = min(1.0, xp_in_level / max(1, xp_for_next)) if xp_for_next > 0 else 0

    body = (
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#' + bg_top + '"/>'
        '<stop offset="100%" stop-color="#' + bg_bot + '"/>'
        '</linearGradient></defs>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="url(#bg)"/>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="none" '
        'stroke="#' + accent + '" stroke-width="2" opacity="0.6"/>'
        '<text x="36" y="50" fill="#' + accent + '" font-family="Space Mono, monospace" '
        'font-size="12" font-weight="700">LEVEL RANK</text>'
        '<text x="36" y="90" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="28" font-weight="700">' + _safe(name[:30]) + '</text>'
        '<text x="36" y="130" fill="#C8BBA8" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="18">Level ' + str(level) + ' &#183; Rank #' + str(rank) + '</text>'
        '<rect x="36" y="160" width="' + str(bar_w) + '" height="24" rx="12" '
        'fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.6)" stroke-width="1"/>'
        '<rect x="36" y="160" width="' + str(int(bar_w * progress)) + '" height="24" rx="12" '
        'fill="#' + accent + '" opacity="0.8"/>'
        '<text x="36" y="220" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="13">'
        + _format_num(xp_in_level) + ' / ' + _format_num(xp_for_next) + ' XP</text>'
        '<text x="36" y="260" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">'
        'Total: ' + _format_num(xp) + ' XP</text>'
        '<text x="' + str(W - 36) + '" y="' + str(H - 20) + '" text-anchor="end" fill="#8C918E" '
        'font-family="Space Mono, monospace" font-size="10">LEVELING</text>'
    )
    return _svg_wrap(body, W, H)

@app.route("/api/cards/leaderboard")
def card_leaderboard():
    """Leaderboard card — variable height. Queries levels from DB."""
    guild_id = _int_param(request.args.get("guild"))
    page = _int_param(request.args.get("page"), 1)
    card_type = request.args.get("type", "level")
    accent, bg_top, bg_bot = _get_guild_card_colors(guild_id) if card_type == "level" else ("FFC45C", "261A16", "120C0A")
    per_page = 10
    offset = (page - 1) * per_page

    if card_type == "level":
        rows = _db_query(
            "SELECT user_id, xp, level FROM levels WHERE guild_id = ? ORDER BY xp DESC LIMIT ? OFFSET ?",
            (guild_id, per_page, offset),
        )
        total_row = _db_fetchone("SELECT COUNT(*) as c FROM levels WHERE guild_id = ?", (guild_id,))
        total = total_row["c"] if total_row else 0
    else:
        rows = _db_query(
            "SELECT user_id, balance, bank FROM economy_users ORDER BY (balance + bank) DESC LIMIT ? OFFSET ?",
            (per_page, offset),
        )
        total_row = _db_fetchone("SELECT COUNT(*) as c FROM economy_users")
        total = total_row["c"] if total_row else 0

    pages = max(1, (total + per_page - 1) // per_page)
    W = 820
    ROW_H = 56
    n = len(rows)
    H = 110 + n * (ROW_H + 8) + 56
    medals = {0: "\u00231st", 1: "\u00232nd", 2: "\u00233rd"}

    rows_svg = ""
    for i, row in enumerate(rows):
        uid = row["user_id"]
        y = 110 + i * (ROW_H + 8)
        name = f"User {uid}"
        try:
            if _discord_bot:
                g = _discord_bot.get_guild(guild_id)
                if g:
                    m = g.get_member(uid)
                    if m:
                        name = m.display_name
        except Exception:
            pass

        if card_type == "level":
            val = row.get("xp", 0)
            subtitle = f"Level {row.get('level', 0)}"
        else:
            val = row.get("balance", 0) + row.get("bank", 0)
            subtitle = _format_num(val)

        rc = "#FFDC8C" if i == 0 else ("#F5E8D2" if i == 1 else ("#" + accent if i == 2 else "#C8BBA8"))
        rt = medals.get(i, f"#{i + 1}")
        fs = "22" if i < 3 else "18"

        rows_svg += (
            '<rect x="28" y="' + str(y) + '" width="' + str(W - 56) + '" height="' + str(ROW_H)
            + '" rx="14" fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.8)" stroke-width="1"/>'
            '<text x="' + str(28 + 56) + '" y="' + str(y + ROW_H // 2 + 6) + '" text-anchor="middle" fill="'
            + rc + '" font-family="Plus Jakarta Sans, sans-serif" font-size="' + fs + '" font-weight="700">'
            + rt + '</text>'
            '<text x="' + str(28 + 60 + ROW_H - 16 + 14 + 28) + '" y="' + str(y + ROW_H // 2 + 2)
            + '" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" font-size="18" font-weight="700">'
            + _safe(name[:25]) + '</text>'
            '<text x="' + str(W - 28 - 24) + '" y="' + str(y + ROW_H // 2 + 2)
            + '" text-anchor="end" fill="#' + accent + '" font-family="Plus Jakarta Sans, sans-serif" '
            'font-size="20" font-weight="700">' + _format_num(val) + '</text>'
        )

    title = "Leveling Leaderboard" if card_type == "level" else "\U0001f3e6 Cafe Rich List"
    body = (
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#' + bg_top + '"/>'
        '<stop offset="100%" stop-color="#' + bg_bot + '"/>'
        '</linearGradient></defs>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="28" fill="url(#bg)"/>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="28" fill="none" '
        'stroke="#' + accent + '" stroke-width="2" opacity="0.6"/>'
        '<text x="36" y="40" fill="#' + accent + '" font-family="Space Mono, monospace" '
        'font-size="12" font-weight="700">CAFE ' + card_type.upper() + '</text>'
        '<text x="36" y="66" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="26" font-weight="700">' + title + '</text>'
        '<text x="' + str(W - 36) + '" y="60" text-anchor="end" fill="#C8BBA8" '
        'font-family="Space Mono, monospace" font-size="13">Page ' + str(page) + '/' + str(pages) + '</text>'
        + rows_svg +
        '<text x="36" y="' + str(H - 20) + '" fill="#C8BBA8" font-family="Space Mono, monospace" '
        'font-size="12">use arrows below to navigate</text>'
    )
    return _svg_wrap(body, W, H)

@app.route("/api/cards/shop")
def card_shop():
    """Shop card (820xvariable). Reads SHOP_ITEMS from config — no DB needed."""
    try:
        from utils.economy_jobs import SHOP_ITEMS
    except ImportError:
        SHOP_ITEMS = {}
    category = request.args.get("cat", "all")
    accent, bg_top, bg_bot = "FFC45C", "261A16", "120C0A"

    items = list(SHOP_ITEMS.values())
    if category and category != "all":
        items = [it for it in items if it.get("category") == category]
    cat_label = category.title() if category and category != "all" else "All Items"

    W = 820
    row_h = 52
    n = len(items)
    H = 120 + n * row_h + 40
    H = min(H, 1200)

    rows_svg = ""
    for i, item in enumerate(items):
        y = 120 + i * row_h
        name_s = _safe(str(item.get("name", "Unknown"))[:30])
        price = _int_param(item.get("price"))
        emoji = _safe(str(item.get("emoji", "\U0001f4e6"))[:8])
        bg_fill = "rgba(50,36,30,0.9)" if i % 2 == 0 else "rgba(40,28,22,0.9)"
        rows_svg += (
            '<rect x="36" y="' + str(y) + '" width="' + str(W - 72) + '" height="' + str(row_h - 4) + '" rx="12" '
            'fill="' + bg_fill + '" stroke="rgba(110,78,50,0.5)" stroke-width="1"/>'
            '<text x="56" y="' + str(y + 30) + '" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
            'font-size="15" font-weight="600">' + emoji + ' ' + name_s + '</text>'
            '<text x="' + str(W - 56) + '" y="' + str(y + 30) + '" text-anchor="end" fill="#' + accent + '" '
            'font-family="Space Mono, monospace" font-size="14" font-weight="700">' + _format_num(price) + '</text>'
        )

    # Try to get user balance if user_id provided
    balance = _int_param(request.args.get("balance"))
    bal_text = (
        '<text x="' + str(W - 36) + '" y="48" text-anchor="end" fill="#C8BBA8" '
        'font-family="Space Mono, monospace" font-size="11">BALANCE</text>'
        '<text x="' + str(W - 36) + '" y="72" text-anchor="end" fill="#' + accent + '" '
        'font-family="Plus Jakarta Sans, sans-serif" font-size="22" font-weight="700">'
        + _format_num(balance) + '</text>'
    ) if balance else ""

    body = (
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#' + bg_top + '"/>'
        '<stop offset="100%" stop-color="#' + bg_bot + '"/>'
        '</linearGradient></defs>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="url(#bg)"/>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="none" '
        'stroke="#' + accent + '" stroke-width="2" opacity="0.6"/>'
        '<text x="36" y="48" fill="#' + accent + '" font-family="Space Mono, monospace" '
        'font-size="11" font-weight="700">SHOP &#8212; ' + cat_label + '</text>'
        '<text x="36" y="78" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="28" font-weight="700">Caf&#233; Boutique</text>'
        + bal_text +
        '<line x1="36" y1="96" x2="' + str(W - 36) + '" y2="96" stroke="rgba(110,78,50,0.5)" stroke-width="1"/>'
        + rows_svg +
        '<text x="' + str(W - 36) + '" y="' + str(H - 16) + '" text-anchor="end" fill="#8C918E" '
        'font-family="Space Mono, monospace" font-size="10">' + str(n) + ' ITEMS</text>'
    )
    return _svg_wrap(body, W, H)

@app.route("/api/cards/economy")
def card_economy():
    """Economy balance card (820x380). Queries economy_users from DB."""
    user_id = _int_param(request.args.get("user"))
    row = _get_user_economy(user_id)
    name = f"User {user_id}"
    balance = 0
    bank = 0
    job = "Unemployed"
    daily_streak = 0
    level = 0
    if row:
        balance = int(row.get("balance", 0))
        bank = int(row.get("bank", 0))
        job = str(row.get("job", "barista"))
        daily_streak = int(row.get("daily_streak", 0))
        level = int(row.get("level", 0))
        # Resolve name from Discord
        try:
            if _discord_bot:
                member = _discord_bot.get_user(user_id)
                if member:
                    name = member.display_name
        except Exception:
            pass

    net_worth = balance + bank
    accent, bg_top, bg_bot = "FFC45C", "261A16", "120C0A"
    W, H = 820, 380

    body = (
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#' + bg_top + '"/>'
        '<stop offset="100%" stop-color="#' + bg_bot + '"/>'
        '</linearGradient></defs>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="url(#bg)"/>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="none" '
        'stroke="#' + accent + '" stroke-width="2" opacity="0.6"/>'
        '<text x="168" y="70" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="28" font-weight="700">' + _safe(name[:25]) + '</text>'
        '<text x="168" y="94" fill="#C8BBA8" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="14" font-weight="500">' + _safe(job) + ' &#183; Level ' + str(level) + '</text>'
        '<rect x="36" y="120" width="' + str(W - 72) + '" height="72" rx="16" '
        'fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.8)" stroke-width="1.5"/>'
        '<text x="56" y="145" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">CASH</text>'
        '<text x="56" y="176" fill="#' + accent + '" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="24" font-weight="700">' + _format_num(balance) + '</text>'
        '<text x="' + str(W // 3 + 26) + '" y="145" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">BANK</text>'
        '<text x="' + str(W // 3 + 26) + '" y="176" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="24" font-weight="700">' + _format_num(bank) + '</text>'
        '<text x="' + str(2 * W // 3 + 16) + '" y="145" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">NET WORTH</text>'
        '<text x="' + str(2 * W // 3 + 16) + '" y="176" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="24" font-weight="700">' + _format_num(net_worth) + '</text>'
        '<rect x="36" y="212" width="' + str(W - 72) + '" height="52" rx="16" '
        'fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.8)" stroke-width="1.5"/>'
        '<text x="56" y="237" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">DAILY STREAK</text>'
        '<text x="56" y="256" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="20" font-weight="700">' + str(daily_streak) + ' days</text>'
        '<text x="' + str(W - 36) + '" y="' + str(H - 20) + '" text-anchor="end" fill="#8C918E" '
        'font-family="Space Mono, monospace" font-size="10">CAFE ECONOMY</text>'
    )
    return _svg_wrap(body, W, H)

@app.route("/api/cards/daily")
def card_daily():
    """Daily reward card (820x280). Queries economy_users from DB."""
    user_id = _int_param(request.args.get("user"))
    reward = _int_param(request.args.get("reward"))
    row = _get_user_economy(user_id)
    name = f"User {user_id}"
    balance = 0
    streak = 0
    job = "barista"
    if row:
        balance = int(row.get("balance", 0))
        streak = int(row.get("daily_streak", 0))
        job = str(row.get("job", "barista"))
        try:
            if _discord_bot:
                member = _discord_bot.get_user(user_id)
                if member:
                    name = member.display_name
        except Exception:
            pass

    accent, bg_top, bg_bot = "FFC45C", "261A16", "120C0A"
    W, H = 820, 280

    body = (
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#' + bg_top + '"/>'
        '<stop offset="100%" stop-color="#' + bg_bot + '"/>'
        '</linearGradient></defs>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="url(#bg)"/>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="none" '
        'stroke="#' + accent + '" stroke-width="2" opacity="0.6"/>'
        '<text x="36" y="48" fill="#' + accent + '" font-family="Space Mono, monospace" '
        'font-size="12" font-weight="700">DAILY REWARD</text>'
        '<text x="36" y="80" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="26" font-weight="700">' + _safe(name[:25]) + '</text>'
        '<text x="36" y="110" fill="#C8BBA8" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="14">' + _safe(job) + ' &#183; Streak: ' + str(streak) + ' days</text>'
        '<rect x="36" y="140" width="' + str(W // 2 - 52) + '" height="80" rx="16" '
        'fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.8)" stroke-width="1.5"/>'
        '<text x="56" y="170" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">REWARD</text>'
        '<text x="56" y="210" fill="#76E29C" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="32" font-weight="700">+' + _format_num(reward) + '</text>'
        '<rect x="' + str(W // 2 + 16) + '" y="140" width="' + str(W // 2 - 52) + '" height="80" rx="16" '
        'fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.8)" stroke-width="1.5"/>'
        '<text x="' + str(W // 2 + 36) + '" y="170" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">NEW BALANCE</text>'
        '<text x="' + str(W // 2 + 36) + '" y="210" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="32" font-weight="700">' + _format_num(balance) + '</text>'
        '<text x="' + str(W - 36) + '" y="' + str(H - 20) + '" text-anchor="end" fill="#8C918E" '
        'font-family="Space Mono, monospace" font-size="10">CAFE ECONOMY</text>'
    )
    return _svg_wrap(body, W, H)

@app.route("/api/cards/work")
def card_work():
    """Work reward card (820x300). Queries economy_users from DB."""
    user_id = _int_param(request.args.get("user"))
    reward = _int_param(request.args.get("reward"))
    message = request.args.get("msg", "Good work!")
    row = _get_user_economy(user_id)
    name = f"User {user_id}"
    balance = 0
    job = "barista"
    if row:
        balance = int(row.get("balance", 0))
        job = str(row.get("job", "barista"))
        try:
            if _discord_bot:
                member = _discord_bot.get_user(user_id)
                if member:
                    name = member.display_name
        except Exception:
            pass

    accent, bg_top, bg_bot = "FFC45C", "261A16", "120C0A"
    W, H = 820, 300

    body = (
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#' + bg_top + '"/>'
        '<stop offset="100%" stop-color="#' + bg_bot + '"/>'
        '</linearGradient></defs>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="url(#bg)"/>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="none" '
        'stroke="#' + accent + '" stroke-width="2" opacity="0.6"/>'
        '<text x="36" y="48" fill="#' + accent + '" font-family="Space Mono, monospace" '
        'font-size="12" font-weight="700">WORK SHIFT</text>'
        '<text x="36" y="80" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="26" font-weight="700">' + _safe(name[:25]) + '</text>'
        '<text x="36" y="106" fill="#C8BBA8" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="14">' + _safe(job) + '</text>'
        '<rect x="36" y="130" width="' + str(W // 2 - 52) + '" height="80" rx="16" '
        'fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.8)" stroke-width="1.5"/>'
        '<text x="56" y="160" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">EARNED</text>'
        '<text x="56" y="200" fill="#76E29C" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="32" font-weight="700">+' + _format_num(reward) + '</text>'
        '<rect x="' + str(W // 2 + 16) + '" y="130" width="' + str(W // 2 - 52) + '" height="80" rx="16" '
        'fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.8)" stroke-width="1.5"/>'
        '<text x="' + str(W // 2 + 36) + '" y="160" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">NEW BALANCE</text>'
        '<text x="' + str(W // 2 + 36) + '" y="200" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="32" font-weight="700">' + _format_num(balance) + '</text>'
        '<text x="36" y="240" fill="#C8BBA8" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="13">' + _safe(message[:60]) + '</text>'
        '<text x="' + str(W - 36) + '" y="' + str(H - 20) + '" text-anchor="end" fill="#8C918E" '
        'font-family="Space Mono, monospace" font-size="10">CAFE ECONOMY</text>'
    )
    return _svg_wrap(body, W, H)

@app.route("/api/cards/inventory")
def card_inventory():
    """Inventory card (820xvariable). Queries economy_users from DB."""
    user_id = _int_param(request.args.get("user"))
    row = _get_user_economy(user_id)
    name = f"User {user_id}"
    balance = 0
    inventory = {}
    if row:
        balance = int(row.get("balance", 0))
        raw_inv = row.get("inventory", "{}")
        try:
            import json
            inventory = json.loads(raw_inv) if isinstance(raw_inv, str) else (raw_inv or {})
        except Exception:
            inventory = {}
        try:
            if _discord_bot:
                member = _discord_bot.get_user(user_id)
                if member:
                    name = member.display_name
        except Exception:
            pass

    # Import shop items for emoji lookup
    try:
        from utils.economy_jobs import get_item
    except ImportError:
        def get_item(iid): return None

    accent, bg_top, bg_bot = "FFC45C", "261A16", "120C0A"
    W = 820
    row_h = 44

    # Build sections grouped by category
    groups = {"consumable": [], "upgrade": [], "collectible": [], "other": []}
    for iid, count in sorted(inventory.items()):
        item = get_item(iid)
        if not item:
            groups["other"].append({"emoji": "\U0001f4e6", "name": iid, "count": int(count)})
        else:
            groups[item.get("category", "other")].append({
                "emoji": str(item.get("emoji", "\U0001f4e6")),
                "name": str(item.get("name", iid)),
                "count": int(count),
            })

    labels = {
        "consumable": "\U0001f9ea Consumables",
        "upgrade": "\U0001f3e6 Upgrades",
        "collectible": "\U0001f396\ufe0f Collectibles",
        "other": "\U0001f4e6 Misc",
    }

    sections = [(labels[cat], items) for cat, items in groups.items() if items]
    total_items = sum(len(items) for _, items in sections)
    H = 120 + len(sections) * 56 + total_items * row_h + 40
    H = min(H, 1200)

    # Letter avatar
    letter = name[0].upper() if name else "U"
    av_elem = (
        '<clipPath id="avclip"><circle cx="48" cy="52" r="28"/></clipPath>'
        '<circle cx="48" cy="52" r="28" fill="#6E4E32"/>'
        '<text x="48" y="58" text-anchor="middle" fill="#F5E8D2" '
        'font-family="Plus Jakarta Sans, sans-serif" font-size="18" font-weight="700">' + letter + '</text>'
    )

    sections_svg = ""
    cur_y = 120
    for label, items in sections:
        sections_svg += (
            '<text x="36" y="' + str(cur_y + 16) + '" fill="#C8BBA8" '
            'font-family="Space Mono, monospace" font-size="12" font-weight="700">' + label + '</text>'
            '<line x1="36" y1="' + str(cur_y + 24) + '" x2="' + str(W - 36) + '" y2="' + str(cur_y + 24) + '" '
            'stroke="rgba(110,78,50,0.4)" stroke-width="1"/>'
        )
        cur_y += 36
        for j, item in enumerate(items):
            iy = cur_y + j * row_h
            bg_fill = "rgba(50,36,30,0.9)" if j % 2 == 0 else "rgba(40,28,22,0.9)"
            sections_svg += (
                '<rect x="36" y="' + str(iy) + '" width="' + str(W - 72) + '" height="' + str(row_h - 4) + '" rx="10" '
                'fill="' + bg_fill + '"/>'
                '<text x="56" y="' + str(iy + 26) + '" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
                'font-size="13" font-weight="600">' + item["emoji"] + ' ' + _safe(item["name"][:25]) + '</text>'
                '<text x="' + str(W - 56) + '" y="' + str(iy + 26) + '" text-anchor="end" fill="#C8BBA8" '
                'font-family="Space Mono, monospace" font-size="14" font-weight="700">&#215;' + str(item["count"]) + '</text>'
            )
        cur_y += len(items) * row_h + 12

    body = (
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#' + bg_top + '"/>'
        '<stop offset="100%" stop-color="#' + bg_bot + '"/>'
        '</linearGradient></defs>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="url(#bg)"/>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="none" '
        'stroke="#' + accent + '" stroke-width="2" opacity="0.6"/>'
        + av_elem +
        '<circle cx="48" cy="52" r="31" fill="none" stroke="#' + accent + '" stroke-width="2"/>'
        '<text x="88" y="46" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="22" font-weight="700">' + _safe(name[:25]) + '</text>'
        '<text x="88" y="66" fill="#C8BBA8" font-family="Space Mono, monospace" '
        'font-size="11">BALANCE: ' + _format_num(balance) + '</text>'
        + sections_svg +
        '<text x="' + str(W - 36) + '" y="' + str(H - 16) + '" text-anchor="end" fill="#8C918E" '
        'font-family="Space Mono, monospace" font-size="10">' + str(total_items) + ' ITEMS</text>'
    )
    return _svg_wrap(body, W, H)

@app.route("/api/cards/coinflip")
def card_coinflip():
    """Coinflip result card (820x300). Queries economy_users from DB."""
    user_id = _int_param(request.args.get("user"))
    call = _safe(request.args.get("call", "heads"))
    result = _safe(request.args.get("result", "heads"))
    won = request.args.get("won", "0") == "1"
    amount = _int_param(request.args.get("amount"))
    payout = _int_param(request.args.get("payout"))

    row = _get_user_economy(user_id)
    name = f"User {user_id}"
    balance = 0
    if row:
        balance = int(row.get("balance", 0))
        try:
            if _discord_bot:
                member = _discord_bot.get_user(user_id)
                if member:
                    name = member.display_name
        except Exception:
            pass

    accent, bg_top, bg_bot = "FFC45C", "261A16", "120C0A"
    W, H = 820, 300
    rc = "76E29C" if won else "F46E7C"
    rt = "WIN" if won else "LOSS"

    body = (
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#' + bg_top + '"/>'
        '<stop offset="100%" stop-color="#' + bg_bot + '"/>'
        '</linearGradient></defs>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="url(#bg)"/>'
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="26" fill="none" '
        'stroke="#' + accent + '" stroke-width="2" opacity="0.6"/>'
        '<text x="36" y="40" fill="#' + rc + '" font-family="Space Mono, monospace" '
        'font-size="12" font-weight="700">COINFLIP &#8212; ' + rt + '</text>'
        '<text x="36" y="76" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="22" font-weight="700">' + _safe(name[:25]) + '</text>'
        '<text x="36" y="98" fill="#C8BBA8" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="13">Called ' + call + ' &#183; Got ' + result + '</text>'
        '<rect x="36" y="130" width="' + str(W // 2 - 52) + '" height="90" rx="16" '
        'fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.8)" stroke-width="1.5"/>'
        '<text x="56" y="160" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">'
        + ("PAYOUT" if won else "BET") + '</text>'
        '<text x="56" y="202" fill="#' + rc + '" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="32" font-weight="700">' + _format_num(payout if won else amount) + '</text>'
        '<rect x="' + str(W // 2 + 16) + '" y="130" width="' + str(W // 2 - 52) + '" height="90" rx="16" '
        'fill="rgba(50,36,30,0.9)" stroke="rgba(110,78,50,0.8)" stroke-width="1.5"/>'
        '<text x="' + str(W // 2 + 36) + '" y="160" fill="#C8BBA8" font-family="Space Mono, monospace" font-size="11">BALANCE</text>'
        '<text x="' + str(W // 2 + 36) + '" y="202" fill="#F5E8D2" font-family="Plus Jakarta Sans, sans-serif" '
        'font-size="32" font-weight="700">' + _format_num(balance) + '</text>'
        '<text x="' + str(W - 36) + '" y="' + str(H - 20) + '" text-anchor="end" fill="#8C918E" '
        'font-family="Space Mono, monospace" font-size="10">CAFE CASINO</text>'
    )
    return _svg_wrap(body, W, H)
