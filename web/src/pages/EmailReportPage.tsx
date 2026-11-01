import { useEffect, useState, type FormEvent } from "react";
import { ApiError, getEmailReport, submitEmailReport } from "../api";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
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
      setLoadError("This link is missing its message id.");
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
          ? "That link does not match a message we sent."
          : reason_ instanceof Error ? reason_.message : "The report form could not be loaded.");
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [token]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!target || sending || !reason) return;
    setSending(true);
    setError("");
    try {
      await submitEmailReport(token, { reason, details: details.trim(), include_thread: includeThread });
      setSent(true);
    } catch (reason_: unknown) {
      setError(reason_ instanceof Error ? reason_.message : "The report could not be filed.");
    } finally {
      setSending(false);
    }
  }

  if (loading) {
    return <><PublicHeader page="email-report" /><main className="application-public-page"><div className="application-public-shell">
      <div className="application-public-card"><div className="application-public-state">
        <div className="loading-ring" /><p>Looking up that message…</p>
      </div></div>
    </div></main></>;
  }

  if (!target) {
    return <><PublicHeader page="email-report" /><main className="application-public-page"><div className="application-public-shell">
      <div className="application-public-brand"><span className="application-public-mark"><Icon name="alert" /></span><span>MESSAGE REPORT <small>PRIVATE · NIKO STAFF</small></span></div>
      <div className="application-public-card"><div className="application-public-state">
        <span className="application-public-symbol"><Icon name="lock" /></span>
        <span className="panel-kicker">Link not recognised</span>
        <h1>We cannot open that report.</h1>
        <p>{loadError || "The link may belong to a message that no longer exists."} If a Niko email worried you, our support page is the way through.</p>
        <a className="button button-muted" href="/support">Contact support</a>
      </div></div>
    </div></main></>;
  }

  if (sent) {
    return <><PublicHeader page="email-report" /><main className="application-public-page"><div className="application-public-shell">
      <div className="application-public-brand"><span className="application-public-mark"><Icon name="alert" /></span><span>MESSAGE REPORT <small>PRIVATE · NIKO STAFF</small></span></div>
      <div className="application-public-card"><div className="application-public-state">
        <span className="application-success-mark"><Icon name="check" /></span>
        <span className="panel-kicker">Report filed</span>
        <h1>Thank you — the Niko team has it.</h1>
        <p>{includeThread
          ? "Your report included the whole conversation. The bot owner reviews it personally."
          : "Your report included only the message you flagged. The bot owner reviews it personally."} If there is anything to say, the reply goes to {target.to_address}.</p>
        <a className="button button-muted" href="/">Back to Niko</a>
      </div></div>
    </div></main></>;
  }

  const shared = target.conversation_count > 1;

  return <><PublicHeader page="email-report" /><main className="application-public-page"><div className="application-public-shell">
    <div className="application-public-brand"><span className="application-public-mark"><Icon name="alert" /></span><span>MESSAGE REPORT <small>PRIVATE · NIKO STAFF</small></span></div>
    <form className="application-public-card" onSubmit={submit}>
      <div className="application-public-topline">
        <span className="application-server-tag">Reporting a message from Niko</span>
        <span className="application-server-tag">{formatSent(target.sent_at)}</span>
      </div>
      <div className="application-public-heading">
        <span className="panel-kicker">What went wrong</span>
        <h1>{target.subject || "(no subject)"}</h1>
        <p>This message was sent to {target.to_address}. Tell us what is wrong with it and the bot owner will review it.</p>
      </div>

      <div className="application-public-form">
        <fieldset className="application-answer-field">
          <legend><span className="form-label">What is wrong with this message? <i>Required</i></span></legend>
          <div className="application-choice-list" role="radiogroup" aria-label="Reason for the report">
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
          <span className="form-label">Anything else we should know? <i>Optional</i></span>
          <textarea
            value={details}
            onChange={(event) => setDetails(event.target.value)}
            maxLength={target.max_details}
            rows={4}
            placeholder="Add anything that would help us understand what happened."
          />
          <small>{details.length}/{target.max_details}</small>
        </label>

        <fieldset className="application-answer-field">
          <legend><span className="form-label">How much should the owner see? <i>Your choice</i></span></legend>
          <p className="form-hint" style={{ margin: "0 0 10px" }}>
            {shared
              ? `This message is part of a conversation with ${target.conversation_count} messages. You can send just the one you flagged, or the whole exchange so nothing is read out of context.`
              : "This message stands on its own, so there is no wider conversation to attach."}
          </p>
          <div className="application-choice-list application-yes-no" role="radiogroup" aria-label="Include the conversation">
            <label className={includeThread ? "" : "is-selected"}>
              <input type="radio" name="scope" checked={!includeThread} onChange={() => setIncludeThread(false)} />
              <span>Just this message</span>
            </label>
            <label className={includeThread ? "is-selected" : ""}>
              <input
                type="radio"
                name="scope"
                checked={includeThread}
                disabled={!shared}
                onChange={() => setIncludeThread(true)}
              />
              <span>Whole conversation{shared ? ` · ${target.conversation_count} messages` : ""}</span>
            </label>
          </div>
        </fieldset>

        {error ? <p className="form-error" role="alert">{error}</p> : null}

        <div className="application-submit-footer">
          <span>The report goes to the bot owner with only what you choose to share. A reply, if there is one, goes to {target.to_address}.</span>
          <button type="submit" className="button button-primary" disabled={sending || !reason}>
            {sending ? "Filing…" : "Send report"}
          </button>
        </div>
      </div>
    </form>
  </div></main></>;
}
