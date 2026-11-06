import {
  Fragment,
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent as ReactKeyboardEvent,
} from "react";
import { createPortal } from "react-dom";
import { useStrings } from "../i18n";
import { contextMenuExtras } from "../utils/contextMenu";
import { notifyError, notifySuccess } from "../utils/toast";
import { Icon } from "./Icon";

/**
 * The site's own context menu.
 *
 * Right-click on a desktop and a long press on a phone used to open the
 * browser's menu: copy, save image, inspect, "search Google for…". Those items
 * know nothing about the site, so the same gesture now opens a small menu built
 * from what was actually pressed — the link, the picture, the selected text —
 * plus the two things that work anywhere, copying the page address and going
 * back. It is deliberately short; there is room to grow per page later.
 *
 * Form fields keep the browser's menu. Pasting, spell-check and autofill have
 * no replacement here — Firefox gives a page no way to read the clipboard at
 * all — so losing them would be a bug rather than a feature. Everywhere else
 * the device's own menu is kept away: one menu, in the site's own style.
 */

/** How long a finger has to rest before the menu opens on a touch screen. */
const LONG_PRESS_MS = 480;

/** Travel that turns a long press into a scroll instead. */
const MOVE_TOLERANCE = 12;

/** Room kept between the menu and the edge of the window. */
const EDGE = 12;

type MenuItem = {
  key: string;
  label: string;
  icon: string;
  /** Draw a hairline above this row, separating it from the context's own items. */
  divider?: boolean;
  action: () => void;
};

/**
 * Where the menu belongs, in page coordinates, so it scrolls with the words it
 * was opened on instead of hanging over whatever scrolls underneath it.
 */
type OpenMenu = {
  x: number;
  y: number;
  items: MenuItem[];
  /** `y` is the menu's bottom edge: it opens upwards, out of the selection. */
  above?: boolean;
};

/**
 * The text the press landed on, or "" when it landed away from it.
 *
 * A selection that is still highlighted is only offered as Copy when the press
 * was inside it — pressing somewhere else is a new gesture, not a request to
 * copy what happens to be selected.
 */
function selectionAt(element: Element | null): string {
  const selection = window.getSelection();
  if (!selection || selection.isCollapsed) return "";
  const text = selection.toString().trim();
  if (!text) return "";
  if (!element) return text;
  for (let index = 0; index < selection.rangeCount; index += 1) {
    if (selection.getRangeAt(index).intersectsNode(element)) return text;
  }
  return "";
}

/** Whether the event came from inside the menu itself. */
function inside(target: EventTarget | null, container: HTMLElement | null): boolean {
  return Boolean(container && target instanceof Node && container.contains(target));
}

/** Fields keep the browser's menu; everything else gets ours. */
function isEditable(target: EventTarget | null): boolean {
  return (
    target instanceof Element &&
    Boolean(target.closest("input, textarea, select, [contenteditable]:not([contenteditable='false'])"))
  );
}

/**
 * Where the highlighted words are on screen, for a menu that should sit beside
 * them rather than on top of them.
 */
function selectionAnchor(): { x: number; y: number } | null {
  const selection = window.getSelection();
  if (!selection || selection.isCollapsed || selection.rangeCount === 0) return null;
  const range = selection.getRangeAt(0);
  const rects = Array.from(range.getClientRects()).filter((rect) => rect.width > 0 || rect.height > 0);
  const first = rects[0] ?? range.getBoundingClientRect();
  if (!first || (!first.width && !first.height)) return null;
  return { x: first.left, y: first.top - 6 };
}

