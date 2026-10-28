"""
AI error views — shared CV2 LayoutView builders for AI failure responses.

Sentinel format returned by the reply pipeline:
  "ai_error:rate_limit:<seconds>"
  "ai_error:safety"
  "ai_error:not_configured"
  "ai_error:budget"
  "ai_error:generic"

Use parse_ai_error() to decode and build_ai_error_view() to render.
"""
import discord

from config.emojis import get_emoji


# Accent colours: error cards keep a semantic accent, unlike normal responses.
_YELLOW = discord.Colour(0xfee75c)   # rate limit / budget
_RED    = discord.Colour(0xed4245)   # safety / content filter
_GREY   = discord.Colour(0x747f8d)   # generic / unknown

_KNOWN_KINDS = {"rate_limit", "safety", "not_configured", "budget", "generic"}


def parse_ai_error(sentinel: str) -> tuple[str, int]:
    """
    Parse an ai_error sentinel string.
    Returns (kind, cooldown_seconds).
    """
    if not isinstance(sentinel, str) or not sentinel.startswith("ai_error:"):
        return ("generic", 0)
    parts = sentinel.split(":", 2)
    kind = parts[1] if len(parts) > 1 else "generic"
    if kind not in _KNOWN_KINDS:
        kind = "generic"
    cooldown = 0
    if kind == "rate_limit" and len(parts) > 2:
        try:
            cooldown = max(int(parts[2]), 1)
        except ValueError:
            cooldown = 30
    return (kind, cooldown)


def _icon(name: str, fallback: str) -> str:
    return get_emoji(name) or fallback


def build_ai_error_view(kind: str, cooldown: int = 30) -> discord.ui.LayoutView:
    """Build a CV2 LayoutView for the given AI error kind."""
    if kind == "rate_limit":
        text = (
            f"### {_icon('cooldown', '⏳')} a little overwhelmed right now~\n"
            f"i hit my request limit — give me about **{cooldown}s** to breathe and try again!\n"
            "-# *the api returned a rate-limit error (429). your message was not sent to the model.*"
        )
        colour = _YELLOW

    elif kind == "budget":
        text = (
            f"### {_icon('cooldown', '⏳')} this server reached its AI limit\n"
            "niko has answered as much as this server's hourly budget allows — the limit resets soon.\n"
            "-# *an admin can raise `AI_GUILD_HOURLY_REQUESTS` if this happens often.*"
        )
        colour = _YELLOW

    elif kind == "not_configured":
        text = (
            f"### {_icon('danger', '⚠️')} AI isn't configured\n"
            "my language model key is missing, so i can't answer right now.\n"
            "-# *a bot owner needs to set the `GROQ_API_KEY` secret.*"
        )
        colour = _GREY

    elif kind == "safety":
        text = (
            f"### {_icon('cross', '🚫')} i can't respond to that one ☕\n"
            "my content policy flagged that message — let's keep things cozy!\n"
            "-# *the request was blocked by the ai provider's safety or content filter.*"
        )
        colour = _RED

    else:
        text = (
            f"### {_icon('danger', '⚠️')} something went wrong~\n"
            "i ran into an unexpected error — try again in a moment!\n"
            "-# *an error occurred while contacting the ai. the bot logs have the details.*"
        )
        colour = _GREY

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        accent_colour=colour,
    ))
    return view
