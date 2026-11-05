"""The DM the inviter gets the moment Niko joins a server.

It is the only message every new owner is guaranteed to see, so it has to name
the wizard, say what leveling does by default, and link the dashboard and docs —
all inside Discord's 4,000-character Components V2 budget.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import discord  # noqa: E402

from cogs.leveling import migration  # noqa: E402


class _Guild:
    id = 424242
    name = "Cozy Corner"
    preferred_locale = "en"


def _view(provider: str | None = None):
    bot = SimpleNamespace(user=SimpleNamespace(
        display_avatar=SimpleNamespace(url="https://cdn.example.test/a.png")))
    return migration.LevelMigration(bot)._welcome_view(_Guild(), provider)


def _texts(item) -> list[str]:
    out = []
    for child in getattr(item, "children", []) or []:
        if isinstance(child, str):
            continue
        content = getattr(child, "content", None)
        if isinstance(content, str):
            out.append(content)
        out.extend(_texts(child))
    return out


def _buttons(item):
    out = []
    for child in getattr(item, "children", []) or []:
        if isinstance(child, discord.ui.Button):
            out.append(child)
        out.extend(_buttons(child))
    return out


def test_the_dm_names_the_setup_wizard_and_links_the_dashboard():
    view = _view()
    body = "\n".join(_texts(view))

    assert "Cozy Corner" in body
    assert "/setup" in body
    urls = {button.url for button in _buttons(view) if button.style is discord.ButtonStyle.link}
    assert f"{migration.WEBSITE}/dashboard/424242/leveling" in urls
    assert migration.DOCS in urls


def test_the_dm_says_leveling_starts_off():
    body = "\n".join(_texts(_view()))
    lowered = body.lower()

    assert "leveling" in lowered
    assert "off" in lowered


def test_the_dm_is_informative_but_inside_the_budget():
    body = "\n".join(_texts(_view()))

    assert len(body) > 600, "the join DM is too short to help anyone"
    assert len(body) < 4000, "Components V2 rejects text over 4,000 characters"


def test_an_import_offer_adds_its_own_buttons_without_losing_the_links():
    view = _view("lurkr")
    labels = {button.label for button in _buttons(view)}
    body = "\n".join(_texts(view))

    assert "Lurkr" in body
    assert len(labels) >= 4, "the import buttons pushed out the dashboard links"
    assert len("\n".join(_texts(view))) < 4000
