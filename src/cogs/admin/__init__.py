from . import customization, language, prefix, emoji, triggers


async def setup(bot):
    await customization.setup(bot)
    await language.setup(bot)
    await prefix.setup(bot)
    await emoji.setup(bot)
    await triggers.setup(bot)
