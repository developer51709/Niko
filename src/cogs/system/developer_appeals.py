"""Discord DMs and the persistent appeal button for suspended API developers.

The button uses one static custom id and is registered at startup, so every DM
Niko has ever sent keeps working across restarts. The account is taken from the
interaction user, which is also why a single button can serve every developer.
"""

from __future__ import annotations

from datetime import datetime, timezone

import discord

from config.links import WEBSITE
from utils import logging

APPEAL_BUTTON_ID = "niko:developer:appeal"
APPEAL_MODAL_ID = "niko:developer:appeal:modal"

RATE_LIMIT_DOCS = f"{WEBSITE}/developers/rate-limits"
POLICY_DOCS = f"{WEBSITE}/developers/policies"
DISCORD_RATE_LIMITS = "https://discord.com/developers/docs/topics/rate-limits"


def _when(value) -> str:
    try:
        moment = datetime.fromtimestamp(float(value), tz=timezone.utc)
        return f"<t:{int(moment.timestamp())}:F>"
    except (TypeError, ValueError, OSError):
        return "recently"


def _appeal_text(suspension: dict) -> str:
    reason = str(suspension.get("reason") or "Automated abuse detection suspended this account.")
    prefix = str(suspension.get("key_prefix") or "").strip()
    lines = [
        "## API access suspended",
        "Niko detected automated activity that exceeded the developer API safety limits. "
        "All API keys on this account have been revoked, and developer-portal key management is locked.",
        "",
        f"**Reason:** {reason}",
        f"**Suspended:** {_when(suspension.get('at'))}",
    ]
    if prefix:
        lines.append(f"**Key involved:** `{prefix}…`")
    lines.extend([
        "",
        "If you believe this was a mistake, submit an appeal below. A staff decision will "
        "arrive in this DM. No new keys can be created until access is restored.",
    ])
    return "\n".join(lines)


def _decision_text(appeal: dict, suspension: dict | None) -> tuple[str, bool]:
    status = str(appeal.get("status") or "")
    note = str(appeal.get("note") or "").strip()
    if status == "approved":
        lines = [
            "## API appeal approved",
            "Your developer API access has been restored. The keys that were active during the "
            "suspension stay revoked; create new keys from the Developer portal when you are ready.",
            "",
            "Before you resume traffic, add conservative request budgets, exponential backoff with "
            "jitter on `429` and `5xx` responses, and a single shared limiter for every process that "
            "uses the same key.",
        ]
        if note:
            lines.extend(["", f"**Staff note:** {note}"])
        return "\n".join(lines), True
    lines = [
        "## API appeal denied",
        "Your developer API access remains suspended. The existing keys stay revoked and the "
        "Developer portal will keep key management locked.",
    ]
    if note:
        lines.extend(["", f"**Staff note:** {note}"])
    lines.extend([
        "",
        "You can review the developer policies for the expected request and data-handling rules. "
        "If you need help understanding the decision, open a support ticket rather than creating another account.",
    ])
    return "\n".join(lines), False


class DeveloperAppealModal(discord.ui.Modal, title="Appeal your API suspension"):
    statement = discord.ui.TextInput(
        label="Why should access be restored?",
        style=discord.TextStyle.paragraph,
        placeholder="Explain what happened, what you changed, and how you will prevent it recurring.",
        max_length=4000,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        from webapp import developer_portal

        try:
            appeal = developer_portal.submit_appeal(interaction.user.id, str(self.statement.value or ""))
        except PermissionError as error:
            return await interaction.response.send_message(str(error), ephemeral=True)
        except ValueError as error:
            return await interaction.response.send_message(str(error), ephemeral=True)
        except Exception as error:
            logging.error("DeveloperAPI", f"Could not submit suspension appeal: {error}")
            return await interaction.response.send_message(
                "The appeal could not be submitted. Try again later or open a support ticket.",
                ephemeral=True,
            )
        await interaction.response.send_message(
            f"Appeal `{appeal['id']}` submitted. Staff will review it and send the decision in this DM.",
            ephemeral=True,
        )


class DeveloperAppealButton(discord.ui.Button):
    """One persistent button shared by every suspension DM."""

    def __init__(self):
        super().__init__(
            label="Submit an appeal",
            style=discord.ButtonStyle.primary,
            custom_id=APPEAL_BUTTON_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        from webapp import developer_portal

        suspension = developer_portal.suspension_for_user(interaction.user.id)
        if suspension is None:
            return await interaction.response.send_message(
                "This account does not have an active API suspension.",
                ephemeral=True,
            )
        appeal = developer_portal.appeal_for_user(interaction.user.id)
        if appeal is not None:
            status = str(appeal.get("status") or "pending")
            if status == "pending":
                message = "Your appeal is already under review. Staff will send the decision in this DM."
            elif status == "denied":
                message = "The appeal for this suspension was already denied. Open a support ticket if you need clarification."
            else:
                message = "This suspension already has an appeal decision."
            return await interaction.response.send_message(message, ephemeral=True)
        await interaction.response.send_modal(DeveloperAppealModal())


def _suspension_view(suspension: dict) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=_appeal_text(suspension)),
        discord.ui.Separator(visible=True, spacing=discord.ui.SeparatorSpacing.small),
        discord.ui.ActionRow(DeveloperAppealButton()),
        discord.ui.ActionRow(
            discord.ui.Button(label="Rate-limit guide", style=discord.ButtonStyle.link, url=RATE_LIMIT_DOCS),
            discord.ui.Button(label="Developer policies", style=discord.ButtonStyle.link, url=POLICY_DOCS),
        ),
        accent_colour=discord.Colour.red(),
    ))
    return view


