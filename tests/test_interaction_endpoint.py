"""Discord's own HTTP request carries the answer to the interaction.

Once the *Interactions Endpoint URL* is configured, Discord stops delivering
interactions over the gateway and POSTs them to our endpoint, expecting the
callback in the response body.  These tests pin the three things that make that
safe: the Ed25519 signature is checked over the raw body before anything is
decoded, the callback a handler produces is mirrored instead of sent, and a
handler that misses the budget is acknowledged with the documented empty 202
while its own request goes out over REST as before.
"""

import asyncio
import json
import sys
import threading
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from nacl.signing import SigningKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import discord
from discord.webhook.async_ import AsyncWebhookAdapter, interaction_message_response_params

from utils import interaction_endpoint
from webapp.routes import interaction_routes

ENDPOINT = "/api/discord/interactions"
TIMESTAMP = "1700000000"
KEY_BYTES = 32


def _slash_payload() -> dict:
    """A slash command interaction, shaped the way Discord posts it."""
    return {
        "id": "1234567890123456789",
        "application_id": "100",
        "type": 2,
        "data": {"id": "555", "name": "ping", "type": 1, "options": []},
        "guild_id": "200",
        "channel_id": "300",
        "channel": {
            "id": "300",
            "type": 0,
            "name": "general",
            "position": 0,
            "permission_overwrites": [],
            "nsfw": False,
            "rate_limit_per_user": 0,
            "parent_id": None,
            "guild_id": "200",
            "topic": None,
            "last_message_id": None,
        },
        "member": {
            "user": {
                "id": "400",
                "username": "tester",
                "discriminator": "0",
                "global_name": "Tester",
                "avatar": None,
            },
            "roles": [],
            "joined_at": "2024-01-01T00:00:00+00:00",
            "deaf": False,
            "mute": False,
            "flags": 0,
            "pending": False,
            "permissions": "0",
        },
        "token": "interaction-token",
        "version": 1,
        "locale": "en-US",
        "guild_locale": "en-US",
        "entitlements": [],
        "app_permissions": "0",
        # Discord sends this on every interaction; discord.py reads it to size
        # attachment uploads.
        "attachment_size_limit": 10485760,
    }


def _sign(key: SigningKey, body: bytes, timestamp: str = TIMESTAMP) -> str:
    return key.sign(timestamp.encode("utf-8") + body).signature.hex()


class FakeResponse:
    """The slice of an aiohttp response the webhook adapter reads."""

    status = 200
    headers = {"Content-Type": "application/json"}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return None

    async def text(self, encoding="utf-8"):
        return json.dumps({"interaction": {"id": "1"}, "resource": None})

    def release(self):
        return None


class FakeSession:
    """Counts what actually left the process."""

    def __init__(self):
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs.get("params")))
        return FakeResponse()


@pytest.fixture
def armed(monkeypatch):
    """An endpoint with a real Ed25519 keypair, as the portal issues one."""
    key = SigningKey.generate()
    monkeypatch.setattr(interaction_endpoint, "_public_key", key.verify_key.encode().hex())
    return key


@pytest.fixture
def bot(monkeypatch):
    """A stand-in for the running bot, so the route has something to dispatch to."""
    stub = SimpleNamespace(loop=None)
    monkeypatch.setattr(interaction_routes, "_discord_bot", stub)
    return stub


def _post(client, body: bytes, *, key=None, timestamp=TIMESTAMP, signed=True):
    headers = {}
    if signed:
        headers["X-Signature-Ed25519"] = _sign(key, body, timestamp)
        headers["X-Signature-Timestamp"] = timestamp
    return client.post(ENDPOINT, data=body, headers=headers, content_type="application/json")


# ── The signature is what makes the route public-safe ─────────────────────────


def test_signature_verification_accepts_what_discord_signs():
    key = SigningKey.generate()
    body = b'{"type":1}'

    assert interaction_endpoint.verify_signature(
        key.verify_key.encode().hex(), _sign(key, body), TIMESTAMP, body
    )


