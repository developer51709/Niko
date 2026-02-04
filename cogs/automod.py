import discord
from discord.ext import commands
import time
import re

INVITE_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.IGNORECASE)


class AutoMod(commands.Cog):
    """Automatic moderation: spam, links, badwords, mass mention."""

    def __init__(self, bot):
        self.bot = bot
        self.message_history = {}  # guild_id -> user_id -> [timestamps]

    def utils(self):
        return self.bot.get_cog("ModerationUtils")

    def get_cfg(self, guild_id: int):
        return self.utils().get_guild_config(guild_id)

    def track_message(self, message: discord.Message):
        gid = message.guild.id
        uid = message.author.id
        now = time.time()
        self.message_history.setdefault(gid, {}).setdefault(uid, [])
        self.message_history[gid][uid].append(now)

        cfg = self.get_cfg(gid)
        interval = cfg["spam_interval"]
        cutoff = now - interval
        self.message_history[gid][uid] = [t for t in self.message_history[gid][uid] if t >= cutoff]
        return len(self.message_history[gid][uid])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        utils = self.utils()
        cfg = self.get_cfg(message.guild.id)
        content = message.content or ""

        # Anti-spam
        if cfg["automod"].get("antispam", True):
            count = self.track_message(message)
            if count >= cfg["spam_threshold"]:
                await message.delete()
                await utils.log_action(
                    message.guild,
                    "Anti-Spam",
                    f"{message.author} triggered anti-spam in {message.channel.mention}."
                )
                await utils.mute_member(message.author, duration=60, reason="Auto-mute: spam")
                return

        # Anti-link (invites)
        if cfg["automod"].get("antilink", True):
            if INVITE_REGEX.search(content):
                await message.delete()
                await utils.log_action(
                    message.guild,
                    "Anti-Link",
                    f"{message.author} posted an invite link in {message.channel.mention}."
                )
                return

        # Badwords (per-server)
        if cfg["automod"].get("badwords", True):
            if utils.contains_blocked_word(message.guild.id, content):
                await message.delete()
                await utils.log_action(
                    message.guild,
                    "Bad Word Filter",
                    f"{message.author} used a blocked word in {message.channel.mention}."
                )
                return

        # Mass mention
        if cfg["automod"].get("massmention", True):
            mentions = len(message.mentions) + int(message.mention_everyone)
            if mentions >= cfg["max_mentions"]:
                await message.delete()
                await utils.log_action(
                    message.guild,
                    "Mass Mention",
                    f"{message.author} mass-mentioned ({mentions}) in {message.channel.mention}."
                )
                await utils.mute_member(message.author, duration=120, reason="Auto-mute: mass mention")
                return

    # ---------- AUTOMOD COMMANDS ----------

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def automod(self, ctx):
        """
        Show automod status.
        Usage:
        `automod [toggle|threshold|mentions]`
        Toggle: 
        `antispam, antilink, badwords, massmention`
        Threshold: 
        `messages per interval (seconds)`
        Mentions: 
        `max mentions before trigger`
        """
        cfg = self.get_cfg(ctx.guild.id)
        auto = cfg["automod"]
        desc = "\n".join(
            f"**{k}**: {'ON' if v else 'OFF'}"
            for k, v in auto.items()
        )
        # await ctx.send(f"🔧 Automod settings:\n{desc}")
        embed = discord.Embed(title="🔧 Automod Settings", description=desc, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @automod.command(name="toggle")
    @commands.has_permissions(manage_guild=True)
    async def automod_toggle(self, ctx, module: str):
        """Toggle an automod module: antispam, antilink, badwords, massmention"""
        cfg = self.get_cfg(ctx.guild.id)
        auto = cfg["automod"]
        module = module.lower()
        if module not in auto:
            return await ctx.send("Unknown module. Valid: antispam, antilink, badwords, massmention")
        auto[module] = not auto[module]
        self.utils().save_config()
        await ctx.send(f"✅ {module} is now {'ON' if auto[module] else 'OFF'}")

    @automod.command(name="threshold")
    @commands.has_permissions(manage_guild=True)
    async def automod_threshold(self, ctx, messages: int = None, interval: int = None):
        """Set spam threshold: messages per interval (seconds)."""
        if not messages or not interval:
            embed = discord.Embed(title="⚠️ Missing Arguments", description="Please provide both messages and interval.\nExample: `!automod threshold 5 10`\nThis would would set the limit to 5 messages per 10 seconds.", color=discord.Color.red())
            return await ctx.send(embed=embed)
        cfg = self.get_cfg(ctx.guild.id)
        cfg["spam_threshold"] = messages
        cfg["spam_interval"] = interval
        self.utils().save_config()
        await ctx.send(f"✅ Spam threshold set to {messages} messages / {interval}s")

    @automod.command(name="mentions")
    @commands.has_permissions(manage_guild=True)
    async def automod_mentions(self, ctx, max_mentions: int):
        """Set max mentions before mass-mention triggers."""
        cfg = self.get_cfg(ctx.guild.id)
        cfg["max_mentions"] = max_mentions
        self.utils().save_config()
        await ctx.send(f"✅ Max mentions set to {max_mentions}")


async def setup(bot):
    await bot.add_cog(AutoMod(bot))