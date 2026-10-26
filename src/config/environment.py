"""Deployment environment flags shared by bot subsystems.

Development and beta instances run beside production, often against the same
Discord application and MongoDB database. Reading live data is harmless, but
anything that accumulates must stay off in development: both instances would
otherwise count the same traffic twice, and the development instance would
overwrite production's stored levels.
"""

import os


def _env_flag(name: str) -> bool:
    """Read an opt-in environment flag, accepting common true values."""
    return (os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "on"}


# Set DEVELOPMENT=true (or 1/yes/on) on beta and local instances.
DEVELOPMENT = _env_flag("DEVELOPMENT")
