import { useLayoutEffect, useRef, useState, type MouseEvent } from "react";
import { createPortal } from "react-dom";
import { Icon } from "./Icon";

interface PublicHeaderActionsProps {
  inviteUrl?: string;
  onNavigate: (path: string) => (event: MouseEvent<HTMLAnchorElement>) => void;
  isDashboard?: boolean;
  menuOpen?: boolean;
  onMenuToggle?: () => void;
}

const publicLinks = [
  { label: "Home", path: "/" },
  { label: "Commands", path: "/commands" },
  { label: "Docs", path: "/docs" },
  { label: "Team", path: "/team" },
  { label: "Changelog", path: "/changelog" },
];

export function PublicHeaderActions({
  inviteUrl,
  onNavigate,
  isDashboard = false,
  menuOpen = false,
  onMenuToggle,
}: PublicHeaderActionsProps) {
  const triggerRef = useRef<HTMLButtonElement>(null);
  const popoverRef = useRef<HTMLElement>(null);
  const [placement, setPlacement] = useState<{ top: number; right: number } | null>(null);

  // The menu is portalled to <body>: the header carries a backdrop-filter, which
  // turns it into a backdrop root, so a menu nested inside it has only the
  // header's own wash to blur and ends up looking transparent. Out here it frosts
  // the page and the animated backdrop like every other glass panel.
  useLayoutEffect(() => {
    if (!menuOpen) {
      setPlacement(null);
      return;
    }
    const place = () => {
      const trigger = triggerRef.current;
      if (!trigger) return;
      const anchor = trigger.getBoundingClientRect();
      const height = popoverRef.current?.getBoundingClientRect().height ?? 0;
      const gap = 10;
      const pad = 12;
      const top = height
        ? Math.max(pad, Math.min(anchor.bottom + gap, window.innerHeight - pad - height))
        : anchor.bottom + gap;
      setPlacement({ top, right: Math.max(pad, window.innerWidth - anchor.right) });
    };
    place();
    window.addEventListener("scroll", place, true);
    window.addEventListener("resize", place);
    return () => {
      window.removeEventListener("scroll", place, true);
      window.removeEventListener("resize", place);
    };
  }, [menuOpen]);

  if (isDashboard) {
    return (
      <div className="dashboard-menu">
        <button
          ref={triggerRef}
          className="button button-small button-muted dashboard-menu-trigger"
          type="button"
          aria-expanded={menuOpen}
          aria-controls="dashboard-navigation-menu"
          onClick={onMenuToggle}
        >
          <Icon name={menuOpen ? "close" : "menu"} />
          <span>Menu</span>
        </button>
        {menuOpen && createPortal(
          <nav
            id="dashboard-navigation-menu"
            ref={popoverRef}
            className="dashboard-menu-popover"
            aria-label="Dashboard navigation"
            style={{
              top: placement?.top ?? 0,
              right: placement?.right ?? 0,
              visibility: placement ? "visible" : "hidden",
            }}
          >
            <span className="dashboard-menu-label">Navigate</span>
            {publicLinks.map((link) => (
              <a key={link.path} href={link.path} onClick={onNavigate(link.path)}>
                {link.label}
              </a>
            ))}
            <a className="dashboard-menu-current" href="/dashboard" aria-current="page" onClick={onNavigate("/dashboard")}>
              Dashboard
            </a>
          </nav>,
          document.body,
        )}
      </div>
    );
  }

  return (
    <>
      <a className="button button-small button-muted dashboard-link" href="/dashboard" onClick={onNavigate("/dashboard")}>
        Dashboard <Icon name="arrow" />
      </a>
      <a className="button button-small button-primary" href={inviteUrl || "#"} target="_blank" rel="noreferrer">
        Add to Discord
      </a>
    </>
  );
}
