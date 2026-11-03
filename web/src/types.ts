export type BotStats = {
  guild_count: number;
  user_count: number;
  command_count: number;
  uptime_since: string | null;
  version: string;
  economy_users: number;
};

/** `/api/status` — what the public status page polls while it is open. */
export type StatusState = "operational" | "degraded" | "maintenance" | "starting" | "offline";
export type CogState = "loaded" | "disabled" | "maintenance" | "failed";

export type StatusCog = {
  name: string;
  label: string;
  state: CogState;
  reason: string | null;
  commands: number;
};

export type StatusShard = {
  id: number;
  /** Null when the shard has not answered yet, which is not the same as 0 ms. */
  latency_ms: number | null;
  connected: boolean;
  /** Connected but still syncing: the page says so instead of calling it slow. */
  starting?: boolean;
  guilds: number;
  members: number;
  ratelimited: boolean;
};

/** Where the locale figures came from: the beta feed or this deployment. */
export type StatusLocaleSource = {
  mode: "beta" | "local";
  /** The configured beta origin, when there is one. */
  origin?: string | null;
  /** Why the last pull failed, if it did. */
  error?: string | null;
  /** Seconds since beta's manifest was read. */
  age_seconds?: number | null;
  /** True when beta is unreachable and the last good reading is being shown. */
  stale?: boolean;
};

/** One page's translation file, as the owner's locale page lists it. */
export type OwnerLocalePage = {
  page: string;
  keys: number;
  languages: Record<string, number>;
};

/** What the last bot-catalogue sync did, for the same page's source card. */
export type OwnerBotSync = {
  packages: number;
  files: number;
  fetched: number;
  /** Files beta could not serve this pass, kept from the previous copy. */
  reused: number;
  error: string | null;
  applied_at: number | null;
};

/** What the owner's locale page reads from `/api/owner/locales`. */
export type OwnerLocales = {
  configured: boolean;
  origin: string | null;
  source: StatusLocaleSource;
  generated_at: number | null;
  languages: { code: string; label: string }[];
  coverage: StatusCoverage[];
  pages: OwnerLocalePage[];
  total_keys: number;
  /** The bot's own catalogues, one row per cog package. */
  bot: OwnerLocalePage[];
  bot_total_keys: number;
  bot_sync: OwnerBotSync;
  synced_at?: number;
};

/** One file an update would add, replace or delete. */
export type OwnerUpdateFile = {
  path: string;
  status: "added" | "modified" | "removed";
  bytes: number;
};

export type OwnerUpdateArea = {
  label: string;
  changed: number;
  bytes: number;
  files: OwnerUpdateFile[];
  truncated: number;
};

/** What one area did when an update was applied. */
export type OwnerUpdateRunArea = {
  ok?: boolean;
  changed?: number;
  written?: number;
  removed?: number;
  strategy?: string;
  error?: string;
  rolled_back?: boolean;
  reloaded?: string[];
  loaded?: string[];
  unloaded?: string[];
  failed?: string[];
  dashboard?: { swapped?: boolean; routes?: number };
  purged?: string[];
};

export type OwnerUpdateRun = {
  id: string;
  started_at: number;
  finished_at: number;
  areas: Record<string, OwnerUpdateRunArea>;
  handoff?: boolean;
};

/** The plan the owner's update page reads, and the result of applying it. */
export type OwnerUpdates = {
  ok: boolean;
  configured: boolean;
  beta: string | null;
  error?: string;
  generated_at?: number;
  areas: Record<string, OwnerUpdateArea>;
  total_changed: number;
  total_bytes: number;
  running?: boolean;
  last?: OwnerUpdateRun | null;
  token_set?: boolean;
  handoff?: {
    state: string;
    pid?: number;
    port?: number;
    at: number;
    error?: string;
  } | null;
};

export type OwnerUpdateApply = {
  ok: boolean;
  error?: string;
  beta?: string | null;
  run?: string;
  areas: Record<string, OwnerUpdateRunArea>;
  last?: OwnerUpdateRun | null;
  handoff?: OwnerUpdates["handoff"];
};

/** A live snapshot of the update currently being applied. */
export type OwnerUpdateProgress = {
  active: boolean;
  /** Areas chosen for this run, in the order they are applied. */
  areas: string[];
  /** The area being worked on, or null between areas. */
  area: string | null;
  index: number;
  total: number;
  /** Areas that have finished, oldest first. */
  done: string[];
  phase: "starting" | "pulling" | "applying" | "applied" | "skipped" | "failed" | "";
  started_at: number | null;
};

