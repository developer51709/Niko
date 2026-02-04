# economy.py cog
# This cog handles the economy system for the bot.
# It includes commands for checking balance, transferring money, and more.

import discord
from discord.ext import commands
import random
import json
import os
import time


class EconomyCog(commands.Cog):
    def __init__(self, bot):
       self.bot = bot
       self.economy_data = self.load_economy_data()

    # Create a directory for economy data if it doesn't exist
    if not os.path.exists("economy_data"):
        print("economy_data directory not found. Creating directory...")
        os.makedirs("economy_data")
        print("economy_data directory created successfully. Continuing...")

    # Load economy data from economy_data directory
    def load_economy_data(self):
        economy_data = {}
        if os.path.exists("economy_data"):
            for filename in os.listdir("economy_data"):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join("economy_data", filename), "r") as f:
                            user_id = filename[:-5]
                            economy_data[user_id] = json.load(f)
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        return economy_data

    # Save economy data to economy_data directory per user
    def save_economy_data(self):
        if not os.path.exists("economy_data"):
            os.makedirs("economy_data")
        for user_id, data in self.economy_data.items():
            with open(os.path.join("economy_data", f"{user_id}.json"), "w") as f:
                json.dump(data, f, indent=4)

    # Get user economy data
    def get_user_economy_data(self, user_id):
        uid = str(user_id)
        if uid not in self.economy_data:
            self.economy_data[uid] = {"balance": 0, "inventory": [], "bank": 0, "net_worth": 0, "daily_streak": 0, "last_daily": 0, "last_work": 0, "last_crime": 0, "last_rob": 0, "last_heist": 0, "last_slots": 0, "last_blackjack": 0, "last_roulette": 0, "last_casino": 0, "last_gamble": 0, "last_bet": 0, "last_race": 0, "last_fight": 0, "last_duel": 0}
        return self.economy_data[uid]

    # -----------------------------
    # Economy Commands
    # -----------------------------

    # !balance command
    @commands.command(name="balance")
    async def balance(self, ctx, member: discord.Member = None):
        '''Check your balance or another user's balance.'''
        target = member or ctx.author
        user_data = self.get_user_economy_data(target.id)
        balance = user_data["balance"]
        await ctx.send(f"{target.display_name}'s balance is {balance} coins.")

    # !daily command
    @commands.command(name="daily")
    async def daily(self, ctx):
        '''Claim your daily reward.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        current_time = int(time.time())
        if current_time - user_data["last_daily"] < 86400:
            await ctx.send("You can only claim your daily reward once every 24 hours.")
        else:
            daily_reward = 1000
            user_data["balance"] += daily_reward
            user_data["last_daily"] = current_time
            self.save_economy_data()
            await ctx.send(f"You claimed your daily reward of {daily_reward} coins!")

    # !work command
    @commands.command(name="work")
    async def work(self, ctx):
        '''Work to earn money.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        current_time = int(time.time())
        if current_time - user_data["last_work"] < 3600:
            await ctx.send("You can only work once every hour.")
        else:
            work_reward = random.randint(30, 100)
            user_data["balance"] += work_reward
            user_data["last_work"] = current_time
            self.save_economy_data()
            await ctx.send(f"You worked and earned {work_reward} coins!")

    # !crime command
    @commands.command(name="crime")
    async def crime(self, ctx):
        '''Commit a crime to earn money.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        current_time = int(time.time())
        if current_time - user_data["last_crime"] < 3600:
            await ctx.send("You can only commit a crime once every hour.")
        else:
            crime_reward = random.randint(-100, 200)
            if crime_reward < 0:
                await ctx.send(f"You were caught and lost {abs(crime_reward)} coins!")
            elif crime_reward == 0:
                await ctx.send("You got away with nothing.")
            else:
                await ctx.send(f"You successfully committed a crime and earned {crime_reward} coins!")
            user_data["balance"] += crime_reward
            user_data["last_crime"] = current_time
            self.save_economy_data()

    # !rob command
    @commands.command(name="rob")
    async def rob(self, ctx, member: discord.Member = None):
        '''Rob another user to earn money.'''
        if member is None:
            await ctx.send("Please specify a user to rob.")
            return
        user_data = self.get_user_economy_data(ctx.author.id)
        target_data = self.get_user_economy_data(member.id)
        current_time = int(time.time())
        if target_data["balance"] < 100:
            await ctx.send("You can't rob someone with less than 100 coins.")
        elif current_time - user_data['last_rob'] < 3600:
            await ctx.send("You can only rob someone once every hour.")
        else:
            rob_amount = random.randint(-200, 300)
            if rob_amount < 0:
                await ctx.send(f"You were caught and lost {abs(rob_amount)} coins!")
            elif rob_amount == 0:
                await ctx.send("You got away with nothing.")
            else:
                await ctx.send(f"You successfully robbed {member.display_name} and earned {rob_amount} coins!")
            user_data["balance"] += rob_amount
            target_data["balance"] -= rob_amount
            user_data["last_rob"] = current_time
            self.save_economy_data()

    # !pay command
    @commands.command(name="pay")
    async def pay(self, ctx, member: discord.Member = None, amount: int = None):
        '''Pay another user money.'''
        if not member:
            return await ctx.send("Please specify a user to pay.")
        if not amount:
            return await ctx.send("Please specify an amount to pay.")
        user_data = self.get_user_economy_data(ctx.author.id)
        target_data = self.get_user_economy_data(member.id)
        if user_data["balance"] < amount:
            await ctx.send("You don't have enough money to pay that amount.")
        else:
            user_data["balance"] -= amount
            target_data["balance"] += amount
            self.save_economy_data()
            await ctx.send(f"You paid {member.display_name} {amount} coins.")

    # !leaderboard command
    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        '''View the economy leaderboard.'''
        leaderboard = sorted(self.economy_data.items(), key=lambda x: x[1]["balance"], reverse=True)
        embed = discord.Embed(title="Economy Leaderboard", color=0x00ff00)
        for i, (user_id, data) in enumerate(leaderboard[:10]):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(name=f"{i+1}. {user.display_name}", value=f"Balance: {data['balance']} coins", inline=False)
            await ctx.send(embed=embed)

    # !shop command
    @commands.command(name="shop")
    async def shop(self, ctx):
        '''View the shop.'''
        shop_items = {
            "item1": {"name": "Item 1", "price": 100, "description": "This is item 1."},
            "item2": {"name": "Item 2", "price": 200, "description": "This is item 2."}
        }
        embed = discord.Embed(title="Shop", color=0x00ff00)
        for item_id, item_data in shop_items.items():
            embed.add_field(name=item_data["name"], value=f"Price: {item_data['price']} coins\nDescription: {item_data['description']}", inline=False)
            await ctx.send(embed=embed)

    # !buy command
    @commands.command(name="buy")
    async def buy(self, ctx, item_id: str = None):
        '''Buy an item from the shop.'''
        if not item_id:
            return await ctx.send("Please specify an item to buy.")
        user_data = self.get_user_economy_data(ctx.author.id)
        shop_items = {
            "item1": {"name": "Item 1", "price": 100, "description": "This is item 1."},
            "item2": {"name": "Item 2", "price": 200, "description": "This is item 2."}
        }
        if item_id not in shop_items:
            await ctx.send("That item does not exist.")
        elif user_data["balance"] < shop_items[item_id]["price"]:
            await ctx.send("You don't have enough money to buy that item.")
        else:
            user_data["balance"] -= shop_items[item_id]["price"]
            user_data["inventory"].append(item_id)
            self.save_economy_data()
            await ctx.send(f"You bought {shop_items[item_id]['name']} for {shop_items[item_id]['price']} coins.")

    # !inventory command
    @commands.command(name="inventory")
    async def inventory(self, ctx):
        '''View your inventory.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        shop_items = {
            "item1": {"name": "Item 1", "price": 100, "description": "This is item 1."},
            "item2": {"name": "Item 2", "price": 200, "description": "This is item 2."}
        }
        embed = discord.Embed(title="Inventory", color=0x00ff00)
        for item_id in user_data["inventory"]:
            embed.add_field(name=shop_items[item_id]["name"], value=f"Price: {shop_items[item_id]['price']} coins\nDescription: {shop_items[item_id]['description']}", inline=False)
            await ctx.send(embed=embed)

    # !sell command
    @commands.command(name="sell")
    async def sell(self, ctx, item_id: str = None):
        '''Sell an item from your inventory.'''
        if not item_id:
            return await ctx.send("Please specify an item to sell.")
        user_data = self.get_user_economy_data(ctx.author.id)
        shop_items = {
            "item1": {"name": "Item 1", "price": 100, "description": "This is item 1."},
            "item2": {"name": "Item 2", "price": 200, "description": "This is item 2."}
        }
        if item_id not in user_data["inventory"]:
            await ctx.send("You don't have that item in your inventory.")
        else:
            user_data["balance"] += shop_items[item_id]["price"]
            user_data["inventory"].remove(item_id)
            self.save_economy_data()
            await ctx.send(f"You sold {shop_items[item_id]['name']} for {shop_items[item_id]['price']} coins.")

    # !bank command
    @commands.command(name="bank")
    async def bank(self, ctx):
        '''View your bank balance.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        await ctx.send(f"You have {user_data['bank']} coins in your bank.")

    # !deposit command
    @commands.command(name="deposit")
    async def deposit(self, ctx, amount: int = None):
        '''Deposit money into the bank.'''
        if not amount:
            return await ctx.send("Please specify an amount to deposit.")
        user_data = self.get_user_economy_data(ctx.author.id)
        if user_data["balance"] < amount:
            await ctx.send("You don't have enough money to deposit that amount.")
        else:
            user_data["balance"] -= amount
            user_data["bank"] += amount
            self.save_economy_data()
            await ctx.send(f"You deposited {amount} coins into the bank.")

    # !withdraw command
    @commands.command(name="withdraw")
    async def withdraw(self, ctx, amount: int = None):
        '''Withdraw money from the bank.'''
        if not amount:
            return await ctx.send("Please specify an amount to withdraw.")
        user_data = self.get_user_economy_data(ctx.author.id)
        if user_data["bank"] < amount:
            await ctx.send("You don't have enough money in the bank to withdraw that amount.")
        else:
            user_data["bank"] -= amount
            user_data["balance"] += amount
            self.save_economy_data()
            await ctx.send(f"You withdrew {amount} coins from the bank.")

    # !networth command
    @commands.command(name="networth")
    async def networth(self, ctx):
        '''View your net worth.'''
        user_data = self.get_user_economy_data(ctx.author.id)
        net_worth = user_data["balance"] + user_data["bank"]
        await ctx.send(f"Your net worth is {net_worth} coins.")
        


async def setup(bot):
    await bot.add_cog(EconomyCog(bot))