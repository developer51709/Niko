import { useEffect, useMemo, useState } from "react";
import { getStats } from "../api";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
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

  const features = [
    ["spark", "AI that remembers", "Thoughtful conversation with a cozy personality and controls that respect your community."],
    ["chart", "A living economy", "Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],
    ["shield", "Confident moderation", "Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],
    ["users", "Community rituals", "Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."],
  ];
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
        <section className="hero shell">
          <div className="hero-copy">
            <div className="eyebrow"><span className="status-dot" /> Discord companion · online</div>
            <div className="hero-identity">
              <span className="hero-avatar">{config?.bot_avatar_url ? <img src={config.bot_avatar_url} alt="Niko" /> : "n"}</span>
              <span><strong>Niko</strong><small>Your server’s calm, capable co-pilot</small></span>
            </div>
            <h1>Useful tools for a <em>better server.</em></h1>
             <p>Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it.</p>
            <div className="hero-buttons">
              <a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">Invite Niko <Icon name="arrow" /></a>
              <a className="button button-muted" href="/commands" onClick={(e) => { e.preventDefault(); navigate("/commands"); }}>Explore commands</a>
            </div>
            <div className="stats-strip">
              <div><strong>{formatNumber(stats?.guild_count)}</strong><span>servers</span></div>
              <div><strong>{formatNumber(stats?.user_count)}</strong><span>members</span></div>
              <div><strong>{formatNumber(stats?.command_count)}</strong><span>commands</span></div>
            </div>
          </div>
           <div className="hero-art" aria-label="A preview of Niko's server workspace">
             <div className="workspace-preview">
               <div className="workspace-preview-top"><span className="preview-dots"><i /><i /><i /></span><span>server workspace</span><span className="preview-status"><span className="status-dot" /> live</span></div>
               <div className="preview-body">
                 <div className="preview-sidebar"><span className="preview-label">NIKO</span><b>Overview</b><span>Economy</span><span>Leveling</span><span>Moderation</span><span>AI controls</span></div>
                 <div className="preview-main"><span className="preview-label">SERVER SNAPSHOT</span><strong>Everything in one place.</strong><div className="preview-stats"><span><b>{formatNumber(stats?.user_count)}</b><small>members</small></span><span><b>{formatNumber(stats?.command_count)}</b><small>commands</small></span></div><div className="preview-line"><i /><i /><i /></div></div>
               </div>
             </div>
           </div>
        </section>
        <section className="shell intro-section"><div className="section-kicker">Why Niko</div><div className="intro-grid"><h2>The good kind of<br /><em>always-on.</em></h2><p>Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile.</p></div></section>
        <section className="shell feature-grid">{features.map(([icon, title, text]) => <article className="feature-card" key={title}><span className="feature-icon"><Icon name={icon} /></span><h3>{title}</h3><p>{text}</p><a href="/docs" onClick={(e) => { e.preventDefault(); navigate("/docs"); }}>Learn more <Icon name="arrow" /></a></article>)}</section>
        <section className="shell callout"><div><div className="section-kicker">Ready when you are</div><h2>A calmer, cleverer home<br />for your community.</h2></div><a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">Bring Niko in <Icon name="arrow" /></a></section>
      </main>
      <Footer />
    </>
  );
}