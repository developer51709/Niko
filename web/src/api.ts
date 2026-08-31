import type {
  AuthStatus,
  BotStats,
  Command,
  EconomyRow,
  Guild,
  GuildConfig,
  GuildOverview,
  LevelRow,
} from "./types";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(payload.error || response.statusText || "Request failed", response.status);
  }
  return payload as T;
}

export const getAuth = () => api<AuthStatus>("/auth/status");
export const getStats = () => api<BotStats>("/api/botstats");
export const getCommands = () => api<Command[]>("/api/commands");
export const getGuilds = () => api<Guild[]>("/api/guilds");
export const getOverview = (id: string) => api<GuildOverview>(`/api/guild/${id}/overview`);
export const getEconomy = (id: string) => api<EconomyRow[]>(`/api/guild/${id}/economy`);
export const getLevels = (id: string) => api<LevelRow[]>(`/api/guild/${id}/levels`);
export const getConfig = (id: string) => api<GuildConfig>(`/api/guild/${id}/config`);

export function saveConfig(id: string, section: "automod" | "ai", body: Record<string, unknown>) {
  return api<{ ok: boolean }>(`/api/guild/${id}/config/${section}`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}