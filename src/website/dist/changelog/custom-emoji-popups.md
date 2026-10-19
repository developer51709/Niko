# Custom Emojis Open Discord's Emoji Popup

- Date: 2026-10-19
- Tags: transcripts, customization, added

Click a custom emoji in a ticket transcript and Discord's emoji popup opens, with both layouts: an application emoji names the Niko app, while a server emoji shows the Nitro prompt and the server it came from. The standalone HTML download has the same popup.

## Highlights

### One Popup per Emoji Source
Niko's own emojis open the application layout, and every other custom emoji opens the server layout with the ticket server's icon and name. An emoji the CDN cannot resolve still stays the plain :name: text Discord shows.

### The Download Matches the Page
The shareable HTML transcript carries the same popup, positioning, click-away and Escape dismissal as the web transcript page, so a saved transcript feels like Discord too.

## Changes

### added
- Clicking a custom emoji in a ticket transcript or its HTML download opens Discord's emoji popup
- Application emojis name the Niko app, while server emojis show the Get Nitro prompt and the ticket server's identity
- Emoji popups reposition above or below the emoji and close on Escape or a click outside
