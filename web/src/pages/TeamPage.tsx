import { useEffect, useState } from "react";
import { getTeam, getTeamMember, getTeamProfileCard } from "../api";
import { PublicHeader } from "../components/PublicHeader";
import { PublicPageIntro } from "../components/PublicPageIntro";
import { Footer } from "../components/Footer";
import { DiscordStatusAvatar } from "../components/DiscordStatusAvatar";
import { navigate } from "../router";
import type { SocialProfileCardData, StaffActivity, StaffEmoji, StaffMember } from "../types";

function avatar(member: StaffMember) {
  return member.avatar_url;
}

function twemojiUrl(value: string) {
  const codepoints = Array.from(value)
    .filter((character) => character !== "\uFE0E" && character !== "\uFE0F")
    .map((character) => character.codePointAt(0)!.toString(16))
    .join("-");
  return `https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/${codepoints}.svg`;
}

function ActivityEmoji({ emoji }: { emoji?: StaffEmoji | null }) {
  if (!emoji) return null;
  if (emoji.kind === "custom") {
    return <img className="presence-emoji" src={`https://cdn.discordapp.com/emojis/${emoji.value}.${emoji.animated ? "gif" : "png"}?size=18`} alt={emoji.name || "custom emoji"} />;
  }
  return <img className="presence-emoji" src={twemojiUrl(emoji.value)} alt={emoji.name || emoji.value} />;
}

function activityLabel(type: string) {
  const labels: Record<string, string> = { playing: "Playing", listening: "Listening to", watching: "Watching", streaming: "Streaming", competing: "Competing in" };
  return labels[type] || (type ? `${type.charAt(0).toUpperCase()}${type.slice(1)}` : "Activity");
}

function formatClock(milliseconds: number) {
  const total = Math.max(0, Math.round(milliseconds / 1000));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

// Spotify shares the custom-status card layout and adds a live track progress
// bar, so a listening status reads as the same kind of card as a custom status.
function SpotifyActivityCard({ activity }: { activity: StaffActivity }) {
  const start = activity.start ? Date.parse(activity.start) : Number.NaN;
  const end = activity.end ? Date.parse(activity.end) : Number.NaN;
  const hasWindow = Number.isFinite(start) && Number.isFinite(end) && end > start;
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (!hasWindow) return;
    setNow(Date.now());
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [hasWindow, start, end]);

  const total = hasWindow ? end - start : 0;
  const elapsed = hasWindow ? Math.min(Math.max(now - start, 0), total) : 0;
  const card = <span className="profile-custom-status profile-spotify-status">
    <span className="profile-custom-status-emoji">{activity.image_url ? <img src={activity.image_url} alt="" /> : <PlatformMark platform="spotify" />}</span>
    <span className="profile-custom-status-copy">
      <small>Listening on Spotify</small>
      <span>{activity.details || "Spotify"}</span>
      {activity.state && <span className="profile-spotify-artist">{activity.state}</span>}
    </span>
    {hasWindow && <span className="profile-status-progress">
      <span className="profile-status-track" aria-hidden="true"><i style={{ width: `${(elapsed / total) * 100}%` }} /></span>
      <span className="profile-status-times"><small>{formatClock(elapsed)}</small><small>{formatClock(total)}</small></span>
    </span>}
  </span>;
  return activity.url ? <a className="presence-activity" href={activity.url} target="_blank" rel="noreferrer">{card}</a> : <span className="presence-activity">{card}</span>;
}

function ActivitySummary({ activity }: { activity: StaffActivity }) {
  if (activity.kind === "spotify") return <SpotifyActivityCard activity={activity} />;
  const primary = activity.name;
  const secondaryLines = [activity.details, activity.state]
    .filter((line): line is string => Boolean(line && line !== primary));
  const card = <span className={`activity-card activity-${activity.kind}`}>
    {activity.image_url && <img className="activity-art" src={activity.image_url} alt="" />}
    <span className="activity-copy"><strong>{activityLabel(activity.type)}</strong><span>{primary}</span>{secondaryLines.map((line, index) => <small key={`${line}-${index}`}>{line}</small>)}</span>
  </span>;
  return activity.url ? <a className="presence-activity" href={activity.url} target="_blank" rel="noreferrer">{card}</a> : <span className="presence-activity">{card}</span>;
}

