# ============================
#  IMPORTS
# ============================

import discord
from discord.ext import commands
import asyncio
import json
import os
import random
import time

from config.emojis import get_emoji
from utils.cooldown import cooldown_ready_at, cooldown_view
from utils.paginator import PaginatedView, paginate
from utils.prefix_manager import resolve_prefix
from utils.image.blackjack import render_table
from utils.image.economy_card import ACCENT_BRIGHT, DANGER, SAGE

from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "messages")
msg = make_flat_msg(MESSAGES)

SHOE_FILE   = "blackjack_shoe.json"
IMAGE_NAME  = "blackjack.png"

ACCENT_GREEN = discord.Colour(0x57F287)
ACCENT_RED   = discord.Colour(0xED4245)
# The brand accent every other Niko view uses, not a casino-only yellow.
ACCENT_BRAND = discord.Colour(0xC8A882)
ACCENT_BLUE  = discord.Colour(0x5865F2)

# Table text follows the website theme, so the rendered table matches the rest
# of Niko's cards (sage for wins, a muted red for losses).
STATUS_NEUTRAL = ACCENT_BRIGHT
STATUS_WIN     = SAGE
STATUS_LOSS    = DANGER


# ============================
#  PREFIX RESOLVER
# ============================

async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await resolve_prefix(bot, ctx_or_interaction)


# ============================
#  SHOE MANAGER (PERSISTENT)
# ============================

class Shoe:
    def __init__(self, decks=6):
        self.decks = decks
        self.cards = []
        self.load_or_create_shoe()

    def load_or_create_shoe(self):
        if os.path.exists(SHOE_FILE):
            try:
                with open(SHOE_FILE, "r") as f:
                    data = json.load(f)
                    self.cards = data.get("cards", [])
                    if len(self.cards) > 0:
                        return
            except Exception:
                pass
        self.reset_shoe()

    def reset_shoe(self):
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        suits = ["S", "H", "D", "C"]
        self.cards = []
        for _ in range(self.decks):
            for suit in suits:
                for rank in ranks:
                    self.cards.append(f"{rank}{suit}")
        random.shuffle(self.cards)
        self.save_shoe()

    def save_shoe(self):
        with open(SHOE_FILE, "w") as f:
            json.dump({"cards": self.cards}, f, indent=4)

    def draw(self):
        if len(self.cards) < 20:
            self.reset_shoe()
        card = self.cards.pop()
        self.save_shoe()
        return card


# ============================
#  CARD UTILITIES
# ============================

def hand_value(cards):
    value = 0
    aces = 0
    for card in cards:
        rank = card[:-1]
        if rank.isdigit():
            value += int(rank)
        elif rank in ("J", "Q", "K"):
            value += 10
        else:
            value += 11
            aces += 1
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def is_blackjack(cards):
    return len(cards) == 2 and hand_value(cards) == 21


# ============================
#  BLACKJACK ENGINE
# ============================

class BlackjackGame:
    def __init__(self, shoe, bet):
        self.shoe = shoe
        self.bet = bet
        self.hands = []
        self.dealer = []
        self.insurance_bet = 0
        self.current_hand = 0

    def initial_deal(self):
        p1 = [self.shoe.draw(), self.shoe.draw()]
        d1 = [self.shoe.draw(), self.shoe.draw()]
        self.hands  = [{"cards": p1, "bet": self.bet, "finished": False}]
        self.dealer = d1

    def can_split(self):
        if len(self.hands) >= 3:
            return False
        cards = self.hands[self.current_hand]["cards"]
        if len(cards) != 2:
            return False
        return cards[0][:-1] == cards[1][:-1]

    def split(self):
        hand = self.hands[self.current_hand]
        c1, c2 = hand["cards"]
        hand["cards"] = [c1, self.shoe.draw()]
        self.hands.append({"cards": [c2, self.shoe.draw()], "bet": self.bet, "finished": False})

    def can_double(self):
        return len(self.hands[self.current_hand]["cards"]) == 2

    def double_down(self):
        hand = self.hands[self.current_hand]
        hand["bet"] *= 2
        hand["cards"].append(self.shoe.draw())
        hand["finished"] = True

    def can_insure(self):
        return self.dealer[0].startswith("A")

    def take_insurance(self):
        self.insurance_bet = self.bet // 2

    def dealer_play(self):
        while hand_value(self.dealer) < 17 or (
            hand_value(self.dealer) == 17 and self._is_soft(self.dealer)
        ):
            self.dealer.append(self.shoe.draw())

    def _is_soft(self, cards):
        value = hand_value(cards)
        if value <= 11:
            return True
        return any(card.startswith("A") for card in cards)

    def settle_hand(self, hand):
        player_val = hand_value(hand["cards"])
        dealer_val = hand_value(self.dealer)
        if player_val > 21:
            return -hand["bet"]
        if dealer_val > 21:
            return hand["bet"]
        if player_val > dealer_val:
            return hand["bet"]
        if player_val < dealer_val:
            return -hand["bet"]
        return 0

    def settle_blackjack(self):
        return int(self.bet * 1.5)


