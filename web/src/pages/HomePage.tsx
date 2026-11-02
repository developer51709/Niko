import { useEffect, useMemo, useState } from "react";
import { getStats } from "../api";
import { DemoDiscordMessage, type DemoEmojiToken } from "../components/DemoDiscordMessage";
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

// The bot's own replies, drawn as Discord messages. The ids are real accounts
// that share a server with the bot, so the names, avatars and the profile
// popups behind them are the live ones rather than painted-on placeholders.
const examples: {
  userId: string;
  command?: string;
  message?: string;
  messageTime?: string;
  time: string;
  reply: (emoji: DemoEmojiToken) => string;
  note: string;
}[] = [
  {
    userId: "1528084386652754010",
    command: "/ban",
    time: "Today at 3:04 PM",
    reply: (emoji) =>
      `### ${emoji("ban")} User Banned\n**<@1514675711493935114>** has been banned.\n**Reason:** spamming invite links`,
    note: "Confirms first, clears the last 7 days of their messages, and writes the ban into your log channel.",
  },
  {
    userId: "1451608836174512301",
    command: "/reminder set",
    time: "Today at 3:06 PM",
    // The bot writes its due time as a Discord timestamp, which the viewer's
    // own client turns into a relative "in 2 hours".
    reply: (emoji) =>
      `### ${emoji("reminder")} Reminder Set\nI will remind you about **check the support queue** <t:${Math.floor(Date.now() / 1000) + 7200}:R>.`,
    note: "Arrives in your DMs, or in the channel it was set in when the whole server needs to see it.",
  },
  {
    userId: "1451608836174512301",
    // XP comes from talking, so the level-up answers something they said.
    message: "gm! anyone up for a few rounds later?",
    messageTime: "Today at 3:08 PM",
    time: "Today at 3:09 PM",
    reply: () => "Congratulations <@1451608836174512301>, you leveled up to level **25**!",
    note: "Talking earns XP; level roles and announcements are set up once and then run themselves.",
  },
];

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
          <div className="home-hero-copy">
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
        </section>

        <section className="shell home-stats-band" aria-label="Niko in numbers">
          <div className="home-stat"><strong>{formatNumber(stats?.guild_count)}</strong><span>servers</span></div>
          <div className="home-stat"><strong>{formatNumber(stats?.user_count)}</strong><span>members</span></div>
          <div className="home-stat"><strong>{formatNumber(stats?.command_count)}</strong><span>commands</span></div>
          <p className="home-stats-note"><span className="status-dot" /> Live from the bot</p>
        </section>

        <section className="shell home-features" aria-labelledby="home-features-title">
          <header className="home-features-head">
            <p className="home-kicker">In the server</p>
            <h2 id="home-features-title">What it actually<br />sends back.</h2>
            <p>
              The panel is Niko&rsquo;s real VoiceMaster interface, wired to the same buttons the bot posts — press one.
              The replies shown with it are what the rest of the stack looks like in a channel.
            </p>
          </header>
          <div className="home-features-grid">
            <VoiceMasterPanel className="home-panel" />
            <div className="home-examples">
              {examples.map((example) => (
                <DemoDiscordMessage
                  key={example.time}
                  userId={example.userId}
                  command={example.command}
                  message={example.message}
                  messageTime={example.messageTime}
                  time={example.time}
                  reply={example.reply}
                  note={example.note}
                />
              ))}
            </div>
          </div>
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
