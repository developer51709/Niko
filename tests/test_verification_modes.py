"""Human verification: the three modes, the challenge store, and the web flow.

The mode is the only thing a server chooses; everything after a member proves
they are human has to be identical, because it is the same role changes and the
same audit log whichever way the answer arrived. These tests cover the shared
pieces (the store and the outcome service) and then the website route, which is
the only surface a browser touches.

The store is exercised against real SQLite — a small adapter maps the ``$1``
placeholders the bot's pool uses — so the statements themselves are tested, not
a hand-written stand-in for them.
"""

import asyncio
import io
import re
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PIL import Image  # noqa: E402

from utils.onboarding.captcha import render_captcha  # noqa: E402
from utils.onboarding.config import OnboardingConfig, _normalize  # noqa: E402
from utils.verification import ip_intel, modes, store  # noqa: E402
from webapp import app, verification_page  # noqa: E402
from webapp.routes import verification_routes as routes  # noqa: E402

SCHEMA = """
CREATE TABLE verification_challenges (
    token      TEXT PRIMARY KEY,
    guild_id   INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    code       TEXT NOT NULL,
    attempts   INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL,
    expires_at REAL NOT NULL
)
"""


class SqlitePool:
    """The subset of the bot's pool the store uses, over in-memory SQLite."""

    db_type = "sqlite"

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(SCHEMA)

    @staticmethod
    def _sql(query: str) -> str:
        return re.sub(r"\$\d+", "?", query)

    async def execute(self, query, *args):
        cursor = self.conn.execute(self._sql(query), args)
        self.conn.commit()
        return cursor

    async def fetchrow(self, query, *args):
        return self.conn.execute(self._sql(query), args).fetchone()

    async def fetchval(self, query, *args):
        row = self.conn.execute(self._sql(query), args).fetchone()
        return row[0] if row else None


def run(coro):
    return asyncio.run(coro)


def run_on_bot_loop(awaitable, timeout: float = 8):
    """The bot-loop bridge, answered inline: these tests have no running bot."""
    return asyncio.run(awaitable)


# ── modes ───────────────────────────────────────────────────────────────────


def test_every_mode_has_a_label_a_description_prompt_and_a_stored_value():
    assert modes.MODES == ("click", "image", "web")
    for mode in modes.MODES:
        assert modes.LABELS[mode]
        assert modes.DESCRIPTIONS[mode]
        assert modes.PANEL_PROMPTS[mode]


def test_unknown_modes_fall_back_to_the_dm_captcha():
    for value in (None, "", "telephone", 3, ["web"]):
        assert modes.normalize_mode(value) == modes.IMAGE
    assert modes.normalize_mode(" WEB ") == modes.WEB


def test_stored_config_normalises_a_missing_or_bogus_mode():
    assert _normalize(OnboardingConfig()).captcha_mode == "image"
    assert _normalize(OnboardingConfig(captcha_mode="web")).captcha_mode == "web"
    assert _normalize(OnboardingConfig(captcha_mode="nonsense")).captcha_mode == "image"


# ── store ───────────────────────────────────────────────────────────────────


def test_challenge_round_trips_and_is_single_use():
    pool = SqlitePool()
    challenge = run(store.create(pool, 10, 20, "ABC123"))

    stored = run(store.get(pool, challenge["token"]))
    assert stored["code"] == "ABC123"
    assert stored["attempts"] == 0
    assert stored["guild_id"] == 10 and stored["user_id"] == 20

    run(store.consume(pool, challenge["token"]))
    assert run(store.get(pool, challenge["token"])) is None


def test_tokens_are_unguessable_and_distinct():
    pool = SqlitePool()
    first = run(store.create(pool, 1, 2, "AAAAAA"))
    second = run(store.create(pool, 1, 3, "BBBBBB"))
    assert first["token"] != second["token"]
    assert len(first["token"]) > 30


