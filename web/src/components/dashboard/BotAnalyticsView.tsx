import { useMemo, useRef, useState } from "react";
import type { KeyboardEvent as ReactKeyboardEvent, PointerEvent as ReactPointerEvent } from "react";
import { getStaffAnalytics } from "../../api";
import { useLiveResource } from "../../hooks/useLiveResource";
import type { StaffAnalytics, StaffAnalyticsDay } from "../../types";
import { formatNumber } from "../../utils/format";
import { Icon } from "../Icon";
import { useStrings } from "../../i18n";

/** The API always returns the long window; the toggle slices it client-side. */
const WINDOWS = [7, 14, 30] as const;
const FETCH_DAYS = 30;

// Labels stay catalogue keys and are translated where the mix is rendered.
const KIND_ROWS = [
  { key: "slash", label: "analytics.kindSlash", color: "#aab1ba" },
  { key: "prefix", label: "analytics.kindPrefix", color: "#7f9db8" },
  { key: "context", label: "analytics.kindContext", color: "#c8a882" },
] as const;

function dayLabel(date: string) {
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric" }).format(new Date(`${date}T12:00:00`));
}

function shareLabel(value: number) {
  return `${Math.round(value * 1000) / 10}%`;
}

function uptimeLabel(seconds: number | null) {
  if (seconds === null) return "—";
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (days) return `${days}d ${hours}h`;
  if (hours) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function useDayScrub(count: number) {
  const [selected, setSelected] = useState<number | null>(null);
  const select = (index: number) => {
    if (!count) return;
    setSelected(Math.min(count - 1, Math.max(0, Math.round(index))));
  };
  const move = (delta: number) => {
    setSelected((current) => {
      if (!count) return null;
      if (current === null) return delta > 0 ? 0 : count - 1;
      return Math.min(count - 1, Math.max(0, current + delta));
    });
  };
  const clear = () => setSelected(null);
  return { selected, select, move, clear };
}

function capturePointer(event: ReactPointerEvent<SVGSVGElement>) {
  // A pointer that already ended has nothing to capture; this is only an
  // optimisation for drag scrubbing across the plot.
  try {
    event.currentTarget.setPointerCapture(event.pointerId);
  } catch {
    /* no active pointer to capture */
  }
}

function handleDayKeyDown(event: ReactKeyboardEvent<HTMLElement>, move: (delta: number) => void) {
  const delta = event.key === "ArrowRight" || event.key === "ArrowDown" ? 1
    : event.key === "ArrowLeft" || event.key === "ArrowUp" ? -1
      : 0;
  if (!delta) return;
  event.preventDefault();
  move(delta);
}

function UsageChart({ days, windowDays, onWindowChange }: {
  days: StaffAnalyticsDay[];
  windowDays: number;
  onWindowChange: (days: number) => void;
}) {
  const { t } = useStrings("dashboard");
  const values = days.map((day) => day.total);
  const total = values.reduce((sum, value) => sum + value, 0);
  const busiest = days.length ? days.reduce((best, day) => (day.total > best.total ? day : best)) : null;
  const max = Math.max(1, ...values);
  const plotLeft = 34;
  const plotRight = 326;
  const plotTop = 14;
  const plotBottom = 100;
  const xAt = (index: number) => (values.length > 1
    ? plotLeft + (index * (plotRight - plotLeft)) / (values.length - 1)
    : (plotLeft + plotRight) / 2);
  const yAt = (value: number) => plotBottom - (value / max) * (plotBottom - plotTop);
  const points = values.map((value, index) => `${xAt(index)},${yAt(value)}`).join(" ");
  const area = values.length ? `${plotLeft},${plotBottom} ${points} ${plotRight},${plotBottom}` : "";
  const ticks = [0, 0.5, 1].map((fraction) => ({
    y: plotBottom - fraction * (plotBottom - plotTop),
    value: Math.round(max * fraction),
  }));
  const chartRef = useRef<SVGSVGElement>(null);
  const { selected, select, move, clear } = useDayScrub(values.length);
  const activeDay = selected === null ? null : days[selected] ?? null;
  // Map the pointer through the SVG's own coordinates so a tap lands on the
  // same day whether the plot is letterboxed or squeezed onto a phone.
  const pick = (clientX: number) => {
    const svg = chartRef.current;
    const matrix = svg?.getScreenCTM();
    if (!svg || !matrix || !values.length) return;
    const point = svg.createSVGPoint();
    point.x = clientX;
    point.y = 0;
    const localX = point.matrixTransform(matrix.inverse()).x;
    const step = values.length > 1 ? (plotRight - plotLeft) / (values.length - 1) : 0;
    select(step ? (localX - plotLeft) / step : 0);
  };

  return <div className="bot-analytics-chart">
    <div className="bot-analytics-chart-head">
      <div className="bot-analytics-chart-total"><span>{t("analytics.commandsPerDay")}</span><strong>{formatNumber(total)}</strong></div>
      <div className="bot-analytics-range" role="group" aria-label={t("analytics.chartWindow")}>
        {WINDOWS.map((value) => <button
          type="button"
          key={value}
          className={value === windowDays ? "is-active" : ""}
          aria-pressed={value === windowDays}
          onClick={() => onWindowChange(value)}
        >{value}d</button>)}
      </div>
    </div>
    <div className="bot-analytics-chart-insights">
      <span>{t("stats.dailyAverage")} <strong>{formatNumber(days.length ? Math.round(total / days.length) : 0)}</strong></span>
      <span>{t("stats.busiestDay")} <strong>{busiest?.total ? `${formatNumber(busiest.total)} · ${dayLabel(busiest.date)}` : t("stats.noData")}</strong></span>
    </div>
    <div className={`bot-analytics-readout${activeDay ? " is-active" : ""}`} aria-live="polite" aria-atomic="true">
      {activeDay
        ? <><strong>{dayLabel(activeDay.date)}</strong><span>{t("analytics.dayReadout", { total: formatNumber(activeDay.total), slash: activeDay.slash, prefix: activeDay.prefix, context: activeDay.context, guilds: activeDay.guilds })}</span></>
        : <span>{t("analytics.inspectDay")}</span>}
    </div>
    <div
      className="bot-analytics-plot"
      role="group"
      tabIndex={0}
      aria-label={t("analytics.chartAria")}
      onKeyDown={(event) => handleDayKeyDown(event, move)}
    >
      <svg
        ref={chartRef}
        viewBox="0 0 340 120"
        role="img"
        aria-label={`Daily command counts for the last ${windowDays} days`}
        onPointerDown={(event) => { capturePointer(event); pick(event.clientX); }}
        onPointerMove={(event) => { if (event.pointerType === "mouse" || event.buttons) pick(event.clientX); }}
        onPointerLeave={(event) => { if (event.pointerType === "mouse" && !event.buttons) clear(); }}
      >
        <defs>
          <linearGradient id="bot-analytics-area-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.28" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
        </defs>
        {ticks.map((tick) => <g key={tick.y}>
          <line className="bot-analytics-gridline" x1={plotLeft} y1={tick.y} x2={plotRight} y2={tick.y} />
          <text className="bot-analytics-gridlabel" x={plotLeft - 7} y={tick.y + 3} textAnchor="end">{formatNumber(tick.value)}</text>
        </g>)}
        {values.length > 0 && <>
          <polygon className="bot-analytics-area" points={area} />
          <polyline className="bot-analytics-line" points={points} />
        </>}
        {values.map((value, index) => value > 0 && <circle
          key={days[index].date}
          className={`bot-analytics-dot${selected === index ? " is-selected" : ""}`}
          cx={xAt(index)}
          cy={yAt(value)}
          r={selected === index ? 3.4 : 1.9}
        />)}
        {selected !== null && <line className="bot-analytics-guide" x1={xAt(selected)} y1={plotTop} x2={xAt(selected)} y2={plotBottom} />}
      </svg>
    </div>
    <div className="bot-analytics-axis">
      <span>{days.length ? dayLabel(days[0].date) : ""}</span>
      <span>{days.length > 2 ? dayLabel(days[Math.floor((days.length - 1) / 2)].date) : ""}</span>
      <span>{days.length ? dayLabel(days[days.length - 1].date) : ""}</span>
    </div>
  </div>;
}

function CommandMix({ byKind }: { byKind: StaffAnalytics["usage"]["by_kind"] }) {
  const { t } = useStrings("dashboard");
  const sum = byKind.slash + byKind.prefix + byKind.context;
  const total = Math.max(1, sum);
  let cursor = 0;
  const stops = KIND_ROWS.map((row) => {
    const start = cursor;
    cursor += byKind[row.key];
    return `${row.color} ${(start / total) * 100}% ${(cursor / total) * 100}%`;
  }).join(", ");

  return <div className="bot-analytics-mix">
    <div className="bot-analytics-donut" style={{ background: sum ? `conic-gradient(${stops})` : "var(--surface-muted)" }} aria-hidden="true">
      <span><strong>{formatNumber(sum)}</strong><small>{t("analytics.allTimeShort")}</small></span>
    </div>
    <ul className="bot-analytics-legend">
      {KIND_ROWS.map((row) => <li key={row.key}>
        <i style={{ background: row.color }} />
        <span>{t(row.label)}</span>
        <strong>{formatNumber(byKind[row.key])}</strong>
        <small>{shareLabel((byKind[row.key] || 0) / total)}</small>
      </li>)}
    </ul>
  </div>;
}

export function BotAnalyticsView() {
  const { t } = useStrings("dashboard");
  const [range, setRange] = useState<number>(FETCH_DAYS);
  const { data, loading, error, stale, syncedAt, refresh } = useLiveResource<StaffAnalytics>(
    "staff-analytics",
    () => getStaffAnalytics(FETCH_DAYS),
    { intervalMs: 15_000, fallbackError: t("analytics.unavailable") },
  );

  const days = useMemo(() => (data ? data.usage.days.slice(-range) : []), [data, range]);
  if (loading && !data) {
    return <div className="bot-analytics bot-analytics-state"><div className="loading-ring" /><p>{t("analytics.loading")}</p></div>;
  }
  if (!data) {
    return <div className="bot-analytics bot-analytics-state">
      <Icon name="alert" />
      <p>{error || t("analytics.unavailable")}</p>
      <button type="button" className="button button-muted" onClick={refresh}>{t("analytics.retry")}</button>
    </div>;
  }

  const { bot, usage, languages, economy, growth } = data;
  const supportedShare = languages.guilds
    ? languages.languages.filter((row) => row.supported).reduce((sum, row) => sum + row.guilds, 0) / languages.guilds
    : 0;
  const topLanguages = languages.languages.slice(0, 8);
  const maxGuilds = Math.max(1, ...topLanguages.map((row) => row.guilds));
  const maxCommand = Math.max(1, ...usage.top_commands.map((row) => row.count));
  const maxJob = Math.max(1, ...(economy?.top_jobs.map((row) => row.count) ?? [1]));
  const growthStart = growth[0];
  const growthNow = growth[growth.length - 1];
  const guildDelta = growth.length > 1 && growthStart && growthNow ? growthNow.guilds - growthStart.guilds : null;

  return <div className="bot-analytics">
    <header className="bot-analytics-heading">
      <div>
        <span className="panel-kicker">{t("analytics.kicker")}</span>
        <h2>{t("analytics.title")}</h2>
        <p>{t("analytics.text")}</p>
      </div>
      <div className="bot-analytics-live">
        <span className={`bot-analytics-live-dot${bot.online ? " is-online" : ""}`} />
        <div>
          <strong>{t(bot.online ? "analytics.live" : "analytics.snapshot")}</strong>
          <small>{stale ? t("analytics.refreshFailed") : syncedAt ? t("analytics.updated", { time: new Date(syncedAt).toLocaleTimeString() }) : t("analytics.waiting")}</small>
        </div>
        <button type="button" className="button button-muted button-small" onClick={refresh}><Icon name="spark" />{t("analytics.refresh")}</button>
      </div>
    </header>

    <div className="bot-analytics-kpis">
      <article className="bot-analytics-kpi">
        <span>{t("analytics.guilds")}</span><strong>{formatNumber(bot.guilds)}</strong>
        <small>{t(bot.online ? "analytics.connectedNow" : "analytics.startupSnapshot")}{guildDelta !== null ? t("analytics.guildDelta", { delta: `${guildDelta > 0 ? "+" : ""}${guildDelta}` }) : ""}</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>{t("stats.members")}</span><strong>{formatNumber(bot.members)}</strong>
        <small>{t("analytics.acrossGuilds")}</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>{t("analytics.commandsToday")}</span><strong>{formatNumber(usage.today.total)}</strong>
        <small>{t("analytics.todayDetail", { guilds: formatNumber(usage.today.guilds), slash: formatNumber(usage.today.slash) })}</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>{t("analytics.last7Days")}</span><strong>{formatNumber(usage.totals.last_7_days)}</strong>
        <small>{t("analytics.inLast30", { count: formatNumber(usage.totals.last_30_days) })}</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>{t("analytics.allTimeCommands")}</span>        <strong>{formatNumber(usage.totals.lifetime)}</strong>
        <small>{t("analytics.sinceEnabled")}</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>{t("analytics.gatewayLatency")}</span><strong>{bot.latency_ms === null ? "—" : `${bot.latency_ms} ms`}</strong>
        <small>{bot.shard_count ? t(bot.shard_count === 1 ? "analytics.shardOne" : "analytics.shardMany", { count: bot.shard_count }) : t("analytics.singleConnection")}</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>{t("analytics.uptime")}</span><strong>{uptimeLabel(bot.uptime_seconds)}</strong>
        <small>{t("analytics.sinceStart")}</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>{t("analytics.economyProfiles")}</span><strong>{economy ? formatNumber(economy.profiles) : "—"}</strong>
        <small>{economy ? t("analytics.coinsInWallets", { count: formatNumber(economy.circulating) }) : t("analytics.economyUnavailable")}</small>
      </article>
    </div>

    <div className="bot-analytics-grid">
      <section className="bot-analytics-card is-wide">
        <div className="bot-analytics-card-heading">
          <div><span className="panel-kicker">{t("analytics.trafficKicker")}</span><h3>{t("analytics.trafficTitle")}</h3></div>
          <Icon name="chart" />
        </div>
        <UsageChart days={days} windowDays={range} onWindowChange={setRange} />
      </section>

      <section className="bot-analytics-card">
        <div className="bot-analytics-card-heading">
          <div><span className="panel-kicker">{t("analytics.mixKicker")}</span><h3>{t("analytics.mixTitle")}</h3></div>
        </div>
        <CommandMix byKind={usage.by_kind} />
      </section>

      <section className="bot-analytics-card">
        <div className="bot-analytics-card-heading">
          <div><span className="panel-kicker">{t("analytics.allTimeKicker")}</span><h3>{t("analytics.topCommands")}</h3></div>
          <span className="bot-analytics-card-tag">{usage.top_commands.length}</span>
        </div>
        {usage.top_commands.length === 0
          ? <p className="bot-analytics-empty">{t("analytics.noCommands")}</p>
          : <ol className="bot-analytics-bars">
            {usage.top_commands.map((row, index) => <li key={row.name}>
              <span className="bot-analytics-bar-rank">{index + 1}</span>
              <div className="bot-analytics-bar-body">
                <div className="bot-analytics-bar-head"><strong>/{row.name}</strong><span>{formatNumber(row.count)}</span></div>
                <div className="bot-analytics-bar"><i style={{ width: `${(row.count / maxCommand) * 100}%` }} /></div>
              </div>
              <span className="bot-analytics-bar-meta">{row.category} · {shareLabel(row.share)}</span>
            </li>)}
          </ol>}
      </section>

      <section className="bot-analytics-card">
        <div className="bot-analytics-card-heading">
          <div><span className="panel-kicker">{t("analytics.languageKicker")}</span><h3>{t("analytics.languageTitle")}</h3></div>
          <span className="bot-analytics-card-tag is-accent">{t("analytics.liveShare", { share: shareLabel(supportedShare) })}</span>
        </div>
        {topLanguages.length === 0
          ? <p className="bot-analytics-empty">{t("analytics.noLanguages")}</p>
          : <div className="bot-analytics-languages">
            {topLanguages.map((row) => <div className="bot-analytics-language" key={row.code}>
              <div className="bot-analytics-language-head">
                <strong>{row.label}</strong>
                <code>{row.code.toUpperCase()}</code>
                <span className={`bot-analytics-pill${row.supported ? " is-supported" : ""}`}>{t(row.supported ? "analytics.live" : "analytics.rolloutNext")}</span>
              </div>
              <div className="bot-analytics-bar"><i style={{ width: `${(row.guilds / maxGuilds) * 100}%` }} /></div>
              <small>{t("analytics.languageCounts", { guilds: formatNumber(row.guilds), members: formatNumber(row.members) })}</small>
            </div>)}
          </div>}
        {usage.by_language.length > 0 && <p className="bot-analytics-note">
          {t("analytics.byLanguage")} {usage.by_language.slice(0, 3).map((row) => `${row.code.toUpperCase()} ${shareLabel(row.share)}`).join(" · ")}
        </p>}
      </section>

      <section className="bot-analytics-card">
        <div className="bot-analytics-card-heading">
          <div><span className="panel-kicker">{t("analytics.economyKicker")}</span><h3>{t("analytics.economyTitle")}</h3></div>
          <Icon name="guild_economy" />
        </div>
        {!economy
          ? <p className="bot-analytics-empty">{t("analytics.economyReconnecting")}</p>
          : <>
            <div className="bot-analytics-stats">
              <div><span>{t("analytics.inWallets")}</span><strong>{formatNumber(economy.circulating)}</strong></div>
              <div><span>{t("analytics.inBanks")}</span><strong>{formatNumber(economy.banked)}</strong></div>
              <div><span>{t("analytics.medianWorth")}</span><strong>{formatNumber(economy.median)}</strong></div>
              <div><span>{t("analytics.averageWorth")}</span><strong>{formatNumber(economy.average)}</strong></div>
              <div><span>{t("analytics.averageLevel")}</span><strong>{economy.average_level}</strong></div>
              <div><span>{t("analytics.dailyStreaks")}</span><strong>{formatNumber(economy.active_streaks)}</strong></div>
            </div>
            <span className="bot-analytics-subheading">{t("analytics.topJobs")}</span>
            {economy.top_jobs.length === 0
              ? <p className="bot-analytics-empty">{t("analytics.noJobs")}</p>
              : <div className="bot-analytics-jobs">
                {economy.top_jobs.map((job) => <div className="bot-analytics-job" key={job.id}>
                  <span className="bot-analytics-job-name">{job.emoji} {job.name}</span>
                  <div className="bot-analytics-bar"><i style={{ width: `${(job.count / maxJob) * 100}%` }} /></div>
                  <small>{formatNumber(job.count)} · {shareLabel(job.share)}</small>
                </div>)}
              </div>}
          </>}
      </section>
    </div>
  </div>;
}
