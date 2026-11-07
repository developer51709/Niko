"""Credential stores, shell history and database dumps for the decoy set.

Fake values only. ``dump.sql`` is the largest file the honeypot serves: a few
hundred rows that take a while to read and contain nothing but strings derived
from ``values.py``.
"""

from __future__ import annotations

import io
import json
import random
import zipfile

from .env import dotenv
from .values import (
    ADMIN_EMAIL,
    OWNER_EMAIL,
    SUPPORT_EMAIL,
    SUPPORT_LEAD_EMAIL,
    hex_id,
    pem,
    text,
    values,
)

_FIRST = (
    "alex", "maya", "jonas", "priya", "leo", "sofia", "noah", "emma", "liam",
    "yuki", "omar", "ines", "tomas", "nina", "rj", "kofi", "elena", "dmitri",
)
_LAST = (
    "keller", "novak", "silva", "haddad", "muller", "rossi", "okafor", "tanaka",
    "larsen", "petrov", "fischer", "costa", "weber", "dubois", "nguyen",
)
_ROLES = ("member", "member", "member", "moderator", "helper", "premium")
_HASH_ALPHABET = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./"
)


def aws_credentials() -> str:
    v = values()
    return f"""[default]
aws_access_key_id = {v["aws_key"]}
aws_secret_access_key = {v["aws_secret"]}

[backup]
aws_access_key_id = {v["aws_backup_key"]}
aws_secret_access_key = {v["aws_backup_secret"]}

[niko-deployer]
aws_access_key_id = {v["aws_key"]}
aws_secret_access_key = {v["aws_secret"]}
"""


def aws_config() -> str:
    v = values()
    return f"""[default]
region = {v["aws_region"]}
output = json

[profile backup]
region = eu-central-1
output = json

[profile niko-deployer]
region = {v["aws_region"]}
s3 =
    max_concurrent_requests = 20
    max_queue_size = 2000
"""


def npmrc() -> str:
    v = values()
    return (
        f"//registry.npmjs.org/:_authToken={v['npm_token']}\n"
        f"//npm.pkg.github.com/:_authToken={v['github_token']}\n"
        "registry=https://registry.npmjs.org/\n"
        "strict-ssl=true\n"
    )


def pypirc() -> str:
    v = values()
    return f"""[distutils]
index-servers =
    pypi
    niko

[pypi]
username = __token__
password = {v["pypi_token"]}

[niko]
repository = https://upload.pypi.org/legacy/
username = __token__
password = {v["pypi_token"]}
"""


def netrc() -> str:
    v = values()
    return f"""machine api.niko-internal.example
  login deploy
  password {v["admin_password"]}

machine vault.niko.sryze.cc
  login niko-deploy
  password {v["vault_token"]}

machine github.com
  login developer51709
  password {v["github_token"]}

machine registry.npmjs.org
  login niko-deploy
  password {v["npm_token"]}
"""


def pgpass() -> str:
    v = values()
    return (
        f"{v['pg_host']}:5432:{v['pg_db']}:{v['pg_user']}:{v['pg_password']}\n"
        f"{v['pg_host']}:5432:niko_staging:{v['pg_user']}:{v['pg_password_old']}\n"
        f"localhost:5432:postgres:postgres:{v['pg_password_old']}\n"
    )


def my_cnf() -> str:
    v = values()
    return f"""[client]
user = {v["mysql_user"]}
password = {v["mysql_password"]}
host = {v["mysql_host"]}
port = 3306

[mysqldump]
user = root
password = {v["admin_password"]}
"""


def git_config() -> str:
    v = values()
    return f"""[core]
\trepositoryformatversion = 0
\tfilemode = true
\tbare = false
\tlogallrefupdates = true
[remote "origin"]
\turl = https://x-access-token:{v["github_token"]}@github.com/developer51709/niko-website.git
\tfetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
\tremote = origin
\tmerge = refs/heads/main
[user]
\tname = niko-deploy
\temail = {v["admin_email"]}
"""


def git_credentials() -> str:
    v = values()
    return (
        f"https://deploy:{v['github_token']}@github.com\n"
        f"https://{v['docker_user']}:{v['docker_password']}@ghcr.io\n"
    )


def git_head() -> str:
    return "ref: refs/heads/main\n"


