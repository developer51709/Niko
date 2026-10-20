import { useEffect, useRef, useState } from "react";

/**
 * Ticks once a second so a relative "synced … ago" label stays honest.
 *
 * The interval only runs while there is something to count from, and restarts
 * whenever a fresh poll lands.
 */
export function useSyncedClock(lastSync: number | null): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!lastSync) return;
    setNow(Date.now());
    const timer = window.setInterval(() => setNow(Date.now()), 1_000);
    return () => window.clearInterval(timer);
  }, [lastSync]);
  return now;
}

/**
 * True for a moment after ``signature`` changes.
 *
 * Live cards use this for a one-shot highlight, so a refresh that changes
 * nothing stays perfectly still while a number that actually moved breathes
 * once instead of animating on a timer.
 */
export function useFreshSignal(signature: string, durationMs = 1_600): boolean {
  const [fresh, setFresh] = useState(false);
  const previous = useRef(signature);
  useEffect(() => {
    if (previous.current === signature) return;
    previous.current = signature;
    setFresh(true);
    const timer = window.setTimeout(() => setFresh(false), durationMs);
    return () => window.clearTimeout(timer);
  }, [signature, durationMs]);
  return fresh;
}
