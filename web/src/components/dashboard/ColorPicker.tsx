import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Check, ChevronsUpDown, Pipette } from "lucide-react";

/**
 * Colour picker popover, ported from the 21st.dev colour picker to this
 * project's CSS system (no Tailwind/shadcn here).
 *
 * HSV is the internal source of truth so dragging through pure black or pure
 * white does not discard the hue the way a hex round-trip would. The value the
 * caller stores stays the six-digit lowercase hex this dashboard already saves.
 */

export interface Hsva {
  h: number;
  s: number;
  v: number;
  a: number;
}

export interface Rgba {
  r: number;
  g: number;
  b: number;
  a: number;
}

const clamp = (n: number, min = 0, max = 100) => Math.min(max, Math.max(min, n));

const round = (n: number, digits = 0) => {
  const p = 10 ** digits;
  return Math.round(n * p) / p;
};

function hsvaToRgba({ h, s, v, a }: Hsva): Rgba {
  const hh = (((h % 360) + 360) % 360) / 60;
  const ss = s / 100;
  const vv = v / 100;
  const c = vv * ss;
  const x = c * (1 - Math.abs((hh % 2) - 1));
  const m = vv - c;
  const seg = Math.floor(hh) % 6;
  const segments: readonly (readonly [number, number, number])[] = [
    [c, x, 0],
    [x, c, 0],
    [0, c, x],
    [0, x, c],
    [x, 0, c],
    [c, 0, x],
  ];
  const [r, g, b] = segments[seg] ?? segments[0]!;
  return {
    r: Math.round((r + m) * 255),
    g: Math.round((g + m) * 255),
    b: Math.round((b + m) * 255),
    a,
  };
}

function rgbaToHsva({ r, g, b, a }: Rgba): Hsva {
  const rr = r / 255;
  const gg = g / 255;
  const bb = b / 255;
  const max = Math.max(rr, gg, bb);
  const min = Math.min(rr, gg, bb);
  const d = max - min;
  let h = 0;
  if (d !== 0) {
    if (max === rr) h = 60 * (((gg - bb) / d) % 6);
    else if (max === gg) h = 60 * ((bb - rr) / d + 2);
    else h = 60 * ((rr - gg) / d + 4);
  }
  if (h < 0) h += 360;
  return {
    h: round(h, 1),
    s: max === 0 ? 0 : round((d / max) * 100, 1),
    v: round(max * 100, 1),
    a,
  };
}

function hsvaToHsl({ h, s, v }: Hsva) {
  const vv = v / 100;
  const ss = s / 100;
  const l = vv * (1 - ss / 2);
  const sl = l === 0 || l === 1 ? 0 : (vv - l) / Math.min(l, 1 - l);
  return { h: Math.round(h), s: Math.round(sl * 100), l: Math.round(l * 100) };
}

function hslToHsva(h: number, s: number, l: number, a: number): Hsva {
  const ll = l / 100;
  const ss = s / 100;
  const v = ll + ss * Math.min(ll, 1 - ll);
  return {
    h: ((h % 360) + 360) % 360,
    s: v === 0 ? 0 : 2 * (1 - ll / v) * 100,
    v: v * 100,
    a,
  };
}

const hex2 = (n: number) =>
  Math.round(clamp(n, 0, 255)).toString(16).padStart(2, "0");

export function rgbaToHex({ r, g, b, a }: Rgba, withAlpha = false): string {
  const base = `#${hex2(r)}${hex2(g)}${hex2(b)}`;
  if (!withAlpha || a >= 1) return base;
  return `${base}${hex2(a * 255)}`;
}

/** Parses `#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa` (the `#` is optional). */
export function parseHex(input: string): Rgba | null {
  const raw = input.trim().replace(/^#/, "");
  if (!/^([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})$/i.test(raw)) return null;
  const full =
    raw.length <= 4
      ? raw
          .split("")
          .map((c) => c + c)
          .join("")
      : raw;
  return {
    r: parseInt(full.slice(0, 2), 16),
    g: parseInt(full.slice(2, 4), 16),
    b: parseInt(full.slice(4, 6), 16),
    a: full.length === 8 ? parseInt(full.slice(6, 8), 16) / 255 : 1,
  };
}

/** WCAG relative luminance, used to pick a readable mark over a swatch. */
function isLightColor({ r, g, b }: Rgba) {
  const channel = (c: number) => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b) > 0.45;
}