def gitignore() -> str:
    return (
        "# Environment\n.env\n.env.*\n!.env.example\n\n"
        "# Build output\n__pycache__/\n*.pyc\nweb/dist/\nnode_modules/\n\n"
        "# Local secrets\nsecrets/\n*.pem\n!public-key.pem\n"
    )


def htaccess() -> str:
    return (
        "Options -Indexes\n"
        "RewriteEngine On\n"
        "RewriteRule ^index\\.html$ - [L]\n"
        "RewriteCond %{REQUEST_FILENAME} !-f\n"
        "RewriteCond %{REQUEST_FILENAME} !-d\n"
        "RewriteRule . /index.html [L]\n"
    )


def vault_token() -> str:
    return values()["vault_token"] + "\n"


def htpasswd() -> str:
    v = values()
    return (
        f"admin:$apr1$9fK2mQ1r${v['jwt_secret'][:22]}\n"
        f"deploy:$apr1$T4x8pW0s${v['session_secret'][:22]}\n"
        f"monitoring:$apr1$Lm3nR7bq${v['gcp_key_id'][:22]}\n"
    )


def bash_history() -> str:
    v = values()
    return f"""export MONGODB_URL="{v["mongo_url"]}"
mongodump --uri "$MONGODB_URL" --out /srv/backups/2026-10-30
pg_dump --dbname="{v["postgres_url"]}" -f /srv/backups/niko-2026-10-30.sql
mysql -h {v["mysql_host"]} -u {v["mysql_user"]} -p{v["mysql_password"]} {v["mysql_db"]} -e "show tables"
redis-cli -h {v["redis_host"]} -a {v["redis_password"]} info keyspace
aws s3 sync /srv/backups s3://{v["s3_bucket"]}/backups/2026-10-30
git clone https://x-access-token:{v["github_token"]}@github.com/developer51709/niko-website.git
docker login ghcr.io -u {v["docker_user"]} -p {v["docker_password"]}
curl -H "Authorization: Bearer {v["jwt_access"]}" https://api.niko-internal.example/api/guilds
scp .env deploy@{v["instance"]}:/srv/niko/.env
ssh deploy@{v["instance"]} "docker compose pull && docker compose up -d"
vault login {v["vault_token"]}
curl -s https://vault.niko.sryze.cc/v1/niko/data/prod | jq .data
curl -s -u niko:{v["queue_password"]} {v["queue_http"]}/api/overview | jq .queue_totals
"""


def zsh_history() -> str:
    v = values()
    commands = [
        f"export AWS_ACCESS_KEY_ID={v['aws_key']}",
        f"export AWS_SECRET_ACCESS_KEY={v['aws_secret']}",
        f"psql {v['postgres_url']} -c 'select count(*) from users'",
        f"mongo \"{v['mongo_url']}\" --eval 'db.stats()'",
        f"ssh -i ~/.ssh/id_rsa deploy@{v['instance']}",
        f"kubectl --kubeconfig ~/.kube/config get pods -n niko",
        f"stripe listen --api-key {v['stripe_secret']}",
        f"gh auth login --with-token <<< {v['github_token']}",
        "vim .env",
        "htop",
    ]
    return "".join(
        f": 1761{index:05d}:0;{command}\n" for index, command in enumerate(commands)
    )


def package_json() -> str:
    return json.dumps({
        "name": "niko-dashboard",
        "private": True,
        "version": "2026.10.30",
        "type": "module",
        "scripts": {
            "dev": "vite --host 0.0.0.0",
            "build": "vite build",
            "preview": "vite preview",
            "lint": "eslint .",
        },
        "dependencies": {
            "framer-motion": "^11.11.9",
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "react-router-dom": "^6.27.0",
        },
        "devDependencies": {
            "@vitejs/plugin-react": "^4.3.3",
            "tailwindcss": "^3.4.14",
            "typescript": "^5.6.3",
            "vite": "^5.4.10",
        },
    }, indent=2) + "\n"


def composer_json() -> str:
    return json.dumps({
        "name": "niko/website",
        "description": "Niko community website",
        "type": "project",
        "require": {
            "php": "^8.3",
            "laravel/framework": "^11.0",
            "stripe/stripe-php": "^16.0",
        },
        "autoload": {"psr-4": {"App\\": "app/"}},
        "config": {"optimize-autoloader": True},
    }, indent=2) + "\n"


