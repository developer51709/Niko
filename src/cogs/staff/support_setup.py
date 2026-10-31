"""Support-server wiring: configure every system, then post its persistent panels.

``support_server`` builds the channels and roles; this module fills them with
the onboarding, ticket, logging, voice and panel configuration that makes the
community usable. Both ``.staff supportsetup`` and ``.staff supportupdate`` go
through here, so a rebuild and a refresh can never drift apart.
"""

import asyncio

import discord

from config.links import WEBSITE
from cogs.staff.panels.rules import _build_rules_panel
from cogs.staff.panels.status import _build_status_panel, _collect_status
from cogs.staff.support_server import SupportGuidePanel, SUPPORT_ROLE_MENUS, support_rules_text
from utils import logging
from utils.i18n import get_lang


async def bot_member_preflight(guild):
    """Refuse the destructive rebuild unless Niko can reach every channel."""
    bot_member = guild.me
    if bot_member is None or not bot_member.guild_permissions.administrator:
        raise RuntimeError("For the destructive setup, give Niko Administrator temporarily; then rerun the confirmed command. This prevents partial loss from inaccessible channels/roles.")


async def _save_support_panel_record(pool, guild_id: int, panel_key: str, channel_id: int, message_id: int) -> None:
    """Upsert a panel registry row using adapter-compatible conflict arguments."""
    await pool.execute(
        "INSERT INTO support_server_panels (guild_id, panel_key, channel_id, message_id, updated_at) "
        "VALUES ($1, $2, $3, $4, datetime('now')) "
        "ON CONFLICT (guild_id, panel_key) DO UPDATE SET channel_id = $5, message_id = $6, updated_at = datetime('now')",
        guild_id, panel_key, channel_id, message_id, channel_id, message_id,
    )


async def _save_voice_master_settings(pool, guild_id: int, channel_id: int, category_id: int) -> None:
    """Upsert the support guild's voice-master channel configuration."""
    await pool.execute(
        "INSERT INTO voicemaster_settings (guild_id, join_channel_id, category_id, default_name, default_limit, default_bitrate) "
        "VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (guild_id) DO UPDATE SET join_channel_id = $7, category_id = $8",
        guild_id, channel_id, category_id, "{user}'s Channel", 0, 64000, channel_id, category_id,
    )


def _panel_channel_key(panel_key: str, channel_key: str | None = None) -> str:
    """Resolve a panel's target channel without evaluating a parameter as a default."""
    return channel_key or panel_key


def _support_log_channels(channels: dict) -> dict[str, int]:
    """Map each logging event group to its dedicated support-server channel."""
    return {
        "moderation": int(channels["logs"]),
        "automod": int(channels["automod_logs"]),
        "members": int(channels["member_logs"]),
        "messages": int(channels["message_logs"]),
        "channels": int(channels["channel_logs"]),
    }


