"""Tests for the fake credential files served to secret-scanning crawlers."""

import io
import itertools
import json
import logging
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app, honeypot
from webapp.honeypot import easter_eggs, nyancat
from webapp.routes import security_decoy_routes as decoys

ROOT = Path(__file__).resolve().parents[1]


def _env_body(client=None) -> str:
    client = client or app.test_client()
    response = client.get("/." + "env")
    assert response.status_code == 200
    return response.get_data(as_text=True)


def _dotenv_pairs(body: str) -> dict[str, str]:
    pairs = {}
    for line in body.splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        pairs[key] = value
    return pairs


def test_every_decoy_path_answers_with_a_file():
    client = app.test_client()
    for path in honeypot.paths():
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.get_data(), path
        assert response.headers["Cache-Control"] == "no-store", path
        assert response.headers["X-Robots-Tag"] == "noindex, nofollow", path


def test_no_decoy_shadows_a_real_route_or_a_shipped_file():
    rules = {rule.rule: rule.endpoint for rule in app.url_map.iter_rules()}
    for path in honeypot.paths():
        assert rules[path].startswith("decoy_probe_"), path
    assert decoys.DECOY_COUNT == len(honeypot.paths())


def test_the_env_decoy_reads_like_a_deployment():
    body = _env_body()
    pairs = _dotenv_pairs(body)
    assert pairs["DISCORD_BOT_TOKEN"]
    assert pairs["MONGODB_URL"].startswith("mongodb+srv://")
    assert pairs["PUBLIC_URL"] == "https://niko.sryze.cc"
    # The donation site is the public site; there is nothing to hide there.
    assert pairs["DONATION_SITE_URL"] == pairs["PUBLIC_URL"]
    # Every line is either a comment, blank, or KEY=value.
    for line in body.splitlines():
        assert not line or line.startswith("#") or "=" in line


def test_the_decoys_agree_with_each_other():
    client = app.test_client()
    env = _dotenv_pairs(_env_body(client))
    password = env["POSTGRES_URL"].split("://", 1)[1].split("@", 1)[0].split(":", 1)[1]

    pgpass = client.get("/.pgpass").get_data(as_text=True)
    assert f":{password}\n" in pgpass or pgpass.startswith("pg-primary.internal")

    compose = client.get("/docker-compose.yml").get_data(as_text=True)
    assert f"POSTGRES_PASSWORD: {password}" in compose

    credentials = json.loads(client.get("/credentials.json").get_data(as_text=True))
    assert credentials["postgres"]["password"] == password
    assert credentials["discord"]["token"] == env["DISCORD_BOT_TOKEN"]


def test_json_decoys_are_valid_json():
    client = app.test_client()
    for path in honeypot.paths():
        payload, mimetype = honeypot.body_for(path)
        if mimetype != "application/json":
            continue
        document = json.loads(client.get(path).get_data(as_text=True))
        assert isinstance(document, (dict, list)), path


def test_the_fake_service_hosts_play_a_terminal_animation(monkeypatch):
    monkeypatch.setattr(easter_eggs, "FRAME_DELAY", 0.0)
    monkeypatch.setattr(nyancat, "FRAME_DELAY", 0.0)
    client = app.test_client()
    for host, marker in (
        ("db.niko.sryze.cc", "nyan"),
        ("read.db.niko.sryze.cc", "nyan"),
        ("cache.niko.sryze.cc", "nyan"),
        ("vault.niko.sryze.cc", "Never gonna"),
        ("queue.niko.sryze.cc", "Never gonna"),
    ):
        response = client.get(
            "/api/overview", headers={"X-Forwarded-Host": host}
        )
        assert response.status_code == 200, host
        assert response.mimetype == "text/plain", host
        # ``no-transform`` has to survive the global /api/ no-store hook.
        assert "no-transform" in response.headers["Cache-Control"], host
        body = response.get_data(as_text=True)
        assert "\x1b[" in body, host
        assert marker.lower() in body.lower(), host
        assert "decoy host" in body, host
        assert "https://github.com/developer51709/Niko" in body


