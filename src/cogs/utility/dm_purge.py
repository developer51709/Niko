"""``.dmpurge`` — clear Niko's own messages out of a direct message.

The command is deliberately private. It is a prefix-only command, it is marked
``hidden`` (the help cog refuses to look up hidden commands by name), it belongs
to no help category, and the startup registry skips hidden commands so it never
reaches ``data/commands.json`` or the public commands page.

Discord has no bulk-delete endpoint outside a guild — bulk delete needs
``MANAGE_MESSAGES``, which does not exist in a DM — so every message is deleted
on its own and paced with the shared DM purge limiter. Only messages Niko sent
are removed; the other side of the conversation is never touched.
"""

from __future__ import annotations

import asyncio

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.ratelimit import dm_purge_limiter

# How many deletions happen between progress edits of the status message. A
# status edit is a second request on the same channel, so the progress panel is
# refreshed in batches rather than after every single delete.
PROGRESS_STEP = 25

# How long the confirm prompt waits before it gives up and deletes nothing.
CONFIRM_TIMEOUT = 60.0


def panel(text: str, accent: discord.Colour | None = None) -> discord.ui.LayoutView:
    """Wrap plain markdown in a components-v2 panel, like the rest of the bot."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        accent_colour=accent or discord.Colour(0xC8A882),
    ))
    return view


async def _replace(message: discord.Message, text: str) -> None:
    """Replace a status panel's contents, tolerating a Discord hiccup."""
    try:
        await message.edit(view=panel(text))
    except discord.HTTPException:
        pass


async def iter_bot_messages(channel, *, bot_id: int, skip_ids=()):
    """Yield Niko's own messages in ``channel``, newest first."""
    skip = {int(message_id) for message_id in skip_ids}
    async for message in channel.history(limit=None, oldest_first=False):
        try:
            if int(getattr(message, "id", 0)) in skip:
                continue
        except (TypeError, ValueError):
            continue
        author_id = getattr(getattr(message, "author", None), "id", None)
        if author_id is None:
            continue
        try:
            if int(author_id) != int(bot_id):
                continue
        except (TypeError, ValueError):
            continue
        yield message


async def count_bot_messages(channel, *, bot_id: int, skip_ids=(), limit: int | None = None) -> int:
    """Count what a purge would delete, without deleting anything.

    ``limit`` stops the count early so ``.dmpurge 25`` in a full inbox does not
    walk the whole conversation before it can offer its confirmation.
    """
    total = 0
    async for _ in iter_bot_messages(channel, bot_id=bot_id, skip_ids=skip_ids):
        total += 1
        if limit is not None and total >= limit:
            break
    return total


async def purge_bot_messages(
    channel,
    *,
    bot_id: int,
    skip_ids=(),
    limit: int | None = None,
    on_progress=None,
) -> tuple[int, int]:
    """Delete Niko's own messages in ``channel`` and report the outcome.

    Returns ``(deleted, failed)``. A message that vanished between the scan and
    the delete is not a failure; anything else Discord refuses is counted, so a
    partial purge is never reported as a clean one.
    """
    deleted = 0
    failed = 0
    scanned = 0
    async for message in iter_bot_messages(channel, bot_id=bot_id, skip_ids=skip_ids):
        if limit is not None and scanned >= limit:
            break
        scanned += 1
        await dm_purge_limiter.acquire(channel.id)
        try:
            await message.delete()
        except discord.NotFound:
            pass
        except discord.HTTPException:
            failed += 1
        else:
            deleted += 1
        if on_progress is not None:
            await on_progress(deleted, failed)
    return deleted, failed


