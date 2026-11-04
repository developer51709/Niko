"""Section subdomains: ``dash.example.com/staff`` is ``/dashboard/staff``."""

import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

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

    cookies = response.headers.getlist("Set-Cookie")
    # A session cookie set while the visitor is on the subdomain must belong to
    # the domain, or signing in there would not be seen on the apex. Werkzeug
    # writes it without the leading dot that ``.domain`` implies.
    written = [header for header in cookies if header.startswith(f"{app.config['SESSION_COOKIE_NAME']}=")]
    assert written
    assert all("Domain=niko.sryze.cc" in header for header in written)


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


def test_a_sign_in_on_another_site_continues_where_the_callback_lands(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    monkeypatch.setenv("DISCORD_REDIRECT_URI", "https://niko.sryze.cc/auth/callback")
    monkeypatch.setattr(config, "DISCORD_CLIENT_SECRET", "test-secret")

    # A preview host and the site are different sites: the state cookie set on
    # one never reaches the other. The sign-in is handed to the address that
    # receives the callback instead of dying on the state check.
    response = app.test_client().get("/auth/login?next=/dashboard", base_url="https://preview.e2b.app")

    assert response.status_code == 302
    assert response.headers["Location"] == "https://niko.sryze.cc/auth/login?next=%2Fdashboard"


def test_a_callback_on_another_address_is_not_followed(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    monkeypatch.setenv("DISCORD_REDIRECT_URI", "https://staging.example.test/auth/callback")
    monkeypatch.setattr(config, "DISCORD_CLIENT_SECRET", "test-secret")

    # A callback that is not the site cannot be followed: sending the visitor
    # there would leave this site for one that may not even exist. The attempt
    # goes ahead and the callback reports both addresses when it fails.
    response = app.test_client().get("/auth/login", base_url="https://niko.sryze.cc")

    assert _redirect_uri_param(response) == "https://staging.example.test/auth/callback"


def test_a_section_host_signs_in_without_leaving_the_site(subdomains, monkeypatch):
    monkeypatch.setenv("DISCORD_REDIRECT_URI", "https://niko.sryze.cc/auth/callback")
    monkeypatch.setattr(config, "DISCORD_CLIENT_SECRET", "test-secret")

    # `dash.` and the apex share the site's cookies, so there is nothing to hop
    # over: the button goes straight to Discord.
    response = app.test_client().get("/auth/login?next=/staff", base_url="https://dash.niko.sryze.cc")

    assert _redirect_uri_param(response) == "https://niko.sryze.cc/auth/callback"


def _state_param(response) -> str:
    return parse_qs(urlparse(response.headers["Location"]).query).get("state", [""])[0]


def _start_sign_in(monkeypatch, path: str = "/dashboard/staff", host: str = "dash.niko.sryze.cc") -> str:
    """Run ``/auth/login`` the way a section host does and return its state."""
    from types import SimpleNamespace
    from webapp.routes import auth_routes

    monkeypatch.setenv("DISCORD_REDIRECT_URI", "https://niko.sryze.cc/auth/callback")
    monkeypatch.setattr(config, "DISCORD_CLIENT_SECRET", "test-secret")
    # The callback would otherwise call Discord; an unusable code is enough to
    # prove the state was accepted, because the session check comes first.
    monkeypatch.setattr(auth_routes, "discord_request", lambda *a, **k: SimpleNamespace(ok=False))

    response = app.test_client().get(f"/auth/login?next={path}", base_url=f"https://{host}")
    return _state_param(response)


def test_a_callback_without_a_state_says_so(subdomains):
    response = app.test_client().get("/auth/callback?code=x", base_url="https://niko.sryze.cc")

    location = response.headers["Location"]
    # A callback opened directly is a different failure from a stale link, and
    # saying which one it was is what makes it diagnosable.
    assert "error=no_state" in location
    assert "to=niko.sryze.cc" in location


def test_a_tampered_state_is_reported_as_a_stale_link(subdomains):
    response = app.test_client().get("/auth/callback?state=abc.def&code=x", base_url="https://niko.sryze.cc")

    location = response.headers["Location"]
    assert "error=invalid_state" in location
    assert "to=niko.sryze.cc" in location


def test_an_expired_state_is_rejected(subdomains, monkeypatch):
    from webapp.routes import auth_routes

    state = _start_sign_in(monkeypatch)
    monkeypatch.setattr(auth_routes, "_OAUTH_STATE_MAX_AGE", -1)

    response = app.test_client().get(f"/auth/callback?state={state}&code=x", base_url="https://niko.sryze.cc")

    assert "error=invalid_state" in response.headers["Location"]


def test_the_state_alone_verifies_the_sign_in(subdomains, monkeypatch):
    state = _start_sign_in(monkeypatch)

    # A client that has never seen this site: no cookies at all. The signature in
    # the state is the whole check, so the sign-in still gets past it.
    response = app.test_client().get(f"/auth/callback?state={state}&code=x", base_url="https://niko.sryze.cc")

    location = response.headers["Location"]
    assert "error=no_state" not in location
    assert "error=invalid_state" not in location
    assert "error=token_exchange_failed" in location


def test_a_stale_duplicate_session_cookie_does_not_block_the_sign_in(subdomains, monkeypatch):
    state = _start_sign_in(monkeypatch)

    # Production sent two ``session`` cookies — an old host-only copy and the new
    # domain one — and the server read the first, so every callback looked like
    # an expired link. Nothing reads that cookie any more; this is the guard.
    response = app.test_client().get(
        f"/auth/callback?state={state}&code=x",
        base_url="https://niko.sryze.cc",
        headers={"Cookie": "session=stale-host-only; session=stale-domain"},
    )

    assert "error=token_exchange_failed" in response.headers["Location"]
    # ...and the dead cookie is cleaned up on the way out.
    cleared = [header for header in response.headers.getlist("Set-Cookie") if header.startswith("session=")]
    assert cleared


def test_a_sign_in_that_completes_lands_on_the_section_host(subdomains, monkeypatch):
    from types import SimpleNamespace
    from webapp.routes import auth_routes

    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    monkeypatch.setenv("DISCORD_REDIRECT_URI", "https://niko.sryze.cc/auth/callback")
    monkeypatch.setattr(config, "DISCORD_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(
        auth_routes,
        "discord_request",
        lambda *a, **k: SimpleNamespace(
            ok=True,
            json=lambda: {"access_token": "token", "refresh_token": "refresh", "expires_in": 3600, "scope": "identify"},
        ),
    )
    monkeypatch.setattr(auth_routes, "discord_get", lambda path, token: {"id": "42", "username": "tester"})

    client = app.test_client()
    state = _state_param(client.get("/auth/login?next=/dashboard/staff", base_url="https://dash.niko.sryze.cc"))
    done = client.get(f"/auth/callback?state={state}&code=abc", base_url="https://niko.sryze.cc")

    # The whole round trip, exactly as production runs it: sign in on ``dash.``,
    # come back to the callback, and land signed in on the section host.
    assert done.headers["Location"] == "https://dash.niko.sryze.cc/staff"


def test_a_finished_sign_in_returns_to_the_section_host(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    from webapp.routes import auth_routes

    state = auth_routes._encode_oauth_state("/dashboard/staff", "/dashboard", "dash.niko.sryze.cc")
    sign_in = auth_routes._decode_oauth_state(state)

    assert auth_routes._oauth_destination(sign_in["r"], sign_in["n"]) == "https://dash.niko.sryze.cc/staff"


def test_an_apex_sign_in_stays_on_the_apex(subdomains, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    from webapp.routes import auth_routes

    state = auth_routes._encode_oauth_state("/dashboard/staff", "", "niko.sryze.cc")
    sign_in = auth_routes._decode_oauth_state(state)

    assert auth_routes._oauth_destination(sign_in["r"], sign_in["n"]) == "/dashboard/staff"


def test_the_helpers_are_inert_without_the_switch(monkeypatch):
    monkeypatch.setattr(config, "SUBDOMAIN_ROUTING", False)
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")

    response = app.test_client().get("/dashboard/staff", base_url="https://dash.niko.sryze.cc")

    # With the feature off a ``dash.`` host is just another host for the site.
    assert response.status_code == 200
    assert '"prefix"' not in response.get_data(as_text=True)
