"""The standalone page the Last.fm linking callback lands on.

Linking runs in the browser (last.fm's web auth sends the member back to this
site), so the answer has to be a page rather than a JSON body. Like the captcha
page it is deliberately outside the React site: it is one small document with
inline CSS, no scripts and no dependencies, using the site's own tokens so it
does not flash a white rectangle between Discord and Niko.

The masthead is the card's masthead: the Last.fm lockup the ``/fm`` cards draw,
on its own, at the same size. Everything else is a small, centred card — a
heading, one sentence, the handle, a hint and a single button — so the page
reads the same way the cards do without decorating past the point of saying
whether the account was linked.
"""

from html import escape
from pathlib import Path

from config import links

# The site's tokens (web/src/styles.css) plus the Last.fm accent from
# utils.image.lastfm_card. Restated because this page ships without the
# stylesheet: canvas #050607, surface #111316, ink #f4f5f7, muted #b4bac3,
# dim #858c96, line #2d3035, Last.fm #d8645c.
_STYLES = """
  *, *::before, *::after { box-sizing: border-box; }
  html { color-scheme: dark; }
  body { margin: 0; min-height: 100vh; display: grid; place-items: center;
         padding: 24px 16px; background: #050607; color: #f4f5f7;
         font: 15px/1.55 "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  main { width: 100%; max-width: 400px; padding: 28px; background: #111316;
         border: 1px solid #2d3035; border-radius: 12px; }
  .masthead { margin: 0 0 22px; }
  .brand { display: block; height: 20px; width: auto; color: #f4f5f7; }
  .brand-text { font-size: 17px; font-weight: 800; letter-spacing: -0.03em; }
  h1 { margin: 0; font-size: 20px; line-height: 1.3; letter-spacing: -0.02em; }
  p { margin: 8px 0 0; color: #b4bac3; font-size: 13px; }
  .handle { margin: 12px 0 0; color: #858c96; font-size: 13px; }
  .handle b { color: #e8928a; font-weight: 600; }
  .error { margin: 10px 0 0; color: #ffb4b0; font-size: 14px; font-weight: 500; }
  a.button { display: block; margin-top: 24px; padding: 10px 14px; border-radius: 6px;
             background: #f4f5f7; color: #111316; font-size: 13px; font-weight: 700;
             text-align: center; text-decoration: none; }
  a.button:hover { background: #d5d9df; }
  .hint { margin: 18px 0 0; color: #858c96; font-size: 11px; line-height: 1.7; }
  .hint code { padding: 1px 4px; border-radius: 4px; background: #191b1f;
               color: #b4bac3; letter-spacing: 0.01em; }
"""

# ── Brand lockup ───────────────────────────────────────────────────────────
#: The same file ``utils.image.lastfm_card`` draws: the official lockup, which
#: already carries the wordmark. Read from the site's asset rather than a copy,
#: so the page and the cards cannot drift into two different marks.
_LOGO_ASSETS = (
    Path(__file__).resolve().parents[2] / "web" / "public" / "assets" / "brand" / "last-fm.svg",
    Path(__file__).resolve().parents[1] / "website" / "dist" / "assets" / "brand" / "last-fm.svg",
)
#: The lockup's content box in the file's own units, measured from its drawn
#: paths (``matrix(.507925 0 0 .507925 100 154.456)`` around a 360×91.088
#: drawing). The file's 560×400 viewBox is mostly margin, and the cards crop to
#: the paths too — using it as-is would float the mark in the middle of a band
#: of empty space.
_LOGO_VIEWBOX = "100 154.456 360 91.088"
_LOGO_FILL = 'fill="#d51007"'
_LOGO_MARKUP: str | None = None


def _logo() -> str:
    """The site's Last.fm lockup, inline and in the page's own ink.

    Inline rather than an ``<img>``: the file is brand red, and the red that
    reads on the card's canvas does not read at 24px on graphite — the cards
    fill the lockup in their ink for exactly that reason, so this does too.
    """
    global _LOGO_MARKUP
    if _LOGO_MARKUP is not None:
        return _LOGO_MARKUP

    source = ""
    for candidate in _LOGO_ASSETS:
        try:
            source = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        break

    inner = ""
    start, end = source.find(">"), source.rfind("</svg>")
    if start != -1 and end > start:
        inner = source[start + 1:end].replace(_LOGO_FILL, 'fill="currentColor"').strip()

    if inner:
        _LOGO_MARKUP = (
            f'<svg class="brand" viewBox="{_LOGO_VIEWBOX}" role="img" aria-label="Last.fm">'
            f"{inner}</svg>"
        )
    else:
        # An install without the site asset still says whose account this is.
        _LOGO_MARKUP = '<span class="brand brand-text">Last.fm</span>'
    return _LOGO_MARKUP


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{escape(title)} · Niko</title>
<style>{_STYLES}</style>
</head>
<body>
<main>
<div class="masthead">{_logo()}</div>
{body}
</main>
</body>
</html>"""


def linked_page(username: str) -> str:
    """The confirmation shown after a member approves the application."""
    return _page(
        "Last.fm connected",
        f"""
<h1>Last.fm connected</h1>
<p>Niko reads your scrobbles straight from Last.fm — any player, any device.</p>
<p class="handle">Connected as <b>@{escape(username)}</b></p>
<p class="hint">Use <code>/fm</code> for your library, or <code>/fm unlink</code> to disconnect.</p>
<a class="button" href="{escape(links.WEBSITE)}">Back to Niko</a>
""",
    )


def error_page(message: str, *, title: str = "Last.fm was not linked") -> str:
    """A readable failure, with the retry path the member should take."""
    return _page(
        title,
        f"""
<h1>{escape(title)}</h1>
<p class="error">{escape(message)}</p>
<p class="hint">Open <code>/fm link</code> in Discord and press connect again — the link
expires after a few minutes.</p>
<a class="button" href="{escape(links.WEBSITE)}">Back to Niko</a>
""",
    )
