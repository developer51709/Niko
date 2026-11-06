import { useEffect, useState } from "react";
import { Icon } from "../Icon";
import { Select } from "../dashboard/Select";
import { Switch } from "../dashboard/Switch";
import type { ErrorReportIncidentEvent, StaffErrorReport, StaffMaintenanceResponse } from "../../types";

const SOURCE_LABELS: Record<string, string> = {
  prefix: "Prefix command",
  slash: "Slash command",
  event: "Gateway event",
  website: "Website",
  api: "API",
  legacy: "Legacy report",
  unknown: "Unknown",
};

function humanise(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatDate(value: string | null | undefined): string {
  if (!value) return "Unknown time";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

const REVIEW_LABELS: Record<string, string> = {
  awaiting_review: "Awaiting review",
  under_review: "Under review",
  fix_needed: "Fix needed",
  investigating_fix: "Investigating fix",
  developing_fix: "Developing fix",
  testing_fix: "Testing fix",
  resolved: "Resolved",
};

const SEVERITY_OPTIONS = [
  { value: "minor", label: "Minor" },
  { value: "major", label: "Major" },
  { value: "critical", label: "Critical" },
];

const TARGET_KIND_OPTIONS = [
  { value: "api", label: "API endpoint" },
  { value: "command", label: "Command" },
];

function eventLabel(event: ErrorReportIncidentEvent): string {
  if (event.type === "created") return "Report created";
  if (event.type === "status") return `Review status: ${REVIEW_LABELS[event.status || ""] || event.status || "updated"}`;
  if (event.type === "public_notice") return event.enabled ? "Published to the status page" : "Removed from the status page";
  if (event.type === "severity") return `Severity set to ${SEVERITY_OPTIONS.find((item) => item.value === event.severity)?.label || event.severity}`;
  if (event.type === "maintenance") {
    const target = [event.kind, event.key].filter(Boolean).join(" ") || "target";
    return event.enabled ? `Maintenance enabled for ${target}` : `Maintenance ended for ${target}`;
  }
  return humanise(event.type || "updated");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isScalar(value: unknown): boolean {
  return value === null || ["string", "number", "boolean"].includes(typeof value);
}

function hasValue(value: unknown): boolean {
  if (value === null || value === undefined || value === "") return false;
  if (Array.isArray(value)) return value.length > 0;
  if (isRecord(value)) return Object.values(value).some(hasValue);
  return true;
}

/** The searchable text of a structured report, without the huge traceback. */
export function reportMatchesSearch(report: StaffErrorReport, query: string): boolean {
  const normalized = query.trim().toLocaleLowerCase();
  if (!normalized) return true;
  const document = report.report;
  const exception = document.exception || { name: "", message: "", type: "" };
  return [
    report.code,
    report.summary,
    report.source,
    document.summary,
    exception.name,
    exception.type,
    exception.message,
    JSON.stringify(document.context || {}),
  ].join(" ").toLocaleLowerCase().includes(normalized);
}

function ValueView({ value }: { value: unknown }) {
  if (!hasValue(value)) return <span className="staff-report-empty">—</span>;
  if (typeof value === "string") {
    return value.includes("\n")
      ? <pre className="staff-report-text">{value}</pre>
      : <span className="staff-report-value">{value}</span>;
  }
  if (isScalar(value)) {
    return <span className="staff-report-value">{String(value)}</span>;
  }
  if (Array.isArray(value) && value.every(isScalar)) {
    return (
      <span className="staff-report-chips">
        {value.map((item, index) => <span key={`${index}-${String(item)}`}>{String(item)}</span>)}
      </span>
    );
  }
  return <pre className="staff-report-json">{JSON.stringify(value, null, 2)}</pre>;
}

function ContextGroup({ name, value }: { name: string; value: unknown }) {
  if (!hasValue(value)) return null;
  const entries = isRecord(value)
    ? Object.entries(value).filter(([, item]) => hasValue(item))
    : [];
  return (
    <section className="staff-report-context-group">
      <h4>{humanise(name)}</h4>
      {isRecord(value) ? (
        <dl className="staff-report-field-list">
          {entries.map(([key, item]) => (
            <div className="staff-report-field" key={key}>
              <dt>{humanise(key)}</dt>
              <dd><ValueView value={item} /></dd>
            </div>
          ))}
        </dl>
      ) : <ValueView value={value} />}
    </section>
  );
}

function suggestedTarget(report: StaffErrorReport): { kind: "api" | "command" | ""; key: string } {
  const context = report.report.context || {};
  const request = isRecord(context.request) ? context.request : {};
  if (report.source === "api" && typeof request.endpoint === "string") {
    return { kind: "api", key: request.endpoint };
  }
  if ((report.source === "prefix" || report.source === "slash" || report.source === "event") && typeof context.command === "string" && context.command !== "(unknown)") {
    return { kind: "command", key: context.command };
  }
  return { kind: "", key: "" };
}

/**
 * Owner controls for turning one report into a public incident.  The target
 * defaults to the failing endpoint or command but stays editable, because the
 * report is evidence, not a guess about what the owner wants to pause.
 */
export function ErrorReportIncidentControls({
  report,
  maintenance,
  busy,
  onSave,
}: {
  report: StaffErrorReport;
  maintenance: StaffMaintenanceResponse | null;
  busy: boolean;
  onSave: (body: {
    public_notice?: boolean;
    severity?: string;
    maintenance?: { enabled: boolean; kind?: "api" | "command"; key?: string };
  }) => void;
}) {
  const suggestion = suggestedTarget(report);
  const [publicNotice, setPublicNotice] = useState(report.public_notice);
  const [severity, setSeverity] = useState(report.severity || "minor");
  const [paused, setPaused] = useState(Boolean(report.maintenance_kind && report.maintenance_key));
  const [kind, setKind] = useState<"api" | "command">(
    (report.maintenance_kind as "api" | "command" | null) || (suggestion.kind || "api"),
  );
  const [key, setKey] = useState(report.maintenance_key || suggestion.key);

  useEffect(() => {
    const next = suggestedTarget(report);
    setPublicNotice(report.public_notice);
    setSeverity(report.severity || "minor");
    setPaused(Boolean(report.maintenance_kind && report.maintenance_key));
    setKind((report.maintenance_kind as "api" | "command" | null) || (next.kind || "api"));
    setKey(report.maintenance_key || next.key);
  }, [report.code, report.public_notice, report.severity, report.maintenance_kind, report.maintenance_key]);

  const userError = report.report.classification === "user_error";
  const targetOptions = kind === "api"
    ? (maintenance?.apis ?? []).map((api) => ({ value: api.endpoint, label: api.label }))
    : (maintenance?.commands ?? []).map((command) => ({ value: command.name, label: command.name }));

  const save = () => {
    const body: Parameters<typeof onSave>[0] = {
      public_notice: paused ? true : publicNotice,
      severity,
    };
    if (paused) {
      if (!key) return;
      body.maintenance = { enabled: true, kind, key };
    } else if (report.maintenance_kind && report.maintenance_key) {
      body.maintenance = { enabled: false };
    }
    onSave(body);
  };

  return (
    <section className="staff-report-incident">
      <div className="staff-report-section-heading">
        <div><span className="panel-kicker">Owner control</span><h3>Public incident</h3></div>
        {report.public_notice && <span className="status-pill warn">On status page</span>}
      </div>
      {userError ? (
        <p className="staff-report-incident-note">
          This is classified as user error, so it stays internal support context. It cannot be published or used to pause an API or command.
        </p>
      ) : (
        <>
          <div className="staff-report-incident-grid">
            <label className="staff-report-incident-toggle">
              <span><strong>Publish to status page</strong><small>Only reports an owner marks severe enough appear publicly.</small></span>
              <Switch checked={publicNotice} onCheckedChange={setPublicNotice} aria-label="Publish this report to the status page" />
            </label>
            <div className="form-field staff-report-incident-severity">
              <span className="form-label">Severity</span>
              <Select ariaLabel="Incident severity" placeholder={null} options={SEVERITY_OPTIONS} value={severity} onChange={setSeverity} />
            </div>
          </div>
          <div className="staff-report-incident-maintenance">
            <label className="staff-report-incident-toggle">
              <span><strong>Pause the affected target</strong><small>Enabling maintenance publishes the notice automatically.</small></span>
              <Switch checked={paused} onCheckedChange={setPaused} aria-label="Put the affected target in maintenance" />
            </label>
            {paused && (
              <div className="staff-report-incident-targets">
                <div className="form-field"><span className="form-label">Target type</span><Select ariaLabel="Maintenance target type" placeholder={null} options={TARGET_KIND_OPTIONS} value={kind} onChange={(value) => { setKind(value as "api" | "command"); setKey(""); }} /></div>
                <div className="form-field"><span className="form-label">{kind === "api" ? "API endpoint" : "Command"}</span><Select ariaLabel="Maintenance target" placeholder={targetOptions.length ? "Choose a target" : "No targets available"} options={targetOptions} value={key} onChange={setKey} /></div>
              </div>
            )}
          </div>
          <div className="staff-report-incident-actions">
            <button type="button" className="button button-primary button-small" disabled={busy || (paused && !key)} onClick={save}>
              {busy ? "Saving…" : "Save incident settings"}
            </button>
          </div>
        </>
      )}
    </section>
  );
}

export function ErrorReportDocument({ report }: { report: StaffErrorReport }) {
  const document = report.report;
  const exception = document.exception || { type: "", name: "Exception", message: "", traceback: "" };
  const contextEntries = Object.entries(document.context || {});
  const environmentEntries = Object.entries(document.environment || {});
  const traceback = exception.traceback || "";
  const frameCount = (traceback.match(/^\s+File "/gm) || []).length;
  const source = SOURCE_LABELS[document.source] || humanise(document.source || "Unknown");
  const schema = document.version ? `JSON v${document.version}` : "Legacy";
  const userError = document.classification === "user_error";

  return (
    <>
      <section className="staff-report-hero">
        <span className="panel-kicker">Exception</span>
        <h4>{exception.name || "Unknown exception"}</h4>
        <p>{exception.message || "No exception message was captured."}</p>
        <code>{exception.type || "unknown type"}</code>
      </section>

      <div className="staff-report-facts">
        <div><span className="panel-kicker">Source</span><strong>{source}</strong></div>
        <div><span className="panel-kicker">Occurred</span><strong>{formatDate(document.created_at || report.created_at)}</strong></div>
        <div><span className="panel-kicker">Schema</span><strong>{schema}</strong></div>
      </div>

      <div className={`staff-report-classification${userError ? " is-user-error" : ""}`}>
        <strong>{userError ? "User error" : "System error"}</strong>
        <span>{userError ? "Internal support context only; it cannot become a public incident." : "Eligible for an owner-published incident and maintenance pause."}</span>
      </div>

      {report.incident_events.length > 0 && (
        <section className="staff-report-section">
          <div className="staff-report-section-heading">
            <div><span className="panel-kicker">Owner record</span><h3>Incident timeline</h3></div>
            <small>{report.incident_events.length} event{report.incident_events.length === 1 ? "" : "s"}</small>
          </div>
          <ol className="staff-report-timeline">
            {report.incident_events.map((event, index) => (
              <li key={`${event.at}-${event.type}-${index}`}>
                <i aria-hidden="true" />
                <div><strong>{eventLabel(event)}</strong><small>{formatDate(event.at)}{event.by_name ? ` · ${event.by_name}` : ""}</small></div>
              </li>
            ))}
          </ol>
        </section>
      )}

      {contextEntries.length > 0 && (
        <section className="staff-report-section">
          <div className="staff-report-section-heading">
            <div><span className="panel-kicker">Captured</span><h3>Invocation context</h3></div>
            <small>{contextEntries.length} group{contextEntries.length === 1 ? "" : "s"}</small>
          </div>
          <div className="staff-report-context">
            {contextEntries.map(([name, value]) => <ContextGroup key={name} name={name} value={value} />)}
          </div>
        </section>
      )}

      {environmentEntries.length > 0 && (
        <section className="staff-report-section">
          <div className="staff-report-section-heading">
            <div><span className="panel-kicker">Runtime</span><h3>Environment</h3></div>
          </div>
          <div className="staff-report-context">
            <ContextGroup name="Runtime" value={document.environment} />
          </div>
        </section>
      )}

      <details className="staff-report-disclosure" open>
        <summary>
          <span>Traceback</span>
          <small>{frameCount ? `${frameCount} frame${frameCount === 1 ? "" : "s"}` : "No frames captured"}</small>
        </summary>
        <pre>{traceback || "No traceback was captured for this report."}</pre>
      </details>

      {document.raw && (
        <details className="staff-report-disclosure">
          <summary><span>Original text report</span><small>Before the JSON format</small></summary>
          <pre>{document.raw}</pre>
        </details>
      )}

      <div className="staff-report-document-actions">
        <button
          type="button"
          className="button button-muted button-small"
          onClick={() => navigator.clipboard?.writeText(JSON.stringify(document, null, 2))}
        >
          <Icon name="copy" />Copy JSON
        </button>
      </div>
    </>
  );
}
