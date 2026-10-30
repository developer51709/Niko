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
import { BotAnalyticsView } from "../components/dashboard/BotAnalyticsView";
import { BroadcastStudioView } from "../components/dashboard/BroadcastStudioView";
import { Switch } from "../components/dashboard/Switch";
import { ColorPicker } from "../components/dashboard/ColorPicker";
import { SettingCard, SettingCards } from "../components/dashboard/SettingCards";
import { PublicHeader } from "../components/PublicHeader";
import { dashboardPath, dashboardServersPath, dashboardUserPath, navigate } from "../router";
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

type StaffTab = "profile" | "analytics" | "global" | "guilds" | "blacklist" | "appeals" | "proxy-workers" | "team-recruitment" | "staff-management" | "broadcasts" | "billing" | "data-removal" | "reports";

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
        getStaffGuilds().then((result) => setStaffGuilds(result.guilds)).catch((reason) => notifyError(reason instanceof Error ? reason.message : "Guild list unavailable.", "staff-guilds")).finally(() => setStaffGuildsLoading(false));
        getStaffBlacklist().then(setBlacklistEntries).catch((reason) => notifyError(reason instanceof Error ? reason.message : "Blacklist unavailable.", "staff-blacklist"));
        if (["owner", "head_admin"].includes(staffStatus.role)) {
          getStaffBlacklistAppeals().then((result) => setAppeals(result.appeals)).catch((reason) => notifyError(reason instanceof Error ? reason.message : "Appeals unavailable.", "staff-appeals"));
        }
      }
      void loadErrorReports();
    }).catch((reason) => {
      if (active) {
        setAccessError(reason instanceof Error ? reason.message : "Staff access unavailable.");
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

  if (accessLoading) return <div className="dashboard-state"><div className="loading-ring" /><p>Verifying your account and staff access…</p></div>;
  if (accessError || !staff || !auth?.authenticated) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><div className="eyebrow">Staff workspace</div><h1>{!auth && accessError ? "Staff access unavailable." : "Private team area."}</h1><p>{!auth && accessError ? accessError : !auth?.authenticated ? "You are not logged in. Sign in with Discord to continue to staff settings." : accessError || "This area is only available to official Niko staff."}</p>{auth && !auth.authenticated && <a className="button button-primary full-width" href="/auth/login?next=/dashboard/staff">Continue with Discord</a>}<button className="back-link" onClick={() => navigate("/dashboard")}>Return to dashboard</button></div></main></>;

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
  const cardProfileUrl = `${window.location.origin}/team/${staff.profile.id}`;
  const cardMarkdown = `[![Niko staff card](${cardBaseUrl})](${cardProfileUrl})`;
  const copyCardMarkdown = async () => {
    try {
      await navigator.clipboard.writeText(cardMarkdown);
      notifySuccess("Card markdown copied — paste it into your GitHub profile README.", "staff-card");
    } catch {
      notifyError("Clipboard access was blocked. Select the snippet and copy it manually.", "staff-card");
    }
  };
  const canManageGlobal = tabAllowedForRole(staff.role, "global");
  const canManageGuilds = tabAllowedForRole(staff.role, "guilds");
  const canReviewAppeals = tabAllowedForRole(staff.role, "appeals");
  const canManageProxyWorkers = tabAllowedForRole(staff.role, "proxy-workers");
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
      notifyError("Choose a link type and enter its URL, or remove the unfinished link.", "staff-profile");
      return;
    }
    setSaving(true); notifyLoading("Saving your public listing…", "staff-profile");
    const payload = {
      public_bio: form.public_bio,
      public_banner_url: form.public_banner_url,
      public_visible: form.public_visible,
      public_links: linksToSave,
    };
    try { await saveStaffProfile(payload, auth.csrf_token); notifySuccess("Your public team listing was saved.", "staff-profile"); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : "Could not save listing.", "staff-profile"); }
    finally { setSaving(false); }
  };
  const saveCard = async () => {
    if (savingCard) return;
    setSavingCard(true); notifyLoading("Saving your card settings…", "staff-card-settings");
    // The API stores the accent as bare hex digits and treats an empty value as
    // "back to the default"; normalise here so the card matches the picker.
    try {
      await saveStaffProfile({
        card_theme: form.card_theme,
        card_accent: form.card_accent.replace(/^#/, "").toUpperCase(),
        card_show_status: form.card_show_status,
      }, auth.csrf_token);
      notifySuccess("Card settings saved. Your README card picks them up on its next refresh.", "staff-card-settings");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "Could not save card settings.", "staff-card-settings");
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
    }, "User added to blacklist.");
  };
  async function loadErrorReports() {
    setReportsLoading(true);
    try { setErrorReports((await getStaffErrorReports()).reports); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : "Error reports unavailable.", "staff-reports"); }
    finally { setReportsLoading(false); }
  };
  const refreshErrorReports = () => void loadErrorReports();
  async function loadAppeals() {
    setAppealsLoading(true);
    try { setAppeals((await getStaffBlacklistAppeals()).appeals); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : "Blacklist appeals unavailable.", "staff-appeals"); }
    finally { setAppealsLoading(false); }
  }
  const reviewAppeal = async (appeal: BlacklistAppeal, status: "approved" | "denied") => {
    if (reviewingAppealId) return;
    setReviewingAppealId(appeal.appeal_id);
    notifyLoading("Saving the appeal decision…", "staff-appeals");
    try {
      await reviewStaffBlacklistAppeal(appeal.appeal_id, status, appealNotes[appeal.appeal_id] || "", auth.csrf_token);
      // The queue below reloads with the new decision, so the spinner is
      // retired here; a reload failure still reports itself as an error toast.
      clearToasts("staff-appeals");
      await loadAppeals();
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : "The appeal decision could not be saved.", "staff-appeals"); }
    finally { setReviewingAppealId(null); }
  };
  const refreshStaffGuilds = async () => {
    setStaffGuildsLoading(true);
    try { setStaffGuilds((await getStaffGuilds()).guilds); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : "Guild list unavailable.", "staff-guilds"); }
    finally { setStaffGuildsLoading(false); }
  };
  const saveGuildAction = async (action: () => Promise<unknown>, success: string) => {
    if (busyGuildAction) return;
    setBusyGuildAction(true); notifyLoading("Applying that guild action…", "staff-guild-action");
    try { await action(); notifySuccess(success, "staff-guild-action"); await refreshStaffGuilds(); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : "The guild action could not be completed.", "staff-guild-action"); }
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
      notifyError(actionError instanceof Error ? actionError.message : "The guild could not be blacklisted.", `staff-guild-lockdown-${guildId}`);
      return null;
    } finally {
      setBusyGuildAction(false);
    }
  };
  async function refreshBilling() {
    try { setBilling(await getStaffBilling()); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : "Billing data unavailable.", "staff-billing"); }
  }
  async function refreshDataRemoval() {
    try { setDataRemoval((await getStaffDataRemovalRequests()).requests); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : "Data removal requests unavailable.", "staff-data-removal"); }
  }
  async function refreshStaffRoster() {
    setStaffRosterLoading(true);
    try {
      const result = await getStaffMembers();
      setStaffRoster(result.members);
      setStaffRosterRoles(result.roles);
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The staff roster could not be loaded.", "staff-roster");
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
    notifyLoading("Updating staff access…", "staff-roster");
    try {
      const result = await manageStaffMember(member.id, { action, role, reason }, auth.csrf_token);
      const roleLabel = staffRosterRoles.find((item) => item.key === role)?.label || role || "staff";
      if (action === "assign" && result.status === "suspended") {
        notifySuccess(`${member.name} has the ${roleLabel} role saved, but their suspension remains active. Lift it when the investigation ends.`, "staff-roster");
      } else if (action === "assign") {
        notifySuccess(`${member.name} now has the ${roleLabel} role. Their retained public-profile settings were preserved.`, "staff-roster");
      } else if (action === "suspend") {
        notifySuccess(`${member.name} is suspended. Their Discord staff roles and all staff access were removed; the stored role and public profile are retained.`, "staff-roster");
      } else if (action === "lift") {
        notifySuccess(`${member.name}'s suspension was lifted and their Discord staff roles were restored.`, "staff-roster");
      } else {
        notifySuccess(`${member.name} was demoted. Their public profile is retained but hidden in case they return.`, "staff-roster");
      }
      await refreshStaffRoster();
    } catch (actionError) {
      notifyError(actionError instanceof Error ? actionError.message : "The staff update could not be completed.", "staff-roster");
    } finally {
      setStaffRosterBusy(false);
    }
  };
  const saveStaffRole = async (member: StaffMember) => {
    const role = staffRosterRoleDrafts[member.id] || member.role;
    if (!role) { notifyError("Choose a staff role first.", "staff-roster"); return; }
    const label = staffRosterRoles.find((item) => item.key === role)?.label || role;
    if (!window.confirm(`Give ${member.name} the ${label} role?`)) return;
    await rosterAction(member, "assign", role);
  };
  const suspendStaffMember = async (member: StaffMember) => {
    const reason = window.prompt(
      `Why is ${member.name} being suspended?\n\nThis is recorded in the staff roster. Their stored role and public profile are retained, but all staff access is removed until you lift the suspension.`,
      "",
    );
    if (reason === null) return;
    if (reason.trim().length < 5) { notifyError("Add a short reason for the suspension.", "staff-roster"); return; }
    if (!window.confirm(`Suspend ${member.name} and remove their staff access now?`)) return;
    await rosterAction(member, "suspend", undefined, reason.trim());
  };
  const demoteStaffMember = async (member: StaffMember) => {
    if (!window.confirm(`Demote ${member.name}? Their public profile will be kept but hidden in case they return.`)) return;
    const reason = window.prompt("Reason for the demotion (optional)", "") || "";
    await rosterAction(member, "demote", undefined, reason.trim());
  };
  const liftStaffSuspension = async (member: StaffMember) => {
    if (!window.confirm(`Lift ${member.name}'s suspension and restore their staff roles?`)) return;
    await rosterAction(member, "lift");
  };
  const addStaffRole = async () => {
    if (!/^\d{5,22}$/.test(newStaffId.trim()) || !newStaffRole) {
      notifyError("Enter a Discord user ID and choose a staff role.", "staff-roster");
      return;
    }
    const roleLabel = staffRosterRoles.find((item) => item.key === newStaffRole)?.label || newStaffRole;
    if (!window.confirm(`Give user ${newStaffId.trim()} the ${roleLabel} role?`)) return;
    await rosterAction(
      { id: newStaffId.trim(), name: `User ${newStaffId.trim()}`, role: newStaffRole, role_label: roleLabel },
      "assign",
      newStaffRole,
    );
    setNewStaffId("");
    setNewStaffRole("");
  };
  const reviewDataRemoval = async (request: StaffDataRemovalRequest, status: "approved" | "denied") => {
    if (dataRemovalBusy) return;
    const action = status === "approved" ? "approve and permanently run this deletion" : "deny this request";
    if (!window.confirm(`Are you sure you want to ${action}?`)) return;
    setDataRemovalBusy(true);
    notifyLoading(status === "approved" ? "Running the scoped deletion…" : "Saving the decision…", "staff-data-removal");
    try {
      await reviewStaffDataRemoval(request.id, status, dataRemovalNotes[request.id] || "", auth.csrf_token);
      notifySuccess(status === "approved" ? "Request completed. Moderation records were preserved." : "Request denied.", "staff-data-removal");
      await refreshDataRemoval();
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : "The request could not be reviewed.", "staff-data-removal"); }
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
      notifySuccess("Billing note saved.", "staff-billing");
      await refreshBilling();
      forgetBillingDraft(payment.order_id);
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : "The note could not be saved.", "staff-billing"); }
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
        status === "resolved" ? "Marked resolved." : status === "open" ? "Flagged for follow-up." : "Decision undone.",
        "staff-billing",
      );
      await refreshBilling();
      forgetBillingDraft(orderId);
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : "The note could not be saved.", "staff-billing"); }
    finally { setBillingBusy(false); }
  };
  const changeBillingSubscription = async (guildId: string, action: "grant" | "cancel") => {
    if (billingBusy || !guildId.trim()) return;
    setBillingBusy(true);
    try {
      await updateStaffSubscription(guildId.trim(), action, action === "grant" ? Number(billingMonths) || 1 : 1, auth.csrf_token);
      notifySuccess(action === "grant" ? `Granted ${billingMonths} month(s) to ${guildId}.` : `Cancelled ${guildId}'s subscription.`, "staff-billing");
      setBillingGuild("");
      await refreshBilling();
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : "The subscription could not be changed.", "staff-billing"); }
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
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : "Team Applications page unavailable.", "staff-niko-applications"); }
    finally { setNikoBusy(false); }
  }
  const toggleNikoOpening = async (application: TeamRecruitmentOpening) => {
    setNikoBusy(true); notifyLoading("Changing that opening…", "staff-niko-applications");
    try { await setTeamRecruitmentOpeningStatus(application.id, application.status === "open" ? "closed" : "open", auth.csrf_token); clearToasts("staff-niko-applications"); await refreshNikoApplications(); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : "Opening status could not be changed.", "staff-niko-applications"); }
    finally { setNikoBusy(false); }
  };
  const reviewNikoSubmission = async (submission: ReviewedTeamSubmission, status: "approved" | "denied") => {
    if (nikoBusy) return;
    const revoking = status === "denied" && submission.review_status === "approved";
    if (revoking && !window.confirm(`Reverse ${submission.display_name}'s approval and remove the ${submission.role_name || "team"} role?`)) return;
    setNikoBusy(true); notifyLoading("Saving that decision…", "staff-niko-applications");
    try {
      const result = await reviewTeamRecruitmentSubmission(submission.opening_id, submission.user_id, status, auth.csrf_token);
      if (result.unchanged) {
        notifySuccess(`${submission.display_name} already has that decision recorded. Nothing was re-sent or changed.`, "staff-niko-applications");
      } else if (status === "approved") {
        notifySuccess(result.dm_sent === false
          ? `${submission.display_name} was approved and the team role was assigned, but the decision DM could not be delivered.`
          : `${submission.display_name} was approved, the team role was assigned, and the decision DM was sent.`, "staff-niko-applications");
      } else {
        notifySuccess(result.role_revoked
          ? `${submission.display_name} was declined and the previously granted team role was removed.`
          : `${submission.display_name} was declined.`, "staff-niko-applications");
      }
      await refreshNikoApplications();
    } catch (reason) { notifyError(reason instanceof Error ? reason.message : "The application decision could not be saved.", "staff-niko-applications"); }
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
    setSavingGlobal(true); notifyLoading("Saving the bot profile…", "staff-global");
    try { await saveGlobalProfile(global, auth.csrf_token); notifySuccess("Niko's global profile was updated.", "staff-global"); }
    catch (reason) { notifyError(reason instanceof Error ? reason.message : "Could not update global profile.", "staff-global"); }
    finally { setSavingGlobal(false); }
  };

  const content = <div className="staff-page">
    <header className="staff-heading">
      <div><div className="eyebrow">Team operations</div><h1>Staff workspace.</h1><p>Manage your public staff profile, guild operations, blacklist appeals, team applications and bot health from one place — with live bot-wide analytics for planning the next rollout.</p></div>
      <div className="staff-role-card"><span className="staff-role-mark"><img src={signedInAvatar} alt="Your Discord profile" onError={(event) => { event.currentTarget.onerror = null; event.currentTarget.src = discordDefaultAvatar; }} /></span><span><small>Signed in as</small><strong>{staff.role_label}</strong></span></div>
    </header>

    <div className="staff-tabs" role="tablist" aria-label="Staff settings" onKeyDown={onTabKeyDown}>
      <button type="button" role="tab" id="staff-profile-tab" aria-selected={activeTab === "profile"} aria-controls="staff-profile-panel" className={activeTab === "profile" ? "active" : ""} onClick={() => setActiveTab("profile")}><Icon name="users" /> Public profile</button>
      <button type="button" role="tab" id="staff-analytics-tab" aria-selected={activeTab === "analytics"} aria-controls="staff-analytics-panel" className={activeTab === "analytics" ? "active" : ""} onClick={() => setActiveTab("analytics")}><Icon name="chart" /> Analytics</button>
      {canManageGlobal && <button type="button" role="tab" id="staff-global-tab" aria-selected={activeTab === "global"} aria-controls="staff-global-panel" className={activeTab === "global" ? "active" : ""} onClick={() => setActiveTab("global")}><Icon name="settings" /> Bot profile</button>}
      {canManageGuilds && <button type="button" role="tab" id="staff-guilds-tab" aria-selected={activeTab === "guilds"} aria-controls="staff-guilds-panel" className={activeTab === "guilds" ? "active" : ""} onClick={() => setActiveTab("guilds")}><Icon name="shield" /> Guild operations <span>{staffGuilds.length}</span></button>}
      {canManageGuilds && <button type="button" role="tab" id="staff-blacklist-tab" aria-selected={activeTab === "blacklist"} aria-controls="staff-blacklist-panel" className={activeTab === "blacklist" ? "active" : ""} onClick={() => setActiveTab("blacklist")}><Icon name="lock" /> Blacklist <span>{blacklistEntries.users.length + blacklistEntries.guilds.length}</span></button>}
      {canReviewAppeals && <button type="button" role="tab" id="staff-appeals-tab" aria-selected={activeTab === "appeals"} aria-controls="staff-appeals-panel" className={activeTab === "appeals" ? "active" : ""} onClick={() => setActiveTab("appeals")}><Icon name="message" /> Appeals <span>{appeals.filter((appeal) => appeal.status === "pending").length}</span></button>}
      {canManageProxyWorkers && <button type="button" role="tab" id="staff-proxy-workers-tab" aria-selected={activeTab === "proxy-workers"} aria-controls="staff-proxy-workers-panel" className={activeTab === "proxy-workers" ? "active" : ""} onClick={() => setActiveTab("proxy-workers")}><Icon name="chart" /> Discord proxy</button>}
      {canManageNikoApplications && <button type="button" role="tab" id="staff-team-recruitment-tab" aria-selected={activeTab === "team-recruitment"} aria-controls="staff-team-recruitment-panel" className={activeTab === "team-recruitment" ? "active" : ""} onClick={() => setActiveTab("team-recruitment")}><Icon name="users" /> Team Applications <span>{nikoApplications.reduce((count, application) => count + application.submission_count, 0)}</span></button>}
      {canManageStaffRoster && <button type="button" role="tab" id="staff-staff-management-tab" aria-selected={activeTab === "staff-management"} aria-controls="staff-staff-management-panel" className={activeTab === "staff-management" ? "active" : ""} onClick={() => setActiveTab("staff-management")}><Icon name="users" /> Staff management <span>{staffRoster.filter((member) => member.staff_status !== "former").length}</span></button>}
      {canManageStaffRoster && <button type="button" role="tab" id="staff-broadcasts-tab" aria-selected={activeTab === "broadcasts"} aria-controls="staff-broadcasts-panel" className={activeTab === "broadcasts" ? "active" : ""} onClick={() => setActiveTab("broadcasts")}><Icon name="message" /> Broadcasts</button>}
      {canManageDataRemoval && <button type="button" role="tab" id="staff-data-removal-tab" aria-selected={activeTab === "data-removal"} aria-controls="staff-data-removal-panel" className={activeTab === "data-removal" ? "active" : ""} onClick={() => setActiveTab("data-removal")}><Icon name="lock" /> Data removal <span>{dataRemoval?.filter((request) => request.status === "pending").length ?? 0}</span></button>}
      {canManageBilling && <button type="button" role="tab" id="staff-billing-tab" aria-selected={activeTab === "billing"} aria-controls="staff-billing-panel" className={activeTab === "billing" ? "active" : ""} onClick={() => setActiveTab("billing")}><Icon name="guild_economy" /> Billing <span>{billing?.payments.filter((payment) => payment.issue_status === "open").length ?? 0}</span></button>}
      <button type="button" role="tab" id="staff-reports-tab" aria-selected={activeTab === "reports"} aria-controls="staff-reports-panel" className={activeTab === "reports" ? "active" : ""} onClick={() => setActiveTab("reports")}><Icon name="alert" /> Error reports <span>{errorReports.length}</span></button>
    </div>

    {activeTab === "profile" && <section id="staff-profile-panel" role="tabpanel" aria-labelledby="staff-profile-tab"><div className="staff-layout">
      <section className="staff-panel staff-panel-main">
        <div className="staff-panel-heading"><div><span className="panel-kicker">Public listing</span><h2>How the team sees you</h2><p>Keep your introduction current while Discord remains the source of truth for your identity.</p></div><span className="staff-step">01</span></div>
        <div className="staff-fields">
          <label className="form-field"><span className="form-label">Banner URL</span><input type="url" value={form.public_banner_url} onChange={(e) => update("public_banner_url", e.target.value)} placeholder="https://…" /><small>Use a publicly reachable image. Leave blank for no banner.</small></label>
          <section className="staff-links-section" aria-labelledby="staff-links-heading">
            <div className="staff-links-heading"><div><span className="form-label" id="staff-links-heading">Links</span><small>Add up to 10 links. They appear on your profile, not the team overview card. GitHub, Bluesky, Twitch, YouTube, Reddit and X links become full profile cards.</small></div><span className="staff-links-count">{links.length}/10</span></div>
            <div className="staff-link-list">
              {links.map((link, index) => <div className="staff-link-row" key={`profile-link-${index}`}>
                <label className="form-field staff-link-type"><span className="sr-only">Link {index + 1} type</span><select value={link.type} onChange={(event) => updateLink(index, "type", event.target.value)}>
                  <option value="">Choose link type…</option>
                  {PUBLIC_LINK_TYPES.map(([value, label]) => <option value={value} key={value}>{label}</option>)}
                </select></label>
                <label className="form-field staff-link-url"><span className="sr-only">Link {index + 1} URL</span><input type="url" value={link.url} onChange={(event) => updateLink(index, "url", event.target.value)} placeholder="https://…" /></label>
                <button type="button" className="staff-link-remove" onClick={() => removeLink(index)} aria-label={`Remove link ${index + 1}`}>Remove</button>
              </div>)}
            </div>
            <button type="button" className="button button-muted staff-add-link" onClick={addLink} disabled={links.length >= 10}>＋ Add link</button>
          </section>
          <label className="form-field staff-bio-field"><span className="form-label">Extended introduction</span><textarea value={form.public_bio} onChange={(e) => update("public_bio", e.target.value)} maxLength={1200} placeholder="Tell the community what you do…" /><small>{form.public_bio.length}/1200 characters</small></label>
        </div>
        <SettingCards className="staff-visibility">
          <SettingCard
            title="Show me on the public Team page"
            hint="Hide your listing without removing your staff access."
            action={<Switch checked={form.public_visible} onCheckedChange={(value) => update("public_visible", value)} aria-label="Show me on the public Team page" />}
          />
        </SettingCards>
        <div className="staff-panel-footer"><span>Changes apply immediately to your public profile.</span><button type="button" className="button button-primary" onClick={save} disabled={saving}>{saving ? "Saving…" : "Save public listing"}</button></div>
      </section>

      <aside className="staff-sidebar-card staff-profile-sidebar">
        <section className="staff-profile-preview" aria-label="Live public profile preview">
          <div className="staff-profile-preview-banner">
            {form.public_banner_url && <img src={form.public_banner_url} alt="" onError={(event) => { event.currentTarget.style.visibility = "hidden"; }} />}
            <span>Public profile</span>
          </div>
          <div className="staff-profile-preview-body">
            <DiscordStatusAvatar status={staff.profile.status} className="staff-profile-preview-avatar" label={staff.profile.status_label || staff.profile.status || "Offline"}><img className="staff-profile-preview-avatar" src={signedInAvatar} alt="" /></DiscordStatusAvatar>
            <div className="staff-profile-preview-identity"><strong>{signedInUser.global_name || signedInUser.username || staff.profile.name}</strong><span>{staff.role_label}</span></div>
            <p className={form.public_bio.trim() ? "" : "is-placeholder"}>{form.public_bio.trim() || "Your introduction will appear here."}</p>
            {links.some((link) => link.type.trim() && link.url.trim()) && <div className="staff-profile-preview-links">{links.filter((link) => link.type.trim() && link.url.trim()).map((link, index) => <span key={`${link.type}-${index}`}>{link.label || PUBLIC_LINK_TYPES.find(([value]) => value === link.type)?.[1] || link.type}</span>)}</div>}
            <div className={`staff-profile-preview-visibility${form.public_visible ? " is-visible" : ""}`}><i />{form.public_visible ? "Visible on Team page" : "Hidden from Team page"}</div>
          </div>
        </section>
        <div className="staff-profile-rules"><span className="panel-kicker">Profile rules</span><h3>Stay consistent with Discord</h3><p>Your global display name and profile picture sync automatically, so updates made in Discord are reflected here without another form.</p><div className="staff-rule"><span>Identity</span><strong>Discord synced</strong></div><div className="staff-rule"><span>Editable</span><strong>Bio · banner · links · GitHub card · visibility</strong></div></div>
      </aside>
    </div>
    <details className="staff-card-section">
      <summary>
        <span className="staff-card-section-copy">
          <span className="panel-kicker">GitHub README</span>
          <strong>Add your staff card to GitHub</strong>
          <small>A live SVG card with your Discord status and Niko staff role. Expand it to preview the card and copy the markdown.</small>
        </span>
        <span className="staff-card-section-hint">Card settings</span>
      </summary>
      <div className="staff-card-body">
        <div className="staff-card-preview-block">
          <img className="staff-card-preview" src={cardPreviewUrl} alt={`Niko staff card preview for ${staff.profile.name}`} />
          <span className="staff-card-preview-caption">Live preview, refreshed every 30 seconds · GitHub re-fetches the card instead of caching an old status. The card follows your Team page visibility.</span>
        </div>
        <div className="staff-card-controls">
          <div className="staff-card-fields">
            <label className="form-field"><span className="form-label">Card theme</span><select value={form.card_theme} onChange={(event) => update("card_theme", event.target.value)}><option value="dark">Dark</option><option value="light">Light</option></select></label>
            <div className="form-field"><span className="form-label">Accent color</span><ColorPicker label="Staff card accent color" value={form.card_accent} onChange={(hex) => update("card_accent", hex)} /></div>
          </div>
          <SettingCards>
            <SettingCard
              title="Show my live Discord status"
              hint="Turn this off to keep only your name and staff role on the card."
              action={<Switch checked={form.card_show_status} onCheckedChange={(value) => update("card_show_status", value)} aria-label="Show my live Discord status on the card" />}
            />
          </SettingCards>
          <div className="staff-card-markdown">
            <span className="form-label">Markdown for your README</span>
            <div className="staff-card-snippet">
              <input readOnly value={cardMarkdown} aria-label="Markdown snippet for your GitHub README" onFocus={(event) => event.currentTarget.select()} />
              <button type="button" className="button button-muted" onClick={() => void copyCardMarkdown()}>Copy markdown</button>
            </div>
            <small className="form-hint">Clicking the card on GitHub opens your staff profile.</small>
          </div>
          <div className="staff-panel-footer staff-card-footer">
            <span>Card settings save on their own — your public listing and README snippet stay untouched.</span>
            <button type="button" className="button button-primary" onClick={saveCard} disabled={savingCard}>{savingCard ? "Saving…" : "Save card settings"}</button>
          </div>
        </div>
      </div>
    </details>
    </section>}

    {activeTab === "analytics" && <section id="staff-analytics-panel" role="tabpanel" aria-labelledby="staff-analytics-tab" className="staff-guild-operations"><BotAnalyticsView /></section>}
    {activeTab === "global" && canManageGlobal && <section id="staff-global-panel" role="tabpanel" aria-labelledby="staff-global-tab" className="staff-panel staff-global-panel"><div className="staff-panel-heading"><div><span className="panel-kicker">Graphic direction</span><h2>Global Niko profile</h2><p>Reserved for Graphic Designers, Head Admins, and owners. Paste publicly reachable image URLs.</p></div><span className="staff-step">02</span></div><div className="staff-fields staff-fields-two"><label className="form-field"><span className="form-label">Bot avatar URL</span><input value={global.avatar_url} onChange={(e) => setGlobal({ ...global, avatar_url: e.target.value })} placeholder="https://…" /></label><label className="form-field"><span className="form-label">Bot banner URL</span><input value={global.banner_url} onChange={(e) => setGlobal({ ...global, banner_url: e.target.value })} placeholder="https://…" /></label></div><div className="staff-panel-footer"><span>Updates the bot-wide Discord profile.</span><button type="button" className="button button-primary" onClick={saveGlobal} disabled={savingGlobal}>{savingGlobal ? "Updating…" : "Update global profile"}</button></div></section>}
    {activeTab === "guilds" && canManageGuilds && <section id="staff-guilds-panel" role="tabpanel" aria-labelledby="staff-guilds-tab" className="staff-guild-operations">
      <header className="staff-guilds-heading"><div><span className="panel-kicker">Bot operations</span><h2>Guild directory</h2><p>Review every server Niko currently serves. Select a guild to inspect its owner, activity footprint, live server profile and operational controls.</p></div><div className="staff-guild-count"><strong>{staffGuilds.length}</strong><span>connected guilds</span></div></header>
      <div className="staff-guild-toolbar"><label className="staff-guild-search"><Icon name="search" /><input type="search" value={guildSearch} onChange={(event) => setGuildSearch(event.target.value)} placeholder="Search guilds, owners, or IDs" aria-label="Search guilds" /></label><button type="button" className="button button-muted" onClick={refreshStaffGuilds} disabled={staffGuildsLoading}><Icon name="spark" />{staffGuildsLoading ? "Refreshing…" : "Refresh guilds"}</button></div>
      {staffGuildsLoading && staffGuilds.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading the live guild directory…</p></div> : filteredGuilds.length === 0 ? <div className="staff-guild-empty"><span>{staffGuilds.length ? "No guilds match that search." : "The bot is not connected to any guilds."}</span></div> : <div className="staff-guild-list">
        {filteredGuilds.map((guild) => {
          const expanded = expandedGuildId === guild.id;
          return <article className={`staff-guild-card${expanded ? " expanded" : ""}`} key={guild.id}>
            <button type="button" className="staff-guild-row" aria-expanded={expanded} onClick={() => setExpandedGuildId(expanded ? null : guild.id)}>
              <span className="staff-guild-icon">{guild.icon_url ? <img src={guild.icon_url} alt="" /> : <b>{guild.name.slice(0, 1).toUpperCase()}</b>}</span>
              <span className="staff-guild-title"><strong>{guild.name}</strong><small>{guild.id} · {guild.member_count.toLocaleString()} members</small></span>
              <span className={`staff-guild-status${guild.blacklisted ? " is-blocked" : ""}`}><i />{guild.blacklisted ? "Blacklisted" : "Active"}</span>
              <Icon name={expanded ? "close" : "arrow"} className="staff-guild-chevron" />
            </button>
            {expanded && <div className="staff-guild-details">
              <div className="staff-guild-summary"><div><span className="panel-kicker">Guild owner</span><DiscordMarkdown text={`<@${guild.owner_id || "0"}>`} mentionNames={{ user: guild.owner_id ? { [guild.owner_id]: guild.owner_name } : {} }} className="staff-guild-owner" /></div><div><span className="panel-kicker">Created</span><strong>{guild.created_at ? new Date(guild.created_at).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" }) : "Unknown"}</strong></div><div><span className="panel-kicker">Channels</span><strong>{guild.channel_count.toLocaleString()} · {guild.category_count} categories</strong></div><div><span className="panel-kicker">Profile name</span><strong>{guild.profile_name || "Niko"}</strong></div><div><span className="panel-kicker">Roles</span><strong>{guild.role_count}</strong></div></div>
              <div className="staff-guild-profile-previews"><div className="staff-guild-preview"><span className="panel-kicker">Guild avatar</span>{guild.bot_avatar_url ? <img src={guild.bot_avatar_url} alt={`${guild.name} bot avatar`} /> : <div className="staff-guild-no-image">No server avatar</div>}</div><div className="staff-guild-preview staff-guild-preview-banner"><span className="panel-kicker">Guild banner</span>{guild.bot_banner_url ? <img src={guild.bot_banner_url} alt={`${guild.name} bot banner`} /> : <div className="staff-guild-no-image">No server banner</div>}</div></div>
              <div className="staff-guild-action-panel"><div className="staff-guild-action-heading"><div><span className="panel-kicker">Quick actions</span><h3>Operations for {guild.name}</h3></div><span className="staff-guild-id">ID · {guild.id}</span></div>
                <div className="staff-guild-actions"><button type="button" className="button button-muted" disabled={busyGuildAction} onClick={() => { setInviteUrl(""); setInviteGuildId(guild.id); notifyLoading("Creating a temporary invite…", "staff-guild-invite"); void createStaffGuildInvite(guild.id, auth.csrf_token).then((result) => { setInviteUrl(result.url); clearToasts("staff-guild-invite"); }).catch((reason) => notifyError(reason instanceof Error ? reason.message : "Could not create an invite.", "staff-guild-invite")); }}><Icon name="link" />Temporary invite</button><button type="button" className="button button-muted" onClick={() => setPermissionGuild(guild)}><Icon name="shield" />Permissions</button><button type="button" className="button button-danger" disabled={busyGuildAction} onClick={() => { if (window.confirm(`Make Niko leave ${guild.name}? This removes the bot from the server.`)) void saveGuildAction(() => leaveStaffGuild(guild.id, auth.csrf_token), `Niko left ${guild.name}.`); }}>Leave guild</button><label className="form-field staff-guild-reason"><span className="form-label">Blacklist reason</span><input value={guildBlacklistReason} onChange={(event) => setGuildBlacklistReason(event.target.value)} maxLength={1000} placeholder="Required when blacklisting" /></label><button type="button" className={`button ${guild.blacklisted ? "button-muted" : "button-danger"}`} disabled={busyGuildAction || (!guild.blacklisted && !guildBlacklistReason.trim())} onClick={() => guild.blacklisted ? void saveGuildAction(() => setStaffGuildBlacklist(guild.id, "remove", guildBlacklistReason, auth.csrf_token), `${guild.name} removed from the blacklist.`) : void blacklistGuild(guild.id, guild.name, guildBlacklistReason)}>{busyGuildAction ? "Working…" : guild.blacklisted ? "Remove blacklist" : "Blacklist guild"}</button><button type="button" className="button button-muted" disabled={busyGuildAction} onClick={() => { if (window.confirm(`Reset Niko’s server profile for ${guild.name}? This clears the customized name, bio, font, colors, avatar, and banner.`)) void saveGuildAction(() => resetStaffGuildProfile(guild.id, auth.csrf_token), `${guild.name} profile reset.`); }}><Icon name="settings" />Reset profile</button></div>
                <label className="form-field staff-guild-notice-field"><span className="form-label">Formal moderation notice</span><textarea rows={4} maxLength={1500} value={noticeMessage} onChange={(event) => setNoticeMessage(event.target.value)} placeholder="Describe the moderation concern and any action required…" /><small>{noticeMessage.length}/1500 · delivered as an official Components v2 notice directly to the server owner</small></label><button type="button" className="button button-primary" disabled={busyGuildAction || !noticeMessage.trim()} onClick={() => { if (window.confirm(`Send this formal moderation notice to ${guild.owner_name}, the owner of ${guild.name}?`)) void saveGuildAction(() => sendStaffGuildNotice(guild.id, noticeMessage, auth.csrf_token), `Moderation notice sent to ${guild.owner_name}.`); }}><Icon name="message" />Send formal notice</button>
                {inviteUrl && inviteGuildId === guild.id && <div className="staff-guild-invite-result" role="status"><span>One-use invite · expires in 10 minutes</span><a href={inviteUrl} target="_blank" rel="noreferrer">{inviteUrl}</a><button type="button" className="button button-muted button-small" onClick={() => navigator.clipboard?.writeText(inviteUrl)}>Copy invite</button></div>}
                {guild.blacklisted && <p className="staff-guild-blacklist-note"><strong>Blacklist reason:</strong> {guild.blacklist_reason || "No reason recorded."}</p>}
              </div>
            </div>}
          </article>;
        })}
      </div>}
    </section>}
    {activeTab === "appeals" && canReviewAppeals && <section id="staff-appeals-panel" role="tabpanel" aria-labelledby="staff-appeals-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Trust &amp; safety</span><h2>Blacklist appeals</h2><p>Review requests privately. Approval removes the active restriction while preserving its appealed history; denied appeals cannot be resubmitted.</p></div><div className="staff-guild-count"><strong>{appeals.filter((appeal) => appeal.status === "pending").length}</strong><span>pending review</span></div></header><div className="staff-guild-toolbar"><span className="staff-appeal-privacy">Visible to the bot owner and Head Admins</span><button type="button" className="button button-muted" onClick={() => void loadAppeals()} disabled={appealsLoading}><Icon name="spark" />{appealsLoading ? "Refreshing…" : "Refresh appeals"}</button></div>{appealsLoading && appeals.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading appeals…</p></div> : appeals.length === 0 ? <div className="staff-guild-empty">No blacklist appeals have been submitted.</div> : <div className="staff-guild-list">{appeals.map((appeal) => <article className={`staff-guild-card staff-appeal-card staff-appeal-${appeal.status}`} key={appeal.appeal_id}><div className="staff-appeal-header"><div className="staff-appeal-identity"><span className="panel-kicker">{appeal.guild_id ? "Guild appeal" : "User appeal"}</span><strong>{appeal.guild_id ? `Guild ${appeal.guild_id}` : appeal.username || "Discord user"}</strong><small>{appeal.guild_id ? `Submitted by user ${appeal.user_id}` : `Discord ID · ${appeal.user_id}`} <span aria-hidden="true">·</span> {new Date(appeal.created_at * 1000).toLocaleString()}</small></div><span className={`staff-guild-status${appeal.status === "denied" ? " is-blocked" : appeal.status === "pending" ? " is-pending" : " is-approved"}`}><i />{appeal.status}</span></div><div className="staff-appeal-reason staff-appeal-context"><span className="panel-kicker">Blacklist reason</span><p>{appeal.blacklist_reason || "No reason recorded."}</p></div><div className="staff-appeal-reason staff-appeal-message"><span className="panel-kicker">Appeal statement</span><p>{appeal.appeal_text}</p></div>{appeal.status === "pending" ? <><label className="form-field"><span className="form-label">Staff note {"(optional)"}</span><textarea rows={3} maxLength={2000} value={appealNotes[appeal.appeal_id] || ""} onChange={(event) => setAppealNotes((current) => ({ ...current, [appeal.appeal_id]: event.target.value }))} placeholder="Add context for the decision; the user can see this note…" /><small>{(appealNotes[appeal.appeal_id] || "").length}/2000 · shown to the user with the decision</small></label><div className="staff-appeal-actions"><button type="button" className="button button-muted" disabled={reviewingAppealId !== null} onClick={() => void reviewAppeal(appeal, "denied")}>{reviewingAppealId === appeal.appeal_id ? "Saving…" : "Deny appeal"}</button><button type="button" className="button button-primary" disabled={reviewingAppealId !== null} onClick={() => void reviewAppeal(appeal, "approved")}>{reviewingAppealId === appeal.appeal_id ? "Saving…" : "Approve appeal"}</button></div></> : <><div className="staff-appeal-reason staff-appeal-note"><span className="panel-kicker">Staff decision note</span><p>{appeal.staff_note || "No note added."}</p></div><small className="staff-appeal-reviewed">{appeal.status === "approved" ? "Approved" : "Denied"}{appeal.reviewed_at ? ` ${new Date(appeal.reviewed_at * 1000).toLocaleString()}` : ""} <span aria-hidden="true">·</span> Staff ID {appeal.reviewed_by || "unknown"}</small></>}</article>)}</div>}</section>}
    {activeTab === "proxy-workers" && canManageProxyWorkers && <section id="staff-proxy-workers-panel" role="tabpanel" aria-labelledby="staff-proxy-workers-tab" className="staff-guild-operations"><ProxyWorkersView csrfToken={auth.csrf_token} /></section>}
    {activeTab === "staff-management" && canManageStaffRoster && <section id="staff-staff-management-panel" role="tabpanel" aria-labelledby="staff-staff-management-tab" className="staff-guild-operations">
      <header className="staff-guilds-heading"><div><span className="panel-kicker">Owner-only · access control</span><h2>Staff management</h2><p>View the full staff roster, assign or change roles, and suspend access during investigations. Suspension preserves the stored role and the member's public profile but removes every official Discord staff role and blocks staff commands and website pages until you lift it.</p></div><div className="staff-guild-count"><strong>{staffRoster.filter((member) => member.staff_status !== "former").length}</strong><span>{staffRoster.filter((member) => member.staff_status === "suspended").length} suspended · {staffRoster.filter((member) => member.staff_status === "former").length} former</span></div></header>
      <div className="staff-guild-toolbar"><label className="staff-guild-search"><Icon name="search" /><input type="search" value={staffRosterSearch} onChange={(event) => setStaffRosterSearch(event.target.value)} placeholder="Search staff by name, role, or ID" aria-label="Search staff roster" /></label><button type="button" className="button button-muted" onClick={() => void refreshStaffRoster()} disabled={staffRosterLoading}><Icon name="spark" />{staffRosterLoading ? "Refreshing…" : "Refresh roster"}</button></div>
      <div className="staff-roster-form"><input value={newStaffId} onChange={(event) => setNewStaffId(event.target.value)} inputMode="numeric" maxLength={22} pattern="[0-9]{1,22}" placeholder="Discord user ID" aria-label="New staff Discord user ID" /><select value={newStaffRole} onChange={(event) => setNewStaffRole(event.target.value)} aria-label="New staff role"><option value="">Choose staff role…</option>{staffRosterRoles.map((role) => <option value={role.key} key={role.key}>{role.label}</option>)}</select><button type="button" className="button button-primary" disabled={staffRosterBusy || !newStaffId.trim() || !newStaffRole} onClick={() => void addStaffRole()}>Add staff role</button></div>
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
              <div className="staff-guild-actions"><label className="form-field staff-guild-reason"><span className="form-label">Staff role</span><select value={selectedRole} onChange={(event) => setStaffRosterRoleDrafts((current) => ({ ...current, [member.id]: event.target.value }))} disabled={staffRosterBusy}>{staffRosterRoles.map((role) => <option value={role.key} key={role.key}>{role.label}</option>)}</select></label><button type="button" className="button button-primary" disabled={staffRosterBusy || !selectedRole} onClick={() => void saveStaffRole(member)}>{status === "former" ? "Assign & reinstate" : "Save role"}</button>{status === "suspended" && <button type="button" className="button button-primary" disabled={staffRosterBusy} onClick={() => void liftStaffSuspension(member)}>Lift suspension</button>}{status === "active" && <button type="button" className="button button-muted" disabled={staffRosterBusy} onClick={() => void suspendStaffMember(member)}>Suspend</button>}{status !== "former" && <button type="button" className="button button-danger" disabled={staffRosterBusy} onClick={() => void demoteStaffMember(member)}>Demote</button>}</div>
              <p className="staff-guild-blacklist-note">{status === "suspended" ? "The stored role and public profile stay saved. Lift the suspension to restore Discord and website access without a new appointment." : status === "former" ? "The public profile remains saved but hidden. Assigning a new role restores it; a data removal request deletes the profile data." : "Suspending interrupts access without demoting. Demoting keeps the public profile saved but hidden for a future return."}</p>
            </div>}
          </div>
        </article>;
      })}</div>}
    </section>}
    {activeTab === "broadcasts" && canManageStaffRoster && <section id="staff-broadcasts-panel" role="tabpanel" aria-labelledby="staff-broadcasts-tab" className="staff-guild-operations"><BroadcastStudioView csrfToken={auth.csrf_token} /></section>}
    {activeTab === "team-recruitment" && canManageNikoApplications && <section id="staff-team-recruitment-panel" role="tabpanel" aria-labelledby="staff-team-recruitment-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Owner-only · official team applications</span><h2>Team Applications</h2><p>Manage fixed role openings and review every submission from one queue. Role questions and role links are managed in code.</p></div><div className="staff-guild-count"><strong>{nikoSubmissions.length}</strong><span>submitted applications</span></div></header><div className="staff-guild-toolbar"><span className="staff-appeal-privacy">{nikoSubmissions.filter((submission) => submission.review_status === "pending").length} pending · {nikoSubmissions.filter((submission) => submission.review_status !== "pending").length} reviewed</span><button type="button" className="button button-muted" onClick={() => void refreshNikoApplications()} disabled={nikoBusy}><Icon name="spark" />{nikoBusy ? "Refreshing…" : "Refresh"}</button></div><section className="team-recruitment-openings"><div className="team-recruitment-list-heading"><div><span className="panel-kicker">Opening controls</span><h3>Role openings</h3></div><span>{nikoApplications.length} fixed roles</span></div><div className="staff-guild-list">{nikoApplications.map((application) => <article className="staff-guild-card" key={application.id}><div className="staff-guild-row"><span className="staff-guild-icon"><Icon name="users" /></span><span className="staff-guild-title"><strong>{application.title} · {application.role_name || "Role"}</strong><small>{application.submission_count} {application.submission_count === 1 ? "submission" : "submissions"} · {application.status === "open" ? "Accepting applications" : "Closed"} · /team/apply/{application.id}</small></span><button type="button" className="button button-muted button-small" onClick={() => void toggleNikoOpening(application)} disabled={nikoBusy}>{application.status === "open" ? "Close" : "Reopen"}</button></div></article>)}{nikoApplications.length === 0 && <div className="staff-guild-empty">Fixed role applications will appear here when available.</div>}</div></section><section className="team-recruitment-submissions"><div className="team-recruitment-list-heading"><div><span className="panel-kicker">Review queue</span><h3>Submitted applications</h3></div><span>{nikoSubmissions.length} total</span></div>{nikoBusy && nikoSubmissions.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading submitted applications…</p></div> : nikoSubmissions.length === 0 ? <div className="staff-guild-empty">No submitted applications yet.</div> : <><div className="team-recruitment-status-group"><div className="team-recruitment-status-heading"><h4>Pending review</h4><span>{nikoSubmissions.filter((submission) => submission.review_status === "pending").length}</span></div>{nikoSubmissions.filter((submission) => submission.review_status === "pending").length === 0 ? <p className="team-recruitment-empty-group">You’re all caught up. New submissions will appear here.</p> : <div className="team-recruitment-review-list">{nikoSubmissions.filter((submission) => submission.review_status === "pending").map((submission) => <article className="team-recruitment-review-entry" key={`${submission.opening_id}-${submission.user_id}`}><header className="team-recruitment-submission-heading"><div><strong>{submission.display_name}</strong><small>Discord ID · {submission.user_id}{submission.submitted_at ? ` · ${new Date(submission.submitted_at).toLocaleString()}` : ""}</small></div><span className="team-recruitment-opening-tag">{submission.opening_title} · {submission.role_name || "Role"}</span></header><div className="team-recruitment-answers">{submission.answers.map((answer) => <div key={answer.question_id}><strong>{answer.prompt}</strong><p>{Array.isArray(answer.answer) ? answer.answer.join(", ") || "No answer provided." : answer.answer || "No answer provided."}</p></div>)}</div><footer className="team-recruitment-review-actions"><button type="button" className="button button-muted button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "denied")}>Decline</button><button type="button" className="button button-primary button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "approved")}>Approve</button></footer></article>)}</div>}</div><div className="team-recruitment-status-group is-reviewed"><div className="team-recruitment-status-heading"><h4>Reviewed</h4><span>{nikoSubmissions.filter((submission) => submission.review_status !== "pending").length}</span></div>{nikoSubmissions.filter((submission) => submission.review_status !== "pending").length === 0 ? <p className="team-recruitment-empty-group">Reviewed applications will be kept here for reference.</p> : <div className="team-recruitment-review-list">{nikoSubmissions.filter((submission) => submission.review_status !== "pending").map((submission) => <article className="team-recruitment-review-entry" key={`${submission.opening_id}-${submission.user_id}`}><header className="team-recruitment-submission-heading"><div><strong>{submission.display_name}</strong><small>Discord ID · {submission.user_id}{submission.submitted_at ? ` · Submitted ${new Date(submission.submitted_at).toLocaleString()}` : ""}</small></div><span className={`team-recruitment-decision ${submission.review_status}`}>{submission.review_status === "approved" ? "Approved" : "Declined"}</span></header><div className="team-recruitment-opening-tag">{submission.opening_title} · {submission.role_name || "Role"}</div><div className="team-recruitment-answers">{submission.answers.map((answer) => <div key={answer.question_id}><strong>{answer.prompt}</strong><p>{Array.isArray(answer.answer) ? answer.answer.join(", ") || "No answer provided." : answer.answer || "No answer provided."}</p></div>)}</div><small className="team-recruitment-review-meta">{submission.reviewed_at ? `Reviewed ${new Date(submission.reviewed_at).toLocaleString()}` : "Decision recorded"}{submission.reviewed_by ? ` · Staff ID ${submission.reviewed_by}` : ""}</small><footer className="team-recruitment-review-actions">{submission.review_status === "approved" ? <button type="button" className="button button-muted button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "denied")}>Revoke approval</button> : <button type="button" className="button button-primary button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "approved")}>Approve instead</button>}</footer></article>)}</div>}</div></>}</section></section>}
    {activeTab === "billing" && canManageBilling && <section id="staff-billing-panel" role="tabpanel" aria-labelledby="staff-billing-tab" className="staff-guild-operations">
      <header className="staff-guilds-heading"><div><span className="panel-kicker">Revenue</span><h2>Billing &amp; subscriptions</h2><p>Recent white-label payments, active premium servers, and the billing notes needed to resolve an issue. Only the bot owner can open this tab.</p></div><div className="staff-guild-count"><strong>{billing?.totals.paid_label || "$0.00 USD"}</strong><span>collected</span></div></header>
      <div className="staff-guild-toolbar"><span className="staff-appeal-privacy">{billing?.gateway.configured ? "OxaPay connected · fal.ai imageutils/nsfw" : "OxaPay merchant key is missing"}</span><button type="button" className="button button-muted" onClick={() => void refreshBilling()}><Icon name="spark" />Refresh billing</button></div>
      {!billing ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading billing data…</p></div> : <>          <div className="staff-guild-summary"><div><span className="panel-kicker">Active servers</span><strong>{billing.totals.active_count}</strong></div><div><span className="panel-kicker">Expiring soon</span><strong>{billing.totals.expiring_soon}</strong></div><div><span className="panel-kicker">Paid payments</span><strong>{billing.totals.paid_count}</strong></div><div><span className="panel-kicker">Needs attention</span><strong>{billing.payments.filter((payment) => payment.issue_status === "open").length}</strong></div><div><span className="panel-kicker">Awaiting payment</span><strong>{billing.payments.filter((payment) => !payment.paid && !payment.issue_status).length}</strong></div></div>
        <div className="staff-billing-grant">
          <label className="form-field"><span className="form-label">Guild ID</span><input value={billingGuild} onChange={(event) => setBillingGuild(event.target.value)} placeholder="123456789012345678" /></label>
          <label className="form-field"><span className="form-label">Months</span><input type="number" min="1" max="12" value={billingMonths} onChange={(event) => setBillingMonths(event.target.value)} /></label>
          <button type="button" className="button button-primary" disabled={billingBusy || !billingGuild.trim()} onClick={() => void changeBillingSubscription(billingGuild, "grant")}>Grant / extend</button>
          <button type="button" className="button button-muted" disabled={billingBusy || !billingGuild.trim()} onClick={() => void changeBillingSubscription(billingGuild, "cancel")}>Cancel</button>
        </div>
        <h3 className="staff-billing-heading">Recent payments</h3>
        {billing.payments.length === 0 ? <div className="staff-guild-empty">No premium payments have been started yet.</div> : <div className="staff-guild-list">{billing.payments.map((payment) => {
          const state = billingPaymentState(payment);
          const note = billingNoteFor(payment);
          const savedNote = payment.issue_note ?? "";
          return <article className={`staff-guild-card staff-billing-payment ${state.className}`} key={payment.order_id}>
            <div className="staff-billing-payment-head"><div className="staff-guild-title"><strong>{payment.guild_name || `Guild ${payment.guild_id}`} · {payment.amount_label}</strong><small>{payment.kind} · {payment.pay_currency || payment.currency} · {payment.payer_name || `User ${payment.payer_id}`} · {payment.created_at ? new Date(payment.created_at.replace(" ", "T") + "Z").toLocaleString() : "unknown time"}</small></div><span className={`staff-guild-status ${state.className}`}><i />{state.label}</span></div>
            <div className="staff-billing-payment-foot"><code>{payment.order_id}</code><span className={`staff-billing-payment-paid${payment.paid ? " is-paid" : ""}`}>{payment.paid ? "Crypto received" : `Provider status · ${payment.status}`}</span></div>
            <div className="staff-billing-payment-note"><label className="form-field staff-billing-note"><span className="form-label">Billing note</span><input maxLength={1000} value={note} onChange={(event) => setBillingNotes((current) => ({ ...current, [payment.order_id]: event.target.value }))} placeholder="What was checked, agreed, or refunded…" /></label><button type="button" className="button button-muted button-small" disabled={billingBusy || note === savedNote} onClick={() => void saveBillingNote(payment)}>Save note</button></div>
            <div className="staff-billing-payment-actions">
              {payment.issue_status ? <button type="button" className="button button-muted button-small" disabled={billingBusy} onClick={() => void resolveBilling(payment.order_id, "clear")}>{payment.issue_status === "resolved" ? "Undo resolve" : "Clear flag"}</button> : <button type="button" className="button button-muted button-small" disabled={billingBusy} onClick={() => void resolveBilling(payment.order_id, "open")}>Flag for follow-up</button>}
              {payment.issue_status !== "resolved" && <button type="button" className="button button-primary button-small" disabled={billingBusy} onClick={() => void resolveBilling(payment.order_id, "resolved")}>Mark resolved</button>}
            </div>
            {payment.issue_status && payment.resolved_at && <p className="staff-guild-blacklist-note">{payment.issue_status === "resolved" ? "Resolved" : "Flagged"} {new Date(payment.resolved_at.replace(" ", "T") + "Z").toLocaleString()} by staff {payment.resolved_by || "unknown"}.</p>}
          </article>;
        })}</div>}
        <h3 className="staff-billing-heading">Subscriptions</h3>
        {billing.subscriptions.length === 0 ? <div className="staff-guild-empty">No premium subscriptions yet.</div> : <div className="staff-guild-list">{billing.subscriptions.map((subscription) => <article className="staff-guild-card staff-billing-subscription" key={subscription.guild_id}>
          <div className="staff-billing-payment-head"><div className="staff-guild-title"><strong>{subscription.guild_name || `Guild ${subscription.guild_id}`}</strong><small>{subscription.active ? `Active · ${subscription.days_remaining ?? 0} days left` : subscription.status} · {subscription.source}{subscription.gifted_by_name ? ` by ${subscription.gifted_by_name}` : ""}</small></div><span className={`staff-guild-status${subscription.active ? " is-approved" : " is-blocked"}`}><i />{subscription.active ? "active" : subscription.status}</span></div>
          <div className="staff-billing-payment-foot"><code>{subscription.guild_id}</code><span className="staff-appeal-privacy">Ends {subscription.expires_at || "unknown"}</span><button type="button" className="button button-muted button-small" disabled={billingBusy} onClick={() => void changeBillingSubscription(subscription.guild_id || "", "cancel")}>Cancel subscription</button></div>
        </article>)}</div>}
      </>}
    </section>}
    {activeTab === "data-removal" && canManageDataRemoval && <section id="staff-data-removal-panel" role="tabpanel" aria-labelledby="staff-data-removal-tab" className="staff-guild-operations">
      <header className="staff-guilds-heading"><div><span className="panel-kicker">Privacy · owner only</span><h2>Data removal requests</h2><p>Verify each request, then approve or deny it. Approval runs the scoped deletion in <code>utils/data_removal.py</code>; moderation and safety records are never touched. Legal requests that must include a retained record are handled directly through the owner contact site, not this queue.</p></div><div className="staff-guild-count"><strong>{dataRemoval?.filter((request) => request.status === "pending").length ?? 0}</strong><span>pending</span></div></header>
      <div className="staff-guild-toolbar"><span className="staff-appeal-privacy">Visible only to the bot owner · identities are never shared with other staff tabs</span><button type="button" className="button button-muted" onClick={() => void refreshDataRemoval()}><Icon name="spark" />Refresh requests</button></div>
      {!dataRemoval ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading removal requests…</p></div> : dataRemoval.length === 0 ? <div className="staff-guild-empty">No data removal requests have been submitted.</div> : <div className="staff-guild-list">{dataRemoval.map((request) => <article className="staff-guild-card" key={request.id}>
        <div className="staff-guild-row"><span className="staff-guild-icon"><Icon name={request.scope === "account" ? "users" : "shield"} /></span><span className="staff-guild-title"><strong>{request.scope === "account" ? `Account · user ${request.user_id}` : request.guild_name || `Server ${request.guild_id}`}</strong><small>{new Date(request.created_at * 1000).toLocaleString()} · request {request.id.slice(0, 8)}{request.guild_id ? ` · guild ${request.guild_id}` : ""}</small></span><span className={`staff-guild-status${request.status === "completed" ? " is-approved" : request.status === "denied" || request.status === "withdrawn" ? " is-blocked" : " is-pending"}`}><i />{request.status}</span></div>
        <div className="staff-appeal-reason"><span className="panel-kicker">Member explanation</span><p>{request.reason || "No explanation provided."}</p></div>
        {request.review_note && <div className="staff-appeal-reason"><span className="panel-kicker">Owner note</span><p>{request.review_note}</p></div>}
        {request.result && <div className="staff-appeal-reason"><span className="panel-kicker">Deletion result</span><p>{request.result.removed?.length ?? 0} tables cleared{request.result.anonymized?.length ? ` · ${request.result.anonymized.length} anonymized` : ""}. {request.result.preserved?.join("; ") || "Safety records preserved."}{request.result.errors?.length ? ` · ${request.result.errors.length} backend warning(s)` : ""}</p></div>}
        {request.status === "pending" && <><label className="form-field"><span className="form-label">Owner note {"(required to deny)"}</span><textarea rows={3} maxLength={2000} value={dataRemovalNotes[request.id] || ""} onChange={(event) => setDataRemovalNotes((current) => ({ ...current, [request.id]: event.target.value }))} placeholder="Context for the decision; the member sees this note…" /></label><div className="staff-appeal-actions"><button type="button" className="button button-muted" disabled={dataRemovalBusy} onClick={() => void reviewDataRemoval(request, "denied")}>Deny</button><button type="button" className="button button-primary" disabled={dataRemovalBusy} onClick={() => void reviewDataRemoval(request, "approved")}>{dataRemovalBusy ? "Working…" : "Approve & delete"}</button></div></>}
      </article>)}</div>}
    </section>}
    {activeTab === "reports" && <section id="staff-reports-panel" role="tabpanel" aria-labelledby="staff-reports-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Diagnostics</span><h2>Bot error reports</h2><p>Recent command and runtime failures collected by Niko. Expand a report to inspect its details and traceback; use the code to retrieve it with <code>.staff getreport CODE</code>.</p></div><div className="staff-guild-count"><strong>{errorReports.length}</strong><span>recent reports</span></div></header><div className="staff-guild-toolbar"><label className="staff-guild-search"><Icon name="search" /><input type="search" value={reportSearch} onChange={(event) => setReportSearch(event.target.value)} placeholder="Search report code, exception, or details" aria-label="Search error reports" /></label><button type="button" className="button button-muted" onClick={() => void refreshErrorReports()} disabled={reportsLoading}><Icon name="spark" />{reportsLoading ? "Refreshing…" : "Refresh reports"}</button></div>{reportsLoading && errorReports.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading recent error reports…</p></div> : errorReports.filter((item) => `${item.code} ${item.report}`.toLocaleLowerCase().includes(reportSearch.trim().toLocaleLowerCase())).length === 0 ? <div className="staff-guild-empty">{errorReports.length ? "No reports match that search." : "No bot error reports have been saved."}</div> : <div className="staff-guild-list">{errorReports.filter((item) => `${item.code} ${item.report}`.toLocaleLowerCase().includes(reportSearch.trim().toLocaleLowerCase())).map((item) => { const lines = item.report.split("\n"); const exceptionIndex = lines.findIndex((line) => line === "Exception"); const exception = lines.slice(exceptionIndex + 2).find((line) => line.startsWith("Type:") || line.startsWith("Message:")) || "Unknown exception"; const detailsIndex = lines.findIndex((line) => line === "Occurred (UTC):"); const summary = lines.slice(detailsIndex + 2).find((line) => line.trim()) || "No report details"; const expanded = expandedReportCode === item.code; return <article className={`staff-guild-card${expanded ? " expanded" : ""}`} key={item.code}><button type="button" className="staff-guild-row staff-report-row" aria-expanded={expanded} onClick={() => setExpandedReportCode(expanded ? null : item.code)}><span className="staff-report-mark"><Icon name="alert" /></span><span className="staff-guild-title"><strong>{item.code} · {exception.replace(/^(Type|Message):\s*/, "")}</strong><small>{new Date(item.created_at).toLocaleString()} · {summary.slice(0, 140)}</small></span><span className="staff-guild-status is-blocked"><i />Error</span><Icon name={expanded ? "close" : "arrow"} className="staff-guild-chevron" /></button>{expanded && <div className="staff-report-details"><div className="staff-report-summary"><span className="panel-kicker">Report code</span><strong>{item.code}</strong></div><pre>{item.report}</pre><div className="staff-report-actions"><button type="button" className="button button-muted button-small" onClick={() => navigator.clipboard?.writeText(item.code)}>Copy code</button><button type="button" className="button button-muted button-small" onClick={() => navigator.clipboard?.writeText(item.report)}>Copy full report</button></div></div>}</article>; })}</div>}</section>}
    {activeTab === "blacklist" && canManageGuilds && <section id="staff-blacklist-panel" role="tabpanel" aria-labelledby="staff-blacklist-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Trust & safety</span><h2>Blacklist management</h2><p>Manage blocked Discord users and guilds. Access follows the guild-operations roles, and every mutation is recorded with its reason.</p></div><div className="staff-guild-count"><strong>{blacklistEntries.users.length + blacklistEntries.guilds.length}</strong><span>active entries</span></div></header><div className="staff-blacklist-form"><select value={blacklistType} onChange={(event) => setBlacklistType(event.target.value as "user" | "guild")}><option value="user">User</option><option value="guild">Guild</option></select><input value={blacklistId} onChange={(event) => setBlacklistId(event.target.value)} inputMode="numeric" maxLength={22} pattern="[0-9]{1,22}" placeholder="Discord ID" aria-label="Discord ID" /><input value={blacklistReason} onChange={(event) => setBlacklistReason(event.target.value)} maxLength={1000} placeholder="Reason (required)" aria-label="Blacklist reason" /><button type="button" className="button button-danger" disabled={busyGuildAction || !blacklistId || blacklistId.length > 22 || [...blacklistId].some((digit) => digit < "0" || digit > "9") || !blacklistReason.trim()} onClick={() => void addBlacklistEntry()}>Add to blacklist</button></div><label className="staff-guild-search"><Icon name="search" /><input type="search" value={blacklistSearch} onChange={(event) => setBlacklistSearch(event.target.value)} placeholder="Filter by ID or reason" aria-label="Filter blacklist" /></label><div className="staff-blacklist-columns">{(["users", "guilds"] as const).map((kind) => <section className="staff-blacklist-list" key={kind}><div className="staff-blacklist-list-heading"><span>{kind === "users" ? "Blocked users" : "Blocked guilds"}</span><strong>{blacklistEntries[kind].length}</strong></div>{blacklistEntries[kind].filter((entry) => `${entry.id} ${entry.reason || ""}`.toLocaleLowerCase().includes(blacklistSearch.trim().toLocaleLowerCase())).map((entry) => <article className="staff-blacklist-entry" key={entry.id}><div><strong>{entry.id}</strong><p>{entry.reason || "No reason recorded."}</p><small>{new Date(entry.timestamp * 1000).toLocaleString()}</small></div><div className="staff-blacklist-entry-actions"><button type="button" className="button button-muted button-small" disabled={busyGuildAction} onClick={() => { const reason = window.prompt("Update blacklist reason", entry.reason || ""); if (reason?.trim()) void saveGuildAction(async () => { await updateStaffBlacklist(kind === "users" ? "user" : "guild", "update", String(entry.id), reason, auth.csrf_token); setBlacklistEntries(await getStaffBlacklist()); }, "Blacklist reason updated."); }}>Edit reason</button><button type="button" className="button button-danger button-small" disabled={busyGuildAction} onClick={() => { if (window.confirm(`Remove ${entry.id} from the blacklist?`)) void saveGuildAction(async () => { await updateStaffBlacklist(kind === "users" ? "user" : "guild", "remove", String(entry.id), "", auth.csrf_token); setBlacklistEntries(await getStaffBlacklist()); }, "Blacklist entry removed."); }}>Remove</button></div></article>)}{blacklistEntries[kind].filter((entry) => `${entry.id} ${entry.reason || ""}`.toLocaleLowerCase().includes(blacklistSearch.trim().toLocaleLowerCase())).length === 0 && <p className="staff-blacklist-empty">{blacklistEntries[kind].length ? "No entries match that filter." : `No ${kind} are blacklisted.`}</p>}</section>)}</div></section>}
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
