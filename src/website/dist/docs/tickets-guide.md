# Ticket System Guide

Niko's ticket system lets members open private support channels when they need help. Everything is controlled from a single `.ticket` command group.

## How Tickets Work

1. You post a **ticket panel** in a channel (usually #support)
2. A member clicks **Create Ticket** on the panel and picks a category if you've configured any
3. Niko creates a private `ticket-<username>` channel visible only to that member and your support roles
4. You discuss the issue in the ticket, then close or delete it when done

## Setting Up the Panel

### Step 1: Open the Setup Panel

```
.ticket setup
```

Requires **Administrator** permission. This opens a panel with two buttons:

- **Configure Panel** — customize the title, description, accent color, and image
- **Post Panel Here** — post the public ticket panel in the current channel

### Step 2: Post the Panel

You can also post the panel manually at any time:

```
.ticket panel
```

This sends the ticket panel to the channel you run it in and remembers where it was posted.

## Managing Categories

Categories let members pick a reason for opening a ticket (e.g. "Billing", "Appeals", "Help").

```
.ticket category add <name>
.ticket category remove <name>
.ticket category list
```

If no categories are configured, tickets open under a default **General** category.

## Managing Support Roles

Support roles are the staff members who can see and manage tickets. Members with **Manage Channels** also count as support automatically.

```
.ticket support add <role>
.ticket support remove <role>
.ticket support list
```

## Working Inside a Ticket

Support members (and the ticket opener) can manage an open ticket with these commands:

| Command | Description |
|---------|-------------|
| `.ticket add <user>` | Grant another member access to this ticket |
| `.ticket remove <user>` | Revoke a member's access to this ticket |
| `.ticket rename <name>` | Rename the ticket channel |
| `.ticket claim` | Mark the ticket as claimed by you |
| `.ticket transcript` | Generate a web transcript of the ticket (see the [Web Transcripts](/docs/tickets-transcripts) guide) |
| `.ticket close` | Soft-close the ticket: members become read-only and the channel is renamed `closed-…` |
| `.ticket delete [seconds]` | Delete the ticket channel after a delay (1–30 seconds, default 5) |

## Best Practices

1. **Pick a support channel**: Keep the panel in a dedicated #support channel
2. **Add categories early**: Members understand why they're opening a ticket
3. **Assign support roles**: Make sure every staff member who should handle tickets has one
4. **Close before deleting**: Soft-close keeps a record of the conversation; generate a [web transcript](/docs/tickets-transcripts) before deleting for a permanent record
