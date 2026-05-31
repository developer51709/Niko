"""
Soundboard — play guild & Discord default sounds in voice channels.

Commands (/soundboard group):
    /soundboard list         — list guild sounds + default sounds
    /soundboard play <name>  — play a sound in your current VC (autocomplete)
    /soundboard default      — list all Discord default sounds

Nitro note: bots can play soundboard sounds without Nitro restrictions.
The `send-soundboard-sound` endpoint works for any bot in a voice channel.
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from config.emojis import get_emoji


def _container(text: str, *, colour: discord.Colour | None = None) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    kw: dict = {}
    if colour:
        kw["accent_colour"] = colour
    view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text), **kw))
    return view


class SoundboardCog(commands.Cog, name="Soundboard"):
    """Play guild and default Discord sounds in voice channels."""

    soundboard = app_commands.Group(
        name="soundboard",
        description="Play guild soundboard sounds in your voice channel.",
    )

    # ── /soundboard list ──────────────────────────────────────────────────

    @soundboard.command(name="list", description="List guild and default soundboard sounds.")
    @app_commands.guild_only()
    async def soundboard_list(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        guild_sounds: list[dict] = []
        default_sounds: list[dict] = []

        try:
            data = await interaction.client.http.get_soundboard_sounds(interaction.guild_id)
            guild_sounds = data.get("items", []) if isinstance(data, dict) else list(data)
        except Exception:
            pass

        try:
            default_sounds = list(await interaction.client.http.get_soundboard_default_sounds())
        except Exception:
            pass

        lines: list[str] = []

        if guild_sounds:
            lines.append(f"### {get_emoji('icon_music')} Guild Sounds")
            for s in guild_sounds:
                emo = f"{s.get('emoji_name', '')} " if s.get("emoji_name") else "🔊 "
                lines.append(f"- {emo}**{s['name']}**  `-# id: {s['sound_id']}`")

        if default_sounds:
            lines.append(f"\n### {get_emoji('icon_star')} Discord Default Sounds")
            for s in default_sounds[:15]:
                emo = f"{s.get('emoji_name', '')} " if s.get("emoji_name") else "🔊 "
                lines.append(f"- {emo}**{s['name']}**")
            if len(default_sounds) > 15:
                lines.append(f"-# …and {len(default_sounds) - 15} more")

        if not lines:
            await interaction.followup.send(
                view=_container("No soundboard sounds found for this server."),
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            view=_container("\n".join(lines), colour=discord.Colour(0xc8a882)),
            ephemeral=True,
        )

    # ── /soundboard play ──────────────────────────────────────────────────

    @soundboard.command(name="play", description="Play a soundboard sound in your voice channel.")
    @app_commands.describe(name="Name of the sound to play")
    @app_commands.guild_only()
    async def soundboard_play(self, interaction: discord.Interaction, name: str) -> None:
        if not interaction.user.voice or not interaction.user.voice.channel:  # type: ignore[union-attr]
            await interaction.response.send_message(
                view=_container(f"{get_emoji('icon_cross')} You need to be in a voice channel."),
                ephemeral=True,
            )
            return

        vc = interaction.user.voice.channel  # type: ignore[union-attr]
        await interaction.response.defer(ephemeral=True)

        sound_id: str | None = None
        source_guild_id: int | None = None
        display_name = name
        display_emoji = "🔊"

        # Search guild sounds first
        try:
            data = await interaction.client.http.get_soundboard_sounds(interaction.guild_id)
            sounds = data.get("items", []) if isinstance(data, dict) else list(data)
            for s in sounds:
                if s["name"].lower() == name.lower():
                    sound_id = s["sound_id"]
                    source_guild_id = interaction.guild_id
                    display_name = s["name"]
                    display_emoji = s.get("emoji_name") or "🔊"
                    break
        except Exception:
            pass

        # Fall back to default sounds
        if sound_id is None:
            try:
                defaults = list(await interaction.client.http.get_soundboard_default_sounds())
                for s in defaults:
                    if s["name"].lower() == name.lower():
                        sound_id = s["sound_id"]
                        source_guild_id = None
                        display_name = s["name"]
                        display_emoji = s.get("emoji_name") or "🔊"
                        break
            except Exception:
                pass

        if sound_id is None:
            await interaction.followup.send(
                view=_container(f"{get_emoji('icon_cross')} No sound named **{name}** found. Use `/soundboard list` to see available sounds."),
                ephemeral=True,
            )
            return

        try:
            payload: dict = {"sound_id": sound_id}
            if source_guild_id is not None:
                payload["source_guild_id"] = source_guild_id
            await interaction.client.http.send_soundboard_sound(vc.id, **payload)
            await interaction.followup.send(
                view=_container(
                    f"### {display_emoji} Playing **{display_name}** in {vc.mention} ☕",
                    colour=discord.Colour(0x57f287),
                ),
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                view=_container(f"{get_emoji('icon_cross')} Could not play sound: {e}"),
                ephemeral=True,
            )

    @soundboard_play.autocomplete("name")
    async def play_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        choices: list[app_commands.Choice[str]] = []
        try:
            data = await interaction.client.http.get_soundboard_sounds(interaction.guild_id)
            sounds = data.get("items", []) if isinstance(data, dict) else list(data)
            for s in sounds:
                if current.lower() in s["name"].lower():
                    choices.append(app_commands.Choice(name=s["name"], value=s["name"]))
        except Exception:
            pass
        try:
            defaults = list(await interaction.client.http.get_soundboard_default_sounds())
            for s in defaults:
                if current.lower() in s["name"].lower():
                    choices.append(app_commands.Choice(name=f"{s['name']} (default)", value=s["name"]))
        except Exception:
            pass
        return choices[:25]

    # ── /soundboard default ───────────────────────────────────────────────

    @soundboard.command(name="default", description="List all Discord default soundboard sounds.")
    async def soundboard_default(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            defaults = list(await interaction.client.http.get_soundboard_default_sounds())
        except Exception as e:
            await interaction.followup.send(
                view=_container(f"{get_emoji('icon_cross')} Could not fetch default sounds: {e}"),
                ephemeral=True,
            )
            return

        lines = [f"### {get_emoji('icon_star')} Discord Default Soundboard Sounds"]
        for s in defaults:
            emo = f"{s.get('emoji_name', '')} " if s.get("emoji_name") else ""
            lines.append(f"- {emo}**{s['name']}**")

        await interaction.followup.send(
            view=_container("\n".join(lines), colour=discord.Colour(0x5865f2)),
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SoundboardCog(bot))
