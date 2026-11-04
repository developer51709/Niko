import type {
  AchievementsResponse,
  AuthStatus,
  BotEmojisResponse,
  BotStats,
  Command,
  EconomyStanding,
  Guild,
  GuildConfig,
  GuildResources,
  BoosterSettings,
  GuildOverview,
  GuildTicketsResponse,
  LavalinkPoolResponse,
  LevelRow,
  GuildLevelsResponse,
  PublicConfig,
  UserOverview,
  StaffAnalytics,
  StaffMember,
  StaffManagementResponse,
  StaffApplication,
  StaffApplicationSubmission,
  PublicStaffApplication,
  StaffGuild,
  StaffBlacklist,
  StaffBillingResponse,
  StaffBroadcast,
  StaffEmailInbox,
  StaffEmailMessage,
  StaffEmailReport,
  StaffEmailReportTarget,
  LockdownStepResult,
  SocialProfileCardData,
  BlacklistAppeal,
  BlacklistAppealStatus,
  DataRemovalOverview,
  StaffDataRemovalRequest,
  ProxyWorkersResponse,
  ReferralSummary,
  ProxyWorkerRouting,
  NotifierConfig,
  NotifierFollow,
  NotifierResponse,
  StaffMaintenanceResponse,
  OwnerLocales,
  OwnerUpdates,
  OwnerUpdateApply,
  OwnerUpdateProgress,
  StatusPayload,
  TeamRecruitmentOpening,
  TeamRecruitmentSettings,
  TeamRecruitmentSubmission,
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
  const isJson = (response.headers.get("content-type") || "").toLowerCase().includes("json");
  const payload: unknown = isJson ? await response.json().catch(() => null) : null;
  if (!response.ok) {
    const message = payload && typeof payload === "object" && "error" in payload && typeof payload.error === "string"
      ? payload.error
      : response.statusText || "Request failed";
    throw new ApiError(message, response.status);
  }
  if (!isJson || payload === null) {
    throw new ApiError("The server returned an unexpected response. Please try again.", response.status);
  }
  return payload as T;
}

export const getAuth = () => api<AuthStatus>("/auth/status");
export const getDashboardAccess = () => api<{ blacklisted: boolean; scope?: "user"; reason?: string }>("/api/dashboard/access");
export const getPublicConfig = () => api<PublicConfig>("/api/config");
export const getBotEmojis = () => api<BotEmojisResponse>("/api/emojis");
export const getStats = () => api<BotStats>("/api/botstats");
export const getStatus = () => api<StatusPayload>("/api/status");
/** The build the site is serving now; an open tab compares it with its own. */
export const getSiteBuild = (signal?: AbortSignal) => api<{ build: string }>("/api/site/build", { signal });

// ── Owner maintenance controls (staff settings) ─────────────
export const getStaffMaintenance = () => api<StaffMaintenanceResponse>("/api/staff/maintenance");
export const setStaffMaintenance = (
  body: { kind: "cog" | "command"; key: string; enabled: boolean; reason?: string },
  csrfToken?: string,
) => api<StaffMaintenanceResponse>("/api/staff/maintenance", {
  method: "POST",
  headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined,
  body: JSON.stringify(body),
});
// ── Owner localization & updates (staff settings) ───────────────────────────
/** Which languages the live site can render right now, and where they came from. */
export const getOwnerLocales = () => api<OwnerLocales>("/api/owner/locales");
/** Pull beta's catalogues immediately instead of waiting for the next poll. */
export const syncOwnerLocales = (csrfToken?: string) => api<OwnerLocales>("/api/owner/locales/sync", {
  method: "POST",
  headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined,
  body: JSON.stringify({}),
});
/** What beta has that this deployment does not, area by area. */
export const getOwnerUpdates = () => api<OwnerUpdates>("/api/owner/updates");
/** Where the update in flight has got to. */
export const getOwnerUpdateProgress = () => api<OwnerUpdateProgress>("/api/owner/updates/progress");
/** Stage and apply the selected areas, reloading only what changed. */
export const applyOwnerUpdates = (areas: string[], csrfToken?: string) => api<OwnerUpdateApply>("/api/owner/updates/apply", {
  method: "POST",
  headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined,
  body: JSON.stringify({ areas }),
});

