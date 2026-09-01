import { Icon } from "../Icon";
import { formatNumber } from "../../utils/format";
import type { BotStats, EconomyRow, GuildConfig, GuildResources, GuildOverview, LevelRow } from "../../types";
import { LevelingSettings } from "./SettingsViews";

export function DashHeading({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) {
  return <div className="dash-heading"><div className="eyebrow">{eyebrow}</div><h2>{title}</h2><p>{text}</p></div>;
}

export function StatCard({ label, value, note, accent = "" }: { label: string; value: string; note: string; accent?: string }) {
  return <div className={`dash-stat ${accent}`}><span>{label}</span><strong>{value}</strong><small>{note}</small></div>;
}

export function RankList({ rows, type }: { rows: (EconomyRow | LevelRow)[]; type: "coins" | "xp" }) {
  return <div className="rank-list">
    {rows.slice(0, 5).map((row, index) => <div className="rank-row" key={`${row.user_id}-${index}`}>
      <span className={`rank rank-${index + 1}`}>{String(index + 1).padStart(2, "0")}</span>
      <span className="rank-user">Member {row.user_id.slice(-4)}</span>
      <strong>{formatNumber(type === "coins" ? (row as EconomyRow).net_worth : (row as LevelRow).xp)}<small>{type === "coins" ? " coins" : " xp"}</small></strong>
    </div>)}
    {!rows.length && <div className="empty-state compact">No data recorded yet.</div>}
  </div>;
}

export function OverviewView({ overview, stats }: { overview: GuildOverview; stats: BotStats | null }) {
  return <>
    <DashHeading eyebrow="Overview" title="A quick read on your room." text="The important signals, without making you hunt for them." />
    <div className="dash-stats">
      <StatCard label="Members across Niko" value={formatNumber(stats?.user_count)} note="Across all connected servers" accent="accent-violet" />
      <StatCard label="Economy in circulation" value={formatNumber(overview.economy.total_coins)} note={`${formatNumber(overview.economy.user_count)} active profiles`} accent="accent-orange" />
      <StatCard label="Warnings logged" value={formatNumber(overview.moderation.warn_count)} note="For this server" accent="accent-blue" />
      <StatCard label="Automod" value={overview.moderation.automod_active ? "Active" : "Quiet"} note="Protection status" accent="accent-green" />
    </div>
    <div className="dash-columns">
      <section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Community economy</span><h3>Top net worth</h3></div><span className="panel-icon"><Icon name="chart" /></span></div><RankList rows={overview.economy.top} type="coins" /></section>
      <section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Community energy</span><h3>Top XP</h3></div><span className="panel-icon"><Icon name="spark" /></span></div><RankList rows={overview.leveling.top} type="xp" /></section>
    </div>
  </>;
}

export function EconomyView({ rows }: { rows: EconomyRow[] }) {
  const total = rows.reduce((sum, row) => sum + row.net_worth, 0);
  return <>
    <DashHeading eyebrow="Economy" title="Give members something to build." text="A snapshot of the café economy and its most active players." />
    <div className="dash-stats"><StatCard label="Tracked net worth" value={formatNumber(total)} note="Top 25 profiles" accent="accent-orange" /><StatCard label="Profiles" value={formatNumber(rows.length)} note="With economy data" accent="accent-violet" /></div>
    <section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Leaderboard</span><h3>Net worth</h3></div><span className="panel-icon"><Icon name="chart" /></span></div>
      <div className="wide-table" role="table" aria-label="Economy leaderboard"><div className="table-head" role="row"><span>Rank</span><span>Member</span><span>Job</span><span>Level</span><span>Net worth</span></div>{rows.map((row, index) => <div className="table-row" role="row" key={row.user_id}><span className="rank">{String(index + 1).padStart(2, "0")}</span><span>Member {row.user_id.slice(-4)}</span><span className="muted">{row.job}</span><span>{row.level}</span><strong>{formatNumber(row.net_worth)}</strong></div>)}</div>
    </section>
  </>;
}

export function LevelingView({ rows, config, resources, csrfToken, guildId }: { rows: LevelRow[]; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string; guildId: string }) {
  return <>
    <DashHeading eyebrow="Leveling" title="Momentum people can see." text="Track the members turning up, and tune the pace to fit your server." />
    <div className="dash-stats"><StatCard label="Top level" value={String(rows[0]?.level || 0)} note={`Member ${rows[0]?.user_id.slice(-4) || "—"}`} accent="accent-violet" /><StatCard label="XP multiplier" value={`${config?.leveling.xp_multiplier || 1}×`} note={config?.leveling.xp_enabled === false ? "XP disabled" : "Currently active"} accent="accent-blue" /><StatCard label="Cooldown" value={`${config?.leveling.xp_cooldown || 0}s`} note="Between XP awards" accent="accent-green" /></div>
    <section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Leaderboard</span><h3>XP leaders</h3></div><span className="panel-icon"><Icon name="spark" /></span></div><RankList rows={rows} type="xp" /></section>
    <LevelingSettings guildId={guildId} config={config} resources={resources} csrfToken={csrfToken} />
  </>;
}