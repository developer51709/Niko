"""Friendly responses for paths crawlers probe when hunting for secrets.

Automated scanners request well-known configuration, backup, and VCS paths on
every host they can reach. Niko's deployment does not serve any of those files,
so without these routes the SPA catch-all answers with the React shell — which
looks like a miss. Each route below answers as a decoy file that explains where
the real source lives and how to report a vulnerability instead.
"""

from flask import Response, request

from . import server as _server

# Kept here rather than imported from config.links so the message has no
# dependency on the bot's runtime configuration.
_GITHUB_REPO = "https://github.com/developer51709/Niko"
_SUPPORT_SERVER = "https://niko.sryze.cc/discord"
_SECURITY_ADVISORIES = f"{_GITHUB_REPO}/security/advisories/new"

_SECURITY_NOTICE = """\
NIKO — SECURITY NOTICE
======================

You requested: {path}

This is a decoy file, not a real configuration file, backup, or credential
store. Niko's website is a static React build served by a small Python API, and
this path never contained environment secrets, database dumps, private keys, or
service credentials. There is nothing here to take.

Our source code is public:
  {github}

REPORTING A VULNERABILITY
-------------------------
We take our users' privacy seriously. It is unlikely that you will find an
environment secret in our website or code, but we still reward people who
report security vulnerabilities. Every vulnerability fixed is a potential
future incident prevented, and valid reports earn the **Bug Bounty** role in
our support server.

1. Join the support server:
     {support}
2. Open the #community-help forum and create a post with the "Bug" tag, or
   open a private ticket from the #create-a-ticket channel and say that it is
   a security report.
3. Include the affected URL or endpoint, clear reproduction steps, and the
   impact you believe it has. Please do not include real secrets, other
   people's private data, or data you obtained by accessing an account that is
   not yours.

You can also open a private GitHub security advisory:
  {advisories}

Please do not run automated scans against production. If a scanner found this
page, that is expected: it is intentionally served to make this notice easy to
find. Thanks for helping keep Niko and its community safe.
"""

# A small, representative set of the paths scanners try first. Only paths the
# deployment genuinely does not serve belong here; real assets and routes must
# keep their normal responses.
_PROBE_PATHS = (
    "/.env",
    "/.env.local",
    "/.env.development",
    "/.env.production",
    "/.env.backup",
    "/.env.example",
    "/.git/config",
    "/.git/HEAD",
    "/.gitignore",
    "/.svn/entries",
    "/.hg/hgrc",
    "/.htaccess",
    "/.htpasswd",
    "/.aws/credentials",
    "/.ssh/id_rsa",
    "/.ssh/id_ed25519",
    "/id_rsa",
    "/wp-config.php",
    "/wp-config.php.bak",
    "/wp-login.php",
    "/xmlrpc.php",
    "/config.php",
    "/configuration.php",
    "/settings.php",
    "/config.json",
    "/credentials.json",
    "/secrets.json",
    "/service-account.json",
    "/backup.sql",
    "/database.sql",
    "/db.sql",
    "/dump.sql",
    "/backup.zip",
    "/www.zip",
    "/docker-compose.yml",
    "/Dockerfile",
    "/server-status",
    "/phpinfo.php",
    "/actuator/env",
    "/debug/vars",
)

_SECURITY_TXT = f"""\
Contact: {_SUPPORT_SERVER}
Contact: {_SECURITY_ADVISORIES}
Expires: 2027-12-31T23:59:59.000Z
Preferred-Languages: en
Canonical: https://niko.sryze.cc/.well-known/security.txt
# Niko does not serve environment secrets or credentials from this website.
# Source: {_GITHUB_REPO}
# Join {_SUPPORT_SERVER}, then open a "Bug"-tagged post in #community-help or a
# private ticket in #create-a-ticket to report a vulnerability. Valid reports
# earn the Bug Bounty role. Every vulnerability fixed is a future incident
# prevented.
"""


def _probe_response() -> Response:
    body = _SECURITY_NOTICE.format(
        path=request.path,
        github=_GITHUB_REPO,
        support=_SUPPORT_SERVER,
        advisories=_SECURITY_ADVISORIES,
    )
    return Response(
        body,
        mimetype="text/plain",
        headers={"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow"},
    )


def _security_txt_response() -> Response:
    return Response(
        _SECURITY_TXT,
        mimetype="text/plain",
        headers={"Cache-Control": "public, max-age=3600"},
    )


for _path in _PROBE_PATHS:
    _endpoint = "security_probe_" + _path.strip("/").replace("/", "_").replace(".", "_")
    _server.app.add_url_rule(_path, endpoint=_endpoint, view_func=_probe_response)

_server.app.add_url_rule(
    "/.well-known/security.txt",
    endpoint="security_txt",
    view_func=_security_txt_response,
)
_server.app.add_url_rule(
    "/security.txt",
    endpoint="security_txt_legacy",
    view_func=_security_txt_response,
)
