# Logging, Moderation & Documentation

- Date: 2026-09-07
- Version: 2.4.0
- Tags: logging, moderation, documentation, dashboard

Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.

## Highlights

### Image Attachments in Logs
Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.

### Avatar Change Tracking
The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.

### Documentation Redesign
The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.

## Changes

### added
- Image attachments rendered in deleted message logs via MediaGallery
- Avatar change detection in Member logging with Section + Thumbnail display
- Startup economy cache that loads all users into memory for accurate leaderboards
- Error handler for role menu post buttons
- Full-text search with result highlighting in documentation
- Category filters and tag cloud in documentation
- Individual documentation article pages with table of contents

### improved
- Logging system now supports media_urls, thumbnail_url, and files parameters
- Commands page expanded with better organization
- Dashboard UI refinements
- Economy interest feature — skips malformed records with non-integer user IDs

### fixed
- Logging command issues
- Documentation command references
- Status device detection issue
- Status rotator conflicts between multiple status types
- on_ready event reliability with proper error handling

## Commits
- 722a34f Added avatar updates to the logging cogs Member logs
- 1d82ea1 Moved file attachments inside the main log message for the deleted message logs
- 358d537 Added a startup economy cache to fix the leaderboard
- 566e0c4 Improved the dashboard
- 132bcbb Fully redesigned the documentation page
- 4f7a89a Improved the commands page
- 6d953b6 Fixed the logging command
- a202687 Fixed some documentation issues
- 49d22ad Fixed the documentation command references
- 52de287 Added an error handler to the post role menu button
