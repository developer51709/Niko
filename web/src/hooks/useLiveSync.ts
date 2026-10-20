import { useEffect, useRef, useState } from "react";

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
