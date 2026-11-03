import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { ApiError, getGuildLeaderboard } from "../api";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import { useStrings } from "../i18n";
import { navigate } from "../router";
import type { GuildLevelsResponse } from "../types";
import { formatNumber, initials } from "../utils/format";
import { rankChanges, rankMap } from "../utils/leaderboard";

// A guild board is small and moves quickly, so it refreshes itself the same
// way the global economy board does. Rows are keyed by an opaque rank key, so a
// member who climbs past someone slides into place instead of snapping.
const POLL_MS = 6_000;
const MOVE_MS = 4_500;

export function GuildLeaderboardPage({ guildId }: { guildId: string }) {
  const { t } = useStrings("guild-leaderboard");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<GuildLevelsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [unknownGuild, setUnknownGuild] = useState(false);
  const [moves, setMoves] = useState<Record<string, number>>({});
  const ranksRef = useRef<Map<string, number>>(new Map());
  const hasDataRef = useRef(false);
  const moveTimer = useRef<number | null>(null);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    let active = true;
    let inFlight = false;
    hasDataRef.current = false;
    ranksRef.current = new Map();
    setLoading(true);
    setError("");
    setUnknownGuild(false);
    setMoves({});

    const load = async () => {
      if (!active || inFlight) return;
      if (document.visibilityState === "hidden") return;
      inFlight = true;
      try {
        const result = await getGuildLeaderboard(guildId, page);
        if (!active) return;
        if (result.pages > 0 && page > result.pages) {
          // The board shrank while this page was open; fall back to the last
          // page that still exists instead of showing an empty one.
          setPage(result.pages);
          return;
        }
        const deltas = rankChanges(ranksRef.current, result.entries);
        ranksRef.current = rankMap(result.entries);
        hasDataRef.current = true;
        setData(result);
        setUnknownGuild(false);
        setError("");
        setLoading(false);
        if (Object.keys(deltas).length) {
          setMoves(deltas);
          if (moveTimer.current) window.clearTimeout(moveTimer.current);
          moveTimer.current = window.setTimeout(() => setMoves({}), MOVE_MS);
        }
      } catch (reason) {
        if (!active) return;
        setLoading(false);
        if (reason instanceof ApiError && reason.status === 404) {
          setUnknownGuild(true);
          setData(null);
          return;
        }
        // A failed poll keeps the standings already on screen and lets the next
        // one catch up; only a first load that never landed is an error.
        if (!hasDataRef.current) {
          setError(reason instanceof Error ? reason.message : "state.error");
        }
      } finally {
        inFlight = false;
      }
    };

    void load();
    const timer = window.setInterval(load, POLL_MS);
    const onVisibilityChange = () => { if (document.visibilityState === "visible") void load(); };
    document.addEventListener("visibilitychange", onVisibilityChange);
    return () => {
      active = false;
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisibilityChange);
      if (moveTimer.current) window.clearTimeout(moveTimer.current);
    };
  }, [guildId, page]);

  const rowTransition = reduceMotion
    ? { duration: 0 }
    : { layout: { duration: 0.5, ease: "easeInOut" as const }, duration: 0.3 };

  const guild = data?.guild;
  const boardDisabled = data ? !data.leveling_enabled : false;

  return <>
    <PublicHeader page="leaderboard" />
    <main className="shell page-main guild-leaderboard-page">
      {unknownGuild ? <UnknownGuild /> : <>
        <section className="guild-leaderboard-hero" aria-label={t("hero.aria")}>
          <span className={`guild-leaderboard-icon${guild ? "" : " is-loading"}`}>
            {guild?.icon_url
              ? <img src={guild.icon_url} alt="" />
              : guild ? initials(guild.name || "Server") : null}
          </span>
          <div className="guild-leaderboard-heading">
            <span className="eyebrow">{t("hero.eyebrow")}</span>
            <h1>{guild?.name || t("hero.titleFallback")}</h1>
            <p>{guild
              ? t("hero.bodyCount", { members: formatNumber(guild.member_count), ranked: formatNumber(data?.total ?? 0) })
              : t("hero.bodyLatest")}</p>
          </div>
          <span className="guild-leaderboard-live"><i aria-hidden="true" />{t("hero.live")}</span>
        </section>

        <section className="leaderboard-panel" aria-label={t("panel.aria")}>
          <div className="leaderboard-panel-heading">
            <div>
              <span className="panel-kicker">{t("panel.kicker")}</span>
              <h2>{t("panel.title")}</h2>
              <p>{data
                ? t(data.total === 1 ? "panel.membersOne" : "panel.membersMany", { count: formatNumber(data.total) })
                : t("panel.bodyLatest")}</p>
            </div>
          </div>
          {loading ? <div className="leaderboard-state" role="status"><span className="loading-ring" />{t("state.loading")}</div>
            : error ? <div className="leaderboard-state leaderboard-error" role="alert">{error.startsWith("state.") ? t(error) : error}</div>
            : boardDisabled ? <div className="leaderboard-state">{t("state.disabled")}</div>
            : !data?.entries.length ? <div className="leaderboard-state">{t("state.empty")}</div>
            : <div className="leaderboard-list">
              <AnimatePresence initial={false} mode="popLayout">
                {data.entries.map((entry) => {
                  const move = moves[entry.key] ?? 0;
                  const progress = entry.xp_for_next > 0
                    ? Math.min(100, Math.max(0, (entry.xp / entry.xp_for_next) * 100))
                    : 0;
                  const name = entry.display_name || entry.username || t("row.member");
                  return <motion.article
                    layout={!reduceMotion}
                    transition={rowTransition}
                    initial={false}
                    exit={{ opacity: 0 }}
                    className={`guild-leaderboard-row${entry.rank <= 3 ? ` leaderboard-rank-${entry.rank}` : ""}`}
                    key={entry.key}
                  >
                    <span className="leaderboard-rank">
                      {String(entry.rank).padStart(2, "0")}
                      <AnimatePresence initial={false}>
                        {move !== 0 && <motion.span
                          key={`${entry.key}-move`}
                          className={`leaderboard-move ${move > 0 ? "leaderboard-move-up" : "leaderboard-move-down"}`}
                          aria-label={move > 0 ? t("move.up", { count: move }) : t("move.down", { count: Math.abs(move) })}
                          initial={{ opacity: 0, y: move > 0 ? 5 : -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: move > 0 ? -5 : 5 }}
                          transition={{ duration: reduceMotion ? 0 : 0.28, ease: "easeOut" }}
                        >
                          {move > 0 ? "▲" : "▼"}{Math.abs(move)}
                        </motion.span>}
                      </AnimatePresence>
                    </span>
                    <span className="leaderboard-avatar">{entry.avatar_url
                      ? <img src={entry.avatar_url} alt="" />
                      : initials(name)}</span>
                    <span className="guild-leaderboard-identity">
                      <strong>{name}</strong>
                      {entry.username && entry.display_name ? <small>@{entry.username}</small> : null}
                      <span
                        className="guild-leaderboard-bar"
                        role="progressbar"
                        aria-label={t("row.progress", { name, level: entry.level + 1 })}
                        aria-valuemin={0}
                        aria-valuemax={entry.xp_for_next}
                        aria-valuenow={entry.xp}
                      ><i style={{ width: `${progress}%` }} /></span>
                    </span>
                    <span className="guild-leaderboard-level">
                      <strong>{t("row.level", { level: entry.level })}</strong>
                      <small>{t("row.xp", { xp: formatNumber(entry.xp), next: formatNumber(entry.xp_for_next) })}</small>
                    </span>
                  </motion.article>;
                })}
              </AnimatePresence>
            </div>}
          {data && data.pages > 1 && <nav className="leaderboard-pagination" aria-label={t("pagination.aria")}>
            <button className="button button-muted button-small" type="button" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page <= 1}><Icon name="arrow" /> {t("pagination.previous")}</button>
            <span>{t("pagination.page", { page, pages: data.pages })}</span>
            <button className="button button-muted button-small" type="button" onClick={() => setPage((current) => Math.min(data.pages, current + 1))} disabled={page >= data.pages}>{t("pagination.next")} <Icon name="arrow" /></button>
          </nav>}
        </section>
        <aside className="leaderboard-privacy-note"><Icon name="chart" /><p><strong>{t("privacy.title")}</strong> {t("privacy.before")} {guild?.name || t("privacy.server")}{t("privacy.middle")} <a href="/docs/leveling-overview">{t("privacy.link")}</a> {t("privacy.after")}</p></aside>
      </>}
    </main>
    <Footer />
  </>;
}

function UnknownGuild() {
  const config = useBotConfig();
  const { t } = useStrings("guild-leaderboard");
  return <section className="guild-leaderboard-unknown">
    <span className="guild-leaderboard-unknown-mark"><Icon name="alert" /></span>
    <span className="panel-kicker">{t("unknown.kicker")}</span>
    <h1>{t("unknown.title")}</h1>
    <p>{t("unknown.body")}</p>
    <div className="guild-leaderboard-unknown-actions">
      <a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">{t("unknown.add")} <Icon name="arrow" /></a>
      <a className="button button-muted" href="/" onClick={(event) => { event.preventDefault(); navigate("/"); }}>{t("unknown.back")}</a>
    </div>
  </section>;
}
