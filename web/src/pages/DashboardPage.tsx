import { useEffect, useState } from "react";
import { getAuth, getConfig, getEconomy, getGuilds, getLevels, getOverview, getResources } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { AiView, ModerationView } from "../components/dashboard/SettingsViews";
import { EconomyView, LevelingView, OverviewView } from "../components/dashboard/DashboardViews";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import { dashboardPath, dashboardRoute, navigate, type DashSection } from "../router";
import type { AuthStatus, BotStats, Guild, GuildConfig, GuildOverview, GuildResources, EconomyRow, LevelRow } from "../types";
import { displayName, initials } from "../utils/format";
import { Icon } from "../components/Icon";

function AuthCard({ auth }: { auth: AuthStatus }) {
  const config = useBotConfig();
  return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card">
    <span className="auth-mark">n</span><div className="eyebrow">Private workspace</div><h1>Settle in, <em>admin.</em></h1><p>Sign in with Discord to view server insights and manage Niko’s settings.</p>
    {auth.oauth_available ? <a className="button button-primary full-width" href="/auth/login?next=/dashboard"><Icon name="lock" /> Continue with Discord <Icon name="arrow" /></a> : <div className="notice warning">Discord login is not configured yet. Add <code>DISCORD_CLIENT_SECRET</code> to the environment and restart the bot.</div>}
    {!config && <p className="form-hint">The public bot configuration is still loading.</p>}
    <a className="back-link" href="/" onClick={(e) => { e.preventDefault(); navigate("/"); }}>Return to public site</a>
  </div></main></>;
}

function DashboardSection({ section, guild, stats, csrfToken }: { section: DashSection; guild: Guild; stats: BotStats | null; csrfToken?: string }) {
  const [overview, setOverview] = useState<GuildOverview | null>(null);
  const [economy, setEconomy] = useState<EconomyRow[]>([]);
  const [levels, setLevels] = useState<LevelRow[]>([]);
  const [config, setConfig] = useState<GuildConfig | null>(null);
  const [resources, setResources] = useState<GuildResources | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true); setError("");
    const request = section === "overview"
      ? getOverview(guild.id).then(setOverview)
      : section === "economy"
        ? getEconomy(guild.id).then(setEconomy)
        : section === "leveling"
          ? Promise.all([getLevels(guild.id), getConfig(guild.id), getResources(guild.id)]).then(([rows, value, available]) => { setLevels(rows); setConfig(value); setResources(available); })
          : Promise.all([getConfig(guild.id), getResources(guild.id)]).then(([value, available]) => { setConfig(value); setResources(available); });
    request.catch((reason) => setError(reason instanceof Error ? reason.message : "This server could not be loaded.")).finally(() => setLoading(false));
  }, [guild.id, section]);

  if (loading) return <div className="section-loading" role="status"><div className="loading-ring" /><span>Loading {section}…</span></div>;
  if (error) return <div className="inline-error" role="alert"><strong>Couldn’t load this page.</strong><span>{error}</span><button className="button button-muted" onClick={() => window.location.reload()}>Try again</button></div>;
  if (section === "overview" && overview) return <OverviewView overview={overview} stats={stats} />;
  if (section === "economy") return <EconomyView rows={economy} />;
  if (section === "leveling") return <LevelingView guildId={guild.id} rows={levels} config={config} resources={resources} csrfToken={csrfToken} />;
  if (section === "moderation") return <ModerationView guildId={guild.id} config={config} csrfToken={csrfToken} />;
  return <AiView guildId={guild.id} config={config} csrfToken={csrfToken} />;
}

export function DashboardPage() {
  const config = useBotConfig();
  const [route, setRoute] = useState(dashboardRoute);
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [stats, setStats] = useState<BotStats | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [selectedGuild, setSelectedGuild] = useState<Guild | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const handleRoute = () => setRoute(dashboardRoute());
    window.addEventListener("popstate", handleRoute);
    return () => window.removeEventListener("popstate", handleRoute);
  }, []);

  useEffect(() => {
    Promise.all([getAuth(), fetch("/api/botstats").then((response) => response.json() as Promise<BotStats>)])
      .then(([authStatus, botStats]) => {
        setAuth(authStatus); setStats(botStats);
        if (authStatus.authenticated) return getGuilds().then(setGuilds);
        return undefined;
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Dashboard unavailable"));
  }, []);

  useEffect(() => {
    if (!guilds.length) return;
    const remembered = localStorage.getItem("niko-guild");
    const selected = guilds.find((guild) => guild.id === route.guildId) || guilds.find((guild) => guild.id === remembered) || guilds[0];
    setSelectedGuild(selected);
    if (!route.guildId || !guilds.some((guild) => guild.id === route.guildId)) navigate(dashboardPath(selected.id, route.section));
  }, [guilds, route.guildId, route.section]);

  if (!auth && !error) return <div className="dashboard-state"><div className="loading-ring" /><p>Connecting to Niko…</p></div>;
  if (error || !auth) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><span className="auth-mark">!</span><div className="eyebrow">Connection issue</div><h1>Couldn’t load<br /><em>your workspace.</em></h1><p>{error || "The dashboard is unavailable."}</p><button className="button button-primary" onClick={() => window.location.reload()}>Try again <Icon name="arrow" /></button></div></main></>;
  if (!auth.authenticated) return <AuthCard auth={auth} />;
  if (!guilds.length) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><span className="auth-mark">n</span><div className="eyebrow">No workspace yet</div><h1>No managed<br /><em>servers found.</em></h1><p>Niko needs to be in a server where your Discord account has Manage Server permission, and Niko must already be installed there.</p><a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">Invite Niko <Icon name="arrow" /></a></div></main></>;

  const changeGuild = (guild: Guild) => { localStorage.setItem("niko-guild", guild.id); navigate(dashboardPath(guild.id, route.section)); };
  const changeSection = (section: DashSection) => { if (selectedGuild) navigate(dashboardPath(selectedGuild.id, section)); };
  return <DashboardShell user={auth.user!} guilds={guilds} selectedGuild={selectedGuild} section={route.section} stats={stats} onGuildChange={changeGuild} onSectionChange={changeSection}>
    {selectedGuild && <DashboardSection key={`${selectedGuild.id}-${route.section}`} section={route.section} guild={selectedGuild} stats={stats} csrfToken={auth.csrf_token} />}
  </DashboardShell>;
}