def test_a_new_challenge_supersedes_the_members_previous_one():
    pool = SqlitePool()
    first = run(store.create(pool, 1, 2, "AAAAAA"))
    second = run(store.create(pool, 1, 2, "BBBBBB"))
    assert run(store.get(pool, first["token"])) is None
    assert run(store.get(pool, second["token"]))["code"] == "BBBBBB"


def test_expired_challenges_disappear_rather_than_stay_usable():
    pool = SqlitePool()
    challenge = run(store.create(pool, 1, 2, "AAAAAA", ttl_seconds=60))
    pool.conn.execute(
        "UPDATE verification_challenges SET expires_at = 0 WHERE token = ?",
        (challenge["token"],),
    )
    assert run(store.get(pool, challenge["token"])) is None
    assert run(store.get(pool, "not-a-token")) is None


def test_failures_count_up_and_rotate_the_code():
    pool = SqlitePool()
    challenge = run(store.create(pool, 1, 2, "AAAAAA"))
    assert run(store.record_failure(pool, challenge["token"], "BBBBBB")) == 1
    assert run(store.record_failure(pool, challenge["token"], "CCCCCC")) == 2
    stored = run(store.get(pool, challenge["token"]))
    assert stored["attempts"] == 2
    assert stored["code"] == "CCCCCC"


def test_purge_expired_only_touches_dead_rows():
    pool = SqlitePool()
    live = run(store.create(pool, 1, 2, "AAAAAA"))
    run(store.create(pool, 1, 3, "BBBBBB", ttl_seconds=60))
    pool.conn.execute("UPDATE verification_challenges SET expires_at = 0 WHERE user_id = 3")
    assert run(store.purge_expired(pool)) == 1
    assert run(store.get(pool, live["token"])) is not None


def test_the_store_refuses_to_pretend_when_the_database_is_missing():
    try:
        run(store.get(None, "token"))
    except store.VerificationUnavailable:
        return
    raise AssertionError("a missing pool must not read as a valid challenge")


# ── the page itself ─────────────────────────────────────────────────────────


def test_the_page_wears_the_sites_dark_palette():
    html, _ = verification_page.challenge_page(
        token="tok", guild_name="Sage Gardens", attempts_left=3,
    )
    # The page ships without the site stylesheet, so its tokens are restated:
    # canvas #050607, surface #111316, sage #8bd5b1. A white page between a dark
    # site and a dark Discord was the thing this replaced.
    assert "color-scheme: dark" in html
    assert "background: #050607" in html
    assert "#111316" in html
    assert "#8bd5b1" in html
    assert "background: #fff" not in html
    assert "background: #ffffff" not in html


def test_the_web_captcha_image_is_drawn_for_a_dark_page():
    light = verification_page_luminance(render_captcha("AB7K3M"))
    dark = verification_page_luminance(render_captcha("AB7K3M", dark=True))
    assert light > 180, "the DM image stays paper-coloured"
    assert dark < 100, "the page image must not be a white block on a dark card"


def verification_page_luminance(image_bytes) -> float:
    # BytesIO, not raw bytes: PIL would treat a bytes object as a filename.
    image = Image.open(io.BytesIO(image_bytes) if isinstance(image_bytes, bytes) else image_bytes).convert("L")
    histogram = image.histogram()
    total = sum(histogram)
    return sum(index * count for index, count in enumerate(histogram)) / max(1, total)


def test_the_stable_verification_page_carries_the_ad_unit(monkeypatch):
    """A-ADS requires one page with the unit on it, at a URL that never changes.

    Challenge links cannot be that page: they expire and every member gets a
    different one. ``/verify`` is the fixed URL registered as the ad unit's page.
    """
    monkeypatch.setenv("AADS_AD_UNIT_ID", "2448856")
    response = app.test_client().get("/verify")

    assert response.status_code == 200
    assert b'data-aa="2448856"' in response.data
    assert b"acceptable.a-ads.com/2448856" in response.data
    # The trailing-slash spelling serves the same page instead of a 404, so a
    # checker that normalises the URL still finds the unit.
    alias = app.test_client().get("/verify/")
    assert alias.status_code == 200
    assert b'data-aa="2448856"' in alias.data


