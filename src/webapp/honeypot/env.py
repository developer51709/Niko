""".env decoy files for the website's credential honeypot.

Fake values only — see ``values.py`` for where the strings come from.
Each variant is a plausible environment file: production and staging use the
deployed URLs, local and test point at containers, and the backup copies carry
a rotated-out database password so the set reads like a real history.
"""

from __future__ import annotations

from .values import values

#: name on disk -> which kind of environment it describes
DOTENV_FILES: dict[str, str] = {
    ".env": "production",
    ".env.prod": "production",
    ".env.production": "production",
    ".env.local": "local",
    ".env_local": "local",
    ".env.development": "development",
    ".env.dev": "development",
    ".env_dev": "development",
    ".env.test": "test",
    ".env.preview": "preview",
    ".env.staging": "staging",
    ".env.backup": "backup",
    ".env.bak": "backup",
    ".env.old": "backup",
    ".env.save": "backup",
    ".env.dist": "example",
    ".env.example": "example",
    ".env.sample": "example",
    ".env.template": "example",
    ".env.docker": "docker",
}

_OVERRIDES: dict[str, dict[str, str]] = {
    "local": {
        "NODE_ENV": "development",
        "DEVELOPMENT": "true",
        "PUBLIC_URL": "http://localhost:5173",
        "DISCORD_REDIRECT_URI": "http://localhost:5173/auth/callback",
        "MONGODB_URL": "mongodb://niko_local:devpass@localhost:27017/niko_dev",
        "MONGODB_DATABASE": "niko_dev",
    },
    "development": {
        "NODE_ENV": "development",
        "DEVELOPMENT": "true",
        "PUBLIC_URL": "http://localhost:5173",
        "DISCORD_REDIRECT_URI": "http://localhost:5173/auth/callback",
        "MONGODB_DATABASE": "niko_dev",
    },
    "test": {
        "NODE_ENV": "test",
        "DEVELOPMENT": "true",
        "PUBLIC_URL": "http://127.0.0.1:5001",
        "MONGODB_DATABASE": "niko_test",
        "POSTGRES_URL": "postgresql://niko_admin:test@pg-test.internal:5432/niko_test",
    },
    "preview": {
        "DEVELOPMENT": "true",
        "PUBLIC_URL": "https://preview.niko.sryze.cc",
        "MONGODB_DATABASE": "niko_preview",
        "MONGODB_URL": "mongodb+srv://niko_admin:preview-shared@cluster0.k7x2m.mongodb.net/niko_preview",
    },
    "staging": {
        "PUBLIC_URL": "https://staging.niko.sryze.cc",
        "DISCORD_REDIRECT_URI": "https://staging.niko.sryze.cc/auth/callback",
        "MONGODB_DATABASE": "niko_staging",
        "PRODUCTION_INSTANCE_URL": "https://niko-staging-01.niko-internal.example:8443",
    },
    "docker": {
        "MONGODB_URL": "mongodb://niko_prod:changeme-in-swarm@mongo:27017/niko_production",
        "PUBLIC_URL": "http://dashboard:5000",
    },
}

_HEADER = [
    "# Niko — environment",
    "# Instance: {instance}    Last edited: 2026-10-30 by deploy",
    '# Load with: docker run --env-file /srv/niko/.env ...',
    "# This file is not in the repository. Do not paste it into tickets.",
    "",
]


