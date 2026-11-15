"""Echo message info buttons, user reports, and staff report review.

The echo command sends a normal message plus a tiny persistent info button. The
button's custom id carries an opaque echo id, so it survives restarts without a
stored view. Staff reports live in the support server's message-reports channel
and carry their own persistent review buttons.
"""

from __future__ import annotations

import uuid
from typing import Any

import discord

from config import links
from config.emojis import get_emoji
from config.ids import SUPPORT_GUILD, is_owner_id
from cogs.staff.records import get_staff_role
from cogs.staff.support_server import get_support_ids
from utils import echo_reports as store
from utils import logging
from utils.moderation.manager import BlacklistManager
from utils.stateless_views import CallbackOnlyButton, CallbackOnlyLayoutView

ECHO_INFO_PREFIX = "echo:info:"
ECHO_REPORT_PREFIX = "echo:report:"
ECHO_CONFIRM_PREFIX = "echo:confirm:"
ECHO_CANCEL_PREFIX = "echo:cancel:"
ECHO_REVIEW_PREFIX = "echo:review:"
MAX_ECHO_LENGTH = 1950
_NO_MENTIONS = discord.AllowedMentions.none()

REPORT_GUIDELINES = (
    "**Reporting guidelines**\n"
    "Reports are reviewed by Niko staff and are confidential. Only report a message "
    "that you believe breaks Niko's policies — not one you simply disagree with.\n"
    "- Staff can see your report; other members cannot.\n"
    "- If staff confirm the report, the message is removed and the sender receives a warning.\n"
    "- Repeated warnings can lead to a temporary or permanent blacklist.\n"
    "- False or abusive reports may be ignored.\n"
    "Select **Confirm** to submit, or **Cancel** to return."
)


def _message_url(echo: dict[str, Any]) -> str:
    return (
        "https://discord.com/channels/"
        f"{int(echo['guild_id'])}/{int(echo['channel_id'])}/{int(echo['message_id'])}"
    )


def _user_ref(user_id: int) -> str:
    return f"<@{int(user_id)}> (`{int(user_id)}`)"


def _shorten(value: str, limit: int) -> str:
    text = str(value or "")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _info_view(echo: dict[str, Any]) -> CallbackOnlyLayoutView:
    content = _shorten(echo.get("content") or "*No content stored.*", 1800)
    removed = "-# This echoed message has already been removed.\n" if echo.get("removed_at") else ""
    truncated = "-# The message was shortened when it was echoed.\n" if echo.get("truncated") else ""
    view = CallbackOnlyLayoutView(timeout=None)
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(
            content=(
                f"**Sent by:** {_user_ref(echo['author_id'])}\n"
                f"**Message:** [Jump to message]({_message_url(echo)})\n"
                f"**Sent:** <t:{int(echo['created_at'])}:F>\n"
                f"{removed}{truncated}"
            )
        ),
        discord.ui.TextDisplay(content=f"**Content**\n>>> {content}"),
        discord.ui.ActionRow(
            CallbackOnlyButton(
                label="Report",
                emoji=get_emoji("warning"),
                style=discord.ButtonStyle.danger,
                custom_id=f"{ECHO_REPORT_PREFIX}{echo['echo_id']}",
            )
        ),
    ))
    return view


def _report_guidelines_view(echo_id: str) -> CallbackOnlyLayoutView:
    view = CallbackOnlyLayoutView(timeout=None)
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=REPORT_GUIDELINES),
        discord.ui.ActionRow(
            CallbackOnlyButton(
                label="Confirm",
                style=discord.ButtonStyle.danger,
                custom_id=f"{ECHO_CONFIRM_PREFIX}{echo_id}",
            ),
            CallbackOnlyButton(
                label="Cancel",
                style=discord.ButtonStyle.secondary,
                custom_id=f"{ECHO_CANCEL_PREFIX}{echo_id}",
            ),
        ),
    ))
    return view


def _report_result_view(content: str) -> CallbackOnlyLayoutView:
    view = CallbackOnlyLayoutView(timeout=None)
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=content)))
    return view


def _echo_button_view(echo_id: str) -> discord.ui.View:
    view = discord.ui.View(timeout=None)
    view.add_item(CallbackOnlyButton(
        emoji=get_emoji("question"),
        style=discord.ButtonStyle.secondary,
        custom_id=f"{ECHO_INFO_PREFIX}{echo_id}",
    ))
    return view


