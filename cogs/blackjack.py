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

# Path for persistent shoe
SHOE_FILE = "blackjack_shoe.json"

# Unicode card back
CARD_BACK = "🂠"

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
        suits = ["S", "H", "D", "C"]  # Spades, Hearts, Diamonds, Clubs

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
        if len(self.cards) < 20:  # reshuffle threshold
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
        self.hands = []  # list of dicts: {"cards": [...], "bet": int, "finished": bool}
        self.dealer = []
        self.insurance_bet = 0
        self.current_hand = 0

    # --------------------------
    #  INITIAL DEAL
    # --------------------------

    def initial_deal(self):
        p1 = [self.shoe.draw(), self.shoe.draw()]
        d1 = [self.shoe.draw(), self.shoe.draw()]

        self.hands = [{"cards": p1, "bet": self.bet, "finished": False}]
        self.dealer = d1

    # --------------------------
    #  SPLIT LOGIC
    # --------------------------

    def can_split(self):
        if len(self.hands) >= 3:
            return False

        cards = self.hands[self.current_hand]["cards"]
        if len(cards) != 2:
            return False

        r1 = cards[0][:-1]
        r2 = cards[1][:-1]
        return r1 == r2

    def split(self):
        hand = self.hands[self.current_hand]
        c1, c2 = hand["cards"]

        # Replace current hand with first split
        hand["cards"] = [c1, self.shoe.draw()]

        # Add second split hand
        self.hands.append({
            "cards": [c2, self.shoe.draw()],
            "bet": self.bet,
            "finished": False
        })

    # --------------------------
    #  DOUBLE DOWN
    # --------------------------

    def can_double(self):
        cards = self.hands[self.current_hand]["cards"]
        return len(cards) == 2

    def double_down(self):
        hand = self.hands[self.current_hand]
        hand["bet"] *= 2
        hand["cards"].append(self.shoe.draw())
        hand["finished"] = True

    # --------------------------
    #  INSURANCE
    # --------------------------

    def can_insure(self):
        return self.dealer[0].startswith("A")

    def take_insurance(self):
        self.insurance_bet = self.bet // 2

    # --------------------------
    #  DEALER LOGIC (H17)
    # --------------------------

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

    # --------------------------
    #  PAYOUTS
    # --------------------------

    def settle_hand(self, hand):
        player_val = hand_value(hand["cards"])
        dealer_val = hand_value(self.dealer)

        # Player bust
        if player_val > 21:
            return -hand["bet"]

        # Dealer bust
        if dealer_val > 21:
            return hand["bet"]

        # Compare
        if player_val > dealer_val:
            return hand["bet"]
        if player_val < dealer_val:
            return -hand["bet"]
        return 0

    def settle_blackjack(self):
        return int(self.bet * 1.5)

# ============================
#  BUTTON VIEWS
# ============================

