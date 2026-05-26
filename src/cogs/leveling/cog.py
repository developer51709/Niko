from .panel import *

class Leveling(commands.Cog):
    """Cozy bilingual leveling system with guild config support."""

    def __init__(self, bot):
        self.bot = bot
        self._cooldown_cache: dict = {}

    async def cog_load(self):
        """Migrate legacy JSON data into the central database (one-time)."""
        await self._migrate_levels_json()
        await self._migrate_level_config_json()

    # ── DB HELPERS ─────────────────────────────────

    async def _guild_cfg(self, guild_id) -> dict:
        """Return the level config dict for a guild, falling back to defaults."""
        gid = int(guild_id)
        row = await self.bot.cxn.fetchrow(
            "SELECT * FROM level_config WHERE guild_id = $1", gid
        )
        cfg = dict(DEFAULT_GUILD_LEVEL_CONFIG)
        if row:
            cfg["xp_enabled"]       = bool(row["xp_enabled"])
            cfg["xp_multiplier"]    = row["xp_multiplier"]
            cfg["xp_cooldown"]      = row["xp_cooldown"]
            cfg["level_up_channel"] = row["level_up_channel"]
            cfg["level_up_message"] = row["level_up_message"]
            try:
                cfg["level_roles"] = json.loads(row["level_roles"] or "{}")
            except Exception:
                cfg["level_roles"] = {}
        return cfg

    async def _save_guild_cfg(self, guild_id, cfg: dict):
        gid = int(guild_id)
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO level_config "
            "(guild_id, xp_enabled, xp_multiplier, xp_cooldown, "
            " level_up_channel, level_up_message, level_roles) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7)",
            gid,
            int(cfg.get("xp_enabled", True)),
            cfg.get("xp_multiplier", 1.0),
            cfg.get("xp_cooldown", 0),
            cfg.get("level_up_channel"),
            cfg.get("level_up_message"),
            json.dumps(cfg.get("level_roles", {})),
        )

    async def _get_user_data(self, guild_id, user_id) -> dict:
        row = await self.bot.cxn.fetchrow(
            "SELECT xp, level FROM levels WHERE guild_id = $1 AND user_id = $2",
            int(guild_id), int(user_id)
        )
        return {"xp": row["xp"], "level": row["level"]} if row else {"xp": 0, "level": 0}

    async def _save_user_data(self, guild_id, user_id, xp: int, level: int):
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO levels (guild_id, user_id, xp, level) VALUES ($1, $2, $3, $4)",
            int(guild_id), int(user_id), xp, level
        )

    async def _get_guild_leaderboard(self, guild_id) -> list:
        return await self.bot.cxn.fetch(
            "SELECT user_id, xp, level FROM levels "
            "WHERE guild_id = $1 ORDER BY level DESC, xp DESC",
            int(guild_id)
        )

    async def _get_user_rank(self, guild_id, user_id) -> int:
        rows = await self.bot.cxn.fetch(
            "SELECT user_id FROM levels WHERE guild_id = $1 ORDER BY level DESC, xp DESC",
            int(guild_id)
        )
        for i, row in enumerate(rows, 1):
            if row["user_id"] == int(user_id):
                return i
        return len(rows) or 1

    # ── MIGRATION HELPERS ──────────────────────────

    async def _migrate_levels_json(self):
        path = "data/levels.json"
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            count = 0
            for guild_id, users in data.items():
                for user_id, ud in users.items():
                    existing = await self.bot.cxn.fetchval(
                        "SELECT 1 FROM levels WHERE guild_id = $1 AND user_id = $2",
                        int(guild_id), int(user_id)
                    )
                    if not existing:
                        await self._save_user_data(guild_id, user_id,
                                                   ud.get("xp", 0), ud.get("level", 0))
                        count += 1
            if count:
                log.info("Leveling", f"Migrated {count} records from levels.json → database.db")
            os.rename(path, path + ".migrated")
        except Exception as e:
            log.warning("Leveling", f"Could not migrate levels.json: {e}")

    async def _migrate_level_config_json(self):
        path = "data/level_config.json"
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                configs = json.load(f)
            count = 0
            for guild_id, cfg in configs.items():
                existing = await self.bot.cxn.fetchval(
                    "SELECT 1 FROM level_config WHERE guild_id = $1", int(guild_id)
                )
                if not existing:
                    await self._save_guild_cfg(guild_id, cfg)
                    count += 1
            if count:
                log.info("Leveling", f"Migrated {count} guild configs from level_config.json → database.db")
            os.rename(path, path + ".migrated")
        except Exception as e:
            log.warning("Leveling", f"Could not migrate level_config.json: {e}")

    # ── XP FORMULA ─────────────────────────────────

    def get_xp_for_level(self, level: int) -> int:
        return 5 * (level ** 2) + (50 * level) + 100

    # ── XP EVENT ───────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        user_id  = message.author.id
        cfg      = await self._guild_cfg(guild_id)

        if not cfg.get("xp_enabled", True):
            return

        # Cooldown check (in-memory)
        cooldown = cfg.get("xp_cooldown", 0)
        if cooldown > 0:
            cache_key = f"{guild_id}:{user_id}"
            last_xp   = self._cooldown_cache.get(cache_key, 0)
            now       = time.time()
            if now - last_xp < cooldown:
                return
            self._cooldown_cache[cache_key] = now

        user_data     = await self._get_user_data(guild_id, user_id)
        multiplier    = cfg.get("xp_multiplier", 1.0)
        xp_gain       = int(random.randint(15, 25) * multiplier)
        current_xp    = user_data["xp"] + xp_gain
        current_level = user_data["level"]
        next_level_xp = self.get_xp_for_level(current_level)

        if current_xp >= next_level_xp:
            current_level += 1
            current_xp     = 0
            await self._save_user_data(guild_id, user_id, current_xp, current_level)

            lu_channel_id = cfg.get("level_up_channel")
            lu_channel    = (
                message.guild.get_channel(lu_channel_id) if lu_channel_id else message.channel
            )

            try:
                custom_template = cfg.get("level_up_message")
                if custom_template:
                    lu_text = custom_template.format(
                        mention=message.author.mention,
                        level=current_level,
                        name=message.author.display_name,
                        guild=message.guild.name,
                    )
                else:
                    lu_text = msg(message, "level_up",
                                  mention=message.author.mention, level=current_level)
                view = discord.ui.LayoutView()
                view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=lu_text)))
                if lu_channel:
                    await lu_channel.send(view=view)
                log.debug("Leveling", f"User {message.author} leveled up to {current_level} in {message.guild.name}")
            except discord.Forbidden:
                pass

            # Assign level roles
            level_roles = cfg.get("level_roles", {})
            role_id = level_roles.get(str(current_level))
            if role_id:
                role = message.guild.get_role(int(role_id))
                if role:
                    try:
                        await message.author.add_roles(role, reason=f"Level-up reward: level {current_level}")
                    except Exception:
                        pass
        else:
            await self._save_user_data(guild_id, user_id, current_xp, current_level)

    # ── RANK COMMAND ───────────────────────────────

    @commands.hybrid_command(
        name="level",
        aliases=["rank"],
        description="Check your cozy level stats",
        help="{ 'en': 'Check your cozy level stats ☕', 'de': 'Zeigt deine Level-Statistiken.', 'es': 'Consulta tus estadísticas de nivel ☕' }"
    )
    async def level(self, ctx, member: discord.Member = None):
        member   = member or ctx.author
        guild_id = ctx.guild.id
        user_id  = member.id

        cfg = await self._guild_cfg(guild_id)
        if not cfg.get("xp_enabled", True):
            return await ctx.send(msg(ctx, "xp_disabled"))

        user_data = await self._get_user_data(guild_id, user_id)
        if user_data["xp"] == 0 and user_data["level"] == 0:
            existing = await self.bot.cxn.fetchval(
                "SELECT 1 FROM levels WHERE guild_id = $1 AND user_id = $2",
                int(guild_id), int(user_id)
            )
            if not existing:
                return await ctx.send(msg(ctx, "no_xp", name=member.display_name))

        current_level = user_data["level"]
        current_xp    = user_data["xp"]
        next_level_xp = self.get_xp_for_level(current_level)
        rank          = await self._get_user_rank(guild_id, user_id)

        text = (
            f"### {msg(ctx, 'stats_title', name=member.display_name)}\n"
            f"**{msg(ctx, 'stats_level')}:** {current_level}\n"
            f"**{msg(ctx, 'stats_xp')}:** {current_xp}/{next_level_xp}\n"
            f"**{msg(ctx, 'stats_rank')}:** #{rank}"
        )

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=text),
                accessory=discord.ui.Thumbnail(member.display_avatar.url)
            )
        ))
        await ctx.send(view=view)

    # ── LEADERBOARD ────────────────────────────────

    @commands.command(
        name="level-leaderboard",
        aliases=["lvl-lb"],
        help="{ 'en': 'View the cozy leaderboard ☕', 'de': 'Zeigt die Level-Bestenliste.' }"
    )
    async def leaderboard(self, ctx):
        guild_id = ctx.guild.id

        cfg = await self._guild_cfg(guild_id)
        if not cfg.get("xp_enabled", True):
            return await ctx.send(msg(ctx, "xp_disabled"))

        rows = await self._get_guild_leaderboard(guild_id)
        if not rows:
            return await ctx.send(msg(ctx, "leaderboard_empty"))

        lines = []
        for i, row in enumerate(rows, start=1):
            user  = self.bot.get_user(row["user_id"])
            name  = user.display_name if user else f"User {row['user_id']}"
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"**{i}.**")
            lines.append(f"{medal} {name} — Level {row['level']} ({row['xp']} XP)")

        pages = paginate(lines, per_page=10)
        view  = PaginatedView(
            title=msg(ctx, "leaderboard_title", guild=ctx.guild.name),
            pages=pages,
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )
        await ctx.send(view=view)

    # ── LEVELCONFIG COMMAND GROUP ──────────────────

    @commands.group(
        name="levelconfig",
        aliases=["lvlcfg"],
        invoke_without_command=True,
        help="{ 'en': 'View or configure the leveling system.', 'de': 'Level-Einstellungen anzeigen / bearbeiten.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig(self, ctx):
        guild_id = ctx.guild.id
        cfg      = await self._guild_cfg(guild_id)

        lu_ch     = ctx.guild.get_channel(cfg.get("level_up_channel") or 0)
        lu_ch_str = lu_ch.mention if lu_ch else "*(same channel)*"
        lr        = cfg.get("level_roles", {})
        lr_lines  = "\n".join(
            f"  Level {lvl}: {ctx.guild.get_role(int(rid)).mention if ctx.guild.get_role(int(rid)) else rid}"
            for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0]))
        ) or "  *(none)*"

        body = (
            f"**XP Enabled:** {get_emoji('icon_tick') if cfg.get('xp_enabled', True) else get_emoji('icon_cross')}\n"
            f"**XP Multiplier:** `{cfg.get('xp_multiplier', 1.0)}x`\n"
            f"**XP Cooldown:** `{cfg.get('xp_cooldown', 0)}s`\n"
            f"**Level-Up Channel:** {lu_ch_str}\n"
            f"**Level Roles:**\n{lr_lines}"
        )

        text = msg(ctx, "cfg_show", guild=ctx.guild.name, body=body)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
        await ctx.send(view=view)

    @levelconfig.command(
        name="toggle", 
        help="{ 'en': 'Enable or disable XP for this server.', 'de': 'XP für diesen Server aktivieren/deaktivieren.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_toggle(self, ctx):
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["xp_enabled"] = not cfg.get("xp_enabled", True)
        await self._save_guild_cfg(ctx.guild.id, cfg)
        state = f"{get_emoji('icon_tick')} enabled" if cfg["xp_enabled"] else f"{get_emoji('icon_cross')} disabled"
        await ctx.send(f"XP tracking is now **{state}** for this server.")

    @levelconfig.command(
        name="multiplier", 
        aliases=["xpmultiplier"],
        help="{ 'en': 'Set XP gain multiplier (e.g. 2.0).', 'de': 'XP-Verstärkung einstellen (z.B. 2.0).' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_multiplier(self, ctx, value: float = None):
        if value is None or value <= 0:
            return await ctx.send("Please provide a positive multiplier (e.g. `1.5`).")
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["xp_multiplier"] = round(value, 2)
        await self._save_guild_cfg(ctx.guild.id, cfg)
        await ctx.send(msg(ctx, "cfg_updated") + f" XP multiplier → `{cfg['xp_multiplier']}x`")

    @levelconfig.command(
        name="cooldown",
        help="{ 'en': 'Set XP cooldown between gains in seconds (0 = off).', 'de': 'XP-Cooldown in Sekunden einstellen (0 = aus).' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_cooldown(self, ctx, seconds: int = None):
        if seconds is None or seconds < 0:
            return await ctx.send("Please provide a non-negative number of seconds.")
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["xp_cooldown"] = seconds
        await self._save_guild_cfg(ctx.guild.id, cfg)
        status = f"`{seconds}s`" if seconds > 0 else "off"
        await ctx.send(msg(ctx, "cfg_updated") + f" XP cooldown → {status}")

    @levelconfig.command(
        name="levelupchannel", 
        aliases=["luchannel"],
        help="{ 'en': 'Set the level-up announcement channel.', 'de': 'Level-Up-Benachrichtigungs-Kanal einstellen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_channel(self, ctx, channel: discord.TextChannel = None):
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["level_up_channel"] = channel.id if channel else None
        await self._save_guild_cfg(ctx.guild.id, cfg)
        dest = channel.mention if channel else "*(same channel)*"
        await ctx.send(msg(ctx, "cfg_updated") + f" Level-up channel → {dest}")

    @levelconfig.command(
        name="levelrole", 
        aliases=["role"],
        help="{ 'en': 'Assign a role when a level is reached.', 'de': 'Rolle bei Erreichen eines Levels zuweisen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_levelrole(self, ctx, level: int = None, role: discord.Role = None):
        if level is None or level < 1:
            return await ctx.send("Please specify a valid level (e.g. `5`).")
        cfg = await self._guild_cfg(ctx.guild.id)
        lr  = cfg.setdefault("level_roles", {})
        if role is None:
            lr.pop(str(level), None)
            await self._save_guild_cfg(ctx.guild.id, cfg)
            await ctx.send(msg(ctx, "cfg_updated") + f" Removed level role for level {level}.")
        else:
            lr[str(level)] = role.id
            await self._save_guild_cfg(ctx.guild.id, cfg)
            await ctx.send(msg(ctx, "cfg_updated") + f" Level {level} → {role.mention}")

    @levelconfig.command(
        name="resetuser", 
        help="{ 'en': 'Reset XP and level for a member.', 'de': 'XP und Level eines Mitglieds zurücksetzen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_resetuser(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("Please specify a member.")
        await self._save_user_data(ctx.guild.id, member.id, 0, 0)
        await ctx.send(f"{get_emoji('icon_tick')} Reset XP and level for **{member.display_name}**.")

    # ── LEVELING PANEL ─────────────────────────────

    @commands.command(
        name="levelpanel",
        aliases=["lvlpanel", "lp"],
        help="{ 'en': 'Open the interactive leveling management panel ☕', 'de': 'Leveling-Dashboard öffnen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def levelpanel(self, ctx):
        panel = await _build_level_panel(self, ctx.guild.id, "overview", ctx.guild)
        await ctx.send(view=panel)


async def setup(bot):
    await bot.add_cog(Leveling(bot))
