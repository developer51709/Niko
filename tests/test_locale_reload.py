"""The locale feed across a zero-downtime update.

An update replaces files under a running process and rebuilds the Flask app from
them. The feed module is deliberately not re-imported with the rest — it owns the
manifest and catalogue caches the rebuilt routes read — so it has to be reloaded
*in place*, or a rebuilt route calls a function the running module does not have.
That is not hypothetical: a new ``coverage_rows`` argument once answered
``/api/owner/locales`` with a 500 for exactly that reason.
"""

import webapp.locale_feed as feed
from webapp import updates
from webapp.routes import owner_routes


def test_reload_keeps_the_module_and_its_caches():
    beta, local, bot, loop = feed._beta, feed._local, feed._bot, feed._loop

    assert updates.reload_locale_feed() is True

    # Same module object: every route holding ``from .. import locale_feed``
    # reads the reloaded functions without being re-imported itself.
    assert feed is __import__("webapp.locale_feed", fromlist=["locale_feed"])
    assert callable(feed.coverage_rows)
    # Same caches: the site keeps serving beta's manifest and the bot its overlay
    # instead of falling back to the build for the first request after an update.
    assert feed._beta is beta
    assert feed._local is local
    assert feed._bot is bot
    assert feed._loop is loop


def test_reload_without_a_loaded_feed_is_harmless(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "webapp.locale_feed", None)
    assert updates.reload_locale_feed() is False


def test_payload_survives_a_feed_older_than_its_route(monkeypatch):
    """A process updated by an older reloader still answers, website-only."""
    seen = {}
    merged = feed.coverage_rows

    def older_signature(document):
        seen["called"] = True
        return merged(document)

    monkeypatch.setattr(feed, "coverage_rows", older_signature)
    monkeypatch.setattr(owner_routes, "_MERGED_COVERAGE", False)
    monkeypatch.setattr(feed, "BETA_INSTANCE_URL", "")

    payload = owner_routes._locale_payload()

    assert seen["called"] is True
    assert payload["coverage"], "the page still gets its per-language rows"
    assert all("bot" not in row for row in payload["coverage"])
    assert payload["pages"], "and the catalogue lists it renders"


def test_payload_counts_the_bot_when_the_feed_can(monkeypatch):
    monkeypatch.setattr(feed, "BETA_INSTANCE_URL", "")
    monkeypatch.setattr(owner_routes, "_MERGED_COVERAGE", True)

    payload = owner_routes._locale_payload()

    rows = payload["coverage"]
    assert rows and all("bot" in row for row in rows)
    assert rows[0]["total"] == payload["total_keys"] + payload["bot_total_keys"]