function statusLabel(member: StaffMember) {
  return member.status_label || ({ online: "Online", idle: "Idle", dnd: "Do Not Disturb", offline: "Offline" }[member.status || "offline"] || "Offline");
}

function StatusAvatar({ member, className }: { member: StaffMember; className: string }) {
  return <DiscordStatusAvatar status={member.status} className={className} label={statusLabel(member)}>
    {avatar(member) ? <img className={className} src={avatar(member)!} alt="" /> : <span className={`${className} team-avatar-fallback`}>{member.name.slice(0, 1)}</span>}
  </DiscordStatusAvatar>;
}

type ProfileLink = NonNullable<StaffMember["public_links"]>[number];

type PlatformMeta = { label: string; mark: string };

// Official brand glyphs (simple-icons) so every profile card names its platform
// in text as well as in colour. The GitHub card previously had neither.
const PLATFORM_META: Record<string, PlatformMeta> = {
  github: {
    label: "GitHub",
    mark: "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12",
  },
  bluesky: {
    label: "Bluesky",
    mark: "M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479.815 2.736 3.713 3.66 6.383 3.364.136-.02.275-.039.415-.056-.138.022-.276.04-.415.056-3.912.58-7.387 2.005-2.83 7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 7.733 4.308 4.267-4.308 1.172-6.498-2.74-7.078a8.741 8.741 0 0 1-.415-.056c.14.017.279.036.415.056 2.67.297 5.568-.628 6.383-3.364.246-.828.624-5.79.624-6.478 0-.69-.139-1.861-.902-2.206-.659-.298-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 12 10.8Z",
  },
  twitch: {
    label: "Twitch",
    mark: "M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714Z",
  },
  youtube: {
    label: "YouTube",
    mark: "M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z",
  },
  reddit: {
    label: "Reddit",
    mark: "M12 0C5.373 0 0 5.373 0 12c0 3.314 1.343 6.314 3.515 8.485l-2.286 2.286C.775 23.225 1.097 24 1.738 24H12c6.627 0 12-5.373 12-12S18.627 0 12 0Zm4.388 3.199c1.104 0 1.999.895 1.999 1.999 0 1.105-.895 2-1.999 2-.946 0-1.739-.657-1.947-1.539v.002c-1.147.162-2.032 1.15-2.032 2.341v.007c1.776.067 3.4.567 4.686 1.363.473-.363 1.064-.58 1.707-.58 1.547 0 2.802 1.254 2.802 2.802 0 1.117-.655 2.081-1.601 2.531-.088 3.256-3.637 5.876-7.997 5.876-4.361 0-7.905-2.617-7.998-5.87-.954-.447-1.614-1.415-1.614-2.538 0-1.548 1.255-2.802 2.803-2.802.645 0 1.239.218 1.712.585 1.275-.79 2.881-1.291 4.64-1.365v-.01c0-1.663 1.263-3.034 2.88-3.207.188-.911.993-1.595 1.959-1.595Zm-8.085 8.376c-.784 0-1.459.78-1.506 1.797-.047 1.016.64 1.429 1.426 1.429.786 0 1.371-.369 1.418-1.385.047-1.017-.553-1.841-1.338-1.841Zm7.406 0c-.786 0-1.385.824-1.338 1.841.047 1.017.634 1.385 1.418 1.385.785 0 1.473-.413 1.426-1.429-.046-1.017-.721-1.797-1.506-1.797Zm-3.703 4.013c-.974 0-1.907.048-2.77.135-.147.015-.241.168-.183.305.483 1.154 1.622 1.964 2.953 1.964 1.33 0 2.47-.81 2.953-1.964.057-.137-.037-.29-.184-.305-.863-.087-1.795-.135-2.769-.135Z",
  },
  x: {
    label: "X",
    mark: "M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z",
  },
  spotify: {
    label: "Spotify",
    mark: "M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z",
  },
};

function PlatformMark({ platform }: { platform: string }) {
  const mark = PLATFORM_META[platform]?.mark;
  if (!mark) return null;
  return <svg className="platform-mark" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d={mark} /></svg>;
}

