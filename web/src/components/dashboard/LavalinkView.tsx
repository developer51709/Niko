import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { addStaffLavalinkNode, applyStaffLavalinkChanges, getStaffLavalinkPool, removeStaffLavalinkNode } from "../../api";
import type { LavalinkNodeRow, LavalinkPoolResponse } from "../../types";
import { Icon } from "../Icon";
import { Switch } from "./Switch";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";

/** A pool node's status, in the wording the buttons on the panel use. */
function statusTone(status: string) {
  if (status === "connected") return { label: "Connected", className: "is-online" };
  if (status === "connecting") return { label: "Connecting", className: "is-connecting" };
  if (status === "disconnected") return { label: "Disconnected", className: "is-offline" };
  return { label: "Not in pool", className: "" };
}

function NodeCard({ node, busy, onRemove }: { node: LavalinkNodeRow; busy: boolean; onRemove?: () => void }) {
  const tone = statusTone(node.status);
  const title = node.label || node.identifier;
  return (
    <article className={`lavalink-node${node.source === "private" ? " is-private" : ""}`}>
      <div className="lavalink-node-main">
        <span className={`lavalink-node-dot ${tone.className}`} aria-hidden="true" />
        <div className="lavalink-node-title">
          <strong>{title}</strong>
          <small>{node.identifier}{node.secure ? " · TLS" : " · plain"}</small>
        </div>
      </div>
      <div className="lavalink-node-stats">
        <span className={`lavalink-node-status ${tone.className}`}>{tone.label}</span>
        <span title="Players running on this node"><b>{node.players}</b> players</span>
        <span title="Websocket heartbeat">{node.status === "connected" ? `${Math.round(node.heartbeat)} ms` : "—"}</span>
      </div>
      {onRemove && (
        <button type="button" className="button button-danger button-small" disabled={busy} onClick={onRemove}>
          Remove
        </button>
      )}
    </article>
  );
}