def babel_config() -> str:
    return """module.exports = {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }],
    ['@babel/preset-react', { runtime: 'automatic' }],
  ],
  plugins: [['transform-define', { API_KEY: '""" + values()["google_maps_key"] + """' }]],
};
"""


def webpack_config() -> str:
    v = values()
    return f"""const path = require('path');
const webpack = require('webpack');

module.exports = {{
  entry: './src/index.js',
  output: {{
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.[contenthash].js',
  }},
  plugins: [
    new webpack.DefinePlugin({{
      'process.env.API_BASE': JSON.stringify('{v["public_url"]}/api'),
      'process.env.DISCORD_TOKEN': JSON.stringify('{v["discord_token"]}'),
      'process.env.MAPBOX_TOKEN': JSON.stringify('{v["google_maps_key"]}'),
    }}),
  ],
}};
"""


def next_config() -> str:
    v = values()
    return f"""const nextConfig = {{
  reactStrictMode: true,
  env: {{
    NEXT_PUBLIC_API_BASE: '{v["public_url"]}/api',
    NEXT_PUBLIC_DISCORD_CLIENT_ID: '{v["discord_id"]}',
    DATABASE_URL: '{v["postgres_url"]}',
    MONGODB_URI: '{v["mongo_url"]}',
    STRIPE_SECRET_KEY: '{v["stripe_secret"]}',
  }},
}};

module.exports = nextConfig;
"""


def nuxt_config() -> str:
    v = values()
    return f"""export default defineNuxtConfig({{
  devtools: {{ enabled: false }},
  runtimeConfig: {{
    discordToken: '{v["discord_token"]}',
    mongoUrl: '{v["mongo_url"]}',
    sessionSecret: '{v["session_secret"]}',
    public: {{
      apiBase: '{v["public_url"]}/api',
    }},
  }},
}});
"""


def vue_config() -> str:
    v = values()
    return f"""const {{ defineConfig }} = require('@vue/cli-service');

module.exports = defineConfig({{
  transpileDependencies: true,
  devServer: {{ host: '0.0.0.0', port: 5173 }},
  configureWebpack: {{
    plugins: [],
  }},
  chainWebpack: (config) => {{
    config.plugin('define').tap((args) => {{
      args[0].__API_KEY__ = JSON.stringify('{v["openai_key"]}');
      return args;
    }});
  }},
}});
"""


def next_chunk() -> str:
    v = values()
    return (
        "(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[931],{"
        '931:function(e,t,n){"use strict";t.D=(e)=>e&&e.__esModule?e:{default:e}}'
        "},e=>{var t={};e.O(undefined,(n)=>{});}]);"
        "\n// config: "
        + json.dumps({"api": v["public_url"] + "/api", "clientId": v["discord_id"]})
        + "\n"
    )


def next_server_page() -> str:
    v = values()
    return (
        '"use strict";\n'
        '(()=>{const e={discordId:"' + v["discord_id"] + '",'
        'mongo:"' + v["mongo_url"] + '",'
        'jwt:"' + v["jwt_secret"] + '",'
        'stripe:"' + v["stripe_secret"] + '"};'
        'console.log("niko config",Object.keys(e));})();\n'
    )


def dockerfile() -> str:
    return """FROM node:20-alpine AS web
WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /srv/niko
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY --from=web /app/web/dist ./web/dist
EXPOSE 5000
CMD ["python", "-m", "src.web_child"]
"""


def wrangler_toml() -> str:
    v = values()
    return f"""name = "niko-edge"
main = "src/index.js"
compatibility_date = "2026-10-01"
account_id = "{v["gcp_client_id"]}"

[vars]
API_BASE = "{v["public_url"]}/api"
ENVIRONMENT = "production"

[[kv_namespaces]]
binding = "CACHE"
id = "{v["session_secret"][:32]}"

[[r2_buckets]]
binding = "ASSETS"
bucket_name = "{v["s3_bucket"]}"
"""


def dev_vars() -> str:
    v = values()
    return (
        f"DISCORD_BOT_TOKEN={v['discord_token']}\n"
        f"MONGODB_URL={v['mongo_url']}\n"
        f"SESSION_SECRET={v['session_secret']}\n"
        f"CLOUDFLARE_API_TOKEN={v['cloudflare_token']}\n"
        f"STRIPE_SECRET_KEY={v['stripe_secret']}\n"
    )


