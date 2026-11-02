import { useEffect, useMemo, useState } from "react";
import { getStats } from "../api";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { VoiceMasterPanel } from "../components/VoiceMasterPanel";
import { navigate } from "../router";
import { useBotConfig } from "../hooks/useBotConfig";
import type { BotStats } from "../types";
import { formatNumber } from "../utils/format";

// /auth/callback reports a failed sign-in by redirecting here with ?error=...
// Without this the visitor lands on the home page with no explanation.
const signInErrorMessages: Record<string, string> = {
  oauth_denied: "Discord sign-in was cancelled before it finished.",
  invalid_state: "That sign-in link expired before it was used.",
  no_code: "Discord did not return a sign-in code.",
  token_exchange_failed: "Niko could not complete the token exchange with Discord.",
  user_fetch_failed: "Niko could not read your Discord profile.",
};

const sections = [
  {
    index: "01",
    title: "Voice",
    body: "Temporary channels members open themselves, run from a panel instead of a command list.",
    tags: "lock · hide · claim · limits",
    link: "/commands",
    linkLabel: "Commands",
  },
  {
    index: "02",
    title: "Moderation",
    body: "Automod, raid protection, warnings and a log channel your moderators can actually read.",
    tags: "automod · anti-raid · warnings · logs",
    link: "/docs",
    linkLabel: "Docs",
  },
  {
    index: "03",
    title: "Economy",
    body: "Jobs, banking, a casino, shops and leaderboards that give members a reason to come back tomorrow.",
    tags: "jobs · bank · gambling · shop",
    link: "/leaderboard",
    linkLabel: "Leaderboard",
  },
  {
    index: "04",
    title: "Assistant",
    body: "A co-pilot with memory for the conversations that matter, and switches to turn it off per channel.",
    tags: "memory · personality · per-channel",
    link: "/docs",
    linkLabel: "Docs",
  },
];

export function HomePage() {
  const config = useBotConfig();
  const [stats, setStats] = useState<BotStats | null>(null);
  const signInError = useMemo(() => new URLSearchParams(window.location.search).get("error"), []);
  useEffect(() => {
    let cancelled = false;
    const refresh = () => getStats().then((s) => { if (!cancelled) setStats(s); }).catch(() => undefined);
    refresh();
    const interval = setInterval(refresh, 10_000);
    return () => { cancelled = true; clearInterval(interval); };
  }, []);

  const open = (path: string) => (event: React.MouseEvent) => { event.preventDefault(); navigate(path); };

  return (
    <>
      <PublicHeader page="home" />
      <main>
        {signInError && (
          <section className="shell">
            <div className="inline-error" role="alert">
              <strong>Sign-in could not be completed.</strong>
              <span>
                {signInErrorMessages[signInError] ?? "Discord rejected the sign-in attempt."}{" "}
                You are still signed out, so nothing was changed.
              </span>
              <a className="button button-muted" href="/auth/login?next=%2Fdashboard">Try again</a>
            </div>
          </section>
        )}

        <section className="shell home-hero">
          <div>
            <p className="home-kicker">Discord app</p>
            <h1>One bot,<br />not five.</h1>
            <p className="home-lede">
              Voice channels, moderation, an economy and an assistant — the jobs usually split across a stack of
              bots, in one app your members only have to learn once.
            </p>
            <div className="home-actions">
              <a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">
                Add Niko <Icon name="arrow" />
              </a>
              <a className="button button-muted" href="/commands" onClick={open("/commands")}>Browse commands</a>
            </div>
            <p className="home-meta">Free to start · No card · Four languages</p>
          </div>
          <VoiceMasterPanel className="home-panel" />
        </section>

        <section className="shell home-stats-band" aria-label="Niko in numbers">
          <div className="home-stat"><strong>{formatNumber(stats?.guild_count)}</strong><span>servers</span></div>
          <div className="home-stat"><strong>{formatNumber(stats?.user_count)}</strong><span>members</span></div>
          <div className="home-stat"><strong>{formatNumber(stats?.command_count)}</strong><span>commands</span></div>
          <p className="home-stats-note"><span className="status-dot" /> Live from the bot</p>
        </section>

        <section className="shell home-inside">
          <header className="home-inside-head">
            <p className="home-kicker">What is inside</p>
            <h2>Four systems,<br />one bot.</h2>
            <p>Nothing here is a checkbox on a feature list. Each one is a full system your staff can run without a manual.</p>
          </header>
          <div className="home-rows">
            {sections.map((section) => (
              <article className="home-row" key={section.title}>
                <span className="home-row-index">{section.index}</span>
                <div className="home-row-copy">
                  <h3>{section.title}</h3>
                  <p>{section.body}</p>
                  <p className="home-row-tags">{section.tags}</p>
                </div>
                <a href={section.link} onClick={open(section.link)}>{section.linkLabel} <Icon name="arrow" /></a>
              </article>
            ))}
          </div>
        </section>

        <section className="shell home-cta">
          <div className="home-cta-identity">
            <span className="home-cta-avatar">
              {config?.bot_avatar_url ? <img src={config.bot_avatar_url} alt="" /> : "N"}
            </span>
            <div>
              <p className="home-kicker">Ready when you are</p>
              <h2>Put Niko in your server.</h2>
              <p>One invite, the settings you already know, and every command documented in the same four languages.</p>
            </div>
          </div>
          <div className="home-cta-actions">
            <a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">
              Add Niko <Icon name="arrow" />
            </a>
            <a className="button button-muted" href="/docs" onClick={open("/docs")}>Read the docs</a>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
