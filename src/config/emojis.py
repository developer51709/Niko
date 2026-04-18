# this is where the bots custom emojis are configured
# this is used to make the bot more customizable and to make it easier to change the emojis


# emojis for the bot
def get_emoji(emoji_name: str):
    if emoji_name == "automod":
        return "<:Automod:1492967599586152448>"
    if emoji_name == "bot_owner":
        return "<:bot_owner:1492967602929143818>"
    if emoji_name == "C4Empty":
        return "<:C4Empty:1494457010723360930>"
    if emoji_name == "C4Red":
        return "<a:C4Red:1494457013696987276>"
    if emoji_name == "C4Top1":
        return "<:C4Top1:1494457016482271402>"
    if emoji_name == "C4Top2":
        return "<:C4Top2:1494457019812282408>"
    if emoji_name == "C4Top3":
        return "<:C4Top3:1494457022790504488>"
    if emoji_name == "C4Top4":
        return "<:C4Top4:1494457025583644762>"
    if emoji_name == "C4Top5":
        return "<:C4Top5:1494457028486234142>"
    if emoji_name == "C4Top6":
        return "<:C4Top6:1494457031644414107>"
    if emoji_name == "C4Top7":
        return "<:C4Top7:1494457035096326204>"
    if emoji_name == "C4Yellow":
        return "<a:C4Yellow:1494457038577729656>"
    if emoji_name == "cpu":
        return "<:cpu:1492967605911289866>"
    if emoji_name == "credit_card":
        return "<a:credit_card:1492967609061081171>"
    if emoji_name == "dbl":
        return "<:dbl:1494434245433622661>"
    if emoji_name == "discord":
        return "<a:discord:1492967612290961428>"
    if emoji_name == "github":
        return "<:github:1492967615243489330>"
    if emoji_name == "hypesquad_balance":
        return "<:hypesquad_balance:1494434248734670938>"
    if emoji_name == "hypesquad_bravery":
        return "<:hypesquad_bravery:1494419243653927053>"
    if emoji_name == "hypesquad_briliance":
        return "<:hypesquad_briliance:1494419246589939743>"
    if emoji_name == "icon_ai":
        return "<:icon_ai:1492967617600684245>"
    if emoji_name == "icon_automod":
        return "<:icon_automod:1492967621128359936>"
    if emoji_name == "icon_ban":
        return "<:icon_ban:1494438789295378522>"
    if emoji_name == "icon_boost":
        return "<:icon_boost:1494419249488461976>"
    if emoji_name == "icon_bot":
        return "<:icon_bot:1494419252520943666>"
    if emoji_name == "icon_bug":
        return "<:icon_bug:1494423941488316620>"
    if emoji_name == "icon_categories":
        return "<:icon_categories:1492967623619645584>"
    if emoji_name == "icon_cross":
        return "<:icon_cross:1492967626320646315>"
    if emoji_name == "icon_danger":
        return "<:icon_danger:1492967630024474684>"
    if emoji_name == "icon_disk":
        return "<:icon_disk:1494738060255166556>"
    if emoji_name == "icon_dnd":
        return "<:icon_dnd:1494421802317778994>"
    if emoji_name == "icon_docs":
        return "<:icon_docs:1494738063383986236>"
    if emoji_name == "icon_economy":
        return "<:icon_economy:1492967632586936333>"
    if emoji_name == "icon_edit":
        return "<:icon_edit:1492967638484385982>"
    if emoji_name == "icon_games":
        return "<:icon_games:1492967635258966279>"
    if emoji_name == "icon_gambling":
        return "<:icon_gambling:1494521368061153280>"
    if emoji_name == "icon_general":
        return "<:icon_general:1494521371689226250>"
    if emoji_name == "icon_giveaway":
        return "<:icon_giveaway:1492967641374265514>"
    if emoji_name == "icon_heart":
        return "<:icon_heart:1494438792038322186>"
    if emoji_name == "icon_home":
        return "<:icon_home:1494738066324066407>"
    if emoji_name == "icon_host":
        return "<:icon_host:1494434252081856776>"
    if emoji_name == "icon_idle":
        return "<:icon_idle:1494421805333479475>"
    if emoji_name == "icon_image":
        return "<:icon_image:1492967644121530459>"
    if emoji_name == "icon_important":
        return "<:icon_important:1494438794760552611>"
    if emoji_name == "icon_invite":
        return "<:icon_invite:1494434254715621600>"
    if emoji_name == "icon_join":
        return "<:icon_join:1493403603166035968>"
    if emoji_name == "icon_leave":
        return "<:icon_leave:1493403606240723044>"
    if emoji_name == "icon_leveling":
        return "<:icon_leveling:1492967646910484480>"
    if emoji_name == "icon_lightbulb":
        return "<:icon_lightbulb:1494438797893570770>"
    if emoji_name == "icon_link":
        return "<:icon_link:1492967649641107496>"
    if emoji_name == "icon_loading":
        return "<a:icon_loading:1493402982883000582>"
    if emoji_name == "icon_loop":
        return "<:icon_loop:1494738069398753452>"
    if emoji_name == "icon_megaphone":
        return "<:icon_megaphone:1494438801328574615>"
    if emoji_name == "icon_moderation":
        return "<:icon_moderation:1492967655819317388>"
    if emoji_name == "icon_nsfw":
        return "<:icon_nsfw:1494521378639183964>"
    if emoji_name == "icon_offline":
        return "<:icon_offline:1494421808345120961>"
    if emoji_name == "icon_online":
        return "<:icon_online:1494421811138662490>"
    if emoji_name == "icon_paint":
        return "<:icon_paint:1494423944466399293>"
    if emoji_name == "icon_partner":
        return "<:icon_partner:1494421813982396719>"
    if emoji_name == "icon_pause":
        return "<:icon_pause:1494414711356391757>"
    if emoji_name == "icon_play":
        return "<:icon_play:1494414714380226681>"
    if emoji_name == "icon_plus":
        return "<:icon_plus:1492967658759393331>"
    if emoji_name == "icon_premium":
        return "<:icon_premium:1494414717266165850>"
    if emoji_name == "icon_question":
        return "<:icon_question:1494414720009109515>"
    if emoji_name == "icon_refresh":
        return "<:icon_refresh:1494438804709441548>"
    if emoji_name == "icon_roleplay":
        return "<:icon_roleplay:1494521386159439965>"
    if emoji_name == "icon_rewind":
        return "<:icon_rewind:1494419255175811193>"
    if emoji_name == "icon_settings":
        return "<:icon_settings:1492967661670502590>"
    if emoji_name == "icon_shuffle":
        return "<:icon_shuffle:1494419258443173940>"
    if emoji_name == "icon_skip":
        return "<:icon_skip:1494419261647753337>"
    if emoji_name == "icon_stats":
        return "<:icon_stats:1494438808219947160>"
    if emoji_name == "icon_stop":
        return "<:icon_stop:1494803197741760514>"
    if emoji_name == "icon_support":
        return "<:icon_support:1494450967440003293>"
    if emoji_name == "icon_tick":
        return "<:icon_tick:1492967664442933540>"
    if emoji_name == "icon_ticket":
        return "<:icon_ticket:1492967666829496353>"
    if emoji_name == "icon_trash":
        return "<:icon_trash:1494438811264876707>"
    if emoji_name == "icon_utility":
        return "<:icon_utility:1492967669547274502>"
    if emoji_name == "icon_verified":
        return "<:icon_verified:1494421816834523278>"
    if emoji_name == "icon_welcome":
        return "<:icon_welcome:1492967672902717622>"
    if emoji_name == "icon_wumpus":
        return "<:icon_wumpus:1494421819602636994>"
    if emoji_name == "music":
        return "<:music:1492967675742261248>"
    if emoji_name == "owner_icon":
        return "<:owner_icon:1492967678573416609>"
    if emoji_name == "python":
        return "<:python:1494434257626595561>"
    if emoji_name == "ram":
        return "<:ram:1492967681341788291>"
    if emoji_name == "soundcloud":
        return "<:soundcloud:1494419264323452990>"
    if emoji_name == "spotify":
        return "<:spotify:1492967684122349648>"
    if emoji_name == "icon_voicemaster":
        return "<:icon_voicemaster:1494521394522882058>"
    if emoji_name == "vm_lock":
        return "<:vm_lock:1492967686932529283>"
    if emoji_name == "vm_unlock":
        return "<:vm_unlock:1492967689637986547>"
    if emoji_name == "wavelink":
        return "<:wavelink:1494414723096117421>"
    if emoji_name == "website":
        return "<:website:1492967699548999851>"
    if emoji_name == "White1":
        return "<:White1:1494485681731534890>"
    if emoji_name == "White2":
        return "<:White2:1494485684705300551>"
    if emoji_name == "White3":
        return "<:White3:1494485687653634059>"
    if emoji_name == "White4":
        return "<:White4:1494485690803814430>"
    if emoji_name == "White5":
        return "<:White5:1494485693685301258>"
    if emoji_name == "White6":
        return "<:White6:1494485696340037641>"
    if emoji_name == "White7":
        return "<:White7:1494485702002348042>"
    if emoji_name == "youtube":
        return "<:youtube:1494419267603533914>"
    # these use two emojis instead of just returning one
    if emoji_name == "enabled":
        return "<:disable_no:1492967702409642126><:enable_yes:1492967705240797204>"
    if emoji_name == "disabled":
        return "<:disable_yes:1492967708592177382><:enable_no:1492967711863603330>"