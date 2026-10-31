"""Landing-page counts and the per-page link-preview contexts behind the Discord
embeds. Rendering itself lives in ``social_preview``."""

from urllib.parse import urlencode
import os
import re
import time
from . import social_preview
from flask import Response, jsonify, request
from . import config, database, runtime, staff


# Landing-page counts for the Discord embeds, refreshed at most once a minute.
_SOCIAL_STATS_TTL = 60

_social_stats_cache: tuple[float, dict] | None = None

# Per-page subject data (a server's leaderboard, a team profile). Slower moving
# than the counts, and cached per route.
_SOCIAL_CONTEXT_TTL = 300

_SOCIAL_CONTEXT_CACHE_LIMIT = 256

_social_context_cache: dict = {}


def _social_stats() -> dict:
    """Command, server and member counts for the landing pages' embeds.

    Serving a page must not wait on the bot loop, so the result is cached for a
    minute: the first landing-page request after each window is the only one
    that asks the bot, and everything else is answered from the cache or from
    the startup snapshot on disk.
    """
    global _social_stats_cache
    now = time.time()
    cached = _social_stats_cache
    if cached is not None and now - cached[0] < _SOCIAL_STATS_TTL:
        return cached[1]
    stats = None
    try:
        from .public_routes import _live_bot_stats
        live = _live_bot_stats()
        try:
            stats = runtime.run_on_bot_loop(live, timeout=2)
        except Exception:
            # Nothing was scheduled (no bot loop, or the future raised), so
            # close the coroutine instead of leaving it un-awaited.
            live.close()
            stats = None
    except Exception:
        stats = None
    if not stats:
        snapshot = runtime.load_json(config.BOT_STATS, {})
        stats = {
            "command_count": snapshot.get("command_count", 0),
            "guild_count":   snapshot.get("guild_count", 0),
            "user_count":    snapshot.get("user_count", 0),
        }
    _social_stats_cache = (now, stats)
    return stats

# Pages whose subject is something other than Niko itself. Each one gets its
# own container instead of the standard branded card, built from data the page
# already publishes: a server's leaderboard shows the server, a team profile
# shows that member, and the applications page lists the roles it is hiring for.
_GUILD_PAGE = re.compile(r"^/levels/(\d+)$")

_STAFF_PAGE = re.compile(r"^/team/([^/]+)$")

# Checked before _STAFF_PAGE: /team/apply is not a team profile, and the pattern
# above would otherwise claim it and borrow the roster's copy.
_TEAM_APPLY_PAGE = "/team/apply"

# One role's own application form, /team/apply/<opening id>.
_TEAM_APPLICATION_PAGE = re.compile(r"^/team/apply/([^/]+)$")

# Discord caps the payload at 3,000 bytes and an unreadably long list helps
# nobody, so the preview names a handful of roles and leaves the rest to the page.
_APPLICATION_LIST_LIMIT = 6

# How many rows the list preview reads before keeping the open ones: closed
# roles are read too (a role's own page reports its status), and they must not
# crowd the roles a reader can actually apply to out of the capped list.
_APPLICATION_READ_LIMIT = 20

# The partnership ad's own art, relative to the built site. The card is written
# by the website build (``web/vite.config.ts``); the icon ships with every build.
PARTNERSHIP_OG_CARD = "og/discord/partnership.png"
PARTNERSHIP_ICON = "icons/niko-512.png"


def _staff_card_accent(member: dict) -> int | None:
    """A team member's own card colour, as the integer Discord wants."""
    raw = str((member.get("card") or {}).get("accent") or "").strip().lstrip("#")
    if len(raw) != 6:
        return None
    try:
        return int(raw, 16)
    except ValueError:
        return None


def _bot_avatar_url() -> str:
    """The bot's own avatar, used as the thumbnail of its own pages.

    An empty string is fine: the preview module falls back to the site icon, so
    a server without a live gateway still previews.
    """
    bot = runtime._discord_bot
    user = getattr(bot, "user", None) if bot is not None else None
    if user is None:
        return ""
    try:
        return str(user.display_avatar.url)
    except Exception:
        return ""


