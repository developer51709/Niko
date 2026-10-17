# Birthday System Guide

Niko's birthday system lets you track and celebrate member birthdays.

## Setting Your Birthday

### Add Your Birthday
```
.birthday set MM-DD
```

Example:
```
.birthday set 06-15
```

### Remove Your Birthday
```
.birthday remove
```

### Check Your Birthday
```
.birthday show
```

## Server Birthdays

### Today's Birthdays
See who has birthdays today:

```
.birthday today
```

### Upcoming Birthdays
See birthdays on the horizon:

```
.birthday upcoming
```

### Birthday Channel
Set a channel for birthday announcements:

```
.birthday channel <channel>
```

When someone has a birthday, Niko will announce it in this channel.

### Birthday Role
Automatically assign a role on someone's birthday:

```
.birthday role <role>
```

## Birthday Commands

| Command | Description |
|---------|-------------|
| `birthday set` | Set your birthday (MM-DD) |
| `birthday remove` | Remove your birthday |
| `birthday show` | Show a user's birthday |
| `birthday today` | Show today's birthdays |
| `birthday upcoming` | Show upcoming birthdays |
| `birthday channel` | Set announcement channel (admin) |
| `birthday role` | Set the birthday role (admin) |

## Tips

1. **Set a channel**: Dedicated birthday channel builds community
2. **Use custom messages**: Make announcements feel personal
3. **Encourage members**: Let members know they can set birthdays
4. **Celebrate monthly**: Consider a monthly birthday roundup
