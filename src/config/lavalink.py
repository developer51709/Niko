"""Static Lavalink candidates — the committed node pool.

This file is the only public node source: no remote list is fetched at
runtime, so what ships here is exactly what the bot probes. Private nodes the
owner adds in the dashboard are stored in the music database instead and are
always preferred over these.

Every entry is health-checked before it is handed to Wavelink.  Public nodes
can disappear or change credentials, so keeping this list comprehensive and
easy to replace is intentional.

Last reviewed: 2026-09-21 (originally collected from DarrenOfficial/lavalink-list).
"""

LAVALINK_NODES: list[dict] = [
    # ── SSL / WSS nodes ────────────────────────────────────────────────
    {"host": "lavalinkv4.serenetia.com", "port": 443, "password": "https://seretia.link/discord", "secure": True, "version": "v4"},
    {"host": "lavalink.jirayu.net", "port": 443, "password": "youshallnotpass", "secure": True, "version": "v4"},
    {"host": "lava-v4.millohost.my.id", "port": 443, "password": "https://discord.gg/mjS5J2K3ep", "secure": True, "version": "v4"},
    {"host": "lavalink-v4.triniumhost.com", "port": 443, "password": "free", "secure": True, "version": "v4"},

    # ── Non-SSL / WS nodes ─────────────────────────────────────────────
    {"host": "lavalinkv4.serenetia.com", "port": 80, "password": "https://seretia.link/discord", "secure": False, "version": "v4"},
    {"host": "lavalink.jirayu.net", "port": 13592, "password": "youshallnotpass", "secure": False, "version": "v4"},
    {"host": "lavalink.triniumhost.com", "port": 4333, "password": "free", "secure": False, "version": "v4"},
    {"host": "lavalink.triniumhost.com", "port": 2333, "password": "kirito", "secure": False, "version": "v4"},
    {"host": "lava.g3v.co.uk", "port": 9008, "password": "lavalinklol", "secure": False, "version": "v4"},
    {"host": "n3.nexcloud.in", "port": 2026, "password": "nexcloud", "secure": False, "version": "v4"},
    {"host": "omega.vexanode.cloud", "port": 2031, "password": "https://discord.vexanode.cloud", "secure": False, "version": "v4"},
    {"host": "lava2.kasawa.pro", "port": 2334, "password": "youshallnotpass", "secure": False, "version": "v4"},
    {"host": "lavav4.minecuta.com", "port": 2333, "password": "discord.gg/gKuXdHs", "secure": False, "version": "v4"},
    {"host": "157.254.192.15", "port": 2333, "password": "youshallnotpass", "secure": False, "version": "v4"},
]
