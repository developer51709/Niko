import { useEffect, useState } from "react";
import { getAuth, getConfig, getGuilds, getLevels, getOverview, getResources, getStats, getUserOverview } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { AiView, ModerationView } from "../components/dashboard/SettingsViews";
import { ServerSettingsView } from "../components/dashboard/ServerSettingsView";
import { LevelingView, OverviewView, ServersView, UserOverviewView } from "../components/dashboard/DashboardViews";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import { dashboardPath, dashboardRoute, dashboardServersPath, navigate, type DashboardView, type DashSection } from "../router";
import type { AuthStatus, BotStats, Guild, GuildConfig, GuildOverview, GuildResources, LevelRow, UserOverview } from "../types";
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

function DashboardSection({ section, guild, stats, csrfToken }: { section: DashSection; guild: Guild; stats: BotStats | null; csrfToken?: string }) {
  const [overview, setOverview] = useState<GuildOverview | null>(null);
  const [levels, setLevels] = useState<LevelRow[]>([]);
  const [config, setConfig] = useState<GuildConfig | null>(null);
  const [resources, setResources] = useState<GuildResources | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true); setError("");
      const request = section === "overview"
      ? getOverview(guild.id).then(setOverview)
      : section === "leveling"
          ? Promise.all([getLevels(guild.id), getConfig(guild.id), getResources(guild.id)]).then(([rows, value, available]) => { setLevels(rows); setConfig(value); setResources(available); })
          : Promise.all([getConfig(guild.id), getResources(guild.id)]).then(([value, available]) => { setConfig(value); setResources(available); });
    request.catch((reason) => setError(reason instanceof Error ? reason.message : "This server could not be loaded.")).finally(() => setLoading(false));
  }, [guild.id, section]);

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
  return <AiView guildId={guild.id} config={config} csrfToken={csrfToken} />;
}

function DashboardLoading() {
  return <div className="section-loading section-skeleton dashboard-loading" role="status">
    <div className="skeleton-title" /><div className="skeleton-copy" /><div className="skeleton-grid"><i /><i /><i /></div>
    <span>Preparing your dashboard...</span>
  </div>;
}

export function DashboardPage() {
  const config = useBotConfig();
  const [route, setRoute] = useState(dashboardRoute);
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [stats, setStats] = useState<BotStats | null>(null);
  const [userOverview, setUserOverview] = useState<UserOverview | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [selectedGuild, setSelectedGuild] = useState<Guild | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
        return Promise.all([getUserOverview(), getGuilds()]).then(([profile, availableGuilds]) => {
          setUserOverview(profile);
          setGuilds(availableGuilds);
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
  const goHome = () => navigate(dashboardPath());
  const goServers = () => navigate(dashboardServersPath());

  let content;
  if (route.view === "servers") {
    content = <ServersView guilds={guilds} onManage={openGuild} />;
  } else if (route.view === "guild") {
    content = selectedGuild
      ? <DashboardSection key={`${selectedGuild.id}-${route.section}`} section={route.section} guild={selectedGuild} stats={stats} csrfToken={auth.csrf_token} />
      : <DashboardLoading />;
  } else {
    content = <UserOverviewView user={auth.user!} overview={userOverview} guilds={guilds} onServers={goServers} onManage={openGuild} />;
  }

  return <DashboardShell user={auth.user!} guilds={guilds} selectedGuild={selectedGuild} view={route.view as DashboardView} section={route.section} stats={stats} onHome={goHome} onServers={goServers} onGuildChange={changeGuild} onSectionChange={changeSection}>
    {content}
  </DashboardShell>;
}