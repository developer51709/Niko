"""The staff applications page's Components V2 link embed.

The applications page needs a signed-in member to list its openings, so the
preview cannot reuse that API: Discord reads the tags from a crawler with no
session. What the preview shows instead is the public part — which roles are
open — with every role linked to its own form, so a reader can pick one without
opening the page first.

Shapes that must not regress: one entry per open role, a real link for each, a
list kept out of the introduction paragraph, and a payload inside Discord's
3,000-byte budget (an over-limit payload is dropped entirely, losing the links).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import database, social, social_preview  # noqa: E402

OPENINGS = [
    {
        "id": "team-moderator",
        "title": "Moderator",
        "description": "Help keep Niko's support community welcoming, safe, and fair.",
    },
    {
        "id": "team-support",
        "title": "Support Team",
        "description": "Help members troubleshoot Niko and find the right answers.",
    },
]

PAGE = {
    "title": "Join the Niko Team — Staff Applications",
    "description": "Explore open staff roles and apply to help build a safer, friendlier Niko community.",
    "image": "https://niko.sryze.cc/og/team/apply.png",
}

INVITE = (
    "https://discord.com/oauth2/authorize"
    "?client_id=1520558530472448170&permissions=8&scope=bot+applications.commands"
)


def payload(context: dict, description: str = None) -> dict:
    rendered = social_preview.component_embed_payload(
        PAGE, INVITE, None,
        context["description"] if description is None else description,
        context,
    )
    return rendered["component"]


def texts(container: dict) -> list[str]:
    """Every text display, including the section's own, in reading order."""
    found = []
    for component in container["components"]:
        if component.get("type") == social_preview.SECTION:
            found.extend(
                child["content"]
                for child in component.get("components", [])
                if child.get("type") == social_preview.TEXT_DISPLAY
            )
        elif component.get("type") == social_preview.TEXT_DISPLAY:
            found.append(component["content"])
    return found


def test_open_roles_become_links_inside_the_preview(monkeypatch):
    monkeypatch.setattr(database, "get_open_team_openings", lambda limit=6: OPENINGS)
    context = social._team_apply_embed_context()
    container = payload(context)

    assert container["type"] == social_preview.CONTAINER
    listing = [text for text in texts(container) if "team/apply/" in text]
    assert len(listing) == 1, "the roles belong in one list, not one block each"
    assert "[Moderator](https://niko.sryze.cc/team/apply/team-moderator)" in listing[0]
    assert "[Support Team](https://niko.sryze.cc/team/apply/team-support)" in listing[0]
    # Each role's one-line description travels with its link.
    assert "welcoming, safe, and fair" in listing[0]


def test_the_list_is_kept_out_of_the_introduction(monkeypatch):
    monkeypatch.setattr(database, "get_open_team_openings", lambda limit=6: OPENINGS)
    container = payload(social._team_apply_embed_context())

    intro = container["components"][0]
    assert intro["type"] == social_preview.SECTION
    assert "STAFF APPLICATIONS" in texts(container)[0]
    assert "team/apply/" not in texts(container)[0]
    # The intro names the count, the list names the roles.
    assert "2 open roles" in texts(container)[0]


def test_a_role_without_openings_still_previews_without_links(monkeypatch):
    monkeypatch.setattr(database, "get_open_team_openings", lambda limit=6: [])
    context = social._team_apply_embed_context()
    container = payload(context)

    assert all("team/apply/" not in text for text in texts(container))
    assert "No staff roles are open right now" in texts(container)[0]


def test_an_unreadable_openings_table_does_not_break_the_page(monkeypatch):
    monkeypatch.setattr(database, "get_open_team_openings", lambda limit=6: None)
    container = payload(social._team_apply_embed_context())
    assert "No staff roles are open right now" in texts(container)[0]


def test_the_button_row_still_closes_the_embed(monkeypatch):
    monkeypatch.setattr(database, "get_open_team_openings", lambda limit=6: OPENINGS)
    container = payload(social._team_apply_embed_context())

    row = container["components"][-1]
    assert row["type"] == social_preview.ACTION_ROW
    labels = [button["label"] for button in row["components"]]
    assert labels == ["Add Niko", "Commands", "Support server"]


def test_the_payload_fits_discords_budget_with_many_roles(monkeypatch):
    monkeypatch.setattr(database, "get_open_team_openings", lambda limit=6: [
        {
            "id": f"team-role{i}",
            "title": f"Long Role Name Number {i}",
            "description": "A deliberately wordy description " * 3,
        }
        for i in range(10)
    ])
    context = social._team_apply_embed_context()
    payload_json = json.dumps(
        social_preview.component_embed_payload(PAGE, INVITE, None, context["description"], context),
        separators=(",", ":"),
    )
    assert len(payload_json.encode("utf-8")) <= social_preview.EMBED_BYTE_LIMIT
    # The cap keeps the preview readable rather than listing every role.
    assert len(context["list"]) == social._APPLICATION_LIST_LIMIT


def test_the_applications_route_is_not_treated_as_a_team_profile(monkeypatch):
    monkeypatch.setattr(database, "get_open_team_openings", lambda limit=6: OPENINGS)
    monkeypatch.setattr(social, "_social_context_cache", {})
    context = social._social_context("/team/apply")
    assert context["kind"] == "applications"
    # A profile URL keeps going to the roster, not to the applications list.
    profile = social._social_context("/team/12345")
    assert (profile or {}).get("kind") != "applications"
