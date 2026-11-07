"""Configuration decoy files: frontend bundles, JSON, PHP, YAML and CI.

Every document is fake. The values come from ``values.py`` so a key
that appears in two files is the same key, which is what makes the set hold up
to a second look.
"""

from __future__ import annotations

import json

from .values import base64_text, values

#: Frontend config files a scanner asks for when it expects a bundled key.
FRONTEND_FILES = (
    "config.js",
    "config.ts",
    "config.json",
    "config/config.js",
    "config/config.json",
    "config/environment.js",
    "config/production.json",
    "config/development.json",
    "src/config.js",
    "src/config.ts",
    "src/config/index.js",
    "app/config.js",
    "assets/config.js",
    "static/config.js",
    "js/config.js",
    "js/app.js",
    "env.js",
    ".env.js",
    "environment.js",
    "environment.ts",
    "environment.prod.ts",
    "src/environments/environment.ts",
    "src/environments/environment.prod.ts",
)

JSON_FILES = (
    "settings.json",
    "secrets.json",
    "credentials.json",
    "auth.json",
    "key.json",
    "service-account.json",
    "firebaseServiceAccountKey.json",
    "firebase.json",
    "database.json",
    "vercel.json",
    "sftp-config.json",
    "appsettings.json",
    "appsettings.Production.json",
    "appsettings.Development.json",
    "appsettings.secrets.json",
    ".mcp.json",
    ".cursor/mcp.json",
    ".vscode/mcp.json",
    ".amazonq/mcp.json",
    ".continue/config.json",
    ".codex/auth.json",
    ".claude/.credentials.json",
    ".azure/accessTokens.json",
    ".azure/msal_token_cache.json",
    ".config/gcloud/application_default_credentials.json",
    ".terraform.d/credentials.tfrc.json",
    ".composer/auth.json",
    ".docker/config.json",
    ".config/containers/auth.json",
    "terraform.tfstate",
)

PHP_FILES = (
    "wp-config.php",
    "wp-config.php.bak",
    "config.php",
    "config.php.bak",
    "configuration.php",
    "config.inc.php",
    "includes/config.php",
    "inc/config.php",
    "admin/config.php",
    "config/settings.inc.php",
    "config/database.php",
    "settings.php",
)

YAML_FILES = (
    "config.yml",
    "config.yaml",
    "database.yml",
    "parameters.yml",
    "secrets.yml",
    "application.yml",
    "application-prod.yml",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "docker-compose.dev.yml",
    "docker-compose.override.yml",
    "values.yaml",
    "secret.yaml",
    "serverless.yml",
    "elasticsearch.yml",
    "litellm_config.yaml",
    "litellm.yaml",
    "proxy_config.yaml",
    "settings.yml",
    ".kube/config",
)

CI_FILES = (
    ".gitlab-ci.yml",
    "Jenkinsfile",
    ".github/workflows/deploy.yml",
    ".github/workflows/main.yml",
    ".circleci/config.yml",
    ".travis.yml",
)


def frontend_config(name: str) -> str:
    """A browser bundle's config object with the deployment's keys in it."""
    v = values()
    config = {
        "production": True,
        "apiBase": v["public_url"] + "/api",
        "discord": {
            "clientId": v["discord_id"],
            "clientSecret": v["discord_client_secret"],
            "redirectUri": v["public_url"] + "/auth/callback",
        },
        "database": {
            "url": v["mongo_url"],
            "name": v["mongo_db"],
            "username": v["mongo_user"],
            "password": v["mongo_password"],
        },
        "aws": {
            "accessKeyId": v["aws_key"],
            "secretAccessKey": v["aws_secret"],
            "region": v["aws_region"],
            "bucket": v["s3_bucket"],
        },
        "stripe": {
            "publishableKey": v["stripe_publishable"],
            "secretKey": v["stripe_secret"],
        },
        "maps": {"apiKey": v["google_maps_key"]},
        "sentry": {"dsn": v["sentry_dsn"], "tracesSampleRate": 0.1},
        "sessionSecret": v["session_secret"],
        "build": {"commit": "9f31c2a", "builtAt": "2026-10-30T21:14:08Z"},
    }
    if name.endswith(".ts"):
        return "export const environment = " + json.dumps(config, indent=2) + ";\n"
    if name.endswith(".json"):
        return json.dumps(config, indent=2) + "\n"
    return "window.__NIKO_CONFIG__ = " + json.dumps(config, indent=2) + ";\n"