export const resolveDiscordText = (text: string, guildId?: string) => api<{
  text: string;
  mention_names: Partial<Record<"user" | "channel" | "role", Record<string, string>>>;
}>("/api/discord/text", {
  method: "POST",
  body: JSON.stringify({ text, ...(guildId ? { guild_id: guildId } : {}) }),
});
export const getTeam = () => api<StaffMember[]>("/api/team");
// `bypassMembership` is the owner devtools switch. The server honours it only
// for a configured owner session, so it cannot be used to skip the real check.
const membershipQuery = (bypassMembership?: boolean) => (bypassMembership ? "?bypass_membership=1" : "");
export const getTeamRecruitmentOpenings = (bypassMembership?: boolean) => api<{ openings: TeamRecruitmentOpening[] }>(`/api/team-recruitment${membershipQuery(bypassMembership)}`);
export const getTeamRecruitmentOpening = (openingId: string, bypassMembership?: boolean) => api<TeamRecruitmentOpening>(`/api/team-recruitment/${encodeURIComponent(openingId)}${membershipQuery(bypassMembership)}`);
export const submitTeamRecruitmentApplication = (openingId: string, answers: Record<string, string | string[]>, csrfToken?: string, bypassMembership?: boolean) => api<{ ok: boolean; message: string }>(`/api/team-recruitment/${encodeURIComponent(openingId)}/submit${membershipQuery(bypassMembership)}`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ answers }) });
export const getTeamRecruitmentSettings = () => api<TeamRecruitmentSettings>("/api/staff/team-recruitment");
export const setTeamRecruitmentOpeningStatus = (openingId: string, status: "open" | "closed", csrfToken?: string) => api<{ ok: boolean; status: string }>(`/api/staff/team-recruitment/${encodeURIComponent(openingId)}/status`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ status }) });
export const getTeamRecruitmentSubmissions = (openingId: string) => api<{ opening: TeamRecruitmentOpening; submissions: TeamRecruitmentSubmission[] }>(`/api/staff/team-recruitment/${encodeURIComponent(openingId)}/submissions`);
export const reviewTeamRecruitmentSubmission = (openingId: string, userId: string, status: "approved" | "denied", csrfToken?: string) => api<{ ok: boolean; review_status: "approved" | "denied"; previous_status?: "pending" | "approved" | "denied"; unchanged?: boolean; dm_sent?: boolean | null; role_revoked?: boolean }>(`/api/staff/team-recruitment/${encodeURIComponent(openingId)}/submissions/${encodeURIComponent(userId)}/review`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ status }) });
export const getTeamMember = (id: string) => api<StaffMember>(`/api/team/${id}`);
export const getTeamProfileCard = (type: string, url: string, signal?: AbortSignal) =>
  api<{ card: SocialProfileCardData }>(`/api/team/profile-card?type=${encodeURIComponent(type)}&url=${encodeURIComponent(url)}`, { signal });
