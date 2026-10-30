from .views import *
from .views import _t
from config.ids import SUPPORT_GUILD
from utils import logging

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="onboarding", help=CMDS.help("onboarding"))
    async def onboarding(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            prefix = await _resolve_prefix(self.bot, ctx)
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=_t(ctx, "help_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=_t(ctx, "help_intro")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=_t(ctx, "help_commands_title")),
                discord.ui.TextDisplay(
                    content=_t(ctx, "help_commands", prefix=prefix)
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=_t(
                        ctx,
                        "help_footer",
                        support=links.SUPPORT_SERVER,
                        docs=links.DOCS,
                    )
                )
            )
            view.add_item(container)
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="setup", help=CMDS.help("onboarding.setup"))
    @commands.has_permissions(administrator=True)
    async def onboarding_setup(self, ctx: commands.Context):
        prefix = await _resolve_prefix(self.bot, ctx)
        await ctx.send(
            view=OnboardingSetupView(ctx.guild.id, ctx.author, prefix=prefix, locale=ctx),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @onboarding.command(name="role-menu", help=CMDS.help("onboarding.role-menu"))
    @commands.has_permissions(administrator=True)
    async def onboarding_role_menu(self, ctx: commands.Context):
        await ctx.send(
            view=RoleMenuManagerView(
                ctx.guild.id, ctx.author, await get_config(ctx.guild.id), ctx,
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @onboarding.command(name="autoroles", help=CMDS.help("onboarding.autoroles"))
    @commands.has_permissions(administrator=True)
    async def onboarding_autoroles(self, ctx: commands.Context):
        await ctx.send(
            view=AutoroleSetupView(
                ctx.guild.id, ctx.author, ctx.guild, await get_config(ctx.guild.id), ctx,
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @onboarding.command(name="captcha", help=CMDS.help("onboarding.captcha"))
    @commands.has_permissions(administrator=True)
    async def onboarding_captcha(self, ctx: commands.Context):
        await ctx.send(
            view=CaptchaSetupView(
                ctx.guild.id, ctx.author, ctx.guild, await get_config(ctx.guild.id), ctx,
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is not None:
            return
        if message.author.bot:
            return

        user_id = message.author.id
        pending = _pending_verifications.get(user_id)
        if pending is None:
            return

        # DMs carry no guild, so the member gets the wording of the server their
        # captcha belongs to rather than English by default.
        locale = self.bot.get_guild(pending["guild_id"])

        guess = message.content.strip().upper()
        correct = pending["code"].upper()

        if guess == correct:
            _pending_verifications.pop(user_id, None)
            guild_id = pending["guild_id"]

            # Roles, the audit log, and the guild/member lookups are shared with
            # the one-click and website modes (utils/verification/service.py).
            result = await verification_service.complete(
                self.bot, guild_id, user_id,
                source=verification_modes.LABELS[verification_modes.IMAGE],
            )

            if result["problem"] == "guild":
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(content=_t(locale, "verified_no_guild")),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                return await message.channel.send(view=view)

            if result["problem"] == "member":
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(content=_t(locale, "verified_no_member")),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                return await message.channel.send(view=view)

            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=_t(locale, "verified_title")),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=_t(locale, "verified_body"))
            )
            if result["applied"]:
                container.add_item(discord.ui.TextDisplay(
                    _t(locale, "verified_roles_added", roles=", ".join(result["applied"]))
                ))
            if result["removed"]:
                container.add_item(discord.ui.TextDisplay(
                    _t(locale, "verified_roles_removed", roles=", ".join(result["removed"]))
                ))
            view.add_item(container)

            await message.channel.send(view=view)

        else:
            pending["attempts"] += 1
            attempts_left = 3 - pending["attempts"]

            if attempts_left <= 0:
                _pending_verifications.pop(user_id, None)
                guild_id = pending["guild_id"]
                guild = self.bot.get_guild(guild_id)
                cfg = await get_config(guild_id) if guild else None

                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(content=_t(locale, "captcha_failed_title")),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(content=_t(locale, "captcha_failed_body"))
                )
                if cfg and cfg.captcha_kick_on_fail:
                    container.add_item(discord.ui.TextDisplay(_t(locale, "captcha_kicked")))
                else:
                    container.add_item(discord.ui.TextDisplay(content=_t(locale, "captcha_retry")))
                view.add_item(container)
                await message.channel.send(view=view)

                await verification_service.fail(
                    self.bot, guild_id, user_id,
                    kick=bool(cfg and cfg.captcha_kick_on_fail),
                    source=verification_modes.LABELS[verification_modes.IMAGE],
                )
            else:
                code, img_bytes = generate_captcha()
                pending["code"] = code
                file = discord.File(img_bytes, filename="captcha.png")
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(content=_t(locale, "captcha_incorrect_title")),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content=_t(locale, "captcha_attempts_left", count=attempts_left)
                    ),
                    discord.ui.MediaGallery(
                        discord.MediaGalleryItem(
                            media=file
                        )
                    )
                )
                view.add_item(container)
                await message.channel.send(view=view, file=file)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        cfg = await get_config(member.guild.id)
        if member.guild.id == SUPPORT_GUILD:
            try:
                from cogs.staff.support_server import get_support_ids, assign_join_roles
                support_ids = await get_support_ids(self.bot)
                await assign_join_roles(self.bot, member, support_ids["roles"])
            except Exception as exc:
                logging.warning("Onboarding", f"Support role synchronization failed for {member.id}: {exc}")

        # ── Autoroles ─────────────────────────────
        configured_role_ids = cfg.bot_autorole_ids if member.bot else cfg.autorole_ids
        if configured_role_ids:
            roles_to_add = [
                member.guild.get_role(rid)
                for rid in configured_role_ids
                if member.guild.get_role(rid)
            ]
            if roles_to_add:
                # Queue role assignments per-guild so a join wave doesn't
                # blow through Discord's role-edit rate limit.
                await role_assign_limiter.acquire(member.guild.id)
                try:
                    await member.add_roles(*roles_to_add, reason="Onboarding bot autoroles" if member.bot else "Onboarding member autoroles")
                except discord.Forbidden:
                    pass  # bot lacks permission — silently skip
                except discord.HTTPException:
                    pass

        # ── Welcome message ───────────────────────
        if not cfg.welcome_channel:
            return

        channel = member.guild.get_channel(cfg.welcome_channel)
        if not channel:
            return

        view = build_welcome_view(cfg, member, member.guild)
        # allow user and role mentions but not everyone and here
        welcome_mentions = discord.AllowedMentions(everyone=False, roles=True, users=True)
        # Throttle welcome sends per-guild so raids can't spam the channel.
        await welcome_limiter.acquire(member.guild.id)
        try:
            await channel.send(view=view, allowed_mentions=welcome_mentions)
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Post the guild's goodbye message when a member leaves.

        Servers only get one if they set a goodbye channel, so the default is
        still silence. Joins and leaves share the same send limiter because both
        are bursts on the same channel.
        """
        cfg = await get_config(member.guild.id)
        if not cfg.goodbye_channel:
            return

        channel = member.guild.get_channel(cfg.goodbye_channel)
        if not channel:
            return

        view = build_goodbye_view(cfg, member, member.guild)
        goodbye_mentions = discord.AllowedMentions(everyone=False, roles=True, users=True)
        await welcome_limiter.acquire(member.guild.id)
        try:
            await channel.send(view=view, allowed_mentions=goodbye_mentions)
        except discord.HTTPException:
            pass

async def setup(bot):
    await bot.add_cog(Onboarding(bot))

    # One-time migration of legacy data/onboarding/*.json into the database.
    await migrate_json_files(bot)

    for guild_id, cfg in await load_all_configs():
        # A persistent view renders once, at startup, so it has to pick its
        # wording from the guild rather than from an interaction.
        guild = bot.get_guild(guild_id)

        if cfg.rules_channel and cfg.rules_message_id:
            bot.add_view(
                RulesAcknowledgeView(guild_id, cfg=cfg, locale=guild),
                message_id=cfg.rules_message_id,
            )

        for menu_id, menu in (cfg.role_menus or {}).items():
            if menu.get("channel_id") and menu.get("message_id"):
                bot.add_view(
                    RoleMenuView(guild_id, menu_id, cfg=cfg, locale=guild),
                    message_id=menu["message_id"],
                )

        if cfg.captcha_channel_id and cfg.captcha_panel_message_id:
            bot.add_view(
                CaptchaPanelView(guild_id, mode=cfg.captcha_mode, locale=guild),
                message_id=cfg.captcha_panel_message_id,
            )
