import { useEffect, useState, type FormEvent } from "react";
import { getAuth, getTeamRecruitmentOpening, getTeamRecruitmentOpenings, submitTeamRecruitmentApplication } from "../api";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { devtools, useDevtoolsFlag } from "../devtools";
import { useBotConfig } from "../hooks/useBotConfig";
import { useStrings } from "../i18n";
import type { AuthStatus, TeamRecruitmentOpening } from "../types";

const TEAM_PATH = "/team/apply";
// A required answer counts as missing when it is empty after trimming, and a
// multiple-choice answer when nothing is ticked.
function isBlankAnswer(answer: string | string[] | undefined) {
  return Array.isArray(answer) ? answer.length === 0 : !(answer ?? "").trim();
}

// Any age past 150 is not treated as a typo to fix politely.
// Catalogue keys, so even the jokes change language with the form.
const AGE_OVER_150_RESPONSES = [
  "age.lies",
  "age.pope",
  "age.museum",
  "age.carbon",
  "age.year",
  "age.immortal",
  "age.lifetime",
  "age.impressive",
];

function pickAgeOver150Response() {
  return AGE_OVER_150_RESPONSES[Math.floor(Math.random() * AGE_OVER_150_RESPONSES.length)];
}

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
  // Set by an attempt to advance or submit, so a blank required answer is only
  // marked once the person has actually tried to continue.
  const [showErrors, setShowErrors] = useState(false);
  // Held in state so the sarcastic reply to an impossible age stays put instead
  // of re-rolling on every keystroke; it is re-picked on each rejected attempt.
  const [ageOver150Response, setAgeOver150Response] = useState(pickAgeOver150Response);
  // Owner devtools switch: renders the application without the membership gate.
  const bypassSupportServer = useDevtoolsFlag(devtools.supportServerBypass);
  const config = useBotConfig();
  const { t } = useStrings("team-application");
  const pathParts = window.location.pathname.split("/").filter(Boolean);
  const openingId = pathParts[2] || "";
  const returnTo = window.location.pathname;

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    // Read once per run: the effect re-runs when the devtools switch changes.
    const bypassMembership = devtools.supportServerBypass();
    getAuth().then(async (status) => {
      if (!active) return;
      setAuth(status);
      if (!status.authenticated) return;
      let member = bypassMembership;
      if (!bypassMembership) {
        const membership = await fetch("/api/team-recruitment/membership", {
          credentials: "same-origin",
          cache: "no-store",
        });
        const membershipResult = await membership.json();
        if (!membership.ok) throw new Error(membershipResult.error || "Could not verify support-server membership.");
        member = Boolean(membershipResult.member);
      }
      // With the bypass on the gate is skipped, so a membership lookup that
      // cannot answer — the bot may not be in the support server at all — never
      // stops the applications from loading.
      if (!active) return;
      setJoined(member);
      if (!member) return;
      if (openingId) {
        const value = await getTeamRecruitmentOpening(openingId, bypassMembership);
        if (active) {
          setOpening(value);
          setEligibilityComplete(false);
          setAnswers({});
          setSubmitted(false);
        }
      } else {
        const result = await getTeamRecruitmentOpenings(bypassMembership);
        if (active) setOpenings(result.openings);
      }
    }).catch((reason) => {
      if (active) setError(reason instanceof Error ? reason.message : t("error.unavailable"));
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [openingId, bypassSupportServer]);

  // The message for one answer, or null when it is acceptable. Blank required
  // answers and the age field are the only things the form can judge itself.
  const answerError = (question: TeamRecruitmentOpening["questions"][number]) => {
    const answer = answers[question.id];
    if (isBlankAnswer(answer)) return question.required ? t("error.answerRequired") : null;
    if (question.id === "niko_age") {
      // Whole numbers only, so text, symbols, decimals, negatives and 0 all fail
      // here rather than in the eligibility check after a round trip.
      const value = (Array.isArray(answer) ? answer[0] ?? "" : answer).trim();
      if (!/^\d+$/.test(value) || Number(value) < 1) return t("error.age");
      if (Number(value) > 150) return t(ageOver150Response);
    }
    return null;
  };

  const invalidQuestions = (questions: TeamRecruitmentOpening["questions"]) =>
    questions.filter((question) => answerError(question) !== null).map((question) => question.id);

  // Bring the first blank required answer into view instead of leaving the
  // person to hunt for the red outline.
  const revealFirstMissing = (missing: string[]) => {
    if (!missing.length) return;
    window.requestAnimationFrame(() => {
      const field = document.querySelector<HTMLElement>(`[data-question="${missing[0]}"]`);
      field?.scrollIntoView({ block: "center", behavior: "smooth" });
      field?.querySelector<HTMLElement>("input, textarea")?.focus({ preventScroll: true });
    });
  };

  // Marks the offending answers and moves the caret to the first one. An
  // impossible age gets a fresh sarcastic line each attempt.
  const rejectAnswers = (missing: string[]) => {
    const age = answers["niko_age"];
    if (missing.includes("niko_age") && Number(Array.isArray(age) ? age[0] : age) > 150) setAgeOver150Response(t(pickAgeOver150Response()));
    setShowErrors(true);
    setError("");
    revealFirstMissing(missing);
  };

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!opening) return;
    if (!eligibilityComplete) {
      continueToRoleQuestions();
      return;
    }
    const missing = invalidQuestions(roleQuestions);
    if (missing.length) {
      rejectAnswers(missing);
      return;
    }
    setSending(true);
    setError("");
    // The bypass also covers submission, so the eligibility and required-answer
    // gates behind the membership check can be reached while testing.
    submitTeamRecruitmentApplication(opening.id, answers, auth?.csrf_token, bypassSupportServer)
      .then(() => setSubmitted(true))
      .catch((reason) => setError(reason instanceof Error ? reason.message : t("error.submit")))
      .finally(() => setSending(false));
  };

  const questionControl = (question: TeamRecruitmentOpening["questions"][number]) => {
    const type = question.type || "paragraph";
    const value = answers[question.id] ?? (type === "multi_choice" ? [] : "");
    const setValue = (next: string | string[]) => setAnswers((current) => ({ ...current, [question.id]: next }));
    const invalidMessage = showErrors ? answerError(question) : null;
    const missing = Boolean(invalidMessage);
    const errorId = `${question.id}-team-apply-error`;
    return <fieldset className={`team-apply-field team-apply-answer${missing ? " is-invalid" : ""}`} key={question.id} data-question={question.id}>
      <legend><span className="team-apply-label">{question.prompt}{question.required && <i>{t("form.required")}</i>}</span></legend>
      {type === "short_text" ? <input type="text" required={question.required} inputMode={question.id === "niko_age" ? "numeric" : undefined} aria-invalid={missing || undefined} aria-describedby={missing ? errorId : undefined} maxLength={200} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} placeholder={t("form.answer")} />
        : type === "single_choice" ? <div className="team-apply-choice-list">{(question.options || []).map((option) => <label className={value === option ? "is-selected" : ""} key={option}><input type="radio" name={question.id} required={question.required && !value} checked={value === option} onChange={() => setValue(option)} /><span>{option}</span></label>)}</div>
        : type === "multi_choice" ? <div className="team-apply-choice-list">{(question.options || []).map((option) => <label className={Array.isArray(value) && value.includes(option) ? "is-selected" : ""} key={option}><input type="checkbox" checked={Array.isArray(value) && value.includes(option)} onChange={(event) => setValue(event.target.checked ? [...(Array.isArray(value) ? value : []), option] : (Array.isArray(value) ? value : []).filter((item) => item !== option))} /><span>{option}</span></label>)}</div>
        : type === "yes_no" ? <div className="team-apply-choice-list team-apply-yes-no">{["yes", "no"].map((option) => <label className={value === option ? "is-selected" : ""} key={option}><input type="radio" name={question.id} required={question.required && !value} checked={value === option} onChange={() => setValue(option)} /><span>{option === "yes" ? t("form.yes") : t("form.no")}</span></label>)}</div>
        : type === "date" ? <input type="date" required={question.required} aria-invalid={missing || undefined} aria-describedby={missing ? errorId : undefined} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} />
        : <><textarea required={question.required} aria-invalid={missing || undefined} aria-describedby={missing ? errorId : undefined} maxLength={4000} rows={4} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} placeholder={t("form.placeholder")} /><small>{t("form.chars", { count: (typeof value === "string" ? value : "").length })}</small></>}
      {missing && <small className="team-apply-field-error" id={errorId}>{invalidMessage}</small>}
    </fieldset>;
  };

  const supportUrl = config?.support_server_url || "/discord";
  const loginUrl = `/auth/login?next=${encodeURIComponent(returnTo)}`;
  const eligibilityQuestions = opening?.questions.filter((question) => ELIGIBILITY_QUESTION_IDS.has(question.id)) || [];
  const roleQuestions = opening?.questions.filter((question) => !ELIGIBILITY_QUESTION_IDS.has(question.id)) || [];
  const activeQuestions = eligibilityComplete ? roleQuestions : eligibilityQuestions;
  const answeredCount = activeQuestions.filter((question) => !isBlankAnswer(answers[question.id])).length;
  const answeredPercent = activeQuestions.length ? Math.round((answeredCount / activeQuestions.length) * 100) : 0;
  const continueToRoleQuestions = () => {
    const missing = invalidQuestions(eligibilityQuestions);
    if (missing.length) {
      rejectAnswers(missing);
      return;
    }
    setError("");
    setShowErrors(false);
    setEligibilityComplete(true);
  };
  // Step 03 used to be a one-way door: the answers stay, so revisiting the
  // eligibility questions is just a step back.
  const backToEligibility = () => {
    setError("");
    setShowErrors(false);
    setEligibilityComplete(false);
  };
  // One back control per screen: the openings list from a role, the team page
  // everywhere else.
  const shell = (content: React.ReactNode, back: { href: string; label: string } = { href: "/team", label: t("back") }) => <><PublicHeader page="team" /><main className="team-apply-page"><div className="team-apply-shell">
    <a className="team-apply-back-link" href={back.href}>← {back.label}</a>
    {content}
    <footer className="team-apply-page-footer"><span>{t("footer")}</span>{config?.bot_avatar_url && <img src={config.bot_avatar_url} alt="Niko" />}</footer>
  </div></main></>;

  if (loading) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="loading-ring" /><p>{t("loading")}</p></div></section>);
  if (!auth?.authenticated) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-symbol"><Icon name="lock" /></div><h1>{t("signin.title")}</h1><p>{t("signin.body")}</p>{auth?.oauth_available ? <a className="button button-primary" href={loginUrl}>{t("signin.cta")} <Icon name="arrow" /></a> : <p className="form-error">{t("signin.unavailable")}</p>}</div></section>);
  if (joined === false && !bypassSupportServer) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-symbol"><Icon name="users" /></div><h1>{t("support.title")}</h1><p>{t("support.body")}</p><div className="team-apply-state-actions"><a className="button button-primary" href={supportUrl} target="_blank" rel="noreferrer">{t("support.join")} <Icon name="arrow" /></a><button type="button" className="button button-muted" onClick={() => window.location.reload()}>{t("support.verify")}</button></div></div></section>);
  if (error && !opening && openings.length === 0) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-symbol"><Icon name="shield" /></div><h1>{t("error.title")}</h1><p>{error}</p><a className="button button-muted" href={TEAM_PATH}>{t("error.retry")}</a></div></section>);
  if (submitted) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-success">✓</div><h1>{t("submitted.title")}</h1><p>{t("submitted.body")}</p><div className="team-apply-notice"><strong>{t("submitted.notice.title")}</strong><br />{t("submitted.notice.before")} <strong>{t("submitted.notice.privacy")}</strong> {t("submitted.notice.and")} <strong>{t("submitted.notice.dms")}</strong>.</div><a className="button button-muted" href={TEAM_PATH}>{t("submitted.back")}</a></div></section>);
  if (opening?.already_submitted) return shell(<section className="team-apply-card"><div className="team-apply-state"><div className="team-apply-success">✓</div><h1>{t("onFile.title")}</h1><p>{t("onFile.body", { title: opening.title })}</p><a className="button button-muted" href={TEAM_PATH}>{t("onFile.back")}</a></div></section>);

  if (!opening) return shell(<section className="team-apply-layout">
    <header className="team-apply-hero"><h1>{t("hero.title")} <em>{t("hero.titleEm")}</em></h1><p>{t("hero.body")}</p></header>
    <section className="team-apply-card team-apply-openings"><div className="team-apply-section-heading"><div><h2>{t("openings.title")}</h2><p>{t("openings.body")}</p></div></div>
      {error && <div className="team-apply-notice" role="alert">{error}</div>}
      {openings.length ? <div className="team-apply-opening-list">{openings.map((item) => {
        const questionCount = item.questions?.length || 0;
        const actionable = !item.already_submitted && item.eligible !== false;
        const content = <>
          <div className="team-apply-opening-main">
            <h2>{item.title}</h2>
            {questionCount ? <p className="team-apply-opening-role">{t(questionCount === 1 ? "opening.questionsOne" : "opening.questionsMany", { count: questionCount })}</p> : null}
            <p>{item.description || t("opening.description")}</p>
          </div>
          <div className="team-apply-opening-action">{item.already_submitted ? <span className="team-apply-complete"><Icon name="check" /> {t("opening.submitted")}</span> : actionable ? <span className="button button-primary">{t("opening.apply")} <Icon name="arrow" /></span> : <span className="team-apply-opening-locked">{t("opening.locked")}</span>}</div>
        </>;
        // The whole card is the link, so the role is not a small target.
        return actionable
          ? <a className="team-apply-opening-card is-actionable" key={item.id} href={`/team/apply/${item.id}`}>{content}</a>
          : <article className="team-apply-opening-card" key={item.id}>{content}</article>;
      })}</div> : <div className="team-apply-empty"><span className="team-apply-symbol"><Icon name="users" /></span><h3>{t("empty.title")}</h3><p>{t("empty.body")}</p></div>}
    </section>
  </section>);

  return shell(<section className="team-apply-layout">
    <article className="team-apply-card team-apply-form-card"><div className="team-apply-role-head"><div><h1>{opening.title}</h1></div></div><p className="team-apply-role-description">{opening.description || t("form.description")}</p>
      <div className="team-apply-verified"><Icon name="shield" /><span><strong>{t(bypassSupportServer ? "form.bypass" : "form.verified")}</strong><small>{bypassSupportServer ? t("form.bypassDetail") : t("form.signedIn", { user: auth.user?.global_name || auth.user?.username || t("form.userFallback") })}</small></span></div>
      {/* `noValidate` hands required-answer reporting to the red-outline state
          below instead of the browser's own bubbles. */}
      <form className="team-apply-form" onSubmit={submit} noValidate>
        <div className="team-apply-form-intro"><h2>{t(eligibilityComplete ? "form.introTitle" : "form.eligibilityTitle")}</h2><p>{t(eligibilityComplete ? "form.introBody" : "form.eligibilityBody")}</p>
          <div className="team-apply-answer-progress">
            <span>{t("form.progress", { done: answeredCount, total: activeQuestions.length })}</span>
            <span className="team-apply-answer-track" role="progressbar" aria-valuenow={answeredCount} aria-valuemin={0} aria-valuemax={activeQuestions.length} aria-label={t("form.progressAria")}><i style={{ width: `${answeredPercent}%` }} /></span>
          </div>
        </div>
        {activeQuestions.map(questionControl)}{error && <div className="team-apply-notice" role="alert">{error}</div>}
        {/* Each button keeps its own key. Without them React reuses one <button>
            node for whichever action is showing and rewrites its `type` while
            the click is still being dispatched, which makes the browser submit
            the form as the click's default action — so stepping forward could
            post a half-finished application. */}
        <div className="team-apply-submit-footer"><div className="team-apply-submit-actions">{eligibilityComplete && <button key="back" type="button" className="button button-muted" onClick={backToEligibility}>{t("form.back")}</button>}{eligibilityComplete ? <button key="submit" type="submit" className="button button-primary" disabled={sending}>{t(sending ? "form.sending" : "form.submit")} <Icon name="arrow" /></button> : <button key="continue" type="button" className="button button-primary" onClick={(event) => { event.preventDefault(); continueToRoleQuestions(); }}>{t("form.continue")} <Icon name="arrow" /></button>}</div></div>
      </form>
    </article>
  </section>, { href: TEAM_PATH, label: t("form.allOpenings") });
}
