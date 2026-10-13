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
export type BackupInstance = { id: string; name: string; url: string; created_at: number };
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
  daily_streak: number;
  achievements: number;
  total_earned: number;
  economy_rank: number | null;
  economy_profiles: number;
  leaderboard_private: boolean;
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

export type ServerConfig = {
  prefixes: string[];
  onboarding: OnboardingConfig;
  logging: LoggingConfig;
  tickets: TicketConfig;
  profile: GuildProfile;
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
};

export type GuildResources = {
  channels: { id: string; name: string }[];
  roles: { id: string; name: string }[];
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