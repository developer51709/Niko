"""Keep interaction callbacks out of Discord's global rate-limit queue.

Discord does not bind its interaction endpoints to the application's global rate
limit — ``POST /interactions/{id}/{token}/callback`` and the interaction webhook
routes behind followups, original-response edits and deletes are exempt — and an
interaction has to be answered within three seconds. discord.py, however, parks
*every* request behind ``HTTPClient._global_over`` while a global 429 is being
slept off, including the callback behind a slash command, button, select or
modal. That is why a global limit hit somewhere else in the bot made menus feel
dead and why the queued callbacks then consumed proxy bandwidth when the traffic
was re-sent through Webshare.

``install_interaction_priority`` wraps one client's ``HTTPClient.request`` and
marks the request in flight when it belongs to an interaction, so the global gate
steps aside for exactly those requests. Every other request keeps waiting for the global limit
to clear, so the bot as a whole still respects it.

The bypass lasts for the request only: a handler's other REST calls (posting a
persistent panel into a channel, for example) are untouched and keep queueing.

With the HTTP interactions endpoint armed (``utils.interaction_endpoint``) the
first callback never reaches the client at all — it is answered in the body of
Discord's own request.  This bypass still covers the followup, original-response
edit and delete routes behind it, and every deployment that still receives its
interactions over the gateway.
"""

from __future__ import annotations

import asyncio
import contextvars
import weakref
from types import MethodType

from utils import logging

#: True only inside an interaction callback / interaction webhook request.
_INTERACTION_REQUEST: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "niko_interaction_request", default=False
)

_CALLBACK_PREFIX = "/interactions/"
_WEBHOOK_PREFIX = "/webhooks/"
_MARKER = "_niko_interaction_priority"


class _InteractionAwareGlobalOver(asyncio.Event):
    """The HTTP client's global-lock event, transparent to interaction requests."""

    async def wait(self) -> bool:
        if _INTERACTION_REQUEST.get():
            return True
        return await super().wait()


def _application_id(bot) -> str | None:
    """The application id interaction webhooks are addressed with."""
    application_id = getattr(bot, "application_id", None)
    if application_id is None:
        # A bot's application id is its own user id.
        application_id = getattr(getattr(bot, "user", None), "id", None)
    return None if application_id is None else str(application_id)


def is_interaction_route(route, application_id: str | None = None) -> bool:
    """Whether ``route`` is an interaction callback or interaction webhook route.

    Discord exempts both from the application's global rate limit. The callback
    route names the interaction, so it needs no other information; a followup or
    original-response route is the application's own webhook, which is why it is
    matched through the application id and never as an ordinary channel webhook.
    """
    path = str(getattr(route, "path", "") or "")
    if path.startswith(_CALLBACK_PREFIX):
        return True
    if not path.startswith(_WEBHOOK_PREFIX):
        return False
    if not getattr(route, "webhook_token", None):
        return False
    webhook_id = getattr(route, "webhook_id", None)
    if webhook_id is None or application_id is None:
        return False
    return str(webhook_id) == str(application_id)


def _install_global_gate(http) -> None:
    """Swap the client's global gate for one that lets interaction requests pass.

    The client is only globally limited while the gate is clear, so the
    replacement starts in the same state as the gate it replaces.  Before login
    discord.py has no event at all (the attribute is its ``MISSING`` sentinel),
    which is an open gate.
    """
    gate = getattr(http, "_global_over", None)
    if isinstance(gate, _InteractionAwareGlobalOver):
        return
    priority_gate = _InteractionAwareGlobalOver()
    if not isinstance(gate, asyncio.Event) or gate.is_set():
        priority_gate.set()
    http._global_over = priority_gate


def install_interaction_priority(bot) -> bool:
    """Route this client's interaction requests around the global rate-limit wait.

    Safe to call more than once, and safe to call before login: the wrapper is
    installed on the client's HTTP object, not on its aiohttp session, so a
    session recreated by a reconnect keeps the behaviour.
    """
    http = getattr(bot, "http", None)
    if http is None or getattr(http, _MARKER, False):
        return bool(getattr(http, _MARKER, False))

    original_request = http.request
    bot_ref = weakref.ref(bot)

    async def interaction_priority_request(self, route, **kwargs):
        # ``static_login`` builds a fresh event, so a later login would otherwise
        # drop the gate back to the unmodified one.
        if not isinstance(getattr(self, "_global_over", None), _InteractionAwareGlobalOver):
            _install_global_gate(self)
        token = _INTERACTION_REQUEST.set(
            is_interaction_route(route, _application_id(bot_ref()))
        )
        try:
            return await original_request(route, **kwargs)
        finally:
            _INTERACTION_REQUEST.reset(token)

    http.request = MethodType(interaction_priority_request, http)
    _install_global_gate(http)
    setattr(http, _MARKER, True)
    logging.info(
        "InteractionPriority",
        "Interaction callbacks now bypass the global rate-limit queue.",
    )
    return True
