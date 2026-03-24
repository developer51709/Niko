import discord
import random
from discord.ext import commands

PERSONALITY = "cafe"

MESSAGES = {
    "normal": {
        "en": {
            "need_mention": "You need to mention someone to use this command on them!",
            "hug_desc": "{author} hugged {target}! :hugging:",
            "kill_desc": "{author} killed {target}!",
            "kill_footer": "*This is a joke, don't actually kill anyone.*",
            "kiss_desc": "{author} kissed {target}! 💋",
        },
        "de": {
            "need_mention": "Du musst jemanden erwähnen, um diesen Befehl zu nutzen!",
            "hug_desc": "{author} hat {target} umarmt! :hugging:",
            "kill_desc": "{author} hat {target} getötet!",
            "kill_footer": "*Das ist ein Witz, töte bitte niemanden wirklich.*",
            "kiss_desc": "{author} hat {target} geküsst! 💋",
        }
    },
    "cafe": {
        "en": {
            "need_mention": "who are we doing this with? mention a friend! ☕✨",
            "hug_desc": "omg! {author} gave {target} a big, warm café hug! ☕💖",
            "kill_desc": "oh no! {author} playfully took out {target}! ☕💀",
            "kill_footer": "*this is just café roleplay, no one actually got hurt ☕*",
            "kiss_desc": "omg! {author} gave {target} a sweet café kiss! ☕️💋",
        },
        "de": {
            "need_mention": "Mit wem machen wir das? Erwähne einen Freund! ☕✨",
            "hug_desc": "omg! {author} hat {target} eine große, warme Café-Umarmung gegeben! ☕💖",
            "kill_desc": "oh nein! {author} hat {target} spielerisch ausgeschaltet! ☕💀",
            "kill_footer": "*das ist nur café-roleplay, niemand wurde wirklich verletzt ☕*",
            "kiss_desc": "omg! {author} hat {target} einen süßen Café-Kuss gegeben! ☕️💋",
        }
    }
}

def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"

def msg(ctx, key, **kwargs):
    personality = PERSONALITY if PERSONALITY in MESSAGES else "normal"
    lang = get_lang(ctx)
    text = MESSAGES.get(personality, {}).get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key, key)
    return text.format(**kwargs) if kwargs else text


class RolePlayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Register context menu commands
        self.hug_context = discord.app_commands.ContextMenu(
            name="Hug 💖",
            callback=self.hug_context_callback
        )
        self.kill_context = discord.app_commands.ContextMenu(
            name="Kill 💀 (playful)",
            callback=self.kill_context_callback
        )
        self.kiss_context = discord.app_commands.ContextMenu(
            name="Kiss 💋",
            callback=self.kiss_context_callback
        )

        bot.tree.add_command(self.hug_context)
        bot.tree.add_command(self.kill_context)
        bot.tree.add_command(self.kiss_context)

    # -----------------------------
    # INTERNAL UI BUILDER
    # -----------------------------
    async def send_roleplay(self, interaction_or_ctx, title, desc, gif, footer=None):
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {title}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=desc),
            discord.ui.MediaGallery(discord.MediaGalleryItem(media=gif)),
        )

        if footer:
            container.children.append(
                discord.ui.TextDisplay(content=f"-# {footer}")
            )

        view.add_item(container)

        if isinstance(interaction_or_ctx, discord.Interaction):
            await interaction_or_ctx.response.send_message(view=view)
        else:
            await interaction_or_ctx.send(view=view)

    # -----------------------------
    # PREFIX COMMANDS
    # -----------------------------
    @commands.command(name="hug")
    async def hug(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send(msg(ctx, "need_mention"))

        gifs = [
            "https://static.klipy.com/ii/e293a233a303a98e471f78d04e13a1b0/88/68/BrZiPlu3.webp",
            "https://static.klipy.com/ii/935d7ab9d8c6202580a668421940ec81/f4/97/FWkQ3IhM.webp",
            "https://static.klipy.com/ii/c3a19a0b747a76e98651f2b9a3cca5ff/8a/00/V2DQIgua.webp"
        ]

        await self.send_roleplay(
            ctx,
            "💖 hug",
            msg(ctx, "hug_desc", author=ctx.author.mention, target=member.mention),
            random.choice(gifs)
        )

    @commands.command(name="kill")
    async def kill(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send(msg(ctx, "need_mention"))

        gifs = [
            "https://i.pinimg.com/originals/36/d5/fd/36d5fd46d8331661819031b2b7adcda4.gif"
        ]

        await self.send_roleplay(
            ctx,
            "💀 kill",
            msg(ctx, "kill_desc", author=ctx.author.mention, target=member.mention),
            random.choice(gifs),
            footer=msg(ctx, "kill_footer")
        )

    @commands.command(name="kiss")
    async def kiss(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send(msg(ctx, "need_mention"))

        gifs = [
            "https://static.klipy.com/ii/ce286d05b8e1a47cd4f32b0e1b6dec0e/38/82/0a0OANF7.webp",
            "https://static.klipy.com/ii/ce286d05b8e1a47cd4f32b0e1b6dec0e/18/bf/Gv1G1AU3.webp",
            "https://static.klipy.com/ii/ce286d05b8e1a47cd4f32b0e1b6dec0e/10/e0/7NCymQJ9.webp",
            "https://static.klipy.com/ii/c3a19a0b747a76e98651f2b9a3cca5ff/3c/c3/sw6nuW60.webp"
        ]

        await self.send_roleplay(
            ctx,
            "💋 kiss",
            msg(ctx, "kiss_desc", author=ctx.author.mention, target=member.mention),
            random.choice(gifs)
        )

    # -----------------------------
    # CONTEXT MENU COMMANDS
    # -----------------------------
    async def hug_context_callback(self, interaction: discord.Interaction, member: discord.Member):
        ctx = interaction
        gifs = [
            "https://static.klipy.com/ii/e293a233a303a98e471f78d04e13a1b0/88/68/BrZiPlu3.webp",
            "https://static.klipy.com/ii/935d7ab9d8c6202580a668421940ec81/f4/97/FWkQ3IhM.webp",
            "https://static.klipy.com/ii/c3a19a0b747a76e98651f2b9a3cca5ff/8a/00/V2DQIgua.webp"
        ]
        await self.send_roleplay(
            interaction,
            "💖 hug",
            msg(ctx, "hug_desc", author=interaction.user.mention, target=member.mention),
            random.choice(gifs)
        )

    async def kill_context_callback(self, interaction: discord.Interaction, member: discord.Member):
        ctx = interaction
        gifs = ["https://i.pinimg.com/originals/36/d5/fd/36d5fd46d8331661819031b2b7adcda4.gif"]
        await self.send_roleplay(
            interaction,
            "💀 kill",
            msg(ctx, "kill_desc", author=interaction.user.mention, target=member.mention),
            random.choice(gifs),
            footer=msg(ctx, "kill_footer")
        )

    async def kiss_context_callback(self, interaction: discord.Interaction, member: discord.Member):
        ctx = interaction
        gifs = [
            "https://static.klipy.com/ii/ce286d05b8e1a47cd4f32b0e1b6dec0e/38/82/0a0OANF7.webp",
            "https://static.klipy.com/ii/ce286d05b8e1a47cd4f32b0e1b6dec0e/18/bf/Gv1G1AU3.webp",
            "https://static.klipy.com/ii/ce286d05b8e1a47cd4f32b0e1b6dec0e/10/e0/7NCymQJ9.webp",
            "https://static.klipy.com/ii/c3a19a0b747a76e98651f2b9a3cca5ff/3c/c3/sw6nuW60.webp"
        ]
        await self.send_roleplay(
            interaction,
            "💋 kiss",
            msg(ctx, "kiss_desc", author=interaction.user.mention, target=member.mention),
            random.choice(gifs)
        )


async def setup(bot):
    await bot.add_cog(RolePlayCog(bot))