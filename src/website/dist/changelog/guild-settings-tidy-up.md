# Server Settings Hand Tickets and Onboarding to Their Own Tabs

- Date: 2026-10-16
- Tags: dashboard, tickets, onboarding, customization, fixed

The ticket and onboarding settings are gone from the dashboard's Server tab now that both own a tab of their own, the ticket cards finally line up with every other settings page, and the Customization tab previews Niko's global avatar and banner for a server that has not set its own.

## Highlights

### One Home per Setting
Ticket panel settings live only in the Tickets tab and the welcome, rules and captcha setup lives only in the Onboarding tab, so the Server tab is now just command prefixes and logging destinations — the same screen with the same save button, minus the duplicates.

### A Preview That Shows the Real Niko
A server that has not uploaded its own avatar or banner sees Niko's global profile picture and banner in the live preview, and is told that it is inherited. Uploading or pasting an image still gives the server its own identity, and saving never writes Niko's global image into the server's profile.

## Changes

### improved
- The ticket configuration, live queue and transcript cards on the Tickets tab now share the dashboard's card spacing instead of being rendered outside the settings stack
- The Server tab's own description only mentions what it still configures

### fixed
- Removed the duplicated ticket panel and welcome/rules settings from the Server tab, which could previously disagree with the values saved on their own tabs
- The Customization tab no longer shows an empty placeholder for a server with no avatar or banner of its own
