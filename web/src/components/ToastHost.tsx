import { useEffect, type CSSProperties } from "react";
import { GooeyToaster } from "goey-toast";
import "goey-toast/styles.css";
import { Toaster } from "react-hot-toast";
import { devtools, useDevtoolsFlag } from "../devtools";

/**
 * The one place success and failure feedback appears.
 *
 * Mounted once from `App`, so every dashboard tab — and every public page —
 * reports results through the same stack instead of each card printing its own
 * status line.
 *
 * The legacy look is inline rather than in a stylesheet on purpose:
 * react-hot-toast appends its portal to `<body>`, outside `.dashboard-layout`,
 * where the dashboard's own theme variables are redefined. Reading the root
 * tokens here keeps the toasts on the same palette and lets them follow the
 * light/dark theme with the rest of the page.
 *
 * The Toast V2 experiment mounts goey-toast instead of the legacy stack. Only
 * one host is mounted at a time, so a toast cannot be painted twice, and the
 * helpers in `utils/toast` send each call to whichever host is live.
 */
const baseToastStyle: CSSProperties = {
  maxWidth: "min(420px, calc(100vw - 32px))",
  padding: "12px 14px",
  color: "var(--ink)",
  background: "var(--surface-raised)",
  backdropFilter: "blur(10px)",
  borderColor: "var(--line)",
  borderStyle: "solid",
  borderWidth: "1px 1px 1px 2px",
  borderLeftColor: "var(--sage)",
  borderRadius: "10px",
  boxShadow: "var(--shadow)",
  fontSize: "12px",
  lineHeight: 1.6,
  textAlign: "left",
};

function LegacyToaster() {
  return (
    <Toaster
      position="top-right"
      gutter={10}
      containerClassName="niko-toast-stack"
      toastOptions={{
        duration: 4000,
        className: "niko-toast",
        style: baseToastStyle,
        success: {
          className: "niko-toast niko-toast-success",
          // A save confirmation is read once and dismissed, so it needs less
          // time on screen than a failure the reader has to act on.
          duration: 3200,
          iconTheme: { primary: "#8bd5b1", secondary: "#0f1113" },
          style: { borderLeftColor: "var(--sage)" },
        },
        error: {
          className: "niko-toast niko-toast-error",
          duration: 6500,
          iconTheme: { primary: "#d0786c", secondary: "#0f1113" },
          style: { borderLeftColor: "#d0786c" },
        },
        loading: {
          className: "niko-toast niko-toast-loading",
          iconTheme: { primary: "var(--accent-dark)", secondary: "var(--line)" },
        },
      }}
    />
  );
}

/**
 * goey-toast measures the Sonner row height when a toast expands, but not when
 * an already-expanded description grows afterwards (a wrapped reason on a
 * phone, or a longer result message). Without this the blob grows while the
 * row keeps its old fixed height, so the text spills out of the card and the
 * stack spacing is wrong.
 *
 * Re-measure every visible v2 wrapper whenever it resizes and mirror the
 * package's own `--initial-height` / `--offset` bookkeeping.
 */
function useExpandedV2Heights() {
  useEffect(() => {
    const observed = new WeakSet<Element>();
    let observer: ResizeObserver | null = null;
    let active = true;
    let frame = 0;

    const sync = () => {
      frame = 0;
      if (!active) return;
      const wrappers = Array.from(document.querySelectorAll<HTMLElement>(".niko-toast-v2"));
      if (wrappers.length === 0) return;

      const heights = new Map<HTMLElement, number>();
      let list: HTMLElement | null = null;
      for (const wrapper of wrappers) {
        const toast = wrapper.closest<HTMLElement>("[data-sonner-toast]");
        const parent = toast?.parentElement;
        if (!toast || !parent) continue;
        list = parent;
        heights.set(toast, wrapper.getBoundingClientRect().height);
        if (!observed.has(wrapper)) {
          observed.add(wrapper);
          observer?.observe(wrapper);
        }
      }
      if (!list) return;

      const toasts = Array.from(
        list.querySelectorAll<HTMLElement>(":scope > [data-sonner-toast]"),
      );
      const rowHeights = toasts.map((toast) => {
        if (toast.getAttribute("data-visible") === "false") return 0;
        const height = heights.get(toast);
        if (height && height > 0) return height;
        const content = toast.firstElementChild;
        const contentHeight = content ? content.getBoundingClientRect().height : 0;
        return contentHeight > 0 ? contentHeight : 48;
      });

      const gap = parseFloat(getComputedStyle(list).getPropertyValue("--gap")) || 10;
      let offset = 0;
      for (let i = toasts.length - 1; i >= 0; i -= 1) {
        const toast = toasts[i];
        toast.style.setProperty("--initial-height", `${rowHeights[i]}px`);
        if (toast.getAttribute("data-visible") === "false") {
          toast.style.setProperty("--offset", "0px");
          continue;
        }
        toast.style.setProperty("--offset", `${offset}px`);
        if (i > 0) offset += rowHeights[i] + gap;
      }
    };

    const schedule = () => {
      if (!active || frame) return;
      frame = window.requestAnimationFrame(sync);
    };

    observer = new ResizeObserver(schedule);
    // New toasts mount after the host, so watch the stack for new wrappers.
    // GooeyToaster portals its list during commit, before this effect runs.
    const toaster = document.querySelector<HTMLElement>("[data-sonner-toaster]");
    const mutations = new MutationObserver(schedule);
    if (toaster) mutations.observe(toaster, { childList: true, subtree: true });
    schedule();

    return () => {
      active = false;
      if (frame) window.cancelAnimationFrame(frame);
      observer?.disconnect();
      mutations.disconnect();
    };
  }, []);
}

function ToastV2Toaster() {
  useExpandedV2Heights();
  return (
    <GooeyToaster
      position="top-right"
      theme="dark"
      gap={10}
      offset={16}
      closeButton
      showProgress
      showTimestamp={false}
      preset="smooth"
      bounce={0.28}
      // Loading toasts are updated through their mounted wrapper, so keep the
      // visible window wide enough that a burst of dashboard actions does not
      // park a loading toast in goey's queue until its result has already
      // arrived.
      visibleToasts={8}
      maxQueue={8}
      queueOverflow="drop-oldest"
      sound={false}
    />
  );
}

export function ToastHost() {
  const toastV2 = useDevtoolsFlag(devtools.toastV2);
  return toastV2 ? <ToastV2Toaster /> : <LegacyToaster />;
}
