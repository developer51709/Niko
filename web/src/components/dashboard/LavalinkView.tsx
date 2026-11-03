import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { addStaffLavalinkNode, applyStaffLavalinkChanges, getStaffLavalinkPool, removeStaffLavalinkNode } from "../../api";
import type { LavalinkNodeRow, LavalinkPoolResponse } from "../../types";
import { Icon } from "../Icon";
import { Switch } from "./Switch";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { useStrings } from "../../i18n";

/** A pool node's status, in the wording the buttons on the panel use. */
function statusTone(status: string) {
  if (status === "connected") return { label: "lavalink.connected", className: "is-online" };
  if (status === "connecting") return { label: "lavalink.connecting", className: "is-connecting" };
  if (status === "disconnected") return { label: "lavalink.disconnected", className: "is-offline" };
  return { label: "lavalink.notInPool", className: "" };
}

function NodeCard({ node, busy, onRemove }: { node: LavalinkNodeRow; busy: boolean; onRemove?: () => void }) {
  const { t } = useStrings("dashboard");
  const tone = statusTone(node.status);
  const title = node.label || node.identifier;
  return (
    <article className={`lavalink-node${node.source === "private" ? " is-private" : ""}`}>
      <div className="lavalink-node-main">
        <span className={`lavalink-node-dot ${tone.className}`} aria-hidden="true" />
        <div className="lavalink-node-title">
          <strong>{title}</strong>
          <small>{node.identifier}{node.secure ? t("lavalink.tls") : t("lavalink.plain")}</small>
        </div>
      </div>
      <div className="lavalink-node-stats">
        <span className={`lavalink-node-status ${tone.className}`}>{t(tone.label)}</span>
        <span title={t("lavalink.playersTitle")}><b>{node.players}</b> {t("lavalink.players")}</span>
        <span title={t("lavalink.heartbeatTitle")}>{node.status === "connected" ? `${Math.round(node.heartbeat)} ms` : "—"}</span>
      </div>
      {onRemove && (
        <button type="button" className="button button-danger button-small" disabled={busy} onClick={onRemove}>
          {t("lavalink.remove")}
        </button>
      )}
    </article>
  );
}