def _report_view(
    report: dict[str, Any],
    echo: dict[str, Any] | None,
    *,
    status: str | None = None,
    warning_count: int | None = None,
    blacklist: dict[str, Any] | None = None,
    deletion_note: str | None = None,
) -> CallbackOnlyLayoutView:
    state = status or report.get("status") or "pending"
    if echo is None:
        details = "-# The stored echo message details are no longer available."
    else:
        details = (
            f"**Sender:** {_user_ref(echo['author_id'])}\n"
            f"**Guild:** `{int(echo['guild_id'])}`\n"
            f"**Channel:** <#{int(echo['channel_id'])}> (`{int(echo['channel_id'])}`)\n"
            f"**Message:** [Jump to message]({_message_url(echo)})\n"
            f"**Sent:** <t:{int(echo['created_at'])}:F>\n"
            f"**Content**\n>>> {_shorten(echo.get('content') or '*No content stored.*', 1800)}"
        )

    if state == "pending":
        state_text = "**Status:** Awaiting staff review."
    elif state == "invalid":
        state_text = "**Status:** ❌ Invalid — no action taken."
    else:
        state_text = "**Status:** ✅ Valid — action taken."
        if deletion_note:
            state_text += f"\n{deletion_note}"
        if warning_count is not None:
            state_text += f"\n**Warnings:** {int(warning_count)}"
        if blacklist:
            if blacklist.get("permanent"):
                if blacklist.get("appealable", True):
                    state_text += "\n**Blacklist:** Permanent — appealable."
                else:
                    state_text += "\n**Blacklist:** Permanent — not appealable."
            elif blacklist.get("expires_at"):
                state_text += f"\n**Blacklist:** Until <t:{int(blacklist['expires_at'])}:F>."
            elif blacklist.get("blacklisted"):
                state_text += "\n**Blacklist:** Applied."

    view = CallbackOnlyLayoutView(timeout=None)
    children = [
        discord.ui.TextDisplay(content="# Message report"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"**Report:** `{report['report_id']}`\n"
                f"**Reporter:** {_user_ref(report['reporter_id'])}\n"
                f"**Reported:** <t:{int(report['created_at'])}:F>\n"
                f"{details}"
            )
        ),
        discord.ui.TextDisplay(content=state_text),
    ]
    if state == "pending":
        children.append(discord.ui.ActionRow(
            CallbackOnlyButton(
                label="Valid — remove & warn",
                style=discord.ButtonStyle.success,
                custom_id=f"{ECHO_REVIEW_PREFIX}valid:{report['report_id']}",
            ),
            CallbackOnlyButton(
                label="Invalid",
                style=discord.ButtonStyle.secondary,
                custom_id=f"{ECHO_REVIEW_PREFIX}invalid:{report['report_id']}",
            ),
        ))
    view.add_item(discord.ui.Container(*children, accent_colour=discord.Color.orange()))
    return view


def _dm_view(
    warning_count: int,
    blacklist: dict[str, Any] | None,
) -> discord.ui.LayoutView:
    lines = [
        "# Your echoed message was removed",
        "Your message was removed from Niko for violating our policies.",
        f"**Warning:** {int(warning_count)}",
    ]
    if blacklist and blacklist.get("blacklisted"):
        if blacklist.get("permanent"):
            if blacklist.get("appealable", True):
                lines.append(
                    "**Blacklist:** Permanent. You can appeal this decision at "
                    f"{links.WEBSITE}/appeals/blacklist."
                )
            else:
                lines.append(
                    "**Blacklist:** Permanent and not appealable. "
                    "Only the bot Owner or a Head Admin can remove it."
                )
        elif blacklist.get("expires_at"):
            lines.append(f"**Blacklist:** Until <t:{int(blacklist['expires_at'])}:F>.")
        else:
            lines.append("**Blacklist:** Applied.")
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content="\n".join(lines)),
        accent_colour=discord.Color.red(),
    ))
    return view


