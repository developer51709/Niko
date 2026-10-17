"""Answer Discord interactions over HTTP instead of POSTing a callback back.

Discord can deliver interactions two ways and only one of them at a time: over
the gateway (``INTERACTION_CREATE``), or to the *Interactions Endpoint URL* saved
in the Developer Portal.  With the endpoint configured, Discord POSTs the
interaction to us and expects the callback **in the response body of that same
request** — the answer never leaves the process.

That is worth a lot here.  The first interaction response has to be inside three
seconds and must never queue or fail, and it is the one part of the exchange
Discord initiates rather than the bot: answering it in that inbound request needs
no egress at all.  When the host's IP is blocked by Cloudflare, a slash command
answered over the callback route has nowhere to go, while one answered from
discord.com's own request still arrives.
Followups, edits and deletes still go out over REST (through the proxy and
rate-limit handling described in ``docs/maintenance.md``), but they are no
longer the critical path.

``discord.py`` always builds a callback as an outbound REST call, so the one
function that does that (``AsyncWebhookAdapter.create_interaction_response``)
is wrapped: while an interaction arrived over HTTP, the body it would have sent
is kept and handed to ``webapp.interaction_routes`` to return in the response,
and the library is given the callback response Discord would have returned.  The
sink is a ``ContextVar``, so exactly the handler for that interaction — and the
tasks it spawns — is captured; anything else still talks to Discord normally.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import contextvars
import json
import os
import secrets
from pathlib import Path
from typing import Any, NamedTuple

from utils import logging

#: Discord invalidates the interaction token three seconds after delivery, which
#: is also when it gives up on the HTTP response.
DISCORD_DEADLINE_SECONDS = 3.0
#: How long the route waits for the handler's callback.  The rest of the window
#: is the round trip to Discord, plus the standby relay on the way (that relay
#: reads upstream with a three second timeout of its own), so the default leaves
#: a full second of margin.  ``DISCORD_INTERACTION_BUDGET_SECONDS`` overrides it
#: for a deployment that can afford to wait longer.
DEFAULT_RESPONSE_BUDGET_SECONDS = 2.0
#: How long past the budget the route waits before it stops waiting for the
#: dispatch itself, so the budget is always what ends the wait.
SCHEDULING_GRACE_SECONDS = 0.5

#: ``MessageFlags.ephemeral`` — the flag an ephemeral callback carries.
_EPHEMERAL_FLAG = 1 << 6
#: ``InteractionResponseType.deferred_channel_message`` — a "thinking" defer.
_DEFERRED_CHANNEL_MESSAGE = 5
#: Callback types 6 and 7 update the message the component sits on, so the id of
#: the message that response creates is already known from the payload.
_MESSAGE_UPDATE_TYPES = (6, 7)

PUBLIC_KEY_ENV = "DISCORD_PUBLIC_KEY"
_BUDGET_ENV = "DISCORD_INTERACTION_BUDGET_SECONDS"

#: The application's Ed25519 public key, as the Developer Portal shows it.  It is
#: public information (it only ever verifies), so the environment variable is a
#: convenience, not a secret.
_public_key: str | None = None
#: Resolved key kept between restarts: fetching it needs egress to Discord, and
#: the endpoint has to keep verifying exactly when egress is what broke.
_KEY_CACHE = Path(__file__).resolve().parents[2] / "data" / "interaction_public_key"

#: The interaction whose handler is running in this context, if any.
_ACTIVE_INTERACTION: contextvars.ContextVar["_InteractionSink | None"] = contextvars.ContextVar(
    "niko_interaction_sink", default=None
)

_CAPTURE_MARKER = "_niko_interaction_capture"


class InteractionBody(NamedTuple):
    """One callback, byte for byte as Discord's API would have received it."""

    payload: bytes
    content_type: str


# ── The endpoint's identity ──────────────────────────────────────────────────


def public_key() -> str | None:
    """The application's Ed25519 public key, or ``None`` when it is unknown."""
    return _public_key


def _read_cached_key() -> str | None:
    try:
        key = _KEY_CACHE.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return key or None


def _cache_key(key: str) -> None:
    """Remember a fetched key so a restart during an egress outage still works."""
    try:
        _KEY_CACHE.parent.mkdir(parents=True, exist_ok=True)
        temporary = _KEY_CACHE.with_suffix(".tmp")
        temporary.write_text(key, encoding="utf-8")
        os.replace(temporary, _KEY_CACHE)
    except OSError as exc:  # a cache that cannot be written is not fatal
        logging.warning("Interactions", f"Could not cache the public key: {exc}")


def verify_signature(key_hex: str, signature_hex: str, timestamp: str, body: bytes) -> bool:
    """Whether ``body`` was signed by the application Discord is posting for.

    Discord signs the timestamp followed by the *raw* request body, so the body
    must be the exact bytes received and never a re-serialised form of it.
    """
    if not key_hex or not signature_hex or not timestamp or not body:
        return False
    try:
        from nacl.exceptions import BadSignatureError
        from nacl.signing import VerifyKey

        VerifyKey(bytes.fromhex(key_hex)).verify(
            timestamp.encode("utf-8") + body, bytes.fromhex(signature_hex)
        )
    except (ValueError, TypeError, BadSignatureError):
        return False
    return True