async def _configure_support_systems(bot, guild, roles, channels):
    from utils.onboarding.utils import get_config, update_config
    from utils.tickets.utils import get_ticket_config, async_update_ticket_config

    def channel_ref(key: str, fallback: str) -> str:
        channel_id = channels.get(key)
        return f"<#{int(channel_id)}>" if channel_id else fallback

    onboarding = await get_config(guild.id)
    onboarding.welcome_channel = int(channels["welcome"])
    onboarding.welcome_title = "Welcome to the Niko community"
    onboarding.welcome_description = (
        "Welcome {user} to the official Niko server — glad you made it here!\n\n"
        "**Get set up**\n"
        f"- Read {channel_ref('rules', '#rules')} once; it takes a minute and covers everything.\n"
        f"- Pick the pings you actually want in {channel_ref('roles', '#roles')} — announcements, events, polls and community news.\n"
        f"- Say hi in {channel_ref('introductions', '#introductions')} if you'd like to meet people.\n\n"
        "**Getting help with Niko**\n"
        f"- Setup questions, errors and feature ideas belong in the {channel_ref('help', '#community-help')} forum. "
        "Search first, then pick the closest tag — **Bug**, **Setup**, **Account** or **Feature request**.\n"
        f"- Account, billing, appeal or other private matters need a ticket in {channel_ref('tickets', '#create-a-ticket')}. "
        "Staff will follow up there, so you never have to share private details in public.\n\n"
        "**A few small things**\n"
        "- Never share passwords, tokens or payment details, and redact personal information from screenshots.\n"
        "- If someone breaks the rules, report it to staff instead of replying to them.\n"
        "- Keep support questions in the support channels so everyone can find the answers later.\n"
        "- Niko is a community project run by volunteers: there is no uptime guarantee, and bot currency has no real-world value.\n\n"
        "Take a look around, and welcome home!"
    )
    onboarding.autorole_ids = [int(roles["member"])]
    onboarding.welcome_color = 0xC8A882
    onboarding.welcome_image = None
    onboarding.captcha_enabled = False
    onboarding.captcha_channel_id = None
    onboarding.captcha_panel_message_id = None
    onboarding.captcha_add_role_ids = []
    onboarding.captcha_remove_role_ids = []
    onboarding.captcha_kick_on_fail = False

    # The member role panels (#roles) are stored as regular onboarding role
    # menus, so `.onboarding role-menu` manages them like any other menu and
    # the startup hook re-registers them after a restart.
    from cogs.staff.support_server import support_role_menus

    menus = support_role_menus(roles)
    if menus:
        configured = getattr(onboarding, "role_menus", None) or {}
        for menu_id, menu in menus.items():
            # Keep where the panel was last posted so a rebuild refreshes the
            # same message instead of leaving a duplicate behind.
            posted = configured.get(menu_id) or {}
            menu["channel_id"] = posted.get("channel_id")
            menu["message_id"] = posted.get("message_id")
            configured[menu_id] = menu
        onboarding.role_menus = configured

    await update_config(guild.id, onboarding)
    from utils.onboarding.config import _pool
    onboarding_pool = _pool()
    if onboarding_pool is None:
        raise RuntimeError("The database is unavailable; onboarding settings could not be saved.")
    if onboarding_pool.db_type != "mongodb":
        saved_config = await onboarding_pool.fetchrow("SELECT guild_id FROM onboarding WHERE guild_id = $1", guild.id)
    else:
        saved_config = await onboarding_pool.collection("onboarding").find_one({"_id": str(guild.id)})
    if not saved_config:
        raise RuntimeError("Onboarding settings could not be saved to the database.")

    ticket_cfg = get_ticket_config(guild.id)
    ticket_cfg.panel_title = "Contact Niko Support"
    ticket_cfg.panel_description = (
        "Open a private ticket and our support team will help you as soon as someone is available.\n\n"
        "**Before you open a ticket**\n"
        "- Check the community-help forum first — most setup questions already have an answer there.\n"
        "- Keep it to one issue per ticket, with a short and specific subject.\n"
        "- Include what you expected, what actually happened, and any error text or screenshots.\n\n"
        "**Please keep in mind**\n"
        "- Never post passwords, tokens, payment details or other private information. Niko staff will never ask for them.\n"
        "- Tickets are answered by volunteers, so response times vary. Opening duplicates slows everyone down.\n"
        "- Abusing the ticket system — spam, harassment or fake reports — can lead to restrictions.\n\n"
        "**Not for Discord-wide issues.** Account recovery, Nitro billing and reports about other users or servers "
        "go to Discord Support, not here."
    )
    ticket_cfg.panel_categories = ["General Support", "Bug Report", "Account & Billing", "Moderation Appeal"]
    ticket_cfg.support_roles = [int(roles[key]) for key in ("staff", "head_admin", "moderator", "head_support", "support")]
    ticket_cfg.panel_channel_id = int(channels["tickets"])
    ticket_cfg.panel_message_id = None
    if not await async_update_ticket_config(guild.id, ticket_cfg):
        raise RuntimeError("Ticket settings could not be saved to the database.")

    from cogs.logging.formatters import _guild_config, _load_log_config, _save_guild_log_config
    all_logs = await _load_log_config()
    log_cfg = dict(_guild_config(all_logs, guild.id))
    log_cfg.update(_support_log_channels(channels))
    await _save_guild_log_config(guild.id, log_cfg)

    from cogs.automod import mrbeast_scam
    await mrbeast_scam.set_review_channel(bot, int(channels["scam_review"]))

    join_channel = guild.get_channel(int(channels["voice_join"]))
    if join_channel is None:
        raise RuntimeError("The configured voice-master join channel disappeared before its settings were saved.")
    await _save_voice_master_settings(
        bot.cxn, guild.id, join_channel.id, join_channel.category_id,
    )
    voice_cog = bot.get_cog("VoiceMaster")
    if voice_cog:
        voice_cog._bust_cache(guild.id)


