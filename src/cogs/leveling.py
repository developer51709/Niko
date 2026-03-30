# leveling.py
# Bilingual EN/DE, café personality, cv2 LayoutView responses.
# Supports per-guild config: XP toggle, multiplier, cooldown, level-up channel, level roles.

import discord
from discord.ext import commands
import random
import json
import os
import time
from utils import logging as log
from utils.paginator import PaginatedView, paginate

PERSONALITY = "cafe"

# ─────────────────────────────────────────────────────────────
#  MESSAGE TABLE
# ─────────────────────────────────────────────────────────────

MESSAGES = {
    "normal": {
        "en": {
            "level_up":          "Congratulations {mention}, you leveled up to level **{level}**!",
            "no_xp":             "{name} hasn't earned any XP yet.",
            "stats_title":       "Level Stats — {name}",
            "stats_level":       "Level",
            "stats_xp":          "XP",
            "stats_rank":        "Rank",
            "leaderboard_title": "Leveling Leaderboard — {guild}",
            "leaderboard_empty": "No one has earned any XP in this server yet.",
            "xp_disabled":       "XP tracking is currently disabled for this server.",
            "cfg_updated":       "✅ Setting updated.",
            "cfg_show":          "### Level Config — {guild}\n{body}",
        },
        "de": {
            "level_up":          "Glückwunsch {mention}, du bist auf Level **{level}** aufgestiegen!",
            "no_xp":             "{name} hat noch keine XP gesammelt.",
            "stats_title":       "Level-Statistiken — {name}",
            "stats_level":       "Level",
            "stats_xp":          "XP",
            "stats_rank":        "Rang",
            "leaderboard_title": "Leveling-Bestenliste — {guild}",
            "leaderboard_empty": "Noch niemand hat XP auf diesem Server gesammelt.",
            "xp_disabled":       "XP-Tracking ist für diesen Server deaktiviert.",
            "cfg_updated":       "✅ Einstellung aktualisiert.",
            "cfg_show":          "### Level-Konfiguration — {guild}\n{body}",
        },
    },
    "cafe": {
        "en": {
            "level_up":          "congratulations {mention}, you leveled up to level **{level}**! ☕✨",
            "no_xp":             "{name} hasn't brewed any XP yet ☕😔",
            "stats_title":       "☕ cozy level stats for {name}",
            "stats_level":       "vibe-level",
            "stats_xp":          "xp brewed",
            "stats_rank":        "café rank",
            "leaderboard_title": "☕ cozy leaderboard — {guild}",
            "leaderboard_empty": "no one has brewed any xp in this café yet 😭",
            "xp_disabled":       "xp tracking is off for this server ☕",
            "cfg_updated":       "✅ setting updated~",
            "cfg_show":          "### ☕ cozy level config — {guild}\n{body}",
        },
        "de": {
            "level_up":          "glückwunsch {mention}, du bist auf level **{level}** aufgestiegen! ☕✨",
            "no_xp":             "{name} hat noch keine XP aufgebrüht ☕😔",
            "stats_title":       "☕ gemütliche level-statistiken für {name}",
            "stats_level":       "vibe-level",
            "stats_xp":          "aufgebrühte xp",
            "stats_rank":        "café-rang",
            "leaderboard_title": "☕ gemütliche bestenliste — {guild}",
            "leaderboard_empty": "niemand hat hier bisher xp aufgebrüht 😭",
            "xp_disabled":       "xp-tracking ist für diesen server deaktiviert ☕",
            "cfg_updated":       "✅ einstellung aktualisiert~",
            "cfg_show":          "### ☕ gemütliche level-config — {guild}\n{body}",
        },
    },
}


def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def get_personality():
    return PERSONALITY if PERSONALITY in MESSAGES else "normal"


