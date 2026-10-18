import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { DiscordBadgeList } from "./DiscordBadgeList";
import { DiscordServerTagPill, type DiscordServerTagInfo } from "./DiscordServerTag";
import { DiscordStatusAvatar } from "./DiscordStatusAvatar";
import { profileBadges } from "../data/profileBadges";
import type { CSSProperties, ReactNode } from "react";
import { resolveDiscordText } from "../api";

export type DiscordMentionNames = Partial<Record<"user" | "channel" | "role", Record<string, string>>>;
type Format = "bold" | "italic" | "italicAlt" | "underline" | "strike" | "spoiler";
type Node =
  | { kind: "text"; text: string }
  | { kind: "code"; text: string }
  | { kind: "link"; text: string; url: string }
  | { kind: "emoji"; name: string; id: string; animated: boolean }
  | { kind: "timestamp"; raw: string; unix: number; style: string }
  | { kind: "mention"; mention: "user" | "channel" | "role" | "everyone"; id: string }
  | { kind: "format"; format: Format; children: Node[] };
type Token = Node | { kind: "marker"; format: Format };

const markerText: Record<Format, string> = { bold: "**", italic: "*", italicAlt: "_", underline: "__", strike: "~~", spoiler: "||" };
const timestampStyles = new Set(["t", "T", "d", "D", "f", "F", "R"]);
// Every marker is a capture group, because the format each one opens is chosen
// by the group that matched: 8 bold (``**``), 9 underline (``__``), 10 italic
// (``*``), 11 italic-alt (``_``), 12 strike (``~~``), 13 spoiler (``||``).
const tokenPattern = /(`[^`\n]+`)|(<t:-?\d+(?::[tTdDfFR])?>)|(<@!?\d+>|<@&\d+>|<#\d+>|@everyone\b|@here\b)|(<a?:[\w~]+:\d+>)|(\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\))|(\*\*)|(__)|((?<!\*)\*(?!\*))|((?<!_)_(?!_))|(~~)|(\|\|)/g;

function timestampLabel(unix: number, style: string): string | null {
  if (!Number.isSafeInteger(unix) || !timestampStyles.has(style)) return null;
  const date = new Date(unix * 1000);
  if (!Number.isFinite(date.getTime())) return null;
  if (style === "R") {
    const seconds = unix - Math.floor(Date.now() / 1000);
    const distance = Math.abs(seconds);
    const unit = distance < 60 ? "second" : distance < 3600 ? "minute" : distance < 86400 ? "hour" : distance < 604800 ? "day" : distance < 2592000 ? "week" : distance < 31536000 ? "month" : "year";
    const divisor = { second: 1, minute: 60, hour: 3600, day: 86400, week: 604800, month: 2592000, year: 31536000 }[unit];
    return new Intl.RelativeTimeFormat(undefined, { numeric: "always" }).format(Math.round(seconds / divisor), unit);
  }
  const options: Intl.DateTimeFormatOptions = style === "t" || style === "T"
    ? { hour: "numeric", minute: "2-digit", ...(style === "T" ? { second: "2-digit" } : {}) }
    : style === "d" ? { year: "numeric", month: "2-digit", day: "2-digit" }
      : style === "D" ? { year: "numeric", month: "long", day: "numeric" }
        : style === "F" ? { weekday: "long", year: "numeric", month: "long", day: "numeric", hour: "numeric", minute: "2-digit" }
          : { year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" };
  return new Intl.DateTimeFormat(undefined, options).format(date);
}

function tokenize(text: string): Node[] {
  const tokens: Token[] = [];
  let cursor = 0;
  const appendPlain = (value: string) => {
    const urls = /(https?:\/\/[^\s<>)]+)/g;
    let from = 0;
    let match: RegExpExecArray | null;
    while ((match = urls.exec(value))) {
      if (match.index > from) tokens.push({ kind: "text", text: value.slice(from, match.index) });
      tokens.push({ kind: "link", text: match[0], url: match[0] });
      from = urls.lastIndex;
    }
    if (from < value.length) tokens.push({ kind: "text", text: value.slice(from) });
  };

  tokenPattern.lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = tokenPattern.exec(text))) {
    if (match.index > cursor) appendPlain(text.slice(cursor, match.index));
    const raw = match[0];
    if (match[1]) tokens.push({ kind: "code", text: raw.slice(1, -1) });
    else if (match[2]) {
      const parts = raw.match(/^<t:(-?\d+)(?::([tTdDfFR]))?>$/)!;
      tokens.push({ kind: "timestamp", raw, unix: Number(parts[1]), style: parts[2] || "f" });
    } else if (match[3]) {
      const user = raw.match(/^<@!?([0-9]+)>$/);
      const role = raw.match(/^<@&([0-9]+)>$/);
      const channel = raw.match(/^<#([0-9]+)>$/);
      tokens.push(user ? { kind: "mention", mention: "user", id: user[1] }
        : role ? { kind: "mention", mention: "role", id: role[1] }
          : channel ? { kind: "mention", mention: "channel", id: channel[1] }
            : { kind: "mention", mention: "everyone", id: raw });
    } else if (match[4]) {
      const [, animated, name, id] = raw.match(/^<(a?):([\w~]+):(\d+)>$/)!;
      tokens.push({ kind: "emoji", animated: animated === "a", name, id });
    } else if (match[5]) tokens.push({ kind: "link", text: match[6], url: match[7] });
    else if (match[8]) tokens.push({ kind: "marker", format: "bold" });
    else if (match[9]) tokens.push({ kind: "marker", format: "underline" });
    else if (match[10]) tokens.push({ kind: "marker", format: "italic" });
    else if (match[11]) tokens.push({ kind: "marker", format: "italicAlt" });
    else if (match[12]) tokens.push({ kind: "marker", format: "strike" });
    else if (match[13]) tokens.push({ kind: "marker", format: "spoiler" });
    cursor = tokenPattern.lastIndex;
  }
  if (cursor < text.length) appendPlain(text.slice(cursor));

  const roots: Node[] = [];
  const stack: { format: Format; children: Node[] }[] = [];
  const append = (node: Node) => (stack.length ? stack[stack.length - 1].children : roots).push(node);
  for (const token of tokens) {
    if (token.kind !== "marker") { append(token); continue; }
    const open = stack.findIndex((frame) => frame.format === token.format);
    if (open < 0) stack.push({ format: token.format, children: [] });
    else {
      const closed = stack.splice(open);
      const formatted: Node[] = [...closed[0].children];
      for (const frame of closed.slice(1)) formatted.push({ kind: "text", text: markerText[frame.format] }, ...frame.children);
      append({ kind: "format", format: token.format, children: formatted });
    }
  }
  while (stack.length) {
    const frame = stack.pop()!;
    const parent = stack.length ? stack[stack.length - 1].children : roots;
    parent.push({ kind: "text", text: markerText[frame.format] }, ...frame.children);
  }
  return roots;
}

/**
 * A Discord custom emoji.
 *
 * Discord never draws a broken emoji: when it cannot resolve one — a deleted
 * emoji, an emoji from another server, a stale id — it writes the name out
 * between colons as plain text. The fallback here is the same, which also keeps
 * a failed image from shifting the line or eating the formatting around it.
 */
export function DiscordEmoji({ name, id, animated = false, className }: {
  name: string;
  id: string;
  animated?: boolean;
  className?: string;
}) {
  const [broken, setBroken] = useState(false);
  if (!id || broken) {
    return <span className="discord-emoji-fallback" data-discord-emoji-name={name}>{`:${name}:`}</span>;
  }
  return <img
    className={className}
    data-discord-emoji-name={name}
    src={`https://cdn.discordapp.com/emojis/${id}.${animated ? "gif" : "png"}`}
    alt={`:${name}:`}
    title={`:${name}:`}
    onError={() => setBroken(true)}
  />;
}

