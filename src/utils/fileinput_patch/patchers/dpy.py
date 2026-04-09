import discord
from .base import BasePatcher

class DPYPatcher(BasePatcher):
    def patch(self):
        # discord.py has no modal handler → patch event dispatcher
        try:
            original_run_event = discord.Client._run_event

            async def patched_run_event(self, event_name, *args, **kwargs):
                if event_name == "interaction_create":
                    interaction = args[0]
                    if interaction.type.name == "modal_submit":
                        self._inject_attachments(interaction)
                return await original_run_event(self, event_name, *args, **kwargs)

            discord.Client._run_event = patched_run_event

        except Exception as e:
            print("[FileInputPatch] Failed to patch discord.py event dispatcher.")
            print("Reason:", str(e))
            print("Solution: File upload modals will be disabled.")
            return

    def _inject_attachments(self, interaction):
        if "attachments" not in interaction.data:
            return

        state = interaction._state
        attachment_map = {
            att["id"]: discord.Attachment(data=att, state=state)
            for att in interaction.data["attachments"]
        }

        for comp in interaction.components:
            for item in comp.children:
                if hasattr(item, "input_type") and item.input_type:
                    attachment_id = item.value
                    if attachment_id in attachment_map:
                        item._attachment = attachment_map[attachment_id]