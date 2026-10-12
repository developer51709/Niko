import { useEffect, useState, type FormEvent } from "react";
import { getAuth, getTeamRecruitmentOpening, getTeamRecruitmentOpenings, submitTeamRecruitmentApplication } from "../api";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import type { AuthStatus, TeamRecruitmentOpening } from "../types";

const TEAM_PATH = "/team/apply";
const ELIGIBILITY_QUESTION_IDS = new Set([
  "eligibility_guidelines",
  "eligibility_confidentiality",
  "niko_age",
  "eligibility_availability",
]);


export function TeamStaffApplicationPage() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [openings, setOpenings] = useState<TeamRecruitmentOpening[]>([]);
  const [opening, setOpening] = useState<TeamRecruitmentOpening | null>(null);
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [eligibilityComplete, setEligibilityComplete] = useState(false);
  const [joined, setJoined] = useState<boolean | null>(null);
  const [error, setError] = useState("");
  const config = useBotConfig();
  const pathParts = window.location.pathname.split("/").filter(Boolean);
  const openingId = pathParts[2] || "";
  const returnTo = window.location.pathname;

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    getAuth().then(async (status) => {
      if (!active) return;
      setAuth(status);
      if (!status.authenticated) return;
      const membership = await fetch("/api/team-recruitment/membership", {
        credentials: "same-origin",
        cache: "no-store",
      });
      const membershipResult = await membership.json();
      if (!membership.ok) throw new Error(membershipResult.error || "Could not verify support-server membership.");
      if (active) setJoined(Boolean(membershipResult.member));
      if (!membershipResult.member) return;
      if (openingId) {
        const value = await getTeamRecruitmentOpening(openingId);
        if (active) {
          setOpening(value);
          setEligibilityComplete(false);
          setAnswers({});
          setSubmitted(false);
        }
      } else {
        const result = await getTeamRecruitmentOpenings();
        if (active) setOpenings(result.openings);
      }
    }).catch((reason) => {
      if (active) setError(reason instanceof Error ? reason.message : "Niko team applications are unavailable.");
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [openingId]);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!opening) return;
    if (!eligibilityComplete) {
      continueToRoleQuestions();
      return;
    }
    const unanswered = opening.questions.find((question) => {
      if (!question.required) return false;
      const answer = answers[question.id];
      return Array.isArray(answer) ? answer.length === 0 : !answer?.trim();
    });
    if (unanswered) {
      setError(`Please answer: ${unanswered.prompt}`);
      return;
    }
    setSending(true);
    setError("");
    submitTeamRecruitmentApplication(opening.id, answers, auth?.csrf_token)
      .then(() => setSubmitted(true))
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Your application could not be submitted."))
      .finally(() => setSending(false));
  };

  const questionControl = (question: TeamRecruitmentOpening["questions"][number], index: number) => {
    const type = question.type || "paragraph";
    const value = answers[question.id] ?? (type === "multi_choice" ? [] : "");
    const setValue = (next: string | string[]) => setAnswers((current) => ({ ...current, [question.id]: next }));
    return <fieldset className="team-apply-field team-apply-answer" key={question.id}>
      <legend><span className="team-apply-question-count">{String(index + 1).padStart(2, "0")}</span><span className="team-apply-label">{question.prompt}{question.required && <i>Required</i>}</span></legend>
      {type === "short_text" ? <input type="text" required={question.required} maxLength={200} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} placeholder="Your answer" />
        : type === "single_choice" ? <div className="team-apply-choice-list">{(question.options || []).map((option) => <label className={value === option ? "is-selected" : ""} key={option}><input type="radio" name={question.id} required={question.required && !value} checked={value === option} onChange={() => setValue(option)} /><span>{option}</span></label>)}</div>
        : type === "multi_choice" ? <div className="team-apply-choice-list">{(question.options || []).map((option) => <label className={Array.isArray(value) && value.includes(option) ? "is-selected" : ""} key={option}><input type="checkbox" checked={Array.isArray(value) && value.includes(option)} onChange={(event) => setValue(event.target.checked ? [...(Array.isArray(value) ? value : []), option] : (Array.isArray(value) ? value : []).filter((item) => item !== option))} /><span>{option}</span></label>)}</div>
        : type === "yes_no" ? <div className="team-apply-choice-list team-apply-yes-no">{["yes", "no"].map((option) => <label className={value === option ? "is-selected" : ""} key={option}><input type="radio" name={question.id} required={question.required && !value} checked={value === option} onChange={() => setValue(option)} /><span>{option === "yes" ? "Yes" : "No"}</span></label>)}</div>
        : type === "date" ? <input type="date" required={question.required} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} />
        : <><textarea required={question.required} maxLength={4000} rows={4} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} placeholder="Write your answer here…" /><small>{(typeof value === "string" ? value : "").length}/4000 characters</small></>}
    </fieldset>;
  };

  const supportUrl = config?.support_server_url || "/discord";
  const loginUrl = `/auth/login?next=${encodeURIComponent(returnTo)}`;
  const eligibilityQuestions = opening?.questions.filter((question) => ELIGIBILITY_QUESTION_IDS.has(question.id)) || [];
  const roleQuestions = opening?.questions.filter((question) => !ELIGIBILITY_QUESTION_IDS.has(question.id)) || [];
  const continueToRoleQuestions = () => {
    const unanswered = eligibilityQuestions.find((question) => {
      const answer = answers[question.id];
      return question.required && (Array.isArray(answer) ? answer.length === 0 : !answer?.trim());
    });
    if (unanswered) {
      setError(`Please answer: ${unanswered.prompt}`);
      return;
    }
    setError("");
    setEligibilityComplete(true);
  };
  const shell = (content: React.ReactNode) => <><PublicHeader page="team" /><main className="team-apply-page"><div className="team-apply-shell">
    <a className="team-apply-back-link" href="/team">← Back to Niko team</a>
    <div className="team-apply-masthead"><span className="team-apply-mark">n</span><span><strong>NIKO · TEAM APPLICATIONS</strong><small>OFFICIAL STAFF APPLICATIONS</small></span><span className="team-apply-secure"><Icon name="shield" /><span>VERIFIED</span></span></div>
    {content}
    <footer className="team-apply-page-footer"><span>Private review · identity verified with Discord</span>{config?.bot_avatar_url && <img src={config.bot_avatar_url} alt="Niko" />}</footer>
  </div></main></>;

  if (loading) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="loading-ring" /><p>Verifying your account and support-server membership…</p></div></section>);
  if (!auth?.authenticated) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-symbol"><Icon name="lock" /></div><span className="panel-kicker">TEAM APPLICATIONS</span><h1>Sign in to begin.</h1><p>Sign in with Discord to verify support-server membership and keep your application tied to your account.</p>{auth?.oauth_available ? <a className="button button-primary" href={loginUrl}>Continue with Discord <Icon name="arrow" /></a> : <p className="form-error">Discord sign-in isn’t available right now.</p>}</div></section>);
  if (joined === false) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-symbol"><Icon name="users" /></div><span className="panel-kicker">BEFORE YOU APPLY</span><h1>Start with support.</h1><p>Join Niko’s official support server first. We verify membership before showing any team openings or application questions.</p><a className="button button-primary" href={supportUrl} target="_blank" rel="noreferrer">Join support server <Icon name="arrow" /></a><button type="button" className="button button-muted" onClick={() => window.location.reload()}>I’ve joined · Verify again</button></div></section>);
  if (error && !opening && openings.length === 0) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-symbol"><Icon name="shield" /></div><span className="panel-kicker">TEAM APPLICATIONS</span><h1>We couldn’t load applications.</h1><p>{error}</p><a className="button button-muted" href={TEAM_PATH}>Try again</a></div></section>);
  if (submitted) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-success">✓</div><span className="panel-kicker">APPLICATION RECEIVED</span><h1>You’re in the review queue.</h1><p>Your Niko staff-team application has been received. The owner will review your answers privately and send your decision by DM.</p><div className="team-apply-notice"><strong>Enable direct messages</strong><br />Make sure DMs are allowed from members of the Niko support server so you can receive your application decision. In Discord, open the server’s <strong>Privacy Settings</strong> and turn on <strong>Direct Messages</strong>.</div><a className="button button-muted" href={TEAM_PATH}>Back to team openings</a></div></section>);
  if (opening?.already_submitted) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-success">✓</div><span className="panel-kicker">ALREADY SUBMITTED</span><h1>Your application is on file.</h1><p>You already applied for {opening.title}. Each Discord account can submit once per opening.</p><a className="button button-muted" href={TEAM_PATH}>View other openings</a></div></section>);

  if (!opening) return shell(<section className="team-apply-layout">
    <header className="team-apply-hero"><span className="panel-kicker">NIKO · TEAM APPLICATIONS</span><h1>Help make Niko <em>better.</em></h1><p>Join a small, thoughtful team helping Discord communities feel safer, warmer, and easier to run.</p><div className="team-apply-proof"><span><Icon name="shield" /> Verified member</span><span><Icon name="users" /> Role-specific</span><span><Icon name="check" /> Eligibility questions</span></div></header>
    <section className="team-apply-card team-apply-openings"><div className="team-apply-section-heading"><div><span className="panel-kicker">OPEN ROLES</span><h2>Choose your role.</h2><p>Every role has a tailored set of questions. You can apply once to each opening.</p></div><span className="team-apply-count">{openings.length.toString().padStart(2, "0")} OPEN</span></div>
      {error && <div className="team-apply-notice" role="alert">{error}</div>}
      {openings.length ? <div className="team-apply-opening-list">{openings.map((item) => <article className="team-apply-opening-card" key={item.id}><div><span className="team-apply-role-status is-open">{item.already_submitted ? "Application received" : "Open role"}</span><h2>{item.title}</h2><p className="team-apply-role">{item.role_name || "Niko team"}</p><p>{item.description || "Help support the Niko community in this role."}</p></div>{item.already_submitted ? <span className="team-apply-complete"><Icon name="check" /> Submitted</span> : item.eligible && <a className="button button-primary" href={`/team/apply/${item.id}`}>View role <Icon name="arrow" /></a>}</article>)}</div> : <div className="team-apply-empty"><span className="team-apply-symbol"><Icon name="users" /></span><h3>No roles are open right now.</h3><p>Check back later — new openings will appear here.</p></div>}
    </section>
  </section>);

  return shell(<section className="team-apply-layout">
    <div className="team-apply-progress"><a className="team-apply-back" href={TEAM_PATH}>← All openings</a><div className="team-apply-stepper"><span className="is-complete"><b>01</b> Membership</span><i /><span className={!eligibilityComplete ? "is-active" : "is-complete"}><b>02</b> Eligibility</span><i /><span className={eligibilityComplete ? "is-active" : ""}><b>03</b> Role questions</span></div></div>
    <article className="team-apply-card team-apply-form-card"><div className="team-apply-role-head"><span className="team-apply-role-icon"><Icon name="users" /></span><div><span className="panel-kicker">TEAM APPLICATION · {opening.role_name || "ROLE"}</span><h1>{opening.title}</h1></div><span className="team-apply-role-status is-open">Open</span></div><p className="team-apply-role-description">{opening.description || "Tell us how you would help this role support the Niko community."}</p>
      <div className="team-apply-verified"><Icon name="shield" /><span><strong>Support-server membership verified</strong><small>Signed in as {auth.user?.global_name || auth.user?.username || "your Discord account"}</small></span></div>
      <form className="team-apply-form" onSubmit={submit}><div className="team-apply-form-intro"><span className="panel-kicker">STEP {eligibilityComplete ? "03" : "02"} OF 03 · {eligibilityComplete ? "ROLE QUESTIONS" : "ELIGIBILITY"}</span><h2>{eligibilityComplete ? "Tell us about your fit for this role." : "A few things to consider first."}</h2><p>{eligibilityComplete ? "Answer the questions for this specific Niko team role." : "Please answer these general questions thoughtfully before continuing."}</p></div>{(eligibilityComplete ? roleQuestions : eligibilityQuestions).map(questionControl)}{error && <div className="team-apply-notice" role="alert">{error}</div>}<div className="team-apply-submit-footer"><span>Private to the Niko owner for application review.</span>{eligibilityComplete ? <button type="submit" className="button button-primary" disabled={sending}>{sending ? "Submitting…" : "Submit application"} <Icon name="arrow" /></button> : <button type="button" className="button button-primary" onClick={continueToRoleQuestions}>Continue <Icon name="arrow" /></button>}</div></form>
    </article>
  </section>);
}
