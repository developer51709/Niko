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

The API is fully SFW and has no "kill" category, so the legacy hug/kill/kiss
set was replaced by the expanded action list below (each maps 1:1 to a
nekos.best category). Every request sends the required application
User-Agent header ``Niko (https://niko.sryze.cc)``.
"""

import aiohttp
import discord
from discord.ext import commands

from utils import logging as log
from utils.i18n import make_msg


# ─────────────────────────────────────────────────────────────────────────────
#  ACTION REGISTRY (order = prefix-command/select-option order)
# ─────────────────────────────────────────────────────────────────────────────

# meta fields per action:
#   emoji   — used in the title and the button label
#   playful — adds the shared "all in good fun" footer
#   label   — "do it back" button text per language (personality-neutral)
#   desc    — roleplay sentence per personality × language
#   help    — English help text for the prefix command
ACTIONS: dict = {
    "hug": {
        "emoji": "💖",
        "playful": False,
        "help": "Give someone a hug! 💖",
        "label": {"en": "Hug back", "de": "Umarm zurück", "es": "Abrazo de vuelta"},
        "desc": {
            "normal": {
                "en": "{author} hugged {target}! :hugging:",
                "de": "{author} hat {target} umarmt! :hugging:",
                "es": "¡{author} abrazó a {target}! :hugging:",
            },
            "cafe": {
                "en": "omg! {author} gave {target} a big, warm café hug! ☕💖",
                "de": "omg! {author} hat {target} eine große, warme Café-Umarmung gegeben! ☕💖",
                "es": "¡omg! {author} le dio a {target} un abrazo grande y calentito del café ☕💖",
            },
        },
    },
    "kiss": {
        "emoji": "💋",
        "playful": False,
        "help": "Give someone a kiss! 💋",
        "label": {"en": "Kiss back", "de": "Küss zurück", "es": "Beso de vuelta"},
        "desc": {
            "normal": {
                "en": "{author} kissed {target}! 💋",
                "de": "{author} hat {target} geküsst! 💋",
                "es": "¡{author} besó a {target}! 💋",
            },
            "cafe": {
                "en": "omg! {author} gave {target} a sweet café kiss! ☕️💋",
                "de": "omg! {author} hat {target} einen süßen Café-Kuss gegeben! ☕️💋",
                "es": "¡omg! {author} le dio a {target} un besito dulce del café ☕️💋",
            },
        },
    },
    "cuddle": {
        "emoji": "🤗",
        "playful": False,
        "help": "Cuddle with someone! 🤗",
        "label": {"en": "Cuddle back", "de": "Kuschel zurück", "es": "Acurruca de vuelta"},
        "desc": {
            "normal": {
                "en": "{author} cuddled {target}! 🤗",
                "de": "{author} hat {target} gekuschelt! 🤗",
                "es": "¡{author} acurrucó a {target}! 🤗",
            },
            "cafe": {
                "en": "aww! {author} snuggled up to {target} for a cozy café cuddle! ☕🤗",
                "de": "aww! {author} hat sich für ein kuscheliges Café-Knuddeln an {target} geschmiegt! ☕🤗",
                "es": "¡aww! {author} se acurrucó con {target} para un mimo bien acogedor del café ☕🤗",
            },
        },
    },
    "pat": {
        "emoji": "🫳",
        "playful": False,
        "help": "Give someone headpats! 🫳",
        "label": {"en": "Pat back", "de": "Pat zurück", "es": "Pat de vuelta"},
        "desc": {
            "normal": {
                "en": "{author} gave {target} headpats! ✨",
                "de": "{author} hat {target} den Kopf gestreichelt! ✨",
                "es": "¡{author} dio palmaditas a {target}! ✨",
            },
            "cafe": {
                "en": "{author} gave {target} the softest café headpats! ☕✨",
                "de": "{author} hat {target} die sanftesten Café-Headpats gegeben! ☕✨",
                "es": "{author} le dio a {target} las palmaditas más suaves del café ☕✨",
            },
        },
    },
    "poke": {
        "emoji": "🫵",
        "playful": False,
        "help": "Poke someone! 🫵",
        "label": {"en": "Poke back", "de": "Stups zurück", "es": "Poke de vuelta"},
        "desc": {
            "normal": {
                "en": "{author} poked {target}! 🫵",
                "de": "{author} hat {target} angestupst! 🫵",
                "es": "¡{author} le picó a {target}! 🫵",
            },
            "cafe": {
                "en": "hehe {author} poked {target} across the café counter! ☕🫵",
                "de": "hehe {author} hat {target} über die Café-Theke angestupst! ☕🫵",
                "es": "hehe {author} le picó a {target} desde la barra del café ☕🫵",
            },
        },
    },
    "tickle": {
        "emoji": "🤭",
        "playful": False,
        "help": "Tickle someone! 🤭",
        "label": {"en": "Tickle back", "de": "Kitzel zurück", "es": "Cosquillas de vuelta"},
        "desc": {
            "normal": {
                "en": "{author} tickled {target}! 😆",
                "de": "{author} hat {target} gekitzelt! 😆",
                "es": "¡{author} le hizo cosquillas a {target}! 😆",
            },
            "cafe": {
                "en": "omg {author} tickled {target} until they giggled! ☕😆",
                "de": "omg {author} hat {target} gekitzelt, bis sie kicherten! ☕😆",
                "es": "¡omg {author} le hizo cosquillas a {target} hasta hacerlo reír! ☕😆",
            },
        },
    },
    "highfive": {
        "emoji": "🙌",
        "playful": False,
        "help": "High-five someone! 🙌",
        "label": {"en": "High five back", "de": "High five zurück", "es": "Choca esos cinco"},
        "desc": {
            "normal": {
                "en": "{author} high-fived {target}! 🙌",
                "de": "{author} hat {target} ein High Five gegeben! 🙌",
                "es": "¡{author} chocó esos cinco con {target}! 🙌",
            },
            "cafe": {
                "en": "omg! {author} high-fived {target} — a very enthusiastic café high five! ☕🙌",
                "de": "omg! {author} hat {target} ein fröhliches Café-High-Five gegeben! ☕🙌",
                "es": "¡omg! {author} chocó esos cinco con {target}, ¡muy cafecito! ☕🙌",
            },
        },
    },
    "slap": {
        "emoji": "✋",
        "playful": True,
        "help": "Playfully slap someone! ✋",
        "label": {"en": "Slap back", "de": "Schlag zurück", "es": "Cachetada de vuelta"},
        "desc": {
            "normal": {
                "en": "{author} slapped {target}! ✋",
                "de": "{author} hat {target} eine geknallt! ✋",
                "es": "¡{author} abofeteó a {target}! ✋",
            },
            "cafe": {
                "en": "oh no! {author} playfully slapped {target}! ☕✋",
                "de": "oh nein! {author} hat {target} spielerisch eine geklebt! ☕✋",
                "es": "¡oh no! {author} le dio a {target} una cachetada en plan jugando ☕✋",
            },
        },
    },
    "bonk": {
        "emoji": "🔨",
        "playful": True,
        "help": "Bonk someone! 🔨",
        "label": {"en": "Bonk back", "de": "Bonk zurück", "es": "Bonk de vuelta"},
        "desc": {
            "normal": {
                "en": "{author} bonked {target}! 🔨",
                "de": "{author} hat {target} gebonkt! 🔨",
                "es": "¡{author} le dio un bonk a {target}! 🔨",
            },
            "cafe": {
                "en": "bonk! {author} bonked {target} over the café counter! ☕🔨",
                "de": "bonk! {author} hat {target} über die Café-Theke gebonkt! ☕🔨",
                "es": "¡bonk! {author} le dio un bonk a {target} sobre la barra del café ☕🔨",
            },
        },
    },
    "yeet": {
        "emoji": "🚀",
        "playful": True,
        "help": "Yeet someone! 🚀",
        "label": {"en": "Yeet back", "de": "Yeet zurück", "es": "Yeet de vuelta"},
        "desc": {
            "normal": {
                "en": "{author} yeeted {target}! 🚀",
                "de": "{author} hat {target} weggeyeeted! 🚀",
                "es": "¡{author} lanzó a {target} por los aires! 🚀",
            },
            "cafe": {
                "en": "{author} yeeted {target} right out of the café! ☕🚀",
                "de": "{author} hat {target} direkt aus dem Café geworfen! ☕🚀",
                "es": "{author} lanzó a {target} directito fuera del café ☕🚀",
            },
        },
    },
}

# Shared, personality-dependent strings (need-mention prompt, playful footer,
# GIF-fetch failure notice). Button labels + sentences live in ACTIONS above.
_BASE_STRINGS: dict = {
    "need_mention": {
        "normal": {
            "en": "You need to mention someone to use this command on them!",
            "de": "Du musst jemanden erwähnen, um diesen Befehl zu nutzen!",
            "es": "¡Tienes que mencionar a alguien para usar este comando!",
        },
        "cafe": {
            "en": "who are we doing this with? mention a friend! ☕✨",
            "de": "Mit wem machen wir das? Erwähne einen Freund! ☕✨",
            "es": "¿con quién hacemos esto? ¡menciona a un amix! ☕✨",
        },
    },
    "rp_footer": {
        "normal": {
            "en": "*all in good fun — no one actually got hurt!*",
            "de": "*alles nur Spaß — niemand wurde wirklich verletzt!*",
            "es": "*¡todo en broma — nadie salió herido de verdad!*",
        },
        "cafe": {
            "en": "*just café roleplay, no one actually got hurt ☕*",
            "de": "*nur café-roleplay, niemand wurde wirklich verletzt ☕*",
            "es": "*solo roleplay del café, nadie salió herido de verdad ☕*",
        },
    },
    "fetch_fail": {
        "normal": {
            "en": "The GIF fairy is on a break — try again in a moment! 🥺",
            "de": "Die GIF-Fee macht gerade Pause — versuch es gleich nochmal! 🥺",
            "es": "¡El hada de los GIFs está de descanso — inténtalo en un momento! 🥺",
        },
        "cafe": {
            "en": "the gif machine needs a coffee refill, try again in a sec! ☕🥺",
            "de": "die gif-maschine braucht einen kaffee-nachschub, versuch es gleich nochmal! ☕🥺",
            "es": "la máquina de gifs necesita más café, ¡inténtalo en un segundito! ☕🥺",
        },
    },
    "only_target": {
        "normal": {
            "en": "Only the person who was on the receiving end can do this one!",
            "de": "Nur die Person, an die sich die Aktion gerichtet hat, kann das tun!",
            "es": "¡Solo quien recibió la acción puede hacer esto!",
        },
        "cafe": {
            "en": "that move belongs to the one it was aimed at, cutie! ☕✨",
            "de": "das ist nur für die Person gedacht, an die es ging! ☕✨",
            "es": "¡ese movimiento es solo para quien lo recibió, amix! ☕✨",
        },
    },
    "expired": {
        "normal": {
            "en": "That roleplay moment has already ended. 💤",
            "de": "Dieser Roleplay-Moment ist schon vorbei. 💤",
            "es": "Ese momento de roleplay ya terminó. 💤",
        },
        "cafe": {
            "en": "that café moment already came and went! 💤☕",
            "de": "dieser café-moment ist schon vorbei! 💤☕",
            "es": "¡ese momento del café ya pasó! 💤☕",
        },
    },
    "cannot_self": {
        "normal": {
            "en": "You can't do that to yourself — right-click someone else!",
            "de": "Das kannst du nicht mit dir selbst machen — klicke jemand anderen an!",
            "es": "¡No puedes hacerte eso a ti mismo — haz clic en otra persona!",
        },
        "cafe": {
            "en": "self-love is great, but roleplay needs a second player ☕ pick a friend!",
            "de": "selbstliebe ist toll, aber roleplay braucht zwei ☕ nimm einen freund!",
            "es": "¡quererse está genial, pero el roleplay necesita a dos ☕ elige a un amix!",
        },
    },
    "pick_hint": {
        "normal": {
            "en": "What should happen to {target}? Pick an action — the card is posted in this channel.",
            "de": "Was soll mit {target} passieren? Wähle eine Aktion — die Karte erscheint in diesem Kanal.",
            "es": "¿Qué le hacemos a {target}? Elige una acción — la tarjeta se publica en este canal.",
        },
        "cafe": {
            "en": "what should {target} be on the receiving end of? ☕✨ pick one and the card shows up right here!",
            "de": "was soll {target} abbekommen? ☕✨ wähl eine aktion und die karte erscheint direkt hier!",
            "es": "¿qué le toca a {target}? ☕✨ elige una y la tarjeta aparece aquí mismo!",
        },
    },
}


def _build_messages() -> dict:
    """Build the personality→lang→key message dict from ACTIONS + _BASE_STRINGS."""
    messages: dict = {
        "normal": {"en": {}, "de": {}, "es": {}},
        "cafe": {"en": {}, "de": {}, "es": {}},
    }
    for personality in ("normal", "cafe"):
        for lang in ("en", "de", "es"):
            entry = messages[personality][lang]
            for base_key in ("need_mention", "rp_footer", "fetch_fail", "only_target", "expired", "cannot_self", "pick_hint"):
                entry[base_key] = _BASE_STRINGS[base_key][personality][lang]

    for action, meta in ACTIONS.items():
        for lang in ("en", "de", "es"):
            messages["normal"][lang][f"{action}_desc"] = meta["desc"]["normal"][lang]
            messages["normal"][lang][f"{action}_back"] = meta["label"][lang]
            messages["cafe"][lang][f"{action}_desc"] = meta["desc"]["cafe"][lang]
    return messages


msg = make_msg(_build_messages())


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


def _build_action_message(ctx_or_interaction, action: str, gif: str, actor, target) -> tuple:
    """Compose one action card: (title, desc, footer, ready-to-send LayoutView).

    Shared by the prefix commands and the context-menu action picker so both
    entry points produce byte-identical cards (GIF fetch happens first, then
    this pure compose step).
    """
    meta = ACTIONS[action]
    title = _action_title(action)
    desc = msg(ctx_or_interaction, f"{action}_desc", author=actor.mention, target=target.mention)
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
            description=meta["help"],
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
    """Factory for prefix commands — one per action, bound at class creation."""
    meta = ACTIONS[action]

    async def _run(self: "RolePlayCog", ctx: commands.Context, member: discord.Member = None):
        await self._do_roleplay(ctx, action, member)

    _run.__name__ = f"roleplay_{action}"
    _run.__doc__ = meta["help"]
    return commands.command(name=action, help=meta["help"])(_run)


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

    async def _reply_error(self, ctx_or_interaction, key: str):
        text = msg(ctx_or_interaction, key)
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
        back_desc = msg(
            interaction,
            f"{action}_desc",
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
