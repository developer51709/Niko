"""
Startup — cog loader.
Discovers and loads every cog under src/cogs/.
"""

import os
import importlib

from utils import logging


async def load_cogs(bot):
    logging.info("Startup", "Loading cogs...")

    for item in os.listdir("./src/cogs"):
        item_path = os.path.join("./src/cogs", item)

        if os.path.isfile(item_path) and item.endswith(".py") and item != "__init__.py":
            module_name = f"cogs.{item[:-3]}"
        elif os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
            module_name = f"cogs.{item}"
        else:
            continue

        try:
            module = importlib.import_module(module_name)

            if getattr(module, "DNL", False):
                reason = getattr(module, "DNL_REASON", "No reason provided")
                logging.warning("Startup", f"Skipped cog: {module_name} ({reason})")
                continue

            await bot.load_extension(module_name)
            logging.success("Startup", f"Loaded cog: {module_name}")

        except Exception as e:
            logging.error("Startup", f"Failed to load cog {module_name}: {e}")
