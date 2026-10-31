"""The public server-rules panel for the support server.

Every rule is printed in the panel itself, so members never have to click
through pages to read them. The panel's only buttons open *ephemeral* helper
cards — important links, and the problems that are not ours to fix — which are
answered privately to whoever clicked.

Components V2 caps a message at 4,000 characters of text, so the body stays
compact: one card per rule group, each rule a short bold title and one plain
sentence on the same line, then a short intro and footer.
"""

import discord

from config import links
from config.emojis import get_emoji

_RULES_LINKS_ID = "niko:rules:links"
_RULES_SCOPE_ID = "niko:rules:scope"

DISCORD_SUPPORT_URL = "https://support.discord.com/hc/en-us/requests/new"
DISCORD_REPORT_URL = "https://discord.com/safety/360044103651-reporting-abusive-behavior-to-discord"

# Rule numbers are derived from position, so inserting a rule never needs the
# rest renumbered by hand.
RULES_SECTIONS: dict[str, dict] = {
    "conduct": {
        "emoji": get_emoji("heart"),
        "label": "Conduct",
        "rules": (
            ("Be respectful", "No harassment, hate speech, discrimination, or personal attacks. Treat everyone the way you'd like to be treated."),
            ("Keep it appropriate", "No NSFW content anywhere in this server."),
            ("No drama or targeted attacks", "Public call-outs and witch hunts are for staff, not members."),
            ("Use English", "It keeps support fast for everyone. Your DMs are yours to use however you like."),
            ("Staff have the final say", "If a moderator asks you to stop, stop. Raise disputes politely afterwards."),
        ),
    },
    "content": {
        "emoji": get_emoji("scroll"),
        "label": "Content & channels",
        "rules": (
            ("Right content, right channel", "Questions in support channels, showcases in theirs, memes in the lounge."),
            ("No spam or unrequested promotion", "That includes unsolicited DMs, and advertising other bots or servers."),
            ("No malicious content", "No scams, phishing, malware, IP grabbers, or jump-scare links. Report anything odd; don't click it."),
            ("No piracy", "No links to or requests for pirated media, software, or paid assets."),
            ("Take drifting topics to a thread", "Long side-discussions move to threads so channels stay readable."),
        ),
    },
    "moderation": {
        "emoji": get_emoji("moderation"),
        "label": "Moderation",
        "rules": (
            ("Moderators act on intent", "Anything against the spirit of these rules counts, even if it isn't listed."),
            ("The escalation ladder", "Warning → timeout → kick → ban. Scams, malware, raids, and CSAM skip straight to a ban and go to Discord's Trust & Safety."),
            ("Ban evasion ends access", "Alternate accounts made to come back after a ban are removed on sight."),
            ("Appeals go through tickets", "Open a ticket in this server and be honest — lying makes it worse."),
            ("Niko's blacklist is separate", "Abusing the bot itself (exploits, command spam) can get you blacklisted bot-wide under its Terms of Service."),
        ),
    },
    "bot": {
        "emoji": get_emoji("bot"),
        "label": "Bot rules",
        "rules": (
            ("Niko is a community project", "Not a product: there's no uptime guarantee. Premium funds development but buys no SLA."),
            ("Economy items have no real value", "Bot currency and items can't be sold, traded for money, or refunded."),
            ("Don't exploit bugs", "Found one? Report it and don't farm it — exploiters lose balances and risk blacklisting."),
            ("No automated abuse", "Self-bots, macro farms, and command spam hurt the bot for everyone."),
            ("AI replies can be wrong", "They're clearly marked. Verify anything important yourself."),
        ),
    },
}


class RulesLinksButton(discord.ui.DynamicItem[discord.ui.Button], template=r"niko:rules:links"):
    """Persistent shortcut to the ephemeral important-links card."""

    def __init__(self) -> None:
        super().__init__(discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Important links",
            emoji=get_emoji("link"),
            custom_id=_RULES_LINKS_ID,
        ))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls()

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            view=_rules_links_view(interaction.client), ephemeral=True
        )


