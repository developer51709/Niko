"""Unused subdomains answer 404; used hosts leave unknown paths to the client."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app, config, site_build  # noqa: E402

SITE = "https://niko.sryze.cc"


@pytest.fixture
def site(monkeypatch):
    """Subdomain routing on, with the site's own domain configured."""
    monkeypatch.setattr(config, "SUBDOMAIN_ROUTING", True)
    monkeypatch.setenv("PUBLIC_URL", SITE)
    return config


def _shell(client, path: str, host: str):
    return client.get(path, base_url=f"https://{host}", headers={"Accept": "text/html"})


def _state(body: str) -> dict:
    return json.loads(body.split("window.__NIKO_SHELL__=", 1)[1].split("</script>", 1)[0])


def test_a_host_under_the_domain_that_serves_nothing_is_unknown(site):
    assert site.unknown_subdomain("foo.niko.sryze.cc") is True
    assert site.unknown_subdomain("anything.bar.niko.sryze.cc") is True


def test_the_hosts_the_site_serves_are_not_unknown(site):
    # The apex, its www alias and every section the site answers for.
    assert site.unknown_subdomain("niko.sryze.cc") is False
    assert site.unknown_subdomain("www.niko.sryze.cc") is False
    assert site.unknown_subdomain("dash.niko.sryze.cc") is False
    assert site.unknown_subdomain("dash.niko.sryze.cc:443") is False


def test_a_host_outside_the_site_is_left_alone(site):
    # A preview host, an unrelated domain or a bare address is not this site's
    # to answer for, even when it carries a label that is not a section.
    assert site.unknown_subdomain("preview.onrender.com") is False
    assert site.unknown_subdomain("foo.example.com") is False
    assert site.unknown_subdomain("localhost:5000") is False
    assert site.unknown_subdomain(None) is False


def test_nothing_is_unknown_without_the_switch(monkeypatch):
    monkeypatch.setattr(config, "SUBDOMAIN_ROUTING", False)
    monkeypatch.setenv("PUBLIC_URL", SITE)

    assert config.unknown_subdomain("foo.niko.sryze.cc") is False


def test_nothing_is_unknown_without_a_configured_domain(site, monkeypatch):
    # Without PUBLIC_URL the request alone cannot tell an unused subdomain of
    # the site from somebody else's host, so nothing is claimed.
    monkeypatch.delenv("PUBLIC_URL", raising=False)

    assert site.unknown_subdomain("foo.niko.sryze.cc") is False


def test_an_unused_subdomain_answers_with_the_subdomain_variant(site):
    response = _shell(app.test_client(), "/anything", "foo.niko.sryze.cc")
    body = response.get_data(as_text=True)

    # A real 404: there is no page behind this host.
    assert response.status_code == 404
    state = _state(body)
    assert state["unknown"] is True
    # The page links out to the site, so the server names it.
    assert state["site"] == SITE
    # A wrong host never pretends to be a section.
    assert "prefix" not in state


def test_the_root_of_an_unused_subdomain_is_also_a_404(site):
    response = _shell(app.test_client(), "/", "foo.niko.sryze.cc")

    assert response.status_code == 404
    assert _state(response.get_data(as_text=True))["unknown"] is True


def test_the_404_page_can_still_load_its_own_files(site):
    # The shell is HTML; its bundle, stylesheet and icons are static files on the
    # same host, and answering those with the 404 page would render a blank one.
    client = app.test_client()
    entry = site_build.build_id()
    assert entry, "the build on disk should name its entry script"

    for path in (entry, "/manifest.webmanifest", "/favicon.svg"):
        response = client.get(path, base_url="https://foo.niko.sryze.cc")

        assert response.status_code == 200, path
        assert response.mimetype != "text/html", path


def test_the_api_still_answers_on_an_unused_subdomain(site):
    # Refusing the API would turn a wrong host into a broken page instead of a
    # 404 page that renders.
    response = app.test_client().get("/api/health", base_url="https://foo.niko.sryze.cc", headers={"Accept": "application/json"})

    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_a_used_host_leaves_unknown_paths_to_the_page_variant(site):
    for host in ("niko.sryze.cc", "dash.niko.sryze.cc", "www.niko.sryze.cc"):
        response = _shell(app.test_client(), "/no-such-page", host)
        body = response.get_data(as_text=True)
        state = _state(body)

        # The server cannot know the client's routes, so this stays a 200 and
        # the page variant is chosen in the browser.
        assert response.status_code == 200, host
        assert "unknown" not in state, host


def test_with_the_switch_off_an_unused_subdomain_serves_the_site(monkeypatch):
    monkeypatch.setattr(config, "SUBDOMAIN_ROUTING", False)
    monkeypatch.setenv("PUBLIC_URL", SITE)

    response = _shell(app.test_client(), "/no-such-page", "foo.niko.sryze.cc")

    assert response.status_code == 200
    assert "unknown" not in _state(response.get_data(as_text=True))