# ============================
#  CONTAINER VIEW BUILDER
# ============================

def _build_view(
    ctx,
    *,
    with_buttons: bool,
    game: BlackjackGame | None = None,
    accent: discord.Colour = ACCENT_GREEN,
    insurance_only: bool = False,
) -> discord.ui.LayoutView:
    """
    Build a LayoutView containing the rendered table image and (optionally)
    the action buttons.  When `with_buttons` is True the view exposes:
        * `view.choice` — set to the clicked button value, or None on timeout
        * `view.stop()` is called automatically when a button is pressed
    """
    view = discord.ui.LayoutView(timeout=60)
    view.choice = None

    items = [
        discord.ui.MediaGallery(
            discord.MediaGalleryItem(media=f"attachment://{IMAGE_NAME}")
        ),
    ]

    if with_buttons and game is not None:
        class _Btn(discord.ui.Button):
            def __init__(self_, label, style, value, disabled=False):
                super().__init__(label=label, style=style, disabled=disabled)
                self_.value = value

            async def callback(self_, interaction: discord.Interaction):
                view.choice = self_.value
                view.stop()
                try:
                    await interaction.response.defer()
                except discord.InteractionResponded:
                    pass

        if insurance_only:
            row = discord.ui.ActionRow(
                _Btn(msg(ctx, "blackjack_btn_insurance"), discord.ButtonStyle.green, "insurance"),
                _Btn(msg(ctx, "blackjack_btn_decline"),   discord.ButtonStyle.gray,  "decline"),
            )
        else:
            row = discord.ui.ActionRow(
                _Btn(msg(ctx, "blackjack_btn_hit"),    discord.ButtonStyle.green,  "hit"),
                _Btn(msg(ctx, "blackjack_btn_stand"),  discord.ButtonStyle.red,    "stand"),
                _Btn(msg(ctx, "blackjack_btn_double"), discord.ButtonStyle.blurple, "double", disabled=not game.can_double()),
                _Btn(msg(ctx, "blackjack_btn_split"),  discord.ButtonStyle.gray,   "split",  disabled=not game.can_split()),
            )

        items.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        items.append(row)

    container = discord.ui.Container(*items, accent_colour=accent)
    view.add_item(container)
    return view


