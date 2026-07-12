from . import chat, config, images


async def setup(bot):
    await chat.setup(bot)
    await config.setup(bot)
    await images.setup(bot)
