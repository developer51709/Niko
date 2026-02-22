from discord.ext import commands
import requests
import random

class CuteAnimals(commands.Cog):
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

    @commands.command()
    async def cuteanimal(self, ctx):
        animal, (url, api_type) = random.choice(list(self.animal_apis.items()))
        response = requests.get(url)
        data = response.json()

        img_url = self.extract_url(api_type, data)
        if img_url:
            await ctx.send(img_url)
        else:
            await ctx.send("Couldn't fetch a cute animal right now.")

    @commands.command()
    async def cat(self, ctx):
        response = requests.get("https://api.thecatapi.com/v1/images/search")
        await ctx.send(response.json()[0]["url"])

    @commands.command()
    async def dog(self, ctx):
        response = requests.get("https://dog.ceo/api/breeds/image/random")
        await ctx.send(response.json()["message"])

async def setup(bot):
    await bot.add_cog(CuteAnimals(bot))