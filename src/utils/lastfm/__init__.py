"""Last.fm — the listening history behind the ``/fm`` commands.

``client`` is the only thing that talks to the Last.fm API: it owns the key,
the rate limit and the small response cache. Everything the cog shows is either
a normalised dictionary from here or a row the cog indexed itself.
"""

from utils.lastfm.client import (
    API_URL,
    PERIODS,
    LastFmClient,
    LastFmError,
    api_signature,
    auth_url,
    period_label,
)

__all__ = [
    "API_URL",
    "PERIODS",
    "LastFmClient",
    "LastFmError",
    "api_signature",
    "auth_url",
    "period_label",
]
