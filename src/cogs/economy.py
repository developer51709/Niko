# economy.py cog
# This cog handles the economy system for the bot.
# It includes commands for checking balance, transferring money, and more.

import discord
from discord.ext import commands
import random
import json
import os
import time
from utils import logging as log
from utils.paginator import PaginatedView, paginate
from utils.ai_config import get_personality
from config.emojis import get_emoji

MESSAGES = {
    "normal": {
        "en": {
            "balance": "{name}'s balance is {balance} coins.",
            "daily_wait": "You can only claim your daily reward once every 24 hours.",
            "daily_success": "You claimed your daily reward of {reward} coins!",
            "work_wait": "You can only work once every hour.",
            "work_success": "You worked and earned {reward} coins!",
        },
        "de": {
            "balance": "Das Guthaben von {name} beträgt {balance} Münzen.",
            "daily_wait": "Du kannst deine tägliche Belohnung nur alle 24 Stunden abholen.",
            "daily_success": "Du hast deine tägliche Belohnung von {reward} Münzen abgeholt!",
            "work_wait": "Du kannst nur einmal pro Stunde arbeiten.",
            "work_success": "Du hast gearbeitet und {reward} Münzen verdient!",
        }
    },
    "cafe": {
        "en": {
            "balance": "hey! {name} has {balance} coins in their pastry bag 🥐✨",
            "daily_wait": "patience, bestie! your daily treats aren't ready yet. try again in a bit ☕🍰",
            "daily_success": "yesss! you got your daily {reward} coins. go buy something cute! 🍬✨",
            "work_wait": "you're working too hard! take a coffee break and come back in an hour ☕💤",
            "work_success": "good job! you worked a shift and earned {reward} coins for the tip jar 🍯✨",
        },
        "de": {
            "balance": "hey! {name} hat {balance} Münzen in der Gebäcktasche 🥐✨",
            "daily_wait": "Geduld, Liebes! Deine täglichen Leckereien sind noch nicht fertig. Versuch es später nochmal ☕🍰",
            "daily_success": "yesss! Du hast deine täglichen {reward} Münzen bekommen. Geh dir was Schönes kaufen! 🍬✨",
            "work_wait": "Du arbeitest zu hart! Mach eine Kaffeepause und komm in einer Stunde wieder ☕💤",
            "work_success": "Gute Arbeit! Du hast eine Schicht gearbeitet und {reward} Münzen für das Trinkgeldglas verdient 🍯✨",
        }
    }
}

def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"

def msg(ctx, key, **kwargs):
    personality = get_personality(ctx)
    lang = get_lang(ctx)
    text = MESSAGES.get(personality, {}).get(lang, {}).get(key)
    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key, key)
    return text.format(**kwargs) if kwargs else text

# Prefix resolver (required for dynamic prefixes to work)
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

    # Fallback prefix if everything else fails
    return "."