class EchoReporter:
    """Owns the echo message buttons and the staff report workflow."""

    def __init__(self, bot):
        self.bot = bot

    @property
    def pool(self):
        return getattr(self.bot, "cxn", None)

    async def send(self, ctx, message: str) -> None:
        if ctx.guild is None:
            await ctx.send("Echo can only be used in a server.", allowed_mentions=_NO_MENTIONS)
            return
        echo_id = uuid.uuid4().hex
        truncated = len(message) > MAX_ECHO_LENGTH
        content = message[:MAX_ECHO_LENGTH]
        if truncated:
            content = content.rstrip() + "…"
        sent = await ctx.send(
            content=content,
            view=_echo_button_view(echo_id),
            allowed_mentions=_NO_MENTIONS,
        )
        try:
            await store.record_echo_message(
                self.pool,
                echo_id=echo_id,
                message_id=sent.id,
                guild_id=ctx.guild.id,
                channel_id=ctx.channel.id,
                author_id=ctx.author.id,
                content=content,
                truncated=truncated,
            )
        except Exception as exc:
            logging.error("Echo", f"Could not store echoed message {sent.id}: {exc}")

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        custom_id = (interaction.data or {}).get("custom_id") or ""
        if custom_id.startswith(ECHO_INFO_PREFIX):
            await self._show_info(interaction, custom_id[len(ECHO_INFO_PREFIX):])
        elif custom_id.startswith(ECHO_REPORT_PREFIX):
            echo_id = custom_id[len(ECHO_REPORT_PREFIX):]
            await self._edit_ephemeral(interaction, view=_report_guidelines_view(echo_id))
        elif custom_id.startswith(ECHO_CONFIRM_PREFIX):
            await self._submit_report(interaction, custom_id[len(ECHO_CONFIRM_PREFIX):])
        elif custom_id.startswith(ECHO_CANCEL_PREFIX):
            await self._show_info(interaction, custom_id[len(ECHO_CANCEL_PREFIX):], edit=True)
        elif custom_id.startswith(ECHO_REVIEW_PREFIX):
            await self._review(interaction, custom_id[len(ECHO_REVIEW_PREFIX):])

    async def _show_info(
        self, interaction: discord.Interaction, echo_id: str, *, edit: bool = False,
    ) -> None:
        respond = self._edit_ephemeral if edit else self._reply
        if self.pool is None:
            return await respond(interaction, content="This message's details are temporarily unavailable.")
        try:
            echo = await store.get_echo_message(self.pool, echo_id)
            if echo is None:
                return await respond(interaction, content="This echoed message could not be found.")
            await respond(interaction, view=_info_view(echo))
        except Exception as exc:
            logging.error("Echo", f"Could not open echoed message {echo_id}: {exc}")
            await respond(interaction, content="This message's details could not be loaded.")

    async def _submit_report(self, interaction: discord.Interaction, echo_id: str) -> None:
        if self.pool is None:
            return await self._edit_ephemeral(
                interaction, view=_report_result_view("Reports are temporarily unavailable.")
            )
        try:
            echo = await store.get_echo_message(self.pool, echo_id)
            if echo is None:
                return await self._edit_ephemeral(
                    interaction, view=_report_result_view("This echoed message could not be found.")
                )
            channel = await self._reports_channel()
            if channel is None:
                return await self._edit_ephemeral(
                    interaction, view=_report_result_view("Message reports are not configured yet.")
                )
            report, created = await store.create_echo_report(
                self.pool,
                echo_id=echo_id,
                reporter_id=interaction.user.id,
                reason="Reported from the echoed message info panel.",
            )
            if not created:
                return await self._edit_ephemeral(
                    interaction, view=_report_result_view("You already have a pending report for this message.")
                )
            try:
                await channel.send(
                    view=_report_view(report, echo),
                    allowed_mentions=_NO_MENTIONS,
                )
            except Exception:
                await store.delete_echo_report(self.pool, report["report_id"])
                raise
            await self._edit_ephemeral(
                interaction, view=_report_result_view("Report submitted. Staff will review the message.")
            )
        except Exception as exc:
            logging.error("Echo", f"Could not submit report for {echo_id}: {exc}")
            await self._edit_ephemeral(
                interaction, view=_report_result_view("The report could not be submitted right now.")
            )

    async def _review(self, interaction: discord.Interaction, payload: str) -> None:
        status, _, report_id = payload.partition(":")
        if status not in {"valid", "invalid"} or not report_id:
            return await self._reply(interaction, "This report action is invalid.")
        if interaction.guild is None or interaction.guild.id != SUPPORT_GUILD:
            return await self._reply(interaction, "Only support staff can review reports.")
        if not await self._is_staff(interaction.user.id):
            return await self._reply(interaction, "Only support staff can review reports.")
        if self.pool is None:
            return await self._reply(interaction, "Reports are temporarily unavailable.")

        try:
            report = await store.get_echo_report(self.pool, report_id)
            if report is None or report.get("status") != "pending":
                return await self._reply(interaction, "This report has already been reviewed.")
            echo = await store.get_echo_message(self.pool, report["echo_id"])
            if status == "invalid":
                resolved = await store.resolve_echo_report(
                    self.pool, report_id, status="invalid", reviewer_id=interaction.user.id,
                )
                if resolved is None:
                    return await self._reply(interaction, "This report has already been reviewed.")
                await self._reply(interaction, "Report marked invalid; no action taken.")
                await self._edit_report(interaction, resolved, echo, status="invalid")
                return

            resolved = await store.resolve_echo_report(
                self.pool, report_id, status="valid", reviewer_id=interaction.user.id,
            )
            if resolved is None:
                return await self._reply(interaction, "This report has already been reviewed.")
            if echo is None:
                await self._reply(interaction, "Report marked valid, but the stored message is no longer available.")
                await self._edit_report(interaction, resolved, None, status="valid")
                return

            deletion_note = await self._remove_echo(echo)
            warning_count = await store.add_echo_warning(
                self.pool,
                user_id=echo["author_id"],
                report_id=report_id,
                reason="Echoed message removed after a valid staff report.",
            )
            blacklist = await BlacklistManager().apply_warning_blacklist(
                echo["author_id"],
                warning_count,
                reason="Echoed message removed after a valid staff report.",
            )
            await self._dm_sender(echo["author_id"], warning_count, blacklist)
            await self._reply(
                interaction,
                f"Report marked valid. Warning #{warning_count} recorded for <@{int(echo['author_id'])}>.",
            )
            await self._edit_report(
                interaction,
                resolved,
                echo,
                status="valid",
                warning_count=warning_count,
                blacklist=blacklist,
                deletion_note=deletion_note,
            )
        except Exception as exc:
            logging.error("Echo", f"Could not review report {report_id}: {exc}")
            await self._reply(interaction, "The report could not be reviewed right now.")

    async def _is_staff(self, user_id: int) -> bool:
        if is_owner_id(user_id):
            return True
        try:
            return await get_staff_role(self.bot, user_id) is not None
        except Exception:
            return False

    async def _reports_channel(self):
        try:
            ids = await get_support_ids(self.bot)
            channel_id = (ids.get("channels") or {}).get("message_reports")
            if not channel_id:
                return None
            channel = self.bot.get_channel(int(channel_id))
            if channel is None:
                channel = await self.bot.fetch_channel(int(channel_id))
            return channel
        except Exception as exc:
            logging.error("Echo", f"Could not resolve the message reports channel: {exc}")
            return None

    async def _remove_echo(self, echo: dict[str, Any]) -> str:
        channel = self.bot.get_channel(int(echo["channel_id"]))
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(int(echo["channel_id"]))
            except Exception as exc:
                logging.error("Echo", f"Could not resolve echoed message channel: {exc}")
                return "-# The original channel is no longer available, so the message could not be removed."
        try:
            await channel.get_partial_message(int(echo["message_id"])).delete()
            await store.mark_echo_removed(self.pool, echo["echo_id"])
            return "The echoed message was removed."
        except discord.NotFound:
            await store.mark_echo_removed(self.pool, echo["echo_id"])
            return "The echoed message was already gone."
        except (discord.Forbidden, discord.HTTPException) as exc:
            logging.error("Echo", f"Could not delete echoed message {echo['message_id']}: {exc}")
            return "-# The echoed message could not be removed; check Niko's permissions."

    async def _dm_sender(
        self,
        user_id: int,
        warning_count: int,
        blacklist: dict[str, Any] | None,
    ) -> None:
        try:
            user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
            if user is not None:
                await user.send(
                    view=_dm_view(warning_count, blacklist),
                    allowed_mentions=_NO_MENTIONS,
                )
        except Exception as exc:
            logging.warning("Echo", f"Could not DM warning notice to {user_id}: {exc}")

    async def _edit_report(
        self,
        interaction: discord.Interaction,
        report: dict[str, Any],
        echo: dict[str, Any] | None,
        **kwargs,
    ) -> None:
        if interaction.message is None:
            return
        try:
            await interaction.message.edit(
                view=_report_view(report, echo, **kwargs),
                allowed_mentions=_NO_MENTIONS,
            )
        except Exception as exc:
            logging.warning("Echo", f"Could not update report message {report['report_id']}: {exc}")

    async def _edit_ephemeral(self, interaction: discord.Interaction, *, view=None, content: str = "") -> None:
        kwargs = {"allowed_mentions": _NO_MENTIONS}
        if view is not None:
            kwargs["view"] = view
        if content:
            kwargs["content"] = content
        if interaction.response.is_done():
            if interaction.message is not None:
                await interaction.message.edit(**kwargs)
            else:
                await interaction.followup.send(ephemeral=True, **kwargs)
        else:
            await interaction.response.edit_message(**kwargs)

    async def _reply(self, interaction: discord.Interaction, content: str = "", **kwargs) -> None:
        payload = {
            "ephemeral": True,
            "allowed_mentions": _NO_MENTIONS,
            **kwargs,
        }
        if content:
            payload["content"] = content
        if interaction.response.is_done():
            await interaction.followup.send(**payload)
        else:
            await interaction.response.send_message(**payload)
