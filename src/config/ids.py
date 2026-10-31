# Optional: Add your owner IDs here if you want multiple owners
OWNER_IDS = {
    1052690741874401360
}


def is_owner_id(user_id) -> bool:
    """Whether this user is a configured bot owner.

    Owners are exempt from the blacklist. Without that exemption an automated
    strike (or a mistyped dashboard action) could blacklist the account that
    runs the bot, and recovering meant editing the database by hand and
    restarting to clear the cached entry — with no way back in from Discord or
    the dashboard in the meantime.
    """
    try:
        return int(user_id) in OWNER_IDS
    except (TypeError, ValueError):
        return False

# support server guild id
SUPPORT_GUILD  = 1497250915034337330

# MrBeast scam experiment — private staff-only review server where reported
# scam images are sent for confirmation before joining the detection database.
SCAM_REVIEW_GUILD   = 1497250915034337330
SCAM_REVIEW_CHANNEL = 1555030193133981777  # set to a channel ID in the review server to enable

# Support-server role IDs are provisioned by `.staff supportsetup` and stored
# in support_server_config; do not hardcode role IDs here.
