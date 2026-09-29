import { useEffect, useState, type FormEvent } from "react";
import { getAuth, getPublicOpenings, getPublicStaffApplication, submitStaffApplication } from "../api";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import { navigate } from "../router";
import type { AuthStatus, PublicStaffApplication } from "../types";

export function StaffApplicationPage() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [application, setApplication] = useState<PublicStaffApplication | null>(null);
  const [openings, setOpenings] = useState<PublicStaffApplication[]>([]);
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [sending, setSending] = useState(false);
  const config = useBotConfig();
  const segments = window.location.pathname.split("/").filter(Boolean);
  const guildId = segments[1] || "";
  const applicationId = segments[2] || "";
  const returnPath = window.location.pathname;

  useEffect(() => {
    let active = true;
    setLoading(true); setError("");
    getAuth().then((status) => {
      if (!active) return;
      setAuth(status);
      if (!status.authenticated) return;
      if (applicationId) {
        return getPublicStaffApplication(guildId, applicationId).then((value) => {
          if (active) setApplication(value);
        });
      }
      return getPublicOpenings(guildId).then((result) => {
        if (!active) return;
        setOpenings(result.openings);
      });
    }).catch((reason) => {
      if (active) setError(reason instanceof Error ? reason.message : "The application could not be loaded.");
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [guildId, applicationId]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!application) return;
    const unanswered = application.questions.find((question) => {
      if (!question.required) return false;
      const answer = answers[question.id];
      return Array.isArray(answer) ? answer.length === 0 : !answer?.trim();
    });
    if (unanswered) {
      setError(`Please answer: ${unanswered.prompt}`);
      return;
    }
    setSending(true); setError("");
    submitStaffApplication(guildId, application.id, answers, auth?.csrf_token).then(() => setSubmitted(true)).catch((reason) => setError(reason instanceof Error ? reason.message : "Your application could not be submitted.")).finally(() => setSending(false));
  };

  const loginUrl = `/auth/login?next=${encodeURIComponent(returnPath)}`;
  const serverName = application?.guild_name || "the server";

  return <><PublicHeader page="dashboard" /><main className="application-public-page"><div className="application-public-shell">
    <a className="application-back-link" href="/" onClick={(event) => { event.preventDefault(); navigate("/"); }}>← Back to Niko</a>
    <div className="application-public-brand"><span className="application-public-mark">n</span><span>TEAM APPLICATIONS <small>POWERED BY NIKO</small></span></div>
    <div className="application-public-card">
      {loading ? <div className="application-public-state"><div className="loading-ring" /><p>Checking your sign-in and server access…</p></div>
        : !auth?.authenticated ? <div className="application-public-state"><div className="application-public-symbol"><Icon name="lock" /></div><span className="panel-kicker">A safe, verified application</span><h1>Sign in to continue.</h1><p>Use your Discord account to confirm that you’re a member of this server and eligible for its openings.</p>{auth?.oauth_available ? <a className="button button-primary" href={loginUrl}>Continue with Discord <Icon name="arrow" /></a> : <p className="form-error">Discord sign-in isn’t available right now.</p>}</div>
        : submitted ? <div className="application-public-state"><div className="application-success-mark">✓</div><span className="panel-kicker">Application received</span><h1>Thanks for stepping up.</h1><p>Your answers were sent to {serverName}. You can only apply once to this opening.</p><a className="button button-muted" href={`/apply/${guildId}`}>View other openings <Icon name="arrow" /></a></div>
        : error && !application && openings.length === 0 ? <div className="application-public-state"><div className="application-public-symbol"><Icon name="shield" /></div><span className="panel-kicker">Access check</span><h1>We couldn’t open this application.</h1><p>{error}</p><a className="button button-muted" href="/">Return home</a></div>
        : application?.already_submitted ? <div className="application-public-state"><div className="application-success-mark">✓</div><span className="panel-kicker">Already submitted</span><h1>Your application is on file.</h1><p>You’ve already submitted an application for {application.title}. Reopening it later won’t allow a second submission.</p><a className="button button-muted" href={`/apply/${guildId}`}>View other openings <Icon name="arrow" /></a></div>
        : application ? <>
          <div className="application-public-topline"><span className="application-status open">Accepting applications</span><span className="application-server-tag">{serverName}</span></div>
          <div className="application-public-heading"><span className="panel-kicker">STAFF APPLICATION · {application.role_name || "ROLE OPENING"}</span><h1>{application.title}</h1><p>{application.description || "Complete the questions below to apply for this opening."}</p></div>
          <div className="application-verified"><span className="application-verified-icon"><Icon name="shield" /></span><span><strong>Membership verified</strong><small>Signed in as {auth.user?.global_name || auth.user?.username || "your Discord account"}. Niko checked your server roles.</small></span><a href="/auth/logout">Switch account</a></div>
          <form className="application-public-form" onSubmit={submit}>
            {application.questions.map((question, index) => {
              const type = question.type || "paragraph";
              const value = answers[question.id] ?? (type === "multi_choice" ? [] : "");
              const setValue = (next: string | string[]) => setAnswers((current) => ({ ...current, [question.id]: next }));
              return <fieldset className="form-field application-answer-field" key={question.id}><legend><span className="application-question-count">{String(index + 1).padStart(2, "0")}</span><span className="form-label">{question.prompt}{question.required && <i>Required</i>}</span></legend>
                {type === "short_text" ? <input type="text" required={question.required} maxLength={200} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} placeholder="Your answer" />
                  : type === "single_choice" ? <div className="application-choice-list application-single-choice">{(question.options || []).map((option) => <label className={value === option ? "is-selected" : ""} key={option}><input type="radio" name={question.id} required={question.required && !value} checked={value === option} onChange={() => setValue(option)} /><span>{option}</span></label>)}</div>
                  : type === "multi_choice" ? <div className="application-choice-list application-multi-choice">{(question.options || []).map((option) => <label className={Array.isArray(value) && value.includes(option) ? "is-selected" : ""} key={option}><input type="checkbox" checked={Array.isArray(value) && value.includes(option)} onChange={(event) => setValue(event.target.checked ? [...(Array.isArray(value) ? value : []), option] : (Array.isArray(value) ? value : []).filter((item) => item !== option))} /><span>{option}</span></label>)}</div>
                  : type === "yes_no" ? <div className="application-choice-list application-yes-no">{["yes", "no"].map((option) => <label className={value === option ? "is-selected" : ""} key={option}><input type="radio" name={question.id} required={question.required && !value} checked={value === option} onChange={() => setValue(option)} /><span>{option === "yes" ? "Yes" : "No"}</span></label>)}</div>
                  : type === "date" ? <input type="date" required={question.required} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} />
                  : <><textarea required={question.required} maxLength={4000} rows={4} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} placeholder="Write your answer here…" /><small>{(typeof value === "string" ? value : "").length}/4000 characters</small></>}
              </fieldset>;
            })}
            {error && <div className="notice warning" role="alert">{error}</div>}
            <div className="application-submit-footer"><span>Your submission is private to this server’s application managers.</span><button type="submit" className="button button-primary" disabled={sending}>{sending ? "Sending…" : "Submit application"} <Icon name="arrow" /></button></div>
          </form>
        </>
        : openings.length > 0 ? <div className="application-public-state application-opening-state"><span className="panel-kicker">{serverName} · open roles</span><h1>Choose your opening.</h1><p>Select an eligible team role to start your application.</p><div className="public-opening-list">{openings.map((opening) => <article className="public-opening-card" key={opening.id}><div><span className={`application-status ${opening.already_submitted ? "closed" : opening.eligible ? "open" : "closed"}`}>{opening.already_submitted ? "Already applied" : opening.eligible ? "Eligible" : "Role required"}</span><h2>{opening.title}</h2><p>{opening.description || `Apply for ${opening.role_name || "this role"}.`}</p></div>{opening.eligible && !opening.already_submitted && <a className="button button-primary" href={`/apply/${guildId}/${opening.id}`}>Apply <Icon name="arrow" /></a>}</article>)}</div></div>
        : <div className="application-public-state"><div className="application-public-symbol"><Icon name="users" /></div><span className="panel-kicker">Nothing open just yet</span><h1>No openings available.</h1><p>{error || "This server doesn’t have any open staff applications right now."}</p><a className="button button-muted" href="/">Return home</a></div>}
    </div>
    <footer className="application-public-footer"><span>Identity and server roles verified by Discord.</span>{config?.bot_avatar_url && <img src={config.bot_avatar_url} alt="Niko" />}</footer>
  </div></main></>;
}
