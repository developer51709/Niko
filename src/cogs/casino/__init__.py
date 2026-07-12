from . import slots, blackjack, roulette, gambling


async def setup(bot):
    await slots.setup(bot)
    await blackjack.setup(bot)
    await roulette.setup(bot)
    await gambling.setup(bot)
