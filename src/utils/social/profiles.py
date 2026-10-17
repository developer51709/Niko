"""Public social-profile lookups for the team profile cards.

Each fetcher returns the same small, presentation-ready shape so the React
team page can render every platform with one card component::

    {
        "platform": "github",
        "display_name": "Linus Torvalds",
        "handle": "torvalds",
        "url": "https://github.com/torvalds",
        "avatar_url": "https://…",
        "bio": "…",
        "stats": [{"label": "Repos", "value": "12"}, …],
        "status": None,          # e.g. "Live · 12,345 viewers" on Twitch
    }

Where a platform's own API needs paid access or credentials, an anonymous
public endpoint is used instead:

* **Twitch** uses app (client-credentials) access from the environment, because
  the notifier needs the same credentials for real, so they are not decoration.
* **X/Twitter** requires a paid API key for profiles, so the card falls back to
  the public FixTweet/VxTwitter mirrors (and then to a plain link card).
* **Reddit** is free but aggressively blocks datacenter IPs on its JSON API, so
  the user/subreddit Atom feeds are used as the fallback.
* **Bluesky**, **YouTube** and **GitHub** are read from their public,
  credential-free endpoints.

Network access is synchronous: the Flask layer calls these directly and the
notifier wraps Twitch in ``asyncio.to_thread``.
"""

from __future__ import annotations

import re
import threading
import time
from collections import deque
from urllib.parse import quote, urlparse

import requests

from utils.social import twitch

_TIMEOUT = 10
_USER_AGENT = "Mozilla/5.0 (compatible; NikoBot/1.0)"
JSON_HEADERS = {"User-Agent": _USER_AGENT, "Accept": "application/json"}

# Cards are refreshed on a timer, so a short TTL removes almost all upstream
# traffic while still showing a changed avatar or follower count quickly.
_CACHE_TTL = 300.0
_FAILURE_TTL = 60.0
_MAX_CALLS_PER_MINUTE = 60

_CACHE_LOCK = threading.Lock()
_CACHE: dict[tuple[str, str], tuple[float, dict | None]] = {}
_CALLS: deque[float] = deque()

SUPPORTED_PLATFORMS = ("github", "bluesky", "twitch", "youtube", "reddit", "x")

