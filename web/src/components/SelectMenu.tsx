import { useEffect, useRef, useState } from "react";
import { Icon } from "./Icon";

export type SelectOption<T extends string = string> = {
  value: T;
  label: string;
  /** Short code shown in the closed trigger, e.g. "EN". */
  code?: string;
  /** Optional second line inside the list. */
  note?: string;
};

/**
 * The site's own dropdown.
 *
 * A native <select> cannot be styled to match anything else on the page and
 * cannot carry a code, a note or an icon per row, so this is a small listbox
 * built out of buttons: one trigger, a popup of options, and the arrow/Home/End
 * keys, Escape and click-outside behaving the way a select should. It takes any
 * option list, so more languages or other pickers can share it.
 */
export function SelectMenu<T extends string>({
  label,
  value,
  options,
  onChange,
  compact = false,
}: {
  label: string;
  value: T;
  options: SelectOption<T>[];
  onChange: (value: T) => void;
  compact?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const rootRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const optionRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const selected = options.find((option) => option.value === value) ?? options[0];

  useEffect(() => {
    if (!open) return;
    optionRefs.current[active]?.focus();
  }, [open, active]);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      if (event.target instanceof Node && rootRef.current?.contains(event.target)) return;
      setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [open]);

  const openList = (index?: number) => {
    setActive(index ?? Math.max(0, options.findIndex((option) => option.value === value)));
    setOpen(true);
  };

  const choose = (option: SelectOption<T>) => {
    onChange(option.value);
    setOpen(false);
    triggerRef.current?.focus();
  };

  const move = (delta: number) => setActive((index) => (index + delta + options.length) % options.length);

  return (
    <div className={`select-menu${compact ? " select-menu-compact" : ""}`} ref={rootRef}>
      <button
        ref={triggerRef}
        type="button"
        className="select-menu-trigger"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={`${label}: ${selected.label}`}
        onClick={() => (open ? setOpen(false) : openList())}
        onKeyDown={(event) => {
          if (event.key === "ArrowDown") { event.preventDefault(); openList(); }
          else if (event.key === "ArrowUp") { event.preventDefault(); openList(); }
          else if (event.key === "Escape") setOpen(false);
        }}
      >
        {selected.code ? <span className="select-menu-code">{selected.code}</span> : null}
        <span className="select-menu-value">{selected.label}</span>
        <svg className="select-menu-chevron" viewBox="0 0 12 12" aria-hidden="true" focusable="false">
          <path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {open && (
        <div
          className="select-menu-list"
          role="listbox"
          aria-label={label}
          onKeyDown={(event) => {
            if (event.key === "ArrowDown") { event.preventDefault(); move(1); }
            else if (event.key === "ArrowUp") { event.preventDefault(); move(-1); }
            else if (event.key === "Home") { event.preventDefault(); setActive(0); }
            else if (event.key === "End") { event.preventDefault(); setActive(options.length - 1); }
            else if (event.key === "Escape") { event.preventDefault(); setOpen(false); triggerRef.current?.focus(); }
            else if (event.key === "Tab") setOpen(false);
          }}
        >
          {options.map((option, index) => (
            <button
              key={option.value}
              ref={(node) => { optionRefs.current[index] = node; }}
              type="button"
              role="option"
              aria-selected={option.value === value}
              tabIndex={index === active ? 0 : -1}
              className={`select-menu-option${option.value === value ? " is-selected" : ""}`}
              onClick={() => choose(option)}
            >
              <span className="select-menu-option-copy">
                <span className="select-menu-option-label">{option.label}</span>
                {option.note ? <small>{option.note}</small> : null}
              </span>
              {option.value === value ? <Icon name="check" /> : null}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
