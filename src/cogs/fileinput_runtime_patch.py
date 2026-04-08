import discord
from discord.ext import commands
from discord.ui import TextInput
from discord.enums import Enum


class FileInputRuntimePatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.patch_input_type()
        self.patch_file_input()
        self.patch_interaction_parser()

    # ---------------------------------------------------------
    # 1. Add InputType.file
    # ---------------------------------------------------------
    def patch_input_type(self):
        if not hasattr(discord, "InputType"):
            class InputType(Enum):
                text = 1
                file = 2
            discord.InputType = InputType
        else:
            discord.InputType.file = 2

    # ---------------------------------------------------------
    # 2. Add FileInput UI component
    # ---------------------------------------------------------
    def patch_file_input(self):
        if hasattr(discord.ui, "FileInput"):
            return

        class FileInput(TextInput):
            def __init__(self, label="Upload File", required=True):
                super().__init__(
                    label=label,
                    required=required,
                    style=discord.TextStyle.short
                )
                self.input_type = discord.InputType.file
                self._attachment = None

            @property
            def value(self):
                return self._attachment

        discord.ui.FileInput = FileInput

    # ---------------------------------------------------------
    # 3. Patch Interaction._from_data (discord.py version)
    # ---------------------------------------------------------
    def patch_interaction_parser(self):
        original_from_data = discord.Interaction._from_data

        def patched_from_data(cls, data):
            interaction = original_from_data(cls, data)

            # Only patch modal submissions
            if interaction.type.name != "modal_submit":
                return interaction

            state = interaction._state

            # Build attachment map
            attachment_map = {}
            if "attachments" in data:
                for att in data["attachments"]:
                    attachment_map[att["id"]] = discord.Attachment(
                        data=att,
                        state=state
                    )

            # Inject attachments into FileInput components
            for comp in interaction.components:
                for item in comp.children:
                    if isinstance(item, TextInput):
                        if getattr(item, "input_type", None) == discord.InputType.file:
                            attachment_id = item.value
                            if attachment_id in attachment_map:
                                item._attachment = attachment_map[attachment_id]

            return interaction

        discord.Interaction._from_data = classmethod(patched_from_data)


async def setup(bot):
    await bot.add_cog(FileInputRuntimePatch(bot))