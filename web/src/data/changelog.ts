export type ChangelogChart = {
  type: "bar" | "line" | "pie" | "comparison";
  title: string;
  data: { label: string; value: number; color?: string }[];
};

export type ChangelogEntry = {
  slug: string;
  title: string;
  date: string;
  version?: string;
  tags: string[];
  summary: string;
  highlights: {
    title: string;
    description: string;
    icon: string;
  }[];
  changes: {
    category: "added" | "improved" | "fixed" | "migrated";
    items: string[];
  }[];
  chart?: ChangelogChart;
  commits: string[];
};

export const CHANGELOG: ChangelogEntry[] = [
  {
    slug: "economy-leveling-overhaul",
    title: "Economy Items, Leveling Cards & Subcommands",
    date: "2026-09-08",
    version: "2.8.0",
    tags: ["economy", "leveling", "shop", "image-cards"],
    summary:
      "The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.",
    highlights: [
      {
        title: "New Shop Items",
        description:
          "Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).",
        icon: "chart",
      },
      {
        title: "Leveling Image Cards",
        description:
          "Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.",
        icon: "spark",
      },
      {
        title: "Leveling Subcommands",
        description:
          "All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.",
        icon: "settings",
      },
      {
        title: "Daily Streak Milestones",
        description:
          "Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.",
        icon: "utility",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Coinflip command with heads/tails call and double-or-nothing payout",
          "Rigged Coin shop item — gives 60/40 coinflip odds for one use",
          "Streak Insurance shop item — protects daily streak if you miss one day",
          "Double Down Token shop item — next gambling win pays 1.5x",
          "Lucky Horseshoe shop item — next work reward gets +10%",
          "Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards",
          "Image card rendering for `/leveling rank` with customizable accent and background",
          "Image card rendering for the leveling leaderboard",
          "Inventory display as an image card in the shop command",
          "Twemoji emoji rendering in economy card images",
          "Pagination buttons (◀ ▶) on the leveling leaderboard",
          "Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom",
        ],
      },
      {
        category: "improved",
        items: [
          "Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands",
          "Shop command visual layout with better font rendering on economy image cards",
          "Crime and rob commands now check for gambling_boost effect for 1.5x payout",
          "HTML download format for ticket transcripts",
          "Dashboard UI refinements",
        ],
      },
      {
        category: "fixed",
        items: [
          "Command name conflicts between leveling and other cogs",
          "Missing import in leveling cog after image card addition",
          "Duplicate command alias in leveling system",
          "Command name conflict in the gambling cog",
        ],
      },
    ],
    chart: {
      type: "bar",
      title: "New Shop Items & Their Effects",
      data: [
        { label: "Rigged Coin", value: 3000, color: "#c9a84c" },
        { label: "Streak Insurance", value: 4000, color: "#4a7fb5" },
        { label: "Double Down Token", value: 5000, color: "#d96545" },
        { label: "Lucky Horseshoe", value: 2500, color: "#66866f" },
      ],
    },
    commits: [
      "41d86fb Expanded the gambling and economy system",
      "bd6a09c Added image cards to the leveling system",
      "5307bb1 Moved the leveling commands to the levels subcommand",
      "dafd224 Added an image card to the inventory command",
      "49fc83b Added emoji rendering to the shop command",
      "0aca6ba Improved the shop command",
      "30c9735 Added better font rendering to the economy system image cards",
      "2b96835 Fixed a command name conflict",
      "158ad8f Fixed a command name conflict in the gambling cog",
      "d465598 Fixed a missing import",
      "1f24ffb Fixed a duplicate command alias",
    ],
  },
  {
    slug: "database-migration",
    title: "Database Migration to MongoDB",
    date: "2026-09-03",
    version: "2.7.0",
    tags: ["database", "mongodb", "migration", "infrastructure"],
    summary:
      "Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.",
    highlights: [
      {
        title: "Full MongoDB Migration",
        description:
          "Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.",
        icon: "settings",
      },
      {
        title: "Slash Command Sync Safeguard",
        description:
          "A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.",
        icon: "utility",
      },
      {
        title: "Proxy Integration",
        description:
          "A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.",
        icon: "shield",
      },
    ],
    changes: [
      {
        category: "migrated",
        items: [
          "Economy system — balances, banks, jobs, achievements, inventory",
          "Leveling system — XP, levels, role rewards, card customization",
          "Moderation system — warnings, mutes, automod config",
          "Ticket system — panels, transcripts, support roles",
          "Birthday system — dates, channels, messages",
          "AFK system — status, timestamps",
          "Sticky messages — content, channels",
          "Blacklist — users, words, filters",
        ],
      },
      {
        category: "added",
        items: [
          "MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations",
          "Proxy manager for shared hosting reliability",
          "Slash command sync safeguard to prevent redundant API calls",
          "Context menu command support in the sync utility",
        ],
      },
      {
        category: "fixed",
        items: [
          "MongoDB interpreter not translating all SQLite write patterns correctly",
          "Economy interest calculation after migration",
          "Birthday system data persistence",
          "Several database connection issues across various cogs",
          "Leveling database initialization issue",
        ],
      },
    ],
    chart: {
      type: "pie",
      title: "Systems Migrated to MongoDB",
      data: [
        { label: "Economy", value: 1, color: "#d96545" },
        { label: "Leveling", value: 1, color: "#66866f" },
        { label: "Moderation", value: 1, color: "#4a7fb5" },
        { label: "Tickets", value: 1, color: "#c9a84c" },
        { label: "Birthdays", value: 1, color: "#b07cc6" },
        { label: "AFK", value: 1, color: "#e0976e" },
        { label: "Sticky Msgs", value: 1, color: "#7ca898" },
        { label: "Blacklist", value: 1, color: "#8c918e" },
      ],
    },
    commits: [
      "c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes",
      "0d3aca5 Migrated the blacklist to the main database",
      "954ebac Migrated the birthday system to the main database",
      "5013d54 Migrated the warns and mutes to use the main database",
      "f29c217 Migrated the afk system to the main database",
      "5732b48 Migrated the sticky messages to use the main database",
      "b0524f1 Migrated the ticket system to the main database",
      "70e6d7a Fixed the sync util to support context commands and slash groups",
      "2c01817 Added a safeguard to prevent slash command syncs when all commands are already present",
      "121afcf Added a proxy integration to reduce downtime on shared hosting",
      "9f2f1fd Fixed several database issues across various cogs",
    ],
  },
  {
    slug: "ticket-system-transcripts",
    title: "Ticket Transcripts & VoiceMaster",
    date: "2026-09-03",
    version: "2.6.0",
    tags: ["tickets", "transcripts", "voicemaster"],
    summary:
      "The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.",
    highlights: [
      {
        title: "Web Transcript Viewer",
        description:
          "Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.",
        icon: "doc",
      },
      {
        title: "VoiceMaster Reliability",
        description:
          "The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.",
        icon: "utility",
      },
      {
        title: "Donation Dashboard Page",
        description:
          "A new customization page in the dashboard lets server admins configure donation settings without using commands.",
        icon: "settings",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Web-based ticket transcript viewer with styled HTML output",
          "Ticket transcript database table for storing transcripts online",
          "Dashboard customization page for donation system settings",
        ],
      },
      {
        category: "improved",
        items: [
          "HTML download format for ticket transcripts",
          "VoiceMaster reliability and database usage patterns",
          "Ticket system persistence and data handling",
        ],
      },
      {
        category: "fixed",
        items: [
          "Ticket transcript pages rendering incorrectly",
          "Ticket system data loss on restart",
          "Ticket transcript generation issues",
          "Ticket transcript page display bugs",
        ],
      },
    ],
    commits: [
      "e953321 Added a new web transcript feature to the ticket system",
      "aa0b73b Improved the donation system and added a customization page to the dashboard",
      "3255385 Improved the html download format for the ticket transcripts",
      "45f1fb0 Fixed the ticket system persistence",
      "ef4e057 Added the ticket system database migrations",
      "d4e0bc8 Fixed the ticket transcripts",
      "4bf5e04 Fixed an issue with the ticket transcript pages",
      "e8dbcb0 Improved the VoiceMaster reliability and improved the database usage",
    ],
  },
  {
    slug: "roleplay-music-status",
    title: "Roleplay, Music & Status Rotation",
    date: "2026-09-05",
    version: "2.5.0",
    tags: ["roleplay", "music", "status", "social"],
    summary:
      "The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.",
    highlights: [
      {
        title: "Roleplay Rewrite",
        description:
          "The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.",
        icon: "users",
      },
      {
        title: "Music Ghost Queue",
        description:
          "A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.",
        icon: "utility",
      },
      {
        title: "Status Rotation",
        description:
          "The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.",
        icon: "spark",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Status message rotation with configurable interval and activity types",
          "Persistent status panel command for the support server (owner only)",
          "Roleplay block feature to prevent specific users from being targeted",
          "Ghost queue feature — queue songs even when nothing is playing",
          "User context menu for roleplay actions (replaces per-action menus)",
          "YouTube channel name validation for notification system",
        ],
      },
      {
        category: "improved",
        items: [
          "Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons",
          "Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)",
          "Music node connection system and autoplay reliability",
          "Spotify playback quality",
          "Music cog restructured with better error handling",
        ],
      },
      {
        category: "fixed",
        items: [
          "Status rotator startup errors and activity conflicts",
          "on_ready event error handling and reliability",
          "Lavalink connection bug",
          "Roleplay prefix command handling",
          "Bluesky and Reddit notification delivery issues",
        ],
      },
    ],
    chart: {
      type: "bar",
      title: "Files Changed per Feature Area",
      data: [
        { label: "Roleplay", value: 3, color: "#d96545" },
        { label: "Music", value: 4, color: "#4a7fb5" },
        { label: "Status", value: 3, color: "#66866f" },
        { label: "Social", value: 2, color: "#c9a84c" },
      ],
    },
    commits: [
      "0c58178 Redesigned the roleplay cog",
      "6c4ee09 Fixed the roleplay prefix commands",
      "f1f8591 Added a roleplay block feature",
      "e01e3e4 Added status message rotation",
      "5e63e1d Added a persistent status panel",
      "ae7501a Restructured the music cog",
      "526813e Added a new ghost queue feature to the music cog",
      "6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback",
      "4264677 Fixed a lavalink connection bug",
      "d62ead8 Improved the social media notification system's emojis",
      "0f0305d Improved the social media notification formatting",
      "42069d4 Added proper channel name validation to the YouTube notification system",
    ],
  },
  {
    slug: "moderation-logging-dashboard",
    title: "Logging, Moderation & Documentation",
    date: "2026-09-07",
    version: "2.4.0",
    tags: ["logging", "moderation", "documentation", "dashboard"],
    summary:
      "Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.",
    highlights: [
      {
        title: "Image Attachments in Logs",
        description:
          "Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.",
        icon: "chart",
      },
      {
        title: "Avatar Change Tracking",
        description:
          "The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.",
        icon: "users",
      },
      {
        title: "Documentation Redesign",
        description:
          "The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.",
        icon: "doc",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Image attachments rendered in deleted message logs via MediaGallery",
          "Avatar change detection in Member logging with Section + Thumbnail display",
          "Startup economy cache that loads all users into memory for accurate leaderboards",
          "Error handler for role menu post buttons",
          "Full-text search with result highlighting in documentation",
          "Category filters and tag cloud in documentation",
          "Individual documentation article pages with table of contents",
        ],
      },
      {
        category: "improved",
        items: [
          "Logging system now supports media_urls, thumbnail_url, and files parameters",
          "Commands page expanded with better organization",
          "Dashboard UI refinements",
          "Economy interest feature — skips malformed records with non-integer user IDs",
        ],
      },
      {
        category: "fixed",
        items: [
          "Logging command issues",
          "Documentation command references",
          "Status device detection issue",
          "Status rotator conflicts between multiple status types",
          "on_ready event reliability with proper error handling",
        ],
      },
    ],
    commits: [
      "722a34f Added avatar updates to the logging cogs Member logs",
      "1d82ea1 Moved file attachments inside the main log message for the deleted message logs",
      "358d537 Added a startup economy cache to fix the leaderboard",
      "566e0c4 Improved the dashboard",
      "132bcbb Fully redesigned the documentation page",
      "4f7a89a Improved the commands page",
      "6d953b6 Fixed the logging command",
      "a202687 Fixed some documentation issues",
      "49d22ad Fixed the documentation command references",
      "52de287 Added an error handler to the post role menu button",
    ],
  },
  {
    slug: "website-launch-donation",
    title: "Website, Donation System & API",
    date: "2026-09-02",
    version: "2.3.0",
    tags: ["website", "donations", "api"],
    summary:
      "The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.",
    highlights: [
      {
        title: "Public Website",
        description:
          "A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.",
        icon: "spark",
      },
      {
        title: "Documentation Center",
        description:
          "The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.",
        icon: "doc",
      },
      {
        title: "Donation Dashboard",
        description:
          "Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.",
        icon: "settings",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Public website with landing page, documentation center, and command reference",
          "Donation system customization page in the dashboard",
          "Ticket transcript viewer web page",
          "Donate page with Oxapay integration",
        ],
      },
      {
        category: "improved",
        items: [
          "Flask API to use proper database calls instead of direct SQLite access",
          "Website commands page with expanded details",
          "Database layer reliability for production",
        ],
      },
      {
        category: "fixed",
        items: [
          "Flask API database call issues",
          "Several database-related bugs across cogs",
          "node_modules folder accidentally committed to repository",
        ],
      },
    ],
    commits: [
      "132bcbb Fully redesigned the documentation page",
      "aa0b73b Improved the donation system and added a customization page to the dashboard",
      "bd5e3be Expanded the website's commands page",
      "e266644 Fixed the flask API to use the proper database calls",
      "e99ed47 Fixed several database related issues",
      "c783514 Minor API fixes and improvements",
      "0df4478 Added the node_modules folder to the gitignore file",
    ],
  },
];

export function getChangelogBySlug(slug: string): ChangelogEntry | undefined {
  return CHANGELOG.find((entry) => entry.slug === slug);
}

export function getChangelogTags(): string[] {
  const tags = new Set<string>();
  CHANGELOG.forEach((entry) => entry.tags.forEach((tag) => tags.add(tag)));
  return Array.from(tags).sort();
}
