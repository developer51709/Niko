import { useEffect, useState, type FormEvent } from "react";
import { ApiError, getEmailReport, submitEmailReport } from "../api";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useStrings } from "../i18n";
import type { StaffEmailReportTarget } from "../types";

/** The token is the last segment of the link the email carried. */
function reportToken() {
  return window.location.pathname.split("/").filter(Boolean).pop() || "";
}

function formatSent(epoch: number) {
  const when = new Date(epoch * 1000);
  if (!Number.isFinite(when.getTime())) return "";
  return when.toLocaleString([], { dateStyle: "long", timeStyle: "short" });
}

/**
 * The form behind the "report this message" footer link. It is public by
 * necessity — the person reporting a mail is not signed in here — and the token
 * in the URL is the whole credential: it names one message and nothing else.
 * Two things are asked: why, and how much of the conversation they will share.
 */
export function EmailReportPage() {
  const { t } = useStrings("email-report");
  const token = reportToken();
  const [target, setTarget] = useState<StaffEmailReportTarget | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [reason, setReason] = useState("");
  const [details, setDetails] = useState("");
  const [includeThread, setIncludeThread] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);

  useEffect(() => {
    let active = true;
    if (!token) {
      setLoadError(t("error.tokenMissing"));
      setLoading(false);
      return;
    }
    getEmailReport(token)
      .then(({ target: found }) => {
        if (!active) return;
        setTarget(found);
        setReason(found.reasons[0]?.value || "");
      })
      .catch((reason_: unknown) => {
        if (!active) return;
        setLoadError(reason_ instanceof ApiError && reason_.status === 404
          ? t("error.unknownLink")
          : reason_ instanceof Error ? reason_.message : t("error.loadFailed"));
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [t, token]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!target || sending || !reason) return;
    setSending(true);
    setError("");
    try {
      await submitEmailReport(token, { reason, details: details.trim(), include_thread: includeThread });
      setSent(true);
    } catch (reason_: unknown) {
      setError(reason_ instanceof Error ? reason_.message : t("error.submit"));
    } finally {
      setSending(false);
    }
  }

  if (loading) {
    return <><PublicHeader page="email-report" /><main className="application-public-page"><div className="application-public-shell">
      <div className="application-public-card"><div className="application-public-state">
        <div className="loading-ring" /><p>{t("loading")}</p>
      </div></div>
    </div></main></>;
  }

  if (!target) {
    return <><PublicHeader page="email-report" /><main className="application-public-page"><div className="application-public-shell">
      <div className="application-public-brand"><span className="application-public-mark"><Icon name="alert" /></span><span>{t("brand.report")} <small>{t("brand.private")}</small></span></div>
      <div className="application-public-card"><div className="application-public-state">
        <span className="application-public-symbol"><Icon name="lock" /></span>
        <span className="panel-kicker">{t("missing.kicker")}</span>
        <h1>{t("missing.title")}</h1>
        <p>{loadError || t("missing.body")} {t("missing.hint")}</p>
        <a className="button button-muted" href="/support">{t("missing.support")}</a>
      </div></div>
    </div></main></>;
  }

  if (sent) {
    return <><PublicHeader page="email-report" /><main className="application-public-page"><div className="application-public-shell">
      <div className="application-public-brand"><span className="application-public-mark"><Icon name="alert" /></span><span>{t("brand.report")} <small>{t("brand.private")}</small></span></div>
      <div className="application-public-card"><div className="application-public-state">
        <span className="application-success-mark"><Icon name="check" /></span>
        <span className="panel-kicker">{t("sent.kicker")}</span>
        <h1>{t("sent.title")}</h1>
        <p>{includeThread ? t("sent.threadBody") : t("sent.singleBody")} {t("sent.replyTo", { address: target.to_address })}</p>
        <a className="button button-muted" href="/">{t("sent.back")}</a>
      </div></div>
    </div></main></>;
  }

  const shared = target.conversation_count > 1;

  return <><PublicHeader page="email-report" /><main className="application-public-page"><div className="application-public-shell">
    <div className="application-public-brand"><span className="application-public-mark"><Icon name="alert" /></span><span>{t("brand.report")} <small>{t("brand.private")}</small></span></div>
    <form className="application-public-card" onSubmit={submit}>
      <div className="application-public-topline">
        <span className="application-server-tag">{t("form.topline")}</span>
        <span className="application-server-tag">{formatSent(target.sent_at)}</span>
      </div>
      <div className="application-public-heading">
        <span className="panel-kicker">{t("form.kicker")}</span>
        <h1>{target.subject || t("form.noSubject")}</h1>
        <p>{t("form.sentTo", { address: target.to_address })}</p>
      </div>

      <div className="application-public-form">
        <fieldset className="application-answer-field">
          <legend><span className="form-label">{t("form.reasonLabel")} <i>{t("form.required")}</i></span></legend>
          <div className="application-choice-list" role="radiogroup" aria-label={t("form.reasonAria")}>
            {target.reasons.map((option) => <label key={option.value} className={reason === option.value ? "is-selected" : ""}>
              <input
                type="radio"
                name="reason"
                value={option.value}
                checked={reason === option.value}
                onChange={() => setReason(option.value)}
              />
              <span>{option.label}</span>
            </label>)}
          </div>
        </fieldset>

        <label className="application-answer-field form-field">
          <span className="form-label">{t("form.detailsLabel")} <i>{t("form.optional")}</i></span>
          <textarea
            value={details}
            onChange={(event) => setDetails(event.target.value)}
            maxLength={target.max_details}
            rows={4}
            placeholder={t("form.detailsPlaceholder")}
          />
          <small>{details.length}/{target.max_details}</small>
        </label>

        <fieldset className="application-answer-field">
          <legend><span className="form-label">{t("form.scopeLabel")} <i>{t("form.scopeChoice")}</i></span></legend>
          <p className="form-hint" style={{ margin: "0 0 10px" }}>
            {shared ? t("form.threadHint", { count: target.conversation_count }) : t("form.singleHint")}
          </p>
          <div className="application-choice-list application-yes-no" role="radiogroup" aria-label={t("form.scopeAria")}>
            <label className={includeThread ? "" : "is-selected"}>
              <input type="radio" name="scope" checked={!includeThread} onChange={() => setIncludeThread(false)} />
              <span>{t("form.justThis")}</span>
            </label>
            <label className={includeThread ? "is-selected" : ""}>
              <input
                type="radio"
                name="scope"
                checked={includeThread}
                disabled={!shared}
                onChange={() => setIncludeThread(true)}
              />
              <span>{shared ? t("form.wholeCount", { count: target.conversation_count }) : t("form.whole")}</span>
            </label>
          </div>
        </fieldset>

        {error ? <p className="form-error" role="alert">{error}</p> : null}

        <div className="application-submit-footer">
          <span>{t("form.footer", { address: target.to_address })}</span>
          <button type="submit" className="button button-primary" disabled={sending || !reason}>
            {sending ? t("form.sending") : t("form.send")}
          </button>
        </div>
      </div>
    </form>
  </div></main></>;
}
