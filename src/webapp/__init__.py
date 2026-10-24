"""Flask web application package entrypoint."""

from .server import app, configure_bot, public_base_url, redirect_uri

# Import routes after the shared application setup so decorators register them
# on the same Flask instance exposed to the API server.
from . import (  # noqa: E402,F401
    auth_routes,
    team_routes,
    staff_management_routes,
    public_routes,
    dashboard_routes,
    notifier_routes,
    booster_routes,
    donation_routes,
    premium_routes,
    privacy_routes,
    discord_text_routes,
    transcript_routes,
    card_routes,
    application_routes,
    team_recruitment_routes,
    economy_routes,
    site_routes,
    security_decoy_routes,
    appeal_routes,
    standby_routes,
    proxy_worker_routes,
    interaction_routes,
)

__all__ = ["app", "configure_bot", "public_base_url", "redirect_uri"]