async def install_interaction_endpoint(bot) -> str | None:
    """Resolve the public key and arm the interactions endpoint.

    The key comes from ``DISCORD_PUBLIC_KEY`` when it is set, otherwise from the
    application object (which is also where the Developer Portal shows it), and
    it is cached on disk so the endpoint keeps verifying across a restart that
    cannot reach Discord.
    """
    global _public_key

    configured = (os.environ.get(PUBLIC_KEY_ENV) or "").strip()
    if configured:
        # An operator who set the variable has the key at hand; trust it over a
        # fetch that may be the very egress that is broken.
        _public_key = configured
    else:
        fetched = None
        info = None
        try:
            info = await bot.application_info()
            fetched = (getattr(info, "verify_key", "") or "").strip() or None
        except Exception as exc:
            logging.warning("Interactions", f"Could not read the application public key: {exc}")

        if fetched:
            _public_key = fetched
            _cache_key(fetched)
            if getattr(info, "interactions_endpoint_url", None):
                logging.info(
                    "Interactions",
                    f"Discord delivers interactions over HTTP to {info.interactions_endpoint_url}.",
                )
            else:
                logging.info(
                    "Interactions",
                    "Discord still delivers interactions over the gateway. The endpoint for this "
                    "deployment is /api/discord/interactions.",
                )
        else:
            _public_key = _read_cached_key()
            if _public_key:
                logging.info("Interactions", "Using the cached public key for the interactions endpoint.")
            else:
                logging.error(
                    "Interactions",
                    "No public key for the interactions endpoint — set DISCORD_PUBLIC_KEY to the "
                    "application's Public Key from the Developer Portal.",
                )

    install_capture()
    if _public_key:
        logging.info(
            "Interactions",
            "Interactions endpoint armed: callbacks are answered in the response to Discord's "
            "own request instead of an outbound one.",
        )
    return _public_key


# ── Capturing the callback discord.py would have sent ─────────────────────────


def _read_file(handle) -> bytes | None:
    """Read a file object the way aiohttp would have streamed it."""
    read = getattr(handle, "read", None)
    if not callable(read):
        return None
    try:
        position = handle.tell()
    except Exception:
        position = None
    try:
        data = read()
    except Exception:
        return None
    if position is not None:
        try:
            handle.seek(position)
        except Exception:
            pass
    if isinstance(data, str):
        return data.encode("utf-8")
    return bytes(data) if isinstance(data, (bytes, bytearray)) else None


def _multipart_body(fields) -> InteractionBody | None:
    """Rebuild the multipart body of a callback that carries a file.

    The field names are the ones discord.py's own request would have used
    (``payload_json`` plus ``files[0]``), because they are what Discord parses.
    """
    boundary = f"----niko{secrets.token_hex(16)}"
    parts: list[bytes] = []
    for field in fields:
        name = field.get("name")
        value = field.get("value")
        if name is None or value is None:
            return None
        if isinstance(value, str):
            chunk = value.encode("utf-8")
        elif isinstance(value, (bytes, bytearray)):
            chunk = bytes(value)
        else:
            chunk = _read_file(value)
            if chunk is None:
                return None

        filename = field.get("filename")
        header = f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"'
        if filename:
            header += f'; filename="{filename}"'
        header += "\r\n"
        content_type = field.get("content_type")
        if filename and content_type:
            header += f"Content-Type: {content_type}\r\n"
        parts.append(header.encode("utf-8") + b"\r\n" + chunk)
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return InteractionBody(b"\r\n".join(parts), f"multipart/form-data; boundary={boundary}")


def callback_body(params) -> InteractionBody | None:
    """The HTTP body for a callback ``params``, or ``None`` if it cannot be rebuilt."""
    payload = getattr(params, "payload", None)
    if isinstance(payload, dict):
        return InteractionBody(json.dumps(payload).encode("utf-8"), "application/json")
    multipart = getattr(params, "multipart", None)
    if multipart:
        return _multipart_body(multipart)
    return None


def callback_response_payload(params, interaction_id, message_id: str | None = None) -> dict:
    """What Discord would have answered the callback with, for the library.

    ``discord.py`` parses this into an ``InteractionCallbackResponse`` and stores
    any view that came with the callback under ``response.message_id``.  A
    component callback that updates its message (a paginator arrow, a panel
    button) updates the message the component sits on, so that id is known and is
    reported.  A callback that posts a *new* message only exists on Discord's
    side once the endpoint has answered, so that id is absent and a view sent
    with it is stored without a message id — ``ViewStore.dispatch_view`` has a
    fallback for exactly that, and discord.py's own buttons carry a per-instance
    ``custom_id``, so a click still reaches the view it belongs to.
    """
    payload = getattr(params, "payload", None)
    flags = 0
    response_type = None
    if isinstance(payload, dict):
        response_type = payload.get("type")
        data = payload.get("data")
        if isinstance(data, dict):
            try:
                flags = int(data.get("flags") or 0)
            except (TypeError, ValueError):
                flags = 0

    interaction: dict[str, Any] = {"id": str(interaction_id)}
    if response_type == _DEFERRED_CHANNEL_MESSAGE:
        interaction["response_message_loading"] = True
    if flags & _EPHEMERAL_FLAG:
        interaction["response_message_ephemeral"] = True
    if response_type in _MESSAGE_UPDATE_TYPES and message_id:
        interaction["response_message_id"] = str(message_id)
    return {"interaction": interaction, "resource": None}


