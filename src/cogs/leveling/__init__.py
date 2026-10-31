from .cog import Leveling
from .migration import LevelMigration


async def setup(bot):
    await bot.add_cog(Leveling(bot))
    # The join DM and the import it offers are their own cog, so the leveling
    # commands and that listener stay independent pieces of state.
    await bot.add_cog(LevelMigration(bot))
