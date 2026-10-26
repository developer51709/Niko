# Bot presence / status configuration.
#
# Status messages support live placeholder variables, substituted every time
# the presence updates:
#
#   {servers}   — number of guilds the bot is in
#   {users}     — total member count across all guilds
#   {shards}    — number of shards the bot is running on
#   {commands}  — number of registered commands

import os


def _env_flag(name: str) -> bool:
    """Read an opt-in environment flag, accepting common true values."""
    return (os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "on"}


# Public beta deployments set this flag to use a distinct presence rotation
# and a fixed development command prefix.
DEVELOPMENT = _env_flag("DEVELOPMENT")

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
PRODUCTION_STATUS_MESSAGES: list[str] = [
    ".help | \u201chey niko\u201d",
    "https://niko.sryze.cc",
    "in over {servers} servers",
    "{commands} commands to explore",
    "music, AI, giveaways & more",
    "watching {users} members chat",
    "try /legal for the fine print",
    "spread across {shards} shard(s)",
    "say hey, I'll say hey back",
]
DEVELOPMENT_STATUS_MESSAGES: list[str] = [
    "Niko beta | try !help",
    "testing the next update",
    "beta running in {servers} servers",
]
STATUS_MESSAGES: list[str] = (
    DEVELOPMENT_STATUS_MESSAGES if DEVELOPMENT else PRODUCTION_STATUS_MESSAGES
)
STATUS_TYPES: list[str] = []
STATUS_INTERVAL = 30

# A non-empty environment value overrides the configured rotation entirely.
STATUS_MESSAGE_OVERRIDE = (os.getenv("STATUS_MESSAGE") or "").strip()
STATUS_MESSAGE = STATUS_MESSAGE_OVERRIDE or STATUS_MESSAGES[0]