def netlify_toml() -> str:
    v = values()
    return f"""[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_ENV = "production"
  VITE_API_BASE = "{v["public_url"]}/api"
  VITE_DISCORD_CLIENT_ID = "{v["discord_id"]}"
  MONGODB_URL = "{v["mongo_url"]}"
  SESSION_SECRET = "{v["session_secret"]}"
  STRIPE_SECRET_KEY = "{v["stripe_secret"]}"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""


def settings_py() -> str:
    v = values()
    return f"""\"\"\"Django settings for the legacy admin panel.\"\"\"

import os

SECRET_KEY = "{v["session_secret"]}"
DEBUG = False
ALLOWED_HOSTS = ["*"]

DATABASES = {{
    "default": {{
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "{v["pg_db"]}",
        "USER": "{v["pg_user"]}",
        "PASSWORD": "{v["pg_password"]}",
        "HOST": "{v["pg_host"]}",
        "PORT": "5432",
    }}
}}

AWS_ACCESS_KEY_ID = "{v["aws_key"]}"
AWS_SECRET_ACCESS_KEY = "{v["aws_secret"]}"
AWS_STORAGE_BUCKET_NAME = "{v["s3_bucket"]}"

EMAIL_HOST = "{v["smtp_host"]}"
EMAIL_HOST_USER = "{v["smtp_user"]}"
EMAIL_HOST_PASSWORD = "{v["smtp_password"]}"

STRIPE_SECRET_KEY = "{v["stripe_secret"]}"
SENTRY_DSN = "{v["sentry_dsn"]}"
"""


def celeryconfig() -> str:
    v = values()
    return f"""broker_url = "{v["redis_url"]}"
result_backend = "{v["redis_url"]}"
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
task_routes = {{"tasks.email.*": {{"queue": "email"}}}}
"""


def alembic_ini() -> str:
    v = values()
    return f"""[alembic]
script_location = migrations
prepend_sys_path = .
sqlalchemy.url = {v["postgres_url"]}

[loggers]
keys = root,sqlalchemy,alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
"""


def application_properties() -> str:
    v = values()
    return f"""server.port=8080
spring.datasource.url=jdbc:postgresql://{v["pg_host"]}:5432/{v["pg_db"]}
spring.datasource.username={v["pg_user"]}
spring.datasource.password={v["pg_password"]}
spring.data.redis.password={v["redis_password"]}
spring.security.oauth2.client.registration.discord.client-id={v["discord_id"]}
spring.security.oauth2.client.registration.discord.client-secret={v["discord_client_secret"]}
management.endpoints.web.exposure.include=*
management.endpoint.env.show-values=ALWAYS
jwt.signing-key={v["jwt_secret"]}
"""


def terraform_tfvars() -> str:
    v = values()
    return f"""region        = "{v["aws_region"]}"
project       = "niko-prod"
db_username   = "{v["pg_user"]}"
db_password   = "{v["pg_password"]}"
aws_access_key = "{v["aws_key"]}"
aws_secret_key = "{v["aws_secret"]}"
discord_token  = "{v["discord_token"]}"
"""


def phpunit_xml() -> str:
    v = values()
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<phpunit bootstrap="vendor/autoload.php" colors="true">
  <testsuites>
    <testsuite name="Unit"><directory>tests/Unit</directory></testsuite>
  </testsuites>
  <php>
    <env name="APP_ENV" value="testing"/>
    <env name="DB_HOST" value="{v["mysql_host"]}"/>
    <env name="DB_DATABASE" value="{v["mysql_db"]}"/>
    <env name="DB_USERNAME" value="{v["mysql_user"]}"/>
    <env name="DB_PASSWORD" value="{v["mysql_password"]}"/>
    <env name="STRIPE_SECRET" value="{v["stripe_secret"]}"/>
  </php>
</phpunit>
"""


def web_config() -> str:
    v = values()
    return f"""<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <connectionStrings>
    <add name="Default" connectionString="Server={v["mysql_host"]};Database={v["mysql_db"]};User Id={v["mysql_user"]};Password={v["mysql_password"]};" />
  </connectionStrings>
  <appSettings>
    <add key="JwtKey" value="{v["jwt_secret"]}" />
    <add key="SendGridKey" value="{v["sendgrid_key"]}" />
  </appSettings>
</configuration>
"""


