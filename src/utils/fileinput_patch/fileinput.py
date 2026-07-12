import discord

def ensure_universal_fileinput():
    # If the library already has FileInput, do nothing
    if hasattr(discord.ui, "FileInput"):
        return

    # Inject universal FileInput
    class FileInput(discord.ui.TextInput):
        def __init__(self, label="Upload File", required=True):
            super().__init__(
                label=label,
                required=required,
                style=discord.TextStyle.short
            )
            self.input_type = getattr(discord, "InputType", None)
            self._attachment = None

        @property
        def value(self):
            return self._attachment

    discord.ui.FileInput = FileInput