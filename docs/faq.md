# Frequently Asked Questions (FAQ)

## 1. How do I change the bot prefix?
Use the `.prefix` command in your server and then add or remove prefixes using the interactive buttons

## 2. How do I add the bot to my server?
The instructions are different depending on if you are trying to add a self-hosted instance or the official hosted instance.
**Official:** Use the link found in the `README.md` file in this repository.
**Self-hosted:** You need to create an application in the [Discord Developer Portal](https://discord.com/developers/applications), enable the necessary intents (Server Members, Message Content), and generate an OAuth2 invite link with 'bot' and 'applications.commands' scopes.

## 3. Why are some commands not working?
Ensure the bot has the required permissions in your server (e.g., Manage Webhooks for `uwulock`). Also, make sure the "Message Content Intent" is enabled in the Discord Developer Portal if you are self-hosting the bot.

## 4. How do I report a bug?
Please open an issue in the project repository or contact `@sorenthedev` on Discord and provide any possible details about the issue.