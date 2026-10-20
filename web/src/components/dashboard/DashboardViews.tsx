import { useEffect, useRef, useState, type ReactNode } from "react";
import { motion, useReducedMotion } from "motion/react";
import { saveEconomyPrivacy } from "../../api";
import { Icon } from "../Icon";
import { formatNumber } from "../../utils/format";
import { displayName } from "../../utils/format";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { GuildIcon } from "./GuildIcon";
import { MemberAvatar, UserAvatar } from "./UserAvatar";
import type { Guild, GuildConfig, GuildResources, GuildOverview, LevelRow, User, UserOverview } from "../../types";
import { LevelingSettings } from "./SettingsViews";
import { ServerStatsCard } from "./ServerStatsCard";

export function DashHeading({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) {
  return <div className="dash-heading">
    <div className="heading-meta"><div className="eyebrow">{eyebrow}</div><span className="heading-context">NIKO / CONTROL ROOM</span></div>
    <h2>{title}</h2>
    <p>{text}</p>
  </div>;
}

/**
 * A value on a live page. It eases in once when the number it shows changes,
 * and stays perfectly still on a refresh that changed nothing.
 */
export function AnimatedValue({ value, children, className = "" }: { value: string | number; children: ReactNode; className?: string }) {
  const reduceMotion = useReducedMotion();
  const previous = useRef(value);
  const changed = previous.current !== value;
  useEffect(() => { previous.current = value; }, [value]);
  return <motion.strong
    className={className || undefined}
    key={String(value)}
    initial={changed && !reduceMotion ? { opacity: 0.4, y: 4 } : false}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.32, ease: "easeOut" }}
  >{children}</motion.strong>;
}

export function StatCard({ label, value, note, accent = "" }: { label: string; value: string; note: string; accent?: string }) {
  return <div className={`dash-stat ${accent}`}><span>{label}</span><AnimatedValue value={value}>{value}</AnimatedValue><small>{note}</small></div>;
}

/**
 * The economy has a single currency, so the unit is set apart once per amount
 * instead of being repeated in bold next to every number.
 */
export function CoinLabel() {
  return <span className="economy-coin">coins</span>;
}

