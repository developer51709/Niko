import { useCallback, useEffect, useState } from "react";
import {
  banOwnerHoneypotIp,
  getOwnerHoneypot,
  saveOwnerHoneypotSettings,
  unbanOwnerHoneypotIp,
} from "../../api";
import { Icon } from "../Icon";
import { LoadingCard } from "../LoadingCard";
import { Switch } from "../dashboard/Switch";
import { useStrings } from "../../i18n";
import { formatNumber } from "../../utils/format";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import type { HoneypotResponse, HoneypotSettings } from "../../types";

const TOAST_KEY = "owner-honeypot";

type Draft = {
  enabled: boolean;
  threshold: string;
  window_seconds: string;
  cooldown_seconds: string;
};

function toDraft(settings: HoneypotSettings): Draft {
  return {
    enabled: settings.enabled,
    threshold: String(settings.threshold),
    window_seconds: String(settings.window_seconds),
    cooldown_seconds: String(settings.cooldown_seconds),
  };
}

function when(timestamp: number | null | undefined) {
  if (!timestamp) return "—";
  const date = new Date(timestamp * 1000);
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleString();
}

function duration(seconds: number) {
  if (seconds >= 86400) return `${Math.round(seconds / 86400)}d`;
  if (seconds >= 3600) return `${Math.round(seconds / 3600)}h`;
  if (seconds >= 60) return `${Math.round(seconds / 60)}m`;
  return `${Math.max(1, Math.round(seconds))}s`;
}