async def _send_support_panels(bot, guild, roles, channels, *, invite_url: str | None = None):
    from cogs.onboarding.views import RoleMenuView
    from cogs.tickets.views import TicketPanelView
    from utils.onboarding.utils import get_config, update_config
    from utils.tickets.utils import get_ticket_config, async_update_ticket_config
    from cogs.voicemaster.cog import VoiceMasterInterface

    pool = bot.cxn

    async def remove_panel(key):
        """Remove an obsolete setup panel and its registry row, if present."""
        old = await pool.fetchrow(
            "SELECT channel_id, message_id FROM support_server_panels WHERE guild_id = $1 AND panel_key = $2",
            guild.id, key,
        )
        if old:
            channel = guild.get_channel(int(old["channel_id"]))
            if channel is not None:
                try:
                    await channel.get_partial_message(int(old["message_id"])).delete()
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass
            await pool.execute(
                "DELETE FROM support_server_panels WHERE guild_id = $1 AND panel_key = $2",
                guild.id, key,
            )

    async def post(key, view, *, unique_table=None, channel_key=None):
        channel_key = _panel_channel_key(key, channel_key)
        channel = guild.get_channel(int(channels[channel_key]))
        if channel is None:
            raise RuntimeError(f"Configured channel `{channel_key}` disappeared before panel post.")
        old = await pool.fetchrow("SELECT message_id FROM support_server_panels WHERE guild_id = $1 AND panel_key = $2", guild.id, key)
        if old:
            try:
                await channel.get_partial_message(int(old["message_id"])).delete()
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass
        message = await channel.send(view=view)
        await _save_support_panel_record(pool, guild.id, key, channel.id, message.id)
        if unique_table:
            old_unique = await pool.fetchrow(f"SELECT message_id FROM {unique_table} WHERE channel_id = $1 AND guild_id = $2", channel.id, guild.id)
            if old_unique:
                try:
                    await channel.get_partial_message(int(old_unique["message_id"])).delete()
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass
            await pool.execute(f"DELETE FROM {unique_table} WHERE channel_id = $1 AND guild_id = $2", channel.id, guild.id)
            await pool.execute(
                f"INSERT INTO {unique_table} (channel_id, guild_id, message_id, created_at) VALUES ($1, $2, $3, datetime('now'))",
                channel.id, guild.id, message.id,
            )
        return message

    async def post_role_menu(menu_id, menu, cfg):
        """Post or refresh one member role panel as its onboarding role menu.

        The menu config owns the message location, exactly as it does for a menu
        an admin posted with `.onboarding role-menu`, so a refresh edits the
        existing message and a deleted panel is simply reposted.
        """
        channel = guild.get_channel(int(channels["roles"]))
        if channel is None:
            raise RuntimeError("Configured channel `roles` disappeared before panel post.")
        view = RoleMenuView(guild.id, menu_id, cfg=cfg)
        message = None
        if menu.get("channel_id") and menu.get("message_id"):
            posted_channel = guild.get_channel(int(menu["channel_id"])) or channel
            try:
                message = await posted_channel.get_partial_message(int(menu["message_id"])).edit(view=view)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                message = None
        if message is None:
            message = await channel.send(view=view)
        menu["channel_id"] = message.channel.id
        menu["message_id"] = message.id
        bot.add_view(RoleMenuView(guild.id, menu_id, cfg=cfg), message_id=message.id)
        return message

    # These channels are self-explanatory; remove legacy setup panels as well
    # as stopping them from being reposted on future support-server refreshes.
    await remove_panel("welcome")
    await remove_panel("staff_announcements")

    status = await _collect_status(bot)
    await post("status", _build_status_panel(bot, status), unique_table="persistent_status_panels")
    # Rules panel content is intentionally the established `.staff sendpanel rules` panel,
    # not the onboarding rules acknowledgement flow.
    await post("rules", _build_rules_panel(bot), unique_table="persistent_rules_panels")
    await post("staff_rules", _staff_rules_panel(), channel_key="staff_rules")
    website_url = f"{WEBSITE.rstrip('/')}/discord"
    # The partnership ad is the website link, not a bot message: partners paste
    # one URL into their own partnership channel and Discord renders it as the
    # Components V2 card (``webapp/social.py``), which reads as a recommendation
    # from that server instead of an advert posted by a bot or webhook.
    ad_url = f"{WEBSITE.rstrip('/')}/discord/partnership"
    partnership_ad = discord.ui.LayoutView().add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=(
            "# Niko × your community\n"
            "-# The partnership ad, ready to paste"
        )),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=(
            "Share this link wherever promotions are welcome — no bot, no webhook, nothing to configure. "
            "Discord turns it into a card with our pitch, the partner terms and working buttons.\n\n"
            f"**{ad_url}**\n\n"
            "**What the card shows**\n"
            "- What Niko does for members, in plain language\n"
            "- What partner servers get, and what we look for\n"
            "- Buttons to add Niko or join the support server"
        )),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=(
            "-# One post per partnership, only where ads belong — and tell us where you shared it "
            "so the team can keep the listing details current."
        )),
        discord.ui.ActionRow(
            discord.ui.Button(label="Open the ad", style=discord.ButtonStyle.link, url=ad_url),
            discord.ui.Button(label="Partnership info", style=discord.ButtonStyle.link, url=website_url),
        ),
        accent_colour=0xC8A882,
    ))
    await post("partnership_ad", partnership_ad, channel_key="partnership_ad")
    partnership_info = discord.ui.LayoutView().add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=(
            "# Niko server partnerships\n"
            "We partner with welcoming Discord communities that share a genuine interest in helping people discover and get more from Niko. The Partnerships team reviews listings and helps keep recommendations useful, safe, and relevant.\n\n"
            "## Who can apply?\n"
            "Your server should be active, well-moderated, and have a clear purpose. We do not list servers built around scams, harassment, hate, illegal activity, or misleading promotions. Partnership is a mutual recommendation—not a paid placement or an endorsement of every post made by a partner community.\n\n"
            "## What to include\n"
            "Contact a **Partnership Manager** or **Partnerships & Promotions Lead** with:\n"
            "- A permanent invite link and a short description of your community.\n"
            "- The audience you serve and why your members may be interested in Niko.\n"
            "- What kind of collaboration or listing you have in mind.\n"
            f"- Where you plan to share our ad: {website_url}/partnership\n\n"
            "## Listing guidelines\n"
            "Keep advertisements accurate, respectful, and relevant. Use only links you own or are authorized to share; do not post referral bait, mass-DM members, or repeatedly bump an ad. Tell the team if your invite, server focus, or moderation standards change.\n\n"
            "## Sharing our ad\n"
            f"The ad is a single link — `{ad_url}` — rather than a bot message, so it works in any server and always shows the current card. Post it once per partnership, keep it inside channels that allow promotions, and let us know where it went.\n\n"
            "## Review and questions\n"
            "Partnerships are reviewed by the Niko team and are not guaranteed. A listing may be declined or removed if it becomes inactive or no longer meets these standards. Please contact the Partnership team privately if you have questions or need to update a listing."
        )),
        accent_colour=0xC8A882,
    ))
    await post("partnership_info", partnership_info, channel_key="partnership_info")
    await post("support_guide", SupportGuidePanel(channels), channel_key="support_guide")
    # #roles holds onboarding role menus now, so clear the messages left behind
    # by the former support-only panels and then refresh each menu in place.
    for legacy_key in ("notification_roles", "pronoun_roles", "age_roles"):
        await remove_panel(legacy_key)
    onboarding_cfg = await get_config(guild.id)
    for menu_id in SUPPORT_ROLE_MENUS:
        menu = (onboarding_cfg.role_menus or {}).get(menu_id)
        if menu is not None:
            await post_role_menu(menu_id, menu, onboarding_cfg)
    await update_config(guild.id, onboarding_cfg)
    ticket_message = await post("tickets", TicketPanelView(guild.id, get_ticket_config(guild.id)))
    ticket_cfg = get_ticket_config(guild.id)
    ticket_cfg.panel_channel_id = ticket_message.channel.id
    ticket_cfg.panel_message_id = ticket_message.id
    if not await async_update_ticket_config(guild.id, ticket_cfg):
        raise RuntimeError("Ticket panel message settings could not be saved to the database.")
    voice_message = await post("voice_panel", VoiceMasterInterface(get_lang(guild)))
    forum = guild.get_channel(int(channels["help"]))
    if not isinstance(forum, discord.ForumChannel):
        raise RuntimeError("The configured public help channel is not a forum.")
    old_guidelines = await pool.fetchrow("SELECT message_id FROM support_server_panels WHERE guild_id = $1 AND panel_key = 'forum-guidelines'", guild.id)
    if old_guidelines:
        old_thread = guild.get_thread(int(old_guidelines["message_id"]))
        if old_thread is None:
            # Archived posts are not in the thread cache, and a repost on every
            # refresh would leave a pile of stale guidelines posts behind.
            try:
                old_thread = await bot.fetch_channel(int(old_guidelines["message_id"]))
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                old_thread = None
        if old_thread:
            try:
                await old_thread.delete(reason="Refresh support forum guidelines")
                await _support_api_pause()
            except discord.HTTPException:
                pass
    guideline_post = await forum.create_thread(
        name="Post guidelines",
        content=(
            "# Posting in community-help\n\n"
            "Use this forum for Niko questions that other community members can help answer. A little context makes it much easier for someone to reproduce the issue and point you in the right direction.\n\n"
            "## Before you post\n"
            "- Search the forum for a similar question and check the documentation or command guide.\n"
            "- Choose the closest topic tag, such as **Bug**, **Setup**, or **Feature request**.\n"
            "- Keep one question or issue per post, with a clear, specific title.\n\n"
            "## Help us understand\n"
            "Include what you were trying to do, the steps you took, what you expected, and what happened instead. For bugs, add the command or feature involved, the relevant error text, and screenshots when useful. Mention your platform or client if it may matter. Be patient—volunteers may not be online right away.\n\n"
            "## Keep everyone safe\n"
            "Be respectful and assume good intent. Never post passwords, authentication tokens, payment details, private messages, or other sensitive personal information. Redact private data from screenshots. Move account-specific, moderation, or otherwise sensitive cases to a private support ticket.\n\n"
            "## Follow up\n"
            "Reply in your original post with useful updates, and mark the topic **Solved** when you find an answer. Please do not bump repeatedly, advertise, or share content that violates the server rules."
        ),
        reason="Publish community-help post guidelines",
    )
    await _support_api_pause()
    await _pin_forum_post(guideline_post.thread)
    await _save_support_panel_record(
        pool, guild.id, "forum-guidelines", forum.id, guideline_post.thread.id,
    )

    bot.add_view(SupportGuidePanel(channels))
    bot.add_view(VoiceMasterInterface(), message_id=voice_message.id)
    bot.add_view(TicketPanelView(guild.id, get_ticket_config(guild.id)), message_id=ticket_message.id)


