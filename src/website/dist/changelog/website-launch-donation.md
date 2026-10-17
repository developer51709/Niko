# Website, Donation System & API

- Date: 2026-09-02
- Version: 2.3.0
- Tags: website, donations, api

The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.

## Highlights

### Public Website
A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.

### Documentation Center
The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.

### Donation Dashboard
Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.

## Changes

### added
- Public website with landing page, documentation center, and command reference
- Donation system customization page in the dashboard
- Ticket transcript viewer web page
- Donate page with Oxapay integration

### improved
- Flask API to use proper database calls instead of direct SQLite access
- Website commands page with expanded details
- Database layer reliability for production

### fixed
- Flask API database call issues
- Several database-related bugs across cogs
- node_modules folder accidentally committed to repository

## Commits
- 132bcbb Fully redesigned the documentation page
- aa0b73b Improved the donation system and added a customization page to the dashboard
- bd5e3be Expanded the website's commands page
- e266644 Fixed the flask API to use the proper database calls
- e99ed47 Fixed several database related issues
- c783514 Minor API fixes and improvements
- 0df4478 Added the node_modules folder to the gitignore file
