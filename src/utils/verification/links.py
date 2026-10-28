"""The public URL a web verification challenge is opened at.

The link is sent in a Discord DM-style reply, so it has to be an absolute URL on
the deployment that actually issued it. ``PUBLIC_URL`` is what the rest of the
process uses for provider callbacks; the site's own domain is the fallback for
deployments that never set it.
"""

import os

from config import links as site_links


def public_origin() -> str:
    explicit = os.environ.get("PUBLIC_URL")
    if explicit:
        return explicit.rstrip("/")
    return site_links.WEBSITE


def verification_url(token: str) -> str:
    """The challenge page for one token."""
    return f"{public_origin()}/verify/{token}"
