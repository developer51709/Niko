import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent } from "react";
import { addStaffProxyWorker, getStaffProxyWorkers, removeStaffProxyWorker, setStaffProxyWorkerRouting } from "../../api";
import type { ProxyWorker, ProxyWorkerLatencyPoint, ProxyWorkersResponse } from "../../types";
import { Icon } from "../Icon";
import { LoadingCard } from "../LoadingCard";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { type Translate, useStrings } from "../../i18n";

function formatMs(value: number | undefined | null) {
  if (value === undefined || value === null || !Number.isFinite(value)) return "—";
  if (value < 1) return "<1 ms";
  if (value >= 1000) return `${(value / 1000).toFixed(1)} s`;
  return `${Math.round(value)} ms`;
}

function formatBytes(value: number | undefined | null) {
  if (!value) return "0 B";
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function formatUptime(seconds: number | undefined | null) {
  if (seconds === undefined || seconds === null) return "—";
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (days) return `${days}d ${hours}h`;
  if (hours) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function formatClock(timestamp: number) {
  if (!Number.isFinite(timestamp)) return "—";
  return new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function relativeTime(timestamp: number | undefined | null, t: Translate) {
  if (!timestamp) return "—";
  const seconds = Math.max(0, Math.round((Date.now() - timestamp) / 1000));
  if (seconds < 3) return t("proxy.justNow");
  if (seconds < 60) return t("proxy.secondsAgo", { count: seconds });
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return t("proxy.minutesAgo", { count: minutes });
  return t("proxy.hoursAgo", { count: Math.floor(minutes / 60) });
}

function errorRate(requests: number, errors: number) {
  if (!requests) return "0%";
  return `${((errors / requests) * 100).toFixed(errors ? 1 : 0)}%`;
}

function statusTone(status: number | undefined) {
  if (!status || status >= 500) return "is-error";
  if (status >= 400) return "is-warn";
  return "is-ok";
}

function LatencyChart({ points, compact = false, title }: { points: ProxyWorkerLatencyPoint[]; compact?: boolean; title: string }) {
  const { t } = useStrings("dashboard");
  const width = compact ? 520 : 760;
  const height = compact ? 112 : 176;
  const padding = compact ? 12 : 18;
  const visible = points.slice(-180);
  const maximum = Math.max(1, ...visible.map((point) => Math.max(point.avg, point.p95)));
  const step = visible.length > 1 ? (width - padding * 2) / (visible.length - 1) : 0;
  const y = (value: number) => height - padding - (value / maximum) * (height - padding * 2);
  const average = visible.map((point, index) => `${padding + index * step},${y(point.avg)}`).join(" ");
  const upper = visible.map((point, index) => `${padding + index * step},${y(point.p95)}`).join(" ");
  const area = visible.length
    ? `M ${padding},${height - padding} L ${visible.map((point, index) => `${padding + index * step},${y(point.avg)}`).join(" L ")} L ${padding + (visible.length - 1) * step},${height - padding} Z`
    : "";
  const errorBars = visible.map((point, index) => {
    if (!point.errors) return null;
    const barHeight = Math.max(3, (point.errors / Math.max(1, point.count)) * (height - padding * 2));
    return <rect key={point.t} x={padding + index * step - 2} y={height - padding - barHeight} width={4} height={barHeight} rx={2} className="proxy-chart-error" />;
  });
  if (!visible.length) {
    return <div className="proxy-chart-empty"><Icon name="chart" /><span>{t("proxy.waitingFirst")}</span></div>;
  }
  return (
    <figure className={`proxy-chart${compact ? " compact" : ""}`}>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={t("proxy.chartAria", { title })} preserveAspectRatio="none">
        <title>{title}</title>
        {[0.25, 0.5, 0.75].map((fraction) => (
          <line key={fraction} x1={padding} x2={width - padding} y1={padding + (height - padding * 2) * fraction} y2={padding + (height - padding * 2) * fraction} className="proxy-chart-grid" />
        ))}
        <path d={area} className="proxy-chart-area" />
        <polyline points={upper} className="proxy-chart-p95" />
        <polyline points={average} className="proxy-chart-average" />
        {errorBars}
        <circle cx={padding + (visible.length - 1) * step} cy={y(visible[visible.length - 1].avg)} r={compact ? 3 : 4} className="proxy-chart-point" />
      </svg>
      <figcaption>
        <span><i className="proxy-legend-average" />{t("proxy.average")} {formatMs(visible[visible.length - 1]?.avg)}</span>
        <span><i className="proxy-legend-p95" />{t("proxy.p95")} {formatMs(visible[visible.length - 1]?.p95)}</span>
        <span><i className="proxy-legend-error" />{t("proxy.errors")}</span>
        <span className="proxy-chart-window">{formatClock(visible[0].t)} – {formatClock(visible[visible.length - 1].t)}</span>
      </figcaption>
    </figure>
  );
}

function WorkerCard({ worker, expanded, onToggle, onRemove, busy }: {
  worker: ProxyWorker;
  expanded: boolean;
  onToggle: () => void;
  onRemove: () => void;
  busy: boolean;
}) {
  const { t } = useStrings("dashboard");
  const stats = worker.stats;
  const totals = stats?.totals;
  const requests = totals?.requests || 0;
  return (
    <article className={`proxy-worker-card${expanded ? " expanded" : ""}`}>
      <button type="button" className="proxy-worker-row" aria-expanded={expanded} onClick={onToggle}>
        <span className="proxy-worker-mark"><Icon name="shield" /></span>
        <span className="proxy-worker-title">
          <strong>{worker.name}</strong>
          <small>{worker.url}</small>
        </span>
        <span className={`proxy-worker-status${worker.health === "online" ? " is-online" : " is-offline"}`}>
          <i />{t(worker.health === "online" ? "proxy.online" : "proxy.offline")}
        </span>
        <span className="proxy-worker-latency">{requests ? formatMs(totals?.p95_latency_ms) : "—"}</span>
        <Icon name={expanded ? "close" : "arrow"} className="proxy-worker-chevron" />
      </button>
      {expanded && (
        <div className="proxy-worker-details">
          {stats?.stats_error && <div className="notice warning" role="status">{stats.stats_error}</div>}
          <div className="proxy-worker-metrics">
            <div><span className="panel-kicker">{t("proxy.requests")}</span><strong>{requests.toLocaleString()}</strong><small>{t("proxy.errorsCount", { rate: errorRate(requests, totals?.errors || 0) })}</small></div>
            <div><span className="panel-kicker">{t("proxy.average")}</span><strong>{requests ? formatMs(totals?.avg_latency_ms) : "—"}</strong><small>{t("proxy.p95")} {requests ? formatMs(totals?.p95_latency_ms) : "—"}</small></div>
            <div><span className="panel-kicker">{t("proxy.uptime")}</span><strong>{formatUptime(stats?.uptime_seconds)}</strong><small>{stats?.version ? `v${stats.version}` : t("proxy.worker")}</small></div>
            <div><span className="panel-kicker">{t("proxy.bandwidth")}</span><strong>{formatBytes((totals?.bytes_in || 0) + (totals?.bytes_out || 0))}</strong><small>{t("proxy.bandwidthSplit", { inbound: formatBytes(totals?.bytes_in), outbound: formatBytes(totals?.bytes_out) })}</small></div>
          </div>
          <LatencyChart points={stats?.latency || []} compact title={t("proxy.workerLatency", { name: worker.name })} />
          <div className="proxy-worker-footer">
            <span>{stats?.ready === false ? t("proxy.missingToken") : t("proxy.checkedAt", { time: relativeTime(stats?.checked_at, t) })}</span>
            <button type="button" className="button button-danger button-small" disabled={busy} onClick={onRemove}>{t("proxy.removeWorker")}</button>
          </div>
        </div>
      )}
    </article>
  );
}

export function ProxyWorkersView({ csrfToken }: { csrfToken?: string }) {
  const { t } = useStrings("dashboard");
  const [data, setData] = useState<ProxyWorkersResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [refreshedAt, setRefreshedAt] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const refreshing = useRef(false);

  const refresh = useCallback(async (silent = false) => {
    if (refreshing.current) return;
    refreshing.current = true;
    try {
      const result = await getStaffProxyWorkers();
      setData(result);
      setLoadError("");
      setRefreshedAt(Date.now());
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : t("proxy.telemetryUnavailable");
      if (!silent) setLoadError(message);
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
    const timer = window.setInterval(() => {
      if (!document.hidden) load(true);
    }, 3000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [refresh]);

  const routing = data?.routing;
  const workers = data?.workers || [];
  const online = workers.filter((worker) => worker.health === "online").length;
  const usage = data?.usage;
  const feed = data?.feed || [];
  const errors = data?.errors || [];
  const totalRequests = usage?.requests || 0;
  const statusEntries = useMemo(() => Object.entries(usage?.statuses || {}).sort((left, right) => Number(right[1]) - Number(left[1])).slice(0, 6), [usage?.statuses]);

  const addWorker = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    notifyLoading(t("proxy.verifying"), "proxy-workers");
    try {
      await addStaffProxyWorker(name.trim(), url.trim(), csrfToken);
      setName("");
      setUrl("");
      await refresh(true);
      notifySuccess(t("proxy.verified"), "proxy-workers");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("proxy.verifyFailed"), "proxy-workers");
    } finally {
      setBusy(false);
    }
  };

  const removeWorker = async (worker: ProxyWorker) => {
    if (busy || !window.confirm(t("proxy.removeConfirm", { name: worker.name }))) return;
    setBusy(true);
    notifyLoading(t("proxy.removing"), "proxy-workers");
    try {
      await removeStaffProxyWorker(worker.id, csrfToken);
      await refresh(true);
      notifySuccess(t("proxy.removed", { name: worker.name }), "proxy-workers");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("proxy.removeFailed"), "proxy-workers");
    } finally {
      setBusy(false);
    }
  };

  const toggleRouting = async () => {
    if (busy || !routing) return;
    setBusy(true);
    const enabled = !routing.enabled;
    notifyLoading(t(enabled ? "proxy.enablingRouting" : "proxy.returningDirect"), "proxy-workers");
    try {
      await setStaffProxyWorkerRouting(enabled, csrfToken);
      await refresh(true);
      notifySuccess(t(enabled ? "proxy.routingOn" : "proxy.routingOff"), "proxy-workers");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("proxy.routingFailed"), "proxy-workers");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="proxy-workers-view">
      <header className="staff-guilds-heading">
        <div>
          <span className="panel-kicker">{t("proxy.kicker")}</span>
          <h2>{t("proxy.title")}</h2>
          <p>{t("proxy.text")}</p>
        </div>
        <div className={`proxy-routing-badge${routing?.enabled ? " is-on" : ""}`}>
          <i />
          <span><small>{t("proxy.routing")}</small><strong>{t(routing?.enabled ? "proxy.workersActive" : "proxy.direct")}</strong></span>
        </div>
      </header>

      {loadError && <div className="notice warning" role="status">{loadError}</div>}
      {!routing?.token_configured && !loading && (
        <div className="notice warning" role="status">
          {t("proxy.tokenMissingBefore")} <code>PROXY_WORKER_TOKEN</code> {t("proxy.tokenMissingMiddle")} <code>AUTH_TOKEN</code> {t("proxy.tokenMissingAfter")}
        </div>
      )}

      <div className="proxy-toolbar">
        <span className="proxy-live-label"><i />{t(routing?.enabled ? "proxy.live" : "proxy.idle")} · {refreshedAt ? t("proxy.updatedAt", { time: new Date(refreshedAt).toLocaleTimeString() }) : t("proxy.connecting")}</span>
        <div className="proxy-toolbar-actions">
          <button type="button" className={`button button-small ${routing?.enabled ? "button-danger" : "button-primary"}`} disabled={busy || loading || !routing || (!routing.enabled && workers.length === 0)} onClick={() => void toggleRouting()}>
            <Icon name="spark" />{t(routing?.enabled ? "proxy.disableRouting" : "proxy.enableRouting")}
          </button>
          <button type="button" className="button button-small button-muted" disabled={loading} onClick={() => void refresh(false)}><Icon name="refresh" />{t("proxy.refreshNow")}</button>
        </div>
      </div>

      <div className="proxy-overview">
        <div><span className="panel-kicker">{t("proxy.workers")}</span><strong>{t("proxy.onlineOf", { online, total: workers.length })}</strong><small>{t(routing?.enabled ? "proxy.servingRest" : "proxy.registeredNotRouting")}</small></div>
        <div><span className="panel-kicker">{t("proxy.requests")}</span><strong>{totalRequests.toLocaleString()}</strong><small>{t("proxy.workerErrors", { rate: errorRate(totalRequests, usage?.errors || 0) })}</small></div>
        <div><span className="panel-kicker">{t("proxy.averageLatency")}</span><strong>{totalRequests ? formatMs(usage?.avg_latency_ms) : "—"}</strong><small>{t("proxy.p95")} {totalRequests ? formatMs(usage?.p95_latency_ms) : "—"}</small></div>
        <div><span className="panel-kicker">{t("proxy.localFailures")}</span><strong>{routing?.total_failures ?? 0}</strong><small>{t(routing?.last_error ? "proxy.seeRecentErrors" : "proxy.noRelayFailures")}</small></div>
      </div>

      <section className="proxy-graph-card" aria-labelledby="proxy-latency-heading">
        <div className="proxy-section-heading">
          <div><span className="panel-kicker">{t("proxy.last15")}</span><h3 id="proxy-latency-heading">{t("proxy.latencyTitle")}</h3></div>
          <span className="proxy-graph-note">{t("proxy.latencyNote")}</span>
        </div>
        <LatencyChart points={data?.latency || []} title={t("proxy.aggregateLatency")} />
        {statusEntries.length > 0 && (
          <div className="proxy-status-strip" aria-label={t("proxy.statusAria")}>
            {statusEntries.map(([status, count]) => (
              <span key={status} className={Number(status) >= 500 ? "is-error" : Number(status) >= 400 ? "is-warn" : "is-ok"}>
                <b>{status}</b>{Number(count).toLocaleString()}
              </span>
            ))}
          </div>
        )}
      </section>

      <form className="proxy-add-form" onSubmit={(event) => void addWorker(event)}>
        <label className="form-field"><span className="form-label">{t("proxy.workerLabel")}</span><input value={name} onChange={(event) => setName(event.target.value)} maxLength={60} placeholder={t("proxy.workerLabelPlaceholder")} required /></label>
        <label className="form-field"><span className="form-label">{t("proxy.workerOrigin")}</span><input value={url} onChange={(event) => setUrl(event.target.value)} type="url" placeholder="https://niko-discord-proxy.example.workers.dev" required /></label>
        <button type="submit" className="button button-primary" disabled={busy || !routing?.token_configured}>{t(busy ? "proxy.verifyingShort" : "proxy.verifyAndAdd")}</button>
      </form>

      <div className="proxy-worker-list">
        {loading && !data ? <LoadingCard message={t("proxy.loading")} /> : workers.length === 0 ? (
          <div className="staff-guild-empty">
            <Icon name="shield" />
            <span>{t("proxy.noneBefore")} <code>proxy-worker/</code>{t("proxy.noneMiddle")} <code>AUTH_TOKEN</code>{t("proxy.noneAfter")}</span>
          </div>
        ) : workers.map((worker) => (
          <WorkerCard
            key={worker.id}
            worker={worker}
            expanded={expandedId === worker.id}
            onToggle={() => setExpandedId(expandedId === worker.id ? null : worker.id)}
            onRemove={() => void removeWorker(worker)}
            busy={busy}
          />
        ))}
      </div>

      <div className="proxy-live-grid">
        <section className="proxy-live-card" aria-labelledby="proxy-feed-heading">
          <div className="proxy-section-heading">
            <div><span className="panel-kicker">{t("proxy.feedKicker")}</span><h3 id="proxy-feed-heading">{t("proxy.feedTitle")}</h3></div>
            <span className="proxy-graph-note">{t("proxy.feedNote")}</span>
          </div>
          {feed.length === 0 ? <div className="proxy-empty-feed">{t("proxy.feedEmpty")}</div> : (
            <ol className="proxy-feed">
              {feed.slice(0, 18).map((item, index) => (
                <li key={`${item.at}-${index}`}>
                  <span className={`proxy-feed-code ${statusTone(item.status)}`}>{item.status || "ERR"}</span>
                  <span className="proxy-feed-method">{item.method}</span>
                  <code title={item.path}>{item.path}</code>
                  <span className="proxy-feed-latency">{formatMs(item.latency_ms)}</span>
                  <small>{item.worker_name} · {formatClock(item.at)}</small>
                </li>
              ))}
            </ol>
          )}
        </section>

        <section className="proxy-live-card" aria-labelledby="proxy-errors-heading">
          <div className="proxy-section-heading">
            <div><span className="panel-kicker">{t("proxy.errorsKicker")}</span><h3 id="proxy-errors-heading">{t("proxy.errorsTitle")}</h3></div>
            <span className="proxy-graph-note">{t("proxy.newestFirst")}</span>
          </div>
          {errors.length === 0 ? <div className="proxy-empty-feed">{t("proxy.errorsEmpty")}</div> : (
            <ol className="proxy-error-list">
              {errors.slice(0, 10).map((item, index) => (
                <li key={`${item.at}-${index}`}>
                  <span className={`proxy-feed-code ${statusTone(item.status)}`}>{item.status || "ERR"}</span>
                  <div><strong>{item.message || t("proxy.requestFailed")}</strong><small>{item.worker_name || t("proxy.localRelay")} · {item.method} {item.path} · {formatClock(item.at)}</small></div>
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>
    </div>
  );
}
