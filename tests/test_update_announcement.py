"""Regression checks for the release announcement behind ``.staff announce``.

The announcement is the main way a release is promoted to communities, so its
docs and changelog buttons have to point at pages that actually shipped with
the update.
"""

import asyncio
import sys
from pathlib import Path

import discord
from discord.ext import commands

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.staff.owner import OwnerCog  # noqa: E402
from cogs.staff.staff import StaffCog  # noqa: E402
from config import links  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class FakeMessage:
    def __init__(self):
        self.deleted = False

    async def delete(self):
        self.deleted = True


class FakeContext:
    """Just enough context for the owner-only announcement command."""

    def __init__(self):
        self.message = FakeMessage()
        self.sent = []

    async def send(self, content=None, *, view=None, **kwargs):
        self.sent.append(view if view is not None else content)


class FakeBot:
    def add_dynamic_items(self, *items):
        pass

    def remove_dynamic_items(self, *items):
        pass


def run_announce(topic=""):
    """Run the real command callback and return the context it posted into."""
    cog = OwnerCog(FakeBot())
    ctx = FakeContext()
    asyncio.run(OwnerCog.announce.callback(cog, ctx, topic))
    return ctx


def walk(component):
    """Every component below ``component``, including itself."""
    found = [component]
    for child in getattr(component, "children", None) or []:
        found.extend(walk(child))
    return found


def view_text(view) -> str:
    return "\n".join(
        part.content for part in walk(view) if isinstance(getattr(part, "content", None), str)
    )


def view_urls(view) -> list[str]:
    return [str(part.url) for part in walk(view) if getattr(part, "url", None)]


def view_labels(view) -> list[str]:
    return [str(part.label) for part in walk(view) if getattr(part, "label", None)]


def test_update_announcement_carries_the_docs_and_changelog_links():
    ctx = run_announce()
    view = ctx.sent[0]

    assert ctx.message.deleted, "an announcement should replace the invoking message"
    assert OwnerCog.UPDATE_DOCS_URL in view_urls(view)
    assert OwnerCog.UPDATE_CHANGELOG_URL in view_urls(view)
    assert view_labels(view) == ["Read the docs", "What's new", "Support Server"]

    text = view_text(view)
    assert "Twitch" in text
    assert "Notifications tab" in text
    assert ".notifier" in text


def test_announcement_links_point_at_pages_that_exist():
    """A renamed docs page or changelog slug must fail here, not in Discord."""
    docs_slug = OwnerCog.UPDATE_DOCS_URL.removeprefix(f"{links.DOCS}/")
    changelog_slug = OwnerCog.UPDATE_CHANGELOG_URL.removeprefix(f"{links.WEBSITE}/changelog/")

    assert OwnerCog.UPDATE_DOCS_URL == f"{links.WEBSITE}/docs/{docs_slug}"
    assert OwnerCog.UPDATE_CHANGELOG_URL == f"{links.WEBSITE}/changelog/{changelog_slug}"
    assert (ROOT / "web/src/content/docs" / f"{docs_slug}.mdx").exists()

    changelog = (ROOT / "web/src/data/changelog.ts").read_text(encoding="utf-8")
    assert f'slug: "{changelog_slug}"' in changelog, changelog_slug


def test_changelog_entry_covers_the_twitch_notifier_update():
    """Twitch ships with this release, so its changelog entry has to say so."""
    changelog = (ROOT / "web/src/data/changelog.ts").read_text(encoding="utf-8")
    entry = changelog.split('slug: "notifier-dashboard-tab"', 1)[1].split("\n  },", 1)[0]

    assert "Twitch" in entry
    assert "TWITCH_CLIENT_ID" in entry
    assert "live" in entry


def test_staff_announce_posts_the_update_with_both_links():
    """``.staff announce`` is the path staff actually use, so cover it too."""
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
    asyncio.run(bot.add_cog(StaffCog(bot)))
    command = next(item for item in bot.get_command("staff").commands if item.name == "announce")
    ctx = FakeContext()
    asyncio.run(command.callback(ctx, ""))

    urls = view_urls(ctx.sent[0])
    assert OwnerCog.UPDATE_DOCS_URL in urls
    assert OwnerCog.UPDATE_CHANGELOG_URL in urls


def test_announce_role_policy_is_the_head_admin_allow_listed_name():
    """``.staff announce`` is granted by name, so the command must keep it."""
    staff = (ROOT / "src/cogs/staff/staff.py").read_text(encoding="utf-8")
    head_admin = staff.split("HEAD_ADMIN_COMMANDS = {", 1)[1].split("}", 1)[0]

    assert '"announce"' in head_admin
    assert OwnerCog.announce.name == "announce"


def test_announce_can_still_post_the_community_policy():
    ctx = run_announce("policy")
    view = ctx.sent[0]

    assert "Community Policy" in view_text(view)
    assert "Read the Community Policy" in view_labels(view)
    assert OwnerCog.UPDATE_DOCS_URL not in view_urls(view)


def test_unknown_announce_topic_explains_itself():
    ctx = run_announce("nonsense")

    assert ctx.message.deleted is False
    assert "`.staff announce policy`" in str(ctx.sent[0])