def test_the_stable_page_works_without_the_bot_or_a_database(monkeypatch):
    """The ad network's own checker must be able to load it while the bot is down."""
    monkeypatch.setattr(routes, "_discord_bot", None)

    def unreachable(*_args, **_kwargs):
        raise AssertionError("the entry page must not touch the bot loop")

    monkeypatch.setattr(routes, "run_on_bot_loop", unreachable)
    monkeypatch.setenv("AADS_AD_UNIT_ID", "2448856")

    response = app.test_client().get("/verify")

    assert response.status_code == 200
    assert b'data-aa="2448856"' in response.data


def test_the_stable_page_serves_even_before_an_ad_unit_is_configured(monkeypatch):
    monkeypatch.delenv("AADS_AD_UNIT_ID", raising=False)
    response = app.test_client().get("/verify")
    assert response.status_code == 200
    assert b"data-aa" not in response.data


def test_the_ad_page_is_served_at_a_fixed_route_not_a_catch_all():
    # A rename would silently move the URL the ad unit is registered against.
    rules = {rule.rule: rule.endpoint for rule in app.url_map.iter_rules()}
    assert rules.get("/verify") == "verification_entry_page"


def test_the_challenge_page_is_scriptless_and_carries_the_captcha(monkeypatch):
    monkeypatch.delenv("AADS_AD_UNIT_ID", raising=False)
    html, status = verification_page.challenge_page(
        token="tok", guild_name="Sage Gardens", attempts_left=3,
    )
    assert status == 200
    assert "Sage Gardens" in html
    assert "/verify/tok/captcha.png" in html
    assert "<script" not in html.lower()
    assert "data-aa" not in html  # no ad unit configured
    assert 'name="robots" content="noindex, nofollow"' in html


def test_the_ad_slot_uses_the_aads_unit_when_one_is_configured(monkeypatch):
    monkeypatch.setenv("AADS_AD_UNIT_ID", "2448856")
    html, _ = verification_page.challenge_page(
        token="tok", guild_name="Sage Gardens", attempts_left=3,
    )
    assert 'data-aa="2448856"' in html
    assert "acceptable.a-ads.com/2448856" in html
    # A non-numeric value is a misconfiguration, not a broken page.
    monkeypatch.setenv("AADS_AD_UNIT_ID", "publisher-name")
    html, _ = verification_page.challenge_page(
        token="tok", guild_name="Sage Gardens", attempts_left=3,
    )
    assert "data-aa" not in html


def test_notice_pages_never_show_ads(monkeypatch):
    monkeypatch.setenv("AADS_AD_UNIT_ID", "2448856")
    html, status = verification_page.notice_page(
        "Verification blocked", "Turn your VPN off.", tone="blocked", ad=False,
    )
    assert status == 403
    assert "data-aa" not in html


# ── the web route ───────────────────────────────────────────────────────────


class FakeRole:
    def __init__(self, role_id, name):
        self.id = role_id
        self.name = name


class FakeMember:
    def __init__(self, member_id):
        self.id = member_id
        self.name = "member"
        self.mention = f"<@{member_id}>"
        self.roles = []
        self.kicked = 0

    def __str__(self):
        return self.name

    async def add_roles(self, *roles, reason=None):
        self.roles.extend(role for role in roles if role not in self.roles)

    async def remove_roles(self, *roles, reason=None):
        self.roles = [role for role in self.roles if role not in roles]

    async def kick(self, reason=None):
        self.kicked += 1


