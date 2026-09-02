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
  invite_url: string;
  oauth_available: boolean;
};

export type CommandType = "slash" | "prefix" | "hybrid" | "context";

export type CommandParameter = {
  name: string;
  description?: string;
  required?: boolean;
  type?: string;
};

export type Command = {
  name: string;
  description: string;
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
  invite_url?: string | null;
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
};

export type LevelRow = {
  user_id: string;
  display_name?: string | null;
  username?: string | null;
  avatar_url?: string | null;
  xp: number;
  level: number;
};

export type GuildOverview = {
  moderation: { warn_count: number; automod_active: boolean };
  leveling: { top: LevelRow[] };
};

export type OnboardingConfig = {
  welcome_channel?: number | null;
  welcome_title?: string | null;
  welcome_description?: string | null;
  welcome_color?: number | null;
  welcome_image?: string | null;
  rules_channel?: number | null;
  rules_text?: string | null;
  rules_role_id?: number | null;
  autorole_ids?: number[];
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
  panel_color?: number | null;
  panel_image?: string | null;
  panel_categories?: string[];
  panel_channel_id?: string | null;
  panel_message_id?: string | null;
  support_roles?: string[];
};

export type ServerConfig = {
  prefixes: string[];
  onboarding: OnboardingConfig;
  logging: LoggingConfig;
  tickets: TicketConfig;
};

export type GuildConfig = {
  moderation: Record<string, any>;
  server: ServerConfig;
  ai: {
    personality?: string;
    enabled?: string | boolean;
    ai_actions_experiment?: string | boolean;
    better_context_experiment?: string | boolean;
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

export type AuthStatus = {
  authenticated: boolean;
  oauth_available: boolean;
  user?: User;
  csrf_token?: string;
};

// ── Documentation types ──────────────────────────────────────────────────────

export type DocCategory =
  | "getting-started"
  | "setup"
  | "economy"
  | "leveling"
  | "moderation"
  | "automod"
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