import { useEffect, useMemo, useState } from "react";
import { ApiError, actOnEmailReport, getAuth, getEmailReports, getGuilds, getStaffMe, getStats } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { EmailMessageBody } from "../components/EmailMessageBody";
import { Icon } from "../components/Icon";
import { AuthScreen, DiscordSignIn } from "../components/AuthScreen";
import { dashboardPath, dashboardServersPath, dashboardUserPath, navigate, staffEmailReportsPath } from "../router";
import { notifyError, notifyLoading, notifySuccess } from "../utils/toast";
import { useStrings } from "../i18n";
import type { AuthStatus, BotStats, Guild, StaffEmailMessage, StaffEmailReport } from "../types";

const STATUS_KEYS: Record<string, string> = {
  open: "status.needsReview",
  replied: "status.answered",
  resolved: "status.closed",
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
  const { t } = useStrings("staff-email-reports");
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
          setLoadError(reason instanceof Error ? reason.message : t("error.loadFailed"));
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
    notifyLoading(action === "reply" ? t("toast.sending") : t("toast.closing"), "staff-email");
    try {
      const result = await actOnEmailReport(selected.report_id, {
        action,
        message: action === "reply" ? reply.trim() : undefined,
      }, auth?.csrf_token);
      setReports((current) => current.map((item) => item.report_id === result.report.report_id
        ? { ...item, ...result.report, message: item.message, thread: item.thread }
        : item));
      setReply("");
      notifySuccess(action === "reply" ? t("toast.sent", { address: selected.reporter_address }) : t("toast.closed"), "staff-email");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("error.updateFailed"), "staff-email");
    } finally {
      setBusy(false);
    }
  }

  const selected = useMemo(
    () => reports.find((report) => report.report_id === selectedId) || null,
    [reports, selectedId],
  );
  const open = reports.filter((report) => report.status === "open").length;

  if (accessLoading) return <div className="dashboard-state"><div className="loading-ring" /><p>{t("auth.checkingAccess")}</p></div>;
  if (!auth?.authenticated) {
    return <AuthScreen
      eyebrow={t("auth.eyebrow")}
      title={<>{t("auth.signInBefore")} <em>{t("auth.signInEmphasis")}</em></>}
      description={t("auth.signedOutText")}
      back={{ label: t("auth.back"), onClick: () => navigate(dashboardPath()) }}
    >
      <DiscordSignIn next={staffEmailReportsPath()} available={auth?.oauth_available} />
    </AuthScreen>;
  }
  if (staffRole !== "owner") {
    return <AuthScreen
      eyebrow={t("auth.eyebrow")}
      title={<>{t("auth.ownerOnlyBefore")} <em>{t("auth.ownerOnlyEmphasis")}</em></>}
      description={t("auth.ownerOnlyText")}
      back={{ label: t("auth.backDashboard"), onClick: () => navigate(dashboardPath()) }}
    />;
  }
  if (loadError && reports.length === 0) {
    return <AuthScreen
      eyebrow={t("auth.eyebrow")}
      title={<>{t("auth.queueUnavailableBefore")} <em>{t("auth.queueUnavailableEmphasis")}</em></>}
      description={loadError}
      back={{ label: t("auth.backDashboard"), onClick: () => navigate(dashboardPath()) }}
    />;
  }

  const content = <div className="staff-page staff-email-page">
    <header className="staff-heading">
      <div>
        <div className="eyebrow">{t("page.eyebrow")}</div>
        <h1>{t("page.title")}</h1>
        <p>{t("page.body")}</p>
      </div>
      <div className="staff-email-head-side">
        <button type="button" className="button button-muted button-small" onClick={() => navigate("/dashboard/staff/email")}>
          <Icon name="mail" /> {t("page.mailbox")}
        </button>
        <div className="staff-role-card"><span className="staff-role-mark staff-email-mark"><Icon name="alert" /></span><span><small>{t("page.awaitingReview")}</small><strong>{t(open === 1 ? "page.reportOne" : "page.reportMany", { count: open })}</strong></span></div>
      </div>
    </header>

    {reports.length === 0 ? (loading ? <div className="staff-guild-empty"><div className="loading-ring" /><p>{t("list.loading")}</p></div> : <section className="staff-guild-empty">
      <span className="staff-email-reader-icon"><Icon name="check" /></span>
      <h2>{t("list.emptyTitle")}</h2>
      <p>{t("list.emptyBody")}</p>
      <button type="button" className="button button-muted" onClick={() => navigate("/dashboard/staff/email")}>{t("list.openMailbox")}</button>
    </section>) : <div className="staff-email-layout">
      <aside className="staff-email-inbox" aria-label={t("list.aria")}>
        <div className="staff-email-inbox-head">
          <span className="panel-kicker">{t(reports.length === 1 ? "page.reportOne" : "page.reportMany", { count: reports.length })}</span>
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
            <span className="staff-email-item-subject">{report.message?.subject || t("item.noSubject")}</span>
            <span className="staff-email-item-preview">{report.details || t("item.reportedBy", { address: report.reporter_address })}</span>
            <span className="staff-email-item-address">{STATUS_KEYS[report.status] ? t(STATUS_KEYS[report.status]) : report.status}{report.include_thread ? t("item.fullShared") : t("item.messageOnly")}</span>
          </button>)}
        </div>
      </aside>

      <section className="staff-email-reader" aria-label={t("reader.aria")}>
        {selected ? <article className="staff-email-message">
          <div className="staff-email-reader-head">
            <div>
              <span className="panel-kicker">{selected.reason_label} · {STATUS_KEYS[selected.status] ? t(STATUS_KEYS[selected.status]) : selected.status}</span>
              <h2>{selected.message?.subject || t("item.noSubject")}</h2>
              <p className="staff-email-meta">
                <strong>{t("detail.reportedBy", { address: selected.reporter_address })}</strong>
                <span>{stamp(selected.created_at)}</span>
              </p>
            </div>
            <button type="button" className="button button-muted button-small" onClick={() => navigate("/dashboard/staff/email")}>
              <Icon name="mail" /> Mailbox
            </button>
          </div>

          <dl className="staff-email-status-facts">
            <div><dt>{t("detail.reason")}</dt><dd>{selected.reason_label}</dd></div>
            <div><dt>{t("detail.shared")}</dt><dd>{selected.include_thread ? t("detail.messages", { count: selected.thread?.length || 1 }) : t("detail.thisMessage")}</dd></div>
            <div className="is-wide"><dt>{t("detail.wrote")}</dt><dd>{selected.details || t("detail.noNote")}</dd></div>
          </dl>

          {selected.message
            ? <ReportMessage message={selected.message} label={t("detail.reportedMessage")} />
            : <p className="staff-email-blank">{t("detail.messageGone")}</p>}

          {selected.include_thread && (selected.thread?.length || 0) > 0 ? <div className="staff-email-thread">
            <p className="staff-email-thread-head"><span>{t("detail.sharedThread")}</span><small>{t("detail.oldestFirst")}</small></p>
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
              <span className="form-label">{t("answer.label")}</span>
              <textarea
                value={reply}
                onChange={(event) => setReply(event.target.value)}
                rows={4}
                maxLength={4000}
                placeholder={t("answer.placeholder", { address: selected.reporter_address })}
                disabled={busy}
              />
              <small>{t("answer.hint", { address: `${selected.mailbox}@niko.sryze.cc` })}</small>
            </label>
            <div className="staff-panel-footer">
              <span>{t("answer.notYet")}</span>
              <span className="staff-email-report-actions">
                <button type="button" className="button button-muted button-small" onClick={() => void act("close")} disabled={busy}>{t("answer.close")}</button>
                <button type="button" className="button button-primary button-small" onClick={() => void act("reply")} disabled={busy || !reply.trim()}>
                  {busy ? t("answer.working") : t("answer.send")}
                </button>
              </span>
            </div>
          </div> : <div className="staff-email-report-note">
            <strong>{t(selected.status === "replied" ? "status.answered" : "status.closed")}</strong>
            {selected.responded_at ? <span> · {stamp(selected.responded_at)}</span> : null}
            {selected.response ? <p>{selected.response}</p> : <p>{t("answer.noneSent")}</p>}
          </div>}
        </article> : <div className="staff-email-reader-empty">
          <span className="staff-email-reader-icon"><Icon name="alert" /></span>
          <h2>{t("reader.pickTitle")}</h2>
          <p>{t("reader.pickBody")}</p>
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