class FakeGuild:
    def __init__(self, guild_id=10):
        self.id = guild_id
        self.name = "Sage Gardens"
        self.member = FakeMember(20)
        self.roles = {1: FakeRole(1, "Verified"), 2: FakeRole(2, "Unverified")}
        self.member.roles = [self.roles[2]]

    def get_role(self, role_id):
        return self.roles.get(int(role_id))

    def get_member(self, user_id):
        return self.member if int(user_id) == self.member.id else None


class FakeBot:
    def __init__(self, pool):
        self.cxn = pool
        self.guild = FakeGuild()
        self.loop = SimpleNamespace(is_running=lambda: True)

    def get_guild(self, guild_id):
        return self.guild if int(guild_id) == self.guild.id else None

    def get_cog(self, name):
        return None


def web_config(**overrides):
    base = dict(
        captcha_enabled=True,
        captcha_mode="web",
        captcha_add_role_ids=[1],
        captcha_remove_role_ids=[2],
        captcha_kick_on_fail=False,
    )
    base.update(overrides)
    return OnboardingConfig(**base)


async def _load_config(guild_id):
    return CURRENT_CONFIG["cfg"]


CURRENT_CONFIG = {"cfg": web_config()}


def prepare(monkeypatch, **config):
    """Point the route at a fake bot, a real SQLite challenge table, and config."""
    pool = SqlitePool()
    bot = FakeBot(pool)
    CURRENT_CONFIG["cfg"] = web_config(**config)
    monkeypatch.setattr(routes, "_discord_bot", bot)
    monkeypatch.setattr(routes, "load_config", _load_config)
    monkeypatch.setattr(routes, "run_on_bot_loop", run_on_bot_loop)
    # The outcome service loads the same guild config from its own module.
    monkeypatch.setattr("utils.verification.service.load_config", _load_config)
    return pool, bot


def issue(pool, guild_id=10, user_id=20, code="AAAAAA"):
    return run(store.create(pool, guild_id, user_id, code))


def test_the_page_renders_the_challenge_for_a_live_token(monkeypatch):
    pool, _bot = prepare(monkeypatch)
    challenge = issue(pool)
    client = app.test_client()

    response = client.get(f"/verify/{challenge['token']}")

    assert response.status_code == 200
    assert b"Sage Gardens" in response.data
    assert b"/captcha.png" in response.data
    assert response.headers["Cache-Control"].startswith("no-store")
    assert response.headers["X-Robots-Tag"].startswith("noindex")


def test_the_captcha_image_is_served_and_never_cached(monkeypatch):
    pool, _bot = prepare(monkeypatch)
    challenge = issue(pool)

    response = app.test_client().get(f"/verify/{challenge['token']}/captcha.png")

    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data.startswith(b"\x89PNG")
    assert response.headers["Cache-Control"].startswith("no-store")
    # The route draws the dark variant that matches the page around it.
    assert verification_page_luminance(response.data) < 100


def test_an_unknown_token_is_reported_as_expired(monkeypatch):
    prepare(monkeypatch)
    response = app.test_client().get("/verify/nope")
    assert response.status_code == 410
    assert b"expired" in response.data.lower()


def test_a_role_change_removes_the_link_so_it_cannot_be_replayed(monkeypatch):
    pool, bot = prepare(monkeypatch)
    challenge = issue(pool)
    client = app.test_client()

    response = client.post(f"/verify/{challenge['token']}", data={"answer": "aaaaaa"})

    assert response.status_code == 200
    assert b"verified" in response.data.lower()
    member = bot.guild.member
    assert bot.guild.roles[1] in member.roles
    assert bot.guild.roles[2] not in member.roles
    # The answer was consumed, so the same link cannot re-run the role change.
    assert run(store.get(pool, challenge["token"])) is None
    assert client.get(f"/verify/{challenge['token']}").status_code == 410