export const getStaffMe = () => api<{ role: string; role_label: string; profile: StaffMember }>("/api/staff/me");
export const getStaffMembers = () => api<StaffManagementResponse>("/api/staff/members");
export const getStaffAnalytics = (days = 30) => api<StaffAnalytics>(`/api/staff/analytics?days=${days}`);
export const manageStaffMember = (userId: string, body: { action: "assign" | "demote" | "suspend" | "lift"; role?: string; reason?: string }, csrfToken?: string) => api<{ ok: boolean; status: string }>(`/api/staff/members/${encodeURIComponent(userId)}/manage`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const getStaffLavalinkPool = () => api<LavalinkPoolResponse>("/api/staff/lavalink");
export const addStaffLavalinkNode = (
  node: { host: string; port: string; password: string; secure: boolean; label: string },
  csrfToken?: string,
) => api<{ ok: boolean; identifier: string; applied: boolean }>("/api/staff/lavalink/nodes", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(node) });
export const removeStaffLavalinkNode = (identifier: string, csrfToken?: string) => api<{ ok: boolean }>(`/api/staff/lavalink/nodes/${encodeURIComponent(identifier)}`, { method: "DELETE", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined });
export const applyStaffLavalinkChanges = (csrfToken?: string) => api<{ ok: boolean }>("/api/staff/lavalink/apply", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined });
export const getStaffProxyWorkers = () => api<ProxyWorkersResponse>("/api/staff/proxy-workers");
export const addStaffProxyWorker = (name: string, url: string, csrfToken?: string) => api<{ ok: boolean }>("/api/staff/proxy-workers", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ name, url }) });
export const removeStaffProxyWorker = (id: string, csrfToken?: string) => api<{ ok: boolean }>(`/api/staff/proxy-workers/${encodeURIComponent(id)}`, { method: "DELETE", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined });
export const setStaffProxyWorkerRouting = (enabled: boolean, csrfToken?: string) => api<{ ok: boolean; routing: ProxyWorkerRouting }>("/api/staff/proxy-workers/routing", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ enabled }) });
export const saveStaffProfile = (body: Record<string, unknown>, csrfToken?: string) => api<{ ok: boolean }>("/api/staff/profile", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const saveGlobalProfile = (body: Record<string, unknown>, csrfToken?: string) => api<{ ok: boolean }>("/api/staff/global-profile", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const getStaffGuilds = () => api<{ guilds: StaffGuild[]; count: number; role: string }>("/api/staff/guilds");
export const setStaffGuildBlacklist = (guildId: string, action: "add" | "remove", reason: string, csrfToken?: string) => api<{ ok: boolean; blacklisted: boolean }>(`/api/staff/guilds/${guildId}/blacklist`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ action, reason }) });
export const resetStaffGuildProfile = (guildId: string, csrfToken?: string) => api<{ ok: boolean }>(`/api/staff/guilds/${guildId}/profile/reset`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({}) });
// One lockdown step per request: the dashboard shows the progress of the feature
// it names, and a failure is reported for that step alone.
export const lockdownStaffGuild = (guildId: string, step: string, csrfToken?: string) => api<{ ok: boolean; blacklisted: boolean } & LockdownStepResult>(`/api/staff/guilds/${guildId}/blacklist/lockdown`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ step }) });
export const sendStaffGuildNotice = (guildId: string, message: string, csrfToken?: string) => api<{ ok: boolean; recipient_id: string }>(`/api/staff/guilds/${guildId}/moderation-notice`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ message }) });
export const getStaffBlacklist = () => api<StaffBlacklist>("/api/staff/blacklist");
export const getStaffErrorReports = () => api<{ reports: { code: string; report: string; created_at: string }[]; count: number }>("/api/staff/error-reports");
export const getStaffBilling = () => api<StaffBillingResponse>("/api/staff/billing");
export const getStaffEmail = () => api<StaffEmailInbox>("/api/staff/email");
// The report form is reached from an email, by whoever received it: the token
// in the link is the whole credential and it names one message.
export const getEmailReport = (token: string) => api<{ target: StaffEmailReportTarget }>(`/api/staff/email/report/${encodeURIComponent(token)}`);
export const submitEmailReport = (token: string, body: { reason: string; details: string; include_thread: boolean }) => api<{ ok: boolean; report: StaffEmailReport }>(`/api/staff/email/report/${encodeURIComponent(token)}`, { method: "POST", body: JSON.stringify(body) });
export const getEmailReports = () => api<{ reports: StaffEmailReport[]; open: number; domain: string }>("/api/staff/email/reports");
export const actOnEmailReport = (reportId: string, body: { action: "reply" | "close"; message?: string }, csrfToken?: string) => api<{ ok: boolean; report: StaffEmailReport; message: StaffEmailMessage | null }>(`/api/staff/email/reports/${encodeURIComponent(reportId)}`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const getStaffEmailMessage = (messageId: string) => api<{ message: StaffEmailMessage }>(`/api/staff/email/${encodeURIComponent(messageId)}`);
// The mail composer sends multipart, because a formatted body and file
// attachments cannot travel in a JSON request.
export async function sendStaffEmail(
  draft: {
    mailbox: string;
    to: string;
    subject: string;
    body: string;
    html?: string;
    thread_id?: string;
    attachments?: File[];
  },
  csrfToken?: string,
) {
  const form = new FormData();
  form.append("mailbox", draft.mailbox);
  form.append("to", draft.to);
  form.append("subject", draft.subject);
  form.append("body", draft.body);
  form.append("html", draft.html || "");
  if (draft.thread_id) form.append("thread_id", draft.thread_id);
  for (const file of draft.attachments || []) form.append("attachments", file, file.name);
  const response = await fetch("/api/staff/email/send", {
    method: "POST",
    credentials: "same-origin",
    cache: "no-store",
    headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined,
    body: form,
  });
  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const message = payload && typeof payload === "object" && "error" in payload && typeof payload.error === "string"
      ? payload.error
      : response.statusText || "The message could not be sent.";
    throw new ApiError(message, response.status);
  }
  return payload as { ok: boolean; message: StaffEmailMessage };
}
// `status: null` saves the note without changing the decision, `"clear"`
// undoes it. The note is always written, so text is never lost by not pressing
// a decision button.
export const resolveStaffBillingPayment = (orderId: string, status: "open" | "resolved" | "clear" | null, note: string, csrfToken?: string) => api<{ ok: boolean; issue_status: string | null; issue_note: string }>(`/api/staff/billing/payments/${encodeURIComponent(orderId)}/resolve`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(status === null ? { note } : { status, note }) });
export const updateStaffSubscription = (guildId: string, action: "grant" | "cancel", months: number, csrfToken?: string) => api<{ ok: boolean; premium: StaffBillingResponse["subscriptions"][number] }>(`/api/staff/billing/subscriptions/${encodeURIComponent(guildId)}`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ action, months }) });
export const getDataRemovalOverview = () => api<DataRemovalOverview>("/api/privacy/data-removal");
export const submitDataRemovalRequest = (body: { scope: "account" | "server"; guild_id?: string; reason: string; confirmation: string }, csrfToken?: string) => api<{ ok: boolean; request: DataRemovalOverview["requests"][number] }>("/api/privacy/data-removal", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const withdrawDataRemovalRequest = (requestId: string, csrfToken?: string) => api<{ ok: boolean; status: string }>(`/api/privacy/data-removal/${encodeURIComponent(requestId)}`, { method: "DELETE", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined });
export const getStaffDataRemovalRequests = () => api<{ requests: StaffDataRemovalRequest[]; pending: number }>("/api/staff/data-removal");
export const reviewStaffDataRemoval = (requestId: string, status: "approved" | "denied", note: string, csrfToken?: string) => api<{ ok: boolean; status: string; result?: { removed?: string[]; errors?: string[] } }>(`/api/staff/data-removal/${encodeURIComponent(requestId)}/review`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ status, note }) });
export const getBlacklistAppealStatus = () => api<BlacklistAppealStatus>("/api/appeals/blacklist");
export const submitBlacklistAppeal = (appeal: string, csrfToken?: string) => api<{ ok: boolean; appeal_id: string; status: "pending" }>("/api/appeals/blacklist", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ appeal }) });
export const getGuildBlacklistAppealStatus = (guildId: string) => api<BlacklistAppealStatus>(`/api/appeals/guild/${encodeURIComponent(guildId)}`);
export const submitGuildBlacklistAppeal = (guildId: string, appeal: string, csrfToken?: string) => api<{ ok: boolean; appeal_id: string; status: "pending" }>(`/api/appeals/guild/${encodeURIComponent(guildId)}`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ appeal }) });
export const getStaffBlacklistAppeals = () => api<{ appeals: BlacklistAppeal[] }>("/api/staff/blacklist-appeals");
export const reviewStaffBlacklistAppeal = (appealId: string, status: "approved" | "denied", note: string, csrfToken?: string) => api<{ ok: boolean; status: "approved" | "denied" }>(`/api/staff/blacklist-appeals/${encodeURIComponent(appealId)}/review`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ status, note }) });
export const updateStaffBlacklist = (type: "user" | "guild", action: "add" | "remove" | "update", id: string, reason: string, csrfToken?: string) => api<{ ok: boolean }>("/api/staff/blacklist", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ type, action, id, reason }) });
export const createStaffGuildInvite = (guildId: string, csrfToken?: string) => api<{ ok: boolean; url: string; channel: string; expires_in: number; max_uses: number }>(`/api/staff/guilds/${guildId}/invite`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({}) });
export const leaveStaffGuild = (guildId: string, csrfToken?: string) => api<{ ok: boolean }>(`/api/staff/guilds/${guildId}/leave`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({}) });
export const getCommands = () => api<Command[]>("/api/commands");
export const getGuilds = () => api<Guild[]>("/api/guilds");
export const getUserOverview = () => api<UserOverview>("/api/me/overview");
export const saveEconomyPrivacy = (leaderboard_private: boolean, csrfToken?: string) => api<{ ok: boolean; leaderboard_private: boolean }>("/api/me/economy-privacy", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ leaderboard_private }) });
export const getOverview = (id: string) => api<GuildOverview>(`/api/guild/${id}/overview`);
export const getMyEconomy = () => api<EconomyStanding>("/api/me/economy");
export const getMyAchievements = () => api<AchievementsResponse>("/api/me/achievements");
export const getMyReferrals = () => api<ReferralSummary>("/api/me/referrals");
export const getLevels = (id: string) => api<LevelRow[]>(`/api/guild/${id}/levels`);
export const getGuildLeaderboard = (id: string, page = 1) => api<GuildLevelsResponse>(`/api/levels/${encodeURIComponent(id)}?page=${page}`);
export const getConfig = (id: string) => api<GuildConfig>(`/api/guild/${id}/config`);
export const getResources = (id: string) => api<GuildResources>(`/api/guild/${id}/resources`);
export const getBoosterSettings = (id: string) =>
  api<{ config: BoosterSettings; placeholders: string[] }>(`/api/guild/${id}/boosters`);
