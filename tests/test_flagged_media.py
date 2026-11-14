"""Content-flagged images in the deleted-message log.

Discord's content scanning marks an attachment as explicit, gore, or self-harm
after the message is sent. Reposting that media in a log would put it back in a
channel, so the entry shows the site's placeholder artwork and a subtext line
linking to the page that explains the flag.
"""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import discord
import pytest
from PIL import Image
from discord.message import _component_factory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.logging import cog as logging_cog  # noqa: E402
from cogs.logging import formatters  # noqa: E402
from utils.safety import flagged_media  # noqa: E402

PLACEHOLDER_DIRS = (
    ROOT / "web" / "public" / "assets" / "placeholders",
    ROOT / "src" / "website" / "dist" / "assets" / "placeholders",
)


# ── Fakes ────────────────────────────────────────

def _attachment(filename="image.png", content_type="image/png", flags=0):
    """An attachment-shaped object; *flags* is the raw content-scanning bitfield."""
    value = getattr(flags, "value", flags)
    return SimpleNamespace(
        filename=filename,
        content_type=content_type,
        proxy_url=f"https://cdn.example/{filename}",
        flags=SimpleNamespace(value=value),
    )


def _message(attachments):
    author = SimpleNamespace(
        id=42, bot=False, mention="<@42>", __str__=lambda _self: "tester#0001",
    )
    return SimpleNamespace(
        guild=SimpleNamespace(id=1),
        author=author,
        channel=SimpleNamespace(mention="#general"),
        content="look at this",
        attachments=list(attachments),
    )


def _cog():
    cog = logging_cog.ServerLogger(SimpleNamespace(user=SimpleNamespace(id=999)))
    cog.log_event = mock.AsyncMock()
    return cog


def _entry(cog):
    call = cog.log_event.await_args
    data = dict(call.kwargs)
    data["title"] = call.args[2]
    data["body"] = call.args[3]
    return SimpleNamespace(**data)


def _texts(view):
    return [
        item.content for item in view.walk_children()
        if isinstance(item, discord.ui.TextDisplay)
    ]


# ── Flag detection ───────────────────────────────

@pytest.mark.parametrize(("bits", "expected"), [
    (0, None),
    # IS_SPOILER is not a content flag: a spoiler still belongs in the log.
    (1 << 3, None),
    (1 << 4, flagged_media.EXPLICIT),
    (1 << 6, flagged_media.GORE),
    (1 << 7, flagged_media.SELF_HARM),
])
def test_each_documented_flag_bit_names_its_type(bits, expected):
    assert flagged_media.flag_type(_attachment(flags=bits)) == expected


def test_several_flags_on_one_image_resolve_to_the_first_documented_one():
    both = (1 << 4) | (1 << 6)
    assert flagged_media.flag_type(_attachment(flags=both)) == flagged_media.EXPLICIT


def test_a_library_that_does_not_know_the_flag_still_reports_it():
    # discord.py 2.7 has no member for the content flags, so a named-enum read
    # would silently drop the bit. The raw value is what counts.
    unknown = SimpleNamespace(value=1 << 7)
    assert flagged_media.flag_type(_attachment(flags=unknown)) == flagged_media.SELF_HARM


def test_an_attachment_without_flags_reads_as_unflagged():
    plain = SimpleNamespace(filename="a.png", content_type="image/png", proxy_url="https://cdn.example/a.png")
    assert flagged_media.flag_type(plain) is None
    assert flagged_media.flag_type(None) is None


# ── Where the placeholder lives ──────────────────

def test_the_log_points_at_the_served_placeholder_and_explainer():
    assert flagged_media.placeholder_url("gore") == "https://niko.sryze.cc/assets/placeholders/gore.png"
    assert flagged_media.learn_more_url("self-harm") == "https://niko.sryze.cc/help/flagged-media?type=self-harm"


