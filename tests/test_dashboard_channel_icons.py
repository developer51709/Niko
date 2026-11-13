"""The dashboard channel picker's per-kind icons.

Each row draws the glyph for the channel it names: a rules channel and an
age-restricted channel have their own, and voice, stage, forum and announcement
channels keep their kind instead of falling back to the text-channel icon.

The picker's only input is the bot's resources payload, so these tests check the
mapping itself (executed through Bun) and the assets it names, plus the payload
rules that keep channel kinds and flags flowing to it.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "web" / "public" / "assets" / "discord-icons" / "from-discord"
MODULE = ROOT / "web" / "src" / "components" / "dashboard" / "channelIcons.ts"
ROUTES = ROOT / "src" / "webapp" / "routes" / "dashboard_routes.py"

#: (channel as the resources payload sends it, icon the picker must draw)
CASES = [
    ({"type": "text"}, "text-channel"),
    ({"type": "news"}, "announcement-channel"),
    ({"type": "forum"}, "forum-channel"),
    ({"type": "media"}, "media-channel"),
    ({"type": "voice"}, "voice-channel"),
    ({"type": "stage_voice"}, "stage-channel"),
    ({"type": "public_thread"}, "thread"),
    ({"type": "category"}, "text-channel"),
    ({"type": "text", "nsfw": True}, "text-channel-nsfw"),
    ({"type": "news", "nsfw": True}, "text-channel-nsfw"),
    ({"type": "voice", "nsfw": True}, "voice-channel"),
    ({"type": "text", "rules": True}, "rules-channel"),
    ({"type": "text", "rules": True, "nsfw": True}, "rules-channel"),
    ({}, "text-channel"),
    (None, "cross"),
]

BUN = shutil.which("bun")


@pytest.mark.skipif(BUN is None, reason="bun is needed to execute the TypeScript mapping")
def test_each_channel_kind_gets_its_own_icon():
    script = (
        "const cases = %s;"
        "import(%s).then(({channelIconName}) => "
        "console.log(JSON.stringify(cases.map((kind) => channelIconName(kind)))));"
    ) % (json.dumps([kind for kind, _ in CASES]), json.dumps(MODULE.as_uri()))
    result = subprocess.run(
        [BUN, "-e", script], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [icon for _, icon in CASES]


def test_every_icon_the_picker_names_is_shipped():
    for _, icon in CASES:
        assert (ICONS / f"{icon}.svg").is_file(), f"missing icon asset: {icon}.svg"


def test_the_general_channel_list_leaves_forums_and_media_out():
    """Forums and media channels post by creating a thread, so they must not be
    offered as welcome, ticket or logging targets just to show their icon."""
    source = ROUTES.read_text(encoding="utf-8")

    assert 'in {"text", "news"}' in source
    assert '"text", "news", "forum", "media"' not in source


def test_the_payload_carries_the_kind_and_the_icon_flags():
    source = ROUTES.read_text(encoding="utf-8")

    assert '"type": str(getattr(getattr(channel, "type", None), "name", "text"))' in source
    assert '"nsfw": bool(getattr(channel, "nsfw", False))' in source
    assert '"rules":' in source