export type StatusCoverage = {
  code: string;
  label: string;
  translated: number;
  total: number;
  missing: number;
  percent: number;
  /** Bot rows: how many locale catalogues were walked. */
  catalogues?: number;
  /** Website rows: how many page catalogue folders were walked. */
  pages?: number;
  /** Website rows: how many of those pages this language has finished. */
  complete_pages?: number;
};

export type StatusHost = {
  platform: string;
  python: string;
  pid: number;
  cores: number | null;
  cpu_percent?: number;
  load?: number[];
  memory?: { used_gb: number; total_gb: number; percent: number };
  disk?: { used_gb: number; total_gb: number; percent: number };
  process?: {
    cpu_percent: number;
    memory_mb: number;
    threads: number;
    started_at: number;
    connections: number;
  };
};

export type StatusPayload = {
  online: boolean;
  state: StatusState;
  reason?: string | null;
  bot: {
    name: string;
    id: string | null;
    avatar_url: string | null;
    ready: boolean;
    latency_ms: number | null;
    guild_count: number;
    user_count: number;
    command_count: number;
    voice_clients: number;
    uptime_seconds: number | null;
    started_at: number | null;
    version: string | null;
  } | null;
  shards: StatusShard[];
  shard_count: number;
  cogs: StatusCog[];
  cog_counts: Record<CogState, number>;
  host: StatusHost;
  locales: {
    languages: string[];
    bot: StatusCoverage[];
    website: StatusCoverage[];
    scanned_at: number;
    /** Which copy of the catalogues the figures describe. */
    source?: StatusLocaleSource;
  };
  generated_at: number;
};

/** One day of bot-wide command usage; the API zero-fills the window. */
export type StaffAnalyticsDay = {
  date: string;
  total: number;
  slash: number;
  prefix: number;
  context: number;
  guilds: number;
  languages: Record<string, number>;
};

export type StaffAnalyticsCommand = {
  name: string;
  count: number;
  share: number;
  category: string;
};

export type StaffAnalyticsLanguageUse = {
  code: string;
  label: string;
  count: number;
  share: number;
  supported: boolean;
};

export type StaffAnalyticsGuildLanguage = {
  code: string;
  label: string;
  guilds: number;
  members: number;
  share: number;
  supported: boolean;
};

export type StaffAnalyticsEconomy = {
  profiles: number;
  circulating: number;
  banked: number;
  average: number;
  median: number;
  average_level: number;
  active_streaks: number;
  top_jobs: { id: string; name: string; emoji: string; count: number; share: number }[];
};

/** Everything the staff analytics tab draws, from ``/api/staff/analytics``. */
export type StaffAnalytics = {
  generated_at: string;
  bot: {
    online: boolean;
    source: "live" | "snapshot";
    guilds: number;
    members: number;
    latency_ms: number | null;
    uptime_seconds: number | null;
    shard_count: number;
    shards: { id: number; latency_ms: number | null }[];
  };
  usage: {
    days: StaffAnalyticsDay[];
    window_days: number;
    today: { total: number; slash: number; prefix: number; context: number; guilds: number };
    totals: { today: number; last_7_days: number; last_30_days: number; lifetime: number };
    by_kind: { slash: number; prefix: number; context: number };
    top_commands: StaffAnalyticsCommand[];
    by_language: StaffAnalyticsLanguageUse[];
  };
  languages: { guilds: number; members: number; languages: StaffAnalyticsGuildLanguage[] };
  economy: StaffAnalyticsEconomy | null;
  growth: { date: string; guilds: number; users: number }[];
};

export type PublicConfig = {
  application_id: string;
  bot_avatar_url?: string | null;
  /** The bot's username, as Discord stores it. */
  bot_name?: string | null;
  /** The four-digit tag, or "0" for accounts Discord no longer tags. */
  bot_discriminator?: string | null;
  /** The name Discord shows above the bot's messages (global display name). */
  bot_display_name?: string | null;
  /** Discord's verified-bot tick, drawn inside the APP tag. */
  bot_verified?: boolean;
  invite_url: string;
  support_server_url?: string | null;
  oauth_available: boolean;
};

/** One of the bot's custom emojis, as `/api/emojis` reports it. */
export type BotEmoji = {
  /** The emoji name Discord stores, without the surrounding colons. */
  name: string;
  /** The emoji id, or a stub id until the bot's emoji sync uploads the art. */
  id: string;
  animated: boolean;
  /** True while the id is a config stub rather than an uploaded emoji. */
  placeholder: boolean;
};

/** A real server emoji from a guild the bot is in, for the rendering lab. */
export type ServerEmoji = {
  name: string;
  id: string;
  animated: boolean;
  guild_name: string;
  guild_icon_url: string | null;
};

export type BotEmojisResponse = {
  emojis: BotEmoji[];
  /** The lab's server-emoji popup sample; null when no guild has an emoji. */
  server_emoji?: ServerEmoji | null;
};