def test_the_explainer_page_lists_the_same_flag_slugs():
    # The bot writes ?type=<slug>; the page decides what to say from that exact
    # string, so a renamed flag would land on the generic answer.
    page = (ROOT / "web" / "src" / "pages" / "FlaggedMediaPage.tsx").read_text(encoding="utf-8")
    for flag in flagged_media.FLAG_TYPES:
        assert f'"{flag}"' in page
    router = (ROOT / "web" / "src" / "router.ts").read_text(encoding="utf-8")
    assert 'if (path === "/help/flagged-media") return "flagged-media";' in router


@pytest.mark.parametrize("flag", flagged_media.FLAG_TYPES)
def test_the_prebuild_script_rendered_every_placeholder(flag):
    for folder in PLACEHOLDER_DIRS:
        path = folder / f"{flag}.png"
        assert path.is_file(), f"{path} is missing — run scripts/generate_placeholder_images.py"
        with Image.open(path) as image:
            assert image.format == "PNG"
            assert image.size == (1200, 900)


# ── The deleted-message entry ────────────────────

def test_a_flagged_image_is_replaced_by_the_placeholder():
    cog = _cog()
    message = _message([
        _attachment("clean.png"),
        _attachment("flagged.png", flags=1 << 6),
    ])

    asyncio.run(cog.on_message_delete(message))

    entry = _entry(cog)
    assert entry.title == "Message Deleted"
    assert entry.media_urls == [
        "https://cdn.example/clean.png",
        flagged_media.placeholder_url(flagged_media.GORE),
    ]
    # The placeholder's gallery position is what the note below it points at.
    assert entry.media_flags == {1: flagged_media.GORE}
    # The entry still names the file that was hidden.
    assert "`flagged.png`" in entry.body


def test_a_message_without_flags_carries_no_notes():
    cog = _cog()
    asyncio.run(cog.on_message_delete(_message([_attachment("clean.png")])))

    entry = _entry(cog)
    assert entry.media_urls == ["https://cdn.example/clean.png"]
    assert entry.media_flags is None


