"""
Per-page social metadata and Discord component embeds for the public site.

Discord renders a **Components V2** link embed when the server-rendered document
carries a ``<script id="discord:component-embed" type="application/json">`` block
(https://docs.discord.com/developers/link-previews/component-embeds). Discord
never runs page scripts and never reads a hash route, so the payload has to be in
the HTML the crawler is handed.

Every route is served the same React shell, and the head is rendered here, per
request, instead of being baked into one HTML file per page at build time:

* the page copy comes from ``social-pages.json``, written by the website build
  (``web/vite.config.ts``), so titles and descriptions keep living next to the
  Open Graph cards they belong to;
* everything that changes between deployments — the invite link, the live
  command/server/member counts on the landing pages, and the per-page-type
  layouts below — is filled in here, so a rebuild is no longer needed to refresh
  them.

**Page types.** Most pages use the standard container: a Niko-branded heading,
the page description, the generated Open Graph card, and the button row. Pages
about something other than Niko itself describe their subject instead, which is
what ``context`` carries in:

* ``kind="guild"`` — a server's leveling leaderboard. A Section component with
  the guild's icon as its thumbnail accessory, the guild's own name, and a short
  stat overview, with no Niko-branded card.
* ``kind="staff"`` — a team member's profile. Also a Section with a thumbnail
  accessory, but coloured with that member's own card accent and carrying their
  role, bio and links, so no two profiles read the same.
* ``kind="applications"`` — the staff applications page. Lists the roles that
  are open, each linked to its own form, so a reader can pick one from the
  preview without opening the page first.
* ``kind="application"`` — one role's application form. Describes that role and
  says whether it is accepting applications right now, so a closed role does
  not read as if it were still hiring.

A context is only ever built from data the page itself already publishes.

The rendered tags replace the shell's own ``description … title`` region, which
is left in place as the fallback preview for anything served without us.
"""

import json
import os
import re
import threading
from html import escape

SITE_URL = "https://niko.sryze.cc"
MANIFEST_NAME = "social-pages.json"

# Discord gives the payload a hard 3,000-byte budget, counting escape sequences
# at full length, and allows 40 components in total including the Container.
EMBED_BYTE_LIMIT = 3000
EMBED_COMPONENT_LIMIT = 40
BRAND_ACCENT = int("8bd5b1", 16)  # the site's --sage token
COMMANDS_PATH = "/commands"
# The support button points at the website's /discord page, which resolves the
# current invite from the live bot instead of a raw discord.gg link.
SUPPORT_PATH = "/discord"

# Component types from Discord's schema (see the module docstring).
CONTAINER, SECTION, TEXT_DISPLAY, THUMBNAIL, MEDIA_GALLERY, SEPARATOR, ACTION_ROW, BUTTON = 17, 9, 10, 11, 12, 14, 1, 2

# What an unlisted route (the dashboard, the transcript viewer, a typo) falls
# back to. The shell carries the same copy, so a page served without the manifest
# still previews sensibly.
DEFAULT_TITLE = "Niko — Discord companion"
DEFAULT_DESCRIPTION = "Niko is the warm, capable Discord companion for communities that care."
# A guild with no icon still needs a thumbnail, and a missing media URL
# invalidates the whole payload.
FALLBACK_THUMBNAIL = f"{SITE_URL}/icons/niko-512.png"

# The region the build used to overwrite: from the description tag through the
# title, which is where the Open Graph, Twitter and canonical tags sit.
_HEAD_REGION = re.compile(r'<meta name="description"[\s\S]*?<title>.*?</title>')
_TITLE_SUFFIX = re.compile(r" — Niko( docs| changelog)?$")

_manifest_lock = threading.Lock()
_manifest_cache: dict = {"path": None, "stamp": None, "pages": {}}


def route_key(route: str | None) -> str:
    """Normalise a request path to the key the manifest is stored under."""
    path = (route or "").split("?", 1)[0].split("#", 1)[0].strip()
    if not path or path == "/":
        return "/"
    return "/" + path.strip("/")


def load_pages(dist_dir: str) -> dict:
    """The page copy from the build manifest, re-read when it changes.

    A missing or unreadable manifest is not an error: the site still serves,
    with the shell's own default preview.
    """
    path = os.path.join(dist_dir, MANIFEST_NAME)
    try:
        stamp = os.stat(path).st_mtime_ns
    except OSError:
        return {}
    with _manifest_lock:
        if _manifest_cache["path"] == path and _manifest_cache["stamp"] == stamp:
            return _manifest_cache["pages"]
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            pages = data.get("pages") if isinstance(data, dict) else None
            pages = pages if isinstance(pages, dict) else {}
        except (OSError, ValueError):
            pages = {}
        _manifest_cache.update({"path": path, "stamp": stamp, "pages": pages})
        return pages


