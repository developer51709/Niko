import { useCallback, useEffect, useState } from "react";
import { getStaffMcpServer, rotateStaffMcpKey } from "../../api";
import { useStrings } from "../../i18n";
import type { StaffMcpGeneratedKey, StaffMcpServer } from "../../types";
import { notifyError, notifySuccess } from "../../utils/toast";
import { Icon } from "../Icon";
import { LoadingCard } from "../LoadingCard";
import { LocaleSyncView } from "./LocaleSyncView";
import { UpdatesView } from "./UpdatesView";

const mcpStyles = `
.mcp-view{display:grid;gap:26px}.mcp-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}.mcp-heading h2{margin:6px 0 7px}.mcp-heading p{max-width:72ch;margin:0;color:var(--muted);font-size:11px;line-height:1.65}.mcp-state{display:inline-flex;align-items:center;gap:6px;padding:5px 8px;color:var(--dim);background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:999px;font:700 9px "Space Mono",monospace;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap}.mcp-state i{width:6px;height:6px;border-radius:50%;background:#d17c72}.mcp-state.is-on{color:var(--sage)}.mcp-state.is-on i{background:var(--sage)}.mcp-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:12px;align-items:start}.mcp-card{padding:17px;background:var(--surface);border:1px solid var(--line);border-radius:10px}.mcp-card h3{margin:5px 0 7px;font-size:14px}.mcp-card p{margin:0 0 12px;color:var(--muted);font-size:10px;line-height:1.65}.mcp-kicker{color:var(--dim);font:700 8px "Space Mono",monospace;letter-spacing:.1em;text-transform:uppercase}.mcp-endpoint{display:flex;align-items:center;gap:7px;min-width:0}.mcp-endpoint code,.mcp-auth code{display:block;min-width:0;overflow:hidden;padding:8px 9px;color:var(--ink);background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:6px;font:10px "Space Mono",monospace;text-overflow:ellipsis;white-space:nowrap}.mcp-endpoint code{flex:1}.mcp-copy{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;flex:0 0 auto;padding:0;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:6px;cursor:pointer}.mcp-copy:hover{color:var(--ink);border-color:var(--line)}.mcp-copy .icon{width:12px;height:12px}.mcp-auth{display:flex;align-items:center;gap:7px;margin-top:7px}.mcp-auth code{flex:1;white-space:normal;overflow-wrap:anywhere}.mcp-note{margin-top:11px;padding:9px 10px;color:var(--muted);background:var(--callout);border-left:2px solid var(--accent);font-size:10px;line-height:1.6}.mcp-note strong{color:var(--ink)}.mcp-note.is-error{border-left-color:#d17c72;color:#e4a39b}.mcp-steps{display:grid;gap:7px;margin:12px 0 0;padding:0;list-style:none;counter-reset:mcp-step}.mcp-steps li{position:relative;padding-left:23px;color:var(--muted);font-size:10px;line-height:1.55;counter-increment:mcp-step}.mcp-steps li:before{position:absolute;top:0;left:0;display:grid;place-items:center;width:16px;height:16px;color:var(--accent-dark);background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:50%;font:700 8px "Space Mono",monospace;content:counter(mcp-step)}.mcp-tools{display:grid;gap:6px;max-height:420px;overflow:auto;padding-right:2px}.mcp-tool{padding:9px 10px;background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:7px}.mcp-tool code{color:var(--accent-dark);font:9px "Space Mono",monospace}.mcp-tool p{margin:3px 0 0;color:var(--dim);font-size:9px;line-height:1.55}.mcp-key-facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:4px 0 12px}.mcp-key-facts div{min-width:0;padding:8px 9px;background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:6px}.mcp-key-facts span{display:block;margin-bottom:3px;color:var(--dim);font:700 7px "Space Mono",monospace;letter-spacing:.08em;text-transform:uppercase}.mcp-key-facts strong{display:block;overflow:hidden;color:var(--ink);font:9px "Space Mono",monospace;text-overflow:ellipsis;white-space:nowrap}.mcp-secret{margin-top:12px;padding:12px;background:var(--callout);border:1px solid var(--accent);border-radius:8px}.mcp-secret h4{margin:4px 0 6px;font-size:12px}.mcp-secret p{margin:0 0 8px;color:var(--muted);font-size:9px;line-height:1.55}.mcp-secret .mcp-endpoint code,.mcp-secret .mcp-auth code{color:var(--ink)}.mcp-secret .mcp-endpoint code{white-space:normal;overflow-wrap:anywhere}.mcp-secret-actions{display:flex;align-items:center;gap:8px;margin-top:8px}.mcp-actions{display:flex;align-items:center;flex-wrap:wrap;gap:9px;margin-top:14px}.mcp-actions small{color:var(--dim);font-size:9px;line-height:1.5}.mcp-embed{min-width:0;padding-top:24px;border-top:1px solid var(--line)}@media(max-width:800px){.mcp-grid{grid-template-columns:1fr}.mcp-heading{display:block}.mcp-state{margin-top:12px}.mcp-key-facts{grid-template-columns:1fr}}`;

/**
 * The owner's single automation page.
 *
 * Locale sync and the deployment feed used to be two tabs. They are one
 * surface now, with the database-backed MCP key and tool catalogue above them,
 * because the MCP server is what replaces beta as the deployment source.
 */
