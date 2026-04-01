# interaction_patch.py
import json
import discord
from discord.ext import commands


class InteractionPatch(commands.Cog):
    """
    Restores Discord's hidden interaction + integration metadata to discord.Message.

    Exposes:
        message.interaction_metadata_ex     -> raw interaction_metadata
        message.integration_owners_ex       -> raw integration_owners
        message.trigger_user_ex             -> the user who triggered the app
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # message_id -> metadata
        self._interaction_metadata = {}
        self._integration_owners = {}
        self._trigger_users = {}

        # Attach this cog to bot state so patched properties can find it
        bot._connection._interaction_patch_cog = self

        # Patch Message class once
        if not getattr(discord.Message, "_interaction_patch_applied", False):
            self._patch_message_class()
            discord.Message._interaction_patch_applied = True

    # ──────────────────────────────────────────────────────────────
    # Patch discord.Message with safe, non-conflicting properties
    # ──────────────────────────────────────────────────────────────
    def _patch_message_class(self):

        def _get_interaction_metadata(msg: discord.Message):
            cog = msg._state._interaction_patch_cog
            return cog._interaction_metadata.get(msg.id)

        def _get_integration_owners(msg: discord.Message):
            cog = msg._state._interaction_patch_cog
            return cog._integration_owners.get(msg.id)

        def _get_trigger_user(msg: discord.Message):
            cog = msg._state._interaction_patch_cog
            return cog._trigger_users.get(msg.id)

        setattr(discord.Message, "interaction_metadata_ex", property(_get_interaction_metadata))
        setattr(discord.Message, "integration_owners_ex", property(_get_integration_owners))
        setattr(discord.Message, "trigger_user_ex", property(_get_trigger_user))

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
        msg_id = int(payload["id"])

        # 1. Newer field: interaction_metadata
        if "interaction_metadata" in payload:
            self._interaction_metadata[msg_id] = payload["interaction_metadata"]

            # Extract trigger user if present
            user = payload["interaction_metadata"].get("user")
            if user:
                self._trigger_users[msg_id] = discord.Object(id=int(user["id"]))

        # 2. Older field: interaction.user
        if "interaction" in payload and payload["interaction"]:
            user = payload["interaction"].get("user")
            if user:
                self._trigger_users[msg_id] = discord.Object(id=int(user["id"]))

        # 3. The important one: application.integration_owners
        app = payload.get("application")
        if app and "integration_owners" in app:
            owners = app["integration_owners"]
            self._integration_owners[msg_id] = owners

            # If user-installed app → key "1" is the user ID
            if "1" in owners:
                self._trigger_users[msg_id] = discord.Object(id=int(owners["1"]))


async def setup(bot: commands.Bot):
    await bot.add_cog(InteractionPatch(bot))