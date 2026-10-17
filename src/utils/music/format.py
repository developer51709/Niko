"""
Music System — formatting helpers (duration, progress bar, source colour).
"""

import discord
import wavelink

from utils.music.constants import SOURCE_COLOURS


def _fmt_dur(ms: int) -> str:
    if ms is None or ms < 0:
        return "0:00"
    s = ms // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _progress_bar(pos_ms: int, total_ms: int, width: int = 14) -> str:
    pct    = min(pos_ms / max(total_ms, 1), 1.0)
    filled = round(pct * width)
    bar    = "█" * filled + "░" * (width - filled)
    return f"`[{bar}]` {_fmt_dur(pos_ms)} / {_fmt_dur(total_ms)}"


def _source_colour(track: wavelink.Playable) -> discord.Colour:
    src = (track.source or "").lower()
    if "youtube" in src:
        return SOURCE_COLOURS["youtube"]
    if "soundcloud" in src:
        return SOURCE_COLOURS["soundcloud"]
    return SOURCE_COLOURS["default"]