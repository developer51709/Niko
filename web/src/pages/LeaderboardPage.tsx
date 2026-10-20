import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { api } from "../api";
import { PublicHeader } from "../components/PublicHeader";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { formatNumber } from "../utils/format";
import { rankChanges, rankMap } from "../utils/leaderboard";
import { syncedLabel } from "../utils/live";
import { useSyncedClock } from "../hooks/useLiveSync";

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
  const [page, setPage] = useState(1);
  const [data, setData] = useState<PageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [stale, setStale] = useState(false);
  const [moves, setMoves] = useState<Record<string, number>>({});
  const [lastSync, setLastSync] = useState<number | null>(null);
  const now = useSyncedClock(lastSync);
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
    setStale(false);
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
        setStale(false);
        setLastSync(Date.now());
        setLoading(false);
        if (Object.keys(deltas).length) {
          setMoves(deltas);
          if (moveTimer.current) window.clearTimeout(moveTimer.current);
          moveTimer.current = window.setTimeout(() => setMoves({}), MOVE_MS);
        }
      } catch (reason) {
        if (!active) return;
        setLoading(false);
        if (hasDataRef.current) {
          // Keep the standings on screen and say we are reconnecting rather
          // than replacing a good board with an error page.
          setStale(true);
        } else {
          setError(reason instanceof Error ? reason.message : "The leaderboard could not be loaded.");
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
    <PublicHeader page="home" />
    <main className="shell page-main economy-leaderboard-page">
      <section className="leaderboard-hero">
        <span className="eyebrow">Niko · global economy standings</span>
        <h1>Global economy leaderboard</h1>
        <p>Every coin counts. See how your earnings stack up across the whole bot.</p>
      </section>
      <section className="leaderboard-panel" aria-label="Global economy leaderboard">
        <div className="leaderboard-panel-heading">
          <div>
            <span className="panel-kicker">🏆 Global economy leaderboard</span>
            <h2>Rankings</h2>
            <p>{data ? `${formatNumber(data.total)} members ordered by net worth` : "The latest economy standings"}</p>
            <span className="leaderboard-synced" role="status" aria-live="polite">{syncedLabel(lastSync, now)}</span>
          </div>
          <span className={`leaderboard-live${stale ? " is-stale" : ""}`}><span className="status-dot" /> {stale ? "RECONNECTING" : "LIVE"}</span>
        </div>
        {loading ? <div className="leaderboard-state" role="status"><span className="loading-ring" />Loading standings…</div> : error ? <div className="leaderboard-state leaderboard-error" role="alert">{error}</div> : !data?.entries.length ? <div className="leaderboard-state">The board is quiet for now — check back after a few coins are earned.</div> : <div className="leaderboard-list">
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
                      aria-label={move > 0 ? `Up ${move} places` : `Down ${Math.abs(move)} places`}
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
                <span className="leaderboard-identity"><strong>{hidden ? "Private member" : entry.display_name || entry.username || "Niko member"}</strong>{hidden ? <small>Identity hidden · still in the rankings</small> : entry.username && entry.display_name ? <small>@{entry.username}</small> : null}</span>
                <motion.strong
                  className="leaderboard-worth"
                  key={`${entry.key}-${entry.net_worth}`}
                  initial={{ opacity: move === 0 ? 0.55 : 1 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: reduceMotion ? 0 : 0.45 }}
                >
                  {formatNumber(entry.net_worth)} <small>coins</small>
                </motion.strong>
              </motion.article>;
            })}
          </AnimatePresence>
        </div>}
        {data && data.pages > 1 && <nav className="leaderboard-pagination" aria-label="Leaderboard pages">
          <button className="button button-muted button-small" type="button" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page <= 1}><Icon name="arrow" /> Previous</button>
          <span>Page <strong>{page}</strong> of {data.pages}</span>
          <button className="button button-muted button-small" type="button" onClick={() => setPage((current) => Math.min(data.pages, current + 1))} disabled={page >= data.pages}>Next <Icon name="arrow" /></button>
        </nav>}
      </section>
      <aside className="leaderboard-privacy-note"><Icon name="shield" /><p><strong>Your identity, your call.</strong> Set your economy profile to private in <a href="/dashboard">your dashboard</a>. You’ll stay on the list; only you, official Niko staff, and people who share a guild with you can see your identity.</p></aside>
    </main>
    <Footer />
  </>;
}
