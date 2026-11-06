/**
 * Owner-only motion lab.
 *
 * A full-screen stage for trying page transitions, component interactions and
 * scroll effects before any of them ships. Nothing here is wired into the real
 * router: both demo pages are mock layouts built from the same anchors, so a
 * transition can be judged on its own instead of on a page that happens to be
 * open.
 *
 * The three page transitions are deliberately different kinds of motion:
 *
 * - **Iris** stacks the incoming layout over the outgoing one and masks it open
 *   from the middle of the stage in a soft, glowing circle: the old page dims
 *   and recedes as the new one is uncovered, so nothing simply cross-fades.
 * - **Morph** measures every `[data-morph]` block before the swap and plays the
 *   incoming block from the outgoing block's rectangle, so titles, copy and
 *   tiles appear to travel into their new layout (a FLIP).
 * - **Blur** defocuses the old layout out and refocuses the new one in.
 *
 * The lab plays its transitions even when the OS asks for reduced motion —
 * that is the point of the lab — while the rest of the site keeps honouring it.
 */

import { useCallback, useEffect, useLayoutEffect, useRef, useState, type MouseEvent as ReactMouseEvent, type PointerEvent as ReactPointerEvent } from "react";
import { Icon } from "./Icon";

export type MotionTransition = "iris" | "morph" | "blur";

/** The page transitions, in the order the devtools panel lists them. */
export const MOTION_TRANSITIONS: { id: MotionTransition; label: string; description: string }[] = [
  { id: "iris", label: "Iris", description: "A soft-edged iris opens from the middle of the stage, the next layout already waiting underneath." },
  { id: "morph", label: "Morph", description: "Titles, copy and tiles travel into the next page's layout and crossfade on the way." },
  { id: "blur", label: "Blur", description: "The old page defocuses out and the new one sharpens into place." },
];

type PageKey = "a" | "b";
type Phase = "idle" | "out" | "in";

type PageContent = {
  kicker: string;
  title: string;
  body: string;
  tiles: { value: string; label: string }[];
  footer: string;
};

/** Mock page copy, anchored by `data-morph` so the morph pairs them up. */
const PAGES: Record<PageKey, PageContent> = {
  a: {
    kicker: "Server overview",
    title: "Everything your server needs",
    body: "Moderation, leveling, economy and tickets share one dashboard — no second bot, no second prefix.",
    tiles: [
      { value: "1.4M", label: "members reached" },
      { value: "12.8k", label: "servers" },
      { value: "99.98%", label: "uptime" },
    ],
    footer: "Open the dashboard",
  },
  b: {
    kicker: "Changelog",
    title: "What shipped this week",
    body: "An iris page transition, a faster command picker, and a quieter moderation log for large servers.",
    tiles: [
      { value: "New", label: "motion lab" },
      { value: "Faster", label: "command picker" },
      { value: "Quieter", label: "mod logs" },
    ],
    footer: "Read the changelog",
  },
};

/** How long the outgoing layout runs before the swap, per transition. */
const OUT_MS: Record<MotionTransition, number> = { iris: 800, morph: 0, blur: 300 };
/** How long the incoming layout runs after the swap. */
const IN_MS: Record<MotionTransition, number> = { iris: 0, morph: 700, blur: 440 };

function DemoPage({ page, layer }: { page: PageKey; layer?: "over" | "under" | "leaving" | "entering" }) {
  const content = PAGES[page];
  return (
    <article className={`motion-page${layer ? ` is-${layer}` : ""}`} data-page={page}>
      <p className="motion-page-kicker" data-morph="kicker">{content.kicker}</p>
      <h3 className="motion-page-title" data-morph="title">{content.title}</h3>
      <p className="motion-page-copy" data-morph="body">{content.body}</p>
      <div className="motion-page-tiles">
        {content.tiles.map((tile, index) => (
          <div className="motion-page-tile" key={tile.label} data-morph={`tile-${index}`}>
            <strong>{tile.value}</strong>
            <span>{tile.label}</span>
          </div>
        ))}
      </div>
      <span className="motion-page-footer" data-morph="footer">
        {content.footer} <Icon name="arrow" />
      </span>
    </article>
  );
}

