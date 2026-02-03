# Niko Discord Bot

## Overview
A Discord bot powered by a local LLM (TinyLlama) that has a unique personality. The bot responds when mentioned by name or pinged, and remembers interactions with users.

## Project Structure
- `bot.py` - Main bot code with Discord integration and LLM handling
- `requirements.txt` - Python dependencies
- `memory.json` - User memory storage (created at runtime)
- `*.gguf` - LLM model file (downloaded at first run)

## Dependencies
- `discord.py` - Discord API wrapper
- `llama-cpp-python` - Local LLM inference
- `requests` - HTTP requests for model download

## Configuration
The bot requires a `DISCORD_BOT_TOKEN` secret to be set. This is your Discord bot token from the Discord Developer Portal.

## Running
The bot runs as a console application. It will:
1. Download the TinyLlama model on first run (~600MB)
2. Load the model into memory
3. Connect to Discord and respond to messages

## Commands
- Mention "niko" in a message or ping the bot
- `!ai <message>` - Direct message to the bot
- `!favor [@user]` - Check favorability score
- `!help` - See the full command list

## To-Do
- [ ] Add a better help command
- [ ] Fix the response speed
- [ ] Add a gambling cog