def test_a_wrong_answer_burns_an_attempt_and_shows_a_new_code(monkeypatch):
    pool, _bot = prepare(monkeypatch)
    challenge = issue(pool)

    response = app.test_client().post(
        f"/verify/{challenge['token']}", data={"answer": "WRONG"},
    )

    assert response.status_code == 200
    assert b"not the code" in response.data.lower()
    stored = run(store.get(pool, challenge["token"]))
    assert stored["attempts"] == 1
    assert stored["code"] != "AAAAAA"


def test_an_empty_submission_does_not_spend_an_attempt(monkeypatch):
    pool, _bot = prepare(monkeypatch)
    challenge = issue(pool)

    response = app.test_client().post(f"/verify/{challenge['token']}", data={"answer": "  "})

    assert response.status_code == 200
    assert run(store.get(pool, challenge["token"]))["attempts"] == 0


def test_the_third_wrong_answer_fails_and_kicks_when_configured(monkeypatch):
    pool, bot = prepare(monkeypatch, captcha_kick_on_fail=True)
    challenge = issue(pool)
    client = app.test_client()
    member = bot.guild.member

    for _ in range(store.MAX_ATTEMPTS):
        response = client.post(f"/verify/{challenge['token']}", data={"answer": "WRONG"})

    assert response.status_code == 410
    assert b"verification failed" in response.data.lower()
    assert member.kicked == 1
    # The challenge is spent, not left for a fourth try.
    assert run(store.get(pool, challenge["token"])) is None


def test_a_link_stops_working_when_the_server_switches_method(monkeypatch):
    pool, _bot = prepare(monkeypatch)
    challenge = issue(pool)
    CURRENT_CONFIG["cfg"] = web_config(captcha_mode="click")

    response = app.test_client().get(f"/verify/{challenge['token']}")

    assert response.status_code == 410
    assert b"no longer using" in response.data.lower()


def test_a_disabled_verification_panel_invalidates_outstanding_links(monkeypatch):
    pool, _bot = prepare(monkeypatch)
    challenge = issue(pool)
    CURRENT_CONFIG["cfg"] = web_config(captcha_enabled=False)

    assert app.test_client().get(f"/verify/{challenge['token']}").status_code == 410


def test_proxy_restrictions_refuse_the_page_before_the_challenge(monkeypatch):
    pool, _bot = prepare(monkeypatch, captcha_block_proxies=True)
    challenge = issue(pool)
    monkeypatch.setattr(
        routes.ip_intel, "refusal",
        lambda ip, block_proxies, block_vpn: "proxy" if block_proxies else None,
    )

    response = app.test_client().get(
        f"/verify/{challenge['token']}", headers={"X-Forwarded-For": "203.0.113.9"},
    )

    assert response.status_code == 403
    assert b"proxy" in response.data.lower()
    assert b"/captcha.png" not in response.data


def test_vpn_restrictions_are_separate_from_proxy_restrictions(monkeypatch):
    ip_intel.clear_cache()
    hosting = {"proxy": False, "hosting": True, "mobile": False, "country": "US"}
    monkeypatch.setattr(ip_intel, "lookup", lambda ip: hosting)
    assert ip_intel.refusal("203.0.113.9", block_proxies=True, block_vpn=False) is None
    assert ip_intel.refusal("203.0.113.9", block_proxies=False, block_vpn=True) == "vpn"
    assert ip_intel.refusal("203.0.113.9", block_proxies=False, block_vpn=False) is None


def test_private_addresses_are_never_looked_up():
    ip_intel.clear_cache()
    flags = ip_intel.lookup("127.0.0.1")
    assert flags == {"proxy": False, "hosting": False, "mobile": False, "country": None}


def test_the_forwarded_client_address_wins_over_the_proxy():
    assert ip_intel.client_ip("10.0.0.1", "203.0.113.5, 10.0.0.1") == "203.0.113.5"
    assert ip_intel.client_ip("10.0.0.1", None) == "10.0.0.1"
    assert ip_intel.client_ip(None, None) == ""