class PurgeConfirmView(discord.ui.LayoutView):
    """Confirm/cancel buttons for a DM purge, gated to the person who asked."""

    def __init__(self, count: int, *, invoker_id: int, timeout: float = CONFIRM_TIMEOUT):
        super().__init__(timeout=timeout)
        self.invoker_id = invoker_id
        self.confirmed: bool | None = None
        self._answered = asyncio.Event()

        self._confirm = discord.ui.Button(
            label="Delete them",
            style=discord.ButtonStyle.danger,
            emoji=get_emoji("trash"),
        )
        self._cancel = discord.ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji("cross"),
        )
        self._confirm.callback = self._on_confirm
        self._cancel.callback = self._on_cancel

        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('trash')} Purge this conversation?"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=(
                f"Niko will delete **{count}** message{'' if count == 1 else 's'} it sent here. "
                "Your own messages stay untouched, and deleted messages cannot be brought back."
            )),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="-# This prompt expires in 60 seconds."),
            discord.ui.ActionRow(self._confirm, self._cancel),
            accent_colour=discord.Colour.orange(),
        ))

    async def _gate(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.invoker_id:
            await interaction.response.send_message(
                "Only the person who ran `.dmpurge` can answer this prompt.",
            )
            return False
        return True

    def _disable(self) -> None:
        self._confirm.disabled = True
        self._cancel.disabled = True

    async def _on_confirm(self, interaction: discord.Interaction) -> None:
        if not await self._gate(interaction):
            return
        self.confirmed = True
        self._disable()
        try:
            await interaction.response.edit_message(view=self)
        except discord.HTTPException:
            pass
        self._answered.set()

    async def _on_cancel(self, interaction: discord.Interaction) -> None:
        if not await self._gate(interaction):
            return
        self.confirmed = False
        self._disable()
        try:
            await interaction.response.edit_message(
                view=panel(
                    f"### {get_emoji('cross')} Purge cancelled\nNothing was deleted.",
                    accent=discord.Colour.greyple(),
                ),
            )
        except discord.HTTPException:
            pass
        self._answered.set()

    async def on_timeout(self) -> None:
        if self.confirmed is None:
            self.confirmed = False
            self._answered.set()

    async def wait_for_response(self) -> bool:
        await self._answered.wait()
        return bool(self.confirmed)


class DMPurge(commands.Cog):
    """Direct-message housekeeping for Niko's own messages."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="dmpurge",
        hidden=True,
        help="Purge the messages Niko sent you in this DM.",
    )
    async def dmpurge(self, ctx: commands.Context, limit: int = None):
        """Delete Niko's own messages in this direct message."""
        # DMs only: a guild has real purge tooling and its own permissions, and
        # this command must never be a hidden way around them.
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("`.dmpurge` only works in a direct message with Niko.")
            return

        bot_id = getattr(getattr(self.bot, "user", None), "id", None)
        if bot_id is None:
            await ctx.send("Niko is still starting up — try again in a moment.")
            return
        if limit is not None and limit < 1:
            await ctx.send("Give a positive number of messages to purge, or leave it out to purge everything.")
            return

        status = await ctx.send(view=panel(
            f"### {get_emoji('scroll')} Scanning this conversation…\n"
            "Looking for messages Niko sent.",
        ))
        skip_ids = {status.id}
        total = await count_bot_messages(ctx.channel, bot_id=bot_id, skip_ids=skip_ids, limit=limit)
        if not total:
            await _replace(
                status,
                f"### {get_emoji('tick')} Nothing to purge\n"
                "Niko has not sent anything in this conversation.",
            )
            return

        planned = total if limit is None else min(total, limit)
        prompt = PurgeConfirmView(planned, invoker_id=ctx.author.id)
        try:
            await status.edit(view=prompt)
        except discord.HTTPException:
            # No visible prompt means nothing can be confirmed, and waiting out
            # the timeout would just look like a hang.
            await ctx.send("Niko could not show the confirmation prompt, so nothing was deleted.")
            return
        if not await prompt.wait_for_response():
            await _replace(
                status,
                f"### {get_emoji('cross')} Purge cancelled\nNothing was deleted.",
            )
            return

        async def on_progress(deleted: int, failed: int) -> None:
            if deleted % PROGRESS_STEP:
                return
            line = (
                f"### {get_emoji('loading')} Purging…\n"
                f"Deleted **{deleted}** of **{planned}**."
            )
            if failed:
                line += f"\nSkipped **{failed}** that Discord refused to delete."
            await _replace(status, line)

        deleted, failed = await purge_bot_messages(
            ctx.channel,
            bot_id=bot_id,
            skip_ids=skip_ids,
            limit=limit,
            on_progress=on_progress,
        )

        summary = [
            f"### {get_emoji('tick')} DM purge complete",
            f"Deleted **{deleted}** of **{planned}** message{'' if planned == 1 else 's'} from Niko.",
        ]
        if failed:
            summary.append(
                f"{get_emoji('danger')} **{failed}** message{'' if failed == 1 else 's'} "
                "could not be deleted — run `.dmpurge` again to retry."
            )
        remaining = max(0, planned - deleted - failed)
        if remaining:
            summary.append(f"-# {remaining} message{'' if remaining == 1 else 's'} left untouched.")
        await _replace(status, "\n".join(summary))


async def setup(bot: commands.Bot):
    await bot.add_cog(DMPurge(bot))
