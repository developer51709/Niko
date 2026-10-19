def get_emoji(emoji_name: str):
    if emoji_name == "active_developer_badge":
        return "<:active_developer_badge:1561569636313473265>"
    # Discord profile badges that Niko did not have emoji art for yet. Their
    # artwork is generated from the badge SVGs into src/assets/emojis/ by
    # scripts/build-badge-art.mjs, and the ids are placeholders: the startup
    # emoji sync uploads the PNGs and rewrites them with the live ids.
    # Discord's server-boosting badge has its own artwork per tier, so every
    # tier gets its own emoji and the cards pick the one the streak reached.
    if emoji_name == "boosting_1_months":
        return "<:boosting_1_months:1560774003130499073>"
    if emoji_name == "boosting_2_months":
        return "<:boosting_2_months:1560774006519369738>"
    if emoji_name == "boosting_3_months":
        return "<:boosting_3_months:1560774009493127199>"
    if emoji_name == "boosting_6_months":
        return "<:boosting_6_months:1560774012756426902>"
    if emoji_name == "boosting_9_months":
        return "<:boosting_9_months:1560774015965200464>"
    if emoji_name == "boosting_12_months":
        return "<:boosting_12_months:1560774019156938872>"
    if emoji_name == "boosting_15_months":
        return "<:boosting_15_months:1560774022030032976>"
    if emoji_name == "boosting_18_months":
        return "<:boosting_18_months:1560774024936558676>"
    if emoji_name == "boosting_24_months":
        return "<:boosting_24_months:1560774028010987670>"
    if emoji_name == "bug_hunter_badge":
        return "<:bug_hunter_badge:1560768150293717052>"
    if emoji_name == "bug_hunter_gold_badge":
        return "<:bug_hunter_gold_badge:1560768153427124235>"
    if emoji_name == "certified_moderator_badge":
        return "<:certified_moderator_badge:1560768156526710957>"
    if emoji_name == "early_supporter_badge":
        return "<:early_supporter_badge:1560768159676366848>"
    if emoji_name == "hypesquad_events":
        return "<:hypesquad_events:1560768162482618401>"
    if emoji_name == "partner_badge":
        return "<:partner_badge:1561572830376755350>"
    if emoji_name == "staff_badge":
        return "<:staff_badge:1560768165527425137>"
    if emoji_name == "supports_commands_badge":
        return "<:supports_commands_badge:1560768169122070598>"
    if emoji_name == "arrow_left":
        return "<:arrow_left:1555276714651942923>"
    if emoji_name == "arrow_right":
        return "<:arrow_right:1555276717487292487>"
    if emoji_name == "automod":
        return "<:Automod:1555276720146227220>"
    # Niko's own role badges, one per team role plus the community roles. The
    # artwork is generated from web/public/assets/badges/niko_*.svg into
    # src/assets/emojis/badge_*.png by scripts/build-badge-art.mjs, and these
    # placeholder ids are replaced by the sync once it uploads them.
    if emoji_name == "badge_event_coordinator":
        return "<:badge_event_coordinator:1560768172280381611>"
    if emoji_name == "badge_graphic_designer":
        return "<:badge_graphic_designer:1560787795801542867>"
    if emoji_name == "badge_head_admin":
        return "<:badge_head_admin:1560768178236301405>"
    if emoji_name == "badge_head_support":
        return "<:badge_head_support:1560787799479812097>"
    if emoji_name == "badge_moderator":
        return "<:badge_moderator:1560768184989126856>"
    if emoji_name == "badge_owner":
        return "<:badge_owner:1560768188071944242>"
    if emoji_name == "badge_partnership_manager":
        return "<:badge_partnership_manager:1560768191079129312>"
    # Discord emoji names stop at 32 characters, so the Partnerships &
    # Promotions Lead badge uses the short name for the same artwork.
    if emoji_name == "badge_partnership_lead":
        return "<:badge_partnership_lead:1560770119334895790>"
    if emoji_name == "badge_staff":
        return "<:badge_staff:1560768194921103410>"
    if emoji_name == "badge_support":
        return "<:badge_support:1560768198083743754>"
    # The community role badges, with the refreshed artwork. Their original
    # names (badge_supporter, badge_bugbounty, badge_partner) are already live
    # application emojis, and the sync only uploads art for names it does not
    # find yet, so the new art needs its own names to reach Discord.
    if emoji_name == "badge_supporter_role":
        return "<:badge_supporter_role:1560774034382262332>"
    if emoji_name == "badge_bug_hunter_role":
        return "<:badge_bug_hunter_role:1560774037666267168>"
    if emoji_name == "badge_partner_role":
        return "<:badge_partner_role:1560787802558435370>"
    if emoji_name == "bluesky":
        return "<:bluesky:1545426285948436610>"
    if emoji_name == "broom":
        return "<:broom:1555276736315392113>"
    if emoji_name == "C4Empty":
        return "<:C4Empty:1520827287761850421>"
    if emoji_name == "C4Red":
        return "<a:C4Red:1520827291524006070>"
    if emoji_name == "C4Top1":
        return "<:C4Top1:1520827296309841990>"
    if emoji_name == "C4Top2":
        return "<:C4Top2:1520827300244094976>"
    if emoji_name == "C4Top3":
        return "<:C4Top3:1520827303196622868>"
    if emoji_name == "C4Top4":
        return "<:C4Top4:1520827306774368287>"
    if emoji_name == "C4Top5":
        return "<:C4Top5:1520827310784122930>"
    if emoji_name == "C4Top6":
        return "<:C4Top6:1520827315444121620>"
    if emoji_name == "C4Top7":
        return "<:C4Top7:1520827319449686157>"
    if emoji_name == "C4Yellow":
        return "<a:C4Yellow:1520827324029997118>"
    if emoji_name == "cpu":
        return "<:cpu:1555276739305799690>"
    if emoji_name == "credit_card":
        return "<a:credit_card:1555276742090821753>"
    if emoji_name == "crypto_bitcoin":
        return "<:crypto_bitcoin:1526343246609911908>"
    if emoji_name == "crypto_bnb":
        return "<:crypto_bnb:1526343249755639818>"
    if emoji_name == "crypto_dogecoin":
        return "<:crypto_dogecoin:1526343252708692019>"
    if emoji_name == "crypto_ethereum":
        return "<:crypto_ethereum:1526343255506157770>"
    if emoji_name == "crypto_ltc":
        return "<:crypto_ltc:1526343258739834930>"
    if emoji_name == "crypto_monero":
        return "<:crypto_monero:1526343262061989918>"
    if emoji_name == "crypto_tether_usdt":
        return "<:crypto_tether_usdt:1526343264834293862>"
    if emoji_name == "crypto_tron":
        return "<:crypto_tron:1526343268395126804>"
    if emoji_name == "dbl":
        return "<:dbl:1520827352127377410>"
    if emoji_name == "disconnect":
        return "<:disconnect:1555276744909394022>"
    if emoji_name == "discord":
        return "<a:discord:1520827356678197300>"
    if emoji_name == "gift":
        return "<:gift:1555276747673571360>"
    if emoji_name == "github":
        return "<:github:1520827361422082069>"
    if emoji_name == "hypesquad_balance":
        return "<:hypesquad_balance:1520827365079650475>"
    if emoji_name == "hypesquad_bravery":
        return "<:hypesquad_bravery:1520827369508700252>"
    if emoji_name == "hypesquad_briliance":
        return "<:hypesquad_briliance:1520827373413466193>"
    if emoji_name == "ai":
        return "<:ai:1555275330518908988>"
    if emoji_name == "ban":
        return "<:ban:1561569639539150858>"
    if emoji_name == "boost":
        return "<:boost:1561569642659577926>"
    if emoji_name == "bot":
        return "<:bot:1555275338660057250>"
    if emoji_name == "bug":
        return "<:bug:1555275341910642718>"
    if emoji_name == "categories":
        return "<:categories:1555275344641130546>"
    if emoji_name == "cross":
        return "<:cross:1555275347715690518>"
    if emoji_name == "danger":
        return "<:danger:1555275350517227660>"
    if emoji_name == "disk":
        return "<:disk:1555275353084399740>"
    if emoji_name == "docs":
        return "<:docs:1555275356225798154>"
    if emoji_name == "economy":
        return "<:economy:1555275358859694135>"
    if emoji_name == "edit":
        return "<:edit:1555275361888116897>"
    if emoji_name == "games":
        return "<:games:1555275364966727840>"
    if emoji_name == "gambling":
        return "<:gambling:1555275367726452877>"
    if emoji_name == "general":
        return "<:general:1555275370440433674>"
    if emoji_name == "giveaway":
        return "<:giveaway:1555275373108011199>"
    if emoji_name == "heart":
        return "<:heart:1555275375708340287>"
    if emoji_name == "home":
        return "<:home:1555275378652614689>"
    if emoji_name == "host":
        return "<:host:1555275381706334248>"
    if emoji_name == "image":
        return "<:image:1555275384512192633>"
    if emoji_name == "important":
        return "<:important:1555275388299513898>"
    if emoji_name == "invite":
        return "<:invite:1555275391298572398>"
    if emoji_name == "join":
        return "<:join:1555275394050035844>"
    if emoji_name == "leave":
        return "<:leave:1555275396751167588>"
    if emoji_name == "leveling":
        return "<:leveling:1555275399582453790>"
    if emoji_name == "lightbulb":
        return "<:lightbulb:1555275402459484240>"
    if emoji_name == "link":
        return "<:link:1555275405114740736>"
    if emoji_name == "loading":
        return "<a:loading:1555275407882985532>"
    if emoji_name == "loop":
        return "<:loop:1555275410714136658>"
    if emoji_name == "megaphone":
        return "<:megaphone:1555275413289304177>"
    if emoji_name == "message":
        return "<:message:1555275416300953621>"
    if emoji_name == "minus":
        return "<:minus:1555275419165397055>"
    if emoji_name == "moderation":
        return "<:moderation:1555275422118191145>"
    if emoji_name == "nsfw":
        return "<:nsfw:1561569646182670367>"
    if emoji_name == "paint":
        return "<:paint:1555275430347415683>"
    if emoji_name == "pause":
        return "<:pause:1555275437150572564>"
    if emoji_name == "play":
        return "<:play:1555275439860088882>"
    if emoji_name == "plus":
        return "<:plus:1555275442494116021>"
    if emoji_name == "premium":
        return "<:premium:1555275445484912731>"
    if emoji_name == "question":
        return "<:question:1555275448219336786>"
    if emoji_name == "refresh":
        return "<:refresh:1555275450836844646>"
    if emoji_name == "reminder":
        return "<:reminder:1555275454141698048>"
    if emoji_name == "roleplay":
        return "<:roleplay:1555275457149141012>"
    if emoji_name == "rewind":
        return "<:rewind:1555275459896283206>"
    if emoji_name == "settings":
        return "<:settings:1555275462698078268>"
    if emoji_name == "shuffle":
        return "<:shuffle:1555275465441288232>"
    if emoji_name == "skip":
        return "<:skip:1555275468142546944>"
    if emoji_name == "stats":
        return "<:stats:1555275470910521427>"
    if emoji_name == "stop":
        return "<:stop:1555275473922035833>"
    if emoji_name == "support":
        return "<:support:1555275476799332412>"
    if emoji_name == "tick":
        return "<:tick:1555275479240675419>"
    if emoji_name == "ticket":
        return "<:ticket:1555275484613443665>"
    if emoji_name == "trash":
        return "<:trash:1555276750198411327>"
    if emoji_name == "utility":
        return "<:utility:1555275487729684550>"
    if emoji_name == "user":
        return "<:user:1555275490720481370>"
    if emoji_name == "verified":
        return "<:verified:1555275493106913334>"
    if emoji_name == "welcome":
        return "<:welcome:1555275496378597426>"
    if emoji_name == "wumpus":
        return "<:wumpus:1555275499306098789>"
    if emoji_name == "instagram":
        return "<:instagram:1520827744907432016>"
    if emoji_name == "lastfm":
        return "<:lastfm:1555276754665476106>"
    if emoji_name == "music":
        return "<:music:1555276757706219530>"
    if emoji_name == "notepad":
        return "<:notepad:1555276760826904717>"
    if emoji_name == "number_eight":
        return "<:number_eight:1522655574997733517>"
    if emoji_name == "number_five":
        return "<:number_five:1522655578026020915>"
    if emoji_name == "number_four":
        return "<:number_four:1522655580827816070>"
    if emoji_name == "number_nine":
        return "<:number_nine:1522655584141312030>"
    if emoji_name == "number_one":
        return "<:number_one:1522653374611193903>"
    if emoji_name == "number_seven":
        return "<:number_seven:1522655587089911949>"
    if emoji_name == "number_six":
        return "<:number_six:1522655590281777263>"
    if emoji_name == "number_three":
        return "<:number_three:1522653377518112939>"
    if emoji_name == "number_two":
        return "<:number_two:1522653380433023088>"
    if emoji_name == "number_zero":
        return "<:number_zero:1522653383536677047>"
    if emoji_name == "owner_icon":
        return "<:owner_icon:1555276763695939664>"
    if emoji_name == "oxapay":
        return "<:oxapay:1526370664720629780>"
    if emoji_name == "pingpong":
        return "<:pingpong:1555276766786883655>"
    if emoji_name == "python":
        return "<:python:1520827759578976266>"
    if emoji_name == "ram":
        return "<:ram:1555276769290887199>"
    if emoji_name == "reddit":
        return "<:reddit:1545426284992270486>"
    if emoji_name == "scroll":
        return "<:scroll:1555276772369498222>"
    if emoji_name == "soundcloud":
        return "<:soundcloud:1520827768038756574>"
    if emoji_name == "spotify":
        return "<:spotify:1520827772069740705>"
    if emoji_name == "star":
        return "<:star:1555276774802329653>"
    if emoji_name == "status_dnd":
        return "<:status_dnd:1526455311286669423>"
    if emoji_name == "status_idle":
        return "<:status_idle:1526455314428203199>"
    if emoji_name == "status_offline":
        return "<:status_offline:1526455317234319461>"
    if emoji_name == "status_online":
        return "<:status_online:1526455320506011728>"
    if emoji_name == "status_streaming":
        return "<:status_streaming:1526455323488157766>"
    if emoji_name == "thumbs_down":
        return "<:thumbs_down:1555276777935609987>"
    if emoji_name == "thumbs_up":
        return "<:thumbs_up:1555276780636606556>"
    if emoji_name == "tiktok":
        return "<:tiktok:1545426286883901610>"
    if emoji_name == "topgg":
        return "<:topgg:1560070335863459861>"
    if emoji_name == "twitch":
        return "<:twitch:1545426287915696178>"
    if emoji_name == "twitterx":
        return "<:twitterx:1545426291749167155>"
    if emoji_name == "voicemaster":
        return "<:voicemaster:1555275502078533763>"
    if emoji_name == "verified_developer_badge":
        return "<:verified_developer_badge:1561569652637831228>"
    if emoji_name == "hide":
        return "<:hide:1555275505022930944>"
    if emoji_name == "lock":
        return "<:lock:1555275507426402337>"
    if emoji_name == "unhide":
        return "<:unhide:1555275510412611688>"
    if emoji_name == "unlock":
        return "<:unlock:1555275513122136065>"
    if emoji_name == "warning":
        return "<:warning:1555276783346126938>"
    if emoji_name == "wavelink":
        return "<:wavelink:1520827814352388289>"
    if emoji_name == "website":
        return "<:website:1555276786005180457>"
    if emoji_name == "White1":
        return "<:White1:1520827822590005318>"
    if emoji_name == "White2":
        return "<:White2:1520827826616537229>"
    if emoji_name == "White3":
        return "<:White3:1520827831158837348>"
    if emoji_name == "White4":
        return "<:White4:1520827835181436958>"
    if emoji_name == "White5":
        return "<:White5:1520827839585193984>"
    if emoji_name == "White6":
        return "<:White6:1520827844190666754>"
    if emoji_name == "White7":
        return "<:White7:1520827857016983652>"
    if emoji_name == "youtube":
        return "<:youtube:1545426288830054461>"
    if emoji_name == "youtube_shorts":
        return "<:youtube_shorts:1545426290020978738>"
    if emoji_name == "enabled":
        return "<:disable_no:1520827872925716580><:enable_yes:1520827877283856445>"
    if emoji_name == "disabled":
        return "<:disable_yes:1520827881574367293><:enable_no:1520827885483458763>"