function copyText(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

export function ContextMenuHost() {
  const { t } = useStrings("shared");
  const [menu, setMenu] = useState<OpenMenu | null>(null);
  const [position, setPosition] = useState<{ left: number; top: number; origin: string } | null>(null);
  const [highlighted, setHighlighted] = useState(0);
  const menuRef = useRef<HTMLDivElement>(null);
  const idPrefix = useId();
  // Whatever had focus before the menu opened, so Escape can hand it back.
  const previousFocus = useRef<Element | null>(null);

  const copy = useCallback(
    (text: string) => {
      copyText(text)
        .then(() => notifySuccess(t("contextMenu.copied"), "context-menu"))
        .catch(() => notifyError(t("contextMenu.copyFailed"), "context-menu"));
    },
    [t],
  );

  /**
   * `x`/`y` are viewport coordinates from the gesture. A press on a selection
   * puts the menu above the highlighted words instead: on a phone the finger is
   * on the text, and a card under it would cover the very words being selected.
   */
  const openAt = useCallback(
    (x: number, y: number, target: EventTarget | null, fromTouch = false) => {
      const element = target instanceof Element ? target : null;
      const link = element?.closest<HTMLAnchorElement>("a[href]");
      const image = element?.closest<HTMLImageElement>("img[src]");
      const selection = selectionAt(element);
      // Rows the pressed element brings itself come first: pressing the devtools
      // button should offer what the button can do, not only what all pages can.
      const items: MenuItem[] = contextMenuExtras(element);

      if (selection) {
        items.push({
          key: "copy-selection",
          label: t("contextMenu.copy"),
          icon: "copy",
          // Read at the moment it is pressed: the selection may have grown
          // while the menu sat open beside it.
          action: () => copy(window.getSelection()?.toString().trim() || selection),
        });
      }
      // A picture inside a link is both, so it gets both sets of rows: the
      // picture's own address first, then the page the link leads to. Before,
      // the link swallowed the image and its address could not be copied at all.
      if (image) {
        const source = image.currentSrc || image.src;
        items.push(
          { key: "copy-image", label: t("contextMenu.copyImage"), icon: "image", action: () => copy(source) },
          {
            key: "open-image",
            label: t("contextMenu.openImage"),
            icon: "external",
            action: () => window.open(source, "_blank", "noopener,noreferrer"),
          },
        );
      }
      if (link) {
        const href = link.href;
        items.push(
          { key: "copy-link", label: t("contextMenu.copyLink"), icon: "link", action: () => copy(href) },
          {
            key: "open-link",
            label: t("contextMenu.openLink"),
            icon: "external",
            action: () => window.open(href, "_blank", "noopener,noreferrer"),
          },
        );
      }

      // Always available: the two things that make sense anywhere on the site.
      items.push(
        {
          key: "copy-page",
          label: t("contextMenu.copyPage"),
          icon: "link",
          divider: items.length > 0,
          action: () => copy(window.location.href),
        },
        {
          key: "back",
          label: t("contextMenu.back"),
          icon: "back",
          action: () => window.history.back(),
        },
      );

      const anchor = fromTouch && selection ? selectionAnchor() : null;
      // Page coordinates, so the menu keeps its place against the text while the
      // page scrolls instead of drifting away from it.
      previousFocus.current = document.activeElement;
      setMenu({
        x: (anchor?.x ?? x) + window.scrollX,
        y: (anchor?.y ?? y) + window.scrollY,
        above: Boolean(anchor),
        items,
      });
      setPosition(null);
      setHighlighted(0);
    },
    [copy, t],
  );

  const close = useCallback((restoreFocus = false) => {
    setMenu(null);
    setPosition(null);
    const previous = previousFocus.current;
    // A page that navigated away while the menu was open has nothing to return to.
    if (restoreFocus && previous instanceof HTMLElement && previous.isConnected) {
      previous.focus({ preventScroll: true });
    }
  }, []);

  const run = useCallback(
    (item: MenuItem | undefined) => {
      if (!item) return;
      // Hand focus back to the page rather than dropping it on <body>: after a
      // copy, the visitor keeps typing where they were typing.
      close(true);
      item.action();
    },
    [close],
  );

  // Reachable without a mouse as well: Shift+F10 and the context-menu key open
  // it on whatever has focus, which is where the browser's own menu would go.
  useEffect(() => {
    if (menu) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "ContextMenu" && !(event.shiftKey && event.key === "F10")) return;
      const focused = document.activeElement;
      if (!(focused instanceof Element) || isEditable(focused)) return;
      event.preventDefault();
      const rect = focused.getBoundingClientRect();
      openAt(rect.left + Math.min(rect.width, 16), rect.top + Math.min(rect.height, 20), focused);
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [menu, openAt]);

  // The gesture itself: the browser's context menu on a desktop, and a finger
  // that stays still on a touch screen — where the browser has no reliable
  // event of its own (iOS never fires one) and the callout is suppressed by CSS
  // on everything except text, which keeps its own selection.
  useEffect(() => {
    let pressTimer: number | undefined;
    let pressPoint: { x: number; y: number } | null = null;
    let openedByTouchAt = 0;
    let suppressClickUntil = 0;
    // A finger held on a row of the open menu: release must not fire that row.
    let insideHoldStartedAt = 0;
    let suppressInsideClick = false;

    const cancelPress = () => {
      if (pressTimer !== undefined) window.clearTimeout(pressTimer);
      pressTimer = undefined;
      pressPoint = null;
    };

    const onContextMenu = (event: MouseEvent) => {
      // A right click on the open menu belongs to it, not to the page under it:
      // the browser's menu stays away and ours is not rebuilt at the pointer.
      if (inside(event.target, menuRef.current)) {
        event.preventDefault();
        return;
      }
      if (isEditable(event.target)) return;
      event.preventDefault();
      // Android reports the long press as a contextmenu event as well; the
      // timer has already opened the menu for that same gesture.
      if (Date.now() - openedByTouchAt < 900) return;
      openAt(event.clientX, event.clientY, event.target);
    };

    const onTouchStart = (event: TouchEvent) => {
      cancelPress();
      suppressInsideClick = false;
      insideHoldStartedAt = 0;
      if (inside(event.target, menuRef.current)) {
        // Keep the menu exactly as it is; only remember how long the press was,
        // so a long one does not end up choosing the row underneath.
        insideHoldStartedAt = Date.now();
        return;
      }
      if (event.touches.length !== 1 || isEditable(event.target)) return;
      const touch = event.touches[0];
      const target = event.target;
      const point = { x: touch.clientX, y: touch.clientY };
      pressPoint = point;
      pressTimer = window.setTimeout(() => {
        pressTimer = undefined;
        pressPoint = null;
        openedByTouchAt = Date.now();
        navigator.vibrate?.(10);
        openAt(point.x, point.y, target, true);
      }, LONG_PRESS_MS);
    };

    const onTouchMove = (event: TouchEvent) => {
      const touch = event.touches[0];
      if (!pressPoint || !touch) return;
      if (Math.hypot(touch.clientX - pressPoint.x, touch.clientY - pressPoint.y) > MOVE_TOLERANCE) {
        cancelPress();
      }
    };

    // The press ends with the menu already up: the click that follows belongs to
    // the gesture, not to the link or button underneath it.
    const onTouchEnd = () => {
      if (insideHoldStartedAt && Date.now() - insideHoldStartedAt >= LONG_PRESS_MS) suppressInsideClick = true;
      insideHoldStartedAt = 0;
      if (openedByTouchAt && Date.now() - openedByTouchAt < 600) suppressClickUntil = Date.now() + 450;
      cancelPress();
    };

    const onClick = (event: MouseEvent) => {
      // A press held on a row is not a tap on it.
      if (suppressInsideClick && inside(event.target, menuRef.current)) {
        suppressInsideClick = false;
        event.preventDefault();
        event.stopPropagation();
        return;
      }
      suppressInsideClick = false;
      // The menu's own rows are pressed right after the finger lifts, so they
      // keep their clicks; only the page underneath loses the one tap.
      if (inside(event.target, menuRef.current)) {
        suppressClickUntil = 0;
        return;
      }
      if (suppressClickUntil && Date.now() < suppressClickUntil) {
        suppressClickUntil = 0;
        event.preventDefault();
        event.stopPropagation();
      }
    };

    document.addEventListener("contextmenu", onContextMenu);
    document.addEventListener("touchstart", onTouchStart, { passive: true });
    document.addEventListener("touchmove", onTouchMove, { passive: true });
    document.addEventListener("touchend", onTouchEnd, { passive: true });
    document.addEventListener("touchcancel", cancelPress, { passive: true });
    window.addEventListener("click", onClick, true);
    return () => {
      document.removeEventListener("contextmenu", onContextMenu);
      document.removeEventListener("touchstart", onTouchStart);
      document.removeEventListener("touchmove", onTouchMove);
      document.removeEventListener("touchend", onTouchEnd);
      document.removeEventListener("touchcancel", cancelPress);
      window.removeEventListener("click", onClick, true);
      cancelPress();
    };
  }, [openAt]);

  // Place the menu at the pointer and keep it inside the window. It is measured
  // before it is shown, so it never flashes half off-screen next to the cursor.
  /**
   * Where the card sits this frame.
   *
   * The anchor is kept in page coordinates, so it moves with the content; the
   * card is then drawn at that point and clamped to the window, exactly like the
   * profile popups. Scrolling carries it along until it reaches the top or the
   * side of the screen, and from there it stays put at the edge instead of
   * sliding out of reach.
   */
  const place = useCallback(() => {
    const element = menuRef.current;
    if (!menu || !element) return;
    const size = element.getBoundingClientRect();
    // `clientWidth`/`clientHeight` leave the scrollbar out, so the menu never
    // tucks underneath it on a desktop, and they follow the visible area on a
    // phone the way `innerHeight` does not.
    const root = document.documentElement;
    const anchorLeft = menu.x - window.scrollX;
    const anchorTop = menu.y - window.scrollY;
    const wantedTop = menu.above ? anchorTop - size.height : anchorTop;
    const maxLeft = Math.max(EDGE, root.clientWidth - size.width - EDGE);
    const maxTop = Math.max(EDGE, root.clientHeight - size.height - EDGE);
    // Whole pixels: a menu on a half pixel renders its labels soft.
    const left = Math.round(Math.min(Math.max(anchorLeft, EDGE), maxLeft));
    const top = Math.round(Math.min(Math.max(wantedTop, EDGE), maxTop));
    // Grow from the corner nearest the press. Opened upwards, or pushed up
    // from the bottom edge, it should rise into place rather than drop in.
    const origin = `${anchorLeft > maxLeft ? "right" : "left"} ${menu.above || wantedTop > maxTop ? "bottom" : "top"}`;
    // Scrolling re-places every frame; only re-render when the card really moves.
    setPosition((current) =>
      current && current.left === left && current.top === top && current.origin === origin
        ? current
        : { left, top, origin },
    );
  }, [menu]);

  useLayoutEffect(() => {
    place();
  }, [place]);

  // Focused once, as soon as it is on screen: a hidden element cannot take
  // focus, and without focus the arrow keys and Enter never reach the menu. A
  // scroll moves the card, not the visitor's attention, so it is not repeated.
  const focusedFor = useRef<OpenMenu | null>(null);
  useLayoutEffect(() => {
    if (!position || focusedFor.current === menu) return;
    focusedFor.current = menu;
    menuRef.current?.focus({ preventScroll: true });
  }, [position, menu]);

  // A tap elsewhere or Escape dismisses, the way a menu should. The page moving
  // is not a reason to lose it.
  useEffect(() => {
    if (!menu) return;
    // Dismissal follows a tap, not a touch. Every scroll on a phone begins by
    // pressing the page, so closing on the press took the card away the instant
    // the visitor scrolled — which is why a long selection kept losing its
    // Copy. A press that lifts where it landed is a tap and does dismiss, the
    // same as a click on a desktop; a drag or a scroll changes nothing.
    let pressOrigin: { x: number; y: number } | null = null;
    const onPointerDown = (event: PointerEvent) => {
      // A second finger is a pinch or a two-finger scroll, never a tap.
      if (!event.isPrimary || inside(event.target, menuRef.current)) {
        pressOrigin = null;
        return;
      }
      pressOrigin = { x: event.clientX, y: event.clientY };
    };
    const onPointerUp = (event: PointerEvent) => {
      const origin = pressOrigin;
      pressOrigin = null;
      if (!origin || !event.isPrimary || inside(event.target, menuRef.current)) return;
      if (Math.hypot(event.clientX - origin.x, event.clientY - origin.y) > MOVE_TOLERANCE) return;
      close();
    };
    const clearPress = () => {
      pressOrigin = null;
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.preventDefault();
      close(true);
    };
    const dismiss = () => close();
    // Scrolling is never a dismissal: the card follows the page and then waits
    // at the edge of the window. Re-placing happens on the next frame, so a
    // fast flick updates once per paint instead of once per scroll event.
    let frame = 0;
    const follow = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(() => {
        frame = 0;
        place();
      });
    };
    window.addEventListener("scroll", follow, { passive: true, capture: true });
    window.addEventListener("resize", follow);
    document.addEventListener("pointerdown", onPointerDown, true);
    document.addEventListener("pointerup", onPointerUp, true);
    document.addEventListener("pointercancel", clearPress, true);
    document.addEventListener("keydown", onKeyDown, true);
    window.addEventListener("blur", dismiss);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown, true);
      document.removeEventListener("pointerup", onPointerUp, true);
      document.removeEventListener("pointercancel", clearPress, true);
      document.removeEventListener("keydown", onKeyDown, true);
      window.removeEventListener("scroll", follow, true);
      window.removeEventListener("resize", follow);
      window.removeEventListener("blur", dismiss);
      if (frame) window.cancelAnimationFrame(frame);
    };
  }, [menu, close, place]);

  // A phone often decides which word was pressed a moment after the press
  // itself, so the selection can arrive after the card is already open. When it
  // does, the Copy row appears (and the card steps above the words), instead of
  // leaving a long drag with nothing to press — the phone's own Copy is gone by
  // then, on purpose.
  useEffect(() => {
    if (!menu) return;
    const sync = () => {
      if (menu.items.some((item) => item.key === "copy-selection")) return;
      const selection = window.getSelection();
      const text = selection?.toString().trim() ?? "";
      if (!selection || !text || selection.rangeCount === 0) return;
      const words = selection.getRangeAt(0).getBoundingClientRect();
      const copyItem: MenuItem = {
        key: "copy-selection",
        label: t("contextMenu.copy"),
        icon: "copy",
        action: () => copy(window.getSelection()?.toString().trim() || text),
      };
      setMenu((current) => {
        if (!current || current.items.some((item) => item.key === "copy-selection")) return current;
        const anchored =
          words.width || words.height
            ? { x: words.left + window.scrollX, y: words.top - 6 + window.scrollY, above: true }
            : {};
        return { ...current, ...anchored, items: [copyItem, ...current.items] };
      });
      setHighlighted(0);
    };
    document.addEventListener("selectionchange", sync);
    return () => document.removeEventListener("selectionchange", sync);
  }, [menu, copy, t]);

  // A short menu rarely scrolls, but on a phone in landscape it can: the row the
  // keys moved to has to stay in view. Scrolls the menu itself only — the page
  // must not jump back to a card that has been scrolled away from.
  useEffect(() => {
    const element = menuRef.current;
    const row = element?.querySelector<HTMLElement>(".context-menu-item.is-highlighted");
    if (!element || !row || element.scrollHeight <= element.clientHeight) return;
    if (row.offsetTop < element.scrollTop) element.scrollTop = row.offsetTop;
    else if (row.offsetTop + row.offsetHeight > element.scrollTop + element.clientHeight) {
      element.scrollTop = row.offsetTop + row.offsetHeight - element.clientHeight;
    }
  }, [highlighted, menu]);

  const onMenuKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>) => {
    if (!menu) return;
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const step = event.key === "ArrowDown" ? 1 : -1;
      setHighlighted((current) => (current + step + menu.items.length) % menu.items.length);
    } else if (event.key === "Home" || event.key === "End") {
      event.preventDefault();
      setHighlighted(event.key === "Home" ? 0 : menu.items.length - 1);
    } else if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      run(menu.items[highlighted]);
    } else if (event.key === "Tab") {
      close(true);
    }
  };

  if (!menu) return null;

  return createPortal(
    <div
      ref={menuRef}
      className="context-menu"
      role="menu"
      aria-label={t("contextMenu.label")}
      aria-activedescendant={position ? `${idPrefix}-${menu.items[highlighted].key}` : undefined}
      tabIndex={-1}
      style={
        {
          left: position?.left ?? menu.x,
          top: position?.top ?? menu.y,
          visibility: position ? "visible" : "hidden",
          transformOrigin: position?.origin,
          "--context-menu-shift": position?.origin.endsWith("bottom") ? "3px" : "-3px",
        } as CSSProperties
      }
      onKeyDown={onMenuKeyDown}
    >
      {/* Rows and rules are direct children: a plain wrapper between the menu
          and its items is one element screen readers have to skip. */}
      {menu.items.map((item, index) => (
        <Fragment key={item.key}>
          {item.divider && <div className="context-menu-separator" role="separator" />}
          <button
            id={`${idPrefix}-${item.key}`}
            type="button"
            role="menuitem"
            tabIndex={-1}
            className={`context-menu-item${index === highlighted ? " is-highlighted" : ""}`}
            onPointerEnter={() => setHighlighted(index)}
            onClick={() => run(item)}
          >
            <Icon name={item.icon} size={14} />
            <span>{item.label}</span>
          </button>
        </Fragment>
      ))}
    </div>,
    document.body,
  );
}
