from . import owner, development, customization, prefix, emoji, pfps


async def setup(bot):
    await owner.setup(bot)
    await development.setup(bot)
    await customization.setup(bot)
    await prefix.setup(bot)
    await emoji.setup(bot)
    await pfps.setup(bot)
