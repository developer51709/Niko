import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import type { CSSProperties, Ref } from "react";
import type { ProfileBadge } from "../data/profileBadges";

/**
 * The badge row inside a profile popup.
 *
 * Discord draws a badge as a small square of art; clicking one opens a popup
 * with that art on the left and the badge's name and description on the right.
 * The art, names and descriptions all come from the shared catalog in
 * web/src/data/profileBadges.ts so the popups, the bot's card and the
 * rendering lab can never drift apart.
 *
 * The badge popup is portalled to the page rather than nested in the profile
 * card: drawn inside the card it was clipped by the card's own scroll box and
 * stretched the profile popup to make room for it, exactly what Discord does
 * not do. Floating above the card keeps the profile popup its own size.
 */
export function DiscordBadgeList({ badges, className, label = "Profile badges" }: {
  badges: ProfileBadge[];
  className?: string;
  label?: string;
}) {
  const [openKey, setOpenKey] = useState<string | null>(null);
  const [popupPosition, setPopupPosition] = useState({ left: 12, top: 12 });
  const listRef = useRef<HTMLDivElement>(null);
  const popupRef = useRef<HTMLDivElement>(null);
  const open = badges.find((badge) => badge.key === openKey) || null;

  // The popup hangs under the badge it belongs to, centred on it, and flips
  // above the badge when the bottom of the window is too close.
  const positionPopup = useCallback(() => {
    const trigger = openKey
      ? listRef.current?.querySelector<HTMLElement>(`[data-badge-key="${openKey}"]`)
      : null;
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
    setPopupPosition({ left, top: Math.min(top, window.innerHeight - height - margin) });
  }, [openKey]);

  useLayoutEffect(() => {
    if (!open) return;
    positionPopup();
  }, [open, positionPopup]);

  useEffect(() => {
    if (!open) return;
    window.addEventListener("resize", positionPopup);
    // Capture, so the card's own scroll box moves the popup with its badge.
    window.addEventListener("scroll", positionPopup, true);
    return () => {
      window.removeEventListener("resize", positionPopup);
      window.removeEventListener("scroll", positionPopup, true);
    };
  }, [open, positionPopup]);

  useEffect(() => {
    if (!openKey) return;
    const onPointerDown = (event: MouseEvent) => {
      const target = event.target;
      if (target instanceof Node && (listRef.current?.contains(target) || popupRef.current?.contains(target))) return;
      setOpenKey(null);
    };
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") setOpenKey(null); };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [openKey]);

  if (badges.length === 0) return null;

  return <div ref={listRef} className={`discord-profile-badges${className ? ` ${className}` : ""}`} role="group" aria-label={label}>
    {badges.map((badge) => <button
      key={badge.key}
      type="button"
      className={`discord-profile-badge-button${openKey === badge.key ? " is-open" : ""}`}
      data-badge-key={badge.key}
      aria-label={badge.label}
      aria-haspopup="dialog"
      aria-expanded={openKey === badge.key}
      title={badge.label}
      onClick={() => setOpenKey((current) => (current === badge.key ? null : badge.key))}
    >
      <img className="discord-profile-badge" src={badge.src} alt="" />
    </button>)}
    {open && createPortal(
      <BadgePopup
        badge={open}
        popupRef={popupRef}
        style={{ "--badge-popup-left": `${popupPosition.left}px`, "--badge-popup-top": `${popupPosition.top}px` } as CSSProperties}
      />,
      document.body,
    )}
  </div>;
}

/**
 * The badge popup itself: the badge art on the left of the card, and its name
 * and description to the right of it. Exported on its own so the popup can be
 * rendered and checked without a click.
 */
export function BadgePopup({ badge, popupRef, style }: {
  badge: ProfileBadge;
  popupRef?: Ref<HTMLDivElement>;
  style?: CSSProperties;
}) {
  return <div ref={popupRef} className="discord-badge-popup" role="dialog" aria-label={`${badge.label} badge`} style={style}>
    <img className="discord-badge-popup-art" src={badge.src} alt="" />
    <div className="discord-badge-popup-copy">
      <strong>{badge.label}</strong>
      <p>{badge.description}</p>
    </div>
  </div>;
}
