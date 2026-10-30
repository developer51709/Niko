"""
Custom message triggers — server admins can create keyword → response rules
managed via an interactive paginated cv2 LayoutView.

Usage: .triggers
"""

import traceback

import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils import logging as log
from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales
from utils.prefix_manager import dynamic_prefix

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "triggers")
msg = make_flat_msg(MESSAGES, {
    "danger": get_emoji("danger"),
    "cross": get_emoji("cross"),
    "message": get_emoji("message"),
    "plus": get_emoji("plus"),
})


def _fill(template: str, **values) -> str:
    """Replace ``{token}`` placeholders literally, for user-authored text.

    A trigger keyword or response is whatever the admin typed, so it may hold
    braces; ``str.format`` would raise on those.
    """
    for name, value in values.items():
        template = template.replace("{" + name + "}", str(value))
    return template


# ──────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _partial(emoji_name: str) -> discord.PartialEmoji:
    """Convert a get_emoji() string like <:name:id> into a PartialEmoji."""
    return discord.PartialEmoji.from_str(get_emoji(emoji_name))


VALID_MATCH_TYPES = ("contains", "exact", "startswith", "endswith")


def _fmt_exc(error: Exception) -> str:
    """Return the full traceback as a plain string so it survives ConsoleFormatter."""
    return "".join(traceback.format_exception(type(error), error, error.__traceback__))


def _error_container(exc: Exception, ctx) -> discord.ui.Container:
    """Build a cv2 error card."""
    text = _fill(
        msg(ctx, "error_card"),
        error=f"{type(exc).__name__}: {exc}",
    )
    return discord.ui.Container(discord.ui.TextDisplay(content=text))


async def _send_error(interaction: discord.Interaction, exc: Exception) -> None:
    """Respond to an interaction with an ephemeral error card."""
    view = discord.ui.LayoutView(timeout=60)
    view.add_item(_error_container(exc, interaction))
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.followup.send(view=view, ephemeral=True)
    except Exception:
        pass  # best-effort only


# ──────────────────────────────────────────────────────────────────────────────
#  MODALS
# ──────────────────────────────────────────────────────────────────────────────

def _match_options(ctx, selected: str = "contains") -> list[discord.SelectOption]:
    """The four match modes, labelled in the guild's language."""
    options = []
    for value in VALID_MATCH_TYPES:
        options.append(discord.SelectOption(
            label=msg(ctx, f"match_{value}"),
            value=value,
            description=msg(ctx, f"match_{value}_description"),
            default=(value == selected),
        ))
    return options


