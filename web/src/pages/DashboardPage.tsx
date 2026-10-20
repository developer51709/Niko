import { useEffect, useRef, useState } from "react";
import { ApiError, getAuth, getConfig, getDashboardAccess, getGuildBlacklistAppealStatus, getGuilds, getLevels, getMyAchievements, getMyEconomy, getOverview, getResources, getStats, getUserOverview, getStaffMe } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { AiView, CustomizationSettings, ModerationView, OnboardingView, TicketsView } from "../components/dashboard/SettingsViews";
import { ServerSettingsView } from "../components/dashboard/ServerSettingsView";
import { StaffApplicationsView } from "../components/dashboard/StaffApplicationsView";
import { NotifierView } from "../components/dashboard/NotifierView";
import { LevelingView, OverviewView, ServersView, UserOverviewView } from "../components/dashboard/DashboardViews";
import { AchievementsView } from "../components/dashboard/AchievementsView";
import { EconomyView } from "../components/dashboard/EconomyView";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import { useLiveResource } from "../hooks/useLiveResource";
import type { PublicConfig } from "../types";
import { dashboardPath, dashboardRoute, dashboardServersPath, dashboardUserPath, navigate, type DashboardView, type DashSection, type UserTab } from "../router";
import type { AchievementsResponse, AuthStatus, BotStats, EconomyStanding, Guild, GuildConfig, GuildOverview, GuildResources, LevelRow, User, UserOverview } from "../types";
import { Icon } from "../components/Icon";

function AuthCard({ auth }: { auth: AuthStatus }) {
  const config = useBotConfig();
  return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card">
    <span className="auth-mark">n</span><div className="eyebrow">Private workspace</div><h1>Settle in, <em>admin.</em></h1><p>Sign in with Discord to see your Niko profile and manage the servers you look after.</p>
    {auth.oauth_available ? <a className="button button-primary full-width" href="/auth/login?next=/dashboard"><Icon name="lock" /> Continue with Discord <Icon name="arrow" /></a> : <div className="notice warning">Discord login is not configured yet. Add <code>DISCORD_CLIENT_SECRET</code> to the environment and restart the bot.</div>}
    {!config && <p className="form-hint">The public bot configuration is still loading.</p>}
    <a className="back-link" href="/" onClick={(e) => { e.preventDefault(); navigate("/"); }}>Return to public site</a>
  </div></main></>;
}

/** How often the overview's analytics refresh themselves while it is open. */
const OVERVIEW_POLL_MS = 10_000;
/** The personal pages refresh on the same rhythm as the guild analytics card. */
const PERSONAL_POLL_MS = 10_000;

