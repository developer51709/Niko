"""
AI error views — shared CV2 LayoutView builders for OpenAI API error responses.

Sentinel format returned by generate_reply_openai:
  "ai_error:rate_limit:<seconds>"
  "ai_error:safety"
  "ai_error:generic"

Use parse_ai_error() to decode and build_ai_error_view() to render.
"""
import discord


# Accent colours
_YELLOW = discord.Colour(0xfee75c)   # rate limit
_RED    = discord.Colour(0xed4245)   # safety / content filter
_GREY   = discord.Colour(0x747f8d)   # generic / unknown


def parse_ai_error(sentinel: str) -> tuple[str, int]:
    """
    Parse an ai_error sentinel string.
    Returns (kind, cooldown_seconds).
    kind is one of: "rate_limit", "safety", "generic".
    """
    if not isinstance(sentinel, str) or not sentinel.startswith("ai_error:"):
        return ("generic", 0)
    parts = sentinel.split(":", 2)
    kind = parts[1] if len(parts) > 1 else "generic"
    cooldown = 0
    if kind == "rate_limit" and len(parts) > 2:
        try:
            cooldown = int(parts[2])
        except ValueError:
            cooldown = 30
    return (kind, cooldown)


def build_ai_error_view(kind: str, cooldown: int = 30) -> discord.ui.LayoutView:
    """
    Build a CV2 LayoutView for the given AI error kind.

    kind: "rate_limit" | "safety" | "generic"
    cooldown: seconds remaining (used for rate_limit messages)
    """
    if kind == "rate_limit":
        text = (
            "### ☕ a little overwhelmed right now~\n"
            f"i hit my request limit — give me about **{cooldown}s** to breathe and try again!\n"
            "-# *the api returned a rate-limit error (429). your message was not sent to the model.*"
        )
        colour = _YELLOW

    elif kind == "safety":
        text = (
            "### 🚫 i can't respond to that one ☕\n"
            "my content policy flagged that message — let's keep things cozy!\n"
            "-# *the request was blocked by the ai provider's safety or content filter.*"
        )
        colour = _RED

    else:
        text = (
            "### ☕ something went wrong~\n"
            "i ran into an unexpected error — try again in a moment!\n"
            "-# *an error occurred while contacting the ai. check the bot logs for details.*"
        )
        colour = _GREY

    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        accent_colour=colour,
    ))
    return view

