import { Icon } from "../Icon";
import { formatNumber } from "../../utils/format";
import { displayName, initials } from "../../utils/format";
import type { BotStats, EconomyRow, Guild, GuildConfig, GuildResources, GuildOverview, LevelRow, User, UserOverview } from "../../types";
import { LevelingSettings } from "./SettingsViews";

export function DashHeading({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) {
  return <div className="dash-heading"><div className="eyebrow">{eyebrow}</div><h2>{title}</h2><p>{text}</p></div>;
}

export function StatCard({ label, value, note, accent = "" }: { label: string; value: string; note: string; accent?: string }) {
  return <div className={`dash-stat ${accent}`}><span>{label}</span><strong>{value}</strong><small>{note}</small></div>;
}

export function UserOverviewView({ user, overview, guilds, onServers, onManage }: { user: User; overview: UserOverview | null; guilds: Guild[]; onServers: () => void; onManage: (guild: Guild) => void }) {
  const installed = guilds.filter((guild) => guild.installed !== false);
  return <>
    <DashHeading eyebrow="Personal overview" title="Your Niko snapshot." text="Keep an eye on your progress, then jump into a server when you’re ready to tune the room." />
    <div className="overview-intro">
      <div className="profile-card">
        <span className="profile-avatar">{initials(displayName(user))}</span>
        <div><span className="panel-kicker">Signed in as</span><h3>{displayName(user)}</h3><p>Personal economy profile</p></div>
      </div>
      <button className="button button-primary" onClick={onServers}>Manage a server <Icon name="arrow" /></button>
    </div>
    <div className="dash-stats overview-stats">
      <StatCard label="Net worth" value={formatNumber(overview?.net_worth)} note="Across your Niko profile" accent="accent-orange" />
      <StatCard label="In your wallet" value={formatNumber(overview?.balance)} note="Ready to spend" accent="accent-violet" />
      <StatCard label="In your vault" value={formatNumber(overview?.bank)} note="Saved for later" accent="accent-blue" />
      <StatCard label="Current level" value={formatNumber(overview?.level)} note={overview?.job ? `Working as a ${overview.job}` : "Keep showing up"} accent="accent-green" />
    </div>
    <div className="dash-columns overview-columns">
      <section className="dash-panel">
        <div className="panel-heading"><div><span className="panel-kicker">Progress</span><h3>Your momentum</h3></div><span className="panel-icon"><Icon name="spark" /></span></div>
        <div className="metric-list">
          <div><span>Daily streak</span><strong>{formatNumber(overview?.daily_streak)} <small>days</small></strong></div>
          <div><span>Achievements</span><strong>{formatNumber(overview?.achievements)} <small>unlocked</small></strong></div>
          <div><span>Total earned</span><strong>{formatNumber(overview?.total_earned)} <small>coins</small></strong></div>
          <div><span>Economy standing</span><strong>{overview?.economy_rank ? `#${formatNumber(overview.economy_rank)}` : "—"} <small>{overview?.economy_profiles ? `of ${formatNumber(overview.economy_profiles)}` : ""}</small></strong></div>
        </div>
      </section>
      <section className="dash-panel">
        <div className="panel-heading"><div><span className="panel-kicker">Quick access</span><h3>Your servers</h3></div><span className="panel-icon"><Icon name="users" /></span></div>
        <div className="mini-server-list">
          {installed.slice(0, 4).map((guild) => <button key={guild.id} onClick={() => onManage(guild)}><span className="guild-avatar">{guild.name.slice(0, 1).toUpperCase()}</span><span>{guild.name}</span><Icon name="arrow" /></button>)}
          {!installed.length && <p className="empty-state compact">Add Niko to a server to start managing it.</p>}
        </div>
        <button className="text-link overview-link" onClick={onServers}>View all servers <Icon name="arrow" /></button>
      </section>
    </div>
  </>;
}

function ServerCard({ guild, onManage }: { guild: Guild; onManage: (guild: Guild) => void }) {
  const installed = guild.installed !== false;
  return <article className="server-card">
    <div className="server-card-heading"><span className="server-avatar">{guild.name.slice(0, 1).toUpperCase()}</span><span className="server-status">{installed ? "Niko is installed" : "Ready to add"}</span></div>
    <h3>{guild.name}</h3>
    <p>{installed ? "Open the dashboard to manage Niko’s features and settings." : "You have permission to manage this server. Add Niko to unlock its controls."}</p>
    {installed ? <button className="button button-muted button-small" onClick={() => onManage(guild)}>Open settings <Icon name="arrow" /></button> : <a className="button button-primary button-small" href={guild.invite_url || "#"} target="_blank" rel="noreferrer">Add Niko <Icon name="external" /></a>}
  </article>;
}

export function ServersView({ guilds, onManage }: { guilds: Guild[]; onManage: (guild: Guild) => void }) {
  const installed = guilds.filter((guild) => guild.installed !== false);
  const available = guilds.filter((guild) => guild.installed === false);
  return <>
    <DashHeading eyebrow="Servers" title="Choose where to work." text="Manage servers with Niko already installed, or add Niko to another server you can administer." />
    <div className="server-summary">
      <div><strong>{formatNumber(installed.length)}</strong><span>Connected to Niko</span></div>
      <div><strong>{formatNumber(available.length)}</strong><span>Ready to add</span></div>
      <div className="server-summary-note"><Icon name="shield" /><span>Only servers where you have Manage Server access are shown.</span></div>
    </div>
    <section className="server-section">
      <div className="section-heading-row"><div><span className="panel-kicker">Connected</span><h3>Manage a server</h3></div><span className="section-count">{installed.length}</span></div>
      <div className="server-grid">{installed.map((guild) => <ServerCard key={guild.id} guild={guild} onManage={onManage} />)}{!installed.length && <div className="empty-state"><strong>No connected servers yet.</strong><span>Add Niko below, then come back here to manage it.</span></div>}</div>
    </section>
    <section className="server-section">
      <div className="section-heading-row"><div><span className="panel-kicker">Available to you</span><h3>Add Niko to a server</h3></div><span className="section-count">{available.length}</span></div>
      <div className="server-grid">{available.map((guild) => <ServerCard key={guild.id} guild={guild} onManage={onManage} />)}{!available.length && <div className="server-note">Niko is already installed in every server you can manage.</div>}</div>
    </section>
  </>;
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