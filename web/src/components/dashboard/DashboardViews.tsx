import { useEffect, useRef, useState, type ReactNode } from "react";
import { motion, useReducedMotion } from "motion/react";
import { saveEconomyPrivacy } from "../../api";
import { useStrings } from "../../i18n";
import { Icon } from "../Icon";
import { formatNumber } from "../../utils/format";
import { displayName } from "../../utils/format";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { GuildIcon } from "./GuildIcon";
import { Switch } from "./Switch";
import { SettingCard, SettingCards } from "./SettingCards";
import { MemberAvatar, UserAvatar } from "./UserAvatar";
import type { Guild, GuildConfig, GuildResources, GuildOverview, LevelRow, ReferralSummary, User, UserOverview } from "../../types";
import { LevelingSettings } from "./SettingsViews";
import { ServerStatsCard } from "./ServerStatsCard";

export function DashHeading({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) {
  const { t } = useStrings("dashboard");
  return <div className="dash-heading">
    <div className="heading-meta"><div className="eyebrow">{eyebrow}</div><span className="heading-context">{t("settings.controlRoom")}</span></div>
    <h1>{title}</h1>
    <p>{text}</p>
  </div>;
}

export function SectionSkeleton({ label }: { label: string }) {
  const { t } = useStrings("dashboard");
  return <div className="section-loading section-skeleton" role="status" aria-label={t("settings.loading", { label })}>
    <div className="skeleton-title" /><div className="skeleton-copy" />
    <div className="skeleton-grid"><i /><i /><i /></div>
    <span>{t("settings.loading", { label })}</span>
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

/**
 * The referral card: one link the member shares, and what it has brought in.
 *
 * The link is the website's ``/discord`` page carrying their id, so it resolves
 * to that member's own invite and every credited join pays them once. The
 * invite is minted on the bot, so the card still renders (and the link still
 * works) while that request is in flight.
 */
function ReferralCard({ referrals, userId }: { referrals: ReferralSummary | null; userId: string }) {
  const { t } = useStrings("dashboard");
  const [copied, setCopied] = useState(false);
  const link = referrals?.link || `${window.location.origin}/discord?ref=${userId}`;
  const invited = referrals?.invited ?? 0;
  const coins = referrals?.coins ?? 0;
  const reward = referrals?.reward ?? 0;
  const recent = referrals?.recent ?? [];
  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(link);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      // The link is printed below the button, so a refused clipboard is not
      // worth an error toast.
    }
  };
  return <section className="dash-panel referral-panel">
    <div className="panel-heading"><div><span className="panel-kicker">{t("dash.referralsKicker")}</span><h3>{t("dash.referralsTitle")}</h3></div><span className="panel-icon"><Icon name="users" /></span></div>
    <p className="referral-copy">{t("dash.referralsBefore")} <strong>{t("dash.referralsReward", { coins: formatNumber(reward) })}</strong> {t("dash.referralsAfter")}</p>
    <div className="referral-link">
      <code>{link}</code>
      <button type="button" className="button button-muted button-small" onClick={() => void copyLink()}>{t(copied ? "dash.copied" : "dash.copyLink")}</button>
    </div>
    <div className="referral-stats">
      <div><span>{t("dash.membersInvited")}</span><AnimatedValue value={invited}>{formatNumber(invited)}</AnimatedValue></div>
      <div><span>{t("dash.coinsEarned")}</span><AnimatedValue value={coins}>{formatNumber(coins)}</AnimatedValue></div>
      <div><span>{t("dash.perJoin")}</span><AnimatedValue value={reward}>{formatNumber(reward)}</AnimatedValue></div>
    </div>
    {recent.length > 0
      ? <ul className="referral-recent">
          {recent.map((entry) => <li key={entry.member_id}>
            <MemberAvatar name={entry.name || t("dash.nikoMember")} avatarUrl={entry.avatar_url} />
            <span className="referral-who"><strong>{entry.name || t("dash.member")}</strong><small>{new Date(entry.joined_at * 1000).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}</small></span>
            <span className="referral-paid">+{formatNumber(entry.reward)}</span>
          </li>)}
        </ul>
      : <p className="referral-empty">{t("dash.referralEmptyBefore")} <strong>{t("dash.firstInviteBadge")}</strong> {t("dash.referralEmptyAfter")}</p>}
  </section>;
}

