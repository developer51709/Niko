import { type KeyboardEvent as ReactKeyboardEvent, type ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ChevronDown } from "lucide-react";
import { useStrings } from "../../i18n";

export type SelectOption = {
  value: string;
  label: string;
  /** Mark drawn before the label, in the trigger and in the row. */
  glyph?: ReactNode;
};

/** Builds options from a plain `[value, label]` list. */
export const selectOptions = (pairs: [string, string][]): SelectOption[] =>
  pairs.map(([value, label]) => ({ value, label }));

/**
 * Resolves a key-labelled option list into display text. Enum lists keep
 * catalogue keys, so a dropdown stays translated whenever it is rendered.
 */
export const localizeOptions = (options: SelectOption[], t: (key: string) => string): SelectOption[] =>
  options.map((option) => ({ ...option, label: t(option.label) }));

type Props = {
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  /** Text for the "nothing chosen" row; `null` makes a choice mandatory. */
  placeholder?: string | null;
  /** Mark for the "nothing chosen" row. */
  placeholderGlyph?: ReactNode;
  /**
   * Builds a row for a saved value that the options list no longer contains, so
   * an unset channel or a deleted role stays visible and selectable.
   */
  unknownOption?: (value: string) => SelectOption;
  ariaLabel?: string;
  disabled?: boolean;
  id?: string;
  /**
   * Extra class on the portalled list, for a surface that lives in its own
   * layer and needs the list above it (the owner devtools panel, for one).
   */
  listClassName?: string;
};

/**
 * The one dropdown behind every single-choice control on the dashboard.
 *
 * A native `<select>` cannot be styled to match the rest of the dashboard and
 * cannot carry a channel icon or a role dot, so the list is a popup of buttons:
 * a trigger, arrow/Enter/Escape handling, a highlight that follows the pointer
 * and a tick on the chosen row. Callers only supply options; `ChannelSelect`
 * and `RolePicker` add their own glyphs to it instead of re-implementing it.
 *
 * The list renders in a portal anchored to the trigger: settings cards carry a
 * backdrop-filter, which makes each card its own stacking context, so a list
 * drawn inside a card would paint underneath the card below it.
 */
export function Select({ options, value, onChange, placeholder, placeholderGlyph, unknownOption, ariaLabel, disabled, id, listClassName }: Props) {
  const { t } = useStrings("dashboard");
  const resolvedPlaceholder = placeholder === undefined ? t("pickers.chooseOption") : placeholder;
  const [open, setOpen] = useState(false);
  const [highlighted, setHighlighted] = useState(-1);
  const [position, setPosition] = useState<{ top: number; left: number; width: number } | null>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const known = options.some((option) => option.value === value);
  const entries = [
    ...(resolvedPlaceholder === null ? [] : [{ value: "", label: resolvedPlaceholder, glyph: placeholderGlyph }]),
    ...(value && !known && unknownOption ? [unknownOption(value)] : []),
    ...options,
  ];
  const chosen = entries.find((entry) => entry.value === value) ?? null;
  const selectedIndex = entries.findIndex((entry) => entry.value === value);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      const target = event.target;
      if (target instanceof Node && (rootRef.current?.contains(target) || listRef.current?.contains(target))) return;
      setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [open]);

  // Anchor the list to its trigger, flipping above and clamping inside the
  // viewport so it stays reachable on short screens and in narrow columns.
  useLayoutEffect(() => {
    if (!open) return;
    const place = () => {
      const trigger = buttonRef.current;
      const list = listRef.current;
      if (!trigger || !list) return;
      const anchor = trigger.getBoundingClientRect();
      const size = list.getBoundingClientRect();
      const gap = 6;
      const pad = 12;
      let top = anchor.bottom + gap;
      if (top + size.height > window.innerHeight - pad && anchor.top - gap - size.height >= pad) {
        top = anchor.top - gap - size.height;
      }
      const width = Math.min(anchor.width, window.innerWidth - pad * 2);
      setPosition({
        top: Math.max(pad, Math.min(top, window.innerHeight - pad - size.height)),
        left: Math.min(Math.max(pad, anchor.left), Math.max(pad, window.innerWidth - pad - width)),
        width,
      });
    };
    place();
    window.addEventListener("scroll", place, true);
    window.addEventListener("resize", place);
    return () => {
      window.removeEventListener("scroll", place, true);
      window.removeEventListener("resize", place);
    };
  }, [open, entries.length]);

  useEffect(() => {
    setOpen(false);
  }, [disabled]);

  useEffect(() => {
    if (!open || highlighted < 0) return;
    const option = listRef.current?.querySelector<HTMLElement>(`[data-index="${highlighted}"]`);
    option?.scrollIntoView({ block: "nearest" });
  }, [open, highlighted]);

  const openList = (from?: number) => {
    if (disabled) return;
    setPosition(null);
    setHighlighted(from ?? (selectedIndex >= 0 ? selectedIndex : 0));
    setOpen(true);
  };

  const choose = (next: string) => {
    onChange(next);
    setOpen(false);
    buttonRef.current?.focus();
  };

  const onKeyDown = (event: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (!open) {
      if (event.key === "ArrowDown" || event.key === "ArrowUp" || event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openList();
      }
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      setOpen(false);
      return;
    }
    if (event.key === "Tab") {
      setOpen(false);
      return;
    }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const step = event.key === "ArrowDown" ? 1 : -1;
      setHighlighted((current) => {
        const start = current < 0 ? selectedIndex : current;
        return Math.max(0, Math.min(entries.length - 1, start + step));
      });
      return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      const entry = entries[highlighted];
      if (entry) choose(entry.value);
    }
  };

  return <div className={`dash-select${open ? " is-open" : ""}`} ref={rootRef}>
    <button
      type="button"
      id={id}
      ref={buttonRef}
      className="dash-select-trigger"
      aria-haspopup="listbox"
      aria-expanded={open}
      aria-label={ariaLabel}
      disabled={disabled}
      onClick={() => (open ? setOpen(false) : openList())}
      onKeyDown={onKeyDown}
    >
      {chosen?.glyph}
      <span className={`dash-select-value${value ? "" : " is-placeholder"}`}>{chosen?.label ?? ""}</span>
      <ChevronDown className="dash-select-chevron" size={14} aria-hidden="true" />
    </button>
    {open && createPortal(<div
      className={`dash-select-list${listClassName ? ` ${listClassName}` : ""}`}
      role="listbox"
      aria-label={ariaLabel}
      ref={listRef}
      style={{
        top: position?.top ?? 0,
        left: position?.left ?? 0,
        width: position?.width,
        visibility: position ? "visible" : "hidden",
      }}
    >
      {entries.map((entry, index) => {
        const isSelected = entry.value === value;
        return <button
          type="button"
          role="option"
          aria-selected={isSelected}
          tabIndex={-1}
          data-index={index}
          key={entry.value || "none"}
          className={`dash-select-option${isSelected ? " is-selected" : ""}${index === highlighted ? " is-highlighted" : ""}`}
          onMouseEnter={() => setHighlighted(index)}
          onClick={() => choose(entry.value)}
        >
          {entry.glyph}
          <span className="dash-select-value">{entry.label}</span>
          {isSelected && <span className="dash-select-check" aria-hidden="true">✓</span>}
        </button>;
      })}
    </div>, document.body)}
  </div>;
}