function hsvaToCss(hsva: Hsva, withAlpha: boolean) {
  const { r, g, b, a } = hsvaToRgba(hsva);
  return withAlpha ? `rgba(${r}, ${g}, ${b}, ${round(a, 2)})` : `rgb(${r}, ${g}, ${b})`;
}

/* ─── shared behaviour ──────────────────────────────────────── */

type ColorFormat = "hex" | "rgb" | "hsl";

const FORMAT_ORDER: ColorFormat[] = ["hex", "rgb", "hsl"];

const DEFAULT_COLOR = "#5865f2";

/** Discord-friendly presets: blurple, the status colours, and a few accents. */
export const DEFAULT_SWATCHES = [
  "#5865f2",
  "#57f287",
  "#fee75c",
  "#eb459e",
  "#ed4245",
  "#1abc9c",
  "#3498db",
  "#9b59b6",
];

/** Maps a pointer event to 0..1 coordinates inside `el`. */
function pointerRatio(el: HTMLElement, event: { clientX: number; clientY: number }) {
  const rect = el.getBoundingClientRect();
  return {
    x: rect.width === 0 ? 0 : clamp((event.clientX - rect.left) / rect.width, 0, 1),
    y: rect.height === 0 ? 0 : clamp((event.clientY - rect.top) / rect.height, 0, 1),
  };
}

function useDrag(
  onMove: (el: HTMLElement, event: { clientX: number; clientY: number }) => void,
  disabled?: boolean,
) {
  const [dragging, setDragging] = useState(false);

  const onPointerDown = useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      if (disabled || event.button !== 0) return;
      const el = event.currentTarget;
      el.setPointerCapture(event.pointerId);
      setDragging(true);
      el.focus();
      onMove(el, event);
    },
    [disabled, onMove],
  );

  const onPointerMove = useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      if (!dragging) return;
      event.preventDefault();
      onMove(event.currentTarget, event);
    },
    [dragging, onMove],
  );

  const stop = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    setDragging(false);
  }, []);

  return { dragging, handlers: { onPointerDown, onPointerMove, onPointerUp: stop, onPointerCancel: stop } };
}

/** Arrow/Page/Home/End stepping shared by the canvas and both rails. */
function arrowStep(key: string, step: number, big: number): { dx: number; dy: number } | null {
  switch (key) {
    case "ArrowLeft":
      return { dx: -step, dy: 0 };
    case "ArrowRight":
      return { dx: step, dy: 0 };
    case "ArrowUp":
      return { dx: 0, dy: step };
    case "ArrowDown":
      return { dx: 0, dy: -step };
    case "PageUp":
      return { dx: big, dy: big };
    case "PageDown":
      return { dx: -big, dy: -big };
    default:
      return null;
  }
}

/* ─── saturation / value canvas ─────────────────────────────── */

function SaturationCanvas({
  hsva,
  onChange,
  disabled,
}: {
  hsva: Hsva;
  onChange: (next: { s: number; v: number }) => void;
  disabled?: boolean;
}) {
  const apply = useCallback(
    (el: HTMLElement, event: { clientX: number; clientY: number }) => {
      const { x, y } = pointerRatio(el, event);
      onChange({ s: round(x * 100, 1), v: round((1 - y) * 100, 1) });
    },
    [onChange],
  );

  const { dragging, handlers } = useDrag(apply, disabled);

  const onKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (disabled) return;
    if (event.key === "Home" || event.key === "End") {
      event.preventDefault();
      onChange(event.key === "Home" ? { s: 0, v: 100 } : { s: 100, v: 100 });
      return;
    }
    const delta = arrowStep(event.key, event.shiftKey ? 10 : 1, 10);
    if (!delta) return;
    event.preventDefault();
    onChange({ s: clamp(hsva.s + delta.dx), v: clamp(hsva.v + delta.dy) });
  };

  return (
    <div
      role="slider"
      aria-label="Saturation and brightness"
      aria-valuetext={`Saturation ${Math.round(hsva.s)}%, brightness ${Math.round(hsva.v)}%`}
      aria-disabled={disabled || undefined}
      data-dragging={dragging || undefined}
      tabIndex={disabled ? -1 : 0}
      onKeyDown={onKeyDown}
      {...handlers}
      className="color-picker-canvas"
      style={{ backgroundColor: `hsl(${hsva.h} 100% 50%)` }}
    >
      <span
        className="color-picker-thumb color-picker-thumb-canvas"
        style={{
          // Half a thumb of padding so the mark never clips at the corners.
          left: `clamp(8px, ${hsva.s}%, calc(100% - 8px))`,
          top: `clamp(8px, ${100 - hsva.v}%, calc(100% - 8px))`,
          backgroundColor: hsvaToCss({ ...hsva, a: 1 }, false),
        }}
      />
    </div>
  );
}

