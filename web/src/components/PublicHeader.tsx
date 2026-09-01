import { useBotConfig } from "../hooks/useBotConfig";
import { navigate, type Page } from "../router";
import { Brand } from "./Brand";
import { Icon } from "./Icon";

export function PublicHeader({ page }: { page: Page }) {
  const config = useBotConfig();
  return (
    <header className="site-header">
      <Brand />
      <nav className="site-nav" aria-label="Main navigation">
        <a className={page === "home" ? "active" : ""} aria-current={page === "home" ? "page" : undefined} href="/" onClick={(e) => { e.preventDefault(); navigate("/"); }}>Home</a>
        <a className={page === "commands" ? "active" : ""} aria-current={page === "commands" ? "page" : undefined} href="/commands" onClick={(e) => { e.preventDefault(); navigate("/commands"); }}>Commands</a>
        <a className={page === "docs" ? "active" : ""} aria-current={page === "docs" ? "page" : undefined} href="/docs" onClick={(e) => { e.preventDefault(); navigate("/docs"); }}>Docs</a>
      </nav>
      <div className="header-actions">
        <a className="button button-small button-muted dashboard-link" href="/dashboard" onClick={(e) => { e.preventDefault(); navigate("/dashboard"); }}>
          Dashboard <Icon name="arrow" />
        </a>
        <a className="button button-small button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">
          Add to Discord
        </a>
      </div>
    </header>
  );
}