def _gcp_service_account() -> dict:
    v = values()
    return {
        "type": "service_account",
        "project_id": v["gcp_project"],
        "private_key_id": v["gcp_key_id"],
        "private_key": v["gcp_private_key"],
        "client_email": v["gcp_client_email"],
        "client_id": v["gcp_client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": (
            "https://www.googleapis.com/robot/v1/metadata/x509/"
            + v["gcp_client_email"].replace("@", "%40")
        ),
        "universe_domain": "googleapis.com",
    }


def _mcp_servers() -> dict:
    v = values()
    return {
        "mcpServers": {
            "postgres": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-postgres",
                    v["postgres_url"],
                ],
                "env": {"PGSSLMODE": "require"},
            },
            "github": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                         "ghcr.io/github/github-mcp-server"],
                "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": v["github_token"]},
            },
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/srv/niko"],
            },
            "sentry": {
                "command": "npx",
                "args": ["-y", "@sentry/mcp-server"],
                "env": {
                    "SENTRY_AUTH_TOKEN": v["sentry_dsn"],
                    "SENTRY_ORG": "niko",
                },
            },
        }
    }


def _vercel() -> dict:
    v = values()
    return {
        "version": 2,
        "name": "niko-dashboard",
        "builds": [{"src": "api/index.py", "use": "@vercel/python"}],
        "env": {
            "DISCORD_BOT_TOKEN": v["discord_token"],
            "MONGODB_URL": v["mongo_url"],
            "SESSION_SECRET": v["session_secret"],
            "STRIPE_SECRET_KEY": v["stripe_secret"],
        },
        "rewrites": [{"source": "/(.*)", "destination": "/index.html"}],
    }


def _appsettings(environment: str) -> dict:
    v = values()
    document = {
        "ConnectionStrings": {
            "DefaultConnection": (
                f"Server={v['mysql_host']};Port=3306;Database={v['mysql_db']};"
                f"Uid={v['mysql_user']};Pwd={v['mysql_password']};"
                "SslMode=Required;"
            ),
            "Mongo": v["mongo_url"],
        },
        "Jwt": {
            "Issuer": v["public_url"],
            "Audience": "niko-dashboard",
            "Key": v["jwt_secret"],
        },
        "SendGrid": {"ApiKey": v["sendgrid_key"], "From": v["admin_email"]},
        "Serilog": {
            "MinimumLevel": {"Default": "Information"},
            "WriteTo": [{"Name": "Console"}],
        },
    }
    if environment != "Production":
        document["DetailedErrors"] = True
        document["DevSeedAdmin"] = {
            "Email": v["admin_email"],
            "Password": v["admin_password"],
        }
    return document