function InteractionDemos() {
  const [count, setCount] = useState(0);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [ripples, setRipples] = useState<{ id: number; x: number; y: number }[]>([]);
  const [on, setOn] = useState(false);
  const [round, setRound] = useState(0);
  const [loading, setLoading] = useState(true);
  const rippleId = useRef(0);

  const addRipple = (event: ReactMouseEvent<HTMLButtonElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    rippleId.current += 1;
    setRipples((current) => [...current, { id: rippleId.current, x: event.clientX - rect.left, y: event.clientY - rect.top }]);
  };

  const moveTilt = (event: ReactPointerEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setTilt({
      x: (event.clientX - rect.left) / rect.width - 0.5,
      y: (event.clientY - rect.top) / rect.height - 0.5,
    });
  };

  return (
    <div className="motion-demos">
      <div className="motion-demo">
        <span className="motion-demo-title">Press &amp; spring</span>
        <button
          type="button"
          className="motion-demo-button"
          onClick={() => setCount((current) => current + 1)}
        >
          Press me
        </button>
        <small>{count === 0 ? "A press dips, releases with a spring." : `${count} press${count === 1 ? "" : "es"} so far.`}</small>
      </div>

      <div className="motion-demo">
        <span className="motion-demo-title">Pointer tilt</span>
        <div
          className="motion-demo-tilt"
          onPointerMove={moveTilt}
          onPointerLeave={() => setTilt({ x: 0, y: 0 })}
          style={{ transform: `perspective(420px) rotateX(${(-tilt.y * 11).toFixed(2)}deg) rotateY(${(tilt.x * 14).toFixed(2)}deg)` }}
        >
          <strong>Follow the cursor</strong>
          <small>rotateX / rotateY from the pointer offset</small>
        </div>
      </div>

      <div className="motion-demo">
        <span className="motion-demo-title">Ripple</span>
        <button type="button" className="motion-demo-ripple" onClick={addRipple}>
          Tap anywhere
          {ripples.map((ripple) => (
            <span
              key={ripple.id}
              className="motion-demo-ripple-ring"
              style={{ left: ripple.x, top: ripple.y }}
              onAnimationEnd={() => setRipples((current) => current.filter((entry) => entry.id !== ripple.id))}
            />
          ))}
        </button>
        <small>The ring starts at the click point, not the centre.</small>
      </div>

      <div className="motion-demo">
        <span className="motion-demo-title">Toggle</span>
        <button
          type="button"
          role="switch"
          aria-checked={on}
          aria-label="Toggle demo"
          className={`motion-demo-toggle${on ? " is-on" : ""}`}
          onClick={() => setOn((current) => !current)}
        >
          <span />
        </button>
        <small>{on ? "On — knob overshoots, then settles." : "Off — the same spring in reverse."}</small>
      </div>

      <div className="motion-demo">
        <span className="motion-demo-title">Stagger</span>
        <ul className="motion-demo-stagger" key={round}>
          {["Detect", "Translate", "Deliver"].map((label, index) => (
            <li key={label} style={{ animationDelay: `${index * 70}ms` }}>{label}</li>
          ))}
        </ul>
        <button type="button" className="motion-demo-replay" onClick={() => setRound((current) => current + 1)}>Replay</button>
      </div>

      <div className="motion-demo">
        <span className="motion-demo-title">Skeleton</span>
        <div className={`motion-demo-skeleton${loading ? " is-loading" : ""}`}>
          <i /><i /><i />
          <span>{loading ? "Loading a panel" : "A panel, loaded"}</span>
        </div>
        <button type="button" className="motion-demo-replay" onClick={() => setLoading((current) => !current)}>
          {loading ? "Show content" : "Show skeleton"}
        </button>
      </div>
    </div>
  );
}

