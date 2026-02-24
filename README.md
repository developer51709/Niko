# Niko Discord Bot

![Niko Banner](banner.png)

## Overview
Niko is a cozy, bilingual Discord bot powered by a local LLM (TinyLlama). With a unique "café bestie" personality, Niko interacts with users, remembers past conversations, and brings a warm, lo-fi aesthetic to your server.

## Features
- **Local AI Personality**: Powered by TinyLlama-1.1B for private, local inference.
- **Bilingual Support**: Fully functional in both English and German.
- **Multi-Personality System**: Currently featuring a cozy "Café" vibe with themed responses.
- **Economy & Games**: A full economy system, gambling (Blackjack, Slots, Roulette), and fun mini-games.
- **Music Player**: High-quality music streaming via Lavalink with a cozy twist.
- **Leveling System**: Earn XP and level up like a growing coffee bean.
- **Moderation & AutoMod**: Powerful tools to keep your server safe and organized.

## Project Structure
- `bot.py` - Main bot entry point and LLM integration.
- `cogs/` - Modular feature sets (Economy, Music, Leveling, etc.).
- `utils/` - Shared utilities including a custom colored logging system.
- `data/` - Persistent storage for levels, warns, and server configs.
- `economy_data/` - Per-user economy profiles.
- `memory.json` - AI conversation memory.

## Setup & Running
1. **Secrets**: Add your `DISCORD_BOT_TOKEN` to the environment secrets.
2. **First Run**: The bot will automatically download the TinyLlama model (~600MB) on its first startup.
3. **Workflows**: Use the "Discord Bot" workflow to start the application.

## Commands
- `!help` - View the full interactive help menu.

### ☕ Café Specials (AI & Leveling)
- Mention "niko" or ping to chat!
- `!favor [@user]` - Check our vibe score ☕✨
- `!memory [@user]` - See my café notes on you ☕📝
- `!level` - Check your cozy level stats ☕
- `!level-leaderboard` - View the cozy leaderboard ☕

### 🥐 Pastry Shop (Economy)
- `!balance` - Check your pastry bag balance 🥐✨
- `!daily` - Claim your daily treats 🍬✨
- `!work` - Work a shift at the café ☕
- `!shop` / `!buy` / `!inventory` - Manage your café goodies.

### 🎶 Cozy Tunes (Music)
- `!play <search>` - Brew a cozy track for your ears ☕🎶
- `!queue` - See what’s on the cozy playlist ☕📜
- `!stop` / `!skip` / `!pause` - Manage the café ambiance.

### 🌿 Social (Roleplay)
- `!hug <@user>` - Give a big, warm café hug ☕💖
- `!kill <@user>` - Playfully take out a friend ☕💀

---
*Niko - Making your Discord server a little bit cozier, one cup at a time.*

## To-Do
- [ ] Fix the AI response speed
- [ ] Add reaction roles
- [ ] Add custom per server commands
- [ ] Add slash command support
- [ ] Add a qotd feature
- [ ] Add more gambling commands
- [ ] Add a dashboard?