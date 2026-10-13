import { useEffect, useState } from "react";
import { api } from "../api";
import { PublicHeader } from "../components/PublicHeader";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { formatNumber } from "../utils/format";

type Entry = { rank: number; net_worth: number; private: boolean; username: string | null; display_name: string | null; avatar_url: string | null };
type PageData = { entries: Entry[]; page: number; page_size: number; total: number; pages: number };

export function LeaderboardPage() {
  const [page, setPage] = useState(1);
  const [data, setData] = useState<PageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    api<PageData>(`/api/economy/leaderboard?page=${page}`)
      .then((result) => { if (active) setData(result); })
      .catch((reason) => { if (active) setError(reason instanceof Error ? reason.message : "The leaderboard could not be loaded."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [page]);

  return <>
    <PublicHeader page="home" />
    <main className="shell page-main economy-leaderboard-page">
      <section className="leaderboard-hero">
        <span className="eyebrow">The Niko café · global standings</span>
        <h1>Who’s got the <em>treats?</em></h1>
        <p>Every coin counts. Climb the café rich list and see how your balance stacks up.</p>
      </section>
      <section className="leaderboard-panel" aria-label="Economy leaderboard">
        <div className="leaderboard-panel-heading">
          <div><span className="panel-kicker">🏆 Café rich list</span><h2>Top café-goers</h2><p>{data ? `${formatNumber(data.total)} profiles · ordered by net worth` : "The latest economy standings"}</p></div>
          <span className="leaderboard-live"><span className="status-dot" /> LIVE RANKS</span>
        </div>
        {loading ? <div className="leaderboard-state" role="status"><span className="loading-ring" />Loading café standings…</div> : error ? <div className="leaderboard-state leaderboard-error" role="alert">{error}</div> : !data?.entries.length ? <div className="leaderboard-state">The café is quiet for now — check back after a few coins are earned.</div> : <div className="leaderboard-list">
          {data.entries.map((entry) => {
            const hidden = entry.private && !entry.display_name;
            return <article className={`leaderboard-row${entry.rank <= 3 ? ` leaderboard-rank-${entry.rank}` : ""}`} key={entry.rank}>
              <span className="leaderboard-rank">{String(entry.rank).padStart(2, "0")}</span>
              {hidden ? <span className="leaderboard-avatar leaderboard-avatar-hidden"><Icon name="lock" /></span> : <span className="leaderboard-avatar">{entry.avatar_url ? <img src={entry.avatar_url} alt="" /> : (entry.display_name || "?").slice(0, 1).toUpperCase()}</span>}
              <span className="leaderboard-identity"><strong>{hidden ? "Private café-goer" : entry.display_name || entry.username || "Café-goer"}</strong>{hidden ? <small>Identity hidden · still in the rankings</small> : entry.username && entry.display_name ? <small>@{entry.username}</small> : null}</span>
              <strong className="leaderboard-worth">{formatNumber(entry.net_worth)} <small>coins</small></strong>
            </article>;
          })}
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