def dotenv(variant: str = "production") -> str:
    """The decoy ``.env`` for one deployment variant."""
    v = values()
    overrides = _OVERRIDES.get(variant, {})
    if variant == "backup":
        overrides = {
            **_OVERRIDES.get("production", {}),
            "POSTGRES_URL": (
                f"postgresql://niko_admin:{v['pg_password_old']}"
                f"@{v['pg_host']}:5432/niko_production"
            ),
            "MONGODB_URL": (
                f"mongodb+srv://niko_admin:{v['mongo_password_old']}"
                "@cluster0.k7x2m.mongodb.net/niko_production"
            ),
        }

    # The donation site is the site itself, so it follows whatever public URL
    # this variant uses instead of pointing at a made-up host.
    public_url = overrides.get("PUBLIC_URL", v["public_url"])
    pairs = [
        ("NODE_ENV", "production"),
        ("DEVELOPMENT", "false"),
        ("PORT", "5000"),
        ("PUBLIC_URL", public_url),
        ("PRODUCTION_INSTANCE_URL", v["prod_instance_url"]),
        ("DISCORD_BOT_TOKEN", v["discord_token"]),
        ("DISCORD_CLIENT_ID", v["discord_id"]),
        ("DISCORD_CLIENT_SECRET", v["discord_client_secret"]),
        ("DISCORD_REDIRECT_URI", public_url + "/auth/callback"),
        ("DONATION_SITE_URL", public_url),
        ("MONGODB_DATABASE", v["mongo_db"]),
        ("MONGODB_URL", v["mongo_url"]),
        ("POSTGRES_URL", v["postgres_url"]),
        ("MYSQL_URL", (
            f"mysql://{v['mysql_user']}:{v['mysql_password']}"
            f"@{v['mysql_host']}:3306/{v['mysql_db']}"
        )),
        ("REDIS_URL", v["redis_url"]),
        ("VAULT_ADDR", v["vault_addr"]),
        ("VAULT_TOKEN", v["vault_token"]),
        ("RABBITMQ_URL", v["queue_url"]),
        ("RABBITMQ_MANAGEMENT_URL", v["queue_http"]),
        ("SESSION_SECRET", v["session_secret"]),
        ("JWT_SECRET", v["jwt_secret"]),
        ("ENCRYPTION_KEY", v["encryption_key"]),
        ("AWS_ACCESS_KEY_ID", v["aws_key"]),
        ("AWS_SECRET_ACCESS_KEY", v["aws_secret"]),
        ("AWS_REGION", v["aws_region"]),
        ("S3_BUCKET", v["s3_bucket"]),
        ("GITHUB_TOKEN", v["github_token"]),
        ("NPM_TOKEN", v["npm_token"]),
        ("CLOUDFLARE_API_TOKEN", v["cloudflare_token"]),
        ("OPENAI_API_KEY", v["openai_key"]),
        ("ANTHROPIC_API_KEY", v["anthropic_key"]),
        ("GROQ_API_KEY", v["groq_key"]),
        ("STRIPE_SECRET_KEY", v["stripe_secret"]),
        ("STRIPE_WEBHOOK_SECRET", v["stripe_webhook"]),
        ("SENDGRID_API_KEY", v["sendgrid_key"]),
        ("MAILGUN_API_KEY", v["mailgun_key"]),
        ("MAILGUN_WEBHOOK_SIGNING_KEY", v["mailgun_signing"]),
        ("SMTP_HOST", v["smtp_host"]),
        ("SMTP_USER", v["smtp_user"]),
        ("SMTP_PASSWORD", v["smtp_password"]),
        ("TWILIO_ACCOUNT_SID", v["twilio_sid"]),
        ("TWILIO_AUTH_TOKEN", v["twilio_token"]),
        ("GOOGLE_APPLICATION_CREDENTIALS", "/srv/niko/secrets/service-account.json"),
        ("GOOGLE_MAPS_API_KEY", v["google_maps_key"]),
        ("SENTRY_DSN", v["sentry_dsn"]),
        ("SPOTIFY_CLIENT_ID", v["spotify_id"]),
        ("SPOTIFY_CLIENT_SECRET", v["spotify_secret"]),
        ("TWITCH_CLIENT_ID", v["twitch_id"]),
        ("TWITCH_CLIENT_SECRET", v["twitch_secret"]),
        ("LASTFM_API_KEY", v["lastfm_key"]),
        ("WEBSHARE_API_KEY", v["webshare_key"]),
        ("OXAPAY_API_KEY", v["oxapay_key"]),
        ("AADS_AD_UNIT_ID", v["aads_unit"]),
        ("BETA_UPDATE_TOKEN", v["beta_token"]),
        ("ADMIN_EMAIL", v["admin_email"]),
        ("ADMIN_PASSWORD", v["admin_password"]),
        ("SHARD_COUNT", "2"),
    ]

    lines = [
        line.format(instance=v["instance"])
        for line in _HEADER
    ]
    if variant == "example":
        lines.append("# Filled from the live container so the prerender job boots.")
        lines.append("# TODO: move these back to the secret store (ticket NIKO-2411).")
        lines.append("")
    elif variant == "backup":
        lines.append("# Superseded 2026-09-14 by the credentials rotated in the live")
        lines.append("# container; kept until the old Mongo replica is decommissioned.")
        lines.append("")
    elif variant in {"local", "development", "test"}:
        lines.append("# Local values. These are the production tokens the team reuses")
        lines.append("# for convenience — do not share this file outside the org.")
        lines.append("")

    seen = set()
    for key, value in pairs:
        seen.add(key)
        lines.append(f"{key}={overrides.get(key, value)}")

    # Anything a variant only adds stays grouped with the keys it belongs to.
    for key, value in overrides.items():
        if key not in seen:
            lines.append(f"{key}={value}")

    lines.extend([
        "",
        "# Legacy (removed from the code, kept until the migration finishes)",
        f"# DISCORD_WEBHOOK_ALERTS=https://discord.com/api/webhooks/"
        f"{v['discord_id']}/{v['discord_token']}",
        f"# MONGO_URI_OLD=mongodb://niko_admin:{v['mongo_password_old']}"
        f"@{v['mongo_host']}:27017/niko_production",
        f"# support: {v['admin_email']}",
        "",
    ])
    return "\n".join(lines)


def vim_swap() -> bytes:
    """A Vim swap file header with the decoy ``.env`` inside it."""
    body = dotenv("production").encode("utf-8")
    header = b"b0VIM 9.0\x00\x00\x00\x00"
    padding = bytes(range(256)) * 6
    return header + padding + body[:8192]
