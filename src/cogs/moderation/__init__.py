from . import commands, utils


async def setup(bot):
    await commands.setup(bot)
    await utils.setup(bot)
