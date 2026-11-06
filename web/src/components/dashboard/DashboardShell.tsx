import { useEffect, useRef, useState, type ReactNode } from "react";
import { PublicHeader } from "../PublicHeader";
import { Icon } from "../Icon";
import { currentPath, navigate, siteHref, type DashboardView, type DashSection, type UserTab } from "../../router";
import { displayName, formatNumber } from "../../utils/format";
import { useStrings } from "../../i18n";
import type { BotStats, Guild, User } from "../../types";
import { GuildIcon } from "./GuildIcon";
import { UserAvatar } from "./UserAvatar";

// Server sections only. The economy and achievements are account-wide, so they
// live in `personalSections` under My overview instead of inside a server. The
// labels are catalogue keys: the dashboard navigation changes language with the
// rest of the site.
const sections: [DashSection, string, string][] = [
  ["overview", "shell.section.overview", "guild_overview"],
  ["leveling", "shell.section.leveling", "guild_leveling"],
  ["moderation", "shell.section.moderation", "guild_moderation"],
  ["server", "shell.section.server", "guild_server"],
  ["onboarding", "shell.section.onboarding", "guild_onboarding"],
  ["tickets", "shell.section.tickets", "guild_tickets"],
  ["notifications", "shell.section.notifications", "guild_notifications"],
  ["boosters", "shell.section.boosters", "spark"],
  ["applications", "shell.section.applications", "guild_applications"],
  ["ai", "shell.section.ai", "guild_ai"],
  ["customization", "shell.section.customization", "guild_customization"],
];

const personalSections: [UserTab, string, string][] = [
  ["overview", "shell.personal.overview", "grid"],
  ["economy", "shell.personal.economy", "guild_economy"],
  ["achievements", "shell.personal.achievements", "guild_achievements"],
];

