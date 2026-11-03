/**
 * Owner-only devtools.
 *
 * A small button in the bottom-left corner of every page, rendered only when
 * `/auth/status` says the session belongs to a configured owner. It holds the
 * browser information an owner reaches for while checking the site, plus tools
 * for the page they are on — including the switch that skips the support-server
 * gate on the team application pages.
 *
 * The panel is an overlay anchored above the button, so opening it never moves
 * the button out from under the pointer that just clicked it, and it is grouped
 * into tabs to keep each view short enough to read at a glance. The tabs follow
 * the WAI-ARIA tabs pattern: one tab in the tab order at a time, arrow keys (and
 * Home/End) move between them, and each view is labelled by its own tab.
 *
 * Everything here is a browser-local aid. The bypass only changes what this tab
 * renders, so a server-side membership check still runs when an application is
 * submitted.
 */

import { useEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from "react";
import { getAuth } from "../api";
import { devtools, useDevtoolsFlag } from "../devtools";
import { useLanguage, type LanguageCode } from "../i18n";
import { pageFromPath } from "../router";
import type { AuthStatus } from "../types";
import { notifyError, notifySuccess } from "../utils/toast";
import { Icon } from "./Icon";

const OUTLINE_CLASS = "owner-devtools-outline";
const TOAST_ID = "owner-devtools";
const PANEL_ID = "owner-devtools-panel";

/** The panel's tabs, in reading order. `id` doubles as the ARIA id fragment. */
const TABS = [
  { id: "page", label: "Page" },
  { id: "browser", label: "Browser" },
  { id: "tools", label: "Tools" },
] as const;

type TabId = (typeof TABS)[number]["id"];

const tabId = (id: TabId) => `owner-devtools-tab-${id}`;
const tabPanelId = (id: TabId) => `owner-devtools-view-${id}`;

/** The JSON a page is already built from, when it has one worth opening. */
function pageJsonPath(page: string, segments: string[], bypassMembership: boolean) {
  if (page === "team") return "/api/team";
  if (page === "team-member") return `/api/team/${encodeURIComponent(segments[1] || "")}`;
  if (page === "team-application") {
    // Match the page: with the gate bypassed the same parameter unlocks the JSON.
    const query = bypassMembership ? "?bypass_membership=1" : "";
    return segments[2] ? `/api/team-recruitment/${encodeURIComponent(segments[2])}${query}` : `/api/team-recruitment${query}`;
  }
  if (page === "guild-leaderboard") return `/api/levels/${encodeURIComponent(segments[1] || "")}`;
  return null;
}

function connectionType() {
  const connection = (navigator as Navigator & { connection?: { effectiveType?: string } }).connection;
  return connection?.effectiveType || (navigator.onLine ? "online" : "offline");
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="owner-devtools-row">
      <span>{label}</span>
      <span className="owner-devtools-value">{value}</span>
    </div>
  );
}

