import { useState, type MouseEvent } from "react";
import { useBotConfig } from "../hooks/useBotConfig";
import { navigate, type Page } from "../router";
import { Brand } from "./Brand";
import { Icon } from "./Icon";

const publicLinks = [
  { label: "Home", path: "/", page: "home" as Page },
  { label: "Commands", path: "/commands", page: "commands" as Page },
  { label: "Docs", path: "/docs", page: "docs" as Page },
  { label: "Changelog", path: "/changelog", page: "changelog" as Page },
];

export function PublicHeader({ page }: { page: Page }) {
  const config = useBotConfig();
  const isDashboard = page === "dashboard";
  const [menuOpen, setMenuOpen] = useState(false);

  const goTo = (path: string) => (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    setMenuOpen(false);
    navigate(path);
  };

  return (
    <header className={`site-header${isDashboard ? " dashboard-header" : ""}`}>
      <Brand onNavigate={() => setMenuOpen(false)} />
      {!isDashboard && (
        <nav className="site-nav" aria-label="Main navigation">
          {publicLinks.map((link) => (
            <a
              key={link.path}
              className={page === link.page ? "active" : ""}
              aria-current={page === link.page ? "page" : undefined}
              href={link.path}
              onClick={goTo(link.path)}
            >
              {link.label}
            </a>
          ))}
        </nav>
      )}
      <div className="header-actions">
        {isDashboard ? (
          <div className="dashboard-menu">
            <button
              className="button button-small button-muted dashboard-menu-trigger"
              type="button"
              aria-expanded={menuOpen}
              aria-controls="dashboard-navigation-menu"
              onClick={() => setMenuOpen((open) => !open)}
            >
              <Icon name={menuOpen ? "close" : "menu"} />
              <span>Menu</span>
            </button>
            {menuOpen && (
              <nav id="dashboard-navigation-menu" className="dashboard-menu-popover" aria-label="Dashboard navigation">
                <span className="dashboard-menu-label">Navigate</span>
                {publicLinks.map((link) => (
                  <a key={link.path} href={link.path} onClick={goTo(link.path)}>
                    {link.label}
                  </a>
                ))}
                <a className="dashboard-menu-current" href="/dashboard" aria-current="page" onClick={goTo("/dashboard")}>
                  Dashboard
                </a>
              </nav>
            )}
          </div>
        ) : (
          <>
            <a className="button button-small button-muted dashboard-link" href="/dashboard" onClick={goTo("/dashboard")}>
              Dashboard <Icon name="arrow" />
            </a>
            <a className="button button-small button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">
              Add to Discord
            </a>
          </>
        )}
      </div>
    </header>
  );
}