def test_signature_verification_rejects_a_changed_body_and_a_wrong_key():
    key = SigningKey.generate()
    other = SigningKey.generate()
    body = b'{"type":1}'
    signature = _sign(key, body)

    assert not interaction_endpoint.verify_signature(
        key.verify_key.encode().hex(), signature, TIMESTAMP, b'{"type":2}'
    )
    assert not interaction_endpoint.verify_signature(
        other.verify_key.encode().hex(), signature, TIMESTAMP, body
    )
    assert not interaction_endpoint.verify_signature(
        key.verify_key.encode().hex(), signature, "1700000001", body
    )


def test_signature_verification_rejects_missing_or_malformed_headers():
    key = SigningKey.generate()
    body = b'{"type":1}'

    assert not interaction_endpoint.verify_signature("", _sign(key, body), TIMESTAMP, body)
    assert not interaction_endpoint.verify_signature(key.verify_key.encode().hex(), "", TIMESTAMP, body)
    assert not interaction_endpoint.verify_signature(key.verify_key.encode().hex(), _sign(key, body), "", body)
    assert not interaction_endpoint.verify_signature(key.verify_key.encode().hex(), "not-hex", TIMESTAMP, body)
    assert not interaction_endpoint.verify_signature("not-hex-either", _sign(key, body), TIMESTAMP, body)
    assert not interaction_endpoint.verify_signature(key.verify_key.encode().hex(), _sign(key, body), TIMESTAMP, b"")


# ── The route ────────────────────────────────────────────────────────────────


def test_a_request_without_a_configured_key_is_refused(monkeypatch):
    monkeypatch.setattr(interaction_endpoint, "_public_key", None)

    response = _post(interaction_routes.app.test_client(), b'{"type":1}', key=SigningKey.generate())

    assert response.status_code == 503


def test_an_unsigned_request_is_refused_without_reaching_the_bot(bot, armed, monkeypatch):
    dispatched = []
    monkeypatch.setattr(interaction_endpoint, "handle_interaction", lambda *a, **k: dispatched.append(a))

    response = _post(interaction_routes.app.test_client(), json.dumps(_slash_payload()).encode(), signed=False)

    assert response.status_code == 401
    assert dispatched == []


def test_the_ping_that_saves_the_endpoint_url_is_ponged(armed):
    response = _post(interaction_routes.app.test_client(), b'{"type":1}', key=armed)

    assert response.status_code == 200
    assert json.loads(response.data) == {"type": 1}


def test_the_captured_callback_is_returned_verbatim(bot, armed, monkeypatch):
    body = interaction_endpoint.InteractionBody(b'{"type":4,"data":{"content":"pong"}}', "application/json")
    seen = []

    def dispatch(received_bot, payload):
        seen.append((received_bot, payload))
        return body

    monkeypatch.setattr(interaction_endpoint, "handle_interaction", dispatch)
    payload = _slash_payload()

    response = _post(interaction_routes.app.test_client(), json.dumps(payload).encode(), key=armed)

    assert response.status_code == 200
    assert response.data == body.payload
    assert response.headers["Content-Type"].startswith("application/json")
    assert seen == [(bot, payload)]


def test_a_multipart_callback_keeps_its_content_type(bot, armed, monkeypatch):
    body = interaction_endpoint.InteractionBody(b"--boundary--\r\n", "multipart/form-data; boundary=boundary")
    monkeypatch.setattr(interaction_endpoint, "handle_interaction", lambda *a, **k: body)

    response = _post(interaction_routes.app.test_client(), json.dumps(_slash_payload()).encode(), key=armed)

    assert response.status_code == 200
    assert response.data == body.payload
    assert response.headers["Content-Type"] == "multipart/form-data; boundary=boundary"


