"""Section subdomains: ``dash.example.com/staff`` is ``/dashboard/staff``."""

import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from flask import session as flask_session

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app, config  # noqa: E402


@pytest.fixture
def subdomains(monkeypatch):
    """Turn the switch on for one test; the module reads it per request."""
    monkeypatch.setattr(config, "SUBDOMAIN_ROUTING", True)
    return config


def _shell(client, path: str, base_url: str = "https://dash.niko.sryze.cc"):
    return client.get(path, base_url=base_url, headers={"Accept": "text/html"})


def test_the_switch_is_off_unless_it_is_set(monkeypatch):
    monkeypatch.setattr(config, "SUBDOMAIN_ROUTING", False)
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")

    assert config.subdomain_prefix("dash.niko.sryze.cc") == ""
    # Nothing is shared across hosts while the feature is off.
    assert config.session_cookie_domain() == ""


def test_the_dashboard_label_maps_to_the_dashboard_path(subdomains):
    assert subdomains.subdomain_prefix("dash.niko.sryze.cc") == "/dashboard"


def test_only_the_first_label_selects_a_section(subdomains):
    # A wildcard certificate and one DNS record cover every deployment host.
    assert subdomains.subdomain_prefix("dash.staging.niko.sryze.cc") == "/dashboard"
    assert subdomains.subdomain_prefix("DASH.niko.sryze.cc:443") == "/dashboard"


def test_the_apex_and_unknown_hosts_keep_the_normal_site(subdomains):
    assert subdomains.subdomain_prefix("niko.sryze.cc") == ""
    assert subdomains.subdomain_prefix("www.niko.sryze.cc") == ""
    assert subdomains.subdomain_prefix("localhost:5000") == ""
    assert subdomains.subdomain_prefix("beta.niko.sryze.cc") == ""
    assert subdomains.subdomain_prefix(None) == ""


def test_a_section_host_tells_the_shell_which_path_it_stands_in_for(subdomains):
    body = _shell(app.test_client(), "/staff").get_data(as_text=True)

    # The client applies this prefix to the path it reads; without it `/staff`
    # would be the home page.
    assert 'window.__NIKO_SHELL__={"build":' in body
    assert '"prefix": "/dashboard"' in body
    # Metadata describes the dashboard page, not the home page, and points at
    # the apex form of the same page.
    assert "https://niko.sryze.cc/dashboard/staff" in body


def test_a_proxied_section_host_is_read_from_the_forwarded_name(subdomains):
    # A reverse proxy may keep the internal address in Host and forward the
    # public one beside it.
    response = app.test_client().get(
        "/staff",
        base_url="http://127.0.0.1:5000",
        headers={"Accept": "text/html", "X-Forwarded-Host": "dash.niko.sryze.cc"},
    )

    assert '"prefix": "/dashboard"' in response.get_data(as_text=True)


def test_the_apex_shell_carries_no_prefix(subdomains):
    response = _shell(app.test_client(), "/staff", base_url="https://niko.sryze.cc")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    # The build id is always there; the path prefix is what only a section host
    # needs, and adding it here would shorten the apex's own links.
    assert "__NIKO_SHELL__" in body
    assert '"prefix"' not in body


def test_the_long_form_on_a_section_host_lands_on_the_short_one(subdomains):
    client = app.test_client()

    response = client.get("/dashboard/staff", base_url="https://dash.niko.sryze.cc")
    assert response.status_code == 301
    assert response.headers["Location"] == "/staff"

    # The dashboard root is the subdomain's own root.
    response = client.get("/dashboard", base_url="https://dash.niko.sryze.cc")
    assert response.status_code == 301
    assert response.headers["Location"] == "/"

    # A query string survives the hop.
    response = client.get("/dashboard/staff?tab=email", base_url="https://dash.niko.sryze.cc")
    assert response.headers["Location"] == "/staff?tab=email"


def test_the_long_form_on_the_apex_is_not_redirected(subdomains):
    response = app.test_client().get("/dashboard/staff", base_url="https://niko.sryze.cc")

    assert response.status_code == 200