def json_document(name: str) -> str:
    """The decoy JSON for one path."""
    v = values()
    if name in {"service-account.json", "key.json", "firebaseServiceAccountKey.json"}:
        document = _gcp_service_account()
    elif name == "auth.json":
        document = {
            "https://registry.npmjs.org/": {"token": v["npm_token"]},
            "https://npm.pkg.github.com/": {"token": v["github_token"]},
        }
    elif name.endswith("mcp.json"):
        document = _mcp_servers()
    elif name == ".continue/config.json":
        document = {
            "models": [
                {
                    "title": "Niko ops",
                    "provider": "openai",
                    "model": "gpt-5.1",
                    "apiKey": v["openai_key"],
                    "apiBase": "https://api.openai.com/v1",
                },
                {
                    "title": "Claude",
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-5",
                    "apiKey": v["anthropic_key"],
                },
            ],
            "contextProviders": [{"name": "code"}, {"name": "docs"}],
            "allowAnonymousTelemetry": False,
        }
    elif name == ".codex/auth.json":
        document = {
            "OPENAI_API_KEY": v["openai_key"],
            "tokens": {
                "id_token": v["jwt_access"],
                "access_token": v["jwt_access"],
                "refresh_token": v["jwt_refresh"],
                "account_id": v["discord_id"],
            },
            "last_refresh": "2026-11-06T22:41:19.402Z",
        }
    elif name == ".claude/.credentials.json":
        document = {
            "claudeAiOauth": {
                "accessToken": "sk-ant-oat01-" + v["anthropic_key"][16:],
                "refreshToken": "sk-ant-ort01-" + v["jwt_secret"],
                "expiresAt": 1793404800000,
                "scopes": ["user:inference", "user:profile"],
                "subscriptionType": "max",
            },
            "organizationUuid": v["gcp_client_id"],
        }
    elif name == ".azure/accessTokens.json":
        document = [
            {
                "accessToken": v["jwt_access"],
                "refreshToken": v["jwt_refresh"],
                "expiresOn": "2026-12-31 23:59:59.000000",
                "resource": "https://management.azure.com/",
                "tokenType": "Bearer",
                "userId": v["admin_email"],
            }
        ]
    elif name == ".azure/msal_token_cache.json":
        document = {
            "AccessToken": {
                "https://management.azure.com": {
                    "credential_type": "AccessToken",
                    "secret": v["jwt_access"],
                    "home_account_id": v["discord_id"] + ".live",
                    "environment": "login.microsoftonline.com",
                    "client_id": v["gcp_client_id"],
                }
            },
            "RefreshToken": {
                "niko-prod": {
                    "credential_type": "RefreshToken",
                    "secret": v["jwt_refresh"],
                    "home_account_id": v["discord_id"] + ".live",
                }
            },
            "Account": {
                "niko-prod": {
                    "home_account_id": v["discord_id"] + ".live",
                    "username": v["admin_email"],
                    "environment": "login.microsoftonline.com",
                }
            },
        }
    elif name.endswith("application_default_credentials.json"):
        document = {
            "type": "authorized_user",
            "client_id": v["gcp_client_id"] + ".apps.googleusercontent.com",
            "client_secret": v["gcp_client_secret"],
            "refresh_token": v["gcp_refresh_token"],
            "quota_project_id": v["gcp_project"],
        }
    elif name.endswith("credentials.tfrc.json"):
        document = {
            "credentials": {
                "app.terraform.io": {"token": v["atlas_token"]},
            }
        }
    elif name == ".composer/auth.json":
        document = {
            "github-oauth": {"github.com": v["github_token"]},
            "http-basic": {
                "repo.packagist.com": {
                    "username": v["docker_user"],
                    "password": v["docker_password"],
                }
            },
            "gitlab-token": {"gitlab.com": v["github_fine_token"]},
        }
    elif name in {".docker/config.json", ".config/containers/auth.json"}:
        document = {
            "auths": {
                "https://index.docker.io/v1/": {
                    "auth": base64_text(
                        f"{v['docker_user']}:{v['docker_password']}"
                    ),
                    "email": v["admin_email"],
                },
                "ghcr.io": {
                    "auth": base64_text(f"deploy:{v['github_token']}"),
                },
            },
            "credsStore": "desktop",
        }
    elif name == "terraform.tfstate":
        document = {
            "version": 4,
            "terraform_version": "1.9.8",
            "serial": 41,
            "lineage": v["gcp_key_id"],
            "outputs": {
                "db_password": {"value": v["pg_password"], "type": "string"},
                "discord_token": {"value": v["discord_token"], "type": "string"},
                "s3_bucket": {"value": v["s3_bucket"], "type": "string"},
            },
            "resources": [
                {
                    "mode": "managed",
                    "type": "aws_db_instance",
                    "name": "primary",
                    "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
                    "instances": [{
                        "schema_version": 2,
                        "attributes": {
                            "id": "niko-prod-primary",
                            "engine": "postgres",
                            "engine_version": "16.4",
                            "instance_class": "db.r6g.large",
                            "username": v["pg_user"],
                            "password": v["pg_password"],
                            "address": v["pg_host"],
                            "port": 5432,
                            "allocated_storage": 200,
                        },
                    }],
                },
                {
                    "mode": "managed",
                    "type": "aws_iam_access_key",
                    "name": "deploy",
                    "instances": [{
                        "schema_version": 0,
                        "attributes": {
                            "id": v["aws_key"],
                            "secret": v["aws_secret"],
                            "user": "niko-deployer",
                        },
                    }],
                },
            ],
            "check_results": None,
        }
    elif name == "firebase.json":
        document = {
            "hosting": {
                "public": "web/dist",
                "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
                "rewrites": [{"source": "**", "destination": "/index.html"}],
            },
            "functions": {"source": "functions", "runtime": "nodejs20"},
            "database": {"rules": "database.rules.json"},
        }
    elif name == "database.json":
        document = {
            "default": {
                "host": v["pg_host"],
                "port": 5432,
                "database": v["pg_db"],
                "user": v["pg_user"],
                "password": v["pg_password"],
                "ssl": True,
            },
            "readonly": {
                "host": "read." + v["pg_host"],
                "database": v["pg_db"],
                "user": "niko_reporting",
                "password": v["pg_password_old"],
            },
        }
    elif name == "sftp-config.json":
        document = {
            "type": "sftp",
            "save_before_upload": True,
            "upload_on_save": False,
            "host": "203.0.113.24",
            "user": "deploy",
            "port": 2222,
            "remote_path": "/srv/niko/current",
            "password": v["admin_password"],
            "ssh_key_file": "/home/deploy/.ssh/id_rsa",
            "connect_timeout": 10,
        }
    elif name.startswith("appsettings"):
        environment = "Production"
        if "Development" in name:
            environment = "Development"
        elif "secrets" in name:
            environment = "Secrets"
        document = _appsettings(environment)
    elif name == "vercel.json":
        document = _vercel()
    elif name == "settings.json":
        document = {
            "app": {"name": "niko-dashboard", "baseUrl": v["public_url"]},
            "database": {"url": v["mongo_url"], "database": v["mongo_db"]},
            "discord": {
                "token": v["discord_token"],
                "clientId": v["discord_id"],
                "clientSecret": v["discord_client_secret"],
            },
            "cache": {"url": v["redis_url"]},
            "logging": {"level": "debug", "sentry": v["sentry_dsn"]},
        }
    elif name == "secrets.json":
        document = {
            "discordBotToken": v["discord_token"],
            "sessionSecret": v["session_secret"],
            "jwtSecret": v["jwt_secret"],
            "encryptionKey": v["encryption_key"],
            "aws": {"key": v["aws_key"], "secret": v["aws_secret"]},
            "stripe": {
                "secret": v["stripe_secret"],
                "webhook": v["stripe_webhook"],
            },
            "smtp": {"user": v["smtp_user"], "password": v["smtp_password"]},
        }
    elif name == "credentials.json":
        document = {
            "discord": {"token": v["discord_token"]},
            "mongodb": {
                "uri": v["mongo_url"],
                "database": v["mongo_db"],
                "user": v["mongo_user"],
                "password": v["mongo_password"],
            },
            "postgres": {
                "uri": v["postgres_url"],
                "user": v["pg_user"],
                "password": v["pg_password"],
            },
            "aws": {"accessKeyId": v["aws_key"], "secretAccessKey": v["aws_secret"]},
            "github": {"token": v["github_token"]},
            "stripe": {"secretKey": v["stripe_secret"]},
            "google": {"serviceAccount": "secrets/service-account.json"},
        }
    else:  # settings.json and anything else that only needs app config
        document = {
            "app": {"baseUrl": v["public_url"], "instance": v["instance"]},
            "mongo": {"url": v["mongo_url"]},
            "session": {"secret": v["session_secret"]},
        }
    return json.dumps(document, indent=2) + "\n"


