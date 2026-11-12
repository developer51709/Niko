import { gooeyToast, type GooeyToastOptions, type GooeyToastUpdateOptions } from "goey-toast";
import { createElement, type ReactNode } from "react";

/**
 * Success and failure messages for the whole app.
 *
 * The dashboard used to print each result as small text inside the card that
 * produced it — above the panel, or in the settings footer — so the same
 * "Saved." message appeared in a different place on every tab. These helpers
 * route those messages through the single `<ToastHost />` stack instead.
 *
 * Pass an `id` when a surface can report the same thing repeatedly (a save
 * button, a per-account row): the toast replaces the previous one, which is
 * what the old single status line did, instead of stacking duplicates.
 */

/** The wrapper class that dresses goey-toast in the site palette. */
const TOAST_WRAPPER_CLASS = "niko-toast";

/** Shared look and motion for every toast. */
const toastDefaults = {
  classNames: { wrapper: TOAST_WRAPPER_CLASS },
  preset: "smooth",
  bounce: 0.28,
  // Rich toasts draw their own progress bar; the package's timed bar would run
  // on a different clock (and on a loading toast, drain before the work ends).
  showProgress: false,
} satisfies GooeyToastOptions;

const SUCCESS_DURATION = 3200;
const ERROR_DURATION = 6500;
/** A rich loading toast has to outlive the work, so its own timer is far away. */
const RICH_TOAST_DURATION = 600_000;

/** A determinate or indeterminate progress bar inside a toast's description. */
export type ToastProgress = {
  /** 0–1. Omit for an indeterminate bar while a single request runs. */
  value?: number;
  label?: string;
};

export type ToastDetail = {
  description?: string;
  progress?: ToastProgress;
};

function toastDescription(detail?: ToastDetail): ReactNode {
  if (!detail) return undefined;
  if (!detail.progress) return detail.description;

  const percent = detail.progress.value === undefined
    ? undefined
    : Math.round(Math.max(0, Math.min(1, detail.progress.value)) * 100);

  return createElement(
    "span",
    { className: "niko-toast-rich" },
    detail.description
      ? createElement("span", { className: "niko-toast-description" }, detail.description)
      : null,
    createElement(
      "span",
      {
        className: `niko-toast-progress${percent === undefined ? " is-indeterminate" : ""}`,
        role: "progressbar",
        "aria-label": detail.progress.label || "Progress",
        "aria-valuemin": 0,
        "aria-valuemax": 100,
        "aria-valuenow": percent,
        "aria-busy": percent === undefined ? true : undefined,
      },
      createElement("span", {
        className: "niko-toast-progress-fill",
        style: percent === undefined ? undefined : { width: `${percent}%` },
      }),
    ),
    detail.progress.label
      ? createElement("span", { className: "niko-toast-progress-label" }, detail.progress.label)
      : null,
  );
}

/**
 * Loading must end in a result, so loading toasts are created with no timer of
 * their own. This map lets a later success/error call update the same live
 * toast instead of creating a second one.
 *
 * goey-toast only keeps React state from the first render when a toast is
 * replaced by id, so calling `gooeyToast.success(..., { id })` on a loading
 * toast leaves the old title and spinner in place. `gooeyToast.update` is the
 * supported path, and it needs to know the toast is still on screen.
 */
type LiveToast = {
  timer: number | null;
  /** Guards a deferred re-apply from overwriting a newer state. */
  version: number;
};

const liveToasts = new Map<string, LiveToast>();

function clearDismissTimer(live: LiveToast) {
  if (live.timer === null) return;
  window.clearTimeout(live.timer);
  live.timer = null;
}

function forgetToast(id: string, live: LiveToast) {
  if (liveToasts.get(id) !== live) return;
  clearDismissTimer(live);
  liveToasts.delete(id);
}

function trackToast(id: string) {
  const live: LiveToast = { timer: null, version: 0 };
  liveToasts.set(id, live);
  return {
    live,
    // Also covers a manual dismissal (close button, swipe, Escape), so a later
    // result does not try to update a toast that is already gone.
    callbacks: {
      onDismiss: () => forgetToast(id, live),
      onAutoClose: () => forgetToast(id, live),
    },
  };
}

/**
 * Updated toasts keep the `Infinity` duration they were created with, so the
 * result needs its own dismiss timer. Re-using the same timer per id also means
 * a new save starts its result countdown from scratch instead of inheriting the
 * previous one.
 */
function updateToast(id: string, live: LiveToast, options: GooeyToastUpdateOptions) {
  const version = ++live.version;
  const apply = () => {
    // The first attempt can arrive before the toast has painted and installed
    // its update listener (for example, a promise that resolves immediately).
    // Re-apply on the next task, but only if this is still the current state.
    if (liveToasts.get(id) !== live || live.version !== version) return;
    gooeyToast.update(id, options);
  };
  apply();
  window.setTimeout(apply, 120);
}