export type CommandType = "slash" | "prefix" | "hybrid" | "context";

export type CommandParameter = {
  name: string;
  description?: string | Record<string, string>;
  required?: boolean;
  type?: string;
};

export type CommandLocalizedDescription = string | Record<string, string>;

export type Command = {
  name: string;
  description: CommandLocalizedDescription;
  category: string;
  type?: CommandType;
  context_type?: "user" | "message";
  aliases?: string[];
  parameters?: CommandParameter[];
  permissions?: string[];
  usage?: string;
  subcommands?: string[];
};

export type Guild = {
  id: string;
  name: string;
  icon_url: string | null;
  owner?: boolean;
  permissions?: number;
  installed?: boolean;
  blacklisted?: boolean;
  blacklist_reason?: string | null;
  invite_url?: string | null;
};

export type StaffGuild = {
  id: string;
  name: string;
  icon_url: string | null;
  owner_id: string | null;
  owner_name: string;
  member_count: number;
  channel_count: number;
  created_at: string | null;
  bot_avatar_url: string | null;
  bot_banner_url: string | null;
  profile_name: string | null;
  blacklisted: boolean;
  blacklist_reason: string | null;
  bot_permissions: { name: string; label: string; granted: boolean }[];
  role_count: number;
  category_count: number;
};

export type StaffBlacklistEntry = { id: string; reason: string | null; timestamp: number; added_by: string | null };
export type StaffBlacklist = { users: StaffBlacklistEntry[]; guilds: StaffBlacklistEntry[] };
export type LockdownStepStatus = "done" | "skipped" | "failed";
/** One feature a blacklist lockdown paused, skipped, or could not switch off. */
export type LockdownStepResult = {
  step: string;
  label: string;
  status: LockdownStepStatus;
  detail: string;
};
export type ProxyWorkerLatencyPoint = {
  t: number;
  avg: number;
  p95: number;
  count: number;
  errors: number;
};
export type ProxyWorkerRequest = {
  at: number;
  method: string;
  path: string;
  status: number;
  latency_ms?: number;
  ok?: boolean;
  worker_id?: string;
  worker_name?: string;
  message?: string;
};
export type ProxyWorkerStats = {
  service?: string;
  name?: string;
  version?: string;
  ready?: boolean;
  uptime_seconds: number;
  now?: number;
  checked_at?: number;
  stats_error?: string;
  totals?: {
    requests: number;
    success: number;
    errors: number;
    bytes_in: number;
    bytes_out: number;
    avg_latency_ms: number;
    p95_latency_ms: number;
  };
  statuses?: Record<string, number>;
  latency?: ProxyWorkerLatencyPoint[];
  recent?: ProxyWorkerRequest[];
  errors?: ProxyWorkerRequest[];
};
export type ProxyWorker = {
  id: string;
  name: string;
  url: string;
  created_at: number;
  health?: "online" | "offline";
  active?: boolean;
  stats?: ProxyWorkerStats | null;
};
export type ProxyWorkerRouting = {
  enabled: boolean;
  token_configured: boolean;
  worker_count: number;
  online_count: number;
  total_requests: number;
  total_failures: number;
  last_error?: string | null;
  last_worker?: string | null;
  last_used_at?: number | null;
  recent_errors?: { at: number; worker?: string | null; message: string }[];
};
export type ProxyWorkerUsage = {
  requests: number;
  success: number;
  errors: number;
  bytes_in: number;
  bytes_out: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  statuses: Record<string, number>;
};
export type ProxyWorkersResponse = {
  workers: ProxyWorker[];
  routing: ProxyWorkerRouting;
  usage: ProxyWorkerUsage;
  latency: ProxyWorkerLatencyPoint[];
  feed: ProxyWorkerRequest[];
  errors: ProxyWorkerRequest[];
};
export type BlacklistAppealStatus = {
  status: "eligible" | "pending" | "approved" | "denied" | "not_blacklisted" | "not_eligible";
  can_appeal: boolean;
  reason?: string;
  appeal_id?: string;
  appeal_text?: string;
  blacklist_reason?: string | null;
  created_at?: number;
  reviewed_at?: number | null;
  staff_note?: string | null;
  previous_appeal?: BlacklistAppealStatus;
};
export type BlacklistAppeal = {
  appeal_id: string;
  user_id: string;
  guild_id?: string | null;
  username?: string | null;
  appeal_text: string;
  blacklist_reason?: string | null;
  blacklist_timestamp?: number | null;
  status: "pending" | "approved" | "denied";
  created_at: number;
  reviewed_by?: string | null;
  reviewed_at?: number | null;
  staff_note?: string | null;
};

