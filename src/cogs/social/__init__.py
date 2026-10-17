from . import birthdays, polls, suggestions, starboard, pfps


async def setup(bot):
    await birthdays.setup(bot)
    await polls.setup(bot)
    await suggestions.setup(bot)
    await starboard.setup(bot)
    await pfps.setup(bot)
