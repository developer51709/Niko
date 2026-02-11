# Frequently Asked Questions (FAQ)

## 1. How do I change the bot prefix?
The prefix is typically configured in the `config.json` or through environment variables. Check the `main.py` file for the exact implementation.

## 2. How do I add the bot to my server?
You need to create an application in the [Discord Developer Portal](https://discord.com/developers/applications), enable the necessary intents (Server Members, Message Content), and generate an OAuth2 invite link with 'bot' and 'applications.commands' scopes.

## 3. Why are some commands not working?
Ensure the bot has the required permissions in your server (e.g., Manage Webhooks for `uwulock`). Also, make sure the "Message Content Intent" is enabled in the Discord Developer Portal.

## 4. How do I report a bug?
Please open an issue in the project repository or contact the bot administrator.