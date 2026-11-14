"""Niko's custom application emoji strings.

``get_emoji`` is imported once per module and called from nearly every cog, and
a module-level constant such as ``INTERFACE_COMMANDS`` freezes whatever it
returned at import. That is fine until an emoji is re-uploaded: Discord has no
way to replace an emoji's art, so new art means a new id, and every frozen
string would keep pointing at the old, deleted one until the process restarted.

``apply_live_emoji_ids`` closes that gap. The runtime sync (utils/emoji_sync.py)
hands it the ids it just uploaded, ``get_emoji`` swaps them in at call time, and
the sync rewrites the constants that were built at import, so a sync takes
effect immediately instead of on the next boot.
"""

from __future__ import annotations

import re

# An emoji as it appears in a message: <:name:id> or <a:name:id>.
_EMOJI_REF = re.compile(r"<(a?):([A-Za-z0-9_]+):(\d+)>")

# Old id → the emoji string that replaced it, filled in by the sync. Keyed by
# id rather than by name because one key can return more than one emoji
# (``enabled``) and a few keys name a different Discord name than the key
# itself (``automod`` → ``Automod``).
_LIVE_IDS: dict[int, str] = {}


def get_emoji(emoji_name: str):
    """The configured emoji string for ``emoji_name``, or ``None`` if unknown.

    Any id the running sync has re-uploaded is swapped for the live one, so a
    caller that imported this function before the sync still sends a working
    emoji.
    """
    return swap_emoji_ids(_configured_emoji(emoji_name))


def swap_emoji_ids(value, remap: dict[int, str] | None = None):
    """Swap every re-uploaded emoji id in ``value`` for its live replacement.

    ``remap`` defaults to the ids currently in force, which is what a live
    ``get_emoji`` call wants; the sync passes its own map while it is still
    applying one.
    """
    ids = _LIVE_IDS if remap is None else remap
    if not value or not ids or not isinstance(value, str):
        return value
    return _EMOJI_REF.sub(lambda match: ids.get(int(match.group(3)), match.group(0)), value)


def apply_live_emoji_ids(remap: dict[int, str]) -> int:
    """Adopt ids the sync just uploaded; returns how many are now in force.

    The map is updated in place, so modules that already hold a reference to
    ``get_emoji`` — the usual ``from config.emojis import get_emoji`` — see the
    new ids on their next call without a reload or a restart.
    """
    _LIVE_IDS.update(remap)
    return len(_LIVE_IDS)


def live_emoji_ids() -> dict[int, str]:
    """A copy of the id replacements currently in force (for reports/tests)."""
    return dict(_LIVE_IDS)