def php_file(name: str) -> str:
    """A PHP application's database configuration, left on disk by mistake."""
    v = values()
    if name.startswith("wp-config"):
        salts = "\n".join(
            f"define( 'AUTH_KEY_{index}', '{v['jwt_secret'][index * 4:index * 4 + 48]}' );"
            for index in range(1, 5)
        )
        password = v["pg_password_old"] if name.endswith(".bak") else v["mysql_password"]
        return f"""<?php
/**
 * The base configuration for WordPress
 *
 * @package WordPress
 */

define( 'DB_NAME', '{v["mysql_db"]}' );
define( 'DB_USER', '{v["mysql_user"]}' );
define( 'DB_PASSWORD', '{password}' );
define( 'DB_HOST', '{v["mysql_host"]}' );
define( 'DB_CHARSET', 'utf8mb4' );
define( 'DB_COLLATE', '' );

{salts}

$table_prefix = 'wp_';

define( 'WP_DEBUG', false );
define( 'WP_AUTO_UPDATE_CORE', true );
define( 'DISALLOW_FILE_EDIT', true );
define( 'AUTH_SALT_LEGACY', '{v["session_secret"]}' );

if ( ! defined( 'ABSPATH' ) ) {{
	define( 'ABSPATH', __DIR__ . '/' );
}}
require_once ABSPATH . 'wp-settings.php';
"""
    if name in {"configuration.php", "config.inc.php", "settings.php"}:
        return f"""<?php
// Generated by the installer. Not web-accessible in a correct deployment.
$host = '{v["mysql_host"]}';
$user = '{v["mysql_user"]}';
$password = '{v["mysql_password"]}';
$database = '{v["mysql_db"]}';
$mail_user = '{v["smtp_user"]}';
$mail_pass = '{v["smtp_password"]}';
$secret = '{v["session_secret"]}';
$app_key = 'base64:{base64_text(v["encryption_key"])}';
$stripe = '{v["stripe_secret"]}';
$smtp_port = 587;
$debug = false;
"""
    if name == "config/database.php":
        return f"""<?php

return [
    'default' => 'mysql',
    'connections' => [
        'mysql' => [
            'driver' => 'mysql',
            'host' => '{v["mysql_host"]}',
            'port' => '3306',
            'database' => '{v["mysql_db"]}',
            'username' => '{v["mysql_user"]}',
            'password' => '{v["mysql_password"]}',
            'charset' => 'utf8mb4',
            'collation' => 'utf8mb4_unicode_ci',
            'prefix' => '',
        ],
        'pgsql' => [
            'driver' => 'pgsql',
            'url' => '{v["postgres_url"]}',
            'sslmode' => 'require',
        ],
    ],
    'redis' => [
        'client' => 'phpredis',
        'default' => [
            'url' => '{v["redis_url"]}',
        ],
    ],
];
"""
    return f"""<?php
// Shared configuration for the legacy admin panel.
$db_host = '{v["mysql_host"]}';
$db_user = '{v["mysql_user"]}';
$db_pass = '{v["mysql_password"]}';
$db_name = '{v["mysql_db"]}';
$api_key = '{v["google_maps_key"]}';
$github_token = '{v["github_token"]}';
$session_key = '{v["session_secret"]}';
"""


