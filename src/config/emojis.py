# this is where the bots custom emojis are configured
# this is used to make the bot more customizable and to make it easier to change the emojis


# emojis for the bot
def get_emoji(emoji_name: str):
    if emoji_name == "automod":
        return "<:Automod:1484537188245835821>"
    if emoji_name == "bot_owner":
        return "<:bot_owner:1484522179034087579>"
    if emoji_name == "cpu":
        return "<:cpu:1488576145518755880>"
    if emoji_name == "credit_card":
        return "<a:credit_card:1488611287545151562>"
    if emoji_name == "discord":
        return "<a:discord:1488569938258952212>"
    if emoji_name == "github":
        return "<:github:1488283491941748736>"
    if emoji_name == "icon_ai":
        return "<:icon_ai:1484520738345189500>"
    if emoji_name == "icon_automod":
        return "<:icon_automod:1484520751624360017>"
    if emoji_name == "icon_categories":
        return "<:icon_categories:1484522112202051734>"
    if emoji_name == "icon_cross":
        return "<:icon_cross:1484520758452686930>"
    if emoji_name == "icon_danger":
        return "<:icon_danger:1484522107802095829>"
    if emoji_name == "icon_economy":
        return "<:icon_economy:1484520797585408113>"
    if emoji_name == "icon_games":
        return "<:icon_games:1484520778798989415>"
    if emoji_name == "icon_edit":
        return "<:icon_edit:1484522084188033097>"
    if emoji_name == "icon_giveaway":
        return "<:icon_giveaway:1484520743214780557>"
    if emoji_name == "icon_image":
        return "<:icon_image:1484520768271286342>"
    if emoji_name == "icon_leveling":
        return "<:icon_leveling:1488609621319876639>"
    if emoji_name == "icon_link":
        return "<:icon_link:1484520754362974420>"
    if emoji_name == "icon_moderation":
        return "<:icon_moderation:1484520749434802187>"
    if emoji_name == "icon_plus":
        return "<:icon_plus:1484520793768591411>"
    if emoji_name == "icon_settings":
        return "<:icon_settings:1484520784402583613>"
    if emoji_name == "icon_tick":
        return "<:icon_tick:1484520756216987738>"
    if emoji_name == "icon_ticket":
        return "<:icon_ticket:1484520746771415040>"
    if emoji_name == "icon_utility":
        return "<:icon_utility:1484520721718706306>"
    if emoji_name == "icon_welcome":
        return "<:icon_welcome:1484520744812806205>"
    if emoji_name == "music":
        return "<:music:1484522123383931010>"
    if emoji_name == "owner_icon":
        return "<:owner_icon:1484537185578389666>"
    if emoji_name == "ram":
        return "<:ram:1488576025247092887>"
    if emoji_name == "spotify":
        return "<:spotify:1488574224997027963>"
    if emoji_name == "vm_lock":
        return "<:vm_lock:1488954833019998359>"
    if emoji_name == "vm_unlock":
        return "<:vm_unlock:1488954649904939158>"
    if emoji_name == "website":
        return "<:website:1488567482007683202>"
    # these use two emojis instead of just returning one
    if emoji_name == "enabled":
        return "<:disable_no:1484520728190517401><:enable_yes:1484520730711298190>"
    if emoji_name == "disabled":
        return "<:disable_yes:1484520726550544486><:enable_no:1484520729444614144>"