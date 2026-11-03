import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { getStatus } from "../api";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useStrings } from "../i18n";
import type { CogState, StatusCoverage, StatusPayload, StatusState } from "../types";
import { formatNumber } from "../utils/format";

const POLL_MS = 5_000;

// Wording lives in the ``status`` catalogue; these maps only say which key a
// state reads, so the pills and rows all change language together.
const STATE_KEYS: Record<StatusState, string> = {
  operational: "state.operational",
  degraded: "state.degraded",
  maintenance: "state.maintenance",
  starting: "state.starting",
  offline: "state.offline",
};

const STATE_TONE: Record<StatusState, string> = {
  operational: "ok",
  degraded: "warn",
  maintenance: "warn",
  starting: "wait",
  offline: "bad",
};

const COG_KEYS: Record<CogState, string> = {
  loaded: "cog.loaded",
  disabled: "cog.disabled",
  maintenance: "cog.maintenance",
  failed: "cog.failed",
};

const COG_TONE: Record<CogState, string> = {
  loaded: "ok",
  disabled: "wait",
  maintenance: "warn",
  failed: "bad",
};

function formatUptime(seconds?: number | null) {
  if (seconds === null || seconds === undefined) return "—";
  const total = Math.max(Math.floor(seconds), 0);
  const days = Math.floor(total / 86_400);
  const hours = Math.floor((total % 86_400) / 3_600);
  const minutes = Math.floor((total % 3_600) / 60);
  if (days) return `${days}d ${hours}h`;
  if (hours) return `${hours}h ${minutes}m`;
  if (minutes) return `${minutes}m ${total % 60}s`;
  return `${total}s`;
}

