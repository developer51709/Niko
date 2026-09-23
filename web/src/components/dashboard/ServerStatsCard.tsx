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

function shortDay(date: string) {
  return new Intl.DateTimeFormat(undefined, { weekday: "short" }).format(new Date(`${date}T12:00:00`));
}

function MessageChart({ stats }: Props) {
  const values = stats.activity.map((day) => day.messages);
  const max = Math.max(1, ...values);
  const points = values.map((value, index) => {
    const x = values.length > 1 ? 12 + (index * 276) / (values.length - 1) : 150;
    const y = 102 - (value / max) * 78;
    return `${x},${y}`;
  }).join(" ");
  const area = `12,104 ${points} 288,104`;

  return <div className="server-chart-wrap">
    <div className="server-chart-heading"><div><span>Daily messages</span><strong>{formatNumber(values.reduce((sum, value) => sum + value, 0))}</strong></div><small>Last 14 days</small></div>
    <svg className="server-line-chart" viewBox="0 0 300 122" role="img" aria-label="Daily messages over the last fourteen days">
      <defs><linearGradient id="message-area-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="var(--accent)" stopOpacity=".24" /><stop offset="100%" stopColor="var(--accent)" stopOpacity="0" /></linearGradient></defs>
      {[24, 50, 76, 104].map((y) => <line key={y} x1="12" x2="288" y1={y} y2={y} className="server-chart-gridline" />)}
      <polygon points={area} fill="url(#message-area-fill)" />
      <polyline points={points} className="server-chart-line" />
      {stats.activity.map((day, index) => {
        const x = values.length > 1 ? 12 + (index * 276) / (values.length - 1) : 150;
        const y = 102 - (day.messages / max) * 78;
        return <circle key={day.date} cx={x} cy={y} r="2.7" className="server-chart-point"><title>{`${day.date}: ${formatNumber(day.messages)} messages`}</title></circle>;
      })}
    </svg>
    <div className="server-chart-days">{stats.activity.filter((_, index) => index % 2 === 0).map((day) => <span key={day.date}>{shortDay(day.date)}</span>)}</div>
  </div>;
}

function MemberChart({ stats }: Props) {
  const max = Math.max(1, ...stats.activity.flatMap((day) => [day.joins, day.leaves]));
  return <div className="server-chart-wrap">
    <div className="server-chart-heading"><div><span>Member changes</span><strong>{formatNumber(stats.activity.reduce((sum, day) => sum + day.joins, 0))} joined</strong></div><small>Last 14 days</small></div>
    <div className="server-member-chart" role="img" aria-label="Daily member joins and departures over the last fourteen days">
      {stats.activity.map((day) => <div className="server-member-day" key={day.date} title={`${day.date}: ${day.joins} joined, ${day.leaves} left`}>
        <div className="server-member-bars"><i className="join-bar" style={{ height: `${Math.max(day.joins ? 5 : 0, (day.joins / max) * 76)}%` }} /><i className="leave-bar" style={{ height: `${Math.max(day.leaves ? 5 : 0, (day.leaves / max) * 76)}%` }} /></div>
        <span>{shortDay(day.date).slice(0, 1)}</span>
      </div>)}
    </div>
    <div className="server-chart-legend"><span><i className="join-key" /> Joined <b>{formatNumber(stats.activity.reduce((sum, day) => sum + day.joins, 0))}</b></span><span><i className="leave-key" /> Left <b>{formatNumber(stats.activity.reduce((sum, day) => sum + day.leaves, 0))}</b></span></div>
  </div>;
}

function LayoutChart({ stats }: Props) {
  const max = Math.max(stats.member_count, stats.channel_count, stats.role_count, 1);
  const items = [
    { label: "Members", value: stats.member_count, color: "members" },
    { label: "Channels", value: stats.channel_count, color: "channels" },
    { label: "Roles", value: stats.role_count, color: "roles" },
  ];
  return <div className="server-layout-chart">
    <div className="server-layout-total"><span>Community size</span><strong>{formatNumber(stats.member_count)}</strong><small>members currently in this server</small></div>
    <div className="server-layout-bars">{items.map((item) => <div className="server-layout-row" key={item.label}>
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
  }), [stats.activity]);
  const panel = tab === "members" ? <MemberChart stats={stats} /> : tab === "layout" ? <LayoutChart stats={stats} /> : <MessageChart stats={stats} />;

  return <section className="dash-panel server-stats-card" aria-label="Server statistics">
    <div className="panel-heading server-stats-heading"><div><span className="panel-kicker">Community analytics</span><h3>Server pulse</h3><p>Daily activity tracked by Niko · last 14 days</p></div><span className="panel-icon"><Activity /></span></div>
    <div className="server-stat-metrics">
      <div><Users /><span>Members</span><strong>{formatNumber(stats.member_count)}</strong></div>
      <div><BarChart3 /><span>Messages · 14d</span><strong>{formatNumber(totals.messages)}</strong></div>
      <div><Hash /><span>New members · 14d</span><strong>{formatNumber(totals.joins)}</strong></div>
    </div>
    <Tabs items={tabItems} value={tab} onValueChange={setTab} label="Server statistics" renderPanel={() => panel} />
    <div className="server-stats-footnote">Activity is collected from the moment tracking is enabled.</div>
  </section>;
}