def test_a_handler_that_misses_the_budget_is_acknowledged_with_202(bot, armed, monkeypatch):
    monkeypatch.setattr(interaction_endpoint, "handle_interaction", lambda *a, **k: None)

    response = _post(interaction_routes.app.test_client(), json.dumps(_slash_payload()).encode(), key=armed)

    assert response.status_code == 202
    assert response.data == b""


def test_a_bot_that_is_not_running_is_reported_as_such(bot, armed, monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise RuntimeError("The Discord bot is not running.")

    monkeypatch.setattr(interaction_endpoint, "handle_interaction", unavailable)

    response = _post(interaction_routes.app.test_client(), json.dumps(_slash_payload()).encode(), key=armed)

    assert response.status_code == 503


def test_a_handler_that_raises_does_not_look_like_a_success(bot, armed, monkeypatch):
    def broken(*_args, **_kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(interaction_endpoint, "handle_interaction", broken)

    response = _post(interaction_routes.app.test_client(), json.dumps(_slash_payload()).encode(), key=armed)

    assert response.status_code == 500


def test_a_signature_over_a_different_body_is_refused(bot, armed):
    """A signature is bound to the exact bytes Discord signed."""
    body = json.dumps(_slash_payload()).encode()
    signature = _sign(armed, body)
    client = interaction_routes.app.test_client()

    # A byte appended in transit invalidates the body half of the signature.
    extended = client.post(
        ENDPOINT,
        data=body + b" ",
        headers={"X-Signature-Ed25519": signature, "X-Signature-Timestamp": TIMESTAMP},
        content_type="application/json",
    )
    assert extended.status_code == 401
    assert "invalid request signature" in extended.get_data(as_text=True)

    # And the timestamp is signed too, so a stale header is refused as well.
    replayed = client.post(
        ENDPOINT,
        data=body,
        headers={"X-Signature-Ed25519": signature, "X-Signature-Timestamp": "1700000001"},
        content_type="application/json",
    )
    assert replayed.status_code == 401


# ── Arming the endpoint ──────────────────────────────────────────────────────


@pytest.fixture
def fresh_endpoint(monkeypatch, tmp_path):
    """An endpoint with no key resolved yet and an empty key cache."""
    monkeypatch.setattr(interaction_endpoint, "_public_key", None)
    cache = tmp_path / "interaction_public_key"
    monkeypatch.setattr(interaction_endpoint, "_KEY_CACHE", cache)
    return cache


def test_the_environment_key_is_used_without_asking_discord(fresh_endpoint, monkeypatch):
    asked = []

    async def application_info():
        asked.append(True)
        return SimpleNamespace(verify_key="ff" * 32)

    monkeypatch.setenv("DISCORD_PUBLIC_KEY", "aa" * 32)

    key = asyncio.run(
        interaction_endpoint.install_interaction_endpoint(SimpleNamespace(application_info=application_info))
    )

    assert key == "aa" * 32
    assert asked == []
    assert not fresh_endpoint.exists()
    assert getattr(AsyncWebhookAdapter.create_interaction_response, "_niko_interaction_capture", False)


def test_the_public_key_is_read_from_the_application_and_cached(fresh_endpoint, monkeypatch):
    monkeypatch.delenv("DISCORD_PUBLIC_KEY", raising=False)

    async def application_info():
        return SimpleNamespace(verify_key="bb" * 32, interactions_endpoint_url="https://niko.example/interactions")

    key = asyncio.run(
        interaction_endpoint.install_interaction_endpoint(SimpleNamespace(application_info=application_info))
    )

    assert key == "bb" * 32
    # Cached on disk: the endpoint has to keep verifying across a restart that
    # cannot reach Discord.
    assert fresh_endpoint.read_text(encoding="utf-8") == "bb" * 32


def test_a_cached_key_carries_the_endpoint_through_an_egress_outage(fresh_endpoint, monkeypatch):
    monkeypatch.delenv("DISCORD_PUBLIC_KEY", raising=False)
    fresh_endpoint.write_text("cc" * 32, encoding="utf-8")

    async def application_info():
        raise RuntimeError("Cloudflare said no")

    key = asyncio.run(
        interaction_endpoint.install_interaction_endpoint(SimpleNamespace(application_info=application_info))
    )

    assert key == "cc" * 32


def test_an_endpoint_without_any_usable_key_stays_disarmed(fresh_endpoint, monkeypatch):
    monkeypatch.delenv("DISCORD_PUBLIC_KEY", raising=False)

    async def application_info():
        raise RuntimeError("no egress either")

    key = asyncio.run(
        interaction_endpoint.install_interaction_endpoint(SimpleNamespace(application_info=application_info))
    )

    assert key is None
    assert interaction_endpoint.public_key() is None


# ── The callback body ────────────────────────────────────────────────────────


def test_a_json_callback_becomes_the_exact_request_discord_would_have_got():
    params = SimpleNamespace(payload={"type": 4, "data": {"content": "hi", "tts": False}}, multipart=None)

    body = interaction_endpoint.callback_body(params)

    assert body.content_type == "application/json"
    assert json.loads(body.payload) == {"type": 4, "data": {"content": "hi", "tts": False}}


def test_a_file_callback_becomes_a_multipart_body_with_the_same_field_names():
    handle = BytesIO(b"png-bytes")
    params = SimpleNamespace(
        payload=None,
        multipart=[
            {"name": "payload_json", "value": '{"type":4,"data":{}}'},
            {
                "name": "files[0]",
                "value": handle,
                "filename": "card.png",
                "content_type": "application/octet-stream",
            },
        ],
    )

    body = interaction_endpoint.callback_body(params)
    boundary = body.content_type.split("boundary=")[1]

    assert body.content_type.startswith("multipart/form-data; boundary=")
    assert f'--{boundary}\r\nContent-Disposition: form-data; name="payload_json"\r\n\r\n{{"type":4,"data":{{}}}}'.encode() in body.payload
    assert f'name="files[0]"; filename="card.png"'.encode() in body.payload
    assert b"png-bytes" in body.payload
    assert body.payload.endswith(f"--{boundary}--\r\n".encode())
    # The file is left where the caller had it, so a retry can send it again.
    assert handle.tell() == 0


def test_a_callback_that_cannot_be_rebuilt_is_left_to_the_normal_request():
    assert interaction_endpoint.callback_body(SimpleNamespace(payload=None, multipart=None)) is None
    assert interaction_endpoint.callback_body(SimpleNamespace(payload=None, multipart=[{"name": "x"}])) is None


def test_the_callback_response_tells_the_library_what_discord_would_have():
    deferral = SimpleNamespace(payload={"type": 5, "data": {"flags": 0}})
    ephemeral = SimpleNamespace(payload={"type": 4, "data": {"flags": 1 << 6}})
    plain = SimpleNamespace(payload={"type": 4, "data": {"content": "hi"}})

    deferred = interaction_endpoint.callback_response_payload(deferral, "42")
    assert deferred["interaction"]["response_message_loading"] is True
    assert deferred["interaction"].get("response_message_ephemeral", False) is False
    assert deferred["resource"] is None

    private = interaction_endpoint.callback_response_payload(ephemeral, "42")
    assert private["interaction"]["response_message_ephemeral"] is True

    # No message id: the message exists on Discord's side only after the endpoint
    # has answered, and views still dispatch without it.
    assert "response_message_id" not in interaction_endpoint.callback_response_payload(plain, "42")["interaction"]


def test_updating_a_message_reports_the_id_it_already_has():
    """A paginator arrow edits the message the button is on, so its id is known."""
    update = SimpleNamespace(payload={"type": 7, "data": {"components": []}})

    response = interaction_endpoint.callback_response_payload(update, "42", "987654321")

    assert response["interaction"]["response_message_id"] == "987654321"
    # Without the component's message there is nothing to report, which keeps the
    # no-message-id fallback for a view.
    assert "response_message_id" not in interaction_endpoint.callback_response_payload(update, "42")["interaction"]


# ── Capture and dispatch ─────────────────────────────────────────────────────


def test_the_captured_callback_never_leaves_the_process():
    async def scenario():
        interaction_endpoint.install_capture()
        session = FakeSession()
        sink = interaction_endpoint._InteractionSink({"id": "1"})
        token = interaction_endpoint._ACTIVE_INTERACTION.set(sink)

        params = interaction_message_response_params(type=4, content="pong")
        try:
            answer = await AsyncWebhookAdapter().create_interaction_response(
                1, "interaction-token", session=session, params=params
            )
        finally:
            interaction_endpoint._ACTIVE_INTERACTION.reset(token)

        # Discord would have answered with this; the library uses it to tell a
        # defer from a message and to store views.
        assert answer == {"interaction": {"id": "1"}, "resource": None}
        assert session.calls == []

        body = await sink.wait(1)
        assert json.loads(body.payload)["data"] == {"tts": False, "content": "pong"}
        assert body.content_type == "application/json"

    asyncio.run(scenario())


def test_a_callback_with_a_file_is_captured_as_multipart():
    """The image commands answer with a file, which cannot be sent as JSON."""

    async def scenario():
        interaction_endpoint.install_capture()
        session = FakeSession()
        sink = interaction_endpoint._InteractionSink({"id": "1"})
        token = interaction_endpoint._ACTIVE_INTERACTION.set(sink)
        params = interaction_message_response_params(
            type=4, file=discord.File(BytesIO(b"png-bytes"), "card.png")
        )
        try:
            await AsyncWebhookAdapter().create_interaction_response(
                1, "interaction-token", session=session, params=params
            )
        finally:
            interaction_endpoint._ACTIVE_INTERACTION.reset(token)
        return await sink.wait(1), session.calls

    body, calls = asyncio.run(scenario())

    assert calls == []
    assert body.content_type.startswith("multipart/form-data; boundary=")
    assert b"png-bytes" in body.payload
    assert b'name="files[0]"; filename="card.png"' in body.payload
    payload_json = body.payload.split(b"\r\n\r\n")[1].split(b"\r\n")[0]
    assert json.loads(payload_json)["type"] == 4


def test_installing_the_capture_twice_keeps_one_wrapper():
    interaction_endpoint.install_capture()
    once = AsyncWebhookAdapter.create_interaction_response

    interaction_endpoint.install_capture()

    assert AsyncWebhookAdapter.create_interaction_response is once


def test_a_handler_outside_its_interaction_still_sends_to_discord():
    async def scenario():
        interaction_endpoint.install_capture()
        session = FakeSession()

        params = interaction_message_response_params(type=4, content="pong")
        await AsyncWebhookAdapter().create_interaction_response(
            1, "interaction-token", session=session, params=params
        )

        assert session.calls == [
            (
                "POST",
                "https://discord.com/api/v10/interactions/1/interaction-token/callback",
                {"with_response": "1"},
            )
        ]

    asyncio.run(scenario())


def _fake_bot(handler):
    """A bot whose connection runs ``handler`` the way discord.py runs a command."""

    class Connection:
        @staticmethod
        def parse_interaction_create(payload):
            asyncio.ensure_future(handler(payload))

    return SimpleNamespace(loop=asyncio.get_running_loop(), _connection=Connection())


def _responder(session):
    async def handler(payload):
        # One loop hop first: discord.py schedules the command as a task too.
        await asyncio.sleep(0)
        await AsyncWebhookAdapter().create_interaction_response(
            int(payload["id"]),
            payload["token"],
            session=session,
            params=interaction_message_response_params(type=4, content="pong"),
        )

    return handler


def test_dispatch_returns_the_callback_from_another_thread():
    """The route runs on Flask's thread; the handler runs on the bot's loop."""
    interaction_endpoint.install_capture()
    session = FakeSession()
    ready = threading.Event()
    holder = {}

    def loop_thread():
        async def runner():
            # The bot is built on its own loop, exactly as the real one is before
            # the dashboard thread can see it.
            holder["bot"] = _fake_bot(_responder(session))
            ready.set()
            await asyncio.sleep(3)

        asyncio.run(runner())

    thread = threading.Thread(target=loop_thread, daemon=True)
    thread.start()
    try:
        assert ready.wait(2)

        body = interaction_endpoint.handle_interaction(holder["bot"], _slash_payload(), budget=1.0)
    finally:
        thread.join(3)

    assert body is not None
    assert json.loads(body.payload)["data"]["content"] == "pong"
    assert session.calls == []


def test_a_slow_handler_releases_the_sink_so_its_request_still_goes_out():
    interaction_endpoint.install_capture()
    session = FakeSession()

    async def slow(payload):
        await asyncio.sleep(0.4)
        await AsyncWebhookAdapter().create_interaction_response(
            int(payload["id"]),
            payload["token"],
            session=session,
            params=interaction_message_response_params(type=4, content="late"),
        )

    async def scenario():
        bot = _fake_bot(slow)
        payload = _slash_payload()
        body = await interaction_endpoint._dispatch(bot, payload, 0.05)
        assert body is None
        # The handler is still running; once it answers, the request is an
        # ordinary one again instead of vanishing into the closed sink.
        await asyncio.sleep(0.6)
        return session.calls

    calls = asyncio.run(scenario())

    assert calls == [
        (
            "POST",
            "https://discord.com/api/v10/interactions/1234567890123456789/interaction-token/callback",
            {"with_response": "1"},
        )
    ]


def _real_client(session) -> discord.Client:
    """A logged-in-enough client: what login() sets that a dispatch relies on."""
    client = discord.Client(intents=discord.Intents.none())
    client.http._HTTPClient__session = session
    client._connection.user = discord.User(
        state=client._connection,
        data={"id": 100, "username": "niko", "discriminator": "0", "global_name": "Niko", "avatar": None},
    )
    return client


def test_the_route_answers_a_real_discord_client_end_to_end(armed, monkeypatch):
    """Flask's thread, the bot's loop, discord.py's dispatch, and the body back."""
    interaction_endpoint.install_capture()
    session = FakeSession()
    ready = threading.Event()
    holder = {}

    def loop_thread():
        async def runner():
            client = _real_client(session)
            await client._async_setup_hook()

            @client.event
            async def on_interaction(interaction):
                await interaction.response.send_message("pong")

            holder["bot"] = client
            ready.set()
            await asyncio.sleep(5)

        asyncio.run(runner())

    thread = threading.Thread(target=loop_thread, daemon=True)
    thread.start()
    try:
        assert ready.wait(2)
        monkeypatch.setattr(interaction_routes, "_discord_bot", holder["bot"])
        response = _post(
            interaction_routes.app.test_client(), json.dumps(_slash_payload()).encode(), key=armed
        )
    finally:
        thread.join(5)

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    assert json.loads(response.data)["data"]["content"] == "pong"
    # The whole point: replying to Discord needed no request to Discord.
    assert session.calls == []


def test_a_real_discord_client_dispatches_the_posted_payload():
    """The endpoint feeds discord.py the same event object the gateway would."""
    interaction_endpoint.install_capture()

    async def scenario():
        client = _real_client(FakeSession())
        session = client.http._HTTPClient__session
        await client._async_setup_hook()
        answered = []

        @client.event
        async def on_interaction(interaction):
            answered.append(interaction.data["name"])
            await interaction.response.send_message("pong")

        body = await interaction_endpoint._dispatch(client, _slash_payload(), 1.0)
        return answered, body, session.calls

    answered, body, calls = asyncio.run(scenario())

    assert answered == ["ping"]
    assert json.loads(body.payload)["data"]["content"] == "pong"
    assert calls == []
