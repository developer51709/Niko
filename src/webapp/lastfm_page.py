"""The standalone page the Last.fm linking callback lands on.

Linking runs in the browser (last.fm's web auth sends the member back to this
site), so the answer has to be a page rather than a JSON body. Like the captcha
page it is deliberately outside the React site: it is one small document with
inline CSS, no scripts and no dependencies, using the site's own tokens so it
does not flash a white rectangle between Discord and Niko. The top border takes
the Last.fm red the cog's cards use, so the flow, the card and the website read
as one thing.
"""

from html import escape

from config import links

# The site's tokens (web/src/styles.css) plus the Last.fm accent from
# utils.image.lastfm_card. Restated because this page ships without the
# stylesheet: canvas #050607, surface #111316, ink #f4f5f7, muted #b4bac3,
# dim #858c96, line #2d3035, Last.fm #d8645c.
_STYLES = """
  *, *::before, *::after { box-sizing: border-box; }
  html { color-scheme: dark; }
  body { margin: 0; padding: 40px 16px 48px; background: #050607; color: #f4f5f7;
         font: 15px/1.55 "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  main { width: 100%; max-width: 420px; margin: 0 auto; padding: 26px 24px 24px;
         background: #111316; border: 1px solid #2d3035; border-top: 2px solid #d8645c;
         border-radius: 8px; }
  .mark { margin: 0 0 18px; color: #858c96; font-size: 11px; font-weight: 700;
          letter-spacing: 0.14em; text-transform: uppercase; }
  .mark b { color: #d8645c; }
  h1 { margin: 0 0 8px; font-size: 22px; line-height: 1.25; letter-spacing: -0.02em; }
  p { margin: 0 0 14px; color: #b4bac3; font-size: 13px; }
  .handle { display: inline-block; margin: 2px 0 16px; padding: 5px 12px; border-radius: 999px;
            border: 1px solid rgba(216, 100, 92, 0.45); background: rgba(216, 100, 92, 0.12);
            color: #e8928a; font-size: 13px; font-weight: 600; }
  .error { margin: 0 0 14px; padding: 10px 12px; border: 1px solid rgba(237, 66, 69, 0.4);
           border-radius: 6px; background: rgba(237, 66, 69, 0.1); color: #ffb4b0; font-size: 13px; }
  a.button { display: block; margin-top: 18px; padding: 11px 16px; border-radius: 6px;
             background: #aab1ba; color: #111316; font-weight: 700; text-align: center;
             text-decoration: none; }
  a.button:hover { background: #d5d9df; }
  .hint { margin: 16px 0 0; color: #858c96; font-size: 11px; }
  .hint code { padding: 1px 5px; border-radius: 4px; background: #191b1f; color: #b4bac3; }
"""


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
<p class="mark">NIKO <b>·</b> LAST.FM</p>
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
<p>Niko now reads your scrobbles, from any player and any device — not just
Spotify on Discord.</p>
<span class="handle">@{escape(username)}</span>
<p class="hint">Use <code>/fm nowplaying</code> for what is playing, <code>/fm</code> for your
library, and <code>/fm unlink</code> to disconnect at any time.</p>
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
<p class="hint">Open <code>/fm link</code> in Discord and press the connect button again —
the link last.fm sends back expires after a few minutes.</p>
<a class="button" href="{escape(links.WEBSITE)}">Back to Niko</a>
""",
    )
