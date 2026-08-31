import { useEffect, useMemo, useState } from "react";
import {
  ApiError,
  getAuth,
  getCommands,
  getConfig,
  getEconomy,
  getGuilds,
  getLevels,
  getOverview,
  getStats,
  saveConfig,
} from "./api";
import type {
  AuthStatus,
  BotStats,
  Command,
  EconomyRow,
  Guild,
  GuildConfig,
  GuildOverview,
  LevelRow,
  User,
} from "./types";

type Page = "home" | "commands" | "docs" | "dashboard" | "privacy" | "terms";
type DashSection = "overview" | "economy" | "leveling" | "moderation" | "ai";

const pageFromPath = (): Page => {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";
  if (path === "/commands") return "commands";
  if (path === "/docs") return "docs";
  if (path === "/dashboard") return "dashboard";
  if (path === "/privacy") return "privacy";
  if (path === "/terms") return "terms";
  return "home";
};

const navigate = (path: string) => {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo({ top: 0, behavior: "smooth" });
};

function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", { notation: value > 9999 ? "compact" : "standard" }).format(value);
}

function displayName(user?: User | null) {
  return user?.global_name || user?.username || "there";
}

function initials(name: string) {
  return name.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
}

function Icon({ name }: { name: string }) {
  const paths: Record<string, string> = {
    arrow: "M5 12h14m-6-6 6 6-6 6",
    grid: "M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z",
    terminal: "m5 7 5 5-5 5m8 0h6",
    chart: "M4 19V5m0 14h16M8 16v-4m4 4V8m4 8v-7",
    shield: "M12 3 20 6v5c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6z",
    spark: "m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7z",
    users: "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m7-10a4 4 0 1 0 0-8 4 4 0 0 0 0 8m7-7a4 4 0 0 1 0 7.8M22 21v-2a4 4 0 0 0-3-3.9",
    settings: "M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7m0-12v2m0 13v2m9-8h-2M5 12H3m15.4-6.4-1.4 1.4M7 17l-1.4 1.4m12.8 0L17 17M7 7 5.6 5.6",
    book: "M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22zm0 0v16",
    external: "M14 4h6v6m-1-5-8 8m-7 4V6a2 2 0 0 1 2-2h5",
  };
  return (
    <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={paths[name] || paths.grid} />
    </svg>
  );
}

function Brand({ onNavigate }: { onNavigate?: () => void }) {
  return <a className="brand" href="/" onClick={(event) => { event.preventDefault(); onNavigate ? onNavigate() : navigate("/"); }}><span className="brand-mark">n</span><span>niko</span></a>;
}

function PublicHeader({ page }: { page: Page }) {
  return (
    <header className="site-header">
      <Brand />
      <nav className="site-nav" aria-label="Main navigation">
        <a className={page === "home" ? "active" : ""} href="/" onClick={(e) => { e.preventDefault(); navigate("/"); }}>Home</a>
        <a className={page === "commands" ? "active" : ""} href="/commands" onClick={(e) => { e.preventDefault(); navigate("/commands"); }}>Commands</a>
        <a className={page === "docs" ? "active" : ""} href="/docs" onClick={(e) => { e.preventDefault(); navigate("/docs"); }}>Docs</a>
      </nav>
      <div className="header-actions">
        <a className="button button-small button-muted" href="/dashboard" onClick={(e) => { e.preventDefault(); navigate("/dashboard"); }}>Dashboard <Icon name="arrow" /></a>
        <a className="button button-small button-primary" href="https://discord.com/oauth2/authorize?client_id=1520558530472448170&permissions=8&scope=bot%20applications.commands" target="_blank" rel="noreferrer">Add to Discord</a>
      </div>
    </header>
  );
}

function Footer() {
  return <footer className="site-footer"><Brand /><span>Built for communities that care.</span><div><a href="/privacy" onClick={(e) => { e.preventDefault(); navigate("/privacy"); }}>Privacy</a><a href="/terms" onClick={(e) => { e.preventDefault(); navigate("/terms"); }}>Terms</a><a href="https://github.com/developer51709/Niko" target="_blank" rel="noreferrer">GitHub</a></div></footer>;
}

function useStats() {
  const [stats, setStats] = useState<BotStats | null>(null);
  useEffect(() => { getStats().then(setStats).catch(() => undefined); }, []);
  return stats;
}

