/**
 * Owner-only devtools.
 *
 * A small button in the bottom-left corner of every page, rendered only when
 * `/auth/status` says the session belongs to a configured owner. It holds the
 * browser information an owner reaches for while checking the site, plus tools
 * for the page they are on — including the switch that skips the support-server
 * gate on the team application pages.
 *
 * Everything here is a browser-local aid. The bypass only changes what this tab
 * renders, so a server-side membership check still runs when an application is
 * submitted.
 */

import { useEffect, useState } from "react";
import { getAuth } from "../api";
import { devtools, useDevtoolsFlag } from "../devtools";
import { pageFromPath } from "../router";
import type { AuthStatus } from "../types";
import { notifyError, notifySuccess } from "../utils/toast";
import { Icon } from "./Icon";

const OUTLINE_CLASS = "owner-devtools-outline";
const TOAST_ID = "owner-devtools";

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
  return <div className="owner-devtools-row"><span>{label}</span><span className="owner-devtools-value">{value}</span></div>;
}

export function OwnerDevtools() {
  const [session, setSession] = useState<AuthStatus | null>(null);
  const [open, setOpen] = useState(false);
  const [viewport, setViewport] = useState(() => ({ width: window.innerWidth, height: window.innerHeight }));
  const [outlined, setOutlined] = useState(false);
  const bypassSupportServer = useDevtoolsFlag(devtools.supportServerBypass);

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
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open]);

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
      type="button"
      className={`owner-devtools-toggle${open ? " is-open" : ""}`}
      aria-expanded={open}
      aria-controls="owner-devtools-panel"
      title="Owner devtools"
      onClick={() => setOpen((current) => !current)}
    >
      <Icon name={open ? "close" : "terminal"} />
      <span>Dev</span>
    </button>
    {open && <section className="owner-devtools-panel" id="owner-devtools-panel" aria-label="Owner devtools">
      <header className="owner-devtools-head">
        <div>
          <span className="owner-devtools-kicker">OWNER DEVTOOLS</span>
          <strong>{label}</strong>
          <small>{user?.username ? `@${user.username} · ${user.id}` : user?.id}</small>
        </div>
        <button type="button" className="owner-devtools-icon-button" onClick={refreshSession} aria-label="Re-read session"><Icon name="refresh" /></button>
      </header>

      <div className="owner-devtools-section">
        <h3>This page</h3>
        <Row label="Route" value={window.location.pathname} />
        <Row label="Page" value={page} />
        {jsonPath && <a className="owner-devtools-link" href={jsonPath} target="_blank" rel="noreferrer">
          Open page JSON <Icon name="external" />
        </a>}
        {page === "team-application" && <div className="owner-devtools-tool">
          <div>
            <strong>Bypass support-server gate</strong>
            <small>Skips the membership check on reading and submitting, even if the bot is not in the server, so the eligibility and required-answer gates can be tested.</small>
          </div>
          <button
            type="button"
            className={`owner-devtools-switch${bypassSupportServer ? " is-on" : ""}`}
            aria-pressed={bypassSupportServer}
            onClick={() => devtools.setSupportServerBypass(!bypassSupportServer)}
          >
            {bypassSupportServer ? "On" : "Off"}
          </button>
        </div>}
      </div>

      <div className="owner-devtools-section">
        <h3>Browser</h3>
        <Row label="Viewport" value={`${viewport.width}×${viewport.height}`} />
        <Row label="Pixel ratio" value={String(window.devicePixelRatio)} />
        <Row label="Language" value={navigator.language} />
        <Row label="Timezone" value={Intl.DateTimeFormat().resolvedOptions().timeZone} />
        <Row label="Connection" value={connectionType()} />
        <p className="owner-devtools-ua">{navigator.userAgent}</p>
        <div className="owner-devtools-actions">
          <button type="button" onClick={() => copy(window.location.href, "Page URL copied.")}>Copy URL</button>
          <button type="button" onClick={() => copy(JSON.stringify(diagnostics, null, 2), "Diagnostics copied.")}>Copy diagnostics</button>
          <button type="button" onClick={() => copy(navigator.userAgent, "User agent copied.")}>Copy UA</button>
        </div>
      </div>

      <div className="owner-devtools-section">
        <h3>Scripts</h3>
        <div className="owner-devtools-actions">
          <button type="button" onClick={toggleOutlines}>{outlined ? "Hide element outlines" : "Show element outlines"}</button>
          <button
            type="button"
            onClick={() => copy(JSON.stringify({ authenticated: session.authenticated, owner: session.owner, user, blacklisted: session.blacklisted }, null, 2), "Session copied.")}
          >
            Copy session
          </button>
          <button type="button" onClick={() => window.location.reload()}>Reload page</button>
        </div>
      </div>
    </section>}
  </div>;
}