_HOSTS = {
    "github": {"github.com", "www.github.com"},
    "bluesky": {"bsky.app", "www.bsky.app", "staging.bsky.app"},
    "twitch": {"twitch.tv", "www.twitch.tv", "m.twitch.tv"},
    "youtube": {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"},
    "reddit": {"reddit.com", "www.reddit.com", "old.reddit.com", "np.reddit.com"},
    "x": {"x.com", "www.x.com", "twitter.com", "www.twitter.com", "mobile.twitter.com"},
}


class ProfileLookupError(Exception):
    """Raised when a link cannot be turned into a profile card."""


# ── Shared helpers ───────────────────────────────────────────────────────────


def _compact(value: int | float | None) -> str:
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        number = 0
    return f"{number:,}"


def _get_json(url: str, *, headers: dict | None = None) -> dict | None:
    try:
        response = requests.get(url, headers={**JSON_HEADERS, **(headers or {})}, timeout=_TIMEOUT)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None


def _get_text(url: str) -> str | None:
    # HTML pages are requested with a browser-style Accept header; some sites
    # answer a JSON-only Accept with a stripped or error page instead.
    try:
        response = requests.get(
            url,
            headers={"User-Agent": _USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
            timeout=_TIMEOUT,
        )
        if response.status_code != 200:
            return None
        return response.text
    except Exception:
        return None


def _throttled() -> bool:
    """Token-bucket guard so a burst of public traffic cannot hammer APIs."""
    now = time.monotonic()
    with _CACHE_LOCK:
        while _CALLS and _CALLS[0] < now - 60:
            _CALLS.popleft()
        if len(_CALLS) >= _MAX_CALLS_PER_MINUTE:
            return True
        _CALLS.append(now)
        return False


def _cached(key: tuple[str, str], loader):
    now = time.time()
    with _CACHE_LOCK:
        entry = _CACHE.get(key)
    if entry and now < entry[0]:
        return entry[1]

    payload = None
    if not _throttled():
        try:
            payload = loader()
        except Exception:
            payload = None

    ttl = _CACHE_TTL if payload else _FAILURE_TTL
    with _CACHE_LOCK:
        _CACHE[key] = (now + ttl, payload)
    return payload


def _card(platform: str, **fields) -> dict:
    base = {
        "platform": platform,
        "display_name": "",
        "handle": "",
        "url": "",
        "avatar_url": None,
        "bio": None,
        "stats": [],
        "status": None,
    }
    base.update({key: value for key, value in fields.items() if value is not None})
    return base


def parse_link(link_type: str, url: str) -> tuple[str, str]:
    """Validate a profile link and return ``(platform, identifier)``.

    Only the platform's own host and a recognised profile path are accepted, so
    an arbitrary URL can never reach an upstream request.
    """
    platform = (link_type or "").strip().lower()
    if platform not in SUPPORTED_PLATFORMS:
        raise ProfileLookupError("Unsupported platform.")
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ProfileLookupError("Enter a valid profile URL.")
    host = parsed.hostname or ""
    # Bluesky handles are domains, so a staff member's own handle URL (for
    # example https://name.bsky.social) is a valid profile link even though it
    # is not on bsky.app. The handle is only ever sent as a query parameter to
    # the fixed public Bluesky API, so no other host is contacted.
    if platform != "bluesky" and host not in _HOSTS[platform]:
        raise ProfileLookupError("That link does not belong to the selected platform.")
    segments = [segment for segment in parsed.path.split("/") if segment]

    if platform == "github":
        if not segments or not re.fullmatch(r"[A-Za-z0-9-]{1,39}", segments[0]):
            raise ProfileLookupError("That GitHub URL has no username.")
        return platform, segments[0]

    if platform == "bluesky":
        if host in _HOSTS["bluesky"]:
            if len(segments) < 2 or segments[0] != "profile":
                raise ProfileLookupError("That Bluesky URL has no handle.")
            handle = segments[1].lstrip("@")
        else:
            handle = host[4:] if host.startswith("www.") else host
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,253}", handle):
            raise ProfileLookupError("That Bluesky handle is not valid.")
        return platform, handle

    if platform == "twitch":
        if not segments:
            raise ProfileLookupError("That Twitch URL has no channel.")
        login = twitch.normalize_login(segments[0])
        if not login:
            raise ProfileLookupError("That Twitch channel name is not valid.")
        return platform, login

    if platform == "youtube":
        if host.endswith("youtu.be"):
            raise ProfileLookupError("Use a channel URL such as youtube.com/@handle.")
        if not segments:
            raise ProfileLookupError("That YouTube URL has no channel.")
        if segments[0] == "channel" and len(segments) > 1 and re.fullmatch(r"UC[A-Za-z0-9_-]{22}", segments[1]):
            return platform, segments[1]
        if segments[0].startswith("@"):
            return platform, segments[0]
        if segments[0] in {"c", "user"} and len(segments) > 1:
            return platform, segments[1]
        # Legacy /custom or vanity paths such as youtube.com/MrBeast.
        return platform, segments[0]

    if platform == "reddit":
        if not segments:
            raise ProfileLookupError("That Reddit URL has no profile.")
        kind = segments[0].lower()
        if kind in {"user", "u"} and len(segments) > 1:
            name = segments[1].lstrip("@")
            return "reddit", f"u/{name}" if re.fullmatch(r"[\w-]{3,20}", name) else ""
        if kind == "r" and len(segments) > 1 and re.fullmatch(r"[\w-]{2,25}", segments[1]):
            return "reddit", f"r/{segments[1]}"
        raise ProfileLookupError("Only Reddit user and subreddit links are supported.")

    # X/Twitter
    if not segments or not re.fullmatch(r"[A-Za-z0-9_]{1,15}", segments[0]):
        raise ProfileLookupError("That X URL has no username.")
    return platform, segments[0]


# ── Platform fetchers ────────────────────────────────────────────────────────


def _github(login: str) -> dict | None:
    data = _get_json(
        f"https://api.github.com/users/{login}",
        headers={"Accept": "application/vnd.github+json"},
    )
    if not data or not data.get("login"):
        return None
    return _card(
        "github",
        display_name=data.get("name") or data["login"],
        handle=data["login"],
        url=data.get("html_url") or f"https://github.com/{login}",
        avatar_url=data.get("avatar_url"),
        bio=data.get("bio"),
        stats=[
            {"label": "Repos", "value": _compact(data.get("public_repos"))},
            {"label": "Followers", "value": _compact(data.get("followers"))},
            {"label": "Following", "value": _compact(data.get("following"))},
        ],
        status=data.get("location") or None,
    )


def _bluesky(handle: str) -> dict | None:
    data = _get_json(
        "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile"
        f"?actor={quote(handle)}"
    )
    if not data or not data.get("handle"):
        return None
    return _card(
        "bluesky",
        display_name=data.get("displayName") or data["handle"],
        handle=data["handle"],
        url=f"https://bsky.app/profile/{data['handle']}",
        avatar_url=data.get("avatar"),
        bio=data.get("description"),
        stats=[
            {"label": "Followers", "value": _compact(data.get("followersCount"))},
            {"label": "Following", "value": _compact(data.get("followsCount"))},
            {"label": "Posts", "value": _compact(data.get("postsCount"))},
        ],
    )


def _twitch(login: str) -> dict | None:
    channel = twitch.fetch_channel(login)
    if not channel:
        return None
    status = None
    stream = twitch.fetch_live_stream(login)
    # Helix's channel ``view_count`` is deprecated and reports 0, so the card
    # shows the live viewer count instead and never a meaningless total.
    stats = []
    if stream:
        status = f"Live now · {stream.get('game_name') or 'Twitch'}"
        stats.append({"label": "Viewers", "value": _compact(stream.get("viewer_count"))})
    created = str(channel.get("created_at") or "")[:4]
    if created.isdigit():
        stats.append({"label": "Created", "value": created})
    handle = channel.get("login") or login
    return _card(
        "twitch",
        display_name=channel.get("display_name") or handle,
        handle=handle,
        url=f"https://www.twitch.tv/{handle}",
        avatar_url=channel.get("profile_image_url"),
        bio=channel.get("description"),
        stats=stats,
        status=status,
    )


def _youtube_paths(identifier: str) -> list[str]:
    """Candidate channel paths for a @handle, legacy vanity name, or id."""
    if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", identifier):
        return [f"channel/{identifier}"]
    if identifier.startswith("@"):
        return [identifier]
    return [f"@{identifier}", f"c/{identifier}", f"user/{identifier}"]


def _youtube(identifier: str) -> dict | None:
    """Read a channel from its About panel.

    YouTube's Data API needs an API key, so the public About page is scraped
    instead: it exposes the channel's own subscriber/video totals in a single
    ``aboutChannelViewModel`` blob, unlike the channel home page whose numbers
    belong to featured channels.
    """
    html = None
    canonical = None
    for path in _youtube_paths(identifier):
        text = _get_text(f"https://www.youtube.com/{quote(path, safe='/@')}/about")
        if not text:
            continue
        if not re.search(r'"subscriberCountText":"[^"]+"', text) and not re.search(r'<meta property="og:title"', text):
            continue
        html = text
        match = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        canonical = match.group(1) if match else None
        break
    if not html:
        return None

    def meta(name: str) -> str | None:
        match = re.search(rf'<meta property="{name}" content="([^"]+)"', html)
        return match.group(1) if match else None

    def field(name: str) -> str | None:
        match = re.search(rf'"{name}":"([^"]+)"', html)
        return match.group(1) if match else None

    def count(name: str) -> str | None:
        value = field(name)
        return value.split(" ")[0] if value else None

    display = meta("og:title")
    if not display:
        return None
    stats = [
        {"label": label, "value": value}
        for label, value in (("Subscribers", count("subscriberCountText")), ("Videos", count("videoCountText")))
        if value
    ]
    return _card(
        "youtube",
        display_name=display,
        handle="" if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", identifier) else identifier.lstrip("@"),
        url=canonical or f"https://www.youtube.com/{quote(_youtube_paths(identifier)[0], safe='/@')}",
        avatar_url=meta("og:image"),
        stats=stats,
    )


def _reddit(identifier: str) -> dict | None:
    kind, name = identifier.split("/", 1)
    if kind == "r":
        feed = _get_text(f"https://www.reddit.com/r/{name}/new/.rss?limit=1")
        if not feed or "<feed" not in feed:
            feed = _get_text(f"https://old.reddit.com/r/{name}/new/.rss?limit=1")
        if not feed or "<feed" not in feed:
            return None
        title = re.search(r"<title>(.*?)</title>", feed, re.DOTALL)
        display = title.group(1).strip() if title else f"r/{name}"
        return _card(
            "reddit",
            display_name=display,
            handle=f"r/{name}",
            url=f"https://www.reddit.com/r/{name}/",
        )

    headers = {"User-Agent": "nikobot/1.0 (Discord bot; +https://nikobot.dev)"}
    about = _get_json(f"https://www.reddit.com/user/{name}/about.json", headers=headers)
    data = (about or {}).get("data") if isinstance(about, dict) else None
    if isinstance(data, dict) and data.get("name"):
        icon = data.get("icon_img") or data.get("snoovatar_img")
        return _card(
            "reddit",
            display_name=data.get("subreddit", {}).get("title") or f"u/{data['name']}",
            handle=f"u/{data['name']}",
            url=f"https://www.reddit.com/user/{data['name']}/",
            avatar_url=(icon or "").split("?")[0] or None,
            bio=data.get("subreddit", {}).get("public_description") or None,
            stats=[
                {"label": "Karma", "value": _compact(data.get("total_karma"))},
                {"label": "Posts", "value": _compact(data.get("link_karma"))},
                {"label": "Comments", "value": _compact(data.get("comment_karma"))},
            ],
        )

    # Reddit blocks its JSON API for many datacenter IPs; the Atom feed still
    # identifies the account so the card degrades instead of disappearing.
    for feed_url in (
        f"https://www.reddit.com/user/{name}/.rss",
        f"https://old.reddit.com/user/{name}/.rss",
    ):
        feed = _get_text(feed_url)
        if feed and "<feed" in feed:
            return _card(
                "reddit",
                display_name=f"u/{name}",
                handle=f"u/{name}",
                url=f"https://www.reddit.com/user/{name}/",
            )
    return None


def _x(login: str) -> dict | None:
    """X profile via the public FixTweet/VxTwitter mirrors (no paid API key)."""
    data = _get_json(f"https://api.fxtwitter.com/{login}")
    user = (data or {}).get("user") if isinstance(data, dict) else None
    if isinstance(user, dict) and (user.get("screen_name") or user.get("name")):
        return _card(
            "x",
            display_name=user.get("name") or user.get("screen_name"),
            handle=user.get("screen_name") or login,
            url=user.get("url") or f"https://x.com/{login}",
            avatar_url=user.get("avatar_url"),
            bio=user.get("description") or None,
            stats=[
                {"label": "Followers", "value": _compact(user.get("followers"))},
                {"label": "Following", "value": _compact(user.get("following"))},
                {"label": "Posts", "value": _compact(user.get("tweets"))},
            ],
            status="Verified" if (user.get("verification") or {}).get("verified") else None,
        )

    fallback = _get_json(f"https://api.vxtwitter.com/{login}")
    if isinstance(fallback, dict) and (fallback.get("screen_name") or fallback.get("name")):
        return _card(
            "x",
            display_name=fallback.get("name") or fallback.get("screen_name"),
            handle=fallback.get("screen_name") or login,
            url=f"https://x.com/{fallback.get('screen_name') or login}",
            avatar_url=fallback.get("profile_image_url"),
            bio=fallback.get("description") or None,
            stats=[
                {"label": "Followers", "value": _compact(fallback.get("followers_count"))},
                {"label": "Following", "value": _compact(fallback.get("following_count"))},
                {"label": "Posts", "value": _compact(fallback.get("tweet_count"))},
            ],
        )
    return None


_LOADERS = {
    "github": _github,
    "bluesky": _bluesky,
    "twitch": _twitch,
    "youtube": _youtube,
    "reddit": _reddit,
    "x": _x,
}


def fetch_public_profile(link_type: str, url: str) -> dict | None:
    """Fetch a renderable profile card for a staff member's public link."""
    platform, identifier = parse_link(link_type, url)
    if not identifier:
        raise ProfileLookupError("That profile URL is not valid.")
    return _cached((platform, identifier), lambda: _LOADERS[platform](identifier))
