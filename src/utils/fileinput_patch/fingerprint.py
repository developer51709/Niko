import discord
import sys
import inspect


def fingerprint_library():
    module_name = discord.__package__ or "discord"
    file_path = inspect.getfile(discord)
    version = getattr(discord, "__version__", "unknown")

    # --------------------------------
    # Detect Disnake
    # --------------------------------
    if "disnake" in module_name or "disnake" in file_path:
        return {
            "lib": "disnake",
            "version": version,
            "features": {
                "has_fileinput": hasattr(discord.ui, "FileInput"),
                "has_inputtype_file": hasattr(discord, "InputType") and hasattr(discord.InputType, "file"),
                "has_modal_handler": any("modal" in name.lower() for name in dir(discord.Interaction)),
            }
        }

    # --------------------------------
    # Detect Nextcord
    # --------------------------------
    if "nextcord" in module_name or "nextcord" in file_path:
        return {
            "lib": "nextcord",
            "version": version,
            "features": {
                "has_fileinput": hasattr(discord.ui, "FileInput"),
                "has_inputtype_file": hasattr(discord, "InputType") and hasattr(discord.InputType, "file"),
                "has_modal_handler": any("modal" in name.lower() for name in dir(discord.Interaction)),
            }
        }

    # --------------------------------
    # Detect Pycord
    # --------------------------------
    # Pycord uses the discord namespace but adds unique modules
    if hasattr(discord, "commands") or "pycord" in version.lower():
        return {
            "lib": "pycord",
            "version": version,
            "features": {
                "has_fileinput": hasattr(discord.ui, "FileInput"),
                "has_inputtype_file": hasattr(discord, "InputType") and hasattr(discord.InputType, "file"),
                "has_modal_handler": any("modal" in name.lower() for name in dir(discord.Interaction)),
            }
        }

    # --------------------------------
    # Default: discord.py
    # --------------------------------
    return {
        "lib": "discord.py",
        "version": version,
        "features": {
            "has_fileinput": hasattr(discord.ui, "FileInput"),
            "has_inputtype_file": hasattr(discord, "InputType") and hasattr(discord.InputType, "file"),
            "has_modal_handler": any("modal" in name.lower() for name in dir(discord.Interaction)),
        }
    }