class _InteractionSink:
    """The callback of one interaction, held until the route can answer Discord."""

    def __init__(self, payload: dict) -> None:
        self.interaction_id = str(payload.get("id") or "")
        message = payload.get("message")
        self.message_id = str(message.get("id")) if isinstance(message, dict) and message.get("id") else None
        self._loop = asyncio.get_running_loop()
        self._body: asyncio.Future[InteractionBody | None] = self._loop.create_future()
        #: Set once the route has stopped listening, so a late callback is sent
        #: to Discord normally instead of vanishing into a closed sink.
        self.released = False

    def capture(self, params) -> dict | None:
        """Take a callback body; ``None`` lets the request go out as usual."""
        body = callback_body(params)
        if body is None:
            return None
        if not self._body.done():
            self._body.set_result(body)
        return callback_response_payload(params, self.interaction_id, self.message_id)

    async def wait(self, timeout: float) -> InteractionBody | None:
        try:
            return await asyncio.wait_for(asyncio.shield(self._body), timeout)
        except asyncio.TimeoutError:
            return None

    def release(self) -> None:
        self.released = True


def install_capture() -> bool:
    """Wrap the single function that sends interaction callbacks to Discord.

    Every callback — slash command, context menu, autocomplete, modal, component
    update, activity launch — is built and sent there, so wrapping it catches all
    of them.  Safe to call more than once.
    """
    from discord.webhook.async_ import AsyncWebhookAdapter

    if getattr(AsyncWebhookAdapter.create_interaction_response, _CAPTURE_MARKER, False):
        return True

    original = AsyncWebhookAdapter.create_interaction_response

    async def capturing_create_interaction_response(self, interaction_id, token, *args, **kwargs):
        sink = _ACTIVE_INTERACTION.get()
        if sink is not None and not sink.released:
            captured = sink.capture(kwargs.get("params"))
            if captured is not None:
                return captured
        return await original(self, interaction_id, token, *args, **kwargs)

    setattr(capturing_create_interaction_response, _CAPTURE_MARKER, True)
    AsyncWebhookAdapter.create_interaction_response = capturing_create_interaction_response
    return True


# ── Dispatching one interaction ──────────────────────────────────────────────


def response_budget_seconds() -> float:
    """How long to wait for the handler, clamped inside Discord's own deadline."""
    raw = (os.environ.get(_BUDGET_ENV) or "").strip()
    if raw:
        try:
            return max(0.1, min(float(raw), DISCORD_DEADLINE_SECONDS))
        except ValueError:
            logging.warning("Interactions", f"{_BUDGET_ENV}={raw!r} is not a number; using the default.")
    return DEFAULT_RESPONSE_BUDGET_SECONDS


async def _dispatch(bot, payload: dict, budget: float) -> InteractionBody | None:
    """Run the interaction on the bot's loop and wait for its callback."""
    connection = getattr(bot, "_connection", None)
    parse = getattr(connection, "parse_interaction_create", None)
    if parse is None:
        raise RuntimeError("The Discord client cannot dispatch interactions.")

    sink = _InteractionSink(payload)
    token = _ACTIVE_INTERACTION.set(sink)
    try:
        # The gateway's own entry point: it builds the Interaction, routes
        # application commands to the command tree, components and modals to the
        # view store, and dispatches on_interaction listeners.
        parse(payload)
        body = await sink.wait(budget)
        if body is None:
            logging.warning(
                "Interactions",
                f"Interaction {sink.interaction_id} was not answered within {budget:.1f}s; "
                "its handler's callback will go out over REST instead.",
            )
        return body
    finally:
        sink.release()
        _ACTIVE_INTERACTION.reset(token)


def handle_interaction(bot, payload: dict, budget: float | None = None) -> InteractionBody | None:
    """Dispatch ``payload`` on the bot's event loop and return the callback body.

    Flask serves the dashboard from its own thread while the command tree, the
    view store and every handler belong to the bot's loop, so the interaction has
    to run there.  ``None`` means no callback arrived inside the budget, and the
    route then answers Discord with the documented empty 202.
    """
    loop = getattr(bot, "loop", None)
    if loop is None or not loop.is_running():
        raise RuntimeError("The Discord bot is not running.")

    budget = response_budget_seconds() if budget is None else budget
    future = asyncio.run_coroutine_threadsafe(_dispatch(bot, payload, budget), loop)
    try:
        return future.result(timeout=budget + SCHEDULING_GRACE_SECONDS)
    except concurrent.futures.TimeoutError:
        logging.warning(
            "Interactions",
            "The interaction handler is still running past the response budget; "
            "answering Discord with 202.",
        )
        return None
