from . import staff, customization, prefix, emoji, pfps, triggers


async def setup(bot):
    await staff.setup(bot)
    await customization.setup(bot)
    await prefix.setup(bot)
    await emoji.setup(bot)
    await pfps.setup(bot)
    await triggers.setup(bot)
