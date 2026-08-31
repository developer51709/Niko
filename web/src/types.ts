export type BotStats = {
  guild_count: number;
  user_count: number;
  command_count: number;
  uptime_since: string | null;
  version: string;
  economy_users: number;
};

export type Command = {
  name: string;
  description: string;
  category: string;
};

export type Guild = {
  id: string;
  name: string;
  icon_url: string | null;
};

export type User = {
  id: string;
  username?: string;
  global_name?: string;
  avatar?: string | null;
};

export type EconomyRow = {
  user_id: string;
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
  xp: number;
  level: number;
};

export type GuildOverview = {
  economy: { total_coins: number; user_count: number; top: EconomyRow[] };
  moderation: { warn_count: number; automod_active: boolean };
  leveling: { top: LevelRow[] };
};

export type GuildConfig = {
  moderation: Record<string, unknown>;
  ai: { personality?: string; enabled?: string | boolean };
  leveling: {
    xp_enabled?: boolean;
    xp_multiplier?: number;
    xp_cooldown?: number;
    level_up_channel?: string | null;
    level_up_message?: string;
  };
};

export type AuthStatus = {
  authenticated: boolean;
  oauth_available: boolean;
  user?: User;
};