export function UserOverviewView({ user, overview, guilds, onServers, onManage, csrfToken, guildsUnavailable = "" }: { user: User; overview: UserOverview | null; guilds: Guild[]; onServers: () => void; onManage: (guild: Guild) => void; csrfToken?: string; guildsUnavailable?: string }) {
  const installed = guilds.filter((guild) => guild.installed !== false);
  const [privateLeaderboard, setPrivateLeaderboard] = useState(Boolean(overview?.leaderboard_private));
  // A poll can land between the switch flipping and the save finishing. While a
  // save is in flight the optimistic value wins, so the switch never snaps back
  // under the reader's finger.
  const savingPrivacy = useRef(false);
  useEffect(() => {
    if (!savingPrivacy.current) setPrivateLeaderboard(Boolean(overview?.leaderboard_private));
  }, [overview?.leaderboard_private]);
  // The toggle itself shows the pending state by staying where the user put it,
  // so only the result is reported, as a toast like every other dashboard save.
  const updatePrivacy = (value: boolean) => {
    setPrivateLeaderboard(value);
    savingPrivacy.current = true;
    notifyLoading("Saving privacy setting…", "economy-privacy");
    saveEconomyPrivacy(value, csrfToken)
      .then(() => notifySuccess(value ? "Profile hidden on the public leaderboard." : "Profile visible on the public leaderboard.", "economy-privacy"))
      .catch((error) => {
        setPrivateLeaderboard(!value);
        notifyError(error instanceof Error ? error.message : "Could not save privacy setting.", "economy-privacy");
      })
      .finally(() => { savingPrivacy.current = false; });
  };
  return <>
    <DashHeading eyebrow="Personal overview" title="Your Niko snapshot." text="Keep an eye on your progress, then jump into a server when you’re ready to tune the room." />
    <div className="overview-intro">
      <div className="profile-card">
         <UserAvatar user={user} className="profile-avatar" />
        <div><span className="panel-kicker">Signed in as</span><h3>{displayName(user)}</h3><p>Personal economy profile</p></div>
      </div>
      <button className="button button-primary" onClick={onServers}>Manage a server <Icon name="arrow" /></button>
    </div>
    <div className="dash-stats overview-stats">
      <StatCard label="Net worth" value={formatNumber(overview?.net_worth)} note="Across your Niko profile" accent="accent-orange" />
      <StatCard label="In your wallet" value={formatNumber(overview?.balance)} note="Ready to spend" accent="accent-violet" />
      <StatCard label="In your vault" value={formatNumber(overview?.bank)} note="Saved for later" accent="accent-blue" />
      <StatCard label="Current level" value={formatNumber(overview?.level)} note={overview?.job_name ? `Working as a ${overview.job_name}` : "Keep showing up"} accent="accent-green" />
    </div>
    <section className="dash-panel economy-privacy-panel">
      <div className="panel-heading"><div><span className="panel-kicker">Leaderboard privacy</span><h3>Choose who sees your identity</h3></div><span className="panel-icon"><Icon name="shield" /></span></div>
      <label className="setting-row"><span><strong>Hide my profile on the public leaderboard</strong><small>You’ll remain ranked, but your avatar, username, and display name are shown only to you, official Niko staff, and people who share a guild with you.</small></span><input type="checkbox" checked={privateLeaderboard} onChange={(event) => updatePrivacy(event.target.checked)} /><i aria-hidden="true" /></label>
    </section>
    <div className="dash-columns overview-columns">
      <section className="dash-panel">
        <div className="panel-heading"><div><span className="panel-kicker">Progress</span><h3>Your momentum</h3></div><span className="panel-icon"><Icon name="spark" /></span></div>
        <div className="metric-list">
          <div><span>Daily streak</span><AnimatedValue value={overview?.daily_streak ?? 0}>{formatNumber(overview?.daily_streak)} <small>days</small></AnimatedValue></div>
          <div><span>Achievements</span><AnimatedValue value={overview?.achievements ?? 0}>{formatNumber(overview?.achievements)} <small>unlocked</small></AnimatedValue></div>
          <div><span>Total earned</span><AnimatedValue value={overview?.total_earned ?? 0}>{formatNumber(overview?.total_earned)} <small>coins</small></AnimatedValue></div>
          <div><span>Economy standing</span><AnimatedValue value={overview?.economy_rank ?? 0}>{overview?.economy_rank ? `#${formatNumber(overview.economy_rank)}` : "—"} <small>{overview?.economy_profiles ? `of ${formatNumber(overview.economy_profiles)}` : ""}</small></AnimatedValue></div>
        </div>
      </section>
      <section className="dash-panel">
        <div className="panel-heading"><div><span className="panel-kicker">Quick access</span><h3>Your servers</h3></div><span className="panel-icon"><Icon name="users" /></span></div>
        <div className="mini-server-list">
          {installed.slice(0, 4).map((guild) => <button key={guild.id} onClick={() => onManage(guild)}><GuildIcon guild={guild} /><span>{guild.name}</span><Icon name="arrow" /></button>)}
          {!installed.length && <p className="empty-state compact">{guildsUnavailable ? "Your server list could not be loaded from Discord. Open Servers to retry." : "Add Niko to a server to start managing it."}</p>}
        </div>
        <button className="text-link overview-link" onClick={onServers}>View all servers <Icon name="arrow" /></button>
      </section>
    </div>
  </>;
}

function ServerCard({ guild, onManage }: { guild: Guild; onManage: (guild: Guild) => void }) {
  const installed = guild.installed !== false;
  return <article className="server-card">
    <div className="server-card-heading"><GuildIcon guild={guild} className="server-avatar" /><span className="server-status">{installed ? "Niko is installed" : "Ready to add"}</span></div>
    <h3>{guild.name}</h3>
    <p>{installed ? "Open the dashboard to manage Niko’s features and settings." : "You have permission to manage this server. Add Niko to unlock its controls."}</p>
    {installed ? <button className="button button-muted button-small" onClick={() => onManage(guild)}>Open settings <Icon name="arrow" /></button> : <a className="button button-primary button-small" href={guild.invite_url || "#"} target="_blank" rel="noreferrer">Add Niko <Icon name="external" /></a>}
  </article>;
}

