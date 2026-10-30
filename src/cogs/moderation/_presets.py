"""
Blocked-word preset filters — curated regex patterns for slurs and other
content a server does not want to hand-maintain a word list for.

A preset is deliberately *not* a plain keyword. Plain keyword matching (which
is what a custom entry still uses) is easy to walk around — ``n1gg3r``,
``n i g g e r``, ``n.i.g.g.e.r``, ``niiiigger``, ``nigger`` with a Cyrillic
``і``, or a fullwidth spelling all sail straight past a substring test. Each
term here is expanded into a regular expression that tolerates:

* leet substitutions — ``n1gg3r``, ``sh1t``, ``@ss``
* separators between letters — ``n i g g e r``, ``n.i.g.g.e.r``, ``n-i-g-g-e-r``
  (and emoji, which are ``\\W`` as well)
* repeated letters — ``niiiigger``, ``fuuuuck``
* a letter hidden behind a self-censoring asterisk — ``sh*t``, ``f*ck``, ``n*gga``
  (a word still has to start with a real letter, so a bare run of mask
  characters such as ``****`` or ``###`` is never a match)
* a dropped doubled letter — ``niger``, ``shiting`` (the country name ``Niger``
  is flagged along with it)
* unicode look-alikes — Cyrillic ``а е о р с х у і`` in place of the Latin
  letters they imitate
* fullwidth forms and zero-width characters, which
  :func:`cogs.moderation.utils.normalize_message_content` folds away first
* simple inflections — ``slurs``, ``faggots``, ``retarded``

Matching is still whole-word: the patterns are fenced with
``(?<![a-z0-9])`` / ``(?![a-z])``, so a slur buried inside an ordinary word
(``class``, ``analysis``, ``raccoon``) is left alone.
"""

from dataclasses import dataclass
from functools import lru_cache
import re
from typing import Iterable

# At most three separator characters may sit between two letters, matching the
# tolerance the custom word matcher uses (``a.s.s`` and ``a s s`` are caught,
# but a stray letter four characters away is not bridged).
MAX_INNER_SEPARATORS = 3

# Bounded like the custom word-pattern cache, so a busy bot cannot grow the
# compiled-pattern cache without limit.
MAX_CACHED_PRESET_PATTERNS = 64

# Inflections appended after a term, so "slurs" and "faggots" are caught by the
# singular entry. Kept short on purpose: the trailing word boundary is what
# keeps the pattern from matching inside a longer, innocent word. "es" is only
# offered after a sibilant ending, because otherwise "spic" would reach
# "spices".
_INFLECTIONS = "(?:s|ed|d|ing|er|ers|ies|y)?"
_SIBILANT_INFLECTIONS = "(?:es|s|ed|d|ing|er|ers|ies|y)?"

# A leading "=" marks a term that must match exactly, with no inflections.
# It is for words that share a stem with ordinary English: "spic" would
# otherwise reach "spicy", "spiced" and "spices", and "chink" would reach
# "chinking" and "a chink in the armour". The plural is not worth flagging
# those for.
EXACT_PREFIX = "="

# The characters people use to hide a letter themselves — "sh*t", "n#gga".
# They are only offered for a letter *inside* a word: a word has to start with a
# real letter, because a bare run of them is not a word at all. It is what a
# censor mask leaves behind, and "###" is Discord's own heading marker. Letting a
# leading letter be a placeholder made masked text match the term it masked, so
# a censored repost was censored again — the same text, forever.
_PLACEHOLDERS = "*#"

# Letters sharing a shape, a keyboard run, or a common leet substitution.
# ``re.escape`` is applied per character when a class is built, so entries like
# "(" or "$" stay literal.
_LETTER_VARIANTS = {
    "a": "a4@а",
    "b": "b8",
    "c": "c(с",
    "d": "d",
    "e": "e3е",
    "f": "f",
    "g": "g96",
    "h": "h",
    "i": "i1!|і",
    "j": "jј",
    "k": "kк",
    "l": "l1|",
    "m": "m",
    "n": "nñ",
    "o": "o0о",
    "p": "pр",
    "q": "q",
    "r": "r",
    "s": "s5$ѕ",
    "t": "t7",
    "u": "u",
    "v": "v",
    "w": "w",
    "x": "xх",
    "y": "yу",
    "z": "z2",
}


@dataclass(frozen=True)
class PresetFilter:
    """One curated filter a server can switch on.

    ``terms`` are base words: every spelling trick above is generated from
    them, so the lists stay readable and editable. ``patterns`` are raw regex
    sources for the rare entry that is not a single word.
    """

    key: str
    labels: dict          # lang -> short name shown in panels and dashboards
    descriptions: dict    # lang -> one-line explanation of what it catches
    terms: tuple
    patterns: tuple = ()