function profileHandle(card: SocialProfileCardData) {
  if (!card.handle) return "";
  return /^[ru]\//i.test(card.handle) ? card.handle : `@${card.handle}`;
}

function ProfileLinkCard({ link }: { link: ProfileLink }) {
  const platform = (link.type || "").toLowerCase();
  const meta = PLATFORM_META[platform];
  const [card, setCard] = useState<SocialProfileCardData | null>(null);
  const [loading, setLoading] = useState(Boolean(meta));

  useEffect(() => {
    if (!meta) return;
    let active = true;
    const controller = new AbortController();
    setLoading(true);
    getTeamProfileCard(platform, link.url, controller.signal)
      .then((response) => {
        if (active) setCard(response.card);
      })
      .catch(() => {
        if (active) setCard(null);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [platform, link.url, meta]);

  if (!meta) {
    return <a className="team-profile-link-card" href={link.url} target="_blank" rel="noopener noreferrer">
      <span>{link.label || link.type}</span><span aria-hidden="true">↗</span>
    </a>;
  }

  const failed = !loading && !card;
  if (failed) {
    return <a className="team-profile-link-card" href={link.url} target="_blank" rel="noopener noreferrer">
      <span className={`link-card-chip platform-${platform}`}><PlatformMark platform={platform} />{meta.label}</span>
      <span>{link.label || meta.label}</span><span aria-hidden="true">↗</span>
    </a>;
  }

  return <a className="team-profile-social-card social-profile-card" href={card?.url || link.url} target="_blank" rel="noopener noreferrer" aria-label={`${card?.display_name || meta.label} on ${meta.label}`}>
    <span className={`social-card-chip platform-${platform}`}><PlatformMark platform={platform} />{meta.label}</span>
    <span className={`social-card-avatar platform-${platform}`}>
      {card?.avatar_url ? <img src={card.avatar_url} alt="" /> : <PlatformMark platform={platform} />}
    </span>
    <span className="social-card-details">
      <strong>{card ? card.display_name || profileHandle(card) : `Loading ${meta.label} profile…`}</strong>
      {card && profileHandle(card) && <small>{profileHandle(card)}</small>}
      {card?.bio && <span className="social-card-bio">{card.bio}</span>}
      {card?.status && <span className="social-card-status">{card.status}</span>}
    </span>
    {Boolean(card?.stats?.length) && <span className="social-card-stats">
      {(card?.stats || []).slice(0, 3).map((stat) => <span key={stat.label}><strong>{stat.value}</strong><small>{stat.label}</small></span>)}
    </span>}
  </a>;
}

function PresenceSummary({ member }: { member: StaffMember }) {
  const custom = member.custom_status;
  const activities = member.activities || [];
  const hasCustom = Boolean(custom?.text || custom?.emoji);
  if (!hasCustom && !activities.length) return null;
  return <div className="presence-stack">
    {hasCustom && <div className="profile-custom-status"><span className="profile-custom-status-emoji"><ActivityEmoji emoji={custom?.emoji} /></span><span className="profile-custom-status-copy"><small>Custom status</small><span>{custom?.text || "Sharing an emoji status"}</span></span></div>}
    {activities.length > 0 && <div className="presence-activity-list">{activities.map((activity, index) => <ActivitySummary activity={activity} key={`${activity.kind}-${activity.name}-${index}`} />)}</div>}
  </div>;
}

const teamStyles = `
.team-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));align-items:start;gap:14px;margin-top:58px}.team-application-cta{display:flex;align-items:center;justify-content:space-between;gap:12px;width:min(100%,480px);margin:44px auto 0;padding:10px 13px;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:8px}.team-application-cta .panel-kicker{color:var(--dim);font-size:8px;white-space:nowrap}.team-application-cta p{flex:1;margin:0;font-size:10px}.team-application-cta>a{color:var(--accent-dark);font-size:10px;font-weight:700;white-space:nowrap}.team-application-cta>a:hover{color:var(--ink);text-decoration:none}.team-card{display:flex;flex-direction:column;min-width:0;overflow:hidden;padding:0;color:var(--ink);text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow-soft)}.team-card:hover{border-color:#dfaa98;transform:translateY(-2px)}.team-card:focus-visible{outline:2px solid var(--accent-dark);outline-offset:3px}.team-card-art,.team-profile-banner{min-height:105px;background:linear-gradient(135deg,var(--callout),var(--surface-muted));background-size:cover;background-position:center}.team-card-body{display:flex;align-items:flex-start;flex:1;min-width:0;gap:14px;padding:18px}.team-card-body>div:last-child{min-width:0}.team-card h2,.team-card p{overflow-wrap:anywhere}.team-avatar,.team-profile-avatar{display:grid;place-items:center;flex:0 0 auto;overflow:hidden;color:#fffaf5;background:var(--accent);border-radius:50%;font-weight:800;object-fit:cover}.team-avatar{width:56px;height:56px;margin-top:-39px;border:3px solid var(--surface)}.team-role{color:var(--accent-dark);text-transform:uppercase;letter-spacing:.1em;font:700 9px "Space Mono",monospace}.team-card h2{margin:5px 0 6px;font-size:17px}.team-card p{margin:0 0 10px;color:var(--muted);font-size:11px;line-height:1.6}.team-card-footer{display:flex;align-items:center;justify-content:space-between;padding:5px 17px 8px;color:#858c96;background:transparent;border:0;font:8px "Space Mono",monospace;letter-spacing:.03em;text-transform:uppercase;transition:color .18s ease}.team-card-footer>span:last-child{color:#858c96;font-size:12px;transition:transform .18s ease}.team-card:hover .team-card-footer{color:#b4bac3;background:transparent}.team-card:hover .team-card-footer>span:last-child{color:#b4bac3}.team-card:hover .team-card-footer>span:last-child{transform:translate(2px,-2px)}.team-status{color:var(--dim);font-size:10px}.presence-stack{display:grid;gap:10px}.profile-custom-status{display:flex;align-items:center;gap:11px;min-width:0;padding:11px 12px;background:#1b1d21;border:1px solid #303238;border-radius:9px}.profile-custom-status-emoji{display:grid;place-items:center;width:36px;height:36px;flex:0 0 auto;background:#25272d;border-radius:8px}.profile-custom-status-emoji:empty{display:none}.profile-custom-status-emoji .presence-emoji{width:21px;height:21px}.profile-custom-status-copy{display:grid;min-width:0;gap:3px}.profile-custom-status-copy small{color:#858c96;font:8px "Space Mono",monospace;letter-spacing:.1em;text-transform:uppercase}.profile-custom-status-copy>span{overflow-wrap:anywhere;color:#e3e5e8;font-size:11px;line-height:1.5}.presence-activity-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:8px}.presence-activity{display:block;min-width:0;color:inherit}.presence-activity:hover{text-decoration:none}.activity-card{display:flex;align-items:center;min-width:0;min-height:62px;gap:11px;padding:9px 11px;background:#1b1d21;border:1px solid #303238;border-radius:9px;text-align:left;transition:background .18s ease,border-color .18s ease,transform .18s ease}.presence-activity[href]:hover .activity-card{transform:translateY(-1px);background:#222429;border-color:#484c55}.activity-art{width:42px;height:42px;flex:0 0 auto;border-radius:7px;object-fit:cover}.activity-copy{display:flex;min-width:0;flex-direction:column;gap:3px}.activity-copy strong{color:#9da5b1;font-size:8px;text-transform:uppercase;letter-spacing:.08em}.activity-copy span,.activity-copy small{overflow:hidden;max-width:100%;text-overflow:ellipsis;white-space:nowrap}.activity-copy span{color:#f2f3f5;font-size:11px;font-weight:650}.activity-copy small{color:#949ba4;font-size:10px}.presence-emoji{width:18px;height:18px;object-fit:contain;vertical-align:middle}.is-online{color:var(--sage)}.team-profile-page{max-width:760px;padding-top:42px}.team-back{width:auto;margin:0 0 18px;padding:0;color:var(--muted);border:0;background:transparent}.team-back:hover{color:var(--ink)}.team-profile-shell{overflow:hidden;background:#111214;border:1px solid #292b30;border-radius:16px;box-shadow:0 24px 70px rgba(0,0,0,.36)}.team-profile-banner{position:relative;min-height:210px;background:linear-gradient(135deg,#30343b,#17191d);background-size:cover;background-position:center}.team-profile-banner:after{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.03),rgba(0,0,0,.28));content:"";pointer-events:none}.team-profile-banner>span{position:absolute;right:17px;bottom:14px;z-index:1;padding:5px 8px;color:#f2f3f5;background:rgba(0,0,0,.48);border:1px solid rgba(255,255,255,.12);border-radius:5px;font:8px "Space Mono",monospace;letter-spacing:.12em}.team-profile-card{position:relative;padding:0 28px 0;color:#f2f3f5;background:#111214;border:0;border-radius:0;box-shadow:none;text-align:left}.team-profile-header{display:flex;align-items:flex-end;justify-content:space-between;min-height:54px;margin-bottom:10px}.team-profile-avatar{width:100px;height:100px;margin:-48px 0 0 2px;border:7px solid #111214;font-size:32px;transform:none}.team-profile-card .team-profile-avatar-status-wrap{width:100px;height:100px;margin:-50px 0 0 0;transform:none}.team-profile-card .team-profile-avatar-status-wrap>.team-profile-avatar{margin:0;transform:none}.team-profile-card .discord-status-icon{right:4px;bottom:4px;width:25px;height:25px;border:4px solid #111214;background:#111214}.team-profile-identity{padding:2px 0 19px}.team-profile-role{display:flex;align-items:center;gap:8px;color:#b7bac2;font:700 9px "Space Mono",monospace;letter-spacing:.1em;text-transform:uppercase}.team-profile-role i{padding:3px 5px;color:#c7cbd2;background:#24262b;border-radius:3px;font:700 8px "Space Mono",monospace;font-style:normal;letter-spacing:.05em}.team-profile-identity h1{margin:8px 0 2px;color:#f2f3f5;font-size:29px;line-height:1.15;letter-spacing:-.055em}.team-profile-handle{margin:0;color:#949ba4;font-size:12px}.team-profile-divider{height:1px;background:#292b30}.team-profile-section{padding:20px 0 18px;border-bottom:1px solid #292b30}.team-profile-section h2{margin:0 0 10px;color:#b5bac1;font:700 10px "Space Mono",monospace;letter-spacing:.1em;text-transform:uppercase}.team-activity-section{padding-bottom:20px}.team-profile-bio{max-width:620px;margin:0;color:#dbdee3;font-size:12px;line-height:1.75;white-space:pre-wrap;overflow-wrap:anywhere}.team-profile-links{display:flex;justify-content:flex-start;flex-wrap:wrap;gap:8px;margin:0}.team-profile-links a{display:inline-flex;align-items:center;gap:7px;padding:8px 11px;color:#e3e5e8;background:#1b1d21;border:1px solid #303238;border-radius:6px;font-size:10px;font-weight:650;transition:background .18s,border-color .18s,transform .18s}.team-profile-links a:hover{background:#25272d;border-color:#555963;transform:translateY(-1px)}.team-profile-social-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:9px}.team-profile-link-card{display:flex;align-items:center;justify-content:space-between;gap:10px;min-width:0;padding:11px 13px;color:#c9ccd2;background:#191b1f;border:1px solid #2c2f35;border-radius:9px;font-size:10px;font-weight:650;transition:background .18s ease,border-color .18s ease,transform .18s ease}.team-profile-link-card:hover,.team-profile-social-card:hover{transform:translateY(-1px);background:#202227;border-color:#454a53;text-decoration:none}.team-profile-link-card>span:last-child{color:#969da7}.team-profile-social-card{position:relative;display:flex;align-items:center;gap:11px;min-width:0;min-height:82px;padding:11px 35px 11px 12px;color:#e3e5e8;background:#191b1f;border:1px solid #2c2f35;border-radius:9px;transition:background .18s ease,border-color .18s ease,transform .18s ease}.platform-mark{width:1em;height:1em;flex:0 0 auto;fill:currentColor}.platform-github{color:#c3cad3}.platform-bluesky{color:#5aa9ff}.platform-twitch{color:#a970ff}.platform-youtube{color:#ff6060}.platform-reddit{color:#ff7034}.platform-x{color:#cfd3d8}.social-card-chip{position:absolute;top:9px;right:11px;display:inline-flex;align-items:center;gap:5px;font:700 8px "Space Mono",monospace;letter-spacing:.09em;text-transform:uppercase}.link-card-chip{display:inline-flex;align-items:center;gap:6px;font:700 9px "Space Mono",monospace;letter-spacing:.08em;text-transform:uppercase}.social-profile-card{padding:24px 13px 12px 12px}.social-card-avatar{display:grid;place-items:center;width:42px;height:42px;flex:0 0 auto;overflow:hidden;color:#8f96a1;background:#25272d;border:1px solid #41454d;border-radius:50%;font-size:19px}.social-card-avatar img{width:100%;height:100%;object-fit:cover}.social-card-details{display:grid;flex:1;min-width:0;gap:2px}.social-card-details>strong,.social-card-details>small,.social-card-bio,.social-card-status{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.social-card-details>strong{font-size:11px}.social-card-details>small{color:#9299a3;font-size:9px}.social-card-bio{color:#c2c6ce;font-size:9px}.social-card-status{color:#7ecf9b;font-size:9px;font-weight:650}.social-card-stats{display:flex;flex:0 0 auto;gap:10px}.social-card-stats>span{display:grid;justify-items:center;gap:2px}.social-card-stats strong{color:#dfe2e7;font-size:10px}.social-card-stats small{color:#858c96;font-size:8px}.profile-custom-status.profile-spotify-status{flex-wrap:wrap;row-gap:9px}.profile-spotify-status .profile-custom-status-copy{flex:1}.profile-spotify-status .profile-custom-status-emoji{overflow:hidden}.profile-spotify-status .profile-custom-status-emoji>img{width:100%;height:100%;object-fit:cover;border-radius:7px}.profile-spotify-artist{overflow-wrap:anywhere;color:#b7bcc4;font-size:10px}.profile-status-progress{display:grid;flex:0 0 100%;gap:5px}.profile-status-track{position:relative;display:block;height:4px;overflow:hidden;background:#2b2e34;border-radius:999px}.profile-status-track>i{position:absolute;top:0;bottom:0;left:0;background:#1db954;border-radius:999px;transition:width .95s linear}.profile-status-times{display:flex;justify-content:space-between;color:#858c96;font:8px "Space Mono",monospace}.team-activity-content{display:block;width:100%;margin:0;padding:0;color:#c9ccd2;font-size:10px;text-align:left}.team-activity-content .presence-line{margin-top:0}.team-activity-content .activity-card{height:100%;width:100%}.team-activity-empty{padding:12px 14px;color:#aeb4bd;background:#181a1e;border:1px solid #303238;border-radius:9px;font-size:11px;line-height:1.5}.team-profile-footer{display:flex;justify-content:space-between;gap:12px;padding:12px 0;color:#737982;font:8px "Space Mono",monospace;letter-spacing:.1em}.team-profile-footer span:last-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}@media(max-width:800px){.team-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.team-grid{grid-template-columns:1fr;margin-top:38px}.team-application-cta{align-items:center;flex-direction:row;margin-top:30px}.team-application-cta p{display:none}.team-profile-page{padding-top:24px;padding-bottom:55px}.team-profile-banner{min-height:155px}.team-profile-card{padding-right:18px;padding-left:18px}.team-profile-header{min-height:48px}.team-profile-avatar,.team-profile-card .team-profile-avatar-status-wrap{width:88px;height:88px}.team-profile-card .team-profile-avatar-status-wrap{margin-top:-43px}.team-profile-card .discord-status-icon{width:23px;height:23px}.team-profile-identity h1{font-size:25px}.team-profile-section{padding:17px 0}.team-profile-footer{font-size:7px}.team-profile-social-grid{grid-template-columns:1fr}.team-profile-social-card{gap:9px;padding-left:10px}.social-card-stats{gap:7px}.social-card-avatar{width:36px;height:36px}}}`;

const PRESENCE_REFRESH_INTERVAL = 5000;

export function TeamPage() {
  const [members, setMembers] = useState<StaffMember[]>([]);
  useEffect(() => {
    let active = true;
    const refresh = () => {
      getTeam()
        .then((nextMembers) => {
          if (active) setMembers(nextMembers);
        })
        .catch(() => {
          // Keep the last known presence visible through a transient poll failure.
        });
    };
    const handleVisibility = () => {
      if (document.visibilityState === "visible") refresh();
    };

    refresh();
    const interval = window.setInterval(() => {
      if (document.visibilityState === "visible") refresh();
    }, PRESENCE_REFRESH_INTERVAL);
    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      active = false;
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, []);
  return <><style>{teamStyles}</style><PublicHeader page="team" /><main className="shell page-main">
    <PublicPageIntro
      eyebrow="The people behind Niko"
      title={<>Meet the <em>team.</em></>}
      description="A small group of builders, moderators, and creative minds keeping Niko friendly, useful, and moving forward."
    />
    <div className="team-grid">{members.map((member) => <button className="team-card" key={member.id} onClick={() => navigate(`/team/${member.id}`)}>
      <div className="team-card-art" style={member.public_banner_url ? { backgroundImage: `url(${member.public_banner_url})` } : undefined} />
      <div className="team-card-body"><StatusAvatar member={member} className="team-avatar" /><div><span className="team-role">{member.role_label}</span><h2>{member.name}</h2><p>{member.bio || "Part of the Niko team."}</p></div></div>
      <span className="team-card-footer"><span>View profile</span><span aria-hidden="true">↗</span></span>
    </button>)}{!members.length && <div className="empty-state">The team roster is being prepared.</div>}</div>
    <section className="team-application-cta"><span className="panel-kicker">Niko recruitment</span><p>Interested in contributing to the team?</p><a href="/team/apply">View open staff roles <span aria-hidden="true">→</span></a></section>
  </main><Footer /></>;
}

export function TeamMemberPage({ id }: { id: string }) {
  const [member, setMember] = useState<StaffMember | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    const refresh = (initial = false) => {
      getTeamMember(id)
        .then((nextMember) => {
          if (active) {
            setMember(nextMember);
            setError("");
          }
        })
        .catch((reason) => {
          if (active && initial) setError(reason instanceof Error ? reason.message : "Team member not found.");
        });
    };
    const handleVisibility = () => {
      if (document.visibilityState === "visible") refresh();
    };

    refresh(true);
    const interval = window.setInterval(() => {
      if (document.visibilityState === "visible") refresh();
    }, PRESENCE_REFRESH_INTERVAL);
    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      active = false;
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [id]);
  return <><style>{teamStyles}</style><PublicHeader page="team" /><main className="shell page-main team-profile-page">{error ? <div className="empty-state">{error}</div> : !member ? <div className="section-loading">Loading profile…</div> : <>
    <button className="back-link team-back" onClick={() => navigate("/team")}>← Back to team</button>
    <section className="team-profile-shell">
      <div className="team-profile-banner" style={member.public_banner_url ? { backgroundImage: `url(${member.public_banner_url})` } : undefined}><span>TEAM MEMBER</span></div>
      <div className="team-profile-card">
        <div className="team-profile-header">
          <StatusAvatar member={member} className="team-profile-avatar" />
        </div>
        <div className="team-profile-identity">
          <span className="team-profile-role">{member.role_label}<i>STAFF</i></span>
          <h1>{member.name}</h1>
          <p className="team-profile-handle">{member.username ? `@${member.username}` : "Niko staff"}</p>
        </div>
        <div className="team-profile-divider" />
        <section className="team-profile-section"><h2>About me</h2><p className="team-profile-bio">{member.bio || "This team member has not added an extended introduction yet."}</p></section>
        <section className="team-profile-section team-activity-section"><h2>Current activity</h2><div className="team-activity-content">{member.custom_status?.text || member.custom_status?.emoji || (member.activities || []).length ? <PresenceSummary member={member} /> : <div className="team-activity-empty">No current activity.</div>}</div></section>
        {(member.public_links || []).length > 0 && <section className="team-profile-section"><h2>Find me elsewhere</h2><div className="team-profile-social-grid" aria-label={`${member.name}'s social profiles`}>
          {(member.public_links || []).map((link, index) => <ProfileLinkCard link={link} key={`${link.type}-${index}`} />)}
        </div></section>}
        <footer className="team-profile-footer"><span>NIKO COMMUNITY</span><span>PROFILE · {member.id}</span></footer>
      </div>
    </section>
  </>}</main><Footer /></>;
}
