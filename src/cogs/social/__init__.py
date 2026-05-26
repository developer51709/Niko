from . import birthdays, polls, suggestions, starboard


async def setup(bot):
    await birthdays.setup(bot)
    await polls.setup(bot)
    await suggestions.setup(bot)
    await starboard.setup(bot)
