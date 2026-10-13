# Using the Web Dashboard

Open the [Niko dashboard](https://niko.sryze.cc/dashboard) and sign in with Discord. The dashboard lists servers that you can manage and where Niko is installed. Access is checked by the server, so a server not visible to your account cannot be configured from the dashboard.

## Select a Server

Choose a server from your dashboard's server list to open its settings. If it is missing, confirm that your Discord account has **Manage Server** permission and that Niko is currently in that server. Invite Niko first if necessary.

## Available Settings

The dashboard provides server overview and configuration views for supported features, including leveling, moderation and AutoMod, onboarding, logging, tickets, AI, and server customization. The exact sections shown depend on the installed bot version and available configuration. Use the matching Discord setup command if a setting is not exposed in the dashboard.

Changes are sent to Niko's API and validated before they are saved. If a save fails, review the error message, verify your server permissions, and retry after the bot is available.

## Security

- Use Discord OAuth on the official Niko website; never share your Discord password or bot token.
- Sign out on shared devices when finished.
- Dashboard access does not grant extra Discord permissions to Niko; the bot must already have the required server permissions.
- Only authorized server managers can change server settings.