export function UserOverviewView({ user, overview, guilds, referrals, onServers, onManage, csrfToken, guildsUnavailable = "" }: { user: User; overview: UserOverview | null; guilds: Guild[]; referrals: ReferralSummary | null; onServers: () => void; onManage: (guild: Guild) => void; csrfToken?: string; guildsUnavailable?: string }) {
  const { t } = useStrings("dashboard");
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
    notifyLoading(t("dash.savingPrivacy"), "economy-privacy");
    saveEconomyPrivacy(value, csrfToken)
      .then(() => notifySuccess(t(value ? "dash.privacyHidden" : "dash.privacyVisible"), "economy-privacy"))
      .catch((error) => {
        setPrivateLeaderboard(!value);
        notifyError(error instanceof Error ? error.message : t("dash.privacyFailed"), "economy-privacy");
      })
      .finally(() => { savingPrivacy.current = false; });
  };
  return <>
    <DashHeading eyebrow={t("dash.personalEyebrow")} title={t("dash.personalTitle")} text={t("dash.personalText")} />
    <div className="overview-intro">
      <div className="profile-card">
         <UserAvatar user={user} className="profile-avatar" />
        <div><span className="panel-kicker">{t("dash.signedInAs")}</span><h3>{displayName(user)}</h3><p>{t("dash.personalProfile")}</p></div>
      </div>
      <button className="button button-primary" onClick={onServers}>{t("dash.manageServer")} <Icon name="arrow" /></button>
    </div>
    <div className="dash-stats overview-stats">
      <StatCard label={t("dash.netWorth")} value={formatNumber(overview?.net_worth)} note={t("dash.netWorthNote")} accent="accent-orange" />
      <StatCard label={t("dash.inWallet")} value={formatNumber(overview?.balance)} note={t("dash.inWalletNote")} accent="accent-violet" />
      <StatCard label={t("dash.inVault")} value={formatNumber(overview?.bank)} note={t("dash.inVaultNote")} accent="accent-blue" />
      <StatCard label={t("dash.currentLevel")} value={formatNumber(overview?.level)} note={overview?.job_name ? t("dash.workingAs", { job: overview.job_name }) : t("dash.keepShowingUp")} accent="accent-green" />
    </div>
    <ReferralCard referrals={referrals} userId={user.id} />
    <section className="dash-panel economy-privacy-panel">
      <div className="panel-heading"><div><span className="panel-kicker">{t("dash.privacyKicker")}</span><h3>{t("dash.privacyTitle")}</h3></div><span className="panel-icon"><Icon name="shield" /></span></div>
      <SettingCards>
        <SettingCard
          title={t("dash.hideProfile")}
          hint={t("dash.hideProfileHint")}
          action={<Switch checked={privateLeaderboard} onCheckedChange={(value) => updatePrivacy(value)} aria-label={t("dash.hideProfile")} />}
        />
      </SettingCards>
    </section>
    <div className="dash-columns overview-columns">
      <section className="dash-panel">
        <div className="panel-heading"><div><span className="panel-kicker">{t("dash.progressKicker")}</span><h3>{t("dash.progressTitle")}</h3></div><span className="panel-icon"><Icon name="spark" /></span></div>
        <div className="metric-list">
          <div><span>{t("dash.dailyStreak")}</span><AnimatedValue value={overview?.daily_streak ?? 0}>{formatNumber(overview?.daily_streak)} <small>{t("dash.days")}</small></AnimatedValue></div>
          <div><span>{t("dash.achievements")}</span><AnimatedValue value={overview?.achievements ?? 0}>{formatNumber(overview?.achievements)} <small>{t("dash.unlocked")}</small></AnimatedValue></div>
          <div><span>{t("dash.totalEarned")}</span><AnimatedValue value={overview?.total_earned ?? 0}>{formatNumber(overview?.total_earned)} <small>{t("dash.coins")}</small></AnimatedValue></div>
          <div><span>{t("dash.economyStanding")}</span><AnimatedValue value={overview?.economy_rank ?? 0}>{overview?.economy_rank ? `#${formatNumber(overview.economy_rank)}` : "—"} <small>{overview?.economy_profiles ? t("dash.ofTotal", { total: formatNumber(overview.economy_profiles) }) : ""}</small></AnimatedValue></div>
        </div>
      </section>
      <section className="dash-panel">
        <div className="panel-heading"><div><span className="panel-kicker">{t("dash.quickAccess")}</span><h3>{t("dash.yourServers")}</h3></div><span className="panel-icon"><Icon name="users" /></span></div>
        <div className="mini-server-list">
          {installed.slice(0, 4).map((guild) => <button key={guild.id} onClick={() => onManage(guild)}><GuildIcon guild={guild} /><span>{guild.name}</span><Icon name="arrow" /></button>)}
          {!installed.length && <p className="empty-state compact">{t(guildsUnavailable ? "dash.serversUnavailable" : "dash.addToStart")}</p>}
        </div>
        <button className="text-link overview-link" onClick={onServers}>{t("dash.viewAllServers")} <Icon name="arrow" /></button>
      </section>
    </div>
  </>;
}