PRESET_FILTERS: tuple[PresetFilter, ...] = (
    PresetFilter(
        key="slurs",
        labels={
            "en": "Slurs & hate speech",
            "de": "Beleidigungen & Hassrede",
            "es": "Insultos y discurso de odio",
            "fr": "Insultes et discours haineux",
        },
        descriptions={
            "en": "Racial, ethnic, religious, homophobic and ableist slurs, including leet or spaced-out spellings.",
            "de": "Rassistische, ethnische, religiöse, homophobe und ableistische Beleidigungen — auch in Leet- oder getrennter Schreibweise.",
            "es": "Insultos raciales, étnicos, religiosos, homófobos y capacitistas, incluso escritos con leet o separados.",
            "fr": "Insultes racistes, ethniques, religieuses, homophobes et validistes, y compris en écriture leet ou espacée.",
        },
        terms=(
            "nigger", "nigga", "niglet", "nigglet", "faggot", "fagg", "fag",
            "dyke", "tranny", "trannie", "shemale", "kike", "spick",
            "wetback", "beaner", "gook", "coon", "sandnigger",
            "raghead", "towelhead", "paki", "pikey", "gyppo", "darkie",
            "=spic",
            "jigaboo", "porchmonkey", "tarbaby", "coonass", "retard",
            "spastic", "spaz", "mongoloid", "midget", "redskin", "injun",
            "squaw", "gypo", "wigger", "whitey", "=chink", "=spick",
        ),
    ),
    PresetFilter(
        key="profanity",
        labels={
            "en": "Severe profanity",
            "de": "Derbe Flüche",
            "es": "Palabrotas graves",
            "fr": "Jurements violents",
        },
        descriptions={
            "en": "The heavy swear words, matched as whole words so ordinary words are safe.",
            "de": "Die derben Schimpfwörter — als ganze Wörter, damit normale Wörter sicher bleiben.",
            "es": "Las palabrotas más fuertes, como palabras completas para no afectar a otras.",
            "fr": "Les jurons les plus violents, détectés comme mots entiers pour épargner les mots courants.",
        },
        terms=(
            "fuck", "motherfucker", "shit", "bullshit", "dipshit", "dumbass",
            "jackass", "cunt", "bitch", "bastard", "asshole", "arsehole",
            "dickhead", "dickface", "wanker", "wank", "twat", "tosser",
            "bollocks", "prick", "whore", "slut", "skank", "douche",
            "douchebag", "piss", "assmunch",
        ),
    ),
    PresetFilter(
        key="sexual",
        labels={
            "en": "Sexual content",
            "de": "Sexuelle Inhalte",
            "es": "Contenido sexual",
            "fr": "Contenu sexuel",
        },
        descriptions={
            "en": "Explicit sexual terms and adult-platform spam bait.",
            "de": "Explizite sexuelle Begriffe und Werbe-Köder von Erwachsenenportalen.",
            "es": "Términos sexuales explícitos y cebos de spam de plataformas para adultos.",
            "fr": "Termes sexuels explicites et appâts de spam des plateformes pour adultes.",
        },
        terms=(
            # "onlyfans" is deliberately absent: bridging the space would flag
            # the ordinary phrase "only fans".
            "porn", "porno", "pornography", "pornhub", "hentai",
            "nsfw", "nude", "dildo", "blowjob", "handjob", "creampie",
            "cumshot", "jizz", "semen", "masturbat", "masturbation", "orgasm",
            "penis", "vagina", "boobs", "tits", "nipple", "horny", "sexting",
            "rape", "rapist", "molest", "pedophile", "pedo", "loli", "incest",
        ),
    ),
    PresetFilter(
        key="threats",
        labels={
            "en": "Threats & self-harm bait",
            "de": "Drohungen & Selbstverletzung",
            "es": "Amenazas y autolesión",
            "fr": "Menaces et incitation à l'automutilation",
        },
        descriptions={
            "en": "Telling someone to kill themselves, and the short forms used for it.",
            "de": "Aufforderungen, sich umzubringen, samt der üblichen Kurzformen.",
            "es": "Decirle a alguien que se mate, incluidas las formas cortas.",
            "fr": "Dire à quelqu'un de se tuer, ainsi que les formes abrégées employées pour le faire.",
        },
        terms=(
            "kill yourself", "kill yourselves", "kill urself", "kill ur self",
            "neck yourself", "hang yourself", "rope yourself", "end yourself",
            "drink bleach", "unalive yourself", "kys", "kyourself",
        ),
    ),
)

PRESETS_BY_KEY: dict[str, PresetFilter] = {preset.key: preset for preset in PRESET_FILTERS}
PRESET_KEYS: tuple[str, ...] = tuple(preset.key for preset in PRESET_FILTERS)

# Default language used when a caller asks for a label without one.
DEFAULT_PRESET_LANG = "en"


def preset_label(preset: PresetFilter, lang: str = DEFAULT_PRESET_LANG) -> str:
    """Localised name of a preset, falling back to English."""
    return preset.labels.get(lang) or preset.labels[DEFAULT_PRESET_LANG]


