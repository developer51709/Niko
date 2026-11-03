// Owner-only debugging switches.
//
// The state lives in sessionStorage on purpose: it belongs to one browser tab
// session, never to the account, so a bypass cannot follow the owner into a
// later visit and cannot be handed to anybody else.

import { useEffect, useState } from "react";

const SUPPORT_SERVER_BYPASS_KEY = "niko.devtools.bypass-support-server";
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

export const devtools = {
  /** Skip the support-server membership screen on the team application pages. */
  supportServerBypass: () => readFlag(SUPPORT_SERVER_BYPASS_KEY),
  setSupportServerBypass: (enabled: boolean) => writeFlag(SUPPORT_SERVER_BYPASS_KEY, enabled),
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
