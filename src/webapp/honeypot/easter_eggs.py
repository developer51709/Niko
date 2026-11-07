"""Terminal animations served from the honeypot's fake service hosts.

The decoy files point connection strings and endpoints at hosts under the
public domain — ``db``, ``read``, ``cache``, ``nyan``, ``vault`` and
``queue``. None of
them is a real service: a request to one is answered with a short ANSI
animation, a nyan cat for the data stores and a rickroll for the secret store
and the queue. A crawler that follows a fake password gets a few seconds of
animation instead of a login prompt, and anything it records is noise.

The nyan animation is a port of klange/nyancat's frame data and renderer (see
``nyancat.py``); the rickroll is drawn here. Only colour and cursor escapes
are used, so the frames render in any terminal that runs ``curl``; on the
finite decoy streams the cursor is restored after the last frame, while the
fun host hides nothing because Ctrl+C ends it without a closing frame. Nothing
here reads configuration or the network, and the frames are the same every
time.
"""

from __future__ import annotations

from typing import Iterator

from . import nyancat

#: Seconds between frames in the streamed response.
FRAME_DELAY = 0.09

#: How many animated frames each egg runs for, before the closing card.
FRAME_COUNT = {"nyan": nyancat.FRAME_COUNT, "rickroll": 42}

#: First host label -> the animation it plays. The hosts themselves are built
#: in ``values.py``; matching the label keeps a staging or preview deployment
#: working under its own domain without any extra configuration.
EGG_LABELS = {
    "db": "nyan",
    "read": "nyan",
    "cache": "nyan",
    "nyan": "nyan",
    "vault": "rickroll",
    "queue": "rickroll",
}

#: Hosts that are only a joke: unlike the decoy hosts, nothing here pretends to
#: be a service and the closing card never mentions fake credentials.
PLAY_HOSTS = {"nyan", "nyancat"}

_CLEAR = "\x1b[2J"
_HOME = "\x1b[H"
_HIDE = "\x1b[?25l"
_SHOW = "\x1b[?25h"
_RESET = "\x1b[0m"
_BOLD = "\x1b[1m"
_DIM = "\x1b[2m"
_PINK = "\x1b[1;95m"
_YELLOW = "\x1b[1;93m"
_CYAN = "\x1b[1;96m"

_DANCER = (
    (" \\o/ ", "  |  ", " / \\ "),
    (" \\o/ ", "  |  ", "  |  "),
    ("  o/ ", " /|  ", " / \\ "),
    (" \\o  ", "  |\\ ", " / \\ "),
)

_LYRICS = (
    "Never gonna give you up",
    "Never gonna let you down",
    "Never gonna run around and desert you",
    "Never gonna make you cry",
    "Never gonna say goodbye",
    "Never gonna tell a lie and hurt you",
)

_TITLE = "N E V E R   G O N N A   G I V E   U P"


def _head(frame: int) -> str:
    """Clear once, then redraw in place so the animation does not flicker."""
    return _CLEAR + _HIDE if frame == 0 else _HOME


def _rickroll_frames(count: int, host: str) -> Iterator[str]:
    inner = len(_TITLE) + 4
    top = "  ╔" + "═" * inner + "╗"
    middle = "  ║  " + _TITLE + "  ║"
    bottom = "  ╚" + "═" * inner + "╝"
    for frame in range(count):
        left = 8 + (frame // 2) % 6
        note = (frame * 5) % 44
        dancer = _DANCER[frame % len(_DANCER)]
        current = (frame // 8) % len(_LYRICS)
        window = [
            _LYRICS[(current + offset) % len(_LYRICS)]
            for offset in (-1, 0, 1)
        ]
        filled = round(24 * (frame + 1) / count)
        bar = "█" * filled + "░" * (24 - filled)
        percent = int(100 * (frame + 1) / count)
        yield (
            f"{_head(frame)}"
            f"  {' ' * note}{_YELLOW}♪{_RESET}\n\n"
            f"{top}\n{middle}\n{bottom}\n\n"
            + "\n".join(f"{' ' * left}{line}" for line in dancer)
            + f"\n\n  {_DIM}{window[0]}{_RESET}\n"
            f"  {_BOLD}{_YELLOW}▶ {window[1]}{_RESET}\n"
            f"  {_DIM}{window[2]}{_RESET}\n\n"
            f"  {_CYAN}{bar}{_RESET}  {percent}%"
            f"{_DIM}  {host or 'vault'}{_RESET}\n"
        )


def closing(kind: str, host: str = "", decoy: bool = True) -> str:
    """The final card, which explains the joke and restores the cursor."""
    if kind == "nyan":
        headline = f"{_PINK}{_BOLD}NYAN!{_RESET}"
    else:
        headline = f"{_YELLOW}{_BOLD}You just got rickrolled.{_RESET}"
    name = host or "this host"
    if not decoy:
        return (
            f"{_CLEAR}{_HOME}{_SHOW}{headline}\n\n"
            f"  You found the easter egg. {name} is just for fun — there\n"
            "  is nothing here but the animation.\n\n"
            f"  {_DIM}Animation ported from "
            f"https://github.com/klange/nyancat{_RESET}\n\n"
        )
    return (
        f"{_CLEAR}{_HOME}{_SHOW}{headline}\n\n"
        f"  {name} is a decoy host from Niko's honeypot.\n"
        "  Nothing that pointed you here is real: every credential in those\n"
        "  files is generated, and this server has no data behind it.\n\n"
        f"  {_DIM}https://github.com/developer51709/Niko{_RESET}\n\n"
    )


def frames(
    kind: str, host: str = "", decoy: bool = True
) -> Iterator[tuple[float, str]]:
    """Yield ``(delay, frame)`` pairs for one animation.

    A decoy host plays a fixed number of frames and then the closing card. The
    fun host (``nyan.``) instead runs the intro and then the animation forever:
    the visitor stops it with Ctrl+C, exactly like the original program, which
    closes the request and ends the generator.
    """
    if kind == "nyan":
        if decoy:
            for frame in nyancat.frames(host, intro_screen=False):
                yield frame
            yield FRAME_DELAY, closing(kind, host, decoy)
        else:
            yield from nyancat.frames(host, endless=True, hide_cursor=False)
        return
    count = FRAME_COUNT.get(kind)
    if count is None:
        raise ValueError(f"unknown easter egg: {kind!r}")
    for frame in _rickroll_frames(count, host):
        yield FRAME_DELAY, frame
    yield FRAME_DELAY, closing(kind, host, decoy)
