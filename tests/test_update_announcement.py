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

from cogs.staff.commands.administration import AdministrationCommands  # noqa: E402
from cogs.staff.permissions import HEAD_ADMIN_COMMANDS  # noqa: E402
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
    cog = AdministrationCommands()
    ctx = FakeContext()
    asyncio.run(AdministrationCommands.announce.callback(cog, ctx, topic))
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


def test_update_announcement_carries_the_changelog_and_site_links():
    ctx = run_announce()
    view = ctx.sent[0]

    assert ctx.message.deleted, "an announcement should replace the invoking message"
    urls = view_urls(view)
    assert AdministrationCommands.UPDATE_CHANGELOG_URL in urls
    assert AdministrationCommands.UPDATE_COMMANDS_URL in urls
    assert AdministrationCommands.UPDATE_SUPPORT_URL in urls
    # The update announcement carries exactly the three links it is announced
    # with: the changelog entry, the command list, and the support server.
    assert view_labels(view) == ["What's new", "All commands", "Support server"]

    text = view_text(view)
    assert "`.fm`" in text
    assert "`/fm overview`" in text
    assert "`/fm link`" in text
    assert "`/fm whoknows`" in text
    assert "`/fm recent`" in text
    assert "`/fm taste`" in text
    # Linking stores a session key, never a password.
    assert "session key" in text
    assert "approval page" in text
    # The feature stays free, and the announcement says so up front.
    assert "the bot stays free" in text


def test_changelog_entry_covers_the_current_update():
    """The announced entry must describe the features the announcement names."""
    changelog = (ROOT / "web/src/data/changelog.ts").read_text(encoding="utf-8")
    entry = changelog.split('slug: "lastfm-listening-stats"', 1)[1].split("\n  },", 1)[0]
    lowered = entry.lower()

    assert "`.fm`" in entry
    assert "last.fm" in lowered
    assert "whoknows" in lowered
    assert "crowns" in lowered
    assert "taste" in lowered
    assert "album art" in lowered
    assert "session key" in lowered
    # The approval flow is the reason the website gained a callback.
    assert "/api/lastfm/callback" in entry
    # The loading cards are part of the release, not an internal detail.
    assert "loading card" in lowered


def test_changelog_entry_is_the_newest_release():
    """The announcement announces the latest entry, so it must sit first."""
    changelog = (ROOT / "web/src/data/changelog.ts").read_text(encoding="utf-8")
    body = changelog.split("CHANGELOG: ChangelogEntry[] = [", 1)[1]
    assert body.lstrip().startswith("{")
    first_slug = body.split('slug: "', 1)[1].split('"', 1)[0]
    announced = AdministrationCommands.UPDATE_CHANGELOG_URL.rsplit("/", 1)[-1]

    assert first_slug == announced


def test_changelog_entry_covers_the_legal_update():
    """The announced entry must describe the legal changes in the same release."""
    changelog = (ROOT / "web/src/data/changelog.ts").read_text(encoding="utf-8")
    entry = changelog.split('slug: "premium-subscriptions"', 1)[1].split("\n  },", 1)[0]
    lowered = entry.lower()

    assert "legal update" in lowered
    assert "data-removal" in entry
    assert "moderation and safety records are preserved" in lowered
    assert "court-ordered" in lowered


def test_announcement_links_point_at_pages_that_exist():
    """A renamed route or changelog slug must fail here, not in Discord."""
    assert AdministrationCommands.UPDATE_COMMANDS_URL == f"{links.WEBSITE}/commands"
    assert AdministrationCommands.UPDATE_SUPPORT_URL == links.SUPPORT_SERVER

    router = (ROOT / "web/src/router.ts").read_text(encoding="utf-8")
    assert 'path === "/commands"' in router

    changelog_slug = AdministrationCommands.UPDATE_CHANGELOG_URL.removeprefix(f"{links.WEBSITE}/changelog/")
    assert AdministrationCommands.UPDATE_CHANGELOG_URL == f"{links.WEBSITE}/changelog/{changelog_slug}"

    changelog = (ROOT / "web/src/data/changelog.ts").read_text(encoding="utf-8")
    assert f'slug: "{changelog_slug}"' in changelog, changelog_slug


def test_changelog_entry_covers_the_giveaway_ban_update():
    """The announced entry has to describe the commands the announcement names."""
    changelog = (ROOT / "web/src/data/changelog.ts").read_text(encoding="utf-8")
    entry = changelog.split('slug: "giveaway-bans"', 1)[1].split("\n  },", 1)[0]

    assert ".giveaway ban" in entry
    assert "unban" in entry
    assert "entries" in entry


def test_the_small_lottery_card_entry_is_not_published():
    """The lottery card was a small economy tweak, not a release of its own."""
    changelog = (ROOT / "web/src/data/changelog.ts").read_text(encoding="utf-8")

    assert 'slug: "lottery-card-and-channel"' not in changelog


def test_staff_announce_posts_the_update_with_every_link():
    """``.staff announce`` is the path staff actually use, so cover it too."""
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
    asyncio.run(bot.add_cog(StaffCog(bot)))
    command = next(item for item in bot.get_command("staff").commands if item.name == "announce")
    ctx = FakeContext()
    asyncio.run(command.callback(AdministrationCommands(), ctx, ""))

    urls = view_urls(ctx.sent[0])
    assert AdministrationCommands.UPDATE_CHANGELOG_URL in urls
    assert AdministrationCommands.UPDATE_COMMANDS_URL in urls
    assert AdministrationCommands.UPDATE_SUPPORT_URL in urls


def test_announce_role_policy_is_the_head_admin_allow_listed_name():
    """``.staff announce`` is granted by name, so the command must keep it."""
    assert "announce" in HEAD_ADMIN_COMMANDS
    assert AdministrationCommands.announce.name == "announce"


def test_announce_can_still_post_the_community_policy():
    ctx = run_announce("policy")
    view = ctx.sent[0]

    assert "Community Policy" in view_text(view)
    assert "Read the Community Policy" in view_labels(view)
    assert AdministrationCommands.UPDATE_CHANGELOG_URL not in view_urls(view)


def test_unknown_announce_topic_explains_itself():
    ctx = run_announce("nonsense")

    assert ctx.message.deleted is False
    assert "`.staff announce policy`" in str(ctx.sent[0])
