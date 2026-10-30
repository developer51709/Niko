import { useMemo, useRef, useState } from "react";
import type { KeyboardEvent as ReactKeyboardEvent, PointerEvent as ReactPointerEvent } from "react";
import { getStaffAnalytics } from "../../api";
import { useLiveResource } from "../../hooks/useLiveResource";
import type { StaffAnalytics, StaffAnalyticsDay } from "../../types";
import { formatNumber } from "../../utils/format";
import { Icon } from "../Icon";

/** The API always returns the long window; the toggle slices it client-side. */
const WINDOWS = [7, 14, 30] as const;
const FETCH_DAYS = 30;

const KIND_ROWS = [
  { key: "slash", label: "Slash", color: "#aab1ba" },
  { key: "prefix", label: "Prefix", color: "#7f9db8" },
  { key: "context", label: "Context", color: "#c8a882" },
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
      <div className="bot-analytics-chart-total"><span>Commands per day</span><strong>{formatNumber(total)}</strong></div>
      <div className="bot-analytics-range" role="group" aria-label="Chart window">
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
      <span>Daily average <strong>{formatNumber(days.length ? Math.round(total / days.length) : 0)}</strong></span>
      <span>Busiest day <strong>{busiest?.total ? `${formatNumber(busiest.total)} · ${dayLabel(busiest.date)}` : "No data"}</strong></span>
    </div>
    <div className={`bot-analytics-readout${activeDay ? " is-active" : ""}`} aria-live="polite" aria-atomic="true">
      {activeDay
        ? <><strong>{dayLabel(activeDay.date)}</strong><span>{formatNumber(activeDay.total)} commands · {activeDay.slash} slash · {activeDay.prefix} prefix · {activeDay.context} context · {activeDay.guilds} guilds</span></>
        : <span>Hover, tap, or use the arrow keys to inspect a day.</span>}
    </div>
    <div
      className="bot-analytics-plot"
      role="group"
      tabIndex={0}
      aria-label="Daily command counts. Tap, hover, or use the arrow keys to inspect a day."
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
      <span><strong>{formatNumber(sum)}</strong><small>all time</small></span>
    </div>
    <ul className="bot-analytics-legend">
      {KIND_ROWS.map((row) => <li key={row.key}>
        <i style={{ background: row.color }} />
        <span>{row.label}</span>
        <strong>{formatNumber(byKind[row.key])}</strong>
        <small>{shareLabel((byKind[row.key] || 0) / total)}</small>
      </li>)}
    </ul>
  </div>;
}