export const saveBoosterSettings = (
  id: string,
  body: Partial<BoosterSettings>,
  csrfToken?: string,
) => api<{ ok: boolean; config: BoosterSettings }>(`/api/guild/${id}/boosters`, {
  method: "POST",
  headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined,
  body: JSON.stringify(body),
});
export const getGuildTickets = (id: string) => api<GuildTicketsResponse>(`/api/guild/${id}/tickets`);
export const updateGuildTicketStatus = (guildId: string, channelId: string, status: "open" | "closed", csrfToken?: string) => api<{ ok: boolean; status: string }>(`/api/guild/${guildId}/tickets/${channelId}/status`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ status }) });
export const getStaffApplications = (id: string) => api<StaffApplication[]>(`/api/guild/${id}/applications`);
export const createStaffApplication = (id: string, body: Record<string, unknown>, csrfToken?: string) => api<{ ok: boolean; application: StaffApplication }>(`/api/guild/${id}/applications`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const updateStaffApplication = (guildId: string, applicationId: string, body: Record<string, unknown>, csrfToken?: string) => api<{ ok: boolean; application: StaffApplication }>(`/api/guild/${guildId}/applications/${applicationId}`, { method: "PUT", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const setStaffApplicationStatus = (guildId: string, applicationId: string, status: "open" | "closed", csrfToken?: string) => api<{ ok: boolean; status: string }>(`/api/guild/${guildId}/applications/${applicationId}/status`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ status }) });
export const deleteStaffApplication = (guildId: string, applicationId: string, csrfToken?: string) => api<{ ok: boolean }>(`/api/guild/${guildId}/applications/${applicationId}`, { method: "DELETE", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined });
export const getStaffSubmissions = (guildId: string, applicationId: string) => api<{ application: StaffApplication; submissions: StaffApplicationSubmission[] }>(`/api/guild/${guildId}/applications/${applicationId}/submissions`);
export const reviewStaffSubmission = (guildId: string, applicationId: string, userId: string, status: "approved" | "denied", csrfToken?: string) => api<{ ok: boolean; review_status: "approved" | "denied"; previous_status?: "pending" | "approved" | "denied"; unchanged?: boolean; reviewed_by?: string | null; reviewed_at?: string | null }>(`/api/guild/${guildId}/applications/${applicationId}/submissions/${userId}/review`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ status }) });
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