export function LavalinkView({ csrfToken }: { csrfToken?: string }) {
  const { t } = useStrings("dashboard");
  const [data, setData] = useState<LavalinkPoolResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showStatic, setShowStatic] = useState(false);
  const [draft, setDraft] = useState({ host: "", port: "2333", password: "", label: "", secure: true });
  const refreshing = useRef(false);

  const refresh = useCallback(async (silent = false) => {
    if (refreshing.current) return;
    refreshing.current = true;
    try {
      setData(await getStaffLavalinkPool());
      setLoadError("");
    } catch (reason) {
      if (!silent) setLoadError(reason instanceof Error ? reason.message : t("lavalink.poolUnavailable"));
    } finally {
      refreshing.current = false;
      if (!silent) setLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    const load = (silent: boolean) => {
      if (active) void refresh(silent);
    };
    load(false);
    // Status is live state, so it polls while the tab is open — silently, so a
    // transient failure never replaces the panel with an error.
    const timer = window.setInterval(() => {
      if (!document.hidden) load(true);
    }, 10000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [refresh]);

  const nodes = data?.nodes || [];
  const privateNodes = nodes.filter((node) => node.source === "private");
  const staticNodes = nodes.filter((node) => node.source === "static");
  const orphans = nodes.filter((node) => node.source === "orphan");

  const update = (key: keyof typeof draft, value: string | boolean) => setDraft((current) => ({ ...current, [key]: value }));

  const addNode = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    notifyLoading(t("lavalink.savingNode"), "staff-lavalink");
    try {
      const result = await addStaffLavalinkNode(
        { host: draft.host.trim(), port: draft.port.trim(), password: draft.password, secure: draft.secure, label: draft.label.trim() },
        csrfToken,
      );
      setDraft({ host: "", port: "2333", password: "", label: "", secure: true });
      await refresh(true);
      notifySuccess(
        result.applied
          ? t("lavalink.savedAndAdded", { id: result.identifier })
          : t("lavalink.savedNextRescan", { id: result.identifier }),
        "staff-lavalink",
      );
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("lavalink.saveFailed"), "staff-lavalink");
    } finally {
      setBusy(false);
    }
  };

  const removeNode = async (node: LavalinkNodeRow) => {
    if (busy || !window.confirm(t("lavalink.removeConfirm", { id: node.identifier }))) return;
    setBusy(true);
    notifyLoading(t("lavalink.removingNode"), "staff-lavalink");
    try {
      await removeStaffLavalinkNode(node.identifier, csrfToken);
      await refresh(true);
      notifySuccess(t("lavalink.removed", { id: node.identifier }), "staff-lavalink");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("lavalink.removeFailed"), "staff-lavalink");
    } finally {
      setBusy(false);
    }
  };

  const applyChanges = async () => {
    if (busy) return;
    setBusy(true);
    notifyLoading(t("lavalink.rescanning"), "staff-lavalink");
    try {
      await applyStaffLavalinkChanges(csrfToken);
      await refresh(true);
      notifySuccess(t("lavalink.rescanDone"), "staff-lavalink");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("lavalink.rescanFailed"), "staff-lavalink");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="lavalink-view">
      <header className="staff-panel lavalink-headline">
        <div>
          <span className="panel-kicker">{t("lavalink.kicker")}</span>
          <h2>{t("lavalink.title")}</h2>
          <p>
            {t("lavalink.introBefore")} <code>config/lavalink.py</code>{t("lavalink.introAfter")}
          </p>
        </div>
        <div className={`lavalink-pool-badge${(data?.connected || 0) > 0 ? " is-on" : ""}`}>
          <i />
          <span>
            <small>{t("lavalink.pool")}</small>
            <strong>{loading && !data ? t("lavalink.reading") : t("lavalink.connectedOf", { connected: data?.connected ?? 0, target: data?.target ?? 0 })}</strong>
          </span>
        </div>
      </header>

      {loadError && <div className="notice warning" role="status">{loadError}</div>}

      <section className="staff-panel lavalink-section">
        <div className="lavalink-section-heading">
          <div>
            <h3>{t("lavalink.privateTitle")}</h3>
            <p>{t("lavalink.privateText")}</p>
          </div>
          <button type="button" className="button button-muted" onClick={() => void refresh()} disabled={loading}>
            <Icon name="refresh" />{t(loading ? "lavalink.refreshing" : "lavalink.refreshStatus")}
          </button>
        </div>

        {privateNodes.length === 0 ? (
          <div className="lavalink-empty">{t("lavalink.noPrivate")}</div>
        ) : (
          <div className="lavalink-node-list">
            {privateNodes.map((node) => (
              <NodeCard key={node.identifier} node={node} busy={busy} onRemove={() => void removeNode(node)} />
            ))}
          </div>
        )}

        <form className="lavalink-add" onSubmit={addNode}>
          <div className="lavalink-add-heading">
            <span className="panel-kicker">{t("lavalink.addKicker")}</span>
            <small>{t("lavalink.addHint")}</small>
          </div>
          <div className="lavalink-add-fields">
            <label className="form-field"><span className="form-label">{t("lavalink.host")}</span><input value={draft.host} onChange={(event) => update("host", event.target.value)} placeholder="lavalink.example.com" autoComplete="off" required /></label>
            <label className="form-field lavalink-add-port"><span className="form-label">{t("lavalink.port")}</span><input value={draft.port} onChange={(event) => update("port", event.target.value)} inputMode="numeric" placeholder="2333" required /></label>
            <label className="form-field"><span className="form-label">{t("lavalink.password")}</span><input type="password" value={draft.password} onChange={(event) => update("password", event.target.value)} placeholder={t("lavalink.passwordPlaceholder")} autoComplete="new-password" required /></label>
            <label className="form-field"><span className="form-label">{t("lavalink.label")}</span><input value={draft.label} onChange={(event) => update("label", event.target.value)} placeholder={t("lavalink.labelPlaceholder")} maxLength={60} /></label>
          </div>
          <div className="lavalink-add-footer">
            <label className="lavalink-add-secure">
              <Switch checked={draft.secure} onCheckedChange={(value) => update("secure", value)} aria-label={t("lavalink.secureAria")} />
              <span>{t("lavalink.secure")} <small>{t("lavalink.secureHint")}</small></span>
            </label>
            <button type="submit" className="button button-primary" disabled={busy}>{t(busy ? "lavalink.working" : "lavalink.saveAndConnect")}</button>
          </div>
        </form>
      </section>

      {orphans.length > 0 && (
        <section className="staff-panel lavalink-section">
          <div className="lavalink-section-heading">
            <div>
              <h3>{t("lavalink.orphansTitle")}</h3>
              <p>{t("lavalink.orphansText")}</p>
            </div>
            <button type="button" className="button button-muted" onClick={() => void applyChanges()} disabled={busy}>{t("lavalink.rescan")}</button>
          </div>
          <div className="lavalink-node-list">
            {orphans.map((node) => <NodeCard key={node.identifier} node={node} busy={busy} />)}
          </div>
        </section>
      )}

      <section className="staff-panel lavalink-section">
        <div className="lavalink-section-heading">
          <div>
            <h3>{t("lavalink.catalogueTitle")}</h3>
            <p>{t("lavalink.catalogueText", { count: data?.static_count ?? 0 })} <code>config/lavalink.py</code>{t("lavalink.catalogueAfter")}</p>
          </div>
          <div className="lavalink-section-actions">
            <button type="button" className="button button-muted" onClick={() => void applyChanges()} disabled={busy}>
              <Icon name="spark" />{t(busy ? "lavalink.working" : "lavalink.rescan")}
            </button>
            <button type="button" className="button button-muted" onClick={() => setShowStatic((open) => !open)} aria-expanded={showStatic}>
              {t(showStatic ? "lavalink.hide" : "lavalink.show")} {t("lavalink.catalogueWord")}
            </button>
          </div>
        </div>
        {showStatic && (
          <div className="lavalink-node-list">
            {staticNodes.map((node) => <NodeCard key={node.identifier} node={node} busy={busy} />)}
          </div>
        )}
      </section>
    </div>
  );
}