class BlackjackView(discord.ui.View):
    def __init__(self, ctx, game, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.game = game
        self.choice = None

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.choice = "hit"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.choice = "stand"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Double", style=discord.ButtonStyle.blurple)
    async def double(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.game.can_double():
            await interaction.response.send_message("You cannot double down now.", ephemeral=True)
            return
        self.choice = "double"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Split", style=discord.ButtonStyle.gray)
    async def split(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.game.can_split():
            await interaction.response.send_message("You cannot split this hand.", ephemeral=True)
            return
        self.choice = "split"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Insurance", style=discord.ButtonStyle.green)
    async def insurance(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.game.can_insure():
            await interaction.response.send_message("Insurance is not available.", ephemeral=True)
            return
        self.choice = "insurance"
        self.stop()
        await interaction.response.defer()


class NextHandView(discord.ui.View):
    def __init__(self, ctx, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(label="Next Hand", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.choice = "next"
        self.stop()
        await interaction.response.defer()


# ============================
#  EMBED BUILDERS
# ============================

def build_hand_embed(ctx, game, reveal_dealer=False, title="Blackjack"):
    embed = discord.Embed(
        title=f"🎰 {title}",
        color=discord.Color.green()
    )

    # Player hands
    for i, hand in enumerate(game.hands):
        cards = " ".join(card_emoji(c) for c in hand["cards"])
        value = hand_value(hand["cards"])
        embed.add_field(
            name=f"Your Hand #{i+1} — Bet: {hand['bet']}",
            value=f"{cards}\nValue: **{value}**",
            inline=False
        )

    # Dealer hand
    if reveal_dealer:
        dealer_cards = " ".join(card_emoji(c) for c in game.dealer)
        dealer_value = hand_value(game.dealer)
        embed.add_field(
            name="Dealer",
            value=f"{dealer_cards}\nValue: **{dealer_value}**",
            inline=False
        )
    else:
        dealer_cards = f"{card_emoji(game.dealer[0])} {CARD_BACK}"
        embed.add_field(
            name="Dealer",
            value=dealer_cards,
            inline=False
        )

    embed.set_footer(text=f"Requested by {ctx.author}")
    return embed


# ============================
#  BLACKJACK COG
# ============================

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shoe = Shoe()  # persistent shoe

    @commands.command(name="blackjack")
    async def blackjack(self, ctx, amount: int = None):
        """Play a full casino‑grade blackjack game."""
        if amount is None or amount <= 0:
            return await ctx.send("You must bet more than 0 coins.")

        economy = self.bot.get_cog("EconomyCog")
        user_data = economy.get_user_economy_data(ctx.author.id)
        balance = user_data["balance"]

        # Cooldown
        if user_data["last_blackjack"] + int(os.getenv("BLACKJACK_COOLDOWN") or 60) > time.time():
            return await ctx.send("You're on cooldown for blackjack.")

        if amount > balance:
            return await ctx.send("You don't have enough coins.")

        # Start game
        game = BlackjackGame(self.shoe, amount)
        game.initial_deal()

        # Dealer checks for blackjack
        dealer_has_blackjack = is_blackjack(game.dealer)
        player_has_blackjack = is_blackjack(game.hands[0]["cards"])

        # Insurance option
        if game.can_insure() and not dealer_has_blackjack:
            view = BlackjackView(ctx, game)
            embed = build_hand_embed(ctx, game, reveal_dealer=False, title="Insurance?")
            msg = await ctx.send(embed=embed, view=view)

            await view.wait()

            if view.choice == "insurance":
                game.take_insurance()

        # Dealer blackjack resolution
        if dealer_has_blackjack:
            embed = build_hand_embed(ctx, game, reveal_dealer=True, title="Dealer Blackjack!")
            await ctx.send(embed=embed)

            if game.insurance_bet > 0:
                user_data["balance"] += game.insurance_bet * 2

            user_data["balance"] -= amount
            user_data["last_blackjack"] = time.time()
            economy = self.bot.get_cog("EconomyCog")
            economy.save_economy_data()
            return

        # Player blackjack
        if player_has_blackjack:
            winnings = game.settle_blackjack()
            user_data["balance"] += winnings
            user_data["last_blackjack"] = time.time()
            economy = self.bot.get_cog("EconomyCog")
            economy.save_economy_data()

            embed = build_hand_embed(ctx, game, reveal_dealer=False, title="Blackjack! You win 3:2")
            return await ctx.send(embed=embed)

        # ===========================
        #  PLAYER TURN (INCLUDING SPLITS)
        # ===========================

        for hand_index in range(len(game.hands)):
            game.current_hand = hand_index

            while not game.hands[hand_index]["finished"]:
                view = BlackjackView(ctx, game)
                embed = build_hand_embed(ctx, game, reveal_dealer=False, title=f"Your Hand #{hand_index+1}")
                msg = await ctx.send(embed=embed, view=view)

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

                await msg.edit(view=None)

            # Move to next hand
            if hand_index < len(game.hands) - 1:
                view = NextHandView(ctx)
                embed = discord.Embed(
                    title="Next Hand",
                    description="Click to continue.",
                    color=discord.Color.green()
                )
                msg = await ctx.send(embed=embed, view=view)
                await view.wait()
                await msg.edit(view=None)

        # ===========================
        #  DEALER TURN
        # ===========================

        game.dealer_play()

        # ===========================
        #  PAYOUTS
        # ===========================

        total_result = 0
        for hand in game.hands:
            total_result += game.settle_hand(hand)

        user_data["balance"] += total_result
        user_data["last_blackjack"] = time.time()
        economy = self.bot.get_cog("EconomyCog")
        economy.save_economy_data()

        # Final embed
        title = "You Win!" if total_result > 0 else "You Lose!" if total_result < 0 else "Push"
        embed = build_hand_embed(ctx, game, reveal_dealer=True, title=title)
        await ctx.send(embed=embed)


# ============================
#  SETUP
# ============================

async def setup(bot):
    await bot.add_cog(Blackjack(bot))