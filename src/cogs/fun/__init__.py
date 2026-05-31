from . import general, roleplay, animals, memes, connect_four, tictactoe, nsfw, uwulock, bnuy, soundboard


async def setup(bot):
    await general.setup(bot)
    await roleplay.setup(bot)
    await animals.setup(bot)
    await memes.setup(bot)
    await connect_four.setup(bot)
    await tictactoe.setup(bot)
    await nsfw.setup(bot)
    await uwulock.setup(bot)
    await bnuy.setup(bot)
    await soundboard.setup(bot)
