from . import cog as _notifier_cog, youtube


async def setup(bot):
    await _notifier_cog.setup(bot)
    await youtube.setup(bot)
