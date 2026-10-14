import { DashHeading } from "./DashboardViews";
import { Icon } from "../Icon";
import { formatNumber } from "../../utils/format";
import type { AchievementEntry, AchievementsResponse } from "../../types";

function AchievementCard({ entry }: { entry: AchievementEntry }) {
  const percent = Math.max(0, Math.min(entry.progress.percent, 100));
  return <article className={`achievement-card${entry.unlocked ? " is-unlocked" : ""}`}>
    <div className="achievement-card-head">
      <span className="achievement-emoji" aria-hidden="true">{entry.emoji}</span>
      <span>
        <strong>{entry.name}</strong>
        <small className="achievement-description">{entry.description}</small>
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
      <span>{formatNumber(entry.progress.current)} / {formatNumber(entry.progress.target)}</span>
      <span className="achievement-reward">
        {entry.unlocked ? <Icon name="check" /> : <Icon name="lock" />}
        {entry.unlocked ? `${formatNumber(entry.reward)} 🥐 paid` : `${formatNumber(entry.reward)} 🥐`}
      </span>
    </div>
  </article>;
}

export function AchievementsView({ achievements }: { achievements: AchievementsResponse }) {
  const locked = achievements.achievements.filter((entry) => !entry.unlocked);
  const unlocked = achievements.achievements.filter((entry) => entry.unlocked);
  const overallPercent = achievements.total ? Math.round((achievements.unlocked / achievements.total) * 100) : 0;
  return <>
    <DashHeading
      eyebrow="People · achievements"
      title="Badges worth chasing."
      text="Every badge pays coins the moment it unlocks. Progress here comes from your café account, which is shared across every server Niko is in."
    />
    <div className="achievement-summary">
      <div>
        <span className="panel-kicker">Collected</span>
        <strong>{formatNumber(achievements.unlocked)} of {formatNumber(achievements.total)}</strong>
        <small>{overallPercent}% of every badge unlocked</small>
      </div>
      <div className="achievement-summary-chips">
        <span className="achievement-chip"><Icon name="check" />Earned from badges <strong>{formatNumber(achievements.coins_earned)} 🥐</strong></span>
        <span className="achievement-chip"><Icon name="lock" />Still on the table <strong>{formatNumber(achievements.coins_available)} 🥐</strong></span>
      </div>
    </div>

    <section className="dash-panel economy-panel">
      <div className="panel-heading">
        <div><span className="panel-kicker">In progress</span><h3>{locked.length ? `${formatNumber(locked.length)} badges left` : "Every badge unlocked"}</h3></div>
        <span className="panel-icon"><Icon name="spark" /></span>
      </div>
      {locked.length
        ? <div className="achievement-grid">{locked.map((entry) => <AchievementCard key={entry.id} entry={entry} />)}</div>
        : <div className="economy-empty">You have collected every café badge. New ones arrive with future café updates.</div>}
    </section>

    <section className="dash-panel economy-panel">
      <div className="panel-heading">
        <div><span className="panel-kicker">Unlocked</span><h3>{unlocked.length ? "Your badge case" : "Nothing unlocked yet"}</h3></div>
        <span className="panel-icon"><Icon name="shield" /></span>
      </div>
      {unlocked.length
        ? <div className="achievement-grid">{unlocked.map((entry) => <AchievementCard key={entry.id} entry={entry} />)}</div>
        : <div className="economy-empty">Work a first shift or claim your daily treats to start collecting.</div>}
    </section>
  </>;
}
