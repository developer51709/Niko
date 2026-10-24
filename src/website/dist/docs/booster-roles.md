# Boost Notifications and Booster Roles

Niko can post a customized message when someone starts or stops boosting, and give active boosters their own server role to customize and share.

## Configure the feature

1. Open the [server dashboard](/dashboard) and choose **Boosters**.
2. Turn on **Post boost and unboost announcements** to enable notifications.
3. Choose a text channel and edit the boost and unboost message templates.
4. Turn on **Enable personal booster roles** to create roles for active boosters.
5. Save your changes.

The bot needs permission to send messages in the announcement channel. It also needs **Manage Roles**, and its highest role must stay above the personal booster roles.

## Message placeholders

Use these placeholders in either announcement template:

| Placeholder | What it inserts |
| --- | --- |
| `{user}` | The member's mention |
| `{name}` | The member's display name |
| `{server}` | The server name |
| `{boost_count}` | The server's current boost count |
| `{boost_level}` | The server's current boost level |

Niko disables role and everyone mentions in announcement templates. The `{user}` placeholder can mention the booster.

## Customize and share a role

Active boosters can use these commands:

```text
/boosterrole rename name:<name>
/boosterrole color hex_color:<#RRGGBB>
/boosterrole gradient first:<#RRGGBB> second:<#RRGGBB>
/boosterrole icon image:<PNG/JPEG>
/boosterrole clear-icon
/boosterrole share member:<member>
/boosterrole unshare member:<member>
```

Each role has no elevated permissions. A booster can change only the name, colors, and icon of their own role, and can assign or remove that role from other members. Role icons accept PNG or JPEG images up to 256 KB. Discord only allows custom role icons and gradient styles when the server has unlocked the corresponding boost perks.

When the role owner stops boosting or leaves the server, Niko deletes their personal role. That also removes it from every member it was shared with.
