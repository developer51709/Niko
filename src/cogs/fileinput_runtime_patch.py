from discord.ext import commands
from utils.fileinput_patch.universal_patcher import UniversalPatcher

class FileInputRuntimePatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        UniversalPatcher().apply(bot)

async def setup(bot):
    await bot.add_cog(FileInputRuntimePatch(bot))