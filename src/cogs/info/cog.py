"""Info cog — composes every info command mixin into a single cog.

The commands are grouped by what they describe:

- ``_server``  — serverinfo, roleinfo, servericon, serverbanner, booststats
- ``_users``   — userinfo, avatar, banner
- ``_about``   — about, creator, invite
- ``_spotify`` — spotify and its loading card
- ``_system``  — debuginfo, hostinfo, shards

``_messages`` holds the EN/DE/ES strings and the card builders all of them
share, ``_avatars`` the persistent avatar buttons and ``_badges`` the badge
emojis the userinfo card draws.
"""

import time

from discord.ext import commands

from ._about import AboutMixin
from ._avatars import register_avatar_persistent_views
from ._server import ServerMixin
from ._spotify import SpotifyMixin
from ._system import SystemMixin
from ._users import UserMixin


class InfoCog(
    AboutMixin,
    ServerMixin,
    SpotifyMixin,
    SystemMixin,
    UserMixin,
    commands.Cog,
):
    """Bilingual server, user and bot info commands."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "start_time"):
            self.bot.start_time = time.time()

    async def cog_load(self):
        register_avatar_persistent_views(self.bot)


async def setup(bot):
    await bot.add_cog(InfoCog(bot))