export function McpServerView({ csrfToken }: { csrfToken?: string }) {
  const { t } = useStrings("staff");
  const [data, setData] = useState<StaffMcpServer | null>(null);
  const [error, setError] = useState("");
  const [generated, setGenerated] = useState<StaffMcpGeneratedKey | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setData(await getStaffMcpServer());
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const copy = async (value: string, message: string) => {
    try {
      await navigator.clipboard.writeText(value);
      notifySuccess(message, "staff-mcp");
    } catch {
      notifyError(t("mcp.copyFailed"), "staff-mcp");
    }
  };

  const rotate = async () => {
    if (!csrfToken || busy) return;
    const confirmed = window.confirm(t(data?.configured ? "mcp.rotateConfirm" : "mcp.generateConfirm"));
    if (!confirmed) return;
    setBusy(true);
    try {
      const result = await rotateStaffMcpKey(csrfToken);
      setGenerated(result);
      notifySuccess(t("mcp.rotated"), "staff-mcp");
      await load();
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("mcp.rotateFailed"), "staff-mcp");
    } finally {
      setBusy(false);
    }
  };

  if (error && !data) {
    return <div className="mcp-view"><div className="staff-guild-empty"><p>{error}</p><button type="button" className="button button-muted" onClick={() => void load()}>{t("owner.retry")}</button></div></div>;
  }
  if (!data) return <div className="mcp-view"><LoadingCard message={t("mcp.loading")} /></div>;

  const key = data.key;
  const activeHeader = generated ? `Authorization: Bearer ${generated.key}` : data.auth_header;
  const lastUsed = key.last_used_at ? new Date(key.last_used_at).toLocaleString() : t("mcp.keyNeverUsed");
  const created = key.created_at ? new Date(key.created_at).toLocaleString() : "—";

  return <div className="mcp-view">
    <style>{mcpStyles}</style>
    <header className="mcp-heading">
      <div>
        <span className="panel-kicker">{t("mcp.kicker")}</span>
        <h2>{t("mcp.title")}</h2>
        <p>{t("mcp.body")}</p>
      </div>
      <span className={`mcp-state${data.configured ? " is-on" : ""}`}><i />{data.configured ? t("mcp.configured") : t("mcp.notConfigured")}</span>
    </header>

    <div className="mcp-grid">
      <section className="mcp-card">
        <span className="mcp-kicker">Connection</span>
        <h3>{t("mcp.connectTitle")}</h3>
        <p>{t("mcp.connectBody")}</p>

        {data.configured && <div className="mcp-key-facts">
          <div><span>{t("mcp.keyPrefix")}</span><strong title={key.key_prefix || ""}>{key.key_prefix || "—"}</strong></div>
          <div><span>{t("mcp.keyCreated")}</span><strong title={created}>{created}</strong></div>
          <div><span>{t("mcp.keyLastUsed")}</span><strong title={lastUsed}>{lastUsed}</strong></div>
        </div>}

        <div className="mcp-endpoint">
          <code title={data.endpoint}>{data.endpoint || t("mcp.unavailable")}</code>
          {data.endpoint && <button type="button" className="mcp-copy" onClick={() => void copy(data.endpoint, t("mcp.endpointCopied"))} aria-label={t("mcp.copyEndpoint")}><Icon name="link" /></button>}
        </div>
        <div className="mcp-auth">
          <code>{activeHeader}</code>
          <button type="button" className="mcp-copy" onClick={() => void copy(activeHeader, t("mcp.authCopied"))} aria-label={t("mcp.copyHeader")}><Icon name="link" /></button>
        </div>

        {generated ? <div className="mcp-secret">
          <span className="mcp-kicker">{t("mcp.generatedKicker")}</span>
          <h4>{t("mcp.generatedTitle")}</h4>
          <p>{t("mcp.generatedBody")}</p>
          <div className="mcp-endpoint">
            <code>{generated.key}</code>
            <button type="button" className="mcp-copy" onClick={() => void copy(generated.key, t("mcp.generatedCopied"))} aria-label={t("mcp.copyKey")}><Icon name="link" /></button>
          </div>
          <div className="mcp-secret-actions">
            <button type="button" className="button button-muted button-small" onClick={() => setGenerated(null)}>{t("mcp.dismissKey")}</button>
          </div>
        </div> : <div className={`mcp-note${key.error ? " is-error" : ""}`}>
          {key.error ? <>{t("mcp.keyUnavailable")} <strong>{key.error}</strong></> : data.configured
            ? <><strong>{t("mcp.keyHashNote")}</strong> {t("mcp.keyHashBody")}</>
            : <>{t("mcp.keyMissing")}</>}
        </div>}

        <div className="mcp-actions">
          <button type="button" className="button button-primary button-small" onClick={() => void rotate()} disabled={!csrfToken || busy}>
            {busy ? t("mcp.rotating") : data.configured ? t("mcp.rotateKey") : t("mcp.generateKey")}
          </button>
          <small>{t("mcp.rotationImmediate")}</small>
        </div>

        <ol className="mcp-steps">
          <li>{t("mcp.stepOne")}</li>
          <li>{t("mcp.stepTwo")}</li>
          <li>{t("mcp.stepThree")}</li>
        </ol>

        {data.beta_configured && <div className="mcp-note" role="note">
          {t("mcp.betaStillSet")}
        </div>}
      </section>

      <section className="mcp-card">
        <span className="mcp-kicker">{t("mcp.toolsKicker")}</span>
        <h3>{t("mcp.toolsTitle")}</h3>
        <p>{t("mcp.toolsBody")}</p>
        <div className="mcp-tools">{data.tools.map((tool) => <article className="mcp-tool" key={tool.name}>
          <code>{tool.name}</code>
          <p>{tool.description}</p>
        </article>)}</div>
      </section>
    </div>

    <section className="mcp-embed" aria-label={t("mcp.localeSection")}>
      <LocaleSyncView csrfToken={csrfToken} />
    </section>
    <section className="mcp-embed" aria-label={t("mcp.updateSection")}>
      <UpdatesView csrfToken={csrfToken} />
    </section>
  </div>;
}
