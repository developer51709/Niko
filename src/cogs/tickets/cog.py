from .views import *

class Tickets(commands.Cog):
    """Premium ticket system."""

    def __init__(self, bot):
        self.bot = bot

    # ───── group root ──────────────────────────────

    @commands.hybrid_group(
        name="ticket",
        description="Ticket system commands.",
        help="{ 'en': 'Ticket system commands.', 'de': 'Ticketsystem-Befehle.', 'es': 'Comandos del sistema de tickets.' }",
        invoke_without_command=True,
    )
    async def ticket(self, ctx: commands.Context):
        await ctx.send_help(self.ticket)

    # ───── admin: setup panel ─────────────────────

    @ticket.command(
        name="setup",
        description="Open the ticket-system setup panel.",
        help="{ 'en': 'Open the ticket-system setup panel (admin).', 'de': 'Setup-Panel des Ticketsystems öffnen (Admin).', 'es': 'Abre el panel de configuración del sistema de tickets (admin).' }",
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def ticket_setup(self, ctx: commands.Context):
        view = TicketSetupView(ctx.guild.id, ctx.author, lang=_ctx_lang(ctx), personality=get_personality(ctx))
        await ctx.send(view=view)

    # ───── admin: post panel here ─────────────────

    @ticket.command(
        name="panel",
        description="Post the public ticket panel in this channel.",
        help="{ 'en': 'Post the ticket panel in this channel (admin).', 'de': 'Ticket-Panel in diesem Kanal posten (Admin).', 'es': 'Publica el panel de tickets en este canal (admin).' }",
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def ticket_panel(self, ctx: commands.Context):
        cfg = get_ticket_config(ctx.guild.id)
        view = TicketPanelView(ctx.guild.id, cfg)
        sent = await ctx.channel.send(view=view)
        cfg.panel_message_id = sent.id
        cfg.panel_channel_id = ctx.channel.id
        update_ticket_config(ctx.guild.id, cfg)
        await ctx.send(view=_cv2_text(ctx, "panel_posted", channel=ctx.channel.mention), ephemeral=True if ctx.interaction else False)

    # ───── admin: category management ─────────────

    @ticket.group(
        name="category",
        description="Manage ticket categories.",
        help="{ 'en': 'Manage ticket categories (add/remove/list).', 'de': 'Ticket-Kategorien verwalten.', 'es': 'Gestiona las categorías de tickets.' }",
        invoke_without_command=True,
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def ticket_category(self, ctx: commands.Context):
        await ctx.send_help(self.ticket_category)

    @ticket_category.command(
        name="add",
        description="Add a ticket category.",
        help="{ 'en': 'Add a ticket category.', 'de': 'Eine Ticket-Kategorie hinzufügen.', 'es': 'Añade una categoría de tickets.' }",
    )
    async def ticket_category_add(self, ctx: commands.Context, *, name: str):
        cfg = get_ticket_config(ctx.guild.id)
        if name in cfg.panel_categories:
            return await ctx.send(view=_cv2_text(ctx, "category_exists", name=name))
        cfg.panel_categories.append(name)
        update_ticket_config(ctx.guild.id, cfg)
        await self._refresh_panel(ctx.guild, cfg)
        await ctx.send(view=_cv2_text(ctx, "category_added", name=name))

    @ticket_category.command(
        name="remove",
        description="Remove a ticket category.",
        help="{ 'en': 'Remove a ticket category.', 'de': 'Eine Ticket-Kategorie entfernen.', 'es': 'Elimina una categoría de tickets.' }",
    )
    async def ticket_category_remove(self, ctx: commands.Context, *, name: str):
        cfg = get_ticket_config(ctx.guild.id)
        if name not in cfg.panel_categories:
            return await ctx.send(view=_cv2_text(ctx, "category_missing", name=name))
        cfg.panel_categories.remove(name)
        update_ticket_config(ctx.guild.id, cfg)
        await self._refresh_panel(ctx.guild, cfg)
        await ctx.send(view=_cv2_text(ctx, "category_removed", name=name))

    @ticket_category.command(
        name="list",
        description="List all ticket categories.",
        help="{ 'en': 'List all ticket categories.', 'de': 'Alle Ticket-Kategorien anzeigen.', 'es': 'Lista todas las categorías de tickets.' }",
    )
    async def ticket_category_list(self, ctx: commands.Context):
        cfg = get_ticket_config(ctx.guild.id)
        if not cfg.panel_categories:
            return await ctx.send(view=_cv2_text(ctx, "categories_empty"))
        body = "\n".join(f"• **{c}**" for c in cfg.panel_categories)
        await ctx.send(view=_cv2_text(ctx, "categories_list", list=body))

    # ───── admin: support role management ─────────

    @ticket.group(
        name="support",
        description="Manage support roles.",
        help="{ 'en': 'Manage support roles (add/remove/list).', 'de': 'Support-Rollen verwalten.', 'es': 'Gestiona los roles de soporte.' }",
        invoke_without_command=True,
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def ticket_support(self, ctx: commands.Context):
        await ctx.send_help(self.ticket_support)

    @ticket_support.command(
        name="add",
        description="Add a support role.",
        help="{ 'en': 'Add a support role.', 'de': 'Eine Support-Rolle hinzufügen.', 'es': 'Añade un rol de soporte.' }",
    )
    async def ticket_support_add(self, ctx: commands.Context, role: discord.Role):
        cfg = get_ticket_config(ctx.guild.id)
        if role.id in cfg.support_roles:
            return await ctx.send(view=_cv2_text(ctx, "support_exists", role=role.mention), allowed_mentions=discord.AllowedMentions.none())
        cfg.support_roles.append(role.id)
        update_ticket_config(ctx.guild.id, cfg)
        await ctx.send(view=_cv2_text(ctx, "support_added", role=role.mention), allowed_mentions=discord.AllowedMentions.none())

    @ticket_support.command(
        name="remove",
        description="Remove a support role.",
        help="{ 'en': 'Remove a support role.', 'de': 'Eine Support-Rolle entfernen.', 'es': 'Elimina un rol de soporte.' }",
    )
    async def ticket_support_remove(self, ctx: commands.Context, role: discord.Role):
        cfg = get_ticket_config(ctx.guild.id)
        if role.id not in cfg.support_roles:
            return await ctx.send(view=_cv2_text(ctx, "support_missing", role=role.mention), allowed_mentions=discord.AllowedMentions.none())
        cfg.support_roles.remove(role.id)
        update_ticket_config(ctx.guild.id, cfg)
        await ctx.send(view=_cv2_text(ctx, "support_removed", role=role.mention), allowed_mentions=discord.AllowedMentions.none())

    @ticket_support.command(
        name="list",
        description="List support roles.",
        help="{ 'en': 'List support roles.', 'de': 'Support-Rollen anzeigen.', 'es': 'Lista los roles de soporte.' }",
    )
    async def ticket_support_list(self, ctx: commands.Context):
        cfg = get_ticket_config(ctx.guild.id)
        if not cfg.support_roles:
            return await ctx.send(view=_cv2_text(ctx, "support_empty"))
        body = "\n".join(
            f"• {ctx.guild.get_role(rid).mention if ctx.guild.get_role(rid) else f'`{rid}`'}"
            for rid in cfg.support_roles
        )
        await ctx.send(view=_cv2_text(ctx, "support_list", list=body), allowed_mentions=discord.AllowedMentions.none())

    # ───── in-ticket: add user ────────────────────

    @ticket.command(
        name="add",
        description="Add a user to this ticket.",
        help="{ 'en': 'Add a user to this ticket (in-ticket).', 'de': 'Einen Nutzer zu diesem Ticket hinzufügen (im Ticket).', 'es': 'Añade un usuario a este ticket (dentro del ticket).' }",
    )
    @commands.guild_only()
    async def ticket_add(self, ctx: commands.Context, user: discord.Member):
        if not is_ticket_channel(ctx):
            return await ctx.send(view=_cv2_text(ctx, "not_in_ticket"))
        cfg = get_ticket_config(ctx.guild.id)
        if not has_support_perms(ctx.author, cfg):
            return await ctx.send(view=_cv2_text(ctx, "no_perm_manage"))
        existing = ctx.channel.overwrites_for(user)
        if existing.read_messages:
            return await ctx.send(view=_cv2_text(ctx, "user_already_added", user=user.mention))
        await ctx.channel.set_permissions(
            user, read_messages=True, send_messages=True,
            attach_files=True, embed_links=True,
            reason=f"Added by {ctx.author}",
        )
        await ctx.send(view=_cv2_text(ctx, "user_added", user=user.mention))

    # ───── in-ticket: remove user ─────────────────

    @ticket.command(
        name="remove",
        description="Remove a user from this ticket.",
        help="{ 'en': 'Remove a user from this ticket (in-ticket).', 'de': 'Einen Nutzer aus diesem Ticket entfernen (im Ticket).', 'es': 'Elimina un usuario de este ticket (dentro del ticket).' }",
    )
    @commands.guild_only()
    async def ticket_remove(self, ctx: commands.Context, user: discord.Member):
        if not is_ticket_channel(ctx):
            return await ctx.send(view=_cv2_text(ctx, "not_in_ticket"))
        cfg = get_ticket_config(ctx.guild.id)
        if not has_support_perms(ctx.author, cfg):
            return await ctx.send(view=_cv2_text(ctx, "no_perm_manage"))
        existing = ctx.channel.overwrites_for(user)
        if not existing.read_messages:
            return await ctx.send(view=_cv2_text(ctx, "user_not_in_ticket", user=user.mention))
        await ctx.channel.set_permissions(user, overwrite=None, reason=f"Removed by {ctx.author}")
        await ctx.send(view=_cv2_text(ctx, "user_removed", user=user.mention))

    # ───── in-ticket: rename ──────────────────────

    @ticket.command(
        name="rename",
        description="Rename this ticket channel.",
        help="{ 'en': 'Rename this ticket (in-ticket).', 'de': 'Dieses Ticket umbenennen (im Ticket).', 'es': 'Renombra este ticket (dentro del ticket).' }",
    )
    @commands.guild_only()
    async def ticket_rename(self, ctx: commands.Context, *, name: str):
        if not is_ticket_channel(ctx):
            return await ctx.send(view=_cv2_text(ctx, "not_in_ticket"))
        cfg = get_ticket_config(ctx.guild.id)
        if not has_support_perms(ctx.author, cfg):
            return await ctx.send(view=_cv2_text(ctx, "no_perm_manage"))
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        clean = name.strip().lower().replace(" ", "-")[:90]
        await ctx.channel.edit(name=clean, reason=f"Renamed by {ctx.author}")
        await ctx.send(view=_cv2_text(ctx, "renamed", name=clean))

    # ───── in-ticket: claim ───────────────────────

    @ticket.command(
        name="claim",
        description="Claim this ticket as a support member.",
        help="{ 'en': 'Claim this ticket as a support member (in-ticket).', 'de': 'Dieses Ticket als Support-Mitglied beanspruchen (im Ticket).', 'es': 'Reclama este ticket como miembro del soporte (dentro del ticket).' }",
    )
    @commands.guild_only()
    async def ticket_claim(self, ctx: commands.Context):
        ticket = is_ticket_channel(ctx)
        if not ticket:
            return await ctx.send(view=_cv2_text(ctx, "not_in_ticket"))
        cfg = get_ticket_config(ctx.guild.id)
        if not has_support_perms(ctx.author, cfg):
            return await ctx.send(view=_cv2_text(ctx, "no_perm_manage"))
        existing = ticket.get("claimed_by")
        if existing and existing != ctx.author.id:
            other = ctx.guild.get_member(existing)
            who = other.mention if other else f"<@{existing}>"
            return await ctx.send(view=_cv2_text(ctx, "already_claimed", user=who))
        ticket["claimed_by"] = ctx.author.id
        update_ticket_config(ctx.guild.id, cfg)
        await ctx.send(view=_cv2_text(ctx, "claimed", user=ctx.author.mention))

    # ───── in-ticket: transcript ──────────────────

    @ticket.command(
        name="transcript",
        description="Generate a transcript of this ticket.",
        help="{ 'en': 'Generate a text transcript of this ticket (in-ticket).', 'de': 'Ein Textprotokoll dieses Tickets erstellen (im Ticket).', 'es': 'Genera una transcripción de texto de este ticket (dentro del ticket).' }",
    )
    @commands.guild_only()
    async def ticket_transcript(self, ctx: commands.Context):
        if not is_ticket_channel(ctx):
            return await ctx.send(view=_cv2_text(ctx, "not_in_ticket"))
        cfg = get_ticket_config(ctx.guild.id)
        if not has_support_perms(ctx.author, cfg):
            return await ctx.send(view=_cv2_text(ctx, "no_perm_manage"))
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        lines = []
        async for m in ctx.channel.history(limit=2000, oldest_first=True):
            ts = m.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            content = m.content or ""
            if m.attachments:
                content += " [attachments: " + ", ".join(a.url for a in m.attachments) + "]"
            lines.append(f"[{ts}] {m.author} ({m.author.id}): {content}")
        body = "\n".join(lines).encode("utf-8")
        file = discord.File(io.BytesIO(body), filename=f"transcript-{ctx.channel.name}.txt")
        view = _cv2(_local_msg(ctx, "transcript_built"))
        await ctx.send(view=view, file=file)

    # ───── in-ticket: close (lock) ────────────────

    @ticket.command(
        name="close",
        description="Soft-close this ticket (locks the channel).",
        help="{ 'en': 'Soft-close (lock) this ticket (in-ticket).', 'de': 'Dieses Ticket weich schließen / sperren (im Ticket).', 'es': 'Cierra suavemente (bloquea) este ticket (dentro del ticket).' }",
    )
    @commands.guild_only()
    async def ticket_close(self, ctx: commands.Context):
        ticket = is_ticket_channel(ctx)
        if not ticket:
            return await ctx.send(view=_cv2_text(ctx, "not_in_ticket"))
        cfg = get_ticket_config(ctx.guild.id)
        if not has_support_perms(ctx.author, cfg):
            return await ctx.send(view=_cv2_text(ctx, "no_perm_close"))

        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()

        opener = ctx.guild.get_member(ticket.get("opener_id", 0))

        # only flip the opener and any explicitly-added users to read-only
        ow = ctx.channel.overwrites
        for target, perms in list(ow.items()):
            if isinstance(target, (discord.Member, discord.User)) and target != ctx.guild.me:
                perms.send_messages = False
                ow[target] = perms
        try:
            await ctx.channel.edit(
                overwrites=ow,
                name=f"closed-{ctx.channel.name}"[:95],
                reason=f"Closed by {ctx.author}",
            )
        except Exception:
            pass

        ticket["status"] = "closed"
        update_ticket_config(ctx.guild.id, cfg)

        await ctx.send(view=_cv2_text(ctx, "closed", user=ctx.author.mention))

    # ───── in-ticket: delete ──────────────────────

    @ticket.command(
        name="delete",
        description="Delete this ticket channel.",
        help="{ 'en': 'Delete this ticket channel (in-ticket).', 'de': 'Diesen Ticket-Kanal löschen (im Ticket).', 'es': 'Elimina este canal de ticket (dentro del ticket).' }",
    )
    @commands.guild_only()
    async def ticket_delete(self, ctx: commands.Context, seconds: int = 5):
        ticket = is_ticket_channel(ctx)
        if not ticket:
            return await ctx.send(view=_cv2_text(ctx, "not_in_ticket"))
        cfg = get_ticket_config(ctx.guild.id)
        if not has_support_perms(ctx.author, cfg):
            return await ctx.send(view=_cv2_text(ctx, "no_perm_delete"))

        seconds = max(1, min(seconds, 30))
        await ctx.send(view=_cv2_text(ctx, "deleting", seconds=seconds))
        await asyncio.sleep(seconds)

        # remove from open tickets list
        cfg.open_tickets = [t for t in cfg.open_tickets if t.get("channel_id") != ctx.channel.id]
        update_ticket_config(ctx.guild.id, cfg)

        try:
            await ctx.channel.delete(reason=f"Ticket deleted by {ctx.author}")
        except Exception:
            pass

    # ───── helpers ────────────────────────────────

    async def _refresh_panel(self, guild: discord.Guild, cfg: TicketConfig):
        if not cfg.panel_message_id or not cfg.panel_channel_id:
            return
        ch = guild.get_channel(cfg.panel_channel_id)
        if not ch:
            return
        try:
            m = await ch.fetch_message(cfg.panel_message_id)
            await m.edit(view=TicketPanelView(guild.id, cfg))
        except Exception:
            pass


# helper: build a localised cv2 view from a key
def _cv2_text(ctx_or_int, key: str, **kwargs):
    return _cv2(_local_msg(ctx_or_int, key, **kwargs))


def _local_msg(ctx_or_int, key: str, **kwargs) -> str:
    return msg(ctx_or_int, key, **kwargs)


# ───────────────────────────────────────────────────
#  SETUP-PANEL VIEW (admin convenience)
# ───────────────────────────────────────────────────

class _ConfigurePanelBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author_id: int):
        super().__init__(label="Configure Panel", style=discord.ButtonStyle.primary)
        self.guild_id = guild_id
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This panel isn't yours to use.", ephemeral=True)
        await interaction.response.send_modal(TicketPanelModal(self.guild_id))


class _PostPanelBtn(discord.ui.Button):
    def __init__(self, guild_id: int, author_id: int):
        super().__init__(label="Post Panel Here", style=discord.ButtonStyle.success)
        self.guild_id = guild_id
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This panel isn't yours to use.", ephemeral=True)
        cfg = get_ticket_config(self.guild_id)
        view = TicketPanelView(self.guild_id, cfg)
        sent = await interaction.channel.send(view=view)
        cfg.panel_message_id = sent.id
        cfg.panel_channel_id = interaction.channel.id
        update_ticket_config(self.guild_id, cfg)
        await interaction.response.send_message(
            msg(interaction, "panel_posted", channel=interaction.channel.mention),
            ephemeral=True,
        )


class TicketSetupView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, author: discord.Member, lang: str = "en", personality: str = "cafe"):
        super().__init__(timeout=None)
        title = MESSAGES.get(personality, MESSAGES["normal"]).get(lang, {}).get("setup_title") \
                or MESSAGES["normal"]["en"]["setup_title"]
        desc = MESSAGES.get(personality, MESSAGES["normal"]).get(lang, {}).get("setup_desc") \
                or MESSAGES["normal"]["en"]["setup_desc"]
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=title.format(icon=get_emoji("icon_ticket"))),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=desc),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _ConfigurePanelBtn(guild_id, author.id),
                _PostPanelBtn(guild_id, author.id),
            ),
        )
        self.add_item(container)


# ───────────────────────────────────────────────────
#  COG SETUP
# ───────────────────────────────────────────────────

async def setup(bot):
    await bot.add_cog(Tickets(bot))

    # reattach persistent ticket panels
    for cfg in get_all_ticket_configs():
        if cfg.panel_message_id:
            bot.add_view(
                TicketPanelView(cfg.guild_id, cfg),
                message_id=cfg.panel_message_id,
            )