class _CreateTriggerModal(discord.ui.Modal):
    def __init__(self, view: "TriggersView"):
        ctx = view.ctx
        super().__init__(title=msg(ctx, "create_modal_title"))
        self._triggers_view = view
        self.trigger_input = discord.ui.TextInput(
            label=msg(ctx, "trigger_label"),
            placeholder=msg(ctx, "trigger_placeholder"),
            style=discord.TextStyle.short,
            max_length=200,
            required=True,
        )
        self.response_input = discord.ui.TextInput(
            label=msg(ctx, "response_label"),
            placeholder=msg(ctx, "response_placeholder"),
            style=discord.TextStyle.paragraph,
            max_length=2000,
            required=True,
        )
        self.add_item(self.trigger_input)
        self.add_item(self.response_input)
        self.match_type_select = discord.ui.Select(
            placeholder=msg(ctx, "match_placeholder"),
            min_values=1,
            max_values=1,
            required=True,
            options=_match_options(ctx),
        )
        label = discord.ui.Label(
            text=msg(ctx, "select_format_label"),
            component=self.match_type_select
        )
        self.add_item(label)

    async def on_submit(self, interaction: discord.Interaction):
        v = self._triggers_view
        mt = self.match_type_select.values[0] if self.match_type_select.values else "contains"
        log.debug("Triggers", f"CreateModal.on_submit — trigger={self.trigger_input.value!r}  mt={mt!r}")
        
        await interaction.response.defer()

        await v.bot.cxn.execute(
            "INSERT INTO triggers (guild_id, trigger, response, match_type, enabled) "
            "VALUES ($1, $2, $3, $4, 1)",
            v.guild_id,
            self.trigger_input.value.strip(),
            self.response_input.value.strip(),
            mt,
        )
        v.triggers = await v.bot.cxn.fetch(
            "SELECT * FROM triggers WHERE guild_id = $1 ORDER BY id",
            v.guild_id,
        )
        v.current_page = len(v.triggers) - 1
        v._build()
        await interaction.message.edit(
            view=v, allowed_mentions=discord.AllowedMentions.none()
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        tb = _fmt_exc(error)
        log.error("Triggers", f"CreateModal.on_error — {type(error).__name__}: {error}\n{tb}")
        await _send_error(interaction, error)


class _EditTriggerModal(discord.ui.Modal):
    def __init__(self, view: "TriggersView", row):
        ctx = view.ctx
        super().__init__(title=msg(ctx, "edit_modal_title"))
        self._triggers_view = view
        self._trigger_id = row["id"]
        self.trigger_input = discord.ui.TextInput(
            label=msg(ctx, "trigger_label"), max_length=200)
        self.response_input = discord.ui.TextInput(
            label=msg(ctx, "response_label"),
            style=discord.TextStyle.paragraph, max_length=2000)
        self.trigger_input.default = row["trigger"]
        self.response_input.default = row["response"]
        self.add_item(self.trigger_input)
        self.add_item(self.response_input)
        # Pre-select the current match type in the dropdown
        current_mt = row.get("match_type") or "contains"
        self.match_type_select = discord.ui.Select(
            placeholder=msg(ctx, "match_placeholder"),
            min_values=1,
            max_values=1,
            required=True,
            options=_match_options(ctx, current_mt),
        )
        label = discord.ui.Label(
            text=msg(ctx, "select_format_label"),
            component=self.match_type_select
        )
        self.add_item(label)

    async def on_submit(self, interaction: discord.Interaction):
        v = self._triggers_view
        mt = self.match_type_select.values[0] if self.match_type_select.values else "contains"
        log.debug("Triggers", f"EditModal.on_submit — id={self._trigger_id}  mt={mt!r}")

        await v.bot.cxn.execute(
            "UPDATE triggers SET trigger = $1, response = $2, match_type = $3 "
            "WHERE id = $4 AND guild_id = $5",
            self.trigger_input.value.strip(),
            self.response_input.value.strip(),
            mt,
            self._trigger_id,
            v.guild_id,
        )
        v.triggers = await v.bot.cxn.fetch(
            "SELECT * FROM triggers WHERE guild_id = $1 ORDER BY id",
            v.guild_id,
        )
        v._build()
        await interaction.response.edit_message(
            view=v, allowed_mentions=discord.AllowedMentions.none()
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        tb = _fmt_exc(error)
        log.error("Triggers", f"EditModal.on_error — {type(error).__name__}: {error}\n{tb}")
        await _send_error(interaction, error)


# ──────────────────────────────────────────────────────────────────────────────
#  BUTTONS
# ──────────────────────────────────────────────────────────────────────────────

def _permission_error_view(ctx) -> discord.ui.LayoutView:
    """The card every manage_guild gate answers with."""
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, "permission_heading")),
        discord.ui.TextDisplay(content=msg(ctx, "permission_denied")),
    ))
    return view


class _CreateButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(
            emoji=_partial("plus"),
            style=discord.ButtonStyle.success,
            custom_id="triggers:create",
        )
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        log.debug("Triggers", "_CreateButton.callback fired")
        v: TriggersView = self.view
        if v is None:
            log.error("Triggers", "_CreateButton.callback — self.view is None; button was not re-registered after rebuild")
            return
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                view=_permission_error_view(interaction), ephemeral=True
            )
        log.debug("Triggers", f"_CreateButton — opening modal for guild {v.guild_id}")
        await interaction.response.send_modal(_CreateTriggerModal(v))


class _EditButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(
            emoji=_partial("edit"),
            label=msg(ctx, "button_edit"),
            style=discord.ButtonStyle.secondary,
            custom_id="triggers:edit",
        )
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        log.debug("Triggers", "_EditButton.callback fired")
        v: TriggersView = self.view
        if v is None:
            log.error("Triggers", "_EditButton.callback — self.view is None")
            return
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                view=_permission_error_view(interaction), ephemeral=True
            )
        row = v.triggers[v.current_page]
        await interaction.response.send_modal(_EditTriggerModal(v, row))


