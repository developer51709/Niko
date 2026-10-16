from . import general, afk, snipe, define, tags, reminders, highlights, translate, sticky, image_tools, dm_purge


async def setup(bot):
    await general.setup(bot)
    await afk.setup(bot)
    await snipe.setup(bot)
    await define.setup(bot)
    await tags.setup(bot)
    await reminders.setup(bot)
    await highlights.setup(bot)
    await translate.setup(bot)
    await sticky.setup(bot)
    await image_tools.setup(bot)
    await dm_purge.setup(bot)
