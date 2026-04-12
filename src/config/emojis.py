# this is where the bots custom emojis are configured
# this is used to make the bot more customizable and to make it easier to change the emojis


# emojis for the bot
def get_emoji(emoji_name: str):
    if emoji_name == "automod":
        return "<:Automod:1492967599586152448>"
    if emoji_name == "bot_owner":
        return "<:bot_owner:1492967602929143818>"
    if emoji_name == "cpu":
        return "<:cpu:1492967605911289866>"
    if emoji_name == "credit_card":
        return "<a:credit_card:1492967609061081171>"
    if emoji_name == "discord":
        return "<a:discord:1492967612290961428>"
    if emoji_name == "github":
        return "<:github:1492967615243489330>"
    if emoji_name == "icon_ai":
        return "<:icon_ai:1492967617600684245>"
    if emoji_name == "icon_automod":
        return "<:icon_automod:1492967621128359936>"
    if emoji_name == "icon_categories":
        return "<:icon_categories:1492967623619645584>"
    if emoji_name == "icon_cross":
        return "<:icon_cross:1492967626320646315>"
    if emoji_name == "icon_danger":
        return "<:icon_danger:1492967630024474684>"
    if emoji_name == "icon_economy":
        return "<:icon_economy:1492967632586936333>"
    if emoji_name == "icon_games":
        return "<:icon_games:1492967635258966279>"
    if emoji_name == "icon_edit":
        return "<:icon_edit:1492967638484385982>"
    if emoji_name == "icon_giveaway":
        return "<:icon_giveaway:1492967641374265514>"
    if emoji_name == "icon_image":
        return "<:icon_image:1492967644121530459>"
    if emoji_name == "icon_leveling":
        return "<:icon_leveling:1492967646910484480>"
    if emoji_name == "icon_link":
        return "<:icon_link:1492967649641107496>"
    if emoji_name == "icon_moderation":
        return "<:icon_moderation:1492967655819317388>"
    if emoji_name == "icon_plus":
        return "<:icon_plus:1492967658759393331>"
    if emoji_name == "icon_settings":
        return "<:icon_settings:1492967661670502590>"
    if emoji_name == "icon_tick":
        return "<:icon_tick:1492967664442933540>"
    if emoji_name == "icon_ticket":
        return "<:icon_ticket:1492967666829496353>"
    if emoji_name == "icon_utility":
        return "<:icon_utility:1492967669547274502>"
    if emoji_name == "icon_welcome":
        return "<:icon_welcome:1492967672902717622>"
    if emoji_name == "music":
        return "<:music:1492967675742261248>"
    if emoji_name == "owner_icon":
        return "<:owner_icon:1492967678573416609>"
    if emoji_name == "ram":
        return "<:ram:1492967681341788291>"
    if emoji_name == "spotify":
        return "<:spotify:1492967684122349648>"
    if emoji_name == "vm_lock":
        return "<:vm_lock:1492967686932529283>"
    if emoji_name == "vm_unlock":
        return "<:vm_unlock:1492967689637986547>"
    if emoji_name == "website":
        return "<:website:1492967699548999851>"
    # these use two emojis instead of just returning one
    if emoji_name == "enabled":
        return "<:disable_no:1492967702409642126><:enable_yes:1492967705240797204>"
    if emoji_name == "disabled":
        return "<:disable_yes:1492967708592177382><:enable_no:1492967711863603330>"