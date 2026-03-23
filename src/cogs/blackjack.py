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

SHOE_FILE = "blackjack_shoe.json"
CARD_BACK = "🂠"

ACCENT_GREEN = discord.Colour(0x57F287)
ACCENT_RED = discord.Colour(0xED4245)
ACCENT_GOLD = discord.Colour(0xFEE75C)

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
            except:
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

CARD_EMOJIS = {
    "AS": "🂡", "2S": "🂢", "3S": "🂣", "4S": "🂤", "5S": "🂥", "6S": "🂦",
    "7S": "🂧", "8S": "🂨", "9S": "🂩", "10S": "🂪", "JS": "🂫", "QS": "🂭", "KS": "🂮",
    "AH": "🂱", "2H": "🂲", "3H": "🂳", "4H": "🂴", "5H": "🂵", "6H": "🂶",
    "7H": "🂷", "8H": "🂸", "9H": "🂹", "10H": "🂺", "JH": "🂻", "QH": "🂽", "KH": "🂾",
    "AD": "🃁", "2D": "🃂", "3D": "🃃", "4D": "🃄", "5D": "🃅", "6D": "🃆",
    "7D": "🃇", "8D": "🃈", "9D": "🃉", "10D": "🃊", "JD": "🃋", "QD": "🃍", "KD": "🃎",
    "AC": "🃑", "2C": "🃒", "3C": "🃓", "4C": "🃔", "5C": "🃕", "6C": "🃖",
    "7C": "🃗", "8C": "🃘", "9C": "🃙", "10C": "🃚", "JC": "🃛", "QC": "🃝", "KC": "🃞",
}

def card_emoji(card):
    return CARD_EMOJIS.get(card, card)

def hand_value(cards):
    value = 0
    aces = 0
    for card in cards:
        rank = card[:-1]
        if rank.isdigit():
            value += int(rank)
        elif rank in ["J", "Q", "K"]:
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
        self.hands = [{"cards": p1, "bet": self.bet, "finished": False}]
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
#  CONTAINER VIEW BUILDERS
# ============================

def _hand_body(game: BlackjackGame, reveal_dealer: bool) -> str:
    lines = []
    for i, hand in enumerate(game.hands):
        cards = " ".join(card_emoji(c) for c in hand["cards"])
        value = hand_value(hand["cards"])
        lines.append(f"**Your Hand #{i+1}** — Bet: {hand['bet']}\n{cards} — Value: **{value}**")

    if reveal_dealer:
        dealer_cards = " ".join(card_emoji(c) for c in game.dealer)
        dealer_value = hand_value(game.dealer)
        lines.append(f"**Dealer**\n{dealer_cards} — Value: **{dealer_value}**")
    else:
        dealer_cards = f"{card_emoji(game.dealer[0])} {CARD_BACK}"
        lines.append(f"**Dealer**\n{dealer_cards}")

    return "\n\n".join(lines)


def build_hand_view(ctx, game: BlackjackGame, reveal_dealer: bool = False, title: str = "Blackjack") -> discord.ui.LayoutView:
    """Display-only hand view (no buttons)."""
    view = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### 🎰 {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=_hand_body(game, reveal_dealer)),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_interactive_hand_view(ctx, game: BlackjackGame, reveal_dealer: bool = False, title: str = "Blackjack") -> discord.ui.LayoutView:
    """Hand view with Hit / Stand / Double / Split / Insurance buttons."""
    view = discord.ui.LayoutView(timeout=30)
    view.ctx = ctx
    view.choice = None

    async def _check(interaction: discord.Interaction) -> bool:
        return interaction.user.id == ctx.author.id

    view.interaction_check = _check

    class _Btn(discord.ui.Button):
        def __init__(self_, label, style, value, disabled=False):
            super().__init__(label=label, style=style, disabled=disabled)
            self_.value = value
        async def callback(self_, interaction):
            view.choice = self_.value
            view.stop()
            await interaction.response.defer()

    container = discord.ui.Container(
        discord.ui.TextDisplay(content=f"### 🎰 {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=_hand_body(game, reveal_dealer)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(
            _Btn("Hit", discord.ButtonStyle.green, "hit"),
            _Btn("Stand", discord.ButtonStyle.red, "stand"),
            _Btn("Double", discord.ButtonStyle.blurple, "double", disabled=not game.can_double()),
            _Btn("Split", discord.ButtonStyle.gray, "split", disabled=not game.can_split()),
            _Btn("Insurance", discord.ButtonStyle.green, "insurance", disabled=not game.can_insure()),
        ),
        accent_colour=ACCENT_GREEN
    )
    view.add_item(container)
    return view


