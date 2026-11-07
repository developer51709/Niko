"""Decoy files for the paths credential crawlers request.

The deployment serves none of these files, and none of them would hold a real
secret if it did: every value comes from ``values.py``, which derives the whole
fake environment from one fixed seed. The set is consistent on
purpose — the PostgreSQL password in ``.env`` is the one in
``docker-compose.yml``, ``.pgpass`` and ``dump.sql`` — because a mismatch
between two leaked files is the quickest way to tell a decoy from a real leak.

This package is part of the public repository, and ``README.md`` next to this
file explains it. Anyone who wants to check whether a credential found on the
site is real can read the code, re-run the generator, and get the same
strings::

    python -m webapp.honeypot --list
    python -m webapp.honeypot .env

Nothing here reads the environment, imports the application's configuration,
or touches the network.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from typing import Callable

from . import configs, env, stores

#: Mime type by file extension; anything else is plain text.
_MIMETYPES = {
    ".json": "application/json",
    ".js": "application/javascript",
    ".mjs": "application/javascript",
    ".html": "text/html; charset=utf-8",
    ".xml": "application/xml",
    ".zip": "application/zip",
    ".yml": "application/yaml",
    ".yaml": "application/yaml",
    ".md": "text/markdown; charset=utf-8",
    ".swp": "application/octet-stream",
}


#: Paths with no telling extension, mostly the Spring actuator documents.
_EXPLICIT_MIMETYPES = {
    "/.kube/config": "application/yaml",
    "/actuator/env": "application/json",
    "/actuator/configprops": "application/json",
    "/debug/vars": "application/json",
}


def _mimetype(path: str) -> str:
    if path in _EXPLICIT_MIMETYPES:
        return _EXPLICIT_MIMETYPES[path]
    suffix = "." + path.rsplit(".", 1)[-1].lower()
    return _MIMETYPES.get(suffix, "text/plain; charset=utf-8")


@lru_cache(maxsize=1)
def _files() -> dict[str, Callable[[], object]]:
    """Every decoy path and the function that renders it."""
    files: dict[str, Callable[[], object]] = {}

    for name, variant in env.DOTENV_FILES.items():
        files["/" + name] = lambda variant=variant: env.dotenv(variant)
    files["/.env.swp"] = env.vim_swap

    for name in configs.FRONTEND_FILES:
        files["/" + name] = lambda name=name: configs.frontend_config(name)
    for name in configs.JSON_FILES:
        files["/" + name] = lambda name=name: configs.json_document(name)
    for name in configs.PHP_FILES:
        files["/" + name] = lambda name=name: configs.php_file(name)
    for name in configs.YAML_FILES:
        files["/" + name] = lambda name=name: configs.yaml_file(name)
    for name in configs.CI_FILES:
        files["/" + name] = lambda name=name: configs.ci_file(name)

    files.update({
        # Version control
        "/.git/config": stores.git_config,
        "/.git/credentials": stores.git_credentials,
        "/.git-credentials": stores.git_credentials,
        "/.git/HEAD": stores.git_head,
        "/.gitignore": stores.gitignore,
        "/.svn/entries": lambda: "12\n",
        "/.hg/hgrc": lambda: "[paths]\ndefault = https://hg.niko-internal.example/niko\n",
        "/.htaccess": stores.htaccess,
        # Shell and credential stores
        "/.aws/credentials": stores.aws_credentials,
        "/.aws/config": stores.aws_config,
        "/.npmrc": stores.npmrc,
        "/.pypirc": stores.pypirc,
        "/.netrc": stores.netrc,
        "/.pgpass": stores.pgpass,
        "/.my.cnf": stores.my_cnf,
        "/.vault-token": stores.vault_token,
        "/.htpasswd": stores.htpasswd,
        "/.bash_history": stores.bash_history,
        "/.zsh_history": stores.zsh_history,
        "/id_rsa": stores.private_key,
        "/.ssh/id_rsa": stores.private_key,
        "/.ssh/id_ed25519": lambda: stores.private_key("ed25519"),
        # Build and framework configuration
        "/package.json": stores.package_json,
        "/composer.json": stores.composer_json,
        "/babel.config.js": stores.babel_config,
        "/webpack.config.js": stores.webpack_config,
        "/next.config.js": stores.next_config,
        "/next.config.mjs": stores.next_config,
        "/nuxt.config.js": stores.nuxt_config,
        "/nuxt.config.ts": stores.nuxt_config,
        "/vue.config.js": stores.vue_config,
        "/.next/server/app/page.js": stores.next_server_page,
        "/_next/static/chunks/main.js": stores.next_chunk,
        "/Dockerfile": stores.dockerfile,
        "/wrangler.toml": stores.wrangler_toml,
        "/.dev.vars": stores.dev_vars,
        "/netlify.toml": stores.netlify_toml,
        # Application configuration
        "/settings.py": stores.settings_py,
        "/local_settings.py": stores.settings_py,
        "/settings/production.py": stores.settings_py,
        "/celeryconfig.py": stores.celeryconfig,
        "/alembic.ini": stores.alembic_ini,
        "/application.properties": stores.application_properties,
        "/terraform.tfvars": stores.terraform_tfvars,
        "/phpunit.xml": stores.phpunit_xml,
        "/web.config": stores.web_config,
        "/storage/logs/laravel.log": stores.laravel_log,
        # Server pages a scanner greps for versions and environment
        "/phpinfo.php": stores.phpinfo,
        "/wp-login.php": stores.wp_login,
        "/xmlrpc.php": stores.xmlrpc,
        "/server-status": stores.server_status,
        "/actuator/env": stores.actuator_env,
        "/actuator/configprops": stores.actuator_configprops,
        "/debug/vars": stores.debug_vars,
        # Agent instructions, a popular target since coding agents took over
        "/CLAUDE.md": stores.agent_notes,
        "/AGENTS.md": stores.agent_notes,
        # Backups
        "/dump.sql": stores.sql_dump,
        "/db.sql": stores.sql_dump,
        "/database.sql": stores.sql_dump,
        "/backup.sql": stores.sql_dump,
        "/backup.zip": stores.backup_zip,
        "/www.zip": stores.backup_zip,
    })
    return files


def paths() -> tuple[str, ...]:
    """Every path the honeypot answers, in a stable order."""
    return tuple(sorted(_files()))


@lru_cache(maxsize=None)
def _render(path: str) -> tuple[str | bytes, str]:
    """Render one decoy once; the strings never change between requests."""
    return _files()[path](), _mimetype(path)


def body_for(path: str) -> tuple[str | bytes, str] | None:
    """The decoy payload and mime type for ``path``, or ``None`` if unhandled."""
    if path not in _files():
        return None
    return _render(path)


def main(argv: list[str] | None = None) -> int:
    """Print a decoy file, so the strings can be checked without the server."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments[0] in {"-l", "--list"}:
        for path in paths():
            print(path)
        return 0
    path = arguments[0]
    if not path.startswith("/"):
        path = "/" + path
    payload = body_for(path)
    if payload is None:
        print(f"{path} is not a decoy path; try --list", file=sys.stderr)
        return 2
    data, _ = payload
    if isinstance(data, bytes):
        sys.stdout.buffer.write(data)
    else:
        sys.stdout.write(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
