import { AnimatedValue, CoinLabel, DashHeading } from "./DashboardViews";
import { siteHref } from "../../router";
import { Icon } from "../Icon";
import { formatNumber } from "../../utils/format";
import type { EconomyStanding, EconomyTransaction, LotteryStanding } from "../../types";
import { useStrings } from "../../i18n";

type Translate = (key: string, values?: Record<string, string | number>) => string;

/** The vote streak caps at ten steps on the server; the track mirrors that. */
const STREAK_STEPS = 10;

/**
 * A round the API has not reported yet. The lottery card is one panel among
 * several, so a payload from an older build leaves an honest "no round yet"
 * card instead of taking the whole tab down.
 */
const NO_ROUND: LotteryStanding = {
  pot: 0,
  participants: 0,
  tickets: 0,
  your_tickets: 0,
  ticket_price: 0,
  next_draw: 0,
  last_winner: null,
  last_pot: 0,
  open: false,
};

function signedAmount(amount: number) {
  const sign = amount >= 0 ? "+" : "−";
  return `${sign}${formatNumber(Math.abs(amount))}`;
}

function rankLabel(rank: number | null, total: number | null, t: Translate) {
  if (rank === null) return t("economy.rankingSoon");
  return total ? t("economy.rankOf", { rank: formatNumber(rank), total: formatNumber(total) }) : `#${formatNumber(rank)}`;
}

/**
 * The draw runs on the bot's clock, so the card counts down to the same unix
 * second the economy tick compares against rather than to a client date.
 */
function drawCountdown(nextDraw: number, t: Translate) {
  if (!nextDraw) return t("economy.roundSoon");
  const remaining = Math.max(0, nextDraw - Math.floor(Date.now() / 1000));
  if (remaining === 0) return t("economy.drawingNow");
  const days = Math.floor(remaining / 86400);
  const hours = Math.floor((remaining % 86400) / 3600);
  const minutes = Math.floor((remaining % 3600) / 60);
  if (days) return t("economy.drawsInDays", { days, hours });
  if (hours) return t("economy.drawsInHours", { hours, minutes });
  return t("economy.drawsInMinutes", { minutes });
}

/** What the last draw paid, or a line that says no draw has happened yet. */
function lastDrawLabel(lottery: LotteryStanding, t: Translate) {
  if (!lottery.last_winner) return t("economy.noWinnerYet");
  return t("economy.lastDraw", { winner: lottery.last_winner, coins: formatNumber(lottery.last_pot) });
}

/**
 * The round, in the member's terms: what is at stake, who is in it, and whether
 * the viewer holds a ticket. A ticket is the only way into the draw, so the
 * viewer's own count is the card's main call to action.
 */
function lotteryNote(lottery: LotteryStanding, t: Translate) {
  if (lottery.your_tickets > 0) {
    const chance = lottery.tickets > 0
      ? t("economy.ticketShare", { percent: Math.round((lottery.your_tickets / lottery.tickets) * 100) })
      : "";
    return t("economy.ticketsHeld", { yours: formatNumber(lottery.your_tickets), total: formatNumber(lottery.tickets), chance });
  }
  if (lottery.participants === 0) return t("economy.noTicketsSold");
  return t("economy.notInRound");
}

function nextVoteLabel(standing: EconomyStanding["vote"], t: Translate) {
  if (standing.can_vote) return t("economy.canVoteNow");
  const remaining = Math.max(0, standing.next_vote_at - Math.floor(Date.now() / 1000));
  const hours = Math.floor(remaining / 3600);
  const minutes = Math.floor((remaining % 3600) / 60);
  return t("economy.nextVoteIn", { hours, minutes });
}

/**
 * A ledger row keeps four facts in two columns: what happened, on which day, and
 * what it was worth. The timestamp is compact on the row and exact in its title.
 */
function TransactionRow({ entry }: { entry: EconomyTransaction }) {
  const { t } = useStrings("dashboard");
  const at = new Date(entry.ts * 1000);
  return <li className="economy-transaction">
    <span className="economy-transaction-kind">{entry.label || entry.kind}</span>
    <span className="economy-transaction-note">{entry.note || t("economy.activityFallback")}</span>
    <span className={`economy-transaction-amount${entry.amount >= 0 ? " is-gain" : " is-loss"}`}>{signedAmount(entry.amount)} <CoinLabel /></span>
    <time dateTime={at.toISOString()} title={at.toLocaleString(undefined, { weekday: "long", year: "numeric", month: "long", day: "numeric", hour: "numeric", minute: "numeric", second: "numeric" })}>
      {at.toLocaleString(undefined, { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "numeric" })}
    </time>
  </li>;
}