def test_only_the_fake_service_hosts_are_animated(monkeypatch):
    monkeypatch.setattr(easter_eggs, "FRAME_DELAY", 0.0)
    client = app.test_client()
    for host in ("niko.sryze.cc", "www.niko.sryze.cc", "dash.niko.sryze.cc"):
        body = client.get("/", headers={"X-Forwarded-Host": host}).get_data(
            as_text=True
        )
        assert "\x1b[?25l" not in body, host
    head = client.head("/", headers={"X-Forwarded-Host": "vault.niko.sryze.cc"})
    assert head.status_code == 200
    assert head.get_data() == b""


def test_the_nyan_host_introduces_itself_and_streams_until_ctrl_c(monkeypatch):
    monkeypatch.setattr(nyancat, "INTRO_DELAY", 0.0)
    monkeypatch.setattr(easter_eggs, "FRAME_DELAY", 0.0)
    client = app.test_client()
    # Even a decoy path on the fun host plays the animation instead of
    # serving the fake credentials: this host has no other purpose.
    response = client.get(
        "/" + ".env",
        headers={"X-Forwarded-Host": "nyan.niko.sryze.cc"},
        buffered=False,
    )
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    chunks = [
        chunk.decode("utf-8", "replace")
        for chunk in itertools.islice(response.response, 12)
    ]
    response.close()
    # Closing the request (what Ctrl+C does to the connection) ends the
    # generator and frees its stream slot.
    assert decoys._egg_streams == 0
    body = "".join(chunks)
    assert "N Y A N   C A T" in body
    assert "press Ctrl+C to stop" in body
    assert "klange/nyancat" in body
    # Ctrl+C disconnects before any closing frame, so never hide the cursor.
    assert "\x1b[?25l" not in body
    for word in ("decoy", "credential", "honeypot", "POSTGRES_URL"):
        assert word not in body, word

    # The fun host never ends the animation on its own.
    endless = list(
        itertools.islice(
            easter_eggs.frames("nyan", "nyan.niko.sryze.cc", decoy=False), 150
        )
    )
    assert len(endless) == 150


def test_the_nyan_egg_is_the_vendored_klange_animation():
    assert len(nyancat.FRAMES) == 12
    for frame in nyancat.FRAMES:
        assert len(frame) == 64
        assert all(len(row) == 64 for row in frame)
        assert set("".join(frame)) <= set(nyancat.COLORS)

    rendered = nyancat._render(0, 7)
    assert rendered.startswith("\x1b[H")
    assert rendered.count("\n") == 23
    assert "\x1b[48;5;17m" in rendered
    assert "You have nyaned for 7 seconds!" in rendered


def test_the_decoy_animations_are_finite_and_restore_the_cursor():
    for kind in ("nyan", "rickroll"):
        frames = list(easter_eggs.frames(kind, "db.niko.sryze.cc"))
        if kind == "nyan":
            # clear + the twelve-frame loop for a while + the closing card
            assert len(frames) == nyancat.FRAME_COUNT + 2
        else:
            assert len(frames) == easter_eggs.FRAME_COUNT[kind] + 1
        assert all(isinstance(delay, float) for delay, _ in frames)
        assert "\x1b[?25l" in frames[0][1]
        assert "\x1b[?25h" in frames[-1][1]
        assert "db.niko.sryze.cc" in frames[-1][1]


def test_the_decoys_point_at_the_fake_service_hosts():
    pairs = _dotenv_pairs(_env_body())
    assert pairs["POSTGRES_URL"].endswith("@db.niko.sryze.cc:5432/niko_production")
    assert pairs["REDIS_URL"].endswith("@cache.niko.sryze.cc:6379/0")
    assert pairs["VAULT_ADDR"] == "https://vault.niko.sryze.cc"
    assert pairs["RABBITMQ_URL"].endswith("@queue.niko.sryze.cc:5672/niko")


