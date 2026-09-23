"""Flask web application package entrypoint."""

from .server import app, configure_bot, public_base_url, redirect_uri

# Import routes after the shared application setup so decorators register them
# on the same Flask instance exposed to the API server.
from . import (  # noqa: E402,F401
    auth_routes,
    team_routes,
    public_routes,
    dashboard_routes,
    donation_routes,
    transcript_routes,
    card_routes,
    site_routes,
)

__all__ = ["app", "configure_bot", "public_base_url", "redirect_uri"]
