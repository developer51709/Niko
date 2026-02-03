# Niko Discord Bot

## Overview
A Discord bot powered by a local LLM (TinyLlama) that has a unique personality. The bot responds when mentioned by name or pinged, and remembers interactions with users.

## Project Structure
- `bot.py` - Main bot code with Discord integration and LLM handling
- `requirements.txt` - Python dependencies
- `memory.json` - User memory storage (created at runtime)
- `*.gguf` - LLM model file (downloaded at first run)
- `\cogs` - This folder is for command cogs and are loaded dynamically when the bot is started

## Dependencies
- `discord.py` - Discord API wrapper
- `ctransformers` - Local LLM inference
- `requests` - HTTP requests for model download
- `colorama` - Adds colored terminal logs for more user friendly logging

## Configuration
The bot requires a `DISCORD_BOT_TOKEN` secret to be set. This is your Discord bot token from the Discord Developer Portal.

## Running
The bot runs as a console application. It will:
1. Download the TinyLlama model on first run (~600MB)
2. Load the model into memory
3. Connect to Discord and respond to messages

## Commands
- `!help` - See the full command list
<details>
  <summary>AI Commands</summary>
  <ul>
    <li>Mention "niko" in a message or ping the bot</li>
    <li><code>!ai &lt;message&gt;</code> - Direct message to the bot</li>
    <li><code>!favor [@user]</code> - Check favorability score</li>
  </ul>
</details>
<details>
  <summary>Economy Commands</summary>
  <ul>
    <li><code>!balance [@user]</code> - Check your balance or another user's balance.</li>
    <li><code>!bank</code> - View your bank balance.</li>
    <li><code>!buy &lt;item&gt;</code> - Buy an item from the shop.</li>
    <li><code>!crime</code> - Commit a crime to earn money.</li>
    <li><code>!daily</code> - Claim your daily reward.</li>
    <li><code>!deposit &lt;amount&gt;</code> - Deposit money into the bank.</li>
    <li><code>!inventory</code> - View your inventory.</li>
    <li><code>!leaderboard</code> - View the economy leaderboard.</li>
    <li><code>!networth</code> - View your net worth.</li>
    <li><code>!pay &lt;user_id&gt; &lt;amount&gt;</code> - Pay another user money.</li>
    <li><code>!rob &lt;user_id&gt;</code> - Rob another user to earn money.</li>
    <li><code>!sell &lt;item&gt;</code> - Sell an item from your inventory.</li>
    <li><code>!shop</code> - View the shop.</li>
    <li><code>!withdraw &lt;amount&gt;</code> - Withdraw money from the bank.</li>
    <li><code>!work</code> - Work to earn money.</li>
  </ul>
</details>
<details>
  <summary>Gambling Commands</summary>
  <ul>
    <li><code>!blackjack &lt;amount&gt;</code> - Play a game of blackjack</li>
    <li><code>!slots &lt;amount&gt;</code> - Play a game of slots</li>
  </ul>
</details>
<details>
  <summary>Info Cog</summary>
  <ul>
    <li><code>!about</code> - Get info about the bot</li>
    <li><code>!avatar [@user]</code> - View a users pfp</li>
    <li><code>!booststats</code> - View boost info for the server</li>
    <li><code>!creator</code> - Learn about the bot creator</li>
    <li><code>!debuginfo</code> - View debug info for the bot</li>
    <li><code>!hostinfo</code> - View info about the bots host</li>
    <li><code>!nyx</code></li>
    <li><code>!roleinfo [@role]</code> - View info about a role on the server</li>
    <li><code>!serverbanner</code> - View the server banner</li>
    <li><code>!servericon</code> - View the server icon</li>
    <li><code>!serverinfo</code> - View info about the server</li>
    <li><code>!serverstats</code> - View the server stats</li>
    <li><code>!spotify [@user]</code> - See what a user is listening to on spotify</li>
    <li><code>!userinfo [@user]</code> - View info about a user</li>
  </ul>
</details>
<details>
  <summary>Roleplay Cog</summary>
  <ul>
    <li><code>!fuck &lt;user_id&gt;</code> - Fuck another user. (not really)</li>
    <li><code>!hug &lt;user_id&gt;</code> - Hug another user. (not really)</li>
    <li><code>!kill &lt;user_id&gt;</code> - Kill another user. (not really)</li>
    <li><code>!makeout &lt;user_id&gt;</code> - Make out with another user. (not really)</li>
    <li><code>!rape &lt;user_id&gt;</code> - Rape another user. (not really)</li>
  </ul>
</details>
<details>
  <summary>Utility Cog</summary>
  <ul>
    <li><code>!boring</code></li>
    <li><code>!crazy</code></li>
    <li><code>!echo</code></li>
    <li><code>!nitro</code></li>
    <li><code>!notboring</code></li>
    <li><code>!partnership_request</code></li>
    <li><code>!ping</code></li>
    <li><code>!uwu</code></li>
  </ul>
</details>

## To-Do
- [ ] Add a better help command
- [ ] Fix the response speed
- [ ] Add a gambling cog