class _ToggleButton(discord.ui.Button):
    def __init__(self, enabled: bool, ctx):
        super().__init__(
            label=msg(ctx, "button_disable" if enabled else "button_enable"),
            style=discord.ButtonStyle.danger if enabled else discord.ButtonStyle.success,
            custom_id="triggers:toggle",
        )
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        log.debug("Triggers", "_ToggleButton.callback fired")
        v: TriggersView = self.view
        if v is None:
            log.error("Triggers", "_ToggleButton.callback — self.view is None")
            return
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                view=_permission_error_view(interaction), ephemeral=True
            )
        row     = v.triggers[v.current_page]
        new_val = 0 if row["enabled"] else 1
        await v.bot.cxn.execute(
            "UPDATE triggers SET enabled = $1 WHERE id = $2 AND guild_id = $3",
            new_val, row["id"], v.guild_id,
        )
        v.triggers = await v.bot.cxn.fetch(
            "SELECT * FROM triggers WHERE guild_id = $1 ORDER BY id",
            v.guild_id,
        )
        v._build()
        await interaction.response.edit_message(
            view=v, allowed_mentions=discord.AllowedMentions.none()
        )


class _DeleteButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(
            emoji=_partial("trash"),
            label=msg(ctx, "button_delete"),
            style=discord.ButtonStyle.danger,
            custom_id="triggers:delete",
        )
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        log.debug("Triggers", "_DeleteButton.callback fired")
        v: TriggersView = self.view
        if v is None:
            log.error("Triggers", "_DeleteButton.callback — self.view is None")
            return
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                view=_permission_error_view(interaction), ephemeral=True
            )
        row = v.triggers[v.current_page]
        await v.bot.cxn.execute(
            "DELETE FROM triggers WHERE id = $1 AND guild_id = $2",
            row["id"], v.guild_id,
        )
        v.triggers = await v.bot.cxn.fetch(
            "SELECT * FROM triggers WHERE guild_id = $1 ORDER BY id",
            v.guild_id,
        )
        if v.current_page >= len(v.triggers) and v.current_page > 0:
            v.current_page -= 1
        v._build()
        await interaction.response.edit_message(
            view=v, allowed_mentions=discord.AllowedMentions.none()
        )


class _PrevButton(discord.ui.Button):
    def __init__(self, disabled: bool):
        super().__init__(
            label="◀",
            style=discord.ButtonStyle.secondary,
            disabled=disabled,
            custom_id="triggers:prev",
        )

    async def callback(self, interaction: discord.Interaction):
        v: TriggersView = self.view
        if v is None:
            return
        v.current_page -= 1
        v._build()
        await interaction.response.edit_message(
            view=v, allowed_mentions=discord.AllowedMentions.none()
        )


class _PageLabel(discord.ui.Button):
    def __init__(self, label: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            disabled=True,
            custom_id="triggers:page_label",
        )

    async def callback(self, interaction: discord.Interaction):
        pass


class _NextButton(discord.ui.Button):
    def __init__(self, disabled: bool):
        super().__init__(
            label="▶",
            style=discord.ButtonStyle.secondary,
            disabled=disabled,
            custom_id="triggers:next",
        )

    async def callback(self, interaction: discord.Interaction):
        v: TriggersView = self.view
        if v is None:
            return
        v.current_page += 1
        v._build()
        await interaction.response.edit_message(
            view=v, allowed_mentions=discord.AllowedMentions.none()
        )


# ──────────────────────────────────────────────────────────────────────────────
#  MAIN VIEW
# ──────────────────────────────────────────────────────────────────────────────