/* ─── rails ─────────────────────────────────────────────────── */

function Rail({
  label,
  value,
  max,
  step = 1,
  valueText,
  trackStyle,
  thumbColor,
  onChange,
  disabled,
}: {
  label: string;
  value: number;
  max: number;
  step?: number;
  valueText: string;
  trackStyle: React.CSSProperties;
  thumbColor: string;
  onChange: (next: number) => void;
  disabled?: boolean;
}) {
  const apply = useCallback(
    (el: HTMLElement, event: { clientX: number; clientY: number }) => {
      onChange(round(pointerRatio(el, event).x * max, 2));
    },
    [max, onChange],
  );

  const { dragging, handlers } = useDrag(apply, disabled);

  const onKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (disabled) return;
    if (event.key === "Home" || event.key === "End") {
      event.preventDefault();
      onChange(event.key === "Home" ? 0 : max);
      return;
    }
    const unit = step * (event.shiftKey ? 10 : 1);
    const delta = arrowStep(event.key, unit, step * 10);
    if (!delta) return;
    event.preventDefault();
    onChange(round(clamp(value + (delta.dx || delta.dy), 0, max), 2));
  };

  return (
    <div
      role="slider"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={round(value, 1)}
      aria-valuetext={valueText}
      aria-disabled={disabled || undefined}
      data-dragging={dragging || undefined}
      tabIndex={disabled ? -1 : 0}
      onKeyDown={onKeyDown}
      {...handlers}
      className="color-picker-rail"
      style={trackStyle}
    >
      <span
        className="color-picker-thumb color-picker-thumb-rail"
        style={{
          // Inset by half the thumb so it never overhangs either rail end.
          left: `calc(9px + (100% - 18px) * ${round(max === 0 ? 0 : value / max, 4)})`,
          background: thumbColor,
        }}
      />
    </div>
  );
}

/* ─── numeric + hex fields ──────────────────────────────────── */

function ChannelField({
  label,
  value,
  min,
  max,
  onCommit,
  disabled,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onCommit: (next: number) => void;
  disabled?: boolean;
}) {
  const [draft, setDraft] = useState<string | null>(null);
  const shown = draft ?? String(Math.round(value));

  const commit = (raw: string) => {
    const parsed = Number.parseFloat(raw);
    setDraft(null);
    if (Number.isNaN(parsed)) return;
    onCommit(clamp(Math.round(parsed), min, max));
  };

  return (
    <label className="color-picker-field">
      <span className="color-picker-field-shell">
        <input
          type="text"
          inputMode="numeric"
          value={shown}
          disabled={disabled}
          aria-label={label}
          onChange={(event) => setDraft(event.target.value)}
          onBlur={(event) => commit(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              commit(event.currentTarget.value);
            }
            if (event.key === "ArrowUp" || event.key === "ArrowDown") {
              event.preventDefault();
              const step = (event.shiftKey ? 10 : 1) * (event.key === "ArrowUp" ? 1 : -1);
              setDraft(null);
              onCommit(clamp(Math.round(value) + step, min, max));
            }
          }}
        />
      </span>
      <span className="color-picker-field-label">{label}</span>
    </label>
  );
}

