import { useCallback, useMemo, useRef, useState, type KeyboardEvent as ReactKeyboardEvent, type ReactNode } from "react";
import { useReducedMotion } from "motion/react";
import { Activity, BarChart3, Hash, Users } from "lucide-react";
import Tabs, { type TabItem } from "../ui/tabs";
import type { ServerStats } from "../../types";
import { formatNumber } from "../../utils/format";
import { useFreshSignal } from "../../hooks/useLiveSync";
import { useCountUp } from "../../hooks/useCountUp";
import { type Translate, useStrings } from "../../i18n";

type Props = { stats: ServerStats };

function dayLabel(date: string) {
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric" }).format(new Date(`${date}T12:00:00`));
}

function reportingWindow(activity: ServerStats["activity"], t: Translate) {
  if (!activity.length) return t("stats.noDates");
  const start = dayLabel(activity[0].date);
  const end = dayLabel(activity[activity.length - 1].date);
  return start === end ? start : `${start} – ${end}`;
}

/** The comparison window: the last week against the week before it. */
const TREND_DAYS = 7;

type Trend = { direction: "up" | "down" | "flat"; text: string };

/**
 * Speak the change as a sentence rather than a raw number, so a tile still
 * reads correctly when the previous week was empty (there is no percentage
 * change from zero) or when the totals did not move at all.
 */
function trendOf(current: number, previous: number, t: Translate): Trend {
  if (!previous) {
    return current
      ? { direction: "up", text: t("stats.trendNew") }
      : { direction: "flat", text: t("stats.trendIdle") };
  }
  const change = Math.round(((current - previous) / previous) * 100);
  if (!change) return { direction: "flat", text: t("stats.trendLevel") };
  return { direction: change > 0 ? "up" : "down", text: t(change > 0 ? "stats.trendUp" : "stats.trendDown", { percent: Math.abs(change) }) };
}

/** Week-over-week movement for the three tiles fed by daily activity. */
function weeklyTrend(activity: ServerStats["activity"], t: Translate) {
  const count = (rows: typeof activity, key: "messages" | "joins" | "leaves") =>
    rows.reduce((sum, row) => sum + row[key], 0);
  const current = activity.slice(-TREND_DAYS);
  const previous = activity.slice(-TREND_DAYS * 2, -TREND_DAYS);
  return {
    messages: trendOf(count(current, "messages"), count(previous, "messages"), t),
    joins: trendOf(count(current, "joins"), count(previous, "joins"), t),
    net: trendOf(
      count(current, "joins") - count(current, "leaves"),
      count(previous, "joins") - count(previous, "leaves"),
      t,
    ),
  };
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
  const { t } = useStrings("dashboard");
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
    <div className="server-chart-heading"><div><span>{t("stats.messagesAcrossPeriod")}</span><strong>{formatNumber(total)}</strong></div><small>{reportingWindow(stats.activity, t)}</small></div>
    <div className="server-chart-insights"><span>{t("stats.dailyAverage")} <strong>{formatNumber(stats.activity.length ? Math.round(total / stats.activity.length) : 0)}</strong></span><span>{t("stats.busiestDay")} <strong>{busiest.date ? `${formatNumber(busiest.messages)} · ${dayLabel(busiest.date)}` : t("stats.noData")}</strong></span></div>
    {total > 0 ? <>
      <div className={`server-chart-readout${selectedDay ? " is-active" : ""}`} aria-live="polite" aria-atomic="true">
        {selectedDay
          ? <><strong>{dayLabel(selectedDay.date)}</strong><span>{t("stats.messageCount", { count: formatNumber(selectedDay.messages) })}</span></>
          : <span>{t("stats.tapForCounts")}</span>}
      </div>
      <div
        className="server-chart-interactive"
        role="group"
        tabIndex={0}
        aria-label={t("stats.messageChartAria")}
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
    </> : <div className="server-chart-empty">{t("stats.noMessages")}</div>}
  </div>;
}

