"""The standalone captcha page a member opens from the Verify panel.

Deliberately not part of the React site. It is the one page in the deployment
that shows advertising — hosting is paid for by it — and ad scripts, the site's
navigation, fonts and analytics in front of the challenge would make a two-field
form slower and harder to trust. So this is one small document with inline CSS,
no scripts, no cookies, and no dependencies: a captcha image, a text input, a
button, and the ad slot below the card.

The ad unit comes from AADS (https://aads.com), whose embed is an iframe carrying
a ``data-aa`` attribute; removing that attribute stops the unit being detected,
so the markup is reproduced exactly. ``AADS_AD_UNIT_ID`` holds the unit id and
the slot is omitted entirely when it is unset, which is also what happens in
tests and on staging.
"""

import os
from html import escape

PAGE_TITLE = "Verify you are human"

# AADS's documented banner embed, with the unit id filled in.
_AADS_MARKUP = """<!-- BEGIN AADS AD UNIT {unit} -->
<div id="frame" style="width: 100%; margin: auto; position: relative; z-index: 99998;">
<iframe
data-aa="{unit}"
src="https://acceptable.a-ads.com/{unit}/?size=Adaptive"
style="border:0; padding:0; width:100%; height:auto; overflow:hidden; display:block; margin:auto;">
</iframe>
</div>
<!-- END AADS AD UNIT {unit} -->"""

# The site's own tokens (web/src/styles.css), restated here because this page
# ships without the stylesheet: canvas #050607, surface #111316, ink #f4f5f7,
# muted #b4bac3, dim #858c96, line #2d3035, sage #8bd5b1. The page stays one
# small card, but it no longer flashes a white rectangle between a dark site and
# a dark Discord.
_STYLES = """
  *, *::before, *::after { box-sizing: border-box; }
  html { color-scheme: dark; }
  body { margin: 0; padding: 32px 16px 48px; background: #050607; color: #f4f5f7;
         font: 15px/1.5 "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  main { width: 100%; max-width: 380px; margin: 0 auto; padding: 24px 22px 22px;
         background: #111316; border: 1px solid #2d3035; border-top: 2px solid #8bd5b1;
         border-radius: 8px; }
  h1 { margin: 0 0 6px; font-size: 21px; line-height: 1.25; letter-spacing: -0.03em; }
  p { margin: 0 0 16px; color: #b4bac3; font-size: 13px; }
  .guild { color: #f4f5f7; font-weight: 600; }
  form { margin: 0 0 8px; }
  img { display: block; width: 100%; height: auto; margin: 0 0 14px; border: 1px solid #2d3035;
        border-radius: 6px; background: #171a1f; image-rendering: auto; }
  label { display: block; margin: 0 0 6px; color: #b4bac3; font-size: 12px; font-weight: 700;
          letter-spacing: 0.02em; }
  input { width: 100%; padding: 11px 12px; border: 1px solid #2d3035; border-radius: 6px;
          background: #191b1f; color: #f4f5f7; font: inherit; letter-spacing: 0.14em;
          text-transform: uppercase; }
  input::placeholder { color: #667080; }
  input:focus { outline: 2px solid rgba(139, 213, 177, 0.45); outline-offset: 1px; border-color: #8bd5b1; }
  button { width: 100%; margin-top: 12px; min-height: 43px; padding: 10px 16px; border: 1px solid transparent;
           border-radius: 6px; background: #aab1ba; color: #111316; font: inherit;
           font-weight: 700; cursor: pointer; }
  button:hover { background: #d5d9df; }
  h2 { margin: 20px 0 8px; color: #b4bac3; font-size: 11px; font-weight: 700;
       letter-spacing: 0.12em; text-transform: uppercase; }
  ol { margin: 0 0 4px; padding-left: 18px; color: #b4bac3; font-size: 13px; }
  ol li { margin: 5px 0; }
  ol li strong { color: #f4f5f7; }
  .error { margin: 0 0 14px; padding: 10px 12px; border: 1px solid rgba(237, 66, 69, 0.4);
           border-radius: 6px; background: rgba(237, 66, 69, 0.1); color: #ffb4b0; font-size: 13px; }
  .hint { margin: 10px 0 0; color: #858c96; font-size: 11px; }
  .ad { max-width: 480px; margin: 24px auto 0; text-align: center; }
  .ad-label { display: block; margin: 0 0 6px; color: #667080; font-size: 10px;
              letter-spacing: 0.13em; text-transform: uppercase; }
  .note { max-width: 480px; margin: 20px auto 0; color: #858c96; font-size: 11px; text-align: center; }
  .note a { color: #b4bac3; }
  .note a:hover { color: #8bd5b1; }
"""


