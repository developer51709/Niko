import { AnimatedValue, CoinLabel, DashHeading } from "./DashboardViews";
import { Icon } from "../Icon";
import { formatNumber } from "../../utils/format";
import type { AchievementEntry, AchievementsResponse, AchievementSeason } from "../../types";
import { useStrings } from "../../i18n";

/** The day an event opens or closes, as a reader would say it out loud. */
function seasonDay(timestamp: number) {
  return new Date(timestamp * 1000).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function SeasonChip({ season }: { season: AchievementSeason }) {
  const { t } = useStrings("dashboard");
  return <small className={`achievement-season${season.active ? " is-active" : ""}`}>
    {t(season.active ? "achievements.seasonOpen" : "achievements.seasonReturns", { label: season.label, date: seasonDay(season.active ? season.ends_at : season.starts_at) })}
  </small>;
}

function AchievementCard({ entry }: { entry: AchievementEntry }) {
  const { t } = useStrings("dashboard");
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
      aria-label={t("achievements.progressAria", { name: entry.name })}
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
        {entry.season?.active && !entry.unlocked ? t("achievements.thisEvent") : ""}
      </span>
      <span className="achievement-reward">
        {entry.unlocked ? <Icon name="check" /> : <Icon name="lock" />}
        {formatNumber(entry.reward)} <CoinLabel />{entry.unlocked ? t("achievements.paid") : ""}
      </span>
    </div>
  </article>;
}

export function AchievementsView({ achievements }: { achievements: AchievementsResponse }) {
  const { t } = useStrings("dashboard");
  const locked = achievements.achievements.filter((entry) => !entry.unlocked);
  const unlocked = achievements.achievements.filter((entry) => entry.unlocked);
  const overallPercent = achievements.total ? Math.round((achievements.unlocked / achievements.total) * 100) : 0;
  return <>
    <DashHeading
      eyebrow={t("achievements.eyebrow")}
      title={t("achievements.title")}
      text={t("achievements.text")}
    />
    <div className="achievement-layout">
      <div className="achievement-summary">
        <div>
          <span className="panel-kicker">{t("achievements.collectedKicker")}</span>
          <AnimatedValue value={`${achievements.unlocked}/${achievements.total}`}>{t("achievements.collectedOf", { unlocked: formatNumber(achievements.unlocked), total: formatNumber(achievements.total) })}</AnimatedValue>
          <small>{t("achievements.percentUnlocked", { percent: overallPercent })}</small>
        </div>
        <div className="achievement-summary-chips">
          <span className="achievement-chip"><Icon name="check" />{t("achievements.earnedFromBadges")} <AnimatedValue value={achievements.coins_earned}>{formatNumber(achievements.coins_earned)} <CoinLabel /></AnimatedValue></span>
          <span className="achievement-chip"><Icon name="lock" />{t("achievements.stillAvailable")} <AnimatedValue value={achievements.coins_available}>{formatNumber(achievements.coins_available)} <CoinLabel /></AnimatedValue></span>
        </div>
      </div>

      <section className="dash-panel">
        <div className="panel-heading">
          <div><span className="panel-kicker">{t("achievements.progressKicker")}</span><h3>{locked.length ? t("achievements.badgesLeft", { count: formatNumber(locked.length) }) : t("achievements.allUnlocked")}</h3></div>
          <span className="panel-icon"><Icon name="spark" /></span>
        </div>
        {locked.length
          ? <div className="achievement-grid">{locked.map((entry) => <AchievementCard key={entry.id} entry={entry} />)}</div>
          : <div className="economy-empty">{t("achievements.allCollected")}</div>}
      </section>

      <section className="dash-panel">
        <div className="panel-heading">
          <div><span className="panel-kicker">{t("achievements.unlockedKicker")}</span><h3>{unlocked.length ? t("achievements.badgeCase") : t("achievements.nothingYet")}</h3></div>
          <span className="panel-icon"><Icon name="shield" /></span>
        </div>
        {unlocked.length
          ? <div className="achievement-grid">{unlocked.map((entry) => <AchievementCard key={entry.id} entry={entry} />)}</div>
          : <div className="economy-empty">{t("achievements.emptyHint")}</div>}
      </section>
    </div>
  </>;
}
