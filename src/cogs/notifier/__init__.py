from . import cog as _notifier_cog


async def setup(bot):
    await _notifier_cog.setup(bot)