class _OfflineSession:
    """An aiohttp session whose CDN fetch fails, so no file bytes are read."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc):
        return False

    def get(self, _url):
        return _FailedResponse()


class _FailedResponse:
    async def __aenter__(self):
        return SimpleNamespace(status=404)

    async def __aexit__(self, *_exc):
        return False


def test_only_inline_images_are_replaced():
    # A flagged file that is not an image is uploaded as a file component, which
    # is outside what the media gallery shows.
    cog = _cog()
    attachment = _attachment("report.pdf", content_type="application/pdf", flags=1 << 4)
    message = _message([attachment])

    with mock.patch("aiohttp.ClientSession", _OfflineSession):
        asyncio.run(cog.on_message_delete(message))

    entry = _entry(cog)
    assert entry.media_urls is None
    assert entry.media_flags is None


# ── What the entry renders ───────────────────────

def _deleted_view(media_urls, media_flags=None, lang="en"):
    return formatters._build_log_view(
        category="messages",
        title="Message Deleted",
        body="**Author:** tester\n**Content:**\nlook at this",
        guild_id=1,
        media_urls=media_urls,
        media_flags=media_flags,
        lang=lang,
    )


def test_the_placeholder_is_captioned_with_a_learn_more_link():
    placeholder = flagged_media.placeholder_url(flagged_media.GORE)
    view = _deleted_view([placeholder], {0: flagged_media.GORE})

    texts = _texts(view)
    note = next(text for text in texts if "flagged-media" in text)
    # Subtext, so it reads as a caption under the gallery rather than a new field.
    assert note.startswith("-# ")
    assert "gore" in note
    assert flagged_media.learn_more_url(flagged_media.GORE) in note

    gallery = next(item for item in view.walk_children() if isinstance(item, discord.ui.MediaGallery))
    assert str(gallery.items[0].media.url) == placeholder


def test_the_note_is_translated_with_the_guilds_language():
    view = _deleted_view([flagged_media.placeholder_url(flagged_media.EXPLICIT)], {0: flagged_media.EXPLICIT}, lang="de")

    note = next(text for text in _texts(view) if "flagged-media" in text)
    assert "automatischen Filter" in note
    assert "?type=explicit" in note


def test_a_placeholder_past_the_gallery_cap_gets_no_note():
    # Discord renders ten gallery items, so an eleventh image has nothing above
    # the note to explain.
    media_urls = [f"https://cdn.example/{index}.png" for index in range(11)]
    view = _deleted_view(media_urls, {10: flagged_media.GORE})

    assert not [text for text in _texts(view) if "flagged-media" in text]


# ── A flag that lands after the entry was posted ─

def _raw_components(media_urls, scan=None):
    """A raw ``components`` payload for an entry whose gallery shows *media_urls*.

    *scan* maps a gallery position to the content-scanning bitfield Discord
    reports in ``content_scan_metadata.flags``.
    """
    scan = scan or {}
    items = []
    for index, url in enumerate(media_urls):
        media = {"url": url}
        if index in scan:
            media["content_scan_metadata"] = {"version": 2, "flags": scan[index]}
        items.append({"media": media, "spoiler": False})
    return [{"type": 17, "components": [{"type": 12, "items": items}]}]


def test_a_late_scan_flag_is_read_from_the_raw_component_payload():
    payload = _raw_components(
        ["https://cdn.example/a.png", "https://cdn.example/b.png"],
        scan={1: 1 << 7},
    )

    assert flagged_media.flagged_gallery_items(payload) == {1: flagged_media.SELF_HARM}


def test_a_payload_without_flagged_media_reports_nothing():
    assert flagged_media.flagged_gallery_items(_raw_components(["https://cdn.example/a.png"])) == {}
    assert flagged_media.flagged_gallery_items(None) == {}
    assert flagged_media.flagged_gallery_items([]) == {}


def test_the_scan_result_falls_back_to_the_media_items_own_flags():
    # A payload from before content_scan_metadata still carries the older field.
    payload = [{"type": 12, "items": [{"media": {"url": "u", "flags": 1 << 4}}]}]

    assert flagged_media.flagged_gallery_items(payload) == {0: flagged_media.EXPLICIT}


def test_a_placeholder_url_names_the_flag_it_stands_in_for():
    assert flagged_media.placeholder_flag(flagged_media.placeholder_url("gore")) == "gore"
    assert flagged_media.placeholder_flag("https://cdn.example/gore.png") is None
    assert flagged_media.placeholder_flag(None) is None


def test_a_late_flag_swaps_in_the_placeholder_under_the_gallery():
    view = _deleted_view(["https://cdn.example/a.png", "https://cdn.example/b.png"])

    assert formatters._apply_media_flags(view, {1: flagged_media.GORE}, "en") is True

    gallery = next(item for item in view.walk_children() if isinstance(item, discord.ui.MediaGallery))
    assert str(gallery.items[0].media.url) == "https://cdn.example/a.png"
    assert str(gallery.items[1].media.url) == flagged_media.placeholder_url(flagged_media.GORE)

    container = next(item for item in view.children if isinstance(item, discord.ui.Container))
    children = list(container.children)
    note = next(
        child for child in children
        if isinstance(child, discord.ui.TextDisplay) and "flagged-media" in child.content
    )
    # The note stays a subtext line directly under the gallery it explains.
    assert note.content.startswith("-# ")
    assert "gore" in note.content
    assert children.index(note) == children.index(gallery) + 1


def test_a_second_late_flag_adds_its_line_without_repeating_the_first():
    view = _deleted_view(
        [flagged_media.placeholder_url(flagged_media.EXPLICIT), "https://cdn.example/b.png"],
        {0: flagged_media.EXPLICIT},
    )

    assert formatters._apply_media_flags(view, {1: flagged_media.SELF_HARM}, "en") is True

    notes = [text for text in _texts(view) if "flagged-media" in text]
    assert len(notes) == 1
    assert "?type=explicit" in notes[0]
    assert "?type=self-harm" in notes[0]


def test_nothing_is_rewritten_when_no_image_carries_a_new_flag():
    view = _deleted_view(["https://cdn.example/a.png"])
    assert formatters._apply_media_flags(view, {}, "en") is False


@pytest.mark.parametrize("flag", flagged_media.FLAG_TYPES)
def test_an_already_replaced_image_is_not_replaced_again(flag):
    view = _deleted_view([flagged_media.placeholder_url(flag)], {0: flag})
    assert formatters._apply_media_flags(view, {0: flag}, "en") is False


# ── The raw update listener ──────────────────────

def _update(components, channel_id=7, guild_id=1, message_id=55):
    return SimpleNamespace(
        data={"components": components},
        guild_id=guild_id,
        channel_id=channel_id,
        message_id=message_id,
    )


def _posted_components(view):
    """The component objects a fetched message carries for a rendered *view*.

    A fetched message holds parsed components rather than the payload dicts a
    view serialises to, which is what ``LayoutView.from_message`` reads.
    """
    return [
        component for component in map(_component_factory, view.to_components())
        if component is not None
    ]


def _late_flag_bot(view, channel_id=7):
    """A bot whose log channel holds *view* as a posted entry."""
    message = SimpleNamespace(
        id=55,
        components=_posted_components(view),
        attachments=[],
        webhook_id=None,
        author=SimpleNamespace(id=999),
        edit=mock.AsyncMock(),
    )
    channel = SimpleNamespace(
        id=channel_id,
        fetch_message=mock.AsyncMock(return_value=message),
        guild=SimpleNamespace(id=1),
    )
    guild = SimpleNamespace(
        id=1,
        preferred_locale="en",
        get_channel_or_thread=lambda _channel_id: channel,
    )
    bot = SimpleNamespace(user=SimpleNamespace(id=999), get_guild=lambda _guild_id: guild)
    return bot, channel, message


def _late_flag_cog(bot, channel_ids=(7,)):
    cog = logging_cog.ServerLogger(bot)
    cog.config = mock.AsyncMock(return_value={})
    cog.configured_channel_ids = lambda _guild_id: set(channel_ids)
    return cog


def test_the_entry_is_edited_when_discord_flags_an_image_afterwards():
    bot, _channel, message = _late_flag_bot(_deleted_view(["https://cdn.example/a.png"]))
    cog = _late_flag_cog(bot)

    asyncio.run(cog.on_raw_message_update(
        _update(_raw_components(["https://cdn.example/a.png"], {0: 1 << 4}))))

    message.edit.assert_awaited_once()
    edited = message.edit.await_args.kwargs["view"]
    gallery = next(item for item in edited.walk_children() if isinstance(item, discord.ui.MediaGallery))
    assert str(gallery.items[0].media.url) == flagged_media.placeholder_url(flagged_media.EXPLICIT)
    assert any(
        "flagged-media" in item.content
        for item in edited.walk_children()
        if isinstance(item, discord.ui.TextDisplay)
    )


def test_the_entry_is_edited_only_once_per_flag():
    bot, _channel, message = _late_flag_bot(_deleted_view(["https://cdn.example/a.png"]))
    cog = _late_flag_cog(bot)
    payload = _update(_raw_components(["https://cdn.example/a.png"], {0: 1 << 4}))

    asyncio.run(cog.on_raw_message_update(payload))
    # The edit itself comes back as an update; the placeholder is already there.
    message.components = _posted_components(message.edit.await_args.kwargs["view"])
    asyncio.run(cog.on_raw_message_update(payload))

    assert message.edit.await_count == 1


def test_an_update_in_a_channel_without_logging_is_left_alone():
    bot, channel, message = _late_flag_bot(_deleted_view(["https://cdn.example/a.png"]))
    cog = _late_flag_cog(bot, channel_ids=())

    asyncio.run(cog.on_raw_message_update(
        _update(_raw_components(["https://cdn.example/a.png"], {0: 1 << 4}))))

    channel.fetch_message.assert_not_awaited()
    message.edit.assert_not_awaited()


def test_an_update_without_a_flagged_image_never_fetches_the_message():
    bot, channel, message = _late_flag_bot(_deleted_view(["https://cdn.example/a.png"]))
    cog = _late_flag_cog(bot)

    asyncio.run(cog.on_raw_message_update(
        _update(_raw_components(["https://cdn.example/a.png"]))))

    channel.fetch_message.assert_not_awaited()
    message.edit.assert_not_awaited()
