import { useEffect, useState } from "react";
import { getSiteBuild } from "../api";
import { useStrings } from "../i18n";
import { siteBuild } from "../router";
import { Icon } from "./Icon";

/** How often a tab that is being read asks whether the site has moved on. */
const VISIBLE_CHECK_MS = 20_000;

/** A hidden tab is not being looked at, so it asks far less often. */
const HIDDEN_CHECK_MS = 60_000;

/** A check that has not answered by then is dropped, so the poll keeps going. */
const CHECK_TIMEOUT_MS = 10_000;

/** A dismissed notice stays quiet for that one build, never for the next. */
const DISMISSED_KEY = "niko.site.dismissedBuild";

function dismissedBuild(): string {
  try {
    return sessionStorage.getItem(DISMISSED_KEY) ?? "";
  } catch {
    // Storage can be unavailable (private mode, blocked cookies). The notice
    // then simply cannot be dismissed for longer than this visit.
    return "";
  }
}

/**
 * Offers a reload when the page is running a build the site has replaced.
 *
 * The server names the build it served in the shell (see
 * `social.render_site_shell`), so this can only ever fire for a tab that is
 * genuinely behind: a deploy that changes anything in the bundle gives the new
 * one a different name, while a server-only update leaves the name alone and
 * nothing is shown.
 *
 * The check runs on its own timer, so the notice appears while someone is
 * sitting on the page rather than only once they come back to the tab. A
 * visible tab asks every twenty seconds; a hidden one drops to a slow poll (a
 * background tab's timers are throttled anyway) and checks immediately when it
 * is focused, shown again, or comes back online.
 */
export function UpdatePrompt() {
  const ours = siteBuild();
  const { t } = useStrings("shared");
  const [latest, setLatest] = useState("");
  const [dismissed, setDismissed] = useState(dismissedBuild);

  useEffect(() => {
    if (!ours) return;
    let live = true;
    let timer = 0;

    // One pending timer at a time: a focus check that lands while another is
    // already scheduled replaces it instead of adding a second poller.
    const schedule = () => {
      window.clearTimeout(timer);
      const delay = document.visibilityState === "visible" ? VISIBLE_CHECK_MS : HIDDEN_CHECK_MS;
      timer = window.setTimeout(() => void check(), delay);
    };

    const check = async () => {
      if (!live) return;
      try {
        // A hung request must not stop the poll: it is dropped and the next one
        // is scheduled like any other.
        const next = await getSiteBuild(AbortSignal.timeout(CHECK_TIMEOUT_MS));
        if (live && next.build) setLatest(next.build);
      } catch {
        // A failed check says nothing about the build; the next one may work.
      } finally {
        // Whether the answer was new or the request failed, the poll goes on.
        if (live) schedule();
      }
    };

    const checkNow = () => {
      window.clearTimeout(timer);
      void check();
    };

    const onVisibility = () => {
      if (document.visibilityState === "visible") checkNow();
      else schedule();
    };

    void check();
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("focus", checkNow);
    window.addEventListener("pageshow", checkNow);
    window.addEventListener("online", checkNow);
    return () => {
      live = false;
      window.clearTimeout(timer);
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("focus", checkNow);
      window.removeEventListener("pageshow", checkNow);
      window.removeEventListener("online", checkNow);
    };
  }, [ours]);

  if (!ours || !latest || latest === ours || latest === dismissed) return null;

  const dismiss = () => {
    setDismissed(latest);
    try {
      sessionStorage.setItem(DISMISSED_KEY, latest);
    } catch {
      // Nothing to remember it with; it stays dismissed for this page.
    }
  };

  return (
    <div className="update-prompt" role="status" aria-live="polite">
      <span className="update-prompt-mark" aria-hidden="true"><Icon name="refresh" /></span>
      <div className="update-prompt-copy">
        <span className="panel-kicker">{t("update.kicker")}</span>
        <p>{t("update.body")}</p>
      </div>
      <div className="update-prompt-actions">
        <button type="button" className="button button-primary button-small" onClick={() => window.location.reload()}>
          {t("update.reload")}
        </button>
        <button type="button" className="button button-muted button-small" onClick={dismiss}>
          {t("update.later")}
        </button>
      </div>
    </div>
  );
}
