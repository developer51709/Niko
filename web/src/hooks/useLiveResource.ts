import { useEffect, useRef, useState } from "react";

type Options = {
  /** How often the resource refreshes while it is on screen. */
  intervalMs?: number;
  /** Skip fetching entirely (for a tab that is not open right now). */
  enabled?: boolean;
  /** Bump to force an immediate reload, e.g. after a manual dashboard refresh. */
  refreshKey?: number;
  /** Shown when the very first load fails. */
  fallbackError?: string;
};

export type LiveResource<T> = {
  data: T | null;
  /** True until the first payload arrives, so a shell can show its skeleton. */
  loading: boolean;
  error: string;
  /** A later poll failed; the last good payload is still on screen. */
  stale: boolean;
  /** When the payload on screen landed. */
  syncedAt: number | null;
  refresh: () => void;
};

/**
 * Poll a dashboard endpoint on the same rhythm as the analytics card.
 *
 * The first load paints a skeleton and reports errors to the page. Every later
 * poll runs in the background: it is skipped while the tab is hidden, refetches
 * as soon as the tab comes back, and a failure keeps the last good payload on
 * screen with ``stale`` set instead of replacing it with an error.
 */
export function useLiveResource<T>(key: string, load: () => Promise<T>, options: Options = {}): LiveResource<T> {
  const { intervalMs = 10_000, enabled = true, refreshKey = 0, fallbackError = "This page could not be loaded." } = options;
  const loader = useRef(load);
  loader.current = load;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState("");
  const [stale, setStale] = useState(false);
  const [syncedAt, setSyncedAt] = useState<number | null>(null);
  const [refreshTick, setRefreshTick] = useState(0);

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    let inFlight = false;
    setLoading(true);
    setError("");
    setStale(false);

    const run = async (background: boolean) => {
      if (!active || inFlight) return;
      if (background && document.visibilityState === "hidden") return;
      inFlight = true;
      try {
        const value = await loader.current();
        if (!active) return;
        setData(value);
        setSyncedAt(Date.now());
        setStale(false);
        setError("");
      } catch (reason) {
        if (!active) return;
        if (background) setStale(true);
        else setError(reason instanceof Error ? reason.message : fallbackError);
      } finally {
        inFlight = false;
        if (active) setLoading(false);
      }
    };

    void run(false);
    const timer = window.setInterval(() => void run(true), intervalMs);
    const onVisibilityChange = () => { if (document.visibilityState === "visible") void run(true); };
    document.addEventListener("visibilitychange", onVisibilityChange);
    return () => {
      active = false;
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, [key, enabled, intervalMs, refreshKey, refreshTick, fallbackError]);

  return { data, loading, error, stale, syncedAt, refresh: () => setRefreshTick((value) => value + 1) };
}
