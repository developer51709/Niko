import { useCallback, useEffect, useState } from "react";
import { applyOwnerUpdates, getOwnerUpdates } from "../../api";
import { useStrings } from "../../i18n";
import type { OwnerUpdateApply, OwnerUpdates } from "../../types";
import { notifyError, notifySuccess } from "../../utils/toast";
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
 * actually did afterwards.
 */
export function UpdatesView({ csrfToken }: { csrfToken?: string }) {
  const { t } = useStrings("staff");
  const [data, setData] = useState<OwnerUpdates | null>(null);
  const [result, setResult] = useState<OwnerUpdateApply | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const next = await getOwnerUpdates();
      setData(next);
      setSelected((current) => {
        const changed = Object.entries(next.areas ?? {})
          .filter(([, area]) => area.changed > 0)
          .map(([name]) => name);
        // Default to the changed areas on first load, then keep the owner's choice.
        return current.length ? current.filter((name) => name in (next.areas ?? {})) : changed;
      });
      setError("");
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const toggle = (name: string, on: boolean) => {
    setSelected((current) => (on ? [...new Set([...current, name])] : current.filter((item) => item !== name)));
  };

  const apply = async () => {
    setBusy(true);
    setResult(null);
    try {
      const next = await applyOwnerUpdates(selected, csrfToken);
      setResult(next);
      notifySuccess(t("owner.updates.applied"), TOAST_KEY);
      // A bot update retires this process mid-response; reloading lands on the
      // successor, which serves the same page on the same socket.
      if (next.areas?.bot?.ok) window.setTimeout(() => window.location.reload(), 2500);
      else void load();
    } catch (exc) {
      notifyError(exc instanceof Error ? exc.message : String(exc), TOAST_KEY);
    } finally {
      setBusy(false);
    }
  };

  if (error && !data) {
    return (
      <div className="owner-view">
        <div className="owner-empty">
          <p>{error}</p>
          <button type="button" className="button button-muted" onClick={() => void load()}>{t("owner.retry")}</button>
        </div>
      </div>
    );
  }

  if (!data) {
    return <div className="owner-view"><div className="owner-empty"><div className="loading-ring" /><p>{t("owner.loading")}</p></div></div>;
  }

  const areas = Object.entries(data.areas ?? {});
  const picked = areas.filter(([name]) => selected.includes(name));
  const changed = picked.reduce((total, [, area]) => total + area.changed, 0);
  const size = picked.reduce((total, [, area]) => total + area.bytes, 0);

  return (
    <div className="owner-view">
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
        <div className="owner-notice">
          <Icon name="shield" />
          <div>
            <strong>{t("owner.updates.notConfigured")}</strong>
            <p>{t("owner.updates.notConfiguredBody")}</p>
            <code>BETA_INSTANCE_URL=https://beta.example.com</code>
            <code>BETA_UPDATE_TOKEN=…</code>
          </div>
        </div>
      )}

      {data.configured && !data.token_set && (
        <div className="owner-notice">
          <Icon name="alert" />
          <div>
            <strong>{t("owner.updates.noToken")}</strong>
            <p>{t("owner.updates.noTokenBody")}</p>
          </div>
        </div>
      )}

      <div className="owner-area-list">
        {areas.map(([name, area]) => {
          const checked = selected.includes(name);
          return (
            <section className={`owner-area${checked ? " is-selected" : ""}${area.changed ? "" : " is-clean"}`} key={name}>
              <header>
                <div className="owner-area-title">
                  <Switch
                    size="sm"
                    checked={checked}
                    onCheckedChange={(next) => toggle(name, next)}
                    aria-label={t("owner.updates.selectArea", { area: area.label })}
                    disabled={busy || area.changed === 0}
                  />
                  <div>
                    <strong>{area.label}</strong>
                    <small>{t(`owner.area.${name}`)}</small>
                  </div>
                </div>
                <span className={`owner-chip${area.changed ? "" : " is-quiet"}`}>
                  {area.changed
                    ? t("owner.updates.filesChanged", { count: area.changed, size: bytes(area.bytes) })
                    : t("owner.updates.upToDate")}
                </span>
              </header>
              {area.changed > 0 && (
                <details className="owner-files">
                  <summary>{t("owner.updates.showFiles", { count: area.changed })}</summary>
                  <ul>
                    {area.files.map((file) => (
                      <li key={file.path} data-status={file.status}>
                        <span className={`owner-file-tag is-${file.status}`}>{file.status}</span>
                        <code>{file.path}</code>
                        <small>{file.bytes ? bytes(file.bytes) : ""}</small>
                      </li>
                    ))}
                    {area.truncated > 0 && <li className="owner-file-more">{t("owner.updates.moreFiles", { count: area.truncated })}</li>}
                  </ul>
                </details>
              )}
            </section>
          );
        })}
      </div>

      <section className="owner-card owner-apply">
        <div className="owner-card-head">
          <div>
            <span className="panel-kicker">{t("owner.updates.applyKicker")}</span>
            <h3>{t("owner.updates.applyTitle", { count: picked.length })}</h3>
            <p>{t("owner.updates.applyBody", { files: changed, size: bytes(size) })}</p>
          </div>
          <div className="owner-card-actions">
            <button type="button" className="button button-muted" onClick={() => void load()} disabled={busy}>
              <Icon name="search" /> {t("owner.updates.refresh")}
            </button>
            <button
              type="button"
              className="button button-primary"
              onClick={() => void apply()}
              disabled={busy || !data.configured || !selected.length || changed === 0}
            >
              <Icon name="spark" /> {busy ? t("owner.updates.applying") : t("owner.updates.apply")}
            </button>
          </div>
        </div>

        {selected.includes("bot") && (
          <p className="owner-warning">{t("owner.updates.botWarning")}</p>
        )}

        {result && (
          <ul className="owner-results">
            {Object.entries(result.areas ?? {}).map(([name, area]) => (
              <li key={name} className={area.ok === false ? "is-failed" : "is-ok"}>
                <strong>{data.areas[name]?.label ?? name}</strong>
                <span>
                  {area.ok === false
                    ? `${area.error ?? t("owner.updates.failed")}${area.rolled_back ? ` · ${t("owner.updates.rolledBack")}` : ""}`
                    : area.strategy ?? t("owner.updates.done")}
                </span>
                {area.reloaded?.length ? <small>{t("owner.updates.reloaded", { count: area.reloaded.length })}</small> : null}
                {area.failed?.length ? <small className="is-bad">{area.failed.join(" · ")}</small> : null}
              </li>
            ))}
          </ul>
        )}
      </section>

      {data.last && (
        <section className="owner-card">
          <div className="owner-card-head">
            <div>
              <span className="panel-kicker">{t("owner.updates.lastKicker")}</span>
              <h3>{t("owner.updates.lastTitle", { time: ago(data.last.finished_at, t) })}</h3>
              <p>{t("owner.updates.lastBody", { id: data.last.id })}</p>
            </div>
            {data.handoff?.state && <span className="owner-chip is-live">{t(`owner.handoff.${data.handoff.state}`, { pid: data.handoff.pid ?? 0 })}</span>}
          </div>
          <ul className="owner-results">
            {Object.entries(data.last.areas ?? {}).map(([name, area]) => (
              <li key={name} className={area.ok === false ? "is-failed" : "is-ok"}>
                <strong>{data.areas[name]?.label ?? name}</strong>
                <span>{area.ok === false ? area.error : `${area.changed ?? 0} · ${area.strategy ?? ""}`}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
