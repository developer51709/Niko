# interaction_metadata_patch.py
import json
import discord
from discord.ext import commands


class InteractionMetadataPatch(commands.Cog):
    """
    Patches discord.py so that discord.Message.interaction_metadata
    returns the real metadata from MESSAGE_CREATE raw events.

    This restores the missing 'Triggered by <user>' info that Discord
    shows in the client but discord.py does not expose.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # message_id -> metadata dict
        self._interaction_meta = {}

        # Attach this cog to the bot state so the patched property can find it
        bot._connection._interaction_metadata_cog = self

        # Monkey‑patch discord.Message only once
        if not hasattr(discord.Message, "_interaction_metadata_patched"):
            self._patch_message_class()
            discord.Message._interaction_metadata_patched = True

    # ──────────────────────────────────────────────────────────────
    # Patch discord.Message to expose .interaction_metadata
    # ──────────────────────────────────────────────────────────────
    def _patch_message_class(self):
        def _get_interaction_metadata(msg: discord.Message):
            cog = msg._state._interaction_metadata_cog
            return cog._interaction_meta.get(msg.id)

        discord.Message.interaction_metadata = property(_get_interaction_metadata)

    # ──────────────────────────────────────────────────────────────
    # Capture raw MESSAGE_CREATE events and store metadata
    # ──────────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_socket_raw_receive(self, raw: str):
        try:
            data = json.loads(raw)
        except Exception:
            return

        if data.get("t") != "MESSAGE_CREATE":
            return

        payload = data["d"]
        meta = payload.get("interaction_metadata")
        if not meta:
            return

        message_id = int(payload["id"])
        self._interaction_meta[message_id] = meta


async def setup(bot: commands.Bot):
    await bot.add_cog(InteractionMetadataPatch(bot))