def page_metadata(dist_dir: str, route: str | None, template: str = None) -> tuple[str, dict]:
    """The copy for one route, plus the canonical path it is stored under.

    Routes that carry a dynamic id — a server's leaderboard, a team profile —
    borrow the copy of their section (``template``) while keeping their own URL.
    """
    pages = load_pages(dist_dir)
    key = route_key(route)
    page = pages.get(key)
    if not isinstance(page, dict) and template:
        page = pages.get(route_key(template))
    if not isinstance(page, dict):
        # Unlisted route: generic copy, but the canonical URL still points at
        # the page that was actually requested.
        return key, {
            "title": DEFAULT_TITLE,
            "description": DEFAULT_DESCRIPTION,
            "section": "",
            "landing": False,
            "image": f"{SITE_URL}/og/home.png",
        }
    return key, {
        "title": str(page.get("title") or DEFAULT_TITLE),
        "description": str(page.get("description") or DEFAULT_DESCRIPTION),
        "section": str(page.get("section") or ""),
        "landing": bool(page.get("landing")),
        "image": str(page.get("image") or f"{SITE_URL}/og/home.png"),
    }


def stats_line(stats: dict | None) -> str:
    """The landing pages' live counts, in Discord's subtext markdown."""
    if not stats:
        return ""
    try:
        commands = int(stats.get("command_count") or 0)
        guilds = int(stats.get("guild_count") or 0)
        members = int(stats.get("user_count") or 0)
    except (TypeError, ValueError):
        return ""
    if min(commands, guilds, members) <= 0:
        return ""
    return f"-# {commands:,} commands · {guilds:,} servers · {members:,} members"


def _link_buttons(invite_url: str) -> dict:
    """The closing button row: invite, commands, support server."""
    return {
        "type": ACTION_ROW,
        "components": [
            {"type": BUTTON, "style": 5, "url": invite_url, "label": "Add Niko"},
            {"type": BUTTON, "style": 5, "url": f"{SITE_URL}{COMMANDS_PATH}", "label": "Commands"},
            {"type": BUTTON, "style": 5, "url": f"{SITE_URL}{SUPPORT_PATH}", "label": "Support server"},
        ],
    }


def _section(content: str, thumbnail: str) -> dict:
    """A Section (type 9) with a text display and a thumbnail accessory."""
    return {
        "type": SECTION,
        "components": [{"type": TEXT_DISPLAY, "content": content}],
        "accessory": {"type": THUMBNAIL, "media": {"url": thumbnail or FALLBACK_THUMBNAIL}},
    }


def _standard_components(page: dict, description: str, stats: dict | None, invite_url: str) -> list:
    """Niko's own pages: heading, card image, separator, button row."""
    text = [f"# {_TITLE_SUFFIX.sub('', page['title'])}"]
    if page.get("section"):
        text.append(f"-# {page['section']}")
    if description:
        text.append(description)
    counts = stats_line(stats)
    if counts:
        text.append(counts)
    return [
        {"type": TEXT_DISPLAY, "content": "\n".join(text)},
        {"type": MEDIA_GALLERY, "items": [{"media": {"url": page["image"]}}]},
        {"type": SEPARATOR},
        _link_buttons(invite_url),
    ]


def _subject_components(context: dict, description: str, invite_url: str) -> list:
    """A page about a subject rather than about Niko.

    No branded card and no page title block: the subject leads, with its own
    thumbnail, and the button row still closes the embed. A subject that lists
    things — the open staff roles on the applications page — puts each entry in
    its own text display below the introduction, so the list reads as a list
    instead of running into the paragraph above it.
    """
    lines = [f"# {context['name']}"]
    if context.get("section"):
        lines.append(f"-# {context['section']}")
    if description:
        lines.append(description)
    lines.extend(line for line in context.get("lines", ()) if line)
    components = [_section("\n".join(lines), context.get("thumbnail"))]
    entries = [entry for entry in context.get("list", ()) if entry]
    if entries:
        components.append({"type": TEXT_DISPLAY, "content": "\n".join(entries)})
    components.extend(({"type": SEPARATOR}, _link_buttons(invite_url)))
    return components


