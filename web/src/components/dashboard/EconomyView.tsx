import { CoinLabel, DashHeading } from "./DashboardViews";
import { Icon } from "../Icon";
import { formatNumber } from "../../utils/format";
import type { EconomyStanding, EconomyTransaction } from "../../types";

/** The vote streak caps at ten steps on the server; the track mirrors that. */
const STREAK_STEPS = 10;

function signedAmount(amount: number) {
  const sign = amount >= 0 ? "+" : "−";
  return `${sign}${formatNumber(Math.abs(amount))}`;
}

function rankLabel(rank: number | null, total: number | null) {
  if (rank === null) return "Ranking soon";
  return total ? `#${formatNumber(rank)} of ${formatNumber(total)}` : `#${formatNumber(rank)}`;
}

function nextVoteLabel(standing: EconomyStanding["vote"]) {
  if (standing.can_vote) return "A vote counts right now.";
  const remaining = Math.max(0, standing.next_vote_at - Math.floor(Date.now() / 1000));
  const hours = Math.floor(remaining / 3600);
  const minutes = Math.floor((remaining % 3600) / 60);
  return `Next counted vote in ${hours}h ${minutes}m.`;
}

/**
 * A ledger row keeps four facts in two columns: what happened, on which day, and
 * what it was worth. The timestamp is compact on the row and exact in its title.
 */
function TransactionRow({ entry }: { entry: EconomyTransaction }) {
  const at = new Date(entry.ts * 1000);
  return <li className="economy-transaction">
    <span className="economy-transaction-kind">{entry.kind}</span>
    <span className="economy-transaction-note">{entry.note || "Economy activity"}</span>
    <span className={`economy-transaction-amount${entry.amount >= 0 ? " is-gain" : " is-loss"}`}>{signedAmount(entry.amount)} <CoinLabel /></span>
    <time dateTime={at.toISOString()} title={at.toLocaleString(undefined, { weekday: "long", year: "numeric", month: "long", day: "numeric", hour: "numeric", minute: "numeric", second: "numeric" })}>
      {at.toLocaleString(undefined, { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "numeric" })}
    </time>
  </li>;
}

