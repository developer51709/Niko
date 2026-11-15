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

from utils.emoji_seasons import seasonal_variant

# An emoji as it appears in a message: <:name:id> or <a:name:id>.
_EMOJI_REF = re.compile(r"<(a?):([A-Za-z0-9_]+):(\d+)>")

# Old id → the emoji string that replaced it, filled in by the sync. Keyed by
# id rather than by name because one key can return more than one emoji
# (``enabled``) and a few keys name a different Discord name than the key
# itself (``automod`` → ``Automod``).
_LIVE_IDS: dict[int, str] = {}

# Seasonal variant names are literal strings so parse_config() can find
# every one in the source file. These are the production application-emoji
# ids, so a fresh checkout and the live bot agree. State indicators and log
# marks stay unseasonal; the bases here are the general-purpose emojis.
_SEASONAL_EMOJI_IDS = {
    "heart_christmas": "<:heart_christmas:1571269830923780096>",
    "heart_halloween": "<:heart_halloween:1571269862297305270>",
    "heart_valentine": "<:heart_valentine:1571269899559505990>",
    "gift_christmas": "<:gift_christmas:1571269834115776622>",
    "gift_halloween": "<:gift_halloween:1571269865749348482>",
    "gift_valentine": "<:gift_valentine:1571269902436802591>",
    "star_christmas": "<:star_christmas:1571269837668360202>",
    "star_halloween": "<:star_halloween:1571269869268246550>",
    "star_valentine": "<:star_valentine:1571269906043904031>",
    "welcome_christmas": "<:welcome_christmas:1571269840809889812>",
    "welcome_halloween": "<:welcome_halloween:1571269872522891374>",
    "welcome_valentine": "<:welcome_valentine:1571269909097218238>",
    "giveaway_christmas": "<:giveaway_christmas:1571269843930583060>",
    "giveaway_halloween": "<:giveaway_halloween:1571269880127422626>",
    "giveaway_valentine": "<:giveaway_valentine:1571269913891311806>",
    "premium_christmas": "<:premium_christmas:1571269847034232912>",
    "premium_halloween": "<:premium_halloween:1571269883268956323>",
    "premium_valentine": "<:premium_valentine:1571269916999286885>",
    "ticket_christmas": "<:ticket_christmas:1571269850108661851>",
    "ticket_halloween": "<:ticket_halloween:1571269886166966296>",
    "ticket_valentine": "<:ticket_valentine:1571269920006607041>",
    "trophy_christmas": "<:trophy_christmas:1571269853367636178>",
    "trophy_halloween": "<:trophy_halloween:1571269889522409514>",
    "trophy_valentine": "<:trophy_valentine:1571269922934231162>",
    "economy_christmas": "<:economy_christmas:1571269856312033360>",
    "economy_halloween": "<:economy_halloween:1571269893012324493>",
    "economy_valentine": "<:economy_valentine:1571269925992141012>",
    "games_christmas": "<:games_christmas:1571269859507966012>",
    "games_halloween": "<:games_halloween:1571269896396873809>",
    "games_valentine": "<:games_valentine:1571269929284669622>",
    "edit_christmas": "<:edit_christmas:1571277721835933736>",
    "edit_halloween": "<:edit_halloween:1571277725224796161>",
    "edit_valentine": "<:edit_valentine:1571277728940953631>",
    "trash_christmas": "<:trash_christmas:1571277732904444215>",
    "trash_halloween": "<:trash_halloween:1571277736104951983>",
    "trash_valentine": "<:trash_valentine:1571277739472847088>",
    "broom_christmas": "<:broom_christmas:1571277742484361257>",
    "broom_halloween": "<:broom_halloween:1571277746162766004>",
    "broom_valentine": "<:broom_valentine:1571277749270872215>",
    "moderation_christmas": "<:moderation_christmas:1571277752303099924>",
    "moderation_halloween": "<:moderation_halloween:1571277755113275445>",
    "moderation_valentine": "<:moderation_valentine:1571277758330445936>",
    "automod_christmas": "<:automod_christmas:1571277761354535094>",
    "automod_halloween": "<:automod_halloween:1571277764735279236>",
    "automod_valentine": "<:automod_valentine:1571277768170283038>",
    "utility_christmas": "<:utility_christmas:1571277770905096308>",
    "utility_halloween": "<:utility_halloween:1571277777070460998>",
    "utility_valentine": "<:utility_valentine:1571277780077903974>",
    "home_christmas": "<:home_christmas:1571277783114580109>",
    "home_halloween": "<:home_halloween:1571277790089711807>",
    "home_valentine": "<:home_valentine:1571277793646354593>",
    "general_christmas": "<:general_christmas:1571277796657991682>",
    "general_halloween": "<:general_halloween:1571277800063631481>",
    "general_valentine": "<:general_valentine:1571277803473862847>",
    "categories_christmas": "<:categories_christmas:1571277806497693756>",
    "categories_halloween": "<:categories_halloween:1571277809559543960>",
    "categories_valentine": "<:categories_valentine:1571277812642480298>",
    "settings_christmas": "<:settings_christmas:1571277815670636685>",
    "settings_halloween": "<:settings_halloween:1571277818854252635>",
    "settings_valentine": "<:settings_valentine:1571277821664567378>",
    "docs_christmas": "<:docs_christmas:1571277825191972945>",
    "docs_halloween": "<:docs_halloween:1571277827825860619>",
    "docs_valentine": "<:docs_valentine:1571277831084834969>",
    "website_christmas": "<:website_christmas:1571277834478034944>",
    "website_halloween": "<:website_halloween:1571277838471139449>",
    "website_valentine": "<:website_valentine:1571277845299204258>",
    "notepad_christmas": "<:notepad_christmas:1571277848503787540>",
    "notepad_halloween": "<:notepad_halloween:1571277851511230664>",
    "notepad_valentine": "<:notepad_valentine:1571277854669283408>",
    "scroll_christmas": "<:scroll_christmas:1571277858599477389>",
    "scroll_halloween": "<:scroll_halloween:1571277861875228812>",
    "scroll_valentine": "<:scroll_valentine:1571277864966299771>",
    "stats_christmas": "<:stats_christmas:1571277867994714252>",
    "stats_halloween": "<:stats_halloween:1571277871111213116>",
    "stats_valentine": "<:stats_valentine:1571277874348957736>",
    "support_christmas": "<:support_christmas:1571277877087834215>",
    "support_halloween": "<:support_halloween:1571277880477089832>",
    "support_valentine": "<:support_valentine:1571277883484414063>",
    "arrow_left_christmas": "<:arrow_left_christmas:1571277886474813520>",
    "arrow_left_halloween": "<:arrow_left_halloween:1571277889763147796>",
    "arrow_left_valentine": "<:arrow_left_valentine:1571277892896292934>",
    "arrow_right_christmas": "<:arrow_right_christmas:1571277895928647791>",
    "arrow_right_halloween": "<:arrow_right_halloween:1571277904120250368>",
    "arrow_right_valentine": "<:arrow_right_valentine:1571277907287085211>",
    "user_christmas": "<:user_christmas:1571277910420099182>",
    "user_halloween": "<:user_halloween:1571277913461100586>",
    "user_valentine": "<:user_valentine:1571277916611022949>",
    "join_christmas": "<:join_christmas:1571277919878381588>",
    "join_halloween": "<:join_halloween:1571277922915061920>",
    "join_valentine": "<:join_valentine:1571277926429630554>",
    "leave_christmas": "<:leave_christmas:1571277929902776602>",
    "leave_halloween": "<:leave_halloween:1571277932671016982>",
    "leave_valentine": "<:leave_valentine:1571277936001286204>",
    "invite_christmas": "<:invite_christmas:1571277939104944181>",
    "invite_halloween": "<:invite_halloween:1571277942871564579>",
    "invite_valentine": "<:invite_valentine:1571277945874686094>",
    "participants_christmas": "<:participants_christmas:1571277949393576030>",
    "participants_halloween": "<:participants_halloween:1571277954854686720>",
    "participants_valentine": "<:participants_valentine:1571277957996220416>",
    "message_christmas": "<:message_christmas:1571277961083101234>",
    "message_halloween": "<:message_halloween:1571277964463579196>",
    "message_valentine": "<:message_valentine:1571277967525413025>",
    "image_christmas": "<:image_christmas:1571277970499305564>",
    "image_halloween": "<:image_halloween:1571277973598904360>",
    "image_valentine": "<:image_valentine:1571277976987766935>",
    "link_christmas": "<:link_christmas:1571277980087619735>",
    "link_halloween": "<:link_halloween:1571277983014977671>",
    "link_valentine": "<:link_valentine:1571277986739781752>",
    "megaphone_christmas": "<:megaphone_christmas:1571277989881053256>",
    "megaphone_halloween": "<:megaphone_halloween:1571277992833978488>",
    "megaphone_valentine": "<:megaphone_valentine:1571277995883237467>",
    "lightbulb_christmas": "<:lightbulb_christmas:1571277999121104946>",
    "lightbulb_halloween": "<:lightbulb_halloween:1571278002191466656>",
    "lightbulb_valentine": "<:lightbulb_valentine:1571278005630668810>",
    "ai_christmas": "<:ai_christmas:1571278008797364387>",
    "ai_halloween": "<:ai_halloween:1571278011859468410>",
    "ai_valentine": "<:ai_valentine:1571278014770188439>",
    "bot_christmas": "<:bot_christmas:1571278018138214472>",
    "bot_halloween": "<:bot_halloween:1571278021296525352>",
    "bot_valentine": "<:bot_valentine:1571278028993069086>",
    "bug_christmas": "<:bug_christmas:1571278031979544707>",
    "bug_halloween": "<:bug_halloween:1571278035347443913>",
    "bug_valentine": "<:bug_valentine:1571278038765674628>",
    "sad_christmas": "<:sad_christmas:1571278041475317934>",
    "sad_halloween": "<:sad_halloween:1571278044868640799>",
    "sad_valentine": "<:sad_valentine:1571278047997591612>",
    "play_christmas": "<:play_christmas:1571278051462086718>",
    "play_halloween": "<:play_halloween:1571278054632722442>",
    "play_valentine": "<:play_valentine:1571278060295159941>",
    "pause_christmas": "<:pause_christmas:1571278063486898216>",
    "pause_halloween": "<:pause_halloween:1571278066314121371>",
    "pause_valentine": "<:pause_valentine:1571278069774159912>",
    "stop_christmas": "<:stop_christmas:1571278072815034549>",
    "stop_halloween": "<:stop_halloween:1571278076149637131>",
    "stop_valentine": "<:stop_valentine:1571278079261671424>",
    "skip_christmas": "<:skip_christmas:1571278082642411712>",
    "skip_halloween": "<:skip_halloween:1571278085742137520>",
    "skip_valentine": "<:skip_valentine:1571278089084735488>",
    "rewind_christmas": "<:rewind_christmas:1571278092142518472>",
    "rewind_halloween": "<:rewind_halloween:1571278095346827505>",
    "rewind_valentine": "<:rewind_valentine:1571278098358607972>",
    "shuffle_christmas": "<:shuffle_christmas:1571278101164593397>",
    "shuffle_halloween": "<:shuffle_halloween:1571278104385556521>",
    "shuffle_valentine": "<:shuffle_valentine:1571278107845992529>",
    "loop_christmas": "<:loop_christmas:1571278110844784680>",
    "loop_halloween": "<:loop_halloween:1571278113944375326>",
    "loop_valentine": "<:loop_valentine:1571278117845213274>",
    "queue_christmas": "<:queue_christmas:1571278121141805277>",
    "queue_halloween": "<:queue_halloween:1571278124140728471>",
    "queue_valentine": "<:queue_valentine:1571278127605481535>",
    "volume_down_christmas": "<:volume_down_christmas:1571278130746761318>",
    "volume_down_halloween": "<:volume_down_halloween:1571278134068908303>",
    "volume_down_valentine": "<:volume_down_valentine:1571278137097060594>",
    "volume_up_christmas": "<:volume_up_christmas:1571278140032942222>",
    "volume_up_halloween": "<:volume_up_halloween:1571278143027679352>",
    "volume_up_valentine": "<:volume_up_valentine:1571278146232262668>",
    "autoplay_christmas": "<:autoplay_christmas:1571278149176655902>",
    "autoplay_halloween": "<:autoplay_halloween:1571278154994028594>",
    "autoplay_valentine": "<:autoplay_valentine:1571278158454595644>",
    "refresh_christmas": "<:refresh_christmas:1571278161772290219>",
    "refresh_halloween": "<:refresh_halloween:1571278165161017504>",
    "refresh_valentine": "<:refresh_valentine:1571278168478715936>",
    "music_christmas": "<:music_christmas:1571278171847000145>",
    "music_halloween": "<:music_halloween:1571278175432867960>",
    "music_valentine": "<:music_valentine:1571278178461155458>",
    "voicemaster_christmas": "<:voicemaster_christmas:1571278181476864190>",
    "voicemaster_halloween": "<:voicemaster_halloween:1571278184480243863>",
    "voicemaster_valentine": "<:voicemaster_valentine:1571278187445620909>",
    "disconnect_christmas": "<:disconnect_christmas:1571278190893211852>",
    "disconnect_halloween": "<:disconnect_halloween:1571278193749524701>",
    "disconnect_valentine": "<:disconnect_valentine:1571278196710834228>",
    "leveling_christmas": "<:leveling_christmas:1571278199680274555>",
    "leveling_halloween": "<:leveling_halloween:1571278203371393164>",
    "leveling_valentine": "<:leveling_valentine:1571278206466789437>",
    "gambling_christmas": "<:gambling_christmas:1571278209453138030>",
    "gambling_halloween": "<:gambling_halloween:1571278212565045268>",
    "gambling_valentine": "<:gambling_valentine:1571278215610241054>",
    "paint_christmas": "<:paint_christmas:1571278231032701088>",
    "paint_halloween": "<:paint_halloween:1571278234434150480>",
    "paint_valentine": "<:paint_valentine:1571278237076562044>",
    "reminder_christmas": "<:reminder_christmas:1571278240553635870>",
    "reminder_halloween": "<:reminder_halloween:1571278243548635167>",
    "reminder_valentine": "<:reminder_valentine:1571278246513873019>",
    "duration_christmas": "<:duration_christmas:1571278249873641643>",
    "duration_halloween": "<:duration_halloween:1571278253069439080>",
    "duration_valentine": "<:duration_valentine:1571278256190128128>",
}

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
    # Seasonal variants are separate uploaded emojis. Picking one by date is a
    # lookup change, not a Discord edit, so the switch happens with the season
    # and the base emoji is used again as soon as the window closes.
    variant = seasonal_variant(emoji_name)
    if variant:
        emoji_name = variant

    # ==========================================================================
    # Status and feedback
    # ==========================================================================
    # Outcomes and labels. A pass is green, a failure or a removal red, a caution
    # orange; everything that only labels something is the one neutral ink.
    if emoji_name == "tick":
        return "<:tick:1571271785637220502>"
    if emoji_name == "cross":
        return "<:cross:1571271788602728518>"
    if emoji_name == "warning":
        return "<:warning:1571271791727353989>"
    if emoji_name == "danger":
        return "<:danger:1571271794839654531>"
    if emoji_name == "important":
        return "<:important:1571271797889044612>"
    if emoji_name == "question":
        return "<:question:1571271801936289933>"
    if emoji_name == "plus":
        return "<:plus:1571271805363294358>"
    if emoji_name == "minus":
        return "<:minus:1571271808403898610>"
    if emoji_name == "thumbs_up":
        return "<:thumbs_up:1571271811365339207>"
    if emoji_name == "thumbs_down":
        return "<:thumbs_down:1571271814624182382>"
    if emoji_name == "verified":
        return "<:verified:1571271818231160952>"
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
        return "<:moderation:1571271821238599720>"
    if emoji_name == "automod":
        return "<:Automod:1564762255667765383>"
    if emoji_name == "ban":
        return "<:ban:1571271824216555681>"
    if emoji_name == "lock":
        return "<:lock:1571271827232395537>"
    if emoji_name == "unlock":
        return "<:unlock:1571271830189379694>"
    if emoji_name == "hide":
        return "<:hide:1571271833259344024>"
    if emoji_name == "unhide":
        return "<:unhide:1571271837369761822>"
    if emoji_name == "edit":
        return "<:edit:1571271840448647239>"
    if emoji_name == "trash":
        return "<:trash:1571271843040469015>"
    if emoji_name == "broom":
        return "<:broom:1571271846563815464>"
    if emoji_name == "utility":
        return "<:utility:1571271849495761178>"
    if emoji_name == "nsfw":
        return "<:nsfw:1571271852855136468>"
    if emoji_name == "loading":
        return "<a:loading:1564762500938076161>"

    # ==========================================================================
    # Navigation and structure
    # ==========================================================================
    # The help menu, the panels and the cards are built from these, so they are all
    # neutral: a menu of coloured icons reads as noise.
    if emoji_name == "home":
        return "<:home:1571271855879229480>"
    if emoji_name == "general":
        return "<:general:1571271858584821851>"
    if emoji_name == "categories":
        return "<:categories:1571271861935931482>"
    if emoji_name == "settings":
        return "<:settings:1571271864741793984>"
    if emoji_name == "docs":
        return "<:docs:1571271868369866762>"
    if emoji_name == "website":
        return "<:website:1565386636332896388>"
    if emoji_name == "notepad":
        return "<:notepad:1571271871452680263>"
    if emoji_name == "scroll":
        return "<:scroll:1571271874468384878>"
    if emoji_name == "stats":
        return "<:stats:1571271877467439198>"
    if emoji_name == "support":
        return "<:support:1571271880717901985>"
    if emoji_name == "arrow_left":
        return "<:arrow_left:1571271883633201242>"
    if emoji_name == "arrow_right":
        return "<:arrow_right:1571271891040211099>"

    # ==========================================================================
    # People and members
    # ==========================================================================
    # People and members.
    if emoji_name == "user":
        return "<:user:1571271894454374650>"
    if emoji_name == "join":
        return "<:join:1571271897507700886>"
    if emoji_name == "leave":
        return "<:leave:1571271900720537740>"
    if emoji_name == "welcome":
        return "<:welcome:1571271903815926000>"
    if emoji_name == "invite":
        return "<:invite:1571271909381767309>"
    if emoji_name == "participants":
        return "<:participants:1571271912489881810>"

    # ==========================================================================
    # Content and social
    # ==========================================================================
    # Content and social.
    if emoji_name == "message":
        return "<:message:1571271915606384641>"
    if emoji_name == "image":
        return "<:image:1571271918986723461>"
    if emoji_name == "link":
        return "<:link:1571271921964687372>"
    if emoji_name == "megaphone":
        return "<:megaphone:1571271929959162047>"
    if emoji_name == "lightbulb":
        return "<:lightbulb:1571271932987441333>"
    if emoji_name == "heart":
        return "<:heart:1571271935969468504>"
    if emoji_name == "star":
        return "<:star:1571271939018854541>"
    if emoji_name == "ai":
        return "<:ai:1571271942110187550>"
    if emoji_name == "bot":
        return "<:bot:1571271945213710467>"
    if emoji_name == "bug":
        return "<:bug:1571271948191670272>"
    if emoji_name == "sad":
        return "<:sad:1571271951165423787>"

    # ==========================================================================
    # Media controls
    # ==========================================================================
    # The music and voicemaster panels post a whole row of these at once, so they are
    # all neutral and share one weight. These are the production application-emoji ids.
    if emoji_name == "play":
        return "<:play:1571271954256625816>"
    if emoji_name == "pause":
        return "<:pause:1571271957565935767>"
    if emoji_name == "stop":
        return "<:stop:1571271960900403261>"
    if emoji_name == "skip":
        return "<:skip:1571271963895398653>"
    if emoji_name == "rewind":
        return "<:rewind:1571271966587879456>"
    if emoji_name == "shuffle":
        return "<:shuffle:1571271969918291988>"
    if emoji_name == "loop":
        return "<:loop:1571271972883529808>"
    if emoji_name == "queue":
        return "<:queue:1571271976008294560>"
    if emoji_name == "volume_down":
        return "<:volume_down:1571271979015741490>"
    if emoji_name == "volume_up":
        return "<:volume_up:1571271981960134698>"
    if emoji_name == "autoplay":
        return "<:autoplay:1571271985470898303>"
    if emoji_name == "refresh":
        return "<:refresh:1571271991120629900>"
    if emoji_name == "music":
        return "<:music:1571271994467688559>"
    if emoji_name == "voicemaster":
        return "<:voicemaster:1571271997537652807>"
    if emoji_name == "owner_icon":
        return "<:owner_icon:1571272000712736929>"
    if emoji_name == "disconnect":
        return "<:disconnect:1571272003380453418>"
    if emoji_name == "pingpong":
        return "<:pingpong:1571272006681501806>"

    # ==========================================================================
    # Commands and rewards
    # ==========================================================================
    # One emoji per command family, plus the giveaway setup panel's own controls.
    if emoji_name == "premium":
        return "<:premium:1571272009726435358>"
    if emoji_name == "gift":
        return "<:gift:1571272017360191528>"
    if emoji_name == "giveaway":
        return "<:giveaway:1571272020426227742>"
    if emoji_name == "ticket":
        return "<:ticket:1571272023345201152>"
    if emoji_name == "economy":
        return "<:economy:1571272026331685065>"
    if emoji_name == "leveling":
        return "<:leveling:1571272029489995937>"
    if emoji_name == "gambling":
        return "<:gambling:1571272032446845108>"
    if emoji_name == "games":
        return "<:games:1571272035672522964>"
    if emoji_name == "roleplay":
        return "<:roleplay:1571272038671323320>"
    if emoji_name == "paint":
        return "<:paint:1571272052197949650>"
    if emoji_name == "reminder":
        return "<:reminder:1571272055255465995>"
    if emoji_name == "duration":
        return "<:duration:1571272058267246653>"
    if emoji_name == "trophy":
        return "<:trophy:1571272061370769408>"
    if emoji_name == "credit_card":
        return "<a:credit_card:1564762347082489889>"

    # ==========================================================================
    # Seasonal variants
    # ==========================================================================
    # Generated from the withicons-christmas / halloween / valentine sets and
    # uploaded once. These are the production application-emoji ids.
    # seasonal_variant() chooses the right one above, then falls back to the
    # unsuffixed emoji outside its window.
    seasonal_emoji = _SEASONAL_EMOJI_IDS.get(emoji_name)
    if seasonal_emoji is not None:
        return seasonal_emoji

    # ==========================================================================
    # Machine stats
    # ==========================================================================
    # The status commands read these four in one block, so they keep one ink.
    if emoji_name == "cpu":
        return "<:cpu:1571272064424222780>"
    if emoji_name == "ram":
        return "<:ram:1571272067381203028>"
    if emoji_name == "disk":
        return "<:disk:1571272070539645040>"
    if emoji_name == "host":
        return "<:host:1571272073949479012>"

    # ==========================================================================
    # Numbers
    # ==========================================================================
    # 0-9 in order. With Icons has no plain digits, so the old Phosphor art is
    # kept in src/assets/emojis/review/ and still uploads through the sync until
    # the digit family is reviewed.
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
    # the badge SVGs by scripts/build-badge-art.mjs; these are the production
    # application-emoji ids, so a fresh checkout recognizes the live emojis.
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
    # rasterises the popup SVGs into these application emojis. These are the
    # production application-emoji ids, pinned so a production push recognizes
    # the live emojis instead of trying to upload placeholders again.
    if emoji_name == "account_age_seed":
        return "<:account_age_seed:1570990039817527386>"
    if emoji_name == "account_age_sprout":
        return "<:account_age_sprout:1570990043219370016>"
    if emoji_name == "account_age_bud":
        return "<:account_age_bud:1570990047006687366>"
    if emoji_name == "account_age_sapling":
        return "<:account_age_sapling:1570990050467127457>"
    if emoji_name == "account_age_blossom":
        return "<:account_age_blossom:1570990053734227968>"
    if emoji_name == "account_age_redwood":
        return "<:account_age_redwood:1570990056792006656>"
    if emoji_name == "account_age_sequoia":
        return "<:account_age_sequoia:1570990059887525919>"
    if emoji_name == "account_age_bristlecone":
        return "<:account_age_bristlecone:1570990062940848179>"
    if emoji_name == "account_age_stromatolite":
        return "<:account_age_stromatolite:1570990066095100015>"
    if emoji_name == "account_age_primordial":
        return "<:account_age_primordial:1570990069291024415>"

    # ==========================================================================
    # Niko role badges
    # ==========================================================================
    # One per team role and community role, drawn by scripts/build-badge-art.mjs;
    # these are the production application-emoji ids. The community roles needed
    # new names for their refreshed art, because the sync only uploads art for
    # names it does not find yet and the originals were already live.
    if emoji_name == "badge_owner":
        return "<:badge_owner:1571272077007134820>"
    if emoji_name == "badge_head_admin":
        return "<:badge_head_admin:1571272079980888156>"
    if emoji_name == "badge_head_support":
        return "<:badge_head_support:1571272083399516240>"
    if emoji_name == "badge_moderator":
        return "<:badge_moderator:1571272086536716419>"
    if emoji_name == "badge_event_coordinator":
        return "<:badge_event_coordinator:1571272089476792420>"
    if emoji_name == "badge_graphic_designer":
        return "<:badge_graphic_designer:1571272094883512538>"
    if emoji_name == "badge_partnership_manager":
        return "<:badge_partnership_manager:1571272097878249572>"
    # Discord emoji names stop at 32 characters, so the Partnerships &
    # Promotions Lead badge uses the short name for the same artwork.
    if emoji_name == "badge_partnership_lead":
        return "<:badge_partnership_lead:1571272100813996222>"
    if emoji_name == "badge_staff":
        return "<:badge_staff:1571272103708332033>"
    if emoji_name == "badge_support":
        return "<:badge_support:1571272106669383852>"
    if emoji_name == "badge_supporter_role":
        return "<:badge_supporter_role:1571272109953384459>"
    if emoji_name == "badge_bug_hunter_role":
        return "<:badge_bug_hunter_role:1571272113120350430>"
    if emoji_name == "badge_partner_role":
        return "<:badge_partner_role:1571272115968024690>"

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
    # grouped the way the logging cog groups them. Generated artwork comes from the
    # With Icons set; the log types with no clean match stay in review/. These are
    # the production application-emoji ids.
    if emoji_name == "log_kick":
        return "<:log_kick:1571272123111047318>"
    if emoji_name == "log_ban":
        return "<:log_ban:1571272126248525964>"
    if emoji_name == "log_unban":
        return "<:log_unban:1571272129368956978>"
    if emoji_name == "log_warn":
        return "<:log_warn:1571272132573270068>"
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
        return "<:log_giveaway_ban:1571272135891222588>"
    if emoji_name == "log_giveaway_unban":
        return "<:log_giveaway_unban:1571272143314882632>"

    if emoji_name == "log_voice_join":
        return "<:log_voice_join:1564762946859434055>"
    if emoji_name == "log_voice_leave":
        return "<:log_voice_leave:1564762950630379520>"
    if emoji_name == "log_voice_move":
        return "<:log_voice_move:1564762955239784622>"

    # ==========================================================================
    # Platform logos
    # ==========================================================================
    # The bot itself, the platforms it is listed on and the services it talks to.
    # With Icons has no brand marks, so the existing Simple Icons art stays in
    # src/assets/emojis/review/ and still uploads through the sync.
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
    # The card mark and the coin marks. With Icons has no cryptocurrency family,
    # so the existing Web3 Icons mono art stays in src/assets/emojis/review/ and
    # still uploads until the payment source is reviewed.
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
