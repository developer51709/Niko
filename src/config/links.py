# this is where the bots links can be updated

import os

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
DATA_REMOVAL = f"{WEBSITE}/data-removal"

# Direct contact for formal legal requests. The owner's public site lists the
# contact details; Niko never publishes a private address on the bot itself.
OWNER_CONTACT = "https://sorenthedev.indevs.in"

# top.gg listing. The bot ID defaults to the application ID the rest of the
# deployment uses; set TOPGG_BOT_ID when the listing belongs to a different app.
TOPGG_BOT_ID = os.environ.get("TOPGG_BOT_ID", "1520558530472448170")
TOPGG_VOTE_URL = f"https://top.gg/bot/{TOPGG_BOT_ID}/vote"