function dismissToastAfter(id: string, live: LiveToast, delay: number) {
  clearDismissTimer(live);
  live.timer = window.setTimeout(() => {
    live.timer = null;
    if (liveToasts.get(id) !== live) return;
    liveToasts.delete(id);
    gooeyToast.dismiss(id);
  }, delay);
}

/**
 * goey-toast can only spin for the promise API, so an in-flight `notifyLoading`
 * supplies the same arc as the toast's own spinner. It inherits the wrapper's
 * colour and turns with a CSS animation (see `styles/toast.css`).
 */
const loadingIcon = createElement(
  "svg",
  {
    xmlns: "http://www.w3.org/2000/svg",
    width: 18,
    height: 18,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    className: "niko-toast-spinner",
    "aria-hidden": true,
  },
  createElement("path", { d: "M21 12a9 9 0 1 1-6.219-8.56" }),
);

/**
 * Show the loading state for work in progress.
 *
 * Calling this with the same `id` the result will use turns the spinner into
 * the outcome in place.
 */
export function notifyLoading(message: string, id?: string, detail?: ToastDetail) {
  const description = toastDescription(detail);
  const rich = description !== undefined;
  if (id) {
    const live = liveToasts.get(id);
    if (live) {
      // A progress poll can repeat the same id many times; updating the title
      // and description keeps one toast in place instead of replaying its
      // entrance each tick. Passing null clears a description that the new
      // step no longer needs.
      clearDismissTimer(live);
      updateToast(id, live, {
        title: message,
        type: "default",
        icon: loadingIcon,
        description: description ?? null,
      });
      return;
    }
    const { callbacks } = trackToast(id);
    gooeyToast(message, {
      ...toastDefaults,
      id,
      duration: Infinity,
      icon: loadingIcon,
      description,
      // A compact loading toast can gain a description when its result
      // arrives; this keeps that expanded result from closing itself early.
      timing: { displayDuration: RICH_TOAST_DURATION },
      ...callbacks,
    });
    return;
  }
  // A loading toast has no natural end; it is replaced by the result or
  // dismissed by the view that started the work.
  gooeyToast(message, {
    ...toastDefaults,
    duration: Infinity,
    icon: loadingIcon,
    description,
    ...(rich ? { timing: { displayDuration: RICH_TOAST_DURATION } } : {}),
  });
}

export function notifySuccess(message: string, id?: string, detail?: ToastDetail) {
  const description = toastDescription(detail);
  if (id) {
    const live = liveToasts.get(id);
    if (live) {
      updateToast(id, live, { title: message, type: "success", icon: null, description: description ?? null });
      dismissToastAfter(id, live, SUCCESS_DURATION);
      return;
    }
    const tracked = trackToast(id);
    gooeyToast.success(message, {
      ...toastDefaults,
      id,
      duration: Infinity,
      description,
      // The manual timer below closes this toast, so keep the package's own
      // expanded-toast timer out of the way.
      timing: { displayDuration: RICH_TOAST_DURATION },
      ...tracked.callbacks,
    });
    dismissToastAfter(id, tracked.live, SUCCESS_DURATION);
    return;
  }
  // A save confirmation is read once and dismissed, so it needs less time on
  // screen than a failure the reader has to act on.
  gooeyToast.success(message, {
    ...toastDefaults,
    duration: description === undefined ? SUCCESS_DURATION : Infinity,
    description,
    ...(description === undefined ? {} : { timing: { displayDuration: SUCCESS_DURATION + 1200 } }),
  });
}

export function notifyError(message: string, id?: string, detail?: ToastDetail) {
  const description = toastDescription(detail);
  if (id) {
    const live = liveToasts.get(id);
    if (live) {
      updateToast(id, live, { title: message, type: "error", icon: null, description: description ?? null });
      dismissToastAfter(id, live, ERROR_DURATION);
      return;
    }
    const tracked = trackToast(id);
    gooeyToast.error(message, {
      ...toastDefaults,
      id,
      duration: Infinity,
      description,
      timing: { displayDuration: RICH_TOAST_DURATION },
      ...tracked.callbacks,
    });
    dismissToastAfter(id, tracked.live, ERROR_DURATION);
    return;
  }
  gooeyToast.error(message, {
    ...toastDefaults,
    duration: description === undefined ? ERROR_DURATION : Infinity,
    description,
    ...(description === undefined ? {} : { timing: { displayDuration: ERROR_DURATION + 1200 } }),
  });
}

/** Clear queued messages, for a view that reloads from scratch. */
export function clearToasts(id?: string) {
  if (id) {
    const live = liveToasts.get(id);
    if (live) {
      clearDismissTimer(live);
      liveToasts.delete(id);
    }
  } else {
    for (const live of liveToasts.values()) clearDismissTimer(live);
    liveToasts.clear();
  }
  gooeyToast.dismiss(id);
}
