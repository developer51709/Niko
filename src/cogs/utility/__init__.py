from . import general, afk, snipe, define, tags, reminders, highlights, translate


async def setup(bot):
    await general.setup(bot)
    await afk.setup(bot)
    await snipe.setup(bot)
    await define.setup(bot)
    await tags.setup(bot)
    await reminders.setup(bot)
    await highlights.setup(bot)
    await translate.setup(bot)
