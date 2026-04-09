import discord
from .base import BasePatcher

class PycordPatcher(BasePatcher):
    def patch(self):
        # Pycord has _handle_modal_submit
        handler_name = "_handle_modal_submit"

        if not hasattr(discord.Interaction, handler_name):
            print("[FileInputPatch] Pycord modal handler not found.")
            print("Reason: Pycord version changed internal handler name.")
            print("Solution: Update Pycord.")
            return

        original = getattr(discord.Interaction, handler_name)

        async def patched(self):
            await original(self)
            self._inject_attachments()

        setattr(discord.Interaction, handler_name, patched)

    def _inject_attachments(self):
        if "attachments" not in self.data:
            return

        state = self._state
        attachment_map = {
            att["id"]: discord.Attachment(data=att, state=state)
            for att in self.data["attachments"]
        }

        for comp in self.components:
            for item in comp.children:
                if hasattr(item, "input_type") and item.input_type:
                    attachment_id = item.value
                    if attachment_id in attachment_map:
                        item._attachment = attachment_map[attachment_id]