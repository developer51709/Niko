import { useEffect, useState } from "react";
import type { FormEvent, KeyboardEvent } from "react";
import { addStaffStandby, controlStaffStandbyFailover, createStaffGuildInvite, getAuth, getGuilds, getTeamRecruitmentSettings, getTeamRecruitmentSubmissions, getStaffStandbys, getStaffBlacklist, getStaffBlacklistAppeals, getStaffErrorReports, getStaffGuilds, getStaffMe, getStats, leaveStaffGuild, removeStaffStandby, resetStaffGuildProfile, reviewTeamRecruitmentSubmission, reviewStaffBlacklistAppeal, saveGlobalProfile, saveStaffProfile, sendStaffGuildNotice, setTeamRecruitmentOpeningStatus, setStaffGuildBlacklist, updateStaffBlacklist } from "../api";
import { DiscordMarkdown } from "../components/DiscordMarkdown";
import { DiscordStatusAvatar } from "../components/DiscordStatusAvatar";
import { Icon } from "../components/Icon";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { PublicHeader } from "../components/PublicHeader";
import { dashboardPath, dashboardServersPath, dashboardUserPath, navigate } from "../router";
import type { AuthStatus, StandbyFailoverStatus, StandbyInstance, BlacklistAppeal, BotStats, Guild, PublicProfileLink, TeamRecruitmentOpening, TeamRecruitmentSubmission, StaffBlacklistEntry, StaffGuild, StaffMember } from "../types";

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

type StaffTab = "profile" | "global" | "guilds" | "blacklist" | "appeals" | "standbys" | "team-recruitment" | "reports";

const OWNER_ROLES = ["owner"];