def yaml_file(name: str) -> str:
    """A Docker Compose, Spring, Rails, k8s or tool configuration decoy."""
    v = values()
    if name.startswith("docker-compose"):
        return f"""version: "3.9"

x-common-env: &common-env
  NODE_ENV: production
  PUBLIC_URL: {v["public_url"]}
  MONGODB_URL: {v["mongo_url"]}
  MONGODB_DATABASE: {v["mongo_db"]}
  POSTGRES_URL: {v["postgres_url"]}
  REDIS_URL: {v["redis_url"]}
  SESSION_SECRET: {v["session_secret"]}
  AWS_ACCESS_KEY_ID: {v["aws_key"]}
  AWS_SECRET_ACCESS_KEY: {v["aws_secret"]}
  STRIPE_SECRET_KEY: {v["stripe_secret"]}

services:
  mongo:
    image: mongo:7
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: {v["mongo_user"]}
      MONGO_INITDB_ROOT_PASSWORD: {v["mongo_password"]}
    volumes:
      - mongo-data:/data/db
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: {v["pg_user"]}
      POSTGRES_PASSWORD: {v["pg_password"]}
      POSTGRES_DB: {v["pg_db"]}
    volumes:
      - pg-data:/var/lib/postgresql/data
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass {v["redis_password"]}
  dashboard:
    build: .
    env_file: .env
    environment: *common-env
    ports:
      - "5000:5000"
    depends_on:
      - mongo
      - redis

volumes:
  mongo-data:
  pg-data:
"""
    if name == ".kube/config":
        return f"""apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: {base64_text("niko-ca-" + v["gcp_key_id"])}
    server: https://k8s.niko-internal.example:6443
  name: niko-prod
contexts:
- context:
    cluster: niko-prod
    namespace: niko
    user: deployer
  name: deployer@niko-prod
current-context: deployer@niko-prod
users:
- name: deployer
  user:
    token: {v["jwt_access"]}
"""
    if name in {"litellm_config.yaml", "litellm.yaml", "proxy_config.yaml"}:
        return f"""model_list:
  - model_name: gpt-5.1
    litellm_params:
      model: openai/gpt-5.1
      api_key: {v["openai_key"]}
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-5
      api_key: {v["anthropic_key"]}
  - model_name: groq-fast
    litellm_params:
      model: groq/llama-3.3-70b
      api_key: {v["groq_key"]}

general_settings:
  master_key: {v["jwt_secret"]}
  database_url: {v["postgres_url"]}
  store_model_in_db: true
"""
    if name.startswith("application"):
        return f"""server:
  port: 8080
  forward-headers-strategy: framework
spring:
  datasource:
    url: jdbc:postgresql://{v["pg_host"]}:5432/{v["pg_db"]}
    username: {v["pg_user"]}
    password: {v["pg_password"]}
  data:
    redis:
      host: {v["redis_host"]}
      password: {v["redis_password"]}
  security:
    oauth2:
      client:
        registration:
          discord:
            client-id: {v["discord_id"]}
            client-secret: {v["discord_client_secret"]}
management:
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    env:
      show-values: ALWAYS
jwt:
  signing-key: {v["jwt_secret"]}
"""
    if name == "secret.yaml":
        return f"""apiVersion: v1
kind: Secret
metadata:
  name: niko-secrets
  namespace: niko
type: Opaque
data:
  discord-token: {base64_text(v["discord_token"])}
  mongodb-url: {base64_text(v["mongo_url"])}
  session-secret: {base64_text(v["session_secret"])}
  stripe-secret: {base64_text(v["stripe_secret"])}
  aws-secret: {base64_text(v["aws_secret"])}
"""
    if name == "values.yaml":
        return f"""replicaCount: 2

image:
  repository: ghcr.io/developer51709/niko
  tag: "2026.10.30"
  pullPolicy: IfNotPresent

env:
  PUBLIC_URL: {v["public_url"]}
  MONGODB_URL: {v["mongo_url"]}
  SESSION_SECRET: {v["session_secret"]}
  DISCORD_BOT_TOKEN: {v["discord_token"]}

imagePullSecrets:
  - name: ghcr-token
  - token: {v["github_token"]}

resources:
  limits:
    cpu: 500m
    memory: 1Gi
"""
    if name == "serverless.yml":
        return f"""service: niko-api
frameworkVersion: "3"

provider:
  name: aws
  runtime: nodejs20.x
  region: {v["aws_region"]}
  environment:
    DISCORD_BOT_TOKEN: {v["discord_token"]}
    MONGODB_URL: {v["mongo_url"]}
    AWS_ACCESS_KEY_ID: {v["aws_key"]}
    AWS_SECRET_ACCESS_KEY: {v["aws_secret"]}
    STRIPE_SECRET_KEY: {v["stripe_secret"]}

functions:
  api:
    handler: handler.main
    events:
      - httpApi: "*"
  worker:
    handler: worker.run
    timeout: 300
"""
    if name == "elasticsearch.yml":
        return f"""cluster.name: niko-search
node.name: es-01
network.host: 0.0.0.0
http.port: 9200
discovery.seed_hosts: ["es-01.internal:9300", "es-02.internal:9300"]

xpack.security.enabled: true
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: certs/elastic-certificates.p12
xpack.security.http.ssl.keystore.secure_password: {v["admin_password"]}
xpack.security.transport.ssl.keystore.secure_password: {v["admin_password"]}
bootstrap.memory_lock: true
"""
    if name == "database.yml":
        return f"""default: &default
  adapter: mysql2
  encoding: utf8mb4
  pool: 5
  username: {v["mysql_user"]}
  password: {v["mysql_password"]}
  host: {v["mysql_host"]}

production:
  <<: *default
  database: {v["mysql_db"]}
  ssl_mode: required

staging:
  <<: *default
  database: {v["mysql_db"]}_staging
"""
    if name == "parameters.yml":
        return f"""parameters:
    database_driver: pdo_mysql
    database_host: {v["mysql_host"]}
    database_port: 3306
    database_name: {v["mysql_db"]}
    database_user: {v["mysql_user"]}
    database_password: {v["mysql_password"]}
    mailer_transport: smtp
    mailer_host: {v["smtp_host"]}
    mailer_user: {v["smtp_user"]}
    mailer_password: {v["smtp_password"]}
    secret: {v["session_secret"]}
    stripe_secret_key: {v["stripe_secret"]}
"""
    if name == "secrets.yml":
        return f"""production:
  secret_key_base: {v["session_secret"]}
  jwt_secret: {v["jwt_secret"]}
  postgres_url: {v["postgres_url"]}
  mongodb_url: {v["mongo_url"]}
  redis_url: {v["redis_url"]}
  aws_access_key_id: {v["aws_key"]}
  aws_secret_access_key: {v["aws_secret"]}
  stripe_secret_key: {v["stripe_secret"]}
  sendgrid_api_key: {v["sendgrid_key"]}
  github_token: {v["github_token"]}

staging:
  secret_key_base: {v["session_secret"][::-1]}
  postgres_url: postgresql://{v["pg_user"]}:{v["pg_password_old"]}@{v["pg_host"]}/niko_staging
"""
    return f"""# Application configuration
app:
  name: niko
  url: {v["public_url"]}
  instance: {v["instance"]}

database:
  host: {v["pg_host"]}
  port: 5432
  name: {v["pg_db"]}
  user: {v["pg_user"]}
  password: {v["pg_password"]}

cache:
  url: {v["redis_url"]}

discord:
  client_id: {v["discord_id"]}
  client_secret: {v["discord_client_secret"]}

mail:
  host: {v["smtp_host"]}
  user: {v["smtp_user"]}
  password: {v["smtp_password"]}

session:
  secret: {v["session_secret"]}
"""