export function ServersView({ guilds, onManage, unavailable = "", onRetry, retrying = false, loginUrl = "" }: { guilds: Guild[]; onManage: (guild: Guild) => void; unavailable?: string; onRetry?: () => void; retrying?: boolean; loginUrl?: string }) {
  const installed = guilds.filter((guild) => guild.installed !== false);
  const available = guilds.filter((guild) => guild.installed === false);
  // A failed read is reported as such: the empty grid below would otherwise
  // read as "you have no servers" when Discord simply did not answer.
  if (unavailable) {
    return <>
      <DashHeading eyebrow="Servers" title="Choose where to work." text="Manage servers with Niko already installed, or add Niko to another server you can administer." />
      <section className="dash-panel server-unavailable" role="alert">
        <div className="panel-heading"><div><span className="panel-kicker">Server list</span><h3>Discord didn’t return your servers</h3></div><span className="panel-icon"><Icon name="shield" /></span></div>
        <div className="server-unavailable-body">
          <p>{unavailable}</p>
          {loginUrl
            ? <a className="button button-primary button-small" href={loginUrl}>Sign in again <Icon name="arrow" /></a>
            : onRetry && <button className="button button-muted button-small" onClick={onRetry} disabled={retrying}>{retrying ? "Retrying…" : "Try again"} <Icon name="arrow" /></button>}
        </div>
      </section>
    </>;
  }
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

export function RankList({ rows }: { rows: LevelRow[] }) {
  return <div className="rank-list">
    {rows.slice(0, 5).map((row, index) => <div className="rank-row" key={`${row.user_id}-${index}`}>
      <span className={`rank rank-${index + 1}`}>{String(index + 1).padStart(2, "0")}</span>
      <span className="rank-user"><MemberAvatar name={row.display_name || row.username || "Unknown member"} avatarUrl={row.avatar_url} /><span><strong>{row.display_name || row.username || "Unknown member"}</strong>{row.username && row.display_name && <small>@{row.username}</small>}</span></span>
      <strong>Level {formatNumber(row.level)}<small>{formatNumber(row.xp)} xp</small></strong>
    </div>)}
    {!rows.length && <div className="empty-state compact">No data recorded yet.</div>}
  </div>;
}

export function OverviewView({ overview }: { overview: GuildOverview }) {
  return <>
    <div className="guild-welcome">
      <div><span className="welcome-mark"><Icon name="grid" /></span><div><span className="panel-kicker">Server pulse</span><strong>Here’s what needs your attention.</strong></div></div>
    </div>
    <DashHeading eyebrow="Overview" title="A quick read on your room." text="The important signals, without making you hunt for them." />
    <div className="dash-stats guild-overview-stats">
      <StatCard label="Warnings logged" value={formatNumber(overview.moderation.warn_count)} note="For this server" accent="accent-blue" />
      <StatCard label="Automod" value={overview.moderation.automod_active ? "Active" : "Quiet"} note="Protection status" accent="accent-green" />
      <StatCard label="Level leaders" value={formatNumber(overview.leveling.top.length)} note="Members with recorded XP" accent="accent-violet" />
    </div>
    <ServerStatsCard stats={overview.server} />
    <div className="dash-columns overview-columns">
      <section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Community energy</span><h3>Top XP</h3></div><span className="panel-icon"><Icon name="spark" /></span></div><RankList rows={overview.leveling.top} /></section>
      <section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Server controls</span><h3>Manage the room</h3></div><span className="panel-icon"><Icon name="settings" /></span></div><div className="server-controls-body"><p>Use Server settings for prefixes, welcome messages, logs, and ticket panels.</p><span className="text-link">Open server settings <Icon name="arrow" /></span></div></section>
    </div>
  </>;
}

export function LevelingView({ rows, config, resources, csrfToken, guildId }: { rows: LevelRow[]; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string; guildId: string }) {
  return <>
    <DashHeading eyebrow="Leveling" title="Momentum people can see." text="Track the members turning up, and tune the pace to fit your server." />
    <div className="dash-stats"><StatCard label="Top level" value={String(rows[0]?.level || 0)} note={rows[0]?.display_name || rows[0]?.username || "No members yet"} accent="accent-violet" /><StatCard label="XP multiplier" value={`${config?.leveling.xp_multiplier || 1}×`} note={config?.leveling.xp_enabled === false ? "XP disabled" : "Currently active"} accent="accent-blue" /><StatCard label="Cooldown" value={`${config?.leveling.xp_cooldown || 0}s`} note="Between XP awards" accent="accent-green" /></div>
    <section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">Leaderboard</span><h3>XP leaders</h3></div><span className="panel-icon"><Icon name="spark" /></span></div><RankList rows={rows} /></section>
    <LevelingSettings guildId={guildId} config={config} resources={resources} csrfToken={csrfToken} />
  </>;
}