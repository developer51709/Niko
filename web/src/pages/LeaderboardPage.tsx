import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { api } from "../api";
import { PublicHeader } from "../components/PublicHeader";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { useStrings } from "../i18n";
import { formatNumber } from "../utils/format";
import { rankChanges, rankMap } from "../utils/leaderboard";

type Entry = {
  key: string;
  rank: number;
  net_worth: number;
  private: boolean;
  username: string | null;
  display_name: string | null;
  avatar_url: string | null;
};
type PageData = { entries: Entry[]; page: number; page_size: number; total: number; pages: number };

// Standings refresh themselves while the page is open, the same way the home
// page keeps its stats live. Rows are keyed by the API's opaque row key, so a
// member who climbs past someone slides into place instead of snapping.
const POLL_MS = 6_000;
const MOVE_MS = 4_500;

export function LeaderboardPage() {
  const { t } = useStrings("leaderboard");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<PageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
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
    setMoves({});

    const load = async () => {
      if (!active || inFlight) return;
      if (document.visibilityState === "hidden") return;
      inFlight = true;
      try {
        const result = await api<PageData>(`/api/economy/leaderboard?page=${page}`);
        if (!active) return;
        if (result.pages > 0 && page > result.pages) {
          // The board shrank while this page was open; fall back to the last page
          // that still exists instead of showing an empty one.
          setPage(result.pages);
          return;
        }
        const deltas = rankChanges(ranksRef.current, result.entries);
        ranksRef.current = rankMap(result.entries);
        hasDataRef.current = true;
        setData(result);
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
  }, [page]);

  const rowTransition = reduceMotion
    ? { duration: 0 }
    : { layout: { duration: 0.5, ease: "easeInOut" as const }, duration: 0.3 };

  return <>
    <PublicHeader page="leaderboard" />
    <main className="shell page-main economy-leaderboard-page">
      <section className="leaderboard-hero">
        <span className="eyebrow">{t("hero.eyebrow")}</span>
        <h1>{t("hero.title")}</h1>
        <p>{t("hero.body")}</p>
      </section>
      <section className="leaderboard-panel" aria-label={t("panel.aria")}>
        <div className="leaderboard-panel-heading">
          <div>
            <span className="panel-kicker">{t("panel.kicker")}</span>
            <h2>{t("panel.title")}</h2>
            <p>{data ? t("panel.bodyCount", { count: formatNumber(data.total) }) : t("panel.bodyLatest")}</p>
          </div>
        </div>
        {loading ? <div className="leaderboard-state" role="status"><span className="loading-ring" />{t("state.loading")}</div> : error ? <div className="leaderboard-state leaderboard-error" role="alert">{error.startsWith("state.") ? t(error) : error}</div> : !data?.entries.length ? <div className="leaderboard-state">{t("state.empty")}</div> : <div className="leaderboard-list">
          <AnimatePresence initial={false} mode="popLayout">
            {data.entries.map((entry) => {
              const hidden = entry.private && !entry.display_name;
              const move = moves[entry.key] ?? 0;
              return <motion.article
                layout={!reduceMotion}
                transition={rowTransition}
                initial={false}
                exit={{ opacity: 0 }}
                className={`leaderboard-row${entry.rank <= 3 ? ` leaderboard-rank-${entry.rank}` : ""}`}
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
                {hidden ? <span className="leaderboard-avatar leaderboard-avatar-hidden"><Icon name="lock" /></span> : <span className="leaderboard-avatar">{entry.avatar_url ? <img src={entry.avatar_url} alt="" /> : (entry.display_name || "?").slice(0, 1).toUpperCase()}</span>}
                <span className="leaderboard-identity"><strong>{hidden ? t("row.private") : entry.display_name || entry.username || t("row.member")}</strong>{hidden ? <small>{t("row.hidden")}</small> : entry.username && entry.display_name ? <small>@{entry.username}</small> : null}</span>
                <motion.strong
                  className="leaderboard-worth"
                  key={`${entry.key}-${entry.net_worth}`}
                  initial={{ opacity: move === 0 ? 0.55 : 1 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: reduceMotion ? 0 : 0.45 }}
                >
                  {formatNumber(entry.net_worth)} <small>{t("row.coins")}</small>
                </motion.strong>
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
      <aside className="leaderboard-privacy-note"><Icon name="shield" /><p><strong>{t("privacy.title")}</strong> {t("privacy.before")} <a href="/dashboard">{t("privacy.link")}</a>. {t("privacy.after")}</p></aside>
    </main>
    <Footer />
  </>;
}