# ============================
#  BLACKJACK COG
# ============================

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shoe = Shoe()

    @commands.hybrid_group(
        name="blackjack",
        description=CMDS.text("blackjack.description"),
        help=CMDS.help("blackjack"),
    )
    async def blackjack(self, ctx):
        if ctx.invoked_subcommand is None:
            prefix = await _resolve_prefix(self.bot, ctx)
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=msg(ctx, "blackjack_help_title")
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=msg(ctx, "blackjack_help_body", prefix=prefix)
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    @blackjack.command(
        name="play",
        description=CMDS.text("blackjack.play.description"),
        help=CMDS.help("blackjack.play"),
    )
    async def blackjack_play(self, ctx, amount: int = None):
        """Play a full casino-grade blackjack game with a rendered table image."""
        if amount is None or amount <= 0:
            return await ctx.send(msg(ctx, "blackjack_bet_positive"))

        economy = self.bot.get_cog("EconomyCog")
        user_data = await economy.get_user_economy_data(ctx.author.id)
        balance = user_data["balance"]

        blackjack_cooldown = int(os.getenv("BLACKJACK_COOLDOWN") or 30)
        if user_data["last_blackjack"] + blackjack_cooldown > time.time():
            return await ctx.send(view=cooldown_view(
                msg(ctx, "blackjack_cooldown_action"),
                cooldown_ready_at(user_data["last_blackjack"], blackjack_cooldown),
                title=msg(ctx, "blackjack_cooldown_title"),
                note=msg(ctx, "blackjack_cooldown_note", seconds=blackjack_cooldown),
                template=msg(ctx, "blackjack_cooldown_sentence"),
            ))

        if amount > balance:
            return await ctx.send(msg(ctx, "blackjack_not_enough"))

        game = BlackjackGame(self.shoe, amount)
        game.initial_deal()

        dealer_has_blackjack = is_blackjack(game.dealer)
        player_has_blackjack = is_blackjack(game.hands[0]["cards"])

        # ── Helpers ────────────────────────────────────────────────────────
        async def _render(reveal_dealer: bool, title: str, status: str = "", status_color=STATUS_NEUTRAL):
            return await render_table(
                game.hands,
                game.dealer,
                reveal_dealer=reveal_dealer,
                current_hand_index=game.current_hand,
                title=title,
                status=status,
                status_color=status_color,
            )

        def _attach_check(view: discord.ui.LayoutView):
            async def _check(interaction: discord.Interaction) -> bool:
                if interaction.user.id != ctx.author.id:
                    try:
                        await interaction.response.send_message(
                            msg(interaction, "blackjack_not_yours"), ephemeral=True
                        )
                    except discord.InteractionResponded:
                        pass
                    return False
                return True
            view.interaction_check = _check

        message: discord.Message | None = None

        async def _send_or_edit(buf, view: discord.ui.LayoutView):
            nonlocal message
            file = discord.File(buf, filename=IMAGE_NAME)
            if message is None:
                message = await ctx.send(view=view, file=file)
            else:
                await message.edit(view=view, attachments=[file])

        # ── Insurance prompt ───────────────────────────────────────────────
        if game.can_insure() and not dealer_has_blackjack:
            buf  = await _render(
                reveal_dealer=False,
                title=msg(ctx, "blackjack_insurance_title"),
                status=msg(ctx, "blackjack_insurance_status"),
                status_color=STATUS_NEUTRAL,
            )
            view = _build_view(ctx, with_buttons=True, game=game, accent=ACCENT_BRAND, insurance_only=True)
            _attach_check(view)
            await _send_or_edit(buf, view)
            await view.wait()
            if view.choice == "insurance":
                game.take_insurance()

        # ── Dealer blackjack resolution ────────────────────────────────────
        if dealer_has_blackjack:
            payout = 0
            if game.insurance_bet > 0:
                payout += game.insurance_bet * 2  # 2:1 insurance payout
            payout -= amount
            economy.record_gamble(
                user_data, payout,
                "blackjack_win" if payout > 0 else "blackjack_loss" if payout < 0 else "blackjack",
                "dealer blackjack" + (" · insurance paid" if game.insurance_bet > 0 else ""),
            )
            user_data["last_blackjack"] = time.time()
            await economy.save_user_economy_data(ctx.author.id)

            status = msg(ctx, "blackjack_status_coins", amount=f"{payout:+d}")
            status_color = STATUS_WIN if payout >= 0 else STATUS_LOSS
            buf  = await _render(
                reveal_dealer=True,
                title=msg(ctx, "blackjack_dealer_blackjack"),
                status=status,
                status_color=status_color,
            )
            view = _build_view(ctx, with_buttons=False, accent=ACCENT_RED)
            return await _send_or_edit(buf, view)

        # ── Player natural blackjack ───────────────────────────────────────
        if player_has_blackjack:
            winnings = game.settle_blackjack()
            economy.record_gamble(user_data, winnings, "blackjack_win", "natural blackjack")
            user_data["last_blackjack"] = time.time()
            await economy.save_user_economy_data(ctx.author.id)

            buf  = await _render(
                reveal_dealer=True,
                title=msg(ctx, "blackjack_natural"),
                status=msg(ctx, "blackjack_status_coins", amount=f"+{winnings}"),
                status_color=STATUS_WIN,
            )
            view = _build_view(ctx, with_buttons=False, accent=ACCENT_BRAND)
            return await _send_or_edit(buf, view)

        # ── PLAYER TURN ────────────────────────────────────────────────────
        hand_index = 0
        while hand_index < len(game.hands):
            game.current_hand = hand_index

            while not game.hands[hand_index]["finished"]:
                title = (
                    msg(ctx, "blackjack_hand", index=hand_index + 1)
                    if len(game.hands) > 1
                    else msg(ctx, "blackjack_your_move")
                )
                buf   = await _render(reveal_dealer=False, title=title)
                view  = _build_view(ctx, with_buttons=True, game=game, accent=ACCENT_GREEN)
                _attach_check(view)
                await _send_or_edit(buf, view)

                await view.wait()
                choice = view.choice

                if choice == "hit":
                    game.hands[hand_index]["cards"].append(game.shoe.draw())
                    if hand_value(game.hands[hand_index]["cards"]) > 21:
                        game.hands[hand_index]["finished"] = True
                elif choice == "double":
                    if game.can_double() and user_data["balance"] >= game.hands[hand_index]["bet"]:
                        game.double_down()
                    else:
                        game.hands[hand_index]["finished"] = True
                elif choice == "split":
                    if game.can_split() and user_data["balance"] >= game.hands[hand_index]["bet"]:
                        game.split()
                    else:
                        game.hands[hand_index]["finished"] = True
                else:
                    # "stand", timeout, or unrecognised — finish the hand
                    game.hands[hand_index]["finished"] = True

            hand_index += 1

        # ── DEALER TURN ────────────────────────────────────────────────────
        game.dealer_play()

        # ── PAYOUTS ────────────────────────────────────────────────────────
        total_result = sum(game.settle_hand(h) for h in game.hands)
        hands = len(game.hands)
        economy.record_gamble(
            user_data, total_result,
            "blackjack_win" if total_result > 0 else "blackjack_loss" if total_result < 0 else "blackjack",
            f"{hands} hand{'s' if hands > 1 else ''} · bet {amount:,}",
        )
        user_data["last_blackjack"] = time.time()
        await economy.save_user_economy_data(ctx.author.id)

        if total_result > 0:
            title  = msg(ctx, "blackjack_win")
            status = msg(ctx, "blackjack_status_coins", amount=f"+{total_result}")
            color  = STATUS_WIN
            accent = ACCENT_GREEN
        elif total_result < 0:
            title  = msg(ctx, "blackjack_lose")
            status = msg(ctx, "blackjack_status_coins", amount=total_result)
            color  = STATUS_LOSS
            accent = ACCENT_RED
        else:
            title  = msg(ctx, "blackjack_push")
            status = msg(ctx, "blackjack_push_status")
            color  = STATUS_NEUTRAL
            accent = ACCENT_BRAND

        # No active hand once the round is settled
        game.current_hand = -1
        for h in game.hands:
            h["finished"] = True

        buf  = await _render(reveal_dealer=True, title=title, status=status, status_color=color)
        view = _build_view(ctx, with_buttons=False, accent=accent)
        await _send_or_edit(buf, view)

    # This command is a tutorial for people who don't know how to play blackjack
    @blackjack.command(
        name="tutorial",
        description=CMDS.text("blackjack.tutorial.description"),
        help=CMDS.help("blackjack.tutorial"),
    )
    async def blackjack_tutorial(self, ctx):
        """Learn how to play blackjack."""
        # Paginated tutorial via the shared PaginatedView
        pages = [msg(ctx, f"blackjack_page_{page}") for page in range(1, 7)]
        view = PaginatedView(title=msg(ctx, "blackjack_tutorial_title"), pages=pages)
        await ctx.send(view=view)


# ============================
#  SETUP
# ============================

async def setup(bot):
    await bot.add_cog(Blackjack(bot))
