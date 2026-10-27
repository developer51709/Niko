"""The ways a server can ask its members to prove they are human.

A server picks one mode, stored as ``captcha_mode`` on its onboarding config:

* ``click`` — the Verify button verifies immediately. The frictionless option,
  for communities that only want a deliberate click between joining and the
  rest of the server.
* ``image`` — the member is DMed a distorted code and replies with it.
* ``web`` — the member opens a page on the website, completes the challenge
  there, and the browser tells the bot the result. This is the only mode that
  can also refuse proxy and VPN traffic, because it is the only one where the
  verification happens from an IP address the bot can see.
"""

CLICK = "click"
IMAGE = "image"
WEB = "web"

MODES = (CLICK, IMAGE, WEB)

# Servers that were verifying before modes existed were all doing the DM image
# challenge, so that is what an unset or unrecognised value means.
DEFAULT_MODE = IMAGE

LABELS = {
    CLICK: "One-click verify",
    IMAGE: "Image captcha in DMs",
    WEB: "Captcha on the website",
}

DESCRIPTIONS = {
    CLICK: "Pressing **Verify** completes verification on the spot.",
    IMAGE: "Pressing **Verify** sends a captcha image in DMs; the member replies with the code.",
    WEB: "Pressing **Verify** opens a short captcha page in the browser. Proxy and VPN checks are available here.",
}

# What the public panel tells a member, per mode. Written for the member, not
# the administrator: it is the first thing they read after joining.
PANEL_PROMPTS = {
    CLICK: (
        "Click **Verify** below to confirm you are human.\n\n"
        "That is the whole check — the roles you need will be added straight away."
    ),
    IMAGE: (
        "Click **Verify** below and the bot will send you a DM with a captcha image. "
        "Reply to the DM with the code shown in the image."
    ),
    WEB: (
        "Click **Verify** below to open a short verification page in your browser. "
        "Type the code it shows and you are done — keep Discord open so the roles arrive."
    ),
}


def normalize_mode(value) -> str:
    """Coerce a stored value into a known mode, falling back to the default."""
    if isinstance(value, str) and value.strip().lower() in MODES:
        return value.strip().lower()
    return DEFAULT_MODE


def is_valid_mode(value) -> bool:
    return isinstance(value, str) and value.strip().lower() in MODES


def describe(mode) -> str:
    return DESCRIPTIONS.get(normalize_mode(mode), DESCRIPTIONS[DEFAULT_MODE])
