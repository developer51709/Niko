"""Shared Components V2 cooldown notice used by the gambling commands.

A pre-rendered "2m 15s" string is already stale when it lands, and it reads
differently for everyone. Discord's dynamic timestamp renders in the viewer's
own locale and counts down by itself, so one notice stays accurate for the
whole cooldown.
"""

import discord

# Same brand accent the economy views use.
DEFAULT_ACCENT = discord.Colour(0xC8A882)


def cooldown_ready_at(last_used, cooldown) -> int:
    """Unix timestamp at which ``cooldown`` seconds after ``last_used`` expire."""
    return int(float(last_used or 0) + float(cooldown))


def cooldown_view(
    action: str,
    ready_at: int,
    *,
    title: str = "⏳ On cooldown",
    note: str | None = None,
    accent: discord.Colour = DEFAULT_ACCENT,
    template: str | None = None,
) -> discord.ui.LayoutView:
    """Build the cooldown notice telling the member when they can *action* again.

    ``action`` completes the sentence "You can … again", e.g. "spin the slots".
    ``template`` replaces that English sentence with a translated one that has
    ``{action}`` and ``{timestamp}`` placeholders.
    """
    timestamp = int(ready_at)
    lines = [note] if note else []
    if template:
        lines.append(template.format(action=action, timestamp=timestamp))
    else:
        lines.append(f"You can {action} again <t:{timestamp}:R>.")
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="\n".join(lines)),
        accent_colour=accent,
    ))
    return view
