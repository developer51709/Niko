from . import error_handler, image_tools, introduction, webhook_proxy, ip_detector, fileinput_patch


async def setup(bot):
    await error_handler.setup(bot)
    await image_tools.setup(bot)
    await introduction.setup(bot)
    await webhook_proxy.setup(bot)
    await ip_detector.setup(bot)
    await fileinput_patch.setup(bot)
