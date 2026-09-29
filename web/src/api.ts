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
  StaffMember,
  StaffApplication,
  StaffApplicationSubmission,
  PublicStaffApplication,
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
export const getTeam = () => api<StaffMember[]>("/api/team");
export const getTeamMember = (id: string) => api<StaffMember>(`/api/team/${id}`);
export const getStaffMe = () => api<{ role: string; role_label: string; profile: StaffMember }>("/api/staff/me");
export const saveStaffProfile = (body: Record<string, unknown>, csrfToken?: string) => api<{ ok: boolean }>("/api/staff/profile", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const saveGlobalProfile = (body: Record<string, unknown>, csrfToken?: string) => api<{ ok: boolean }>("/api/staff/global-profile", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const getCommands = () => api<Command[]>("/api/commands");
export const getGuilds = () => api<Guild[]>("/api/guilds");
export const getUserOverview = () => api<UserOverview>("/api/me/overview");
export const getOverview = (id: string) => api<GuildOverview>(`/api/guild/${id}/overview`);
export const getLevels = (id: string) => api<LevelRow[]>(`/api/guild/${id}/levels`);
export const getConfig = (id: string) => api<GuildConfig>(`/api/guild/${id}/config`);
export const getResources = (id: string) => api<GuildResources>(`/api/guild/${id}/resources`);
export const getStaffApplications = (id: string) => api<StaffApplication[]>(`/api/guild/${id}/applications`);
export const createStaffApplication = (id: string, body: Record<string, unknown>, csrfToken?: string) => api<{ ok: boolean; application: StaffApplication }>(`/api/guild/${id}/applications`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const updateStaffApplication = (guildId: string, applicationId: string, body: Record<string, unknown>, csrfToken?: string) => api<{ ok: boolean; application: StaffApplication }>(`/api/guild/${guildId}/applications/${applicationId}`, { method: "PUT", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const setStaffApplicationStatus = (guildId: string, applicationId: string, status: "open" | "closed", csrfToken?: string) => api<{ ok: boolean; status: string }>(`/api/guild/${guildId}/applications/${applicationId}/status`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ status }) });
export const deleteStaffApplication = (guildId: string, applicationId: string, csrfToken?: string) => api<{ ok: boolean }>(`/api/guild/${guildId}/applications/${applicationId}`, { method: "DELETE", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined });
export const getStaffSubmissions = (guildId: string, applicationId: string) => api<{ application: StaffApplication; submissions: StaffApplicationSubmission[] }>(`/api/guild/${guildId}/applications/${applicationId}/submissions`);
export const reviewStaffSubmission = (guildId: string, applicationId: string, userId: string, status: "approved" | "denied", csrfToken?: string) => api<{ ok: boolean; review_status: "approved" | "denied"; reviewed_by?: string | null; reviewed_at?: string | null }>(`/api/guild/${guildId}/applications/${applicationId}/submissions/${userId}/review`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ status }) });
export const getPublicOpenings = (guildId: string) => api<{ openings: PublicStaffApplication[] }>(`/api/applications/${guildId}`);
export const getPublicStaffApplication = (guildId: string, applicationId: string) => api<PublicStaffApplication>(`/api/applications/${guildId}/${applicationId}`);
export const submitStaffApplication = (guildId: string, applicationId: string, answers: Record<string, string | string[]>, csrfToken?: string) => api<{ ok: boolean; message: string }>(`/api/applications/${guildId}/${applicationId}/submit`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ answers }) });

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

export function saveProfile(
  id: string,
  body: Record<string, unknown>,
  csrfToken?: string,
) {
  return api<{ ok: boolean; profile?: Record<string, any> }>(`/api/guild/${id}/config/profile`, {
    method: "POST",
    headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined,
    body: JSON.stringify(body),
  });
}