function DashboardSection({ section, guild, stats, csrfToken, refreshToken }: { section: DashSection; guild: Guild; stats: BotStats | null; csrfToken?: string; refreshToken: number }) {
  const [overview, setOverview] = useState<GuildOverview | null>(null);
  const [levels, setLevels] = useState<LevelRow[]>([]);
  const [config, setConfig] = useState<GuildConfig | null>(null);
  const [resources, setResources] = useState<GuildResources | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const overviewRef = useRef<GuildOverview | null>(null);

  useEffect(() => {
    let active = true;
    let inFlight = false;
    setLoading(true); setError("");
    overviewRef.current = null;

    // The overview holds the analytics cards, so it refreshes on its own while
    // the tab is open: the first paint still shows the skeleton, later polls
    // swap the numbers in place.
    if (section === "overview") {
      const loadOverview = async (background: boolean) => {
        if (!active || inFlight) return;
        if (background && document.visibilityState === "hidden") return;
        inFlight = true;
        try {
          const value = await getOverview(guild.id);
          if (!active) return;
          overviewRef.current = value;
          setOverview(value);
          setError("");
        } catch (reason) {
          if (!active) return;
          // A failed refresh keeps the last snapshot on screen; only the first
          // load replaces the page with an error.
          if (!background || !overviewRef.current) setError(reason instanceof Error ? reason.message : "This server could not be loaded.");
        } finally {
          inFlight = false;
          if (active) setLoading(false);
        }
      };
      void loadOverview(false);
      const timer = window.setInterval(() => void loadOverview(true), OVERVIEW_POLL_MS);
      const onVisibilityChange = () => { if (document.visibilityState === "visible") void loadOverview(true); };
      document.addEventListener("visibilitychange", onVisibilityChange);
      return () => {
        active = false;
        window.clearInterval(timer);
        document.removeEventListener("visibilitychange", onVisibilityChange);
      };
    }

    const request = section === "leveling"
      ? Promise.all([getLevels(guild.id), getConfig(guild.id), getResources(guild.id)]).then(([rows, value, available]) => { setLevels(rows); setConfig(value); setResources(available); })
      : section === "applications"
          ? getResources(guild.id).then(setResources)
          : Promise.all([getConfig(guild.id), getResources(guild.id)]).then(([value, available]) => { setConfig(value); setResources(available); });
    request.catch((reason) => setError(reason instanceof Error ? reason.message : "This server could not be loaded.")).finally(() => setLoading(false));
    return () => { active = false; };
  }, [guild.id, section, refreshToken]);

  if (loading) return <div className="section-loading section-skeleton" role="status" aria-label={`Loading ${section}`}>
    <div className="skeleton-title" /><div className="skeleton-copy" />
    <div className="skeleton-grid"><i /><i /><i /></div>
    <span>Loading {section}...</span>
  </div>;
  if (error) return <div className="inline-error" role="alert"><strong>Couldn’t load this page.</strong><span>{error}</span><button className="button button-muted" onClick={() => window.location.reload()}>Try again</button></div>;
  if (section === "overview" && overview) return <OverviewView overview={overview} />;
  if (section === "leveling") return <LevelingView guildId={guild.id} rows={levels} config={config} resources={resources} csrfToken={csrfToken} />;
  if (section === "moderation") return <ModerationView guildId={guild.id} config={config} csrfToken={csrfToken} />;
  if (section === "server") return <ServerSettingsView guildId={guild.id} config={config} resources={resources} csrfToken={csrfToken} />;
  if (section === "onboarding") return <OnboardingView guildId={guild.id} config={config} resources={resources} csrfToken={csrfToken} />;
  if (section === "tickets") return <TicketsView guildId={guild.id} config={config} resources={resources} csrfToken={csrfToken} />;
  if (section === "notifications") return <NotifierView guildId={guild.id} resources={resources} csrfToken={csrfToken} />;
  if (section === "applications") return <StaffApplicationsView guildId={guild.id} resources={resources} csrfToken={csrfToken} />;
  if (section === "customization") return <CustomizationSettings guildId={guild.id} config={config} csrfToken={csrfToken} />;
  return <AiView guildId={guild.id} config={config} csrfToken={csrfToken} />;
}

function SectionSkeleton({ label }: { label: string }) {
  return <div className="section-loading section-skeleton" role="status" aria-label={`Loading ${label}`}>
    <div className="skeleton-title" /><div className="skeleton-copy" />
    <div className="skeleton-grid"><i /><i /><i /></div>
    <span>Loading {label}...</span>
  </div>;
}

function SectionError({ message }: { message: string }) {
  return <div className="inline-error" role="alert"><strong>Couldn’t load this page.</strong><span>{message}</span><button className="button button-muted" onClick={() => window.location.reload()}>Try again</button></div>;
}

/**
 * The personal tabs under My overview. The economy and achievements are global
 * per Discord account, so they load from `/api/me/*` and never need a server.
 * Each tab keeps itself current while it is open, like the guild analytics card.
 */
function UserSection({ tab, user, overview, guilds, guildsUnavailable, csrfToken, refreshToken, onServers, onManage }: {
  tab: UserTab;
  user: User;
  overview: UserOverview | null;
  guilds: Guild[];
  guildsUnavailable: string;
  csrfToken?: string;
  refreshToken: number;
  onServers: () => void;
  onManage: (guild: Guild) => void;
}) {
  const economy = useLiveResource<EconomyStanding>("personal-economy", getMyEconomy, { enabled: tab === "economy", refreshKey: refreshToken });
  const achievements = useLiveResource<AchievementsResponse>("personal-achievements", getMyAchievements, { enabled: tab === "achievements", refreshKey: refreshToken });

  if (tab === "overview") {
    if (!overview) return <SectionSkeleton label="overview" />;
    return <UserOverviewView user={user} overview={overview} guilds={guilds} onServers={onServers} onManage={onManage} csrfToken={csrfToken} guildsUnavailable={guildsUnavailable} />;
  }
  if (tab === "economy") {
    if (economy.error) return <SectionError message={economy.error} />;
    if (economy.loading && !economy.data) return <SectionSkeleton label="economy" />;
    return economy.data ? <EconomyView standing={economy.data} /> : null;
  }
  if (tab === "achievements") {
    if (achievements.error) return <SectionError message={achievements.error} />;
    if (achievements.loading && !achievements.data) return <SectionSkeleton label="achievements" />;
    return achievements.data ? <AchievementsView achievements={achievements.data} /> : null;
  }
  return null;
}

