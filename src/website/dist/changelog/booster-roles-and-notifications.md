# Booster Roles and Boost Announcements

- Date: 2026-10-24
- Tags: boosters, roles, dashboard, notifications, added

Server admins can now customize boost and unboost announcements in the dashboard and enable personal roles for active boosters. Boosters can rename, recolor, add an eligible role icon, choose gradient colors when Discord unlocks them, and share or unshare their role.

## Highlights

### A Custom Thank-You for Every Boost
Choose the announcement channel and write separate messages for new and departing boosters. Templates support the member, server, boost count, and boost level.

### One Role for Each Active Booster
When enabled, Niko creates a permission-free role for each active booster. The owner can style that role and share it with other members.

### Role Styles Follow Discord's Perks
Custom icons and gradient role colors are available only when the server has unlocked the matching Discord boost features.

## Changes

### added
- A new Boosters dashboard section to enable notifications and roles per server
- Separate editable boost and unboost message templates with `{user}`, `{name}`, `{server}`, `{boost_count}`, and `{boost_level}` placeholders
- Automatic personal roles for active boosters and cleanup when a role owner stops boosting or leaves
- `/boosterrole` commands to rename, recolor, set or clear an icon, and share or unshare a personal role
- Solid colors, gradient colors, and role icons gated by Discord's server feature unlocks
- Public documentation for dashboard setup, supported placeholders, role commands, and cleanup behavior