/** One tab of a page whose navigation lives in the sidebar rather than a bar. */
export type ShellTab = { id: string; label: string; icon: string; badge?: number };

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
  /** The staff workspace's tabs. Present only on the staff page, where they
   *  take the place of a navigation bar at the top of the page. */
  staffTabs?: ShellTab[];
  activeStaffTab?: string;
  onStaffTabChange?: (id: string) => void;
  /** Hidden for everyone until the owner grants developer access. */
  developerAccess?: boolean;
  developerTabs?: ShellTab[];
  activeDeveloperTab?: string;
  onDeveloperTabChange?: (id: string) => void;
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
  staffTabs = [],
  activeStaffTab,
  onStaffTabChange,
  developerAccess = false,
  developerTabs = [],
  activeDeveloperTab,
  onDeveloperTabChange,
  children,
}: Props) {
  const { t } = useStrings("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const sidebarRef = useRef<HTMLElement>(null);
  const wasSidebarOpen = useRef(false);
  const installedGuilds = guilds.filter((guild) => guild.installed !== false);
  // The private staff pages are routed outside the view/section state this shell
  // drives, so their current entry is read from the path itself; the mailbox and
  // its report queue share one entry.
  const path = currentPath().replace(/\/+$/, "");
  const staffPage: "workspace" | "email" | null = path.startsWith("/dashboard/staff/email")
    ? "email"
    : path === "/dashboard/staff" ? "workspace" : null;
  const developerPage = path === "/dashboard/developer" || path.startsWith("/dashboard/developer/");

  useEffect(() => {
    if (!sidebarOpen) {
      if (wasSidebarOpen.current) {
        const trigger = document.querySelector<HTMLButtonElement>(".dashboard-sidebar-toggle");
        if (trigger?.getClientRects().length) trigger.focus();
        wasSidebarOpen.current = false;
      }
      return;
    }

    wasSidebarOpen.current = true;
    const sidebar = sidebarRef.current;
    const trigger = document.querySelector<HTMLButtonElement>(".dashboard-sidebar-toggle");
    const focusableElements = () => Array.from(
      sidebar?.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])') || [],
    ).filter((element) => element.getClientRects().length > 0);
    const firstNavigationItem = sidebar?.querySelector<HTMLElement>('.dash-nav button[aria-current="page"]')
      || sidebar?.querySelector<HTMLElement>(".dash-nav button");
    const focusFrame = window.requestAnimationFrame(() => (firstNavigationItem || focusableElements()[0])?.focus());

    const handleDrawerKeys = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSidebarOpen(false);
        return;
      }
      if (event.key !== "Tab") return;

      const focusable = focusableElements();
      if (!focusable.length) {
        event.preventDefault();
        sidebar?.focus();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const focusIsInside = sidebar?.contains(document.activeElement);
      if (event.shiftKey && (document.activeElement === first || !focusIsInside)) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && (document.activeElement === last || !focusIsInside)) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", handleDrawerKeys);
    return () => {
      window.cancelAnimationFrame(focusFrame);
      document.removeEventListener("keydown", handleDrawerKeys);
    };
  }, [sidebarOpen]);
  const sectionNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-nav-mobile" : "dash-nav"} aria-label={t("shell.serverSettings")}>
      {sections.map(([id, label, icon]) => (
        <button
          key={id}
          className={view === "guild" && section === id ? "active" : ""}
          aria-current={view === "guild" && section === id ? "page" : undefined}
          onClick={() => { onSectionChange(id); setSidebarOpen(false); }}
        >
          <Icon name={icon} /><span>{t(label)}</span>
        </button>
      ))}
    </nav>
  );

  const personalNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-nav-mobile" : "dash-nav"} aria-label={t("shell.personalSections")}>
      {personalSections.map(([id, label, icon]) => (
        <button
          key={id}
          className={view === "overview" && !staffPage && !developerPage && userTab === id ? "active" : ""}
          aria-current={view === "overview" && !staffPage && !developerPage && userTab === id ? "page" : undefined}
          onClick={() => { onUserTabChange(id); setSidebarOpen(false); }}
        >
          <Icon name={icon} /><span>{t(label)}</span>
        </button>
      ))}
    </nav>
  );

  // The staff workspace's own tabs, in the same place the server settings and
  // personal tabs sit: one sidebar for everything, never a bar over the page.
  // The ids are what the panels' aria-labelledby points at; the mobile copy
  // leaves them off so they are not duplicated in the document.
  const staffNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-nav-mobile" : "dash-nav"} aria-label={t("shell.staffTabs")}>
      {staffTabs.map((tab) => (
        <button
          key={tab.id}
          id={mobile ? undefined : `staff-${tab.id}-tab`}
          className={activeStaffTab === tab.id ? "active" : ""}
          aria-current={activeStaffTab === tab.id ? "page" : undefined}
          onClick={() => { onStaffTabChange?.(tab.id); setSidebarOpen(false); }}
        >
          <Icon name={tab.icon} /><span>{tab.label}</span>
          {tab.badge ? <span className="nav-badge">{tab.badge}</span> : null}
        </button>
      ))}
    </nav>
  );

  const developerNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-nav-mobile" : "dash-nav"} aria-label={t("shell.developerTabs")}>
      {developerTabs.map((tab) => (
        <button
          key={tab.id}
          id={mobile ? undefined : `developer-${tab.id}-tab`}
          className={activeDeveloperTab === tab.id ? "active" : ""}
          aria-current={activeDeveloperTab === tab.id ? "page" : undefined}
          onClick={() => { onDeveloperTabChange?.(tab.id); setSidebarOpen(false); }}
        >
          <Icon name={tab.icon} /><span>{tab.label}</span>
          {tab.badge ? <span className="nav-badge">{tab.badge}</span> : null}
        </button>
      ))}
    </nav>
  );

  const primaryNav = (mobile = false) => (
    <nav className={mobile ? "dash-nav dash-primary-nav dash-nav-mobile" : "dash-nav dash-primary-nav"} aria-label={t("shell.dashboard")}>
      <button className={view === "overview" && !staffPage && !developerPage ? "active" : ""} aria-current={view === "overview" && !staffPage && !developerPage ? "page" : undefined} onClick={() => { onHome(); setSidebarOpen(false); }}>
        <Icon name="grid" /><span>{t("shell.myOverview")}</span>
      </button>
      <button className={view === "servers" ? "active" : ""} aria-current={view === "servers" ? "page" : undefined} onClick={() => { onServers(); setSidebarOpen(false); }}>
        <Icon name="users" /><span>{t("shell.myServers")}</span>
      </button>
      {developerAccess && <button
        className={developerPage ? "active" : ""}
        aria-current={developerPage ? "page" : undefined}
        onClick={() => { navigate("/dashboard/developer"); setSidebarOpen(false); }}
      ><Icon name="terminal" /><span>{t("shell.developerPortal")}</span></button>}
      {staffRole && <button
        className={staffPage === "workspace" ? "active" : ""}
        aria-current={staffPage === "workspace" ? "page" : undefined}
        onClick={() => { navigate("/dashboard/staff"); setSidebarOpen(false); }}
      ><Icon name="shield" /><span>{t("shell.staffWorkspace")}</span></button>}
      {/* Every staff member holds an address here, and the page is never linked publicly. */}
      {staffRole && <button
        className={staffPage === "email" ? "active" : ""}
        aria-current={staffPage === "email" ? "page" : undefined}
        onClick={() => { navigate("/dashboard/staff/email"); setSidebarOpen(false); }}
      ><Icon name="mail" /><span>{t("shell.staffEmail")}</span></button>}
    </nav>
  );

  const topActions = () => (
    <div className="dash-top-actions">
      {view === "guild" ? (
        <label className="guild-switcher">
          <span className="sr-only">{t("shell.switchServer")}</span>
          <select value={selectedGuild?.id || ""} onChange={(e) => {
            const guild = installedGuilds.find((item) => item.id === e.target.value);
            if (guild) { onGuildChange(guild); setSidebarOpen(false); }
          }}>
            <option value="" disabled>{t("shell.switchServer")}</option>
            {installedGuilds.map((guild) => <option value={guild.id} key={guild.id}>{guild.name}</option>)}
          </select>
        </label>
      ) : (
        <button className="button button-muted button-small top-action" onClick={() => { onServers(); setSidebarOpen(false); }}><Icon name="users" /> {t("shell.browseServers")}</button>
      )}
      <button className="button button-muted button-small top-action refresh-action" onClick={onRefresh} disabled={refreshing} aria-label={t("shell.refreshAria")}>
        <Icon name="spark" /> {t(refreshing ? "shell.refreshing" : "shell.refresh")}
      </button>
      {view === "guild" && <span className="connection-chip"><span className="status-dot" /> {t("shell.connected")}</span>}
      <div className="user-pill"><UserAvatar user={user} /><span>{displayName(user)}</span></div>
      <a className="logout-button" href="/auth/logout" aria-label={t("shell.logOut")} title={t("shell.logOut")}><Icon name="logout" /></a>
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
        aria-label={t("shell.closeNav")}
        aria-hidden={!sidebarOpen}
        tabIndex={sidebarOpen ? 0 : -1}
        onClick={() => setSidebarOpen(false)}
      />
      <div className="dashboard-workspace">
        <aside id="dashboard-sidebar" ref={sidebarRef} tabIndex={-1} className={`dash-sidebar${sidebarOpen ? " is-open" : ""}`}>
          <div className="dash-mobile-controls">{topActions()}</div>
          <div className="side-rail-heading"><span className="side-label">{t("shell.workspace")}</span><span className="rail-status"><span className="status-dot" /> {t("shell.live")}</span></div>
          {primaryNav()}
          {/* The personal tabs are not this page's navigation, so a staff or
              developer page shows its own group instead of them. */}
          {view === "overview" && !staffPage && !developerPage && (
            <>
              <div className="side-label side-label-settings">{t("shell.personal")}</div>
              <div className="side-guild">
                <UserAvatar user={user} className="guild-avatar" />
                <span><strong>{displayName(user)}</strong><small>{t("shell.economyProfile")}</small></span>
              </div>
              <div className="side-settings-caption"><span>{t("shell.yourTabs")}</span><small>{t("shell.notTied")}</small></div>
              {personalNav()}
            </>
          )}
          {view === "guild" && selectedGuild && (
            <>
              <div className="side-label side-label-settings">{t("shell.currentServer")}</div>
              <div className="side-guild">
                <GuildIcon guild={selectedGuild} />
                <span><strong>{selectedGuild.name}</strong><small>{t("shell.liveConfiguration")}</small></span>
                <span className="guild-presence" title={t("shell.botConnected")}><span className="status-dot" /></span>
              </div>
              <div className="side-settings-caption"><span>{t("shell.settingsMap")}</span><small>{t("shell.pickRoom")}</small></div>
              {sectionNav()}
            </>
          )}
          {developerPage && developerTabs.length > 0 && (
            <>
              <div className="side-label side-label-settings">{t("shell.developerTabs")}</div>
              {developerNav()}
            </>
          )}
          {staffPage === "workspace" && staffTabs.length > 0 && (
            <>
              <div className="side-label side-label-settings">{t("shell.staffTabs")}</div>
              {staffNav()}
            </>
          )}
          <div className="sidebar-bottom">
            <span className="online-label"><span className="status-dot" /> {t("shell.botOnline")}</span>
            <small>{t("shell.connectedServers", { count: formatNumber(stats?.guild_count), version: stats?.version || "2.28.0" })}</small>
            <a href={siteHref("/")} onClick={(e) => { e.preventDefault(); navigate("/"); }}>{t("shell.backToSite")} <Icon name="arrow" /></a>
          </div>
        </aside>
        <div className="dash-content">
          <div className="dash-contextbar">{topActions()}</div>
          <div className="mobile-primary-bar">{primaryNav(true)}</div>
          {view === "guild" && <div className="mobile-section-bar">{sectionNav(true)}</div>}
          {view === "overview" && !staffPage && !developerPage && <div className="mobile-section-bar">{personalNav(true)}</div>}
          {developerPage && developerTabs.length > 0 && <div className="mobile-section-bar">{developerNav(true)}</div>}
          {staffPage === "workspace" && staffTabs.length > 0 && <div className="mobile-section-bar">{staffNav(true)}</div>}
          <main className="dash-main">{children}</main>
        </div>
      </div>
    </div>
  );
}