function BlacklistAppealScreen({ scope, reason, guildId, guildName, supportUrl, embedded = false }: { scope: "user" | "guild"; reason?: string | null; guildId?: string; guildName?: string; supportUrl?: string | null; embedded?: boolean }) {
  const safeSupportUrl = supportUrl?.trim();
  const [appealable, setAppealable] = useState<boolean | null>(scope !== "guild");
  useEffect(() => {
    if (scope !== "guild" || !guildId) return;
    let active = true;
    setAppealable(null);
    getGuildBlacklistAppealStatus(guildId)
      .then((status) => { if (active) setAppealable(status.can_appeal); })
      .catch(() => { if (active) setAppealable(false); });
    return () => { active = false; };
  }, [guildId, scope]);
  return <>{!embedded && <PublicHeader page="dashboard" />}<div className={`auth-page blacklist-appeal-page${embedded ? " blacklist-appeal-embedded" : ""}`}><section className="auth-card blacklist-appeal-card" role="alert"><span className="blacklist-appeal-mark"><Icon name="lock" /></span><div className="eyebrow">Dashboard access restricted</div><h1>{scope === "guild" ? "This server is blacklisted." : "This account is blacklisted."}</h1><p>{scope === "guild" ? `${guildName || "This server"} can’t use Niko’s dashboard or bot features right now.` : "This Discord account can’t access Niko’s dashboard or bot features right now."}</p><div className="blacklist-appeal-reason"><span className="panel-kicker">Reason for the restriction</span><p>{reason?.trim() || "No reason was recorded. Contact the support team for clarification."}</p></div><p className="blacklist-appeal-note">If you believe this restriction was made in error, submit an appeal directly to the Niko team. You don’t need to join the support server.</p>{scope === "user" ? <a className="button button-primary full-width" href="/appeals/blacklist">Appeal this blacklist <Icon name="arrow" /></a> : appealable ? <a className="button button-primary full-width" href={`/appeals/blacklist?guild_id=${encodeURIComponent(guildId || "")}`}>Appeal this server blacklist <Icon name="arrow" /></a> : <button type="button" className="button button-muted full-width" disabled>{appealable === null ? "Checking appeal eligibility…" : "This guild blacklist cannot be appealed"}</button>}{safeSupportUrl && <a className="back-link" href={safeSupportUrl} target="_blank" rel="noreferrer">Or visit the support server <Icon name="external" /></a>}{!embedded && <a className="back-link" href="/" onClick={(event) => { event.preventDefault(); navigate("/"); }}>Return to the public site</a>}</section></div></>;
}

function DashboardLoading() {
  return <div className="section-loading section-skeleton dashboard-loading" role="status">
    <div className="skeleton-title" /><div className="skeleton-copy" /><div className="skeleton-grid"><i /><i /><i /></div>
    <span>Preparing your dashboard...</span>
  </div>;
}

/**
 * Read the manageable server list without letting a Discord hiccup take the
 * dashboard down: a failed read keeps the workspace usable and reports itself
 * on the servers view, which is the only place the list is shown in full.
 */
function loadGuilds(): Promise<{ guilds: Guild[]; error: string; expired: boolean }> {
  return getGuilds().then(
    (guilds) => ({ guilds, error: "", expired: false }),
    (reason: unknown) => ({
      guilds: [] as Guild[],
      error: reason instanceof Error ? reason.message : "Your server list could not be loaded.",
      // A 401 means Discord rejected the session token and it could not be
      // refreshed: retrying changes nothing until the reader signs in again.
      expired: reason instanceof ApiError && reason.status === 401,
    }),
  );
}

