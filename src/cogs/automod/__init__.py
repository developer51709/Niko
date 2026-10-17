from . import cog, mrbeast_scam


async def setup(bot):
    await cog.setup(bot)
    await mrbeast_scam.setup(bot)
