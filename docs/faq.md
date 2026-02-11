# Frequently Asked Questions (FAQ)

## 1. How do I change the bot prefix?
The command prefix can be changed by changing the `CMD_PREFIX` variable in the `bot.py` file around line 31.

## 2. How do I add the bot to my server?
You need to create an application in the [Discord Developer Portal](https://discord.com/developers/applications), enable the necessary intents (Server Members, Message Content), and generate an OAuth2 invite link with 'bot' and 'applications.commands' scopes.

## 3. Why are some commands not working?
Ensure the bot has the required permissions in your server (e.g., Manage Webhooks for `uwulock`). Also, make sure the "Message Content Intent" is enabled in the Discord Developer Portal.

## 4. How do I report a bug?
Please open an issue in the project repository or contact `@.n.y.x.e.n.` on Discord and provide any possible details about the issue.