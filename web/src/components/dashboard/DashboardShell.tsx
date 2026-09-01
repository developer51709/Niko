import type { ReactNode } from "react";
import { Brand } from "../Brand";
import { Icon } from "../Icon";
import { dashboardPath, dashboardServersPath, navigate, type DashboardView, type DashSection } from "../../router";
import { displayName, formatNumber, initials } from "../../utils/format";
import type { BotStats, Guild, User } from "../../types";

const sections: [DashSection, string, string][] = [
  ["overview", "Server overview", "grid"],
  ["economy", "Economy", "chart"],
  ["leveling", "Leveling", "spark"],
  ["moderation", "Moderation", "shield"],
  ["ai", "AI controls", "settings"],
];

type Props = {
  user: User;
  guilds: Guild[];
  selectedGuild: Guild | null;
  view: DashboardView;
  section: DashSection;
  stats: BotStats | null;
  onHome: () => void;
  onServers: () => void;
  onGuildChange: (guild: Guild) => void;
  onSectionChange: (section: DashSection) => void;
  children: ReactNode;
};

export function DashboardShell({
  user,
  guilds,
  selectedGuild,
  view,
  section,
  stats,
  onHome,
  onServers,
  onGuildChange,
  onSectionChange,
  children,
}: Props) {
  const installedGuilds = guilds.filter((guild) => guild.installed !== false);
  const sectionNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-nav-mobile" : "dash-nav"} aria-label="Server settings">
      {sections.map(([id, label, icon]) => (
        <button
          key={id}
          className={view === "guild" && section === id ? "active" : ""}
          aria-current={view === "guild" && section === id ? "page" : undefined}
          onClick={() => onSectionChange(id)}
        >
          <Icon name={icon} /><span>{label}</span>
        </button>
      ))}
    </nav>
  );

  const primaryNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-primary-nav dash-nav-mobile" : "dash-nav dash-primary-nav"} aria-label="Dashboard">
      <button className={view === "overview" ? "active" : ""} aria-current={view === "overview" ? "page" : undefined} onClick={onHome}>
        <Icon name="grid" /><span>My overview</span>
      </button>
      <button className={view === "servers" ? "active" : ""} aria-current={view === "servers" ? "page" : undefined} onClick={onServers}>
        <Icon name="users" /><span>My servers</span>
      </button>
    </nav>
  );

  const pageTitle = view === "overview" ? `Welcome, ${displayName(user)}` : view === "servers" ? "Your servers" : selectedGuild?.name || "Server settings";
  const pageOverline = view === "guild" ? "Managing server" : "Niko dashboard";

  return (
    <div className="dashboard-layout">
      <aside className="dash-sidebar">
        <Brand onNavigate={onHome} />
        <div className="side-label">Workspace</div>
        {primaryNav()}
        {view === "guild" && selectedGuild && (
          <>
            <div className="side-label side-label-settings">Server settings</div>
            <div className="side-guild">
              <span className="guild-avatar">{selectedGuild.name.slice(0, 1).toUpperCase()}</span>
              <span><strong>{selectedGuild.name}</strong><small>Configuration</small></span>
            </div>
            {sectionNav()}
          </>
        )}
        <div className="sidebar-bottom">
          <span className="online-label"><span className="status-dot" /> Niko is online</span>
          <small>{formatNumber(stats?.guild_count)} connected servers · v{stats?.version || "1.0"}</small>
          <a href="/" onClick={(e) => { e.preventDefault(); navigate("/"); }}>Back to public site <Icon name="arrow" /></a>
        </div>
      </aside>
      <div className="dash-content">
        <header className="dash-topbar">
          <div className="mobile-top-row">
            <span className="mobile-brand"><Brand /></span>
            <span className="mobile-status"><span className="status-dot" /> Online</span>
          </div>
          <div className="dash-title">
            <span className="dash-overline">{pageOverline}</span>
            <h1>{pageTitle}</h1>
          </div>
          <div className="dash-top-actions">
            {view === "guild" ? (
              <label className="guild-switcher">
                <span className="sr-only">Switch server</span>
                <select value={selectedGuild?.id || ""} onChange={(e) => {
                  const guild = installedGuilds.find((item) => item.id === e.target.value);
                  if (guild) onGuildChange(guild);
                }}>
                  <option value="" disabled>Switch server</option>
                  {installedGuilds.map((guild) => <option value={guild.id} key={guild.id}>{guild.name}</option>)}
                </select>
              </label>
            ) : (
              <button className="button button-muted button-small top-action" onClick={onServers}><Icon name="users" /> Browse servers</button>
            )}
            <div className="user-pill"><span className="avatar">{initials(displayName(user))}</span><span>{displayName(user)}</span></div>
            <a className="logout-link" href="/auth/logout">Log out</a>
          </div>
        </header>
        <div className="mobile-primary-bar">{primaryNav(true)}</div>
        {view === "guild" && <div className="mobile-section-bar">{sectionNav(true)}</div>}
        <main className="dash-main">{children}</main>
      </div>
    </div>
  );
}