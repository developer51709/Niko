"""
Roleplay cog — anime reaction GIFs from the nekos.best API.

Every action fetches a random SFW GIF from ``https://nekos.best/api/v2/<action>``
and renders it in a CV2 layout message:

    ### <emoji> <action>
    ─────────────────
    <desc>            (author did X to target)
    <gif>
    [💖 Hug back]     ← ActionRow at the bottom of the container

Right-clicking a user exposes a **single** ``Roleplay`` user context command:
Discord caps global user commands at 15 per app, so one menu per action would
blow the quota. The menu opens an *ephemeral* CV2 container with a select menu
of every action; picking one posts that action's card in the channel (the
ephemeral picker then disappears).

The "do it back" button:

  * is only usable by the **target** user,
  * **persists across restarts** — click handling is a cog listener that
    resolves per-message state from the ``roleplay_actions`` table (no view
    store to lose), so old messages keep working after a redeploy,
  * **disables itself after first use** by rebuilding the original layout
    (same title/desc/GIF) with the button set to ``disabled=True``, and
  * sends a **new** roleplay message without a button as the "back" action.

``rpblock`` / ``rpunblock`` manage a per-user block list: blocking someone
refuses every roleplay path that targets you — prefix commands, the context-
menu action picker, and "do it back" buttons (the ``roleplay_blocks`` table,
resolved by (blocker, blocked) pairs).

The API is fully SFW and has no "kill" category, so the legacy hug/kill/kiss
set was replaced by the expanded action list below (each maps 1:1 to a
nekos.best category). Every request sends the required application
User-Agent header ``Niko (https://niko.sryze.cc)``.
"""

import random

import aiohttp
import discord
from discord.ext import commands

from utils import logging as log
from utils.i18n import get_lang, make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)


# ─────────────────────────────────────────────────────────────────────────────
#  ACTION REGISTRY (order = prefix-command/select-option order)
# ─────────────────────────────────────────────────────────────────────────────

# meta fields per action:
#   emoji   — used in the title and the button label
#   playful — adds the shared "all in good fun" footer
#   (help text lives in locales/commands under "<action>.help")
#
# Everything translated lives in ``locales/`` instead: "<action>_back" is the
# "do it back" button label and "<action>_desc" the list of sentence variants
# picked at random per message, both under the ``roleplay_actions`` namespace.
ACTIONS: dict = {
    "hug": {
        "emoji": "💖",
        "playful": False,
    },
    "kiss": {
        "emoji": "💋",
        "playful": False,
    },
    "cuddle": {
        "emoji": "🤗",
        "playful": False,
    },
    "pat": {
        "emoji": "🫳",
        "playful": False,
    },
    "poke": {
        "emoji": "🫵",
        "playful": False,
    },
    "tickle": {
        "emoji": "🤭",
        "playful": False,
    },
    "highfive": {
        "emoji": "🙌",
        "playful": False,
    },
    "slap": {
        "emoji": "✋",
        "playful": True,
    },
    "bonk": {
        "emoji": "🔨",
        "playful": True,
    },
    "yeet": {
        "emoji": "🚀",
        "playful": True,
        },
}

# Shared strings (need-mention prompt, playful footer, GIF-fetch failure
# notice). Button labels + sentences live in ACTIONS above.
_STRINGS = load_locales(__package__, "roleplay_strings")
_ACTION_TEXTS = load_locales(__package__, "roleplay_actions")


def _build_messages() -> dict:
    """Build the lang→key message dict from the catalogue + action labels."""
    messages: dict = {}
    for lang, translations in _STRINGS.items():
        entry = dict(translations)
        for key, text in _ACTION_TEXTS[lang].items():
            if key.endswith("_back"):
                entry[key] = text
        messages[lang] = entry
    return messages


msg = make_flat_msg(_build_messages())


# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────────────────

NEKOS_API = "https://nekos.best/api/v2"
NEKOS_UA = "Niko (https://niko.sryze.cc)"  # required application User-Agent
NEKOS_TIMEOUT = 10
FETCH_RETRIES = 2

