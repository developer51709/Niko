import { useEffect, useRef, useState } from "react";
import { ApiError, getAuth, getBoosterSettings, getConfig, getDashboardAccess, getGuildBlacklistAppealStatus, getGuilds, getLevels, getMyAchievements, getMyEconomy, getMyReferrals, getOverview, getResources, getStats, getUserOverview, getStaffMe } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { AiView, CustomizationSettings, ModerationView, OnboardingView, TicketsView } from "../components/dashboard/SettingsViews";
import { ServerSettingsView } from "../components/dashboard/ServerSettingsView";
import { StaffApplicationsView } from "../components/dashboard/StaffApplicationsView";
import { NotifierView } from "../components/dashboard/NotifierView";
import { BoostersView } from "../components/dashboard/BoostersView";
import { LevelingView, OverviewView, SectionSkeleton, ServersView, UserOverviewView } from "../components/dashboard/DashboardViews";
import { AchievementsView } from "../components/dashboard/AchievementsView";
import { EconomyView } from "../components/dashboard/EconomyView";
import { AuthBackLink, AuthScreen, DiscordSignIn } from "../components/AuthScreen";
import { useBotConfig } from "../hooks/useBotConfig";
import { useLiveResource } from "../hooks/useLiveResource";
import { useStrings } from "../i18n";
import type { PublicConfig } from "../types";
import { dashboardPath, dashboardRoute, dashboardServersPath, dashboardUserPath, navigate, siteHref, type DashboardView, type DashSection, type UserTab } from "../router";
import type { AchievementsResponse, AuthStatus, BotStats, BoosterSettings, EconomyStanding, Guild, GuildConfig, GuildOverview, GuildResources, LevelRow, ReferralSummary, User, UserOverview } from "../types";
import { Icon } from "../components/Icon";

function AuthCard({ auth }: { auth: AuthStatus }) {
  const { t } = useStrings("dashboard");
  const config = useBotConfig();
  return <AuthScreen
    eyebrow={t("auth.eyebrow")}
    title={<>{t("auth.titleBefore")} <em>{t("auth.titleEmphasis")}</em></>}
    description={t("auth.description")}
    back={{ label: t("auth.back"), href: siteHref("/"), onClick: () => navigate("/") }}
  >
    <DiscordSignIn
      next="/dashboard"
      available={auth.oauth_available}
      unavailableNotice={<>{t("auth.notConfiguredBefore")} <code>DISCORD_CLIENT_SECRET</code> {t("auth.notConfiguredAfter")}</>}
    />
    {!config && <p className="form-hint">{t("auth.configLoading")}</p>}
  </AuthScreen>;
}

/** How often the overview's analytics refresh themselves while it is open. */
const OVERVIEW_POLL_MS = 10_000;
/** The personal pages refresh on the same rhythm as the guild analytics card. */
const PERSONAL_POLL_MS = 10_000;