def laravel_log() -> str:
    v = values()
    return f"""# Niko — last 200 lines
[2026-11-06 22:41:02] production.ERROR: SQLSTATE[HY000] [1045] Access denied for user '{v["mysql_user"]}'@'10.42.0.17' (using password: YES) {{"exception":"[object] (PDOException(code: 1045): SQLSTATE[HY000] [1045] Access denied for user '{v["mysql_user"]}'@'10.42.0.17' (using password: YES) at /srv/niko/vendor/laravel/framework/src/Illuminate/Database/Connectors/Connector.php:65)"}}
[2026-11-06 22:41:02] production.INFO: Retrying with the rotation password from .env.bak
[2026-11-06 22:41:04] production.ERROR: cURL error 28: Operation timed out for https://discord.com/api/v10/guilds (see https://curl.haxx.se/libcurl/c/libcurl-errors.html)
[2026-11-06 22:44:11] production.WARNING: Stripe webhook signature failed for key {v["stripe_webhook"]}
[2026-11-06 22:51:38] production.ERROR: Class "Redis" not found at /srv/niko/app/Cache/RedisStore.php:41
"""


def phpinfo() -> str:
    v = values()
    return f"""<!DOCTYPE html>
<html><head><title>phpinfo()</title></head><body>
<h1>PHP Version 8.3.12</h1>
<table>
<tr><td>System</td><td>Linux {v["instance"]} 6.8.0-45-generic</td></tr>
<tr><td>Document Root</td><td>/var/www/niko/public</td></tr>
<tr><td>Server API</td><td>FPM/FastCGI</td></tr>
</table>
<h2>Environment</h2>
<table>
<tr><td>MONGODB_URL</td><td>{v["mongo_url"]}</td></tr>
<tr><td>POSTGRES_URL</td><td>{v["postgres_url"]}</td></tr>
<tr><td>AWS_ACCESS_KEY_ID</td><td>{v["aws_key"]}</td></tr>
<tr><td>AWS_SECRET_ACCESS_KEY</td><td>{v["aws_secret"]}</td></tr>
<tr><td>STRIPE_SECRET_KEY</td><td>{v["stripe_secret"]}</td></tr>
</table>
<h2>PHP Credits</h2>
</body></html>
"""


def wp_login() -> str:
    v = values()
    return f"""<!DOCTYPE html>
<html lang="en-US"><head><meta charset="utf-8"><title>Log In &lsaquo; Niko</title></head>
<body class="login">
<div id="login">
<h1><a href="{v["public_url"]}">Niko</a></h1>
<form name="loginform" id="loginform" action="/wp-login.php" method="post">
<p><label for="user_login">Username or Email Address</label>
<input type="text" name="log" id="user_login" /></p>
<p><label for="user_pass">Password</label>
<input type="password" name="pwd" id="user_pass" /></p>
<p class="submit"><input type="submit" name="wp-submit" id="wp-submit" value="Log In" /></p>
</form>
</div>
</body></html>
"""


def xmlrpc() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<methodResponse>
  <params>
    <param><value><array><data>
      <value><string>XML-RPC server accepts POST requests only.</string></value>
    </data></array></value></param>
  </params>
</methodResponse>
"""


def server_status() -> str:
    v = values()
    return f"""Apache Server Status for {v["instance"]}