def test_the_api_is_served_unchanged_on_a_section_host(subdomains):
    response = app.test_client().get("/api/health", base_url="https://dash.niko.sryze.cc")

    # Nothing under /api/ is a page, so no host may rewrite or redirect it.
    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_the_canonical_origin_decides_the_shared_domain(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc/")

    # The cookie belongs to the whole domain so both the apex and `dash.` see
    # the same session.
    assert subdomains.session_cookie_domain() == ".niko.sryze.cc"


@pytest.mark.parametrize("public_url", ["", "https://localhost:5000", "http://127.0.0.1:5000"])
def test_a_host_without_a_domain_shares_nothing(subdomains, monkeypatch, public_url):
    monkeypatch.setenv("PUBLIC_URL", public_url)

    assert subdomains.session_cookie_domain() == ""


def test_a_section_host_carries_the_shared_cookie(subdomains, monkeypatch):
    monkeypatch.setitem(app.config, "SESSION_COOKIE_DOMAIN", ".niko.sryze.cc")

    response = app.test_client().get(
        "/auth/logout",
        base_url="https://dash.niko.sryze.cc",
        headers={"Accept": "text/html"},
    )

    cookie = response.headers.get("Set-Cookie", "")
    # A session cookie set while the visitor is on the subdomain must belong to
    # the domain, or signing in there would not be seen on the apex. Werkzeug
    # writes it without the leading dot that ``.domain`` implies.
    assert "Domain=niko.sryze.cc" in cookie


def test_every_section_is_known_by_the_origin_that_serves_it(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc/")

    assert subdomains.section_origins() == {"/dashboard": "https://dash.niko.sryze.cc"}


@pytest.mark.parametrize("public_url", ["", "not-a-url"])
def test_a_site_that_cannot_name_itself_names_no_sections(subdomains, monkeypatch, public_url):
    monkeypatch.setenv("PUBLIC_URL", public_url)

    # An unknown origin (or a bare host) leaves every section link relative.
    assert subdomains.section_origins() == {}


def test_a_port_on_the_site_survives_the_section_origin(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "http://localhost:5000")

    assert subdomains.section_origins() == {"/dashboard": "http://dash.localhost:5000"}


def test_the_apex_shell_says_where_the_dashboard_lives(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")

    body = _shell(app.test_client(), "/", base_url="https://niko.sryze.cc").get_data(as_text=True)

    # The apex keeps its own paths, but its dashboard link has to reach the
    # section host, or it would land on the long form.
    assert '"sections": {"/dashboard": "https://dash.niko.sryze.cc"}' in body


def test_the_shell_names_no_sections_without_the_switch(monkeypatch):
    monkeypatch.setattr(config, "SUBDOMAIN_ROUTING", False)
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")

    body = _shell(app.test_client(), "/", base_url="https://niko.sryze.cc").get_data(as_text=True)

    assert '"sections"' not in body


def _redirect_uri_param(response) -> str:
    location = response.headers["Location"]
    assert location.startswith("https://discord.com/oauth2/authorize?")
    return parse_qs(urlparse(location).query)["redirect_uri"][0]


def test_a_section_host_signs_in_through_the_sites_own_callback(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    monkeypatch.setattr(config, "DISCORD_CLIENT_SECRET", "test-secret")
    # The deployment's own registered callback and the development fallback are
    # both unset here, so this is the address the server works out itself.
    monkeypatch.delenv("DISCORD_REDIRECT_URI", raising=False)
    monkeypatch.delenv("REPLIT_DEV_DOMAIN", raising=False)
    client = app.test_client()

    # Discord refuses a redirect_uri it has not been given, and `dash.` is not
    # one of them: the sign-in has to name the site's one callback even when it
    # starts on a section host.
    shared = _redirect_uri_param(client.get("/auth/login?next=/staff", base_url="https://dash.niko.sryze.cc"))
    apex = _redirect_uri_param(client.get("/auth/login?next=/dashboard/staff", base_url="https://niko.sryze.cc"))

    assert shared == "https://niko.sryze.cc/auth/callback"
    assert apex == "https://niko.sryze.cc/auth/callback"


def test_the_callback_stays_with_the_request_host_without_the_switch(monkeypatch):
    monkeypatch.setattr(config, "SUBDOMAIN_ROUTING", False)
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    monkeypatch.setattr(config, "DISCORD_CLIENT_SECRET", "test-secret")
    monkeypatch.delenv("DISCORD_REDIRECT_URI", raising=False)
    monkeypatch.delenv("REPLIT_DEV_DOMAIN", raising=False)

    response = app.test_client().get("/auth/login", base_url="https://dash.niko.sryze.cc")

    # Nothing is routed, so the callback a host asks for is its own — which is
    # what a deployment without sections has always registered.
    assert _redirect_uri_param(response) == "https://dash.niko.sryze.cc/auth/callback"


def test_a_configured_callback_wins_over_everything(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    monkeypatch.setenv("DISCORD_REDIRECT_URI", "https://niko.sryze.cc/auth/callback")
    monkeypatch.setattr(config, "DISCORD_CLIENT_SECRET", "test-secret")

    response = app.test_client().get("/auth/login", base_url="https://dash.niko.sryze.cc")

    # A deployment that registered its own address keeps it, sections or not.
    assert _redirect_uri_param(response) == "https://niko.sryze.cc/auth/callback"


@pytest.mark.parametrize("host, path, expected", [
    ("dash.niko.sryze.cc", "/staff", "/dashboard/staff"),
    ("dash.niko.sryze.cc", "/", "/dashboard"),
    ("dash.niko.sryze.cc", "/dashboard/staff", "/dashboard/staff"),
    ("dash.niko.sryze.cc", "/staff?tab=email", "/dashboard/staff?tab=email"),
    ("dash.niko.sryze.cc", "/dashboardx", "/dashboard/dashboardx"),
    ("niko.sryze.cc", "/dashboard/staff", "/dashboard/staff"),
    ("niko.sryze.cc", "/", "/"),
])
def test_a_short_path_is_remembered_in_its_apex_form(subdomains, host, path, expected):
    assert config.apex_path(host, path) == expected


def test_a_finished_sign_in_returns_to_the_section_host(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    from webapp.routes import auth_routes

    with app.test_request_context("/auth/callback"):
        flask_session["oauth_return"] = "/dashboard"

        assert auth_routes._oauth_destination("/dashboard/staff") == "https://dash.niko.sryze.cc/staff"


def test_an_apex_sign_in_stays_on_the_apex(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    from webapp.routes import auth_routes

    with app.test_request_context("/auth/callback"):
        flask_session["oauth_return"] = ""

        assert auth_routes._oauth_destination("/dashboard/staff") == "/dashboard/staff"


def test_the_helpers_are_inert_without_the_switch(monkeypatch):
    monkeypatch.setattr(config, "SUBDOMAIN_ROUTING", False)
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")

    response = app.test_client().get("/dashboard/staff", base_url="https://dash.niko.sryze.cc")

    # With the feature off a ``dash.`` host is just another host for the site.
    assert response.status_code == 200
    assert '"prefix"' not in response.get_data(as_text=True)