function ServerCard({ guild, onManage }: { guild: Guild; onManage: (guild: Guild) => void }) {
  const { t } = useStrings("dashboard");
  const installed = guild.installed !== false;
  return <article className="server-card">
    <div className="server-card-heading"><GuildIcon guild={guild} className="server-avatar" /><span className="server-status">{t(installed ? "dash.installed" : "dash.readyToAdd")}</span></div>
    <h3>{guild.name}</h3>
    <p>{t(installed ? "dash.cardInstalledText" : "dash.cardAvailableText")}</p>
    {installed ? <button className="button button-muted button-small" onClick={() => onManage(guild)}>{t("dash.openSettings")} <Icon name="arrow" /></button> : <a className="button button-primary button-small" href={guild.invite_url || "#"} target="_blank" rel="noreferrer">{t("dash.addNiko")} <Icon name="external" /></a>}
  </article>;
}

export function ServersView({ guilds, onManage, unavailable = "", onRetry, retrying = false, loginUrl = "" }: { guilds: Guild[]; onManage: (guild: Guild) => void; unavailable?: string; onRetry?: () => void; retrying?: boolean; loginUrl?: string }) {
  const { t } = useStrings("dashboard");
  const installed = guilds.filter((guild) => guild.installed !== false);
  const available = guilds.filter((guild) => guild.installed === false);
  // A failed read is reported as such: the empty grid below would otherwise
  // read as "you have no servers" when Discord simply did not answer.
  if (unavailable) {
    return <>
      <DashHeading eyebrow={t("dash.serversEyebrow")} title={t("dash.serversTitle")} text={t("dash.serversText")} />
      <section className="dash-panel server-unavailable" role="alert">
        <div className="panel-heading"><div><span className="panel-kicker">{t("dash.serverListKicker")}</span><h3>{t("dash.serversFailed")}</h3></div><span className="panel-icon"><Icon name="shield" /></span></div>
        <div className="server-unavailable-body">
          <p>{unavailable}</p>
          {loginUrl
            ? <a className="button button-primary button-small" href={loginUrl}>{t("dash.signInAgain")} <Icon name="arrow" /></a>
            : onRetry && <button className="button button-muted button-small" onClick={onRetry} disabled={retrying}>{t(retrying ? "dash.retrying" : "dash.tryAgain")} <Icon name="arrow" /></button>}
        </div>
      </section>
    </>;
  }
  return <>
    <DashHeading eyebrow={t("dash.serversEyebrow")} title={t("dash.serversTitle")} text={t("dash.serversText")} />
    <div className="server-summary">
      <div><strong>{formatNumber(installed.length)}</strong><span>{t("dash.connectedToNiko")}</span></div>
      <div><strong>{formatNumber(available.length)}</strong><span>{t("dash.readyToAdd")}</span></div>
      <div className="server-summary-note"><Icon name="shield" /><span>{t("dash.manageAccessNote")}</span></div>
    </div>
    <section className="server-section">
      <div className="section-heading-row"><div><span className="panel-kicker">{t("dash.connectedKicker")}</span><h3>{t("dash.manageServer")}</h3></div><span className="section-count">{installed.length}</span></div>
      <div className="server-grid">{installed.map((guild) => <ServerCard key={guild.id} guild={guild} onManage={onManage} />)}{!installed.length && <div className="empty-state"><strong>{t("dash.noConnected")}</strong><span>{t("dash.noConnectedHint")}</span></div>}</div>
    </section>
    <section className="server-section">
      <div className="section-heading-row"><div><span className="panel-kicker">{t("dash.availableKicker")}</span><h3>{t("dash.addNikoTitle")}</h3></div><span className="section-count">{available.length}</span></div>
      <div className="server-grid">{available.map((guild) => <ServerCard key={guild.id} guild={guild} onManage={onManage} />)}{!available.length && <div className="server-note">{t("dash.allInstalled")}</div>}</div>
    </section>
  </>;
}

