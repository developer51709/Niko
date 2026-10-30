"""AI Action cards and the server layout the model receives.

The confirmation card is the only message a request posts: confirming it edits
the card into the result instead of leaving a spent prompt behind with a second
message under it.
"""

import asyncio
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import utils.ai.actions as actions  # noqa: E402
import utils.ai.openai_client as openai_client  # noqa: E402


# ── Fakes ─────────────────────────────────────────────────────────────────────

class SentMessage:
    def __init__(self, view=None):
        self.view = view
        self.edits = []

    async def edit(self, *, view=None, **kwargs):
        # The original view stays inspectable; edits collect what replaced it.
        self.edits.append(view)


class Channel:
    def __init__(self, guild, name, cid, category=None):
        self.guild = guild
        self.name = name
        self.id = cid
        self.category = category
        self.sent = []
        self.mention = f"<#{cid}>"

    def permissions_for(self, member):
        return SimpleNamespace(manage_channels=True, manage_roles=True, send_messages=True)

    async def send(self, content=None, *, view=None, **kwargs):
        message = SentMessage(view)
        self.sent.append(message)
        return message


class Category:
    def __init__(self, name, cid):
        self.name = name
        self.id = cid
        self.channels = []
        self.mention = name


class Role:
    def __init__(self, name, rid, position, colour=0, hoist=False):
        import discord

        self.name = name
        self.id = rid
        self.position = position
        self.colour = discord.Colour(colour)
        self.hoist = hoist
        self.mentionable = False
        self.managed = False
        self.mention = f"<@&{rid}>"
        self.edits = []

    def is_default(self):
        return False

    async def edit(self, **kwargs):
        self.edits.append(kwargs)
        for field, value in kwargs.items():
            if field != "reason":
                setattr(self, field, value)

    def __ge__(self, other):
        return self.position >= other.position

    def __gt__(self, other):
        return self.position > other.position

    def __lt__(self, other):
        return self.position < other.position

    def __le__(self, other):
        return self.position <= other.position


class Member:
    def __init__(self, name, mid, top_role=None):
        self.name = name
        self.display_name = name
        self.id = mid
        self.mention = f"<@{mid}>"
        self.top_role = top_role
        self.guild_permissions = SimpleNamespace(administrator=True)

    def __str__(self):
        return self.name


class Guild:
    def __init__(self):
        self.id = 1
        self.owner_id = 999
        self.created = []
        self.categories = [Category("Information", 10), Category("Community", 11)]
        rules = Channel(self, "rules", 100, self.categories[0])
        memes = Channel(self, "memes-and-gifs", 103, self.categories[1])
        general = Channel(self, "general", 102, self.categories[1])
        self.categories[0].channels = [rules]
        self.categories[1].channels = [general, memes]
        self.channels = [rules, general, memes]
        self.roles = [
            Role("Member", 300, 1),
            Role("Moderator", 301, 5, 0x00AAFF, hoist=True),
        ]
        self.me = Member("Niko", 555, top_role=self.roles[-1])
        self.members = [self.me]

    def get_channel(self, cid):
        return next((c for c in [*self.channels, *self.categories] if c.id == int(cid)), None)

    def get_role(self, rid):
        return next((r for r in self.roles if r.id == int(rid)), None)

    def get_member(self, uid):
        return next((m for m in self.members if m.id == int(uid)), None)

    async def create_text_channel(self, *, name, category=None, topic=None, reason=None):
        created = {"name": name, "category": category, "topic": topic}
        self.created.append(created)
        return Channel(self, name, 900, category)

    async def create_voice_channel(self, *, name, category=None, reason=None):
        self.created.append({"name": name, "category": category})
        return Channel(self, name, 901, category)

    async def create_role(self, **kwargs):
        role = Role(kwargs["name"], 800, 0)
        self.created.append(kwargs)
        self.roles.append(role)
        return role


class Bot:
    def get_cog(self, name):
        return None


@pytest.fixture
def world(monkeypatch):
    guild = Guild()
    member = Member("tester", 42, top_role=guild.roles[-1])
    member.guild = guild
    channel = guild.channels[2]
    msg = SimpleNamespace(guild=guild, channel=channel, author=member)

    async def accepted(self):
        return True

    monkeypatch.setattr(actions.AIActionConfirmView, "wait_for_response", accepted)
    return msg


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_confirming_edits_the_card_into_the_result_instead_of_sending(world):
    asyncio.run(actions.dispatch_ai_action(
        Bot(), world,
        {"action": "create_channel", "name": "screenshots", "category": "Community"},
    ))

    # One message: the card. The outcome replaced it rather than being appended.
    assert len(world.channel.sent) == 1
    card = world.channel.sent[0]
    assert len(card.edits) == 1
    assert "Completed" in card.edits[-1].children[0].children[0].content
    assert world.guild.created[0]["category"] is world.guild.categories[1]


