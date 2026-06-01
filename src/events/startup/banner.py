"""
Startup — ASCII banner printer.
"""

import re

import colorama

_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')


def _vis(s: str) -> int:
    return len(_ANSI_RE.sub('', s))


def print_banner(bot, guild_count: int = 0):
    R  = colorama.Style.RESET_ALL
    M  = colorama.Fore.MAGENTA
    BR = colorama.Style.BRIGHT
    C  = colorama.Fore.CYAN
    W  = colorama.Fore.WHITE
    DM = colorama.Style.DIM

    IW = 55

    def bline(content: str = "") -> str:
        pad = max(0, IW - _vis(content))
        return f"{M}{BR}│{R}{content}{' ' * pad}{M}{BR}│{R}"

    def div(left: str = "├", right: str = "┤") -> str:
        return f"{M}{BR}{left}{'─' * IW}{right}{R}"

    art = [
        f"  {W}{BR} ███╗   ██╗ ██╗██╗  ██╗  ██████╗ {R}",
        f"  {W}{BR} ████╗  ██║ ██║██║ ██╔╝ ██╔═══██╗{R}",
        f"  {W}{BR} ██╔██╗ ██║ ██║█████╔╝  ██║   ██║{R}",
        f"  {W}{BR} ██║╚██╗██║ ██║██╔═██╗  ██║   ██║{R}",
        f"  {W}{BR} ██║ ╚████║ ██║██║  ██╗ ╚██████╔╝{R}",
        f"  {W}{BR} ╚═╝  ╚═══╝ ╚═╝╚═╝  ╚═╝  ╚═════╝ {R}",
    ]

    def irow(lk: str, lv: str, rk: str = "", rv: str = "") -> str:
        left = f"  {DM}{lk:<7}{R}  {W}{lv}{R}"
        if not rk:
            return bline(left)
        gap   = max(2, 30 - _vis(left))
        right = f"{' ' * gap}{DM}{rk:<8}{R}  {W}{rv}{R}"
        return bline(left + right)

    guild_str  = str(guild_count)
    user_count = f"{len(bot.users):,}"

    try:
        from utils.ai.reply import AI_MODE as ai_mode
    except Exception:
        ai_mode = "OPENAI"

    rows = [
        "",
        div("╭", "╮"),
        bline(),
        *[bline(a) for a in art],
        bline(),
        bline(f"  {C}a cozy cafe AI companion for Discord{R}"),
        bline(f"  {DM}bilingual  ·  modular  ·  33+ cogs{R}"),
        bline(),
        div(),
        bline(),
        irow("bot",     str(bot.user),  "servers", guild_str),
        irow("version", "1.0",          "users",   user_count),
        irow("model",   ai_mode,        "author",  "@n.y.x.e.n"),
        bline(),
        div("╰", "╯"),
        "",
    ]

    print("\n".join(rows))
