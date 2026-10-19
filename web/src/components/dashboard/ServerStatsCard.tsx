import { useCallback, useMemo, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from "react";
import { Activity, BarChart3, Hash, Users } from "lucide-react";
import Tabs, { type TabItem } from "../ui/tabs";
import type { ServerStats } from "../../types";
import { formatNumber } from "../../utils/format";

type Props = { stats: ServerStats };
const tabItems: TabItem[] = [
  { value: "messages", label: "Messages" },
  { value: "members", label: "Members" },
  { value: "layout", label: "Server layout" },
];

function dayLabel(date: string) {
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric" }).format(new Date(`${date}T12:00:00`));
}

function reportingWindow(activity: ServerStats["activity"]) {
  if (!activity.length) return "No reporting dates yet";
  const start = dayLabel(activity[0].date);
  const end = dayLabel(activity[activity.length - 1].date);
  return start === end ? start : `${start} – ${end}`;
}

/**
 * The one day a chart is inspecting. Touch screens have no hover state, so a
 * tap (or a drag across the plot) selects a day and its readout stays visible;
 * mouse users still get the old hover preview, and the arrow keys walk the
 * range for keyboards.
 */
function useDayScrub(count: number) {
  const [selected, setSelected] = useState<number | null>(null);
  const select = useCallback((index: number) => {
    if (!count) return;
    setSelected(Math.min(count - 1, Math.max(0, Math.round(index))));
  }, [count]);
  const move = useCallback((delta: number) => {
    setSelected((current) => {
      if (!count) return null;
      if (current === null) return delta > 0 ? 0 : count - 1;
      return Math.min(count - 1, Math.max(0, current + delta));
    });
  }, [count]);
  const clear = useCallback(() => setSelected(null), []);
  return { selected, select, move, clear };
}

function capturePointer(event: { currentTarget: Element; pointerId: number }) {
  // A pointer that already ended (or a synthetic test event) has nothing to
  // capture, and capturing is only an optimisation for drag scrubbing.
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

function MessageChart({ stats }: Props) {
  const values = stats.activity.map((day) => day.messages);
  const total = values.reduce((sum, value) => sum + value, 0);
  const busiest = stats.activity.reduce((best, day) => day.messages > best.messages ? day : best, stats.activity[0] || { date: "", messages: 0, joins: 0, leaves: 0 });
  const max = Math.max(1, ...values);
  const plotLeft = 40;
  const plotRight = 322;
  const plotTop = 14;
  const plotBottom = 106;
  const xAt = (index: number) => values.length > 1 ? plotLeft + (index * (plotRight - plotLeft)) / (values.length - 1) : (plotLeft + plotRight) / 2;
  const yAt = (value: number) => plotBottom - (value / max) * (plotBottom - plotTop);
  const points = values.map((value, index) => `${xAt(index)},${yAt(value)}`).join(" ");
  const area = values.length ? `${plotLeft},${plotBottom} ${points} ${plotRight},${plotBottom}` : "";
  const ticks = [0, 0.33, 0.66, 1].map((fraction) => ({
    y: plotBottom - fraction * (plotBottom - plotTop),
    value: Math.round(max * fraction),
  }));
  const chartRef = useRef<SVGSVGElement>(null);
  const { selected, select, move, clear } = useDayScrub(values.length);
  const selectedDay = selected === null ? null : stats.activity[selected] || null;
  // Map the pointer through the SVG's own coordinate system, so a tap lands on
  // the same day whether the plot is letterboxed on a wide panel or squeezed
  // onto a phone.
  const pick = (clientX: number) => {
    const svg = chartRef.current;
    const matrix = svg?.getScreenCTM();
    if (!svg || !matrix || !values.length) return;
    const point = svg.createSVGPoint();
    point.x = clientX;
    point.y = 0;
    const localX = point.matrixTransform(matrix.inverse()).x;
    const step = values.length > 1 ? (plotRight - plotLeft) / (values.length - 1) : 0;
    select(step ? Math.round((localX - plotLeft) / step) : 0);
  };

  return <div className="server-chart-wrap">
    <div className="server-chart-heading"><div><span>Messages across the period</span><strong>{formatNumber(total)}</strong></div><small>{reportingWindow(stats.activity)}</small></div>
    <div className="server-chart-insights"><span>Daily average <strong>{formatNumber(stats.activity.length ? Math.round(total / stats.activity.length) : 0)}</strong></span><span>Busiest day <strong>{busiest.date ? `${formatNumber(busiest.messages)} · ${dayLabel(busiest.date)}` : "No data"}</strong></span></div>
    {total > 0 ? <>
      <div className={`server-chart-readout${selectedDay ? " is-active" : ""}`} aria-live="polite" aria-atomic="true">
        {selectedDay
          ? <><strong>{dayLabel(selectedDay.date)}</strong><span>{formatNumber(selectedDay.messages)} messages</span></>
          : <span>Tap or hover a day for exact counts</span>}
      </div>
      <div
        className="server-chart-interactive"
        role="group"
        tabIndex={0}
        aria-label="Daily message counts. Tap, hover, or use the arrow keys to inspect a day."
        onKeyDown={(event) => handleDayKeyDown(event, move)}
      >
        <svg
          ref={chartRef}
          className="server-line-chart is-interactive"
          viewBox="0 0 336 122"
          aria-hidden="true"
          onPointerDown={(event) => { capturePointer(event); pick(event.clientX); }}
          onPointerMove={(event) => { if (event.pointerType === "mouse" || event.buttons) pick(event.clientX); }}
          onPointerLeave={(event) => { if (event.pointerType === "mouse" && !event.buttons) clear(); }}
        >
          <defs><linearGradient id="message-area-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="var(--accent)" stopOpacity=".24" /><stop offset="100%" stopColor="var(--accent)" stopOpacity="0" /></linearGradient></defs>
          {ticks.map((tick, index) => <g key={index}><line x1={plotLeft} x2={plotRight} y1={tick.y} y2={tick.y} className="server-chart-gridline" /><text x="34" y={tick.y + 3} textAnchor="end" className="server-chart-axis-label">{formatNumber(tick.value)}</text></g>)}
          {selected !== null && stats.activity[selected] && <line x1={xAt(selected)} x2={xAt(selected)} y1={plotTop} y2={plotBottom} className="server-chart-guide" />}
          <polygon points={area} fill="url(#message-area-fill)" />
          <polyline points={points} className="server-chart-line" />
          {stats.activity.map((day, index) => <circle key={day.date} cx={xAt(index)} cy={yAt(day.messages)} r={index === selected ? 4.5 : 3} className={`server-chart-point${index === selected ? " is-selected" : ""}`} />)}
        </svg>
      </div>
      <div className="server-chart-days">{stats.activity.filter((_, index) => index % 2 === 0 || index === stats.activity.length - 1).map((day) => <span key={day.date}>{dayLabel(day.date)}</span>)}</div>
    </> : <div className="server-chart-empty">No messages were recorded in this period. Activity history starts when tracking is enabled.</div>}
  </div>;
}

function MemberChart({ stats }: Props) {
  const joined = stats.activity.reduce((sum, day) => sum + day.joins, 0);
  const left = stats.activity.reduce((sum, day) => sum + day.leaves, 0);
  const net = joined - left;
  const max = Math.max(1, ...stats.activity.flatMap((day) => [day.joins, day.leaves]));
  const chartRef = useRef<HTMLDivElement>(null);
  const { selected, select, move, clear } = useDayScrub(stats.activity.length);
  const selectedDay = selected === null ? null : stats.activity[selected] || null;
  // One column per day, so the pointer's horizontal position picks the day and
  // a drag scrubs the range the same way the line chart does.
  const pick = (clientX: number) => {
    const box = chartRef.current?.getBoundingClientRect();
    if (!box || !box.width || !stats.activity.length) return;
    select(((clientX - box.left) / box.width) * stats.activity.length - 0.5);
  };

  return <div className="server-chart-wrap">
    <div className="server-chart-heading"><div><span>Member movement</span><strong>{net > 0 ? "+" : ""}{formatNumber(net)} net members</strong></div><small>{reportingWindow(stats.activity)}</small></div>
    <p className="server-chart-description">Each date compares joins with departures; bar height shares one scale across all days.</p>
    {(joined || left) ? <>
      <div className={`server-chart-readout${selectedDay ? " is-active" : ""}`} aria-live="polite" aria-atomic="true">
        {selectedDay
          ? <><strong>{dayLabel(selectedDay.date)}</strong><span>{formatNumber(selectedDay.joins)} joined</span><span>{formatNumber(selectedDay.leaves)} left</span></>
          : <span>Tap or hover a day for exact counts</span>}
      </div>
      <div
        ref={chartRef}
        className="server-member-chart"
        role="group"
        tabIndex={0}
        aria-label="Daily member joins and departures. Tap, hover, or use the arrow keys to inspect a day."
        onKeyDown={(event) => handleDayKeyDown(event, move)}
        onPointerDown={(event) => { capturePointer(event); pick(event.clientX); }}
        onPointerMove={(event) => { if (event.pointerType === "mouse" || event.buttons) pick(event.clientX); }}
        onPointerLeave={(event) => { if (event.pointerType === "mouse" && !event.buttons) clear(); }}
      >
        {stats.activity.map((day, index) => <button
          type="button"
          tabIndex={-1}
          className={`server-member-day${index === selected ? " is-selected" : ""}`}
          key={day.date}
          onClick={() => select(index)}
          aria-label={`${dayLabel(day.date)}: ${formatNumber(day.joins)} joined, ${formatNumber(day.leaves)} left`}
        >
          <div className="server-member-bars" aria-hidden="true"><i className="join-bar" style={{ height: `${Math.max(day.joins ? 5 : 0, (day.joins / max) * 76)}%` }} /><i className="leave-bar" style={{ height: `${Math.max(day.leaves ? 5 : 0, (day.leaves / max) * 76)}%` }} /></div>
          <span aria-hidden="true">{index % 3 === 0 || index === stats.activity.length - 1 || index === selected ? dayLabel(day.date) : ""}</span>
        </button>)}
      </div>
      <div className="server-chart-legend"><span><i className="join-key" /> Joined <b>{formatNumber(joined)}</b></span><span><i className="leave-key" /> Left <b>{formatNumber(left)}</b></span></div>
    </> : <div className="server-chart-empty">No member changes were recorded in this period. Current membership is shown in Server layout.</div>}
  </div>;
}

function serverAge(createdAt: string | null) {
  if (!createdAt) return "Creation date unavailable";
  const days = Math.max(0, Math.floor((Date.now() - new Date(createdAt).getTime()) / 86_400_000));
  if (days >= 730) return `About ${Math.floor(days / 365)} years old`;
  if (days >= 60) return `About ${Math.floor(days / 30)} months old`;
  return `${days} days old`;
}

function LayoutChart({ stats }: Props) {
  const max = Math.max(stats.member_count, stats.channel_count, stats.role_count, 1);
  const items = [
    { label: "Members", value: stats.member_count, color: "members" },
    { label: "Channels", value: stats.channel_count, color: "channels" },
    { label: "Roles", value: stats.role_count, color: "roles" },
  ];
  return <div className="server-layout-chart">
    <div className="server-layout-total"><span>Community size</span><strong>{formatNumber(stats.member_count)}</strong><small>members currently in this server</small><small>{serverAge(stats.created_at)}</small></div>
    <div className="server-layout-bars"><p className="server-chart-description">Bar lengths share a scale; the longest is the largest count.</p>{items.map((item) => <div className="server-layout-row" key={item.label}>
      <div><span>{item.label}</span><strong>{formatNumber(item.value)}</strong></div>
      <div className="server-layout-track"><i className={`layout-${item.color}`} style={{ width: `${Math.max(item.value ? 4 : 0, (item.value / max) * 100)}%` }} /></div>
    </div>)}</div>
  </div>;
}

export function ServerStatsCard({ stats }: Props) {
  const [tab, setTab] = useState("messages");
  const totals = useMemo(() => ({
    messages: stats.activity.reduce((sum, day) => sum + day.messages, 0),
    joins: stats.activity.reduce((sum, day) => sum + day.joins, 0),
    leaves: stats.activity.reduce((sum, day) => sum + day.leaves, 0),
  }), [stats.activity]);
  const panel = tab === "members" ? <MemberChart stats={stats} /> : tab === "layout" ? <LayoutChart stats={stats} /> : <MessageChart stats={stats} />;

  return <section className="dash-panel server-stats-card" aria-label="Server statistics">
    <div className="panel-heading server-stats-heading"><div><span className="panel-kicker">Community analytics</span><h3>Server pulse</h3><p>Daily totals for {reportingWindow(stats.activity)}. These trends begin when Niko’s activity tracking is enabled.</p></div><span className="panel-icon"><Activity /></span></div>
    <div className="server-stat-metrics">
      <div><Users /><span>Members now</span><strong>{formatNumber(stats.member_count)}</strong><small>Current server size</small></div>
      <div><BarChart3 /><span>Messages</span><strong>{formatNumber(totals.messages)}</strong><small>Across this period</small></div>
      <div><Hash /><span>Joined</span><strong>{formatNumber(totals.joins)}</strong><small>Across this period</small></div>
      <div><Users /><span>Net members</span><strong>{totals.joins - totals.leaves > 0 ? "+" : ""}{formatNumber(totals.joins - totals.leaves)}</strong><small>Joined minus left</small></div>
    </div>
    <Tabs items={tabItems} value={tab} onValueChange={setTab} label="Server statistics" renderPanel={() => panel} />
    <div className="server-stats-footnote">Counts are daily aggregates; no message content or member identities are shown. Days before tracking began may have no recorded activity.</div>
  </section>;
}