def component_embed_payload(
    page: dict,
    invite_url: str,
    stats: dict | None = None,
    description: str | None = None,
    context: dict | None = None,
) -> dict:
    """The Components V2 payload Discord renders for a page."""
    body = page["description"] if description is None else description
    if context and context.get("kind"):
        components = _subject_components(context, body, invite_url)
        # A subject can colour its own container: a team member's card accent,
        # for instance. Everything else keeps Niko's.
        accent = context.get("accent")
        accent = accent if isinstance(accent, int) and 0 <= accent <= 0xFFFFFF else BRAND_ACCENT
    else:
        components = _standard_components(page, body, stats, invite_url)
        accent = BRAND_ACCENT
    return {
        "component": {
            "type": CONTAINER,
            "accent_color": accent,
            "components": components,
        },
    }


def component_embed_script(
    page: dict,
    invite_url: str,
    stats: dict | None = None,
    context: dict | None = None,
) -> str:
    """The ``<script>`` block Discord reads, or "" when nothing would fit.

    A payload over the byte limit is ignored and the plain Open Graph card is
    shown instead, which would lose the button row — so the copy is shortened,
    then the counts dropped, until the payload fits.
    """
    attempts = (
        (page["description"], stats),
        (page["description"], None),
        (f"{page['description'][:160]}…" if page["description"] else "", None),
        ("", None),
    )
    for description, attempt_stats in attempts:
        payload = component_embed_payload(page, invite_url, attempt_stats, description, context)
        container = payload["component"]
        if 1 + len(container["components"]) > EMBED_COMPONENT_LIMIT:
            continue
        # The element lives in the markup, so anything that could end it early is
        # escaped; Discord counts those escapes at full length, hence measuring
        # the escaped form.
        escaped = (
            json.dumps(payload, separators=(",", ":"))
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
        )
        if len(escaped.encode("utf-8")) <= EMBED_BYTE_LIMIT:
            return (
                '<script id="discord:component-embed" type="application/json">'
                f"{escaped}</script>"
            )
    return ""


def render_head(
    dist_dir: str,
    route: str | None,
    invite_url: str,
    stats_provider=None,
    context_provider=None,
) -> str:
    """The full replacement for the shell's ``description … title`` region.

    The Open Graph tags stay as the fallback preview; the component embed below
    them is what Discord renders as a Components V2 layout.
    """
    context = context_provider(route) if callable(context_provider) else None
    context = context if isinstance(context, dict) else None
    # A provider can recognise the route without having a subject to describe —
    # a server the bot is not in, a staff profile that is hidden. It still names
    # the section whose copy the page borrows.
    subject = context if (context and context.get("kind")) else None
    key, page = page_metadata(dist_dir, route, context.get("template") if context else None)
    # A subject page describes itself, so its own copy wins over the section's.
    if subject:
        page = {**page, "title": subject.get("title") or page["title"],
                "description": subject.get("description") or page["description"]}
    # The counts are only wanted on the landing pages, so the provider (which
    # may go as far as the bot loop) is never called for the others.
    stats = stats_provider() if (page["landing"] and callable(stats_provider)) else None
    canonical = f"{SITE_URL}{key}"
    title = escape(page["title"], quote=True)
    description = escape(page["description"], quote=True)
    image = escape(page["image"], quote=True)
    return (
        '<link rel="icon" type="image/svg+xml" href="/favicon.svg" />'
        f"<title>{title}</title>"
        f'<meta name="description" content="{description}" />'
        f'<link rel="canonical" href="{canonical}" />'
        '<meta property="og:type" content="website" />'
        f'<meta property="og:url" content="{canonical}" />'
        f'<meta property="og:title" content="{title}" />'
        f'<meta property="og:description" content="{description}" />'
        f'<meta property="og:image" content="{image}" />'
        '<meta property="og:image:width" content="1200" />'
        '<meta property="og:image:height" content="630" />'
        f'<meta property="og:image:alt" content="{description}" />'
        '<meta name="twitter:card" content="summary_large_image" />'
        f'<meta name="twitter:title" content="{title}" />'
        f'<meta name="twitter:description" content="{description}" />'
        f'<meta name="twitter:image" content="{image}" />'
        f"{component_embed_script(page, invite_url, stats, subject)}"
    )


def inject(
    shell: str,
    dist_dir: str,
    route: str | None,
    invite_url: str,
    stats_provider=None,
    context_provider=None,
) -> str:
    """The React shell with this route's social metadata rendered in."""
    head = render_head(dist_dir, route, invite_url, stats_provider, context_provider)
    if _HEAD_REGION.search(shell):
        return _HEAD_REGION.sub(lambda _match: head, shell, count=1)
    # A shell that does not carry the region (a hand-edited build, an older
    # index.html) still gets the tags, just appended before the head closes.
    if "</head>" in shell:
        return shell.replace("</head>", f"{head}</head>", 1)
    return shell