export type DataRemovalRequest = {
  id: string;
  scope: "account" | "server";
  guild_id?: string | null;
  guild_name?: string | null;
  reason: string;
  status: "pending" | "completed" | "denied" | "withdrawn";
  created_at: number;
  updated_at: number;
  review_note?: string | null;
  completed_at?: number | null;
  reviewed_by?: string | null;
};

export type DataRemovalServer = {
  id: string;
  name: string;
  icon_url?: string | null;
  bot_present: boolean;
  removed_at?: number | null;
  pending: boolean;
};

export type DataRemovalOverview = {
  requests: DataRemovalRequest[];
  account: { pending: boolean };
  servers: DataRemovalServer[];
  confirmations: { account: string; min_reason_length: number };
};

export type StaffDataRemovalRequest = DataRemovalRequest & {
  user_id: string;
  result?: { removed?: string[]; anonymized?: string[]; preserved?: string[]; errors?: string[] } | null;
};

export type User = {
  id: string;
  username?: string;
  global_name?: string;
  avatar?: string | null;
};

export type UserOverview = {
  balance: number;
  bank: number;
  net_worth: number;
  level: number;
  job: string;
  job_name: string;
  daily_streak: number;
  achievements: number;
  total_earned: number;
  economy_rank: number | null;
  economy_profiles: number;
  leaderboard_private: boolean;
};

// ── Economy standing, voting and achievements ────────────────────────────────

export type EconomyTransaction = {
  kind: string;
  /** Friendly name for `kind`, e.g. "Blackjack won" instead of `blackjack_win`. */
  label: string;
  amount: number;
  note: string;
  ts: number;
};

export type VoteStanding = {
  votes: number;
  streak: number;
  best_streak: number;
  last_vote: number;
  next_vote_at: number;
  can_vote: boolean;
  reward_multiplier: number;
  earnings_multiplier: number;
  vote_url: string;
};

/**
 * The weekly lottery as the economy tab shows it: the prize the next draw pays,
 * how many members are in the round, and how many tickets the viewer holds.
 */
export type LotteryStanding = {
  /** Coins the next draw pays out, after the house rake. */
  pot: number;
  /** Members holding at least one ticket this round, not the ticket count. */
  participants: number;
  tickets: number;
  your_tickets: number;
  ticket_price: number;
  /** Unix seconds of the next draw, or 0 before the first round exists. */
  next_draw: number;
  /** The last winner's display name, when the bot still knows the account. */
  last_winner: string | null;
  last_pot: number;
  /** False while the pot is empty, so the card can say the round has not started. */
  open: boolean;
};

export type EconomyStanding = {
  user_id: string | null;
  balance: number;
  bank: number;
  net_worth: number;
  level: number;
  job: string;
  job_name: string;
  bank_tier: number;
  daily_streak: number;
  total_earned: number;
  total_spent: number;
  times_worked: number;
  achievements_unlocked: number;
  achievements_total: number;
  achievement_coins: number;
  global_rank: number | null;
  account_count: number | null;
  transactions: EconomyTransaction[];
  lottery: LotteryStanding;
  vote: VoteStanding;
};

export type AchievementProgress = {
  current: number;
  target: number;
  percent: number;
};

/** An event window on a seasonal badge: the dates it opens and closes. */
export type AchievementSeason = {
  label: string;
  active: boolean;
  starts_at: number;
  ends_at: number;
};

export type AchievementEntry = {
  id: string;
  name: string;
  emoji: string;
  /** A logo to draw instead of the emoji, e.g. the top.gg mark on voting badges. */
  icon_url: string | null;
  /** ``null`` for a badge that can be earned at any time of year. */
  season: AchievementSeason | null;
  description: string;
  reward: number;
  unlocked: boolean;
  progress: AchievementProgress;
};

export type AchievementsResponse = {
  achievements: AchievementEntry[];
  unlocked: number;
  total: number;
  coins_earned: number;
  coins_available: number;
};

// ── Support-server referrals ────────────────────────────────────────────────

/** One member an account's referral link brought into the support server. */
export type ReferralJoin = {
  member_id: string;
  /** The member's display name, when the bot still shares a guild with them. */
  name: string | null;
  avatar_url: string | null;
  joined_at: number;
  reward: number;
};

/**
 * The referral card: the link to share and what it has brought in. The invite
 * behind the link is minted the first time somebody opens it, so nothing here
 * waits on the bot.
 */
export type ReferralSummary = {
  link: string;
  invited: number;
  coins: number;
  /** Coins paid per credited join. */
  reward: number;
  recent: ReferralJoin[];
};

export type LevelRow = {
  user_id: string;
  display_name?: string | null;
  username?: string | null;
  avatar_url?: string | null;
  xp: number;
  level: number;
};

