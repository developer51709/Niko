# Niko Discord Bot

## Overview

Niko is a Discord bot powered by a local LLM (TinyLlama) with a unique "femboy AI" personality. The bot responds when mentioned by name or pinged, maintains memory of user interactions, tracks favorability scores based on user behavior, and includes various utility features like an economy system and roleplay commands.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py with Cogs pattern**: The bot uses Discord.py's commands extension with a modular cog system for organizing functionality. Each feature category (economy, info, utility, roleplay, AI utilities) is separated into its own cog file under the `cogs/` directory.
- **Rationale**: Cogs provide clean separation of concerns and make it easy to add/remove features without modifying core bot code.

### AI/LLM Integration
- **Local LLM inference using ctransformers**: The bot runs TinyLlama-1.1B locally using ctransformers library rather than calling external APIs.
- **Model**: TinyLlama-1.1B-Chat GGUF format (Q4_K_M quantization, ~600MB)
- **Auto-download**: Model is downloaded from HuggingFace on first run if not present
- **Rationale**: Local inference provides free, unlimited AI responses without API costs or rate limits. The small model size allows running on modest hardware.

### Memory System
- **JSON-based persistent storage**: User interactions are stored in `memory.json` with three tracked dimensions:
  - `users`: Raw message history per user
  - `favorability`: Numeric score (-100 to 100+) tracking how much Niko "likes" each user
  - `conversations`: Structured conversation history with role/content pairs
- **Rationale**: Simple file-based storage is sufficient for this use case and requires no database setup.

### Economy System
- **Per-user JSON files**: Economy data stored in `economy_data/` directory with one JSON file per user ID
- **Features tracked**: balance, bank, inventory, net worth, cooldown timestamps for various actions (daily, work, crime, gambling, etc.)
- **Rationale**: Separate files per user prevent data corruption from affecting all users and make debugging easier.

### Personality System
- **System prompt engineering**: Niko's personality is defined through a detailed system prompt that instructs the LLM on behavior, speech patterns, and social dynamics
- **Favorability-aware responses**: The bot tracks positive/negative interactions and adjusts responses based on user favorability scores

## External Dependencies

### Discord API
- **discord.py**: Primary interface for Discord bot functionality
- **Requires**: `DISCORD_BOT_TOKEN` environment secret from Discord Developer Portal

### AI Model
- **ctransformers**: Local GGUF model inference library (CPU-based)
- **Model source**: HuggingFace (TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF)
- **Download**: Automatic on first run via requests library

### System Libraries
- **psutil**: System resource monitoring (used in info commands for bot statistics)
- **requests**: HTTP client for downloading the AI model

### Data Storage
- **Local filesystem**: All data persisted to JSON files (no external database required)
  - `memory.json`: AI memory and favorability
  - `economy_data/*.json`: Per-user economy state