def msg(ctx, key, **kwargs):
    personality = get_personality()
    lang = get_lang(ctx)
    block = MESSAGES.get(personality, {}).get(lang, {})
    text = block.get(key)
    if text is None:
        text = MESSAGES.get(personality, {}).get("en", {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


# ─────────────────────────────────────────────────────────────
#  GUILD CONFIG
# ─────────────────────────────────────────────────────────────

LEVEL_CONFIG_PATH = "data/level_config.json"

DEFAULT_GUILD_LEVEL_CONFIG = {
    "xp_enabled":      True,
    "xp_multiplier":   1.0,
    "xp_cooldown":     0,
    "level_up_channel": None,
    "level_roles":     {},
}


def _load_level_config() -> dict:
    if os.path.exists(LEVEL_CONFIG_PATH):
        try:
            with open(LEVEL_CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_level_config(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(LEVEL_CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)


def _get_guild_level_cfg(configs: dict, guild_id: str) -> dict:
    if guild_id not in configs:
        import copy
        configs[guild_id] = copy.deepcopy(DEFAULT_GUILD_LEVEL_CONFIG)
    else:
        for k, v in DEFAULT_GUILD_LEVEL_CONFIG.items():
            configs[guild_id].setdefault(k, v)
    return configs[guild_id]


# ─────────────────────────────────────────────────────────────
#  LEVELING COG
# ─────────────────────────────────────────────────────────────

class Leveling(commands.Cog):
    """Cozy bilingual leveling system with guild config support."""

    def __init__(self, bot):
        self.bot = bot
        self.data_path = "data/levels.json"
        self.levels = self._load_levels()
        self.level_configs = _load_level_config()
        self._cooldown_cache: dict[str, float] = {}

    def _load_levels(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {}

    def _save_levels(self):
        with open(self.data_path, "w") as f:
            json.dump(self.levels, f, indent=4)

    def _save_configs(self):
        _save_level_config(self.level_configs)

    def _guild_cfg(self, guild_id: str) -> dict:
        return _get_guild_level_cfg(self.level_configs, guild_id)

    def get_xp_for_level(self, level: int) -> int:
        return 5 * (level ** 2) + (50 * level) + 100

    # ─── XP EVENT ────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        user_id  = str(message.author.id)
        cfg      = self._guild_cfg(guild_id)

        if not cfg.get("xp_enabled", True):
            return

        # Cooldown check
        cooldown = cfg.get("xp_cooldown", 0)
        if cooldown > 0:
            cache_key = f"{guild_id}:{user_id}"
            last_xp = self._cooldown_cache.get(cache_key, 0)
            now = time.time()
            if now - last_xp < cooldown:
                return
            self._cooldown_cache[cache_key] = now

        if guild_id not in self.levels:
            self.levels[guild_id] = {}
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0}

        multiplier = cfg.get("xp_multiplier", 1.0)
        xp_gain = int(random.randint(15, 25) * multiplier)
        self.levels[guild_id][user_id]["xp"] += xp_gain

        current_xp    = self.levels[guild_id][user_id]["xp"]
        current_level = self.levels[guild_id][user_id]["level"]
        next_level_xp = self.get_xp_for_level(current_level)

        if current_xp >= next_level_xp:
            self.levels[guild_id][user_id]["level"] += 1
            self.levels[guild_id][user_id]["xp"] = 0
            new_level = self.levels[guild_id][user_id]["level"]

            # Determine level-up channel
            lu_channel_id = cfg.get("level_up_channel")
            lu_channel = (
                message.guild.get_channel(lu_channel_id)
                if lu_channel_id
                else message.channel
            )

            try:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=msg(message, "level_up",
                                    mention=message.author.mention, level=new_level)
                    )
                )
                view.add_item(container)
                if lu_channel:
                    await lu_channel.send(view=view)
                log.info("Leveling", f"User {message.author} leveled up to {new_level} in {message.guild.name}")
            except discord.Forbidden:
                pass

            # Assign level roles if configured
            level_roles = cfg.get("level_roles", {})
            role_id = level_roles.get(str(new_level))
            if role_id:
                role = message.guild.get_role(int(role_id))
                if role:
                    try:
                        await message.author.add_roles(role, reason=f"Level-up reward: level {new_level}")
                    except Exception:
                        pass

        self._save_levels()

    # ─── RANK COMMAND ────────────────────────────────────────

    @commands.command(
        name="level",
        aliases=["rank"],
        help="Check your cozy level stats ☕ | Zeigt deine Level-Statistiken."
    )
    async def level(self, ctx, member: discord.Member = None):
        member   = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id  = str(member.id)

        cfg = self._guild_cfg(guild_id)
        if not cfg.get("xp_enabled", True):
            return await ctx.send(msg(ctx, "xp_disabled"))

        if guild_id not in self.levels or user_id not in self.levels[guild_id]:
            return await ctx.send(msg(ctx, "no_xp", name=member.display_name))

        user_data     = self.levels[guild_id][user_id]
        current_level = user_data["level"]
        current_xp    = user_data["xp"]
        next_level_xp = self.get_xp_for_level(current_level)

        sorted_users = sorted(
            self.levels[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )
        rank = next((i for i, (uid, _) in enumerate(sorted_users, 1) if uid == user_id), 1)

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

    # ─── LEADERBOARD COMMAND ──────────────────────────────────

    @commands.command(
        name="level-leaderboard",
        aliases=["lvl-lb"],
        help="View the cozy leaderboard ☕ | Zeigt die Level-Bestenliste."
    )
    async def leaderboard(self, ctx):
        guild_id = str(ctx.guild.id)

        cfg = self._guild_cfg(guild_id)
        if not cfg.get("xp_enabled", True):
            return await ctx.send(msg(ctx, "xp_disabled"))

        if guild_id not in self.levels or not self.levels[guild_id]:
            return await ctx.send(msg(ctx, "leaderboard_empty"))

        sorted_users = sorted(
            self.levels[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )

        lines = []
        for i, (user_id, data) in enumerate(sorted_users, start=1):
            user   = self.bot.get_user(int(user_id))
            name   = user.display_name if user else f"User {user_id}"
            medal  = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"**{i}.**")
            lines.append(f"{medal} {name} — Level {data['level']} ({data['xp']} XP)")

        pages = paginate(lines, per_page=10)
        view = PaginatedView(
            title=msg(ctx, "leaderboard_title", guild=ctx.guild.name),
            pages=pages,
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )
        await ctx.send(view=view)

    # ─── LEVELCONFIG COMMAND GROUP ────────────────────────────

    @commands.group(
        name="levelconfig",
        aliases=["lvlcfg"],
        invoke_without_command=True,
        help="View or configure the leveling system. | Level-Einstellungen anzeigen / bearbeiten."
    )
    @commands.has_permissions(manage_guild=True)
    async def levelconfig(self, ctx):
        """Show current leveling config for this server."""
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)

        lu_ch = ctx.guild.get_channel(cfg.get("level_up_channel") or 0)
        lu_ch_str = lu_ch.mention if lu_ch else "*(same channel)*"

        lr = cfg.get("level_roles", {})
        lr_lines = "\n".join(
            f"  Level {lvl}: {ctx.guild.get_role(int(rid)).mention if ctx.guild.get_role(int(rid)) else rid}"
            for lvl, rid in sorted(lr.items(), key=lambda x: int(x[0]))
        ) or "  *(none)*"

        body = (
            f"**XP Enabled:** {'✅' if cfg.get('xp_enabled', True) else '❌'}\n"
            f"**XP Multiplier:** `{cfg.get('xp_multiplier', 1.0)}x`\n"
            f"**XP Cooldown:** `{cfg.get('xp_cooldown', 0)}s`\n"
            f"**Level-Up Channel:** {lu_ch_str}\n"
            f"**Level Roles:**\n{lr_lines}"
        )

        text = msg(ctx, "cfg_show", guild=ctx.guild.name, body=body)
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
        await ctx.send(view=view)

    @levelconfig.command(name="toggle", help="Enable or disable XP for this server.")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_toggle(self, ctx):
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        cfg["xp_enabled"] = not cfg.get("xp_enabled", True)
        self._save_configs()
        state = "✅ enabled" if cfg["xp_enabled"] else "❌ disabled"
        await ctx.send(f"XP tracking is now **{state}** for this server.")

    @levelconfig.command(name="multiplier", aliases=["xpmultiplier"], help="Set XP gain multiplier (e.g. 2.0).")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_multiplier(self, ctx, value: float = None):
        if value is None or value <= 0:
            return await ctx.send("Please provide a positive multiplier (e.g. `1.5`).")
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        cfg["xp_multiplier"] = round(value, 2)
        self._save_configs()
        await ctx.send(msg(ctx, "cfg_updated") + f" XP multiplier → `{cfg['xp_multiplier']}x`")

    @levelconfig.command(name="cooldown", help="Set XP cooldown between gains in seconds (0 = off).")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_cooldown(self, ctx, seconds: int = None):
        if seconds is None or seconds < 0:
            return await ctx.send("Please provide a non-negative number of seconds.")
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        cfg["xp_cooldown"] = seconds
        self._save_configs()
        status = f"`{seconds}s`" if seconds > 0 else "off"
        await ctx.send(msg(ctx, "cfg_updated") + f" XP cooldown → {status}")

    @levelconfig.command(name="levelupchannel", aliases=["luchannel"], help="Set the level-up announcement channel.")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_channel(self, ctx, channel: discord.TextChannel = None):
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        cfg["level_up_channel"] = channel.id if channel else None
        self._save_configs()
        dest = channel.mention if channel else "*(same channel)*"
        await ctx.send(msg(ctx, "cfg_updated") + f" Level-up channel → {dest}")

    @levelconfig.command(name="levelrole", aliases=["role"], help="Assign a role when a level is reached. Usage: .levelconfig levelrole <level> @role")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_levelrole(self, ctx, level: int = None, role: discord.Role = None):
        if level is None or level < 1:
            return await ctx.send("Please specify a valid level (e.g. `5`).")
        guild_id = str(ctx.guild.id)
        cfg = self._guild_cfg(guild_id)
        lr = cfg.setdefault("level_roles", {})
        if role is None:
            lr.pop(str(level), None)
            self._save_configs()
            await ctx.send(msg(ctx, "cfg_updated") + f" Removed level role for level {level}.")
        else:
            lr[str(level)] = role.id
            self._save_configs()
            await ctx.send(msg(ctx, "cfg_updated") + f" Level {level} → {role.mention}")

    @levelconfig.command(name="resetuser", help="Reset XP and level for a member.")
    @commands.has_permissions(manage_guild=True)
    async def levelconfig_resetuser(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("Please specify a member.")
        guild_id = str(ctx.guild.id)
        user_id  = str(member.id)
        if guild_id in self.levels and user_id in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0}
            self._save_levels()
        await ctx.send(f"✅ Reset XP and level for **{member.display_name}**.")


async def setup(bot):
    await bot.add_cog(Leveling(bot))