def ad_unit() -> str:
    """The AADS embed for the configured unit, or "" when none is configured."""
    unit = (os.environ.get("AADS_AD_UNIT_ID") or "").strip()
    if not unit.isdigit():
        return ""
    return _AADS_MARKUP.format(unit=unit)


def _document(title: str, body: str, *, ad: bool = True, status: int = 200) -> tuple[str, int]:
    markup = ad_unit() if ad else ""
    ad_block = (
        f'<aside class="ad"><span class="ad-label">Advertisement</span>{markup}</aside>'
        if markup else ""
    )
    note = (
        '<p class="note">Ads pay for Niko\'s hosting. '
        'See the <a href="/privacy" rel="noopener">privacy policy</a>.</p>'
        if markup else ""
    )
    return (
        "<!doctype html>\n"
        '<html lang="en"><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="robots" content="noindex, nofollow">'
        f"<title>{escape(title)} — Niko</title>"
        f"<style>{_STYLES}</style>"
        "</head><body>"
        f"{body}"
        f"{ad_block}"
        f"{note}"
        "</body></html>"
    ), status


def entry_page() -> tuple[str, int]:
    """The verification page at a stable, always-available URL.

    A-ADS requires at least one page to carry the ad unit permanently, at a URL
    that does not change, that anyone can load without authorising or solving
    anything. A challenge link cannot be that page: every member gets a different
    token and each link expires.

    So ``/verify`` is that URL. It reads no database and touches no bot state, and
    it is the only page in the deployment whose ad slot is unconditional — keep it
    that way (see the route, and ``AADS_AD_UNIT_ID``) or the ad unit stops being
    detected, which stops it earning at all.
    """
    body = (
        "<main>"
        f"<h1>{escape(PAGE_TITLE)}</h1>"
        "<p>Some Discord servers ask Niko to check that new members are human before "
        "they can post. This is where that check happens.</p>"
        "<h2>How it works</h2>"
        "<ol>"
        "<li>Press <strong>Verify</strong> on the panel in the server.</li>"
        "<li>Niko replies with a link to this page that is just for you.</li>"
        "<li>Type the code it shows and you are done.</li>"
        "</ol>"
        '<p class="hint">This page on its own does not verify anyone — your link from '
        "Discord carries the challenge.</p>"
        "</main>"
    )
    return _document(PAGE_TITLE, body)


def challenge_page(
    *,
    token: str,
    guild_name: str,
    attempts_left: int,
    attempt: int = 0,
    error: str = "",
) -> tuple[str, int]:
    """The captcha form, with the code image for this challenge."""
    error_block = f'<p class="error">{escape(error)}</p>' if error else ""
    remaining = max(0, int(attempts_left))
    plural = "" if remaining == 1 else "s"
    body = (
        "<main>"
        f"<h1>{escape(PAGE_TITLE)}</h1>"
        f'<p>Verifying for <span class="guild">{escape(guild_name)}</span>.</p>'
        f"{error_block}"
        f'<form method="post" action="/verify/{escape(token)}" autocomplete="off">'
        f'<img src="/verify/{escape(token)}/captcha.png?v={int(attempt)}" '
        'alt="Captcha image — type the characters it shows" width="300" height="100">'
        '<label for="answer">Type the characters above</label>'
        '<input id="answer" name="answer" type="text" inputmode="latin" autocapitalize="characters" '
        'autocorrect="off" spellcheck="false" maxlength="10" required autofocus>'
        "<button type=\"submit\">Verify</button>"
        "</form>"
        f'<p class="hint">Not case-sensitive. {remaining} attempt{plural} left. '
        "This page expires in 30 minutes.</p>"
        "</main>"
    )
    return _document(PAGE_TITLE, body)


def notice_page(
    title: str, message: str, *, tone: str = "neutral", ad: bool = True, status: int = None,
) -> tuple[str, int]:
    """A one-paragraph result page: verified, failed, expired, or refused.

    The title is escaped; ``message`` is trusted markup owned by
    ``webapp/routes/verification_routes.py`` (it uses ``<strong>`` for the button
    it tells the reader to press) and is inserted as-is, so never pass it
    anything a visitor supplied.
    """
    heading = escape(title)
    body = (
        "<main>"
        f"<h1>{heading}</h1>"
        f"<p>{message}</p>"
        "</main>"
    )
    default_status = 403 if tone == "blocked" else 410 if tone == "expired" else 200
    return _document(title, body, ad=ad, status=status or default_status)
