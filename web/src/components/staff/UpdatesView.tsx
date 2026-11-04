import { useCallback, useEffect, useRef, useState } from "react";
import { applyOwnerUpdates, getOwnerUpdateProgress, getOwnerUpdates } from "../../api";
import { useStrings } from "../../i18n";
import type { OwnerUpdateApply, OwnerUpdateProgress, OwnerUpdates } from "../../types";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { Icon } from "../Icon";
import { Switch } from "../dashboard/Switch";

type Translate = (key: string, values?: Record<string, string | number>) => string;

const TOAST_KEY = "owner-updates";

function bytes(value: number) {
  if (!value) return "0 B";
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

/** How far along the run is, counting the area in flight as partly done. */
function percentOf(progress: OwnerUpdateProgress | null) {
  if (!progress || !progress.total) return 0;
  const inFlight = progress.area && !progress.done.includes(progress.area) ? 0.4 : 0;
  return Math.min(100, Math.round(((progress.done.length + inFlight) / progress.total) * 100));
}

function stageLabel(progress: OwnerUpdateProgress, area: string | undefined, t: Translate) {
  const position = Math.min(progress.total, Math.max(1, progress.index + 1));
  const name = area ?? progress.area ?? "";
  if (progress.phase === "pulling") return t("owner.updates.progressPulling", { area: name, position, total: progress.total });
  if (progress.phase === "applying") return t("owner.updates.progressApplying", { area: name, position, total: progress.total });
  if (progress.phase === "failed") return t("owner.updates.progressFailed", { area: name });
  return t("owner.updates.progressStarting");
}

function ago(timestamp: number | null | undefined, t: Translate) {
  if (!timestamp) return t("owner.never");
  const seconds = Math.max(0, Math.round(Date.now() / 1000 - timestamp));
  if (seconds < 60) return t("owner.justNow");
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return t("owner.minutesAgo", { count: minutes });
  return t("owner.hoursAgo", { count: Math.floor(minutes / 60) });
}

/**
 * The owner's update page.
 *
 * One switch per area, because each area is applied differently: files for the
 * website, a reload for cogs, a module purge for utilities, a Flask rebuild for
 * the API, and a successor process for the bot core. The page names what the
 * selected areas will do before anything is written, and reports what each one
 * actually did afterwards. Areas and the apply panel sit side by side on a
 * desktop and stack on a phone, where the apply panel follows the list.
 */
export function UpdatesView({ csrfToken }: { csrfToken?: string }) {
  const { t } = useStrings("staff");
  const [data, setData] = useState<OwnerUpdates | null>(null);
  const [result, setResult] = useState<OwnerUpdateApply | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState<OwnerUpdateProgress | null>(null);
  // Incremented to abandon a poll loop, on completion and on unmount.
  const pollRef = useRef(0);
  // True once the first load has pre-selected the changed areas. Clearing the
  // selection after an update must survive the refresh that follows it, so only
  // that first load is allowed to choose for the owner.
  const chosenOnce = useRef(false);

  useEffect(() => () => {
    pollRef.current += 1;
  }, []);

  /**
   * Read the feed, and say so in a toast when the owner asked for it.
   *
   * The refresh button is the only caller that announces: the page's own loads
   * (first paint, after an apply) must not stack toasts over the result the
   * owner is already reading.
   */
  const load = useCallback(async (announce = false) => {
    if (announce) notifyLoading(t("owner.updates.refreshing"), TOAST_KEY);
    try {
      const next = await getOwnerUpdates();
      const areas = next.areas ?? {};
      // Decided before the state update, not inside it: a state updater has to
      // stay pure, and the first load is the only one that picks for the owner.
      const firstLoad = !chosenOnce.current;
      chosenOnce.current = true;
      const defaults = Object.entries(areas)
        .filter(([, area]) => area.changed > 0)
        .map(([name]) => name);
      setData(next);
      // Default to the changed areas on first load, then keep the owner's choice.
      setSelected((current) => (firstLoad ? defaults : current.filter((name) => name in areas)));
      setError("");
      if (announce) {
        notifySuccess(t("owner.updates.refreshed", { count: next.total_changed }), TOAST_KEY);
      }
      return next;
    } catch (exc) {
      const message = exc instanceof Error ? exc.message : String(exc);
      setError(message);
      if (announce) notifyError(message, TOAST_KEY);
      return null;
    }
  }, [t]);

  useEffect(() => {
    void load();
  }, [load]);

  const toggle = (name: string, on: boolean) => {
    setSelected((current) => (on ? [...new Set([...current, name])] : current.filter((item) => item !== name)));
  };

  const apply = async () => {
    setBusy(true);
    setResult(null);
    setProgress(null);
    notifyLoading(t("owner.updates.progressStarting"), TOAST_KEY);

    // The apply request stays open until every area has been written; the bar,
    // the step list and the toast read the server's own run state meanwhile.
    const token = ++pollRef.current;
    const tick = async () => {
      try {
        const next = await getOwnerUpdateProgress();
        if (pollRef.current !== token) return;
        setProgress(next);
        if (next.active) {
          notifyLoading(stageLabel(next, next.area ? data?.areas[next.area]?.label : undefined, t), TOAST_KEY);
        }
      } catch {
        // A bot handoff can drop one poll; the next one lands on the successor.
      }
      if (pollRef.current === token) window.setTimeout(tick, 700);
    };
    void tick();

    try {
      const next = await applyOwnerUpdates(selected, csrfToken);
      setResult(next);
      // The applied areas are no longer waiting, so the selection that produced
      // them is cleared rather than left ticked for the refreshed list.
      setSelected([]);
      notifySuccess(t("owner.updates.applied"), TOAST_KEY);
      // A bot update retires this process mid-response; reloading lands on the
      // successor, which serves the same page on the same socket.
      if (next.areas?.bot?.ok) window.setTimeout(() => window.location.reload(), 2500);
      else void load();
    } catch (exc) {
      notifyError(exc instanceof Error ? exc.message : String(exc), TOAST_KEY);
    } finally {
      pollRef.current += 1;
      setProgress(null);
      setBusy(false);
    }
  };

  if (error && !data) {
    return (
      <div className="updates-view">
        <div className="staff-guild-empty updates-state">
          <span className="updates-state-mark is-bad"><Icon name="alert" /></span>
          <p>{error}</p>
          <button type="button" className="button button-muted" onClick={() => void load()}>{t("owner.retry")}</button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="updates-view">
        <div className="staff-guild-empty updates-state">
          <span className="updates-state-mark"><div className="loading-ring" /></span>
          <p>{t("owner.loading")}</p>
        </div>
      </div>
    );
  }

  const areas = Object.entries(data.areas ?? {});
  const picked = areas.filter(([name]) => selected.includes(name));
  const changed = picked.reduce((total, [, area]) => total + area.changed, 0);
  const size = picked.reduce((total, [, area]) => total + area.bytes, 0);
  const percent = percentOf(progress);
  const activeLabel = progress ? stageLabel(progress, progress.area ? data.areas[progress.area]?.label : undefined, t) : t("owner.updates.progressStarting");

  return (
    <div className="updates-view" aria-busy={busy}>
      <header className="staff-guilds-heading">
        <div>
          <span className="panel-kicker">{t("owner.updates.kicker")}</span>
          <h2>{t("owner.updates.title")}</h2>
          <p>{t("owner.updates.body")}</p>
        </div>
        <div className="staff-guild-count">
          <strong>{data.total_changed}</strong>
          <span>{t("owner.updates.pendingCount", { size: bytes(data.total_bytes) })}</span>
        </div>
      </header>

      {!data.configured && (
        <div className="updates-notice" role="note">
          <span className="updates-notice-mark"><Icon name="shield" /></span>
          <div>
            <strong>{t("owner.updates.notConfigured")}</strong>
            <p>{t("owner.updates.notConfiguredBody")}</p>
            <div className="updates-notice-code">
              <code>BETA_INSTANCE_URL=https://beta.example.com</code>
              <code>BETA_UPDATE_TOKEN=…</code>
            </div>
          </div>
        </div>
      )}

      {data.configured && !data.token_set && (
        <div className="updates-notice is-warn" role="note">
          <span className="updates-notice-mark"><Icon name="alert" /></span>
          <div>
            <strong>{t("owner.updates.noToken")}</strong>
            <p>{t("owner.updates.noTokenBody")}</p>
          </div>
        </div>
      )}

      <div className="updates-layout">
        <section className="staff-guild-card updates-panel updates-areas">
          <header className="updates-panel-head">
            <div className="updates-panel-copy">
              <span className="panel-kicker">{t("owner.updates.areasKicker")}</span>
              <h3>{t("owner.updates.areasTitle")}</h3>
              <p>{t("owner.updates.areasBody")}</p>
            </div>
            <span className="updates-tally">
              {t("owner.updates.selectedCount", { selected: picked.length, total: areas.length })}
            </span>
          </header>

          <div className="updates-area-list">
            {areas.map(([name, area]) => {
              const checked = selected.includes(name);
              return (
                <article className={`updates-area${checked ? " is-selected" : ""}${area.changed ? "" : " is-clean"}`} key={name}>
                  <div className="updates-area-main">
                    <Switch
                      size="sm"
                      checked={checked}
                      onCheckedChange={(next) => toggle(name, next)}
                      aria-label={t("owner.updates.selectArea", { area: area.label })}
                      disabled={busy || area.changed === 0}
                    />
                    <div className="updates-area-copy">
                      <div className="updates-area-heading">
                        <h4>{area.label}</h4>
                        <span className={`updates-badge${area.changed ? "" : " is-quiet"}`}>
                          {area.changed
                            ? t("owner.updates.filesChanged", { count: area.changed, size: bytes(area.bytes) })
                            : t("owner.updates.upToDate")}
                        </span>
                      </div>
                      <p>{t(`owner.area.${name}`)}</p>
                    </div>
                  </div>

                  {area.changed > 0 && (
                    <details className="updates-files">
                      <summary>
                        <Icon name="file" />
                        <span>{t("owner.updates.showFiles", { count: area.changed })}</span>
                        {/* A real disclosure arrow rather than a text glyph:
                            it inherits the icon stroke and turns with the
                            panel instead of sitting fixed. */}
                        <Icon name="chevron" className="updates-files-caret" />
                      </summary>
                      <ul>
                        {area.files.map((file) => (
                          <li key={file.path} data-status={file.status}>
                            <span className={`updates-file-tag is-${file.status}`}>{file.status}</span>
                            <code>{file.path}</code>
                            <small>{file.bytes ? bytes(file.bytes) : ""}</small>
                          </li>
                        ))}
                        {area.truncated > 0 && <li className="updates-file-more">{t("owner.updates.moreFiles", { count: area.truncated })}</li>}
                      </ul>
                    </details>
                  )}
                </article>
              );
            })}
          </div>
        </section>

        <aside className="updates-side">
          <section className="staff-guild-card updates-panel updates-apply">
            <div className="updates-panel-copy">
              <span className="panel-kicker">{t("owner.updates.applyKicker")}</span>
              <h3>{t("owner.updates.applyTitle", { count: picked.length })}</h3>
              <p>{t("owner.updates.applyBody", { files: changed, size: bytes(size) })}</p>
            </div>

            {busy ? (
              <div className="updates-progress">
                <div className="updates-progress-head">
                  <span className="panel-kicker">{t("owner.updates.progressKicker")}</span>
                  <strong>{percent}%</strong>
                </div>
                <div
                  className="updates-progress-track"
                  role="progressbar"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={percent}
                  aria-label={t("owner.updates.progressAria")}
                >
                  <span style={{ width: `${percent}%` }} />
                </div>
                <p className="updates-progress-line" aria-live="polite">{activeLabel}</p>
                <ol className="updates-progress-steps">
                  {picked.map(([name, area]) => {
                    const state = progress?.done.includes(name) ? "done" : progress?.area === name ? "active" : "pending";
                    return (
                      <li key={name} className={`is-${state}`}>
                        <i aria-hidden="true" />
                        <span>{area.label}</span>
                        <small>{t(`owner.updates.progressStep.${state}`)}</small>
                      </li>
                    );
                  })}
                </ol>
              </div>
            ) : picked.length > 0 && (
              <ul className="updates-picks" aria-label={t("owner.updates.picksAria")}>
                {picked.map(([name, area]) => (
                  <li key={name}>{area.label}</li>
                ))}
              </ul>
            )}

            <div className="updates-apply-actions">
              <button
                type="button"
                className="button button-primary"
                onClick={() => void apply()}
                disabled={busy || !data.configured || !selected.length || changed === 0}
              >
                <Icon name="spark" /> {busy ? t("owner.updates.applying") : t("owner.updates.apply")}
              </button>
              <button type="button" className="button button-muted" onClick={() => void load(true)} disabled={busy}>
                <Icon name="refresh" /> {t("owner.updates.refresh")}
              </button>
            </div>

            {selected.includes("bot") && (
              <p className="updates-warning" role="note">
                <Icon name="alert" />
                <span>{t("owner.updates.botWarning")}</span>
              </p>
            )}

            {result && (
              <ul className="updates-results" role="status" aria-live="polite">
                {Object.entries(result.areas ?? {}).map(([name, area]) => (
                  <li key={name} className={area.ok === false ? "is-failed" : "is-ok"}>
                    <span className="updates-result-mark"><Icon name={area.ok === false ? "close" : "check"} /></span>
                    <div className="updates-result-copy">
                      <strong>{data.areas[name]?.label ?? name}</strong>
                      <span>
                        {area.ok === false
                          ? `${area.error ?? t("owner.updates.failed")}${area.rolled_back ? ` · ${t("owner.updates.rolledBack")}` : ""}`
                          : area.strategy ?? t("owner.updates.done")}
                      </span>
                      {area.reloaded?.length ? <small>{t("owner.updates.reloaded", { count: area.reloaded.length })}</small> : null}
                      {area.failed?.length ? <small className="is-bad">{area.failed.join(" · ")}</small> : null}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </aside>
      </div>

      {data.last && (
        <section className="staff-guild-card updates-panel updates-last">
          <header className="updates-panel-head">
            <div className="updates-panel-copy">
              <span className="panel-kicker">{t("owner.updates.lastKicker")}</span>
              <h3>{t("owner.updates.lastTitle", { time: ago(data.last.finished_at, t) })}</h3>
              <p>{t("owner.updates.lastBody", { id: data.last.id })}</p>
            </div>
            {data.handoff?.state && (
              <span className="updates-live">{t(`owner.handoff.${data.handoff.state}`, { pid: data.handoff.pid ?? 0 })}</span>
            )}
          </header>
          <ul className="updates-results is-history">
            {Object.entries(data.last.areas ?? {}).map(([name, area]) => (
              <li key={name} className={area.ok === false ? "is-failed" : "is-ok"}>
                <span className="updates-result-mark"><Icon name={area.ok === false ? "close" : "check"} /></span>
                <div className="updates-result-copy">
                  <strong>{data.areas[name]?.label ?? name}</strong>
                  <span>{area.ok === false ? area.error : `${area.changed ?? 0} · ${area.strategy ?? ""}`}</span>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
