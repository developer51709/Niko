import discord
from discord.ext import commands


class Moderation(commands.Cog):
    """Staff-facing moderation commands."""

    def __init__(self, bot):
        self.bot = bot

    def utils(self):
        return self.bot.get_cog("ModerationUtils")

    # ---------- BASIC MOD COMMANDS ----------

    @commands.command(help="Kick a member from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if not member:
            await ctx.send("Please specify a member to kick.")
            return
        await member.kick(reason=reason)
        await ctx.send(f"✅ Kicked {member} | Reason: {reason}")
        await self.utils().log_action(ctx.guild, "Kick", f"{member} was kicked by {ctx.author}.\nReason: {reason}")

    @commands.command(help="Ban a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if not member:
            await ctx.send("Please specify a member to ban.")
            return
        await member.ban(reason=reason)
        await ctx.send(f"✅ Banned {member} | Reason: {reason}")
        await self.utils().log_action(ctx.guild, "Ban", f"{member} was banned by {ctx.author}.\nReason: {reason}")

    @commands.command(help="Unban a user by ID.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int = None):
        if not user_id:
            await ctx.send("Please provide a user ID to unban.")
            return
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ Unbanned {user}")
        await self.utils().log_action(ctx.guild, "Unban", f"{user} was unbanned by {ctx.author}.")

    # ---------- WARN SYSTEM ----------

    @commands.command(help="Warn a member.")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            await ctx.send("Please specify a member to warn.")
            return
        utils.add_warn(ctx.guild.id, member.id, ctx.author.id, reason)
        await ctx.send(f"⚠️ Warned {member} | Reason: {reason}")
        await utils.log_action(ctx.guild, "Warn", f"{member} was warned by {ctx.author}.\nReason: {reason}")

    @commands.command(help="View a member's warnings.")
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            await ctx.send("Please specify a member to view warnings for.")
            return
        warns = utils.get_warnings(ctx.guild.id, member.id)
        if not warns:
            return await ctx.send(f"{member} has no warnings.")
        embed = discord.Embed(title=f"Warnings for {member}", color=discord.Color.orange())
        for i, w in enumerate(warns, start=1):
            mod = ctx.guild.get_member(w["mod"])
            embed.add_field(
                name=f"#{i} by {mod or w['mod']}",
                value=f"Reason: {w['reason']}\nTime: {w['time']}",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(help="Clear all warnings for a member.")
    @commands.has_permissions(moderate_members=True)
    async def clearwarnings(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            await ctx.send("Please specify a member to clear warnings for.")
            return
        utils.clear_warnings(ctx.guild.id, member.id)
        await ctx.send(f"✅ Cleared warnings for {member}")
        await utils.log_action(ctx.guild, "Clear Warnings", f"{ctx.author} cleared warnings for {member}.")

    # ---------- MUTE / UNMUTE / TEMPMUTE ----------

    @commands.command(help="Mute a member.")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            await ctx.send("Please specify a member to mute.")
            return
        await utils.mute_member(member, duration=None, reason=reason)
        await ctx.send(f"🔇 Muted {member} | Reason: {reason}")
        await utils.log_action(ctx.guild, "Mute", f"{member} was muted by {ctx.author}.\nReason: {reason}")

    @commands.command(help="Temporarily mute a member. Duration in seconds.")
    @commands.has_permissions(moderate_members=True)
    async def tempmute(self, ctx, member: discord.Member = None, duration: int = None, *, reason: str = "No reason provided"):
        utils = self.utils()
        if not member:
            await ctx.send("Please specify a member to tempmute.")
            return
        if not duration:
            await ctx.send("Please specify a duration in seconds.")
            return
        await utils.mute_member(member, duration=duration, reason=reason)
        await ctx.send(f"⏳ Muted {member} for {duration}s | Reason: {reason}")
        await utils.log_action(ctx.guild, "Tempmute", f"{member} was tempmuted by {ctx.author} for {duration}s.\nReason: {reason}")

    @commands.command(help="Unmute a member.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member = None):
        utils = self.utils()
        if not member:
            await ctx.send("Please specify a member to unmute.")
            return
        await utils.unmute_member(member, reason=f"Unmuted by {ctx.author}")
        await ctx.send(f"🔊 Unmuted {member}")
        await utils.log_action(ctx.guild, "Unmute", f"{member} was unmuted by {ctx.author}.")

    # ---------- CLEAR / PURGE ----------

    @commands.command(help="Clear a number of messages.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = None):
        if not amount:
            await ctx.send("Please specify an amount of messages to delete.")
            return
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"🧹 Deleted {len(deleted)} messages.", delete_after=5)

    @commands.command(help="Purge messages from a specific user.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, member: discord.Member = None, amount: int = 100):
        if not member:
            await ctx.send("Please specify a member to purge messages from.")
            return
        def check(m):
            return m.author.id == member.id
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(f"🧹 Deleted {len(deleted)} messages from {member}.", delete_after=5)

    # ---------- SLOWMODE / LOCK / UNLOCK ----------

    @commands.command(help="Set slowmode in this channel (seconds).")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"🐢 Slowmode set to {seconds} seconds.")

    @commands.command(help="Lock this channel.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔒 Channel locked.")

    @commands.command(help="Unlock this channel.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔓 Channel unlocked.")

    # ---------- NICKNAME ----------

    @commands.command(help="Change a member's nickname.")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member = None, *, nickname: str = None):
        if not member:
            await ctx.send("Please specify a member to change the nickname for.")
            return
        if not nickname:
            await ctx.send("Please specify a new nickname.")
            return
        await member.edit(nick=nickname)
        await ctx.send(f"✏️ Changed nickname for {member} to `{nickname}`")

    # ---------- MODLOG CONFIG ----------

    @commands.command(help="Set the mod-log channel.")
    @commands.has_permissions(manage_guild=True)
    async def setmodlog(self, ctx, channel: discord.TextChannel | None):
        utils = self.utils()
        cid = channel.id if channel else None
        utils.set_modlog_channel(ctx.guild.id, cid)
        if channel:
            await ctx.send(f"✅ Mod-log channel set to {channel.mention}")
        else:
            await ctx.send("✅ Mod-log channel cleared.")

    # ---------- BLOCKED WORD LIST COMMANDS ----------

    @commands.group(name="badwords", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def badwords(self, ctx):
        """Show the blocked word list."""
        utils = self.utils()
        words = utils.get_blocked_words(ctx.guild.id)

        if not words:
            return await ctx.send("No blocked words set for this server.")

        embed = discord.Embed(
            title="🚫 Blocked Words",
            description="\n".join(f"- {w}" for w in words),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @badwords.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def badwords_add(self, ctx, *, word: str = None):
        utils = self.utils()
        if not word:
            await ctx.send("Please specify a word to add to the blocked list.")
            return
        utils.add_blocked_word(ctx.guild.id, word)
        await ctx.send(f"Added `{word}` to the blocked words list.")

    @badwords.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def badwords_remove(self, ctx, *, word: str = None):
        utils = self.utils()
        if not word:
            await ctx.send("Please specify a word to remove from the blocked list.")
            return
        utils.remove_blocked_word(ctx.guild.id, word)
        await ctx.send(f"Removed `{word}` from the blocked words list.")

    @badwords.command(name="clear")
    @commands.has_permissions(manage_guild=True)
    async def badwords_clear(self, ctx):
        utils = self.utils()
        utils.clear_blocked_words(ctx.guild.id)
        await ctx.send("Cleared all blocked words for this server.")


async def setup(bot):
    await bot.add_cog(Moderation(bot))