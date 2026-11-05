from .cog import Setup


async def setup(bot):
    await bot.add_cog(Setup(bot))