function MemberChart({ stats }: Props) {
  const { t } = useStrings("dashboard");
  const joined = stats.activity.reduce((sum, day) => sum + day.joins, 0);
  const left = stats.activity.reduce((sum, day) => sum + day.leaves, 0);
  const net = joined - left;
  const busiestJoin = stats.activity.reduce((best, day) => day.joins > best.joins ? day : best, stats.activity[0] || { date: "", messages: 0, joins: 0, leaves: 0 });
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
    <div className="server-chart-heading"><div><span>{t("stats.memberMovement")}</span><strong>{net > 0 ? "+" : ""}{formatNumber(net)} {t("stats.netMembers")}</strong></div><small>{reportingWindow(stats.activity, t)}</small></div>
    <p className="server-chart-description">{t("stats.memberChartDescription")}</p>
    {(joined || left) ? <>
      <div className="server-chart-insights"><span>{t("stats.dailyAverage")} <strong>{net > 0 ? "+" : ""}{formatNumber(Math.round(net / stats.activity.length))}</strong></span><span>{t("stats.mostJoins")} <strong>{formatNumber(busiestJoin.joins)} · {dayLabel(busiestJoin.date)}</strong></span></div>
      <div className={`server-chart-readout${selectedDay ? " is-active" : ""}`} aria-live="polite" aria-atomic="true">
        {selectedDay
          ? <><strong>{dayLabel(selectedDay.date)}</strong><span>{t("stats.joinedCount", { count: formatNumber(selectedDay.joins) })}</span><span>{t("stats.leftCount", { count: formatNumber(selectedDay.leaves) })}</span></>
          : <span>{t("stats.tapForCounts")}</span>}
      </div>
      <div
        ref={chartRef}
        className="server-member-chart"
        style={{ gridTemplateColumns: `repeat(${Math.max(1, stats.activity.length)}, minmax(0, 1fr))` }}
        role="group"
        tabIndex={0}
        aria-label={t("stats.memberChartAria")}
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
          aria-label={t("stats.dayAria", { date: dayLabel(day.date), joined: formatNumber(day.joins), left: formatNumber(day.leaves) })}
        >
          <div className="server-member-bars" aria-hidden="true"><i className="join-bar" style={{ height: `${Math.max(day.joins ? 5 : 0, (day.joins / max) * 76)}%` }} /><i className="leave-bar" style={{ height: `${Math.max(day.leaves ? 5 : 0, (day.leaves / max) * 76)}%` }} /></div>
          <span aria-hidden="true">{index % 3 === 0 || index === stats.activity.length - 1 || index === selected ? dayLabel(day.date) : ""}</span>
        </button>)}
      </div>
      <div className="server-chart-legend"><span><i className="join-key" /> {t("stats.joined")} <b>{formatNumber(joined)}</b></span><span><i className="leave-key" /> {t("stats.left")} <b>{formatNumber(left)}</b></span></div>
    </> : <div className="server-chart-empty">{t("stats.noMembers")}</div>}
  </div>;
}

function serverAge(createdAt: string | null, t: Translate) {
  if (!createdAt) return t("stats.ageUnknown");
  const days = Math.max(0, Math.floor((Date.now() - new Date(createdAt).getTime()) / 86_400_000));
  if (days >= 730) return t("stats.ageYears", { count: Math.floor(days / 365) });
  if (days >= 60) return t("stats.ageMonths", { count: Math.floor(days / 30) });
  return t("stats.ageDays", { count: days });
}

function LayoutChart({ stats }: Props) {
  const { t } = useStrings("dashboard");
  const max = Math.max(stats.member_count, stats.channel_count, stats.role_count, 1);
  const items = [
    { label: t("stats.members"), value: stats.member_count, color: "members" },
    { label: t("stats.channels"), value: stats.channel_count, color: "channels" },
    { label: t("stats.roles"), value: stats.role_count, color: "roles" },
  ];
  return <div className="server-layout-chart">
    <div className="server-layout-total"><span>{t("stats.communitySize")}</span><strong>{formatNumber(stats.member_count)}</strong><small>{t("stats.membersCurrently")}</small><small>{serverAge(stats.created_at, t)}</small></div>
    <div className="server-layout-bars"><p className="server-chart-description">{t("stats.barScaleNote")}</p>{items.map((item) => <div className="server-layout-row" key={item.label}>
      <div><span>{item.label}</span><strong>{formatNumber(item.value)}</strong></div>
      <div className="server-layout-track"><i className={`layout-${item.color}`} style={{ width: `${Math.max(item.value ? 4 : 0, (item.value / max) * 100)}%` }} /></div>
    </div>)}</div>
  </div>;
}