// ── Social notifier (dashboard notifications tab) ────────────────────────────
// An empty string clears the stored channel or role; omitting a key leaves it
// untouched, so each edit sends only the field it actually changes.

export const getGuildNotifier = (id: string) => api<NotifierResponse>(`/api/guild/${id}/notifier`);
export const saveNotifierConfig = (
  id: string,
  body: { enabled?: boolean; default_channel_id?: string | null; ping_role_id?: string | null },
  csrfToken?: string,
) => api<{ ok: boolean; config: NotifierConfig }>(`/api/guild/${id}/notifier/config`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const addNotifierFollow = (
  id: string,
  body: { platform: string; query: string; channel_id?: string | null; ping_role_id?: string | null; template?: string },
  csrfToken?: string,
) => api<{ ok: boolean; created: boolean; follow: NotifierFollow }>(`/api/guild/${id}/notifier/follows`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const updateNotifierFollow = (
  id: string,
  body: { platform: string; username: string; channel_id?: string | null; ping_role_id?: string | null; template?: string; enabled?: boolean },
  csrfToken?: string,
) => api<{ ok: boolean; follow: NotifierFollow }>(`/api/guild/${id}/notifier/follows/update`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const removeNotifierFollow = (id: string, platform: string, username: string, csrfToken?: string) => api<{ ok: boolean }>(`/api/guild/${id}/notifier/follows/${encodeURIComponent(platform)}/${encodeURIComponent(username)}`, { method: "DELETE", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined });
export const testNotifierFollow = (id: string, platform: string, username: string, csrfToken?: string) => api<{ ok: boolean; delivered: boolean; message?: string; channel?: string }>(`/api/guild/${id}/notifier/test`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({ platform, username }) });

// ── Staff broadcast studio ───────────────────────────────────────────────────
// Uploads are the only multipart calls in the dashboard: a JSON content type
// would swallow the file, so they build their own request and skip `api()`.

export async function uploadStaffBroadcastMedia(broadcastId: string, file: File, csrfToken?: string) {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`/api/staff/broadcasts/${encodeURIComponent(broadcastId)}/media`, {
    method: "POST",
    credentials: "same-origin",
    cache: "no-store",
    headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined,
    body: form,
  });
  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const message = payload && typeof payload === "object" && "error" in payload && typeof payload.error === "string"
      ? payload.error
      : response.statusText || "The image could not be uploaded.";
    throw new ApiError(message, response.status);
  }
  return payload as { broadcast: StaffBroadcast; syncing: boolean };
}