class RulesScopeButton(discord.ui.DynamicItem[discord.ui.Button], template=r"niko:rules:scope"):
    """Persistent shortcut to the ephemeral out-of-scope reporting card."""

    def __init__(self) -> None:
        super().__init__(discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Not ours to fix",
            emoji=get_emoji("question"),
            custom_id=_RULES_SCOPE_ID,
        ))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls()

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            view=_rules_scope_view(interaction.client), ephemeral=True
        )


#: Every persistent item of the rules panel, registered by the staff cog.
PERSISTENT_ITEMS = (RulesLinksButton, RulesScopeButton)


def _rules_header(bot, title: str, subtitle: str) -> discord.ui.Item:
    """Panel header with the bot's avatar as thumbnail (plain text fallback)."""
    header_text = discord.ui.TextDisplay(content=(f"## {get_emoji('support')} {title}\n-# {subtitle}"))
    avatar = None
    try:
        user = getattr(bot, "user", None)
        avatar = getattr(user, "display_avatar", None)
    except Exception:
        avatar = None
    if avatar is not None:
        return discord.ui.Section(header_text, accessory=discord.ui.Thumbnail(str(avatar.url)))
    return header_text


def _rules_panel_row() -> discord.ui.ActionRow:
    """The public panel's only buttons: shortcuts to the helper cards."""
    return discord.ui.ActionRow(RulesLinksButton(), RulesScopeButton())


def _rules_links_view(bot) -> discord.ui.LayoutView:
    """Ephemeral card listing every official Niko link."""
    bot_id = getattr(getattr(bot, "user", None), "id", None)
    invite = (
        f"https://discord.com/oauth2/authorize?client_id={bot_id}&permissions=8&scope=bot%20applications.commands"
        if bot_id else links.SUPPORT_SERVER
    )
    items: list = [
        _rules_header(bot, "Important links", "Every official Niko page in one place."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=(
            "**Start here**\n"
            f"- {get_emoji('website')} [Website]({links.WEBSITE}) — news, changelog and the server dashboard.\n"
            f"- {get_emoji('docs')} [Documentation]({links.DOCS}) — setup guides and the full command reference.\n"
            f"- {get_emoji('support')} [Support server]({links.SUPPORT_SERVER}) — this community's permanent invite.\n"
            f"- {get_emoji('invite')} [Invite Niko]({invite}) — add the bot to your own server.\n\n"
            "**Policies**\n"
            f"- {get_emoji('docs')} [Terms of Service]({links.TOS})\n"
            f"- {get_emoji('important')} [Privacy Policy]({links.PRIVACY})\n"
            f"- {get_emoji('verified')} [Community Guidelines]({links.COMMUNITY})\n"
            f"- {get_emoji('lock')} [Request removal of your data]({links.DATA_REMOVAL})\n\n"
            "**Elsewhere**\n"
            f"- {get_emoji('github')} [GitHub]({links.GITHUB}) — source, issues and release notes.\n"
            f"- {get_emoji('topgg')} [Vote on top.gg]({links.TOPGG_VOTE_URL}) — a free way to help other servers find Niko."
        )),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            discord.ui.Button(style=discord.ButtonStyle.link, label="Website", url=links.WEBSITE),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Docs", url=links.DOCS),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Support server", url=links.SUPPORT_SERVER),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Privacy", url=links.PRIVACY),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Terms", url=links.TOS),
        ),
    ]
    view = discord.ui.LayoutView(timeout=300)
    view.add_item(discord.ui.Container(*items, accent_colour=0xC8A882))
    return view


