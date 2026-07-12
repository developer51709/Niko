from .views import *

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="onboarding", help="Manage server onboarding")
    async def onboarding(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            prefix = await _resolve_prefix(self.bot, ctx)
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(content="### Server Onboarding"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="Setup onboarding for your server to help new members get started without requiring an entire staff team to welcome them!"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content="**Onboarding Commands**"),
                discord.ui.TextDisplay(
                    content=(
                        f"**`{prefix}onboarding setup`** — Setup onboarding for the server.\n"
                        f"**`{prefix}onboarding role-menu`** — Setup role menu for the server.\n"
                        f"**`{prefix}onboarding autoroles`** — Configure auto-assigned roles on join.\n"
                        f"**`{prefix}onboarding captcha`** — Configure captcha human verification."
                    )
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"-# **Need help?**\n-# Ask in the [support server]({links.SUPPORT_SERVER}) or check the [documentation]({links.DOCS})"
                )
            )
            view.add_item(container)
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def onboarding_setup(self, ctx: commands.Context):
        """Setup onboarding for the server."""
        prefix = await _resolve_prefix(self.bot, ctx)
        await ctx.send(view=OnboardingSetupView(ctx.guild.id, ctx.author, prefix=prefix), allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="role-menu")
    @commands.has_permissions(administrator=True)
    async def onboarding_role_menu(self, ctx: commands.Context):
        """Setup role menu for the server."""
        prefix = await _resolve_prefix(self.bot, ctx)
        await ctx.send(view=RoleMenuSetupView(ctx.guild.id, ctx.author, prefix=prefix), allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="autoroles")
    @commands.has_permissions(administrator=True)
    async def onboarding_autoroles(self, ctx: commands.Context):
        """Configure which roles are automatically given to new members on join."""
        await ctx.send(view=AutoroleSetupView(ctx.guild.id, ctx.author, ctx.guild), allowed_mentions=discord.AllowedMentions.none())

    @onboarding.command(name="captcha")
    @commands.has_permissions(administrator=True)
    async def onboarding_captcha(self, ctx: commands.Context):
        """Configure captcha verification for the server."""
        await ctx.send(view=CaptchaSetupView(ctx.guild.id, ctx.author, ctx.guild), allowed_mentions=discord.AllowedMentions.none())

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

        guess = message.content.strip().upper()
        correct = pending["code"].upper()

        if guess == correct:
            _pending_verifications.pop(user_id, None)
            guild_id = pending["guild_id"]
            guild = self.bot.get_guild(guild_id)
            cfg = get_config(guild_id)

            if guild is None:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} Verification passed! However, I could not find the server to apply roles."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                return await message.channel.send(view=view)

            member = guild.get_member(user_id)
            if member is None:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"{get_emoji('icon_tick')} Verification passed! However, I could not find you in the server."
                    ),
                    accent_colour=discord.Color.green()
                )
                view.add_item(container)
                return await message.channel.send(view=view)

            applied = []
            removed = []

            if cfg.captcha_add_role_ids:
                for rid in cfg.captcha_add_role_ids:
                    role = guild.get_role(rid)
                    if role:
                        try:
                            await member.add_roles(role, reason="Captcha verification passed")
                            applied.append(role.name)
                        except discord.Forbidden:
                            pass

            if cfg.captcha_remove_role_ids:
                for rid in cfg.captcha_remove_role_ids:
                    role = guild.get_role(rid)
                    if role and role in member.roles:
                        try:
                            await member.remove_roles(role, reason="Captcha verification passed")
                            removed.append(role.name)
                        except discord.Forbidden:
                            pass

            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_tick')} Verification complete!"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="You have been verified."
                )
            )
            if applied:
                container.add_item(discord.ui.TextDisplay(f"Roles added: {', '.join(applied)}"))
            if removed:
                container.add_item(discord.ui.TextDisplay(f"Roles removed: {', '.join(removed)}"))
            view.add_item(container)

            await message.channel.send(view=view)

            # Log captcha pass
            logger = self.bot.get_cog("ServerLogger")
            if logger and guild and member:
                pass_body = (
                    f"**User:** {member.mention} (`{member}` — ID: `{member.id}`)\n"
                    f"**Result:** Passed\n"
                    f"**Roles Added:** {', '.join(applied) if applied else 'None'}\n"
                    f"**Roles Removed:** {', '.join(removed) if removed else 'None'}"
                )
                await logger.log_event(
                    guild, "captcha", "Captcha Passed", pass_body,
                    target_id=member.id
                )

        else:
            pending["attempts"] += 1
            attempts_left = 3 - pending["attempts"]

            if attempts_left <= 0:
                _pending_verifications.pop(user_id, None)
                guild_id = pending["guild_id"]
                guild = self.bot.get_guild(guild_id)
                cfg = get_config(guild_id) if guild else None

                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"### {get_emoji('icon_cross')} Verification failed!"
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content="You have failed the captcha verification."
                    )
                )
                if cfg and cfg.captcha_kick_on_fail:
                    container.add_item(discord.ui.TextDisplay("You have been kicked from the server."))
                else:
                    container.add_item(discord.ui.TextDisplay(content="Return to the server and click **Verify** again to get a new captcha."))
                view.add_item(container)
                await message.channel.send(view=view)

                will_kick = guild and cfg and cfg.captcha_kick_on_fail

                # Log captcha fail / kick
                logger = self.bot.get_cog("ServerLogger")
                if logger and guild:
                    log_title = "Captcha Kicked" if will_kick else "Captcha Failed"
                    fail_body = (
                        f"**User:** <@{user_id}> (ID: `{user_id}`)\n"
                        f"**Result:** {'Failed all 3 attempts and kicked' if will_kick else 'Failed all 3 attempts'}"
                    )
                    await logger.log_event(
                        guild, "captcha", log_title, fail_body,
                        target_id=user_id, action_key=log_title
                    )

                if will_kick:
                    member = guild.get_member(user_id)
                    if member:
                        try:
                            await member.kick(reason="Failed captcha verification (3 wrong attempts)")
                        except discord.Forbidden:
                            pass
            else:
                code, img_bytes = generate_captcha()
                pending["code"] = code
                file = discord.File(img_bytes, filename="captcha.png")
                view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"### {get_emoji('icon_cross')} Incorrect."
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(
                        content=f"You have **{attempts_left}** attempt(s) left. Here is a new captcha:"
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
        cfg = get_config(member.guild.id)

        # ── Autoroles ─────────────────────────────
        if cfg.autorole_ids:
            roles_to_add = [
                member.guild.get_role(rid)
                for rid in cfg.autorole_ids
                if member.guild.get_role(rid)
            ]
            if roles_to_add:
                # Queue role assignments per-guild so a join wave doesn't
                # blow through Discord's role-edit rate limit.
                await role_assign_limiter.acquire(member.guild.id)
                try:
                    await member.add_roles(*roles_to_add, reason="Onboarding autoroles")
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

        view = build_welcome_view(cfg, member)
        # allow user and role mentions but not everyone and here
        welcome_mentions = discord.AllowedMentions(everyone=False, roles=True, users=True)
        # Throttle welcome sends per-guild so raids can't spam the channel.
        await welcome_limiter.acquire(member.guild.id)
        try:
            await channel.send(view=view, allowed_mentions=welcome_mentions)
        except discord.HTTPException:
            pass

async def setup(bot):
    await bot.add_cog(Onboarding(bot))

    for guild_id, cfg in load_all_configs():
        if cfg.rules_channel and cfg.rules_message_id:
            bot.add_view(RulesAcknowledgeView(guild_id), message_id=cfg.rules_message_id)

        if cfg.role_menu_channel and cfg.role_menu_message_id:
            bot.add_view(RoleMenuView(guild_id), message_id=cfg.role_menu_message_id)

        if cfg.captcha_channel_id and cfg.captcha_panel_message_id:
            bot.add_view(CaptchaPanelView(guild_id), message_id=cfg.captcha_panel_message_id)
