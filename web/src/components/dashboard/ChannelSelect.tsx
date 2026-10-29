import { type CSSProperties, type KeyboardEvent as ReactKeyboardEvent, useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import type { GuildResources } from "../../types";

type Channel = GuildResources["channels"][number];

type Props = {
  channels: Channel[];
  value: string;
  onChange: (value: string) => void;
  /** Label for the empty choice; pass null to make a channel mandatory. */
  placeholder?: string | null;
  ariaLabel?: string;
  disabled?: boolean;
  id?: string;
};

// Channel types as the bot reports them, mapped onto Discord's own icon set.
const CHANNEL_ICONS: Record<string, string> = {
  text: "text-channel",
  news: "announcement-channel",
  forum: "forum-channel",
  media: "media-channel",
  voice: "voice-channel",
  stage_voice: "stage-channel",
  public_thread: "thread",
  private_thread: "thread",
  announcement_thread: "thread",
};

function iconName(channel: Channel | undefined) {
  if (!channel) return "cross";
  return CHANNEL_ICONS[channel.type || ""] || "text-channel";
}

function glyphStyle(name: string) {
  return { "--mask-icon": `url(/assets/discord-icons/from-discord/${name}.svg)` } as CSSProperties;
}

/**
 * A channel picker built on Discord's own channel icons. A native `<select>`
 * cannot hold images, so the list is a custom popup while the trigger keeps the
 * form-field shape every other settings control uses.
 */
export function ChannelSelect({ channels, value, onChange, placeholder = "Choose a channel", ariaLabel, disabled, id }: Props) {
  const [open, setOpen] = useState(false);
  const [highlighted, setHighlighted] = useState(-1);
  const rootRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const options = useMemo(() => {
    const known = channels.some((channel) => String(channel.id) === String(value));
    if (!value || known) return channels;
    // A saved channel the bot can no longer list stays selectable.
    return [{ id: value, name: `Saved channel · ${value}` }, ...channels];
  }, [channels, value]);

  const entries = useMemo(() => [
    ...(placeholder === null ? [] : [{ id: "", name: placeholder, type: "" }]),
    ...options,
  ], [options, placeholder]);

  const selected = options.find((channel) => String(channel.id) === String(value));
  const selectedIndex = entries.findIndex((entry) => String(entry.id) === String(value));

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      if (event.target instanceof Node && rootRef.current?.contains(event.target)) return;
      setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [open]);

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
      if (entries[highlighted]) choose(String(entries[highlighted].id));
    }
  };

  return <div className={`channel-select${open ? " is-open" : ""}`} ref={rootRef}>
    <button
      type="button"
      id={id}
      ref={buttonRef}
      className="channel-select-trigger"
      aria-haspopup="listbox"
      aria-expanded={open}
      aria-label={ariaLabel}
      disabled={disabled}
      onClick={() => (open ? setOpen(false) : openList())}
      onKeyDown={onKeyDown}
    >
      <span className={`mask-icon channel-select-glyph${selected ? "" : " is-empty"}`} style={glyphStyle(iconName(selected))} aria-hidden="true" />
      <span className={`channel-select-value${selected ? "" : " is-placeholder"}`}>
        {selected ? `#${selected.name}` : placeholder ?? "Choose a channel"}
      </span>
      <ChevronDown className="channel-select-chevron" size={14} aria-hidden="true" />
    </button>
    {open && <div className="channel-select-list" role="listbox" aria-label={ariaLabel} ref={listRef}>
      {entries.map((entry, index) => {
        const isSelected = String(entry.id) === String(value);
        return <button
          type="button"
          role="option"
          aria-selected={isSelected}
          tabIndex={-1}
          data-index={index}
          key={entry.id || "none"}
          className={`channel-select-option${isSelected ? " is-selected" : ""}${index === highlighted ? " is-highlighted" : ""}`}
          onMouseEnter={() => setHighlighted(index)}
          onClick={() => choose(String(entry.id))}
        >
          <span className={`mask-icon channel-select-glyph${entry.id ? "" : " is-empty"}`} style={glyphStyle(iconName(entry.id ? entry : undefined))} aria-hidden="true" />
          <span className="channel-select-value">{entry.id ? `#${entry.name}` : entry.name}</span>
          {isSelected && <span className="channel-select-check" aria-hidden="true">✓</span>}
        </button>;
      })}
    </div>}
  </div>;
}