export function OwnerDevtools() {
  const [session, setSession] = useState<AuthStatus | null>(null);
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<TabId>("page");
  const [viewport, setViewport] = useState(() => ({ width: window.innerWidth, height: window.innerHeight }));
  const [outlined, setOutlined] = useState(false);
  const bypassSupportServer = useDevtoolsFlag(devtools.supportServerBypass);
  // The site's own language choice, not the browser's: this is the control that
  // makes testing a translation possible without changing device settings.
  const { language, languages, browser, overridden, setLanguage, resetLanguage } = useLanguage();

  const toggleRef = useRef<HTMLButtonElement | null>(null);
  const tabRefs = useRef<Record<TabId, HTMLButtonElement | null>>({ page: null, browser: null, tools: null });

  useEffect(() => {
    let active = true;
    getAuth()
      .then((status) => { if (active) setSession(status); })
      .catch(() => { if (active) setSession(null); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    const handleResize = () => setViewport({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    if (!open) return;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setOpen(false);
      toggleRef.current?.focus();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open]);

  // Opening the panel moves focus into it, so a keyboard user lands on the tab
  // strip instead of having to tab past the button a second time.
  useEffect(() => {
    if (open) tabRefs.current[tab]?.focus();
  }, [open, tab]);

  // The outline overlay is a page-wide debug style, so it never outlives the
  // panel that switches it on.
  useEffect(() => () => document.documentElement.classList.remove(OUTLINE_CLASS), []);

  const refreshSession = () => {
    getAuth()
      .then(setSession)
      .catch(() => notifyError("The session could not be re-read.", TOAST_ID));
  };

  const copy = (value: string, message: string) => {
    navigator.clipboard
      .writeText(value)
      .then(() => notifySuccess(message, TOAST_ID))
      .catch(() => notifyError("Clipboard access was blocked.", TOAST_ID));
  };

  const toggleOutlines = () => {
    const next = !document.documentElement.classList.contains(OUTLINE_CLASS);
    document.documentElement.classList.toggle(OUTLINE_CLASS, next);
    setOutlined(next);
  };

  /** Arrow keys walk the tab strip, Home/End jump to its ends. */
  const handleTabKeys = (event: ReactKeyboardEvent<HTMLDivElement>) => {
    const current = TABS.findIndex((entry) => entry.id === tab);
    let next: number;
    if (event.key === "ArrowRight") next = (current + 1) % TABS.length;
    else if (event.key === "ArrowLeft") next = (current - 1 + TABS.length) % TABS.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = TABS.length - 1;
    else return;
    event.preventDefault();
    setTab(TABS[next].id);
    tabRefs.current[TABS[next].id]?.focus();
  };

  if (!session?.authenticated || !session.owner) return null;

  const user = session.user;
  const segments = window.location.pathname.split("/").filter(Boolean);
  const page = pageFromPath();
  const jsonPath = pageJsonPath(page, segments, bypassSupportServer);
  const label = user?.global_name || user?.username || "Owner";
  const diagnostics = {
    url: window.location.href,
    page,
    viewport: `${viewport.width}×${viewport.height}`,
    device_pixel_ratio: window.devicePixelRatio,
    language: navigator.language,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    connection: connectionType(),
    user_agent: navigator.userAgent,
  };

  return <div className="owner-devtools">
    <button
      ref={toggleRef}
      type="button"
      className={`owner-devtools-toggle${open ? " is-open" : ""}`}
      aria-expanded={open}
      aria-controls={PANEL_ID}
      aria-haspopup="dialog"
      title="Owner devtools"
      onClick={() => setOpen((current) => !current)}
    >
      <Icon name={open ? "close" : "terminal"} />
      <span>Dev</span>
    </button>

    {open && <section
      className="owner-devtools-panel"
      id={PANEL_ID}
      role="dialog"
      aria-modal="false"
      aria-labelledby="owner-devtools-title"
    >
      <header className="owner-devtools-head">
        <div>
          <span className="owner-devtools-kicker">OWNER DEVTOOLS</span>
          <strong id="owner-devtools-title">{label}</strong>
          <small>{user?.username ? `@${user.username} · ${user.id}` : user?.id}</small>
        </div>
        <button type="button" className="owner-devtools-icon-button" onClick={refreshSession} aria-label="Re-read session" title="Re-read session">
          <Icon name="refresh" />
        </button>
      </header>

      <div className="owner-devtools-tabs" role="tablist" aria-label="Devtools sections" onKeyDown={handleTabKeys}>
        {TABS.map((entry) => {
          const selected = entry.id === tab;
          return <button
            key={entry.id}
            ref={(node) => { tabRefs.current[entry.id] = node; }}
            type="button"
            role="tab"
            id={tabId(entry.id)}
            aria-selected={selected}
            aria-controls={tabPanelId(entry.id)}
            tabIndex={selected ? 0 : -1}
            className={`owner-devtools-tab${selected ? " is-active" : ""}`}
            onClick={() => setTab(entry.id)}
          >
            {entry.label}
          </button>;
        })}
      </div>

      <div className="owner-devtools-body">
        {tab === "page" && <div
          role="tabpanel"
          id={tabPanelId("page")}
          aria-labelledby={tabId("page")}
          tabIndex={0}
          className="owner-devtools-view"
        >
          <h3>This page</h3>
          <Row label="Route" value={window.location.pathname} />
          <Row label="Page" value={page} />
          <Row label="Site language" value={`${language}${overridden ? " (override)" : " (browser)"}`} />
          {jsonPath && <a className="owner-devtools-link" href={jsonPath} target="_blank" rel="noreferrer">
            Open page JSON <Icon name="external" />
          </a>}
          <h3>Site language</h3>
          <div className="owner-devtools-tool owner-devtools-locale">
            <div>
              <strong id="owner-devtools-language">Website language</strong>
              <small>
                Switches the site's catalogues for this browser only. Discord replies keep following each
                server's own locale.
              </small>
            </div>
            <select
              className="owner-devtools-select"
              aria-labelledby="owner-devtools-language"
              value={language}
              onChange={(event) => setLanguage(event.target.value as LanguageCode)}
            >
              {languages.map((entry) => <option key={entry.code} value={entry.code}>{entry.label}</option>)}
            </select>
          </div>
          {overridden && <button type="button" className="owner-devtools-reset" onClick={resetLanguage}>
            Use browser language ({languages.find((entry) => entry.code === browser)?.label ?? "English"})
          </button>}
          {page === "team-application" && <div className="owner-devtools-tool">
            <div>
              <strong id="owner-devtools-bypass">Bypass support-server gate</strong>
              <small>Skips the membership check on reading and submitting, even if the bot is not in the server, so the eligibility and required-answer gates can be tested.</small>
            </div>
            <button
              type="button"
              className={`owner-devtools-switch${bypassSupportServer ? " is-on" : ""}`}
              aria-pressed={bypassSupportServer}
              aria-labelledby="owner-devtools-bypass"
              onClick={() => devtools.setSupportServerBypass(!bypassSupportServer)}
            >
              {bypassSupportServer ? "On" : "Off"}
            </button>
          </div>}
        </div>}

        {tab === "browser" && <div
          role="tabpanel"
          id={tabPanelId("browser")}
          aria-labelledby={tabId("browser")}
          tabIndex={0}
          className="owner-devtools-view"
        >
          <h3>Browser</h3>
          <Row label="Viewport" value={`${viewport.width}×${viewport.height}`} />
          <Row label="Pixel ratio" value={String(window.devicePixelRatio)} />
          <Row label="Language" value={navigator.language} />
          <Row label="Timezone" value={Intl.DateTimeFormat().resolvedOptions().timeZone} />
          <Row label="Connection" value={connectionType()} />
          <p className="owner-devtools-ua" aria-label="User agent">{navigator.userAgent}</p>
          <div className="owner-devtools-actions">
            <button type="button" onClick={() => copy(window.location.href, "Page URL copied.")}>Copy URL</button>
            <button type="button" onClick={() => copy(JSON.stringify(diagnostics, null, 2), "Diagnostics copied.")}>Copy diagnostics</button>
            <button type="button" onClick={() => copy(navigator.userAgent, "User agent copied.")}>Copy UA</button>
          </div>
        </div>}

        {tab === "tools" && <div
          role="tabpanel"
          id={tabPanelId("tools")}
          aria-labelledby={tabId("tools")}
          tabIndex={0}
          className="owner-devtools-view"
        >
          <h3>Session</h3>
          <div className="owner-devtools-actions">
            <button
              type="button"
              onClick={() => copy(JSON.stringify({ authenticated: session.authenticated, owner: session.owner, user, blacklisted: session.blacklisted }, null, 2), "Session copied.")}
            >
              Copy session
            </button>
            <button type="button" onClick={refreshSession}>Re-read session</button>
          </div>

          <h3>Page scripts</h3>
          <div className="owner-devtools-actions">
            <button type="button" aria-pressed={outlined} onClick={toggleOutlines}>
              {outlined ? "Hide element outlines" : "Show element outlines"}
            </button>
            <button type="button" onClick={() => window.location.reload()}>Reload page</button>
          </div>
        </div>}
      </div>
    </section>}
  </div>;
}
