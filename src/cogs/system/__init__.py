from . import error_handler, introduction, fileinput_patch, nitro, server_stats


async def setup(bot):
    await error_handler.setup(bot)
    await introduction.setup(bot)
    await fileinput_patch.setup(bot)
    await nitro.setup(bot)
    await server_stats.setup(bot)