function HexField({
  hex,
  onCommit,
  disabled,
}: {
  hex: string;
  onCommit: (next: string) => void;
  disabled?: boolean;
}) {
  const [draft, setDraft] = useState<string | null>(null);
  const shown = (draft ?? hex).replace(/^#/, "").toUpperCase();

  const commit = (raw: string) => {
    setDraft(null);
    if (parseHex(raw)) onCommit(raw.startsWith("#") ? raw : `#${raw}`);
  };

  return (
    <label className="color-picker-field">
      <span className="color-picker-field-shell">
        <span aria-hidden="true" className="color-picker-field-prefix">#</span>
        <input
          type="text"
          spellCheck={false}
          autoComplete="off"
          value={shown}
          disabled={disabled}
          aria-label="Hex color"
          onChange={(event) => setDraft(event.target.value)}
          onBlur={(event) => commit(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              commit(event.currentTarget.value);
            }
          }}
          className="color-picker-hex-input"
        />
      </span>
      <span className="color-picker-field-label">HEX</span>
    </label>
  );
}

/* ─── colour state ──────────────────────────────────────────── */

function useColorState({
  value,
  onChange,
  alpha,
}: {
  value: string;
  onChange: (hex: string) => void;
  alpha: boolean;
}) {
  const withAlpha = alpha;

  const [hsva, setHsvaState] = useState<Hsva>(() => {
    const parsed = parseHex(value) ?? parseHex(DEFAULT_COLOR)!;
    return rgbaToHsva(parsed);
  });

  const rgba = hsvaToRgba(hsva);
  const hex = rgbaToHex(rgba, withAlpha);

  // Adopt an external value only when it is a different colour than the one
  // rendered, so hue survives achromatic round-trips and the value this picker
  // just emitted does not bounce back through the state.
  const externalRgba = parseHex(value);
  if (externalRgba && rgbaToHex(externalRgba, withAlpha).toLowerCase() !== hex.toLowerCase()) {
    setHsvaState((prev) => {
      const next = rgbaToHsva(externalRgba);
      return { ...next, h: next.s === 0 || next.v === 0 ? prev.h : next.h };
    });
  }

  const commit = (next: Hsva) => {
    setHsvaState(next);
    onChange(rgbaToHex(hsvaToRgba(next), withAlpha));
  };

  const setHsva = (patch: Partial<Hsva>) => commit({ ...hsva, ...patch });

  const setFromRgba = (next: Rgba) => {
    const converted = rgbaToHsva(next);
    commit({ ...converted, h: converted.s === 0 || converted.v === 0 ? hsva.h : converted.h });
  };

  return { hsva, rgba, hex, withAlpha, setHsva, setFromRgba };
}

/* ─── panel ─────────────────────────────────────────────────── */

export interface ColorPickerProps {
  /** Colour as a hex string, with or without `#`. */
  value: string;
  /** Fires on every committed change with `#rrggbb` (or `#rrggbbaa` with alpha). */
  onChange: (hex: string) => void;
  /** Names the trigger, dialog, and controls, e.g. "welcome accent color". */
  label: string;
  /** Shows the opacity rail and includes alpha in the emitted value. */
  alpha?: boolean;
  /** Preset swatches rendered under the fields; defaults to a Discord palette. */
  swatches?: string[];
  disabled?: boolean;
}