def _configured_emoji(emoji_name: str):
    """The emoji exactly as written in this file; see :func:`get_emoji`."""
    # ==========================================================================
    # Status and feedback
    # ==========================================================================
    # Outcomes and labels. A pass is green, a failure or a removal red, a caution
    # orange; everything that only labels something is the one neutral ink.
    if emoji_name == "tick":
        return "<:tick:1564762582282280990>"
    if emoji_name == "cross":
        return "<:cross:1564762429378793502>"
    if emoji_name == "warning":
        return "<:warning:1564762738826154057>"
    if emoji_name == "danger":
        return "<:danger:1564762432562270238>"
    if emoji_name == "important":
        return "<:important:1564762474979393578>"
    if emoji_name == "question":
        return "<:question:1564762541064851516>"
    if emoji_name == "plus":
        return "<:plus:1564762534769201284>"
    if emoji_name == "minus":
        return "<:minus:1564762513076133920>"
    if emoji_name == "thumbs_up":
        return "<:thumbs_up:1564762702444896417>"
    if emoji_name == "thumbs_down":
        return "<:thumbs_down:1564762699961860177>"
    if emoji_name == "verified":
        return "<:verified:1564762597784289372>"
    if emoji_name == "enabled":
        return "<:disable_no:1564762961594290307><:enable_yes:1564762964760731729>"
    if emoji_name == "disabled":
        return "<:disable_yes:1564762967868702861><:enable_no:1564762970951516160>"

    # ==========================================================================
    # Moderation and utility
    # ==========================================================================
    # The tools a moderator or an admin reaches for, and the spinner every command
    # shows while it works.
    if emoji_name == "moderation":
        return "<:moderation:1564762517190869324>"
    if emoji_name == "automod":
        return "<:Automod:1564762255667765383>"
    if emoji_name == "ban":
        return "<:ban:1564762413788700712>"
    if emoji_name == "lock":
        return "<:lock:1564762729577979995>"
    if emoji_name == "unlock":
        return "<:unlock:1564762736171290754>"
    if emoji_name == "hide":
        return "<:hide:1564762725853298698>"
    if emoji_name == "unhide":
        return "<:unhide:1564762732966846495>"
    if emoji_name == "edit":
        return "<:edit:1564762446604800180>"
    if emoji_name == "trash":
        return "<:trash:1564762588619743424>"
    if emoji_name == "broom":
        return "<:broom:1565386565730041866>"
    if emoji_name == "utility":
        return "<:utility:1564762591656542410>"
    if emoji_name == "nsfw":
        return "<:nsfw:1564762520726671391>"
    if emoji_name == "loading":
        return "<a:loading:1564762500938076161>"

    # ==========================================================================
    # Navigation and structure
    # ==========================================================================
    # The help menu, the panels and the cards are built from these, so they are all
    # neutral: a menu of coloured icons reads as noise.
    if emoji_name == "home":
        return "<:home:1564762465848397904>"
    if emoji_name == "general":
        return "<:general:1564762456335843429>"
    if emoji_name == "categories":
        return "<:categories:1564762426233069639>"
    if emoji_name == "settings":
        return "<:settings:1564762562762121307>"
    if emoji_name == "docs":
        return "<:docs:1564762438660792472>"
    if emoji_name == "website":
        return "<:website:1565386636332896388>"
    if emoji_name == "notepad":
        return "<:notepad:1564762617879335062>"
    if emoji_name == "scroll":
        return "<:scroll:1564762670698336306>"
    if emoji_name == "stats":
        return "<:stats:1564762573063069876>"
    if emoji_name == "support":
        return "<:support:1564762579102867536>"
    if emoji_name == "arrow_left":
        return "<:arrow_left:1564762250055651478>"
    if emoji_name == "arrow_right":
        return "<:arrow_right:1564762252987601056>"

    # ==========================================================================
    # People and members
    # ==========================================================================
    # People and members.
    if emoji_name == "user":
        return "<:user:1564762594722578572>"
    if emoji_name == "join":
        return "<:join:1564762483032326206>"
    if emoji_name == "leave":
        return "<:leave:1564762486400622603>"
    if emoji_name == "welcome":
        return "<:welcome:1564762600816779445>"
    if emoji_name == "invite":
        return "<:invite:1564762478469185657>"
    if emoji_name == "participants":
        return "<:participants:1565046580262993961>"

    # ==========================================================================
    # Content and social
    # ==========================================================================
    # Content and social.
    if emoji_name == "message":
        return "<:message:1564762510358224956>"
    if emoji_name == "image":
        return "<:image:1564762472030674944>"
    if emoji_name == "link":
        return "<:link:1564762497733361728>"
    if emoji_name == "megaphone":
        return "<:megaphone:1564762507338322080>"
    if emoji_name == "lightbulb":
        return "<:lightbulb:1564762494684102736>"
    if emoji_name == "heart":
        return "<:heart:1564762462442623166>"
    if emoji_name == "star":
        return "<:star:1564762680038793296>"
    if emoji_name == "ai":
        return "<:ai:1564762410412155051>"
    if emoji_name == "bot":
        return "<:bot:1564762420260643008>"
    if emoji_name == "bug":
        return "<:bug:1564762423259439155>"
    if emoji_name == "sad":
        return "<:sad:1565046593122472006>"

    # ==========================================================================
    # Media controls
    # ==========================================================================
    # The music and voicemaster panels post a whole row of these at once, so they are
    # all neutral and share one weight. The ids here are stubs on a fresh checkout and
    # live application-emoji ids after the first sync.
    if emoji_name == "play":
        return "<:play:1564762531447181322>"
    if emoji_name == "pause":
        return "<:pause:1564762526678253689>"
    if emoji_name == "stop":
        return "<:stop:1564762576074703138>"
    if emoji_name == "skip":
        return "<:skip:1564762569615351841>"
    if emoji_name == "rewind":
        return "<:rewind:1564762559100227664>"
    if emoji_name == "shuffle":
        return "<:shuffle:1564762566927061144>"
    if emoji_name == "loop":
        return "<:loop:1564762503915901152>"
    if emoji_name == "queue":
        return "<:queue:1565046583332970656>"
    if emoji_name == "volume_down":
        return "<:volume_down:1565046586029908172>"
    if emoji_name == "volume_up":
        return "<:volume_up:1565046590035730502>"
    if emoji_name == "autoplay":
        return "<:autoplay:1565046573170167918>"
    if emoji_name == "refresh":
        return "<:refresh:1564762544160243826>"
    if emoji_name == "music":
        return "<:music:1564762613790019675>"
    if emoji_name == "voicemaster":
        return "<:voicemaster:1564762718290837575>"
    if emoji_name == "owner_icon":
        return "<:owner_icon:1564762651609923638>"
    if emoji_name == "disconnect":
        return "<:disconnect:1564762385171087501>"
    if emoji_name == "pingpong":
        return "<:pingpong:1564762657813168149>"

    # ==========================================================================
    # Commands and rewards
    # ==========================================================================
    # One emoji per command family, plus the giveaway setup panel's own controls.
    if emoji_name == "premium":
        return "<:premium:1564762537764069556>"
    if emoji_name == "gift":
        return "<:gift:1564762392112402523>"
    if emoji_name == "giveaway":
        return "<:giveaway:1564762459473182720>"
    if emoji_name == "ticket":
        return "<:ticket:1564762585373610146>"
    if emoji_name == "economy":
        return "<:economy:1564762442339192943>"
    if emoji_name == "leveling":
        return "<:leveling:1564762491425390823>"
    if emoji_name == "gambling":
        return "<:gambling:1564762453257224402>"
    if emoji_name == "games":
        return "<:games:1564762450182668288>"
    if emoji_name == "roleplay":
        return "<:roleplay:1564762550598504578>"
    if emoji_name == "paint":
        return "<:paint:1564762523603828857>"
    if emoji_name == "reminder":
        return "<:reminder:1564762547440189521>"
    if emoji_name == "duration":
        return "<:duration:1565046576613687506>"
    if emoji_name == "trophy":
        return "<:trophy:1565046596293627966>"
    if emoji_name == "credit_card":
        return "<a:credit_card:1564762347082489889>"

    # ==========================================================================
    # Machine stats
    # ==========================================================================
    # The status commands read these four in one block, so they keep one ink.
    if emoji_name == "cpu":
        return "<:cpu:1564762344079495188>"
    if emoji_name == "ram":
        return "<:ram:1564762664503091241>"
    if emoji_name == "disk":
        return "<:disk:1564762435632496841>"
    if emoji_name == "host":
        return "<:host:1564762468981678194>"

    # ==========================================================================
    # Numbers
    # ==========================================================================
    # 0-9 in order, drawn from Phosphor Icons by scripts/build-emoji-icons.mjs. Lucide
    # has no plain digit, and the old hand-exported digits were smaller and a
    # different design from the rest of the set.
    if emoji_name == "number_zero":
        return "<:number_zero:1567262936315994203>"
    if emoji_name == "number_one":
        return "<:number_one:1567262939705118853>"
    if emoji_name == "number_two":
        return "<:number_two:1567262943073144832>"
    if emoji_name == "number_three":
        return "<:number_three:1567262946189512797>"
    if emoji_name == "number_four":
        return "<:number_four:1567262950048399401>"
    if emoji_name == "number_five":
        return "<:number_five:1567262953009582194>"
    if emoji_name == "number_six":
        return "<:number_six:1567262956536864898>"
    if emoji_name == "number_seven":
        return "<:number_seven:1567262960504807585>"
    if emoji_name == "number_eight":
        return "<:number_eight:1567262964027891752>"
    if emoji_name == "number_nine":
        return "<:number_nine:1567262967047786628>"

    # ==========================================================================
    # Discord profile and badges
    # ==========================================================================
    # Discord's own profile badges and presence dots. Their artwork is generated from
    # the badge SVGs by scripts/build-badge-art.mjs, and the ids are placeholders: the
    # startup emoji sync uploads the PNGs and rewrites them with the live ids.
    if emoji_name == "active_developer_badge":
        return "<:active_developer_badge:1564762177959759935>"
    if emoji_name == "verified_developer_badge":
        return "<:verified_developer_badge:1564762722711769138>"
    if emoji_name == "bug_hunter_badge":
        return "<:bug_hunter_badge:1564762209085690018>"
    if emoji_name == "bug_hunter_gold_badge":
        return "<:bug_hunter_gold_badge:1564762215532466298>"
    if emoji_name == "certified_moderator_badge":
        return "<:certified_moderator_badge:1564762218627600394>"
    if emoji_name == "early_supporter_badge":
        return "<:early_supporter_badge:1564762222545084548>"
    if emoji_name == "partner_badge":
        return "<:partner_badge:1564762228425752626>"
    if emoji_name == "staff_badge":
        return "<:staff_badge:1564762231684464811>"
    if emoji_name == "supports_commands_badge":
        return "<:supports_commands_badge:1564762245475606538>"
    if emoji_name == "hypesquad_events":
        return "<:hypesquad_events:1564762225284218881>"
    if emoji_name == "hypesquad_balance":
        return "<:hypesquad_balance:1564762399821537403>"
    if emoji_name == "hypesquad_bravery":
        return "<:hypesquad_bravery:1564762403856588842>"
    if emoji_name == "hypesquad_briliance":
        return "<:hypesquad_briliance:1564762407249907712>"
    if emoji_name == "status_online":
        return "<:status_online:1564762692420501645>"
    if emoji_name == "status_idle":
        return "<:status_idle:1564762686175313930>"
    if emoji_name == "status_dnd":
        return "<:status_dnd:1564762682765222052>"
    if emoji_name == "status_offline":
        return "<:status_offline:1564762688951812097>"
    if emoji_name == "status_streaming":
        return "<:status_streaming:1564762696795291850>"

    # Discord's account-age badges. The player and the profile popups only draw
    # the highest tier an account has reached; scripts/build-badge-art.mjs
    # rasterises the popup SVGs into these application emojis.
    if emoji_name == "account_age_seed":
        return "<:account_age_seed:1569000000000000001>"
    if emoji_name == "account_age_sprout":
        return "<:account_age_sprout:1569000000000000002>"
    if emoji_name == "account_age_bud":
        return "<:account_age_bud:1569000000000000003>"
    if emoji_name == "account_age_sapling":
        return "<:account_age_sapling:1569000000000000004>"
    if emoji_name == "account_age_blossom":
        return "<:account_age_blossom:1569000000000000005>"
    if emoji_name == "account_age_redwood":
        return "<:account_age_redwood:1569000000000000006>"
    if emoji_name == "account_age_sequoia":
        return "<:account_age_sequoia:1569000000000000007>"
    if emoji_name == "account_age_bristlecone":
        return "<:account_age_bristlecone:1569000000000000008>"
    if emoji_name == "account_age_stromatolite":
        return "<:account_age_stromatolite:1569000000000000009>"
    if emoji_name == "account_age_primordial":
        return "<:account_age_primordial:1569000000000000010>"

    # ==========================================================================
    # Niko role badges
    # ==========================================================================
    # One per team role and community role, drawn by scripts/build-badge-art.mjs;
    # the ids are placeholders the startup sync replaces once it uploads the PNGs.
    # The community roles needed new names for their refreshed art, because the
    # sync only uploads art for names it does not find yet and the originals were
    # already live.
    if emoji_name == "badge_owner":
        return "<:badge_owner:1564762276135960659>"
    if emoji_name == "badge_head_admin":
        return "<:badge_head_admin:1564762265775898744>"
    if emoji_name == "badge_head_support":
        return "<:badge_head_support:1564762268963442820>"
    if emoji_name == "badge_moderator":
        return "<:badge_moderator:1564762273023664212>"
    if emoji_name == "badge_event_coordinator":
        return "<:badge_event_coordinator:1564762259131990106>"
    if emoji_name == "badge_graphic_designer":
        return "<:badge_graphic_designer:1564762262047035447>"
    if emoji_name == "badge_partnership_manager":
        return "<:badge_partnership_manager:1564762279486955623>"
    # Discord emoji names stop at 32 characters, so the Partnerships &
    # Promotions Lead badge uses the short name for the same artwork.
    if emoji_name == "badge_partnership_lead":
        return "<:badge_partnership_lead:1564762282246799464>"
    if emoji_name == "badge_staff":
        return "<:badge_staff:1564762285543526451>"
    if emoji_name == "badge_support":
        return "<:badge_support:1564762288777334826>"
    if emoji_name == "badge_supporter_role":
        return "<:badge_supporter_role:1564762291788976128>"
    if emoji_name == "badge_bug_hunter_role":
        return "<:badge_bug_hunter_role:1564762294594961575>"
    if emoji_name == "badge_partner_role":
        return "<:badge_partner_role:1564762297937698957>"

    # ==========================================================================
    # Server boosting
    # ==========================================================================
    # The boost mark and one badge per tier, in tier order; the cards pick the one the
    # member's streak has reached.
    if emoji_name == "boost":
        return "<:boost:1564762417047543808>"
    if emoji_name == "boosting_1_months":
        return "<:boosting_1_months:1564762180933517345>"
    if emoji_name == "boosting_2_months":
        return "<:boosting_2_months:1564762184352010454>"
    if emoji_name == "boosting_3_months":
        return "<:boosting_3_months:1564762187808120942>"
    if emoji_name == "boosting_6_months":
        return "<:boosting_6_months:1564762190844526672>"
    if emoji_name == "boosting_9_months":
        return "<:boosting_9_months:1564762193520762965>"
    if emoji_name == "boosting_12_months":
        return "<:boosting_12_months:1564762197022736454>"
    if emoji_name == "boosting_15_months":
        return "<:boosting_15_months:1564762200030056578>"
    if emoji_name == "boosting_18_months":
        return "<:boosting_18_months:1564762203079450665>"
    if emoji_name == "boosting_24_months":
        return "<:boosting_24_months:1564762206116122774>"

    # ==========================================================================
    # Connect Four
    # ==========================================================================
    # Game sprites, owned by the Connect Four board rather than by an icon font. The
    # numbered pieces run in drop order.
    if emoji_name == "C4Empty":
        return "<:C4Empty:1564762307295191080>"
    if emoji_name == "C4Red":
        return "<a:C4Red:1564762310600429598>"
    if emoji_name == "C4Yellow":
        return "<a:C4Yellow:1564762341000741226>"
    if emoji_name == "C4Top1":
        return "<:C4Top1:1564762313574060103>"
    if emoji_name == "C4Top2":
        return "<:C4Top2:1564762316640227491>"
    if emoji_name == "C4Top3":
        return "<:C4Top3:1564762319555137638>"
    if emoji_name == "C4Top4":
        return "<:C4Top4:1564762325016256553>"
    if emoji_name == "C4Top5":
        return "<:C4Top5:1564762331177812128>"
    if emoji_name == "C4Top6":
        return "<:C4Top6:1564762334499447024>"
    if emoji_name == "C4Top7":
        return "<:C4Top7:1564762337729318972>"
    if emoji_name == "White1":
        return "<:White1:1564762748477247639>"
    if emoji_name == "White2":
        return "<:White2:1564762751706988594>"
    if emoji_name == "White3":
        return "<:White3:1564762754777354411>"
    if emoji_name == "White4":
        return "<:White4:1564762758199779338>"
    if emoji_name == "White5":
        return "<:White5:1564762762805252210>"
    if emoji_name == "White6":
        return "<:White6:1564762766332530718>"
    if emoji_name == "White7":
        return "<:White7:1564762769797025792>"

    # ==========================================================================
    # Server logs
    # ==========================================================================
    # One emoji per log message type so no two entries in a log channel share an icon,
    # grouped the way the logging cog groups them. The artwork comes from Lucide, and
    # the ids here are short on purpose: they are stubs the startup emoji sync replaces
    # with the live application-emoji id, and the website marks a short id as
    # not-yet-uploaded instead of requesting it from Discord's CDN.
    if emoji_name == "log_kick":
        return "<:log_kick:1564762780425265172>"
    if emoji_name == "log_ban":
        return "<:log_ban:1564762783537434816>"
    if emoji_name == "log_unban":
        return "<:log_unban:1564762786754601074>"
    if emoji_name == "log_warn":
        return "<:log_warn:1564762791490101268>"
    if emoji_name == "log_clear_warnings":
        return "<:log_clear_warnings:1564762794727968988>"
    if emoji_name == "log_mute":
        return "<:log_mute:1564762797903061172>"
    if emoji_name == "log_tempmute":
        return "<:log_tempmute:1564762800771834059>"
    if emoji_name == "log_unmute":
        return "<:log_unmute:1564762804542505123>"
    if emoji_name == "log_nickname":
        return "<:log_nickname:1564762808292348025>"
    if emoji_name == "log_timeout":
        return "<:log_timeout:1564762811513573386>"
    if emoji_name == "log_timeout_removed":
        return "<:log_timeout_removed:1564762814814359634>"
    if emoji_name == "log_clear":
        return "<:log_clear:1564762818522386523>"
    if emoji_name == "log_purge":
        return "<:log_purge:1564762821600874617>"
    if emoji_name == "log_lock":
        return "<:log_lock:1564762824721305660>"
    if emoji_name == "log_unlock":
        return "<:log_unlock:1564762827762442410>"

    if emoji_name == "log_anti_spam":
        return "<:log_anti_spam:1564762831285395616>"
    if emoji_name == "log_anti_link":
        return "<:log_anti_link:1564762834653421619>"
    if emoji_name == "log_bad_words":
        return "<:log_bad_words:1564762838348730469>"
    if emoji_name == "log_mass_mention":
        return "<:log_mass_mention:1564762842530447521>"
    if emoji_name == "log_nsfw_filter":
        return "<:log_nsfw_filter:1564762846003200152>"
    if emoji_name == "log_app_detected":
        return "<:log_app_detected:1564762849253785650>"
    if emoji_name == "log_app_action":
        return "<:log_app_action:1564762853158813868>"
    if emoji_name == "log_interaction_flood":
        return "<:log_interaction_flood:1564762857567035462>"
    if emoji_name == "log_anti_nuke":
        return "<:log_anti_nuke:1564762860796510338>"
    if emoji_name == "log_anti_raid":
        return "<:log_anti_raid:1564762864084975716>"

    if emoji_name == "log_message_deleted":
        return "<:log_message_deleted:1564762868367229000>"
    if emoji_name == "log_message_edited":
        return "<:log_message_edited:1564762872066740325>"

    if emoji_name == "log_channel_created":
        return "<:log_channel_created:1564762875292286976>"
    if emoji_name == "log_channel_deleted":
        return "<:log_channel_deleted:1564762878530289694>"
    if emoji_name == "log_channel_updated":
        return "<:log_channel_updated:1564762881562648778>"

    if emoji_name == "log_member_join":
        return "<:log_member_join:1564762884871954442>"
    if emoji_name == "log_member_leave":
        return "<:log_member_leave:1564762888114278410>"
    if emoji_name == "log_member_updated":
        return "<:log_member_updated:1564762891163271178>"
    if emoji_name == "log_avatar":
        return "<:log_avatar:1564762894799741019>"

    if emoji_name == "log_captcha_passed":
        return "<:log_captcha_passed:1564762899694616757>"
    if emoji_name == "log_captcha_failed":
        return "<:log_captcha_failed:1564762902752268294>"
    if emoji_name == "log_captcha_kicked":
        return "<:log_captcha_kicked:1564762906187268236>"

    if emoji_name == "log_invite_created":
        return "<:log_invite_created:1564762911543660755>"
    if emoji_name == "log_invite_deleted":
        return "<:log_invite_deleted:1564762914655838218>"
    if emoji_name == "log_invite_used":
        return "<:log_invite_used:1564762917717540934>"
    if emoji_name == "log_vanity_invite":
        return "<:log_vanity_invite:1564762920909275227>"
    if emoji_name == "log_unknown_join":
        return "<:log_unknown_join:1564762924235497502>"

    if emoji_name == "log_role_created":
        return "<:log_role_created:1564762927192477888>"
    if emoji_name == "log_role_deleted":
        return "<:log_role_deleted:1564762930929737880>"
    if emoji_name == "log_role_updated":
        return "<:log_role_updated:1564762934180188260>"

    if emoji_name == "log_server_updated":
        return "<:log_server_updated:1564762937422385333>"
    if emoji_name == "log_emoji_updated":
        return "<:log_emoji_updated:1564762940584886272>"
    if emoji_name == "log_sticker_updated":
        return "<:log_sticker_updated:1564762943562850485>"

    if emoji_name == "log_giveaway_ban":
        return "<:log_giveaway_ban:1565046599556800553>"
    if emoji_name == "log_giveaway_unban":
        return "<:log_giveaway_unban:1565046603130343424>"

    if emoji_name == "log_voice_join":
        return "<:log_voice_join:1564762946859434055>"
    if emoji_name == "log_voice_leave":
        return "<:log_voice_leave:1564762950630379520>"
    if emoji_name == "log_voice_move":
        return "<:log_voice_move:1564762955239784622>"

    # ==========================================================================
    # Platform logos
    # ==========================================================================
    # The bot itself, the platforms it is listed on and the services it talks to,
    # drawn from Simple Icons by scripts/build-emoji-icons.mjs.
    if emoji_name == "discord":
        return "<:discord:1565388699204587681>"
    if emoji_name == "github":
        return "<:github:1565386601809449094>"
    if emoji_name == "python":
        return "<:python:1565386611250696382>"
    if emoji_name == "topgg":
        return "<:topgg:1565386627021275256>"
    if emoji_name == "lastfm":
        return "<:lastfm:1565386608168009848>"
    if emoji_name == "spotify":
        return "<:spotify:1565386620935471347>"
    if emoji_name == "instagram":
        return "<:instagram:1565386605148119060>"
    if emoji_name == "tiktok":
        return "<:tiktok:1565386624081072138>"
    if emoji_name == "twitterx":
        return "<:twitterx:1565386633426247700>"
    if emoji_name == "youtube":
        return "<:youtube:1565386639738535953>"
    if emoji_name == "youtube_shorts":
        return "<:youtube_shorts:1565386642779406526>"
    if emoji_name == "reddit":
        return "<:reddit:1565386614598013059>"
    if emoji_name == "bluesky":
        return "<:bluesky:1565386562446032926>"
    if emoji_name == "soundcloud":
        return "<:soundcloud:1565386617764708463>"
    if emoji_name == "twitch":
        return "<:twitch:1565386629940781390>"
    if emoji_name == "wavelink":
        return "<:wavelink:1564762742030860320>"

    # ==========================================================================
    # Payments and cryptocurrencies
    # ==========================================================================
    # The card mark and the coin marks, from Web3 Icons' mono variant, so a payment
    # row reads as one set of icons instead of a row of differently-framed coins.
    if emoji_name == "oxapay":
        return "<:oxapay:1564762654499668011>"
    if emoji_name == "crypto_bitcoin":
        return "<:crypto_bitcoin:1565386569316045181>"
    if emoji_name == "crypto_ethereum":
        return "<:crypto_ethereum:1565386578883510405>"
    if emoji_name == "crypto_bnb":
        return "<:crypto_bnb:1565386572294127887>"
    if emoji_name == "crypto_dogecoin":
        return "<:crypto_dogecoin:1565386575393853541>"
    if emoji_name == "crypto_ltc":
        return "<:crypto_ltc:1565386582729687150>"
    if emoji_name == "crypto_monero":
        return "<:crypto_monero:1565386586072285346>"
    if emoji_name == "crypto_tether_usdt":
        return "<:crypto_tether_usdt:1565386589834584095>"
    if emoji_name == "crypto_tron":
        return "<:crypto_tron:1565386595513933944>"