// One source of truth for tab access: the sidebar buttons and the deep-link
// guard both read it, so a role can never reach a panel it may not open.
const TAB_ROLES: Record<StaffTab, string[]> = {
  profile: [],
  global: ["owner", "head_admin", "graphic_designer"],
  guilds: ["owner", "head_admin"],
  blacklist: ["owner", "head_admin"],
  appeals: ["owner", "head_admin"],
  standbys: OWNER_ROLES,
  "team-recruitment": OWNER_ROLES,
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

export function StaffDashboardPage() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [accessLoading, setAccessLoading] = useState(true);
  const [staff, setStaff] = useState<{ role: string; role_label: string; profile: StaffMember } | null>(null);
  const [stats, setStats] = useState<BotStats | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [form, setForm] = useState({ public_bio: "", public_banner_url: "", public_visible: true });
  const [links, setLinks] = useState<PublicProfileLink[]>([]);
  const [global, setGlobal] = useState({ avatar_url: "", banner_url: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [savingGlobal, setSavingGlobal] = useState(false);
  const [activeTab, setActiveTab] = useState<StaffTab>(() => tabFromHash(window.location.hash, null) ?? "profile");
  const [nikoApplications, setNikoApplications] = useState<TeamRecruitmentOpening[]>([]);
  const [nikoSubmissions, setNikoSubmissions] = useState<ReviewedTeamSubmission[]>([]);
  const [nikoBusy, setNikoBusy] = useState(false);
  const [nikoError, setNikoError] = useState("");
  const [nikoNotice, setNikoNotice] = useState("");
  const [standbys, setStandbys] = useState<StandbyInstance[]>([]);
  const [standbyFailover, setStandbyFailover] = useState<StandbyFailoverStatus | null>(null);
  const [expandedStandbyId, setExpandedStandbyId] = useState<string | null>(null);
  const [standbyRefreshedAt, setStandbyRefreshedAt] = useState<number | null>(null);
  const [standbyName, setStandbyName] = useState("");
  const [standbyUrl, setStandbyUrl] = useState("");
  const [standbyBusy, setStandbyBusy] = useState(false);
  const [standbyError, setStandbyError] = useState("");
  const [standbyMessage, setStandbyMessage] = useState("");
  const [appeals, setAppeals] = useState<BlacklistAppeal[]>([]);
  const [appealsLoading, setAppealsLoading] = useState(false);
  const [appealsError, setAppealsError] = useState("");
  const [appealNotes, setAppealNotes] = useState<Record<string, string>>({});
  const [reviewingAppealId, setReviewingAppealId] = useState<string | null>(null);
  const [errorReports, setErrorReports] = useState<{ code: string; report: string; created_at: string }[]>([]);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [reportsError, setReportsError] = useState("");
  const [reportSearch, setReportSearch] = useState("");
  const [expandedReportCode, setExpandedReportCode] = useState<string | null>(null);
  const [staffGuilds, setStaffGuilds] = useState<StaffGuild[]>([]);
  const [staffGuildsLoading, setStaffGuildsLoading] = useState(false);
  const [expandedGuildId, setExpandedGuildId] = useState<string | null>(null);
  const [guildSearch, setGuildSearch] = useState("");
  const [guildActionError, setGuildActionError] = useState("");
  const [guildActionMessage, setGuildActionMessage] = useState("");
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
      });
      setLinks(staffStatus.profile.public_links || []);
      if (staffStatus.role === "owner") {
        void refreshStandbys();
        void refreshNikoApplications();
      }
      if (tabAllowedForRole(staffStatus.role, "guilds")) {
        setStaffGuildsLoading(true);
        getStaffGuilds().then((result) => setStaffGuilds(result.guilds)).catch((reason) => setGuildActionError(reason instanceof Error ? reason.message : "Guild list unavailable.")).finally(() => setStaffGuildsLoading(false));
        getStaffBlacklist().then(setBlacklistEntries).catch((reason) => setGuildActionError(reason instanceof Error ? reason.message : "Blacklist unavailable."));
        if (["owner", "head_admin"].includes(staffStatus.role)) {
          getStaffBlacklistAppeals().then((result) => setAppeals(result.appeals)).catch((reason) => setAppealsError(reason instanceof Error ? reason.message : "Appeals unavailable."));
        }
      }
      void loadErrorReports();
    }).catch((reason) => {
      if (active) {
        setError(reason instanceof Error ? reason.message : "Staff access unavailable.");
        setAccessLoading(false);
      }
    });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (!staff || staff.role !== "owner" || activeTab !== "standbys") return;
    const timer = window.setInterval(() => void refreshStandbys(), 5000);
    return () => window.clearInterval(timer);
  }, [staff?.role, activeTab]);
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
  }, [staff?.role, activeTab]);

  if (accessLoading) return <div className="dashboard-state"><div className="loading-ring" /><p>Verifying your account and staff access…</p></div>;
  if (error || !staff || !auth?.authenticated) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><div className="eyebrow">Staff workspace</div><h1>{!auth && error ? "Staff access unavailable." : "Private team area."}</h1><p>{!auth && error ? error : !auth?.authenticated ? "You are not logged in. Sign in with Discord to continue to staff settings." : error || "This area is only available to official Niko staff."}</p>{auth && !auth.authenticated && <a className="button button-primary full-width" href="/auth/login?next=/dashboard/staff">Continue with Discord</a>}<button className="back-link" onClick={() => navigate("/dashboard")}>Return to dashboard</button></div></main></>;

  const signedInUser = auth.user!;
  const discordDefaultAvatar = `https://cdn.discordapp.com/embed/avatars/${Number(BigInt(signedInUser.id) % 5n)}.png`;
  const signedInAvatar = signedInUser.avatar
    ? `https://cdn.discordapp.com/avatars/${signedInUser.id}/${signedInUser.avatar}.png?size=128`
    : discordDefaultAvatar;
  const canManageGlobal = tabAllowedForRole(staff.role, "global");
  const canManageGuilds = tabAllowedForRole(staff.role, "guilds");
  const canReviewAppeals = tabAllowedForRole(staff.role, "appeals");
  const canManageStandbys = tabAllowedForRole(staff.role, "standbys");
  const canManageNikoApplications = tabAllowedForRole(staff.role, "team-recruitment");
  const query = guildSearch.trim().toLocaleLowerCase();
  const filteredGuilds = staffGuilds.filter((guild) =>
    !query || `${guild.name} ${guild.id} ${guild.owner_name}`.toLocaleLowerCase().includes(query)
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
      setError("Choose a link type and enter its URL, or remove the unfinished link.");
      setMessage("");
      return;
    }
    setSaving(true); setError(""); setMessage("");
    try { await saveStaffProfile({ ...form, public_links: linksToSave }, auth.csrf_token); setMessage("Your public team listing was saved."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not save listing."); }
    finally { setSaving(false); }
  };
  async function loadErrorReports() {
    setReportsLoading(true);
    setReportsError("");
    try { setErrorReports((await getStaffErrorReports()).reports); }
    catch (reason) { setReportsError(reason instanceof Error ? reason.message : "Error reports unavailable."); }
    finally { setReportsLoading(false); }
  };
  const refreshErrorReports = () => void loadErrorReports();
  async function loadAppeals() {
    setAppealsLoading(true);
    setAppealsError("");
    try { setAppeals((await getStaffBlacklistAppeals()).appeals); }
    catch (reason) { setAppealsError(reason instanceof Error ? reason.message : "Blacklist appeals unavailable."); }
    finally { setAppealsLoading(false); }
  }
  const reviewAppeal = async (appeal: BlacklistAppeal, status: "approved" | "denied") => {
    if (reviewingAppealId) return;
    setReviewingAppealId(appeal.appeal_id);
    setAppealsError("");
    try {
      await reviewStaffBlacklistAppeal(appeal.appeal_id, status, appealNotes[appeal.appeal_id] || "", auth.csrf_token);
      await loadAppeals();
    } catch (reason) { setAppealsError(reason instanceof Error ? reason.message : "The appeal decision could not be saved."); }
    finally { setReviewingAppealId(null); }
  };
  const refreshStaffGuilds = async () => {
    setStaffGuildsLoading(true);
    try { setStaffGuilds((await getStaffGuilds()).guilds); }
    catch (reason) { setGuildActionError(reason instanceof Error ? reason.message : "Guild list unavailable."); }
    finally { setStaffGuildsLoading(false); }
  };
  const saveGuildAction = async (action: () => Promise<unknown>, success: string) => {
    if (busyGuildAction) return;
    setBusyGuildAction(true); setGuildActionError(""); setGuildActionMessage("");
    try { await action(); setGuildActionMessage(success); await refreshStaffGuilds(); }
    catch (reason) { setGuildActionError(reason instanceof Error ? reason.message : "The guild action could not be completed."); }
    finally { setBusyGuildAction(false); }
  };
  async function refreshStandbys() {
    try {
      const result = await getStaffStandbys();
      setStandbys(result.standbys);
      setStandbyFailover(result.failover);
      setStandbyRefreshedAt(Date.now());
      setStandbyError("");
    } catch (reason) { setStandbyError(reason instanceof Error ? reason.message : "Standby status unavailable."); }
  }
  const standbyControl = async (action: { action: "mode"; mode: "auto" | "off" } | { action: "activate"; standby_id: string } | { action: "rotate" }, success: string) => {
    if (standbyBusy) return;
    setStandbyBusy(true); setStandbyError(""); setStandbyMessage("");
    try {
      await controlStaffStandbyFailover(action, auth.csrf_token);
      await refreshStandbys();
      setStandbyMessage(success);
    } catch (reason) { setStandbyError(reason instanceof Error ? reason.message : "Failover control failed."); }
    finally { setStandbyBusy(false); }
  };
  const saveStandby = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (standbyBusy) return;
    setStandbyBusy(true); setStandbyError(""); setStandbyMessage("");
    try {
      await addStaffStandby(standbyName, standbyUrl, auth.csrf_token);
      await refreshStandbys();
      setStandbyName(""); setStandbyUrl("");
      setStandbyMessage("Standby verified and registered. It is available for authenticated Discord traffic failover.");
    } catch (reason) { setStandbyError(reason instanceof Error ? reason.message : "Standby could not be verified."); }
    finally { setStandbyBusy(false); }
  };
  const deleteStandby = async (standby: StandbyInstance) => {
    if (standbyBusy || !window.confirm(`Remove ${standby.name} from standby failover?`)) return;
    setStandbyBusy(true); setStandbyError(""); setStandbyMessage("");
    try { await removeStaffStandby(standby.id, auth.csrf_token); await refreshStandbys(); setStandbyMessage(`${standby.name} was removed.`); }
    catch (reason) { setStandbyError(reason instanceof Error ? reason.message : "Standby could not be removed."); }
    finally { setStandbyBusy(false); }
  };
  async function refreshNikoApplications() {
    setNikoBusy(true); setNikoError("");
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
    } catch (reason) { setNikoError(reason instanceof Error ? reason.message : "Team Applications page unavailable."); }
    finally { setNikoBusy(false); }
  }
  const toggleNikoOpening = async (application: TeamRecruitmentOpening) => {
    setNikoBusy(true); setNikoError(""); setNikoNotice("");
    try { await setTeamRecruitmentOpeningStatus(application.id, application.status === "open" ? "closed" : "open", auth.csrf_token); await refreshNikoApplications(); }
    catch (reason) { setNikoError(reason instanceof Error ? reason.message : "Opening status could not be changed."); }
    finally { setNikoBusy(false); }
  };
  const reviewNikoSubmission = async (submission: ReviewedTeamSubmission, status: "approved" | "denied") => {
    if (nikoBusy) return;
    const revoking = status === "denied" && submission.review_status === "approved";
    if (revoking && !window.confirm(`Reverse ${submission.display_name}'s approval and remove the ${submission.role_name || "team"} role?`)) return;
    setNikoBusy(true); setNikoError(""); setNikoNotice("");
    try {
      const result = await reviewTeamRecruitmentSubmission(submission.opening_id, submission.user_id, status, auth.csrf_token);
      if (result.unchanged) {
        setNikoNotice(`${submission.display_name} already has that decision recorded. Nothing was re-sent or changed.`);
      } else if (status === "approved") {
        setNikoNotice(result.dm_sent === false
          ? `${submission.display_name} was approved and the team role was assigned, but the decision DM could not be delivered.`
          : `${submission.display_name} was approved, the team role was assigned, and the decision DM was sent.`);
      } else {
        setNikoNotice(result.role_revoked
          ? `${submission.display_name} was declined and the previously granted team role was removed.`
          : `${submission.display_name} was declined.`);
      }
      await refreshNikoApplications();
    } catch (reason) { setNikoError(reason instanceof Error ? reason.message : "The application decision could not be saved."); }
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
    setSavingGlobal(true); setError(""); setMessage("");
    try { await saveGlobalProfile(global, auth.csrf_token); setMessage("Niko's global profile was updated."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not update global profile."); }
    finally { setSavingGlobal(false); }
  };

  const content = <div className="staff-page">
    <header className="staff-heading">
      <div><div className="eyebrow">Staff workspace</div><h1>Shape your presence.</h1><p>Manage the public details granted to your <strong>{staff.role_label}</strong> role. Your name and avatar always come directly from Discord.</p></div>
      <div className="staff-role-card"><span className="staff-role-mark"><img src={signedInAvatar} alt="Your Discord profile" onError={(event) => { event.currentTarget.onerror = null; event.currentTarget.src = discordDefaultAvatar; }} /></span><span><small>Signed in as</small><strong>{staff.role_label}</strong></span></div>
    </header>

    <div className="staff-tabs" role="tablist" aria-label="Staff settings" onKeyDown={onTabKeyDown}>
      <button type="button" role="tab" id="staff-profile-tab" aria-selected={activeTab === "profile"} aria-controls="staff-profile-panel" className={activeTab === "profile" ? "active" : ""} onClick={() => setActiveTab("profile")}><Icon name="users" /> Public profile</button>
      {canManageGlobal && <button type="button" role="tab" id="staff-global-tab" aria-selected={activeTab === "global"} aria-controls="staff-global-panel" className={activeTab === "global" ? "active" : ""} onClick={() => setActiveTab("global")}><Icon name="settings" /> Bot profile</button>}
      {canManageGuilds && <button type="button" role="tab" id="staff-guilds-tab" aria-selected={activeTab === "guilds"} aria-controls="staff-guilds-panel" className={activeTab === "guilds" ? "active" : ""} onClick={() => setActiveTab("guilds")}><Icon name="shield" /> Guild operations <span>{staffGuilds.length}</span></button>}
      {canManageGuilds && <button type="button" role="tab" id="staff-blacklist-tab" aria-selected={activeTab === "blacklist"} aria-controls="staff-blacklist-panel" className={activeTab === "blacklist" ? "active" : ""} onClick={() => setActiveTab("blacklist")}><Icon name="lock" /> Blacklist <span>{blacklistEntries.users.length + blacklistEntries.guilds.length}</span></button>}
      {canReviewAppeals && <button type="button" role="tab" id="staff-appeals-tab" aria-selected={activeTab === "appeals"} aria-controls="staff-appeals-panel" className={activeTab === "appeals" ? "active" : ""} onClick={() => setActiveTab("appeals")}><Icon name="message" /> Appeals <span>{appeals.filter((appeal) => appeal.status === "pending").length}</span></button>}
      {canManageStandbys && <button type="button" role="tab" id="staff-standbys-tab" aria-selected={activeTab === "standbys"} aria-controls="staff-standbys-panel" className={activeTab === "standbys" ? "active" : ""} onClick={() => setActiveTab("standbys")}><Icon name="shield" /> Standby instances <span>{standbys.length}</span></button>}
      {canManageNikoApplications && <button type="button" role="tab" id="staff-team-recruitment-tab" aria-selected={activeTab === "team-recruitment"} aria-controls="staff-team-recruitment-panel" className={activeTab === "team-recruitment" ? "active" : ""} onClick={() => setActiveTab("team-recruitment")}><Icon name="users" /> Team Applications <span>{nikoApplications.reduce((count, application) => count + application.submission_count, 0)}</span></button>}
      <button type="button" role="tab" id="staff-reports-tab" aria-selected={activeTab === "reports"} aria-controls="staff-reports-panel" className={activeTab === "reports" ? "active" : ""} onClick={() => setActiveTab("reports")}><Icon name="alert" /> Error reports <span>{errorReports.length}</span></button>
    </div>

    {activeTab === "profile" && <section id="staff-profile-panel" role="tabpanel" aria-labelledby="staff-profile-tab"><div className="staff-layout">
      <section className="staff-panel staff-panel-main">
        <div className="staff-panel-heading"><div><span className="panel-kicker">Public listing</span><h2>How the team sees you</h2><p>Keep your introduction current while Discord remains the source of truth for your identity.</p></div><span className="staff-step">01</span></div>
        <div className="staff-fields">
          <label className="form-field"><span className="form-label">Banner URL</span><input type="url" value={form.public_banner_url} onChange={(e) => update("public_banner_url", e.target.value)} placeholder="https://…" /><small>Use a publicly reachable image. Leave blank for no banner.</small></label>
          <section className="staff-links-section" aria-labelledby="staff-links-heading">
            <div className="staff-links-heading"><div><span className="form-label" id="staff-links-heading">Links</span><small>Add up to 10 links. They appear on your profile, not the team overview card.</small></div><span className="staff-links-count">{links.length}/10</span></div>
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
        <label className="setting-row staff-visibility"><span><strong>Show me on the public Team page</strong><small>Hide your listing without removing your staff access.</small></span><input type="checkbox" checked={form.public_visible} onChange={(e) => update("public_visible", e.target.checked)} /><i /></label>
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
        <div className="staff-profile-rules"><span className="panel-kicker">Profile rules</span><h3>Stay consistent with Discord</h3><p>Your global display name and profile picture sync automatically, so updates made in Discord are reflected here without another form.</p><div className="staff-rule"><span>Identity</span><strong>Discord synced</strong></div><div className="staff-rule"><span>Editable</span><strong>Bio · banner · links · visibility</strong></div></div>
      </aside>
    </div></section>}

    {activeTab === "global" && canManageGlobal && <section id="staff-global-panel" role="tabpanel" aria-labelledby="staff-global-tab" className="staff-panel staff-global-panel"><div className="staff-panel-heading"><div><span className="panel-kicker">Graphic direction</span><h2>Global Niko profile</h2><p>Reserved for Graphic Designers, Head Admins, and owners. Paste publicly reachable image URLs.</p></div><span className="staff-step">02</span></div><div className="staff-fields staff-fields-two"><label className="form-field"><span className="form-label">Bot avatar URL</span><input value={global.avatar_url} onChange={(e) => setGlobal({ ...global, avatar_url: e.target.value })} placeholder="https://…" /></label><label className="form-field"><span className="form-label">Bot banner URL</span><input value={global.banner_url} onChange={(e) => setGlobal({ ...global, banner_url: e.target.value })} placeholder="https://…" /></label></div><div className="staff-panel-footer"><span>Updates the bot-wide Discord profile.</span><button type="button" className="button button-primary" onClick={saveGlobal} disabled={savingGlobal}>{savingGlobal ? "Updating…" : "Update global profile"}</button></div></section>}
    {activeTab === "guilds" && canManageGuilds && <section id="staff-guilds-panel" role="tabpanel" aria-labelledby="staff-guilds-tab" className="staff-guild-operations">
      <header className="staff-guilds-heading"><div><span className="panel-kicker">Bot operations</span><h2>Guild directory</h2><p>Review every server Niko currently serves. Select a guild to inspect its owner, activity footprint, live server profile and operational controls.</p></div><div className="staff-guild-count"><strong>{staffGuilds.length}</strong><span>connected guilds</span></div></header>
      <div className="staff-guild-toolbar"><label className="staff-guild-search"><Icon name="search" /><input type="search" value={guildSearch} onChange={(event) => setGuildSearch(event.target.value)} placeholder="Search guilds, owners, or IDs" aria-label="Search guilds" /></label><button type="button" className="button button-muted" onClick={refreshStaffGuilds} disabled={staffGuildsLoading}><Icon name="spark" />{staffGuildsLoading ? "Refreshing…" : "Refresh guilds"}</button></div>
      {staffGuildsLoading && staffGuilds.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading the live guild directory…</p></div> : filteredGuilds.length === 0 ? <div className="staff-guild-empty"><span>{staffGuilds.length ? "No guilds match that search." : "The bot is not connected to any guilds."}</span></div> : <div className="staff-guild-list">
        {filteredGuilds.map((guild) => {
          const expanded = expandedGuildId === guild.id;
          return <article className={`staff-guild-card${expanded ? " expanded" : ""}`} key={guild.id}>
            <button type="button" className="staff-guild-row" aria-expanded={expanded} onClick={() => { setExpandedGuildId(expanded ? null : guild.id); setGuildActionError(""); setGuildActionMessage(""); }}>
              <span className="staff-guild-icon">{guild.icon_url ? <img src={guild.icon_url} alt="" /> : <b>{guild.name.slice(0, 1).toUpperCase()}</b>}</span>
              <span className="staff-guild-title"><strong>{guild.name}</strong><small>{guild.id} · {guild.member_count.toLocaleString()} members</small></span>
              <span className={`staff-guild-status${guild.blacklisted ? " is-blocked" : ""}`}><i />{guild.blacklisted ? "Blacklisted" : "Active"}</span>
              <Icon name={expanded ? "close" : "arrow"} className="staff-guild-chevron" />
            </button>
            {expanded && <div className="staff-guild-details">
              <div className="staff-guild-summary"><div><span className="panel-kicker">Guild owner</span><DiscordMarkdown text={`<@${guild.owner_id || "0"}>`} mentionNames={{ user: guild.owner_id ? { [guild.owner_id]: guild.owner_name } : {} }} className="staff-guild-owner" /></div><div><span className="panel-kicker">Created</span><strong>{guild.created_at ? new Date(guild.created_at).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" }) : "Unknown"}</strong></div><div><span className="panel-kicker">Channels</span><strong>{guild.channel_count.toLocaleString()} · {guild.category_count} categories</strong></div><div><span className="panel-kicker">Profile name</span><strong>{guild.profile_name || "Niko"}</strong></div><div><span className="panel-kicker">Roles</span><strong>{guild.role_count}</strong></div></div>
              <div className="staff-guild-profile-previews"><div className="staff-guild-preview"><span className="panel-kicker">Guild avatar</span>{guild.bot_avatar_url ? <img src={guild.bot_avatar_url} alt={`${guild.name} bot avatar`} /> : <div className="staff-guild-no-image">No server avatar</div>}</div><div className="staff-guild-preview staff-guild-preview-banner"><span className="panel-kicker">Guild banner</span>{guild.bot_banner_url ? <img src={guild.bot_banner_url} alt={`${guild.name} bot banner`} /> : <div className="staff-guild-no-image">No server banner</div>}</div></div>
              <div className="staff-guild-action-panel"><div className="staff-guild-action-heading"><div><span className="panel-kicker">Quick actions</span><h3>Operations for {guild.name}</h3></div><span className="staff-guild-id">ID · {guild.id}</span></div>
                <div className="staff-guild-actions"><button type="button" className="button button-muted" disabled={busyGuildAction} onClick={() => { setInviteUrl(""); setInviteGuildId(guild.id); void createStaffGuildInvite(guild.id, auth.csrf_token).then((result) => setInviteUrl(result.url)).catch((reason) => setGuildActionError(reason instanceof Error ? reason.message : "Could not create an invite.")); }}><Icon name="link" />Temporary invite</button><button type="button" className="button button-muted" onClick={() => setPermissionGuild(guild)}><Icon name="shield" />Permissions</button><button type="button" className="button button-danger" disabled={busyGuildAction} onClick={() => { if (window.confirm(`Make Niko leave ${guild.name}? This removes the bot from the server.`)) void saveGuildAction(() => leaveStaffGuild(guild.id, auth.csrf_token), `Niko left ${guild.name}.`); }}>Leave guild</button><label className="form-field staff-guild-reason"><span className="form-label">Blacklist reason</span><input value={guildBlacklistReason} onChange={(event) => setGuildBlacklistReason(event.target.value)} maxLength={1000} placeholder="Required when blacklisting" /></label><button type="button" className={`button ${guild.blacklisted ? "button-muted" : "button-danger"}`} disabled={busyGuildAction || (!guild.blacklisted && !guildBlacklistReason.trim())} onClick={() => saveGuildAction(() => setStaffGuildBlacklist(guild.id, guild.blacklisted ? "remove" : "add", guildBlacklistReason, auth.csrf_token), guild.blacklisted ? `${guild.name} removed from the blacklist.` : `${guild.name} added to the blacklist.`)}>{busyGuildAction ? "Working…" : guild.blacklisted ? "Remove blacklist" : "Blacklist guild"}</button><button type="button" className="button button-muted" disabled={busyGuildAction} onClick={() => { if (window.confirm(`Reset Niko’s server profile for ${guild.name}? This clears the customized name, bio, font, colors, avatar, and banner.`)) void saveGuildAction(() => resetStaffGuildProfile(guild.id, auth.csrf_token), `${guild.name} profile reset.`); }}><Icon name="settings" />Reset profile</button></div>
                <label className="form-field staff-guild-notice-field"><span className="form-label">Formal moderation notice</span><textarea rows={4} maxLength={1500} value={noticeMessage} onChange={(event) => setNoticeMessage(event.target.value)} placeholder="Describe the moderation concern and any action required…" /><small>{noticeMessage.length}/1500 · delivered as an official Components v2 notice directly to the server owner</small></label><button type="button" className="button button-primary" disabled={busyGuildAction || !noticeMessage.trim()} onClick={() => { if (window.confirm(`Send this formal moderation notice to ${guild.owner_name}, the owner of ${guild.name}?`)) void saveGuildAction(() => sendStaffGuildNotice(guild.id, noticeMessage, auth.csrf_token), `Moderation notice sent to ${guild.owner_name}.`); }}><Icon name="message" />Send formal notice</button>
                {inviteUrl && inviteGuildId === guild.id && <div className="staff-guild-invite-result" role="status"><span>One-use invite · expires in 10 minutes</span><a href={inviteUrl} target="_blank" rel="noreferrer">{inviteUrl}</a><button type="button" className="button button-muted button-small" onClick={() => navigator.clipboard?.writeText(inviteUrl)}>Copy invite</button></div>}
                {guild.blacklisted && <p className="staff-guild-blacklist-note"><strong>Blacklist reason:</strong> {guild.blacklist_reason || "No reason recorded."}</p>}
                {guildActionMessage && <div className="notice" role="status">{guildActionMessage}</div>}
              </div>
            </div>}
          </article>;
        })}
      </div>}
    </section>}
    {activeTab === "appeals" && canReviewAppeals && <section id="staff-appeals-panel" role="tabpanel" aria-labelledby="staff-appeals-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Trust &amp; safety</span><h2>Blacklist appeals</h2><p>Review requests privately. Approval removes the active restriction while preserving its appealed history; denied appeals cannot be resubmitted.</p></div><div className="staff-guild-count"><strong>{appeals.filter((appeal) => appeal.status === "pending").length}</strong><span>pending review</span></div></header><div className="staff-guild-toolbar"><span className="staff-appeal-privacy">Visible to the bot owner and Head Admins</span><button type="button" className="button button-muted" onClick={() => void loadAppeals()} disabled={appealsLoading}><Icon name="spark" />{appealsLoading ? "Refreshing…" : "Refresh appeals"}</button></div>{appealsError && <div className="notice warning" role="alert">{appealsError}</div>}{appealsLoading && appeals.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading appeals…</p></div> : appeals.length === 0 ? <div className="staff-guild-empty">No blacklist appeals have been submitted.</div> : <div className="staff-guild-list">{appeals.map((appeal) => <article className={`staff-guild-card staff-appeal-card staff-appeal-${appeal.status}`} key={appeal.appeal_id}><div className="staff-appeal-header"><div className="staff-appeal-identity"><span className="panel-kicker">{appeal.guild_id ? "Guild appeal" : "User appeal"}</span><strong>{appeal.guild_id ? `Guild ${appeal.guild_id}` : appeal.username || "Discord user"}</strong><small>{appeal.guild_id ? `Submitted by user ${appeal.user_id}` : `Discord ID · ${appeal.user_id}`} <span aria-hidden="true">·</span> {new Date(appeal.created_at * 1000).toLocaleString()}</small></div><span className={`staff-guild-status${appeal.status === "denied" ? " is-blocked" : appeal.status === "pending" ? " is-pending" : " is-approved"}`}><i />{appeal.status}</span></div><div className="staff-appeal-reason staff-appeal-context"><span className="panel-kicker">Blacklist reason</span><p>{appeal.blacklist_reason || "No reason recorded."}</p></div><div className="staff-appeal-reason staff-appeal-message"><span className="panel-kicker">Appeal statement</span><p>{appeal.appeal_text}</p></div>{appeal.status === "pending" ? <><label className="form-field"><span className="form-label">Staff note {"(optional)"}</span><textarea rows={3} maxLength={2000} value={appealNotes[appeal.appeal_id] || ""} onChange={(event) => setAppealNotes((current) => ({ ...current, [appeal.appeal_id]: event.target.value }))} placeholder="Add context for the decision; the user can see this note…" /><small>{(appealNotes[appeal.appeal_id] || "").length}/2000 · shown to the user with the decision</small></label><div className="staff-appeal-actions"><button type="button" className="button button-muted" disabled={reviewingAppealId !== null} onClick={() => void reviewAppeal(appeal, "denied")}>{reviewingAppealId === appeal.appeal_id ? "Saving…" : "Deny appeal"}</button><button type="button" className="button button-primary" disabled={reviewingAppealId !== null} onClick={() => void reviewAppeal(appeal, "approved")}>{reviewingAppealId === appeal.appeal_id ? "Saving…" : "Approve appeal"}</button></div></> : <><div className="staff-appeal-reason staff-appeal-note"><span className="panel-kicker">Staff decision note</span><p>{appeal.staff_note || "No note added."}</p></div><small className="staff-appeal-reviewed">{appeal.status === "approved" ? "Approved" : "Denied"}{appeal.reviewed_at ? ` ${new Date(appeal.reviewed_at * 1000).toLocaleString()}` : ""} <span aria-hidden="true">·</span> Staff ID {appeal.reviewed_by || "unknown"}</small></>}</article>)}</div>}</section>}
    {activeTab === "standbys" && canManageStandbys && <section id="staff-standbys-panel" role="tabpanel" aria-labelledby="staff-standbys-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Owner-only · authenticated failover</span><h2>Standby backend instances</h2><p>Each standby runs a warm, full copy of the production backend and dashboard. It takes Discord gateway ownership only after an authenticated failover handoff; Webshare proxies remain a separate egress feature.</p></div><div className="staff-guild-count"><strong>{standbys.length}</strong><span>verified instances</span></div></header><form className="staff-blacklist-form" onSubmit={(event) => void saveStandby(event)}><input value={standbyName} onChange={(event) => setStandbyName(event.target.value)} maxLength={60} placeholder="Region / instance name" aria-label="Standby name" required /><input value={standbyUrl} onChange={(event) => setStandbyUrl(event.target.value)} type="url" placeholder="https://standby.example.com" aria-label="Standby HTTPS origin" required /><button type="submit" className="button button-primary" disabled={standbyBusy}>{standbyBusy ? "Verifying…" : "Verify & add standby"}</button></form><div className="staff-guild-toolbar standby-toolbar"><span className="standby-live-label"><i />Live status · {standbyRefreshedAt ? `updated ${new Date(standbyRefreshedAt).toLocaleTimeString()}` : "connecting…"}</span><div className="standby-mode-actions"><button type="button" className={`button button-small ${standbyFailover?.mode === "auto" || standbyFailover?.mode === "standby" ? "button-primary" : "button-muted"}`} disabled={standbyBusy} onClick={() => void standbyControl({ action: "mode", mode: "auto" }, "Automatic standby-first failover enabled.")}>Auto · standby first</button><button type="button" className={`button button-small ${standbyFailover?.mode === "off" ? "button-danger" : "button-muted"}`} disabled={standbyBusy} onClick={() => void standbyControl({ action: "mode", mode: "off" }, "Automatic routing disabled.")}>Direct / off</button><button type="button" className="button button-small button-muted" disabled={standbyBusy} onClick={() => void refreshStandbys()}><Icon name="spark" />Refresh now</button></div></div>{standbyFailover && <div className="standby-overview"><div><span className="panel-kicker">Route</span><strong>{standbyFailover.enabled ? standbys.find((item) => item.id === standbyFailover.active_standby_id)?.name || "Standby active" : standbyFailover.mode === "off" ? "Direct · failover off" : "Direct · auto armed"}</strong></div><div><span className="panel-kicker">Failovers</span><strong>{standbyFailover.failover_count}</strong></div><div><span className="panel-kicker">Egress</span><strong>{standbyFailover.egress_blocked ? "Blocked · rerouted" : "Clear"}</strong></div></div>}{standbyError && <div className="notice warning" role="alert">{standbyError}</div>}{standbyMessage && <div className="notice" role="status">{standbyMessage}</div>}{standbyFailover?.last_error && <div className="notice warning" role="status">Last route warning: {standbyFailover.last_error}</div>}<div className="staff-guild-list">{standbys.map((standby) => { const expanded = expandedStandbyId === standby.id; const stats = standby.stats; return <article className={`staff-guild-card standby-card${expanded ? " expanded" : ""}`} key={standby.id}><button type="button" className="staff-guild-row standby-card-toggle" aria-expanded={expanded} onClick={() => setExpandedStandbyId(expanded ? null : standby.id)}><span className="staff-guild-icon"><Icon name="shield" /></span><span className="staff-guild-title"><strong>{standby.name}</strong><small>{standby.url} · verified {new Date(standby.created_at * 1000).toLocaleString()}</small></span><span className={`staff-guild-status${standby.health === "online" ? " is-approved" : " is-blocked"}`}><i />{standby.health === "online" ? "Online" : "Offline"}</span>{standby.active && <span className="standby-active-tag">Active</span>}<Icon name={expanded ? "close" : "arrow"} className="staff-guild-chevron" /></button>{expanded && <div className="standby-card-details"><div className="standby-stats-grid"><div><span className="panel-kicker">Health</span><strong>{standby.health === "online" ? "Reachable" : "Unavailable"}</strong></div><div><span className="panel-kicker">Discord API requests</span><strong>{stats?.total_api_requests ?? "—"}</strong></div><div><span className="panel-kicker">Failed requests</span><strong>{stats?.failed_api_requests ?? "—"}</strong></div><div><span className="panel-kicker">Uptime</span><strong>{stats ? `${Math.floor(stats.uptime_seconds / 3600)}h ${Math.floor(stats.uptime_seconds % 3600 / 60)}m` : "—"}</strong></div></div><div className="standby-manual-actions"><button type="button" className="button button-primary button-small" disabled={standbyBusy || standby.health !== "online"} onClick={() => void standbyControl({ action: "activate", standby_id: standby.id }, `${standby.name} is now the active Discord route.`)}><Icon name="spark" />Route through standby</button><button type="button" className="button button-muted button-small" disabled={standbyBusy} onClick={() => void standbyControl({ action: "rotate" }, "Failover route rotated.")}><Icon name="refresh" />Rotate route</button><button type="button" className="button button-danger button-small" disabled={standbyBusy} onClick={() => void deleteStandby(standby)}>Remove standby</button></div></div>}</article>; })}{standbys.length === 0 && <div className="staff-guild-empty">No verified standby instances yet.</div>}</div></section>}
    {activeTab === "team-recruitment" && canManageNikoApplications && <section id="staff-team-recruitment-panel" role="tabpanel" aria-labelledby="staff-team-recruitment-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Owner-only · official team applications</span><h2>Team Applications</h2><p>Manage fixed role openings and review every submission from one queue. Role questions and role links are managed in code.</p></div><div className="staff-guild-count"><strong>{nikoSubmissions.length}</strong><span>submitted applications</span></div></header><div className="staff-guild-toolbar"><span className="staff-appeal-privacy">{nikoSubmissions.filter((submission) => submission.review_status === "pending").length} pending · {nikoSubmissions.filter((submission) => submission.review_status !== "pending").length} reviewed</span><button type="button" className="button button-muted" onClick={() => void refreshNikoApplications()} disabled={nikoBusy}><Icon name="spark" />{nikoBusy ? "Refreshing…" : "Refresh"}</button></div>{nikoError && <div className="notice warning" role="alert">{nikoError}</div>}{nikoNotice && <div className="notice applications-success" role="status">{nikoNotice}</div>}<section className="team-recruitment-openings"><div className="team-recruitment-list-heading"><div><span className="panel-kicker">Opening controls</span><h3>Role openings</h3></div><span>{nikoApplications.length} fixed roles</span></div><div className="staff-guild-list">{nikoApplications.map((application) => <article className="staff-guild-card" key={application.id}><div className="staff-guild-row"><span className="staff-guild-icon"><Icon name="users" /></span><span className="staff-guild-title"><strong>{application.title} · {application.role_name || "Role"}</strong><small>{application.submission_count} {application.submission_count === 1 ? "submission" : "submissions"} · {application.status === "open" ? "Accepting applications" : "Closed"} · /team/apply/{application.id}</small></span><button type="button" className="button button-muted button-small" onClick={() => void toggleNikoOpening(application)} disabled={nikoBusy}>{application.status === "open" ? "Close" : "Reopen"}</button></div></article>)}{nikoApplications.length === 0 && <div className="staff-guild-empty">Fixed role applications will appear here when available.</div>}</div></section><section className="team-recruitment-submissions"><div className="team-recruitment-list-heading"><div><span className="panel-kicker">Review queue</span><h3>Submitted applications</h3></div><span>{nikoSubmissions.length} total</span></div>{nikoBusy && nikoSubmissions.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading submitted applications…</p></div> : nikoSubmissions.length === 0 ? <div className="staff-guild-empty">No submitted applications yet.</div> : <><div className="team-recruitment-status-group"><div className="team-recruitment-status-heading"><h4>Pending review</h4><span>{nikoSubmissions.filter((submission) => submission.review_status === "pending").length}</span></div>{nikoSubmissions.filter((submission) => submission.review_status === "pending").length === 0 ? <p className="team-recruitment-empty-group">You’re all caught up. New submissions will appear here.</p> : <div className="team-recruitment-review-list">{nikoSubmissions.filter((submission) => submission.review_status === "pending").map((submission) => <article className="team-recruitment-review-entry" key={`${submission.opening_id}-${submission.user_id}`}><header className="team-recruitment-submission-heading"><div><strong>{submission.display_name}</strong><small>Discord ID · {submission.user_id}{submission.submitted_at ? ` · ${new Date(submission.submitted_at).toLocaleString()}` : ""}</small></div><span className="team-recruitment-opening-tag">{submission.opening_title} · {submission.role_name || "Role"}</span></header><div className="team-recruitment-answers">{submission.answers.map((answer) => <div key={answer.question_id}><strong>{answer.prompt}</strong><p>{Array.isArray(answer.answer) ? answer.answer.join(", ") || "No answer provided." : answer.answer || "No answer provided."}</p></div>)}</div><footer className="team-recruitment-review-actions"><button type="button" className="button button-muted button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "denied")}>Decline</button><button type="button" className="button button-primary button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "approved")}>Approve</button></footer></article>)}</div>}</div><div className="team-recruitment-status-group is-reviewed"><div className="team-recruitment-status-heading"><h4>Reviewed</h4><span>{nikoSubmissions.filter((submission) => submission.review_status !== "pending").length}</span></div>{nikoSubmissions.filter((submission) => submission.review_status !== "pending").length === 0 ? <p className="team-recruitment-empty-group">Reviewed applications will be kept here for reference.</p> : <div className="team-recruitment-review-list">{nikoSubmissions.filter((submission) => submission.review_status !== "pending").map((submission) => <article className="team-recruitment-review-entry" key={`${submission.opening_id}-${submission.user_id}`}><header className="team-recruitment-submission-heading"><div><strong>{submission.display_name}</strong><small>Discord ID · {submission.user_id}{submission.submitted_at ? ` · Submitted ${new Date(submission.submitted_at).toLocaleString()}` : ""}</small></div><span className={`team-recruitment-decision ${submission.review_status}`}>{submission.review_status === "approved" ? "Approved" : "Declined"}</span></header><div className="team-recruitment-opening-tag">{submission.opening_title} · {submission.role_name || "Role"}</div><div className="team-recruitment-answers">{submission.answers.map((answer) => <div key={answer.question_id}><strong>{answer.prompt}</strong><p>{Array.isArray(answer.answer) ? answer.answer.join(", ") || "No answer provided." : answer.answer || "No answer provided."}</p></div>)}</div><small className="team-recruitment-review-meta">{submission.reviewed_at ? `Reviewed ${new Date(submission.reviewed_at).toLocaleString()}` : "Decision recorded"}{submission.reviewed_by ? ` · Staff ID ${submission.reviewed_by}` : ""}</small><footer className="team-recruitment-review-actions">{submission.review_status === "approved" ? <button type="button" className="button button-muted button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "denied")}>Revoke approval</button> : <button type="button" className="button button-primary button-small" disabled={nikoBusy} onClick={() => void reviewNikoSubmission(submission, "approved")}>Approve instead</button>}</footer></article>)}</div>}</div></>}</section></section>}
    {activeTab === "reports" && <section id="staff-reports-panel" role="tabpanel" aria-labelledby="staff-reports-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Diagnostics</span><h2>Bot error reports</h2><p>Recent command and runtime failures collected by Niko. Expand a report to inspect its details and traceback; use the code to retrieve it with <code>.staff getreport CODE</code>.</p></div><div className="staff-guild-count"><strong>{errorReports.length}</strong><span>recent reports</span></div></header><div className="staff-guild-toolbar"><label className="staff-guild-search"><Icon name="search" /><input type="search" value={reportSearch} onChange={(event) => setReportSearch(event.target.value)} placeholder="Search report code, exception, or details" aria-label="Search error reports" /></label><button type="button" className="button button-muted" onClick={() => void refreshErrorReports()} disabled={reportsLoading}><Icon name="spark" />{reportsLoading ? "Refreshing…" : "Refresh reports"}</button></div>{reportsError && <div className="notice warning" role="alert">{reportsError}</div>}{reportsLoading && errorReports.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading recent error reports…</p></div> : errorReports.filter((item) => `${item.code} ${item.report}`.toLocaleLowerCase().includes(reportSearch.trim().toLocaleLowerCase())).length === 0 ? <div className="staff-guild-empty">{errorReports.length ? "No reports match that search." : "No bot error reports have been saved."}</div> : <div className="staff-guild-list">{errorReports.filter((item) => `${item.code} ${item.report}`.toLocaleLowerCase().includes(reportSearch.trim().toLocaleLowerCase())).map((item) => { const lines = item.report.split("\n"); const exceptionIndex = lines.findIndex((line) => line === "Exception"); const exception = lines.slice(exceptionIndex + 2).find((line) => line.startsWith("Type:") || line.startsWith("Message:")) || "Unknown exception"; const detailsIndex = lines.findIndex((line) => line === "Occurred (UTC):"); const summary = lines.slice(detailsIndex + 2).find((line) => line.trim()) || "No report details"; const expanded = expandedReportCode === item.code; return <article className={`staff-guild-card${expanded ? " expanded" : ""}`} key={item.code}><button type="button" className="staff-guild-row staff-report-row" aria-expanded={expanded} onClick={() => setExpandedReportCode(expanded ? null : item.code)}><span className="staff-report-mark"><Icon name="alert" /></span><span className="staff-guild-title"><strong>{item.code} · {exception.replace(/^(Type|Message):\s*/, "")}</strong><small>{new Date(item.created_at).toLocaleString()} · {summary.slice(0, 140)}</small></span><span className="staff-guild-status is-blocked"><i />Error</span><Icon name={expanded ? "close" : "arrow"} className="staff-guild-chevron" /></button>{expanded && <div className="staff-report-details"><div className="staff-report-summary"><span className="panel-kicker">Report code</span><strong>{item.code}</strong></div><pre>{item.report}</pre><div className="staff-report-actions"><button type="button" className="button button-muted button-small" onClick={() => navigator.clipboard?.writeText(item.code)}>Copy code</button><button type="button" className="button button-muted button-small" onClick={() => navigator.clipboard?.writeText(item.report)}>Copy full report</button></div></div>}</article>; })}</div>}</section>}
    {activeTab === "blacklist" && canManageGuilds && <section id="staff-blacklist-panel" role="tabpanel" aria-labelledby="staff-blacklist-tab" className="staff-guild-operations"><header className="staff-guilds-heading"><div><span className="panel-kicker">Trust & safety</span><h2>Blacklist management</h2><p>Manage blocked Discord users and guilds. Access follows the guild-operations roles, and every mutation is recorded with its reason.</p></div><div className="staff-guild-count"><strong>{blacklistEntries.users.length + blacklistEntries.guilds.length}</strong><span>active entries</span></div></header><div className="staff-blacklist-form"><select value={blacklistType} onChange={(event) => setBlacklistType(event.target.value as "user" | "guild")}><option value="user">User</option><option value="guild">Guild</option></select><input value={blacklistId} onChange={(event) => setBlacklistId(event.target.value)} inputMode="numeric" maxLength={22} pattern="[0-9]{1,22}" placeholder="Discord ID" aria-label="Discord ID" /><input value={blacklistReason} onChange={(event) => setBlacklistReason(event.target.value)} maxLength={1000} placeholder="Reason (required)" aria-label="Blacklist reason" /><button type="button" className="button button-danger" disabled={busyGuildAction || !blacklistId || blacklistId.length > 22 || [...blacklistId].some((digit) => digit < "0" || digit > "9") || !blacklistReason.trim()} onClick={() => void saveGuildAction(async () => { await updateStaffBlacklist(blacklistType, "add", blacklistId, blacklistReason, auth.csrf_token); setBlacklistEntries(await getStaffBlacklist()); setBlacklistId(""); }, `${blacklistType === "user" ? "User" : "Guild"} added to blacklist.`)}>Add to blacklist</button></div><label className="staff-guild-search"><Icon name="search" /><input type="search" value={blacklistSearch} onChange={(event) => setBlacklistSearch(event.target.value)} placeholder="Filter by ID or reason" aria-label="Filter blacklist" /></label><div className="staff-blacklist-columns">{(["users", "guilds"] as const).map((kind) => <section className="staff-blacklist-list" key={kind}><div className="staff-blacklist-list-heading"><span>{kind === "users" ? "Blocked users" : "Blocked guilds"}</span><strong>{blacklistEntries[kind].length}</strong></div>{blacklistEntries[kind].filter((entry) => `${entry.id} ${entry.reason || ""}`.toLocaleLowerCase().includes(blacklistSearch.trim().toLocaleLowerCase())).map((entry) => <article className="staff-blacklist-entry" key={entry.id}><div><strong>{entry.id}</strong><p>{entry.reason || "No reason recorded."}</p><small>{new Date(entry.timestamp * 1000).toLocaleString()}</small></div><div className="staff-blacklist-entry-actions"><button type="button" className="button button-muted button-small" disabled={busyGuildAction} onClick={() => { const reason = window.prompt("Update blacklist reason", entry.reason || ""); if (reason?.trim()) void saveGuildAction(async () => { await updateStaffBlacklist(kind === "users" ? "user" : "guild", "update", String(entry.id), reason, auth.csrf_token); setBlacklistEntries(await getStaffBlacklist()); }, "Blacklist reason updated."); }}>Edit reason</button><button type="button" className="button button-danger button-small" disabled={busyGuildAction} onClick={() => { if (window.confirm(`Remove ${entry.id} from the blacklist?`)) void saveGuildAction(async () => { await updateStaffBlacklist(kind === "users" ? "user" : "guild", "remove", String(entry.id), "", auth.csrf_token); setBlacklistEntries(await getStaffBlacklist()); }, "Blacklist entry removed."); }}>Remove</button></div></article>)}{blacklistEntries[kind].filter((entry) => `${entry.id} ${entry.reason || ""}`.toLocaleLowerCase().includes(blacklistSearch.trim().toLocaleLowerCase())).length === 0 && <p className="staff-blacklist-empty">{blacklistEntries[kind].length ? "No entries match that filter." : `No ${kind} are blacklisted.`}</p>}</section>)}</div>{guildActionMessage && <div className="notice" role="status">{guildActionMessage}</div>}{guildActionError && <div className="notice warning" role="alert">{guildActionError}</div>}</section>}
    {permissionGuild && <div className="modal-backdrop" role="presentation" onClick={() => setPermissionGuild(null)}><section className="modal-card staff-permissions-modal" role="dialog" aria-modal="true" aria-labelledby="guild-permissions-title" onClick={(event) => event.stopPropagation()}><div className="panel-heading"><div><span className="panel-kicker">Discord access audit</span><h3 id="guild-permissions-title">{permissionGuild.name} permissions</h3><p>{permissionGuild.bot_permissions.filter((permission) => permission.granted).length} granted · {permissionGuild.bot_permissions.filter((permission) => !permission.granted).length} missing</p></div><button type="button" className="button button-muted" onClick={() => setPermissionGuild(null)}>Close</button></div><div className="staff-permissions-list">{permissionGuild.bot_permissions.map((permission) => <div key={permission.name} className={permission.granted ? "granted" : "missing"}><span>{permission.label}</span><strong>{permission.granted ? "Granted" : "Missing"}</strong></div>)}</div></section></div>}
    {activeTab === "profile" && message && <div className="notice">{message}</div>}{activeTab === "profile" && error && <div className="notice warning">{error}</div>}
  </div>;

  return <DashboardShell user={auth.user!} guilds={guilds} selectedGuild={null} view="overview" section="overview" userTab="overview" stats={stats} staffRole={staff.role} onHome={() => navigate(dashboardPath())} onServers={() => navigate(dashboardServersPath())} onGuildChange={() => undefined} onSectionChange={() => undefined} onUserTabChange={(tab) => navigate(dashboardUserPath(tab))} onRefresh={() => window.location.reload()} refreshing={false}>{content}</DashboardShell>;
}