export function DashboardPage() {
  const config = useBotConfig();
  const [route, setRoute] = useState(dashboardRoute);
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [stats, setStats] = useState<BotStats | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [guildsError, setGuildsError] = useState("");
  const [guildsExpired, setGuildsExpired] = useState(false);
  const [selectedGuild, setSelectedGuild] = useState<Guild | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [blacklist, setBlacklist] = useState<{ blacklisted: boolean; scope?: "user"; reason?: string } | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [staffRole, setStaffRole] = useState<string | null>(null);
  // The personal tabs share one account-wide snapshot; it stays current while a
  // personal page is open and pauses as soon as the reader moves to a server.
  const personalOverview = useLiveResource<UserOverview>("personal-overview", getUserOverview, {
    enabled: Boolean(auth?.authenticated) && route.view === "overview",
    intervalMs: PERSONAL_POLL_MS,
    fallbackError: "Your profile could not be loaded.",
  });

  useEffect(() => {
    const handleRoute = () => setRoute(dashboardRoute());
    window.addEventListener("popstate", handleRoute);
    return () => window.removeEventListener("popstate", handleRoute);
  }, []);

  useEffect(() => {
    setLoading(true);
    Promise.all([getAuth(), getStats()])
      .then(([authStatus, botStats]) => {
        setAuth(authStatus);
        setStats(botStats);
        if (!authStatus.authenticated) return null;
        return getDashboardAccess().then((access) => {
          setBlacklist(access);
          if (access.blacklisted) return null;
          return Promise.all([loadGuilds(), getStaffMe().catch(() => null)]).then(([available, staffStatus]) => {
            setGuilds(available.guilds);
            setGuildsError(available.error);
            setGuildsExpired(available.expired);
            setStaffRole(staffStatus?.role || null);
          });
        });
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Dashboard unavailable"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (route.view !== "guild") {
      setSelectedGuild(null);
      return;
    }
    const selected = guilds.find((guild) => guild.id === route.guildId && guild.installed !== false);
    if (selected) {
      setSelectedGuild(selected);
      localStorage.setItem("niko-guild", selected.id);
    } else if (route.guildId && guilds.length) {
      navigate(dashboardServersPath());
    }
  }, [guilds, route.guildId, route.view]);

  if (loading || !auth) return <div className="dashboard-state"><div className="loading-ring" /><p>Connecting to Niko…</p></div>;
  if (error) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><span className="auth-mark">!</span><div className="eyebrow">Connection issue</div><h1>Couldn’t load<br /><em>your workspace.</em></h1><p>{error}</p><button className="button button-primary" onClick={() => window.location.reload()}>Try again <Icon name="arrow" /></button></div></main></>;
  if (!auth.authenticated) return <AuthCard auth={auth} />;
  if (blacklist?.blacklisted) {
    return <BlacklistAppealScreen scope="user" reason={blacklist.reason} supportUrl={config?.support_server_url} />;
  }

  const changeGuild = (guild: Guild) => {
    if (guild.installed === false) return;
    localStorage.setItem("niko-guild", guild.id);
    navigate(dashboardPath(guild.id, route.section));
  };
  const openGuild = (guild: Guild) => {
    if (guild.installed === false) return;
    localStorage.setItem("niko-guild", guild.id);
    navigate(dashboardPath(guild.id, "overview"));
  };
  const changeSection = (section: DashSection) => {
    if (selectedGuild) navigate(dashboardPath(selectedGuild.id, section));
    else navigate(dashboardPath());
  };
  const goHome = () => navigate(dashboardUserPath("overview"));
  const goServers = () => navigate(dashboardServersPath());
  const changeUserTab = (tab: UserTab) => navigate(dashboardUserPath(tab));
  const refreshDashboard = async () => {
    if (refreshing) return;
    setRefreshing(true);
    try {
      const [authStatus, botStats] = await Promise.all([getAuth(), getStats()]);
      setAuth(authStatus);
      setStats(botStats);
      if (authStatus.authenticated) {
        const access = await getDashboardAccess();
        setBlacklist(access);
        if (!access.blacklisted) {
          const [available, staffStatus] = await Promise.all([loadGuilds(), getStaffMe().catch(() => null)]);
          setGuilds(available.guilds);
          setGuildsError(available.error);
          setGuildsExpired(available.expired);
          setStaffRole(staffStatus?.role || null);
        }
      }
      personalOverview.refresh();
      setRefreshToken((value) => value + 1);
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Dashboard refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  let content;
  if (route.view === "servers") {
    content = <ServersView guilds={guilds} onManage={openGuild} unavailable={guildsError} onRetry={refreshDashboard} retrying={refreshing} loginUrl={guildsExpired ? `/auth/login?next=${encodeURIComponent(window.location.pathname + window.location.search)}` : ""} />;
  } else if (route.view === "guild") {
    content = selectedGuild
      ? selectedGuild.blacklisted
        ? <BlacklistAppealScreen scope="guild" guildId={selectedGuild.id} guildName={selectedGuild.name} reason={selectedGuild.blacklist_reason || undefined} supportUrl={config?.support_server_url} embedded />
        : <DashboardSection key={`${selectedGuild.id}-${route.section}`} section={route.section} guild={selectedGuild} stats={stats} csrfToken={auth.csrf_token} refreshToken={refreshToken} />
      : <DashboardLoading />;
  } else {
    content = <UserSection key={route.tab} tab={route.tab} user={auth.user!} overview={personalOverview.data} guilds={guilds} guildsUnavailable={guildsError} csrfToken={auth.csrf_token} refreshToken={refreshToken} onServers={goServers} onManage={openGuild} />;
  }

  return <DashboardShell user={auth.user!} guilds={guilds} selectedGuild={selectedGuild} view={route.view as DashboardView} section={route.section} userTab={route.tab} stats={stats} onHome={goHome} onServers={goServers} onGuildChange={changeGuild} onSectionChange={changeSection} onUserTabChange={changeUserTab} onRefresh={refreshDashboard} refreshing={refreshing} staffRole={staffRole}>
    {content}
  </DashboardShell>;
}