def preset_description(preset: PresetFilter, lang: str = DEFAULT_PRESET_LANG) -> str:
    """Localised one-line explanation of a preset, falling back to English."""
    return preset.descriptions.get(lang) or preset.descriptions[DEFAULT_PRESET_LANG]


def preset_catalog(lang: str = DEFAULT_PRESET_LANG) -> list[dict]:
    """The preset list as plain data, for the dashboard and the panel.

    Each entry carries its key plus a label and description, so a UI never has
    to hard-code the catalog and drift from the patterns the bot actually runs.
    """
    return [
        {
            "key": preset.key,
            "label": preset_label(preset, lang),
            "description": preset_description(preset, lang),
            "terms": len(preset.terms),
        }
        for preset in PRESET_FILTERS
    ]


def normalize_presets(value) -> list[str]:
    """Enabled preset keys from stored config, deduplicated and ordered.

    Junk is dropped rather than raising: the value can come from a hand-edited
    store, and a bad entry must never disable the whole filter.
    """
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set, frozenset)):
        return []
    enabled = {str(entry).strip().lower() for entry in value if isinstance(entry, (str, int))}
    return [key for key in PRESET_KEYS if key in enabled]


def _letter_class(char: str, *, leading: bool = False) -> str:
    """A repeatable class of every spelling of one letter.

    ``leading`` drops the self-censoring placeholders: the first letter of a
    word has to be a real one, or a run of mask characters (``****``, ``###``)
    satisfies a term on its own.
    """
    variants = _LETTER_VARIANTS.get(char, char) + ("" if leading else _PLACEHOLDERS)
    unique = dict.fromkeys(variants)
    return "[" + "".join(re.escape(variant) for variant in unique) + "]+"


def _run_lengths(token: str) -> list[tuple[str, int]]:
    """The token as (letter, run length) pairs — "nigger" and "piss" have runs."""
    runs: list[tuple[str, int]] = []
    for char in token:
        if runs and runs[-1][0] == char:
            letter, length = runs[-1]
            runs[-1] = (letter, length + 1)
        else:
            runs.append((char, 1))
    return runs


def _token_source(token: str, gap: str) -> str:
    """One word of a term, tolerant of separators and of a dropped double.

    A doubled letter stays optional (``gg`` also matches a single ``g``), which
    is how "n1ger" and "niger" are caught alongside "nigger" — while still
    allowing the letters to be separated, so "n i g g e r" matches too.
    """
    parts = []
    for position, (letter, run) in enumerate(_run_lengths(token)):
        klass = _letter_class(letter, leading=position == 0)
        parts.append(f"{klass}(?:{gap}{klass}){{0,{run - 1}}}" if run > 1 else klass)
    return gap.join(parts)


def _term_source(term: str) -> tuple[str, str] | None:
    """One term expanded to a tolerant pattern, plus the inflection to allow.

    Split on separators so a multi-word phrase ("kill yourself") keeps its
    word split while still tolerating punctuation and spacing inside it.
    """
    term = str(term).strip().lower()
    exact = term.startswith(EXACT_PREFIX)
    if exact:
        term = term[len(EXACT_PREFIX):]
    tokens = [token for token in re.split(r"[\W_]+", term) if token]
    if not tokens:
        return None
    gap = r"[\W_]{0,%d}" % MAX_INNER_SEPARATORS
    source = r"[\W_]+".join(_token_source(token, gap) for token in tokens)
    if exact:
        return source, ""
    last = tokens[-1]
    if last[-1] in "sxz" or last.endswith(("ch", "sh")):
        return source, _SIBILANT_INFLECTIONS
    return source, _INFLECTIONS


def build_preset_regex(keys: Iterable[str]) -> re.Pattern | None:
    """Compile the enabled presets into one case-insensitive pattern.

    Returns None when nothing usable is enabled, so callers can skip matching
    entirely instead of searching an empty pattern.
    """
    return _compile_preset_regex(tuple(normalize_presets(list(keys))))


@lru_cache(maxsize=MAX_CACHED_PRESET_PATTERNS)
def _compile_preset_regex(keys: tuple) -> re.Pattern | None:
    alternatives: list[str] = []
    for key in keys:
        preset = PRESETS_BY_KEY.get(key)
        if preset is None:
            continue
        for term in preset.terms:
            expanded = _term_source(term)
            if expanded:
                source, inflection = expanded
                alternatives.append(source + inflection)
        # Raw regex sources are matched as written, so a curated pattern can
        # express something a single word cannot.
        alternatives.extend(str(pattern) for pattern in preset.patterns)
    if not alternatives:
        return None
    body = "|".join(r"(?:" + alternative + r")" for alternative in alternatives)
    return re.compile(r"(?<![a-z0-9])(?:" + body + r")(?![a-z])", re.IGNORECASE)