function renderInline(nodes: Node[], names?: DiscordMentionNames, prefix = "discord-md", interactiveUsers = true): ReactNode[] {
  return nodes.map((node, index) => {
    const key = `${prefix}-${index}`;
    if (node.kind === "text") return <span key={key}>{node.text}</span>;
    if (node.kind === "code") return <code key={key} className="discord-md-code">{node.text}</code>;
    if (node.kind === "link") return <a key={key} className="discord-md-link" href={node.url} target="_blank" rel="noopener noreferrer">{node.text}</a>;
    if (node.kind === "emoji") return <DiscordEmoji key={key} name={node.name} id={node.id} animated={node.animated} className="discord-md-emoji" />;
    if (node.kind === "timestamp") {
      const label = timestampLabel(node.unix, node.style);
      const date = new Date(node.unix * 1000);
      return label ? <time key={key} className="discord-md-timestamp" dateTime={date.toISOString()} title={node.raw}>{label}</time> : <span key={key}>{node.raw}</span>;
    }
    if (node.kind === "mention") {
      const label = node.mention === "everyone" ? node.id : names?.[node.mention]?.[node.id] || `${node.mention === "channel" ? "#" : "@"}${node.id}`;
      const mentionLabel = node.mention === "user" && !label.startsWith("@") ? `@${label}` : label;
      if (node.mention === "user" && interactiveUsers) {
        return <button key={key} type="button" className={`discord-md-mention discord-md-mention-${node.mention}`} data-discord-user-id={node.id} title={`user · ${node.id}`}>{mentionLabel}</button>;
      }
      return <span key={key} className={`discord-md-mention discord-md-mention-${node.mention}`} title={node.mention === "everyone" ? undefined : `${node.mention} · ${node.id}`}>{mentionLabel}</span>;
    }
    const style: CSSProperties = node.format === "bold" ? { fontWeight: 700 }
      : node.format === "italic" || node.format === "italicAlt" ? { fontStyle: "italic" }
        : node.format === "underline" ? { textDecoration: "underline" }
          : node.format === "strike" ? { textDecoration: "line-through" }
            : { background: "#3f4147", borderRadius: 3 };
    return <span key={key} style={style}>{renderInline(node.children, names, key, interactiveUsers)}</span>;
  });
}