def _decision_view(appeal: dict, suspension: dict | None) -> discord.ui.LayoutView:
    text, approved = _decision_text(appeal, suspension)
    row = (
        discord.ui.ActionRow(
            discord.ui.Button(label="Rate-limit guide", style=discord.ButtonStyle.link, url=RATE_LIMIT_DOCS),
            discord.ui.Button(label="Developer policies", style=discord.ButtonStyle.link, url=POLICY_DOCS),
            discord.ui.Button(label="Discord rate limits", style=discord.ButtonStyle.link, url=DISCORD_RATE_LIMITS),
        )
        if approved
        else discord.ui.ActionRow(
            discord.ui.Button(label="Developer policies", style=discord.ButtonStyle.link, url=POLICY_DOCS),
        )
    )
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=text),
        discord.ui.Separator(visible=True, spacing=discord.ui.SeparatorSpacing.small),
        row,
        accent_colour=discord.Colour.green() if approved else discord.Colour.red(),
    ))
    return view


async def send_suspension_dm(bot, user_id: str, suspension_id: str) -> bool:
    from webapp import developer_portal

    suspension = developer_portal.suspension_for_user(user_id)
    if suspension is None or str(suspension.get("id")) != str(suspension_id):
        return False
    try:
        user = bot.get_user(int(user_id)) or await bot.fetch_user(int(user_id))
        await user.send(view=_suspension_view(suspension), allowed_mentions=discord.AllowedMentions.none())
        developer_portal.mark_suspension_notified(user_id, suspension_id)
        return True
    except discord.Forbidden:
        logging.warning(
            "DeveloperAPI",
            f"Could not DM suspended developer {user_id}; their DMs are closed.",
        )
    except discord.HTTPException as error:
        logging.warning("DeveloperAPI", f"Could not DM suspended developer {user_id}: {error}")
    except Exception as error:
        logging.warning("DeveloperAPI", f"Unexpected suspension DM failure for {user_id}: {error}")
    return False


async def send_appeal_decision_dm(bot, user_id: str, appeal_id: str) -> bool:
    from webapp import developer_portal

    appeal = developer_portal.appeal_by_id(appeal_id)
    if appeal is None:
        return False
    suspension = developer_portal.suspension_for_user(user_id)
    try:
        user = bot.get_user(int(user_id)) or await bot.fetch_user(int(user_id))
        await user.send(
            view=_decision_view(appeal, suspension),
            allowed_mentions=discord.AllowedMentions.none(),
        )
        developer_portal.mark_appeal_notified(appeal_id)
        return True
    except discord.Forbidden:
        logging.warning(
            "DeveloperAPI",
            f"Could not DM the appeal decision to {user_id}; their DMs are closed.",
        )
    except discord.HTTPException as error:
        logging.warning("DeveloperAPI", f"Could not DM the appeal decision to {user_id}: {error}")
    except Exception as error:
        logging.warning("DeveloperAPI", f"Unexpected appeal DM failure for {user_id}: {error}")
    return False


def register_developer_persistent_views(bot) -> None:
    registry = discord.ui.LayoutView(timeout=None)
    registry.add_item(discord.ui.Container(
        discord.ui.ActionRow(DeveloperAppealButton()),
    ))
    bot.add_view(registry)


async def setup(bot):
    register_developer_persistent_views(bot)