function DashboardSection({ section, guild, stats, csrfToken, refreshToken }: { section: DashSection; guild: Guild; stats: BotStats | null; csrfToken?: string; refreshToken: number }) {
  const { t } = useStrings("dashboard");
  const [overview, setOverview] = useState<GuildOverview | null>(null);
  const [levels, setLevels] = useState<LevelRow[]>([]);
  const [config, setConfig] = useState<GuildConfig | null>(null);
  const [resources, setResources] = useState<GuildResources | null>(null);
  const [boosterSettings, setBoosterSettings] = useState<BoosterSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [loadAttempt, setLoadAttempt] = useState(0);
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
          if (!background || !overviewRef.current) setError(reason instanceof Error ? reason.message : t("load.server"));
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

    const request = section === "boosters"
      ? Promise.all([getBoosterSettings(guild.id), getResources(guild.id)]).then(([boosterResult, available]) => {
          setBoosterSettings(boosterResult.config);
          setResources(available);
        })
      : section === "leveling"
      ? Promise.all([getLevels(guild.id), getConfig(guild.id), getResources(guild.id)]).then(([rows, value, available]) => { setLevels(rows); setConfig(value); setResources(available); })
      : section === "applications"
          ? getResources(guild.id).then(setResources)
          : Promise.all([getConfig(guild.id), getResources(guild.id)]).then(([value, available]) => { setConfig(value); setResources(available); });
    request.catch((reason) => setError(reason instanceof Error ? reason.message : "This server could not be loaded.")).finally(() => setLoading(false));
    return () => { active = false; };
  }, [guild.id, section, refreshToken, loadAttempt]);

  if (loading) return <SectionSkeleton label={section} />;
  if (error) return <div className="inline-error" role="alert"><strong>Couldn’t load this page.</strong><span>{error}</span><button className="button button-muted" type="button" onClick={() => setLoadAttempt((attempt) => attempt + 1)}>Try again</button></div>;
  if (section === "overview" && overview) return <OverviewView overview={overview} />;
  if (section === "leveling") return <LevelingView guildId={guild.id} rows={levels} config={config} resources={resources} csrfToken={csrfToken} />;
  if (section === "moderation") return <ModerationView guildId={guild.id} config={config} csrfToken={csrfToken} />;
  if (section === "server") return <ServerSettingsView guildId={guild.id} config={config} resources={resources} csrfToken={csrfToken} />;
  if (section === "onboarding") return <OnboardingView guildId={guild.id} config={config} resources={resources} csrfToken={csrfToken} />;
  if (section === "tickets") return <TicketsView guildId={guild.id} config={config} resources={resources} csrfToken={csrfToken} />;
  if (section === "notifications") return <NotifierView guildId={guild.id} resources={resources} csrfToken={csrfToken} />;
  if (section === "boosters") return <BoostersView guildId={guild.id} resources={resources} csrfToken={csrfToken} initialSettings={boosterSettings} />;
  if (section === "applications") return <StaffApplicationsView guildId={guild.id} resources={resources} csrfToken={csrfToken} />;
  if (section === "customization") return <CustomizationSettings guildId={guild.id} config={config} csrfToken={csrfToken} />;
  return <AiView guildId={guild.id} config={config} csrfToken={csrfToken} />;
}

function SectionError({ message, onRetry }: { message: string; onRetry: () => void }) {
  const { t } = useStrings("dashboard");
  return <div className="inline-error" role="alert"><strong>{t("sectionError.title")}</strong><span>{message}</span><button className="button button-muted" type="button" onClick={onRetry}>{t("sectionError.retry")}</button></div>;
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
  // The referral card sits on the overview, so its link is fetched there; the
  // card still renders while the bot mints the invite behind it.
  const referrals = useLiveResource<ReferralSummary>("personal-referrals", getMyReferrals, { enabled: tab === "overview", refreshKey: refreshToken });

  if (tab === "overview") {
    if (!overview) return <SectionSkeleton label="overview" />;
    return <UserOverviewView user={user} overview={overview} guilds={guilds} referrals={referrals.data} onServers={onServers} onManage={onManage} csrfToken={csrfToken} guildsUnavailable={guildsUnavailable} />;
  }
  if (tab === "economy") {
    if (economy.error) return <SectionError message={economy.error} onRetry={economy.refresh} />;
    if (economy.loading && !economy.data) return <SectionSkeleton label="economy" />;
    return economy.data ? <EconomyView standing={economy.data} /> : null;
  }
  if (tab === "achievements") {
    if (achievements.error) return <SectionError message={achievements.error} onRetry={achievements.refresh} />;
    if (achievements.loading && !achievements.data) return <SectionSkeleton label="achievements" />;
    return achievements.data ? <AchievementsView achievements={achievements.data} /> : null;
  }
  return null;
}

