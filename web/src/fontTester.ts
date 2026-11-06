/**
 * The site typeface tester.
 *
 * Unlike the rest of the devtools, this is not an owner tool and is not behind
 * any permission check: it is installed for every visitor on every page and is
 * meant to be played with from the browser console.
 *
 *     nikoFont.list()          every face on offer
 *     nikoFont.set("starborn") paint the site in one of them
 *     nikoFont.load("Poppins") try any Google Font by name
 *     nikoFont.reset()         back to the site's own font
 *
 * The choice is per tab (sessionStorage), because it is a toy: it should not
 * follow a visitor into their next visit, and closing the tab is the undo.
 * Everything the site renders reads `--font-sans`, so setting it on `<html>`
 * re-typesets the public pages and the dashboard together.
 */

import { useEffect, useState } from "react";

export type TestFont = {
  key: string;
  label: string;
  /** CSS stack, always falling back to the site's own font. */
  family: string;
  /** Google Fonts family to fetch while this choice is active. */
  google?: string;
  /**
   * Target x-height, as a fraction of the em, for a face that draws far bigger
   * than the site's own. `font-size-adjust` then scales its type size down to
   * this ratio, so it keeps the layout's boxes instead of overflowing them.
   */
  sizeAdjust?: number;
};

const STORAGE_KEY = "niko.font-tester";
const FONT_LINK_ID = "niko-font-tester-link";
const CHANGE_EVENT = "niko:font-change";
const CUSTOM_PREFIX = "custom:";

const SITE_FONT = `"Plus Jakarta Sans", sans-serif`;

/**
 * Plus Jakarta Sans' own x-height: 536 of its 1000 em units. A test face that
 * declares `sizeAdjust` is normalised to this, which is what makes an outsized
 * display font sit in the site's line boxes at the size the site already uses.
 */
const SITE_X_HEIGHT = 0.536;

/**
 * The faces offered by the tester, in the order they are shown.
 *
 * A handful of webfonts sit next to the faces every machine already has, so a
 * candidate can be read against the real page — long headings, dense table
 * rows, the dashboard sidebar — instead of against a specimen sheet. The
 * webfonts are fetched only while they are chosen, so ordinary visits never pay
 * for one that is not in use. Starborn ships with the site (see
 * `styles/test-fonts.css`) because it is not on any system.
 */
