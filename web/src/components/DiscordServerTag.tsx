import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import type { CSSProperties, Ref } from "react";

/**
 * The server (guild tag) a Discord profile wears beside its username.
 *
 * The payload mirrors the three states Discord's own server-tag popup draws:
 * a public server with its identity, a private server that has limited who can
 * see its profile, and a server Niko is not in so nothing could be read.
 */
export type DiscordServerTagInfo = {
  id?: string | null;
  tag?: string | null;
  badge_url?: string | null;
  available?: boolean;
  private?: boolean;
  name?: string | null;
  icon_url?: string | null;
  banner_url?: string | null;
  description?: string | null;
  online_count?: number | null;
  member_count?: number | null;
  created_at?: number | null;
  invite_url?: string | null;
  /** Whether the signed-in viewer already belongs to this server. */
  viewer_is_member?: boolean | null;
};

function monthYear(unix?: number | null) {
  if (typeof unix !== "number" || !Number.isFinite(unix)) return null;
  const date = new Date(unix * 1000);
  if (!Number.isFinite(date.getTime())) return null;
  return new Intl.DateTimeFormat(undefined, { month: "short", year: "numeric" }).format(date);
}

function count(value?: number | null) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0
    ? new Intl.NumberFormat().format(Math.round(value))
    : null;
}

/**
 * A clickable guild-tag pill. Clicking it opens Discord's server popup, which
 * floats above the profile card instead of stretching or being clipped by it.
 */
export function DiscordServerTagPill({ server, tag, badgeUrl, className }: {
  server: DiscordServerTagInfo | null;
  tag: string;
  badgeUrl?: string | null;
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState({ left: 12, top: 12 });
  const triggerRef = useRef<HTMLButtonElement>(null);
  const popupRef = useRef<HTMLDivElement>(null);

  const positionPopup = useCallback(() => {
    const trigger = triggerRef.current;
    const popup = popupRef.current;
    if (!trigger || !popup) return;
    const rect = trigger.getBoundingClientRect();
    const margin = 12;
    const gap = 8;
    const width = popup.offsetWidth;
    const height = popup.offsetHeight;
    const left = Math.max(margin, Math.min(rect.left + rect.width / 2 - width / 2, window.innerWidth - width - margin));
    const below = rect.bottom + gap;
    const top = below + height <= window.innerHeight - margin
      ? below
      : Math.max(margin, rect.top - height - gap);
    setPosition({ left, top: Math.min(top, window.innerHeight - height - margin) });
  }, []);

  useLayoutEffect(() => {
    if (open) positionPopup();
  }, [open, positionPopup]);

  useEffect(() => {
    if (!open) return;
    window.addEventListener("resize", positionPopup);
    // Capture, so the profile card's own scroll box moves the popup with the pill.
    window.addEventListener("scroll", positionPopup, true);
    return () => {
      window.removeEventListener("resize", positionPopup);
      window.removeEventListener("scroll", positionPopup, true);
    };
  }, [open, positionPopup]);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      const target = event.target;
      if (target instanceof Node && (triggerRef.current?.contains(target) || popupRef.current?.contains(target))) return;
      setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const pill = <>
    {badgeUrl && <img src={badgeUrl} alt="" />}
    <span>{tag}</span>
  </>;

  // A tag without a resolved guild still renders as the plain pill Discord
  // shows; only a tag whose server state is known becomes interactive.
  if (!server) return <span className={className ? `discord-profile-guild-tag ${className}` : "discord-profile-guild-tag"}>{pill}</span>;

  return <>
    <button
      ref={triggerRef}
      type="button"
      className={`discord-profile-guild-tag${open ? " is-open" : ""}${className ? ` ${className}` : ""}`}
      aria-haspopup="dialog"
      aria-expanded={open}
      title={`Server tag · ${tag}`}
      onClick={() => setOpen((value) => !value)}
    >
      {pill}
    </button>
    {open && createPortal(
      <ServerTagPopup
        server={server}
        tag={tag}
        badgeUrl={badgeUrl}
        popupRef={popupRef}
        style={{ "--server-tag-left": `${position.left}px`, "--server-tag-top": `${position.top}px` } as CSSProperties}
      />,
      document.body,
    )}
  </>;
}

/** The popup itself, exported so it can be rendered and checked without a click. */
export function ServerTagPopup({ server, tag, badgeUrl, popupRef, style }: {
  server: DiscordServerTagInfo;
  tag: string;
  badgeUrl?: string | null;
  popupRef?: Ref<HTMLDivElement>;
  style?: CSSProperties;
}) {
  const isPrivate = Boolean(server.private);
  const isUnknown = !isPrivate && !server.available;
  const name = isPrivate ? "Private Server" : isUnknown ? "Unknown Server" : server.name || tag;
  const description = isPrivate
    ? "The server has limited who can see this profile."
    : isUnknown
      ? "This server is unavailable, or Niko is not a member of it."
      : server.description;
  const online = count(server.online_count);
  const members = count(server.member_count);
  const established = monthYear(server.created_at);
  const showDetails = !isPrivate && !isUnknown;
  const hasStats = showDetails && (online !== null || members !== null);
  // Discord offers Go to Server to people who already belong to the server,
  // and Join to everyone else only when the guild has a vanity invite it can
  // use. With no invite to offer, the button is simply left out. A signed-out
  // viewer is treated as a non-member.
  const isMember = Boolean(server.viewer_is_member);
  const memberUrl = isMember && server.id ? `https://discord.com/channels/${server.id}` : null;
  const joinUrl = showDetails && !isMember ? server.invite_url || null : null;

  return <div
    ref={popupRef}
    className={`discord-server-tag-popup${isPrivate ? " is-private" : ""}${isUnknown ? " is-unknown" : ""}`}
    role="dialog"
    aria-label={`${name} server tag`}
    style={style}
  >
    {showDetails && server.banner_url
      ? <img className="discord-server-tag-banner" src={server.banner_url} alt="" />
      : <div className="discord-server-tag-banner" aria-hidden="true" />}
    <div className="discord-server-tag-body">
      <div className="discord-server-tag-icon-shell">
        {showDetails && server.icon_url
          ? <img className="discord-server-tag-icon" src={server.icon_url} alt="" />
          : <span className="discord-server-tag-icon is-placeholder" aria-hidden="true">?</span>}
      </div>
      <div className="discord-server-tag-title-row">
        <h3 className="discord-server-tag-name">{name}</h3>
        {/* A private server hides its identity, so Discord drops the tag pill
            from the popup too; the tag stays on the profile itself. */}
        {tag && !isPrivate && <span className="discord-server-tag-pill">
          {badgeUrl && <img src={badgeUrl} alt="" />}
          <span>{tag}</span>
        </span>}
      </div>
      {hasStats && <p className="discord-server-tag-stats">
        {online !== null && <span className="discord-server-tag-online"><i aria-hidden="true" />{online} Online</span>}
        {members !== null && <span className="discord-server-tag-members"><i aria-hidden="true" />{members} Members</span>}
      </p>}
      {showDetails && established && <p className="discord-server-tag-created">Est. {established}</p>}
      {description && <p className="discord-server-tag-description">{description}</p>}
      {memberUrl
        ? <a className="discord-server-tag-invite" href={memberUrl} target="_blank" rel="noopener noreferrer">Go to Server</a>
        : joinUrl
          ? <a className="discord-server-tag-invite is-join" href={joinUrl} target="_blank" rel="noopener noreferrer">Join</a>
          : null}
    </div>
  </div>;
}
