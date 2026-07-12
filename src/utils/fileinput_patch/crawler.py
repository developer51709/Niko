import inspect
import discord

def crawl_for_modal_handlers():
    handlers = []

    for name, member in inspect.getmembers(discord.Interaction):
        if "modal" in name.lower():
            if inspect.iscoroutinefunction(member) or inspect.isfunction(member):
                handlers.append(name)

    return handlers