def test_the_staff_addresses_are_the_public_ones():
    # ``niko-internal.example`` stays for internal hosts, never for a mailbox:
    # the shared staff addresses are public, and an invented address that
    # bounces is a hint that the file is fake.
    for path in honeypot.paths():
        payload, _ = honeypot.body_for(path)
        text = (
            payload.decode("utf-8", "replace")
            if isinstance(payload, bytes)
            else payload
        )
        assert "@niko-internal.example" not in text, path

    dump = app.test_client().get("/dump.sql").get_data(as_text=True)
    for address in (
        "owner@niko.sryze.cc",
        "admin@niko.sryze.cc",
        "support@niko.sryze.cc",
        "support-lead@niko.sryze.cc",
    ):
        assert address in dump


def test_the_backup_zip_holds_the_fake_files():
    response = app.test_client().get("/backup.zip")
    assert response.mimetype == "application/zip"
    with zipfile.ZipFile(io.BytesIO(response.get_data())) as archive:
        names = set(archive.namelist())
        assert {".env", "dump.sql", "service-account.json"} <= names
        assert b"DISCORD_BOT_TOKEN=" in archive.read(".env")


def test_the_swap_file_is_binary():
    response = app.test_client().get("/." + "env.swp")
    assert response.mimetype == "application/octet-stream"
    assert response.get_data().startswith(b"b0VIM")


def test_the_decoys_are_stable_between_requests():
    client = app.test_client()
    first = client.get("/dump.sql").get_data()
    second = client.get("/dump.sql").get_data()
    assert first == second
    assert b"INSERT INTO `users`" in first


def test_the_dump_has_rows_to_sort_through():
    body = app.test_client().get("/dump.sql").get_data(as_text=True)
    assert body.count("','203.0.113.") >= 150
    assert "INSERT INTO `sessions`" in body
    assert "INSERT INTO `payments`" in body
    assert "$2b$12$" in body


def test_real_routes_keep_their_normal_responses():
    client = app.test_client()
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.mimetype == "application/json"
    shell = client.get("/dashboard")
    assert shell.status_code == 200
    assert shell.mimetype == "text/html"
    unknown = client.get("/api/definitely-not-a-route")
    assert unknown.status_code == 404


def test_a_probe_burst_is_collapsed_into_one_log_line(caplog):
    decoys._hits.clear()
    client = app.test_client()
    with caplog.at_level(logging.INFO, logger="Honeypot"):
        for path in ("/." + "env", "/.aws/credentials", "/.npmrc"):
            client.get(path, headers={"X-Forwarded-For": "203.0.113.77"})
    lines = [record for record in caplog.records if record.name == "Honeypot"]
    assert len(lines) == 1
    assert "203.0.113.77" in lines[0].getMessage()
    decoys._hits.clear()


def test_the_generator_never_reads_real_configuration():
    for name in (
        "__init__.py",
        "env.py",
        "configs.py",
        "stores.py",
        "values.py",
        "easter_eggs.py",
        "nyancat.py",
        "nyancat_frames.py",
    ):
        source = (ROOT / "src" / "webapp" / "honeypot" / name).read_text(
            encoding="utf-8"
        )
        assert "os.environ" not in source, name
        assert "os.getenv" not in source, name
        assert "from .config" not in source, name
        assert "from ..config" not in source, name


def test_security_txt_is_machine_readable_and_points_reports_at_the_team():
    response = app.test_client().get("/.well-known/security.txt")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "Contact: https://niko.sryze.cc/discord" in body
    assert "Contact: https://github.com/developer51709/Niko/security/advisories/new" in body
    assert "Expires: 2027-12-31T23:59:59.000Z" in body
    assert "Preferred-Languages: en" in body
