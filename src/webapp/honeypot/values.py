"""Deterministic fake credentials behind the website's decoy files.

Nothing here is a real secret. Every value is derived from ``_SEED`` with
HMAC-SHA256, so the same call gives the same string in every process, on every
restart, and for anyone who reads this file in the public repository::

    python -c "from webapp.honeypot.values import values; print(values()['aws_key'])"

The point is a decoy environment that agrees with itself. The PostgreSQL
password written to ``.env`` is the one in ``docker-compose.yml``, ``.pgpass``
and ``dump.sql``; the AWS key in ``.env`` is the one in ``.aws/credentials``.
A mismatch between two leaked files is the quickest way for a crawler to tell a
decoy from a real leak, so there are none.

This module never reads the environment, never imports the application's
configuration, and never touches the network: a fake value that happened to be
a live one would be far worse than no decoy at all.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import random
import string

#: The whole fake world comes from this seed. Changing it regenerates every
#: decoy file at once, which is only useful if the strings ever get reposted.
_SEED = b"niko-decoy-environment/2026-11"

_LOWER = string.ascii_lowercase
_UPPER = string.ascii_uppercase
_DIGITS = string.digits
_ALNUM = _LOWER + _UPPER + _DIGITS
_HEX = "0123456789abcdef"
_URLSAFE = _ALNUM + "-_"
_BASE64 = _ALNUM + "+/"

#: Hostname used for internal infrastructure. The public parts of the decoy —
#: the site's own URL and the shared staff addresses — are the real ones,
#: because they are already public and a wrong value there would give the game
#: away for no benefit.
INTERNAL_DOMAIN = "niko-internal.example"
PUBLIC_URL = "https://niko.sryze.cc"
SUPPORT_URL = "https://niko.sryze.cc/discord"

#: The shared staff addresses, which are public on the site (see
#: ``webapp.staff_email``). Decoys use these instead of inventing mailboxes on
#: a made-up domain: they are already known, and a real-looking address that
#: bounces is a hint that the file is fake.
OWNER_EMAIL = "owner@niko.sryze.cc"
ADMIN_EMAIL = "admin@niko.sryze.cc"
SUPPORT_EMAIL = "support@niko.sryze.cc"
SUPPORT_LEAD_EMAIL = "support-lead@niko.sryze.cc"


def _stream(label: str) -> random.Random:
    """A random source that depends only on ``label`` and the fixed seed."""
    digest = hmac.new(_SEED, label.encode("utf-8"), hashlib.sha256).digest()
    return random.Random(int.from_bytes(digest, "big"))


def text(rng: random.Random, length: int, alphabet: str = _ALNUM) -> str:
    return "".join(rng.choice(alphabet) for _ in range(length))


def hex_id(rng: random.Random, length: int) -> str:
    return text(rng, length, _HEX)


def digits(rng: random.Random, length: int) -> str:
    return text(rng, length, _DIGITS)


def base64_text(raw: str) -> str:
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")


def base64_url(raw: str) -> str:
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")


def snowflake(rng: random.Random) -> str:
    """A Discord-shaped id: 18 digits, inside the range real ids occupy."""
    return str(rng.randrange(10**17, 10**18))


def pem(rng: random.Random, label: str = "RSA PRIVATE KEY", lines: int = 28) -> str:
    """A PEM block of the right shape and the wrong contents."""
    body = "\n".join(text(rng, 64, _BASE64) for _ in range(lines))
    return f"-----BEGIN {label}-----\n{body}\n-----END {label}-----\n"


def jwt(rng: random.Random, audience: str, scope: str) -> str:
    """A signed-looking JWT whose signature verifies against nothing."""
    header = base64_url(json.dumps(
        {"alg": "RS256", "typ": "JWT", "kid": hex_id(rng, 16)},
        separators=(",", ":"),
    ))
    payload = base64_url(json.dumps({
        "iss": f"https://auth.{INTERNAL_DOMAIN}/",
        "sub": "niko-prod",
        "aud": audience,
        "iat": 1761868800,
        "exp": 1793404800,
        "scope": scope,
    }, separators=(",", ":")))
    return f"{header}.{payload}.{text(rng, 342, _URLSAFE)}"


def _values() -> dict[str, str]:
    """Build the fake world. Cached by the caller; pure either way."""
    rng = _stream("credentials")
    discord_id = snowflake(rng)
    discord_token = ".".join((
        base64_url(discord_id),
        base64_url(digits(rng, 10)),
        text(rng, 38, _URLSAFE),
    ))
    pg_password = text(rng, 24)
    mongo_password = text(rng, 24)
    pg_password_old = text(rng, 24)
    mongo_password_old = text(rng, 24)
    aws_key = "AKIA" + text(rng, 16, _UPPER + _DIGITS)
    aws_secret = text(rng, 40, _BASE64)
    redis_password = text(rng, 24)
    queue_password = text(rng, 20)
    gcp_project = "niko-prod-" + digits(rng, 6)
    # The service hosts are subdomains of the real site. None of them runs a
    # service: following a fake connection string there plays an easter egg
    # (see ``easter_eggs.py``) instead of reaching a login prompt.
    pg_host = "db.niko.sryze.cc"
    redis_host = "cache.niko.sryze.cc"
    return {
        # ── Discord and the bot itself ──────────────────────────────────────
        "discord_id": discord_id,
        "discord_token": discord_token,
        "discord_client_secret": text(rng, 32),
        "public_url": PUBLIC_URL,
        "support_url": SUPPORT_URL,
        "donation_url": PUBLIC_URL,
        "instance": "niko-prod-01",
        "prod_instance_url": "https://niko-prod-01.niko-internal.example:8443",
        "session_secret": hex_id(rng, 64),
        "beta_token": text(rng, 48),
        "admin_email": ADMIN_EMAIL,
        "admin_password": text(rng, 18),
        # ── Databases ───────────────────────────────────────────────────────
        "pg_user": "niko_admin",
        "pg_password": pg_password,
        "pg_password_old": pg_password_old,
        "pg_host": pg_host,
        "pg_db": "niko_production",
        "postgres_url": (
            f"postgresql://niko_admin:{pg_password}"
            f"@{pg_host}:5432/niko_production"
        ),
        "mysql_user": "niko_web",
        "mysql_password": text(rng, 20),
        "mysql_host": pg_host,
        "mysql_db": "niko_wp",
        "mongo_user": "niko_admin",
        "mongo_password": mongo_password,
        "mongo_password_old": mongo_password_old,
        "mongo_host": "cluster0.k7x2m.mongodb.net",
        "mongo_db": "niko_production",
        "mongo_url": (
            f"mongodb+srv://niko_admin:{mongo_password}"
            "@cluster0.k7x2m.mongodb.net/niko_production"
            "?retryWrites=true&w=majority&appName=niko-prod"
        ),
        "redis_host": redis_host,
        "redis_password": redis_password,
        "redis_url": f"redis://:{redis_password}@{redis_host}:6379/0",
        # ── Internal services behind the same domain ────────────────────────
        "vault_addr": "https://vault.niko.sryze.cc",
        "queue_password": queue_password,
        "queue_url": (
            f"amqp://niko:{queue_password}@queue.niko.sryze.cc:5672/niko"
        ),
        "queue_http": "https://queue.niko.sryze.cc",
        # ── Third-party services ────────────────────────────────────────────
        "aws_key": aws_key,
        "aws_secret": aws_secret,
        "aws_region": "eu-central-1",
        "aws_backup_key": "AKIA" + text(rng, 16, _UPPER + _DIGITS),
        "aws_backup_secret": text(rng, 40, _BASE64),
        "s3_bucket": "niko-prod-assets",
        "github_token": "ghp_" + text(rng, 36),
        "github_fine_token": "github_pat_" + text(rng, 59, _ALNUM + "_"),
        "npm_token": "npm_" + text(rng, 36),
        "pypi_token": "pypi-AgEIcHlwaS5vcmc" + text(rng, 71, _URLSAFE),
        "cloudflare_token": text(rng, 40, _URLSAFE),
        "vercel_token": text(rng, 24),
        "stripe_secret": "sk_live_" + text(rng, 99, _ALNUM),
        "stripe_publishable": "pk_live_" + text(rng, 24),
        "stripe_webhook": "whsec_" + text(rng, 32, _BASE64),
        "sendgrid_key": (
            "SG." + text(rng, 22, _URLSAFE) + "." + text(rng, 43, _URLSAFE)
        ),
        "twilio_sid": "AC" + hex_id(rng, 32),
        "twilio_token": hex_id(rng, 32),
        "mailgun_key": "key-" + hex_id(rng, 32),
        "mailgun_signing": hex_id(rng, 32),
        "smtp_host": "smtp.mailgun.org",
        "smtp_user": "postmaster@niko.sryze.cc",
        "smtp_password": text(rng, 18),
        "openai_key": "sk-proj-" + text(rng, 148, _URLSAFE),
        "anthropic_key": "sk-ant-api03-" + text(rng, 93, _URLSAFE),
        "groq_key": "gsk_" + text(rng, 52),
        "lastfm_key": hex_id(rng, 32),
        "spotify_id": hex_id(rng, 32),
        "spotify_secret": hex_id(rng, 32),
        "twitch_id": text(rng, 30, _LOWER + _DIGITS),
        "twitch_secret": text(rng, 30),
        "webshare_key": text(rng, 40),
        "oxapay_key": hex_id(rng, 40),
        "google_maps_key": "AIza" + text(rng, 35, _URLSAFE),
        "aads_unit": (
            "ca-app-pub-" + digits(rng, 16) + "/" + digits(rng, 10)
        ),
        "sentry_dsn": (
            f"https://{hex_id(rng, 32)}@o{rng.randrange(10**5, 10**6)}"
            f".ingest.sentry.io/{rng.randrange(10**6, 10**7)}"
        ),
        "jwt_secret": hex_id(rng, 64),
        "encryption_key": base64_text(text(rng, 32)),
        "vault_token": "hvs." + text(rng, 24, _URLSAFE),
        "atlas_token": "atlasv1." + text(rng, 60, _URLSAFE),
        "jwt_access": jwt(rng, "https://api.niko-internal.example", "read write"),
        "jwt_refresh": jwt(rng, "https://auth.niko-internal.example", "offline_access"),
        "docker_user": "niko-deploy",
        "docker_password": text(rng, 20),
        # ── Google service account ──────────────────────────────────────────
        "gcp_project": gcp_project,
        "gcp_key_id": hex_id(rng, 40),
        "gcp_client_id": digits(rng, 21),
        "gcp_client_email": (
            f"niko-backend@{gcp_project}.iam.gserviceaccount.com"
        ),
        "gcp_private_key": pem(rng),
        "gcp_refresh_token": "1//0" + text(rng, 60, _URLSAFE),
        "gcp_client_secret": "GOCSPX-" + text(rng, 28, _URLSAFE),
    }


_VALUES: dict[str, str] | None = None


def values() -> dict[str, str]:
    """The fake world, built once per process."""
    global _VALUES
    if _VALUES is None:
        _VALUES = _values()
    return _VALUES
