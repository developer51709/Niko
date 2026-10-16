export type ChangelogDatum = {
  label: string;
  value: number;
  color?: string;
};

export type ChangelogChart =
  | { type: "bar"; title: string; data: ChangelogDatum[] }
  | { type: "pie"; title: string; data: ChangelogDatum[] }
  | { type: "line"; title: string; data: (ChangelogDatum & { detail?: string })[] }
  | { type: "timeline"; title: string; data: (ChangelogDatum & { detail?: string })[] }
  | {
      type: "donut";
      title: string;
      data: ChangelogDatum[];
      centerLabel?: string;
    }
  | {
      type: "comparison";
      title: string;
      before: ChangelogDatum[];
      after: ChangelogDatum[];
    }
  | {
      type: "metrics";
      title: string;
      data: { label: string; value: string; detail?: string; color?: string }[];
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
    slug: "blacklist-lockdown",
    title: "Blacklisting a Server Now Pauses Its Features Instead of Erasing Them",
    date: "2026-10-16",
    tags: ["blacklist", "moderation", "dashboard", "starboard", "polls", "giveaways", "added"],
    summary:
      "Blacklisting a server used to be one opaque database write. It is now a reported sequence of steps — save the entry, pause social notifications, disable the starboard, lock open polls and giveaways, notify the owner — each announced as it runs in the staff dashboard, followed by a summary of what was paused, skipped, or could not be switched off. Everything saved comes back untouched if the appeal is approved, and every disabled feature stays disabled across a bot restart.",
    highlights: [
      {
        title: "You Can See Every Step Happening",
        description:
          "The blacklist button walks through the six steps one request at a time, showing 'Saving to database…', 'Pausing social notifs…', 'Disabling starboard…', 'Disabling polls…', 'Disabling giveaways…' and 'Sending blacklist notification…' as progress toasts, then a success message and a summary panel grouped into paused, not in use, and needs attention.",
        icon: "shield",
      },
      {
        title: "Paused, Not Erased",
        description:
          "The starboard channel, open polls, active giveaways and the notifier switch are saved and switched off instead of deleted, so an approved appeal puts the server back exactly as it was. Only the social notifier stays off by design, because a server turns its own announcements back on in the dashboard.",
        icon: "refresh",
      },
      {
        title: "Off Means Off, Restart or Not",
        description:
          "Every disabled feature lives in the database rather than in memory: a blacklisted server keeps its locked polls, frozen giveaways and cleared starboard channel through a restart, and it stops receiving official staff broadcasts until the blacklist is lifted.",
        icon: "alert",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "A step-by-step guild lockdown in utils/guild_lockdown.py that reports each feature separately and never aborts the rest of the blacklist when one step fails",
          "Progress toasts, a success toast and a summary popup in the staff dashboard for both blacklist entry points, driven per step through /api/staff/guilds/<id>/blacklist/lockdown",
          "A guild_feature_locks record of what each step replaced, which is what unblacklisting or an approved appeal replays",
          "Locked polls and giveaways: votes and entries are refused with a localized 'paused' reply, and giveaway draws skip frozen rows",
          "A direct message to the server owner announcing the blacklist and where to appeal",
        ],
      },
      {
        category: "improved",
        items: [
          "The starboard, polls, giveaways and notifier all check the blacklist from persisted state, so a blacklisted server cannot keep using a feature through a component button or an in-flight message",
          "Official staff broadcasts skip blacklisted servers and report how many were skipped",
          "The poll and giveaway cogs migrate the new locked column at startup, so databases created before this change need no manual step",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "notifier-dashboard-tab",
    title: "Twitch Live Alerts and a Dashboard Tab for Social Notifications",
    date: "2026-10-16",
    tags: ["dashboard", "notifier", "social", "twitch", "added"],
    summary:
      "Twitch joins the social notifier, so a stream going live is announced in your channel through the same application credentials the team profile cards use — and every server now has a Notifications tab in the dashboard, where an account can be added by pasting a profile link, pointed at its own channel, ping role and custom message, tested, paused or resumed. The poll loop behind it got cheaper and more honest too: one request per creator no matter how many servers follow them, and an account that keeps failing is paused automatically instead of being retried forever.",
    highlights: [
      {
        title: "A Notifications Tab Per Server",
        description:
          "Dashboard → your server → Notifications shows every followed account as a card with its channel, ping role, custom message and health, plus Send test, Pause, Resume and Remove — no slash command needed.",
        icon: "guild_notifications",
      },
      {
        title: "Twitch Streams Go Live in Your Channel",
        description:
          "Twitch is a first-class notifier platform: a channel going live gets a live alert, and when it is offline Niko falls back to its newest broadcast, thumbnail included. Public channel data is read through an application (client-credentials) token from TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET — no user login, and the same credentials power the Twitch profile cards on the team page.",
        icon: "spark",
      },
      {
        title: "Paste a Link, Niko Does the Rest",
        description:
          "Pasting a profile URL pre-selects the platform, and the account is validated against the real platform API before anything is stored. A re-added account is updated rather than duplicated, and the newest post is seeded silently so a new follow never dumps a back catalogue.",
        icon: "link",
      },
      {
        title: "Feeds That Go Quiet Now Say So",
        description:
          "Each account records its last check and its consecutive failures. After five failed checks it is paused automatically and the channel is told once, with the command to resume it, instead of retrying a dead channel every five minutes.",
        icon: "alert",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "A per-server Notifications dashboard tab backed by /api/guild/<id>/notifier, sharing the cog's own platform validators so a follow added in the browser behaves exactly like one added in Discord",
          "Twitch as a notifier platform: a stream going live is announced as a live alert and falls back to the newest broadcast when the channel is offline, plus a Twitch button in the notifier setup panel",
          "TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET environment variables for Twitch app access, documented in the self-hosting guide and the notifier docs",
          ".notifier pause and .notifier resume for a single account, and a health line on .notifier list showing failed checks and the last check time",
          "A server-wide announcement switch with a default channel and default ping role, used by accounts that do not set their own",
          "Custom announcement messages with {account}, {platform}, {title} and {url} placeholders, validated before they are stored",
        ],
      },
      {
        category: "improved",
        items: [
          "The poll loop groups followed accounts by platform and handle, so several servers following the same creator cost one API request per cycle with a bounded number of requests in flight",
          "A failed check now resets on success and counts toward an automatic pause, so a deleted channel or blocked IP no longer looks like a working feed",
          "Follow storage moved into utils/social/follows, giving the cog, the slash commands and the dashboard one validated source of truth with per-server limits enforced in both places",
          "The Twitch credentials that authenticate the notifier are the same application credentials the team profile cards use, so one Twitch app registration covers both features",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "team-profile-cards",
    title: "Team Profiles Get Platform Cards and a Spotify Progress Bar",
    date: "2026-10-16",
    tags: ["team", "profiles", "notifier", "twitch", "added"],
    summary:
      "Staff profiles now draw a real profile card for every supported platform instead of a bare link — GitHub, Bluesky, Twitch, YouTube, Reddit and X — the Spotify status keeps the custom-status card layout with a live track progress bar, and Twitch joins the notifier using the same application credentials those cards use, so the credentials earn their keep twice.",
    highlights: [
      {
        title: "Every Link Is a Profile Card",
        description:
          "Find me elsewhere cards now show a platform badge, avatar, display name, handle, bio and headline stats for GitHub, Bluesky, Twitch, YouTube, Reddit and X. GitHub finally names itself instead of being an unlabelled card.",
        icon: "link",
      },
      {
        title: "Spotify Reads Like the Custom Status Card",
        description:
          "A listening status uses the same card as a custom status, and adds a progress bar with elapsed and total track time that ticks in real time from Discord's track window.",
        icon: "spark",
      },
      {
        title: "Twitch With Real Credentials",
        description:
          "The notifier tracks Twitch channels going live and new broadcasts through an application (client-credentials) token from TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET, and the team profile cards reuse that same credentials-backed lookup.",
        icon: "users",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Team profile cards for Bluesky, Twitch, YouTube, Reddit and X, resolved server-side through /api/team/profile-card with a short cache so the public page cannot hammer third-party APIs",
          "A Twitch notifier platform that announces a channel going live and falls back to the newest broadcast, plus a Twitch button in the notifier setup panel",
          "TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET environment variables for Twitch app access, documented in the self-hosting guide and the notifier docs",
          "A progress bar with elapsed and total time on the Spotify status card, driven by the track start and end timestamps from Discord's presence",
        ],
      },
      {
        category: "improved",
        items: [
          "The GitHub card carries a GitHub badge and label, and profile lookups it shares with the other platforms no longer depend on the visitor's browser CORS and rate limits",
          "X profiles are read from public endpoints instead of a paid API key, and Reddit falls back to its Atom feeds when its JSON API blocks a datacenter IP",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "personal-economy-tabs",
    title: "Economy & Achievements Move to Your Profile",
    date: "2026-10-14",
    tags: ["dashboard", "economy", "achievements", "fixed"],
    summary:
      "The dashboard's economy and achievements views now sit under My overview as personal tabs, because the Niko economy is one account-wide balance rather than something a server owns, and My servers finally separates the servers Niko is already in from the ones you can add it to.",
    highlights: [
      {
        title: "Tabs On Your Profile, Not a Server",
        description:
          "My overview now has Overview at /dashboard, Economy at /dashboard/me/economy and Achievements at /dashboard/me/achievements, all reading your global account: wallet, vault, level, job, global rank, recent ledger activity and your top.gg vote streak.",
        icon: "grid",
      },
      {
        title: "Nothing Server-Shaped Left",
        description:
          "The economy has no per-server settings to manage, so the only control that remains is the leaderboard privacy toggle on the personal Overview tab, and the server sidebar keeps just the sections that really do belong to a server.",
        icon: "shield",
      },
      {
        title: "My Servers Lists Your Servers",
        description:
          "The My servers tab showed every server as “Ready to add” whenever the dashboard process had no live gateway cache of Niko's guilds; it now also trusts the guild list Niko records at startup.",
        icon: "users",
      },
    ],
    changes: [
      {
        category: "improved",
        items: [
          "Economy and Achievements are now personal tabs under My overview instead of server sections, since the economy is global per Discord account",
          "The Economy tab shows global rank, worth, streaks and recent ledger activity, and rewards no longer require selecting a server to read",
          "The Achievements tab keeps every badge, its progress bar, its unlock state and the coins it paid",
          "Server sidebars list only sections that configure that server, and economy reads through /api/me/economy and /api/me/achievements",
        ],
      },
      {
        category: "fixed",
        items: [
          "My servers listed installed servers under “Add Niko to a server” because guild install state came only from the live gateway cache, which is empty on a standby instance or before the gateway's first sync; the dashboard now falls back to the guild list Niko writes at startup",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "economy-card-theme-refresh",
    title: "Economy & Leveling Cards Match the Website Theme",
    date: "2026-10-14",
    tags: ["economy", "leveling", "theme", "cards", "dashboard"],
    summary:
      "Every rendered economy and leveling image now uses the same graphite, steel and sage palette as the website and dashboard, retiring the warm café styling that outlived the site theme change.",
    highlights: [
      {
        title: "One Palette Everywhere",
        description:
          "Balance, reward, leaderboard, shop, inventory, coinflip, blackjack and level cards are drawn from the website's own theme tokens, so a card finally looks like a panel of the dashboard.",
        icon: "paint",
      },
      {
        title: "The Café Look Is Gone",
        description:
          "The espresso gradients, gold borders, coffee-cup placeholder avatar and café banner are replaced by a near-black graphite canvas with a steel accent and sage for money earned.",
        icon: "guild_economy",
      },
      {
        title: "Discord Views Followed",
        description:
          "Economy and shop containers now use the same brand accent as every other Niko view instead of their own café brown, so commands and cards match again.",
        icon: "spark",
      },
    ],
    changes: [
      {
        category: "improved",
        items: [
          "Economy, gambling and leveling image cards use the website theme palette: graphite surfaces, a steel accent for numerals, sage for money earned and a muted red for losses",
          "Card banners read “NIKO ECONOMY” and “NIKO LEVELING”, and the placeholder avatar is a neutral profile mark",
          "Server-configured level card colours still take precedence over the defaults",
        ],
      },
      {
        category: "fixed",
        items: [
          "The card palettes could drift from the site theme unnoticed; a test now pins every card colour to the stylesheet tokens",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "topgg-voting-rewards-and-achievements",
    title: "top.gg Voting Rewards & Café Achievements",
    date: "2026-10-14",
    tags: ["economy", "voting", "achievements", "dashboard", "streaks"],
    summary:
      "Voting for Niko on top.gg now pays coins and builds a streak that boosts your daily and work earnings, with a new set of badges to collect. Both the café standings and every badge are visible in two new dashboard tabs.",
    highlights: [
      {
        title: "Rewarded Votes",
        description:
          "Every counted top.gg vote credits coins and sends you a thank-you DM. Weekend votes pay double, and repeated webhook deliveries never pay out twice.",
        icon: "guild_economy",
      },
      {
        title: "Streaks That Pay Off",
        description:
          "Vote every 12 hours to build a streak of up to ten steps, raising your vote payout to 2.0x and your daily and work earnings to 1.5x. Missing a day restarts the streak, and the vote card in Discord and the dashboard both show where you stand.",
        icon: "chart",
      },
      {
        title: "Twenty-One Badges to Chase",
        description:
          "The café now tracks twenty-one achievements across work, banking, streaks, spending and voting. Each one pays its reward automatically the moment it unlocks, and the new Achievements tab shows progress bars for every badge you are still working on.",
        icon: "guild_achievements",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "top.gg vote webhook that credits coins, tracks streaks and sends a thank-you DM",
          "Streak multipliers for vote payouts and for daily and work earnings, with weekend vote doubling",
          "Seven voting badges covering total votes and vote streaks, plus fourteen existing café badges shown with progress and rewards",
          "Economy tab in the dashboard with wallet, vault, level, global and server ranks, recent ledger activity and the vote card",
          "Achievements tab in the dashboard listing locked and unlocked badges with progress bars",
          "`/vote` command with the listing link, streak status and current multipliers",
        ],
      },
      {
        category: "improved",
        items: [
          "Economy accounts persist their vote counters, so streaks survive restarts on both SQLite and MongoDB deployments",
          "Existing databases gain the vote counter columns automatically on startup",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "global-economy-leaderboard-privacy",
    title: "Global Economy Leaderboard & Privacy",
    date: "2026-10-13",
    tags: ["economy", "leaderboard", "privacy", "dashboard"],
    summary:
      "The public economy leaderboard is now a paginated global ranking, ranked by net worth, with a dashboard privacy control that lets members protect their identity without leaving the rankings.",
    highlights: [
      {
        title: "A Live, Paginated Rich List",
        description:
          "Browse global economy standings a page at a time, with stable ranks and net-worth totals across the full leaderboard.",
        icon: "chart",
      },
      {
        title: "Choose Your Visibility",
        description:
          "Members can make their leaderboard profile private from the dashboard. Private profiles remain ranked, while their identity is shown only to the account owner, official Niko staff, and people who share a guild with them.",
        icon: "shield",
      },
      {
        title: "Efficient Page Loading",
        description:
          "Leaderboard pages are fetched with bounded database-side pagination, keeping requests focused on the requested slice of rankings.",
        icon: "utility",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Public global economy leaderboard with net-worth rankings and previous/next pagination",
          "Dashboard economy privacy preference for hiding a member’s identity on the public leaderboard",
          "Privacy-aware identity visibility for account owners, official Niko staff, and mutual-guild members",
        ],
      },
      {
        category: "improved",
        items: [
          "Leaderboard loading uses bounded database-side pagination and retains global rank numbers between pages",
          "The Discord leaderboard command links directly to the public leaderboard page and explains its privacy behavior",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "dashboard-and-community-experience-refresh",
    title: "Dashboard & Community Experience Refresh",
    date: "2026-10-10",
    tags: ["dashboard", "website", "transcripts", "moderation", "staff", "accessibility"],
    summary:
      "A substantial platform update across Niko’s dashboard, public website, Discord integrations, and core bot systems. Guild admins get a redesigned server-profile editor and clearer analytics, while communities benefit from richer Discord-aware transcripts, expanded staff tools, and reliability improvements throughout moderation and data handling.",
    highlights: [
      {
        title: "Server Profile Studio",
        description:
          "Guild admins can preview and edit Niko’s server-specific name, bio, font, color effects, avatar, and banner in one focused editor. Image changes are applied to the Discord guild profile, and the dashboard resolves current images from Discord’s CDN instead of storing copies.",
        icon: "spark",
      },
      {
        title: "Discord-Aware Transcript Viewer",
        description:
          "Transcript pages and HTML exports better reflect Discord conversations, including resolved user, role, and channel mentions, custom emoji, stickers, timestamps, media, and richer message layouts.",
        icon: "doc",
      },
      {
        title: "A More Complete Public Experience",
        description:
          "The responsive website adds refined navigation, expanded documentation and command references, public team profiles, staff application flows, and clearer support and policy destinations, with polished route metadata and social previews.",
        icon: "users",
      },
      {
        title: "More Resilient Bot Operations",
        description:
          "Core bot updates improve database-backed persistence, moderation and automod workflows, ticket handling, staff tooling, and live dashboard statistics while tightening validation around server-scoped changes.",
        icon: "shield",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Interactive server-profile preview and editors for guild-specific display name, bio, typography, color effects, avatar, and banner",
          "Discord guild-profile image updates with avatar and banner CDN URL resolution; profile image data is excluded from persisted profile records",
          "Server pulse analytics with recent message and member activity plus server layout counts",
          "Public team directory and staff profile pages with Discord-synced identity and editable public profile details",
          "Guild staff-opening management and Discord-verified application forms with role eligibility checks",
          "Shared Discord text resolver for user, channel, and role mentions in transcript views and exports",
          "Route-aware social metadata, generated preview artwork, and expanded public documentation and command pages",
          "Dashboard controls for server AI identity and configurable experimental AI features",
        ],
      },
      {
        category: "improved",
        items: [
          "Dashboard and public navigation, responsive layouts, server settings, and profile editing flow",
          "Ticket transcript rendering and export fidelity for mentions, emoji, stickers, timestamps, attachments, and Discord message content",
          "Live public bot statistics and profile data sourced from the running bot and Discord where available",
          "Database-backed persistence and startup recovery across bot features, including moderation, economy, tickets, and community tools",
          "Automod reporting and review workflows, including scam-image detection and false-positive feedback",
          "Localization, request validation, access checks, and error handling across dashboard and bot interactions",
        ],
      },
      {
        category: "fixed",
        items: [
          "Dashboard TypeScript errors in the server-profile editing state",
          "Stale CDN image previews and accidental profile-image re-uploads during text-only profile saves",
          "Transcript mention and rich-content rendering gaps across online pages and downloadable HTML",
          "Dashboard and bot reliability issues surfaced while improving server configuration and persistence",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "scam-image-filter",
    title: "Scam Image Filter (Experimental)",
    date: "2026-10-01",
    tags: ["automod", "scam", "images", "experimental", "dashboard", "discord"],
    summary:
      "A community-driven image filter that catches known MrBeast scam images: members report suspicious messages, Niko staff verify them, and confirmed images are then detected and removed automatically — with a feedback loop that lets servers flag false positives to improve accuracy. The feature is still in early testing and may have some reliability issues.",
    highlights: [
      {
        title: "One-Click Reporting",
        description:
          "Anyone can right-click a suspicious message and choose “Report MrBeast Scam”. The message's image assets, author, server, and a jump link are forwarded to the scam review queue in Niko's private staff server.",
        icon: "users",
      },
      {
        title: "Perceptual Hash Detection",
        description:
          "Confirmed images are fingerprinted with a 64-bit difference hash and compared by visual similarity, so resized, re-compressed, and re-encoded copies of a known scam image are still caught — even when the file itself is different.",
        icon: "shield",
      },
      {
        title: "Staff-Verified Review Queue",
        description:
          "Nothing enters the filter automatically. Niko staff review each report and press Confirm Scam (or Reject). Multi-image reports store a fingerprint for every image, and confirmations work offline because hashes are captured at report time.",
        icon: "utility",
      },
      {
        title: "False-Positive Feedback Loop",
        description:
          "Every removal is logged to the server's automod log channel with the original images and a “Report False Positive” button. Reports land back in the staff queue where a “Remove From Filter” action deletes the hash, steadily improving accuracy.",
        icon: "message",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "“🚩 Report MrBeast Scam” message context-menu command that forwards image assets and context to the staff-only review channel",
          "Persistent Confirm Scam / Reject buttons on review reports that survive bot restarts, restricted to Niko staff",
          "Perceptual image fingerprinting (64-bit dHash with Hamming-distance matching) so re-encoded and resized scam variants are detected",
          "Automatic deletion of messages matching confirmed scam hashes in servers that enable the filter, with per-hash deletion counters",
          "Automod log channel entry for every removal, including the original image gallery and a Report False Positive button",
          "False-positive review cards with a Remove From Filter action so mis-detections can be pulled from the database",
          "Per-guild Scam Images toggle in the /automod command panel (all languages) and the dashboard's AutoMod modules",
          "Experimental badge and early-testing warning on both the command panel and the dashboard",
          "Dedicated database tables for confirmed scam hashes and report history, with counter tracking for deletions and false positives",
        ],
      },
      {
        category: "improved",
        items: [
          "Application-command error routing so every slash and context-menu failure now replies to the user instead of failing silently",
          "Automod log delivery works identically on both SQLite and MongoDB deployments",
          "Attachments no longer wake the AI on their own — images and voice only add context when Niko is triggered by name, ping, or command",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "staff-applications",
    title: "Staff Applications",
    date: "2026-09-29",
    tags: ["applications", "staff", "dashboard", "discord"],
    summary:
      "Guild dashboards can now manage multiple staff role openings with shareable web forms, Discord membership and eligibility checks, and reusable application links.",
    highlights: [
      {
        title: "Multiple Role Openings",
        description:
          "Create a separate application for each role, add custom questions, and optionally limit applications to members with selected server roles.",
        icon: "users",
      },
      {
        title: "Reusable Application Links",
        description:
          "Close an opening when hiring pauses and reopen it later with the same link. Earlier responses remain saved, and each Discord account can apply only once per opening.",
        icon: "utility",
      },
      {
        title: "Verified Applicant Forms",
        description:
          "Applicants sign in with Discord, and Niko verifies server membership and role eligibility before accepting a response. Managers can review submissions in the guild dashboard.",
        icon: "shield",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Guild dashboard tab to create and manage staff application openings",
          "Custom application questions and optional role-based eligibility gates",
          "Public Discord-authenticated application forms with bot-verified server membership",
          "Stable per-opening application links, close/reopen controls, and response review",
          "Database-enforced one-submission-per-user limit for each opening",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "server-logging-onboarding-updates",
    title: "Logging Reliability & Onboarding Rules",
    date: "2026-09-29",
    tags: ["logging", "onboarding", "dashboard"],
    summary:
      "Server event logs are less likely to be delayed during busy periods, and onboarding now gives communities more room to share their rules with new members.",
    highlights: [
      {
        title: "More Reliable Server Logs",
        description:
          "Server event logs are less likely to be delayed during busy periods, helping moderation and activity updates stay easier to follow.",
        icon: "utility",
      },
      {
        title: "Longer Onboarding Rules",
        description:
          "Server rules in onboarding can now be up to 4,000 characters, making it easier to share complete guidelines with new members.",
        icon: "doc",
      },
    ],
    changes: [
      {
        category: "improved",
        items: [
          "Server event log delivery reliability during busy periods",
          "Onboarding rules support for up to 4,000 characters",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "uwulock-starboard-overhaul",
    title: "UwU Lock Rebuilt & Starboard Persistence",
    date: "2026-09-25",
    version: "2.11.0",
    tags: ["uwulock", "starboard", "database", "fun", "social"],
    summary:
      "The UwU Lock command has been completely rebuilt around the main database with immediate webhook reposts, reliable message transforms, and full Starboard integration — with proper author attribution that persists cleanly across restarts.",
    highlights: [
      {
        title: "Instant Webhook Transforms",
        description:
          "Locked users' messages are now deleted and immediately reposted via a shared per-channel webhook with their display name and avatar, including attachments, embeds, and stickers, with thread support and a guard against double-processing.",
        icon: "spark",
      },
      {
        title: "Real Author on the Starboard",
        description:
          "When a uwu-ified webhook message is starred, the Starboard resolves the original author from persistent attribution and renders their name, avatar, and original timestamp — not the webhook — in a clean Section with Thumbnail layout.",
        icon: "users",
      },
      {
        title: "Survives Restarts",
        description:
          "Both UwU Lock rules and Starboard configuration now live in the main database, loaded on startup via cog_load with automatic migration from the legacy JSON files and stale-webhook healing.",
        icon: "settings",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Main-database tables uwulock_config and uwulock_messages for lock rules and author attribution",
          "Main-database tables starboard_config and starboard_messages for channel, threshold, emoji and post mappings",
          "Automatic migration of legacy data/uwulock.json and data/starboard.json into the primary database with .migrated backups",
          "Per-channel webhook reuse with stale-webhook detection via fetch and shared-webhook protection on removal",
          "Thread-aware webhook sending with AllowedMentions.none and wait:true repost handling",
          "UwU attribution storage (author name, avatar, original timestamp) for every transformed message",
          "Starboard Section + Thumbnail rendering for uwu-locked messages with correct original author credit",
          "Explicit UwU lock hook in events.on_message before AI triggers with a 2,000-entry dedup guard and fallback listener",
        ],
      },
      {
        category: "improved",
        items: [
          "UwU Lock now deletes the original message immediately instead of queuing for a background task",
          "Attachment, embed, and sticker handling with text truncation and text-only fallback on send failure",
          "Permission checks for Manage Messages and Manage Webhooks with localized failure messaging",
          "Starboard reaction handling now distinguishes webhook reposts via database attribution",
          "Starboard message edits and sends now use AllowedMentions.none for cleaner output",
          "Webhook Channel resolution for threads via parent channel with robust create_webhook flow",
        ],
      },
      {
        category: "fixed",
        items: [
          "UwU Lock not creating the webhook or showing any sign it saw the message",
          "Webhook created but original message not deleted and no new message sent",
          "UwU transforms silently failing due to queue delay and background-task errors",
          "Starboard not displaying correct author for uwu-locked webhook messages",
          "Starboard and UwU Lock losing all state after a restart despite being stored",
          "Stale or deleted webhooks leaving lock rules in a broken state",
        ],
      },
      {
        category: "migrated",
        items: [
          "UwU Lock from data/uwulock.json file storage to the primary database",
          "Starboard configuration and starred post IDs from data/starboard.json to the primary database",
        ],
      },
    ],
    chart: {
      type: "metrics",
      title: "Release At a Glance",
      data: [
        { label: "Added", value: "8", detail: "new persistence features", color: "#66866f" },
        { label: "Improved", value: "6", detail: "reliability upgrades", color: "#4a7fb5" },
        { label: "Fixed", value: "6", detail: "workflow bugs", color: "#d96545" },
      ],
    },
    commits: [],
  },
  {
    slug: "guild-server-pulse-stats",
    title: "Guild Server Pulse Stats",
    date: "2026-09-24",
    tags: ["dashboard", "guild", "analytics", "stats"],
    summary:
      "Guild settings now include a Server pulse analytics card with an at-a-glance view of server size and recent community activity.",
    highlights: [
      {
        title: "Server Activity at a Glance",
        description:
          "The card summarizes member count, messages, and new members over the last 14 days, with interactive views for message trends, member joins and departures, and the server's members, channels, and roles.",
        icon: "chart",
      },
      {
        title: "Community Analytics",
        description:
          "Daily activity charts make it easier to spot changes in conversation and membership, with activity tracking noted from the time it is enabled.",
        icon: "users",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Server pulse analytics card in guild settings",
          "14-day daily message activity and member join/leave charts",
          "Server layout view for member, channel, and role counts",
        ],
      },
    ],
    commits: [],
  },
  {
    slug: "team-page-ai-name-config",
    title: "Team Profiles & Custom AI Names",
    date: "2026-09-22",
    version: "2.10.0",
    tags: ["team", "staff", "dashboard", "ai", "website"],
    summary:
      "Niko's public website now introduces the people behind the bot, while server owners can give their AI a custom name and manage its experimental capabilities from the dashboard.",
    highlights: [
      {
        title: "Meet the Niko Team",
        description:
          "The new Team page showcases owners, developers, moderators, support staff, and other persisted staff roles with Discord-synced identities, presence, activities, bios, and profile pages.",
        icon: "users",
      },
      {
        title: "Choose Your AI's Name",
        description:
          "Server administrators can configure the AI's display name from the dashboard or the AI configuration command. The chosen name is used for mention detection and reply identity in that server.",
        icon: "spark",
      },
      {
        title: "Staff Public Listings",
        description:
          "Staff members can customize their public bio, banner, and visibility while their name and avatar remain synchronized with Discord.",
        icon: "settings",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Public Team page with persisted staff roles and linked staff profiles",
          "Discord-synced staff presence, current activities, Spotify, streaming, and custom status display",
          "Staff self-service controls for public bio, banner, and Team page visibility",
          "Configurable per-server AI name in the dashboard and AI configuration command",
          "Dashboard controls for AI Actions, Better Context, and Multimodal Conversation experiments",
          "Learn-more dialogs explaining each AI experiment",
        ],
      },
      {
        category: "improved",
        items: [
          "Dashboard staff workspace navigation and responsive layout",
          "Team profile cards and profile-page activity presentation",
          "AI configuration persistence through the shared database",
          "Public page metadata and favicon handling during the website build",
        ],
      },
      {
        category: "fixed",
        items: [
          "Team presence labels showing online staff as away",
          "Spotify and streaming activities being hidden behind custom statuses",
          "Staff profile updates being rejected for authorized owners",
          "Staff profile avatars being clipped by profile banners",
        ],
      },
    ],
    chart: {
      type: "metrics",
      title: "Release At a Glance",
      data: [
        { label: "Team", value: "1", detail: "new public experience", color: "#66866f" },
        { label: "AI", value: "4", detail: "new configuration controls", color: "#d96545" },
        { label: "Profiles", value: "3", detail: "public staff controls", color: "#4a7fb5" },
      ],
    },
    commits: [],
  },
  {
    slug: "september-platform-updates",
    title: "September Platform Updates",
    date: "2026-09-21",
    version: "2.9.0",
    tags: ["dashboard", "ai", "tickets", "music", "website"],
    summary:
      "A broad set of public improvements landed across Niko: richer ticket transcripts, a multimodal AI experiment, more reliable music playback, a redesigned dashboard experience, persistent giveaways and suggestions, and a refreshed public website with dynamic social previews.",
    highlights: [
      {
        title: "More Natural AI Conversations",
        description:
          "The new opt-in Multimodal Conversation experiment can understand image attachments and transcribe voice messages before generating a reply, while safely falling back to text when media processing is unavailable.",
        icon: "spark",
      },
      {
        title: "Richer Ticket Transcripts",
        description:
          "Transcript pages and HTML downloads now render Discord custom emojis, stickers, and dynamic timestamps such as <t:1788800225:f> in a more faithful format.",
        icon: "doc",
      },
      {
        title: "Dashboard & Website Refresh",
        description:
          "Dashboard navigation and mobile layouts were refined, documentation was expanded, and public routes now receive route-specific Open Graph cards generated during the build.",
        icon: "settings",
      },
      {
        title: "Reliable Long-Running Features",
        description:
          "Giveaways and suggestions now restore their state from the main database at startup, while music nodes are rescanned periodically to keep playback available.",
        icon: "utility",
      },
    ],
    changes: [
      {
        category: "added",
        items: [
          "Opt-in Multimodal Conversation AI experiment for image understanding and voice-message transcription",
          "Official update notification system with a configurable server notification channel",
          "Discord custom emoji and sticker rendering in ticket transcript pages and HTML downloads",
          "Dynamic Discord timestamp rendering in ticket transcripts",
          "Persistent suggestion configuration and voting buttons restored from the main database",
          "Automatic hourly Lavalink node rescans with a hardcoded fallback node catalog",
          "Additional economy SVG card API endpoints",
          "Community Policy page on the public website",
          "Route-specific Open Graph metadata and generated social preview cards",
        ],
      },
      {
        category: "improved",
        items: [
          "Dashboard navigation consistency and mobile layout",
          "Dashboard page layout and visual polish",
          "Music connection reliability, autoplay, Spotify playback, and node recovery",
          "Giveaway persistence and startup restoration for MongoDB-backed data",
          "Onboarding setup handling and configuration persistence",
          "Poll command design and interaction flow",
          "Ticket transcript HTML download formatting",
          "Economy image-card font rendering, SVG output, and emoji support",
          "Documentation pages and public website frontend",
        ],
      },
      {
        category: "fixed",
        items: [
          "Giveaways losing their live buttons after a restart or extended runtime",
          "Suggestion buttons and configuration not surviving process restarts",
          "Ticket transcript rendering for custom media and dynamic timestamps",
          "Lavalink connection failures and stale music nodes",
          "Broken SVG card and SVG endpoint output",
          "Status panel polling noise and retired image-model defaults",
        ],
      },
    ],
    chart: {
      type: "metrics",
      title: "Release At a Glance",
      data: [
        { label: "Added", value: "9", detail: "new capabilities", color: "#66866f" },
        { label: "Improved", value: "9", detail: "upgraded systems", color: "#4a7fb5" },
        { label: "Fixed", value: "6", detail: "reliability issues", color: "#d96545" },
      ],
    },
    commits: [
      "ac102df Fixed the Open Graph image cards",
      "33aaf12 Added dynamic Open Graph tags to the website",
      "3153e28 Rebuilt the frontend",
      "bab665e Added a new Lavalink node",
      "ee44a5e Improved the music cog",
      "bc61e34 Released the new Multimodal Conversation AI experiment",
      "c46af7d Fixed the suggestion system persistence",
      "25703ca Added a broadcast system for official updates and announcements",
      "265bdb2 Added dynamic timestamp rendering inside ticket transcripts",
      "d8005db Added custom emoji and sticker rendering to ticket transcripts",
      "e561d84 Fixed the dashboards navbar",
      "a0bab78 Improved the dashboards mobile layout",
      "fb2f5aa Patched giveaway persistence for MongoDB compatibility",
      "d77779e Fixed several dashboard flaws",
      "b8e06a5 Improved the dashboard pages",
      "3708207 Patched issues in the giveaway and onboarding cogs",
      "d58bb37 Redesigned the poll command",
      "bb523e3 Added a Community Policy page",
      "5b34c7c Updated the documentation pages",
      "3a52fc2 Added new economy card API endpoints",
      "df3ea25 Fixed an issue in the SVG endpoints",
      "39b7340 Fixed an error in the SVG cards",
      "9e3483e Replaced HTML entities with valid XML numeric character references in economy cards",
    ],
  },
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
      type: "donut",
      title: "Systems Migrated to MongoDB",
      centerLabel: "8 systems",
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
