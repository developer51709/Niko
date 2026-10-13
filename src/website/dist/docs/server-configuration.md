# Server Configuration Basics

Proper server configuration ensures Niko works the way you want. This guide covers the essential settings.

## Access Settings

There are two ways to configure Niko:

1. **Discord Commands**: Use commands like `.automod`, `.logging`, or `/leveling config`
2. **Web Dashboard**: Visit the dashboard at `/dashboard` for a visual interface

## Essential Settings to Configure

### Welcome Messages
Set up welcome messages for new members:
```
.onboarding setup
```

### Logging Channels
Configure where moderation and event logs are sent:
```
.logging status
```

### Moderation Settings
Customize moderation behavior:
```
.automod
```

### Leveling Settings
Configure XP and leveling:
```
/leveling config
```

### Ticket Settings
Set up a support ticket system with categories and support roles:
```
.ticket setup
```

See the [Ticket System Guide](/docs/tickets-guide) for the full setup walkthrough.

## Setting Up Categories

For larger servers, consider setting up category-specific settings:

- Different welcome channels for different sections
- Separate log channels for different moderation types
- Custom leveling rates per channel
