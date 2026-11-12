"""Decoy files for the paths credential crawlers probe.

Automated scanners request well-known configuration, backup and VCS paths on
every host they can reach. Niko's deployment serves none of them, so before
this module every hit fell through to the SPA shell or a 404: a clear miss, and
a line in the access log for each path.

These routes answer with generated fake files instead (see ``webapp.honeypot``).
Nothing they serve is a real credential, and every value is reproducible from
the public source. The practical effects are:

* a scanner that finds a plausible ``.env`` keeps reading and downloading,
  which costs it time and gets it nothing;
* the requests are answered ``200``, so ``_QuietSuccessfulRequests`` keeps them
  out of the console and the owner's live feed entirely;
* one compact line per probing address per minute records that it happened, in
  place of the dozens of ``404`` lines it used to produce.

Only paths the deployment genuinely does not serve are registered. A real route
or a file in the built site always wins, because registration skips anything
the Flask app already answers.

Several decoy connection strings point at hosts the site does not run
(``db``, ``read``, ``cache``, ``vault`` and ``queue`` under the public
``.niko.sryze.cc`` domain). Those hosts are wildcard DNS, so a crawler that
follows a fake password there reaches this service; instead of the subdomain
404 it gets a short terminal animation (see ``webapp.honeypot.easter_eggs``).
``nyan`` (and ``nyancat``) is the same animation as a pure easter egg: no decoy
files, no fake credentials, and a closing card that says so. The check runs
first, before subdomain routing, so it also covers hosts the site treats as
unused.
"""

from __future__ import annotations

import logging
import os
import threading
import time

from flask import Response, g, request
from utils.verification.ip_intel import client_ip

from .. import honeypot
from .. import security
from .. import server as _server
from ..config import public_domain
from ..honeypot import easter_eggs
from ..runtime import request_host
from ..security_guard import banned_response

_GITHUB_REPO = "https://github.com/developer51709/Niko"
_SUPPORT_SERVER = "https://niko.sryze.cc/discord"
_SECURITY_ADVISORIES = f"{_GITHUB_REPO}/security/advisories/new"

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

_PROBE_LOG = logging.getLogger("Honeypot")

#: At most one summary line per address in this many seconds. The throttle is
#: only for the log; the hit itself is written to the database by
#: ``webapp.security`` on every request.
_HIT_WINDOW_SECONDS = 60.0

#: Addresses remembered for the log throttle. The map is insertion-ordered, so
#: the oldest entry is dropped when a scanner fakes its way through a range.
_MAX_TRACKED_ADDRESSES = 512

_log_throttle: dict[str, tuple[float, int]] = {}


def _remember_probe(path: str) -> None:
    """Persist a decoy hit and collapse its log line to one per address/minute."""
    address = client_ip(
        request.remote_addr, request.headers.get("X-Forwarded-For")
    ) or "unknown"
    try:
        result = security.record_hit(
            ip=address,
            path=path,
            host=request_host(),
            method=request.method,
            user_agent=request.headers.get("User-Agent") or "",
        )
    except Exception as exc:
        _PROBE_LOG.warning("Could not save a honeypot hit: %s", exc)
        result = None

    now = time.monotonic()
    entry = _log_throttle.get(address)
    if entry is None:
        _PROBE_LOG.info(
            "Decoy files: %s is probing the deployment (%s) — serving fake credentials",
            address,
            path,
        )
        _log_throttle[address] = (now, 0)
    elif now - entry[0] >= _HIT_WINDOW_SECONDS:
        _PROBE_LOG.info(
            "Decoy files: %s probed %d more decoy paths in %ds — still fake",
            address,
            entry[1] + 1,
            int(now - entry[0]),
        )
        _log_throttle[address] = (now, 0)
    else:
        _log_throttle[address] = (entry[0], entry[1] + 1)

    while len(_log_throttle) > _MAX_TRACKED_ADDRESSES:
        _log_throttle.pop(next(iter(_log_throttle)))

    if result and result.get("ban"):
        _PROBE_LOG.warning(
            "Autoban: %s crossed the honeypot threshold and is now blocked — %s",
            address,
            result["ban"].get("reason") or "autoban",
        )


def _decoy_response() -> Response:
    payload = honeypot.body_for(request.path)
    if payload is None:  # pragma: no cover - only registered paths reach here
        return Response("Not Found", status=404, mimetype="text/plain")
    body, mimetype = payload
    _remember_probe(request.path)
    return Response(
        body,
        content_type=mimetype,
        headers={
            "Cache-Control": "no-store",
            "X-Robots-Tag": "noindex, nofollow",
        },
    )


def _security_txt_response() -> Response:
    return Response(
        _SECURITY_TXT,
        mimetype="text/plain",
        headers={"Cache-Control": "public, max-age=3600"},
    )


#: Domains the fake service hosts live under. The literal public domain is
#: always accepted, so the decoys work even on a deployment whose
#: ``PUBLIC_URL`` points somewhere else (a preview or a staging host).
_EGG_DOMAINS = ("niko.sryze.cc",)