def build_next_hand_view(ctx) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView(timeout=30)
    view.ctx = ctx
    view.choice = None

    async def _check(interaction: discord.Interaction) -> bool:
        return interaction.user.id == ctx.author.id

    view.interaction_check = _check

    class _NextBtn(discord.ui.Button):
        def __init__(self_):
            super().__init__(label="Next Hand", style=discord.ButtonStyle.green)
        async def callback(self_, interaction):
            view.choice = "next"
            view.stop()
            await interaction.response.defer()

    container = discord.ui.Container(
        discord.ui.TextDisplay(content="### 🎰 Blackjack"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="Hand complete. Ready for the next hand?"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(_NextBtn()),
        accent_colour=ACCENT_GOLD
    )
    view.add_item(container)
    return view


# ============================
#  BLACKJACK COG
# ============================

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shoe = Shoe()

    @commands.command(name="blackjack")
    async def blackjack(self, ctx, amount: int = None):
        """Play a full casino‑grade blackjack game."""
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

        # Insurance option
        if game.can_insure() and not dealer_has_blackjack:
            view = build_interactive_hand_view(ctx, game, reveal_dealer=False, title="Insurance?")
            msg = await ctx.send(view=view)
            await view.wait()
            if view.choice == "insurance":
                game.take_insurance()
            await msg.edit(view=discord.ui.LayoutView())

        # Dealer blackjack resolution
        if dealer_has_blackjack:
            await ctx.send(view=build_hand_view(ctx, game, reveal_dealer=True, title="Dealer Blackjack!"))
            if game.insurance_bet > 0:
                user_data["balance"] += game.insurance_bet * 2
            user_data["balance"] -= amount
            user_data["last_blackjack"] = time.time()
            economy.save_economy_data()
            return

        # Player blackjack
        if player_has_blackjack:
            winnings = game.settle_blackjack()
            user_data["balance"] += winnings
            user_data["last_blackjack"] = time.time()
            economy.save_economy_data()
            return await ctx.send(view=build_hand_view(ctx, game, reveal_dealer=False, title="Blackjack! You win 3:2"))

        # PLAYER TURN
        msg = None
        for hand_index in range(len(game.hands)):
            game.current_hand = hand_index

            while not game.hands[hand_index]["finished"]:
                view = build_interactive_hand_view(ctx, game, reveal_dealer=False, title=f"Your Hand #{hand_index+1}")
                if msg is None:
                    msg = await ctx.send(view=view)
                else:
                    await msg.edit(view=view)

                await view.wait()

                if view.choice == "hit":
                    game.hands[hand_index]["cards"].append(game.shoe.draw())
                    if hand_value(game.hands[hand_index]["cards"]) > 21:
                        game.hands[hand_index]["finished"] = True
                elif view.choice == "stand":
                    game.hands[hand_index]["finished"] = True
                elif view.choice == "double":
                    game.double_down()
                elif view.choice == "split":
                    game.split()
                elif view.choice == "insurance":
                    game.take_insurance()

                await msg.edit(view=discord.ui.LayoutView())

            if hand_index < len(game.hands) - 1:
                view = build_next_hand_view(ctx)
                await msg.edit(view=view)
                await view.wait()
                await msg.edit(view=discord.ui.LayoutView())

        # DEALER TURN
        game.dealer_play()

        # PAYOUTS
        total_result = 0
        for hand in game.hands:
            total_result += game.settle_hand(hand)

        user_data["balance"] += total_result
        user_data["last_blackjack"] = time.time()
        economy.save_economy_data()

        title = "🎉 You Win!" if total_result > 0 else "💀 You Lose!" if total_result < 0 else "🤝 Push"
        await ctx.send(view=build_hand_view(ctx, game, reveal_dealer=True, title=title))


# ============================
#  SETUP
# ============================

async def setup(bot):
    await bot.add_cog(Blackjack(bot))
