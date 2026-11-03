import { useEffect, useState } from "react";
import type { KeyboardEvent } from "react";
import { createStaffGuildInvite, getAuth, getGuilds, getTeamRecruitmentSettings, getTeamRecruitmentSubmissions, getStaffBilling, getStaffDataRemovalRequests, getStaffMembers, getStaffBlacklist, getStaffBlacklistAppeals, getStaffErrorReports, getStaffGuilds, getStaffMe, getStats, leaveStaffGuild, manageStaffMember, resetStaffGuildProfile, resolveStaffBillingPayment, reviewStaffDataRemoval, reviewTeamRecruitmentSubmission, reviewStaffBlacklistAppeal, saveGlobalProfile, saveStaffProfile, sendStaffGuildNotice, setTeamRecruitmentOpeningStatus, setStaffGuildBlacklist, updateStaffBlacklist, updateStaffSubscription } from "../api";
import { DiscordMarkdown } from "../components/DiscordMarkdown";
import { DiscordStatusAvatar } from "../components/DiscordStatusAvatar";
import { Icon } from "../components/Icon";
import { clearToasts, notifyError, notifyLoading, notifySuccess } from "../utils/toast";
import { LOCKDOWN_STATUS_LABELS, blacklistGuildWithLockdown, groupLockdownSteps } from "../utils/guildBlacklist";
import type { GuildLockdownSummary } from "../utils/guildBlacklist";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { ProxyWorkersView } from "../components/dashboard/ProxyWorkersView";
import { LavalinkView } from "../components/dashboard/LavalinkView";
import { BotAnalyticsView } from "../components/dashboard/BotAnalyticsView";
import { BroadcastStudioView } from "../components/dashboard/BroadcastStudioView";
import { MaintenanceView } from "../components/dashboard/MaintenanceView";
import { LocaleSyncView } from "../components/staff/LocaleSyncView";
import { UpdatesView } from "../components/staff/UpdatesView";
import { Switch } from "../components/dashboard/Switch";
import { ColorPicker } from "../components/dashboard/ColorPicker";
import { Select, selectOptions } from "../components/dashboard/Select";
import { SettingCard, SettingCards } from "../components/dashboard/SettingCards";
import { AuthScreen, DiscordSignIn } from "../components/AuthScreen";
import { dashboardPath, dashboardServersPath, dashboardUserPath, navigate } from "../router";
import { useStrings } from "../i18n";
import type { AuthStatus, BlacklistAppeal, BotStats, Guild, PublicProfileLink, TeamRecruitmentOpening, TeamRecruitmentSubmission, StaffBillingPayment, StaffBillingResponse, StaffBlacklistEntry, StaffDataRemovalRequest, StaffGuild, StaffMember, StaffRosterRole } from "../types";

type ReviewedTeamSubmission = TeamRecruitmentSubmission & {
  opening_id: string;
  opening_title: string;
  role_name?: string | null;
};

const PUBLIC_LINK_TYPES = [
  ["website", "Website"],
  ["github", "GitHub"],
  ["instagram", "Instagram"],
  ["x", "X"],
  ["tiktok", "TikTok"],
  ["youtube", "YouTube"],
  ["twitch", "Twitch"],
  ["bluesky", "Bluesky"],
  ["linkedin", "LinkedIn"],
  ["reddit", "Reddit"],
  ["mastodon", "Mastodon"],
  ["facebook", "Facebook"],
  ["discord", "Discord"],
  ["other", "Other"],
] as const;

const CARD_THEMES = selectOptions([["dark", "Dark"], ["light", "Light"]]);
const BLACKLIST_TYPES = selectOptions([["user", "User"], ["guild", "Guild"]]);

type StaffTab = "profile" | "analytics" | "global" | "guilds" | "blacklist" | "appeals" | "proxy-workers" | "lavalink" | "maintenance" | "locales" | "updates" | "team-recruitment" | "staff-management" | "broadcasts" | "billing" | "data-removal" | "reports";

const OWNER_ROLES = ["owner"];

/**
 * The badge a payment earns: its billing decision comes first, then whether the
 * provider was actually paid. A waiting payment and a paid one must never wear
 * the same pill.
 */
function billingPaymentState(payment: StaffBillingPayment): { label: string; className: string } {
  if (payment.issue_status === "open") return { label: "Needs attention", className: "is-blocked" };
  if (payment.issue_status === "resolved") return { label: "Resolved", className: "is-resolved" };
  if (payment.paid) return { label: "Paid", className: "is-approved" };
  const status = (payment.status || "").toLowerCase();
  if (status === "expired" || status === "failed") {
    return { label: payment.status || "Expired", className: "is-blocked" };
  }
  return { label: "Awaiting payment", className: "is-pending" };
}

// One source of truth for tab access: the sidebar buttons and the deep-link
// guard both read it, so a role can never reach a panel it may not open.
const TAB_ROLES: Record<StaffTab, string[]> = {
  profile: [],
  analytics: [],
  global: ["owner", "head_admin", "graphic_designer"],
  guilds: ["owner", "head_admin"],
  blacklist: ["owner", "head_admin"],
  appeals: ["owner", "head_admin"],
  "proxy-workers": OWNER_ROLES,
  lavalink: OWNER_ROLES,
  maintenance: OWNER_ROLES,
  locales: OWNER_ROLES,
  updates: OWNER_ROLES,
  "team-recruitment": OWNER_ROLES,
  "staff-management": OWNER_ROLES,
  broadcasts: OWNER_ROLES,
  billing: OWNER_ROLES,
  "data-removal": OWNER_ROLES,
  reports: [],
};

/** An empty role list means every staff member may open the tab. */
function tabAllowedForRole(role: string, tab: StaffTab): boolean {
  const roles = TAB_ROLES[tab];
  return roles.length === 0 || roles.includes(role);
}