export function BotAnalyticsView() {
  const [range, setRange] = useState<number>(FETCH_DAYS);
  const { data, loading, error, stale, syncedAt, refresh } = useLiveResource<StaffAnalytics>(
    "staff-analytics",
    () => getStaffAnalytics(FETCH_DAYS),
    { intervalMs: 15_000, fallbackError: "Bot analytics are temporarily unavailable." },
  );

  const days = useMemo(() => (data ? data.usage.days.slice(-range) : []), [data, range]);
  if (loading && !data) {
    return <div className="bot-analytics bot-analytics-state"><div className="loading-ring" /><p>Gathering bot-wide analytics…</p></div>;
  }
  if (!data) {
    return <div className="bot-analytics bot-analytics-state">
      <Icon name="alert" />
      <p>{error || "Bot analytics are temporarily unavailable."}</p>
      <button type="button" className="button button-muted" onClick={refresh}>Try again</button>
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
        <span className="panel-kicker">Bot-wide · live telemetry</span>
        <h2>Analytics</h2>
        <p>Command traffic, invocation mix, language reach and economy usage across every server Niko serves. Figures update every 15 seconds from the running bot.</p>
      </div>
      <div className="bot-analytics-live">
        <span className={`bot-analytics-live-dot${bot.online ? " is-online" : ""}`} />
        <div>
          <strong>{bot.online ? "Live" : "Snapshot"}</strong>
          <small>{stale ? "Refresh failed · showing last good data" : syncedAt ? `Updated ${new Date(syncedAt).toLocaleTimeString()}` : "Waiting for the first poll"}</small>
        </div>
        <button type="button" className="button button-muted button-small" onClick={refresh}><Icon name="spark" />Refresh</button>
      </div>
    </header>

    <div className="bot-analytics-kpis">
      <article className="bot-analytics-kpi">
        <span>Guilds</span><strong>{formatNumber(bot.guilds)}</strong>
        <small>{bot.online ? "Connected right now" : "From the startup snapshot"}{guildDelta !== null ? ` · ${guildDelta > 0 ? "+" : ""}${guildDelta} this window` : ""}</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>Members</span><strong>{formatNumber(bot.members)}</strong>
        <small>Across every connected guild</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>Commands today</span><strong>{formatNumber(usage.today.total)}</strong>
        <small>{formatNumber(usage.today.guilds)} guilds active · {formatNumber(usage.today.slash)} slash</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>Last 7 days</span><strong>{formatNumber(usage.totals.last_7_days)}</strong>
        <small>{formatNumber(usage.totals.last_30_days)} in the last 30</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>All-time commands</span>        <strong>{formatNumber(usage.totals.lifetime)}</strong>
        <small>Recorded since analytics was enabled</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>Gateway latency</span><strong>{bot.latency_ms === null ? "—" : `${bot.latency_ms} ms`}</strong>
        <small>{bot.shard_count ? `${bot.shard_count} shard${bot.shard_count === 1 ? "" : "s"}` : "Single connection"}</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>Uptime</span><strong>{uptimeLabel(bot.uptime_seconds)}</strong>
        <small>Since this process started</small>
      </article>
      <article className="bot-analytics-kpi">
        <span>Economy profiles</span><strong>{economy ? formatNumber(economy.profiles) : "—"}</strong>
        <small>{economy ? `${formatNumber(economy.circulating)} coins in wallets` : "Economy data unavailable"}</small>
      </article>
    </div>

    <div className="bot-analytics-grid">
      <section className="bot-analytics-card is-wide">
        <div className="bot-analytics-card-heading">
          <div><span className="panel-kicker">Command traffic</span><h3>Daily command usage</h3></div>
          <Icon name="chart" />
        </div>
        <UsageChart days={days} windowDays={range} onWindowChange={setRange} />
      </section>

      <section className="bot-analytics-card">
        <div className="bot-analytics-card-heading">
          <div><span className="panel-kicker">How commands arrive</span><h3>Invocation mix</h3></div>
        </div>
        <CommandMix byKind={usage.by_kind} />
      </section>

      <section className="bot-analytics-card">
        <div className="bot-analytics-card-heading">
          <div><span className="panel-kicker">All-time</span><h3>Top commands</h3></div>
          <span className="bot-analytics-card-tag">{usage.top_commands.length}</span>
        </div>
        {usage.top_commands.length === 0
          ? <p className="bot-analytics-empty">No commands have been recorded yet. Usage counts begin with the next command.</p>
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
          <div><span className="panel-kicker">Localisation reach</span><h3>Languages across guilds</h3></div>
          <span className="bot-analytics-card-tag is-accent">{shareLabel(supportedShare)} live</span>
        </div>
        {topLanguages.length === 0
          ? <p className="bot-analytics-empty">No guild languages available yet.</p>
          : <div className="bot-analytics-languages">
            {topLanguages.map((row) => <div className="bot-analytics-language" key={row.code}>
              <div className="bot-analytics-language-head">
                <strong>{row.label}</strong>
                <code>{row.code.toUpperCase()}</code>
                <span className={`bot-analytics-pill${row.supported ? " is-supported" : ""}`}>{row.supported ? "Live" : "Rollout next"}</span>
              </div>
              <div className="bot-analytics-bar"><i style={{ width: `${(row.guilds / maxGuilds) * 100}%` }} /></div>
              <small>{formatNumber(row.guilds)} guilds · {formatNumber(row.members)} members</small>
            </div>)}
          </div>}
        {usage.by_language.length > 0 && <p className="bot-analytics-note">
          Command runs by language: {usage.by_language.slice(0, 3).map((row) => `${row.code.toUpperCase()} ${shareLabel(row.share)}`).join(" · ")}
        </p>}
      </section>

      <section className="bot-analytics-card">
        <div className="bot-analytics-card-heading">
          <div><span className="panel-kicker">Economy</span><h3>Usage &amp; wealth</h3></div>
          <Icon name="guild_economy" />
        </div>
        {!economy
          ? <p className="bot-analytics-empty">Economy data is unavailable while the database is reconnecting.</p>
          : <>
            <div className="bot-analytics-stats">
              <div><span>In wallets</span><strong>{formatNumber(economy.circulating)}</strong></div>
              <div><span>In banks</span><strong>{formatNumber(economy.banked)}</strong></div>
              <div><span>Median worth</span><strong>{formatNumber(economy.median)}</strong></div>
              <div><span>Average worth</span><strong>{formatNumber(economy.average)}</strong></div>
              <div><span>Average level</span><strong>{economy.average_level}</strong></div>
              <div><span>Daily streaks</span><strong>{formatNumber(economy.active_streaks)}</strong></div>
            </div>
            <span className="bot-analytics-subheading">Most common jobs</span>
            {economy.top_jobs.length === 0
              ? <p className="bot-analytics-empty">No jobs have been chosen yet.</p>
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
