import type {
  AuthStatus,
  BotStats,
  Command,
  Guild,
  GuildConfig,
  GuildResources,
  GuildOverview,
  LevelRow,
  PublicConfig,
  UserOverview,
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
    ...options,
    credentials: "same-origin",
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(payload.error || response.statusText || "Request failed", response.status);
  }
  return payload as T;
}

export const getAuth = () => api<AuthStatus>("/auth/status");
export const getPublicConfig = () => api<PublicConfig>("/api/config");
export const getStats = () => api<BotStats>("/api/botstats");
export const getCommands = () => api<Command[]>("/api/commands");
export const getGuilds = () => api<Guild[]>("/api/guilds");
export const getUserOverview = () => api<UserOverview>("/api/me/overview");
export const getOverview = (id: string) => api<GuildOverview>(`/api/guild/${id}/overview`);
export const getLevels = (id: string) => api<LevelRow[]>(`/api/guild/${id}/levels`);
export const getConfig = (id: string) => api<GuildConfig>(`/api/guild/${id}/config`);
export const getResources = (id: string) => api<GuildResources>(`/api/guild/${id}/resources`);

export function saveConfig(
  id: string,
  section: "automod" | "ai" | "leveling" | "server",
  body: Record<string, unknown>,
  csrfToken?: string,
) {
  return api<{ ok: boolean; config?: Record<string, any> }>(`/api/guild/${id}/config/${section}`, {
    method: "POST",
    headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined,
    body: JSON.stringify(body),
  });
}