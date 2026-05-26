from .formatters import *

class ServerLogger(commands.Cog):
    """Multi-channel server event logging."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._config: dict = _load_log_config()
        # guild_id → {invite_code: uses_count}
        self._invite_cache: dict[int, dict[str, int]] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """Populate invite cache for all guilds on startup."""
        for guild in self.bot.guilds:
            try:
                invites = await guild.invites()
                self._invite_cache[guild.id] = {inv.code: inv.uses for inv in invites}
            except (discord.Forbidden, discord.HTTPException):
                pass

    def _get_cfg(self, guild_id: int) -> dict:
        return _guild_config(self._config, guild_id)

    def _reload(self):
        self._config = _load_log_config()

    # ── Core logging method ───────────────────────

    async def log_event(
        self,
        guild: discord.Guild,
        category: str,
        title: str,
        body: str,
        target_id: int | None = None,
        action_key: str | None = None,
        channel_id: int | None = None,
    ):
        """Send a structured log entry to the configured channel for the given category."""
        self._reload()
        cfg = self._get_cfg(guild.id)

        if category in cfg.get("disabled", []):
            return

        log_channel_id = cfg.get(category)
        if not log_channel_id:
            return

        channel = guild.get_channel(log_channel_id)
        if not channel:
            return

        view = _build_log_view(
            category=category,
            title=title,
            body=body,
            guild_id=guild.id,
            target_id=target_id,
            action_key=action_key or title,
            channel_id=channel_id,
        )
        try:
            # Stay under Discord's per-channel send budget so a burst of
            # events (e.g. mass-ban) can't get the channel rate-limited.
            await log_channel_limiter.acquire((guild.id, channel.id))
            await channel.send(view=view, allowed_mentions=discord.AllowedMentions.none())
        except Exception as e:
            logging.error("logging_cog", f"Failed to send log message to {channel} in {guild}: {e}")
            pass

    #Backward-compat wrapper used by moderation_utils

    async def log_action(
        self,
        guild: discord.Guild,
        title: str,
        description: str,
        target: discord.Member | discord.User | None = None,
        moderator: discord.Member | None = None,
    ):
        """Drop-in replacement for the old ModerationUtils.log_action."""
        # Determine category from title
        category = _TITLE_CATEGORY.get(title)
        if not category:
            if any(s in title for s in _AUTOMOD_SUBSTRINGS):
                category = "automod"
            else:
                category = "moderation"

        body = description
        if moderator and f"{moderator}" not in description:
            body += f"\n**Moderator:** {moderator.mention}"

        target_id = target.id if target else None
        await self.log_event(guild, category, title, body, target_id=target_id, action_key=title)

    # ── Gateway event listeners ───────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        created = member.created_at.strftime("%Y-%m-%d")
        account_age = (datetime.now(timezone.utc) - member.created_at).days
        age_warn = f"\n-# {get_emoji('icon_danger')} New account — only **{account_age}d** old" if account_age < 7 else ""

        # ── Detect which invite was used ──────────
        used_invite = None
        try:
            current_invites = await guild.invites()
            cached = self._invite_cache.get(guild.id, {})
            for inv in current_invites:
                if inv.uses > cached.get(inv.code, 0):
                    used_invite = inv
                    break
            self._invite_cache[guild.id] = {inv.code: inv.uses for inv in current_invites}
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Log invite usage to the invites category
        if used_invite:
            inv_body = (
                f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Invite Code:** `{used_invite.code}`\n"
                f"**Created By:** {used_invite.inviter.mention if used_invite.inviter else 'Unknown'}\n"
                f"**Total Uses:** {used_invite.uses}"
            )
            await self.log_event(
                guild, "invites", "Invite Used", inv_body,
                target_id=member.id
            )

        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Account Created:** {created} ({account_age} days ago){age_warn}"
        )
        await self.log_event(
            guild, "members", "Member Joined", body,
            target_id=member.id, action_key="member_join"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild

        # ── Check audit log for an external kick ──
        kick_entry = None
        try:
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
                if entry.target.id == member.id:
                    kick_entry = entry
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        if kick_entry and kick_entry.user != self.bot.user:
            kick_body = (
                f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Action:** Kick\n"
                f"**Reason:** {kick_entry.reason or 'No reason provided'}\n"
                f"**Moderator:** {kick_entry.user.mention if kick_entry.user else 'Unknown'}"
            )
            await self.log_event(
                guild, "moderation", "Kick", kick_body,
                target_id=member.id, action_key="Kick"
            )

        roles = [r.mention for r in member.roles if r != guild.default_role]
        roles_text = ", ".join(roles) if roles else "None"
        body = (
            f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
            f"**Roles:** {roles_text}"
        )
        await self.log_event(guild, "members", "Member Left", body)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild = after.guild
        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added = after_roles - before_roles
        removed = before_roles - after_roles

        changes = []
        if added:
            changes.append(f"**Roles Added:** {', '.join(r.mention for r in added)}")
        if removed:
            changes.append(f"**Roles Removed:** {', '.join(r.mention for r in removed)}")

        # ── Nick change — attribute to moderator via audit log ──
        if before.nick != after.nick:
            nick_moderator = None
            try:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id:
                        nick_moderator = entry.user
                        break
            except (discord.Forbidden, discord.HTTPException):
                pass

            if nick_moderator and nick_moderator != self.bot.user:
                nick_body = (
                    f"**Member:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                    f"**Old Nickname:** `{before.nick or before.name}`\n"
                    f"**New Nickname:** `{after.nick or after.name}`\n"
                    f"**Changed By:** {nick_moderator.mention}"
                )
                await self.log_event(
                    guild, "moderation", "Nickname Changed", nick_body,
                    target_id=after.id
                )

            changes.append(f"**Nickname:** `{before.nick or before.name}` → `{after.nick or after.name}`")

        # ── Discord native timeout detection ──────
        before_timeout = getattr(before, "timed_out_until", None)
        after_timeout = getattr(after, "timed_out_until", None)
        if before_timeout != after_timeout:
            timeout_mod = None
            try:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id:
                        timeout_mod = entry.user
                        break
            except (discord.Forbidden, discord.HTTPException):
                pass

            if timeout_mod and timeout_mod != self.bot.user:
                if after_timeout:
                    timeout_body = (
                        f"**User:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                        f"**Action:** Timeout applied\n"
                        f"**Until:** <t:{int(after_timeout.timestamp())}:F> (<t:{int(after_timeout.timestamp())}:R>)\n"
                        f"**Moderator:** {timeout_mod.mention}"
                    )
                    await self.log_event(
                        guild, "moderation", "Timeout", timeout_body,
                        target_id=after.id, action_key="Timeout"
                    )
                else:
                    timeout_body = (
                        f"**User:** {after.mention} (`{after}` — ID: `{after.id}`)\n"
                        f"**Action:** Timeout removed\n"
                        f"**Moderator:** {timeout_mod.mention}"
                    )
                    await self.log_event(
                        guild, "moderation", "Timeout Removed", timeout_body,
                        target_id=after.id
                    )

        if not changes:
            return

        body = f"**Member:** {after.mention} (`{after}`)\n" + "\n".join(changes)
        await self.log_event(guild, "members", "Member Updated", body, target_id=after.id)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        content = message.content or "*No text content*"
        if len(content) > 900:
            content = content[:900] + "…"

        attachment_note = ""
        if message.attachments:
            names = ", ".join(f"`{a.filename}`" for a in message.attachments)
            attachment_note = f"\n**Attachments ({len(message.attachments)}):** {names}"

        body = (
            f"**Author:** {message.author.mention} (`{message.author}`)\n"
            f"**Channel:** {message.channel.mention}\n"
            f"**Content:**\n{content}"
            f"{attachment_note}"
        )
        await self.log_event(message.guild, "messages", "Message Deleted", body, target_id=message.author.id)

        # Re-upload any cached attachment bytes to the log channel
        if message.attachments:
            self._reload()
            cfg = self._get_cfg(message.guild.id)
            if "messages" not in cfg.get("disabled", []):
                log_channel_id = cfg.get("messages")
                log_channel = message.guild.get_channel(log_channel_id) if log_channel_id else None
                if log_channel:
                    import aiohttp
                    import io
                    files = []
                    async with aiohttp.ClientSession() as session:
                        for att in message.attachments:
                            try:
                                async with session.get(att.proxy_url) as resp:
                                    if resp.status == 200:
                                        data = await resp.read()
                                        files.append(discord.File(io.BytesIO(data), filename=att.filename))
                            except Exception:
                                pass
                    if files:
                        try:
                            await log_channel_limiter.acquire((message.guild.id, log_channel.id))
                            await log_channel.send(
                                content=f"-# Attachments from deleted message by {message.author.mention}:",
                                files=files,
                                allowed_mentions=discord.AllowedMentions.none(),
                            )
                        except Exception as e:
                            logging.error("logging_cog", f"Failed to re-upload deleted attachments: {e}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not after.guild or after.author.bot:
            return
        if before.content == after.content:
            return
        before_content = before.content or "*empty*"
        after_content = after.content or "*empty*"
        if len(before_content) > 450:
            before_content = before_content[:450] + "…"
        if len(after_content) > 450:
            after_content = after_content[:450] + "…"
        body = (
            f"**Author:** {after.author.mention} (`{after.author}`)\n"
            f"**Channel:** {after.channel.mention}\n"
            f"**Before:**\n{before_content}\n"
            f"**After:**\n{after_content}\n"
            f"-# [Jump to message]({after.jump_url})"
        )
        await self.log_event(after.guild, "messages", "Message Edited", body, target_id=after.author.id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Cache invites when the bot joins a new guild."""
        try:
            invites = await guild.invites()
            self._invite_cache[guild.id] = {inv.code: inv.uses for inv in invites}
        except (discord.Forbidden, discord.HTTPException):
            pass

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        guild = invite.guild
        if not guild:
            return
        # Update cache
        cached = self._invite_cache.setdefault(guild.id, {})
        cached[invite.code] = invite.uses

        expires_text = (
            f"<t:{int(invite.expires_at.timestamp())}:R>" if invite.expires_at else "Never"
        )
        max_uses_text = str(invite.max_uses) if invite.max_uses else "Unlimited"
        body = (
            f"**Invite Code:** `{invite.code}`\n"
            f"**Created By:** {invite.inviter.mention if invite.inviter else 'Unknown'}\n"
            f"**Channel:** {invite.channel.mention if invite.channel else 'Unknown'}\n"
            f"**Max Uses:** {max_uses_text}\n"
            f"**Expires:** {expires_text}"
        )
        await self.log_event(guild, "invites", "Invite Created", body)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        guild = invite.guild
        if not guild:
            return
        # Remove from cache
        cached = self._invite_cache.get(guild.id, {})
        cached.pop(invite.code, None)

        body = (
            f"**Invite Code:** `{invite.code}`\n"
            f"**Channel:** {invite.channel.mention if invite.channel else 'Unknown'}"
        )
        await self.log_event(guild, "invites", "Invite Deleted", body)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        responsible = None
        try:
            async for entry in channel.guild.audit_logs(limit=3, action=discord.AuditLogAction.channel_create):
                if entry.target.id == channel.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Channel:** {channel.mention} (`{channel.name}`)\n"
            f"**Type:** {str(channel.type).replace('_', ' ').title()}\n"
            f"**Created By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(channel.guild, "channels", "Channel Created", body)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        responsible = None
        try:
            async for entry in channel.guild.audit_logs(limit=3, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Channel:** `#{channel.name}`\n"
            f"**Type:** {str(channel.type).replace('_', ' ').title()}\n"
            f"**Deleted By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(channel.guild, "channels", "Channel Deleted", body)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        changes = []

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")

        if isinstance(after, discord.TextChannel) or isinstance(after, discord.ForumChannel):
            if getattr(before, "topic", None) != getattr(after, "topic", None):
                b_topic = getattr(before, "topic", None) or "*None*"
                a_topic = getattr(after, "topic", None) or "*None*"
                changes.append(f"**Topic:** {b_topic} → {a_topic}")
            if getattr(before, "slowmode_delay", 0) != getattr(after, "slowmode_delay", 0):
                changes.append(f"**Slowmode:** `{getattr(before, 'slowmode_delay', 0)}s` → `{getattr(after, 'slowmode_delay', 0)}s`")
            if getattr(before, "nsfw", False) != getattr(after, "nsfw", False):
                changes.append(f"**NSFW:** `{getattr(before, 'nsfw', False)}` → `{getattr(after, 'nsfw', False)}`")

        if isinstance(after, discord.VoiceChannel):
            if getattr(before, "bitrate", None) != getattr(after, "bitrate", None):
                changes.append(f"**Bitrate:** `{getattr(before, 'bitrate', 0) // 1000}kbps` → `{getattr(after, 'bitrate', 0) // 1000}kbps`")
            if getattr(before, "user_limit", 0) != getattr(after, "user_limit", 0):
                b_lim = getattr(before, "user_limit", 0) or "Unlimited"
                a_lim = getattr(after, "user_limit", 0) or "Unlimited"
                changes.append(f"**User Limit:** `{b_lim}` → `{a_lim}`")

        if not changes:
            return

        responsible = None
        try:
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_update):
                if entry.target.id == after.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Channel:** {after.mention} (`{after.name}`)\n"
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after.guild, "channels", "Channel Updated", body)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        responsible = None
        try:
            async for entry in role.guild.audit_logs(limit=3, action=discord.AuditLogAction.role_create):
                if entry.target.id == role.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        color_text = str(role.color) if role.color.value else "Default"
        body = (
            f"**Role:** {role.mention} (`{role.name}`)\n"
            f"**Color:** `{color_text}`\n"
            f"**Hoisted:** `{role.hoist}` | **Mentionable:** `{role.mentionable}`\n"
            f"**Created By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(role.guild, "roles", "Role Created", body)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        responsible = None
        try:
            async for entry in role.guild.audit_logs(limit=3, action=discord.AuditLogAction.role_delete):
                if entry.target.id == role.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Role:** `{role.name}` (ID: `{role.id}`)\n"
            f"**Deleted By:** {responsible.mention if responsible else 'Unknown'}"
        )
        await self.log_event(role.guild, "roles", "Role Deleted", body)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        changes = []

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")
        if before.color != after.color:
            changes.append(f"**Color:** `{before.color}` → `{after.color}`")
        if before.hoist != after.hoist:
            changes.append(f"**Hoisted:** `{before.hoist}` → `{after.hoist}`")
        if before.mentionable != after.mentionable:
            changes.append(f"**Mentionable:** `{before.mentionable}` → `{after.mentionable}`")
        if before.permissions != after.permissions:
            perm_changes = []
            for perm, value in iter(after.permissions):
                if getattr(before.permissions, perm) != value:
                    symbol = get_emoji('icon_tick') if value else get_emoji('icon_cross')
                    perm_changes.append(f"{symbol} `{perm.replace('_', ' ').title()}`")
            if perm_changes:
                changes.append("**Permissions Changed:**\n" + " ".join(perm_changes))

        if not changes:
            return

        responsible = None
        try:
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_update):
                if entry.target.id == after.id:
                    responsible = entry.user
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Role:** {after.mention} (`{after.name}`)\n"
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after.guild, "roles", "Role Updated", body)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        changes = []

        if before.name != after.name:
            changes.append(f"**Name:** `{before.name}` → `{after.name}`")
        if before.description != after.description:
            b_desc = before.description or "*None*"
            a_desc = after.description or "*None*"
            changes.append(f"**Description:** {b_desc} → {a_desc}")
        if before.verification_level != after.verification_level:
            changes.append(f"**Verification Level:** `{before.verification_level}` → `{after.verification_level}`")
        if before.explicit_content_filter != after.explicit_content_filter:
            changes.append(f"**Explicit Content Filter:** `{before.explicit_content_filter}` → `{after.explicit_content_filter}`")
        if before.default_notifications != after.default_notifications:
            changes.append(f"**Default Notifications:** `{before.default_notifications}` → `{after.default_notifications}`")
        if before.afk_channel != after.afk_channel:
            b_afk = before.afk_channel.name if before.afk_channel else "None"
            a_afk = after.afk_channel.name if after.afk_channel else "None"
            changes.append(f"**AFK Channel:** `{b_afk}` → `{a_afk}`")
        if before.icon != after.icon:
            changes.append("**Server Icon:** changed")
        if before.banner != after.banner:
            changes.append("**Server Banner:** changed")

        if not changes:
            return

        responsible = None
        try:
            async for entry in after.audit_logs(limit=5, action=discord.AuditLogAction.guild_update):
                responsible = entry.user
                break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(changes)
        )
        await self.log_event(after, "server", "Server Updated", body)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: discord.Guild, before: list, after: list):
        before_ids = {e.id for e in before}
        after_ids = {e.id for e in after}

        added = [e for e in after if e.id not in before_ids]
        removed = [e for e in before if e.id not in after_ids]

        if not added and not removed:
            return

        lines = []
        if added:
            lines.append("**Added:** " + ", ".join(f"`:{e.name}:`" for e in added))
        if removed:
            lines.append("**Removed:** " + ", ".join(f"`:{e.name}:`" for e in removed))

        responsible = None
        try:
            action = discord.AuditLogAction.emoji_create if added else discord.AuditLogAction.emoji_delete
            async for entry in guild.audit_logs(limit=3, action=action):
                responsible = entry.user
                break
        except (discord.Forbidden, discord.HTTPException):
            pass

        body = (
            f"**Updated By:** {responsible.mention if responsible else 'Unknown'}\n"
            + "\n".join(lines)
        )
        await self.log_event(guild, "server", "Emoji Updated", body)

    @commands.Cog.listener()
    async def on_guild_stickers_update(self, guild: discord.Guild, before: list, after: list):
        before_ids = {s.id for s in before}
        after_ids = {s.id for s in after}

        added = [s for s in after if s.id not in before_ids]
        removed = [s for s in before if s.id not in after_ids]

        if not added and not removed:
            return

        lines = []
        if added:
            lines.append("**Added:** " + ", ".join(f"`{s.name}`" for s in added))
        if removed:
            lines.append("**Removed:** " + ", ".join(f"`{s.name}`" for s in removed))

        body = "\n".join(lines)
        await self.log_event(guild, "server", "Sticker Updated", body)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        if before.channel is None and after.channel is not None:
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Joined:** {after.channel.mention}"
            )
            await self.log_event(guild, "voice", "Voice Join", body, target_id=member.id)

        elif before.channel is not None and after.channel is None:
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**Left:** {before.channel.mention}"
            )
            await self.log_event(guild, "voice", "Voice Leave", body, target_id=member.id)

        elif (
            before.channel is not None
            and after.channel is not None
            and before.channel.id != after.channel.id
        ):
            body = (
                f"**Member:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                f"**From:** {before.channel.mention}\n"
                f"**To:** {after.channel.mention}"
            )
            await self.log_event(guild, "voice", "Voice Move", body, target_id=member.id)

    @commands.Cog.listener()
    # update: discord.py does not support the moderator parameter so we must use the audit log to get the moderator.
    async def on_member_ban(self, guild: discord.Guild, user: discord.User, reason: str | None = None):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            moderator = entry.user
        if moderator == self.bot.user:
            return
        body = (
            f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n"
            f"**Action:** Ban\n"
            f"**Reason:** {reason or 'No reason provided'}\n"
            f"**Moderator:** {moderator.mention if moderator else 'Unknown'}"
        )
        await self.log_event(
            guild, "moderation", "Ban", body, 
            target_id=user.id, action_key="Ban"
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User, reason: str | None = None):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            moderator = entry.user
        if moderator == self.bot.user:
            return
        body = (
            f"**User:** {user.mention} (`{user}` — ID: `{user.id}`)\n"
            f"**Action:** Unban\n"
            f"**Reason:** {reason or 'No reason provided'}\n"
            f"**Moderator:** {moderator.mention if moderator else 'Unknown'}"
        )
        await self.log_event(
            guild, "moderation", "Unban", body,
            target_id=user.id, action_key="Unban"
        )

    # ── Commands ──────────────────────────────────

    @commands.group(name="logging", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def logging_cmd(self, ctx: commands.Context):
        """Open the server logging configuration panel."""
        await ctx.send(view=LoggingSetupView(ctx.guild.id, ctx.author))

    @logging_cmd.command(name="status")
    @commands.has_permissions(manage_guild=True)
    async def logging_status(self, ctx: commands.Context):
        """Show the current logging configuration."""
        self._reload()
        cfg = self._get_cfg(ctx.guild.id)
        icon = get_emoji("icon_settings")

        lines = []
        for key, info in CATEGORIES.items():
            ch_id = cfg.get(key)
            ch_text = f"<#{ch_id}>" if ch_id else "`Not set`"
            disabled = key in cfg.get("disabled", [])
            status = get_emoji("disabled") if disabled else get_emoji("enabled")
            lines.append(f"{status} **{info['label']}** — {ch_text}")

        body = "\n".join(lines)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {icon} Logging Status"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=body),
            accent_colour=discord.Colour(0x5865F2),
        ))
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLogger(bot))