export function ColorPicker({
  value,
  onChange,
  label,
  alpha = false,
  swatches = DEFAULT_SWATCHES,
  disabled,
}: ColorPickerProps) {
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState<{ top: number; left: number } | null>(null);
  const [format, setFormat] = useState<ColorFormat>("hex");
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  const { hsva, rgba, hex, withAlpha, setHsva, setFromRgba } = useColorState({
    value,
    onChange,
    alpha,
  });

  const dropperSupported = useState(() => typeof window !== "undefined" && "EyeDropper" in window)[0];
  const hsl = hsvaToHsl(hsva);
  const solid = hsvaToCss({ ...hsva, a: 1 }, false);
  const current = hsvaToCss(hsva, withAlpha);

  const close = useCallback((returnFocus = false) => {
    setOpen(false);
    if (returnFocus) triggerRef.current?.focus();
  }, []);

  // Anchor the panel to its trigger, flipping above and clamping inside the
  // viewport so the fields stay reachable on short screens.
  useLayoutEffect(() => {
    if (!open) return;
    const place = () => {
      const trigger = triggerRef.current;
      const panel = panelRef.current;
      if (!trigger || !panel) return;
      const anchor = trigger.getBoundingClientRect();
      const size = panel.getBoundingClientRect();
      const gap = 8;
      const pad = 12;
      let top = anchor.bottom + gap;
      if (top + size.height > window.innerHeight - pad && anchor.top - gap - size.height >= pad) {
        top = anchor.top - gap - size.height;
      }
      const left = Math.min(
        Math.max(pad, anchor.left),
        Math.max(pad, window.innerWidth - size.width - pad),
      );
      setPosition({ top: Math.max(pad, top), left });
    };
    place();
    window.addEventListener("scroll", place, true);
    window.addEventListener("resize", place);
    return () => {
      window.removeEventListener("scroll", place, true);
      window.removeEventListener("resize", place);
    };
  }, [open, alpha, swatches.length]);

  // The panel renders in a portal at the end of the document, so move focus into
  // it: Tab then walks the panel's own controls instead of the page footer.
  useEffect(() => {
    if (!open) return;
    panelRef.current?.querySelector<HTMLElement>(".color-picker-canvas")?.focus();
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node;
      if (panelRef.current?.contains(target) || triggerRef.current?.contains(target)) return;
      close();
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        close(true);
      }
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open, close]);

  const cycleFormat = () =>
    setFormat((prev) => FORMAT_ORDER[(FORMAT_ORDER.indexOf(prev) + 1) % FORMAT_ORDER.length] ?? "hex");

  const pickFromScreen = async () => {
    const Ctor = (window as unknown as { EyeDropper?: new () => { open: () => Promise<{ sRGBHex: string }> } })
      .EyeDropper;
    if (!Ctor) return;
    try {
      const result = await new Ctor().open();
      const parsed = parseHex(result.sRGBHex);
      if (parsed) setFromRgba({ ...parsed, a: hsva.a });
    } catch {
      // The user dismissed the eyedropper with Escape; nothing to report.
    }
  };

  const panel = open
    ? createPortal(
        <div
          ref={panelRef}
          role="dialog"
          aria-label={`Choose ${label}`}
          className="color-picker-panel"
          style={{
            top: position?.top ?? 0,
            left: position?.left ?? 0,
            visibility: position ? "visible" : "hidden",
          }}
        >
          <SaturationCanvas
            hsva={hsva}
            disabled={disabled}
            onChange={(next) => setHsva(next)}
          />

          <div className="color-picker-body">
            <div className="color-picker-head">
              {dropperSupported && (
                <button
                  type="button"
                  onClick={pickFromScreen}
                  disabled={disabled}
                  aria-label="Pick a color from the screen"
                  className="color-picker-icon-button"
                >
                  <Pipette size={15} strokeWidth={1.7} aria-hidden="true" />
                </button>
              )}

              <span className="color-picker-swatch color-picker-checker" aria-hidden="true">
                <span style={{ backgroundColor: current }} />
              </span>

              <div className="color-picker-rails">
                <Rail
                  label="Hue"
                  value={hsva.h}
                  max={360}
                  valueText={`${Math.round(hsva.h)} degrees`}
                  disabled={disabled}
                  onChange={(h) => setHsva({ h })}
                  thumbColor={`hsl(${hsva.h} 100% 50%)`}
                  trackStyle={{
                    backgroundImage:
                      "linear-gradient(to right, #f00 0%, #ff0 17%, #0f0 33%, #0ff 50%, #00f 67%, #f0f 83%, #f00 100%)",
                  }}
                />
                {withAlpha && (
                  <Rail
                    label="Opacity"
                    value={hsva.a * 100}
                    max={100}
                    valueText={`${Math.round(hsva.a * 100)}%`}
                    disabled={disabled}
                    onChange={(a) => setHsva({ a: clamp(a, 0, 100) / 100 })}
                    thumbColor={current}
                    trackStyle={{
                      background: `linear-gradient(to right, transparent, ${solid}), repeating-conic-gradient(rgba(226, 234, 246, .26) 0% 25%, transparent 0% 50%) 50% / 8px 8px, var(--surface-raised)`,
                    }}
                  />
                )}
              </div>
            </div>

            <div className="color-picker-fields">
              {format === "hex" && (
                <HexField
                  hex={hex}
                  disabled={disabled}
                  onCommit={(next) => {
                    const parsed = parseHex(next);
                    if (parsed) setFromRgba(withAlpha ? parsed : { ...parsed, a: hsva.a });
                  }}
                />
              )}

              {format === "rgb" && (
                <>
                  <ChannelField label="R" value={rgba.r} min={0} max={255} disabled={disabled} onCommit={(r) => setFromRgba({ ...rgba, r })} />
                  <ChannelField label="G" value={rgba.g} min={0} max={255} disabled={disabled} onCommit={(g) => setFromRgba({ ...rgba, g })} />
                  <ChannelField label="B" value={rgba.b} min={0} max={255} disabled={disabled} onCommit={(b) => setFromRgba({ ...rgba, b })} />
                </>
              )}

              {format === "hsl" && (
                <>
                  <ChannelField label="H" value={hsl.h} min={0} max={360} disabled={disabled} onCommit={(h) => setHsva(hslToHsva(h, hsl.s, hsl.l, hsva.a))} />
                  <ChannelField label="S" value={hsl.s} min={0} max={100} disabled={disabled} onCommit={(s) => setHsva(hslToHsva(hsl.h, s, hsl.l, hsva.a))} />
                  <ChannelField label="L" value={hsl.l} min={0} max={100} disabled={disabled} onCommit={(l) => setHsva(hslToHsva(hsl.h, hsl.s, l, hsva.a))} />
                </>
              )}

              {withAlpha && format !== "hex" && (
                <ChannelField
                  label="A"
                  value={hsva.a * 100}
                  min={0}
                  max={100}
                  disabled={disabled}
                  onCommit={(a) => setHsva({ a: a / 100 })}
                />
              )}

              <button
                type="button"
                onClick={cycleFormat}
                disabled={disabled}
                aria-label={`Color format: ${format.toUpperCase()}. Switch format`}
                className="color-picker-icon-button color-picker-format"
              >
                <ChevronsUpDown size={15} strokeWidth={1.7} aria-hidden="true" />
              </button>
            </div>

            {swatches.length > 0 && (
              <div className="color-picker-swatches">
                {swatches.map((swatch) => {
                  const selected = swatch.toLowerCase() === hex.slice(0, 7).toLowerCase();
                  const parsedSwatch = parseHex(swatch);
                  const darkMark = parsedSwatch ? isLightColor(parsedSwatch) : false;
                  return (
                    <button
                      key={swatch}
                      type="button"
                      disabled={disabled}
                      aria-label={swatch}
                      aria-pressed={selected}
                      onClick={() => {
                        const parsed = parseHex(swatch);
                        if (parsed) setFromRgba({ ...parsed, a: hsva.a });
                      }}
                      className="color-picker-swatch-button"
                      style={{ backgroundColor: swatch }}
                    >
                      <Check
                        size={12}
                        strokeWidth={2.6}
                        aria-hidden="true"
                        className={`${selected ? "is-selected" : ""} ${darkMark ? "is-dark-mark" : ""}`}
                      />
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>,
        document.body,
      )
    : null;

  return (
    <div className="color-picker">
      <button
        ref={triggerRef}
        type="button"
        className="color-picker-trigger"
        aria-label={`${label} color`}
        aria-haspopup="dialog"
        aria-expanded={open}
        disabled={disabled}
        onClick={() => setOpen((current) => !current)}
      >
        <span className="color-picker-trigger-swatch color-picker-checker" aria-hidden="true">
          <span style={{ backgroundColor: hex }} />
        </span>
        <span className="color-picker-trigger-value">{hex.replace(/^#/, "").toUpperCase()}</span>
      </button>
      {panel}
    </div>
  );
}
