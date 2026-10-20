import { AnimatedValue, CoinLabel, DashHeading, LiveChip } from "./DashboardViews";
import { Icon } from "../Icon";
import { formatNumber } from "../../utils/format";
import type { AchievementEntry, AchievementsResponse, AchievementSeason } from "../../types";

/** The day an event opens or closes, as a reader would say it out loud. */
function seasonDay(timestamp: number) {
  return new Date(timestamp * 1000).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function SeasonChip({ season }: { season: AchievementSeason }) {
  return <small className={`achievement-season${season.active ? " is-active" : ""}`}>
    {season.active
      ? `${season.label} · open until ${seasonDay(season.ends_at)}`
      : `${season.label} · returns ${seasonDay(season.starts_at)}`}
  </small>;
}

function AchievementCard({ entry }: { entry: AchievementEntry }) {
  const percent = Math.max(0, Math.min(entry.progress.percent, 100));
  return <article className={`achievement-card${entry.unlocked ? " is-unlocked" : ""}`}>
    <div className="achievement-card-head">
      {entry.icon_url
        ? <span className="achievement-emoji is-logo"><img src={entry.icon_url} alt="" aria-hidden="true" /></span>
        : <span className="achievement-emoji" aria-hidden="true">{entry.emoji}</span>}
      <span>
        <strong>{entry.name}</strong>
        <small className="achievement-description">{entry.description}</small>
        {entry.season && <SeasonChip season={entry.season} />}
      </span>
    </div>
    <div
      className="achievement-bar"
      role="progressbar"
      aria-label={`${entry.name} progress`}
      aria-valuenow={entry.progress.current}
      aria-valuemin={0}
      aria-valuemax={entry.progress.target}
    >
      <span className="achievement-bar-fill" style={{ width: `${percent}%` }} />
    </div>
    <div className="achievement-foot">
      <span>
        {formatNumber(entry.progress.current)} / {formatNumber(entry.progress.target)}
        {/* A seasonal badge counts inside its window only, and the bar is the
            in-window measure, so the number is labelled rather than left to
            read like a lifetime total. */}
        {entry.season?.active && !entry.unlocked ? " this event" : ""}
      </span>
      <span className="achievement-reward">
        {entry.unlocked ? <Icon name="check" /> : <Icon name="lock" />}
        {formatNumber(entry.reward)} <CoinLabel />{entry.unlocked ? " paid" : ""}
      </span>
    </div>
  </article>;
}

export function AchievementsView({ achievements, liveAt = null, liveStale = false }: { achievements: AchievementsResponse; liveAt?: number | null; liveStale?: boolean }) {
  const locked = achievements.achievements.filter((entry) => !entry.unlocked);
  const unlocked = achievements.achievements.filter((entry) => entry.unlocked);
  const overallPercent = achievements.total ? Math.round((achievements.unlocked / achievements.total) * 100) : 0;
  return <>
    <DashHeading
      eyebrow="People · achievements"
      title="Badges worth chasing."
      text="Every badge pays coins the moment it unlocks. Progress here comes from your Niko account, which is shared across every server Niko is in."
    />
    <div className="achievement-layout">
      <div className="achievement-summary">
        <div>
          <span className="panel-kicker">Collected</span>
          <AnimatedValue value={`${achievements.unlocked}/${achievements.total}`}>{formatNumber(achievements.unlocked)} of {formatNumber(achievements.total)}</AnimatedValue>
          <small>{overallPercent}% of every badge unlocked</small>
        </div>
        <div className="achievement-summary-chips">
          <LiveChip liveAt={liveAt} liveStale={liveStale} />
          <span className="achievement-chip"><Icon name="check" />Earned from badges <AnimatedValue value={achievements.coins_earned}>{formatNumber(achievements.coins_earned)} <CoinLabel /></AnimatedValue></span>
          <span className="achievement-chip"><Icon name="lock" />Still on the table <AnimatedValue value={achievements.coins_available}>{formatNumber(achievements.coins_available)} <CoinLabel /></AnimatedValue></span>
        </div>
      </div>

      <section className="dash-panel">
        <div className="panel-heading">
          <div><span className="panel-kicker">In progress</span><h3>{locked.length ? `${formatNumber(locked.length)} badges left` : "Every badge unlocked"}</h3></div>
          <span className="panel-icon"><Icon name="spark" /></span>
        </div>
        {locked.length
          ? <div className="achievement-grid">{locked.map((entry) => <AchievementCard key={entry.id} entry={entry} />)}</div>
          : <div className="economy-empty">You have collected every badge. New ones arrive with future economy updates.</div>}
      </section>

      <section className="dash-panel">
        <div className="panel-heading">
          <div><span className="panel-kicker">Unlocked</span><h3>{unlocked.length ? "Your badge case" : "Nothing unlocked yet"}</h3></div>
          <span className="panel-icon"><Icon name="shield" /></span>
        </div>
        {unlocked.length
          ? <div className="achievement-grid">{unlocked.map((entry) => <AchievementCard key={entry.id} entry={entry} />)}</div>
          : <div className="economy-empty">Work a first shift or claim your daily reward to start collecting.</div>}
      </section>
    </div>
  </>;
}
