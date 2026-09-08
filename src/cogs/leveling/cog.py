from .panel import *
import asyncio
import json
import os
import time
import random
from utils.discord_extras import burst_react
from utils.image.level_card import render_level_card, render_level_leaderboard_card
from utils.image.economy_card import fetch_avatar_bytes, _strip_discord_emoji


class Leveling(commands.Cog):
    """Modern leveling system with image cards and slash commands."""

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
            # Card customization
            for key, col in [("card_accent", "card_accent"), ("card_bg_top", "card_bg_top"), ("card_bg_bottom", "card_bg_bottom")]:
                try:
                    val = row[col]
                    cfg[key] = json.loads(val) if val else None
                except Exception:
                    cfg[key] = None
        return cfg

    async def _save_guild_cfg(self, guild_id, cfg: dict):
        gid = int(guild_id)
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO level_config "
            "(guild_id, xp_enabled, xp_multiplier, xp_cooldown, "
            " level_up_channel, level_up_message, level_roles, "
            " card_accent, card_bg_top, card_bg_bottom) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
            gid,
            int(cfg.get("xp_enabled", True)),
            cfg.get("xp_multiplier", 1.0),
            cfg.get("xp_cooldown", 0),
            cfg.get("level_up_channel"),
            cfg.get("level_up_message"),
            json.dumps(cfg.get("level_roles", {})),
            json.dumps(cfg.get("card_accent"))    if cfg.get("card_accent")    else None,
            json.dumps(cfg.get("card_bg_top"))    if cfg.get("card_bg_top")    else None,
            json.dumps(cfg.get("card_bg_bottom")) if cfg.get("card_bg_bottom") else None,
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
                    lu_msg = await lu_channel.send(view=view)
                    asyncio.create_task(burst_react(self.bot, lu_channel.id, lu_msg.id, "🎉"))
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

    # ── LEVELING GROUP ────────────────────────────

    @commands.hybrid_group(
        name="leveling",
        aliases=["levels", "lvl", "lv"],
        invoke_without_command=True,
        description="All leveling commands — rank, leaderboard, config, and panel",
        help="{ 'en': 'All leveling commands.', 'de': 'Alle Leveling-Befehle.' }"
    )
    async def leveling(self, ctx):
        """Show a quick overview or help for the leveling system."""
        cfg = await self._guild_cfg(ctx.guild.id)
        enabled_s = get_emoji("icon_tick") if cfg.get("xp_enabled", True) else get_emoji("icon_cross")
        embed_text = (
            f"### ☕ Leveling Commands\n"
            f"**Status:** {enabled_s} • **Multiplier:** `{cfg.get('xp_multiplier', 1.0)}x` • "
            f"**Cooldown:** `{cfg.get('xp_cooldown', 0)}s`\n\n"
            "Use `/leveling rank`, `/leveling leaderboard`, `/leveling panel`, or `/leveling config`.\n"
            "-# Type `/leveling` to see this help, or use a subcommand."
        )
        view = discord.ui.LayoutView()
        accent_rgb = cfg.get("card_accent")
        accent_colour = discord.Colour.from_rgb(*accent_rgb) if accent_rgb else discord.Colour(0xFFC45C)
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=embed_text),
            accent_colour=accent_colour,
        ))
        await ctx.send(view=view)

    # ── RANK SUBCOMMAND ───────────────────────────

    @leveling.command(
        name="rank",
        aliases=["level", "profile"],
        description="Check your level stats with a beautiful image card",
        help="{ 'en': 'Check your level stats ☕', 'de': 'Zeigt deine Level-Statistiken.', 'es': 'Consulta tus estadísticas de nivel ☕' }"
    )
    async def leveling_rank(self, ctx, member: discord.Member = None):
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

        # Fetch avatar
        avatar_url = member.display_avatar.url if member.display_avatar else None
        avatar_bytes = await fetch_avatar_bytes(avatar_url)

        # Parse card customization colours
        accent = tuple(cfg.get("card_accent")) if cfg.get("card_accent") else None
        bg_top = tuple(cfg.get("card_bg_top")) if cfg.get("card_bg_top") else None
        bg_bot = tuple(cfg.get("card_bg_bottom")) if cfg.get("card_bg_bottom") else None

        # Render the level card image
        card_image = await render_level_card(
            avatar_bytes=avatar_bytes,
            name=member.display_name,
            level=current_level,
            xp=current_xp,
            xp_for_next=next_level_xp,
            rank=rank,
            accent=accent,
            bg_top=bg_top,
            bg_bot=bg_bot,
        )

        # Build CV2 LayoutView with MediaGallery
        file = discord.File(card_image, filename="level_card.png")
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.MediaGallery(discord.MediaGalleryItem(media="attachment://level_card.png")),
            accent_colour=discord.Colour.from_rgb(*accent) if accent else discord.Colour(0xFFC45C),
        )
        view.add_item(container)
        await ctx.send(file=file, view=view)

    # ── LEADERBOARD SUBCOMMAND (with pagination) ──

    @leveling.command(
        name="leaderboard",
        aliases=["lb", "top"],
        description="View the server's leveling leaderboard with navigation buttons",
        help="{ 'en': 'View the leaderboard 🏆', 'de': 'Zeigt die Bestenliste.' }"
    )
    async def leveling_leaderboard(self, ctx):
        guild_id = ctx.guild.id

        cfg = await self._guild_cfg(guild_id)
        if not cfg.get("xp_enabled", True):
            return await ctx.send(msg(ctx, "xp_disabled"))

        rows = await self._get_guild_leaderboard(guild_id)
        if not rows:
            return await ctx.send(msg(ctx, "leaderboard_empty"))

        if ctx.interaction:
            await ctx.interaction.defer()

        # Pre-build all pages of entries
        per_page = 10
        total_pages = max(1, (len(rows) + per_page - 1) // per_page)

        # Parse card customization
        accent = tuple(cfg.get("card_accent")) if cfg.get("card_accent") else None
        bg_top = tuple(cfg.get("card_bg_top")) if cfg.get("card_bg_top") else None
        bg_bot = tuple(cfg.get("card_bg_bottom")) if cfg.get("card_bg_bottom") else None

        # Build entry data for all pages
        pages_entries = []
        for page_idx in range(total_pages):
            start = page_idx * per_page
            page_rows = rows[start:start + per_page]
            entries = []
            for i, row in enumerate(page_rows, start=start + 1):
                user = self.bot.get_user(row["user_id"])
                name = user.display_name if user else f"User {row['user_id']}"
                avatar_bytes = None
                if user and user.display_avatar:
                    avatar_bytes = await fetch_avatar_bytes(user.display_avatar.url)
                entries.append({
                    "rank": i,
                    "name": _strip_discord_emoji(name),
                    "level": row["level"],
                    "xp": row["xp"],
                    "avatar": avatar_bytes,
                })
            pages_entries.append(entries)

        total_pages = len(pages_entries)
        title = msg(ctx, "leaderboard_title", guild=ctx.guild.name)

        # ── Interactive paginated view ─────────────

        class _PrevButton(discord.ui.Button):
            def __init__(self, disabled: bool):
                super().__init__(label="◀", style=discord.ButtonStyle.secondary, disabled=disabled)

            async def callback(self, interaction: discord.Interaction):
                v: _LBView = self.view
                if v.current_page == 0:
                    return await interaction.defer()
                v.current_page -= 1
                await interaction.response.defer()
                buf = await render_level_leaderboard_card(
                    title=title, entries=v.pages[v.current_page],
                    page=v.current_page + 1, pages=total_pages,
                    accent=accent, bg_top=bg_top, bg_bot=bg_bot,
                )
                v._build()
                await interaction.message.edit(
                    view=v,
                    attachments=[discord.File(buf, "leaderboard.png")],
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        class _NextButton(discord.ui.Button):
            def __init__(self, disabled: bool):
                super().__init__(label="▶", style=discord.ButtonStyle.secondary, disabled=disabled)

            async def callback(self, interaction: discord.Interaction):
                v: _LBView = self.view
                if v.current_page >= len(v.pages) - 1:
                    return await interaction.defer()
                v.current_page += 1
                await interaction.response.defer()
                buf = await render_level_leaderboard_card(
                    title=title, entries=v.pages[v.current_page],
                    page=v.current_page + 1, pages=total_pages,
                    accent=accent, bg_top=bg_top, bg_bot=bg_bot,
                )
                v._build()
                await interaction.message.edit(
                    view=v,
                    attachments=[discord.File(buf, "leaderboard.png")],
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        class _PageLabel(discord.ui.Button):
            def __init__(self, label: str):
                super().__init__(label=label, style=discord.ButtonStyle.secondary, disabled=True)

        class _LBView(discord.ui.LayoutView):
            def __init__(self, pages: list[list[dict]]):
                super().__init__(timeout=180)
                self.pages = pages
                self.current_page = 0
                self._build()

            def _build(self):
                self.clear_items()
                total = len(self.pages)
                container = discord.ui.Container(
                    discord.ui.TextDisplay(content=f"### 🏆 Leveling Leaderboard"),
                    discord.ui.MediaGallery(discord.MediaGalleryItem(media="attachment://leaderboard.png")),
                )
                container.add_item(discord.ui.TextDisplay(
                    content=f"-# Showing top **{min(len(rows), per_page)}** of **{len(rows)}** members."
                ))

                if total > 1:
                    container.add_item(discord.ui.Separator(
                        visible=True, spacing=discord.SeparatorSpacing.small,
                    ))
                    container.add_item(discord.ui.ActionRow(
                        _PrevButton(disabled=self.current_page == 0),
                        _PageLabel(label=f"{self.current_page + 1} / {total}"),
                        _NextButton(disabled=self.current_page == total - 1),
                    ))

                self.add_item(container)

        # Render first page and send
        first_buf = await render_level_leaderboard_card(
            title=title, entries=pages_entries[0],
            page=1, pages=total_pages,
            accent=accent, bg_top=bg_top, bg_bot=bg_bot,
        )
        view = _LBView(pages_entries)

        if ctx.interaction:
            await ctx.interaction.followup.send(
                view=view,
                file=discord.File(first_buf, "leaderboard.png"),
                allowed_mentions=discord.AllowedMentions.none(),
            )
        else:
            await ctx.send(
                view=view,
                file=discord.File(first_buf, "leaderboard.png"),
                allowed_mentions=discord.AllowedMentions.none(),
            )

    # ── PANEL SUBCOMMAND ──────────────────────────

    @leveling.command(
        name="panel",
        aliases=["levelpanel", "settings"],
        description="Open the interactive leveling management panel",
        help="{ 'en': 'Open the interactive leveling management panel ☕', 'de': 'Leveling-Dashboard öffnen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def leveling_panel(self, ctx):
        panel = await _build_level_panel(self, ctx.guild.id, "overview", ctx.guild)
        await ctx.send(view=panel)

    # ── CONFIG SUBCOMMAND GROUP ────────────────────

    @leveling.group(
        name="config",
        aliases=["cfg", "settings"],
        invoke_without_command=True,
        description="View or configure the leveling system",
        help="{ 'en': 'View or configure the leveling system.', 'de': 'Level-Einstellungen anzeigen / bearbeiten.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def leveling_config(self, ctx):
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

        accent_rgb = cfg.get("card_accent")
        accent_colour = discord.Colour.from_rgb(*accent_rgb) if accent_rgb else discord.Colour(0xFFC45C)

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=text),
            accent_colour=accent_colour,
        ))
        await ctx.send(view=view)

    @leveling_config.command(
        name="toggle",
        description="Enable or disable XP for this server",
        help="{ 'en': 'Enable or disable XP for this server.', 'de': 'XP für diesen Server aktivieren/deaktivieren.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def leveling_config_toggle(self, ctx):
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["xp_enabled"] = not cfg.get("xp_enabled", True)
        await self._save_guild_cfg(ctx.guild.id, cfg)
        state = f"{get_emoji('icon_tick')} enabled" if cfg["xp_enabled"] else f"{get_emoji('icon_cross')} disabled"
        await ctx.send(f"XP tracking is now **{state}** for this server.")

    @leveling_config.command(
        name="multiplier",
        aliases=["xpmultiplier"],
        description="Set XP gain multiplier",
        help="{ 'en': 'Set XP gain multiplier (e.g. 2.0).', 'de': 'XP-Verstärkung einstellen (z.B. 2.0).' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def leveling_config_multiplier(self, ctx, value: float = None):
        if value is None or value <= 0:
            return await ctx.send("Please provide a positive multiplier (e.g. `1.5`).")
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["xp_multiplier"] = round(value, 2)
        await self._save_guild_cfg(ctx.guild.id, cfg)
        await ctx.send(msg(ctx, "cfg_updated") + f" XP multiplier → `{cfg['xp_multiplier']}x`")

    @leveling_config.command(
        name="cooldown",
        description="Set XP cooldown between gains in seconds",
        help="{ 'en': 'Set XP cooldown between gains in seconds (0 = off).', 'de': 'XP-Cooldown in Sekunden einstellen (0 = aus).' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def leveling_config_cooldown(self, ctx, seconds: int = None):
        if seconds is None or seconds < 0:
            return await ctx.send("Please provide a non-negative number of seconds.")
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["xp_cooldown"] = seconds
        await self._save_guild_cfg(ctx.guild.id, cfg)
        status = f"`{seconds}s`" if seconds > 0 else "off"
        await ctx.send(msg(ctx, "cfg_updated") + f" XP cooldown → {status}")

    @leveling_config.command(
        name="levelupchannel",
        aliases=["luchannel", "channel"],
        description="Set the level-up announcement channel",
        help="{ 'en': 'Set the level-up announcement channel.', 'de': 'Level-Up-Benachrichtigungs-Kanal einstellen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def leveling_config_channel(self, ctx, channel: discord.TextChannel = None):
        cfg = await self._guild_cfg(ctx.guild.id)
        cfg["level_up_channel"] = channel.id if channel else None
        await self._save_guild_cfg(ctx.guild.id, cfg)
        dest = channel.mention if channel else "*(same channel)*"
        await ctx.send(msg(ctx, "cfg_updated") + f" Level-up channel → {dest}")

    @leveling_config.command(
        name="levelrole",
        aliases=["role"],
        description="Assign a role when a level is reached",
        help="{ 'en': 'Assign a role when a level is reached.', 'de': 'Rolle bei Erreichen eines Levels zuweisen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def leveling_config_levelrole(self, ctx, level: int = None, role: discord.Role = None):
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

    @leveling_config.command(
        name="resetuser",
        description="Reset XP and level for a member",
        help="{ 'en': 'Reset XP and level for a member.', 'de': 'XP und Level eines Mitglieds zurücksetzen.' }"
    )
    @commands.has_permissions(manage_guild=True)
    async def leveling_config_resetuser(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("Please specify a member.")
        await self._save_user_data(ctx.guild.id, member.id, 0, 0)
        await ctx.send(f"{get_emoji('icon_tick')} Reset XP and level for **{member.display_name}**.")


async def setup(bot):
    await bot.add_cog(Leveling(bot))
