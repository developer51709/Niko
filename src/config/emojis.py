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
    if emoji_name == "active_developer_badge":
        return "<:active_developer_badge:1564757534718566554>"
    # Discord profile badges that Niko did not have emoji art for yet. Their
    # artwork is generated from the badge SVGs into src/assets/emojis/ by
    # scripts/build-badge-art.mjs, and the ids are placeholders: the startup
    # emoji sync uploads the PNGs and rewrites them with the live ids.
    # Discord's server-boosting badge has its own artwork per tier, so every
    # tier gets its own emoji and the cards pick the one the streak reached.
    if emoji_name == "boosting_1_months":
        return "<:boosting_1_months:1564757538061291670>"
    if emoji_name == "boosting_2_months":
        return "<:boosting_2_months:1564757541316202519>"
    if emoji_name == "boosting_3_months":
        return "<:boosting_3_months:1564757544449347594>"
    if emoji_name == "boosting_6_months":
        return "<:boosting_6_months:1564757547020460223>"
    if emoji_name == "boosting_9_months":
        return "<:boosting_9_months:1564757550723891240>"
    if emoji_name == "boosting_12_months":
        return "<:boosting_12_months:1564757553622294601>"
    if emoji_name == "boosting_15_months":
        return "<:boosting_15_months:1564757556868677645>"
    if emoji_name == "boosting_18_months":
        return "<:boosting_18_months:1564757560341303386>"
    if emoji_name == "boosting_24_months":
        return "<:boosting_24_months:1564757563302739990>"
    if emoji_name == "bug_hunter_badge":
        return "<:bug_hunter_badge:1564757566880489594>"
    if emoji_name == "bug_hunter_gold_badge":
        return "<:bug_hunter_gold_badge:1564757569891733535>"
    if emoji_name == "certified_moderator_badge":
        return "<:certified_moderator_badge:1564757573083734136>"
    if emoji_name == "early_supporter_badge":
        return "<:early_supporter_badge:1564757586073489448>"
    if emoji_name == "hypesquad_events":
        return "<:hypesquad_events:1564757588917227603>"
    if emoji_name == "partner_badge":
        return "<:partner_badge:1564757592276861109>"
    if emoji_name == "staff_badge":
        return "<:staff_badge:1564757595275657367>"
    if emoji_name == "supports_commands_badge":
        return "<:supports_commands_badge:1564757598329241672>"
    if emoji_name == "arrow_left":
        return "<:arrow_left:1564757601277968445>"
    if emoji_name == "arrow_right":
        return "<:arrow_right:1564757604314644550>"
    if emoji_name == "automod":
        return "<:Automod:1564757607758172253>"
    # Niko's own role badges, one per team role plus the community roles. The
    # artwork is generated from web/public/assets/badges/niko_*.svg into
    # src/assets/emojis/badge_*.png by scripts/build-badge-art.mjs, and these
    # placeholder ids are replaced by the sync once it uploads them.
    if emoji_name == "badge_event_coordinator":
        return "<:badge_event_coordinator:1564757611130388596>"
    if emoji_name == "badge_graphic_designer":
        return "<:badge_graphic_designer:1564757614745747486>"
    if emoji_name == "badge_head_admin":
        return "<:badge_head_admin:1564757618063442002>"
    if emoji_name == "badge_head_support":
        return "<:badge_head_support:1564757621267767346>"
    if emoji_name == "badge_moderator":
        return "<:badge_moderator:1564757624841441385>"
    if emoji_name == "badge_owner":
        return "<:badge_owner:1564757628398211102>"
    if emoji_name == "badge_partnership_manager":
        return "<:badge_partnership_manager:1564757631539609691>"
    # Discord emoji names stop at 32 characters, so the Partnerships &
    # Promotions Lead badge uses the short name for the same artwork.
    if emoji_name == "badge_partnership_lead":
        return "<:badge_partnership_lead:1564757634324766863>"
    if emoji_name == "badge_staff":
        return "<:badge_staff:1564757639290687608>"
    if emoji_name == "badge_support":
        return "<:badge_support:1564757642382147604>"
    # The community role badges, with the refreshed artwork. Their original
    # names (badge_supporter, badge_bugbounty, badge_partner) are already live
    # application emojis, and the sync only uploads art for names it does not
    # find yet, so the new art needs its own names to reach Discord.
    if emoji_name == "badge_supporter_role":
        return "<:badge_supporter_role:1564757645389205594>"
    if emoji_name == "badge_bug_hunter_role":
        return "<:badge_bug_hunter_role:1564757648342130730>"
    if emoji_name == "badge_partner_role":
        return "<:badge_partner_role:1564757651881988250>"
    if emoji_name == "bluesky":
        return "<:bluesky:1564757655174520842>"
    if emoji_name == "broom":
        return "<:broom:1564757658165321841>"
    if emoji_name == "C4Empty":
        return "<:C4Empty:1564757661243932732>"
    if emoji_name == "C4Red":
        return "<a:C4Red:1564757664376950864>"
    if emoji_name == "C4Top1":
        return "<:C4Top1:1564757667405103134>"
    if emoji_name == "C4Top2":
        return "<:C4Top2:1564757670710222868>"
    if emoji_name == "C4Top3":
        return "<:C4Top3:1564757674036559962>"
    if emoji_name == "C4Top4":
        return "<:C4Top4:1564757676951605432>"
    if emoji_name == "C4Top5":
        return "<:C4Top5:1564757681477259324>"
    if emoji_name == "C4Top6":
        return "<:C4Top6:1564757684610277416>"
    if emoji_name == "C4Top7":
        return "<:C4Top7:1564757687680499902>"
    if emoji_name == "C4Yellow":
        return "<a:C4Yellow:1564757691023360043>"
    if emoji_name == "cpu":
        return "<:cpu:1564757694068428911>"
    if emoji_name == "credit_card":
        return "<a:credit_card:1564757697822335176>"
    if emoji_name == "crypto_bitcoin":
        return "<:crypto_bitcoin:1564757701358125199>"
    if emoji_name == "crypto_bnb":
        return "<:crypto_bnb:1564757705124483125>"
    if emoji_name == "crypto_dogecoin":
        return "<:crypto_dogecoin:1564757711982432336>"
    if emoji_name == "crypto_ethereum":
        return "<:crypto_ethereum:1564757714603868181>"
    if emoji_name == "crypto_ltc":
        return "<:crypto_ltc:1564757722493231364>"
    if emoji_name == "crypto_monero":
        return "<:crypto_monero:1564757725689421844>"
    if emoji_name == "crypto_tether_usdt":
        return "<:crypto_tether_usdt:1564757729057177731>"
    if emoji_name == "crypto_tron":
        return "<:crypto_tron:1564757732416815146>"
    if emoji_name == "dbl":
        return "<:dbl:1564757735394779208>"
    if emoji_name == "disconnect":
        return "<:disconnect:1564757738427261120>"
    if emoji_name == "discord":
        return "<a:discord:1564757741887819838>"
    if emoji_name == "gift":
        return "<:gift:1564757745079685210>"
    if emoji_name == "github":
        return "<:github:1564757748175085679>"
    if emoji_name == "hypesquad_balance":
        return "<:hypesquad_balance:1564757751324999762>"
    if emoji_name == "hypesquad_bravery":
        return "<:hypesquad_bravery:1564757754340446278>"
    if emoji_name == "hypesquad_briliance":
        return "<:hypesquad_briliance:1564757757599678577>"
    if emoji_name == "ai":
        return "<:ai:1564757760594288782>"
    if emoji_name == "ban":
        return "<:ban:1564757765535301692>"
    if emoji_name == "boost":
        return "<:boost:1564757768517197976>"
    if emoji_name == "bot":
        return "<:bot:1564757771587428363>"
    if emoji_name == "bug":
        return "<:bug:1564757774565642240>"
    if emoji_name == "categories":
        return "<:categories:1564757777807573032>"
    if emoji_name == "cross":
        return "<:cross:1564757780886331565>"
    if emoji_name == "danger":
        return "<:danger:1564757784367464619>"
    if emoji_name == "disk":
        return "<:disk:1564757787571916950>"
    if emoji_name == "docs":
        return "<:docs:1564757790520647750>"
    if emoji_name == "economy":
        return "<:economy:1564757793175769171>"
    if emoji_name == "edit":
        return "<:edit:1564757797399171092>"
    if emoji_name == "games":
        return "<:games:1564757800368738455>"
    if emoji_name == "gambling":
        return "<:gambling:1564757803321659532>"
    if emoji_name == "general":
        return "<:general:1564757806412726413>"
    if emoji_name == "giveaway":
        return "<:giveaway:1564757809441284306>"
    if emoji_name == "heart":
        return "<:heart:1564757812360257688>"
    if emoji_name == "home":
        return "<:home:1564757815371894855>"
    if emoji_name == "host":
        return "<:host:1564757818483937310>"
    if emoji_name == "image":
        return "<:image:1564757821281673359>"
    if emoji_name == "important":
        return "<:important:1564757824742105134>"
    if emoji_name == "invite":
        return "<:invite:1564757828017852518>"
    if emoji_name == "join":
        return "<:join:1564757831255719956>"
    if emoji_name == "leave":
        return "<:leave:1564757834258849932>"
    if emoji_name == "leveling":
        return "<:leveling:1564757837228413038>"
    if emoji_name == "lightbulb":
        return "<:lightbulb:1564757840130736192>"
    if emoji_name == "link":
        return "<:link:1564757843150639134>"
    if emoji_name == "loading":
        return "<a:loading:1564757846275399780>"
    if emoji_name == "loop":
        return "<:loop:1564757849341694063>"
    if emoji_name == "megaphone":
        return "<:megaphone:1564757852487426091>"
    if emoji_name == "message":
        return "<:message:1564757855570100415>"
    if emoji_name == "minus":
        return "<:minus:1564757858623684718>"
    if emoji_name == "moderation":
        return "<:moderation:1564757861462970400>"
    if emoji_name == "nsfw":
        return "<:nsfw:1564757864906625054>"
    if emoji_name == "paint":
        return "<:paint:1564757867905683605>"
    if emoji_name == "pause":
        return "<:pause:1564757871625900183>"
    if emoji_name == "play":
        return "<:play:1564757875816005804>"
    if emoji_name == "plus":
        return "<:plus:1564757878680584365>"
    if emoji_name == "premium":
        return "<:premium:1564757887459393567>"
    if emoji_name == "question":
        return "<:question:1564757890798059540>"
    if emoji_name == "refresh":
        return "<:refresh:1564757893851643964>"
    if emoji_name == "reminder":
        return "<:reminder:1564757899773739248>"
    if emoji_name == "roleplay":
        return "<:roleplay:1564757902869397624>"
    if emoji_name == "rewind":
        return "<:rewind:1564757906082111509>"
    if emoji_name == "settings":
        return "<:settings:1564757908762132504>"
    if emoji_name == "shuffle":
        return "<:shuffle:1564757912667295894>"
    if emoji_name == "skip":
        return "<:skip:1564757916190253126>"
    if emoji_name == "stats":
        return "<:stats:1564757920271564921>"
    if emoji_name == "stop":
        return "<:stop:1564757925069717514>"
    if emoji_name == "support":
        return "<:support:1564757928072978532>"
    if emoji_name == "tick":
        return "<:tick:1564757931323293806>"
    if emoji_name == "ticket":
        return "<:ticket:1564757934284611738>"
    if emoji_name == "trash":
        return "<:trash:1564757938923638814>"
    if emoji_name == "utility":
        return "<:utility:1564757942232686612>"
    if emoji_name == "user":
        return "<:user:1564757945378410580>"
    if emoji_name == "verified":
        return "<:verified:1564757948452962375>"
    if emoji_name == "welcome":
        return "<:welcome:1564757952420647004>"
    if emoji_name == "wumpus":
        return "<:wumpus:1564757958091604110>"
    if emoji_name == "instagram":
        return "<:instagram:1564757961480343716>"
    if emoji_name == "lastfm":
        return "<:lastfm:1564757964622012519>"
    if emoji_name == "music":
        return "<:music:1564757967650295998>"
    if emoji_name == "notepad":
        return "<:notepad:1564757971412721688>"
    if emoji_name == "number_eight":
        return "<:number_eight:1564757974919151646>"
    if emoji_name == "number_five":
        return "<:number_five:1564757977968283689>"
    if emoji_name == "number_four":
        return "<:number_four:1564757981210607687>"
    if emoji_name == "number_nine":
        return "<:number_nine:1564757984263798784>"
    if emoji_name == "number_one":
        return "<:number_one:1564757987325903060>"
    if emoji_name == "number_seven":
        return "<:number_seven:1564757990396137652>"
    if emoji_name == "number_six":
        return "<:number_six:1564757993264910357>"
    if emoji_name == "number_three":
        return "<:number_three:1564757996490334249>"
    if emoji_name == "number_two":
        return "<:number_two:1564758000512536607>"
    if emoji_name == "number_zero":
        return "<:number_zero:1564758007764754522>"
    if emoji_name == "owner_icon":
        return "<:owner_icon:1564758012453855323>"
    if emoji_name == "oxapay":
        return "<:oxapay:1564758015549374585>"
    if emoji_name == "pingpong":
        return "<:pingpong:1564758018610962463>"
    if emoji_name == "python":
        return "<:python:1564758021538717746>"
    if emoji_name == "ram":
        return "<:ram:1564758024378253444>"
    if emoji_name == "reddit":
        return "<:reddit:1564758027670786159>"
    if emoji_name == "scroll":
        return "<:scroll:1564758030695010466>"
    if emoji_name == "soundcloud":
        return "<:soundcloud:1564758033991733298>"
    if emoji_name == "spotify":
        return "<:spotify:1564758037246513242>"
    if emoji_name == "star":
        return "<:star:1564758040073469973>"
    if emoji_name == "status_dnd":
        return "<:status_dnd:1564758043403624532>"
    if emoji_name == "status_idle":
        return "<:status_idle:1564758046696276180>"
    if emoji_name == "status_offline":
        return "<:status_offline:1564758050013974619>"
    if emoji_name == "status_online":
        return "<:status_online:1564758053079875635>"
    if emoji_name == "status_streaming":
        return "<:status_streaming:1564758057236562171>"
    if emoji_name == "thumbs_down":
        return "<:thumbs_down:1564758060130373746>"
    if emoji_name == "thumbs_up":
        return "<:thumbs_up:1564758063578226818>"
    if emoji_name == "tiktok":
        return "<:tiktok:1564758066598125628>"
    if emoji_name == "topgg":
        return "<:topgg:1564758070033391800>"
    if emoji_name == "twitch":
        return "<:twitch:1564758073229320412>"
    if emoji_name == "twitterx":
        return "<:twitterx:1564758076421308529>"
    if emoji_name == "voicemaster":
        return "<:voicemaster:1564758079546065132>"
    if emoji_name == "verified_developer_badge":
        return "<:verified_developer_badge:1564758083165622292>"
    if emoji_name == "hide":
        return "<:hide:1564758085954965556>"
    if emoji_name == "lock":
        return "<:lock:1564758089159282850>"
    if emoji_name == "unhide":
        return "<:unhide:1564758092380377240>"
    if emoji_name == "unlock":
        return "<:unlock:1564758095568183317>"
    if emoji_name == "warning":
        return "<:warning:1564758098764238878>"
    if emoji_name == "wavelink":
        return "<:wavelink:1564758101838532608>"
    if emoji_name == "website":
        return "<:website:1564758105215078510>"
    if emoji_name == "White1":
        return "<:White1:1564758108243366070>"
    if emoji_name == "White2":
        return "<:White2:1564758111741411378>"
    if emoji_name == "White3":
        return "<:White3:1564758114962640896>"
    if emoji_name == "White4":
        return "<:White4:1564758118083203204>"
    if emoji_name == "White5":
        return "<:White5:1564758121342308392>"
    if emoji_name == "White6":
        return "<:White6:1564758124169003080>"
    if emoji_name == "White7":
        return "<:White7:1564758127717654538>"
    if emoji_name == "youtube":
        return "<:youtube:1564758130829824081>"
    if emoji_name == "youtube_shorts":
        return "<:youtube_shorts:1564758133648392316>"
    # Server-log emojis, one per log message type so no two log entries ever
    # share an icon. The artwork is generated from Lucide icons into
    # src/assets/emojis/ by scripts/build-emoji-icons.mjs, and the ids below are
    # stubs: the startup emoji sync uploads each PNG and rewrites the stub with
    # the live application-emoji id. They are short on purpose so the website's
    # rendering lab marks them as not-yet-uploaded and never requests a
    # placeholder id from Discord's CDN.
    if emoji_name == "log_kick":
        return "<:log_kick:1564758138094227656>"
    if emoji_name == "log_ban":
        return "<:log_ban:1564758140778447020>"
    if emoji_name == "log_unban":
        return "<:log_unban:1564758144473894994>"
    if emoji_name == "log_warn":
        return "<:log_warn:1564758147296665631>"
    if emoji_name == "log_clear_warnings":
        return "<:log_clear_warnings:1564758150664429658>"
    if emoji_name == "log_mute":
        return "<:log_mute:1564758154112405604>"
    if emoji_name == "log_tempmute":
        return "<:log_tempmute:1564758157966835755>"
    if emoji_name == "log_unmute":
        return "<:log_unmute:1564758160995254327>"
    if emoji_name == "log_nickname":
        return "<:log_nickname:1564758164602232903>"
    if emoji_name == "log_timeout":
        return "<:log_timeout:1564758167941021716>"
    if emoji_name == "log_timeout_removed":
        return "<:log_timeout_removed:1564758171174703204>"
    if emoji_name == "log_clear":
        return "<:log_clear:1564758174349922414>"
    if emoji_name == "log_purge":
        return "<:log_purge:1564758177692516404>"
    if emoji_name == "log_lock":
        return "<:log_lock:1564758181370921071>"
    if emoji_name == "log_unlock":
        return "<:log_unlock:1564758184470651041>"
    if emoji_name == "log_anti_spam":
        return "<:log_anti_spam:1564758187519910069>"
    if emoji_name == "log_anti_link":
        return "<:log_anti_link:1564758190263115918>"
    if emoji_name == "log_bad_words":
        return "<:log_bad_words:1564758194021212192>"
    if emoji_name == "log_mass_mention":
        return "<:log_mass_mention:1564758197082919015>"
    if emoji_name == "log_nsfw_filter":
        return "<:log_nsfw_filter:1564758200052359168>"
    if emoji_name == "log_app_detected":
        return "<:log_app_detected:1564758203106074634>"
    if emoji_name == "log_app_action":
        return "<:log_app_action:1564758206087962627>"
    if emoji_name == "log_interaction_flood":
        return "<:log_interaction_flood:1564758209229627544>"
    if emoji_name == "log_anti_nuke":
        return "<:log_anti_nuke:1564758212291334314>"
    if emoji_name == "log_anti_raid":
        return "<:log_anti_raid:1564758215395250347>"
    if emoji_name == "log_message_deleted":
        return "<:log_message_deleted:1564758219673571379>"
    if emoji_name == "log_message_edited":
        return "<:log_message_edited:1564758222513111051>"
    if emoji_name == "log_channel_created":
        return "<:log_channel_created:1564758225734205531>"
    if emoji_name == "log_channel_deleted":
        return "<:log_channel_deleted:1564758229156761620>"
    if emoji_name == "log_channel_updated":
        return "<:log_channel_updated:1564758232302489785>"
    if emoji_name == "log_member_join":
        return "<:log_member_join:1564758235418992701>"
    if emoji_name == "log_member_leave":
        return "<:log_member_leave:1564758238702862416>"
    if emoji_name == "log_member_updated":
        return "<:log_member_updated:1564758241894994101>"
    if emoji_name == "log_avatar":
        return "<:log_avatar:1564758245137059902>"
    if emoji_name == "log_captcha_passed":
        return "<:log_captcha_passed:1564758248332984420>"
    if emoji_name == "log_captcha_failed":
        return "<:log_captcha_failed:1564758251684495455>"
    if emoji_name == "log_captcha_kicked":
        return "<:log_captcha_kicked:1564758255547187231>"
    if emoji_name == "log_invite_created":
        return "<:log_invite_created:1564758258676142191>"
    if emoji_name == "log_invite_deleted":
        return "<:log_invite_deleted:1564758261784383538>"
    if emoji_name == "log_invite_used":
        return "<:log_invite_used:1564758265144016996>"
    if emoji_name == "log_vanity_invite":
        return "<:log_vanity_invite:1564758267954204838>"
    if emoji_name == "log_unknown_join":
        return "<:log_unknown_join:1564758271326298162>"
    if emoji_name == "log_role_created":
        return "<:log_role_created:1564758274925002852>"
    if emoji_name == "log_role_deleted":
        return "<:log_role_deleted:1564758278380978257>"
    if emoji_name == "log_role_updated":
        return "<:log_role_updated:1564758281530900581>"
    if emoji_name == "log_server_updated":
        return "<:log_server_updated:1564758284550938755>"
    if emoji_name == "log_emoji_updated":
        return "<:log_emoji_updated:1564758287654588607>"
    if emoji_name == "log_sticker_updated":
        return "<:log_sticker_updated:1564758290775408710>"
    if emoji_name == "log_voice_join":
        return "<:log_voice_join:1564758293665292301>"
    if emoji_name == "log_voice_leave":
        return "<:log_voice_leave:1564758296982716568>"
    if emoji_name == "log_voice_move":
        return "<:log_voice_move:1564758301076365453>"
    if emoji_name == "enabled":
        return "<:disable_no:1564758304125751337><:enable_yes:1564758307149971466>"
    if emoji_name == "disabled":
        return "<:disable_yes:1564758311059067032><:enable_no:1564758314011598939>"
