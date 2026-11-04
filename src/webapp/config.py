"""Environment, filesystem, and permission constants for the web
application process."""

import os
from urllib.parse import urlparse


def _flag(name: str) -> bool:
    """A switch that reads 1/true/yes/on as on and everything else as off."""
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


DISCORD_CLIENT_ID     = os.environ.get("DISCORD_CLIENT_ID", "1520558530472448170")

DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")

DISCORD_BOT_TOKEN     = os.environ.get("DISCORD_BOT_TOKEN", "")

DISCORD_API           = "https://discord.com/api/v10"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

ECONOMY_DIR  = os.path.join(DATA_DIR, "economy_data")

BOT_STATS    = os.path.join(DATA_DIR, "bot_stats.json")

AI_CONFIG_DATABASE_SENTINEL_LEGACY        = os.path.join(DATA_DIR, "ai_config.json")

AI_CONFIG_DATABASE_SENTINEL = AI_CONFIG_DATABASE_SENTINEL_LEGACY  # compatibility alias; AI reads/writes are database-backed

LEVELS_JSON  = os.path.join(DATA_DIR, "levels.json.migrated")

LEVELCFG_JSON = os.path.join(DATA_DIR, "level_config.json.migrated")

DATABASE_PATH = os.path.join(DATA_DIR, "database.db")

OXAPAY_KEY = os.environ.get("OXAPAY_API_KEY", "")

MANAGE_GUILD_PERM = 0x20

ADMINISTRATOR_PERM = 0x8

WEB_DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "website", "dist")


# ── Subdomain routing ─────────────────────────────────────────────────────────

#: OPTIONAL. Serve sections from their own subdomain instead of the apex path:
#: with this on, ``https://dash.example.com/staff`` is the dashboard's
#: ``https://example.com/dashboard/staff``. Off by default, and nothing changes
#: for hosts whose first label is not listed below.
SUBDOMAIN_ROUTING = _flag("SUBDOMAIN_ROUTING")

#: Subdomain label → the apex path that host serves from its root. Only labels
#: listed here do anything; the apex, ``www`` and every other host keep serving
#: the normal site.
#:
#: ``dash`` is the dashboard, whose whole subtree already lives under one
#: prefix, which is what makes the swap safe: ``dash.example.com/staff`` is
#: ``example.com/dashboard/staff`` and nothing else on the site moves. Adding a
#: second entry works the same way for any section whose pages only link inside
#: their own subtree — the client keeps the short form, and the few links that
#: leave the subtree are absolute (``router.siteHref``).
SUBDOMAIN_SECTIONS = {
    "dash": "/dashboard",
}

def subdomain_prefix(host: str | None) -> str:
    """The apex path a request host stands in for, or "" for the normal site.

    Only the first label of the host is read, so ``dash.example.com`` and
    ``dash.staging.example.com`` are both the dashboard and no per-domain
    configuration is needed beyond pointing the wildcard at this service.
    """
    if not SUBDOMAIN_ROUTING or not host:
        return ""
    label = host.split(":", 1)[0].strip().lower().split(".", 1)[0]
    return SUBDOMAIN_SECTIONS.get(label, "")


def apex_path(host: str | None, path: str) -> str:
    """The apex form of a path, whichever host it was written on.

    ``/staff`` on ``dash.example.com`` is the dashboard's ``/dashboard/staff``,
    while on the apex the path is already in that form and comes back
    unchanged. A section host's own pages and redirects write the short form, so
    anything captured there — a redirect target, the ``next=`` a sign-in should
    return to — is translated with this before the rest of the server sees it.
    Query strings are carried along untouched.
    """
    pathname, separator, query = path.partition("?")
    prefix = subdomain_prefix(host)
    if prefix:
        if pathname in ("", "/"):
            pathname = prefix
        elif not pathname.startswith(prefix + "/") and pathname != prefix:
            pathname = prefix + (pathname if pathname.startswith("/") else "/" + pathname)
    return pathname + separator + query


def public_path(prefix: str, path: str) -> str:
    """The short form of an apex path on the host that serves ``prefix``.

    The inverse of ``apex_path`` for a host the caller already knows: the
    section's root is that host's ``/``, and anything else that is not inside
    the prefix stays as it is.
    """
    pathname, separator, query = path.partition("?")
    if prefix:
        if pathname == prefix:
            pathname = "/"
        elif pathname.startswith(prefix + "/"):
            pathname = pathname[len(prefix):]
    return pathname + separator + query


def section_origins() -> dict[str, str]:
    """Apex path → the origin that serves it, when sections have their own hosts.

    The apex keeps its own paths, but a link *to* a section belongs on that
    section's host: ``/dashboard`` on ``https://dash.example.com``, where the
    dashboard's own navigation is the short form. Empty while routing is off or
    ``PUBLIC_URL`` is unset, which is the signal to leave those links relative.
    """
    if not SUBDOMAIN_ROUTING:
        return {}
    parts = urlparse(canonical_origin())
    host = parts.hostname or ""
    if not host:
        return {}
    port = f":{parts.port}" if parts.port else ""
    return {
        prefix: f"{parts.scheme}://{label}.{host}{port}"
        for label, prefix in SUBDOMAIN_SECTIONS.items()
    }


def public_domain() -> str:
    """The site's own host name, taken from ``PUBLIC_URL``; "" when unset.

    It answers the one question a request cannot: which hosts belong to this
    site. The cookie's domain and whether a host is an unused subdomain of the
    site — as opposed to somebody else's address — are both decided from it.
    """
    return (urlparse(os.environ.get("PUBLIC_URL", "")).hostname or "").strip(".").lower()


def canonical_origin() -> str:
    """``PUBLIC_URL`` as an origin, or "" when it is not configured."""
    url = (os.environ.get("PUBLIC_URL", "") or "").strip().rstrip("/")
    return url if url.startswith(("http://", "https://")) else ""


def session_cookie_domain() -> str:
    """The domain the session cookie is shared on, or "" for host-only.

    A sign-in has to survive the hop between the apex and a section host, and a
    cookie can only be shared on the domain that issued it. It is read once, at
    import, from ``PUBLIC_URL`` — the canonical apex — because the alternative,
    deriving it from whichever host is answering, would let one host's response
    widen (or break) another's. Bare hosts and IP addresses have no domain to
    share on, so they keep host-only cookies.
    """
    if not SUBDOMAIN_ROUTING:
        return ""
    name = public_domain()
    if not name or "." not in name or name.replace(".", "").isdigit():
        return ""
    return f".{name}"


def unknown_subdomain(host: str | None) -> bool:
    """A host under the site's own domain that the site does not serve.

    ``foo.example.com`` belongs to ``example.com`` but is not one of the
    sections in ``SUBDOMAIN_SECTIONS``, so there is no site behind it and it
    answers with the subdomain variant of the 404 page. The apex, ``www`` and
    every section are served normally; a host that is not under the site's
    domain at all — a preview host, an IP, a staging deployment with its own
    ``PUBLIC_URL`` — is somebody else's address and is left alone.
    """
    if not SUBDOMAIN_ROUTING or not host:
        return False
    name = host.split(":", 1)[0].strip().lower().strip(".")
    domain = public_domain()
    if not domain or name == domain:
        return False
    label, _, rest = name.partition(".")
    if not rest or label == "www" or label in SUBDOMAIN_SECTIONS:
        return False
    return rest == domain or rest.endswith("." + domain)
