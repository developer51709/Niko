# Bot presence / status configuration.

# Single-message mode: the bot shows one activity at startup.
STATUS_MESSAGE = ".help | \u201chey niko\u201d"

# Activity type: playing, watching, listening, competing, or streaming.
STATUS_TYPE = "playing"

# Optional link used for streaming (twitch/youtube) to get the purple status icon.
STATUS_LINK = "https://twitch.tv/niko"

# Device presence override: normal, embedded, desktop, vr, mobile_android, mobile_ios.
STATUS_DEVICE = "vr"

# Multi-message rotation (optional).
# Set STATUS_ROTATE to True and provide STATUS_MESSAGES + STATUS_TYPES to rotate
# through multiple activities on a timer. STATUS_INTERVAL is the seconds between
# each rotation step.
STATUS_ROTATE = True
STATUS_MESSAGES: list[str] = [
    ".help | \u201chey niko\u201d",
    "https://niko.sryze.cc"
]
STATUS_TYPES: list[str] = []
STATUS_INTERVAL = 30
