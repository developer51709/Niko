import { useEffect, useMemo, useState } from "react";
import { getStats } from "../api";
import { useStrings } from "../i18n";
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
// Without this the visitor lands on the home page with no explanation. The map
// holds catalogue keys, so the explanation follows the site language too.
const signInErrorKeys: Record<string, string> = {
  oauth_denied: "signin.denied",
  invalid_state: "signin.invalid",
  no_state: "signin.no_state",
  no_code: "signin.no_code",
  token_exchange_failed: "signin.token",
  user_fetch_failed: "signin.profile",
};

type HomeExample = {
  userId: string;
  command?: string;
  message?: string;
  messageTime?: string;
  time: string;
  reply: (emoji: DemoEmojiToken) => string;
  note: string;
};

// The accounts shown in the cards. They are real accounts that share a server
// with the bot, so the names, avatars and profile popups are the live ones
// rather than painted-on placeholders.
const BAN_TARGET = "<@1514675711493935114>";
const EXAMPLE_MEMBER = "1451608836174512301";
// The reminder card answers a second member, so the two cards do not both read
// as the same person's messages.
const REMINDER_MEMBER = "1495618222488162439";

/**
 * The bot's own replies, drawn as Discord messages.
 *
 * Every string comes from the ``home`` catalogue, so the cards follow the site
 * language like the rest of the page. Only the command names and ids stay
 * literal: ``/ban`` is the command a member actually types, and a mention is an
 * id, not copy.
 */
function useHomeExamples(): HomeExample[] {
  const { t } = useStrings("home");

  return useMemo(() => [
    {
      userId: "1528084386652754010",
      command: "/ban",
      time: t("examples.ban.time"),
      reply: (emoji) => t("examples.ban.reply", {
        emoji: emoji("ban"),
        user: BAN_TARGET,
        reason: t("examples.ban.reason"),
      }),
      note: t("examples.ban.note"),
    },
    {
      userId: REMINDER_MEMBER,
      command: "/reminder set",
      time: t("examples.reminder.time"),
      // The bot writes its due time as a Discord timestamp, which the viewer's
      // own client turns into a relative "in 2 hours".
      reply: (emoji) => t("examples.reminder.reply", {
        emoji: emoji("reminder"),
        timestamp: Math.floor(Date.now() / 1000) + 7200,
      }),
      note: t("examples.reminder.note"),
    },
    {
      userId: EXAMPLE_MEMBER,
      // XP comes from talking, so the level-up answers something they said.
      message: t("examples.level.message"),
      messageTime: t("examples.level.messageTime"),
      time: t("examples.level.time"),
      reply: () => t("examples.level.reply", { user: `<@${EXAMPLE_MEMBER}>` }),
      note: t("examples.level.note"),
    },
  ], [t]);
}

// The four systems, built from the catalogue so their wording follows the site
// language. Only the numbers and the destinations are fixed.
function useHomeSections() {
  const { t } = useStrings("home");

  return useMemo(() => [
    { index: "01", key: "inside.voice", link: "/commands" },
    { index: "02", key: "inside.moderation", link: "/docs" },
    { index: "03", key: "inside.economy", link: "/leaderboard" },
    { index: "04", key: "inside.assistant", link: "/docs" },
  ].map((section) => ({
    index: section.index,
    link: section.link,
    title: t(`${section.key}.title`),
    body: t(`${section.key}.body`),
    tags: t(`${section.key}.tags`),
    linkLabel: t(`${section.key}.link`),
  })), [t]);
}

export function HomePage() {
  const config = useBotConfig();
  const [stats, setStats] = useState<BotStats | null>(null);
  const signInParams = useMemo(() => new URLSearchParams(window.location.search), []);
  const signInError = signInParams.get("error");
  // A failed sign-in carries the address it started on and the one Discord
  // returned to. When they differ that difference *is* the failure, so both are
  // shown rather than leaving the visitor with only "the link expired".
  const signInHop = useMemo(() => {
    const from = signInParams.get("from") || "";
    const to = signInParams.get("to") || "";
    return from && to && from !== to ? { from, to } : null;
  }, [signInParams]);
  useEffect(() => {
    let cancelled = false;
    const refresh = () => getStats().then((s) => { if (!cancelled) setStats(s); }).catch(() => undefined);
    refresh();
    const interval = setInterval(refresh, 10_000);
    return () => { cancelled = true; clearInterval(interval); };
  }, []);

  const examples = useHomeExamples();
  const sections = useHomeSections();
  const { t } = useStrings("home");
  const open = (path: string) => (event: React.MouseEvent) => { event.preventDefault(); navigate(path); };

  return (
    <>
      <PublicHeader page="home" />
      <main>
        {signInError && (
          <section className="shell">
            <div className="inline-error" role="alert">
              <strong>{t("signin.title")}</strong>
              <span>
                {t(signInErrorKeys[signInError] ?? "signin.unknown")}{" "}
                {signInHop && `${t("signin.addresses", { from: signInHop.from, to: signInHop.to })} `}
                {t("signin.body")}
              </span>
              <a className="button button-muted" href="/auth/login?next=%2Fdashboard">{t("signin.retry")}</a>
            </div>
          </section>
        )}

        <section className="shell home-hero">
          <div className="home-hero-copy">
            <p className="home-kicker">{t("hero.kicker")}</p>
            <h1>{t("hero.titleA")}<br />{t("hero.titleB")}</h1>
            <p className="home-lede">{t("hero.lede")}</p>
            <div className="home-actions">
              <a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">
                {t("hero.add")} <Icon name="arrow" />
              </a>
              <a className="button button-muted" href="/commands" onClick={open("/commands")}>{t("hero.browse")}</a>
            </div>
            <p className="home-meta">{t("hero.meta")}</p>
          </div>
        </section>

        <section className="shell home-stats-band" aria-label={t("stats.aria")}>
          <div className="home-stat"><strong>{formatNumber(stats?.guild_count)}</strong><span>{t("stats.servers")}</span></div>
          <div className="home-stat"><strong>{formatNumber(stats?.user_count)}</strong><span>{t("stats.members")}</span></div>
          <div className="home-stat"><strong>{formatNumber(stats?.command_count)}</strong><span>{t("stats.commands")}</span></div>
        </section>

        <section className="shell home-features" aria-labelledby="home-features-title">
          <header className="home-features-head">
            <p className="home-kicker">{t("features.kicker")}</p>
            <h2 id="home-features-title">{t("features.titleA")}<br />{t("features.titleB")}</h2>
            <p>{t("features.body")}</p>
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
            <p className="home-kicker">{t("inside.kicker")}</p>
            <h2>{t("inside.titleA")}<br />{t("inside.titleB")}</h2>
            <p>{t("inside.body")}</p>
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

        <section className="shell home-cta" aria-labelledby="home-cta-title">
          <div className="home-cta-copy">
            <p className="home-kicker">
              <span className="home-cta-mark">
                {config?.bot_avatar_url ? <img src={config.bot_avatar_url} alt="" /> : "N"}
              </span>
              {t("cta.kicker")}
            </p>
            <h2 id="home-cta-title">{t("cta.title")}</h2>
            <p>{t("cta.body")}</p>
          </div>
          <div className="home-cta-actions">
            <a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">
              {t("cta.add")} <Icon name="arrow" />
            </a>
            <a className="button button-muted" href="/docs" onClick={open("/docs")}>{t("cta.docs")}</a>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
