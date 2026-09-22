import { useEffect, useState } from "react";
import { getTeam, getTeamMember } from "../api";
import { PublicHeader } from "../components/PublicHeader";
import { Footer } from "../components/Footer";
import { navigate } from "../router";
import type { StaffEmoji, StaffMember } from "../types";

function avatar(member: StaffMember) {
  return member.avatar_url;
}

function twemojiUrl(value: string) {
  const codepoints = Array.from(value).map((character) => character.codePointAt(0)!.toString(16)).join("-");
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
  const secondary = isSpotify ? activity.state : activity.details;
  const card = <span className={`activity-card activity-${activity.kind}`}>
    {activity.image_url && <img className="activity-art" src={activity.image_url} alt="" />}
    <span className="activity-copy"><strong>{title}</strong><span>{primary}</span>{secondary && <small>{secondary}</small>}</span>
  </span>;
  return activity.url ? <a className="presence-activity" href={activity.url} target="_blank" rel="noreferrer">{card}</a> : <span className="presence-activity">{card}</span>;
}

function statusLabel(member: StaffMember) {
  return member.status_label || ({ online: "Online", idle: "Idle", dnd: "Do Not Disturb", offline: "Offline" }[member.status || "offline"] || "Offline");
}

function PresenceSummary({ member }: { member: StaffMember }) {
  const custom = member.custom_status;
  const activities = member.activities || [];
  const hasCustom = Boolean(custom?.text || custom?.emoji);
  if (!hasCustom && !activities.length) return null;
  return <span className="presence-stack">
    {hasCustom && <span className="presence-line"><ActivityEmoji emoji={custom?.emoji} />{custom?.text || "Custom status"}</span>}
    {activities.length > 0 && <span className="presence-line activity-list">{activities.map((activity, index) => <ActivitySummary activity={activity} key={`${activity.kind}-${activity.name}-${index}`} />)}</span>}
  </span>;
}

const teamStyles = `
.team-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:58px}.team-card{display:flex;flex-direction:column;min-width:0;min-height:286px;overflow:hidden;padding:0;color:var(--ink);text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow-soft)}.team-card:hover{border-color:#dfaa98;transform:translateY(-2px)}.team-card-art,.team-profile-banner{min-height:105px;background:linear-gradient(135deg,var(--callout),var(--surface-muted));background-size:cover;background-position:center}.team-card-body{display:flex;align-items:flex-start;flex:1;min-width:0;gap:14px;padding:18px}.team-card-body>div:last-child{min-width:0}.team-card h2,.team-card p{overflow-wrap:anywhere}.team-avatar,.team-profile-avatar{display:grid;place-items:center;flex:0 0 auto;overflow:hidden;color:#fffaf5;background:var(--accent);border-radius:50%;font-weight:800;object-fit:cover}.team-avatar{width:48px;height:48px;margin-top:-35px;border:3px solid var(--surface)}.team-role{color:var(--accent-dark);text-transform:uppercase;letter-spacing:.1em;font:700 9px "Space Mono",monospace}.team-card h2{margin:5px 0 6px;font-size:17px}.team-card p{margin:0 0 10px;color:var(--muted);font-size:11px;line-height:1.6}.team-status{color:var(--dim);font-size:10px}.presence-stack{display:block}.presence-line{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin-top:7px;color:var(--muted);font-size:10px}.presence-activity{display:inline-flex;align-items:center;gap:4px;color:inherit}.presence-activity:hover{text-decoration:none}.activity-card{display:flex;align-items:center;min-width:0;gap:8px;padding:7px 9px;background:var(--surface-muted);border:1px solid var(--line);border-radius:8px;text-align:left}.activity-art{width:30px;height:30px;flex:0 0 auto;border-radius:5px;object-fit:cover}.activity-copy{display:flex;min-width:0;flex-direction:column;gap:1px}.activity-copy strong{color:var(--accent-dark);font-size:9px;text-transform:uppercase;letter-spacing:.06em}.activity-copy span,.activity-copy small{overflow:hidden;max-width:210px;text-overflow:ellipsis;white-space:nowrap}.activity-copy span{color:var(--ink);font-size:10px}.activity-copy small{color:var(--dim);font-size:9px}.presence-emoji{width:18px;height:18px;object-fit:contain;vertical-align:middle}.is-online{color:var(--sage)}.team-profile-page{max-width:760px}.team-back{width:auto;margin:0 0 18px;border:0;background:transparent}.team-profile-banner{min-height:220px;border:1px solid var(--line);border-radius:14px 14px 0 0}.team-profile-card{padding:0 34px 38px;text-align:center;background:var(--surface);border:1px solid var(--line);border-top:0;border-radius:0 0 14px 14px;box-shadow:var(--shadow-soft)}.team-profile-avatar{width:100px;height:100px;margin:-50px auto 18px;border:5px solid var(--surface);font-size:32px}.team-profile-card h1{margin:8px 0 5px;font-size:34px;letter-spacing:-.07em}.team-profile-handle{color:var(--dim);font-size:11px}.team-profile-bio{max-width:560px;margin:27px auto 0;color:var(--muted);line-height:1.8}.team-activity{display:block;width:min(100%,560px);margin:20px auto 0;padding:12px;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line);border-radius:12px;font-size:10px;text-align:left}.team-activity .presence-line{margin-top:0}.team-activity .activity-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));align-items:stretch}.team-activity .activity-card{height:100%;width:100%}@media(max-width:800px){.team-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.team-grid{grid-template-columns:1fr;margin-top:38px}.team-profile-card{padding-left:18px;padding-right:18px}.team-profile-banner{min-height:150px}}`;

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
    <div className="page-heading"><div className="eyebrow">The people behind Niko</div><h1>Meet the team.</h1><p>A small group of builders, moderators, and creative minds keeping Niko friendly, useful, and moving forward.</p></div>
    <div className="team-grid">{members.map((member) => <button className="team-card" key={member.id} onClick={() => navigate(`/team/${member.id}`)}>
      <div className="team-card-art" style={member.public_banner_url ? { backgroundImage: `url(${member.public_banner_url})` } : undefined} />
      <div className="team-card-body">{avatar(member) ? <img className="team-avatar" src={avatar(member)!} alt="" /> : <span className="team-avatar team-avatar-fallback">{member.name.slice(0, 1)}</span>}<div><span className="team-role">{member.role_label}</span><h2>{member.name}</h2><p>{member.bio || "Part of the Niko team."}</p><span className={`team-status status-${member.status || "offline"} ${member.status === "online" ? "is-online" : ""}`}>{statusLabel(member)}</span>{<PresenceSummary member={member} />}</div></div>
    </button>)}{!members.length && <div className="empty-state">The team roster is being prepared.</div>}</div>
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
    <div className="team-profile-banner" style={member.public_banner_url ? { backgroundImage: `url(${member.public_banner_url})` } : undefined} />
    <section className="team-profile-card">{avatar(member) ? <img className="team-profile-avatar" src={avatar(member)!} alt="" /> : <span className="team-profile-avatar team-avatar-fallback">{member.name.slice(0, 1)}</span>}<div className="team-role">{member.role_label}</div><h1>{member.name}</h1><p className="team-profile-handle">{member.username ? `@${member.username}` : "Niko staff"} · <span className={`status-${member.status || "offline"} ${member.status === "online" ? "is-online" : ""}`}>{statusLabel(member)}</span></p><p className="team-profile-bio">{member.bio || "This team member has not added an extended introduction yet."}</p><div className="team-activity"><PresenceSummary member={member} />{!member.custom_status && !(member.activities || []).length && "No current activity"}</div></section>
  </>}</main><Footer /></>;
}
