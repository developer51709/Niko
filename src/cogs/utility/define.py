import discord
from discord.ext import commands
import aiohttp
import textwrap


def format_definition_dict(entry: dict) -> str:
    """Convert the dictionary entry into a clean, readable block."""
    word = entry.get("word", "unknown")
    phonetic = entry.get("phonetic", "N/A")
    origin = entry.get("origin", "N/A")

    lines = [
        f"**Word:** {word}",
        f"**Phonetic:** {phonetic}",
        f"**Origin:** {origin}",
        "",
        "**Meanings:**"
    ]

    for meaning in entry.get("meanings", []):
        pos = meaning.get("partOfSpeech", "unknown")
        lines.append(f"• *{pos}*")

        for d in meaning.get("definitions", []):
            definition = d.get("definition", "")
            example = d.get("example", None)

            lines.append(f"-#     - {definition}")
            # if example:
            #     lines.append(f"    _Example:_ {example}")

        lines.append("")

    return "\n".join(lines)


class Define(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="define", help="Define a word using a dictionary API.")
    async def define(self, ctx, *, word: str):
        # trigger typing indicator
        async with ctx.typing():

            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status != 200:
                        return await ctx.reply(f"No definition found for **{word}**.")

                    data = await r.json()

            entry = data[0]

            # Normalize into a clean dict-like structure
            definition_dict = {
                "word": entry.get("word", "unknown"),
                "phonetic": entry.get("phonetic", "N/A"),
                "origin": entry.get("origin", "N/A"),
                "meanings": []
            }

            for meaning in entry.get("meanings", []):
                definition_dict["meanings"].append({
                    "partOfSpeech": meaning.get("partOfSpeech", "unknown"),
                    "definitions": meaning.get("definitions", [])
                })

            # Convert to readable block
            pretty_text = format_definition_dict(definition_dict)

            # Create the LayoutView
            view = discord.ui.LayoutView()
        
            # Build Components v2 container
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=f"### Definition: **{word}**"),
                discord.ui.Separator(),
                discord.ui.TextDisplay(content=pretty_text),
                accent_colour=discord.Colour(0x5865F2)
            )

            # add the container to the view
            view.add_item(container)

        await ctx.reply(view=view)


async def setup(bot):
    await bot.add_cog(Define(bot))