type DiscordCustomStatus = {
  text: string | null;
  emoji_name: string | null;
  emoji_id: string | null;
  emoji_animated: boolean;
};

type DiscordProfileActivity = {
  type: string;
  title: string | null;
  artists: string[];
  album: string | null;
  album_cover_url: string;
  url: string | null;
  start: number | null;
  end: number | null;
  duration_seconds: number | null;
};

type TranscriptProfile = {
  id: string; username: string; display_name: string; avatar_url: string | null;
  banner_url: string | null;  banner_color: string | null; bio: string | null;
  guild_nick: string | null; guild_tag: string | null; guild_badge_url: string | null;
  server_tag?: DiscordServerTagInfo | null;
  status?: string | null;

  avatar_decoration_url: string | null;
  badges?: string[] | null;
  custom_status?: DiscordCustomStatus | null;
  activities?: DiscordProfileActivity[] | null;
};

// Presence lives on the gateway's live member cache and can change while a popup
// is open, so an open popup re-reads its profile on the same 5s cadence the Team
// page uses instead of freezing at the moment it was first opened.
const PROFILE_REFRESH_INTERVAL = 5000;

const PROFILE_STATUS_LABELS: Record<string, string> = {
  online: "Online",
  idle: "Idle",
  dnd: "Do Not Disturb",
  offline: "Offline",
  streaming: "Streaming",
};

/** Discord may report a status enum or a plain string; unknown values are offline. */
function profileStatusKey(status?: string | null) {
  const value = typeof status === "string" ? status.trim().toLowerCase().replace(/^status\./, "") : "";
  return Object.prototype.hasOwnProperty.call(PROFILE_STATUS_LABELS, value) ? value : "offline";
}

function profileStatusLabel(status?: string | null) {
  return PROFILE_STATUS_LABELS[profileStatusKey(status)];
}

async function fetchDiscordProfile(userId: string): Promise<TranscriptProfile> {
  const response = await fetch(`/api/discord/users/${encodeURIComponent(userId)}`);
  if (!response.ok) throw new Error("Could not load this Discord profile.");
  return await response.json() as TranscriptProfile;
}

function statusEmoji(status: DiscordCustomStatus) {
  if (status.emoji_id) {
    return <DiscordEmoji name={status.emoji_name || "emoji"} id={status.emoji_id} animated={status.emoji_animated} className="discord-profile-status-emoji" />;
  }
  return status.emoji_name ? <span className="discord-profile-status-emoji">{status.emoji_name}</span> : null;
}