export function EconomyView({ standing }: { standing: EconomyStanding }) {
  const { t } = useStrings("dashboard");
  const vote = standing.vote;
  const lottery = standing.lottery ?? NO_ROUND;
  const filledSteps = Math.min(Math.max(vote.streak, 0), STREAK_STEPS);
  return <>
    <DashHeading
      eyebrow={t("economy.eyebrow")}
      title={t("economy.title")}
      text={t("economy.text")}
    />
    <div className="economy-layout">
      <section className="dash-panel">
        <div className="economy-headline">
          <div>
            <span className="panel-kicker">{t("dash.netWorth")}</span>
            <AnimatedValue value={standing.net_worth}>{formatNumber(standing.net_worth)} <CoinLabel /></AnimatedValue>
            <small>{t("economy.walletSplit", { wallet: formatNumber(standing.balance), vault: formatNumber(standing.bank) })}</small>
          </div>
          <div className="achievement-summary-chips">
            <span className="achievement-chip"><Icon name="chart" /><strong>{t("economy.globalRankChip", { rank: rankLabel(standing.global_rank, standing.account_count, t) })}</strong></span>
            <span className="achievement-chip"><Icon name="guild_achievements" /><strong>{t("economy.badgesOf", { unlocked: formatNumber(standing.achievements_unlocked), total: formatNumber(standing.achievements_total) })}</strong></span>
          </div>
        </div>
        <div className="economy-stat-grid">
          <div className="economy-stat"><span>{t("economy.level")}</span><AnimatedValue value={standing.level}>{formatNumber(standing.level)}</AnimatedValue><small>{t("dash.workingAs", { job: standing.job_name })}</small></div>
          <div className="economy-stat"><span>{t("economy.bankTier")}</span><AnimatedValue value={standing.bank_tier + 1}>{formatNumber(standing.bank_tier + 1)}</AnimatedValue><small>{t("economy.bankTierHint")}</small></div>
          <div className="economy-stat"><span>{t("dash.dailyStreak")}</span><AnimatedValue value={standing.daily_streak}>{formatNumber(standing.daily_streak)}</AnimatedValue><small>{t("economy.streakHint")}</small></div>
          <div className="economy-stat"><span>{t("dash.totalEarned")}</span><AnimatedValue value={standing.total_earned}>{formatNumber(standing.total_earned)} <CoinLabel /></AnimatedValue><small>{t("economy.spentOverall", { coins: formatNumber(standing.total_spent) })}</small></div>
          <div className="economy-stat"><span>{t("economy.shiftsWorked")}</span><AnimatedValue value={standing.times_worked}>{formatNumber(standing.times_worked)}</AnimatedValue><small>{t("economy.shiftsHint")}</small></div>
          <div className="economy-stat is-accent"><span>{t("dash.achievements")}</span><AnimatedValue value={`${standing.achievements_unlocked}/${standing.achievements_total}`}>{formatNumber(standing.achievements_unlocked)} / {formatNumber(standing.achievements_total)}</AnimatedValue><small>{t("economy.coinsFromBadges", { coins: formatNumber(standing.achievement_coins) })}</small></div>
        </div>
      </section>

      <section className="dash-panel">
        <div className="panel-heading">
          <div><span className="panel-kicker">{t("economy.lotteryKicker")}</span><h3>{t("economy.lotteryTitle")}</h3></div>
          <span className="panel-icon"><Icon name="guild_achievements" /></span>
        </div>
        <div className={`lottery-card${lottery.your_tickets > 0 ? " is-entered" : ""}`}>
          <div className="lottery-prize">
            <strong>{formatNumber(lottery.pot)} <CoinLabel /></strong>
            <span>{drawCountdown(lottery.next_draw, t)}</span>
          </div>
          <div className="lottery-chips">
            <span className="lottery-chip">{t("economy.entrants")}<strong>{formatNumber(lottery.participants)}</strong></span>
            <span className="lottery-chip">{t("economy.ticketsInPlay")}<strong>{formatNumber(lottery.tickets)}</strong></span>
            <span className="lottery-chip">{t("economy.yourTickets")}<strong>{formatNumber(lottery.your_tickets)}</strong></span>
            <span className="lottery-chip">{t("economy.ticketPrice")}<strong>{lottery.ticket_price ? <>{formatNumber(lottery.ticket_price)} <CoinLabel /></> : "—"}</strong></span>
          </div>
          <p className="economy-panel-note">{lotteryNote(lottery, t)}</p>
          <small className="lottery-last">{lastDrawLabel(lottery, t)}</small>
          <p className="lottery-how">
            {t("economy.lotteryHowBefore")} <code>/lottery buy &lt;count&gt;</code>{t("economy.lotteryHowMiddle")} <code>#lottery</code> {t("economy.lotteryHowAfter")}
          </p>
        </div>
      </section>

      <section className="dash-panel">
        <div className="panel-heading">
          <div><span className="panel-kicker">{t("economy.voteKicker")}</span><h3>{t("economy.voteTitle")}</h3></div>
          <span className="panel-icon"><Icon name="spark" /></span>
        </div>
        <div className="vote-card">
          <div className="vote-card-head">
            <Icon name="check" />
            <strong>{vote.streak > 0 ? t("economy.votesInARow", { count: formatNumber(vote.streak) }) : t("economy.noVoteStreak")}</strong>
          </div>
          <div className="vote-streak-track" role="img" aria-label={t("economy.streakTrackAria", { streak: vote.streak, steps: STREAK_STEPS })}>
            {Array.from({ length: STREAK_STEPS }, (_, index) =>
              <span key={index} className={`vote-streak-step${index < filledSteps ? " is-filled" : ""}`} />)}
          </div>
          <small>{t("economy.voteHint")}</small>
          <div className="vote-multipliers">
            <span className="vote-multiplier-chip">{t("economy.voteReward")}<strong>x{vote.reward_multiplier}</strong></span>
            <span className="vote-multiplier-chip">{t("economy.dailyAndWork")}<strong>x{vote.earnings_multiplier}</strong></span>
            <span className="vote-multiplier-chip">{t("economy.totalVotes")}<strong>{formatNumber(vote.votes)}</strong></span>
            <span className="vote-multiplier-chip">{t("economy.bestStreak")}<strong>{formatNumber(vote.best_streak)}</strong></span>
          </div>
          <p className="economy-panel-note">
            {nextVoteLabel(vote, t)}
            {vote.last_vote > 0 ? t("economy.lastVote", { date: new Date(vote.last_vote * 1000).toLocaleString(undefined, { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "numeric" }) }) : t("economy.voteToStart")}
          </p>
          <a className="button button-muted button-small" href={vote.vote_url} target="_blank" rel="noreferrer">
            {t("economy.voteOnTopgg")} <Icon name="external" />
          </a>
        </div>
      </section>

      <div className="economy-columns">
        <section className="dash-panel">
          <div className="panel-heading">
            <div><span className="panel-kicker">{t("economy.globalKicker")}</span><h3>{t("economy.whereYouRank")}</h3></div>
            <span className="panel-icon"><Icon name="chart" /></span>
          </div>
          <div className="metric-list">
            <div><span>{t("economy.globalRank")}</span><AnimatedValue value={standing.global_rank ?? 0}>{standing.global_rank ? `#${formatNumber(standing.global_rank)}` : t("economy.unranked")}</AnimatedValue></div>
            <div><span>{t("economy.rankedAccounts")}</span><AnimatedValue value={standing.account_count ?? 0}>{formatNumber(standing.account_count ?? 0)}</AnimatedValue></div>
            <div><span>{t("economy.coinsFromBadgeShort")}</span><AnimatedValue value={standing.achievement_coins}>{formatNumber(standing.achievement_coins)}</AnimatedValue></div>
            <div><span>{t("economy.lifetimeEarnings")}</span><AnimatedValue value={standing.total_earned}>{formatNumber(standing.total_earned)}</AnimatedValue></div>
          </div>
          <p className="economy-panel-note">{t("economy.rankNote")}</p>
          <a className="button button-muted button-small" href={siteHref("/leaderboard")}>{t("economy.openLeaderboard")} <Icon name="arrow" /></a>
        </section>

        <section className="dash-panel">
          <div className="panel-heading">
            <div><span className="panel-kicker">{t("economy.activityKicker")}</span><h3>{t("economy.activityTitle")}</h3></div>
            <span className="panel-icon"><Icon name="chart" /></span>
          </div>
          {standing.transactions.length
            ? <ul className="economy-transaction-list">{standing.transactions.map((entry, index) => <TransactionRow key={`${entry.ts}-${entry.kind}-${index}`} entry={entry} />)}</ul>
            : <div className="economy-empty">{t("economy.activityEmpty")}</div>}
        </section>
      </div>
    </div>
  </>;
}
