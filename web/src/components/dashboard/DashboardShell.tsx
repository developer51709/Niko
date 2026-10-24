import { useState, type ReactNode } from "react";
import { PublicHeader } from "../PublicHeader";
import { Icon } from "../Icon";
import { navigate, type DashboardView, type DashSection, type UserTab } from "../../router";
import { displayName, formatNumber } from "../../utils/format";
import type { BotStats, Guild, User } from "../../types";
import { GuildIcon } from "./GuildIcon";
import { UserAvatar } from "./UserAvatar";

// Server sections only. The economy and achievements are account-wide, so they
// live in `personalSections` under My overview instead of inside a server.
const sections: [DashSection, string, string, string][] = [
  ["overview", "Overview", "guild_overview", "At a glance"],
  ["leveling", "Leveling", "guild_leveling", "Reward participation"],
  ["moderation", "Moderation", "guild_moderation", "Keep things steady"],
  ["server", "Server", "guild_server", "Manage server features"],
  ["onboarding", "Onboarding", "guild_onboarding", "Welcome and join roles"],
  ["tickets", "Tickets", "guild_tickets", "Support desk and transcripts"],
  ["notifications", "Notifications", "guild_notifications", "Social announcements"],
  ["boosters", "Boosters", "spark", "Boost announcements and custom roles"],
  ["applications", "Applications", "guild_applications", "Staff role openings"],
  ["ai", "AI controls", "guild_ai", "Shape Niko’s voice"],
  ["customization", "Customization", "guild_customization", "Niko’s server identity"],
];

const personalSections: [UserTab, string, string][] = [
  ["overview", "Overview", "grid"],
  ["economy", "Economy", "guild_economy"],
  ["achievements", "Achievements", "guild_achievements"],
];

type Props = {
  user: User;
  guilds: Guild[];
  selectedGuild: Guild | null;
  view: DashboardView;
  section: DashSection;
  userTab: UserTab;
  stats: BotStats | null;
  onHome: () => void;
  onServers: () => void;
  onGuildChange: (guild: Guild) => void;
  onSectionChange: (section: DashSection) => void;
  onUserTabChange: (tab: UserTab) => void;
  onRefresh: () => void;
  refreshing: boolean;
  staffRole?: string | null;
  children: ReactNode;
};