export function EconomyView({ standing }: { standing: EconomyStanding }) {
  const vote = standing.vote;
  const filledSteps = Math.min(Math.max(vote.streak, 0), STREAK_STEPS);
  return <>
    <DashHeading
      eyebrow="Personal · economy"
      title="Your economy standing."
      text="Wallets, vaults, streaks and voting, in one place. The economy is global, so these numbers follow your Niko account into every server — no server needs to be selected to read them."
    />
    <div className="economy-layout">
      <section className="dash-panel">
        <div className="economy-headline">
          <div>
            <span className="panel-kicker">Net worth</span>
            <strong>{formatNumber(standing.net_worth)} <CoinLabel /></strong>
            <small>{formatNumber(standing.balance)} in your wallet · {formatNumber(standing.bank)} in the vault</small>
          </div>
          <div className="achievement-summary-chips">
            <span className="achievement-chip"><Icon name="chart" /><strong>Global rank {rankLabel(standing.global_rank, standing.account_count)}</strong></span>
            <span className="achievement-chip"><Icon name="guild_achievements" /><strong>{formatNumber(standing.achievements_unlocked)} of {formatNumber(standing.achievements_total)} badges</strong></span>
          </div>
        </div>
        <div className="economy-stat-grid">
          <div className="economy-stat"><span>Level</span><strong>{formatNumber(standing.level)}</strong><small>Working as {standing.job_name}</small></div>
          <div className="economy-stat"><span>Bank tier</span><strong>{formatNumber(standing.bank_tier + 1)}</strong><small>Vault upgrades raise interest</small></div>
          <div className="economy-stat"><span>Daily streak</span><strong>{formatNumber(standing.daily_streak)}</strong><small>Days claimed in a row</small></div>
          <div className="economy-stat"><span>Total earned</span><strong>{formatNumber(standing.total_earned)} <CoinLabel /></strong><small>{formatNumber(standing.total_spent)} spent overall</small></div>
          <div className="economy-stat"><span>Shifts worked</span><strong>{formatNumber(standing.times_worked)}</strong><small>Across every job shift</small></div>
          <div className="economy-stat is-accent"><span>Achievements</span><strong>{formatNumber(standing.achievements_unlocked)} / {formatNumber(standing.achievements_total)}</strong><small>{formatNumber(standing.achievement_coins)} coins won from badges</small></div>
        </div>
      </section>

      <section className="dash-panel">
        <div className="panel-heading">
          <div><span className="panel-kicker">top.gg voting</span><h3>Vote streak &amp; multipliers</h3></div>
          <span className="panel-icon"><Icon name="spark" /></span>
        </div>
        <div className="vote-card">
          <div className="vote-card-head">
            <Icon name="check" />
            <strong>{vote.streak > 0 ? `${formatNumber(vote.streak)} votes in a row` : "No active vote streak yet"}</strong>
          </div>
          <div className="vote-streak-track" role="img" aria-label={`Vote streak ${vote.streak} of ${STREAK_STEPS} bonus steps`}>
            {Array.from({ length: STREAK_STEPS }, (_, index) =>
              <span key={index} className={`vote-streak-step${index < filledSteps ? " is-filled" : ""}`} />)}
          </div>
          <small>Every counted vote pays coins, and a live streak also boosts your daily and work earnings — up to the tenth step.</small>
          <div className="vote-multipliers">
            <span className="vote-multiplier-chip">Vote reward<strong>x{vote.reward_multiplier}</strong></span>
            <span className="vote-multiplier-chip">Daily &amp; work<strong>x{vote.earnings_multiplier}</strong></span>
            <span className="vote-multiplier-chip">Total votes<strong>{formatNumber(vote.votes)}</strong></span>
            <span className="vote-multiplier-chip">Best streak<strong>{formatNumber(vote.best_streak)}</strong></span>
          </div>
          <p className="economy-panel-note">
            {nextVoteLabel(vote)}
            {vote.last_vote > 0 ? ` Last counted vote: ${new Date(vote.last_vote * 1000).toLocaleString(undefined, { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "numeric" })}.` : " Vote once to start a streak."}
          </p>
          <a className="button button-muted button-small" href={vote.vote_url} target="_blank" rel="noreferrer">
            Vote on top.gg <Icon name="external" />
          </a>
        </div>
      </section>

      <div className="economy-columns">
        <section className="dash-panel">
          <div className="panel-heading">
            <div><span className="panel-kicker">Global</span><h3>Where you rank</h3></div>
            <span className="panel-icon"><Icon name="chart" /></span>
          </div>
          <div className="metric-list">
            <div><span>Global rank</span><strong>{standing.global_rank ? `#${formatNumber(standing.global_rank)}` : "Unranked"}</strong></div>
            <div><span>Ranked accounts</span><strong>{formatNumber(standing.account_count ?? 0)}</strong></div>
            <div><span>Coins from badges</span><strong>{formatNumber(standing.achievement_coins)}</strong></div>
            <div><span>Lifetime earnings</span><strong>{formatNumber(standing.total_earned)}</strong></div>
          </div>
          <p className="economy-panel-note">Your account is ranked against every Niko member, not against the members of one server. The public leaderboard shows the same standings.</p>
          <a className="button button-muted button-small" href="/leaderboard">Open the public leaderboard <Icon name="arrow" /></a>
        </section>

        <section className="dash-panel">
          <div className="panel-heading">
            <div><span className="panel-kicker">Recent activity</span><h3>Latest ledger entries</h3></div>
            <span className="panel-icon"><Icon name="chart" /></span>
          </div>
          {standing.transactions.length
            ? <ul className="economy-transaction-list">{standing.transactions.map((entry, index) => <TransactionRow key={`${entry.ts}-${entry.kind}-${index}`} entry={entry} />)}</ul>
            : <div className="economy-empty">Nothing recorded yet — work a shift or claim your daily reward.</div>}
        </section>
      </div>
    </div>
  </>;
}