def test_cancelling_leaves_the_card_as_the_only_message(world, monkeypatch):
    async def declined(self):
        return False

    monkeypatch.setattr(actions.AIActionConfirmView, "wait_for_response", declined)
    asyncio.run(actions.dispatch_ai_action(
        Bot(), world, {"action": "create_channel", "name": "screenshots"},
    ))

    assert len(world.channel.sent) == 1
    assert world.channel.sent[0].edits == []
    assert world.guild.created == []


def test_a_failed_action_reports_in_the_card(world, monkeypatch):
    async def explode(**kwargs):
        raise actions.discord.HTTPException(SimpleNamespace(status=500, reason="boom"), "boom")

    monkeypatch.setattr(world.guild, "create_text_channel", explode)
    asyncio.run(actions.dispatch_ai_action(
        Bot(), world, {"action": "create_channel", "name": "screenshots"},
    ))

    assert len(world.channel.sent) == 1
    assert "Refused" in world.channel.sent[0].edits[-1].children[0].children[0].content


def test_an_unknown_category_is_reported_instead_of_being_dropped(world):
    asyncio.run(actions.dispatch_ai_action(
        Bot(), world, {"action": "create_channel", "name": "screenshots", "category": "Nope"},
    ))

    assert world.guild.created == []
    assert "Community" in world.channel.sent[-1].view.children[0].children[2].content


def test_a_shortened_name_finds_the_channel(world):
    assert actions._resolve_channel(world.guild, "memes").name == "memes-and-gifs"
    assert actions._resolve_channel(world.guild, "#Community") is None


def test_a_category_can_be_named_by_one_of_its_channels(world):
    assert actions._resolve_category(world.guild, "general").name == "Community"


def test_the_confirm_card_speaks_the_guild_language(world):
    world.guild.preferred_locale = "fr"
    asyncio.run(actions.dispatch_ai_action(
        Bot(), world,
        {"action": "create_channel", "name": "clips", "category": "Community", "topic": "best of"},
    ))

    card = world.channel.sent[0]
    assert isinstance(card.view, actions.AIActionConfirmView)
    assert card.view._confirm.label == "Confirmer"
    assert card.view._cancel.label == "Annuler"
    body = card.view.children[0].children[2].content
    assert "créer un salon" in body.lower()
    assert "créer" in body.lower()
    assert "best of" in body

    # The completed card is in the same language, not English.
    title = card.edits[-1].children[0].children[0].content
    assert "terminée" in title


def test_a_permission_refusal_speaks_the_guild_language(world):
    world.guild.preferred_locale = "de"
    world.author.guild_permissions = SimpleNamespace(administrator=False, manage_channels=False)
    asyncio.run(actions.dispatch_ai_action(
        Bot(), world, {"action": "create_channel", "name": "clips"},
    ))

    body = world.channel.sent[0].view.children[0].children[2].content
    assert "Berechtigung" in body
    assert "Kanäle verwalten" in body
    assert world.guild.created == []


def test_an_edit_card_lists_the_changes_in_the_guild_language(world):
    world.guild.preferred_locale = "de"
    asyncio.run(actions.dispatch_ai_action(
        Bot(), world,
        {"action": "edit_role", "role": "Member", "colour": "#ff8800", "hoist": True},
    ))

    card = world.channel.sent[0]
    body = card.view.children[0].children[2].content
    assert "Farbe" in body
    assert "Gehisst" in body and "ja" in body
    role = world.guild.get_role(300)
    assert role.colour.value == 0xFF8800
    assert role.hoist is True
    assert "aktualisiert" in card.edits[-1].children[0].children[2].content


def test_every_catalogue_entry_resolves_and_formats_in_every_language():
    languages = ("en", "de", "es", "fr")
    english = actions.MESSAGES["en"]
    for lang in languages:
        ctx = SimpleNamespace(guild=SimpleNamespace(preferred_locale=lang))
        assert set(actions.MESSAGES[lang]) == set(english), f"{lang} is missing keys"
        for key, text in english.items():
            assert actions.MESSAGES[lang][key].strip(), f"{lang}: {key} is empty"
            kwargs = {name: "X" for name in re.findall(r"{(\w+)}", text)}
            rendered = actions.t(ctx, key, **kwargs)
            assert "{" not in rendered and "}" not in rendered, (
                f"{lang}: {key} left a placeholder behind: {rendered!r}"
            )


def test_the_layout_lists_categories_channels_and_roles(world):
    layout = openai_client._server_layout(world.guild)

    assert "Category 'Community' (11): general (text, 102), memes-and-gifs (text, 103)" in layout
    assert "Roles (highest to lowest): Moderator (id 301, #00aaff, hoisted) | Member (id 300)" in layout
    assert "Niko's highest role is 'Moderator'" in layout


def test_the_layout_is_only_added_for_action_requests(world):
    assert openai_client._server_layout(None) == ""
    assert openai_client._message_requests_action("create a channel called memes")
    assert not openai_client._message_requests_action("how are you today")
