export type BotStats = {
  guild_count: number;
  user_count: number;
  command_count: number;
  uptime_since: string | null;
  version: string;
  economy_users: number;
};

export type PublicConfig = {
  application_id: string;
  bot_avatar_url?: string | null;
  invite_url: string;
  support_server_url?: string | null;
  oauth_available: boolean;
};

export type CommandType = "slash" | "prefix" | "hybrid" | "context";

export type CommandParameter = {
  name: string;
  description?: string;
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
export type StandbyInstance = {
  id: string;
  name: string;
  url: string;
  created_at: number;
  health?: "online" | "offline";
  active?: boolean;
  stats?: { uptime_seconds: number; total_api_requests: number; failed_api_requests: number } | null;
};
export type StandbyFailoverStatus = {
  mode: "auto" | "off" | "standby";
  enabled: boolean;
  active_standby_id: string | null;
  standby_count: number;
  last_error?: string | null;
  last_changed_at: number;
  failover_count: number;
  egress_blocked: boolean;
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

export type LevelRow = {
  user_id: string;
  display_name?: string | null;
  username?: string | null;
  avatar_url?: string | null;
  xp: number;
  level: number;
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

/** Niko's application-wide avatar and banner, shown until a server sets its own. */
export type GlobalProfile = {
  avatar_url?: string | null;
  banner_url?: string | null;
};

export type ServerConfig = {
  prefixes: string[];
  development?: boolean;
  default_prefix?: string;
  prefix_override?: string;
  onboarding: OnboardingConfig;
  logging: LoggingConfig;
  tickets: TicketConfig;
  profile: GuildProfile;
  privacy?: { private: boolean };
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
  };
  premium?: PremiumSubscription;
};

export type GuildResources = {
  channels: { id: string; name: string }[];
  roles: { id: string; name: string }[];
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