/** Read a deep-linked tab from the URL hash, ignoring unknown or inaccessible ones. */
function tabFromHash(hash: string, role: string | null): StaffTab | null {
  const name = hash.replace(/^#/, "").trim().toLocaleLowerCase() as StaffTab;
  if (!(name in TAB_ROLES)) return null;
  if (role && !tabAllowedForRole(role, name)) return null;
  return name;
}

function tabFromTabButton(button: HTMLButtonElement): StaffTab | null {
  const name = /^staff-(.+)-tab$/.exec(button.id)?.[1] as StaffTab | undefined;
  return name && name in TAB_ROLES ? name : null;
}

/** The brand accent the staff card uses when no custom colour is saved. */
const CARD_ACCENT_FALLBACK = "#C8A882";

export function StaffDashboardPage() {
  const { t } = useStrings("staff");
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [accessLoading, setAccessLoading] = useState(true);
  const [staff, setStaff] = useState<{ role: string; role_label: string; profile: StaffMember } | null>(null);
  const [stats, setStats] = useState<BotStats | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [form, setForm] = useState({
    public_bio: "",
    public_banner_url: "",
    public_visible: true,
    card_theme: "dark" as "dark" | "light",
    card_accent: CARD_ACCENT_FALLBACK,
    card_show_status: true,
  });
  const [links, setLinks] = useState<PublicProfileLink[]>([]);
  // The card endpoint is never cached, so each tick pulls the current Discord
  // presence into the dashboard preview while the profile tab is open.
  const [cardPreviewStamp, setCardPreviewStamp] = useState(() => Date.now());
  const [global, setGlobal] = useState({ avatar_url: "", banner_url: "" });
  // Staff access is the only failure that replaces the whole page; every result
  // a staff member triggers from a tab is reported as a toast instead.
  const [accessError, setAccessError] = useState("");
  const [saving, setSaving] = useState(false);
  // Card settings have their own save so a README card change never depends on
  // (or gets bundled with) the public listing form.
  const [savingCard, setSavingCard] = useState(false);
  const [savingGlobal, setSavingGlobal] = useState(false);
  const [activeTab, setActiveTab] = useState<StaffTab>(() => tabFromHash(window.location.hash, null) ?? "profile");
  const [nikoApplications, setNikoApplications] = useState<TeamRecruitmentOpening[]>([]);
  const [nikoSubmissions, setNikoSubmissions] = useState<ReviewedTeamSubmission[]>([]);
  const [nikoBusy, setNikoBusy] = useState(false);
  const [staffRoster, setStaffRoster] = useState<StaffMember[]>([]);
  const [staffRosterRoles, setStaffRosterRoles] = useState<StaffRosterRole[]>([]);
  const [staffRosterLoading, setStaffRosterLoading] = useState(false);
  const [staffRosterBusy, setStaffRosterBusy] = useState(false);
  const [staffRosterSearch, setStaffRosterSearch] = useState("");
  const [staffRosterRoleDrafts, setStaffRosterRoleDrafts] = useState<Record<string, string>>({});
  const [newStaffId, setNewStaffId] = useState("");
  const [newStaffRole, setNewStaffRole] = useState("");
  // Only the silent 5s poll writes this: it is live status, not an answer to an
  // action, so it stays on the panel instead of becoming a repeating toast.
  const [appeals, setAppeals] = useState<BlacklistAppeal[]>([]);
  const [appealsLoading, setAppealsLoading] = useState(false);
  const [appealNotes, setAppealNotes] = useState<Record<string, string>>({});
  const [reviewingAppealId, setReviewingAppealId] = useState<string | null>(null);
  const [errorReports, setErrorReports] = useState<{ code: string; report: string; created_at: string }[]>([]);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [reportSearch, setReportSearch] = useState("");
  const [expandedReportCode, setExpandedReportCode] = useState<string | null>(null);
  const [billing, setBilling] = useState<StaffBillingResponse | null>(null);
  const [billingBusy, setBillingBusy] = useState(false);
  const [billingNotes, setBillingNotes] = useState<Record<string, string>>({});
  const [billingGuild, setBillingGuild] = useState("");
  const [billingMonths, setBillingMonths] = useState("1");
  const [dataRemoval, setDataRemoval] = useState<StaffDataRemovalRequest[] | null>(null);
  const [dataRemovalNotes, setDataRemovalNotes] = useState<Record<string, string>>({});
  const [dataRemovalBusy, setDataRemovalBusy] = useState(false);
  const [staffGuilds, setStaffGuilds] = useState<StaffGuild[]>([]);
  const [staffGuildsLoading, setStaffGuildsLoading] = useState(false);
  const [expandedGuildId, setExpandedGuildId] = useState<string | null>(null);
  const [guildSearch, setGuildSearch] = useState("");
  const [busyGuildAction, setBusyGuildAction] = useState(false);
  const [blacklistReason, setBlacklistReason] = useState("");
  const [noticeMessage, setNoticeMessage] = useState("");
  const [guildBlacklistReason, setGuildBlacklistReason] = useState("");
  const [blacklistEntries, setBlacklistEntries] = useState<{ users: StaffBlacklistEntry[]; guilds: StaffBlacklistEntry[] }>({ users: [], guilds: [] });
  const [blacklistType, setBlacklistType] = useState<"user" | "guild">("user");
  const [blacklistId, setBlacklistId] = useState("");
  const [blacklistSearch, setBlacklistSearch] = useState("");
  const [permissionGuild, setPermissionGuild] = useState<StaffGuild | null>(null);
  const [inviteUrl, setInviteUrl] = useState("");
  const [inviteGuildId, setInviteGuildId] = useState<string | null>(null);
  // Set once a blacklist lockdown finishes: the panel lists what was paused,
  // skipped, and could not be switched off, then the staff member closes it.
  const [lockdownSummary, setLockdownSummary] = useState<GuildLockdownSummary | null>(null);

  useEffect(() => {
    let active = true;
    getAuth().then(async (authStatus) => {
      if (!active) return;
      setAuth(authStatus);
      if (!authStatus.authenticated) {
        setAccessLoading(false);
        return;
      }
      const staffStatus = await getStaffMe();
      if (!active) return;
      setStaff(staffStatus);
      setAccessLoading(false);
      const [botStats, availableGuilds] = await Promise.all([getStats(), getGuilds()]);
      if (!active) return;
      setStats(botStats);
      setGuilds(availableGuilds);
      setForm({
        public_bio: staffStatus.profile.bio || "",
        public_banner_url: staffStatus.profile.public_banner_url || "",
        public_visible: staffStatus.profile.visible !== false,
        card_theme: staffStatus.profile.card?.theme === "light" ? "light" : "dark",
        card_accent: staffStatus.profile.card?.accent ? `#${staffStatus.profile.card.accent}` : CARD_ACCENT_FALLBACK,
        card_show_status: staffStatus.profile.card?.show_status !== false,
      });
      setLinks(staffStatus.profile.public_links || []);
      if (staffStatus.role === "owner") {
        void refreshNikoApplications();
        void refreshBilling();
        void refreshStaffRoster();
      }
      if (tabAllowedForRole(staffStatus.role, "guilds")) {
        setStaffGuildsLoading(true);
        getStaffGuilds().then((result) => setStaffGuilds(result.guilds)).catch((reason) => notifyError(reason instanceof Error ? reason.message : t("guilds.listUnavailable"), "staff-guilds")).finally(() => setStaffGuildsLoading(false));
        getStaffBlacklist().then(setBlacklistEntries).catch((reason) => notifyError(reason instanceof Error ? reason.message : t("blacklist.unavailable"), "staff-blacklist"));
        if (["owner", "head_admin"].includes(staffStatus.role)) {
          getStaffBlacklistAppeals().then((result) => setAppeals(result.appeals)).catch((reason) => notifyError(reason instanceof Error ? reason.message : t("appeals.unavailable"), "staff-appeals"));
        }
      }
      void loadErrorReports();
    }).catch((reason) => {
      if (active) {
        setAccessError(reason instanceof Error ? reason.message : t("staffAuth.unavailableTitle"));
        setAccessLoading(false);
      }
    });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    const syncFromHash = () => {
      const linked = tabFromHash(window.location.hash, null);
      if (linked) setActiveTab(linked);
    };
    syncFromHash();
    window.addEventListener("hashchange", syncFromHash);
    return () => window.removeEventListener("hashchange", syncFromHash);
  }, []);
  useEffect(() => {
    // Keep the URL shareable and never leave a panel blank: a hand-typed hash
    // or a role change falls back to the profile tab the member can always open.
    if (staff && !tabAllowedForRole(staff.role, activeTab)) {
      setActiveTab("profile");
      return;
    }
    const target = `#${activeTab}`;
    if (staff && window.location.hash !== target) window.history.replaceState(null, "", target);
  }, [staff?.role, activeTab]);
  useEffect(() => {
    // Refresh live queues when their tab is opened instead of showing whatever
    // was loaded when the page first mounted.
    if (!staff) return;
    if (activeTab === "reports") void loadErrorReports();
    else if (activeTab === "appeals") void loadAppeals();
    else if (activeTab === "billing") void refreshBilling();
    else if (activeTab === "staff-management") void refreshStaffRoster();
    else if (activeTab === "data-removal") void refreshDataRemoval();
  }, [staff?.role, activeTab]);

  useEffect(() => {
    if (activeTab !== "profile") return;
    const refresh = () => {
      if (!document.hidden) setCardPreviewStamp(Date.now());
    };
    const timer = window.setInterval(refresh, 30000);
    // A tab that was hidden for a while shows the status from when it left;
    // refresh as soon as it is visible again.
    document.addEventListener("visibilitychange", refresh);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, [activeTab]);

  if (accessLoading) return <div className="dashboard-state"><div className="loading-ring" /><p>{t("staffAuth.verifying")}</p></div>;
  if (accessError || !staff || !auth?.authenticated) return <AuthScreen
    eyebrow={t("staffAuth.eyebrow")}
    title={!auth && accessError ? t("staffAuth.unavailableTitle") : <>{t("staffAuth.privateBefore")} <em>{t("staffAuth.privateEmphasis")}</em></>}
    description={!auth && accessError ? accessError : !auth?.authenticated ? t("staffAuth.signedOut") : accessError || t("staffAuth.staffOnly")}
    back={{ label: t("staffAuth.back"), onClick: () => navigate("/dashboard") }}
  >
    {auth && !auth.authenticated && <DiscordSignIn next="/dashboard/staff" available={auth.oauth_available} />}
  </AuthScreen>;

  const signedInUser = auth.user!;
  const discordDefaultAvatar = `https://cdn.discordapp.com/embed/avatars/${Number(BigInt(signedInUser.id) % 5n)}.png`;
  const signedInAvatar = signedInUser.avatar
    ? `https://cdn.discordapp.com/avatars/${signedInUser.id}/${signedInUser.avatar}.png?size=128`
    : discordDefaultAvatar;
  // The preview follows the unsaved draft, so a theme, accent, or status change
  // is visible before the listing is saved. The embedded card caches for a
  // minute on GitHub and uses the saved values from the same profile row.
  const cardBaseUrl = `${window.location.origin}/staff/${staff.profile.id}/card.svg`;
  const cardPreviewUrl = `${cardBaseUrl}?theme=${form.card_theme}&accent=${encodeURIComponent(form.card_accent.replace(/^#/, "").toUpperCase())}&status=${form.card_show_status ? 1 : 0}&t=${cardPreviewStamp}`;
  // The image itself is the link, so clicking the card on GitHub opens the
  // member's public staff profile instead of the raw SVG.
  // The shareable profile link is the username; the id link still resolves.
  const cardProfileUrl = `${window.location.origin}/team/${staff.profile.handle || staff.profile.id}`;
  const cardMarkdown = `[![Niko staff card](${cardBaseUrl})](${cardProfileUrl})`;
  const copyCardMarkdown = async () => {
    try {
      await navigator.clipboard.writeText(cardMarkdown);
      notifySuccess(t("card.copied"), "staff-card");
    } catch {
      notifyError(t("card.clipboardBlocked"), "staff-card");
    }
  };
  const canManageGlobal = tabAllowedForRole(staff.role, "global");
  const canManageGuilds = tabAllowedForRole(staff.role, "guilds");
  const canReviewAppeals = tabAllowedForRole(staff.role, "appeals");
  const canManageProxyWorkers = tabAllowedForRole(staff.role, "proxy-workers");
  const canManageLavalink = tabAllowedForRole(staff.role, "lavalink");
  const canManageMaintenance = tabAllowedForRole(staff.role, "maintenance");
  const canManageLocales = tabAllowedForRole(staff.role, "locales");
  const canManageUpdates = tabAllowedForRole(staff.role, "updates");
  const canManageNikoApplications = tabAllowedForRole(staff.role, "team-recruitment");
  const canManageStaffRoster = tabAllowedForRole(staff.role, "staff-management");
  const canManageBilling = tabAllowedForRole(staff.role, "billing");
  const canManageDataRemoval = tabAllowedForRole(staff.role, "data-removal");
  const query = guildSearch.trim().toLocaleLowerCase();
  const filteredGuilds = staffGuilds.filter((guild) =>
    !query || `${guild.name} ${guild.id} ${guild.owner_name}`.toLocaleLowerCase().includes(query)
  );
  const rosterQuery = staffRosterSearch.trim().toLocaleLowerCase();
  const filteredStaffRoster = staffRoster.filter((member) =>
    !rosterQuery || `${member.name} ${member.username || ""} ${member.id} ${member.role_label} ${member.staff_status_label || ""}`.toLocaleLowerCase().includes(rosterQuery)
  );
  const update = (key: string, value: string | boolean) => setForm((current) => ({ ...current, [key]: value }));
  const addLink = () => setLinks((current) => current.length < 10 ? [...current, { type: "", url: "" }] : current);
  const updateLink = (index: number, key: "type" | "url", value: string) => {
    setLinks((current) => current.map((link, linkIndex) => linkIndex === index ? { ...link, [key]: value } : link));
  };
  const removeLink = (index: number) => setLinks((current) => current.filter((_, linkIndex) => linkIndex !== index));
  const save = async () => {
    if (saving) return;
    const linksToSave = links.filter((link) => link.type.trim() || link.url.trim());
    if (linksToSave.some((link) => !link.type.trim() || !link.url.trim())) {
      notifyError(t("profile.linkIncomplete"), "staff-profile");
      return;
    }
    setSaving(true); notifyLoading(t("profile.saving"), "staff-profile");
    const payload = {
      public_bio: form.public_bio,
      public_banner_url: form.public_banner_url,
      public_visible: form.public_visible,
      public_links: linksToSave,
    };
    try { await saveStaffProfile(payload, auth.csrf_token); notifySuccess(t("profile.saved"), "staff-profile"); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : t("profile.saveFailed"), "staff-profile"); }
    finally { setSaving(false); }
  };
  const saveCard = async () => {
    if (savingCard) return;
    setSavingCard(true); notifyLoading(t("card.saving"), "staff-card-settings");
    // The API stores the accent as bare hex digits and treats an empty value as
    // "back to the default"; normalise here so the card matches the picker.
    try {
      await saveStaffProfile({
        card_theme: form.card_theme,
        card_accent: form.card_accent.replace(/^#/, "").toUpperCase(),
        card_show_status: form.card_show_status,
      }, auth.csrf_token);
      notifySuccess(t("card.saved"), "staff-card-settings");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("card.saveFailed"), "staff-card-settings");
    } finally { setSavingCard(false); }
  };
  // Both blacklist entry points run the same flow for guilds, so a server is
  // never blacklisted with its features still answering. The name is only used
  // in the toasts, so the directory is the fallback-free source and a guild the
  // bot is not in yields an ID label (the API rejects those entries anyway).
  const addBlacklistEntry = async () => {
    if (blacklistType === "guild") {
      const guildName = staffGuilds.find((item) => item.id === blacklistId)?.name || `Guild ${blacklistId}`;
      if (await blacklistGuild(blacklistId, guildName, blacklistReason)) {
        setBlacklistId("");
        setBlacklistReason("");
      }
      return;
    }
    await saveGuildAction(async () => {
      await updateStaffBlacklist("user", "add", blacklistId, blacklistReason, auth.csrf_token);
      setBlacklistEntries(await getStaffBlacklist());
      setBlacklistId("");
    }, t("blacklist.userAdded"));
  };
  async function loadErrorReports() {
    setReportsLoading(true);
    try { setErrorReports((await getStaffErrorReports()).reports); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : t("reports.unavailable"), "staff-reports"); }
    finally { setReportsLoading(false); }
  };
  const refreshErrorReports = () => void loadErrorReports();
  async function loadAppeals() {
    setAppealsLoading(true);
    try { setAppeals((await getStaffBlacklistAppeals()).appeals); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : t("appeals.unavailable"), "staff-appeals"); }
    finally { setAppealsLoading(false); }
  }
  const reviewAppeal = async (appeal: BlacklistAppeal, status: "approved" | "denied") => {
    if (reviewingAppealId) return;
    setReviewingAppealId(appeal.appeal_id);
    notifyLoading(t("appeals.saving"), "staff-appeals");
    try {
      await reviewStaffBlacklistAppeal(appeal.appeal_id, status, appealNotes[appeal.appeal_id] || "", auth.csrf_token);
      // The queue below reloads with the new decision, so the spinner is
      // retired here; a reload failure still reports itself as an error toast.
      clearToasts("staff-appeals");
      await loadAppeals();
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : t("appeals.saveFailed"), "staff-appeals"); }
    finally { setReviewingAppealId(null); }
  };
  const refreshStaffGuilds = async () => {
    setStaffGuildsLoading(true);
    try { setStaffGuilds((await getStaffGuilds()).guilds); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : t("guilds.listUnavailable"), "staff-guilds"); }
    finally { setStaffGuildsLoading(false); }
  };
  const saveGuildAction = async (action: () => Promise<unknown>, success: string) => {
    if (busyGuildAction) return;
    setBusyGuildAction(true); notifyLoading(t("guildAction.applying"), "staff-guild-action");
    try { await action(); notifySuccess(success, "staff-guild-action"); await refreshStaffGuilds(); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : t("guildAction.failed"), "staff-guild-action"); }
    finally { setBusyGuildAction(false); }
  };
  // Blacklisting is a sequence of reported steps, so it runs through its own
  // flow instead of the one-shot `saveGuildAction`: each feature announces its
  // progress as a toast, and the summary lists whatever could not be paused.
  const blacklistGuild = async (guildId: string, guildName: string, reason: string): Promise<GuildLockdownSummary | null> => {
    if (busyGuildAction) return null;
    setBusyGuildAction(true);
    try {
      const summary = await blacklistGuildWithLockdown({ guildId, guildName, reason, csrfToken: auth.csrf_token });
      if (summary) setLockdownSummary(summary);
      setBlacklistEntries(await getStaffBlacklist());
      await refreshStaffGuilds();
      return summary;
    } catch (actionError) {
      notifyError(actionError instanceof Error ? actionError.message : t("guildAction.blacklistFailed"), `staff-guild-lockdown-${guildId}`);
      return null;
    } finally {
      setBusyGuildAction(false);
    }
  };
  async function refreshBilling() {
    try { setBilling(await getStaffBilling()); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : t("billing.unavailable"), "staff-billing"); }
  }
  async function refreshDataRemoval() {
    try { setDataRemoval((await getStaffDataRemovalRequests()).requests); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : t("dataRemoval.unavailable"), "staff-data-removal"); }
  }
  async function refreshStaffRoster() {
    setStaffRosterLoading(true);
    try {
      const result = await getStaffMembers();
      setStaffRoster(result.members);
      setStaffRosterRoles(result.roles);
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("roster.loadFailed"), "staff-roster");
    } finally {
      setStaffRosterLoading(false);
    }
  }
  const rosterAction = async (
    member: StaffMember,
    action: "assign" | "demote" | "suspend" | "lift",
    role?: string,
    reason?: string,
  ) => {
    if (staffRosterBusy) return;
    setStaffRosterBusy(true);
    notifyLoading(t("roster.updating"), "staff-roster");
    try {
      const result = await manageStaffMember(member.id, { action, role, reason }, auth.csrf_token);
      const roleLabel = staffRosterRoles.find((item) => item.key === role)?.label || role || "staff";
      if (action === "assign" && result.status === "suspended") {
        notifySuccess(t("roster.assignSuspended", { name: member.name, role: roleLabel }), "staff-roster");
      } else if (action === "assign") {
        notifySuccess(t("roster.assignDone", { name: member.name, role: roleLabel }), "staff-roster");
      } else if (action === "suspend") {
        notifySuccess(t("roster.suspended", { name: member.name }), "staff-roster");
      } else if (action === "lift") {
        notifySuccess(t("roster.lifted", { name: member.name }), "staff-roster");
      } else {
        notifySuccess(t("roster.demoted", { name: member.name }), "staff-roster");
      }
      await refreshStaffRoster();
    } catch (actionError) {
      notifyError(actionError instanceof Error ? actionError.message : t("roster.updateFailed"), "staff-roster");
    } finally {
      setStaffRosterBusy(false);
    }
  };
  const saveStaffRole = async (member: StaffMember) => {
    const role = staffRosterRoleDrafts[member.id] || member.role;
    if (!role) { notifyError(t("roster.chooseRole"), "staff-roster"); return; }
    const label = staffRosterRoles.find((item) => item.key === role)?.label || role;
    if (!window.confirm(t("roster.confirmAssign", { name: member.name, role: label }))) return;
    await rosterAction(member, "assign", role);
  };
  const suspendStaffMember = async (member: StaffMember) => {
    const reason = window.prompt(t("roster.suspendPrompt", { name: member.name }), "");
    if (reason === null) return;
    if (reason.trim().length < 5) { notifyError(t("roster.reasonTooShort"), "staff-roster"); return; }
    if (!window.confirm(t("roster.confirmSuspend", { name: member.name }))) return;
    await rosterAction(member, "suspend", undefined, reason.trim());
  };
  const demoteStaffMember = async (member: StaffMember) => {
    if (!window.confirm(t("roster.confirmDemote", { name: member.name }))) return;
    const reason = window.prompt(t("roster.demoteReason"), "") || "";
    await rosterAction(member, "demote", undefined, reason.trim());
  };
  const liftStaffSuspension = async (member: StaffMember) => {
    if (!window.confirm(t("roster.confirmLift", { name: member.name }))) return;
    await rosterAction(member, "lift");
  };
  const addStaffRole = async () => {
    if (!/^\d{5,22}$/.test(newStaffId.trim()) || !newStaffRole) {
      notifyError(t("roster.enterId"), "staff-roster");
      return;
    }
    const roleLabel = staffRosterRoles.find((item) => item.key === newStaffRole)?.label || newStaffRole;
    if (!window.confirm(t("roster.confirmAdd", { id: newStaffId.trim(), role: roleLabel }))) return;
    await rosterAction(
      { id: newStaffId.trim(), name: t("roster.userName", { id: newStaffId.trim() }), role: newStaffRole, role_label: roleLabel },
      "assign",
      newStaffRole,
    );
    setNewStaffId("");
    setNewStaffRole("");
  };
  const reviewDataRemoval = async (request: StaffDataRemovalRequest, status: "approved" | "denied") => {
    if (dataRemovalBusy) return;
    const action = t(status === "approved" ? "dataRemoval.actionApprove" : "dataRemoval.actionDeny");
    if (!window.confirm(t("dataRemoval.confirm", { action }))) return;
    setDataRemovalBusy(true);
    notifyLoading(status === "approved" ? t("dataRemoval.running") : t("dataRemoval.savingDecision"), "staff-data-removal");
    try {
      await reviewStaffDataRemoval(request.id, status, dataRemovalNotes[request.id] || "", auth.csrf_token);
      notifySuccess(status === "approved" ? t("dataRemoval.completed") : t("dataRemoval.denied"), "staff-data-removal");
      await refreshDataRemoval();
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : t("dataRemoval.reviewFailed"), "staff-data-removal"); }
    finally { setDataRemovalBusy(false); }
  };
  // The note being edited for a payment, falling back to what is on record so
  // flagging or resolving never wipes a saved note.
  const billingNoteFor = (payment: StaffBillingPayment) =>
    billingNotes[payment.order_id] ?? payment.issue_note ?? "";
  const forgetBillingDraft = (orderId: string) => setBillingNotes((current) => {
    const next = { ...current };
    delete next[orderId];
    return next;
  });
  const saveBillingNote = async (payment: StaffBillingPayment) => {
    if (billingBusy) return;
    setBillingBusy(true);
    try {
      await resolveStaffBillingPayment(payment.order_id, null, billingNoteFor(payment), auth.csrf_token);
      notifySuccess(t("billing.noteSaved"), "staff-billing");
      await refreshBilling();
      forgetBillingDraft(payment.order_id);
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : t("billing.noteFailed"), "staff-billing"); }
    finally { setBillingBusy(false); }
  };
  const resolveBilling = async (orderId: string, status: "open" | "resolved" | "clear") => {
    if (billingBusy) return;
    setBillingBusy(true);
    try {
      const payment = billing?.payments.find((item) => item.order_id === orderId);
      const note = payment ? billingNoteFor(payment) : billingNotes[orderId] || "";
      await resolveStaffBillingPayment(orderId, status, note, auth.csrf_token);
      notifySuccess(
        status === "resolved" ? t("billing.markedResolved") : status === "open" ? t("billing.flagged") : t("billing.undone"),
        "staff-billing",
      );
      await refreshBilling();
      forgetBillingDraft(orderId);
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : t("billing.noteFailed"), "staff-billing"); }
    finally { setBillingBusy(false); }
  };
  const changeBillingSubscription = async (guildId: string, action: "grant" | "cancel") => {
    if (billingBusy || !guildId.trim()) return;
    setBillingBusy(true);
    try {
      await updateStaffSubscription(guildId.trim(), action, action === "grant" ? Number(billingMonths) || 1 : 1, auth.csrf_token);
      notifySuccess(action === "grant" ? t("billing.granted", { months: billingMonths, id: guildId }) : t("billing.cancelled", { id: guildId }), "staff-billing");
      setBillingGuild("");
      await refreshBilling();
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : t("billing.changeFailed"), "staff-billing"); }
    finally { setBillingBusy(false); }
  };
  async function refreshNikoApplications() {
    setNikoBusy(true);
    try {
      const result = await getTeamRecruitmentSettings();
      const groupedSubmissions = await Promise.all(result.openings.map(async (opening) => {
        const response = await getTeamRecruitmentSubmissions(opening.id);
        return response.submissions.map((submission) => ({
          ...submission,
          opening_id: opening.id,
          opening_title: opening.title,
          role_name: opening.role_name,
        }));
      }));
      setNikoApplications(result.openings);
      setNikoSubmissions(groupedSubmissions.flat().sort((left, right) => {
        if (left.review_status === "pending" && right.review_status !== "pending") return -1;
        if (right.review_status === "pending" && left.review_status !== "pending") return 1;
        return (right.submitted_at || "").localeCompare(left.submitted_at || "");
      }));
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : t("applications.unavailable"), "staff-niko-applications"); }
    finally { setNikoBusy(false); }
  }
  const toggleNikoOpening = async (application: TeamRecruitmentOpening) => {
    setNikoBusy(true); notifyLoading(t("applications.changing"), "staff-niko-applications");
    try { await setTeamRecruitmentOpeningStatus(application.id, application.status === "open" ? "closed" : "open", auth.csrf_token); clearToasts("staff-niko-applications"); await refreshNikoApplications(); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : t("applications.statusFailed"), "staff-niko-applications"); }
    finally { setNikoBusy(false); }
  };
  const reviewNikoSubmission = async (submission: ReviewedTeamSubmission, status: "approved" | "denied") => {
    if (nikoBusy) return;
    const revoking = status === "denied" && submission.review_status === "approved";
    if (revoking && !window.confirm(t("applications.revokeConfirm", { name: submission.display_name, role: submission.role_name || t("applications.teamRole") }))) return;
    setNikoBusy(true); notifyLoading(t("applications.savingDecision"), "staff-niko-applications");
    try {
      const result = await reviewTeamRecruitmentSubmission(submission.opening_id, submission.user_id, status, auth.csrf_token);
      if (result.unchanged) {
        notifySuccess(t("applications.alreadyRecorded", { name: submission.display_name }), "staff-niko-applications");
      } else if (status === "approved") {
        notifySuccess(t(result.dm_sent === false ? "applications.approvedNoDm" : "applications.approved", { name: submission.display_name }), "staff-niko-applications");
      } else {
        notifySuccess(t(result.role_revoked ? "applications.declinedRoleRemoved" : "applications.declined", { name: submission.display_name }), "staff-niko-applications");
      }
      await refreshNikoApplications();
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : t("applications.saveFailed"), "staff-niko-applications"); }
    finally { setNikoBusy(false); }
  };
  const onTabKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (!["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) return;
    const tabs = Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>('[role="tab"]'));
    if (!tabs.length) return;
    const current = tabs.findIndex((tab) => tab === document.activeElement);
    const next = event.key === "Home" ? 0
      : event.key === "End" ? tabs.length - 1
      : ((current === -1 ? 0 : current) + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
    event.preventDefault();
    const target = tabs[next];
    const tab = tabFromTabButton(target);
    target.focus();
    if (tab) setActiveTab(tab);
  };
  const saveGlobal = async () => {
    if (savingGlobal) return;
    setSavingGlobal(true); notifyLoading(t("global.saving"), "staff-global");
    try { await saveGlobalProfile(global, auth.csrf_token); notifySuccess(t("global.saved"), "staff-global"); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : t("global.saveFailed"), "staff-global"); }
    finally { setSavingGlobal(false); }
  };

  const content = <div className="staff-page">
    <header className="staff-heading">
      <div><div className="eyebrow">{t("page.eyebrow")}</div><h1>{t("page.title")}</h1><p>{t("page.body")}</p></div>
      <div className="staff-role-card"><span className="staff-role-mark"><img src={signedInAvatar} alt={t("page.avatarAlt")} onError={(event) => { event.currentTarget.onerror = null; event.currentTarget.src = discordDefaultAvatar; }} /></span><span><small>{t("page.signedInAs")}</small><strong>{staff.role_label}</strong></span></div>
    </header>

    <div className="staff-tabs" role="tablist" aria-label={t("tabs.aria")} onKeyDown={onTabKeyDown}>
      <button type="button" role="tab" id="staff-profile-tab" aria-selected={activeTab === "profile"} aria-controls="staff-profile-panel" className={activeTab === "profile" ? "active" : ""} onClick={() => setActiveTab("profile")}><Icon name="users" /> {t("tabs.profile")}</button>
      <button type="button" role="tab" id="staff-analytics-tab" aria-selected={activeTab === "analytics"} aria-controls="staff-analytics-panel" className={activeTab === "analytics" ? "active" : ""} onClick={() => setActiveTab("analytics")}><Icon name="chart" /> {t("tabs.analytics")}</button>
      {canManageGlobal && <button type="button" role="tab" id="staff-global-tab" aria-selected={activeTab === "global"} aria-controls="staff-global-panel" className={activeTab === "global" ? "active" : ""} onClick={() => setActiveTab("global")}><Icon name="settings" /> {t("tabs.global")}</button>}
      {canManageGuilds && <button type="button" role="tab" id="staff-guilds-tab" aria-selected={activeTab === "guilds"} aria-controls="staff-guilds-panel" className={activeTab === "guilds" ? "active" : ""} onClick={() => setActiveTab("guilds")}><Icon name="shield" /> {t("tabs.guilds")} <span>{staffGuilds.length}</span></button>}
      {canManageGuilds && <button type="button" role="tab" id="staff-blacklist-tab" aria-selected={activeTab === "blacklist"} aria-controls="staff-blacklist-panel" className={activeTab === "blacklist" ? "active" : ""} onClick={() => setActiveTab("blacklist")}><Icon name="lock" /> {t("tabs.blacklist")} <span>{blacklistEntries.users.length + blacklistEntries.guilds.length}</span></button>}
      {canReviewAppeals && <button type="button" role="tab" id="staff-appeals-tab" aria-selected={activeTab === "appeals"} aria-controls="staff-appeals-panel" className={activeTab === "appeals" ? "active" : ""} onClick={() => setActiveTab("appeals")}><Icon name="message" /> {t("tabs.appeals")} <span>{appeals.filter((appeal) => appeal.status === "pending").length}</span></button>}
      {canManageProxyWorkers && <button type="button" role="tab" id="staff-proxy-workers-tab" aria-selected={activeTab === "proxy-workers"} aria-controls="staff-proxy-workers-panel" className={activeTab === "proxy-workers" ? "active" : ""} onClick={() => setActiveTab("proxy-workers")}><Icon name="chart" /> {t("tabs.proxy")}</button>}
      {canManageLavalink && <button type="button" role="tab" id="staff-lavalink-tab" aria-selected={activeTab === "lavalink"} aria-controls="staff-lavalink-panel" className={activeTab === "lavalink" ? "active" : ""} onClick={() => setActiveTab("lavalink")}><Icon name="guild_server" /> {t("tabs.lavalink")}</button>}
      {canManageNikoApplications && <button type="button" role="tab" id="staff-team-recruitment-tab" aria-selected={activeTab === "team-recruitment"} aria-controls="staff-team-recruitment-panel" className={activeTab === "team-recruitment" ? "active" : ""} onClick={() => setActiveTab("team-recruitment")}><Icon name="users" /> {t("tabs.applications")} <span>{nikoApplications.reduce((count, application) => count + application.submission_count, 0)}</span></button>}
      {canManageMaintenance && <button type="button" role="tab" id="staff-maintenance-tab" aria-selected={activeTab === "maintenance"} aria-controls="staff-maintenance-panel" className={activeTab === "maintenance" ? "active" : ""} onClick={() => setActiveTab("maintenance")}><Icon name="settings" /> {t("tabs.maintenance")}</button>}
      {canManageLocales && <button type="button" role="tab" id="staff-locales-tab" aria-selected={activeTab === "locales"} aria-controls="staff-locales-panel" className={activeTab === "locales" ? "active" : ""} onClick={() => setActiveTab("locales")}><Icon name="doc" /> {t("tabs.locales")}</button>}
      {canManageUpdates && <button type="button" role="tab" id="staff-updates-tab" aria-selected={activeTab === "updates"} aria-controls="staff-updates-panel" className={activeTab === "updates" ? "active" : ""} onClick={() => setActiveTab("updates")}><Icon name="spark" /> {t("tabs.updates")}</button>}
      {canManageStaffRoster && <button type="button" role="tab" id="staff-staff-management-tab" aria-selected={activeTab === "staff-management"} aria-controls="staff-staff-management-panel" className={activeTab === "staff-management" ? "active" : ""} onClick={() => setActiveTab("staff-management")}><Icon name="users" /> {t("tabs.roster")} <span>{staffRoster.filter((member) => member.staff_status !== "former").length}</span></button>}
      {canManageStaffRoster && <button type="button" role="tab" id="staff-broadcasts-tab" aria-selected={activeTab === "broadcasts"} aria-controls="staff-broadcasts-panel" className={activeTab === "broadcasts" ? "active" : ""} onClick={() => setActiveTab("broadcasts")}><Icon name="message" /> {t("tabs.broadcasts")}</button>}
      {canManageDataRemoval && <button type="button" role="tab" id="staff-data-removal-tab" aria-selected={activeTab === "data-removal"} aria-controls="staff-data-removal-panel" className={activeTab === "data-removal" ? "active" : ""} onClick={() => setActiveTab("data-removal")}><Icon name="lock" /> {t("tabs.dataRemoval")} <span>{dataRemoval?.filter((request) => request.status === "pending").length ?? 0}</span></button>}
      {canManageBilling && <button type="button" role="tab" id="staff-billing-tab" aria-selected={activeTab === "billing"} aria-controls="staff-billing-panel" className={activeTab === "billing" ? "active" : ""} onClick={() => setActiveTab("billing")}><Icon name="guild_economy" /> {t("tabs.billing")} <span>{billing?.payments.filter((payment) => payment.issue_status === "open").length ?? 0}</span></button>}
      <button type="button" role="tab" id="staff-reports-tab" aria-selected={activeTab === "reports"} aria-controls="staff-reports-panel" className={activeTab === "reports" ? "active" : ""} onClick={() => setActiveTab("reports")}><Icon name="alert" /> {t("tabs.reports")} <span>{errorReports.length}</span></button>
    </div>

    {activeTab === "profile" && <section id="staff-profile-panel" role="tabpanel" aria-labelledby="staff-profile-tab"><div className="staff-layout">
      <section className="staff-panel staff-panel-main">
        <div className="staff-panel-heading"><div><span className="panel-kicker">{t("profile.kicker")}</span><h2>{t("profile.title")}</h2><p>{t("profile.body")}</p></div><span className="staff-step">01</span></div>
        <div className="staff-fields">
          <label className="form-field"><span className="form-label">{t("profile.bannerLabel")}</span><input type="url" value={form.public_banner_url} onChange={(e) => update("public_banner_url", e.target.value)} placeholder="https://…" /><small>{t("profile.bannerHint")}</small></label>
          <section className="staff-links-section" aria-labelledby="staff-links-heading">
            <div className="staff-links-heading"><div><span className="form-label" id="staff-links-heading">{t("profile.linksLabel")}</span><small>{t("profile.linksHint")}</small></div><span className="staff-links-count">{links.length}/10</span></div>
            <div className="staff-link-list">
              {links.map((link, index) => <div className="staff-link-row" key={`profile-link-${index}`}>
                <div className="form-field staff-link-type"><span className="sr-only">{t("profile.linkType", { count: index + 1 })}</span><Select ariaLabel={t("profile.linkType", { count: index + 1 })} placeholder={t("profile.linkTypePlaceholder")} options={PUBLIC_LINK_TYPES.map(([value, label]) => ({ value, label }))} value={link.type} onChange={(value) => updateLink(index, "type", value)} /></div>
                <label className="form-field staff-link-url"><span className="sr-only">{t("profile.linkUrl", { count: index + 1 })}</span><input type="url" value={link.url} onChange={(event) => updateLink(index, "url", event.target.value)} placeholder="https://…" /></label>
                <button type="button" className="staff-link-remove" onClick={() => removeLink(index)} aria-label={t("profile.removeLink", { count: index + 1 })}>{t("profile.remove")}</button>
              </div>)}
            </div>
            <button type="button" className="button button-muted staff-add-link" onClick={addLink} disabled={links.length >= 10}>＋ {t("profile.addLink")}</button>
          </section>
          <label className="form-field staff-bio-field"><span className="form-label">{t("profile.bioLabel")}</span><textarea value={form.public_bio} onChange={(e) => update("public_bio", e.target.value)} maxLength={1200} placeholder={t("profile.bioPlaceholder")} /><small>{t("profile.bioCount", { count: form.public_bio.length })}</small></label>
        </div>
        <SettingCards className="staff-visibility">
          <SettingCard
            title={t("profile.visibleTitle")}
            hint={t("profile.visibleHint")}
            action={<Switch checked={form.public_visible} onCheckedChange={(value) => update("public_visible", value)} aria-label={t("profile.visibleTitle")} />}
          />
        </SettingCards>
        <div className="staff-panel-footer"><span>{t("profile.footer")}</span><button type="button" className="button button-primary" onClick={save} disabled={saving}>{saving ? t("profile.savingButton") : t("profile.saveButton")}</button></div>
      </section>

      <aside className="staff-sidebar-card staff-profile-sidebar">
        <section className="staff-profile-preview" aria-label={t("preview.aria")}>
          <div className="staff-profile-preview-banner">
            {form.public_banner_url && <img src={form.public_banner_url} alt="" onError={(event) => { event.currentTarget.style.visibility = "hidden"; }} />}
            <span>{t("preview.banner")}</span>
          </div>
          <div className="staff-profile-preview-body">
            <DiscordStatusAvatar status={staff.profile.status} className="staff-profile-preview-avatar" label={staff.profile.status_label || staff.profile.status || t("preview.offline")}><img className="staff-profile-preview-avatar" src={signedInAvatar} alt="" /></DiscordStatusAvatar>
            <div className="staff-profile-preview-identity"><strong>{signedInUser.global_name || signedInUser.username || staff.profile.name}</strong><span>{staff.role_label}</span></div>
            <p className={form.public_bio.trim() ? "" : "is-placeholder"}>{form.public_bio.trim() || t("preview.bioPlaceholder")}</p>
            {links.some((link) => link.type.trim() && link.url.trim()) && <div className="staff-profile-preview-links">{links.filter((link) => link.type.trim() && link.url.trim()).map((link, index) => <span key={`${link.type}-${index}`}>{link.label || PUBLIC_LINK_TYPES.find(([value]) => value === link.type)?.[1] || link.type}</span>)}</div>}
            <div className={`staff-profile-preview-visibility${form.public_visible ? " is-visible" : ""}`}><i />{form.public_visible ? t("preview.visible") : t("preview.hidden")}</div>
          </div>
        </section>
        <div className="staff-profile-rules"><span className="panel-kicker">{t("rules.kicker")}</span><h3>{t("rules.title")}</h3><p>{t("rules.body")}</p><div className="staff-rule"><span>{t("rules.identity")}</span><strong>{t("rules.synced")}</strong></div><div className="staff-rule"><span>{t("rules.editable")}</span><strong>{t("rules.editableFields")}</strong></div></div>
      </aside>
    </div>
    <details className="staff-card-section">
      <summary>
        <span className="staff-card-section-copy">
          <span className="panel-kicker">{t("card.kicker")}</span>
          <strong>{t("card.title")}</strong>
          <small>{t("card.body")}</small>
        </span>
        <span className="staff-card-section-hint">{t("card.settings")}</span>
      </summary>
      <div className="staff-card-body">
        <div className="staff-card-preview-block">
          <img className="staff-card-preview" src={cardPreviewUrl} alt={t("card.previewAlt", { name: staff.profile.name })} />
          <span className="staff-card-preview-caption">{t("card.previewCaption")}</span>
        </div>
        <div className="staff-card-controls">
          <div className="staff-card-fields">
            <div className="form-field"><span className="form-label">{t("card.theme")}</span><Select ariaLabel={t("card.theme")} placeholder={null} options={CARD_THEMES} value={form.card_theme} onChange={(value) => update("card_theme", value)} /></div>
            <div className="form-field"><span className="form-label">{t("card.accent")}</span><ColorPicker label={t("card.accentAria")} value={form.card_accent} onChange={(hex) => update("card_accent", hex)} /></div>
          </div>
          <SettingCards>
            <SettingCard
              title={t("card.statusTitle")}
              hint={t("card.statusHint")}
              action={<Switch checked={form.card_show_status} onCheckedChange={(value) => update("card_show_status", value)} aria-label={t("card.statusAria")} />}
            />
          </SettingCards>
          <div className="staff-card-markdown">
            <span className="form-label">{t("card.markdownLabel")}</span>
            <div className="staff-card-snippet">
              <input readOnly value={cardMarkdown} aria-label={t("card.markdownAria")} onFocus={(event) => event.currentTarget.select()} />
              <button type="button" className="button button-muted" onClick={() => void copyCardMarkdown()}>{t("card.copyMarkdown")}</button>
            </div>
            <small className="form-hint">{t("card.markdownHint")}</small>
          </div>
          <div className="staff-panel-footer staff-card-footer">
            <span>{t("card.footer")}</span>
            <button type="button" className="button button-primary" onClick={saveCard} disabled={savingCard}>{savingCard ? t("profile.savingButton") : t("card.saveButton")}</button>
          </div>
        </div>
      </div>
    </details>
    </section>}

    {activeTab === "analytics" && <section id="staff-analytics-panel" role="tabpanel" aria-labelledby="staff-analytics-tab" className="staff-guild-operations"><BotAnalyticsView /></section>}
    {activeTab === "global" && canManageGlobal && <section id="staff-global-panel" role="tabpanel" aria-labelledby="staff-global-tab" className="staff-panel staff-global-panel"><div className="staff-panel-heading"><div><span className="panel-kicker">{t("global.kicker")}</span><h2>{t("global.title")}</h2><p>{t("global.body")}</p></div><span className="staff-step">02</span></div><div className="staff-fields staff-fields-two"><label className="form-field"><span className="form-label">{t("global.avatarLabel")}</span><input value={global.avatar_url} onChange={(e) => setGlobal({ ...global, avatar_url: e.target.value })} placeholder="https://…" /></label><label className="form-field"><span className="form-label">{t("global.bannerLabel")}</span><input value={global.banner_url} onChange={(e) => setGlobal({ ...global, banner_url: e.target.value })} placeholder="https://…" /></label></div><div className="staff-panel-footer"><span>{t("global.footer")}</span><button type="button" className="button button-primary" onClick={saveGlobal} disabled={savingGlobal}>{savingGlobal ? t("global.updating") : t("global.update")}</button></div></section>}
    {activeTab === "guilds" && canManageGuilds && <section id="staff-guilds-panel" role="tabpanel" aria-labelledby="staff-guilds-tab" className="staff-guild-operations">
      <header className="staff-guilds-heading"><div><span className="panel-kicker">{t("guilds.kicker")}</span><h2>{t("guilds.title")}</h2><p>{t("guilds.body")}</p></div><div className="staff-guild-count"><strong>{staffGuilds.length}</strong><span>{t("guilds.connected")}</span></div></header>
      <div className="staff-guild-toolbar"><label className="staff-guild-search"><Icon name="search" /><input type="search" value={guildSearch} onChange={(event) => setGuildSearch(event.target.value)} placeholder={t("guilds.search")} aria-label={t("guilds.searchAria")} /></label><button type="button" className="button button-muted" onClick={refreshStaffGuilds} disabled={staffGuildsLoading}><Icon name="spark" />{staffGuildsLoading ? t("common.refreshing") : t("guilds.refresh")}</button></div>
      {staffGuildsLoading && staffGuilds.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>{t("guilds.loading")}</p></div> : filteredGuilds.length === 0 ? <div className="staff-guild-empty"><span>{staffGuilds.length ? t("guilds.noMatch") : t("guilds.none")}</span></div> : <div className="staff-guild-list">
        {filteredGuilds.map((guild) => {
          const expanded = expandedGuildId === guild.id;
          return <article className={`staff-guild-card${expanded ? " expanded" : ""}`} key={guild.id}>
            <button type="button" className="staff-guild-row" aria-expanded={expanded} onClick={() => setExpandedGuildId(expanded ? null : guild.id)}>
              <span className="staff-guild-icon">{guild.icon_url ? <img src={guild.icon_url} alt="" /> : <b>{guild.name.slice(0, 1).toUpperCase()}</b>}</span>
              <span className="staff-guild-title"><strong>{guild.name}</strong><small>{t("guild.members", { id: guild.id, count: guild.member_count.toLocaleString() })}</small></span>
              <span className={`staff-guild-status${guild.blacklisted ? " is-blocked" : ""}`}><i />{guild.blacklisted ? t("guild.blacklisted") : t("guild.active")}</span>
              <Icon name={expanded ? "close" : "arrow"} className="staff-guild-chevron" />
            </button>
            {expanded && <div className="staff-guild-details">
              <div className="staff-guild-summary"><div><span className="panel-kicker">{t("guild.owner")}</span><DiscordMarkdown text={`<@${guild.owner_id || "0"}>`} mentionNames={{ user: guild.owner_id ? { [guild.owner_id]: guild.owner_name } : {} }} className="staff-guild-owner" /></div><div><span className="panel-kicker">{t("guild.created")}</span><strong>{guild.created_at ? new Date(guild.created_at).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" }) : t("guild.unknown")}</strong></div><div><span className="panel-kicker">{t("guild.channels")}</span><strong>{t("guild.channelCount", { channels: guild.channel_count.toLocaleString(), categories: guild.category_count })}</strong></div><div><span className="panel-kicker">{t("guild.profileName")}</span><strong>{guild.profile_name || t("guild.niko")}</strong></div><div><span className="panel-kicker">{t("guild.roles")}</span><strong>{guild.role_count}</strong></div></div>
              <div className="staff-guild-profile-previews"><div className="staff-guild-preview"><span className="panel-kicker">{t("guild.avatar")}</span>{guild.bot_avatar_url ? <img src={guild.bot_avatar_url} alt={t("guild.avatarAlt", { name: guild.name })} /> : <div className="staff-guild-no-image">{t("guild.noAvatar")}</div>}</div><div className="staff-guild-preview staff-guild-preview-banner"><span className="panel-kicker">{t("guild.banner")}</span>{guild.bot_banner_url ? <img src={guild.bot_banner_url} alt={t("guild.bannerAlt", { name: guild.name })} /> : <div className="staff-guild-no-image">{t("guild.noBanner")}</div>}</div></div>
              <div className="staff-guild-action-panel"><div className="staff-guild-action-heading"><div><span className="panel-kicker">{t("guild.quickActions")}</span><h3>{t("guild.operationsFor", { name: guild.name })}</h3></div><span className="staff-guild-id">{t("guild.idLabel", { id: guild.id })}</span></div>
                <div className="staff-guild-actions"><button type="button" className="button button-muted" disabled={busyGuildAction} onClick={() => { setInviteUrl(""); setInviteGuildId(guild.id); notifyLoading(t("guild.creatingInvite"), "staff-guild-invite"); void createStaffGuildInvite(guild.id, auth.csrf_token).then((result) => { setInviteUrl(result.url); clearToasts("staff-guild-invite"); }).catch((reason) => notifyError(reason instanceof Error ? reason.message : t("guild.inviteFailed"), "staff-guild-invite")); }}><Icon name="link" />{t("guild.temporaryInvite")}</button><button type="button" className="button button-muted" onClick={() => setPermissionGuild(guild)}><Icon name="shield" />{t("guild.permissions")}</button><button type="button" className="button button-danger" disabled={busyGuildAction} onClick={() => { if (window.confirm(t("guild.leaveConfirm", { name: guild.name }))) void saveGuildAction(() => leaveStaffGuild(guild.id, auth.csrf_token), t("guild.left", { name: guild.name })); }}>{t("guild.leave")}</button><label className="form-field staff-guild-reason"><span className="form-label">{t("guild.reasonLabel")}</span><input value={guildBlacklistReason} onChange={(event) => setGuildBlacklistReason(event.target.value)} maxLength={1000} placeholder={t("guild.reasonPlaceholder")} /></label><button type="button" className={`button ${guild.blacklisted ? "button-muted" : "button-danger"}`} disabled={busyGuildAction || (!guild.blacklisted && !guildBlacklistReason.trim())} onClick={() => guild.blacklisted ? void saveGuildAction(() => setStaffGuildBlacklist(guild.id, "remove", guildBlacklistReason, auth.csrf_token), t("guild.unblacklisted", { name: guild.name })) : void blacklistGuild(guild.id, guild.name, guildBlacklistReason)}>{busyGuildAction ? t("common.working") : guild.blacklisted ? t("guild.removeBlacklist") : t("guild.blacklistGuild")}</button><button type="button" className="button button-muted" disabled={busyGuildAction} onClick={() => { if (window.confirm(t("guild.resetConfirm", { name: guild.name }))) void saveGuildAction(() => resetStaffGuildProfile(guild.id, auth.csrf_token), t("guild.resetDone", { name: guild.name })); }}><Icon name="settings" />{t("guild.reset")}</button></div>
                <label className="form-field staff-guild-notice-field"><span className="form-label">{t("notice.label")}</span><textarea rows={4} maxLength={1500} value={noticeMessage} onChange={(event) => setNoticeMessage(event.target.value)} placeholder={t("notice.placeholder")} /><small>{t("notice.hint", { count: noticeMessage.length })}</small></label><button type="button" className="button button-primary" disabled={busyGuildAction || !noticeMessage.trim()} onClick={() => { if (window.confirm(t("notice.confirm", { owner: guild.owner_name, name: guild.name }))) void saveGuildAction(() => sendStaffGuildNotice(guild.id, noticeMessage, auth.csrf_token), t("notice.sent", { owner: guild.owner_name })); }}><Icon name="message" />{t("notice.send")}</button>
                {inviteUrl && inviteGuildId === guild.id && <div className="staff-guild-invite-result" role="status"><span>{t("invite.note")}</span><a href={inviteUrl} target="_blank" rel="noreferrer">{inviteUrl}</a><button type="button" className="button button-muted button-small" onClick={() => navigator.clipboard?.writeText(inviteUrl)}>{t("invite.copy")}</button></div>}
                {guild.blacklisted && <p className="staff-guild-blacklist-note"><strong>{t("guild.reasonLabel")}:</strong> {guild.blacklist_reason || t("guild.noReason")}</p>}
              </div>
            </div>}
          </article>;
        })}
      </div>}
    </section>}
    {activeTab === "appeals" && canReviewAppeals && <section id="staff-appeals-panel" role="tabpanel" aria-labelledby="staff-appeals-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Trust &amp; safety</span><h2>Blacklist appeals</h2><p>Review requests privately. Approval removes the active restriction while preserving its appealed history; denied appeals cannot be resubmitted.</p></div><div className="staff-guild-count"><strong>{appeals.filter((appeal) => appeal.status === "pending").length}</strong><span>pending review</span></div></header><div className="staff-guild-toolbar"><span className="staff-appeal-privacy">Visible to the bot owner and Head Admins</span><button type="button" className="button button-muted" onClick={() => void loadAppeals()} disabled={appealsLoading}><Icon name="spark" />{appealsLoading ? "Refreshing…" : "Refresh appeals"}</button></div>{appealsLoading && appeals.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading appeals…</p></div> : appeals.length === 0 ? <div className="staff-guild-empty">No blacklist appeals have been submitted.</div> : <div className="staff-guild-list">{appeals.map((appeal) => <article className={`staff-guild-card staff-appeal-card staff-appeal-${appeal.status}`} key={appeal.appeal_id}><div className="staff-appeal-header"><div className="staff-appeal-identity"><span className="panel-kicker">{appeal.guild_id ? "Guild appeal" : "User appeal"}</span><strong>{appeal.guild_id ? `Guild ${appeal.guild_id}` : appeal.username || "Discord user"}</strong><small>{appeal.guild_id ? `Submitted by user ${appeal.user_id}` : `Discord ID · ${appeal.user_id}`} <span aria-hidden="true">·</span> {new Date(appeal.created_at * 1000).toLocaleString()}</small></div><span className={`staff-guild-status${appeal.status === "denied" ? " is-blocked" : appeal.status === "pending" ? " is-pending" : " is-approved"}`}><i />{appeal.status}</span></div><div className="staff-appeal-reason staff-appeal-context"><span className="panel-kicker">Blacklist reason</span><p>{appeal.blacklist_reason || "No reason recorded."}</p></div><div className="staff-appeal-reason staff-appeal-message"><span className="panel-kicker">Appeal statement</span><p>{appeal.appeal_text}</p></div>{appeal.status === "pending" ? <><label className="form-field"><span className="form-label">Staff note {"(optional)"}</span><textarea rows={3} maxLength={2000} value={appealNotes[appeal.appeal_id] || ""} onChange={(event) => setAppealNotes((current) => ({ ...current, [appeal.appeal_id]: event.target.value }))} placeholder="Add context for the decision; the user can see this note…" /><small>{(appealNotes[appeal.appeal_id] || "").length}/2000 · shown to the user with the decision</small></label><div className="staff-appeal-actions"><button type="button" className="button button-muted" disabled={reviewingAppealId !== null} onClick={() => void reviewAppeal(appeal, "denied")}>{reviewingAppealId === appeal.appeal_id ? "Saving…" : "Deny appeal"}</button><button type="button" className="button button-primary" disabled={reviewingAppealId !== null} onClick={() => void reviewAppeal(appeal, "approved")}>{reviewingAppealId === appeal.appeal_id ? "Saving…" : "Approve appeal"}</button></div></> : <><div className="staff-appeal-reason staff-appeal-note"><span className="panel-kicker">Staff decision note</span><p>{appeal.staff_note || "No note added."}</p></div><small className="staff-appeal-reviewed">{appeal.status === "approved" ? "Approved" : "Denied"}{appeal.reviewed_at ? ` ${new Date(appeal.reviewed_at * 1000).toLocaleString()}` : ""} <span aria-hidden="true">·</span> Staff ID {appeal.reviewed_by || "unknown"}</small></>}</article>)}</div>}</section>}
    {activeTab === "proxy-workers" && canManageProxyWorkers && <section id="staff-proxy-workers-panel" role="tabpanel" aria-labelledby="staff-proxy-workers-tab" className="staff-guild-operations"><ProxyWorkersView csrfToken={auth.csrf_token} /></section>}
    {activeTab === "lavalink" && canManageLavalink && <section id="staff-lavalink-panel" role="tabpanel" aria-labelledby="staff-lavalink-tab" className="staff-guild-operations"><LavalinkView csrfToken={auth.csrf_token} /></section>}
    {activeTab === "maintenance" && canManageMaintenance && <section id="staff-maintenance-panel" role="tabpanel" aria-labelledby="staff-maintenance-tab" className="staff-guild-operations"><MaintenanceView csrfToken={auth.csrf_token} /></section>}
    {activeTab === "locales" && canManageLocales && <section id="staff-locales-panel" role="tabpanel" aria-labelledby="staff-locales-tab" className="staff-guild-operations"><LocaleSyncView csrfToken={auth.csrf_token} /></section>}
    {activeTab === "updates" && canManageUpdates && <section id="staff-updates-panel" role="tabpanel" aria-labelledby="staff-updates-tab" className="staff-guild-operations"><UpdatesView csrfToken={auth.csrf_token} /></section>}
    {activeTab === "staff-management" && canManageStaffRoster && <section id="staff-staff-management-panel" role="tabpanel" aria-labelledby="staff-staff-management-tab" className="staff-guild-operations">
      <header className="staff-guilds-heading"><div><span className="panel-kicker">Owner-only · access control</span><h2>Staff management</h2><p>View the full staff roster, assign or change roles, and suspend access during investigations. Suspension preserves the stored role and the member's public profile but removes every official Discord staff role and blocks staff commands and website pages until you lift it.</p></div><div className="staff-guild-count"><strong>{staffRoster.filter((member) => member.staff_status !== "former").length}</strong><span>{staffRoster.filter((member) => member.staff_status === "suspended").length} suspended · {staffRoster.filter((member) => member.staff_status === "former").length} former</span></div></header>
      <div className="staff-guild-toolbar"><label className="staff-guild-search"><Icon name="search" /><input type="search" value={staffRosterSearch} onChange={(event) => setStaffRosterSearch(event.target.value)} placeholder="Search staff by name, role, or ID" aria-label="Search staff roster" /></label><button type="button" className="button button-muted" onClick={() => void refreshStaffRoster()} disabled={staffRosterLoading}><Icon name="spark" />{staffRosterLoading ? "Refreshing…" : "Refresh roster"}</button></div>
      <div className="staff-roster-form"><input value={newStaffId} onChange={(event) => setNewStaffId(event.target.value)} inputMode="numeric" maxLength={22} pattern="[0-9]{1,22}" placeholder="Discord user ID" aria-label="New staff Discord user ID" /><Select ariaLabel="New staff role" placeholder="Choose staff role…" options={staffRosterRoles.map((role) => ({ value: role.key, label: role.label }))} value={newStaffRole} onChange={setNewStaffRole} /><button type="button" className="button button-primary" disabled={staffRosterBusy || !newStaffId.trim() || !newStaffRole} onClick={() => void addStaffRole()}>Add staff role</button></div>
      {staffRosterLoading && staffRoster.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading the staff roster…</p></div> : filteredStaffRoster.length === 0 ? <div className="staff-guild-empty">{staffRoster.length ? "No staff match that search." : "No staff records yet."}</div> : <div className="staff-guild-list">{filteredStaffRoster.map((member) => {
        const status = member.staff_status || "active";
        const isOwner = member.role === "owner";
        const selectedRole = staffRosterRoleDrafts[member.id] || member.role;
        const statusClass = status === "active" ? " is-approved" : status === "suspended" ? " is-blocked" : " is-pending";
        const profileLabel = member.visible ? "Public" : member.profile_visible ? "Saved · hidden" : "Hidden";
        return <article className="staff-guild-card" key={member.id}>
          <div className="staff-guild-row"><span className="staff-guild-icon">{member.avatar_url ? <img src={member.avatar_url} alt="" /> : <b>{member.name.slice(0, 1).toUpperCase()}</b>}</span><span className="staff-guild-title"><strong>{member.name}{member.username ? ` · @${member.username}` : ""}</strong><small>{member.role_label} · Discord ID {member.id}{member.status_changed_at ? ` · ${member.staff_status_label || status} ${new Date(member.status_changed_at * 1000).toLocaleDateString()}` : ""}</small></span><span className={`staff-guild-status${statusClass}`}><i />{member.staff_status_label || status}</span></div>
          <div className="staff-guild-details">
            <div className="staff-guild-summary"><div><span className="panel-kicker">Assigned role</span><strong>{member.role_label}</strong></div><div><span className="panel-kicker">Public profile</span><strong>{profileLabel}</strong></div><div><span className="panel-kicker">Staff access</span><strong>{status === "active" ? "Enabled" : "Blocked"}</strong></div>{member.status_reason && <div><span className="panel-kicker">Status note</span><strong>{member.status_reason}</strong></div>}</div>
            {isOwner ? <p className="staff-guild-blacklist-note">This is a configured bot owner. Owner access cannot be suspended or demoted from the staff roster.</p> : <div className="staff-guild-action-panel"><div className="staff-guild-action-heading"><div><span className="panel-kicker">Role &amp; access</span><h3>{status === "former" ? "Restore or keep this profile retained" : "Manage this staff member"}</h3></div><span className="staff-guild-id">{status === "suspended" ? "Suspension active" : status === "former" ? "Former staff" : "Active staff"}</span></div>
              <div className="staff-guild-actions"><div className="form-field staff-guild-reason"><span className="form-label">Staff role</span><Select ariaLabel="Staff role" placeholder={null} options={staffRosterRoles.map((role) => ({ value: role.key, label: role.label }))} value={selectedRole} onChange={(value) => setStaffRosterRoleDrafts((current) => ({ ...current, [member.id]: value }))} disabled={staffRosterBusy} /></div><button type="button" className="button button-primary" disabled={staffRosterBusy || !selectedRole} onClick={() => void saveStaffRole(member)}>{status === "former" ? "Assign & reinstate" : "Save role"}</button>{status === "suspended" && <button type="button" className="button button-primary" disabled={staffRosterBusy} onClick={() => void liftStaffSuspension(member)}>Lift suspension</button>}{status === "active" && <button type="button" className="button button-muted" disabled={staffRosterBusy} onClick={() => void suspendStaffMember(member)}>Suspend</button>}{status !== "former" && <button type="button" className="button button-danger" disabled={staffRosterBusy} onClick={() => void demoteStaffMember(member)}>Demote</button>}</div>
              <p className="staff-guild-blacklist-note">{status === "suspended" ? "The stored role and public profile stay saved. Lift the suspension to restore Discord and website access without a new appointment." : status === "former" ? "The public profile remains saved but hidden. Assigning a new role restores it; a data removal request deletes the profile data." : "Suspending interrupts access without demoting. Demoting keeps the public profile saved but hidden for a future return."}</p>
            </div>}
          </div>
        </article>;
      })}</div>}
    </section>}
    {activeTab === "broadcasts" && canManageStaffRoster && <section id="staff-broadcasts-panel" role="tabpanel" aria-labelledby="staff-broadcasts-tab" className="staff-guild-operations"><BroadcastStudioView csrfToken={auth.csrf_token} /></section>}
    {activeTab === "team-recruitment" && canManageNikoApplications && <section id="staff-team-recruitment-panel" role="tabpanel" aria-labelledby="staff-team-recruitment-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Owner-only · official team applications</span><h2>Team Applications</h2><p>Manage fixed role openings and review every submission from one queue. Role questions and role links are managed in code.</p></div><div className="staff-guild-count"><strong>{nikoSubmissions.length}</strong><span>submitted applications</span></div></header><div className="staff-guild-toolbar"><span className="staff-appeal-privacy">{nikoSubmissions.filter((submission) => submission.review_status === "pending").length} pending · {nikoSubmissions.filter((submission) => submission.review_status !== "pending").length} reviewed</span><button type="button" className="button button-muted" onClick={() => void refreshNikoApplications()} disabled={nikoBusy}><Icon name="spark" />{nikoBusy ? "Refreshing…" : "Refresh"}</button></div><section className="team-recruitment-openings"><div className="team-recruitment-list-heading"><div><span className="panel-kicker">Opening controls</span><h3>Role openings</h3></div><span>{nikoApplications.length} fixed roles</span></div><div className="staff-guild-list">{nikoApplications.map((application) => <article className="staff-guild-card" key={application.id}><div className="staff-guild-row"><span className="staff-guild-icon"><Icon name="users" /></span><span className="staff-guild-title"><strong>{application.title} · {application.role_name || "Role"}</strong><small>{application.submission_count} {application.submission_count === 1 ? "submission" : "submissions"} · {application.status === "open" ? "Accepting applications" : "Closed"} · /team/apply/{application.id}</small></span><button type="button" className="button button-muted button-small" onClick={() => void toggleNikoOpening(application)} disabled={nikoBusy}>{application.status === "open" ? "Close" : "Reopen"}</button></div></article>)}{nikoApplications.length === 0 && <div className="staff-guild-empty">Fixed role applications will appear here when available.</div>}</div></section><section className="team-recruitment-submissions"><div className="team-recruitment-list-heading"><div><span className="panel-kicker">Review queue</span><h3>Submitted applications</h3></div><span>{nikoSubmissions.length} total</span></div>{nikoBusy && nikoSubmissions.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading submitted applications…</p></div> : nikoSubmissions.length === 0 ? <div className="staff-guild-empty">No submitted applications yet.</div> : <><div className="team-recruitment-status-group"><div className="team-recruitment-status-heading"><h4>Pending review</h4><span>{nikoSubmissions.filter((submission) => submission.review_status === "pending").length}</span></div>{nikoSubmissions.filter((submission) => submission.review_status === "pending").length === 0 ? <p className="team-recruitment-empty-group">You’re all caught up. New submissions will appear here.</p> : <div className="team-recruitment-review-list">{nikoSubmissions.filter((submission) => submission.review_status === "pending").map((submission) => <article className="team-recruitment-review-entry" key={`${submission.opening_id}-${submission.user_id}`}><header className="team-recruitment-submission-heading"><div><strong>{submission.display_name}</strong><small>Discord ID · {submission.user_id}{submission.submitted_at ? ` · ${new Date(submission.submitted_at).toLocaleString()}` : ""}</small></div><span className="team-recruitment-opening-tag">{submission.opening_title} · {submission.role_name || "Role"}</span></header><div className="team-recruitment-answers">{submission.answers.map((answer) => <div key={answer.question_id}><strong>{answer.prompt}</strong><p>{Array.isArray(answer.answer) ? answer.answer.join(", ") || "No answer provided." : answer.answer || "No answer provided."}</p></div>)}</div><footer className="team-recruitment-review-actions"><button type="button" className="button button-muted button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "denied")}>Decline</button><button type="button" className="button button-primary button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "approved")}>Approve</button></footer></article>)}</div>}</div><div className="team-recruitment-status-group is-reviewed"><div className="team-recruitment-status-heading"><h4>Reviewed</h4><span>{nikoSubmissions.filter((submission) => submission.review_status !== "pending").length}</span></div>{nikoSubmissions.filter((submission) => submission.review_status !== "pending").length === 0 ? <p className="team-recruitment-empty-group">Reviewed applications will be kept here for reference.</p> : <div className="team-recruitment-review-list">{nikoSubmissions.filter((submission) => submission.review_status !== "pending").map((submission) => <article className="team-recruitment-review-entry" key={`${submission.opening_id}-${submission.user_id}`}><header className="team-recruitment-submission-heading"><div><strong>{submission.display_name}</strong><small>Discord ID · {submission.user_id}{submission.submitted_at ? ` · Submitted ${new Date(submission.submitted_at).toLocaleString()}` : ""}</small></div><span className={`team-recruitment-decision ${submission.review_status}`}>{submission.review_status === "approved" ? "Approved" : "Declined"}</span></header><div className="team-recruitment-opening-tag">{submission.opening_title} · {submission.role_name || "Role"}</div><div className="team-recruitment-answers">{submission.answers.map((answer) => <div key={answer.question_id}><strong>{answer.prompt}</strong><p>{Array.isArray(answer.answer) ? answer.answer.join(", ") || "No answer provided." : answer.answer || "No answer provided."}</p></div>)}</div><small className="team-recruitment-review-meta">{submission.reviewed_at ? `Reviewed ${new Date(submission.reviewed_at).toLocaleString()}` : "Decision recorded"}{submission.reviewed_by ? ` · Staff ID ${submission.reviewed_by}` : ""}</small><footer className="team-recruitment-review-actions">{submission.review_status === "approved" ? <button type="button" className="button button-muted button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "denied")}>Revoke approval</button> : <button type="button" className="button button-primary button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "approved")}>Approve instead</button>}</footer></article>)}</div>}</div></>}</section></section>}
    {activeTab === "billing" && canManageBilling && <section id="staff-billing-panel" role="tabpanel" aria-labelledby="staff-billing-tab" className="staff-guild-operations">
      <header className="staff-guilds-heading"><div><span className="panel-kicker">{t("billing.kicker")}</span><h2>{t("billing.title")}</h2><p>{t("billing.body")}</p></div><div className="staff-guild-count"><strong>{billing?.totals.paid_label || t("billing.zero")}</strong><span>{t("billing.collected")}</span></div></header>
      <div className="staff-guild-toolbar"><span className="staff-appeal-privacy">{billing?.gateway.configured ? t("billing.gatewayOk") : t("billing.gatewayMissing")}</span><button type="button" className="button button-muted" onClick={() => void refreshBilling()}><Icon name="spark" />{t("billing.refresh")}</button></div>
      {!billing ? <div className="staff-guild-empty"><div className="loading-ring" /><p>{t("billing.loading")}</p></div> : <>          <div className="staff-guild-summary"><div><span className="panel-kicker">{t("billing.activeServers")}</span><strong>{billing.totals.active_count}</strong></div><div><span className="panel-kicker">{t("billing.expiring")}</span><strong>{billing.totals.expiring_soon}</strong></div><div><span className="panel-kicker">{t("billing.paidPayments")}</span><strong>{billing.totals.paid_count}</strong></div><div><span className="panel-kicker">{t("billing.needsAttention")}</span><strong>{billing.payments.filter((payment) => payment.issue_status === "open").length}</strong></div><div><span className="panel-kicker">{t("billing.awaiting")}</span><strong>{billing.payments.filter((payment) => !payment.paid && !payment.issue_status).length}</strong></div></div>
        <div className="staff-billing-grant">
          <label className="form-field"><span className="form-label">{t("billing.guildId")}</span><input value={billingGuild} onChange={(event) => setBillingGuild(event.target.value)} placeholder="123456789012345678" /></label>
          <label className="form-field"><span className="form-label">{t("billing.months")}</span><input type="number" min="1" max="12" value={billingMonths} onChange={(event) => setBillingMonths(event.target.value)} /></label>
          <button type="button" className="button button-primary" disabled={billingBusy || !billingGuild.trim()} onClick={() => void changeBillingSubscription(billingGuild, "grant")}>{t("billing.grant")}</button>
          <button type="button" className="button button-muted" disabled={billingBusy || !billingGuild.trim()} onClick={() => void changeBillingSubscription(billingGuild, "cancel")}>{t("billing.cancel")}</button>
        </div>
        <h3 className="staff-billing-heading">{t("billing.recentPayments")}</h3>
        {billing.payments.length === 0 ? <div className="staff-guild-empty">{t("billing.noPayments")}</div> : <div className="staff-guild-list">{billing.payments.map((payment) => {
          const state = billingPaymentState(payment);
          const note = billingNoteFor(payment);
          const savedNote = payment.issue_note ?? "";
          return <article className={`staff-guild-card staff-billing-payment ${state.className}`} key={payment.order_id}>
            <div className="staff-billing-payment-head"><div className="staff-guild-title"><strong>{payment.guild_name || t("billing.guild", { id: payment.guild_id })} · {payment.amount_label}</strong><small>{payment.kind} · {payment.pay_currency || payment.currency} · {payment.payer_name || t("billing.user", { id: payment.payer_id })} · {payment.created_at ? new Date(payment.created_at.replace(" ", "T") + "Z").toLocaleString() : t("billing.unknownTime")}</small></div><span className={`staff-guild-status ${state.className}`}><i />{state.label}</span></div>
            <div className="staff-billing-payment-foot"><code>{payment.order_id}</code><span className={`staff-billing-payment-paid${payment.paid ? " is-paid" : ""}`}>{payment.paid ? t("billing.cryptoReceived") : t("billing.providerStatus", { status: payment.status })}</span></div>
            <div className="staff-billing-payment-note"><label className="form-field staff-billing-note"><span className="form-label">{t("billing.noteLabel")}</span><input maxLength={1000} value={note} onChange={(event) => setBillingNotes((current) => ({ ...current, [payment.order_id]: event.target.value }))} placeholder={t("billing.notePlaceholder")} /></label><button type="button" className="button button-muted button-small" disabled={billingBusy || note === savedNote} onClick={() => void saveBillingNote(payment)}>{t("billing.saveNote")}</button></div>
            <div className="staff-billing-payment-actions">
              {payment.issue_status ? <button type="button" className="button button-muted button-small" disabled={billingBusy} onClick={() => void resolveBilling(payment.order_id, "clear")}>{payment.issue_status === "resolved" ? t("billing.undoResolve") : t("billing.clearFlag")}</button> : <button type="button" className="button button-muted button-small" disabled={billingBusy} onClick={() => void resolveBilling(payment.order_id, "open")}>{t("billing.flag")}</button>}
              {payment.issue_status !== "resolved" && <button type="button" className="button button-primary button-small" disabled={billingBusy} onClick={() => void resolveBilling(payment.order_id, "resolved")}>{t("billing.markResolved")}</button>}
            </div>
            {payment.issue_status && payment.resolved_at && <p className="staff-guild-blacklist-note">{t(payment.issue_status === "resolved" ? "billing.resolvedAt" : "billing.flaggedAt", { date: new Date(payment.resolved_at.replace(" ", "T") + "Z").toLocaleString(), staff: payment.resolved_by || t("billing.unknownStaff") })}</p>}
          </article>;
        })}</div>}
        <h3 className="staff-billing-heading">{t("billing.subscriptions")}</h3>
        {billing.subscriptions.length === 0 ? <div className="staff-guild-empty">{t("billing.noSubscriptions")}</div> : <div className="staff-guild-list">{billing.subscriptions.map((subscription) => <article className="staff-guild-card staff-billing-subscription" key={subscription.guild_id}>
          <div className="staff-billing-payment-head"><div className="staff-guild-title"><strong>{subscription.guild_name || t("billing.guild", { id: subscription.guild_id || "" })}</strong><small>{subscription.active ? t("billing.activeLeft", { count: subscription.days_remaining ?? 0 }) : subscription.status} · {subscription.source}{subscription.gifted_by_name ? t("billing.giftedBy", { name: subscription.gifted_by_name }) : ""}</small></div><span className={`staff-guild-status${subscription.active ? " is-approved" : " is-blocked"}`}><i />{subscription.active ? t("billing.active") : subscription.status}</span></div>
          <div className="staff-billing-payment-foot"><code>{subscription.guild_id}</code><span className="staff-appeal-privacy">{t("billing.ends", { date: subscription.expires_at || t("billing.unknown") })}</span><button type="button" className="button button-muted button-small" disabled={billingBusy} onClick={() => void changeBillingSubscription(subscription.guild_id || "", "cancel")}>{t("billing.cancelSubscription")}</button></div>
        </article>)}</div>}
      </>}
    </section>}
    {activeTab === "data-removal" && canManageDataRemoval && <section id="staff-data-removal-panel" role="tabpanel" aria-labelledby="staff-data-removal-tab" className="staff-guild-operations">
      <header className="staff-guilds-heading"><div><span className="panel-kicker">{t("dataRemoval.kicker")}</span><h2>{t("dataRemoval.title")}</h2><p>{t("dataRemoval.bodyBefore")} <code>utils/data_removal.py</code>{t("dataRemoval.bodyAfter")}</p></div><div className="staff-guild-count"><strong>{dataRemoval?.filter((request) => request.status === "pending").length ?? 0}</strong><span>{t("dataRemoval.pending")}</span></div></header>
      <div className="staff-guild-toolbar"><span className="staff-appeal-privacy">{t("dataRemoval.privacy")}</span><button type="button" className="button button-muted" onClick={() => void refreshDataRemoval()}><Icon name="spark" />{t("dataRemoval.refresh")}</button></div>
      {!dataRemoval ? <div className="staff-guild-empty"><div className="loading-ring" /><p>{t("dataRemoval.loading")}</p></div> : dataRemoval.length === 0 ? <div className="staff-guild-empty">{t("dataRemoval.none")}</div> : <div className="staff-guild-list">{dataRemoval.map((request) => <article className="staff-guild-card" key={request.id}>
        <div className="staff-guild-row"><span className="staff-guild-icon"><Icon name={request.scope === "account" ? "users" : "shield"} /></span><span className="staff-guild-title"><strong>{request.scope === "account" ? t("dataRemoval.accountOf", { id: request.user_id }) : request.guild_name || t("dataRemoval.serverOf", { id: request.guild_id || "" })}</strong><small>{new Date(request.created_at * 1000).toLocaleString()} · {t("dataRemoval.requestShort", { id: request.id.slice(0, 8) })}{request.guild_id ? t("dataRemoval.guildShort", { id: request.guild_id }) : ""}</small></span><span className={`staff-guild-status${request.status === "completed" ? " is-approved" : request.status === "denied" || request.status === "withdrawn" ? " is-blocked" : " is-pending"}`}><i />{request.status}</span></div>
        <div className="staff-appeal-reason"><span className="panel-kicker">{t("dataRemoval.explanation")}</span><p>{request.reason || t("dataRemoval.noExplanation")}</p></div>
        {request.review_note && <div className="staff-appeal-reason"><span className="panel-kicker">{t("dataRemoval.ownerNote")}</span><p>{request.review_note}</p></div>}
        {request.result && <div className="staff-appeal-reason"><span className="panel-kicker">{t("dataRemoval.result")}</span><p>{t("dataRemoval.tablesCleared", { count: request.result.removed?.length ?? 0 })}{request.result.anonymized?.length ? t("dataRemoval.anonymized", { count: request.result.anonymized.length }) : ""}. {request.result.preserved?.join("; ") || t("dataRemoval.preserved")}{request.result.errors?.length ? t("dataRemoval.backendWarnings", { count: request.result.errors.length }) : ""}</p></div>}
        {request.status === "pending" && <><label className="form-field"><span className="form-label">{t("dataRemoval.noteLabel")} {t("dataRemoval.noteRequired")}</span><textarea rows={3} maxLength={2000} value={dataRemovalNotes[request.id] || ""} onChange={(event) => setDataRemovalNotes((current) => ({ ...current, [request.id]: event.target.value }))} placeholder={t("dataRemoval.notePlaceholder")} /></label><div className="staff-appeal-actions"><button type="button" className="button button-muted" disabled={dataRemovalBusy} onClick={() => void reviewDataRemoval(request, "denied")}>{t("dataRemoval.deny")}</button><button type="button" className="button button-primary" disabled={dataRemovalBusy} onClick={() => void reviewDataRemoval(request, "approved")}>{dataRemovalBusy ? t("common.working") : t("dataRemoval.approve")}</button></div></>}
      </article>)}</div>}
    </section>}
    {activeTab === "reports" && <section id="staff-reports-panel" role="tabpanel" aria-labelledby="staff-reports-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Diagnostics</span><h2>Bot error reports</h2><p>Recent command and runtime failures collected by Niko. Expand a report to inspect its details and traceback; use the code to retrieve it with <code>.staff getreport CODE</code>.</p></div><div className="staff-guild-count"><strong>{errorReports.length}</strong><span>recent reports</span></div></header><div className="staff-guild-toolbar"><label className="staff-guild-search"><Icon name="search" /><input type="search" value={reportSearch} onChange={(event) => setReportSearch(event.target.value)} placeholder="Search report code, exception, or details" aria-label="Search error reports" /></label><button type="button" className="button button-muted" onClick={() => void refreshErrorReports()} disabled={reportsLoading}><Icon name="spark" />{reportsLoading ? "Refreshing…" : "Refresh reports"}</button></div>{reportsLoading && errorReports.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading recent error reports…</p></div> : errorReports.filter((item) => `${item.code} ${item.report}`.toLocaleLowerCase().includes(reportSearch.trim().toLocaleLowerCase())).length === 0 ? <div className="staff-guild-empty">{errorReports.length ? "No reports match that search." : "No bot error reports have been saved."}</div> : <div className="staff-guild-list">{errorReports.filter((item) => `${item.code} ${item.report}`.toLocaleLowerCase().includes(reportSearch.trim().toLocaleLowerCase())).map((item) => { const lines = item.report.split("\n"); const exceptionIndex = lines.findIndex((line) => line === "Exception"); const exception = lines.slice(exceptionIndex + 2).find((line) => line.startsWith("Type:") || line.startsWith("Message:")) || "Unknown exception"; const detailsIndex = lines.findIndex((line) => line === "Occurred (UTC):"); const summary = lines.slice(detailsIndex + 2).find((line) => line.trim()) || "No report details"; const expanded = expandedReportCode === item.code; return <article className={`staff-guild-card${expanded ? " expanded" : ""}`} key={item.code}><button type="button" className="staff-guild-row staff-report-row" aria-expanded={expanded} onClick={() => setExpandedReportCode(expanded ? null : item.code)}><span className="staff-report-mark"><Icon name="alert" /></span><span className="staff-guild-title"><strong>{item.code} · {exception.replace(/^(Type|Message):\s*/, "")}</strong><small>{new Date(item.created_at).toLocaleString()} · {summary.slice(0, 140)}</small></span><span className="staff-guild-status is-blocked"><i />Error</span><Icon name={expanded ? "close" : "arrow"} className="staff-guild-chevron" /></button>{expanded && <div className="staff-report-details"><div className="staff-report-summary"><span className="panel-kicker">Report code</span><strong>{item.code}</strong></div><pre>{item.report}</pre><div className="staff-report-actions"><button type="button" className="button button-muted button-small" onClick={() => navigator.clipboard?.writeText(item.code)}>Copy code</button><button type="button" className="button button-muted button-small" onClick={() => navigator.clipboard?.writeText(item.report)}>Copy full report</button></div></div>}</article>; })}</div>}</section>}
    {activeTab === "blacklist" && canManageGuilds && <section id="staff-blacklist-panel" role="tabpanel" aria-labelledby="staff-blacklist-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Trust & safety</span><h2>Blacklist management</h2><p>Manage blocked Discord users and guilds. Access follows the guild-operations roles, and every mutation is recorded with its reason.</p></div><div className="staff-guild-count"><strong>{blacklistEntries.users.length + blacklistEntries.guilds.length}</strong><span>active entries</span></div></header><div className="staff-blacklist-form"><Select ariaLabel="Blacklist entry type" placeholder={null} options={BLACKLIST_TYPES} value={blacklistType} onChange={(value) => setBlacklistType(value as "user" | "guild")} /><input value={blacklistId} onChange={(event) => setBlacklistId(event.target.value)} inputMode="numeric" maxLength={22} pattern="[0-9]{1,22}" placeholder="Discord ID" aria-label="Discord ID" /><input value={blacklistReason} onChange={(event) => setBlacklistReason(event.target.value)} maxLength={1000} placeholder="Reason (required)" aria-label="Blacklist reason" /><button type="button" className="button button-danger" disabled={busyGuildAction || !blacklistId || blacklistId.length > 22 || [...blacklistId].some((digit) => digit < "0" || digit > "9") || !blacklistReason.trim()} onClick={() => void addBlacklistEntry()}>Add to blacklist</button></div><label className="staff-guild-search"><Icon name="search" /><input type="search" value={blacklistSearch} onChange={(event) => setBlacklistSearch(event.target.value)} placeholder="Filter by ID or reason" aria-label="Filter blacklist" /></label><div className="staff-blacklist-columns">{(["users", "guilds"] as const).map((kind) => <section className="staff-blacklist-list" key={kind}><div className="staff-blacklist-list-heading"><span>{kind === "users" ? "Blocked users" : "Blocked guilds"}</span><strong>{blacklistEntries[kind].length}</strong></div>{blacklistEntries[kind].filter((entry) => `${entry.id} ${entry.reason || ""}`.toLocaleLowerCase().includes(blacklistSearch.trim().toLocaleLowerCase())).map((entry) => <article className="staff-blacklist-entry" key={entry.id}><div><strong>{entry.id}</strong><p>{entry.reason || "No reason recorded."}</p><small>{new Date(entry.timestamp * 1000).toLocaleString()}</small></div><div className="staff-blacklist-entry-actions"><button type="button" className="button button-muted button-small" disabled={busyGuildAction} onClick={() => { const reason = window.prompt("Update blacklist reason", entry.reason || ""); if (reason?.trim()) void saveGuildAction(async () => { await updateStaffBlacklist(kind === "users" ? "user" : "guild", "update", String(entry.id), reason, auth.csrf_token); setBlacklistEntries(await getStaffBlacklist()); }, "Blacklist reason updated."); }}>Edit reason</button><button type="button" className="button button-danger button-small" disabled={busyGuildAction} onClick={() => { if (window.confirm(`Remove ${entry.id} from the blacklist?`)) void saveGuildAction(async () => { await updateStaffBlacklist(kind === "users" ? "user" : "guild", "remove", String(entry.id), "", auth.csrf_token); setBlacklistEntries(await getStaffBlacklist()); }, "Blacklist entry removed."); }}>Remove</button></div></article>)}{blacklistEntries[kind].filter((entry) => `${entry.id} ${entry.reason || ""}`.toLocaleLowerCase().includes(blacklistSearch.trim().toLocaleLowerCase())).length === 0 && <p className="staff-blacklist-empty">{blacklistEntries[kind].length ? "No entries match that filter." : `No ${kind} are blacklisted.`}</p>}</section>)}</div></section>}
    {permissionGuild && <div className="modal-backdrop" role="presentation" onClick={() => setPermissionGuild(null)}><section className="modal-card staff-permissions-modal" role="dialog" aria-modal="true" aria-labelledby="guild-permissions-title" onClick={(event) => event.stopPropagation()}><div className="panel-heading"><div><span className="panel-kicker">Discord access audit</span><h3 id="guild-permissions-title">{permissionGuild.name} permissions</h3><p>{permissionGuild.bot_permissions.filter((permission) => permission.granted).length} granted · {permissionGuild.bot_permissions.filter((permission) => !permission.granted).length} missing</p></div><button type="button" className="button button-muted" onClick={() => setPermissionGuild(null)}>Close</button></div><div className="staff-permissions-list">{permissionGuild.bot_permissions.map((permission) => <div key={permission.name} className={permission.granted ? "granted" : "missing"}><span>{permission.label}</span><strong>{permission.granted ? "Granted" : "Missing"}</strong></div>)}</div></section></div>}
    {lockdownSummary && <div className="modal-backdrop" role="presentation" onClick={() => setLockdownSummary(null)}><section className="modal-card staff-lockdown-modal" role="dialog" aria-modal="true" aria-labelledby="guild-lockdown-title" onClick={(event) => event.stopPropagation()}><div className="panel-heading"><div><span className="panel-kicker">Blacklist complete</span><h3 id="guild-lockdown-title">{lockdownSummary.guildName} is blacklisted</h3><p>Saved settings, polls, giveaways and the starboard are kept and switched off. An approved appeal gives them back; the social notifier is turned back on by the server itself.</p></div><button type="button" className="button button-muted" onClick={() => setLockdownSummary(null)}>Close</button></div><div className="staff-lockdown-summary">
      {([["paused", "Paused"], ["skipped", "Not in use"], ["failed", "Needs attention"]] as const).map(([bucket, heading]) => {
        const items = groupLockdownSteps(lockdownSummary.steps)[bucket];
        return <section className={`staff-lockdown-group is-${bucket}`} key={bucket}><div className="staff-lockdown-group-heading"><span>{heading}</span><strong>{items.length}</strong></div>{items.length === 0 ? <p className="staff-lockdown-empty">Nothing here.</p> : items.map((item) => <article key={item.step}><strong>{item.label.replace(/…$/, "")}</strong><p>{item.detail}</p><small>{LOCKDOWN_STATUS_LABELS[item.status]}</small></article>)}</section>;
      })}
    </div></section></div>}
  </div>;

  return <DashboardShell user={auth.user!} guilds={guilds} selectedGuild={null} view="overview" section="overview" userTab="overview" stats={stats} staffRole={staff.role} onHome={() => navigate(dashboardPath())} onServers={() => navigate(dashboardServersPath())} onGuildChange={() => undefined} onSectionChange={() => undefined} onUserTabChange={(tab) => navigate(dashboardUserPath(tab))} onRefresh={() => window.location.reload()} refreshing={false}>{content}</DashboardShell>;
}