function ScrollDemo() {
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const parallaxRef = useRef<HTMLDivElement | null>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const root = scrollerRef.current;
    if (!root) return;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) entry.target.classList.add("is-revealed");
        }
      },
      { root, threshold: 0.3, rootMargin: "0px 0px -8% 0px" },
    );
    const nodes = Array.from(root.querySelectorAll<HTMLElement>("[data-reveal]"));
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, []);

  const handleScroll = () => {
    const root = scrollerRef.current;
    if (!root) return;
    const max = root.scrollHeight - root.clientHeight;
    setProgress(max > 0 ? Math.min(1, root.scrollTop / max) : 0);
    if (parallaxRef.current) parallaxRef.current.style.transform = `translate3d(0, ${root.scrollTop * 0.24}px, 0)`;
  };

  return (
    <div className="motion-scroll">
      <div className="motion-scroll-bar" aria-hidden="true"><span style={{ width: `${Math.round(progress * 100)}%` }} /></div>
      <div
        ref={scrollerRef}
        className="motion-scroll-view"
        onScroll={handleScroll}
        tabIndex={0}
        aria-label="Scroll animation demo — scroll inside this box"
      >
        <div ref={parallaxRef} className="motion-scroll-parallax" aria-hidden="true">
          <span /><span /><span />
        </div>
        <div className="motion-scroll-sticky">{Math.round(progress * 100)}% scrolled</div>
        <div className="motion-scroll-inner">
          {["Reveal on entry", "Parallax behind", "A second reveal"].map((title, index) => (
            <article className="motion-scroll-card" key={title} data-reveal>
              <span className="motion-scroll-index">0{index + 1}</span>
              <strong>{title}</strong>
              <p>
                Each card fades and rises the first time it enters the scrolling box, observed through
                IntersectionObserver rooted at this element.
              </p>
            </article>
          ))}
        </div>
      </div>
      <button
        type="button"
        className="motion-lab-ghost"
        onClick={() => scrollerRef.current?.scrollTo({ top: 0, behavior: "smooth" })}
      >
        Back to top
      </button>
    </div>
  );
}

