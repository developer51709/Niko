import { useEffect } from "react";
import { GooeyToaster } from "goey-toast";
import "goey-toast/styles.css";

/**
 * The one place success and failure feedback appears.
 *
 * Mounted once from `App`, so every dashboard tab — and every public page —
 * reports results through the same goey-toast stack instead of each card
 * printing its own status line.
 */
function useExpandedToastHeights() {
  useEffect(() => {
    const observed = new WeakSet<Element>();
    let observer: ResizeObserver | null = null;
    let active = true;
    let frame = 0;

    const sync = () => {
      frame = 0;
      if (!active) return;
      const wrappers = Array.from(document.querySelectorAll<HTMLElement>(".niko-toast"));
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

function ToastToaster() {
  useExpandedToastHeights();
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
  return <ToastToaster />;
}
