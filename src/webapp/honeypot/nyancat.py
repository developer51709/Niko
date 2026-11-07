"""A Python port of klange/nyancat's terminal renderer.

Upstream is a small C program (and telnet server) that draws the classic Nyan
Cat from twelve 64x64 character frames in xterm-256 colours. This deployment is
Python-only and ships its updates as Python files, so the frames are vendored
(``nyancat_frames.py``) and the render loop is ported here rather than compiled
to a binary: the same frames, palette, 40x23 crop, 90 ms cadence and the
"You have nyaned for N seconds!" counter.

See ``LICENSE-nyancat.txt`` for the upstream NCSA/UIUC licence.
"""

from __future__ import annotations

import time
from typing import Iterator

from .nyancat_frames import FRAMES

#: Upstream's default frame delay, and how many frames a decoy host plays.
FRAME_DELAY = 0.09
FRAME_COUNT = 60

#: Upstream's intro screen: five countdown ticks 400 ms apart, then the loop.
INTRO_STEPS = 5
INTRO_DELAY = 0.4

#: Upstream's xterm-256 palette (its ``case 1``, for ``TERM=xterm-256color``).
COLORS = {
    ",": "\x1b[48;5;17m",   # blue background
    ".": "\x1b[48;5;231m",  # white stars
    "'": "\x1b[48;5;16m",   # black border
    "@": "\x1b[48;5;230m",  # tan poptart
    "$": "\x1b[48;5;175m",  # pink poptart
    "-": "\x1b[48;5;162m",  # red poptart
    ">": "\x1b[48;5;196m",  # red rainbow
    "&": "\x1b[48;5;214m",  # orange rainbow
    "+": "\x1b[48;5;226m",  # yellow rainbow
    "#": "\x1b[48;5;118m",  # green rainbow
    "=": "\x1b[48;5;33m",   # light blue rainbow
    ";": "\x1b[48;5;19m",   # dark blue rainbow
    "*": "\x1b[48;5;240m",  # gray cat face
    "%": "\x1b[48;5;175m",  # pink cheeks
}

#: Upstream crops the 64x64 frames to the middle 40x23 pixels for an 80x24
#: terminal and writes two spaces per pixel. There is no terminal width to
#: negotiate over HTTP, so this is the size every visitor gets.
MIN_COL, MAX_COL = 12, 52
MIN_ROW, MAX_ROW = 20, 43
PIXEL = "  "
_WIDTH = 80

_COUNTER = "You have nyaned for {seconds} seconds!"

_INTRO = (
    "",
    "                  N Y A N   C A T",
    "                  ─────────────────",
    "",
    "  {host} — an easter egg, nothing more",
    "",
    "  A Python port of klange/nyancat, drawn in xterm-256 colours.",
    "  If the colours look wrong, try:",
    "      TERM=xterm-256color curl {url}",
    "",
    "  This is a one-way HTTP stream, not a telnet server:",
    "      press Ctrl+C to stop",
    "",
    "  Starting in {seconds}...",
)


def _render(frame_index: int, seconds: int) -> str:
    rows = FRAMES[frame_index]
    parts = ["\x1b[H"]
    for y in range(MIN_ROW, MAX_ROW):
        row = rows[y]
        color = ""
        for x in range(MIN_COL, MAX_COL):
            next_color = COLORS[row[x]]
            if next_color != color:
                parts.append(next_color)
                color = next_color
            parts.append(PIXEL)
        parts.append("\n")

    # ``29`` is everything in the counter except the number, as upstream counts
    # it when centring the line.
    padding = (_WIDTH - 29 - len(str(seconds))) // 2
    if padding > 0:
        parts.append(" " * padding)
    parts.append(f"\x1b[1;37m{_COUNTER.format(seconds=seconds)}\x1b[J\x1b[0m")
    return "".join(parts)


def intro(
    host: str = "", hide_cursor: bool = True
) -> Iterator[tuple[float, str]]:
    """Upstream's intro screen, with the countdown animating in place."""
    name = host or "nyan.niko.sryze.cc"
    for step in range(INTRO_STEPS):
        fields = {
            "host": name,
            "url": f"https://{name}/",
            "seconds": INTRO_STEPS - step,
        }
        screen = "\n".join(line.format(**fields) for line in _INTRO)
        yield INTRO_DELAY, "\x1b[H" + screen + "\n"
    # An endless stream has no closing card to restore the cursor, and Ctrl+C
    # disconnects before one could be sent, so only hide it when someone will
    # definitely get ``\x1b[?25h`` at the end.
    yield 0.0, "\x1b[H\x1b[2J" + ("\x1b[?25l" if hide_cursor else "")


def frames(
    host: str = "",
    endless: bool = False,
    count: int = FRAME_COUNT,
    intro_screen: bool = True,
    hide_cursor: bool = True,
) -> Iterator[tuple[float, str]]:
    """Yield ``(delay, frame)`` pairs: the twelve-frame loop, timed like upstream.

    ``endless`` keeps drawing until the client goes away (Ctrl+C closes the
    request), which is how the original program ran.
    """
    if intro_screen:
        yield from intro(host, hide_cursor)
    else:
        yield 0.0, "\x1b[2J" + ("\x1b[?25l" if hide_cursor else "")

    started = time.monotonic()
    index = 0
    while endless or index < count:
        yield FRAME_DELAY, _render(index % len(FRAMES), int(time.monotonic() - started))
        index += 1