function trackClock(seconds: number) {
  const total = Math.max(0, Math.round(seconds));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

/** The Spotify card Discord shows at the bottom of a profile popout. */
function ProfileSpotifyCard({ activity }: { activity: DiscordProfileActivity }) {
  const start = activity.start;
  const end = activity.end;
  const hasWindow = typeof start === "number" && typeof end === "number" && end > start;
  const [now, setNow] = useState(() => Math.floor(Date.now() / 1000));
  useEffect(() => {
    if (!hasWindow) return;
    setNow(Math.floor(Date.now() / 1000));
    const timer = window.setInterval(() => setNow(Math.floor(Date.now() / 1000)), 1000);
    return () => window.clearInterval(timer);
  }, [hasWindow, start, end]);
  const total = activity.duration_seconds || (hasWindow ? (end as number) - (start as number) : 0);
  const elapsed = hasWindow ? Math.min(Math.max(now - (start as number), 0), total) : 0;
  const card = <div className="discord-profile-spotify">
    <div className="discord-profile-spotify-head"><img src="/spotify.svg" alt="" /><span>Listening to Spotify</span></div>
    <div className="discord-profile-spotify-body">
      <img className="discord-profile-spotify-art" src={activity.album_cover_url} alt="" />
      <div className="discord-profile-spotify-copy">
        <strong title={activity.title || "Spotify"}>{activity.title || "Spotify"}</strong>
        {activity.artists.length > 0 && <small title={activity.artists.join(", ")}>{activity.artists.join(", ")}</small>}
        {hasWindow && total > 0 && <div className="discord-profile-spotify-progress">
          <span>{trackClock(elapsed)}</span>
          <span className="discord-profile-spotify-track" aria-hidden="true"><i style={{ width: `${(elapsed / total) * 100}%` }} /></span>
          <span>{trackClock(total)}</span>
        </div>}
      </div>
    </div>
  </div>;
  return activity.url
    ? <a className="discord-profile-spotify-link" href={activity.url} target="_blank" rel="noreferrer">{card}</a>
    : card;
}

/** The circular "..." menu in the popup's top corner, with Copy User ID. */
function ProfileMenu({ userId }: { userId: string }) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      if (event.target instanceof Node && menuRef.current?.contains(event.target)) return;
      setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [open]);
  useEffect(() => {
    if (!copied) return;
    const timer = window.setTimeout(() => setCopied(false), 1800);
    return () => window.clearTimeout(timer);
  }, [copied]);
  const copyUserId = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(userId);
      setCopied(true);
    } catch {
      // A browser without clipboard access: leave the label alone rather than
      // claiming a copy that did not happen.
      setCopied(false);
    }
  }, [userId]);
  return <div className="discord-profile-menu" ref={menuRef}>
    <button
      type="button"
      className="discord-profile-menu-button"
      aria-label="More options"
      aria-haspopup="menu"
      aria-expanded={open}
      onClick={() => setOpen((value) => !value)}
    >
      <span className="discord-profile-menu-dots" aria-hidden="true"><i /><i /><i /></span>
    </button>
    {open && <div className="discord-profile-menu-list" role="menu">
      <button type="button" className="discord-profile-menu-item" role="menuitem" onClick={() => void copyUserId()}>
        {copied ? "Copied!" : "Copy User ID"}
      </button>
    </div>}
  </div>;
}

