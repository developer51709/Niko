from discord.ext import commands
import re
import random
import requests

class IPPullerDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Keywords commonly found in IP puller services
        self.suspicious_keywords = [
            "grabify",
            "iplogger",
            "ip logger",
            "tracking link",
            "trackip",
            "webresolver",
            "logger",
            "ip-grabber",
            "ip grabber",
        ]

        # Regex to detect URLs
        self.url_pattern = re.compile(
            r"https?://[^\s]+",
            re.IGNORECASE
        )

        self.sarcasm = [
            "Ah yes, the ol’ ‘totally safe’ mystery link.",
            "That link has the same energy as a popup saying ‘You won an iPhone’.",
            "Wow, a link I definitely won’t click.",
            "Nice try, Agent 47.",
            "This link smells like Windows XP crying.",
            "Let me guess… free V‑Bucks too?",
            "Cute link. Shame nobody’s clicking it.",
            "That URL screams ‘trust me bro’.",
        ]

    def scan_metadata(self, url: str) -> bool:
        try:
            # Try HEAD first (faster)
            head = requests.head(url, timeout=3, allow_redirects=True)
            content_type = head.headers.get("Content-Type", "")

            # If it's HTML, fetch the body
            if "text/html" in content_type.lower():
                page = requests.get(url, timeout=5)
                html = page.text.lower()

                # Look for suspicious keywords
                for keyword in self.suspicious_keywords:
                    if keyword in html:
                        return True

        except Exception:
            # If the site blocks HEAD/GET or errors out, treat as suspicious
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
            if self.scan_metadata(url):
                await message.reply(random.choice(self.sarcasm))
                break

async def setup(bot):
    await bot.add_cog(IPPullerDetector(bot))