// One row of a guild's public leveling page. `key` is an opaque, stable row
// key so the page can animate members who change rank between polls.
export type GuildLevelEntry = {
  key: string;
  rank: number;
  level: number;
  xp: number;
  xp_for_next: number;
  username: string | null;
  display_name: string | null;
  avatar_url: string | null;
};

export type GuildLevelsResponse = {
  guild: {
    id: string;
    name: string;
    icon_url: string | null;
    member_count: number;
  };
  leveling_enabled: boolean;
  entries: GuildLevelEntry[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
};

export type ServerStats = {
  member_count: number;
  channel_count: number;
  role_count: number;
  created_at: string | null;
  activity: Array<{
    date: string;
    messages: number;
    joins: number;
    leaves: number;
  }>;
};

export type GuildOverview = {
  moderation: { warn_count: number; automod_active: boolean };
  leveling: { top: LevelRow[] };
  server: ServerStats;
};

export type OnboardingConfig = {
  welcome_channel?: number | null;
  welcome_title?: string | null;
  welcome_description?: string | null;
  welcome_color?: number | null | string;
  welcome_image?: string | null;
  goodbye_channel?: number | null;
  goodbye_title?: string | null;
  goodbye_description?: string | null;
  goodbye_color?: number | null | string;
  goodbye_image?: string | null;
  rules_channel?: number | null;
  rules_text?: string | null;
  rules_role_id?: number | null;
  autorole_ids?: number[];
  bot_autorole_ids?: number[];
  captcha_enabled?: boolean;
  captcha_channel_id?: number | null;
  captcha_add_role_ids?: number[];
  captcha_remove_role_ids?: number[];
  captcha_kick_on_fail?: boolean;
  /** How members prove they are human: an immediate click, a DM captcha, or the website page. */
  captcha_mode?: "click" | "image" | "web";
  /** Website method only: refuse proxy, VPN, and Tor connections. */
  captcha_block_proxies?: boolean;
  /** Website method only: refuse hosting and datacenter address ranges. */
  captcha_block_vpn?: boolean;
};

export type LoggingConfig = Record<string, string | number | null> & {
  disabled?: string[];
};

export type TicketConfig = {
  panel_title?: string | null;
  panel_description?: string | null;
  panel_color?: number | null | string;
  panel_image?: string | null;
  panel_categories?: string[];
  panel_channel_id?: string | null;
  panel_message_id?: string | null;
  support_roles?: string[];
  open_tickets?: TicketRow[];
};

export type TicketRow = {
  channel_id: string;
  message_id?: string | number | null;
  opener_id: string;
  opener_name?: string | null;
  channel_name?: string;
  category?: string;
  status?: "open" | "closed";
  claimed_by?: string | null;
};

export type TicketTranscript = {
  transcript_id: string;
  channel_name: string;
  opener_id: string;
  category: string;
  claimed_by?: string | null;
  message_count: number;
  created_at: string;
  url: string;
};

export type GuildTicketsResponse = {
  config: TicketConfig;
  tickets: TicketRow[];
  transcripts: TicketTranscript[];
};

export type GuildProfile = {
  display_name?: string | null;
  bio?: string | null;
  avatar_url?: string | null;
  banner_url?: string | null;
  name_font_id?: number | null;
  name_effect_id?: number | null;
  name_colors?: number[];
};

/** Niko's application-wide identity, shown until a server sets its own. */
export type GlobalProfile = {
  avatar_url?: string | null;
  banner_url?: string | null;
  /** The bot's Discord bio, set globally with /setprofile. */
  bio?: string | null;
};

export type ServerConfig = {
  prefixes: string[];
  development?: boolean;
  default_prefix?: string;
  prefix_override?: string;
  onboarding: OnboardingConfig;
  logging: LoggingConfig;
  /** The bot's own log categories, so the dashboard cannot drift from it. */
  logging_categories?: { key: string; label: string; description?: string }[];
  tickets: TicketConfig;
  profile: GuildProfile;
  global_profile?: GlobalProfile;
};

export type PremiumSubscription = {
  guild_id?: string;
  plan?: string;
  status?: string;
  active: boolean;
  price_cents?: number;
  currency?: string;
  started_at?: string | null;
  expires_at?: string | null;
  days_remaining?: number;
  source?: string;
  gifted_by?: string | null;
  gifted_by_name?: string | null;
  auto_renew?: boolean;
};

export type StaffBillingPayment = {
  order_id: string;
  track_id: string | null;
  guild_id: string;
  guild_name?: string | null;
  payer_id: string;
  payer_name?: string | null;
  kind: string;
  months: number;
  amount_cents: number;
  amount_label: string;
  currency: string;
  pay_currency?: string | null;
  status: string;
  paid: boolean;
  issue_status?: string | null;
  issue_note?: string | null;
  resolved_by?: string | null;
  resolved_at?: string | null;
  created_at?: string | null;
  paid_at?: string | null;
};

export type StaffBillingResponse = {
  payments: StaffBillingPayment[];
  subscriptions: (PremiumSubscription & { guild_name?: string | null; owner_id?: string | null })[];
  totals: { paid_count: number; paid_cents: number; paid_label: string; active_count: number; expiring_soon: number };
  gateway: { configured: boolean; model: string };
};

/**
 * One staff address on Niko's own domain: a shared team mailbox (`owner@…`,
 * `support@…`) or a staff member's private address minted from their Discord
 * username and shown under their display name.
 */
export type StaffMailbox = {
  local: string;
  label: string;
  address: string;
  kind?: "shared" | "personal";
  sender_name?: string;
};

/** A mail in the staff inbox; `body` is only sent by the detail endpoint. */
/** What the mail provider last said about a sent message. */
export type StaffEmailStatus =
  | "sent"
  | "accepted"
  | "retrying"
  | "delivered"
  | "opened"
  | "failed"
  | "complained"
  | "unsubscribed"
  | "received";

/** A file sent with a mail, described but not stored. */
export type StaffEmailAttachment = {
  name: string;
  size: number;
  type?: string;
};

/** One webhook event; `opened` is the read receipt. */
export type StaffEmailEvent = {
  event: string;
  recipient: string;
  reason: string;
  severity: string;
  /** The provider's own sentence about the event (a bounce message, say). */
  detail?: string;
  occurred_at: number;
};

export type StaffEmailMessage = {
  message_id: string;
  /** The conversation this message belongs to; replies share it. */
  thread_id?: string;
  mailbox: string;
  direction: "inbound" | "outbound";
  from_address: string;
  from_name?: string | null;
  to_address: string;
  subject: string;
  created_at: number;
  read: boolean;
  status?: StaffEmailStatus;
  delivered_at?: number | null;
  opened_at?: number | null;
  opened_count?: number;
  events?: StaffEmailEvent[];
  preview?: string;
  body?: string;
  /** The body as markup — the same rendering the recipient's client shows.
   * The server sanitizes it before storing it, so it is safe to mount. */
  html?: string;
  /** The quoted history the message carried, folded out of the body. */
  quoted_html?: string;
  /** Names and sizes of the files sent with a mail (never the file bytes). */
  attachments?: StaffEmailAttachment[];
  /** Every message of the conversation, oldest first (detail endpoint only). */
  thread?: StaffEmailMessage[];
};

/** One of the reasons the report form offers, with the words it shows. */
export type StaffEmailReportReason = { value: string; label: string };

/** Which mail a report link belongs to, and what the form may ask about it. */
export type StaffEmailReportTarget = {
  subject: string;
  from_name?: string | null;
  from_address: string;
  to_address: string;
  sent_at: number;
  conversation_count: number;
  reasons: StaffEmailReportReason[];
  max_details: number;
};

/** A recipient's complaint, and the owner's handling of it. */
export type StaffEmailReport = {
  report_id: string;
  message_id: string;
  mailbox: string;
  reason: string;
  reason_label: string;
  details: string;
  include_thread: boolean;
  reporter_address: string;
  created_at: number;
  status: "open" | "replied" | "resolved";
  response?: string | null;
  responded_at?: number | null;
  responded_by?: string | null;
  message?: StaffEmailMessage | null;
  /** The conversation, only when the reporter agreed to share it. */
  thread?: StaffEmailMessage[];
};

export type StaffEmailInbox = {
  role: string;
  domain: string;
  mailboxes: StaffMailbox[];
  messages: StaffEmailMessage[];
  configured: boolean;
  missing: string[];
  unread: number;
  /** Where lifecycle auto-replies point senders (`support@…`). */
  support_address?: string;
};

/**
 * One blocked-word preset filter.
 *
 * Served by the bot inside the moderation payload (`preset_filters`) and used
 * by the dashboard to render the toggles, so the list can never drift from the
 * patterns the filter actually runs. Toggling one saves its `key` in
 * `badwords_presets`.
 */
export type PresetFilter = {
  key: string;
  label: string;
  description: string;
  /** How many base terms the filter expands, shown as a size hint. */
  terms?: number;
};

export type GuildConfig = {
  moderation: Record<string, any>;
  server: ServerConfig;
  ai: {
    personality?: string;
    enabled?: string | boolean;
    ai_actions_experiment?: string | boolean;
    better_context_experiment?: string | boolean;
    multimodal_experiment?: string | boolean;
    ai_name?: string;
  };
  leveling: {
    xp_enabled?: boolean;
    xp_multiplier?: number;
    xp_cooldown?: number;
    level_up_channel?: string | null;
    level_up_message?: string;
    xp_excluded_channels?: string[];
    xp_vc_enabled?: boolean;
    /** Level number → role ID, both as strings so snowflakes stay exact in JS. */
    level_roles?: Record<string, string>;
  };
  premium?: PremiumSubscription;
};

export type GuildResources = {
  channels: { id: string; name: string; type?: string }[];
  voice_channels?: { id: string; name: string; type?: string }[];
  roles: { id: string; name: string; color?: string | null; colors?: string[] }[];
};

export type BoosterSettings = {
  notifications_enabled: boolean;
  roles_enabled: boolean;
  channel_id: string;
  boost_message: string;
  unboost_message: string;
};

export type PublicProfileLink = {
  type: string;
  url: string;
  label?: string;
};

export type StaffMember = {
  id: string;
  name: string;
  username?: string | null;
  /** Readable public profile slug: `/team/<handle>`; `id` stays the permanent link. */
  handle?: string | null;
  role: string;
  role_label: string;
  bio?: string | null;
  public_name?: string | null;
  public_avatar_url?: string | null;
  public_banner_url?: string | null;
  public_links?: PublicProfileLink[];
  avatar_url?: string | null;
  status?: string;
  status_label?: string;
  activities?: StaffActivity[];
  custom_status?: StaffCustomStatus | null;
  activity?: string | null;
  visible?: boolean;
  /** Active staff keep access; suspended and former profiles stay retained but hidden. */
  staff_status?: "active" | "suspended" | "former";
  staff_status_label?: string;
  status_reason?: string | null;
  status_changed_by?: string | null;
  status_changed_at?: number | null;
  /** The member's own public-listing switch, before staff status is applied. */
  profile_visible?: boolean;
  /** Presentation for the SVG card at /staff/<id>/card.svg. */
  card?: {
    theme: "dark" | "light";
    accent?: string | null;
    show_status?: boolean;
  };
};

export type StaffRosterRole = {
  key: string;
  label: string;
};

export type StaffManagementResponse = {
  members: StaffMember[];
  roles: StaffRosterRole[];
  count: number;
};

/** A cog as the maintenance tab sees it: what it is and whether it is paused. */
export type StaffMaintenanceCog = {
  name: string;
  label: string;
  state: "loaded" | "disabled" | "maintenance" | "failed";
  reason: string | null;
  /** Set by the cog's source (`MAINTENANCE`/`DNL`), which the dashboard cannot override. */
  declared: boolean;
  commands: number;
  maintenance: boolean;
  since: number | null;
  by: string | null;
};

export type StaffMaintenanceCommand = {
  name: string;
  cog: string | null;
  cog_label: string | null;
  maintenance: boolean;
  /** The entry that actually blocks this command: its own, or its cog. */
  blocked_by: string | null;
  reason: string | null;
  since: number | null;
  by: string | null;
};

export type StaffMaintenanceResponse = {
  cogs: StaffMaintenanceCog[];
  commands: StaffMaintenanceCommand[];
  updated_at: number;
};

export type StaffEmoji = {
  kind: "unicode" | "custom";
  value: string;
  name?: string | null;
  animated?: boolean;
};

export type StaffActivity = {
  kind: "spotify" | "streaming" | "activity";
  type: string;
  name: string;
  details?: string | null;
  state?: string | null;
  url?: string | null;
  application_id?: string | null;
  platform?: string | null;
  image_url?: string | null;
  /** ISO timestamps for a Spotify track, used by the track progress bar. */
  start?: string | null;
  end?: string | null;
};

export type SocialProfileCardData = {
  platform: string;
  display_name: string;
  handle: string;
  url: string;
  avatar_url?: string | null;
  bio?: string | null;
  stats?: { label: string; value: string }[];
  status?: string | null;
};

export type StaffCustomStatus = {
  text?: string | null;
  emoji?: StaffEmoji | null;
};

export type AuthStatus = {
  authenticated: boolean;
  oauth_available: boolean;
  /** Configured owner sessions see the in-page devtools button. */
  owner?: boolean;
  user?: User;
  csrf_token?: string;
  blacklisted?: boolean;
  blacklist_reason?: string | null;
};

export type StaffApplicationQuestionType = "short_text" | "paragraph" | "single_choice" | "multi_choice" | "yes_no" | "date";
export type StaffApplicationQuestion = { id: string; prompt: string; required: boolean; type?: StaffApplicationQuestionType; options?: string[] };
export type StaffApplicationAnswer = { question_id: string; prompt: string; answer: string | string[] };
export type StaffApplication = {
  id: string;
  guild_id: string;
  role_id: string;
  title: string;
  description: string;
  questions: StaffApplicationQuestion[];
  eligible_role_ids: string[];
  status: "open" | "closed";
  submission_count: number;
  role_name?: string | null;
  created_at?: string;
  link: string;
};
export type StaffApplicationSubmission = {
  user_id: string;
  display_name: string;
  username?: string | null;
  avatar_url?: string | null;
  answers: StaffApplicationAnswer[];
  submitted_at?: string;
  review_status: "pending" | "approved" | "denied";
  reviewed_by?: string | null;
  reviewed_at?: string | null;
};
export type TeamRecruitmentQuestionType = "short_text" | "paragraph" | "single_choice" | "multi_choice" | "yes_no" | "date";
export type TeamRecruitmentQuestion = { id: string; prompt: string; required: boolean; type?: TeamRecruitmentQuestionType; options?: string[] };
export type TeamRecruitmentAnswer = { question_id: string; prompt: string; answer: string | string[] };
export type TeamRecruitmentOpening = {
  id: string;
  role_id: string;
  title: string;
  description: string;
  questions: TeamRecruitmentQuestion[];
  status: "open" | "closed";
  submission_count: number;
  role_name?: string | null;
  created_at?: string;
  link: string;
  already_submitted?: boolean;
  eligible?: boolean;
};
export type TeamRecruitmentSubmission = {
  user_id: string;
  display_name: string;
  answers: TeamRecruitmentAnswer[];
  submitted_at?: string;
  review_status: "pending" | "approved" | "denied";
  reviewed_by?: string | null;
  reviewed_at?: string | null;
};
export type TeamRecruitmentSettings = { openings: TeamRecruitmentOpening[] };
export type PublicStaffApplication = StaffApplication & {
  role_name?: string | null;
  guild_name?: string | null;
  eligible?: boolean;
  already_submitted?: boolean;
};

// ── Social notifier (dashboard notifications tab) ────────────────────────────

export type NotifierPlatform = {
  id: string;
  label: string;
  field_label: string;
  field_placeholder: string;
};

export type NotifierFollow = {
  platform: string;
  username: string;
  display: string;
  channel_id: string | null;
  template: string;
  ping_role_id: string | null;
  enabled: boolean;
  last_post_id: string | null;
  failures: number;
  last_checked_at: string | null;
};

export type NotifierConfig = {
  enabled: boolean;
  default_channel_id: string | null;
  ping_role_id: string | null;
};

export type NotifierLimits = {
  max_follows: number;
  max_follows_per_platform: number;
  max_template_length: number;
  template_placeholders: string[];
};

export type NotifierResponse = {
  config: NotifierConfig;
  follows: NotifierFollow[];
  platforms: NotifierPlatform[];
  limits: NotifierLimits;
};

// ── Documentation types ──────────────────────────────────────────────────────

export type DocCategory =
  | "getting-started"
  | "setup"
  | "economy"
  | "leveling"
  | "moderation"
  | "automod"
  | "logging"
  | "social"
  | "utility"
  | "voice"
  | "ai"
  | "dashboard"
  | "tips";

// ── Staff broadcast studio ───────────────────────────────────────────────────
// A broadcast is stored server-side; ``status`` moves draft → sending → sent and
// briefly to syncing while an edit is pushed to every delivered copy.

export type StaffBroadcastStatus = "draft" | "sending" | "sent" | "syncing" | "failed";

export type StaffBroadcastMedia = {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  url: string;
};

export type StaffBroadcast = {
  id: string;
  title: string;
  body: string;
  accent: string;
  footer: string;
  status: StaffBroadcastStatus;
  created_by: string;
  created_at: number;
  updated_at: number;
  target_count: number;
  sent_count: number;
  failed_count: number;
  skipped_count: number;
  edited_count: number;
  last_error: string | null;
  media: StaffBroadcastMedia[];
};

/** One Lavalink node as the owner dashboard sees it — never includes secrets. */
export type LavalinkNodeRow = {
  identifier: string;
  host: string;
  port: number;
  secure: boolean;
  label: string;
  /** Where the node came from: committed catalogue, database, or a stale pool entry. */
  source: "static" | "private" | "orphan";
  status: string;
  players: number;
  heartbeat: number;
};

export type LavalinkPoolResponse = {
  nodes: LavalinkNodeRow[];
  connected: number;
  target: number;
  private_count: number;
  static_count: number;
};

export type DocPage = {
  slug: string;
  title: string;
  category: DocCategory;
  excerpt: string;
  content: string;
  tags: string[];
  order: number;
};

export type DocSection = {
  id: string;
  label: string;
  description: string;
  icon: string;
  count: number;
};

export type SearchFilters = {
  category: DocCategory | "";
  tags: string[];
  query: string;
};

export type SearchResult = {
  page: DocPage;
  score: number;
  highlights: string[];
};