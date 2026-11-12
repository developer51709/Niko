/**
 * Owner-only devtools.
 *
 * A small button in the bottom corner of every page, rendered only when
 * `/auth/status` says the session belongs to a configured owner. Its own context
 * menu moves it — and the panel — to the other edge of the screen, which is what
 * gets it out of a dashboard sidebar on a phone. It holds the
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
import { devtools, useDevtoolsFlag, useDevtoolsValue, type DevtoolsSide } from "../devtools";
import { TEST_FONTS, resetTestFont, setTestFont, testFontLabel, useTestFont } from "../fontTester";
import { useLanguage, useStrings, type LanguageCode } from "../i18n";
import { pageFromPath } from "../router";
import type { AuthStatus } from "../types";
import { registerContextMenuExtras } from "../utils/contextMenu";
import { notifyError, notifySuccess } from "../utils/toast";
import { Select } from "./dashboard/Select";
import { Switch } from "./dashboard/Switch";
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

/** The presence the status-icon preview paints, live included. */
const PRESENCE_OPTIONS = [
  { value: "online", label: "Online" },
  { value: "idle", label: "Idle" },
  { value: "dnd", label: "Do not disturb" },
  { value: "offline", label: "Offline" },
  { value: "online_mobile", label: "Online · mobile" },
  { value: "idle_mobile", label: "Idle · mobile" },
  { value: "dnd_mobile", label: "Do not disturb · mobile" },
];

/** The font tester's rows: every candidate; the site's own face is the reset. */
const FONT_OPTIONS = TEST_FONTS.map((font) => ({ value: font.key, label: font.label }));

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

type PanelPhase = "closed" | "open" | "closing";

export function OwnerDevtools() {
  const [session, setSession] = useState<AuthStatus | null>(null);
  const [panelPhase, setPanelPhase] = useState<PanelPhase>("closed");
  const open = panelPhase === "open";
  const [tab, setTab] = useState<TabId>("page");
  const [viewport, setViewport] = useState(() => ({ width: window.innerWidth, height: window.innerHeight }));
  const [outlined, setOutlined] = useState(false);
  const bypassSupportServer = useDevtoolsFlag(devtools.supportServerBypass);
  const presencePreview = useDevtoolsValue(devtools.presencePreview);
  // Which edge the button lives on. The dashboard sidebar sits bottom-left on a
  // phone, so the panel opened over it had to be movable.
  const side: DevtoolsSide = useDevtoolsValue(devtools.side);
  const { t } = useStrings("shared");
  // The typeface tester is public (it is installed for every visitor and driven
  // from the console); this panel only mirrors it while an owner is here.
  const fontFamily = useTestFont();
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
      setPanelPhase("closing");
      toggleRef.current?.focus();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open]);

  // The panel stays mounted for one short exit animation. A timeout unmounts
  // it even when the user has asked the browser to reduce motion and the CSS
  // animation does not run.
  useEffect(() => {
    if (panelPhase !== "closing") return;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const timer = window.setTimeout(() => setPanelPhase("closed"), reduceMotion ? 0 : 190);
    return () => window.clearTimeout(timer);
  }, [panelPhase]);

  // Opening the panel moves focus into it, so a keyboard user lands on the tab
  // strip instead of having to tab past the button a second time.
  useEffect(() => {
    if (open) tabRefs.current[tab]?.focus();
  }, [open, tab]);

  // The outline overlay is a page-wide debug style, so it never outlives the
  // panel that switches it on.
  useEffect(() => () => document.documentElement.classList.remove(OUTLINE_CLASS), []);

  // The button answers its own context menu with the one choice it has: the edge
  // the whole cluster sits on. Registered here rather than in the menu because
  // the current side lives in this component.
  useEffect(
    () =>
      registerContextMenuExtras((target) => {
        if (!target.closest(".owner-devtools-toggle")) return null;
        const next: DevtoolsSide = side === "right" ? "left" : "right";
        return [{
          key: "devtools-side",
          label: t(next === "right" ? "contextMenu.moveDevtoolsRight" : "contextMenu.moveDevtoolsLeft"),
          icon: next === "right" ? "arrow" : "back",
          action: () => devtools.setSide(next),
        }];
      }),
    [side, t],
  );

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

  return <div className="owner-devtools" data-side={side}>
    <button
      ref={toggleRef}
      type="button"
      className={`owner-devtools-toggle${open ? " is-open" : ""}`}
      aria-expanded={open}
      aria-controls={PANEL_ID}
      aria-haspopup="dialog"
      title="Owner devtools"
      onClick={() => setPanelPhase((phase) => (phase === "open" ? "closing" : "open"))}
    >
      <Icon name={open ? "close" : "terminal"} />
      <span>Dev</span>
    </button>

    {panelPhase !== "closed" && <section
        className={`owner-devtools-panel${panelPhase === "closing" ? " is-closing" : ""}`}
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
            {/* The panel's own dropdown, so the language picker matches the
                rest of the site instead of dropping back to the browser's
                native menu inside developer tooling. */}
            <Select
              ariaLabel="Website language"
              listClassName="owner-devtools-select-list"
              placeholder={null}
              value={language}
              onChange={(value) => setLanguage(value as LanguageCode)}
              options={languages.map((entry) => ({ value: entry.code, label: entry.label }))}
            />
          </div>
          {overridden && <button type="button" className="owner-devtools-reset" onClick={resetLanguage}>
            Use browser language ({languages.find((entry) => entry.code === browser)?.label ?? "English"})
          </button>}
          {page === "team-application" && <div className="owner-devtools-tool">
            <div>
              <strong id="owner-devtools-bypass">Bypass support-server gate</strong>
              <small>Skips the membership check on reading and submitting, even if the bot is not in the server, so the eligibility and required-answer gates can be tested.</small>
            </div>
            <Switch
              size="sm"
              checked={bypassSupportServer}
              onCheckedChange={(checked) => devtools.setSupportServerBypass(checked)}
              aria-labelledby="owner-devtools-bypass"
            />
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

          <h3>Typeface</h3>
          <div className="owner-devtools-tool owner-devtools-locale">
            <div>
              <strong id="owner-devtools-font">Site font</strong>
              <small>
                Re-typesets this tab — public pages and the dashboard together — so a candidate face can be
                read at real sizes, line lengths and weights. The site itself is unchanged, and anyone can
                do the same from the console with <code>nikoFont</code>.
              </small>
            </div>
            <Select
              ariaLabel="Site font"
              listClassName="owner-devtools-select-list"
              placeholder="Site default"
              value={fontFamily}
              onChange={setTestFont}
              unknownOption={(value) => ({ value, label: testFontLabel(value) })}
              options={FONT_OPTIONS}
            />
          </div>
          {fontFamily && <button type="button" className="owner-devtools-reset" onClick={resetTestFont}>
            Use the site font
          </button>}

          <h3>Presence preview</h3>
          <div className="owner-devtools-tool owner-devtools-locale">
            <div>
              <strong id="owner-devtools-presence">Status icons</strong>
              <small>
                Fakes one presence on every avatar in this tab, so the round and mobile status icons can be
                checked across the site without waiting for a client to change.
              </small>
            </div>
            <Select
              ariaLabel="Status icon preview"
              listClassName="owner-devtools-select-list"
              placeholder="Live status"
              value={presencePreview}
              onChange={(value) => devtools.setPresencePreview(value)}
              options={PRESENCE_OPTIONS}
            />
          </div>
          {presencePreview && <button type="button" className="owner-devtools-reset" onClick={() => devtools.setPresencePreview("")}>
            Use live status
          </button>}
        </div>}
      </div>
      </section>}
  </div>;
}
