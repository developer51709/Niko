# interaction_metadata_patch.py
import json
import discord
from discord.ext import commands


class InteractionMetadataPatch(commands.Cog):
    """
    Adds a safe, non-conflicting property to discord.Message:
        message.interaction_metadata_ex

    This exposes the hidden 'interaction_metadata' field from raw
    MESSAGE_CREATE events without conflicting with discord.py internals.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # message_id -> metadata
        self._interaction_meta = {}

        # Attach this cog to the bot state so the property can access it
        bot._connection._interaction_metadata_cog = self

        # Patch the Message class once
        if not getattr(discord.Message, "_interaction_metadata_ex_patched", False):
            self._patch_message_class()
            discord.Message._interaction_metadata_ex_patched = True

    # ──────────────────────────────────────────────────────────────
    # Patch discord.Message to expose .interaction_metadata_ex
    # ──────────────────────────────────────────────────────────────
    def _patch_message_class(self):
        def _get_interaction_metadata_ex(msg: discord.Message):
            cog = msg._state._interaction_metadata_cog
            return cog._interaction_meta.get(msg.id)

        # Use a SAFE attribute name discord.py will never touch
        setattr(discord.Message, "interaction_metadata_ex", property(_get_interaction_metadata_ex))

    # ──────────────────────────────────────────────────────────────
    # Capture raw MESSAGE_CREATE events
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