def _guild_embed_context(guild_id: str) -> dict | None:
    """The server a leveling leaderboard belongs to.

    Everything here is already public on that page (its own API returns the
    name, icon, member count and ranked total), and a guild the bot is not in
    has nothing to describe, so it keeps the section's generic copy.
    """
    if runtime._discord_bot is None or not guild_id.isdigit():
        return None
    try:
        guild = runtime._discord_bot.get_guild(int(guild_id))
    except Exception:
        guild = None
    if guild is None:
        return None
    icon = getattr(guild, "icon", None)
    members = int(getattr(guild, "member_count", 0) or 0)
    ranked = None
    try:
        # The reader schedules the bot loop itself and only counts the total, so
        # one row is all this needs to read.
        page = database.get_runtime_guild_level_page(guild_id, 0, 1)
    except Exception:
        page = None
    if isinstance(page, tuple) and len(page) == 2:
        ranked = int(page[1] or 0)
    stats = []
    if members:
        stats.append(f"**{members:,}** members")
    if ranked:
        stats.append(f"**{ranked:,}** ranked by XP" if members else f"**{ranked:,}** members ranked by XP")
    lines = [" · ".join(stats)] if stats else []
    paused = False
    try:
        paused = not bool(database.get_runtime_level_config(guild_id).get("xp_enabled", True))
    except Exception:
        paused = False
    if paused:
        lines.append("-# XP earning is currently paused in this server.")
    if ranked is None:
        description = f"Leveling standings for {guild.name}, ranked by level and XP."
    elif members:
        description = f"Leveling standings for {guild.name} — {members:,} members, {ranked:,} ranked by XP."
    else:
        description = f"Leveling standings for {guild.name} — {ranked:,} members ranked by XP."
    return {
        "kind": "guild",
        "template": "/levels",
        "title": f"{guild.name} — Level leaderboard",
        "description": description,
        "name": guild.name,
        "section": "Level leaderboard",
        "thumbnail": str(icon.url) if icon is not None else "",
        "accent": None,
        "lines": lines,
    }


def _staff_embed_context(member_id: str) -> dict | None:
    """One team member, from the public roster only.

    ``_load_staff_rows`` is the same list the team page itself serves, so a
    hidden or suspended profile has no context and falls back to the section's
    generic copy rather than leaking through the preview.
    """
    if not member_id or not member_id.isdigit():
        return None
    try:
        member = next((item for item in staff._load_staff_rows() if str(item.get("id")) == member_id), None)
    except Exception:
        member = None
    if not member:
        return None
    name = str(member.get("name") or member.get("username") or "Niko staff")
    role_label = str(member.get("role_label") or "Staff")
    bio = " ".join(str(member.get("bio") or "").split())
    if len(bio) > 180:
        bio = bio[:177].rstrip() + "…"
    lines = []
    links = [link for link in (member.get("public_links") or []) if isinstance(link, dict) and link.get("url")]
    if links:
        label = "link" if len(links) == 1 else "links"
        lines.append(f"-# {len(links)} public {label} · niko.sryze.cc/team")
    return {
        "kind": "staff",
        "template": "/team",
        "title": f"{name} — Niko team",
        "description": bio or f"{role_label} on the Niko team. Say hi in the support server.",
        "name": name,
        "section": f"{role_label.upper()} · STAFF",
        "thumbnail": str(member.get("avatar_url") or ""),
        # Each profile carries the member's own card colour, so no two staff
        # previews look the same.
        "accent": _staff_card_accent(member),
        "lines": lines,
    }


