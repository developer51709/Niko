import type { ReactNode } from "react";
import { Brand } from "../Brand";
import { Icon } from "../Icon";
import { dashboardPath, navigate, type DashSection } from "../../router";
import { displayName, formatNumber, initials } from "../../utils/format";
import type { BotStats, Guild, User } from "../../types";

const sections: [DashSection, string, string][] = [
  ["overview", "Overview", "grid"],
  ["economy", "Economy", "chart"],
  ["leveling", "Leveling", "spark"],
  ["moderation", "Moderation", "shield"],
  ["ai", "AI controls", "settings"],
];

type Props = {
  user: User;
  guilds: Guild[];
  selectedGuild: Guild | null;
  section: DashSection;
  stats: BotStats | null;
  onGuildChange: (guild: Guild) => void;
  onSectionChange: (section: DashSection) => void;
  children: ReactNode;
};

export function DashboardShell({ user, guilds, selectedGuild, section, stats, onGuildChange, onSectionChange, children }: Props) {
  const sectionNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-nav-mobile" : "dash-nav"} aria-label="Dashboard sections">
      {sections.map(([id, label, icon]) => (
        <button
          key={id}
          className={section === id ? "active" : ""}
          aria-current={section === id ? "page" : undefined}
          onClick={() => onSectionChange(id)}
        >
          <Icon name={icon} /><span>{label}</span>
        </button>
      ))}
    </nav>
  );

  return (
    <div className="dashboard-layout">
      <aside className="dash-sidebar">
        <Brand onNavigate={() => navigate("/")} />
        <div className="side-label">Workspace</div>
        {sectionNav()}
        <div className="sidebar-bottom">
          <span className="online-label"><span className="status-dot" /> Niko is online</span>
          <small>{formatNumber(stats?.guild_count)} servers · v{stats?.version || "1.0"}</small>
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
            <span className="dash-overline">Server workspace</span>
            <h1>{selectedGuild?.name || "Select a server"}</h1>
          </div>
          <div className="dash-top-actions">
            <label className="sr-only" htmlFor="guild-select">Select a server</label>
            <select id="guild-select" value={selectedGuild?.id || ""} onChange={(e) => {
              const guild = guilds.find((item) => item.id === e.target.value);
              if (guild) onGuildChange(guild);
            }}>
              <option value="" disabled>Select a server</option>
              {guilds.map((guild) => <option value={guild.id} key={guild.id}>{guild.name}</option>)}
            </select>
            <div className="user-pill"><span className="avatar">{initials(displayName(user))}</span><span>{displayName(user)}</span></div>
            <a className="logout-link" href="/auth/logout">Log out</a>
          </div>
        </header>
        <div className="mobile-section-bar">{sectionNav(true)}</div>
        <main className="dash-main">{children}</main>
      </div>
    </div>
  );
}