BACK_PREFIX = "roleplay_back:"  # custom_id prefix for the "do it back" buttons
PICK_PREFIX = "roleplay_pick:"  # custom_id prefix for the action-picker selects


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_nekos_gif(action: str) -> str | None:
    """Fetch one random GIF url from the nekos.best API (or None on failure)."""
    meta = ACTIONS.get(action)
    category = meta.get("category", action) if meta else action
    url = f"{NEKOS_API}/{category}"
    headers = {"User-Agent": NEKOS_UA}
    timeout = aiohttp.ClientTimeout(total=NEKOS_TIMEOUT)

    for attempt in range(FETCH_RETRIES):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=timeout) as resp:
                    if resp.status != 200:
                        log.warning("RolePlay", f"nekos.best {category} → HTTP {resp.status} (attempt {attempt + 1})")
                        continue
                    data = await resp.json()
            results = (data or {}).get("results") or []
            if results and results[0].get("url"):
                return results[0]["url"]
        except Exception as exc:
            log.warning("RolePlay", f"nekos.best {category} fetch failed (attempt {attempt + 1}): {exc}")
    return None


class _RoleplayLayoutView(discord.ui.LayoutView):
    """LayoutView that bypasses discord.py's in-memory per-message view store.

    discord.py registers every dispatchable view against the message it was
    sent on and would then try to invoke a *button callback* when it is
    clicked. These buttons deliberately have no callback — every click is
    resolved from the ``roleplay_actions`` table by the cog's
    ``on_interaction`` listener, which is what lets them keep working after a
    restart (there is no view store to lose). Reporting "not dispatchable"
    keeps the layout out of the per-message store so each click reaches the
    listener exactly once, instead of also tripping a callback-less dispatch
    on messages sent earlier in the same process.
    """

    def is_dispatchable(self) -> bool:
        return False


def build_roleplay_view(
    *,
    title: str,
    desc: str,
    gif: str,
    footer: str | None = None,
    back_action: str | None = None,
    back_label: str | None = None,
    disabled: bool = False,
    emoji: str | None = None,
) -> discord.ui.LayoutView:
    """Build the CV2 roleplay layout.

    The ActionRow with the "do it back" button sits at the *bottom of the
    container*, after the text/media/footer content. ``disabled`` rebuilds the
    exact same layout (so the GIF is preserved) with the button greyed out.
    """
    items: list = [
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=desc),
        discord.ui.MediaGallery(discord.MediaGalleryItem(media=gif)),
    ]
    if footer:
        items.append(discord.ui.TextDisplay(content=f"-# {footer}"))

    if back_action:
        label = back_label or back_action
        if emoji and not label.startswith(emoji):
            label = f"{emoji} {label}"
        button = discord.ui.Button(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"{BACK_PREFIX}{back_action}",
            disabled=disabled,
        )
        items.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        items.append(discord.ui.ActionRow(button))

    view = _RoleplayLayoutView()
    view.add_item(discord.ui.Container(*items))
    return view


def _mention(user_id: int) -> str:
    return f"<@{int(user_id)}>"


def _action_title(action: str) -> str:
    meta = ACTIONS[action]
    return f"{meta['emoji']} {action}"


def _pick_desc(ctx, action: str, *, author: str, target: str) -> str:
    """Pick a random sentence variant for ``action`` in the guild's language.

    Falls back to English, then to a bare generated sentence. The variant is
    chosen AFTER the fallback so every language keeps its full variety.
    """
    lang = get_lang(ctx) if ctx else "en"
    variants = (
        _ACTION_TEXTS.get(lang, {}).get(f"{action}_desc")
        or _ACTION_TEXTS["en"].get(f"{action}_desc")
        or [f"{author} {action}ed {target}!"]
    )
    return random.choice(variants).format(author=author, target=target)


def _build_action_message(ctx_or_interaction, action: str, gif: str, actor, target) -> tuple:
    """Compose one action card: (title, desc, footer, ready-to-send LayoutView).

    Shared by the prefix commands and the context-menu action picker so both
    entry points produce byte-identical cards (GIF fetch happens first, then
    this pure compose step).
    """
    meta = ACTIONS[action]
    title = _action_title(action)
    desc = _pick_desc(ctx_or_interaction, action, author=actor.mention, target=target.mention)
    footer = msg(ctx_or_interaction, "rp_footer") if meta.get("playful") else None
    view = build_roleplay_view(
        title=title,
        desc=desc,
        gif=gif,
        footer=footer,
        back_action=action,
        back_label=msg(ctx_or_interaction, f"{action}_back"),
        emoji=meta["emoji"],
    )
    return title, desc, footer, view


