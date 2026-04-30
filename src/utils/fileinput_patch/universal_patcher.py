from .fingerprint import fingerprint_library
from .crawler import crawl_for_modal_handlers
from .fileinput import ensure_universal_fileinput

from .patchers.dpy import DPYPatcher
from .patchers.pycord import PycordPatcher
from .patchers.nextcord import NextcordPatcher
from .patchers.disnake import DisnakePatcher


class UniversalPatcher:
    def apply(self, bot):
        fp = fingerprint_library()
        handlers = crawl_for_modal_handlers()

        ensure_universal_fileinput()

        lib = fp["lib"]

        if lib == "discord.py":
            DPYPatcher(bot, fp, handlers).patch()

        elif lib == "pycord":
            PycordPatcher(bot, fp, handlers).patch()

        elif lib == "nextcord":
            NextcordPatcher(bot, fp, handlers).patch()

        elif lib == "disnake":
            DisnakePatcher(bot, fp, handlers).patch()

        else:
            print("[FileInputPatch] Unsupported Discord library.")
            print("Reason: Could not identify library type.")
            print("Solution: Use discord.py, Pycord, Nextcord, or Disnake.")