export function DashboardShell({
  user,
  guilds,
  selectedGuild,
  view,
  section,
  userTab,
  stats,
  onHome,
  onServers,
  onGuildChange,
  onSectionChange,
  onUserTabChange,
  onRefresh,
  refreshing,
  staffRole,
  children,
}: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const installedGuilds = guilds.filter((guild) => guild.installed !== false);
  const sectionNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-nav-mobile" : "dash-nav"} aria-label="Server settings">
      {sections.map(([id, label, icon]) => (
        <button
          key={id}
          className={view === "guild" && section === id ? "active" : ""}
          aria-current={view === "guild" && section === id ? "page" : undefined}
          onClick={() => { onSectionChange(id); setSidebarOpen(false); }}
        >
          <Icon name={icon} /><span>{label}</span>
        </button>
      ))}
    </nav>
  );

  const personalNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-nav-mobile" : "dash-nav"} aria-label="Personal sections">
      {personalSections.map(([id, label, icon]) => (
        <button
          key={id}
          className={view === "overview" && userTab === id ? "active" : ""}
          aria-current={view === "overview" && userTab === id ? "page" : undefined}
          onClick={() => { onUserTabChange(id); setSidebarOpen(false); }}
        >
          <Icon name={icon} /><span>{label}</span>
        </button>
      ))}
    </nav>
  );

  const primaryNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-primary-nav dash-nav-mobile" : "dash-nav dash-primary-nav"} aria-label="Dashboard">
      <button className={view === "overview" ? "active" : ""} aria-current={view === "overview" ? "page" : undefined} onClick={() => { onHome(); setSidebarOpen(false); }}>
        <Icon name="grid" /><span>My overview</span>
      </button>
      <button className={view === "servers" ? "active" : ""} aria-current={view === "servers" ? "page" : undefined} onClick={() => { onServers(); setSidebarOpen(false); }}>
        <Icon name="users" /><span>My servers</span>
      </button>
      {staffRole && <button onClick={() => { navigate("/dashboard/staff"); setSidebarOpen(false); }}><Icon name="shield" /><span>Staff workspace</span></button>}
    </nav>
  );

  const topActions = () => (
    <div className="dash-top-actions">
      {view === "guild" ? (
        <label className="guild-switcher">
          <span className="sr-only">Switch server</span>
          <select value={selectedGuild?.id || ""} onChange={(e) => {
            const guild = installedGuilds.find((item) => item.id === e.target.value);
            if (guild) { onGuildChange(guild); setSidebarOpen(false); }
          }}>
            <option value="" disabled>Switch server</option>
            {installedGuilds.map((guild) => <option value={guild.id} key={guild.id}>{guild.name}</option>)}
          </select>
        </label>
      ) : (
        <button className="button button-muted button-small top-action" onClick={() => { onServers(); setSidebarOpen(false); }}><Icon name="users" /> Browse servers</button>
      )}
      <button className="button button-muted button-small top-action refresh-action" onClick={onRefresh} disabled={refreshing} aria-label="Refresh dashboard data">
        <Icon name="spark" /> {refreshing ? "Refreshing…" : "Refresh data"}
      </button>
      {view === "guild" && <span className="connection-chip"><span className="status-dot" /> Connected</span>}
      <div className="user-pill"><UserAvatar user={user} /><span>{displayName(user)}</span></div>
      <a className="logout-button" href="/auth/logout" aria-label="Log out" title="Log out"><Icon name="logout" /></a>
    </div>
  );

  return (
    <div className="dashboard-layout">
      <PublicHeader
        page="dashboard"
        sidebarOpen={sidebarOpen}
        onSidebarToggle={() => setSidebarOpen((open) => !open)}
      />
      <button
        className={`dashboard-sidebar-backdrop${sidebarOpen ? " is-visible" : ""}`}
        type="button"
        aria-label="Close dashboard navigation"
        aria-hidden={!sidebarOpen}
        tabIndex={sidebarOpen ? 0 : -1}
        onClick={() => setSidebarOpen(false)}
      />
      <div className="dashboard-workspace">
        <aside id="dashboard-sidebar" className={`dash-sidebar${sidebarOpen ? " is-open" : ""}`}>
          <div className="dash-mobile-controls">{topActions()}</div>
          <div className="side-rail-heading"><span className="side-label">Workspace</span><span className="rail-status"><span className="status-dot" /> Live</span></div>
          {primaryNav()}
          {view === "overview" && (
            <>
              <div className="side-label side-label-settings">Personal</div>
              <div className="side-guild">
                <UserAvatar user={user} className="guild-avatar" />
                <span><strong>{displayName(user)}</strong><small>Global economy profile</small></span>
              </div>
              <div className="side-settings-caption"><span>Your tabs</span><small>Not tied to a server</small></div>
              {personalNav()}
            </>
          )}
          {view === "guild" && selectedGuild && (
            <>
              <div className="side-label side-label-settings">Current server</div>
              <div className="side-guild">
                <GuildIcon guild={selectedGuild} />
                <span><strong>{selectedGuild.name}</strong><small>Live configuration</small></span>
                <span className="guild-presence" title="Niko is connected"><span className="status-dot" /></span>
              </div>
              <div className="side-settings-caption"><span>Settings map</span><small>Pick a room to tune</small></div>
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
          <div className="dash-contextbar">{topActions()}</div>
          <div className="mobile-primary-bar">{primaryNav(true)}</div>
          {view === "guild" && <div className="mobile-section-bar">{sectionNav(true)}</div>}
          {view === "overview" && <div className="mobile-section-bar">{personalNav(true)}</div>}
          <main className="dash-main">{children}</main>
        </div>
      </div>
    </div>
  );
}