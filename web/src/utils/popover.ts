/** Where a floating popup sits on screen, in viewport coordinates. */
export type PopupPosition = { left: number; top: number };

/** Room kept between the popup and the edge of the window. */
const MARGIN = 12;

/** Room between the trigger and the popup. */
const GAP = 8;

/**
 * Place a popup next to the element that opened it.
 *
 * It hangs under the trigger and flips above it when the bottom of the window
 * is too close, then both edges are clamped so the popup stays fully visible.
 * `align` decides whether the popup is centred on the trigger (badges, emoji,
 * server tags) or lines up with its left edge (profile cards, which would
 * otherwise sit half a card off to the side of the name they belong to).
 *
 * Shared by the public profile popups and every popup that reuses them, so the
 * placement rules only exist once.
 */
export function placePopup(
  trigger: HTMLElement,
  popup: HTMLElement,
  align: "center" | "start" = "center",
): PopupPosition {
  const rect = trigger.getBoundingClientRect();
  const width = popup.offsetWidth;
  const height = popup.offsetHeight;
  const left = align === "center" ? rect.left + rect.width / 2 - width / 2 : rect.left;
  const below = rect.bottom + GAP;
  const top = below + height <= window.innerHeight - MARGIN
    ? below
    : Math.max(MARGIN, rect.top - height - GAP);
  return {
    left: Math.max(MARGIN, Math.min(left, window.innerWidth - width - MARGIN)),
    top: Math.min(top, window.innerHeight - height - MARGIN),
  };
}