export function DiscordMarkdown({ text, mentionNames, guildId, className, style, interactiveUsers = true, inline = false }: {
  text: string;
  mentionNames?: DiscordMentionNames;
  guildId?: string;
  className?: string;
  style?: CSSProperties;
  interactiveUsers?: boolean;
  inline?: boolean;
}) {
  const [resolvedNames, setResolvedNames] = useState<{ key: string; names: DiscordMentionNames }>({ key: "", names: {} });
  const resolutionKey = `${guildId || ""}:${text}`;
  const mentionNamesKey = JSON.stringify(mentionNames || {});
  useEffect(() => {
    const mentions = { user: new Set<string>(), channel: new Set<string>(), role: new Set<string>() };
    const mentionPattern = /<@!?(\d+)>|<@&(\d+)>|<#(\d+)>/g;
    let match: RegExpExecArray | null;
    while ((match = mentionPattern.exec(text))) {
      if (match[1]) mentions.user.add(match[1]);
      else if (match[2]) mentions.role.add(match[2]);
      else if (match[3]) mentions.channel.add(match[3]);
    }
    const hasMissingNames = (["user", "channel", "role"] as const).some((kind) =>
      Array.from(mentions[kind]).some((id) => !mentionNames?.[kind]?.[id]),
    );
    if (!hasMissingNames) return;
    let active = true;
    void resolveDiscordText(text, guildId).then((result) => {
      if (active) setResolvedNames({ key: resolutionKey, names: result.mention_names });
    }).catch(() => {
      // Keep the ID fallback when Discord name lookup is unavailable.
    });
    return () => { active = false; };
  }, [guildId, mentionNamesKey, resolutionKey, text]);
  const resolvedMentionNames: DiscordMentionNames = {
    ...(resolvedNames.key === resolutionKey ? resolvedNames.names : {}),
    ...mentionNames,
    user: { ...(resolvedNames.key === resolutionKey ? resolvedNames.names.user : {}), ...mentionNames?.user },
    channel: { ...(resolvedNames.key === resolutionKey ? resolvedNames.names.channel : {}), ...mentionNames?.channel },
    role: { ...(resolvedNames.key === resolutionKey ? resolvedNames.names.role : {}), ...mentionNames?.role },
  };
  const [profile, setProfile] = useState<TranscriptProfile | null>(null);
  const [profilePosition, setProfilePosition] = useState({ left: 12, top: 12 });
  const profileCardRef = useRef<HTMLDivElement>(null);
  const profileTriggerRef = useRef<HTMLElement | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState("");
  const requestRef = useRef(0);
  const profileBadgeList = profileBadges(profile?.badges);
  const customStatus = profile?.custom_status || null;
  const spotifyActivity = (profile?.activities || []).find((activity) => Boolean(activity.album_cover_url)) || null;
  const closeProfile = useCallback(() => {
    requestRef.current += 1;
    profileTriggerRef.current = null;
    setProfile(null);
    setProfileLoading(false);
    setProfileError("");
  }, []);
  const positionProfile = useCallback(() => {
    const trigger = profileTriggerRef.current;
    const card = profileCardRef.current;
    if (!trigger || !card) return;
    const rect = trigger.getBoundingClientRect();
    const margin = 12;
    const gap = 8;
    const width = card.offsetWidth;
    const height = card.offsetHeight;
    const left = Math.max(margin, Math.min(rect.left, window.innerWidth - width - margin));
    const below = rect.bottom + gap;
    const top = below + height <= window.innerHeight - margin
      ? below
      : Math.max(margin, rect.top - height - gap);
    setProfilePosition({ left, top: Math.min(top, window.innerHeight - height - margin) });
  }, []);
  useLayoutEffect(() => {
    if (!profileLoading && !profileError && !profile) return;
    positionProfile();
  }, [positionProfile, profile, profileError, profileLoading]);
  useEffect(() => {
    if (!profileLoading && !profileError && !profile) return;
    window.addEventListener("resize", positionProfile);
    window.addEventListener("scroll", positionProfile, true);
    return () => {
      window.removeEventListener("resize", positionProfile);
      window.removeEventListener("scroll", positionProfile, true);
    };
  }, [positionProfile, profile, profileError, profileLoading]);
  const openProfile = useCallback(async (userId: string, trigger: HTMLElement) => {
    if (!/^\d{1,22}$/.test(userId)) return;
    const requestId = ++requestRef.current;
    profileTriggerRef.current = trigger;
    setProfilePosition({ left: 12, top: 12 });
    setProfile(null);
    setProfileError("");
    setProfileLoading(true);
    try {
      const result = await fetchDiscordProfile(userId);
      if (requestRef.current === requestId) setProfile(result);
    } catch (error) {
      if (requestRef.current === requestId) setProfileError(error instanceof Error ? error.message : "Could not load this Discord profile.");
    } finally {
      if (requestRef.current === requestId) setProfileLoading(false);
    }
  }, []);
  const openProfileId = profile?.id || "";
  useEffect(() => {
    if (!openProfileId) return;
    let active = true;
    const refresh = () => {
      // A transient poll failure keeps the last known presence: the popup never
      // blanks out or flashes a loading state while it refreshes.
      fetchDiscordProfile(openProfileId)
        .then((next) => {
          if (active) setProfile((current) => (current && current.id === next.id ? next : current));
        })
        .catch(() => {});
    };
    const handleVisibility = () => {
      if (document.visibilityState === "visible") refresh();
    };

    const interval = window.setInterval(() => {
      if (document.visibilityState === "visible") refresh();
    }, PROFILE_REFRESH_INTERVAL);
    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      active = false;
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [openProfileId]);
  useEffect(() => {
    if (!interactiveUsers || (!profile && !profileLoading && !profileError)) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      // A floating server-tag popup is the topmost layer, so Escape closes it
      // and leaves the profile underneath open for the next Escape.
      if (document.querySelector(".discord-server-tag-popup")) return;
      closeProfile();
    };
    const onClick = (event: MouseEvent) => {
      const target = event.target;
      // The badge popup floats outside the card, so a click inside it keeps the
      // profile open.
      if (target instanceof Element && !target.closest(".discord-profile-card") && !target.closest(".discord-badge-popup") && !target.closest(".discord-server-tag-popup") && !target.closest("[data-discord-user-id]")) closeProfile();
    };
    window.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onClick);
    return () => { window.removeEventListener("keydown", onKey); document.removeEventListener("mousedown", onClick); };
  }, [closeProfile, interactiveUsers, profile, profileError, profileLoading]);

  const lines = text.split("\n");
  const children: ReactNode[] = [];
  const renderInlineText = (line: string, key: string | number) => {
    let content = line;
    const task = content.match(/^\s*[-*]\s+\[([ xX])\]\s+(.*)$/);
    const ordered = content.match(/^\s*(\d+)\.\s+(.*)$/);
    if (task) content = `• ${task[2]}`;
    else if (/^\s*[-*]\s+/.test(content)) content = `• ${content.replace(/^\s*[-*]\s+/, "")}`;
    else if (ordered) content = `${ordered[1]}. ${ordered[2]}`;
    return <span key={key} className={task ? "discord-md-task" : undefined}>{renderInline(tokenize(content), resolvedMentionNames, `line-${key}`, interactiveUsers)}</span>;
  };
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const trimmed = line.trimStart();
    if (trimmed.startsWith("```")) {
      const code: string[] = [];
      index += 1;
      while (index < lines.length && !lines[index].trimStart().startsWith("```")) code.push(lines[index++]);
      children.push(<pre className="discord-md-block-code" key={`code-${index}`}><code>{code.join("\n")}</code></pre>);
      continue;
    }
    const isTableRow = (value: string) => value.trimStart().startsWith("|");
    if (isTableRow(line)) {
      const rows: string[][] = [];
      while (index < lines.length && isTableRow(lines[index])) {
        rows.push(lines[index++].trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim()));
      }
      index -= 1;
      const isSeparator = (cells: string[]) => cells.length > 0 && cells.every((cell) => /^:?-{2,}:?$/.test(cell.replace(/\s+/g, "")));
      const header = rows[0];
      const body = rows.length > 1 && isSeparator(rows[1]) ? rows.slice(2) : rows.slice(1);
      children.push(<div className="discord-md-table-wrap" key={`table-${index}`}><table className="discord-md-table"><thead><tr>{header.map((cell, cellIndex) => <th key={cellIndex}>{renderInline(tokenize(cell), resolvedMentionNames, `table-head-${index}-${cellIndex}`, interactiveUsers)}</th>)}</tr></thead><tbody>{body.map((row, rowIndex) => <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={cellIndex}>{renderInline(tokenize(cell), resolvedMentionNames, `table-${index}-${rowIndex}-${cellIndex}`, interactiveUsers)}</td>)}</tr>)}</tbody></table></div>);
      continue;
    }
    const heading = trimmed.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      const Heading = `h${heading[1].length}` as "h1" | "h2" | "h3" | "h4";
      children.push(<Heading className="discord-md-heading" key={index}>{renderInline(tokenize(heading[2]), resolvedMentionNames, `line-${index}`, interactiveUsers)}</Heading>);
      continue;
    }
    const quote = trimmed.match(/^>\s?(.*)$/);
    const subtext = trimmed.startsWith("-# ");
    const content = subtext ? trimmed.slice(3) : quote ? quote[1] : line;
    const inline = renderInlineText(content, index);
    children.push(quote
      ? <blockquote className="discord-md-quote" key={index}>{inline}</blockquote>
      : subtext
        ? <small className="discord-md-subtext" key={index}>{inline}{index < lines.length - 1 ? <br /> : null}</small>
        : <span key={index}>{inline}{index < lines.length - 1 ? <br /> : null}</span>);
  }
  const Wrapper = inline ? "span" : "div";
  return <Wrapper className={`discord-markdown${inline ? " discord-markdown-inline" : ""}${className ? ` ${className}` : ""}`} style={style} onClick={interactiveUsers ? (event) => {
    const target = event.target;
    if (target instanceof Element) {
      const mention = target.closest<HTMLElement>("[data-discord-user-id]");
      if (mention) {
        event.preventDefault();
        void openProfile(mention.dataset.discordUserId || "", mention);
      }
    }
  } : undefined}>
    {children}
    {interactiveUsers && (profileLoading || profileError || profile) && createPortal(<div className="discord-profile-popover" role="presentation">
      <div ref={profileCardRef} className="discord-profile-card" role={profileError ? "alert" : profileLoading ? "status" : "dialog"} aria-label={profile ? `${profile.display_name} Discord profile` : undefined} style={{ "--profile-left": `${profilePosition.left}px`, "--profile-top": `${profilePosition.top}px` } as CSSProperties}>
        {profileLoading ? <div className="discord-profile-state">Loading Discord profile…</div> : profileError ? <div className="discord-profile-state">{profileError}</div> : profile && <>
          {profile.banner_url
            ? <img className="discord-profile-banner" src={profile.banner_url} alt="" />
            : <div className="discord-profile-banner" style={{ backgroundColor: profile.banner_color || "#202225" }} />}
          {/* Keyed by user so an open menu never carries over to the next popup. */}
          <ProfileMenu key={profile.id} userId={profile.id} />
          <div className="discord-profile-body">
            <div className="discord-profile-head">
              {profile.avatar_url && <DiscordStatusAvatar status={profileStatusKey(profile.status)} className="discord-profile-avatar-wrap" label={profileStatusLabel(profile.status)}>
                <img className="discord-profile-avatar" src={profile.avatar_url} alt="" />
                {profile.avatar_decoration_url && <img className="discord-profile-avatar-decoration" src={profile.avatar_decoration_url} alt="" />}
              </DiscordStatusAvatar>}
              {customStatus && (customStatus.text || customStatus.emoji_id || customStatus.emoji_name) && <div className="discord-profile-status">
                <span className="discord-profile-status-text">{statusEmoji(customStatus)}{customStatus.text}</span>
              </div>}
            </div>
            <h2 className="discord-profile-name">{profile.display_name}</h2>
            {/* Discord puts the server tag pill on the username row and the
                profile badges on the line directly below it. */}
            <p className="discord-profile-username">
              <span className="discord-profile-user-tag">{profile.username}</span>
              {profile.guild_tag && <DiscordServerTagPill
                server={profile.server_tag || null}
                tag={profile.guild_tag}
                badgeUrl={profile.guild_badge_url}
              />}
            </p>
            {/* Badge artwork ships with the app; clicking one opens the badge
                popup owned by DiscordBadgeList. */}
            <DiscordBadgeList badges={profileBadgeList} />
            {profile.bio && <section className="discord-profile-about"><h3>About Me</h3><p>{profile.bio}</p></section>}
            {spotifyActivity && <ProfileSpotifyCard activity={spotifyActivity} />}
            <a className="discord-profile-full-link" href={`https://discord.com/users/${profile.id}`} target="_blank" rel="noopener noreferrer">Open Discord profile</a>
          </div>
        </>}
      </div>
    </div>, document.body)}
  </Wrapper>;
}
