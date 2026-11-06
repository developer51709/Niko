import { useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";
import { Icon } from "../Icon";

type Props = {
  open: boolean;
  title: string;
  /** What the action does, in the space of a sentence or two. */
  body: string;
  confirmLabel: string;
  cancelLabel: string;
  /** A destructive action paints its button red instead of neutral. */
  danger?: boolean;
  /** The action is running, so neither button may fire again. */
  busy?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

/**
 * The dashboard's own confirmation prompt.
 *
 * A browser `confirm()` cannot be styled, ignores the site's theme and blocks
 * the page, so a destructive action asks in a glass card over the app instead:
 * Escape or the backdrop cancels, the safe button takes focus, and the
 * destructive one only fires on an explicit click or Enter on itself.
 */
export function ConfirmDialog({
  open,
  title,
  body,
  confirmLabel,
  cancelLabel,
  danger = false,
  busy = false,
  onConfirm,
  onCancel,
}: Props) {
  const headingId = useId();
  const bodyId = useId();
  const cancelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    const handle = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        if (!busy) onCancel();
      }
    };
    document.addEventListener("keydown", handle);
    cancelRef.current?.focus({ preventScroll: true });
    return () => document.removeEventListener("keydown", handle);
  }, [open, busy, onCancel]);

  if (!open) return null;

  return createPortal(
    <div
      className="confirm-backdrop"
      onMouseDown={(event) => {
        // Only a click that starts and ends on the backdrop dismisses: a drag
        // out of the card (selecting the traceback text) must not cancel it.
        if (event.target === event.currentTarget && !busy) onCancel();
      }}
    >
      <div
        className="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={headingId}
        aria-describedby={bodyId}
      >
        <span className="confirm-dialog-mark" aria-hidden="true">
          <Icon name={danger ? "alert" : "check"} size={18} />
        </span>
        <h2 id={headingId}>{title}</h2>
        <p id={bodyId}>{body}</p>
        <div className="confirm-dialog-actions">
          <button
            ref={cancelRef}
            type="button"
            className="button button-muted"
            onClick={onCancel}
            disabled={busy}
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            className={`button ${danger ? "button-danger" : "button-primary"}`}
            onClick={onConfirm}
            disabled={busy}
          >
            {busy ? `${confirmLabel}…` : confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
