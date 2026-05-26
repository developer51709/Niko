from .views import *

class AutoMod(commands.Cog):
    """Automatic moderation: spam, links, badwords, mass mention,
    anti-nuke, anti-raid, interaction-flood, and user-installed app abuse."""

    def __init__(self, bot):
        self.bot = bot
        self._msg_history = {}  # guild_id -> user_id -> [timestamps]
        self._nuke_history = {}  # guild_id -> user_id -> {action_key: [ts]}
        # Dedup guard: stores expiry timestamp per (guild_id, user_id).
        # While now < expiry the user is already actioned — all further audit
        # events from them are silently ignored so exactly one DM is sent.
        self._nuke_actioned: dict[int, dict[int, float]] = {}
        # Dedup for anti-raid: guild_id → expiry timestamp.  While active,
        # extra join events that re-hit the threshold are silently dropped so
        # only one enforcement wave runs per raid event.
        self._raid_actioned: dict[int, float] = {}
        self._join_history = {}  # guild_id -> [timestamps]
        self._interaction_history = {}  # guild_id -> [(user_id, timestamp)]
        self._ext_app_history = {}  # guild_id -> user_id -> [timestamps]
        self._invite_cache = {}  # guild_id -> {invite_code: uses}
        self._missing_perms_warned = set()  # guild_ids where we've already logged a missing-perm warning

    def utils(self):
        return self.bot.get_cog("ModerationUtils")

    def get_cfg(self, guild_id: int):
        return self.utils().get_guild_config(guild_id)

    # ─── INVITE CACHE ─────────────────────────────

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self._snapshot_invites(guild)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        if invite.guild:
            await self._snapshot_invites(invite.guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        if invite.guild:
            await self._snapshot_invites(invite.guild)

    async def _snapshot_invites(self, guild: discord.Guild):
        try:
            invites = await guild.invites()
            self._invite_cache[guild.id] = {inv.code: inv.uses for inv in invites}
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _identify_operator(self, guild: discord.Guild):
        cached = self._invite_cache.get(guild.id, {})
        try:
            current_invites = await guild.invites()
        except (discord.Forbidden, discord.HTTPException):
            return None
        best_invite = None
        best_delta = 0
        for inv in current_invites:
            delta = inv.uses - cached.get(inv.code, 0)
            if delta > best_delta:
                best_delta = delta
                best_invite = inv
        self._invite_cache[guild.id] = {inv.code: inv.uses for inv in current_invites}
        if best_invite and best_delta >= 2 and best_invite.inviter:
            return guild.get_member(best_invite.inviter.id)
        return None

    # ─── MESSAGE TRACKING ─────────────────────────

    def _track_message(self, message: discord.Message) -> int:
        gid, uid = message.guild.id, message.author.id
        now = time.time()
        cfg = self.get_cfg(gid)
        interval = cfg.get("spam_interval", 7)
        cutoff = now - interval
        bucket = self._msg_history.setdefault(gid, {}).setdefault(uid, [])
        bucket.append(now)
        self._msg_history[gid][uid] = [t for t in bucket if t >= cutoff]
        return len(self._msg_history[gid][uid])

    # ─── MESSAGE FILTER + USER-APP DETECTION ──────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return
        if not message.guild:
            return

        utils = self.utils()
        cfg = self.get_cfg(message.guild.id)

        if utils.is_whitelisted(message.guild.id, message.author):
            return

        # ── User-installed app abuse detection ────
        # Must run before content filters because the message author here is the
        # external app (a webhook/system user), not the human attacker.
        if (cfg["automod"].get("antiraid_ext", False)
                and cfg["antiraid_ext"].get("ext_app_detection", True)):
            await self._check_user_installed_app(message, cfg, utils)

        content = message.content or ""

        if cfg["automod"].get("antispam", True):
            count = self._track_message(message)
            if count >= cfg.get("spam_threshold", 6):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Anti-Spam",
                    f"{message.author.mention} triggered anti-spam in {message.channel.mention}.")
                try:
                    user = message.guild.get_member(message.author.id)
                    await utils.mute_member(message.guild, user, duration=60, reason="Auto-mute: spam")
                except discord.Forbidden:
                    if message.guild.id not in self._missing_perms_warned:
                        self._missing_perms_warned.add(message.guild.id)
                        log.warning("Anti-Spam",
                                    f"Missing permissions to mute in {message.guild.name} — mute skipped silently.")
                except discord.HTTPException:
                    pass
                return

        if cfg["automod"].get("antilink", True):
            if INVITE_REGEX.search(content):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Anti-Link",
                    f"{message.author.mention} posted an invite link in {message.channel.mention}.\n\n"
                    f"**Message:**\n{content}")
                return

        if cfg["automod"].get("badwords", True):
            if utils.contains_blocked_word(message.guild.id, content):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Bad Word Filter",
                    f"{message.author.mention} used a blocked word in {message.channel.mention}.\n\n"
                    f"**Message:**\n{content}")
                return

        if cfg["automod"].get("massmention", True):
            mentions = len(message.mentions) + int(message.mention_everyone)
            if mentions >= cfg.get("max_mentions", 5):
                try:
                    await message.delete()
                except Exception:
                    pass
                await utils.log_action(
                    message.guild, "Mass Mention",
                    f"{message.author.mention} mass-mentioned `{mentions}` users in {message.channel.mention}.")
                try:
                    await utils.mute_member(message.guild, message.author, duration=120, reason="Auto-mute: mass mention")
                except discord.Forbidden:
                    if message.guild.id not in self._missing_perms_warned:
                        self._missing_perms_warned.add(message.guild.id)
                        log.warning("AutoMod",
                                    f"Missing permissions to mute in {message.guild.name} — mute skipped silently.")
                except discord.HTTPException:
                    pass
                return

    # ─── USER-INSTALLED APP ABUSE ─────────────────

    async def _check_user_installed_app(self, message: discord.Message, cfg: dict, utils):
        """
        Detect messages created by user-installed applications (external apps)
        triggered via slash commands.

        Detection criteria:
        1. message.application_id is set and != our bot's application_id
        2. message.interaction_metadata exists (discord.py MessageInteractionMetadata)
        3. _is_user_installed_app() returns True (key 1 in _integration_owners, key 0 absent)
        4. triggering user = interaction_metadata.user
        """

        # Must be an application-generated message that isn't our own bot
        if not message.application_id:
            return
        if message.application_id == self.bot.application_id:
            return

        # Requires interaction metadata (only present on app-command responses)
        meta = getattr(message, "interaction_metadata", None)
        if meta is None:
            return

        # Only flag user-installed apps (integration_owners key 1 present, key 0 absent)
        if not _is_user_installed_app(meta):
            return

        # The user who triggered the app
        triggering_user = getattr(meta, "user", None)
        if not triggering_user:
            return

        # Skip whitelisted users
        if utils.is_whitelisted(message.guild.id, triggering_user):
            return

        # Config
        are = cfg.get("antiraid_ext", {})
        threshold = are.get("ext_app_threshold", 3)
        window = are.get("ext_app_window", 15)
        action = are.get("ext_app_action", "kick")

        now = time.time()
        bucket = self._ext_app_history \
            .setdefault(message.guild.id, {}) \
            .setdefault(triggering_user.id, [])

        bucket.append(now)

        # Keep only timestamps within the window
        self._ext_app_history[message.guild.id][triggering_user.id] = [
            t for t in bucket if now - t <= window
        ]
        count = len(self._ext_app_history[message.guild.id][triggering_user.id])

        # Log first detection
        if count == 1:
            log.warning(
                "Ext-App",
                f"{triggering_user} used a user-installed app (ID {message.application_id}) "
                f"in {message.guild.name}."
            )
            await utils.log_action(
                message.guild,
                "🤖 User-Installed App Detected",
                f"{triggering_user.mention} used a **user-installed** external application "
                f"command in {message.channel.mention}.\n"
                f"App ID: `{message.application_id}`\n"
                f"-# Count: {count}/{threshold} before action is taken."
            )

        # Threshold reached → take action
        if count >= threshold:
            self._ext_app_history[message.guild.id][triggering_user.id] = []
            member = message.guild.get_member(triggering_user.id)

            log.warning(
                "Ext-App",
                f"Threshold reached for {triggering_user} in {message.guild.name} — "
                f"action: {action}"
            )
            await utils.log_action(
                message.guild,
                "🚫 User-Installed App Action Taken",
                f"**{triggering_user.mention}** fired `{count}` user-installed app commands "
                f"within `{window}s`.\n"
                f"App ID: `{message.application_id}`\n"
                f"Action taken: `{action}`"
            )

            if member:
                try:
                    if action == "ban":
                        await message.guild.ban(
                            member,
                            reason="AutoMod: user-installed app raid abuse"
                        )
                    elif action == "kick":
                        await member.kick(reason="AutoMod: user-installed app raid abuse")
                    elif action == "warn":
                        utils.add_warn(
                            message.guild.id, member.id, self.bot.user.id,
                            "AutoMod: user-installed app raid abuse"
                        )
                except Exception as e:
                    log.error("Ext-App", f"Failed to action {triggering_user}: {e}")

    # ─── INTERACTION FLOOD DETECTION ──────────────

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """
        Track interactions from recently-joined members.
        When multiple new members fire interactions simultaneously, it indicates
        an external automation tool is coordinating them.
        """
        if not interaction.guild:
            return

        guild = interaction.guild
        member = interaction.user

        cfg = self.get_cfg(guild.id)
        if not cfg["automod"].get("antiraid_ext", False):
            return

        if member.bot:
            return
        if self.utils().is_whitelisted(guild.id, member):
            return

        are = cfg.get("antiraid_ext", {})
        join_age_limit = are.get("join_age_limit", 120)

        joined_at = getattr(member, "joined_at", None)
        if not joined_at:
            return
        now = time.time()
        if now - joined_at.timestamp() > join_age_limit:
            return

        bucket = self._interaction_history.setdefault(guild.id, [])
        bucket.append((member.id, now))

        window = are.get("interaction_window", 30)
        self._interaction_history[guild.id] = [
            (uid, t) for uid, t in bucket if now - t <= window
        ]

        unique_users = len({uid for uid, _ in self._interaction_history[guild.id]})
        threshold = are.get("interaction_threshold", 5)

        if unique_users >= threshold:
            raider_ids = list({uid for uid, _ in self._interaction_history[guild.id]})
            self._interaction_history[guild.id] = []
            log.warning(
                "Ext-Raid",
                f"Interaction flood in {guild.name}: {unique_users} new members "
                f"in {window}s."
            )
            await self._handle_ext_raid(guild, cfg, raider_ids)

    async def _handle_ext_raid(self, guild: discord.Guild, cfg: dict, raider_ids: list):
        are = cfg.get("antiraid_ext", {})
        raider_action = are.get("raider_action", "kick")
        op_action = are.get("operator_action", "notify")

        operator = await self._identify_operator(guild)

        op_mention = operator.mention if operator else "*could not be determined*"
        raider_mentions = ", ".join(f"<@{uid}>" for uid in raider_ids)
        await self.utils().log_action(
            guild,
            "🤖 Interaction Flood Raid Detected",
            f"**{len(raider_ids)}** recently-joined members fired bot interactions "
            f"simultaneously — consistent with an external raid tool.\n\n"
            f"**Suspected Operator:** {op_mention}\n"
            f"**Raiding Accounts:** {raider_mentions}\n\n"
            f"Raider action: `{raider_action}`  •  Operator action: `{op_action}`"
        )

        for uid in raider_ids:
            member = guild.get_member(uid)
            if not member:
                continue
            try:
                if raider_action == "ban":
                    await guild.ban(member, reason="Ext. App Raid: interaction flood")
                else:
                    await member.kick(reason="Ext. App Raid: interaction flood")
                await asyncio.sleep(0.4)
            except Exception:
                pass

        if operator:
            try:
                if op_action == "ban":
                    await guild.ban(operator, reason="Ext. App Raid: suspected operator")
                elif op_action == "kick":
                    await operator.kick(reason="Ext. App Raid: suspected operator")
            except Exception:
                pass

        lang = get_lang(guild)
        try:
            await guild.owner.send(
                f"{get_emoji('icon_danger')} "
                + _t(lang, "extraid_dm",
                     guild=guild.name, count=len(raider_ids),
                     operator=str(operator) if operator else "unknown",
                     ra=raider_action, oa=op_action)
            )
        except Exception:
            pass

    # ─── ANTI-RAID (JOIN FLOOD) ───────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # Snapshot invites in the background — never blocks the join handler
        asyncio.create_task(self._snapshot_invites(guild))

        cfg = self.get_cfg(guild.id)
        if not cfg["automod"].get("antiraid", False):
            return

        ar        = cfg.get("antiraid", {})
        threshold = ar.get("join_threshold", 10)
        interval  = ar.get("join_interval", 10)
        now       = time.time()

        # ── Dedup guard: if a raid wave is already being actioned, drop this event ──
        if now < self._raid_actioned.get(guild.id, 0):
            return

        cutoff = now - interval
        bucket = self._join_history.setdefault(guild.id, [])
        bucket.append(now)
        self._join_history[guild.id] = [t for t in bucket if t >= cutoff]

        if len(self._join_history[guild.id]) < threshold:
            return

        # ── Threshold reached — lock out further waves immediately ───────────
        self._raid_actioned[guild.id] = now + max(interval, 60)
        self._join_history[guild.id]  = []
        join_count = len(bucket)

        log.warning("Anti-Raid", f"Join flood in {guild.name} ({join_count} joins / {interval}s)")

        # Dispatch enforcement as an independent task — this handler returns
        # in microseconds and does zero API calls itself.
        asyncio.create_task(
            self._execute_raid_action(guild, ar, now, join_count)
        )

    # ─── ANTI-NUKE ────────────────────────────────

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        guild = entry.guild
        if not guild:
            return

        cfg = self.get_cfg(guild.id)
        if not cfg["automod"].get("antinuke", False):
            return
        if entry.user is None:
            return
        if entry.user == self.bot.user or entry.user == guild.owner:
            return
        if self.utils().is_whitelisted(guild.id, entry.user):
            return

        an         = cfg.get("antinuke", {})
        interval   = an.get("interval", 10)
        uid        = entry.user.id
        now        = time.time()

        # ── Dedup guard — if this user was already actioned, suppress entirely ──
        # This ensures exactly ONE enforcement action and ONE DM no matter how
        # many audit log events the nuke bot generates.
        guild_actioned = self._nuke_actioned.setdefault(guild.id, {})
        if now < guild_actioned.get(uid, 0):
            return

        action_map = {
            discord.AuditLogAction.ban:            ("ban",            an.get("ban_threshold", 3)),
            discord.AuditLogAction.kick:           ("kick",           an.get("kick_threshold", 3)),
            discord.AuditLogAction.channel_delete: ("channel_delete", an.get("channel_delete_threshold", 3)),
            discord.AuditLogAction.role_delete:    ("role_delete",    an.get("role_delete_threshold", 3)),
            discord.AuditLogAction.channel_create: ("channel_create", an.get("channel_create_threshold", 5)),
            discord.AuditLogAction.webhook_delete: ("webhook_delete", an.get("webhook_delete_threshold", 3)),
        }
        if entry.action not in action_map:
            return

        action_key, threshold = action_map[entry.action]
        cutoff      = now - interval
        user_history = self._nuke_history.setdefault(guild.id, {}).setdefault(uid, {})
        bucket       = user_history.setdefault(action_key, [])
        bucket.append(now)
        user_history[action_key] = [t for t in bucket if t >= cutoff]

        if len(user_history[action_key]) < threshold:
            return  # threshold not yet reached

        # ── Threshold reached ────────────────────────────────────────────────
        # Mark actioned IMMEDIATELY (synchronously, no await) so any concurrent
        # audit events for this user are dropped before we even start the task.
        guild_actioned[uid] = now + max(interval, 60)
        user_history[action_key] = []

        nuke_action = an.get("action", "strip")
        offender    = entry.user
        lang        = get_lang(guild)

        log.warning(
            "Anti-Nuke",
            f"Nuke by {offender} in {guild.name} — "
            f"{threshold}x {action_key} — action: {nuke_action}",
        )

        # Dispatch enforcement as an independent task so it starts on the very
        # next event-loop tick without blocking further audit-log processing.
        asyncio.create_task(
            self._execute_nuke_action(
                guild, offender, action_key, threshold, interval, nuke_action, lang
            )
        )

    async def _execute_nuke_action(
        self,
        guild:       discord.Guild,
        offender:    discord.User,
        action_key:  str,
        threshold:   int,
        interval:    int,
        nuke_action: str,
        lang:        str,
    ):
        """
        Carry out anti-nuke enforcement.  Runs as a fire-and-forget task.

        Order of operations
        ───────────────────
        1. Execute the configured action (strip / kick / ban) immediately.
        2. Run mod-log and owner DM concurrently so neither waits on the other.
        """
        uid    = offender.id
        member = guild.get_member(uid)

        # ── 1. Enforce configured action ─────────────────────────────────────
        if member:
            try:
                if nuke_action == "strip":
                    await self._strip_dangerous_roles(member)
                elif nuke_action == "kick":
                    await member.kick(reason="Anti-Nuke: suspicious mass action")
                elif nuke_action == "ban":
                    await guild.ban(member, reason="Anti-Nuke: suspicious mass action")
            except Exception as exc:
                log.error("Anti-Nuke", f"Failed to {nuke_action} {offender}: {exc}")

        # ── 3. Mod-log + owner DM concurrently ──────────────────────────────
        async def _do_log():
            await self.utils().log_action(
                guild,
                "💣 Anti-Nuke Triggered",
                f"**{offender.mention}** performed `{threshold}` `{action_key}` actions "
                f"within `{interval}s`.\n**Action:** `{nuke_action}`",
            )

        async def _do_dm():
            dm_view = _build_nuke_dm_view(
                guild, offender, action_key, threshold, interval, nuke_action, lang
            )
            await guild.owner.send(view=dm_view)

        await asyncio.gather(_do_log(), _do_dm(), return_exceptions=True)

    async def _execute_raid_action(
        self,
        guild:      discord.Guild,
        ar:         dict,
        trigger_ts: float,
        join_count: int,
    ):
        """
        Carry out anti-raid enforcement.  Runs as a fire-and-forget task.

        Speed strategy
        ─────────────
        • Collect the target members first (pure Python, zero API calls).
        • Fire ALL kick/ban operations via asyncio.gather() — discord.py's
          internal rate-limiter queues them and drains as fast as Discord
          allows.  No artificial asyncio.sleep() delays.
        • Slowmode / lockdown channel edits are also gathered so all channels
          are updated in parallel rather than one-by-one.
        • Log and DM run concurrently after enforcement.
        """
        action            = ar.get("action", "kick")
        interval          = ar.get("join_interval", 10)
        new_account_days  = ar.get("new_account_days", 0)
        lockdown_slowmode = ar.get("lockdown_slowmode", 30)
        lang              = get_lang(guild)

        # ── Collect targets (synchronous — no API calls) ─────────────────────
        now = time.time()
        recent_members: list[discord.Member] = []
        for m in list(guild.members):
            joined = m.joined_at
            if not joined or (now - joined.timestamp()) > interval + 5:
                continue
            if new_account_days > 0:
                if (discord.utils.utcnow() - m.created_at).days >= new_account_days:
                    continue
            recent_members.append(m)

        # ── Enforcement ──────────────────────────────────────────────────────
        if action in ("kick", "ban", "softban"):
            if action == "ban":
                coros = [guild.ban(m, reason="Anti-Raid: mass join") for m in recent_members]
            elif action == "softban":
                coros = [self._softban(guild, m) for m in recent_members]
            else:
                coros = [m.kick(reason="Anti-Raid: mass join") for m in recent_members]
            await asyncio.gather(*coros, return_exceptions=True)

        elif action == "slowmode":
            coros = [
                ch.edit(slowmode_delay=lockdown_slowmode, reason=f"Anti-Raid: slowmode {lockdown_slowmode}s")
                for ch in guild.text_channels
            ]
            await asyncio.gather(*coros, return_exceptions=True)

        elif action == "lockdown":
            async def _lock_channel(ch: discord.TextChannel):
                ow = ch.overwrites_for(guild.default_role)
                ow.send_messages = False
                await ch.set_permissions(guild.default_role, overwrite=ow, reason="Anti-Raid: lockdown")
            await asyncio.gather(
                *[_lock_channel(ch) for ch in guild.text_channels],
                return_exceptions=True,
            )

        # ── Log + DM concurrently ────────────────────────────────────────────
        async def _do_log():
            await self.utils().log_action(
                guild,
                "🌊 Anti-Raid Triggered",
                f"**{join_count}** members joined within `{interval}s`. "
                f"Actioned `{len(recent_members)}` member(s). Executing `{action}`.",
            )

        async def _do_dm():
            await guild.owner.send(
                f"{get_emoji('icon_danger')} "
                + _t(lang, "raid_dm",
                     guild=guild.name, count=join_count,
                     interval=interval, action=action)
            )

        await asyncio.gather(_do_log(), _do_dm(), return_exceptions=True)

    async def _softban(self, guild: discord.Guild, member: discord.Member):
        """Ban + immediate unban to clear recent messages without a permanent ban."""
        await guild.ban(member, reason="Anti-Raid: mass join (softban)", delete_message_days=1)
        await guild.unban(member, reason="Anti-Raid: softban removal")

    async def _strip_dangerous_roles(self, member: discord.Member):
        dangerous = (
            discord.Permissions.administrator,
            discord.Permissions.ban_members,
            discord.Permissions.kick_members,
            discord.Permissions.manage_guild,
            discord.Permissions.manage_channels,
            discord.Permissions.manage_roles,
        )
        roles_to_remove = []
        for role in member.roles:
            if role.managed or role == member.guild.default_role:
                continue
            for perm in dangerous:
                if role.permissions >= perm:
                    roles_to_remove.append(role)
                    break
        if roles_to_remove:
            try:
                await member.remove_roles(
                    *roles_to_remove, reason="Anti-Nuke: dangerous roles stripped")
            except Exception:
                pass

    # ─── SETTINGS COMMAND ─────────────────────────

    @commands.command(
        name="automod",
        help="{ 'en': 'Open the AutoMod settings panel ☕🛡️', 'de': 'AutoMod-Einstellungen' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def automod_settings(self, ctx):
        panel = _build_panel(self, ctx.guild.id, "overview", ctx.guild)
        await ctx.send(view=panel, allowed_mentions=ALLOWED_MENTIONS)


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