#: How many animations may stream at once. Everything else gets the closing
#: card immediately, so a scanner cannot pin a thread per request.
_MAX_EGG_STREAMS = 8
_egg_streams = 0
_egg_lock = threading.Lock()

#: At most one easter-egg line per address per minute.
_egg_seen: dict[str, float] = {}


def _egg_for(host: str) -> tuple[str, bool]:
    """The animation a request host plays, and whether it is a decoy host."""
    name = (host or "").split(":", 1)[0].strip().strip(".").lower()
    label, _, rest = name.partition(".")
    if not label or not rest:
        return "", False
    domains = set(_EGG_DOMAINS)
    served = public_domain()
    if served:
        domains.add(served)
    if not any(
        rest == domain or rest.endswith("." + domain) for domain in domains
    ):
        return "", False
    kind = easter_eggs.EGG_LABELS.get(label, "")
    if not kind:
        return "", False
    return kind, label not in easter_eggs.PLAY_HOSTS


def _note_egg(address: str, kind: str, host: str, decoy: bool) -> None:
    """Record that somebody found an easter egg."""
    now = time.monotonic()
    if now - _egg_seen.get(address, float("-inf")) < _HIT_WINDOW_SECONDS:
        return
    _egg_seen[address] = now
    if decoy:
        _PROBE_LOG.info(
            "Easter egg: %s opened the %s on %s — the host is a decoy",
            address,
            kind,
            host,
        )
    else:
        _PROBE_LOG.info(
            "Easter egg: %s is watching the %s on %s", address, kind, host
        )
    while len(_egg_seen) > _MAX_TRACKED_ADDRESSES:
        _egg_seen.pop(next(iter(_egg_seen)))


def _easter_egg_response(kind: str, host: str, decoy: bool) -> Response:
    global _egg_streams
    # ``no-transform`` keeps a CDN from compressing (and therefore buffering)
    # the stream: an animation that arrives in one lump at the end is just a
    # wall of escape codes.
    headers = {
        "Cache-Control": "no-store, no-transform",
        "X-Robots-Tag": "noindex, nofollow",
        "X-Accel-Buffering": "no",
    }
    with _egg_lock:
        if _egg_streams >= _MAX_EGG_STREAMS:
            return Response(
                easter_eggs.closing(kind, host, decoy),
                content_type="text/plain; charset=utf-8",
                headers=headers,
            )
        _egg_streams += 1

    def stream():
        global _egg_streams
        try:
            for delay, frame in easter_eggs.frames(kind, host, decoy):
                yield frame
                time.sleep(delay)
        finally:
            with _egg_lock:
                _egg_streams -= 1

    return Response(
        stream(), content_type="text/plain; charset=utf-8", headers=headers
    )


def _play_easter_egg():
    """Answer the fake service hosts with an animation, before anything else."""
    denied = banned_response()
    if denied is not None:
        return denied
    if request.method not in ("GET", "HEAD"):
        return None
    host = request_host()
    kind, decoy = _egg_for(host)
    if not kind:
        return None
    if request.method == "HEAD":
        return Response(
            status=200,
            content_type="text/plain; charset=utf-8",
            headers={"Cache-Control": "no-store, no-transform"},
        )
    address = client_ip(
        request.remote_addr, request.headers.get("X-Forwarded-For")
    ) or "unknown"
    _note_egg(address, kind, host, decoy)
    g.easter_egg = True
    return _easter_egg_response(kind, host, decoy)


def _keep_egg_stream_live(response: Response) -> Response:
    """Keep ``no-transform`` after the global no-store hook has run."""
    if g.get("easter_egg"):
        response.headers["Cache-Control"] = "no-store, no-transform"
    return response


# ``after_request`` handlers run in reverse registration order, so inserting
# this one first makes it the last to touch the response.
_after_hooks = _server.app.after_request_funcs.setdefault(None, [])
if _keep_egg_stream_live not in _after_hooks:
    _after_hooks.insert(0, _keep_egg_stream_live)


def _register_decoys() -> int:
    """Register every decoy path the app does not already answer."""
    registered = 0
    existing = {rule.rule for rule in _server.app.url_map.iter_rules()}
    for index, path in enumerate(honeypot.paths()):
        if path in existing:
            continue
        shipped = os.path.isfile(
            os.path.join(_server.app.static_folder or "", path.lstrip("/"))
        )
        if shipped:
            continue
        _server.app.add_url_rule(
            path,
            endpoint=f"decoy_probe_{index}",
            view_func=_decoy_response,
        )
        registered += 1
    return registered


DECOY_COUNT = _register_decoys()

# The egg check has to run before subdomain routing: the site treats these
# hosts as unused subdomains and would answer them with a 404 first.
_hooks = _server.app.before_request_funcs.setdefault(None, [])
if _play_easter_egg not in _hooks:
    _hooks.insert(0, _play_easter_egg)

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
