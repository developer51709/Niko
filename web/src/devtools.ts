// Owner-only debugging switches.
//
// The state lives in sessionStorage on purpose: it belongs to one browser tab
// session, never to the account, so a bypass cannot follow the owner into a
// later visit and cannot be handed to anybody else.

import { useEffect, useState } from "react";

const SUPPORT_SERVER_BYPASS_KEY = "niko.devtools.bypass-support-server";
const PRESENCE_PREVIEW_KEY = "niko.devtools.presence-preview";
const MOTION_TRANSITION_KEY = "niko.devtools.motion-transition";
const SIDE_KEY = "niko.devtools.side";
const CHANGE_EVENT = "niko:devtools-change";

function readFlag(key: string) {
  try {
    return window.sessionStorage.getItem(key) === "1";
  } catch {
    // Storage can be blocked entirely; the switch then simply reads as off.
    return false;
  }
}

function writeFlag(key: string, enabled: boolean) {
  try {
    if (enabled) window.sessionStorage.setItem(key, "1");
    else window.sessionStorage.removeItem(key);
  } catch {
    // Nothing to recover from: the page still re-renders from the flag below.
  }
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

function readValue(key: string) {
  try {
    return window.sessionStorage.getItem(key) || "";
  } catch {
    return "";
  }
}

function writeValue(key: string, value: string) {
  try {
    if (value) window.sessionStorage.setItem(key, value);
    else window.sessionStorage.removeItem(key);
  } catch {
    // Same as above: the panel re-renders from the value it just set.
  }
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

/** The screen edge the devtools button and its panel sit on. */
export type DevtoolsSide = "left" | "right";

/**
 * The side is a layout preference, not a debugging switch, so it is stored in
 * localStorage: pushing the button out of a dashboard sidebar should still hold
 * when the tab is closed and opened again elsewhere.
 */
function readSide(): DevtoolsSide {
  try {
    return window.localStorage.getItem(SIDE_KEY) === "right" ? "right" : "left";
  } catch {
    return "left";
  }
}

function writeSide(side: DevtoolsSide) {
  try {
    window.localStorage.setItem(SIDE_KEY, side);
  } catch {
    // Blocked storage leaves the button where the change already moved it.
  }
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

/** A status the devtools preview paints over every presence dot on the page. */
export type PresencePreview = {
  status: "online" | "idle" | "dnd" | "offline";
  mobile: boolean;
};

const PRESENCE_STATUSES = new Set(["online", "idle", "dnd", "offline"]);

/**
 * Read a stored preview choice (`online`, `dnd_mobile`, ...) into the status
 * and shape an avatar should draw, or `null` when the preview is off.
 */
export function parsePresencePreview(value: string): PresencePreview | null {
  const [status, shape] = String(value || "").split("_");
  if (!PRESENCE_STATUSES.has(status)) return null;
  return { status: status as PresencePreview["status"], mobile: shape === "mobile" };
}

export const devtools = {
  /** Skip the support-server membership screen on the team application pages. */
  supportServerBypass: () => readFlag(SUPPORT_SERVER_BYPASS_KEY),
  setSupportServerBypass: (enabled: boolean) => writeFlag(SUPPORT_SERVER_BYPASS_KEY, enabled),
  /**
   * The presence this tab fakes on every avatar, so the status icons can be
   * checked without waiting for a real client to change. Empty means live.
   */
  presencePreview: () => readValue(PRESENCE_PREVIEW_KEY),
  setPresencePreview: (value: string) => writeValue(PRESENCE_PREVIEW_KEY, value),
  /**
   * The page transition the motion lab should open with. Kept per tab session
   * like the other previews, so the lab remembers what was being judged.
   */
  motionTransition: () => readValue(MOTION_TRANSITION_KEY),
  setMotionTransition: (value: string) => writeValue(MOTION_TRANSITION_KEY, value),
  /** Which edge the button sits on; the panel follows it. */
  side: readSide,
  setSide: writeSide,
};

/**
 * Follow one switch so a page reacts the moment the devtools panel flips it.
 *
 * Pass one of the stable `devtools` readers; the reset inside the effect also
 * covers a remount, when sessionStorage may have changed elsewhere.
 */
export function useDevtoolsFlag(read: () => boolean) {
  const [enabled, setEnabled] = useState(read);
  useEffect(() => {
    const update = () => setEnabled(read());
    update();
    window.addEventListener(CHANGE_EVENT, update);
    return () => window.removeEventListener(CHANGE_EVENT, update);
  }, [read]);
  return enabled;
}

/** The same follow-along read for a switch whose value is a string. */
export function useDevtoolsValue<T extends string>(read: () => T) {
  const [value, setValue] = useState(read);
  useEffect(() => {
    const update = () => setValue(read());
    update();
    window.addEventListener(CHANGE_EVENT, update);
    return () => window.removeEventListener(CHANGE_EVENT, update);
  }, [read]);
  return value;
}
