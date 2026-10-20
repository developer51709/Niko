# Giveaway Bans Keep Ban-Dodgers Out of Your Giveaways

- Date: 2026-10-20
- Tags: giveaway, moderation, commands, added

Servers can now ban a member from their giveaways with `.giveaway ban`, and lift it with `.giveaway unban`. A ban is per server, clears the entries the member already holds, and is enforced at the draw as well as on the Join button, so a banned member cannot win by entering before the ban or during a giveaway's final seconds.

## Highlights

### One Ban, Every Giveaway
The ban is stored against the server rather than one giveaway message, so every giveaway started afterwards refuses that member. It never removes them from the server — it only stops them entering giveaways.

### Entries Go With It
Banning a member also removes the entries they already hold in the server's active giveaways, so a ban is not just a rule for next time.

### Enforced at the Draw
The draw and the reroll both skip banned members. An entry that slips in while a giveaway is ending can no longer turn into a win.

## Changes

### added
- `.giveaway ban <member>` stops a member joining any giveaway in the server, backed by a per-server ban list
- `.giveaway unban <member>` lifts the ban again
- Banning a member clears the entries they already hold in the server's active giveaways
- The Join button, the draw and the reroll all refuse banned members, and the ban check runs before the join requirements

### improved
- Giveaway bans live in the giveaway schema and survive restarts, in both the SQLite and MongoDB backends
- The `.giveaway` help card lists the ban and unban commands
