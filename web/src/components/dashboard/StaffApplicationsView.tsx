import { useCallback, useEffect, useState, type FormEvent } from "react";
import { createStaffApplication, getStaffApplications, getStaffSubmissions, setStaffApplicationStatus } from "../../api";
import { Icon } from "../Icon";
import type { GuildResources, StaffApplication, StaffApplicationSubmission } from "../../types";
import { DashHeading } from "./DashboardViews";

type Props = { guildId: string; resources: GuildResources | null; csrfToken?: string };
type QuestionDraft = { id: string; prompt: string; required: boolean };
const newQuestion = (): QuestionDraft => ({ id: crypto.randomUUID(), prompt: "", required: true });

export function StaffApplicationsView({ guildId, resources, csrfToken }: Props) {
  const [applications, setApplications] = useState<StaffApplication[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [roleId, setRoleId] = useState("");
  const [eligibleRoles, setEligibleRoles] = useState<string[]>([]);
  const [questions, setQuestions] = useState<QuestionDraft[]>([newQuestion()]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [selectedSubmissions, setSelectedSubmissions] = useState<string | null>(null);
  const [submissions, setSubmissions] = useState<StaffApplicationSubmission[]>([]);
  const [copiedId, setCopiedId] = useState("");

  const refresh = useCallback(() => getStaffApplications(guildId).then(setApplications), [guildId]);
  useEffect(() => {
    setLoading(true);
    refresh().catch((reason) => setError(reason instanceof Error ? reason.message : "Applications could not be loaded.")).finally(() => setLoading(false));
  }, [refresh]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    setSaving(true); setError(""); setNotice("");
    createStaffApplication(guildId, {
      title, description, role_id: roleId, eligible_role_ids: eligibleRoles,
      questions: questions.map(({ id, prompt, required }) => ({ id, prompt, required })),
    }, csrfToken).then(({ application }) => {
      setApplications((current) => [application, ...current]);
      setTitle(""); setDescription(""); setRoleId(""); setEligibleRoles([]); setQuestions([newQuestion()]);
      setNotice("Application created. Its link is ready to share.");
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Application could not be created.")).finally(() => setSaving(false));
  };

  const toggleStatus = (application: StaffApplication) => {
    const status = application.status === "open" ? "closed" : "open";
    setStaffApplicationStatus(guildId, application.id, status, csrfToken).then(() => {
      setApplications((current) => current.map((item) => item.id === application.id ? { ...item, status } : item));
      setNotice(status === "open" ? "Opening reopened. The same link is active again." : "Opening closed. Its link and responses are preserved.");
      setError("");
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Application status could not be changed."));
  };

  const openSubmissions = (application: StaffApplication) => {
    if (selectedSubmissions === application.id) { setSelectedSubmissions(null); return; }
    setSelectedSubmissions(application.id);
    setSubmissions([]);
    getStaffSubmissions(guildId, application.id).then((result) => setSubmissions(result.submissions)).catch((reason) => setError(reason instanceof Error ? reason.message : "Responses could not be loaded."));
  };

  const copyLink = async (application: StaffApplication) => {
    const link = `${window.location.origin}/apply/${guildId}/${application.id}`;
    try {
      await navigator.clipboard.writeText(link);
      setCopiedId(application.id); window.setTimeout(() => setCopiedId(""), 1800);
    } catch {
      setError("Could not copy the link. Open it in a new tab and copy the address instead.");
    }
  };

  return <>
    <DashHeading eyebrow="People · applications" title="Build your next team." text="Keep separate role openings active at once. Close an opening when hiring pauses, then reopen the same link next time—past responses and one-time submissions stay attached." />
    <div className="applications-intro"><span className="applications-intro-icon"><Icon name="users" /></span><div><span className="panel-kicker">Hiring desk</span><strong>{applications.filter((item) => item.status === "open").length} open · {applications.length} saved openings</strong><p>Each opening has its own stable public link and response archive.</p></div><a href={`/apply/${guildId}`} target="_blank" rel="noreferrer" className="button button-muted button-small">Preview server link <Icon name="arrow" /></a></div>
    {error && <div className="notice warning" role="alert">{error}</div>}
    {notice && <div className="notice applications-success" role="status">{notice}</div>}
    <section className="applications-layout">
      <form className="dash-panel applications-editor" onSubmit={submit}>
        <div className="panel-heading"><div><span className="panel-kicker">New opening</span><h3>Create a role application</h3><p>One saved opening per role and hiring round. Reopen it later to reuse its URL.</p></div><span className="panel-icon"><Icon name="plus" /></span></div>
        <div className="form-grid applications-fields">
          <label className="form-field"><span className="form-label">Opening title</span><input required maxLength={100} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Community moderator" /></label>
          <label className="form-field"><span className="form-label">Discord role</span><select required value={roleId} onChange={(event) => setRoleId(event.target.value)}><option value="">Choose the role you’re hiring for</option>{(resources?.roles || []).map((role) => <option key={role.id} value={role.id}>@{role.name}</option>)}</select></label>
          <label className="form-field application-description"><span className="form-label">About this opening</span><textarea rows={3} maxLength={2000} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Share what the role involves and who you’re looking for." /></label>
          <label className="form-field application-role-gates"><span className="form-label">Eligibility role gates</span><select multiple value={eligibleRoles} onChange={(event) => setEligibleRoles(Array.from(event.target.selectedOptions, (option) => option.value))}>{(resources?.roles || []).map((role) => <option key={role.id} value={role.id}>@{role.name}</option>)}</select><small>Applicants need at least one selected role. Leave empty to allow any server member.</small></label>
        </div>
        <div className="application-question-heading"><div><span className="form-label">Application questions</span><small>Ask up to 12 questions. Required answers must be completed.</small></div><button type="button" className="button button-muted button-small" onClick={() => setQuestions((current) => current.length < 12 ? [...current, newQuestion()] : current)} disabled={questions.length >= 12}>＋ Add question</button></div>
        <div className="application-question-list">{questions.map((question, index) => <div className="application-question" key={question.id}><label className="form-field"><span className="form-label">Question {index + 1}</span><input required maxLength={240} value={question.prompt} onChange={(event) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, prompt: event.target.value } : item))} placeholder="Why would you be a good fit?" /></label><label className="application-required"><input type="checkbox" checked={question.required} onChange={(event) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, required: event.target.checked } : item))} /> Required</label>{questions.length > 1 && <button type="button" className="application-remove-question" onClick={() => setQuestions((current) => current.filter((item) => item.id !== question.id))} aria-label={`Remove question ${index + 1}`}>×</button>}</div>)}</div>
        <div className="setting-footer"><span>Your public application link requires Discord sign-in and server membership.</span><button className="button button-primary" type="submit" disabled={saving || !resources?.roles.length}>{saving ? "Creating…" : "Create opening"}</button></div>
      </form>
      <aside className="applications-aside dash-panel"><span className="panel-kicker">Applicant checks</span><h3>Fair, verified submissions.</h3><p>Niko confirms membership directly with Discord before showing or submitting a form. Selected role gates are checked against the applicant’s current server roles.</p><div className="applications-check"><span>01</span><div><strong>Discord identity</strong><small>One verified account per response</small></div></div><div className="applications-check"><span>02</span><div><strong>Server membership</strong><small>Bot-verified at form load and submit</small></div></div><div className="applications-check"><span>03</span><div><strong>One application per opening</strong><small>Reopening never clears old submissions</small></div></div></aside>
    </section>
    <section className="applications-list-section"><div className="section-heading-row"><div><span className="panel-kicker">Opening library</span><h3>Applications & responses</h3></div><span className="section-count">{applications.length} total</span></div>
      {loading ? <div className="empty-state">Loading saved applications…</div> : applications.length === 0 ? <div className="empty-state">No applications yet. Create your first role opening above.</div> : <div className="applications-list">{applications.map((application) => <article className="application-card dash-panel" key={application.id}>
        <div className="application-card-main"><div className={`application-status ${application.status}`}>{application.status === "open" ? "Open" : "Closed"}</div><h4>{application.title}</h4><p>{application.description || "A role application for this server."}</p><div className="application-meta"><span>{resources?.roles.find((role) => role.id === application.role_id)?.name || `Role ${application.role_id}`}</span><span>{application.submission_count} {application.submission_count === 1 ? "response" : "responses"}</span><span>{application.eligible_role_ids.length ? `${application.eligible_role_ids.length} eligibility role${application.eligible_role_ids.length === 1 ? "" : "s"}` : "Open to all members"}</span></div></div>
        <div className="application-card-actions"><button className="button button-muted button-small" onClick={() => void copyLink(application)}><Icon name="link" /> {copiedId === application.id ? "Copied" : "Copy link"}</button><button className="button button-muted button-small" onClick={() => openSubmissions(application)}><Icon name="book" /> {selectedSubmissions === application.id ? "Hide responses" : "Responses"}</button><button className={`button button-small ${application.status === "open" ? "button-muted" : "button-primary"}`} onClick={() => toggleStatus(application)}>{application.status === "open" ? "Close opening" : "Reopen"}</button></div>
        {selectedSubmissions === application.id && <div className="application-response-list">{submissions.length === 0 ? <div className="empty-state compact">No responses yet, or loading…</div> : submissions.map((submission) => <details className="application-response" key={submission.user_id}><summary><span className="application-response-identity">{submission.avatar_url && <img src={submission.avatar_url} alt="" />}<strong>{submission.display_name}</strong></span><time>{submission.submitted_at ? new Date(`${submission.submitted_at}Z`).toLocaleString() : "Submitted"}</time></summary><div className="application-answers">{submission.answers.map((answer) => <div key={answer.question_id}><strong>{answer.prompt}</strong><p>{answer.answer || "No answer provided."}</p></div>)}</div></details>)}</div>}
      </article>)}</div>}
    </section>
  </>;
}
