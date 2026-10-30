"""Command wording in the help menu: no emoji, sentence-cased lines.

The help card lists each command as its usage line plus a one-line description,
so decoration inside those lines competes with the layout's own emoji and a line
that starts lowercase reads as a continuation of the command above it.
"""

import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.locales import available_namespaces, load_locales  # noqa: E402

LANGS = ("en", "de", "es", "fr")
SRC = Path(__file__).resolve().parents[1] / "src"

# Typography that belongs in prose: arrows used as words ("top ↔ bottom"),
# the multiplication sign, the non-breaking hyphen and the em dash.
KEEP = {0x2194, 0x2195, 0x00D7, 0x2011, 0x2014}


def is_emoji(char: str) -> bool:
    code = ord(char)
    if code < 0x2000 or code in KEEP:
        return False
    if char in "\ufe0f\u200d\u20e3":
        return True
    if 0x1F000 <= code <= 0x1FAFF or 0x2600 <= code <= 0x27BF:
        return True
    return unicodedata.category(char) in {"So", "Sk"}


def catalogues():
    for path in sorted((SRC / "cogs").glob("*/locales/en.json")):
        package = ".".join(path.parent.parent.relative_to(SRC).parts)
        if "commands" not in available_namespaces(package):
            continue
        yield package, load_locales(package, "commands")


def test_no_command_description_carries_emoji():
    offenders = []
    for package, tables in catalogues():
        for lang in LANGS:
            for key, text in tables[lang].items():
                if not (key.endswith(".help") or key.endswith(".description")):
                    continue
                if any(is_emoji(char) for char in text):
                    offenders.append(f"{package} {lang} {key}: {text!r}")

    assert offenders == []


def test_every_help_line_starts_with_a_capital():
    offenders = []
    for package, tables in catalogues():
        for lang in LANGS:
            for key, text in tables[lang].items():
                if not key.endswith(".help"):
                    continue
                # Spanish opens with ¿ or ¡ before the first word.
                first = text.lstrip("¿¡").strip()[:1]
                if first and first.isalpha() and first.islower():
                    offenders.append(f"{package} {lang} {key}: {text!r}")

    assert offenders == []


def test_help_lines_have_no_stray_spacing():
    offenders = []
    for package, tables in catalogues():
        for lang in LANGS:
            for key, text in tables[lang].items():
                if not key.endswith(".help"):
                    continue
                if "  " in text or text != text.strip():
                    offenders.append(f"{package} {lang} {key}: {text!r}")

    assert offenders == []
