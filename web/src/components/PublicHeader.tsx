import { useState, type MouseEvent } from "react";
import { useBotConfig } from "../hooks/useBotConfig";
import { navigate, type Page } from "../router";
import { Brand } from "./Brand";
import { PublicHeaderActions } from "./PublicHeaderActions";

const publicLinks = [
  { label: "Home", path: "/", page: "home" as Page },
  { label: "Commands", path: "/commands", page: "commands" as Page },
  { label: "Docs", path: "/docs", page: "docs" as Page },
  { label: "Team", path: "/team", page: "team" as Page },
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
        <PublicHeaderActions
          inviteUrl={config?.invite_url}
          onNavigate={goTo}
          isDashboard={isDashboard}
          menuOpen={menuOpen}
          onMenuToggle={() => setMenuOpen((open) => !open)}
        />
      </div>
    </header>
  );
}