export const getStaffBroadcasts = () => api<{ broadcasts: StaffBroadcast[] }>("/api/staff/broadcasts");
export const getStaffBroadcast = (id: string) => api<{ broadcast: StaffBroadcast }>(`/api/staff/broadcasts/${encodeURIComponent(id)}`);
export const createStaffBroadcast = (csrfToken?: string) => api<{ broadcast: StaffBroadcast }>("/api/staff/broadcasts", { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({}) });
export const updateStaffBroadcast = (id: string, body: { title: string; body: string; accent: string; footer: string }, csrfToken?: string) => api<{ broadcast: StaffBroadcast; syncing: boolean }>(`/api/staff/broadcasts/${encodeURIComponent(id)}`, { method: "PUT", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify(body) });
export const deleteStaffBroadcast = (id: string, csrfToken?: string) => api<{ ok: boolean }>(`/api/staff/broadcasts/${encodeURIComponent(id)}`, { method: "DELETE", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined });
export const deleteStaffBroadcastMedia = (id: string, mediaId: string, csrfToken?: string) => api<{ broadcast: StaffBroadcast; syncing: boolean }>(`/api/staff/broadcasts/${encodeURIComponent(id)}/media/${encodeURIComponent(mediaId)}`, { method: "DELETE", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined });
export const sendStaffBroadcast = (id: string, csrfToken?: string) => api<{ broadcast: StaffBroadcast }>(`/api/staff/broadcasts/${encodeURIComponent(id)}/send`, { method: "POST", headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined, body: JSON.stringify({}) });