import {
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import type { KeyboardEvent, ReactNode } from "react";
import { motion, useReducedMotion } from "motion/react";

const INDICATOR = { type: "spring", stiffness: 620, damping: 42, mass: 0.35 } as const;
const PANEL = { type: "spring", stiffness: 460, damping: 38, mass: 0.8 } as const;
const useIsoLayoutEffect = typeof window === "undefined" ? useEffect : useLayoutEffect;

export type TabItem = { value: string; label: string; disabled?: boolean };
export type TabsActivation = "automatic" | "manual";
export type UseTabsOptions = {
  items: TabItem[];
  value?: string;
  defaultValue?: string;
  onValueChange?: (value: string) => void;
  activation?: TabsActivation;
};

export function useTabs({
  items,
  value: controlled,
  defaultValue,
  onValueChange,
  activation = "automatic",
}: UseTabsOptions) {
  const base = useId();
  const nodes = useRef(new Map<string, HTMLButtonElement>());
  const direction = useRef(1);
  const [internal, setInternal] = useState(
    () => defaultValue ?? items.find((item) => !item.disabled)?.value ?? items[0]?.value ?? "",
  );
  const value = controlled ?? internal;
  const emit = useRef(onValueChange);
  emit.current = onValueChange;

  const select = useCallback((next: string) => {
    if (next === value || !items.some((item) => item.value === next && !item.disabled)) return;
    const from = items.findIndex((item) => item.value === value);
    const to = items.findIndex((item) => item.value === next);
    direction.current = to < from ? -1 : 1;
    if (controlled === undefined) setInternal(next);
    emit.current?.(next);
  }, [controlled, items, value]);

  const focusAt = useCallback((index: number) => {
    const item = items[index];
    if (item) nodes.current.get(item.value)?.focus();
  }, [items]);

  const moveFocus = useCallback((from: number, step: number) => {
    const count = items.length;
    if (!count) return 0;
    let index = from;
    for (let attempt = 0; attempt < count; attempt += 1) {
      index = (index + step + count) % count;
      if (!items[index].disabled) return index;
    }
    return from;
  }, [items]);

  const endStop = useCallback((reverse: boolean) => {
    const indices = items.map((_, index) => index);
    if (reverse) indices.reverse();
    return indices.find((index) => !items[index].disabled) ?? 0;
  }, [items]);

  const getTabProps = useCallback((item: TabItem, index: number) => ({
    id: `${base}-tab-${item.value}`,
    role: "tab" as const,
    type: "button" as const,
    "aria-selected": item.value === value,
    "aria-controls": `${base}-panel-${item.value}`,
    "aria-disabled": item.disabled ? true as const : undefined,
    tabIndex: item.value === value ? 0 : -1,
    ref: (node: HTMLButtonElement | null) => {
      if (node) nodes.current.set(item.value, node);
      else nodes.current.delete(item.value);
    },
    onClick: () => { if (!item.disabled) select(item.value); },
    onKeyDown: (event: KeyboardEvent<HTMLButtonElement>) => {
      if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
        event.preventDefault();
        const next = moveFocus(index, event.key === "ArrowRight" ? 1 : -1);
        focusAt(next);
        if (activation === "automatic") select(items[next].value);
      } else if (event.key === "Home" || event.key === "End") {
        event.preventDefault();
        const next = endStop(event.key === "End");
        focusAt(next);
        if (activation === "automatic") select(items[next].value);
      } else if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        if (!item.disabled) select(item.value);
      }
    },
  }), [activation, base, endStop, focusAt, items, moveFocus, select, value]);

  const getPanelProps = useCallback((panelValue: string) => ({
    id: `${base}-panel-${panelValue}`,
    role: "tabpanel" as const,
    "aria-labelledby": `${base}-tab-${panelValue}`,
    tabIndex: 0,
  }), [base]);

  return {
    value,
    select,
    direction: direction.current,
    tabListProps: { role: "tablist" as const, "aria-orientation": "horizontal" as const },
    getTabProps,
    getPanelProps,
  };
}

export type UseTabsReturn = ReturnType<typeof useTabs>;
export type TabsProps = UseTabsOptions & {
  renderPanel?: (value: string) => ReactNode;
  label?: string;
  panelClassName?: string;
  className?: string;
};

export function Tabs({
  items,
  value,
  defaultValue,
  onValueChange,
  activation = "automatic",
  renderPanel,
  label = "Tabs",
  panelClassName = "",
  className = "",
}: TabsProps) {
  const tabs = useTabs({ items, value, defaultValue, onValueChange, activation });
  const reduced = useReducedMotion();
  const rowRef = useRef<HTMLDivElement | null>(null);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const [indicator, setIndicator] = useState({ x: 0, width: 0, ready: false });
  const selectedIndex = items.findIndex((item) => item.value === tabs.value);

  useIsoLayoutEffect(() => {
    const node = tabRefs.current[selectedIndex];
    const row = rowRef.current;
    if (!node || !row) return;
    const read = () => setIndicator((previous) =>
      previous.x === node.offsetLeft && previous.width === node.offsetWidth && previous.ready
        ? previous
        : { x: node.offsetLeft, width: node.offsetWidth, ready: true },
    );
    read();
    const observer = new ResizeObserver(read);
    observer.observe(row);
    return () => observer.disconnect();
  }, [items, selectedIndex]);

  return <div className={`stats-tabs ${className}`}>
    <div {...tabs.tabListProps} ref={rowRef} aria-label={label} className="stats-tabs-list">
      <motion.span layout aria-hidden="true" className="stats-tabs-indicator" style={{ left: indicator.x, width: indicator.width, opacity: indicator.ready ? 1 : 0 }} transition={reduced ? { duration: 0 } : INDICATOR} />
      {items.map((item, index) => {
        const selected = item.value === tabs.value;
        const { ref: register, ...tabProps } = tabs.getTabProps(item, index);
        return <button
          key={item.value}
          {...tabProps}
          ref={(node) => { register(node); tabRefs.current[index] = node; }}
          className={`stats-tab${selected ? " selected" : ""}${item.disabled ? " disabled" : ""}`}
        >{item.label}</button>;
      })}
    </div>
    {renderPanel && <motion.div
      key={tabs.value}
      custom={tabs.direction}
      {...tabs.getPanelProps(tabs.value)}
      initial={reduced ? false : { opacity: 0, x: tabs.direction * 12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={reduced ? { duration: 0 } : PANEL}
      className={`stats-tab-panel ${panelClassName}`}
    >{renderPanel(tabs.value)}</motion.div>}
  </div>;
}

export default Tabs;