export function LavalinkView({ csrfToken }: { csrfToken?: string }) {
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
      if (!silent) setLoadError(reason instanceof Error ? reason.message : "The Lavalink pool is unavailable.");
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
    notifyLoading("Saving the private node…", "staff-lavalink");
    try {
      const result = await addStaffLavalinkNode(
        { host: draft.host.trim(), port: draft.port.trim(), password: draft.password, secure: draft.secure, label: draft.label.trim() },
        csrfToken,
      );
      setDraft({ host: "", port: "2333", password: "", label: "", secure: true });
      await refresh(true);
      notifySuccess(
        result.applied
          ? `${result.identifier} was saved and added to the live pool.`
          : `${result.identifier} was saved. It will join the pool on the next rescan.`,
        "staff-lavalink",
      );
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The private node could not be saved.", "staff-lavalink");
    } finally {
      setBusy(false);
    }
  };

  const removeNode = async (node: LavalinkNodeRow) => {
    if (busy || !window.confirm(`Remove ${node.identifier} from the private node list?\n\nIts players are disconnected and the node leaves the pool.`)) return;
    setBusy(true);
    notifyLoading("Removing the private node…", "staff-lavalink");
    try {
      await removeStaffLavalinkNode(node.identifier, csrfToken);
      await refresh(true);
      notifySuccess(`${node.identifier} was removed.`, "staff-lavalink");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The private node could not be removed.", "staff-lavalink");
    } finally {
      setBusy(false);
    }
  };

  const applyChanges = async () => {
    if (busy) return;
    setBusy(true);
    notifyLoading("Probing the catalogue and rescanning the pool…", "staff-lavalink");
    try {
      await applyStaffLavalinkChanges(csrfToken);
      await refresh(true);
      notifySuccess("Pool rescan finished. Every node above shows its current state.", "staff-lavalink");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The pool could not be rescanned.", "staff-lavalink");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="lavalink-view">
      <header className="staff-panel lavalink-headline">
        <div>
          <span className="panel-kicker">Owner-only · Music backend</span>
          <h2>Lavalink nodes</h2>
          <p>
            The pool is built from two places: the hardcoded catalogue committed in <code>config/lavalink.py</code>, and the private
            nodes you add here. Private nodes are stored in the music database — never in the repository — and always get a pool slot
            ahead of public nodes.
          </p>
        </div>
        <div className={`lavalink-pool-badge${(data?.connected || 0) > 0 ? " is-on" : ""}`}>
          <i />
          <span>
            <small>Pool</small>
            <strong>{loading && !data ? "Reading…" : `${data?.connected ?? 0} / ${data?.target ?? 0} connected`}</strong>
          </span>
        </div>
      </header>

      {loadError && <div className="notice warning" role="status">{loadError}</div>}

      <section className="staff-panel lavalink-section">
        <div className="lavalink-section-heading">
          <div>
            <h3>Private nodes</h3>
            <p>Your own servers. Passwords are sent once, stored in the database, and never returned to the browser.</p>
          </div>
          <button type="button" className="button button-muted" onClick={() => void refresh()} disabled={loading}>
            <Icon name="refresh" />{loading ? "Refreshing…" : "Refresh status"}
          </button>
        </div>

        {privateNodes.length === 0 ? (
          <div className="lavalink-empty">No private nodes yet. Add one below and it joins the pool immediately.</div>
        ) : (
          <div className="lavalink-node-list">
            {privateNodes.map((node) => (
              <NodeCard key={node.identifier} node={node} busy={busy} onRemove={() => void removeNode(node)} />
            ))}
          </div>
        )}

        <form className="lavalink-add" onSubmit={addNode}>
          <div className="lavalink-add-heading">
            <span className="panel-kicker">Add private node</span>
            <small>Use the host and port your Lavalink server listens on. TLS is on unless the server is plain HTTP.</small>
          </div>
          <div className="lavalink-add-fields">
            <label className="form-field"><span className="form-label">Host</span><input value={draft.host} onChange={(event) => update("host", event.target.value)} placeholder="lavalink.example.com" autoComplete="off" required /></label>
            <label className="form-field lavalink-add-port"><span className="form-label">Port</span><input value={draft.port} onChange={(event) => update("port", event.target.value)} inputMode="numeric" placeholder="2333" required /></label>
            <label className="form-field"><span className="form-label">Password</span><input type="password" value={draft.password} onChange={(event) => update("password", event.target.value)} placeholder="Node password" autoComplete="new-password" required /></label>
            <label className="form-field"><span className="form-label">Label (optional)</span><input value={draft.label} onChange={(event) => update("label", event.target.value)} placeholder="Home node" maxLength={60} /></label>
          </div>
          <div className="lavalink-add-footer">
            <label className="lavalink-add-secure">
              <Switch checked={draft.secure} onCheckedChange={(value) => update("secure", value)} aria-label="Connect over HTTPS and WSS" />
              <span>HTTPS / WSS <small>Turn off only for a plain-HTTP node</small></span>
            </label>
            <button type="submit" className="button button-primary" disabled={busy}>{busy ? "Working…" : "Save and connect"}</button>
          </div>
        </form>
      </section>

      {orphans.length > 0 && (
        <section className="staff-panel lavalink-section">
          <div className="lavalink-section-heading">
            <div>
              <h3>Awaiting removal</h3>
              <p>These nodes are still in the live pool but are no longer configured. Rescan to close them.</p>
            </div>
            <button type="button" className="button button-muted" onClick={() => void applyChanges()} disabled={busy}>Rescan pool</button>
          </div>
          <div className="lavalink-node-list">
            {orphans.map((node) => <NodeCard key={node.identifier} node={node} busy={busy} />)}
          </div>
        </section>
      )}

      <section className="staff-panel lavalink-section">
        <div className="lavalink-section-heading">
          <div>
            <h3>Hardcoded catalogue</h3>
            <p>{data?.static_count ?? 0} public nodes ship with the bot in <code>config/lavalink.py</code>. They are read-only here — edit the source to change them.</p>
          </div>
          <div className="lavalink-section-actions">
            <button type="button" className="button button-muted" onClick={() => void applyChanges()} disabled={busy}>
              <Icon name="spark" />{busy ? "Working…" : "Rescan pool"}
            </button>
            <button type="button" className="button button-muted" onClick={() => setShowStatic((open) => !open)} aria-expanded={showStatic}>
              {showStatic ? "Hide" : "Show"} catalogue
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