Server Version: Apache/2.4.62 (Debian)
Server MPM: event
Current Time: Saturday, 07-Nov-2026 00:03:11 UTC
Restart Time: Friday, 06-Nov-2026 18:00:03 UTC
Parent Server Config. Generation: 3
Total accesses: 1842231 - Total Traffic: 41.2 GB
CPU Usage: u182.2 s31.4
"""


def actuator_env() -> str:
    v = values()
    document = {
        "activeProfiles": ["prod"],
        "propertySources": [
            {
                "name": "systemEnvironment",
                "properties": {
                    "DISCORD_BOT_TOKEN": {"value": v["discord_token"]},
                    "MONGODB_URL": {"value": v["mongo_url"]},
                    "POSTGRES_URL": {"value": v["postgres_url"]},
                    "SESSION_SECRET": {"value": v["session_secret"]},
                    "STRIPE_SECRET_KEY": {"value": v["stripe_secret"]},
                    "AWS_ACCESS_KEY_ID": {"value": v["aws_key"]},
                },
            },
            {
                "name": "Config resource 'file [/srv/niko/config/application.yml]'",
                "properties": {
                    "spring.datasource.password": {"value": v["pg_password"]},
                    "spring.data.redis.password": {"value": v["redis_password"]},
                },
            },
        ],
    }
    return json.dumps(document, indent=2) + "\n"


def actuator_configprops() -> str:
    v = values()
    document = {
        "contexts": {
            "application": {
                "beans": {
                    "dataSource": {
                        "prefix": "spring.datasource",
                        "properties": {
                            "url": f"jdbc:postgresql://{v['pg_host']}:5432/{v['pg_db']}",
                            "username": v["pg_user"],
                            "password": v["pg_password"],
                        },
                    },
                    "stripeClient": {
                        "prefix": "stripe",
                        "properties": {"apiKey": v["stripe_secret"]},
                    },
                }
            }
        }
    }
    return json.dumps(document, indent=2) + "\n"


def debug_vars() -> str:
    v = values()
    document = {
        "cmdline": ["./niko-api", "-config", "/srv/niko/config/production.yml"],
        "config": {
            "public_url": v["public_url"],
            "mongo_url": v["mongo_url"],
            "discord_token": v["discord_token"],
            "session_secret": v["session_secret"],
        },
        "memstats": {"Alloc": 41_289_112, "TotalAlloc": 918_442_992, "NumGC": 1204},
        "uptime_seconds": 734_912,
    }
    return json.dumps(document, indent=2) + "\n"


def agent_notes() -> str:
    v = values()
    return f"""# Niko — engineering notes

## Deploying

The dashboard is served by the Python supervisor, not by a Node server. Build
the site first, then restart the preview:

    npm --prefix web run build
    python3 src/supervisor.py --port 5173

Production deploys run from `main`. The deploy key lives in
`~/.ssh/id_rsa`; the CI token is in the pipeline settings. Do not put either in
a commit.

## Environment

Copy `.env.example` to `.env` and fill it in. The staging box reuses the
production Mongo cluster on a separate database, so ask for the connection
string rather than reading `.env.production` in the repo.

Known values from the last rotation (they are also in the vault under
`niko/prod`):

    DISCORD_BOT_TOKEN={v["discord_token"]}
    MONGODB_URL={v["mongo_url"]}
    SESSION_SECRET={v["session_secret"]}
    STRIPE_SECRET_KEY={v["stripe_secret"]}

## Notes

- The mute role denies `send messages`, `speak`, `add reactions`,
  `use application commands` and `use external apps`.
