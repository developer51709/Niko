import { useEffect, useMemo, useState } from "react";
import { ApiError, actOnEmailReport, getAuth, getEmailReports, getGuilds, getStaffMe, getStats } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { EmailMessageBody } from "../components/EmailMessageBody";
import { Icon } from "../components/Icon";
import { AuthScreen, DiscordSignIn } from "../components/AuthScreen";
import { dashboardPath, dashboardServersPath, dashboardUserPath, navigate, staffEmailReportsPath } from "../router";
import { notifyError, notifyLoading, notifySuccess } from "../utils/toast";
import type { AuthStatus, BotStats, Guild, StaffEmailMessage, StaffEmailReport } from "../types";

const STATUS_LABELS: Record<string, string> = {
  open: "Needs review",
  replied: "Answered",
  resolved: "Closed",
};

function stamp(epoch?: number | null) {
  if (!epoch) return "—";
  return new Date(epoch * 1000).toLocaleString();
}

function shortWhen(epoch: number) {
  const when = new Date(epoch * 1000);
  if (!Number.isFinite(when.getTime())) return "";
  if (when.toDateString() === new Date().toDateString()) {
    return when.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  return when.toLocaleDateString([], { month: "short", day: "numeric" });
}

function ReportMessage({ message, label }: { message: StaffEmailMessage; label: string }) {
  return <article className="staff-email-turn is-outbound">
    <header>
      <strong>{label} · {message.from_address}</strong>
      <time dateTime={new Date(message.created_at * 1000).toISOString()}>{stamp(message.created_at)}</time>
    </header>
    <p className="staff-email-report-address">To {message.to_address} · “{message.subject || "(no subject)"}”</p>
    <EmailMessageBody message={message} />
  </article>;
}

/**
 * The bot owner's queue for reports filed from the footer of a sent mail.
 *
 * A report is about one message, and the conversation around it is shown only
 * when the reporter chose to share it — that choice is the point of the form, so
 * the queue never widens it. Answering writes back to the address the mail went
 * to, from the address it came from, and the answer is filed in the mailbox.
 */
export function StaffEmailReportsPage() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [accessLoading, setAccessLoading] = useState(true);
  const [staffRole, setStaffRole] = useState<string | null>(null);
  const [stats, setStats] = useState<BotStats | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [reports, setReports] = useState<StaffEmailReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const authStatus = await getAuth();
        if (!active) return;
        setAuth(authStatus);
        if (!authStatus.authenticated) {
          setAccessLoading(false);
          return;
        }
        const staffStatus = await getStaffMe();
        if (!active) return;
        setStaffRole(staffStatus.role);
        setAccessLoading(false);
        if (staffStatus.role !== "owner") return;
        const [botStats, availableGuilds] = await Promise.all([getStats(), getGuilds()]);
        if (!active) return;
        setStats(botStats);
        setGuilds(availableGuilds);
        const loaded = await getEmailReports();
        if (!active) return;
        setReports(loaded.reports);
        setSelectedId(loaded.reports[0]?.report_id || null);
      } catch (reason) {
        if (active) {
          setLoadError(reason instanceof Error ? reason.message : "The report queue could not be loaded.");
          setAccessLoading(false);
        }
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  async function load() {
    setLoading(true);
    try {
      const loaded = await getEmailReports();
      setReports(loaded.reports);
      setLoadError("");
      setSelectedId((current) => current && loaded.reports.some((report) => report.report_id === current)
        ? current
        : loaded.reports[0]?.report_id || null);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 403) {
        setLoadError(reason.message);
      } else {
        notifyError(reason instanceof Error ? reason.message : "The report queue could not be loaded.", "staff-email");
      }
    } finally {
      setLoading(false);
    }
  }

  async function act(action: "reply" | "close") {
    if (!selected || busy) return;
    if (action === "reply" && !reply.trim()) return;
    setBusy(true);
    notifyLoading(action === "reply" ? "Sending the response…" : "Closing the report…", "staff-email");
    try {
      const result = await actOnEmailReport(selected.report_id, {
        action,
        message: action === "reply" ? reply.trim() : undefined,
      }, auth?.csrf_token);
      setReports((current) => current.map((item) => item.report_id === result.report.report_id
        ? { ...item, ...result.report, message: item.message, thread: item.thread }
        : item));
      setReply("");
      notifySuccess(action === "reply" ? `Response sent to ${selected.reporter_address}.` : "Report closed.", "staff-email");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "That report could not be updated.", "staff-email");
    } finally {
      setBusy(false);
    }
  }

  const selected = useMemo(
    () => reports.find((report) => report.report_id === selectedId) || null,
    [reports, selectedId],
  );
  const open = reports.filter((report) => report.status === "open").length;

  if (accessLoading) return <div className="dashboard-state"><div className="loading-ring" /><p>Checking your access…</p></div>;
  if (!auth?.authenticated) {
    return <AuthScreen
      eyebrow="Message reports"
      title={<>Sign in to <em>continue.</em></>}
      description="The report queue opens with the bot owner's Discord account."
      back={{ label: "Return to dashboard", onClick: () => navigate(dashboardPath()) }}
    >
      <DiscordSignIn next={staffEmailReportsPath()} available={auth?.oauth_available} />
    </AuthScreen>;
  }
  if (staffRole !== "owner") {
    return <AuthScreen
      eyebrow="Message reports"
      title={<>Owner <em>only.</em></>}
      description="Reports filed from a staff email are read by the bot owner. Your account does not hold that role."
      back={{ label: "Back to dashboard", onClick: () => navigate(dashboardPath()) }}
    />;
  }
  if (loadError && reports.length === 0) {
    return <AuthScreen
      eyebrow="Message reports"
      title={<>The queue is <em>unavailable.</em></>}
      description={loadError}
      back={{ label: "Back to dashboard", onClick: () => navigate(dashboardPath()) }}
    />;
  }

  const content = <div className="staff-page staff-email-page">
    <header className="staff-heading">
      <div>
        <div className="eyebrow">Mail safety</div>
        <h1>Report queue.</h1>
        <p>Every mail sent from a Niko address carries a link its recipient can complain through. Reports land here with the message they are about, and with the conversation only when the reporter agreed to share it. Your answer goes out as a real email and is filed in the mailbox.</p>
      </div>
      <div className="staff-email-head-side">
        <button type="button" className="button button-muted button-small" onClick={() => navigate("/dashboard/staff/email")}>
          <Icon name="mail" /> Mailbox
        </button>
        <div className="staff-role-card"><span className="staff-role-mark staff-email-mark"><Icon name="alert" /></span><span><small>Awaiting review</small><strong>{open} {open === 1 ? "report" : "reports"}</strong></span></div>
      </div>
    </header>

    {reports.length === 0 ? (loading ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading reports…</p></div> : <section className="staff-guild-empty">
      <span className="staff-email-reader-icon"><Icon name="check" /></span>
      <h2>Nothing reported.</h2>
      <p>When a recipient flags a mail from the footer link, it shows up here with the reason they chose.</p>
      <button type="button" className="button button-muted" onClick={() => navigate("/dashboard/staff/email")}>Open the mailbox</button>
    </section>) : <div className="staff-email-layout">
      <aside className="staff-email-inbox" aria-label="Reports">
        <div className="staff-email-inbox-head">
          <span className="panel-kicker">{reports.length} {reports.length === 1 ? "report" : "reports"}</span>
          <button type="button" className="button button-muted button-small" onClick={() => void load()} disabled={loading}>
            <Icon name="refresh" /> Refresh
          </button>
        </div>
        <div className="staff-email-list">
          {reports.map((report) => <button
            type="button"
            key={report.report_id}
            className={`staff-email-item${selectedId === report.report_id ? " is-open" : ""}${report.status === "open" ? " is-unread" : ""}`}
            onClick={() => { setSelectedId(report.report_id); setReply(""); }}
          >
            <span className="staff-email-item-top">
              <strong>{report.reason_label}</strong>
              <span className="staff-email-item-when">
                <time dateTime={new Date(report.created_at * 1000).toISOString()}>{shortWhen(report.created_at)}</time>
              </span>
            </span>
            <span className="staff-email-item-subject">{report.message?.subject || "(message unavailable)"}</span>
            <span className="staff-email-item-preview">{report.details || `Reported by ${report.reporter_address}`}</span>
            <span className="staff-email-item-address">{STATUS_LABELS[report.status] || report.status}{report.include_thread ? " · full conversation shared" : " · message only"}</span>
          </button>)}
        </div>
      </aside>

      <section className="staff-email-reader" aria-label="Report">
        {selected ? <article className="staff-email-message">
          <div className="staff-email-reader-head">
            <div>
              <span className="panel-kicker">{selected.reason_label} · {STATUS_LABELS[selected.status] || selected.status}</span>
              <h2>{selected.message?.subject || "(message unavailable)"}</h2>
              <p className="staff-email-meta">
                <strong>Reported by {selected.reporter_address}</strong>
                <span>{stamp(selected.created_at)}</span>
              </p>
            </div>
            <button type="button" className="button button-muted button-small" onClick={() => navigate("/dashboard/staff/email")}>
              <Icon name="mail" /> Mailbox
            </button>
          </div>

          <dl className="staff-email-status-facts">
            <div><dt>Reason</dt><dd>{selected.reason_label}</dd></div>
            <div><dt>Shared</dt><dd>{selected.include_thread ? `${selected.thread?.length || 1} messages` : "This message only"}</dd></div>
            <div className="is-wide"><dt>What they wrote</dt><dd>{selected.details || "No note was added."}</dd></div>
          </dl>

          {selected.message
            ? <ReportMessage message={selected.message} label="Reported message" />
            : <p className="staff-email-blank">The reported message is no longer in the mailbox.</p>}

          {selected.include_thread && (selected.thread?.length || 0) > 0 ? <div className="staff-email-thread">
            <p className="staff-email-thread-head"><span>Conversation the reporter shared</span><small>Oldest first</small></p>
            {selected.thread!.map((entry) => <article key={entry.message_id} className={`staff-email-turn is-${entry.direction}`}>
              <header>
                <strong>{entry.direction === "outbound" ? `Niko · ${entry.from_address}` : entry.from_name || entry.from_address}</strong>
                <time dateTime={new Date(entry.created_at * 1000).toISOString()}>{stamp(entry.created_at)}</time>
              </header>
              <EmailMessageBody message={entry} />
            </article>)}
          </div> : null}

          {selected.status === "open" ? <div className="staff-email-report-answer">
            <label className="form-field">
              <span className="form-label">Your response</span>
              <textarea
                value={reply}
                onChange={(event) => setReply(event.target.value)}
                rows={4}
                maxLength={4000}
                placeholder={`Write back to ${selected.reporter_address}…`}
                disabled={busy}
              />
              <small>Sent from {selected.mailbox}@niko.sryze.cc, filed in the mailbox conversation, and recorded on this report.</small>
            </label>
            <div className="staff-panel-footer">
              <span>Nothing is sent until you answer.</span>
              <span className="staff-email-report-actions">
                <button type="button" className="button button-muted button-small" onClick={() => void act("close")} disabled={busy}>Close without reply</button>
                <button type="button" className="button button-primary button-small" onClick={() => void act("reply")} disabled={busy || !reply.trim()}>
                  {busy ? "Working…" : "Send response"}
                </button>
              </span>
            </div>
          </div> : <div className="staff-email-report-note">
            <strong>{selected.status === "replied" ? "Answered" : "Closed"}</strong>
            {selected.responded_at ? <span> · {stamp(selected.responded_at)}</span> : null}
            {selected.response ? <p>{selected.response}</p> : <p>No response was sent.</p>}
          </div>}
        </article> : <div className="staff-email-reader-empty">
          <span className="staff-email-reader-icon"><Icon name="alert" /></span>
          <h2>Pick a report.</h2>
          <p>Reports are on the left, newest first. Opening one shows what was flagged, the reason, and the conversation if the reporter shared it.</p>
        </div>}
      </section>
    </div>}
  </div>;

  return <DashboardShell
    user={auth.user!}
    guilds={guilds}
    selectedGuild={null}
    view="overview"
    section="overview"
    userTab="overview"
    stats={stats}
    staffRole={staffRole}
    onHome={() => navigate(dashboardPath())}
    onServers={() => navigate(dashboardServersPath())}
    onGuildChange={() => undefined}
    onSectionChange={() => undefined}
    onUserTabChange={(tab) => navigate(dashboardUserPath(tab))}
    onRefresh={() => void load()}
    refreshing={loading}
  >{content}</DashboardShell>;
}
