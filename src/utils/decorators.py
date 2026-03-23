from discord.ext import commands


def group(*args, **kwargs):
    return commands.group(*args, **kwargs)