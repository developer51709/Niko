import re
import random
import aiohttp
from urllib.parse import urlparse
from discord.ext import commands

class IPPullerDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.suspicious_keywords = [
            "grabify",
            "iplogger",
            "ip logger",
            "tracking link",
            "trackip",
            "ip-grabber",
            "ip grabber",
        ]

        self.url_pattern = re.compile(r"https?://[^\s]+", re.IGNORECASE)

        self.sarcasm = [
            "omg bestie… that link is giving ‘trust me, I won’t steal your soul’ vibes and I’m not buying it lol (≧▽≦)",
            "wowww that link looks sooo legit… totally not suspicious at all… nope… not even a little bit ✨😌",
            "lmao you really dropped that like I wouldn’t notice the ✨chaos energy✨ radiating off it",
            "that link is serving ‘mysterious stranger in a dark alley’ realness and I’m kinda screaming rn",
            "okay but why does that URL look like it wants my social security number and a hug at the same time",
            "bestie… that link is blushing suspiciously… you good?? (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
            "oh wow, a totally normal, definitely safe, absolutely trustworthy link… sureeee babe 💅",
            "that link is giving ‘click me and regret it’ energy and I’m not emotionally prepared for that",
            "pls… that URL is literally wearing a fake mustache trying to blend in 😭",
            "I love how that link is pretending to be normal like we can’t all feel the chaos radiating off it lol",
            "bruhhh that link is radiating ✨mysterious hacker energy✨ and I’m low‑key scared but also impressed (≧◡≦)",
            "lol not you dropping a link that screams ‘I promise I won’t steal your soul’ 💀✨",
            "okay but why does that URL look like it wants my IP AND a hug at the same time 😭",
        ]

    async def scan_single_url(self, url: str) -> bool:
        """Scan a single URL by following redirects and checking final HTML."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, allow_redirects=True, timeout=7) as resp:
                    final_url = str(resp.url).lower()
                    html = (await resp.text()).lower()

                # Check final URL
                for keyword in self.suspicious_keywords:
                    if keyword in final_url:
                        return True

                # Check HTML content
                for keyword in self.suspicious_keywords:
                    if keyword in html:
                        return True

        except Exception:
            # If the site blocks scanning or errors out, treat as suspicious
            return True

        return False

    async def scan_url_and_root(self, url: str) -> bool:
        """Scan both the URL and its root domain."""
        # 1. Scan the original URL
        if await self.scan_single_url(url):
            return True

        # 2. Extract root domain
        parsed = urlparse(url)
        root_url = f"{parsed.scheme}://{parsed.netloc}/"

        # 3. Scan the root domain
        if await self.scan_single_url(root_url):
            return True

        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        urls = self.url_pattern.findall(message.content)
        if not urls:
            return

        for url in urls:
            if await self.scan_url_and_root(url):
                await message.reply(random.choice(self.sarcasm))
                break

async def setup(bot):
    await bot.add_cog(IPPullerDetector(bot))