/**
 * One metric tile. A live refresh counts the number up to its new value and
 * breathes the tile once, so movement is felt rather than just repainted.
 */
function LiveMetric({ icon, label, value, note, signed = false, trend }: { icon: ReactNode; label: string; value: number; note: string; signed?: boolean; trend?: Trend }) {
  const reduceMotion = useReducedMotion();
  const display = useCountUp(value, !reduceMotion);
  const fresh = useFreshSignal(String(value), 1_400) && !reduceMotion;
  return <div className={fresh ? "is-fresh" : undefined}>
    {icon}<span>{label}</span>
    <strong>{signed && display > 0 ? "+" : ""}{formatNumber(display)}</strong>
    <small>{note}</small>
    {trend && <em className={`server-metric-trend is-${trend.direction}`}>
      <i aria-hidden="true">{trend.direction === "up" ? "▲" : trend.direction === "down" ? "▼" : "—"}</i>{trend.text}
    </em>}
  </div>;
}

export function ServerStatsCard({ stats }: Props) {
  const { t } = useStrings("dashboard");
  const tabItems = useMemo<TabItem[]>(() => [
    { value: "messages", label: t("stats.tabMessages") },
    { value: "members", label: t("stats.tabMembers") },
    { value: "layout", label: t("stats.tabLayout") },
  ], [t]);
  const [tab, setTab] = useState("messages");
  const reduceMotion = useReducedMotion();
  const totals = useMemo(() => ({
    messages: stats.activity.reduce((sum, day) => sum + day.messages, 0),
    joins: stats.activity.reduce((sum, day) => sum + day.joins, 0),
    leaves: stats.activity.reduce((sum, day) => sum + day.leaves, 0),
  }), [stats.activity]);
  const net = totals.joins - totals.leaves;
  const trend = useMemo(() => weeklyTrend(stats.activity, t), [stats.activity, t]);
  // Only a refresh that actually moved the numbers brightens the chart.
  const chartFresh = useFreshSignal(
    `${totals.messages}|${totals.joins}|${totals.leaves}|${stats.member_count}|${stats.channel_count}|${stats.role_count}`,
    1_200,
  ) && !reduceMotion;
  const panel = tab === "members" ? <MemberChart stats={stats} /> : tab === "layout" ? <LayoutChart stats={stats} /> : <MessageChart stats={stats} />;

  return <section className="dash-panel server-stats-card" aria-label={t("stats.cardAria")}>
    <div className="panel-heading server-stats-heading"><div><span className="panel-kicker">{t("stats.kicker")}</span><h3>{t("stats.title")}</h3><p>{t("stats.subtitle", { window: reportingWindow(stats.activity, t) })}</p></div><span className="panel-icon"><Activity /></span></div>
    <div className="server-stat-metrics">
      <LiveMetric icon={<Users />} label={t("stats.membersNow")} value={stats.member_count} note={t("stats.membersNowNote")} />
      <LiveMetric icon={<BarChart3 />} label={t("stats.messages")} value={totals.messages} note={t("stats.acrossPeriod")} trend={trend.messages} />
      <LiveMetric icon={<Hash />} label={t("stats.joined")} value={totals.joins} note={t("stats.acrossPeriod")} trend={trend.joins} />
      <LiveMetric icon={<Users />} label={t("stats.netMembersLabel")} value={net} note={t("stats.joinedMinusLeft")} signed trend={trend.net} />
    </div>
    <div className={chartFresh ? "server-live-panel is-fresh" : "server-live-panel"}>
      <Tabs items={tabItems} value={tab} onValueChange={setTab} label={t("stats.cardAria")} renderPanel={() => panel} />
    </div>
    <div className="server-stats-footnote">{t("stats.footnote")}</div>
  </section>;
}
