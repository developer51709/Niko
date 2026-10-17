import type { MouseEvent } from "react";
import { Icon } from "./Icon";

interface PublicHeaderActionsProps {
  inviteUrl?: string;
  onNavigate: (path: string) => (event: MouseEvent<HTMLAnchorElement>) => void;
  isDashboard?: boolean;
  menuOpen?: boolean;
  onMenuToggle?: () => void;
}

const publicLinks = [
  { label: "Home", path: "/" },
  { label: "Commands", path: "/commands" },
  { label: "Docs", path: "/docs" },
  { label: "Team", path: "/team" },
  { label: "Changelog", path: "/changelog" },
];

export function PublicHeaderActions({
  inviteUrl,
  onNavigate,
  isDashboard = false,
  menuOpen = false,
  onMenuToggle,
}: PublicHeaderActionsProps) {
  if (isDashboard) {
    return (
      <div className="dashboard-menu">
        <button
          className="button button-small button-muted dashboard-menu-trigger"
          type="button"
          aria-expanded={menuOpen}
          aria-controls="dashboard-navigation-menu"
          onClick={onMenuToggle}
        >
          <Icon name={menuOpen ? "close" : "menu"} />
          <span>Menu</span>
        </button>
        {menuOpen && (
          <nav id="dashboard-navigation-menu" className="dashboard-menu-popover" aria-label="Dashboard navigation">
            <span className="dashboard-menu-label">Navigate</span>
            {publicLinks.map((link) => (
              <a key={link.path} href={link.path} onClick={onNavigate(link.path)}>
                {link.label}
              </a>
            ))}
            <a className="dashboard-menu-current" href="/dashboard" aria-current="page" onClick={onNavigate("/dashboard")}>
              Dashboard
            </a>
          </nav>
        )}
      </div>
    );
  }

  return (
    <>
      <a className="button button-small button-muted dashboard-link" href="/dashboard" onClick={onNavigate("/dashboard")}>
        Dashboard <Icon name="arrow" />
      </a>
      <a className="button button-small button-primary" href={inviteUrl || "#"} target="_blank" rel="noreferrer">
        Add to Discord
      </a>
    </>
  );
}
