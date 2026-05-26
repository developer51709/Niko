from discord.ext import commands
import asyncio
import requests
import discord
import random
from utils.ai_config import get_personality

# -----------------------------
# MESSAGE DICTIONARY
# -----------------------------
MESSAGES = {
    "normal": {
        "en": {
            "fetch_fail": "Couldn't fetch a cute animal right now.",
            "sending_random": "Here's a random {animal}:",
            "sending_cat": "Here's a cat:",
            "sending_dog": "Here's a dog:",
        },
        "de": {
            "fetch_fail": "Konnte gerade kein süßes Tier abrufen.",
            "sending_random": "Hier ist ein zufälliges {animal}:",
            "sending_cat": "Hier ist eine Katze:",
            "sending_dog": "Hier ist ein Hund:",
        },
        "es": {
            "fetch_fail": "No pude traer un animalito ahora mismo.",
            "sending_random": "Aquí tienes un {animal} aleatorio:",
            "sending_cat": "Aquí tienes un gato:",
            "sending_dog": "Aquí tienes un perro:",
        },
    },

    "cafe": {
        "en": {
            "fetch_fail": "aww i couldn’t fetch a cute lil animal rn 😭☕",
            "sending_random": "okay bestie, here’s a cozy lil {animal} for you ☕✨",
            "sending_cat": "brewing a soft lil kitty just for you ☕🐱",
            "sending_dog": "serving a warm fluffy doggo straight from the café counter ☕🐶",
        },
        "de": {
            "fetch_fail": "aww ich konnte gerade kein süßes tierchen holen 😭☕",
            "sending_random": "okay liebchen, hier ist ein gemütliches kleines {animal} für dich ☕✨",
            "sending_cat": "brühe dir ein kleines kätzchen auf ☕🐱",
            "sending_dog": "serviere dir einen warmen flauschigen hund aus dem café ☕🐶",
        },
        "es": {
            "fetch_fail": "ay no pude traer un animalito ahora 😭☕",
            "sending_random": "okey amix, aquí tienes un {animal} acogedor ☕✨",
            "sending_cat": "te preparo un gatito bien suave ☕🐱",
            "sending_dog": "te sirvo un perrito calentito recién salido del café ☕🐶",
        },
    },

    # future personalities can be added here
}

# -----------------------------
# LANGUAGE + PERSONALITY HELPERS
# -----------------------------
def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(ctx.guild.preferred_locale).lower().startswith("es"):
            return "es"
    return "en"


def msg(ctx, key, **kwargs):
    personality = get_personality(ctx)
    lang = get_lang(ctx)

    # try personality + lang
    block = MESSAGES.get(personality, {}).get(lang, {})
    text = block.get(key)

    # fallback personality + en
    if text is None:
        text = MESSAGES.get(personality, {}).get("en", {}).get(key)

    # fallback normal + lang
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)

    # fallback normal + en
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)

    return text.format(**kwargs) if kwargs else text


# -----------------------------
# CUTE ANIMALS COG
# -----------------------------
class CuteAnimals(commands.Cog):
    """Cute animal image commands with cozy café personality + bilingual support."""

    def __init__(self, bot):
        self.bot = bot

        # All free, keyless APIs that return animal images
        self.animal_apis = {
            "cat": ("https://api.thecatapi.com/v1/images/search", "cat"),
            "dog": ("https://dog.ceo/api/breeds/image/random", "dog"),
            "fox": ("https://randomfox.ca/floof/", "fox"),
            "duck": ("https://random-d.uk/api/random", "duck"),
            "panda": ("https://some-random-api.com/animal/panda", "some-random"),
            "redpanda": ("https://some-random-api.com/animal/red_panda", "some-random"),
            "koala": ("https://some-random-api.com/animal/koala", "some-random"),
            "bird": ("https://some-random-api.com/animal/bird", "some-random"),
            "raccoon": ("https://some-random-api.com/animal/raccoon", "some-random"),
            "kangaroo": ("https://some-random-api.com/animal/kangaroo", "some-random"),
            "whale": ("https://some-random-api.com/animal/whale", "some-random"),
            "elephant": ("https://some-random-api.com/animal/elephant", "some-random"),
            "giraffe": ("https://some-random-api.com/animal/giraffe", "some-random"),
            "otter": ("https://some-random-api.com/animal/otter", "some-random"),
            "capybara": ("https://api.capy.lol/v1/capybara?json=true", "capy"),
        }

    def extract_url(self, animal_type, data):
        """Normalize different API response formats."""
        if animal_type == "cat":
            return data[0]["url"]
        if animal_type == "dog":
            return data["message"]
        if animal_type == "fox":
            return data["image"]
        if animal_type == "duck":
            return data["url"]
        if animal_type == "capy":
            return data["data"]["url"]
        if animal_type == "some-random":
            return data["image"]
        return None

    # -----------------------------
    # RANDOM ANIMAL COMMAND
    # -----------------------------
    @commands.command(
        name="cuteanimal",
        help="{ 'en': 'get a cozy random animal pic ☕✨', 'de': 'zeigt ein zufälliges süßes tier' }"
    )
    async def cuteanimal(self, ctx):
        """Sends a random cute animal image."""
        animal, (url, api_type) = random.choice(list(self.animal_apis.items()))
        response = await asyncio.to_thread(requests.get, url, timeout=10)
        data = response.json()

        img_url = self.extract_url(api_type, data)
        if img_url:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(ctx, "sending_random", animal=animal)
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(
                        media=img_url
                    )
                )
            )
            view.add_item(container)
            await ctx.send(view=view)
        else:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(ctx, "fetch_fail")
                )
            )
            await ctx.send(view=view)

    # -----------------------------
    # CAT COMMAND
    # -----------------------------
    @commands.command(
        name="cat",
        help="{ 'en': 'get a cozy lil kitty ☕🐱', 'de': 'zeigt ein süßes kätzchen' }"
    )
    async def cat(self, ctx):
        """Sends a random cat image."""
        response = await asyncio.to_thread(
            requests.get, "https://api.thecatapi.com/v1/images/search", timeout=10
        )
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(ctx, "sending_cat")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=response.json()[0]["url"]
                )
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    # -----------------------------
    # DOG COMMAND
    # -----------------------------
    @commands.command(
        name="dog",
        help="{ 'en': 'get a warm fluffy doggo ☕🐶', 'de': 'zeigt einen süßen hund' }"
    )
    async def dog(self, ctx):
        """Sends a random dog image."""
        response = await asyncio.to_thread(
            requests.get, "https://dog.ceo/api/breeds/image/random", timeout=10
        )
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=msg(ctx, "sending_dog")
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=response.json()["message"]
                )
            )
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(CuteAnimals(bot))