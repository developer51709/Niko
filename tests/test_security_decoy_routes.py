"""Tests for the friendly security decoys served to secret-scanning crawlers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app


def test_secret_probe_paths_return_the_friendly_security_notice():
    client = app.test_client()
    for path in (
        "/.env",
        "/.env.local",
        "/.git/config",
        "/.git/HEAD",
        "/wp-config.php",
        "/config.php",
        "/credentials.json",
        "/backup.sql",
        "/.aws/credentials",
        "/.ssh/id_rsa",
        "/docker-compose.yml",
        "/phpinfo.php",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.mimetype == "text/plain"
        body = response.get_data(as_text=True)
        flat = " ".join(body.split())
        assert path in body
        assert "This is a decoy file" in body
        assert "https://github.com/developer51709/Niko" in body
        assert "https://niko.sryze.cc/discord" in body
        assert "#community-help" in body
        assert "#create-a-ticket" in body
        assert "Bug Bounty" in body
        assert "vulnerability fixed is a potential future incident prevented" in flat
        assert "users' privacy" in body
        assert response.headers["Cache-Control"] == "no-store"
        assert response.headers["X-Robots-Tag"] == "noindex, nofollow"


def test_security_txt_is_machine_readable_and_points_reports_at_the_team():
    response = app.test_client().get("/.well-known/security.txt")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "Contact: https://niko.sryze.cc/discord" in body
    assert "Contact: https://github.com/developer51709/Niko/security/advisories/new" in body
    assert "Expires: 2027-12-31T23:59:59.000Z" in body
    assert "Preferred-Languages: en" in body


def test_api_and_spa_routes_keep_their_normal_responses():
    client = app.test_client()
    api = client.get("/api/definitely-not-a-route")
    assert api.status_code == 404
    assert api.mimetype == "application/json"
    shell = client.get("/dashboard")
    assert shell.status_code == 200
    assert shell.mimetype == "text/html"
