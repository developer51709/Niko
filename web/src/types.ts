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

export type Command = {
  name: string;
  description: string;
  category: string;
  type?: CommandType;
  context_type?: "user" | "message";
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

export type EconomyRow = {
  user_id: string;
  display_name?: string | null;
  username?: string | null;
  avatar_url?: string | null;
  balance?: number;
  bank?: number;
  net_worth: number;
  level: number;
  job: string;
  daily_streak: number;
  achievements?: number;
  total_earned?: number;
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
  economy: { total_coins: number; user_count: number; top: EconomyRow[] };
  moderation: { warn_count: number; automod_active: boolean };
  leveling: { top: LevelRow[] };
};

export type GuildConfig = {
  moderation: Record<string, any>;
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