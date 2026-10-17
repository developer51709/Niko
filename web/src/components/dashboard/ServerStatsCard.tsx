import { useMemo, useState } from "react";
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

  return <div className="server-chart-wrap">
    <div className="server-chart-heading"><div><span>Messages across the period</span><strong>{formatNumber(total)}</strong></div><small>{reportingWindow(stats.activity)}</small></div>
    <div className="server-chart-insights"><span>Daily average <strong>{formatNumber(stats.activity.length ? Math.round(total / stats.activity.length) : 0)}</strong></span><span>Busiest day <strong>{busiest.date ? `${formatNumber(busiest.messages)} · ${dayLabel(busiest.date)}` : "No data"}</strong></span></div>
    {total > 0 ? <>
      <svg className="server-line-chart" viewBox="0 0 336 122" role="img" aria-label={`Daily messages from ${stats.activity[0]?.date || ""} to ${stats.activity[stats.activity.length - 1]?.date || ""}`}>
        <defs><linearGradient id="message-area-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="var(--accent)" stopOpacity=".24" /><stop offset="100%" stopColor="var(--accent)" stopOpacity="0" /></linearGradient></defs>
        {ticks.map((tick, index) => <g key={index}><line x1={plotLeft} x2={plotRight} y1={tick.y} y2={tick.y} className="server-chart-gridline" /><text x="34" y={tick.y + 3} textAnchor="end" className="server-chart-axis-label">{formatNumber(tick.value)}</text></g>)}
        <polygon points={area} fill="url(#message-area-fill)" />
        <polyline points={points} className="server-chart-line" />
        {stats.activity.map((day, index) => <circle key={day.date} cx={xAt(index)} cy={yAt(day.messages)} r="3" className="server-chart-point"><title>{`${day.date}: ${formatNumber(day.messages)} messages`}</title></circle>)}
      </svg>
      <div className="server-chart-days">{stats.activity.filter((_, index) => index % 2 === 0 || index === stats.activity.length - 1).map((day) => <span key={day.date}>{dayLabel(day.date)}</span>)}</div>
    </> : <div className="server-chart-empty">No messages were recorded in this period. Activity history starts when tracking is enabled.</div>}
  </div>;
}

function MemberChart({ stats }: Props) {
  const joined = stats.activity.reduce((sum, day) => sum + day.joins, 0);
  const left = stats.activity.reduce((sum, day) => sum + day.leaves, 0);
  const net = joined - left;
  const max = Math.max(1, ...stats.activity.flatMap((day) => [day.joins, day.leaves]));
  return <div className="server-chart-wrap">
    <div className="server-chart-heading"><div><span>Member movement</span><strong>{net > 0 ? "+" : ""}{formatNumber(net)} net members</strong></div><small>{reportingWindow(stats.activity)}</small></div>
    <p className="server-chart-description">Each date compares joins with departures; bar height shares one scale across all days.</p>
    {(joined || left) ? <>
      <div className="server-member-chart" role="img" aria-label={`Daily member joins and departures from ${stats.activity[0]?.date || ""} to ${stats.activity[stats.activity.length - 1]?.date || ""}`}>
        {stats.activity.map((day, index) => <div className="server-member-day" key={day.date} title={`${day.date}: ${formatNumber(day.joins)} joined, ${formatNumber(day.leaves)} left`}>
          <div className="server-member-bars"><i className="join-bar" style={{ height: `${Math.max(day.joins ? 5 : 0, (day.joins / max) * 76)}%` }} /><i className="leave-bar" style={{ height: `${Math.max(day.leaves ? 5 : 0, (day.leaves / max) * 76)}%` }} /></div>
          <span>{index % 3 === 0 || index === stats.activity.length - 1 ? dayLabel(day.date) : ""}</span>
        </div>)}
      </div>
      <div className="server-chart-legend"><span><i className="join-key" /> Joined <b>{formatNumber(joined)}</b></span><span><i className="leave-key" /> Left <b>{formatNumber(left)}</b></span><small>Hover a day for exact counts</small></div>
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
