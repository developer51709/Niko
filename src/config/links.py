# this is where the bots links can be updated

WEBSITE = "https://niko.sryze.cc"

# Support-server references always point at the website's /discord page. That
# page resolves the current invite from the live bot config, so it keeps working
# when an invite is rotated, expired, or recreated. Never hardcode a raw
# discord.gg invite here again.
SUPPORT_SERVER = f"{WEBSITE}/discord"

# Legacy community-server invite. No surface references this any more; keep it
# only so older imports resolve. Use SUPPORT_SERVER for anything user-facing.
COMMUNITY_SERVER = "https://discord.gg/3sAKtw3dMa"

GITHUB = "https://github.com/developer51709/Niko"
TOS = f"{WEBSITE}/terms"
PRIVACY = f"{WEBSITE}/privacy"
COMMUNITY = f"{WEBSITE}/community"
DOCS = f"{WEBSITE}/docs"