def build_picker_view(*, target_id: int, hint: str) -> discord.ui.LayoutView:
    """Build the ephemeral CV2 action picker behind the ``Roleplay`` menu.

    A single select lists every action (in ``ACTIONS`` insertion order). The
    target's user id rides in the select's custom id so the follow-up select
    interaction can be resolved with zero stored view state — the same model
    as the back buttons.
    """
    select = discord.ui.Select(
        custom_id=f"{PICK_PREFIX}{int(target_id)}",
        placeholder="🎭 Pick a roleplay action…",
        min_values=1,
        max_values=1,
    )
    for action, meta in ACTIONS.items():
        select.add_option(
            label=f"{meta['emoji']} {action.title()}",
            value=action,
            description=CMDS.text(f"{action}.help"),
        )

    view = _RoleplayLayoutView()
    view.add_item(
        discord.ui.Container(
            discord.ui.TextDisplay(content="### 🎭 Roleplay"),
            discord.ui.TextDisplay(content=hint),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(select),
        )
    )
    return view


# ─────────────────────────────────────────────────────────────────────────────
#  COG
# ─────────────────────────────────────────────────────────────────────────────

def _make_roleplay_command(action: str):
    """Factory for prefix commands — one per action, assigned in the class body.

    discord.py decides which signature parameters belong to the caller by
    checking ``is_inside_class(callback)``: a class method's ``__qualname__``
    makes it skip both ``self`` and ``ctx``. A function defined inside this
    factory would normally have ``<locals>`` in its qualname, so discord.py
    would treat ``ctx`` as the first user argument — the bug where every
    roleplay command demanded a "ctx" member. Overriding ``__qualname__`` to
    a class-like path fixes the signature parsing while keeping the factory.
    At invocation discord.py passes ``(cog, ctx, *args)`` itself, so the
    callback stays a plain unbound function taking ``(self, ctx, member)``.
    """
    meta = ACTIONS[action]

    async def roleplay_action(self, ctx: commands.Context, member: discord.Member = None):
        await self._do_roleplay(ctx, action, member)

    roleplay_action.__name__ = f"roleplay_{action}"
    roleplay_action.__qualname__ = f"RolePlayCog.roleplay_{action}"
    return commands.command(name=action, help=CMDS.help(action))(roleplay_action)


class RolePlayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Single user context menu — Discord allows only 15 global user
        # commands, so every roleplay action lives behind one "Roleplay" entry
        # that opens an ephemeral action-picker select.
        self._context_menu = discord.app_commands.ContextMenu(
            name="Roleplay",
            callback=self._roleplay_picker,
        )
        bot.tree.add_command(self._context_menu)

    async def cog_unload(self) -> None:
        """Remove the user context menu from the tree on cog unload.

        Tree commands added manually in ``__init__`` are not cleaned up by
        discord.py, so without this ``!devreload fun`` would fail on
        ``CommandAlreadyRegistered`` when the cog re-registers it.
        """
        try:
            self.bot.tree.remove_command(self._context_menu.name, type=self._context_menu.type)
        except Exception:
            pass

    # ── expanded action commands (prefix) ──────────────────────────────────
    hug = _make_roleplay_command("hug")
    kiss = _make_roleplay_command("kiss")
    cuddle = _make_roleplay_command("cuddle")
    pat = _make_roleplay_command("pat")
    poke = _make_roleplay_command("poke")
    tickle = _make_roleplay_command("tickle")
    highfive = _make_roleplay_command("highfive")
    slap = _make_roleplay_command("slap")
    bonk = _make_roleplay_command("bonk")
    yeet = _make_roleplay_command("yeet")

    # ── block / unblock (prefix) ────────────────────────────────────────────
    @commands.command(
        name="rpblock",
        help=CMDS.help("rpblock"),
    )
    async def rpblock(self, ctx: commands.Context, member: discord.Member = None):
        """Stop a member from using roleplay commands on you."""
        target = await self._resolve_block_target(ctx, member)
        if target is None:
            return
        if await self._is_blocked(ctx.author.id, target.id):
            return await ctx.send(content=msg(ctx, "already_blocked", target=target.mention))
        if not await self._add_block(ctx.author.id, target.id):
            return await ctx.send(content=msg(ctx, "db_fail"))
        await ctx.send(content=msg(ctx, "block_success", target=target.mention))

    @commands.command(
        name="rpunblock",
        help=CMDS.help("rpunblock"),
    )
    async def rpunblock(self, ctx: commands.Context, member: discord.Member = None):
        """Remove your roleplay block on a member."""
        target = await self._resolve_block_target(ctx, member)
        if target is None:
            return
        if not await self._is_blocked(ctx.author.id, target.id):
            return await ctx.send(content=msg(ctx, "not_blocked", target=target.mention))
        if not await self._remove_block(ctx.author.id, target.id):
            return await ctx.send(content=msg(ctx, "db_fail"))
        await ctx.send(content=msg(ctx, "unblock_success", target=target.mention))

    async def _resolve_block_target(self, ctx, member: discord.Member | None):
        """Resolve the member argument for rpblock/rpunblock, or None on error."""
        if member is None:
            await self._reply_error(ctx, "need_mention")
            return None
        if member.id == ctx.author.id:
            await self._reply_error(ctx, "cannot_block_self")
            return None
        return member

    # ────────────────────────────────────────────────────────────────────────
    #  CONTEXT MENU → ACTION PICKER
    # ────────────────────────────────────────────────────────────────────────
    async def _roleplay_picker(self, interaction: discord.Interaction, member: discord.Member):
        """Callback of the single ``Roleplay`` user context command.

        Opens an ephemeral select menu listing every action for ``member``.
        """
        if member.id == interaction.user.id:
            try:
                await interaction.response.send_message(content=msg(interaction, "cannot_self"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        if await self._is_blocked(member.id, interaction.user.id):
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "blocked", target=member.mention),
                    ephemeral=True,
                )
            except discord.HTTPException:
                pass
            return

        view = build_picker_view(
            target_id=member.id,
            hint=msg(interaction, "pick_hint", target=member.mention),
        )
        try:
            await interaction.response.send_message(view=view, ephemeral=True)
        except discord.HTTPException as exc:
            log.error("RolePlay", f"Could not open the roleplay picker: {exc}")

    async def _handle_pick(self, interaction: discord.Interaction, custom_id: str):
        """Resolve an action-picker select into a real roleplay card.

        The picker is ephemeral, so the select interaction carries everything
        needed: the chosen action in ``values`` and the target user id inside
        the custom id. The card is posted to the channel as a normal (public)
        follow-up and the ephemeral picker is then dismissed.
        """
        try:
            target_id = int(custom_id[len(PICK_PREFIX):])
        except ValueError:
            target_id = 0

        values = (interaction.data or {}).get("values") or []
        action = str(values[0]) if values else ""
        if action not in ACTIONS or not target_id:
            try:
                await interaction.response.send_message(content=msg(interaction, "expired"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        guild = interaction.guild
        member = guild.get_member(target_id) if guild is not None else None
        if member is None and guild is not None:
            try:
                member = await guild.fetch_member(target_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                member = None
        if member is None:
            try:
                await interaction.response.send_message(content=msg(interaction, "expired"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        if member.id == interaction.user.id:
            try:
                await interaction.response.send_message(content=msg(interaction, "cannot_self"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        if await self._is_blocked(member.id, interaction.user.id):
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "blocked", target=member.mention),
                    ephemeral=True,
                )
            except discord.HTTPException:
                pass
            return

        # Ack first — fetching the GIF can take a moment.
        try:
            await interaction.response.defer()
        except discord.HTTPException:
            return

        gif = await fetch_nekos_gif(action)
        if not gif:
            try:
                await interaction.followup.send(content=msg(interaction, "fetch_fail"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        title, desc, footer, view = _build_action_message(interaction, action, gif, interaction.user, member)
        try:
            message = await interaction.followup.send(view=view)
        except discord.HTTPException as exc:
            log.error("RolePlay", f"Could not send {action} card: {exc}")
            try:
                await interaction.followup.send(content=msg(interaction, "fetch_fail"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        await self._store_action(
            message_id=message.id,
            channel_id=interaction.channel_id,
            guild_id=guild.id if guild is not None else None,
            action=action,
            actor_id=interaction.user.id,
            target_id=member.id,
            gif=gif,
            title=title,
            desc=desc,
            footer=footer,
        )

        # Done — dismiss the ephemeral picker.
        try:
            await interaction.delete_original_response()
        except discord.HTTPException:
            pass

    # ────────────────────────────────────────────────────────────────────────
    #  SHARED ROLEPLAY FLOW (prefix commands + context action picker)
    # ────────────────────────────────────────────────────────────────────────
    async def _do_roleplay(self, ctx_or_interaction, action: str, member: discord.Member | None):
        if isinstance(ctx_or_interaction, discord.Interaction):
            actor = ctx_or_interaction.user
        else:
            actor = ctx_or_interaction.author

        if member is None or member.id == actor.id:
            return await self._reply_error(ctx_or_interaction, "need_mention")

        # The target may have blocked the actor from roleplaying on them.
        if await self._is_blocked(member.id, actor.id):
            return await self._reply_error(ctx_or_interaction, "blocked", target=member.mention)

        # 1) Fetch the GIF
        gif = await fetch_nekos_gif(action)
        if not gif:
            return await self._reply_error(ctx_or_interaction, "fetch_fail")

        # 2) Compose the layout
        title, desc, footer, view = _build_action_message(ctx_or_interaction, action, gif, actor, member)

        # 3) Send
        try:
            if isinstance(ctx_or_interaction, discord.Interaction):
                await ctx_or_interaction.response.send_message(view=view)
                message = await ctx_or_interaction.original_response()
            else:
                message = await ctx_or_interaction.send(view=view)
        except discord.HTTPException as exc:
            log.error("RolePlay", f"Could not send {action} message: {exc}")
            return await self._reply_error(ctx_or_interaction, "fetch_fail")

        # 4) Persist the interaction state so the button works across restarts
        await self._store_action(
            message_id=message.id,
            channel_id=message.channel.id,
            guild_id=getattr(message.guild, "id", None),
            action=action,
            actor_id=actor.id,
            target_id=member.id,
            gif=gif,
            title=title,
            desc=desc,
            footer=footer,
        )

    async def _store_action(self, **fields):
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            log.warning("RolePlay", "No database connection — roleplay back-button state not stored")
            return
        try:
            await cxn.execute(
                "INSERT INTO roleplay_actions "
                "(message_id, guild_id, channel_id, action, actor_id, target_id, gif, title, desc, footer) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
                fields["message_id"],
                fields.get("guild_id"),
                fields["channel_id"],
                fields["action"],
                fields["actor_id"],
                fields["target_id"],
                fields["gif"],
                fields["title"],
                fields["desc"],
                fields.get("footer"),
            )
        except Exception as exc:
            log.warning("RolePlay", f"Could not store roleplay action for {fields.get('message_id')}: {exc}")

    # ────────────────────────────────────────────────────────────────────────
    #  ROLEPLAY BLOCKS ("don't let X use roleplay commands on me")
    # ────────────────────────────────────────────────────────────────────────
    async def _is_blocked(self, blocker_id: int, blocked_id: int) -> bool:
        """True if ``blocker_id`` has blocked ``blocked_id`` from roleplaying on them."""
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            return False
        try:
            row = await cxn.fetchrow(
                "SELECT 1 FROM roleplay_blocks "
                "WHERE blocker_id = $1 AND blocked_id = $2",
                int(blocker_id),
                int(blocked_id),
            )
            return row is not None
        except Exception as exc:
            log.warning("RolePlay", f"roleplay block lookup failed: {exc}")
            return False

    async def _add_block(self, blocker_id: int, blocked_id: int) -> bool:
        """Persist a block; returns False when the database is unavailable."""
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            return False
        try:
            await cxn.execute(
                "INSERT OR IGNORE INTO roleplay_blocks (blocker_id, blocked_id) "
                "VALUES ($1, $2)",
                int(blocker_id),
                int(blocked_id),
            )
            return True
        except Exception as exc:
            log.warning("RolePlay", f"Could not store roleplay block: {exc}")
            return False

    async def _remove_block(self, blocker_id: int, blocked_id: int) -> bool:
        """Delete a block; returns False when the database is unavailable."""
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            return False
        try:
            await cxn.execute(
                "DELETE FROM roleplay_blocks "
                "WHERE blocker_id = $1 AND blocked_id = $2",
                int(blocker_id),
                int(blocked_id),
            )
            return True
        except Exception as exc:
            log.warning("RolePlay", f"Could not remove roleplay block: {exc}")
            return False

    async def _reply_error(self, ctx_or_interaction, key: str, **kwargs):
        text = msg(ctx_or_interaction, key, **kwargs)
        if isinstance(ctx_or_interaction, discord.Interaction):
            try:
                await ctx_or_interaction.response.send_message(content=text, ephemeral=True)
            except discord.HTTPException:
                await ctx_or_interaction.followup.send(content=text, ephemeral=True)
        else:
            await ctx_or_interaction.send(content=text)

    # ────────────────────────────────────────────────────────────────────────
    #  PERSISTENT "DO IT BACK" BUTTON
    # ────────────────────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle roleplay component interactions without stored view state.

        discord.py dispatches ``on_interaction`` for every component click, so
        both the action-picker selects and the per-message back-buttons work
        with no view store to lose across restarts: the picker custom id
        carries the target, the back-button message id resolves the stored
        action state from the DB.
        """
        if interaction.type is not discord.InteractionType.component:
            return
        custom_id = (interaction.data or {}).get("custom_id") or ""
        if custom_id.startswith(PICK_PREFIX):
            return await self._handle_pick(interaction, custom_id)
        if not custom_id.startswith(BACK_PREFIX):
            return
        action = custom_id[len(BACK_PREFIX):]
        if action not in ACTIONS:
            return
        await self._handle_back(interaction, action)

    async def _handle_back(self, interaction: discord.Interaction, action: str):
        meta = ACTIONS[action]
        cxn = getattr(self.bot, "cxn", None)
        message = interaction.message

        if cxn is None or message is None:
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "expired"), ephemeral=True
                )
            except discord.HTTPException:
                pass
            return

        # Resolve the original action from persistent state
        try:
            row = await cxn.fetchrow(
                "SELECT message_id, guild_id, channel_id, action, actor_id, target_id, "
                "gif, title, desc, footer, used "
                "FROM roleplay_actions WHERE message_id = $1",
                message.id,
            )
        except Exception as exc:
            log.error("RolePlay", f"roleplay back lookup failed for {message.id}: {exc}")
            row = None

        if row is None or row.get("used"):
            try:
                await interaction.response.send_message(content=msg(interaction, "expired"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        # Only the target user may do the action back
        if interaction.user.id != int(row["target_id"]):
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "only_target"), ephemeral=True
                )
            except discord.HTTPException:
                pass
            return

        # The original actor may have blocked the target in the meantime — the
        # "back" action is aimed at them, so it is refused too.
        if await self._is_blocked(row["actor_id"], row["target_id"]):
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "blocked", target=_mention(row["actor_id"])),
                    ephemeral=True,
                )
            except discord.HTTPException:
                pass
            return

        # Acknowledge so we have time for the GIF fetch + message edits
        try:
            await interaction.response.defer()
        except discord.HTTPException:
            return

        # Claim the action first so double-clicks / restarts can't replay it
        try:
            await cxn.execute(
                "UPDATE roleplay_actions SET used = 1 WHERE message_id = $1", message.id
            )
        except Exception as exc:
            log.warning("RolePlay", f"Could not mark {message.id} as used: {exc}")

        # 1) The back action message — target does the action back to the author,
        #    fetched fresh from nekos.best. No button on this message.
        new_gif = await fetch_nekos_gif(action) or row["gif"]
        back_desc = _pick_desc(
            interaction,
            action,
            author=_mention(row["target_id"]),
            target=_mention(row["actor_id"]),
        )
        back_footer = msg(interaction, "rp_footer") if meta.get("playful") else None
        back_view = build_roleplay_view(
            title=row["title"] or _action_title(action),
            desc=back_desc,
            gif=new_gif,
            footer=back_footer,
        )
        try:
            await interaction.followup.send(view=back_view)
        except discord.HTTPException as exc:
            log.warning("RolePlay", f"Could not send {action} back message: {exc}")

        # 2) Disable the button on the original message — rebuild the exact same
        #    layout (preserving the GIF) with the button disabled.
        try:
            disabled_view = build_roleplay_view(
                title=row["title"] or _action_title(action),
                desc=row["desc"],
                gif=row["gif"],
                footer=row.get("footer"),
                back_action=action,
                back_label=msg(interaction, f"{action}_back"),
                emoji=meta["emoji"],
                disabled=True,
            )
            await message.edit(view=disabled_view)
        except discord.NotFound:
            pass
        except discord.HTTPException as exc:
            log.warning("RolePlay", f"Could not disable button on {message.id}: {exc}")


async def setup(bot):
    await bot.add_cog(RolePlayCog(bot))