function BlacklistAppealScreen({ scope, reason, guildId, guildName, supportUrl, embedded = false }: { scope: "user" | "guild"; reason?: string | null; guildId?: string; guildName?: string; supportUrl?: string | null; embedded?: boolean }) {
  const { t } = useStrings("dashboard");
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
  return <AuthScreen
    header={!embedded}
    pageClassName={`blacklist-appeal-page${embedded ? " blacklist-appeal-embedded" : ""}`}
    cardClassName="blacklist-appeal-card"
    role="alert"
    mark={<Icon name="lock" />}
    markClassName="blacklist-appeal-mark"
    eyebrow={t("auth.restrictedEyebrow")}
    title={scope === "guild" ? t("auth.guildBlacklisted") : t("auth.accountBlacklisted")}
    description={scope === "guild" ? t("auth.guildBlacklistedText", { server: guildName || t("auth.thisServer") }) : t("auth.accountBlacklistedText")}
  >
    <div className="blacklist-appeal-reason"><span className="panel-kicker">{t("auth.reasonKicker")}</span><p>{reason?.trim() || t("auth.noReason")}</p></div>
    <p className="blacklist-appeal-note">{t("auth.appealNote")}</p>
    {scope === "user" ? <a className="button button-primary full-width" href={siteHref("/appeals/blacklist")}>{t("auth.appealUser")} <Icon name="arrow" /></a> : appealable ? <a className="button button-primary full-width" href={siteHref(`/appeals/blacklist?guild_id=${encodeURIComponent(guildId || "")}`)}>{t("auth.appealGuild")} <Icon name="arrow" /></a> : <button type="button" className="button button-muted full-width" disabled>{t(appealable === null ? "auth.checkingEligibility" : "auth.notAppealable")}</button>}
    {safeSupportUrl && <AuthBackLink label={<>{t("auth.orSupport")} <Icon name="external" /></>} href={safeSupportUrl} external />}
    {!embedded && <AuthBackLink label={t("auth.backPublic")} href={siteHref("/")} onClick={() => navigate("/")} />}
  </AuthScreen>;
}

function DashboardLoading() {
  const { t } = useStrings("dashboard");
  return <div className="section-loading section-skeleton dashboard-loading" role="status">
    <div className="skeleton-title" /><div className="skeleton-copy" /><div className="skeleton-grid"><i /><i /><i /></div>
    <span>{t("auth.preparing")}</span>
  </div>;
}

/**
 * Read the manageable server list without letting a Discord hiccup take the
 * dashboard down: a failed read keeps the workspace usable and reports itself
 * on the servers view, which is the only place the list is shown in full.
 */
function loadGuilds(t: (key: string) => string): Promise<{ guilds: Guild[]; error: string; expired: boolean }> {
  return getGuilds().then(
    (guilds) => ({ guilds, error: "", expired: false }),
    (reason: unknown) => ({
      guilds: [] as Guild[],
      error: reason instanceof Error ? reason.message : t("load.guilds"),
      // A 401 means Discord rejected the session token and it could not be
      // refreshed: retrying changes nothing until the reader signs in again.
      expired: reason instanceof ApiError && reason.status === 401,
    }),
  );
}

export function DashboardPage() {
  const { t } = useStrings("dashboard");
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
    fallbackError: t("load.profile"),
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
          return Promise.all([loadGuilds(t), getStaffMe().catch(() => null)]).then(([available, staffStatus]) => {
            setGuilds(available.guilds);
            setGuildsError(available.error);
            setGuildsExpired(available.expired);
            setStaffRole(staffStatus?.role || null);
          });
        });
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : t("load.dashboardFailed")))
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

  if (loading || !auth) return <div className="dashboard-state"><div className="loading-ring" /><p>{t("auth.connecting")}</p></div>;
  if (error) return <AuthScreen
    mark="!"
    eyebrow={t("auth.connectionEyebrow")}
    title={<>{t("auth.connectionTitle")}<br /><em>{t("auth.connectionEmphasis")}</em></>}
    description={error}
    back={{ label: t("auth.back"), href: siteHref("/"), onClick: () => navigate("/") }}
  >
    <button className="button button-primary full-width" onClick={() => window.location.reload()}>{t("auth.tryAgain")} <Icon name="arrow" /></button>
  </AuthScreen>;
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
          const [available, staffStatus] = await Promise.all([loadGuilds(t), getStaffMe().catch(() => null)]);
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
      setError(reason instanceof Error ? reason.message : t("load.refreshFailed"));
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