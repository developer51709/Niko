"""Interaction callbacks never queue behind Discord's global rate limit.

Discord does not count the interaction endpoints against the application's global
limit, but discord.py parks *every* request behind ``HTTPClient._global_over``
while a global 429 is slept off.  These tests pin the bypass: the callback behind
a slash command, button, select or modal goes out immediately, every other
request keeps waiting, and the bypass never leaks into the next request.
"""

import asyncio
import sys
from types import SimpleNamespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from discord.http import Route

from utils.interaction_priority import (
    install_interaction_priority,
    is_interaction_route,
)

APPLICATION_ID = 100
CALLBACK = "/interactions/123/interaction-token/callback"


class FakeHTTP:
    """discord.py's HTTPClient, reduced to the parts the bypass touches."""

    def __init__(self):
        self._global_over = asyncio.Event()
        self._global_over.set()
        self.seen = []

    async def request(self, route, **kwargs):
        # discord.py's own global gate, verbatim.
        if not self._global_over.is_set():
            await self._global_over.wait()
        self.seen.append(route.path)
        return SimpleNamespace(status=200, route=route)


class FakeBot:
    def __init__(self):
        self.http = FakeHTTP()
        self.application_id = APPLICATION_ID


def _installed():
    bot = FakeBot()
    install_interaction_priority(bot)
    return bot


def test_the_callback_and_followup_routes_are_recognised_as_interactions():
    callback = Route("POST", "/interactions/{webhook_id}/{webhook_token}/callback",
                     webhook_id=123, webhook_token="interaction-token")
    followup = Route("POST", "/webhooks/{webhook_id}/{webhook_token}",
                     webhook_id=APPLICATION_ID, webhook_token="interaction-token")
    original = Route("PATCH", "/webhooks/{webhook_id}/{webhook_token}/messages/@original",
                     webhook_id=APPLICATION_ID, webhook_token="interaction-token")

    assert is_interaction_route(callback, str(APPLICATION_ID))
    assert is_interaction_route(followup, str(APPLICATION_ID))
    assert is_interaction_route(original, str(APPLICATION_ID))


def test_channel_routes_are_not_interactions():
    # A channel webhook is a different egress: its id is not the application id.
    channel_webhook = Route("POST", "/webhooks/{webhook_id}/{webhook_token}",
                            webhook_id=999, webhook_token="channel-token")
    channel_webhook_by_id = Route("POST", "/webhooks/{webhook_id}",
                                  webhook_id=APPLICATION_ID)
    channel_message = Route("POST", "/channels/{channel_id}/messages", channel_id=1)

    assert not is_interaction_route(channel_webhook, str(APPLICATION_ID))
    assert not is_interaction_route(channel_webhook_by_id, str(APPLICATION_ID))
    assert not is_interaction_route(channel_message, str(APPLICATION_ID))
    # Without a known application id a followup cannot be told from a channel
    # webhook, so it must not be waved through.
    assert not is_interaction_route(channel_webhook, None)


def test_an_interaction_callback_goes_out_while_the_global_gate_is_shut():
    async def scenario():
        bot = _installed()
        bot.http._global_over.clear()

        callback = await asyncio.wait_for(
            bot.http.request(Route("POST", CALLBACK)), timeout=0.5
        )
        followup = await asyncio.wait_for(
            bot.http.request(Route("POST", "/webhooks/{webhook_id}/{webhook_token}",
                                   webhook_id=APPLICATION_ID, webhook_token="t")),
            timeout=0.5,
        )

        assert (callback.status, followup.status) == (200, 200)

    asyncio.run(scenario())


def test_other_requests_still_wait_for_the_global_gate():
    async def scenario():
        bot = _installed()
        bot.http._global_over.clear()
        waiting = asyncio.create_task(
            bot.http.request(Route("POST", "/channels/{channel_id}/messages", channel_id=1))
        )
        await asyncio.sleep(0.05)

        assert not waiting.done()
        # The callback is served while that request is still parked.
        await asyncio.wait_for(bot.http.request(Route("POST", CALLBACK)), timeout=0.5)
        assert not waiting.done()

        bot.http._global_over.set()
        await asyncio.wait_for(waiting, timeout=0.5)
        assert waiting.done()

    asyncio.run(scenario())


def test_the_bypass_does_not_leak_into_the_next_request():
    async def scenario():
        bot = _installed()
        bot.http._global_over.clear()
        await bot.http.request(Route("POST", CALLBACK))

        # Same task, next request: it is an ordinary route again and must wait.
        waiting = asyncio.create_task(
            bot.http.request(Route("POST", "/channels/{channel_id}/messages", channel_id=1))
        )
        await asyncio.sleep(0.05)

        assert not waiting.done()
        bot.http._global_over.set()
        await asyncio.wait_for(waiting, timeout=0.5)

    asyncio.run(scenario())


def test_the_replaced_gate_keeps_the_clients_limited_state():
    bot = FakeBot()
    bot.http._global_over.clear()
    install_interaction_priority(bot)

    assert not bot.http._global_over.is_set()
    bot.http._global_over.set()
    assert bot.http._global_over.is_set()


def test_installing_twice_keeps_exactly_one_wrapper():
    async def scenario():
        bot = _installed()
        install_interaction_priority(bot)
        await bot.http.request(Route("POST", CALLBACK))

        assert bot.http.seen == [CALLBACK]

    asyncio.run(scenario())


def test_a_client_without_http_is_left_alone():
    assert install_interaction_priority(SimpleNamespace()) is False


def test_a_real_discord_client_serves_callbacks_while_the_gate_is_shut():
    """The bypass has to work inside discord.py's own request, not a stand-in."""
    import discord

    class Response:
        status = 200
        headers = {"Content-Type": "application/json"}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return None

        async def text(self, encoding="utf-8"):
            return "{}"

        def release(self):
            return None

    class Session:
        def __init__(self):
            self.calls = []

        def request(self, method, url, **kwargs):
            self.calls.append((method, url))
            return Response()

    async def scenario():
        client = discord.Client(intents=discord.Intents.none())
        install_interaction_priority(client)
        session = Session()
        client.http._HTTPClient__session = session
        client.http._global_over.clear()

        callback = Route("POST", "/interactions/{webhook_id}/{webhook_token}/callback",
                         webhook_id=1, webhook_token="interaction-token")
        await asyncio.wait_for(client.http.request(callback, json={"type": 1}), timeout=1)

        # An ordinary REST call is still parked behind the same global limit.
        waiting = asyncio.create_task(
            client.http.request(Route("POST", "/channels/{channel_id}/messages", channel_id=1), json={})
        )
        await asyncio.sleep(0.05)
        assert not waiting.done()
        assert len(session.calls) == 1

        client.http._global_over.set()
        await asyncio.wait_for(waiting, timeout=1)
        assert [url for _, url in session.calls] == [
            "https://discord.com/api/v10/interactions/1/interaction-token/callback",
            "https://discord.com/api/v10/channels/1/messages",
        ]

    asyncio.run(scenario())