export const TEST_FONTS: TestFont[] = [
  // Starborn's x-height is 0.78 em and it draws about half again as wide as the
  // site font, so at the same size it spills out of every card and heading.
  { key: "starborn", label: "Starborn", family: `"Starborn", ${SITE_FONT}`, sizeAdjust: SITE_X_HEIGHT },
  { key: "inter", label: "Inter", family: `"Inter", ${SITE_FONT}`, google: "Inter" },
  { key: "manrope", label: "Manrope", family: `"Manrope", ${SITE_FONT}`, google: "Manrope" },
  { key: "dm-sans", label: "DM Sans", family: `"DM Sans", ${SITE_FONT}`, google: "DM Sans" },
  { key: "space-grotesk", label: "Space Grotesk", family: `"Space Grotesk", ${SITE_FONT}`, google: "Space Grotesk" },
  { key: "outfit", label: "Outfit", family: `"Outfit", ${SITE_FONT}`, google: "Outfit" },
  { key: "system-ui", label: "System UI", family: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` },
  { key: "helvetica", label: "Helvetica / Arial", family: `Helvetica, Arial, sans-serif` },
  { key: "verdana", label: "Verdana", family: `Verdana, Geneva, sans-serif` },
  { key: "trebuchet", label: "Trebuchet MS", family: `"Trebuchet MS", Tahoma, sans-serif` },
  { key: "georgia", label: "Georgia", family: `Georgia, "Times New Roman", serif` },
  { key: "times", label: "Times New Roman", family: `"Times New Roman", Times, serif` },
];

/**
 * Follow the tester, so a control can show the face that is on screen even when
 * the switch happened in the console.
 */
export function useTestFont() {
  const [value, setValue] = useState(readTestFont);
  useEffect(() => {
    const update = () => setValue(readTestFont());
    update();
    window.addEventListener(CHANGE_EVENT, update);
    return () => window.removeEventListener(CHANGE_EVENT, update);
  }, []);
  return value;
}

/** The stored choice: empty, a `TEST_FONTS` key, or `custom:<family>`. */
export function readTestFont(): string {
  try {
    return window.sessionStorage.getItem(STORAGE_KEY) || "";
  } catch {
    return "";
  }
}

function store(value: string) {
  try {
    if (value) window.sessionStorage.setItem(STORAGE_KEY, value);
    else window.sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // Storage can be blocked; the page still switches for this visit below.
  }
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

function googleLink(): HTMLLinkElement {
  let link = document.getElementById(FONT_LINK_ID) as HTMLLinkElement | null;
  if (!link) {
    link = document.createElement("link");
    link.id = FONT_LINK_ID;
    link.rel = "stylesheet";
    document.head.append(link);
  }
  return link;
}

/** The family a Google Fonts CSS request resolves to, quoted for the stack. */
function customStack(family: string) {
  return `"${family.replace(/["']/g, "").trim()}", ${SITE_FONT}`;
}

/**
 * Paint the page with `value` — a `TEST_FONTS` key, `custom:<family>`, or empty
 * for the site's own font.
 */
export function applyTestFont(value: string) {
  const root = document.documentElement;
  const existing = document.getElementById(FONT_LINK_ID);
  const custom = value.startsWith(CUSTOM_PREFIX) ? value.slice(CUSTOM_PREFIX.length).trim() : "";
  const preset = custom ? undefined : TEST_FONTS.find((font) => font.key === value);
  if (!custom && !preset) {
    root.style.removeProperty("--font-sans");
    root.style.removeProperty("font-size-adjust");
    root.removeAttribute("data-font");
    existing?.remove();
    return;
  }
  const family = preset ? preset.family : customStack(custom);
  const google = preset ? preset.google : custom;
  root.style.setProperty("--font-sans", family);
  // Faces that draw too large declare the ratio to normalise to; the rest keep
  // their own metrics, which already fit the site.
  if (preset?.sizeAdjust) root.style.setProperty("font-size-adjust", String(preset.sizeAdjust));
  else root.style.removeProperty("font-size-adjust");
  // Test faces are often single-weight: let the browser draw a bold face while
  // one is active so headings are not left flat (the site itself keeps
  // `font-synthesis: none`).
  root.setAttribute("data-font", preset ? preset.key : custom);
  if (!google) {
    existing?.remove();
    return;
  }
  // Curated faces ask for the weights the site uses; an arbitrary family is
  // requested bare, since Google answers 400 for weights it does not carry.
  const weights = preset ? ":wght@400;500;600;700" : "";
  const href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(google)}${weights}&display=swap`;
  const link = googleLink();
  if (link.getAttribute("href") !== href) link.setAttribute("href", href);
}

/** Switch to one of `TEST_FONTS`, by key or by label. */
export function setTestFont(key: string) {
  if (!key) {
    resetTestFont();
    return;
  }
  const match = TEST_FONTS.find((font) => font.key === key)
    ?? TEST_FONTS.find((font) => font.label.toLowerCase() === key.trim().toLowerCase());
  const value = match ? match.key : key;
  store(value);
  applyTestFont(value);
}

/** Try any Google Font by family name, e.g. `loadTestFont("Poppins")`. */
export function loadTestFont(family: string) {
  const name = family.replace(/["']/g, "").trim();
  if (!name) {
    resetTestFont();
    return;
  }
  const value = `${CUSTOM_PREFIX}${name}`;
  store(value);
  applyTestFont(value);
}

/** Back to the site's own typeface. */
export function resetTestFont() {
  store("");
  applyTestFont("");
}

/** The face the tester is showing, as it reads in a dropdown. */
export function testFontLabel(value: string) {
  if (!value) return "Site default";
  if (value.startsWith(CUSTOM_PREFIX)) return value.slice(CUSTOM_PREFIX.length);
  return TEST_FONTS.find((font) => font.key === value)?.label ?? value;
}

/** Console surface, described once so the help text cannot drift from it. */
export type FontTesterApi = {
  list: () => Pick<TestFont, "key" | "label" | "family">[];
  set: (key: string) => void;
  load: (family: string) => void;
  reset: () => void;
  current: () => string;
  help: () => void;
};

function help() {
  const style = "color:#8bd5b1;font-weight:700";
  console.log("%cNiko font tester", style);
  console.log("  nikoFont.list()            every face on offer");
  console.log('  nikoFont.set("starborn")   paint the site in one of them');
  console.log('  nikoFont.load("Poppins")   try any Google Font by name');
  console.log("  nikoFont.reset()           back to the site's own font");
  console.log("  Faces that draw larger than the site font are scaled down to its x-height.");
  console.log("  Applies to this tab only, and only until it is closed.");
}

/**
 * Install the tester: apply whatever this tab last chose, then publish the
 * console API. Called once from `main.tsx`, before the app renders, so every
 * visitor gets it — no session, role or owner check is involved.
 */
export function installFontTester() {
  applyTestFont(readTestFont());
  window.nikoFont = {
    list: () => TEST_FONTS.map(({ key, label, family }) => ({ key, label, family })),
    set: setTestFont,
    load: loadTestFont,
    reset: resetTestFont,
    current: readTestFont,
    help,
  };
}

declare global {
  interface Window {
    nikoFont: FontTesterApi;
  }
}