def _team_apply_embed_context() -> dict:
    """The staff roles accepting applications, linked in the preview itself.

    The applications page needs a signed-in member to list its openings, but a
    link preview is read by everyone (and by Discord), so this describes the
    roles without asking the crawler to authenticate. The role list is plain
    public information; every entry links straight to that role's form so a
    reader can pick one from the preview instead of opening the page first.
    """
    # The page only lists roles it can take applications for, so the preview
    # does the same: the reader returns closed roles as well (their own pages
    # report their status), and they are dropped here. The list stays capped
    # because an over-long payload is discarded entirely, which would lose the
    # links (an over-limit embed is dropped in full).
    openings = [
        opening for opening in (database.get_team_openings(_APPLICATION_READ_LIMIT) or [])
        if opening.get("open")
    ][:_APPLICATION_LIST_LIMIT]
    entries = []
    for opening in openings:
        title = str(opening.get("title") or "").strip()
        if not title or not opening.get("id"):
            continue
        summary = str(opening.get("description") or "").strip()
        if len(summary) > 90:
            summary = summary[:87].rstrip() + "…"
        link = f"{social_preview.SITE_URL}/team/apply/{opening['id']}"
        entry = f"**[{title}]({link})**"
        if summary:
            entry = f"{entry}\n-# {summary}"
        entries.append(entry)

    lines = []
    if entries:
        count = len(entries)
        lines.append(f"-# {count} open role{'s' if count != 1 else ''} · apply with your Discord account")
    # No title: the page's own copy is the right title for it, and the embed
    # only needs to describe what the page lists.
    return {
        "kind": "applications",
        "template": _TEAM_APPLY_PAGE,
        "description": (
            "Pick a role below to open its application."
            if entries
            else "No staff roles are open right now — check back soon, or say hi in the support server."
        ),
        "name": "Join the Niko team",
        "section": "Staff applications",
        # Niko's own face, like every other page it fronts: a list of its staff
        # roles should look like Niko, not like the site's generic icon.
        "thumbnail": _bot_avatar_url(),
        "accent": None,
        "lines": lines,
        "list": entries,
    }


def _team_application_embed_context(opening_id: str) -> dict | None:
    """One staff role's application page: what it is, and whether it is hiring.

    A role that has stopped taking applications still has a page — old links
    are shared around — so it is described with its status instead of falling
    back to the section's generic copy. Everything here is already public: the
    applications page lists each role's title and description.
    """
    if not opening_id:
        return None
    openings = database.get_team_openings(_APPLICATION_READ_LIMIT, opening_id=opening_id)
    opening = next(
        (item for item in (openings or []) if str(item.get("id")) == opening_id),
        None,
    )
    if not opening:
        return None
    title = str(opening.get("title") or "Niko team")
    accepting = bool(opening.get("open"))
    description = str(opening.get("description") or "").strip()
    if len(description) > 200:
        description = description[:197].rstrip() + "…"
    if not description:
        description = f"Applications for {title} on the Niko team."
    status = (
        "-# Open now · accepting new applications"
        if accepting
        else "-# Closed right now · not accepting new applications"
    )
    return {
        "kind": "application",
        "template": _TEAM_APPLY_PAGE,
        "title": f"{title} — Niko staff application",
        "description": description,
        "name": title,
        "section": "Niko staff application" if accepting else "Niko staff application · closed",
        "thumbnail": _bot_avatar_url(),
        "accent": None,
        "lines": [status],
    }


def _partnership_media() -> list[str]:
    """Images the ad can show, keeping only the ones this build actually has.

    A media gallery pointing at a missing file invalidates the whole payload, so
    a build without the generated card falls back to the icon that always ships.
    """
    return [
        f"{social_preview.SITE_URL}/{relative}"
        for relative in (PARTNERSHIP_OG_CARD, PARTNERSHIP_ICON)
        if os.path.isfile(os.path.join(config.WEB_DIST_DIR, relative))
    ]


def _partnership_og_image() -> str | None:
    """The generated ad card, and only once the build has written it.

    A link without a card image still previews; pointing ``og:image`` at a file
    that is not there, and claiming a 1200×630 size for the square icon, does not.
    """
    if not os.path.isfile(os.path.join(config.WEB_DIST_DIR, PARTNERSHIP_OG_CARD)):
        return None
    return f"{social_preview.SITE_URL}/{PARTNERSHIP_OG_CARD}"