export function HoneypotView({ csrfToken }: { csrfToken?: string }) {
  const { t } = useStrings("staff");
  const [data, setData] = useState<HoneypotResponse | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [reasons, setReasons] = useState<Record<string, string>>({});

  const apply = useCallback((payload: HoneypotResponse) => {
    setData(payload);
    setDraft(toDraft(payload.settings));
    setError(payload.error || "");
  }, []);

  const load = useCallback(async (announce = false) => {
    if (announce) notifyLoading(t("honeypot.refreshing"), TOAST_KEY);
    try {
      const payload = await getOwnerHoneypot();
      apply(payload);
      if (announce) notifySuccess(t("honeypot.refreshed"), TOAST_KEY);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : t("honeypot.loadFailed");
      setError(message);
      if (announce) notifyError(message, TOAST_KEY);
    } finally {
      setLoading(false);
    }
  }, [apply, t]);

  useEffect(() => {
    void load();
  }, [load]);

  const ban = async (ip: string) => {
    if (busy) return;
    if (!window.confirm(t("honeypot.banConfirm", { ip }))) return;
    setBusy(`ban:${ip}`);
    notifyLoading(t("honeypot.banning", { ip }), TOAST_KEY);
    try {
      apply(await banOwnerHoneypotIp(ip, reasons[ip] || "", csrfToken));
      notifySuccess(t("honeypot.banned", { ip }), TOAST_KEY);
    } catch (cause) {
      notifyError(cause instanceof Error ? cause.message : t("honeypot.banFailed"), TOAST_KEY);
    } finally {
      setBusy(null);
    }
  };

  const unban = async (ip: string) => {
    if (busy) return;
    setBusy(`unban:${ip}`);
    notifyLoading(t("honeypot.unbanning", { ip }), TOAST_KEY);
    try {
      apply(await unbanOwnerHoneypotIp(ip, csrfToken));
      notifySuccess(t("honeypot.unbanned", { ip }), TOAST_KEY);
    } catch (cause) {
      notifyError(cause instanceof Error ? cause.message : t("honeypot.unbanFailed"), TOAST_KEY);
    } finally {
      setBusy(null);
    }
  };

  const save = async () => {
    if (!draft || busy) return;
    const threshold = Number(draft.threshold);
    const windowSeconds = Number(draft.window_seconds);
    const cooldownSeconds = Number(draft.cooldown_seconds);
    if (![threshold, windowSeconds, cooldownSeconds].every(Number.isFinite)) {
      notifyError(t("honeypot.settingsNumbers"), TOAST_KEY);
      return;
    }
    setBusy("settings");
    notifyLoading(t("honeypot.saving"), TOAST_KEY);
    try {
      apply(await saveOwnerHoneypotSettings({
        enabled: draft.enabled,
        threshold,
        window_seconds: windowSeconds,
        cooldown_seconds: cooldownSeconds,
      }, csrfToken));
      notifySuccess(t("honeypot.saved"), TOAST_KEY);
    } catch (cause) {
      notifyError(cause instanceof Error ? cause.message : t("honeypot.saveFailed"), TOAST_KEY);
    } finally {
      setBusy(null);
    }
  };

  if (loading && !data) {
    return <div className="honeypot-view"><LoadingCard message={t("honeypot.loading")} /></div>;
  }

  const settings = data?.settings;
  const changed = Boolean(draft && settings && (
    draft.enabled !== settings.enabled
    || Number(draft.threshold) !== settings.threshold
    || Number(draft.window_seconds) !== settings.window_seconds
    || Number(draft.cooldown_seconds) !== settings.cooldown_seconds
  ));

  return (
    <div className="honeypot-view">
      <header className="staff-guilds-heading">
        <div>
          <span className="panel-kicker">{t("honeypot.kicker")}</span>
          <h2>{t("honeypot.title")}</h2>
          <p>{t("honeypot.body")}</p>
        </div>
        <div className="staff-guild-count">
          <strong>{formatNumber(data?.totals.addresses ?? 0)}</strong>
          <span>{t("honeypot.addresses")}</span>
        </div>
      </header>

      {error && <div className="notice warning" role="alert">{error}</div>}

      <div className="honeypot-metrics">
        <div>
          <span className="panel-kicker">{t("honeypot.metricHits")}</span>
          <strong>{formatNumber(data?.totals.hits ?? 0)}</strong>
          <small>{t("honeypot.metricHitsHint")}</small>
        </div>
        <div>
          <span className="panel-kicker">{t("honeypot.metricAddresses")}</span>
          <strong>{formatNumber(data?.totals.addresses ?? 0)}</strong>
          <small>{t("honeypot.metricAddressesHint")}</small>
        </div>
        <div>
          <span className="panel-kicker">{t("honeypot.metricBans")}</span>
          <strong>{formatNumber(data?.totals.bans ?? 0)}</strong>
          <small>{t("honeypot.metricBansHint")}</small>
        </div>
        <div>
          <span className="panel-kicker">{t("honeypot.metricGuard")}</span>
          <strong>{t(settings?.enabled ? "honeypot.guardOn" : "honeypot.guardOff")}</strong>
          <small>{data?.storage === "mongodb"
            ? t("honeypot.storageDatabase")
            : data?.storage === "files"
              ? t("honeypot.storageLocal")
              : t("honeypot.storageUnavailable")}</small>
        </div>
      </div>

      <section className="staff-guild-card honeypot-guard">
        <div className="honeypot-section-head">
          <div>
            <span className="panel-kicker">{t("honeypot.guardKicker")}</span>
            <h3>{t("honeypot.guardTitle")}</h3>
            <p>{t("honeypot.guardBody")}</p>
          </div>
          <div className="honeypot-guard-switch">
            <span className={draft?.enabled ? "honeypot-chip is-on" : "honeypot-chip"}>
              {t(draft?.enabled ? "honeypot.guardOn" : "honeypot.guardOff")}
            </span>
            <Switch
              checked={draft?.enabled ?? false}
              onCheckedChange={(enabled) => setDraft((current) => current ? { ...current, enabled } : current)}
              aria-label={t("honeypot.guardToggle")}
              disabled={!draft || busy === "settings"}
            />
          </div>
        </div>

        <div className="honeypot-settings-grid">
          <label className="form-field">
            <span className="form-label">{t("honeypot.threshold")}</span>
            <input
              type="number"
              min={2}
              max={10000}
              value={draft?.threshold ?? ""}
              onChange={(event) => setDraft((current) => current ? { ...current, threshold: event.target.value } : current)}
              disabled={!draft || busy === "settings"}
            />
            <small>{t("honeypot.thresholdHint")}</small>
          </label>
          <label className="form-field">
            <span className="form-label">{t("honeypot.window")}</span>
            <input
              type="number"
              min={30}
              max={86400}
              value={draft?.window_seconds ?? ""}
              onChange={(event) => setDraft((current) => current ? { ...current, window_seconds: event.target.value } : current)}
              disabled={!draft || busy === "settings"}
            />
            <small>{t("honeypot.windowHint", { duration: duration(Number(draft?.window_seconds) || 300) })}</small>
          </label>
          <label className="form-field">
            <span className="form-label">{t("honeypot.cooldown")}</span>
            <input
              type="number"
              min={60}
              max={2592000}
              value={draft?.cooldown_seconds ?? ""}
              onChange={(event) => setDraft((current) => current ? { ...current, cooldown_seconds: event.target.value } : current)}
              disabled={!draft || busy === "settings"}
            />
            <small>{t("honeypot.cooldownHint", { duration: duration(Number(draft?.cooldown_seconds) || 86400) })}</small>
          </label>
        </div>

        <div className="honeypot-actions">
          <span>{t("honeypot.guardScope")}</span>
          <button
            type="button"
            className="button button-primary button-small"
            onClick={() => void save()}
            disabled={!draft || !changed || busy === "settings"}
          >
            {busy === "settings" ? t("honeypot.saving") : t("honeypot.save")}
          </button>
        </div>
      </section>

      <section className="staff-guild-card honeypot-hits">
        <div className="honeypot-section-head">
          <div>
            <span className="panel-kicker">{t("honeypot.hitsKicker")}</span>
            <h3>{t("honeypot.hitsTitle")}</h3>
            <p>{t("honeypot.hitsBody")}</p>
          </div>
          <button type="button" className="button button-muted button-small" onClick={() => void load(true)} disabled={loading}>
            <Icon name="refresh" /> {t("honeypot.refresh")}
          </button>
        </div>

        {!data?.hits.length ? (
          <div className="honeypot-empty">
            <Icon name="shield" />
            <p>{t("honeypot.empty")}</p>
          </div>
        ) : (
          <div className="honeypot-hit-list">
            {data.hits.map((hit) => (
              <article className={hit.banned ? "honeypot-hit is-banned" : "honeypot-hit"} key={hit.ip}>
                <div className="honeypot-hit-top">
                  <code>{hit.ip}</code>
                  {hit.banned && <span className="honeypot-chip is-danger">{t("honeypot.bannedChip")}</span>}
                  {hit.bannable === false && <span className="honeypot-chip">{t("honeypot.internal")}</span>}
                  <span className="honeypot-hit-count">{t("honeypot.hitCount", { count: hit.hits })}</span>
                </div>
                <div className="honeypot-hit-meta">
                  <span><strong>{hit.last_method}</strong> <code>{hit.last_path}</code></span>
                  <span>{hit.last_host || t("honeypot.unknownHost")}</span>
                  <span>{when(hit.last_seen)}</span>
                </div>
                {hit.last_user_agent && (
                  <details className="honeypot-hit-agent">
                    <summary>{t("honeypot.userAgent")}</summary>
                    <code>{hit.last_user_agent}</code>
                  </details>
                )}
                <div className="honeypot-hit-actions">
                  {hit.banned ? (
                    <button
                      type="button"
                      className="button button-muted button-small"
                      onClick={() => void unban(hit.ip)}
                      disabled={busy === `unban:${hit.ip}`}
                    >
                      {t("honeypot.unban")}
                    </button>
                  ) : hit.bannable === false ? (
                    <span className="honeypot-internal-note">{t("honeypot.internalHint")}</span>
                  ) : (
                    <>
                      <input
                        type="text"
                        value={reasons[hit.ip] || ""}
                        maxLength={500}
                        placeholder={t("honeypot.reasonPlaceholder")}
                        aria-label={t("honeypot.reasonAria", { ip: hit.ip })}
                        onChange={(event) => setReasons((current) => ({ ...current, [hit.ip]: event.target.value }))}
                        disabled={busy === `ban:${hit.ip}`}
                      />
                      <button
                        type="button"
                        className="button button-danger button-small"
                        onClick={() => void ban(hit.ip)}
                        disabled={busy === `ban:${hit.ip}`}
                      >
                        {t("honeypot.ban")}
                      </button>
                    </>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}

        {data?.bans.length ? (
          <div className="honeypot-bans">
            <h4>{t("honeypot.bansTitle")}</h4>
            <div className="honeypot-ban-list">
              {data.bans.map((ban) => (
                <div className="honeypot-ban" key={ban.ip}>
                  <div>
                    <code>{ban.ip}</code>
                    <span>{ban.reason}</span>
                  </div>
                  <small>
                    {ban.expires_at
                      ? t("honeypot.expiresAt", { time: when(ban.expires_at) })
                      : t("honeypot.permanent")}
                    {" · "}
                    {ban.source === "autoban" ? t("honeypot.autoban") : t("honeypot.manualBan")}
                  </small>
                  <button
                    type="button"
                    className="button button-muted button-small"
                    onClick={() => void unban(ban.ip)}
                    disabled={busy === `unban:${ban.ip}`}
                  >
                    {t("honeypot.unban")}
                  </button>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}