- Logs live in `data/logs/`; the owner page reads the in-memory ring.
- Never widen the API to `*` CORS. The dashboard is same-origin only.
"""


def _sql_values(rows: list[str]) -> str:
    return ",\n".join(rows) + ";\n"


def sql_dump() -> str:
    """A few hundred fake rows in a MySQL dump."""
    v = values()
    rng = random.Random(20261107)

    def date(year: int = 2026) -> str:
        return (
            f"{year}-{rng.randrange(1, 11):02d}-{rng.randrange(1, 29):02d} "
            f"{rng.randrange(0, 24):02d}:{rng.randrange(0, 60):02d}:"
            f"{rng.randrange(0, 60):02d}"
        )

    users = []
    for index in range(1, 141):
        username = (
            rng.choice(_FIRST) + rng.choice(_LAST)
            + (str(rng.randrange(1, 99)) if rng.random() < 0.4 else "")
        )
        email = f"{username}@{rng.choice(['example.com', 'example.net', 'mail.example.com'])}"
        users.append(
            f"({index},'{rng.randrange(10**17, 10**18)}','{username}',"
            f"'{email}','$2b$12${text(rng, 53, _HASH_ALPHABET)}',"
            f"'{rng.choice(_ROLES)}','203.0.113.{rng.randrange(2, 250)}',"
            f"'{date()}','{date()}')"
        )

    sessions = []
    for index in range(1, 49):
        sessions.append(
            f"({index},{rng.randrange(1, 141)},'{hex_id(rng, 64)}',"
            f"'203.0.113.{rng.randrange(2, 250)}',"
            f"'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',"
            f"'{date()}','{date(2027)}')"
        )

    payments = []
    for index in range(1, 31):
        provider = rng.choice(["stripe", "oxapay"])
        payments.append(
            f"({index},{rng.randrange(1, 141)},'{provider}',"
            f"'{rng.randrange(1, 500)}.00','{rng.choice(['EUR', 'USD', 'USDT'])}',"
            f"'{rng.choice(['succeeded', 'succeeded', 'refunded', 'pending'])}',"
            f"'{rng.choice(['cus_', 'pi_', 'ch_'])}{text(rng, 20, 'abcdefghijklmnopqrstuvwxyz0123456789')}',"
            f"'{date()}')"
        )

    api_keys = [
        (1, "dashboard", "niko_live_", v["jwt_secret"]),
        (2, "stripe", "sk_live_", v["stripe_secret"]),
        (3, "github", "ghp_", v["github_token"]),
        (4, "sendgrid", "SG.", v["sendgrid_key"]),
        (5, "openai", "sk-proj-", v["openai_key"]),
        (6, "cloudflare", None, v["cloudflare_token"]),
    ]
    keys = []
    for index, name, prefix, secret in api_keys:
        value = secret if prefix is None else secret
        keys.append(
            f"({index},'{name}','{prefix or ''}','{value}',"
            f"'{date()}','active')"
        )

    # The shared staff addresses are public on the site, so using them here
    # costs nothing and makes the dump read like a real export.
    staff = [
        (1, OWNER_EMAIL, "owner"),
        (2, ADMIN_EMAIL, "admin"),
        (3, SUPPORT_EMAIL, "support"),
        (4, SUPPORT_LEAD_EMAIL, "support-lead"),
    ]
    staff_rows = [
        f"({index},'{email}','{role}',"
        f"'$2b$12${text(rng, 53, _HASH_ALPHABET)}','{date()}')"
        for index, email, role in staff
    ]

    return f"""-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: {v["pg_host"]}    Database: {v["pg_db"]}
-- ------------------------------------------------------
-- Server version\t8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
SET TIME_ZONE='+00:00';

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `discord_id` varchar(32) NOT NULL,
  `username` varchar(64) NOT NULL,
  `email` varchar(190) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(32) NOT NULL DEFAULT 'member',
  `last_ip` varchar(45) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `last_login_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_discord_id_unique` (`discord_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `users` VALUES
{_sql_values(users)}

DROP TABLE IF EXISTS `sessions`;
CREATE TABLE `sessions` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `token` char(64) NOT NULL,
  `ip` varchar(45) NOT NULL,
  `user_agent` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL,
  `expires_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sessions_token_unique` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `sessions` VALUES
{_sql_values(sessions)}

DROP TABLE IF EXISTS `payments`;
CREATE TABLE `payments` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `provider` varchar(16) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `currency` char(3) NOT NULL,
  `status` varchar(16) NOT NULL,
  `provider_id` varchar(64) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `payments` VALUES
{_sql_values(payments)}

DROP TABLE IF EXISTS `api_keys`;
CREATE TABLE `api_keys` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `prefix` varchar(16) NOT NULL,
  `token` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL,
  `status` varchar(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `api_keys` VALUES
{_sql_values(keys)}

DROP TABLE IF EXISTS `staff_accounts`;
CREATE TABLE `staff_accounts` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `email` varchar(190) NOT NULL,
  `role` varchar(32) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `staff_accounts` VALUES
{_sql_values(staff_rows)}

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
"""


def private_key(kind: str = "rsa") -> str:
    if kind == "ed25519":
        return pem(random.Random(20261108), "OPENSSH PRIVATE KEY", 22)
    return pem(random.Random(20261109), "RSA PRIVATE KEY", 28)


def backup_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(".env", dotenv())
        archive.writestr("dump.sql", sql_dump())
        archive.writestr("service-account.json", json.dumps(
            {
                "type": "service_account",
                "project_id": values()["gcp_project"],
                "private_key": values()["gcp_private_key"],
                "client_email": values()["gcp_client_email"],
            },
            indent=2,
        ))
        archive.writestr("docker-compose.yml", "services: {}\n")
        archive.writestr("README.txt", "Nightly backup — /srv/niko/backups\n")
    return buffer.getvalue()
