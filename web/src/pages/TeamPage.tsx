import { useEffect, useState } from "react";
import { getTeam, getTeamMember } from "../api";
import { PublicHeader } from "../components/PublicHeader";
import { PublicPageIntro } from "../components/PublicPageIntro";
import { Footer } from "../components/Footer";
import { DiscordStatusAvatar } from "../components/DiscordStatusAvatar";
import { navigate } from "../router";
import type { StaffEmoji, StaffMember } from "../types";

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

function ActivitySummary({ activity }: { activity: NonNullable<StaffMember["activities"]>[number] }) {
  const isSpotify = activity.kind === "spotify";
  const title = isSpotify ? "Listening on Spotify" : activityLabel(activity.type);
  const primary = isSpotify ? (activity.details || "Spotify") : activity.name;
  const secondaryLines = (isSpotify ? [activity.state] : [activity.details, activity.state])
    .filter((line): line is string => Boolean(line && line !== primary));
  const card = <span className={`activity-card activity-${activity.kind}`}>
    {activity.image_url && <img className="activity-art" src={activity.image_url} alt="" />}
    <span className="activity-copy"><strong>{title}</strong><span>{primary}</span>{secondaryLines.map((line, index) => <small key={`${line}-${index}`}>{line}</small>)}</span>
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

type GithubProfile = {
  login: string;
  name: string | null;
  avatar_url: string;
  html_url: string;
  bio: string | null;
  location: string | null;
  public_repos: number;
  followers: number;
};

function getGithubUsername(url: string) {
  try {
    const parsed = new URL(url);
    if (parsed.hostname !== "github.com" && parsed.hostname !== "www.github.com") return null;
    const username = parsed.pathname.split("/").filter(Boolean)[0] || "";
    return /^[a-zA-Z0-9-]{1,39}$/.test(username) ? username : null;
  } catch {
    return null;
  }
}

function GithubProfileCard({ link }: { link: NonNullable<StaffMember["public_links"]>[number] }) {
  const username = getGithubUsername(link.url);
  const [profile, setProfile] = useState<GithubProfile | null>(null);
  const [loading, setLoading] = useState(Boolean(username));
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    if (!username) return;
    const controller = new AbortController();
    setLoading(true);
    setUnavailable(false);
    fetch(`https://api.github.com/users/${encodeURIComponent(username)}`, {
      headers: { Accept: "application/vnd.github+json" },
      signal: controller.signal,
    }).then((response) => {
      if (!response.ok) throw new Error("GitHub profile unavailable");
      return response.json() as Promise<GithubProfile>;
    }).then(setProfile).catch(() => {
      if (!controller.signal.aborted) setUnavailable(true);
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [username]);

  if (!username || unavailable) return <a className="team-profile-link-card team-profile-link-fallback" href={link.url} target="_blank" rel="noopener noreferrer"><span>{link.label || "GitHub"}</span><span aria-hidden="true">↗</span></a>;
  if (loading || !profile) return <a className="team-profile-social-card github-profile-card is-loading" href={link.url} target="_blank" rel="noopener noreferrer" aria-label={`Loading ${username}'s GitHub profile`}><span className="github-profile-skeleton" /><span className="github-profile-loading">Loading GitHub profile…</span></a>;

  return <a className="team-profile-social-card github-profile-card" href={profile.html_url} target="_blank" rel="noopener noreferrer">
    <img className="github-profile-avatar" src={profile.avatar_url} alt="" />
    <span className="github-profile-details"><strong>{profile.name || profile.login}</strong><small>@{profile.login}</small>{profile.bio && <span className="github-profile-bio">{profile.bio}</span>}{profile.location && <small className="github-profile-location">{profile.location}</small>}</span>
    <span className="github-profile-stats"><span><strong>{profile.public_repos.toLocaleString()}</strong><small>repos</small></span><span><strong>{profile.followers.toLocaleString()}</strong><small>followers</small></span></span>
    <span className="github-profile-open" aria-hidden="true">↗</span>
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
.team-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));align-items:start;gap:14px;margin-top:58px}.team-application-cta{display:flex;align-items:center;justify-content:space-between;gap:12px;width:min(100%,480px);margin:44px auto 0;padding:10px 13px;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:8px}.team-application-cta .panel-kicker{color:var(--dim);font-size:8px;white-space:nowrap}.team-application-cta p{flex:1;margin:0;font-size:10px}.team-application-cta>a{color:var(--accent-dark);font-size:10px;font-weight:700;white-space:nowrap}.team-application-cta>a:hover{color:var(--ink);text-decoration:none}.team-card{display:flex;flex-direction:column;min-width:0;overflow:hidden;padding:0;color:var(--ink);text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow-soft)}.team-card:hover{border-color:#dfaa98;transform:translateY(-2px)}.team-card:focus-visible{outline:2px solid var(--accent-dark);outline-offset:3px}.team-card-art,.team-profile-banner{min-height:105px;background:linear-gradient(135deg,var(--callout),var(--surface-muted));background-size:cover;background-position:center}.team-card-body{display:flex;align-items:flex-start;flex:1;min-width:0;gap:14px;padding:18px}.team-card-body>div:last-child{min-width:0}.team-card h2,.team-card p{overflow-wrap:anywhere}.team-avatar,.team-profile-avatar{display:grid;place-items:center;flex:0 0 auto;overflow:hidden;color:#fffaf5;background:var(--accent);border-radius:50%;font-weight:800;object-fit:cover}.team-avatar{width:56px;height:56px;margin-top:-39px;border:3px solid var(--surface)}.team-role{color:var(--accent-dark);text-transform:uppercase;letter-spacing:.1em;font:700 9px "Space Mono",monospace}.team-card h2{margin:5px 0 6px;font-size:17px}.team-card p{margin:0 0 10px;color:var(--muted);font-size:11px;line-height:1.6}.team-card-footer{display:flex;align-items:center;justify-content:space-between;padding:5px 17px 8px;color:#858c96;background:transparent;border:0;font:8px "Space Mono",monospace;letter-spacing:.03em;text-transform:uppercase;transition:color .18s ease}.team-card-footer>span:last-child{color:#858c96;font-size:12px;transition:transform .18s ease}.team-card:hover .team-card-footer{color:#b4bac3;background:transparent}.team-card:hover .team-card-footer>span:last-child{color:#b4bac3}.team-card:hover .team-card-footer>span:last-child{transform:translate(2px,-2px)}.team-status{color:var(--dim);font-size:10px}.presence-stack{display:grid;gap:10px}.profile-custom-status{display:flex;align-items:center;gap:11px;min-width:0;padding:11px 12px;background:#1b1d21;border:1px solid #303238;border-radius:9px}.profile-custom-status-emoji{display:grid;place-items:center;width:36px;height:36px;flex:0 0 auto;background:#25272d;border-radius:8px}.profile-custom-status-emoji:empty{display:none}.profile-custom-status-emoji .presence-emoji{width:21px;height:21px}.profile-custom-status-copy{display:grid;min-width:0;gap:3px}.profile-custom-status-copy small{color:#858c96;font:8px "Space Mono",monospace;letter-spacing:.1em;text-transform:uppercase}.profile-custom-status-copy>span{overflow-wrap:anywhere;color:#e3e5e8;font-size:11px;line-height:1.5}.presence-activity-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:8px}.presence-activity{display:block;min-width:0;color:inherit}.presence-activity:hover{text-decoration:none}.activity-card{display:flex;align-items:center;min-width:0;min-height:62px;gap:11px;padding:9px 11px;background:#1b1d21;border:1px solid #303238;border-radius:9px;text-align:left;transition:background .18s ease,border-color .18s ease,transform .18s ease}.presence-activity[href]:hover .activity-card{transform:translateY(-1px);background:#222429;border-color:#484c55}.activity-art{width:42px;height:42px;flex:0 0 auto;border-radius:7px;object-fit:cover}.activity-copy{display:flex;min-width:0;flex-direction:column;gap:3px}.activity-copy strong{color:#9da5b1;font-size:8px;text-transform:uppercase;letter-spacing:.08em}.activity-copy span,.activity-copy small{overflow:hidden;max-width:100%;text-overflow:ellipsis;white-space:nowrap}.activity-copy span{color:#f2f3f5;font-size:11px;font-weight:650}.activity-copy small{color:#949ba4;font-size:10px}.presence-emoji{width:18px;height:18px;object-fit:contain;vertical-align:middle}.is-online{color:var(--sage)}.team-profile-page{max-width:760px;padding-top:42px}.team-back{width:auto;margin:0 0 18px;padding:0;color:var(--muted);border:0;background:transparent}.team-back:hover{color:var(--ink)}.team-profile-shell{overflow:hidden;background:#111214;border:1px solid #292b30;border-radius:16px;box-shadow:0 24px 70px rgba(0,0,0,.36)}.team-profile-banner{position:relative;min-height:210px;background:linear-gradient(135deg,#30343b,#17191d);background-size:cover;background-position:center}.team-profile-banner:after{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.03),rgba(0,0,0,.28));content:"";pointer-events:none}.team-profile-banner>span{position:absolute;right:17px;bottom:14px;z-index:1;padding:5px 8px;color:#f2f3f5;background:rgba(0,0,0,.48);border:1px solid rgba(255,255,255,.12);border-radius:5px;font:8px "Space Mono",monospace;letter-spacing:.12em}.team-profile-card{position:relative;padding:0 28px 0;color:#f2f3f5;background:#111214;border:0;border-radius:0;box-shadow:none;text-align:left}.team-profile-header{display:flex;align-items:flex-end;justify-content:space-between;min-height:54px;margin-bottom:10px}.team-profile-avatar{width:100px;height:100px;margin:-48px 0 0 2px;border:7px solid #111214;font-size:32px;transform:none}.team-profile-card .team-profile-avatar-status-wrap{width:100px;height:100px;margin:-50px 0 0 0;transform:none}.team-profile-card .team-profile-avatar-status-wrap>.team-profile-avatar{margin:0;transform:none}.team-profile-card .discord-status-icon{right:4px;bottom:4px;width:25px;height:25px;border:4px solid #111214;background:#111214}.team-profile-identity{padding:2px 0 19px}.team-profile-role{display:flex;align-items:center;gap:8px;color:#b7bac2;font:700 9px "Space Mono",monospace;letter-spacing:.1em;text-transform:uppercase}.team-profile-role i{padding:3px 5px;color:#c7cbd2;background:#24262b;border-radius:3px;font:700 8px "Space Mono",monospace;font-style:normal;letter-spacing:.05em}.team-profile-identity h1{margin:8px 0 2px;color:#f2f3f5;font-size:29px;line-height:1.15;letter-spacing:-.055em}.team-profile-handle{margin:0;color:#949ba4;font-size:12px}.team-profile-divider{height:1px;background:#292b30}.team-profile-section{padding:20px 0 18px;border-bottom:1px solid #292b30}.team-profile-section h2{margin:0 0 10px;color:#b5bac1;font:700 10px "Space Mono",monospace;letter-spacing:.1em;text-transform:uppercase}.team-activity-section{padding-bottom:20px}.team-profile-bio{max-width:620px;margin:0;color:#dbdee3;font-size:12px;line-height:1.75;white-space:pre-wrap;overflow-wrap:anywhere}.team-profile-links{display:flex;justify-content:flex-start;flex-wrap:wrap;gap:8px;margin:0}.team-profile-links a{display:inline-flex;align-items:center;gap:7px;padding:8px 11px;color:#e3e5e8;background:#1b1d21;border:1px solid #303238;border-radius:6px;font-size:10px;font-weight:650;transition:background .18s,border-color .18s,transform .18s}.team-profile-links a:hover{background:#25272d;border-color:#555963;transform:translateY(-1px)}.team-profile-social-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:9px}.team-profile-link-card{display:flex;align-items:center;justify-content:space-between;gap:10px;min-width:0;padding:11px 13px;color:#c9ccd2;background:#191b1f;border:1px solid #2c2f35;border-radius:9px;font-size:10px;font-weight:650;transition:background .18s ease,border-color .18s ease,transform .18s ease}.team-profile-link-card:hover,.team-profile-social-card:hover{transform:translateY(-1px);background:#202227;border-color:#454a53;text-decoration:none}.team-profile-link-card>span:last-child{color:#969da7}.team-profile-social-card{position:relative;display:flex;align-items:center;gap:11px;min-width:0;min-height:82px;padding:11px 35px 11px 12px;color:#e3e5e8;background:#191b1f;border:1px solid #2c2f35;border-radius:9px;transition:background .18s ease,border-color .18s ease,transform .18s ease}.github-profile-avatar{width:42px;height:42px;flex:0 0 auto;border:1px solid #41454d;border-radius:50%;object-fit:cover;background:#25272d}.github-profile-details{display:grid;flex:1;min-width:0;gap:2px}.github-profile-details>strong,.github-profile-details>small,.github-profile-bio{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.github-profile-details>strong{font-size:11px}.github-profile-details>small{color:#9299a3;font-size:9px}.github-profile-bio{color:#c2c6ce;font-size:9px}.github-profile-location{color:#858c96!important}.github-profile-stats{display:flex;flex:0 0 auto;gap:10px}.github-profile-stats>span{display:grid;justify-items:center;gap:2px}.github-profile-stats strong{color:#dfe2e7;font-size:10px}.github-profile-stats small{color:#858c96;font-size:8px}.github-profile-open{position:absolute;top:10px;right:11px;color:#9299a3;font-size:12px}.github-profile-card.is-loading{min-height:66px}.github-profile-skeleton{width:36px;height:36px;flex:0 0 auto;border-radius:50%;background:#282b31;animation:profile-skeleton-pulse 1.2s ease-in-out infinite alternate}.github-profile-loading{color:#9299a3;font-size:10px}@keyframes profile-skeleton-pulse{to{opacity:.45}}.team-activity-content{display:block;width:100%;margin:0;padding:0;color:#c9ccd2;font-size:10px;text-align:left}.team-activity-content .presence-line{margin-top:0}.team-activity-content .activity-card{height:100%;width:100%}.team-activity-empty{padding:12px 14px;color:#aeb4bd;background:#181a1e;border:1px solid #303238;border-radius:9px;font-size:11px;line-height:1.5}.team-profile-footer{display:flex;justify-content:space-between;gap:12px;padding:12px 0;color:#737982;font:8px "Space Mono",monospace;letter-spacing:.1em}.team-profile-footer span:last-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}@media(max-width:800px){.team-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.team-grid{grid-template-columns:1fr;margin-top:38px}.team-application-cta{align-items:center;flex-direction:row;margin-top:30px}.team-application-cta p{display:none}.team-profile-page{padding-top:24px;padding-bottom:55px}.team-profile-banner{min-height:155px}.team-profile-card{padding-right:18px;padding-left:18px}.team-profile-header{min-height:48px}.team-profile-avatar,.team-profile-card .team-profile-avatar-status-wrap{width:88px;height:88px}.team-profile-card .team-profile-avatar-status-wrap{margin-top:-43px}.team-profile-card .discord-status-icon{width:23px;height:23px}.team-profile-identity h1{font-size:25px}.team-profile-section{padding:17px 0}.team-profile-footer{font-size:7px}.team-profile-social-grid{grid-template-columns:1fr}.team-profile-social-card{gap:9px;padding-left:10px}.github-profile-stats{gap:7px}.github-profile-avatar{width:36px;height:36px}}}`;

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
          {(member.public_links || []).map((link, index) => link.type.toLowerCase() === "github" ? <GithubProfileCard link={link} key={`${link.type}-${index}`} /> : <a className="team-profile-link-card" href={link.url} target="_blank" rel="noopener noreferrer" key={`${link.type}-${index}`}>{link.label || link.type}<span aria-hidden="true">↗</span></a>)}
        </div></section>}
        <footer className="team-profile-footer"><span>NIKO COMMUNITY</span><span>PROFILE · {member.id}</span></footer>
      </div>
    </section>
  </>}</main><Footer /></>;
}