def _partnership_embed_context() -> dict:
    """The partnership ad, in full.

    This is the copy partners paste into their own servers: one link that
    Discord renders as a Components V2 layout, so it can carry separators, a
    gallery and buttons — and so it reads as a recommendation from that server's
    own partnership channel rather than as a bot or webhook posting.
    """
    media = _partnership_media()
    description = (
        "Niko keeps the busywork off your staff: AutoMod that explains itself, "
        "private tickets, leveling, music, games and a full economy, all "
        "configured from a dashboard instead of a wall of commands."
    )
    return {
        "kind": social_preview.PARTNERSHIP_KIND,
        "template": social_preview.PARTNERSHIP_PATH,
        "title": "Partner with Niko — Niko partnerships",
        "description": description,
        "name": "Partner with Niko",
        "section": "A friendly bot for communities that care",
        "thumbnail": _bot_avatar_url(),
        "image": _partnership_og_image(),
        "sections": [
            ("What your members get", [
                "**Moderation that stays calm** — warnings, timeouts and AutoMod answers, explained in plain language",
                "**Reasons to stay** — leveling, an economy, games, music and a weekly lottery",
                "**Help without a queue** — private tickets, a public help forum and an AI assistant",
            ]),
            ("What partners get", [
                "A permanent listing with your own description in our partners channel",
                "A shout-out for your community from the partnerships team",
                "A direct line to us when something needs a human",
            ]),
            ("What we look for", [
                "An active, well-moderated community with a clear purpose",
                "Advertisements people opt into — no mass DMs, no invite bait",
                "Nothing built around scams, hate, or NSFW content",
            ]),
        ],
        "media": media,
    }


def _social_context(route: str) -> dict | None:
    """The subject of a page, when it is not Niko itself (cached briefly).

    Resolving a subject can touch the bot loop or the roster, so the result is
    cached: link previews are not latency sensitive, and Discord re-crawls the
    same URLs.
    """
    key = social_preview.route_key(route)
    now = time.time()
    cached = _social_context_cache.get(key)
    if cached is not None and now - cached[0] < _SOCIAL_CONTEXT_TTL:
        return cached[1]
    context = None
    if key == social_preview.PARTNERSHIP_PATH:
        # The ad is the same for everybody, so it needs no subject lookup.
        context = _partnership_embed_context()
    elif key == _TEAM_APPLY_PAGE:
        context = _team_apply_embed_context()
    elif (match := _TEAM_APPLICATION_PAGE.match(key)):
        # An unknown role borrows the applications page's copy rather than
        # describing a role that does not exist.
        context = _team_application_embed_context(match.group(1)) or {"template": _TEAM_APPLY_PAGE}
    elif (match := _GUILD_PAGE.match(key)):
        # No server data (the bot is not in it, or it is not reachable) still
        # borrows the leaderboard section's copy.
        context = _guild_embed_context(match.group(1)) or {"template": "/levels"}
    else:
        match = _STAFF_PAGE.match(key)
        if match:
            context = _staff_embed_context(match.group(1)) or {"template": "/team"}
    if len(_social_context_cache) >= _SOCIAL_CONTEXT_CACHE_LIMIT:
        _social_context_cache.clear()
    _social_context_cache[key] = (now, context)
    return context


def _social_invite_url() -> str:
    """The invite for the embed's Add Niko button.

    Built the same way /api/config builds it, from this process's own
    application id, so the button lands on the same OAuth screen the site's own
    Add Niko button uses.
    """
    return "https://discord.com/oauth2/authorize?" + urlencode({
        "client_id": config.DISCORD_CLIENT_ID,
        "permissions": "8",
        "scope": "bot applications.commands",
    })


def render_site_shell(path: str = None):
    """Serve the React shell with this route's social metadata rendered in.

    One shell is served for every route and decorated here, per request: the
    per-page HTML, the invite link and the live counts used to be baked into the
    build, so they only changed on a deploy. The page copy comes from the build
    manifest (src/webapp/social_preview.py), everything request-dependent is
    filled in now.
    """
    route = request.path if path is None else path
    shell_path = os.path.join(config.WEB_DIST_DIR, "index.html")
    try:
        with open(shell_path, "r", encoding="utf-8") as handle:
            shell = handle.read()
    except OSError:
        return jsonify({"error": "The site build is unavailable."}), 503
    body = social_preview.inject(
        shell,
        config.WEB_DIST_DIR,
        route,
        _social_invite_url(),
        stats_provider=_social_stats,
        context_provider=_social_context,
    )
    response = Response(body, mimetype="text/html")
    # The served head depends on the request (and, on landing pages, on live
    # counts), so it is revalidated rather than cached blind.
    response.headers["Cache-Control"] = "no-cache"
    return response