function formatClock(seconds?: number) {
  if (!seconds) return "—";
  return new Date(seconds * 1000).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

/** A thin fill bar; the parent row always prints the same figure as text. */
function Meter({ percent, tone = "" }: { percent: number; tone?: string }) {
  const clamped = Math.min(100, Math.max(0, percent));
  return (
    <span className={`status-meter${tone ? ` ${tone}` : ""}`} aria-hidden="true">
      <span style={{ width: `${clamped}%` }} />
    </span>
  );
}

function coverageTone(row: StatusCoverage) {
  if (row.total === 0 || row.missing === 0) return "is-complete";
  return row.percent >= 90 ? "is-near" : "is-partial";
}

/** One language's translation progress, used by both coverage tables. */
function CoverageRow({ row }: { row: StatusCoverage }) {
  const { t } = useStrings("status");

  return (
    <li className={`status-locale-card ${coverageTone(row)}`}>
      <div className="status-locale-head">
        <span className="status-locale-code">{row.code}</span>
        <span className="status-locale-name">{row.label}</span>
        <strong className="status-locale-percent">{row.percent}%</strong>
      </div>
      <Meter percent={row.percent} tone={coverageTone(row)} />
      {/* One wrapping line instead of right-aligned columns: the same card reads
          correctly in a phone column and in the desktop grid. */}
      <p className="status-locale-meta">
        {t("locales.figures", { translated: formatNumber(row.translated), total: formatNumber(row.total) })}
        {row.missing > 0
          ? ` ${t("locales.missing", { count: formatNumber(row.missing) })}`
          : ` ${t("locales.completeWord")}`}
        {row.complete_pages !== undefined && row.pages !== undefined && (
          <> · {t("locales.pagesDone", { done: formatNumber(row.complete_pages), total: formatNumber(row.pages) })}</>
        )}
      </p>
    </li>
  );
}

export function StatusPage() {
  const { t } = useStrings("status");
  const [data, setData] = useState<StatusPayload | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [updatedAt, setUpdatedAt] = useState<number | null>(null);
  const hasData = useRef(false);
  const inFlight = useRef(false);

  const load = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    try {
      const payload = await getStatus();
      hasData.current = true;
      setData(payload);
      setUpdatedAt(Date.now());
      setError("");
    } catch (reason) {
      // A failed poll keeps the last snapshot on screen and lets the next one
      // catch up; only a first load that never landed is an error.
      if (!hasData.current) {
        setError(reason instanceof Error ? reason.message : "error.generic");
      }
    } finally {
      inFlight.current = false;
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const timer = window.setInterval(() => {
      if (document.visibilityState === "hidden") return;
      void load();
    }, POLL_MS);
    // Coming back to the tab should not wait out the rest of the interval.
    const onVisible = () => {
      if (document.visibilityState === "visible") void load();
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [load]);

  const bot = data?.bot ?? null;
  const state = data?.state ?? "offline";
  const cogs = data?.cogs ?? [];
  const shards = data?.shards ?? [];
  const host = data?.host;
  const locales = data?.locales;

  const cogCounts = data?.cog_counts;
  const issueCount = (cogCounts?.disabled ?? 0) + (cogCounts?.maintenance ?? 0) + (cogCounts?.failed ?? 0);

  const averageLatency = useMemo(() => {
    const values = shards.map((shard) => shard.latency_ms).filter((value): value is number => typeof value === "number");
    if (!values.length) return null;
    return Math.round(values.reduce((total, value) => total + value, 0) / values.length);
  }, [shards]);

  const localeComplete = useMemo(() => {
    if (!locales) return 0;
    const rows = [...locales.bot, ...locales.website];
    return rows.filter((row) => row.total > 0 && row.missing === 0).length;
  }, [locales]);

  return <>
    <PublicHeader page="status" />
    <main className="shell page-main status-page">
      <section className="status-hero">
        <div className="status-hero-copy">
          <span className="eyebrow"><span className={`status-live-dot ${STATE_TONE[state]}`} />{t("hero.eyebrow")}</span>
          <h1>{t("hero.title")} <em>{t("hero.titleEm")}</em></h1>
          <p>{t("hero.body")}</p>
        </div>
        <div className={`status-verdict status-verdict-${STATE_TONE[state]}`} aria-live="polite">
          <span className={`status-pill ${STATE_TONE[state]}`}>{t(STATE_KEYS[state])}</span>
          <small>
            {loading && !data
              ? t("verdict.loading")
              : updatedAt
                ? t("verdict.updated", { time: new Date(updatedAt).toLocaleTimeString("en-GB") })
                : t("verdict.waiting")}
          </small>
          <button className="status-refresh" type="button" onClick={() => void load()} disabled={loading}>
            <Icon name="refresh" /> {t("verdict.refresh")}
          </button>
        </div>
      </section>

      {error && !data
        ? <div className="status-error" role="alert">
          <Icon name="alert" />
          <div><strong>{t("error.title")}</strong><p>{error.startsWith("error.") ? t(error) : error}</p></div>
          <button className="button button-muted button-small" type="button" onClick={() => void load()}>{t("error.retry")}</button>
        </div>
        : <>
          <section className="status-metrics" aria-label={t("metrics.aria")}>
            <article className="status-metric">
              <span className="panel-kicker">{t("metrics.latency")}</span>
              <strong>{bot?.latency_ms !== null && bot?.latency_ms !== undefined ? `${bot.latency_ms} ms` : "—"}</strong>
              <small>{averageLatency !== null ? t("metrics.latencyAverage", { ms: averageLatency }) : t("metrics.notConnected")}</small>
            </article>
            <article className="status-metric">
              <span className="panel-kicker">{t("metrics.uptime")}</span>
              <strong>{formatUptime(bot?.uptime_seconds)}</strong>
              <small>{bot?.started_at ? t("metrics.since", { time: formatClock(bot.started_at) }) : t("metrics.startedRecently")}</small>
            </article>
            <article className="status-metric">
              <span className="panel-kicker">{t("metrics.servers")}</span>
              <strong>{formatNumber(bot?.guild_count ?? 0)}</strong>
              <small>{t("metrics.membersReached", { count: formatNumber(bot?.user_count ?? 0) })}</small>
            </article>
            <article className="status-metric">
              <span className="panel-kicker">{t("metrics.commands")}</span>
              <strong>{formatNumber(bot?.command_count ?? 0)}</strong>
              <small>{t("metrics.cogs", { cogs: formatNumber(cogs.length), issues: issueCount })}</small>
            </article>
          </section>

          {data && !data.online && <div className="status-callout" role="status">
            <Icon name="alert" />
            <p><strong>{t("offline.title")}</strong> {data.reason || t("offline.body")}</p>
          </div>}

          <div className="status-sections">
            {/* Collapsed by default: 24 rows is the longest section on the page. */}
            <details className="status-section">
              <summary className="status-section-summary">
                <span className="status-section-heading">
                  <span className="status-section-icon"><Icon name="grid" /></span>
                  <span>
                    <strong>{t("cogs.title")}</strong>
                    <small>{t("cogs.subtitle")}</small>
                  </span>
                </span>
                <span className="status-section-meta">
                  {(["loaded", "disabled", "maintenance", "failed"] as CogState[]).map((key) => {
                    const count = cogCounts?.[key] ?? 0;
                    if (!count) return null;
                    return <span key={key} className={`status-pill ${COG_TONE[key]}`}>{count} {t(COG_KEYS[key]).toLowerCase()}</span>;
                  })}
                  {!cogs.length && <span className="status-pill wait">{t("cogs.noReading")}</span>}
                </span>
              </summary>
              <div className="status-section-body">
                {cogs.length === 0
                  ? <p className="status-empty">{t("cogs.empty")}</p>
                  : <ul className="status-cog-list">
                    {cogs.map((cog) => (
                      <li className={`status-cog status-cog-${COG_TONE[cog.state]}`} key={cog.name}>
                        <span className="status-cog-name">
                          <strong>{cog.label}</strong>
                          <code>{cog.name}</code>
                        </span>
                        <span className="status-cog-detail">
                          {cog.commands > 0 && <small>{t("cogs.commandCount", { count: formatNumber(cog.commands) })}</small>}
                          {cog.reason && <small className="status-cog-reason">{cog.reason}</small>}
                        </span>
                        <span className={`status-pill ${COG_TONE[cog.state]}`}>{t(COG_KEYS[cog.state])}</span>
                      </li>
                    ))}
                  </ul>}
              </div>
            </details>

            <details className="status-section">
              <summary className="status-section-summary">
                <span className="status-section-heading">
                  <span className="status-section-icon"><Icon name="guild_server" /></span>
                  <span>
                    <strong>{t("shards.title")}</strong>
                    <small>{t("shards.subtitle")}</small>
                  </span>
                </span>
                <span className="status-section-meta">
                  <span className="status-pill wait">{formatNumber(shards.length)} {t(shards.length === 1 ? "shards.one" : "shards.many")}</span>
                  {averageLatency !== null && <span className="status-pill ok">{t("shards.average", { ms: averageLatency })}</span>}
                </span>
              </summary>
              <div className="status-section-body">
                {shards.length === 0
                  ? <p className="status-empty">{t("shards.empty")}</p>
                  : <ul className="status-shard-list">
                    {shards.map((shard) => {
                      // A shard that is connected but has not reported latency yet
                      // is still starting: calling that slow would flag every boot.
                      const starting = shard.connected && Boolean(shard.starting || shard.latency_ms === null);
                      const slow = shard.connected && !starting && (shard.latency_ms ?? 0) > 600;
                      const tone = !shard.connected || starting ? "wait" : slow ? "warn" : "ok";
                      const label = t(starting
                        ? "shards.starting"
                        : shard.ratelimited
                          ? "shards.rateLimited"
                          : !shard.connected
                            ? "shards.awaiting"
                            : slow ? "shards.slow" : "shards.connected");
                      return (
                        <li className={`status-shard status-shard-${tone}`} key={shard.id}>
                          <span className="status-shard-id">{t("shards.id", { id: shard.id })}</span>
                          <span className="status-shard-figures">
                            <span><strong>{shard.latency_ms === null ? "—" : `${shard.latency_ms} ms`}</strong><small>{t("shards.latency")}</small></span>
                            <span><strong>{formatNumber(shard.guilds)}</strong><small>{t("shards.servers")}</small></span>
                            <span><strong>{formatNumber(shard.members)}</strong><small>{t("shards.members")}</small></span>
                          </span>
                          <span className={`status-pill ${shard.ratelimited ? "warn" : tone}`}>{label}</span>
                        </li>
                      );
                    })}
                  </ul>}
              </div>
            </details>

            <details className="status-section">
              <summary className="status-section-summary">
                <span className="status-section-heading">
                  <span className="status-section-icon"><Icon name="guild_overview" /></span>
                  <span>
                    <strong>{t("host.title")}</strong>
                    <small>{t("host.subtitle")}</small>
                  </span>
                </span>
                <span className="status-section-meta">
                  {typeof host?.cpu_percent === "number" && <span className="status-pill wait">CPU {host.cpu_percent}%</span>}
                  {host?.memory && <span className="status-pill wait">RAM {host.memory.percent}%</span>}
                  {bot?.version && <span className="status-pill ok">v{bot.version}</span>}
                </span>
              </summary>
              <div className="status-section-body">
                {!host ? <p className="status-empty">{t("host.empty")}</p> : <>
                  <div className="status-host-grid">
                    <div className="status-host-card">
                      <span className="panel-kicker">{t("host.cpu")}</span>
                      <strong>{typeof host.cpu_percent === "number" ? `${host.cpu_percent}%` : "—"}</strong>
                      <Meter percent={host.cpu_percent ?? 0} tone={(host.cpu_percent ?? 0) > 85 ? "is-partial" : "is-complete"} />
                      <small>
                        {t("host.cores", { count: host.cores ?? "—" })}
                        {host.load ? ` · ${t("host.load", { values: host.load.join(" / ") })}` : ""}
                      </small>
                    </div>
                    <div className="status-host-card">
                      <span className="panel-kicker">{t("host.memory")}</span>
                      <strong>{host.memory ? `${host.memory.used_gb} / ${host.memory.total_gb} GB` : "—"}</strong>
                      <Meter percent={host.memory?.percent ?? 0} tone={(host.memory?.percent ?? 0) > 85 ? "is-partial" : "is-complete"} />
                      <small>{host.memory ? t("host.memoryOf", { percent: host.memory.percent }) : t("host.notReported")}</small>
                    </div>
                    <div className="status-host-card">
                      <span className="panel-kicker">{t("host.disk")}</span>
                      <strong>{host.disk ? `${host.disk.used_gb} / ${host.disk.total_gb} GB` : "—"}</strong>
                      <Meter percent={host.disk?.percent ?? 0} tone={(host.disk?.percent ?? 0) > 85 ? "is-partial" : "is-complete"} />
                      <small>{host.disk ? t("host.diskOf", { percent: host.disk.percent }) : t("host.notReported")}</small>
                    </div>
                    <div className="status-host-card">
                      <span className="panel-kicker">{t("host.process")}</span>
                      <strong>{host.process ? `${host.process.memory_mb} MB` : "—"}</strong>
                      <Meter percent={Math.min(100, ((host.process?.memory_mb ?? 0) / 512) * 100)} tone="is-near" />
                      <small>
                        {host.process
                          ? t("host.processDetail", { threads: host.process.threads, cpu: host.process.cpu_percent, pid: host.pid })
                          : t("host.pid", { pid: host.pid })}
                      </small>
                    </div>
                  </div>
                  <ul className="status-host-facts">
                    <li><span>{t("host.python")}</span><strong>{host.python}</strong></li>
                    <li><span>{t("host.platform")}</span><strong>{host.platform}</strong></li>
                    <li><span>{t("host.voice")}</span><strong>{formatNumber(bot?.voice_clients ?? 0)}</strong></li>
                    <li><span>{t("host.started")}</span><strong>{host.process ? formatClock(host.process.started_at) : "—"}</strong></li>
                  </ul>
                </>}
              </div>
            </details>

            <details className="status-section">
              <summary className="status-section-summary">
                <span className="status-section-heading">
                  <span className="status-section-icon"><Icon name="doc" /></span>
                  <span>
                    <strong>{t("locales.title")}</strong>
                    <small>{t("locales.subtitle")}</small>
                  </span>
                </span>
                <span className="status-section-meta">
                  {locales && <span className="status-pill wait">{t("locales.languages", { count: locales.languages.length })}</span>}
                  {locales && (
                    <span className="status-pill ok">
                      {t("locales.complete", { done: localeComplete, total: locales.bot.length + locales.website.length })}
                    </span>
                  )}
                </span>
              </summary>
              <div className="status-section-body">
                {!locales ? <p className="status-empty">{t("locales.scanning")}</p> : <>
                  <div className="status-locale-grid">
                    <section className="status-locale-block">
                      <header>
                        <span className="panel-kicker">{t("locales.botTitle")}</span>
                        <p>{t("locales.botBody", { count: locales.bot[0]?.catalogues ?? 0 })}</p>
                      </header>
                      <ul className="status-locale-list">
                        {locales.bot.map((row) => <CoverageRow key={row.code} row={row} />)}
                      </ul>
                    </section>
                    <section className="status-locale-block">
                      <header>
                        <span className="panel-kicker">{t("locales.websiteTitle")}</span>
                        <p>{t("locales.websiteBody", { count: locales.website[0]?.pages ?? 0 })}</p>
                      </header>
                      <ul className="status-locale-list">
                        {locales.website.map((row) => <CoverageRow key={row.code} row={row} />)}
                      </ul>
                    </section>
                  </div>
                  <p className="status-locale-foot">
                    {t("locales.foot", { time: formatClock(locales.scanned_at) })}
                  </p>
                </>}
              </div>
            </details>
          </div>

          <p className="status-footnote">
            {t("foot.note")} <a href="/support">{t("foot.support")}</a>.
          </p>
        </>}
    </main>
    <Footer />
  </>;
}
