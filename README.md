<div align="center">

# ☕ **Niko Discord Bot**  
*A cozy, bilingual café‑themed companion for your server*

![Niko Banner](banner.png)

---

### **Badges**

![Python 3.10 Badge](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![discord.py Badge](https://img.shields.io/badge/discord.py-2.3-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![License Badge](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status Badge](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![TinyLlama Badge](https://img.shields.io/badge/Powered_by-TinyLlama-orange?style=for-the-badge)
![Platform Badge](https://img.shields.io/badge/Platform-Discord-5865F2?style=for-the-badge&logo=discord)

</div>

---

## 🌸 Overview
Niko is a warm, bilingual Discord bot powered by a local LLM (TinyLlama). With a soft café‑bestie personality, Niko chats naturally, remembers past interactions, and brings a lo‑fi aesthetic to any community.

---

## ✨ Features

### 🧠 AI & Personality
- **Local AI Personality** — Powered by TinyLlama‑1.1B for private, local inference  
- **Bilingual** — Fluent in English and German  
- **Multi‑Personality System** — Currently featuring a cozy café vibe  

### 🎮 Fun & Interaction
- **Economy System** — Pastries, daily rewards, work shifts, and more  
- **Gambling Games** — Blackjack, Slots, Roulette  
- **Mini‑Games** — Lighthearted fun for everyone  
- **Leveling System** — Earn XP and grow like a coffee bean  

### 🎶 Music
- **High‑Quality Music Player** — Powered by Lavalink with a cozy twist  

### 🛡️ Moderation
- **Moderation Tools** — Keep your server safe and tidy  
- **AutoMod** — Automated filters and protections  

---

## 📁 Project Structure

```
bot.py           → Main bot entry point + LLM integration
cogs/            → Modular features (Economy, Music, Leveling, etc.)
utils/           → Shared utilities (custom colored logging, helpers)
data/            → Persistent storage (levels, warns, configs)
economy_data/    → Per-user economy profiles
memory.json      → AI conversation memory
```

---

## 🚀 Setup & Running

1. Add your `DISCORD_BOT_TOKEN` to environment secrets  
2. On first run, the bot automatically downloads the TinyLlama model (~600MB)  
3. Use the **Discord Bot** workflow to start the application  

---

## 📜 Commands

### ☕ **Café Specials (AI & Leveling)**
- Mention **niko** or ping to chat  
- `!favor [@user]` — Check your vibe score  
- `!memory [@user]` — View Niko’s café notes  
- `!level` — Your cozy level stats  
- `!level-leaderboard` — Global cozy leaderboard  

### 🥐 **Pastry Shop (Economy)**
- `!balance` — Check your pastry bag  
- `!daily` — Claim daily treats  
- `!work` — Work a café shift  
- `!shop` / `!buy` / `!inventory` — Manage your goodies  

### 🎶 **Cozy Tunes (Music)**
- `!play <search>` — Brew a cozy track  
- `!queue` — View the playlist  
- `!stop` / `!skip` / `!pause` — Control the ambiance  

### 🌿 **Social (Roleplay)**
- `!hug <@user>` — Warm café hug  
- `!kill <@user>` — Playful chaos  

---

<div align="center">

*Niko — Making your Discord server cozier, one cup at a time.*

</div>

---

## 📝 To‑Do
- [ ] Improve AI response speed  
- [ ] Add reaction roles  
- [ ] Custom per‑server commands  
- [ ] Slash command support  
- [ ] QOTD feature  
- [ ] More gambling commands  
- [ ] Dashboard?