class TriggersView(discord.ui.LayoutView):
    """
    Interactive paginated cv2 panel for managing custom triggers.

    One trigger is shown per page.  Each trigger has its own ActionRow
    with Edit / Enable-Disable / Delete buttons.  The header Section
    carries a Create (➕) button as its accessory.
    """

    def __init__(self, *, bot, guild_id: int, triggers: list, ctx, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.bot      = bot
        self.guild_id = guild_id
        self.triggers = triggers
        self.ctx      = ctx
        self.current_page = 0
        self._build()

    # ── error handler ─────────────────────────────────────────────────────────

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item,
    ) -> None:
        tb = _fmt_exc(error)
        log.error(
            "Triggers",
            f"Unhandled error in {type(item).__name__} "
            f"(custom_id={getattr(item, 'custom_id', '?')!r}) — "
            f"{type(error).__name__}: {error}\n{tb}",
        )
        await _send_error(interaction, error)

    # ── layout ────────────────────────────────────────────────────────────────

    def _build(self):
        self.clear_items()
        total = len(self.triggers)

        log.debug("Triggers", f"TriggersView._build — total={total}  page={self.current_page}")

        # ── Header: title on the left, ➕ create button as Section accessory ──
        create_btn = _CreateButton(self.ctx)
        count_key = "panel_count_one" if total == 1 else "panel_count_other"
        header_container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=_fill(
                        msg(self.ctx, "panel_heading"),
                        count=msg(self.ctx, count_key, total=total),
                    )
                ),
                accessory=create_btn,
            )
        )
        self.add_item(header_container)

        # Verify the create button has a live view reference after being nested
        if create_btn._view is None:
            log.error("Triggers", "_build: create_btn._view is None after add_item — Section accessory _update_view chain broken")

        # ── Empty state ────────────────────────────────────────────────────────
        if total == 0:
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=msg(self.ctx, "empty_state")
                    )
                )
            )
            return

        # ── Current trigger card ───────────────────────────────────────────────
        row       = self.triggers[self.current_page]
        enabled   = bool(row["enabled"])
        status    = get_emoji("enabled") if enabled else get_emoji("disabled")
        match_lbl = msg(self.ctx, f"match_{row.get('match_type') or 'contains'}")

        response_preview = row["response"]
        if len(response_preview) > 200:
            response_preview = response_preview[:197] + "…"

        trigger_container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=_fill(
                    msg(self.ctx, "trigger_card"),
                    trigger=row["trigger"],
                    response=response_preview,
                    match=match_lbl,
                    status=status,
                )
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                _EditButton(self.ctx),
                _ToggleButton(enabled=enabled, ctx=self.ctx),
                _DeleteButton(self.ctx),
            ),
        )
        self.add_item(trigger_container)

        # ── Navigation footer ─────────────────────────────────────────────────
        footer_items: list = [
            discord.ui.TextDisplay(content=_fill(
                msg(self.ctx, "footer_page"),
                page=self.current_page + 1,
                total=total,
            )),
        ]
        if total > 1:
            footer_items.append(
                discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small)
            )
            footer_items.append(
                discord.ui.ActionRow(
                    _PrevButton(disabled=self.current_page == 0),
                    _PageLabel(label=f"{self.current_page + 1} / {total}"),
                    _NextButton(disabled=self.current_page == total - 1),
                )
            )

        self.add_item(discord.ui.Container(*footer_items))


# ──────────────────────────────────────────────────────────────────────────────
#  COG
# ──────────────────────────────────────────────────────────────────────────────

class TriggersCog(commands.Cog, name="Triggers"):
    def __init__(self, bot):
        self.bot = bot

    # ── Management command ────────────────────────────────────────────────────

    @commands.command(name="triggers", help=CMDS.help("triggers"))
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def triggers_panel(self, ctx: commands.Context):
        log.debug("Triggers", f"triggers_panel invoked by {ctx.author} in guild {ctx.guild.id}")
        try:
            rows = await self.bot.cxn.fetch(
                "SELECT * FROM triggers WHERE guild_id = $1 ORDER BY id",
                ctx.guild.id,
            )
            view = TriggersView(
                bot=self.bot,
                guild_id=ctx.guild.id,
                triggers=list(rows),
                ctx=ctx,
            )
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())
            log.debug("Triggers", f"Panel sent — {len(rows)} triggers for guild {ctx.guild.id}")
        except Exception as exc:
            tb = _fmt_exc(exc)
            log.error("Triggers", f"triggers_panel command failed — {type(exc).__name__}: {exc}\n{tb}")
            await ctx.send(
                _fill(msg(ctx, "panel_failed"), error=exc),
                allowed_mentions=discord.AllowedMentions.none(),
            )

    # ── Runtime listener ──────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if not message.content:
            return

        # Don't fire on bot prefix commands
        prefixes = await dynamic_prefix(self.bot, message)
        if any(message.content.startswith(p) for p in prefixes):
            return

        try:
            rows = await self.bot.cxn.fetch(
                "SELECT * FROM triggers WHERE guild_id = $1 AND enabled = 1",
                message.guild.id,
            )
        except Exception as exc:
            log.error("Triggers", f"on_message DB fetch failed: {exc}")
            return

        if not rows:
            return

        content = message.content.lower()
        for t in rows:
            keyword    = t["trigger"].lower()
            match_type = (t.get("match_type") or "contains").lower()

            if match_type == "exact":
                matched = content == keyword
            elif match_type == "startswith":
                matched = content.startswith(keyword)
            elif match_type == "endswith":
                matched = content.endswith(keyword)
            else:
                matched = keyword in content

            if matched:
                try:
                    await message.channel.send(
                        t["response"],
                        allowed_mentions=discord.AllowedMentions.none(),
                    )
                except Exception as exc:
                    log.error("Triggers", f"Failed to send trigger response: {exc}")
                break


async def setup(bot):
    await bot.add_cog(TriggersCog(bot))