export function RankList({ rows }: { rows: LevelRow[] }) {
  const { t } = useStrings("dashboard");
  return <div className="rank-list">
    {rows.slice(0, 5).map((row, index) => <div className="rank-row" key={`${row.user_id}-${index}`}>
      <span className={`rank rank-${index + 1}`}>{String(index + 1).padStart(2, "0")}</span>
      <span className="rank-user"><MemberAvatar name={row.display_name || row.username || t("dash.unknownMember")} avatarUrl={row.avatar_url} /><span><strong>{row.display_name || row.username || t("dash.unknownMember")}</strong>{row.username && row.display_name && <small>@{row.username}</small>}</span></span>
      <strong>{t("dash.levelValue", { level: formatNumber(row.level) })}<small>{t("dash.xpValue", { xp: formatNumber(row.xp) })}</small></strong>
    </div>)}
    {!rows.length && <div className="empty-state compact">{t("dash.noData")}</div>}
  </div>;
}

export function OverviewView({ overview }: { overview: GuildOverview }) {
  const { t } = useStrings("dashboard");
  return <>
    <div className="guild-welcome">
      <div><span className="welcome-mark"><Icon name="grid" /></span><div><span className="panel-kicker">{t("dash.pulseKicker")}</span><strong>{t("dash.pulseTitle")}</strong></div></div>
    </div>
    <DashHeading eyebrow={t("dash.overviewEyebrow")} title={t("dash.overviewTitle")} text={t("dash.overviewText")} />
    <div className="dash-stats guild-overview-stats">
      <StatCard label={t("dash.warningsLogged")} value={formatNumber(overview.moderation.warn_count)} note={t("dash.forThisServer")} accent="accent-blue" />
      <StatCard label={t("dash.automod")} value={t(overview.moderation.automod_active ? "notifier.active" : "dash.quiet")} note={t("dash.protectionStatus")} accent="accent-green" />
      <StatCard label={t("dash.levelLeaders")} value={formatNumber(overview.leveling.top.length)} note={t("dash.membersWithXp")} accent="accent-violet" />
    </div>
    <ServerStatsCard stats={overview.server} />
    <div className="dash-columns overview-columns">
      <section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">{t("dash.communityEnergy")}</span><h3>{t("dash.topXp")}</h3></div><span className="panel-icon"><Icon name="spark" /></span></div><RankList rows={overview.leveling.top} /></section>
    </div>
  </>;
}

export function LevelingView({ rows, config, resources, csrfToken, guildId }: { rows: LevelRow[]; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string; guildId: string }) {
  const { t } = useStrings("dashboard");
  return <>
    <DashHeading eyebrow={t("dash.levelingEyebrow")} title={t("dash.levelingTitle")} text={t("dash.levelingText")} />
    <div className="dash-stats"><StatCard label={t("dash.topLevel")} value={String(rows[0]?.level || 0)} note={rows[0]?.display_name || rows[0]?.username || t("dash.noMembersYet")} accent="accent-violet" /><StatCard label={t("leveling.multiplierLabel")} value={`${config?.leveling.xp_multiplier || 1}×`} note={t(config?.leveling.xp_enabled === false ? "dash.xpDisabled" : "dash.currentlyActive")} accent="accent-blue" /><StatCard label={t("dash.cooldown")} value={`${config?.leveling.xp_cooldown || 0}s`} note={t("dash.betweenAwards")} accent="accent-green" /></div>
    <section className="dash-panel"><div className="panel-heading"><div><span className="panel-kicker">{t("dash.leaderboardKicker")}</span><h3>{t("dash.xpLeaders")}</h3></div><span className="panel-icon"><Icon name="spark" /></span></div><RankList rows={rows} /></section>
    <LevelingSettings guildId={guildId} config={config} resources={resources} csrfToken={csrfToken} />
  </>;
}