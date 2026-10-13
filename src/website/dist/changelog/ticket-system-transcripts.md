# Ticket Transcripts & VoiceMaster

- Date: 2026-09-03
- Version: 2.6.0
- Tags: tickets, transcripts, voicemaster

The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.

## Highlights

### Web Transcript Viewer
Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.

### VoiceMaster Reliability
The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.

### Donation Dashboard Page
A new customization page in the dashboard lets server admins configure donation settings without using commands.

## Changes

### added
- Web-based ticket transcript viewer with styled HTML output
- Ticket transcript database table for storing transcripts online
- Dashboard customization page for donation system settings

### improved
- HTML download format for ticket transcripts
- VoiceMaster reliability and database usage patterns
- Ticket system persistence and data handling

### fixed
- Ticket transcript pages rendering incorrectly
- Ticket system data loss on restart
- Ticket transcript generation issues
- Ticket transcript page display bugs

## Commits
- e953321 Added a new web transcript feature to the ticket system
- aa0b73b Improved the donation system and added a customization page to the dashboard
- 3255385 Improved the html download format for the ticket transcripts
- 45f1fb0 Fixed the ticket system persistence
- ef4e057 Added the ticket system database migrations
- d4e0bc8 Fixed the ticket transcripts
- 4bf5e04 Fixed an issue with the ticket transcript pages
- e8dbcb0 Improved the VoiceMaster reliability and improved the database usage