function HomePage() {
  const stats = useStats();
  const features = [
    ["spark", "AI that remembers", "Thoughtful conversation with a cozy personality and controls that respect your community."],
    ["chart", "A living economy", "Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],
    ["shield", "Confident moderation", "Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],
    ["users", "Community rituals", "Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."],
  ];
  return <><PublicHeader page="home" /><main>
    <section className="hero shell">
      <div className="hero-copy">
        <div className="eyebrow"><span className="status-dot" /> Discord companion · online</div>
        <h1>Make your server feel more <em>alive.</em></h1>
        <p>Niko brings warmth, useful tools, and a little café energy to the communities people choose to stay in.</p>
        <div className="hero-buttons"><a className="button button-primary" href="https://discord.com/oauth2/authorize?client_id=1520558530472448170&permissions=8&scope=bot%20applications.commands" target="_blank" rel="noreferrer">Invite Niko <Icon name="arrow" /></a><a className="button button-muted" href="/commands" onClick={(e) => { e.preventDefault(); navigate("/commands"); }}>Explore commands</a></div>
        <div className="stats-strip">
          <div><strong>{formatNumber(stats?.guild_count)}</strong><span>servers</span></div><div><strong>{formatNumber(stats?.user_count)}</strong><span>members</span></div><div><strong>{formatNumber(stats?.command_count)}</strong><span>commands</span></div>
        </div>
      </div>
      <div className="hero-art">
        <div className="orbit orbit-one" /><div className="orbit orbit-two" />
        <div className="coffee-orb"><span>n</span></div>
        <div className="floating-card card-top"><span className="mini-icon violet"><Icon name="spark" /></span><div><b>AI chat</b><small>“what are we brewing?”</small></div><span className="pulse-line" /></div>
        <div className="floating-card card-bottom"><span className="mini-icon green"><Icon name="chart" /></span><div><b>Community growth</b><small>+24% this month</small></div><span className="trend">↗</span></div>
        <div className="hero-stamp">EST.<br /><b>2024</b></div>
      </div>
    </section>
    <section className="shell intro-section"><div className="section-kicker">Why Niko</div><div className="intro-grid"><h2>The good kind of<br /><em>always-on.</em></h2><p>Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile.</p></div></section>
    <section className="shell feature-grid">{features.map(([icon, title, text]) => <article className="feature-card" key={title}><span className="feature-icon"><Icon name={icon} /></span><h3>{title}</h3><p>{text}</p><a href="/docs" onClick={(e) => { e.preventDefault(); navigate("/docs"); }}>Learn more <Icon name="arrow" /></a></article>)}</section>
    <section className="shell callout"><div><div className="section-kicker">Ready when you are</div><h2>A calmer, cleverer home<br />for your community.</h2></div><a className="button button-primary" href="https://discord.com/oauth2/authorize?client_id=1520558530472448170&permissions=8&scope=bot%20applications.commands" target="_blank" rel="noreferrer">Bring Niko in <Icon name="arrow" /></a></section>
  </main><Footer /></>;
}

function CommandsPage() {
  const [commands, setCommands] = useState<Command[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  useEffect(() => { getCommands().then(setCommands).catch(() => undefined); }, []);
  const categories = useMemo(() => ["all", ...Array.from(new Set(commands.map((command) => command.category))).sort()], [commands]);
  const filtered = commands.filter((command) => (category === "all" || command.category === category) && `${command.name} ${command.description}`.toLowerCase().includes(query.toLowerCase()));
  return <><PublicHeader page="commands" /><main className="shell page-main"><div className="page-heading"><div className="eyebrow">Reference library</div><h1>Everything Niko<br /><em>knows how to do.</em></h1><p>Browse the live command registry from the bot. Search by name, description, or category.</p></div><div className="command-toolbar"><label className="search-field"><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search commands" /></label><div className="filter-list">{categories.map((item) => <button className={category === item ? "filter active" : "filter"} key={item} onClick={() => setCategory(item)}>{item}</button>)}</div></div><div className="command-meta"><strong>{filtered.length}</strong> commands <span>·</span> updated from the connected bot</div><div className="commands-grid">{filtered.map((command) => <article className="command-card" key={`${command.category}-${command.name}`}><div className="command-name">/{command.name}</div><p>{command.description || "A Niko command for your server."}</p><span className="category-tag">{command.category}</span></article>)}{!filtered.length && <div className="empty-state">No commands match that search.</div>}</div></main><Footer /></>;
}

function DocsPage() {
  return <><PublicHeader page="docs" /><main className="shell page-main docs-page"><div className="page-heading"><div className="eyebrow">Documentation</div><h1>A clear starting point<br /><em>for every server.</em></h1><p>Niko is built to be approachable for members and manageable for moderators. Here are the paths people use most.</p></div><div className="docs-grid"><article><span className="docs-number">01</span><h2>Invite & configure</h2><p>Add Niko with the permissions your server needs, then open the setup panels from Discord. Admin configuration is permission-gated.</p><a className="text-link" href="https://discord.com/oauth2/authorize?client_id=1520558530472448170&permissions=8&scope=bot%20applications.commands" target="_blank" rel="noreferrer">Invite Niko <Icon name="external" /></a></article><article><span className="docs-number">02</span><h2>Build the room</h2><p>Use leveling, economy, tickets, polls, giveaways, and reminders to create repeatable rituals for your members.</p><a className="text-link" href="/commands" onClick={(e) => { e.preventDefault(); navigate("/commands"); }}>Browse commands <Icon name="arrow" /></a></article><article><span className="docs-number">03</span><h2>Keep it healthy</h2><p>Turn on automod, anti-raid, logs, and AI controls one at a time. Every setting can be revisited from Discord or the dashboard.</p><a className="text-link" href="/dashboard" onClick={(e) => { e.preventDefault(); navigate("/dashboard"); }}>Open dashboard <Icon name="arrow" /></a></article></div><div className="docs-note"><Icon name="book" /><div><strong>Want the implementation details?</strong><p>The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in <code>docs/</code>.</p></div></div></main><Footer /></>;
}

const legalCopy: Record<"privacy" | "terms", { title: string; intro: string; sections: [string, string][] }> = {
  privacy: {
    title: "Privacy policy",
    intro: "Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",
    sections: [
      ["Information we use", "User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],
      ["How it is used", "Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],
      ["Storage and retention", "Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],
      ["Third-party services", "When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],
      ["Your choices", "Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."],
    ],
  },
  terms: {
    title: "Terms of service",
    intro: "By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",
    sections: [
      ["Permitted use", "Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],
      ["Availability", "Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],
      ["Moderation", "The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],
      ["AI content", "AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],
      ["Virtual items", "In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],
      ["Contact", "Questions or concerns can be sent through the Niko support server."],
    ],
  },
};

function LegalPage({ type }: { type: "privacy" | "terms" }) {
  const content = legalCopy[type];
  return <><PublicHeader page={type} /><main className="shell page-main legal-page"><div className="page-heading"><div className="eyebrow">Niko legal</div><h1>{content.title}</h1><p>{content.intro}</p><small>Effective date: 1 January 2025</small></div><div className="legal-copy">{content.sections.map(([heading, text]) => <section key={heading}><h2>{heading}</h2><p>{text}</p></section>)}</div></main><Footer /></>;
}

function DashboardShell({ user, guilds, selectedGuild, onGuildChange, section, onSectionChange, children, stats }: { user: User; guilds: Guild[]; selectedGuild: Guild | null; onGuildChange: (guild: Guild) => void; section: DashSection; onSectionChange: (section: DashSection) => void; children: React.ReactNode; stats: BotStats | null }) {
  const items: [DashSection, string, string][] = [["overview", "Overview", "grid"], ["economy", "Economy", "chart"], ["leveling", "Leveling", "spark"], ["moderation", "Moderation", "shield"], ["ai", "AI controls", "settings"]];
  return <div className="dashboard-layout"><aside className="dash-sidebar"><Brand onNavigate={() => navigate("/")} /><div className="side-label">Workspace</div><nav className="dash-nav">{items.map(([id, label, icon]) => <button key={id} className={section === id ? "active" : ""} onClick={() => onSectionChange(id)}><Icon name={icon} />{label}</button>)}</nav><div className="sidebar-bottom"><span className="online-label"><span className="status-dot" /> Niko is online</span><small>{formatNumber(stats?.guild_count)} servers · v{stats?.version || "1.0"}</small><a href="/" onClick={(e) => { e.preventDefault(); navigate("/"); }}>Back to public site <Icon name="arrow" /></a></div></aside><div className="dash-content"><header className="dash-topbar"><div><span className="mobile-brand"><Brand /></span><span className="dash-overline">Server workspace</span><h1>{selectedGuild?.name || "Select a server"}</h1></div><div className="dash-top-actions"><select aria-label="Select server" value={selectedGuild?.id || ""} onChange={(e) => { const guild = guilds.find((item) => item.id === e.target.value); if (guild) onGuildChange(guild); }}><option value="" disabled>Select a server</option>{guilds.map((guild) => <option value={guild.id} key={guild.id}>{guild.name}</option>)}</select><div className="user-pill"><span className="avatar">{initials(displayName(user))}</span><span>{displayName(user)}</span></div><a className="logout-link" href="/auth/logout">Log out</a></div></header><main className="dash-main">{children}</main></div></div>;
}

function DashboardPage() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [stats, setStats] = useState<BotStats | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [selectedGuild, setSelectedGuild] = useState<Guild | null>(null);
  const [section, setSection] = useState<DashSection>("overview");
  const [error, setError] = useState("");
  useEffect(() => { Promise.all([getAuth(), getStats()]).then(([authStatus, botStats]) => { setAuth(authStatus); setStats(botStats); if (authStatus.authenticated) return getGuilds().then((items) => { setGuilds(items); const remembered = localStorage.getItem("niko-guild"); setSelectedGuild(items.find((item) => item.id === remembered) || items[0] || null); }); }).catch((reason) => setError(reason instanceof Error ? reason.message : "Dashboard unavailable")); }, []);
  if (!auth) return <div className="dashboard-state"><div className="loading-ring" /><p>Connecting to Niko…</p></div>;
  if (!auth.authenticated) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><span className="auth-mark">n</span><div className="eyebrow">Private workspace</div><h1>Settle in, <em>admin.</em></h1><p>Sign in with Discord to view server insights and manage Niko’s settings.</p>{auth.oauth_available ? <a className="button button-primary full-width" href="/auth/login">Continue with Discord <Icon name="arrow" /></a> : <div className="notice warning">Discord login is not configured yet. Add <code>DISCORD_CLIENT_SECRET</code> to the environment and restart the bot.</div>}<a className="back-link" href="/" onClick={(e) => { e.preventDefault(); navigate("/"); }}>Return to public site</a></div></main></>;
  if (error) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><span className="auth-mark">!</span><div className="eyebrow">Connection issue</div><h1>Couldn’t load<br /><em>your workspace.</em></h1><p>{error}</p><button className="button button-primary" onClick={() => window.location.reload()}>Try again <Icon name="arrow" /></button></div></main></>;
  if (!guilds.length) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><span className="auth-mark">n</span><div className="eyebrow">No workspace yet</div><h1>No managed<br /><em>servers found.</em></h1><p>Niko needs to be in a server where your Discord account has Manage Server permission.</p><a className="button button-primary" href="https://discord.com/oauth2/authorize?client_id=1520558530472448170&permissions=8&scope=bot%20applications.commands" target="_blank" rel="noreferrer">Invite Niko <Icon name="arrow" /></a></div></main></>;
  const changeGuild = (guild: Guild) => { localStorage.setItem("niko-guild", guild.id); setSelectedGuild(guild); };
  return <DashboardShell user={auth.user!} guilds={guilds} selectedGuild={selectedGuild} onGuildChange={changeGuild} section={section} onSectionChange={setSection} stats={stats}>{selectedGuild ? <DashboardSection section={section} guild={selectedGuild} stats={stats} /> : <div className="empty-state">Select a server to continue.</div>}</DashboardShell>;
}

function DashboardSection({ section, guild, stats }: { section: DashSection; guild: Guild; stats: BotStats | null }) {
  const [overview, setOverview] = useState<GuildOverview | null>(null);
  const [economy, setEconomy] = useState<EconomyRow[]>([]);
  const [levels, setLevels] = useState<LevelRow[]>([]);
  const [config, setConfig] = useState<GuildConfig | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { setLoading(true); const load = section === "overview" ? getOverview(guild.id).then(setOverview) : section === "economy" ? getEconomy(guild.id).then(setEconomy) : section === "leveling" ? Promise.all([getLevels(guild.id), getConfig(guild.id)]).then(([rows, value]) => { setLevels(rows); setConfig(value); }) : getConfig(guild.id).then(setConfig); load.catch(() => undefined).finally(() => setLoading(false)); }, [guild.id, section]);
  if (loading) return <div className="section-loading"><div className="loading-ring" /><span>Loading {section}…</span></div>;
  if (section === "overview" && overview) return <OverviewView overview={overview} stats={stats} />;
  if (section === "economy") return <EconomyView rows={economy} />;
  if (section === "leveling") return <LevelingView rows={levels} config={config} />;
  if (section === "moderation") return <ModerationView guildId={guild.id} config={config} />;
  return <AiView guildId={guild.id} config={config} />;
}

function DashHeading({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) { return <div className="dash-heading"><div className="eyebrow">{eyebrow}</div><h2>{title}</h2><p>{text}</p></div>; }
function StatCard({ label, value, note, accent = "" }: { label: string; value: string; note: string; accent?: string }) { return <div className={`dash-stat ${accent}`}><span>{label}</span><strong>{value}</strong><small>{note}</small></div>; }
function RankList({ rows, type }: { rows: (EconomyRow | LevelRow)[]; type: "coins" | "xp" }) { return <div className="rank-list">{rows.slice(0, 5).map((row, index) => <div className="rank-row" key={`${row.user_id}-${index}`}><span className={`rank rank-${index + 1}`}>{String(index + 1).padStart(2, "0")}</span><span className="rank-user">Member {row.user_id.slice(-4)}</span><strong>{formatNumber(type === "coins" ? (row as EconomyRow).net_worth : (row as LevelRow).xp)}<small>{type === "coins" ? " coins" : " xp"}</small></strong></div>)}{!rows.length && <div className="empty-state compact">No data recorded yet.</div>}</div>; }

function OverviewView({ overview, stats }: { overview: GuildOverview; stats: BotStats | null }) {
  return <><DashHeading eyebrow="Overview" title="A quick read on your room." text="The important signals, without making you hunt for them." /><div className="dash-stats"><StatCard label="Members across Niko" value={formatNumber(stats?.user_count)} note="Across all connected servers" accent="accent-violet" /><StatCard label="Economy in circulation" value={formatNumber(overview.economy.total_coins)} note={`${formatNumber(overview.economy.user_count)} active profiles`} accent="accent-orange" /><StatCard label="Warnings logged" value={formatNumber(overview.moderation.warn_count)} note="For this server" accent="accent-blue" /><StatCard label="Automod" value={overview.moderation.automod_active ? "Active" : "Quiet"} note="Protection status" accent="accent-green" /></div><div className="dash-columns"><section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Community economy</span><h3>Top net worth</h3></div><span className="panel-icon"><Icon name="chart" /></span></div><RankList rows={overview.economy.top} type="coins" /></section><section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Community energy</span><h3>Top XP</h3></div><span className="panel-icon"><Icon name="spark" /></span></div><RankList rows={overview.leveling.top} type="xp" /></section></div></>;
}

function EconomyView({ rows }: { rows: EconomyRow[] }) { const total = rows.reduce((sum, row) => sum + row.net_worth, 0); return <><DashHeading eyebrow="Economy" title="Give members something to build." text="A snapshot of the café economy and its most active players." /><div className="dash-stats"><StatCard label="Tracked net worth" value={formatNumber(total)} note="Top 25 profiles" accent="accent-orange" /><StatCard label="Profiles" value={formatNumber(rows.length)} note="With economy data" accent="accent-violet" /></div><section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Leaderboard</span><h3>Net worth</h3></div><span className="panel-icon"><Icon name="chart" /></span></div><div className="wide-table"><div className="table-head"><span>Rank</span><span>Member</span><span>Job</span><span>Level</span><span>Net worth</span></div>{rows.map((row, index) => <div className="table-row" key={row.user_id}><span className="rank">{String(index + 1).padStart(2, "0")}</span><span>Member {row.user_id.slice(-4)}</span><span className="muted">{row.job}</span><span>{row.level}</span><strong>{formatNumber(row.net_worth)}</strong></div>)}</div></section></>; }

function LevelingView({ rows, config }: { rows: LevelRow[]; config: GuildConfig | null }) { return <><DashHeading eyebrow="Leveling" title="Momentum people can see." text="Track the members turning up, and tune the pace to fit your server." /><div className="dash-stats"><StatCard label="Top level" value={String(rows[0]?.level || 0)} note={`Member ${rows[0]?.user_id.slice(-4) || "—"}`} accent="accent-violet" /><StatCard label="XP multiplier" value={`${config?.leveling.xp_multiplier || 1}×`} note={config?.leveling.xp_enabled === false ? "XP disabled" : "Currently active"} accent="accent-blue" /><StatCard label="Cooldown" value={`${config?.leveling.xp_cooldown || 0}s`} note="Between XP awards" accent="accent-green" /></div><section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Leaderboard</span><h3>XP leaders</h3></div><span className="panel-icon"><Icon name="spark" /></span></div><RankList rows={rows} type="xp" /></section></>; }

function ModerationView({ guildId, config }: { guildId: string; config: GuildConfig | null }) { const [saving, setSaving] = useState(false); const [saved, setSaved] = useState(false); const flags = ["antispam", "antilink", "badwords", "massmention", "antiraid_ext"]; const current = (config?.moderation.automod || {}) as Record<string, boolean>; const [values, setValues] = useState<Record<string, boolean>>(Object.fromEntries(flags.map((flag) => [flag, Boolean(current[flag])] ))); const save = () => { setSaving(true); saveConfig(guildId, "automod", values).then(() => { setSaved(true); setTimeout(() => setSaved(false), 2500); }).finally(() => setSaving(false)); }; return <><DashHeading eyebrow="Moderation" title="Keep the room feeling good." text="Small, deliberate controls for the moments that need a little backup." /><section className="dash-panel settings-panel"><div className="panel-heading"><div><span className="panel-kicker">AutoMod</span><h3>Protection rules</h3></div><span className="panel-icon"><Icon name="shield" /></span></div><div className="setting-list">{flags.map((flag) => <label className="setting-row" key={flag}><span><strong>{flag.replace("_", " ")}</strong><small>Protect against {flag.replace("_", " ")} activity</small></span><input type="checkbox" checked={values[flag]} onChange={(e) => setValues({ ...values, [flag]: e.target.checked })} /><i /></label>)}</div><div className="setting-footer"><span>{saved ? "Changes saved." : "Changes are saved to this server."}</span><button className="button button-primary" disabled={saving} onClick={save}>{saving ? "Saving…" : "Save changes"}</button></div></section></>; }

function AiView({ guildId, config }: { guildId: string; config: GuildConfig | null }) { const [personality, setPersonality] = useState(config?.ai.personality || "cafe"); const [enabled, setEnabled] = useState(config?.ai.enabled !== "False" && config?.ai.enabled !== false); const [saving, setSaving] = useState(false); const [saved, setSaved] = useState(false); const save = () => { setSaving(true); saveConfig(guildId, "ai", { personality, enabled }).then(() => { setSaved(true); setTimeout(() => setSaved(false), 2500); }).finally(() => setSaving(false)); }; return <><DashHeading eyebrow="AI controls" title="Give Niko the right tone." text="AI is optional, configurable per server, and designed to stay out of the way when the room doesn’t need it." /><section className="dash-panel settings-panel"><div className="panel-heading"><div><span className="panel-kicker">Personality</span><h3>Conversation settings</h3></div><span className="panel-icon"><Icon name="settings" /></span></div><label className="setting-row"><span><strong>Enable AI chat</strong><small>Respond when Niko is mentioned</small></span><input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} /><i /></label><div className="personality-options"><button className={personality === "cafe" ? "personality active" : "personality"} onClick={() => setPersonality("cafe")}><span className="personality-mark">n</span><span><strong>Café</strong><small>Warm, playful, familiar</small></span></button><button className={personality === "normal" ? "personality active" : "personality"} onClick={() => setPersonality("normal")}><span className="personality-mark">—</span><span><strong>Normal</strong><small>Clear and straightforward</small></span></button></div><div className="setting-footer"><span>{saved ? "Changes saved." : "Conversation history is managed in Discord."}</span><button className="button button-primary" disabled={saving} onClick={save}>{saving ? "Saving…" : "Save changes"}</button></div></section></>; }

export function App() {
  const [page, setPage] = useState<Page>(pageFromPath);
  useEffect(() => { const handle = () => setPage(pageFromPath()); window.addEventListener("popstate", handle); return () => window.removeEventListener("popstate", handle); }, []);
  if (page === "commands") return <CommandsPage />;
  if (page === "docs") return <DocsPage />;
  if (page === "dashboard") return <DashboardPage />;
  if (page === "privacy") return <LegalPage type="privacy" />;
  if (page === "terms") return <LegalPage type="terms" />;
  return <HomePage />;
}