export function MotionLab({
  transition,
  onTransition,
  onClose,
}: {
  transition: MotionTransition;
  onTransition: (transition: MotionTransition) => void;
  onClose: () => void;
}) {
  const [page, setPage] = useState<PageKey>("a");
  // The iris needs the destination on screen while the outgoing page is still
  // underneath, so it is mounted as an over-layer for the length of the run.
  const [destPage, setDestPage] = useState<PageKey | null>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [running, setRunning] = useState<MotionTransition | null>(null);
  const [morphRound, setMorphRound] = useState(0);

  const stageRef = useRef<HTMLDivElement | null>(null);
  const closeRef = useRef<HTMLButtonElement | null>(null);
  const busyRef = useRef(false);
  const timersRef = useRef<number[]>([]);
  const morphRectsRef = useRef<Record<string, DOMRect> | null>(null);

  const clearTimers = useCallback(() => {
    timersRef.current.forEach((id) => window.clearTimeout(id));
    timersRef.current = [];
  }, []);

  const schedule = useCallback((fn: () => void, ms: number) => {
    timersRef.current.push(window.setTimeout(fn, ms));
  }, []);

  // Closing the lab mid-transition takes every pending swap with it.
  useEffect(() => () => clearTimers(), [clearTimers]);

  useEffect(() => {
    closeRef.current?.focus();
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        onClose();
      }
    };
    window.addEventListener("keydown", handleKey, true);
    return () => window.removeEventListener("keydown", handleKey, true);
  }, [onClose]);

  const play = useCallback((kind: MotionTransition) => {
    const stage = stageRef.current;
    if (!stage || busyRef.current) return;
    busyRef.current = true;
    clearTimers();
    morphRectsRef.current = null;
    setRunning(kind);

    const next: PageKey = page === "a" ? "b" : "a";
    const finish = () => {
      busyRef.current = false;
      setPhase("idle");
      setRunning(null);
      setDestPage(null);
    };

    if (kind === "iris") {
      // The destination mounts over the outgoing page, masked to nothing. The
      // mask opens as a real circle whose final size clears this stage's
      // corners, so the geometry is measured here rather than guessed in CSS.
      const bounds = stage.getBoundingClientRect();
      stage.style.setProperty("--iris-size", `${Math.ceil(Math.hypot(bounds.width, bounds.height) * 1.7)}px`);
      // The swap at the end is invisible because the iris has already uncovered
      // the whole frame.
      setDestPage(next);
      setPhase("out");
      schedule(() => {
        setPage(next);
        finish();
      }, OUT_MS.iris);
      return;
    }

    setPhase("out");

    if (kind === "morph") {
      // Measure the layout that is on screen, then mount the destination beside
      // it. Both layers animate in the layout effect below — the old blocks
      // travel to their new slots as they fade, the new ones arrive — so the
      // stage is never empty between the two pages and there is nothing to
      // flash through.
      const rects: Record<string, DOMRect> = {};
      stage.querySelectorAll<HTMLElement>("[data-morph]").forEach((node) => {
        const key = node.dataset.morph;
        if (key) rects[key] = node.getBoundingClientRect();
      });
      morphRectsRef.current = rects;
      setDestPage(next);
      setMorphRound((current) => current + 1);
      schedule(() => {
        setPage(next);
        finish();
      }, IN_MS.morph);
      return;
    }

    schedule(() => {
      setPage(next);
      setPhase("in");
    }, OUT_MS[kind]);
    schedule(finish, OUT_MS[kind] + IN_MS[kind]);
  }, [page, schedule, clearTimers]);

  const playRef = useRef(play);
  playRef.current = play;

  // Opening the lab, or picking another transition in it, previews that
  // transition on the same stage instead of leaving an empty frame.
  useEffect(() => {
    const id = window.setTimeout(() => playRef.current(transition), 260);
    return () => window.clearTimeout(id);
  }, [transition]);

  const selectTransition = (kind: MotionTransition) => {
    if (kind === transition) {
      play(kind);
      return;
    }
    clearTimers();
    morphRectsRef.current = null;
    busyRef.current = false;
    setDestPage(null);
    setPhase("idle");
    setRunning(null);
    onTransition(kind);
  };

  useLayoutEffect(() => {
    const rects = morphRectsRef.current;
    morphRectsRef.current = null;
    const stage = stageRef.current;
    if (!rects || !stage) return;

    const easing = "cubic-bezier(.2,.9,.2,1)";
    const entering = Array.from(stage.querySelectorAll<HTMLElement>(".motion-page.is-entering [data-morph]"));
    const targets = new Map<string, DOMRect>();
    for (const node of entering) {
      const key = node.dataset.morph;
      if (key) targets.set(key, node.getBoundingClientRect());
    }

    // The new blocks fly from the old blocks' rectangles into their own. They
    // stay faint at first so the page that is leaving owns the opening beat.
    for (const node of entering) {
      const key = node.dataset.morph;
      const start = key ? rects[key] : undefined;
      const end = key ? targets.get(key) : undefined;
      if (!start || !end || !end.width || !end.height) continue;
      // Hide the block for the frame before the animation is applied. This is
      // per block rather than on the layer, because a layer-level opacity would
      // multiply the block animations and hide the whole page.
      node.style.opacity = "0";
      node.animate(
        [
          {
            transform: `translate(${start.left - end.left}px, ${start.top - end.top}px) scale(${start.width / end.width}, ${start.height / end.height})`,
            opacity: 0,
            filter: "blur(3px)",
          },
          // Hold the new copy back long enough for the old page to own the
          // opening beat, then bring it through as the old blocks leave.
          { opacity: 0.4, offset: 0.42 },
          { transform: "none", opacity: 1, filter: "blur(0px)" },
        ],
        { duration: 640, easing, fill: "both" },
      );
    }

    // The old blocks make the same journey towards the new slots and fade out
    // on the way, so the two pages read as one transformation rather than a
    // page swap with a gap in between.
    stage.querySelectorAll<HTMLElement>(".motion-page.is-leaving [data-morph]").forEach((node) => {
      const key = node.dataset.morph;
      const target = key ? targets.get(key) : undefined;
      if (!target) return;
      const from = node.getBoundingClientRect();
      if (!from.width || !from.height) return;
      node.animate(
        [
          { transform: "none", opacity: 1, filter: "blur(0px)" },
          { offset: 0.6, opacity: 0 },
          {
            transform: `translate(${target.left - from.left}px, ${target.top - from.top}px) scale(${target.width / from.width}, ${target.height / from.height})`,
            opacity: 0,
            filter: "blur(1.5px)",
          },
        ],
        { duration: 620, easing, fill: "both" },
      );
    });
  }, [morphRound]);

  const activeTransition = MOTION_TRANSITIONS.find((entry) => entry.id === transition) ?? MOTION_TRANSITIONS[0];

  return (
    <div
      className="motion-lab-backdrop"
      onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}
    >
      <div className="motion-lab" role="dialog" aria-modal="true" aria-labelledby="motion-lab-title">
        <header className="motion-lab-head">
          <div>
            <span className="motion-lab-kicker">Owner devtools · Motion</span>
            <h2 id="motion-lab-title">Motion lab</h2>
            <p>Try page transitions, component interactions and scroll animations before they ship.</p>
          </div>
          <button ref={closeRef} type="button" className="motion-lab-close" onClick={onClose} aria-label="Close motion lab">
            <Icon name="close" />
          </button>
        </header>

        <div className="motion-lab-body">
          <section className="motion-lab-section" aria-labelledby="motion-lab-pages">
            <div className="motion-lab-section-head">
              <div>
                <span className="motion-lab-kicker">Page transitions</span>
                <h3 id="motion-lab-pages">Iris, morph and blur</h3>
              </div>
              <div className="motion-lab-controls" role="group" aria-label="Page transition">
                {MOTION_TRANSITIONS.map((entry) => (
                  <button
                    key={entry.id}
                    type="button"
                    aria-pressed={entry.id === transition}
                    className={entry.id === transition ? "is-active" : ""}
                    onClick={() => selectTransition(entry.id)}
                  >
                    {entry.label}
                  </button>
                ))}
                <button type="button" className="motion-lab-play" onClick={() => play(transition)} disabled={phase !== "idle"}>
                  <Icon name="refresh" /> Replay
                </button>
              </div>
            </div>
            <p className="motion-lab-hint">{activeTransition.description}</p>
            <div
              ref={stageRef}
              className="motion-stage"
              data-phase={phase}
              data-motion={running ?? transition}
            >
              {destPage && running === "iris" && <>
                <DemoPage page={page} layer="under" />
                <DemoPage page={destPage} layer="over" />
                <span className="motion-iris-ring" aria-hidden="true" />
              </>}
              {destPage && running === "morph" && <>
                <DemoPage page={page} layer="leaving" />
                <DemoPage page={destPage} layer="entering" />
              </>}
              {!destPage && <DemoPage page={page} />}
            </div>
          </section>

          <section className="motion-lab-section" aria-labelledby="motion-lab-components">
            <div className="motion-lab-section-head">
              <div>
                <span className="motion-lab-kicker">Component interactions</span>
                <h3 id="motion-lab-components">Small, real interactions</h3>
              </div>
            </div>
            <InteractionDemos />
          </section>

          <section className="motion-lab-section" aria-labelledby="motion-lab-scroll">
            <div className="motion-lab-section-head">
              <div>
                <span className="motion-lab-kicker">Scroll animations</span>
                <h3 id="motion-lab-scroll">Reveal, parallax, progress</h3>
              </div>
              <p className="motion-lab-hint">Scroll inside the frame.</p>
            </div>
            <ScrollDemo />
          </section>
        </div>
      </div>
    </div>
  );
}
