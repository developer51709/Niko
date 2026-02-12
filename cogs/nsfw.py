# nsfw.py
# uses the rule34 and gelbooru APIs to fetch images
# only works in NSFW channels

import discord
from discord.ext import commands
import requests
import random
import os

# get api keys and user ids from environment variables
RULE34_API_KEY = os.getenv('RULE34_API_KEY')
RULE34_USER_ID = os.getenv('RULE34_USER_ID')
GELBOORU_API_KEY = os.getenv('GELBOORU_API_KEY')
GELBOORU_USER_ID = os.getenv('GELBOORU_USER_ID')

class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='rule34', help='Search for images on rule34.xxx')
    @commands.is_nsfw()
    async def rule34(self, ctx, *, query: str = None):
        if not ctx.channel.is_nsfw():
            embed = discord.Embed(
                title='Rule34',
                description='This command can only be used in NSFW channels.',
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        if not query:
            embed = discord.Embed(
                title='Rule34', 
                description='Please provide a search query.', 
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        # make request to rule34 API with api key and user id
        RULE34_API_URL = f'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={query}&limit=100&pid=0&api_key={RULE34_API_KEY}&user_id={RULE34_USER_ID}'
        response = requests.get(RULE34_API_URL)
        # check if response is valid
        if response.status_code != 200:
            embed = discord.Embed(
                title='Rule34', 
                description='An error occurred while fetching images.', 
                color=discord.Color.red()
            )
            embed.set_footer(text=f'Response code: `{response.status_code}`')
            return await ctx.send(embed=embed)
        # parse response
        data = response.json()
        # check if any images were found
        if not data:
            embed = discord.Embed(
                title='Rule34',
                description='No images found for the given query.',
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        # select random image
        image = random.choice(data)
        # check if image is valid
        if not image.get('file_url'):
            embed = discord.Embed(
                title='Rule34',
                description='An error occurred while fetching the image.',
                color=discord.Color.red()
            )
            embed.set_footer(text='Invalid image URL')
            return await ctx.send(embed=embed)
        # send image in an embed with the query and image source
        embed = discord.Embed(
            title=f'Rule34 - {query}',
            description=f'[Image Source]({image["file_url"]})',
            color=discord.Color.blue()
        )
        embed.set_image(url=image['file_url'])
        embed.set_footer(text=f'Requested by {ctx.author.display_name}')
        await ctx.send(embed=embed)

    @commands.command(name='gelbooru', help='Search for images on gelbooru.com')
    @commands.is_nsfw()
    async def gelbooru(self, ctx, *, query: str = None):
        if not ctx.channel.is_nsfw():
            embed = discord.Embed(
                title='Gelbooru',
                description='This command can only be used in NSFW channels.',
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        if not query:
            embed = discord.Embed(
                title='Gelbooru',
                description='Please provide a search query.',
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        # make request to gelbooru API with api key and user id
        GELBOORU_API_URL = f'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={query}&limit=100&pid=0&api_key={GELBOORU_API_KEY}&user_id={GELBOORU_USER_ID}'
        response = requests.get(GELBOORU_API_URL)
        # check if response is valid
        if response.status_code != 200:
            embed = discord.Embed(
                title='Gelbooru', 
                description='An error occurred while fetching images.', 
                color=discord.Color.red()
            )
            embed.set_footer(text=f'Response code: `{response.status_code}`')
            return await ctx.send(embed=embed)
        # check if response is valid json
        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            embed = discord.Embed(
                title="Gelbooru",
                description="The API returned an unexpected response format.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        # parse response
        data = response.json()
        posts = data.get("post", [])

        if not posts:
            embed = discord.Embed(
                title='Gelbooru',
                description='No images found for the given query.',
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        image = random.choice(posts)
        # check if image is valid
        if not image.get('file_url'):
            embed = discord.Embed(
                title='Gelbooru',
                description='An error occurred while fetching the image.',
                color=discord.Color.red()
            )
            embed.set_footer(text='Invalid image URL')
            return await ctx.send(embed=embed)
        # send image in an embed with the query and image source
        embed = discord.Embed(
            title=f'Gelbooru - {query}',
            description=f'[Image Source]({image["file_url"]})',
            color=discord.Color.blue()
        )
        embed.set_image(url=image['file_url'])
        embed.set_footer(text=f'Requested by {ctx.author.display_name}')
        await ctx.send(embed=embed)


# setup
async def setup(bot):
    await bot.add_cog(NSFW(bot))