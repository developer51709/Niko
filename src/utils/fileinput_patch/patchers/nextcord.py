import discord
from .base import BasePatcher

class NextcordPatcher(BasePatcher):
    def patch(self):
        handler_name = "_process_modal_submit"

        if not hasattr(discord.Interaction, handler_name):
            print("[FileInputPatch] Nextcord modal handler not found.")
            print("Reason: Nextcord version changed internal handler name.")
            print("Solution: Update Nextcord.")
            return

        original = getattr(discord.Interaction, handler_name)

        async def patched(self, data):
            await original(self, data)
            self._inject_attachments(data)

        setattr(discord.Interaction, handler_name, patched)

    def _inject_attachments(self, data):
        if "attachments" not in data:
            return

        state = self._state
        attachment_map = {
            att["id"]: discord.Attachment(data=att, state=state)
            for att in data["attachments"]
        }

        for comp in self.components:
            for item in comp.children:
                if hasattr(item, "input_type") and item.input_type:
                    attachment_id = item.value
                    if attachment_id in attachment_map:
                        item._attachment = attachment_map[attachment_id]