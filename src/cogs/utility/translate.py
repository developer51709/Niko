import discord

from utils.translator import Translator, SUPPORTED_LANGUAGES

from discord.ext import commands
from discord import app_commands


# Languages offered in the select menus (codes must exist in
# SUPPORTED_LANGUAGES). Capped at 24 so the "from" menu fits its 25-option
# limit together with the auto-detect option.
POPULAR_LANGUAGE_CODES = [
    "en", "de", "es", "fr", "ja", "ko", "zh-CN", "zh-TW",
    "pt", "it", "ru", "ar", "hi", "nl", "pl", "tr",
    "sv", "da", "no", "fi", "cs", "el", "he", "uk",
]

_NAME_BY_CODE = {code: name.title() for name, code in SUPPORTED_LANGUAGES.items()}

LANGUAGE_CHOICES: list[tuple[str, str]] = [
    (code, _NAME_BY_CODE.get(code, code))
    for code in POPULAR_LANGUAGE_CODES
    if code in _NAME_BY_CODE
]


class TranslateSelectView(discord.ui.LayoutView):
    """Ephemeral picker with a translate-to select and an optional from select.

    Both selects carry bound callbacks, so the view works for as long as the
    (ephemeral) picker message exists. The target message id rides in the
    custom ids; the chosen source language is kept in ``cog._pending`` keyed
    by ``(user_id, message_id)`` and consumed by the translate-to pick.
    """

    def __init__(self, cog: "ContextMenu", message_id: int, src: str = "auto") -> None:
        self.cog = cog
        self.message_id = message_id

        to_select = discord.ui.Select(
            custom_id=f"translate_to:{message_id}",
            placeholder="🌐 Translate to…",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label=name, value=code)
                for code, name in LANGUAGE_CHOICES
            ],
        )
        to_select.callback = self.on_to_select

        from_select = discord.ui.Select(
            custom_id=f"translate_from:{message_id}",
            placeholder="🔎 Translate from… (optional — auto-detect)",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Auto-detect", value="auto", default=src == "auto"),
                *[
                    discord.SelectOption(label=name, value=code, default=code == src)
                    for code, name in LANGUAGE_CHOICES
                ],
            ],
        )
        from_select.callback = self.on_from_select

        items: list = [
            discord.ui.TextDisplay(content="### 🌐 Translate Message"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(to_select),
            discord.ui.ActionRow(from_select),
        ]
        if src != "auto":
            items.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            items.append(
                discord.ui.TextDisplay(
                    content=(
                        f"-# Source: **{_NAME_BY_CODE.get(src, src)}** — "
                        "now pick the language to translate to."
                    )
                )
            )

        super().__init__()
        self.add_item(discord.ui.Container(*items))

    async def on_to_select(self, interaction: discord.Interaction) -> None:
        await self.cog.handle_to_select(interaction, self.message_id)

    async def on_from_select(self, interaction: discord.Interaction) -> None:
        await self.cog.handle_from_select(interaction, self.message_id)


class ContextMenu(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        # (user_id, picker_message_id) -> {"content": str, "src": str}
        self._pending: dict[tuple[int, int], dict] = {}

        self.context_commands = [
            app_commands.ContextMenu(
                name = "Translate",
                callback = self.translate_message,
                type = discord.AppCommandType.message,
            )
        ]

        for command in self.context_commands:
            self.bot.tree.add_command(command)

    async def cog_unload(self) -> None:
        for command in self.context_commands:
            self.bot.tree.remove_command(command.name, type=command.type)

    async def translate_message(self, interaction: discord.Interaction, message: discord.Message) -> None:
        if not message.content.strip():
            await interaction.response.send_message("The message is empty.", ephemeral=True)
            return

        # Cap the pending map so abandoned pickers cannot grow it unbounded.
        if len(self._pending) > 500:
            for key in list(self._pending)[: len(self._pending) - 500]:
                self._pending.pop(key, None)

        self._pending[(interaction.user.id, message.id)] = {
            "content": message.content,
            "src": "auto",
        }
        view = TranslateSelectView(self, message.id)
        await interaction.response.send_message(view=view, ephemeral=True)

    # ── select handling ───────────────────────────────────────────────────

    async def handle_from_select(self, interaction: discord.Interaction, message_id: int) -> None:
        """Remember the chosen source language and re-render the picker."""
        values = (interaction.data or {}).get("values") or []
        src = str(values[0]) if values else "auto"

        pending = self._pending.get((interaction.user.id, message_id))
        if pending is not None:
            pending["src"] = src
        else:
            pending = {"content": None, "src": src}
            self._pending[(interaction.user.id, message_id)] = pending

        # Re-render through the same view class so every select keeps its
        # bound callback, and the chosen source shows as selected.
        view = TranslateSelectView(self, message_id, src=src)
        await interaction.response.edit_message(view=view)

    async def handle_to_select(self, interaction: discord.Interaction, message_id: int) -> None:
        """Translate the stored message content into the chosen language."""
        values = (interaction.data or {}).get("values") or []
        if not values:
            return
        dest_code = str(values[0])

        pending = self._pending.pop((interaction.user.id, message_id), None)
        content = (pending or {}).get("content")
        src = (pending or {}).get("src", "auto")
        if not content or not content.strip():
            self._pending.pop((interaction.user.id, message_id), None)
            await interaction.response.send_message(
                "That translate request has expired — run Translate again.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        try:
            analysis = await Translator.detect(content) if src == "auto" else src
            source_flag = Translator.code_to_flag(analysis)
            dest_flag = Translator.code_to_flag(dest_code)
            dest_name = _NAME_BY_CODE.get(dest_code, dest_code)
            translation = await Translator.translate(content, dest=dest_code, src=src)

            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=f"### {source_flag} -> {dest_flag}"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=f"**Original:**\n{content.strip()}"),
                discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=f"**Translation:**\n{translation}"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=(
                        "-# Translated using Google Translate"
                        + ("" if src == "auto" else f" from {_NAME_BY_CODE.get(src, src)}")
                        + f" to {dest_name}."
                    )
                ),
            )
            view.add_item(container)
            await interaction.followup.send(view=view, ephemeral=True)
        except Exception:
            await interaction.followup.send(
                "Translation failed — try a different language.", ephemeral=True
            )
            return

        # Done — dismiss the ephemeral picker.
        try:
            await interaction.delete_original_response()
        except discord.HTTPException:
            pass


async def setup(bot) -> None:
    await bot.add_cog(ContextMenu(bot))