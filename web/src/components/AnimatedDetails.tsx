import { useEffect, useRef } from "react";
import type { ComponentProps } from "react";

/** Long enough to read as a slide, short enough not to feel slow. */
const DURATION = 240;

/** Ease-out: the card settles into place instead of stopping dead. */
const EASING = "cubic-bezier(.22, .61, .36, 1)";

/** The part that moves: everything after the summary. */
const CONTENT = ":scope > :not(summary)";

/**
 * A `<details>` whose content slides open and shut.
 *
 * The element offers no CSS hook for its own height, so the panel is animated
 * with the Web Animations API: opening pins the content to zero and grows it to
 * the height it asked for, closing shrinks it back and only then flips `open`,
 * which keeps the content on screen for the whole animation. The header and its
 * pills stay where they are while the card below them grows or folds away.
 *
 * Both directions are driven from the click itself rather than the `toggle`
 * event, because `toggle` arrives a task late — long enough for the browser to
 * paint the card fully open and then snap it shut before the slide begins.
 *
 * Interrupting either direction reads the height on screen at that moment, so
 * clicking quickly never makes the card jump. Motion is skipped for readers who
 * ask for reduced motion, where the native toggle is used instead.
 */
export function AnimatedDetails({ className, children, ...props }: ComponentProps<"details">) {
  const ref = useRef<HTMLDetailsElement>(null);
  const running = useRef<Animation | null>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    const content = () => element.querySelector<HTMLElement>(CONTENT);

    // Drop whatever is playing and hand the content back to the layout.
    const settle = (panel: HTMLElement) => {
      running.current?.cancel();
      running.current = null;
      panel.style.removeProperty("height");
      panel.style.removeProperty("overflow");
    };

    const slide = (panel: HTMLElement, keyframes: Keyframe[], done?: () => void) => {
      running.current?.cancel();
      panel.style.overflow = "hidden";
      const animation = panel.animate(keyframes, { duration: DURATION, easing: EASING, fill: "forwards" });
      running.current = animation;
      animation.onfinish = () => {
        if (running.current !== animation) return;
        settle(panel);
        done?.();
      };
    };

    const expand = () => {
      const panel = content();
      if (!panel) return;
      const height = panel.offsetHeight;
      // Pinned before the first paint of the open card, so the growth starts
      // from a folded one instead of flashing the finished card for a frame.
      panel.style.overflow = "hidden";
      panel.style.height = "0px";
      slide(panel, [
        { height: "0px", opacity: 0 },
        { height: `${height}px`, opacity: 1 },
      ]);
    };

    const collapse = () => {
      const panel = content();
      if (!panel) {
        element.open = false;
        return;
      }
      // Measured before the running animation is cancelled, so reversing
      // mid-slide carries on from where the card currently is.
      const height = panel.offsetHeight;
      // `open` cannot drop until the fold is done, so the chevron is pointed the
      // other way here; the stylesheet reads this to turn it as the slide starts.
      element.setAttribute("data-closing", "");
      slide(panel, [
        { height: `${height}px`, opacity: 1 },
        { height: "0px", opacity: 0 },
      ], () => {
        element.removeAttribute("data-closing");
        element.open = false;
      });
    };

    const onClick = (event: MouseEvent) => {
      const target = event.target;
      if (!(target instanceof Element)) return;
      const summary = target.closest("summary");
      // Only this card's own header, not a summary nested inside its content,
      // and never a control that happens to sit in the header.
      if (!summary || summary.parentElement !== element) return;
      if (target.closest("a, button, input, select, textarea")) return;
      // Take the toggle over instead of letting it happen instantly; keyboard
      // activation of the summary arrives here as a click too.
      event.preventDefault();
      if (reduced.matches) {
        element.open = !element.open;
        return;
      }
      if (element.open) collapse();
      else {
        element.open = true;
        expand();
      }
    };

    element.addEventListener("click", onClick);
    return () => {
      element.removeEventListener("click", onClick);
      running.current?.cancel();
      running.current = null;
    };
  }, []);

  return <details ref={ref} className={className} {...props}>{children}</details>;
}
