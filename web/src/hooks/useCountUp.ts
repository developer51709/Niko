import { useEffect, useRef, useState } from "react";

const COUNT_MS = 480;

/**
 * Ease a displayed integer towards ``target``.
 *
 * Live cards refresh on their own, so a metric that jumped from 812 to 940
 * should travel rather than blink. The tween starts from whatever was last
 * painted, which keeps it smooth when two refreshes land close together, and
 * ``animate`` false (reduced motion, or the first render) snaps straight to the
 * value.
 */
export function useCountUp(target: number, animate: boolean): number {
  const [display, setDisplay] = useState(target);
  const painted = useRef(target);

  useEffect(() => {
    if (!animate || painted.current === target) {
      painted.current = target;
      setDisplay(target);
      return;
    }
    const from = painted.current;
    const started = performance.now();
    let frame = 0;
    const step = (now: number) => {
      const progress = Math.min(1, (now - started) / COUNT_MS);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = Math.round(from + (target - from) * eased);
      painted.current = value;
      setDisplay(value);
      if (progress < 1) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => window.cancelAnimationFrame(frame);
  }, [target, animate]);

  return display;
}