def _rules_scope_view(bot) -> discord.ui.LayoutView:
    """Ephemeral card for problems Niko's team cannot act on."""
    items: list = [
        _rules_header(bot, "Not ours to fix", "Some reports belong to Discord or another team — here is where each one goes."),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=(
            "**Discord account & platform issues**\n"
            "- Lost account, 2FA, a hacked account, Nitro or Discord billing, or a bug inside the Discord app "
            f"→ [Discord Support]({DISCORD_SUPPORT_URL}). Niko staff cannot view or change your Discord account.\n"
            "- A user, message or server breaking Discord's own rules "
            f"→ [report it to Discord Trust & Safety]({DISCORD_REPORT_URL}), or use the in-app **Report** option. "
            "We can only moderate inside this server.\n"
            "- A different bot, bot list or third-party service "
            "→ that project's own support server. We have no access to it.\n\n"
            "**What we do handle**\n"
            "- A Niko command failing, an error code, or a feature that does not work as documented "
            "→ open a **Bug** post in the community-help forum with the exact error text.\n"
            "- Anything tied to your account, a purchase, premium, appeals or data removal "
            "→ open a private ticket and never post payment details in public.\n"
            "- A member or post in this server that needs staff attention "
            "→ mention a member of staff or open a ticket instead of confronting anyone publicly."
        )),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            discord.ui.Button(style=discord.ButtonStyle.link, label="Discord Support", url=DISCORD_SUPPORT_URL),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Report to Discord", url=DISCORD_REPORT_URL),
            discord.ui.Button(style=discord.ButtonStyle.link, label="Niko docs", url=links.DOCS),
        ),
    ]
    view = discord.ui.LayoutView(timeout=300)
    view.add_item(discord.ui.Container(*items, accent_colour=0x5865F2))
    return view


def _rules_spacer() -> discord.ui.Separator:
    """Invisible separator: adds breathing room between cards, draws nothing."""
    return discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.large)


def _rules_section_cards() -> list:
    """One container per rule group, so each group reads as its own card."""
    cards: list = []
    number = 1
    for meta in RULES_SECTIONS.values():
        rules = meta["rules"]
        last = number + len(rules) - 1
        blocks = [f"### {meta['emoji']} {meta['label']} · {number}–{last}"]
        for title, detail in rules:
            # Title and sentence share a line: a line break reads as a paragraph
            # gap and doubles the height of every rule.
            blocks.append(f"**{number}. {title}** — {detail}")
            number += 1
        cards.append(discord.ui.Container(
            discord.ui.TextDisplay(content="\n".join(blocks)),
            accent_colour=0xC8A882,
        ))
    return cards


def _rules_home_view(bot) -> discord.ui.LayoutView:
    """The public panel: every rule, printed inline, plus helper-card buttons."""
    intro = discord.ui.Container(
        _rules_header(
            bot,
            "Niko Support — Server Rules",
            "Twenty rules in four short sections. Skim the bold titles — every rule is one sentence.",
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=(
            f"{get_emoji('welcome')} Hey, I'm **Niko** — a cozy Discord companion for communities that care. "
            "This is the official Niko support server: help, ideas, announcements, and a friendly corner of Discord.\n"
            "Being kind is most of it. These rules apply everywhere in this server."
        )),
        accent_colour=0xC8A882,
    )

    footer = discord.ui.Container(
        discord.ui.TextDisplay(content=(
            f"-# {get_emoji('question')} Bot help belongs in the community-help forum; account or sensitive issues "
            "belong in a ticket. The buttons below open important links, and where to report things that aren't ours to fix."
        )),
        _rules_panel_row(),
        accent_colour=0x2E3440,
    )

    view = discord.ui.LayoutView()
    view.add_item(intro)
    for card in _rules_section_cards():
        # A spacer before each card keeps the four groups visibly apart while
        # staying inside the ten top-level components a V2 message allows.
        view.add_item(_rules_spacer())
        view.add_item(card)
    view.add_item(footer)
    return view


def _build_rules_panel(bot) -> discord.ui.LayoutView:
    return _rules_home_view(bot)
