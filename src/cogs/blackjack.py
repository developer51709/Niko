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
from utils.paginator import PaginatedView, paginate
from utils.image.blackjack import render_table

SHOE_FILE   = "blackjack_shoe.json"
IMAGE_NAME  = "blackjack.png"

ACCENT_GREEN = discord.Colour(0x57F287)
ACCENT_RED   = discord.Colour(0xED4245)
ACCENT_GOLD  = discord.Colour(0xFEE75C)
ACCENT_BLUE  = discord.Colour(0x5865F2)


# ============================
#  PREFIX RESOLVER
# ============================

async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """
    Resolve the primary prefix for the current context/interaction.

    Supports:
    - Static string prefix
    - Static list/tuple of prefixes
    - Dynamic prefix function: command_prefix(bot, message) -> list[str]
    """
    raw = bot.command_prefix

    # Static prefix (string)
    if isinstance(raw, str):
        return raw

    # Static list/tuple of prefixes
    if isinstance(raw, (list, tuple)):
        return raw[0]

    # Dynamic prefix function
    try:
        # Context: has .message
        msg = getattr(ctx_or_interaction, "message", None)

        # Interaction: use the original message if present
        if msg is None and isinstance(ctx_or_interaction, discord.Interaction):
            msg = ctx_or_interaction.message

        if msg is None:
            return "!"

        prefixes = raw(bot, msg)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass

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
                _Btn("Take Insurance", discord.ButtonStyle.green,   "insurance"),
                _Btn("Decline",        discord.ButtonStyle.gray,    "decline"),
            )
        else:
            row = discord.ui.ActionRow(
                _Btn("Hit",       discord.ButtonStyle.green,   "hit"),
                _Btn("Stand",     discord.ButtonStyle.red,     "stand"),
                _Btn("Double",    discord.ButtonStyle.blurple, "double",  disabled=not game.can_double()),
                _Btn("Split",     discord.ButtonStyle.gray,    "split",   disabled=not game.can_split()),
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
        description="Play a full casino-grade blackjack game",
        help="{ 'en': 'play a full casino-grade blackjack game', 'de': 'spiele ein volles Casino-Blackjack-Spiel', 'es': 'juega un blackjack de casino completo' }"
    )
    async def blackjack(self, ctx):
        if ctx.invoked_subcommand is None:
            prefix = await _resolve_prefix(self.bot, ctx)
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### 🎰 Blackjack Help"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"**{prefix}blackjack play <amount>** - Play a game of blackjack.\n**{prefix}blackjack tutorial** - Learn how to play blackjack."
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    @blackjack.command(
        name="play",
        description="Play a game of blackjack",
        help="{ 'en': 'play a full casino-grade blackjack game', 'de': 'spiele ein volles Casino-Blackjack-Spiel', 'es': 'juega una partida de blackjack' }"
    )
    async def blackjack_play(self, ctx, amount: int = None):
        """Play a full casino-grade blackjack game with a rendered table image."""
        if amount is None or amount <= 0:
            return await ctx.send("You must bet more than 0 coins.")

        economy = self.bot.get_cog("EconomyCog")
        user_data = economy.get_user_economy_data(ctx.author.id)
        balance = user_data["balance"]

        if user_data["last_blackjack"] + int(os.getenv("BLACKJACK_COOLDOWN") or 60) > time.time():
            return await ctx.send("You're on cooldown for blackjack.")

        if amount > balance:
            return await ctx.send("You don't have enough coins.")

        game = BlackjackGame(self.shoe, amount)
        game.initial_deal()

        dealer_has_blackjack = is_blackjack(game.dealer)
        player_has_blackjack = is_blackjack(game.hands[0]["cards"])

        # ── Helpers ────────────────────────────────────────────────────────
        async def _render(reveal_dealer: bool, title: str, status: str = "", status_color=(255, 215, 0)):
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
                            "This isn't your blackjack game.", ephemeral=True
                        )
                    except discord.InteractionResponded:
                        pass
                    return False
                return True
            view.interaction_check = _check

        msg: discord.Message | None = None

        async def _send_or_edit(buf, view: discord.ui.LayoutView):
            nonlocal msg
            file = discord.File(buf, filename=IMAGE_NAME)
            if msg is None:
                msg = await ctx.send(view=view, file=file)
            else:
                await msg.edit(view=view, attachments=[file])

        # ── Insurance prompt ───────────────────────────────────────────────
        if game.can_insure() and not dealer_has_blackjack:
            buf  = await _render(reveal_dealer=False, title="Insurance?",
                                 status="Dealer is showing an Ace.", status_color=(255, 215, 0))
            view = _build_view(with_buttons=True, game=game, accent=ACCENT_GOLD, insurance_only=True)
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
            user_data["balance"] += payout
            user_data["last_blackjack"] = time.time()
            economy.save_economy_data()

            status = f"{payout:+d} coins"
            status_color = (87, 242, 135) if payout >= 0 else (237, 90, 96)
            buf  = await _render(reveal_dealer=True, title="Dealer Blackjack",
                                 status=status, status_color=status_color)
            view = _build_view(with_buttons=False, accent=ACCENT_RED)
            return await _send_or_edit(buf, view)

        # ── Player natural blackjack ───────────────────────────────────────
        if player_has_blackjack:
            winnings = game.settle_blackjack()
            user_data["balance"] += winnings
            user_data["last_blackjack"] = time.time()
            economy.save_economy_data()

            buf  = await _render(reveal_dealer=True, title="Blackjack! 3:2",
                                 status=f"+{winnings} coins", status_color=(87, 242, 135))
            view = _build_view(with_buttons=False, accent=ACCENT_GOLD)
            return await _send_or_edit(buf, view)

        # ── PLAYER TURN ────────────────────────────────────────────────────
        hand_index = 0
        while hand_index < len(game.hands):
            game.current_hand = hand_index

            while not game.hands[hand_index]["finished"]:
                title = f"Hand #{hand_index+1}" if len(game.hands) > 1 else "Your Move"
                buf   = await _render(reveal_dealer=False, title=title)
                view  = _build_view(with_buttons=True, game=game, accent=ACCENT_GREEN)
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
        user_data["balance"] += total_result
        user_data["last_blackjack"] = time.time()
        economy.save_economy_data()

        if total_result > 0:
            title  = "You Win"
            status = f"+{total_result} coins"
            color  = (87, 242, 135)
            accent = ACCENT_GREEN
        elif total_result < 0:
            title  = "You Lose"
            status = f"{total_result} coins"
            color  = (237, 90, 96)
            accent = ACCENT_RED
        else:
            title  = "Push"
            status = "Bet returned"
            color  = (255, 215, 0)
            accent = ACCENT_GOLD

        # No active hand once the round is settled
        game.current_hand = -1
        for h in game.hands:
            h["finished"] = True

        buf  = await _render(reveal_dealer=True, title=title, status=status, status_color=color)
        view = _build_view(with_buttons=False, accent=accent)
        await _send_or_edit(buf, view)

    # This command is a tutorial for people who don't know how to play blackjack
    @blackjack.command(
        name="tutorial",
        description="Learn how to play blackjack",
        help="{ 'en': 'learn how to play blackjack', 'de': 'lerne, wie man Blackjack spielt', 'es': 'aprende a jugar blackjack' }"
    )
    async def blackjack_tutorial(self, ctx):
        """Learn how to play blackjack."""
        # Paginated tutorial via the shared PaginatedView
        pages = [
            "## **Page 1 — What Is Blackjack? (The Goal of the Game)**\nBlackjack (also called **21**) is a simple card game where **you play against the dealer**, not the other players.\nYour goal is to get a hand value **closer to 21 than the dealer** *without going over 21*. Going over 21 is called **busting**, and it means you automatically lose.\n\nBlackjack is played with one or more standard 52‑card decks. Each round begins with everyone placing a bet. After that, the dealer gives each player **two cards face‑up**, and gives themselves **one face‑up card and one face‑down card**.",
            "## **Page 2 — Understanding Card Values (No Math Skills Needed!)**\nBlackjack uses very simple card values:\n- **Number cards (2–10):** worth their number\n- **Face cards (J, Q, K):** worth **10**\n- **Ace:** worth **1 or 11**, whichever helps your hand more\n\nYou don’t need to calculate anything complicated — just add the values together.\nExample:\n- A **7** and a **King** = **17**\n- An **Ace** and a **6** = **7 or 17** (the Ace adjusts automatically)\n\nA hand with an Ace that can count as 11 without busting is called a **soft hand**.\nA hand where the Ace must count as 1 is a **hard hand**.",
            "## **Page 3 — What Happens at the Start of a Round**\nA typical round looks like this:\n1. You place your bet.\n2. You receive **two cards face‑up**.\n3. The dealer receives **one face‑up card** and **one face‑down card** (the “hole card”).\n4. If you have an **Ace + 10‑value card**, that’s a **Blackjack**, also called a **natural**.\n   - A natural Blackjack usually pays **3:2**, though some tables pay **6:5** (which is worse for players).\n\nIf you don’t have a natural, you choose what to do next.",
            "## **Page 4 — Your Options: Hit, Stand, Double, Split, Surrender**\nYou can choose from several actions:\n\n### **Hit**\nAsk for another card. Use this when your hand is low and you want to improve it.\n\n### **Stand**\nKeep your current hand and end your turn.\n\n### **Double Down**/nDouble your bet and receive **exactly one more card**.\nThis is best when you have a strong starting hand (like 10 or 11).\n\n### **Split**\nIf your two cards have the **same value**, you can split them into **two separate hands**, doubling your bet.\nEach new hand gets one extra card.\n\n### **Surrender** (not always available)\nYou give up your hand immediately and get **half your bet back**.\n\n### **Insurance**\nA side bet offered only when the dealer shows an Ace.\nIt pays **2:1** if the dealer has Blackjack — but statistically, it’s usually a bad bet.",
            "## **Page 5 — Dealer Rules**\nThe dealer must follow strict rules:\n- The dealer must **hit until reaching 17 or higher**.\n- Most casinos require the dealer to stand on **all 17s**, but some require hitting on a “soft 17.”\n- If the dealer busts (goes over 21), **all players who didn’t bust win**.\n\nYou don’t need to guess what the dealer will do — the rules are fixed.",
            "## **Page 6 — How You Win (and What a Push Is)**\nAfter all players finish their turns, the dealer reveals their hidden card and plays their hand. Then:\n\n- If your total is **closer to 21 than the dealer**, you win.\n- If your total is **lower**, you lose.\n- If both totals are **equal**, it’s a **push** (tie) — you get your bet back.\n\nA natural Blackjack (Ace + 10‑value card) pays **3:2** at most tables, but some pay **6:5**, which is worse for players. Avoid 6:5 tables when possible."
        ]
        view = PaginatedView(title="Blackjack Tutorial", pages=pages)
        await ctx.send(view=view)


# ============================
#  SETUP
# ============================

async def setup(bot):
    await bot.add_cog(Blackjack(bot))
