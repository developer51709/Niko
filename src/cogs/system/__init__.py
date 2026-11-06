from . import developer_appeals, error_handler, introduction, fileinput_patch, server_stats, guild_ownership, boosters


async def setup(bot):
    await developer_appeals.setup(bot)
    await error_handler.setup(bot)
    await introduction.setup(bot)
    await fileinput_patch.setup(bot)
    await server_stats.setup(bot)
    await guild_ownership.setup(bot)
    await boosters.setup(bot)