class EconomyCog(commands.Cog):
    def __init__(self, bot):
       self.bot = bot
       self.economy_data = self.load_economy_data()

    # Create a directory for economy data if it doesn't exist
    if not os.path.exists("data/economy_data"):
        log.info("Economy", "economy_data directory not found. Creating directory...")
        os.makedirs("data/economy_data")
        log.success("Economy", "economy_data directory created successfully. Continuing...")

    # Load economy data from economy_data directory
    def load_economy_data(self):
        economy_data = {}
        if os.path.exists("data/economy_data"):
            for filename in os.listdir("data/economy_data"):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join("data/economy_data", filename), "r") as f:
                            user_id = filename[:-5]
                            economy_data[user_id] = json.load(f)
                    except Exception as e:
                        log.error("Economy", f"Error loading {filename}: {e}")
        return economy_data

    # Save economy data to economy_data directory per user
    def save_economy_data(self):
        if not os.path.exists("data/economy_data"):
            os.makedirs("data/economy_data")
        for user_id, data in self.economy_data.items():
            with open(os.path.join("data/economy_data", f"{user_id}.json"), "w") as f:
                json.dump(data, f, indent=4)

    # Get user economy data
    def get_user_economy_data(self, user_id):
        uid = str(user_id)
        if uid not in self.economy_data:
            self.economy_data[uid] = {
                "balance": 100, 
                "inventory": [], 
                "bank": 0, 
                "net_worth": 100, 
                "daily_streak": 0, 
                "last_daily": 0, 
                "last_work": 0, 
                "last_crime": 0, 
                "last_rob": 0, 
                "last_heist": 0, 
                "last_slots": 0, 
                "last_blackjack": 0, 
                "last_roulette": 0, 
                "last_casino": 0, 
                "last_gamble": 0, 
                "last_bet": 0, 
                "last_race": 0, 
                "last_fight": 0, 
                "last_duel": 0
            }
        
        # Ensure net_worth is always up to date
        self.economy_data[uid]["net_worth"] = self.economy_data[uid].get("balance", 0) + self.economy_data[uid].get("bank", 0)
        return self.economy_data[uid]

    # -----------------------------
    # Economy Commands
    # -----------------------------

    # !balance command
    @commands.command(name="balance", aliases=["bal", "wallet"], help="{ 'en': 'check your pastry bag balance 🥐✨', 'de': 'sieh nach, wie viele Münzen du hast' }")
    async def balance(self, ctx, member: discord.Member = None):
        '''Check your balance or another user's balance.'''
        target = member or ctx.author
        user_data = self.get_user_economy_data(target.id)
        balance = user_data["balance"]
        bank = user_data["bank"]
        prefix = await _resolve_prefix(self.bot, ctx)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('credit_card')} Wallet\nUser: {target.display_name}"
                ),
                discord.ui.TextDisplay(
                    content=f"-# **Tip:** Use `{prefix}deposit` to safely store your coins in the bank! 🏦✨️"
                ),
                accessory=discord.ui.Thumbnail(target.display_avatar.url)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"**Cash**\n{balance} 🥐\n**Bank**\n{bank} 🏦\n**Total**\n{user_data['net_worth']} ✨"
            ),
            accent_colour=discord.Colour(0xFFA500)
        )
        view.add_item(container)
        
        await ctx.send(view=view)

    # !daily command
    @commands.command(name="daily", help="{ 'en': 'claim your daily treats 🍬✨', 'de': 'hol dir deine täglichen Belohnungen' }")
    async def daily(self, ctx):
        '''Claim your daily reward.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        current_time = int(time.time())
        if current_time - user_data["last_daily"] < 86400:
            remaining = 86400 - (current_time - user_data["last_daily"])
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### ⏳️ Daily Reward Cooldown"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"Patience! Your treats are still baking. Try again in {hours}h {minutes}m. ☕🍰"
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)
        else:
            daily_reward = 1000
            user_data["balance"] += daily_reward
            user_data["last_daily"] = current_time
            self.save_economy_data()
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### 🍬 Daily Reward Claimed!"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=msg(ctx, "daily_success", reward=daily_reward)
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    # !work command
    @commands.command(name="work", help="{ 'en': 'work a shift at the café ☕', 'de': 'arbeite eine Schicht im Café' }")
    async def work(self, ctx):
        '''Work to earn money.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        current_time = int(time.time())
        if current_time - user_data["last_work"] < 3600:
            remaining = 3600 - (current_time - user_data["last_work"])
            minutes = remaining // 60
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### ⏳️ Work Cooldown"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"You're on break! Take it easy for another {minutes} minutes. ☕💤"
                )
            )
            view.add_item(container)
            return await ctx.send(view=view)
        else:
            work_reward = random.randint(50, 200)
            user_data["balance"] += work_reward
            user_data["last_work"] = current_time
            self.save_economy_data()
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### 🍯 Work Shift Complete!"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=msg(ctx, "work_success", reward=work_reward)
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    # !crime command
    @commands.command(name="crime", help="{ 'en': 'try to steal some extra treats 😈', 'de': 'versuch, ein paar extra Leckereien zu stibitzen' }")
    async def crime(self, ctx):
        '''Commit a crime to earn money.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        current_time = int(time.time())
        if current_time - user_data["last_crime"] < 3600:
            await ctx.send("The shopkeeper is watching! Wait an hour before trying anything sneaky again. 👮‍♂️")
        else:
            success = random.random() > 0.5
            if success:
                reward = random.randint(200, 500)
                user_data["balance"] += reward
                await ctx.send(f"You successfully swiped {reward} coins from the tip jar! 🍯✨")
            else:
                loss = random.randint(100, 300)
                user_data["balance"] = max(0, user_data["balance"] - loss)
                await ctx.send(f"Caught! You had to pay {loss} coins in fines. 😭👮‍♂️")
            
            user_data["last_crime"] = current_time
            self.save_economy_data()

    # !rob command
    @commands.command(name="rob", help="{ 'en': 'try to rob another user 🔫', 'de': 'versuch, einen anderen Nutzer auszurauben' }")
    async def rob(self, ctx, member: discord.Member):
        '''Rob another user to earn money.'''
        if member.id == ctx.author.id:
            return await ctx.send("You can't rob yourself, silly! ☕")
            
        user_data = self.get_user_economy_data(ctx.author.id)
        target_data = self.get_user_economy_data(member.id)
        current_time = int(time.time())
        
        if user_data["balance"] < 100:
            return await ctx.send("You need at least 100 coins to plan a robbery! 🥐")
        if target_data["balance"] < 100:
            return await ctx.send("They don't even have 100 coins... leave them alone! 😭")
            
        if current_time - user_data['last_rob'] < 3600:
            return await ctx.send("You're still laying low. Try again in an hour! 🕵️‍♂️")
            
        success = random.random() > 0.6
        if success:
            amount = random.randint(10, min(target_data["balance"], 500))
            user_data["balance"] += amount
            target_data["balance"] -= amount
            await ctx.send(f"Success! You robbed {member.display_name} and made off with {amount} coins! 💰✨")
        else:
            loss = 150
            user_data["balance"] = max(0, user_data["balance"] - loss)
            await ctx.send(f"Failed! You got caught and had to pay {loss} coins to {member.display_name} as apology. 😭🥐")
            target_data["balance"] += loss
            
        user_data["last_rob"] = current_time
        self.save_economy_data()

    # !pay command
    @commands.command(name="pay", help="{ 'en': 'share some treats with a friend 💸🥐', 'de': 'teile deine Leckereien mit einem Freund' }")
    async def pay(self, ctx, member: discord.Member = None, amount: int = None):
        '''pay another user 💸💰 | bezahl einen anderen Nutzer'''
        if not member:
            return await ctx.send("Please specify a user to pay. 🥐")
        if not amount or amount <= 0:
            return await ctx.send("Please specify a valid amount to pay. ☕")
        user_data = self.get_user_economy_data(ctx.author.id)
        target_data = self.get_user_economy_data(member.id)
        if user_data["balance"] < amount:
            await ctx.send("You don't have enough coins in your pastry bag! 🥐")
        else:
            user_data["balance"] -= amount
            target_data["balance"] += amount
            self.save_economy_data()
            await ctx.send(f"You gave {member.display_name} {amount} coins! 💸✨")

    # !leaderboard command
    @commands.command(name="leaderboard", aliases=["lb", "top"], help="{ 'en': 'see who has the most treats 🏆🥐', 'de': 'sieh nach, wer die meisten Leckereien hat' }")
    async def leaderboard(self, ctx):
        '''View the economy leaderboard.'''
        sorted_users = sorted(
            self.economy_data.items(),
            key=lambda x: x[1]["balance"] + x[1].get("bank", 0),
            reverse=True,
        )

        if not sorted_users:
            return await ctx.send("no one has any coins yet — the café is just opening! ☕")

        lines = []
        for i, (user_id, data) in enumerate(sorted_users, start=1):
            user = self.bot.get_user(int(user_id))
            name = user.mention if user else user_id
            total = data["balance"] + data.get("bank", 0)
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"**{i}.**")
            lines.append(f"{medal} {name} — {total:,}")

        pages = paginate(lines, per_page=10)
        view = PaginatedView(
            title="☕ café rich list 🥐✨",
            pages=pages,
            # icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # !shop command
    @commands.command(name="shop", help="{ 'en': 'browse the café boutique 🛍️✨', 'de': 'stöbere in der Café-Boutique' }")
    async def shop(self, ctx):
        '''View the shop.'''
        shop_items = {
            "coffee": {"name": "Premium Coffee", "price": 500, "description": "A warm cup of high-quality coffee."},
            "cake": {"name": "Strawberry Cake", "price": 1200, "description": "A delicious slice of strawberry cake."},
            "badge": {"name": "Café Regular Badge", "price": 5000, "description": "Show everyone you're a regular here!"}
        }
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="### Niko's Café Boutique 🛍️✨"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            accent_colour=discord.Colour(0xFFA500),
        )
        for item_id, item_data in shop_items.items():
            container.add_item(
                discord.ui.TextDisplay(
                    content=f"**{item_data['name']} — {item_data['price']} 🥐**\n{item_data['description']}"
                ),
            )
        view.add_item(container)
        await ctx.send(view=view)

    # !buy command
    @commands.command(name="buy", help="{ 'en': 'buy a treat from the shop 🍰✨', 'de': 'kauf dir eine Leckerei im Shop' }")
    async def buy(self, ctx, item_id: str = None):
        '''Buy an item from the shop.'''
        if not item_id:
            return await ctx.send("What would you like to buy? 🥐")
        user_data = self.get_user_economy_data(ctx.author.id)
        shop_items = {
            "coffee": {"name": "Premium Coffee", "price": 500},
            "cake": {"name": "Strawberry Cake", "price": 1200},
            "badge": {"name": "Café Regular Badge", "price": 5000}
        }
        item_id = item_id.lower()
        if item_id not in shop_items:
            await ctx.send("We don't have that in stock! 🥐")
        elif user_data["balance"] < shop_items[item_id]["price"]:
            await ctx.send("You don't have enough coins in your bag! 🥐")
        else:
            user_data["balance"] -= shop_items[item_id]["price"]
            user_data["inventory"].append(item_id)
            self.save_economy_data()
            await ctx.send(f"You bought a {shop_items[item_id]['name']}! Enjoy! 🍰✨")

    # !inventory command
    @commands.command(name="inventory", aliases=["inv"], help="{ 'en': 'check your collection of treats 🎒✨', 'de': 'sieh dir deine gesammelten Leckereien an' }")
    async def inventory(self, ctx):
        '''View your inventory.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        if not user_data["inventory"]:
            return await ctx.send("Your bag is empty! Go buy some treats! 🥐")
            
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"### {ctx.author.display_name}'s Bag 🎒"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            # blue accent colour
            accent_colour=discord.Colour(0x0000FF)
        )
        for item in user_data["inventory"]:
            container.add_item(
                discord.ui.TextDisplay(
                    content=f"**→ {item}**"
                )
            )
        view.add_item(container)
        await ctx.send(view=view)

    # !sell command
    @commands.command(name="sell", help="{ 'en': 'sell back a treat for some coins 💰', 'de': 'verkauf eine Leckerei gegen Münzen' }")
    async def sell(self, ctx, item_id: str = None):
        '''Sell an item from your inventory.'''
        if not item_id:
            return await ctx.send("What would you like to sell? 🥐")
        user_data = self.get_user_economy_data(ctx.author.id)
        shop_items = {
            "coffee": {"name": "Premium Coffee", "price": 250},
            "cake": {"name": "Strawberry Cake", "price": 600},
            "badge": {"name": "Café Regular Badge", "price": 2500}
        }
        item_id = item_id.lower()
        if item_id not in user_data["inventory"]:
            await ctx.send("You don't have that in your bag! 🥐")
        else:
            sell_price = shop_items.get(item_id, {"price": 50})["price"]
            user_data["balance"] += sell_price
            user_data["inventory"].remove(item_id)
            self.save_economy_data()
            await ctx.send(f"Sold your {item_id} for {sell_price} coins! 💰")

    # !bank command (Handled by balance embed, but kept for legacy)
    @commands.command(name="bank", help="{ 'en': 'check your vault balance 🏦', 'de': 'sieh dir dein Tresorguthaben an' }")
    async def bank(self, ctx):
        '''View your bank balance.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        await ctx.send(f"You have {user_data['bank']} coins safely tucked away in your vault! 🏦✨")

    # !deposit command
    @commands.command(name="deposit", aliases=["dep"], help="{ 'en': 'put coins in the safety vault 🏦', 'de': 'zahl Münzen in den Safe ein' }")
    async def deposit(self, ctx, amount: str):
        '''Deposit money into the bank.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        
        if amount.lower() == "all":
            amount = user_data["balance"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send("Please specify a valid number or 'all'! 🥐")
                
        if amount <= 0:
            return await ctx.send("You can't deposit nothing! ☕")
        if user_data["balance"] < amount:
            return await ctx.send("You don't have that many coins in your pastry bag! 🥐")
            
        user_data["balance"] -= amount
        user_data["bank"] += amount
        self.save_economy_data()
        await ctx.send(f"Deposited {amount} coins into your vault! 🏦✨")

    # !withdraw command
    @commands.command(name="withdraw", aliases=["with"], help="{ 'en': 'take coins from the vault 🥐', 'de': 'nimm Münzen aus dem Safe' }")
    async def withdraw(self, ctx, amount: str):
        '''Withdraw money from the bank.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        
        if amount.lower() == "all":
            amount = user_data["bank"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send("Please specify a valid number or 'all'! 🥐")
                
        if amount <= 0:
            return await ctx.send("You can't withdraw nothing! ☕")
        if user_data["bank"] < amount:
            return await ctx.send("You don't have that many coins in your vault! 🏦")
            
        user_data["bank"] -= amount
        user_data["balance"] += amount
        self.save_economy_data()
        await ctx.send(f"Withdrew {amount} coins from your vault! 🥐✨")

    # !networth command
    @commands.command(name="networth", aliases=["nw"], help="{ 'en': 'calculate your total café fortune 📊🥐', 'de': 'berechne dein gesamtes Café-Vermögen' }")
    async def networth(self, ctx):
        '''View your net worth.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        net_worth = user_data["balance"] + user_data["bank"]
        await ctx.send(f"Your total net worth is {net_worth} coins! You're quite the regular! 📊🥐✨")
        


async def setup(bot):
    await bot.add_cog(EconomyCog(bot))