async def _support_api_pause():
    await asyncio.sleep(0.35)


async def _pin_forum_post(thread) -> bool:
    """Pin a forum post, then lock and archive it.

    Discord ignores the pinned flag when ``archived`` is sent in the same
    request, which is why the community-help guidelines post was published
    without ever showing up in the forum's pinned list. Pinning first — while
    the post is still active — then archiving keeps it pinned.
    """
    try:
        pinned = await thread.edit(
            archived=False, pinned=True,
            reason="Pin the read-only community-help post guidelines",
        )
    except discord.HTTPException as exc:
        logging.warning("SupportServer", f"Could not pin the community-help guidelines post: {exc}")
        return False
    pin_kept = bool(getattr(getattr(pinned, "flags", None), "pinned", False))
    if not pin_kept:
        logging.warning("SupportServer", "Discord did not keep the community-help guidelines post pinned.")
    await _support_api_pause()
    # Lock and archive either way: an unlocked guidelines post invites replies
    # that nobody monitors, even if the pin above needs a manual retry.
    try:
        await thread.edit(
            archived=True, locked=True,
            reason="Lock the read-only community-help post guidelines",
        )
    except discord.HTTPException as exc:
        logging.warning("SupportServer", f"Could not lock the community-help guidelines post: {exc}")
    await _support_api_pause()
    return pin_kept


def _staff_rules_panel():
    view = discord.ui.LayoutView()
    sections = support_rules_text().split("\n\n")
    items = [
        discord.ui.TextDisplay(content="# Staff guidelines\n-# Niko Support · Internal team handbook"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    ]
    for index, section in enumerate(sections):
        if index:
            items.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        items.append(discord.ui.TextDisplay(content=section))
    view.add_item(discord.ui.Container(*items, accent_colour=0xC8A882))
    return view