def ci_file(name: str) -> str:
    """A pipeline definition with the deployment secrets in it."""
    v = values()
    if name == "Jenkinsfile":
        return f"""pipeline {{
    agent any
    environment {{
        DISCORD_BOT_TOKEN = '{v["discord_token"]}'
        MONGODB_URL       = '{v["mongo_url"]}'
        AWS_ACCESS_KEY_ID = '{v["aws_key"]}'
        AWS_SECRET_ACCESS_KEY = '{v["aws_secret"]}'
        REGISTRY_PASSWORD = '{v["docker_password"]}'
    }}
    stages {{
        stage('Test') {{
            steps {{ sh 'pytest -q' }}
        }}
        stage('Deploy') {{
            steps {{
                sh 'docker build -t ghcr.io/developer51709/niko:$BUILD_NUMBER .'
                sh 'docker push ghcr.io/developer51709/niko:$BUILD_NUMBER'
            }}
        }}
    }}
}}
"""
    if name.startswith(".github/workflows"):
        return f"""name: deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      DISCORD_BOT_TOKEN: {v["discord_token"]}
      MONGODB_URL: {v["mongo_url"]}
      AWS_ACCESS_KEY_ID: {v["aws_key"]}
      AWS_SECRET_ACCESS_KEY: {v["aws_secret"]}
      STRIPE_SECRET_KEY: {v["stripe_secret"]}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest -q
      - name: Deploy
        run: sh ./scripts/deploy.sh
        env:
          DEPLOY_KEY: {v["github_token"]}
"""
    if name == ".circleci/config.yml":
        return f"""version: 2.1

orbs:
  python: circleci/python@2.1

jobs:
  build:
    docker:
      - image: cimg/python:3.12
        environment:
          MONGODB_URL: {v["mongo_url"]}
          DISCORD_BOT_TOKEN: {v["discord_token"]}
          SESSION_SECRET: {v["session_secret"]}
    steps:
      - checkout
      - run: pip install -r requirements.txt
      - run: pytest -q
      - run: docker login -u {v["docker_user"]} -p {v["docker_password"]} ghcr.io

workflows:
  test-and-deploy:
    jobs:
      - build
"""
    if name == ".travis.yml":
        return f"""language: python
python:
  - "3.12"
env:
  global:
    - DISCORD_BOT_TOKEN={v["discord_token"]}
    - MONGODB_URL={v["mongo_url"]}
    - AWS_ACCESS_KEY_ID={v["aws_key"]}
    - AWS_SECRET_ACCESS_KEY={v["aws_secret"]}
install:
  - pip install -r requirements.txt
script:
  - pytest -q
deploy:
  provider: script
  script: sh ./scripts/deploy.sh
  on:
    branch: main
"""
    return f"""stages:
  - test
  - deploy

variables:
  DISCORD_BOT_TOKEN: "{v["discord_token"]}"
  MONGODB_URL: "{v["mongo_url"]}"
  POSTGRES_URL: "{v["postgres_url"]}"
  AWS_ACCESS_KEY_ID: "{v["aws_key"]}"
  AWS_SECRET_ACCESS_KEY: "{v["aws_secret"]}"
  DOCKER_PASSWORD: "{v["docker_password"]}"

test:
  image: python:3.12
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest -q

deploy:
  image: docker:27
  stage: deploy
  script:
    - echo "$DOCKER_PASSWORD" | docker login ghcr.io -u {v["docker_user"]} --password-stdin
    - docker build -t ghcr.io/developer51709/niko:$CI_COMMIT_SHORT_SHA .
    - docker push ghcr.io/developer51709/niko:$CI_COMMIT_SHORT_SHA
  only:
    - main
"""
