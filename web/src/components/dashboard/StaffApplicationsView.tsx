import { useCallback, useEffect, useState, type FormEvent } from "react";
import { createStaffApplication, deleteStaffApplication, getStaffApplications, getStaffSubmissions, reviewStaffSubmission, setStaffApplicationStatus, updateStaffApplication } from "../../api";
import { Icon } from "../Icon";
import type { ApplicationQuestionType, GuildResources, StaffApplication, StaffApplicationSubmission } from "../../types";
import { DashHeading } from "./DashboardViews";

type Props = { guildId: string; resources: GuildResources | null; csrfToken?: string };
type QuestionDraft = { id: string; prompt: string; required: boolean; type: ApplicationQuestionType; options: string[] };
const newQuestion = (): QuestionDraft => ({ id: crypto.randomUUID(), prompt: "", required: true, type: "paragraph", options: ["", ""] });

export function StaffApplicationsView({ guildId, resources, csrfToken }: Props) {
  const [applications, setApplications] = useState<StaffApplication[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [roleId, setRoleId] = useState("");
  const [eligibleRoles, setEligibleRoles] = useState<string[]>([]);
  const [questions, setQuestions] = useState<QuestionDraft[]>([newQuestion()]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [selectedSubmissions, setSelectedSubmissions] = useState<string | null>(null);
  const [submissions, setSubmissions] = useState<StaffApplicationSubmission[]>([]);
  const [reviewingUserId, setReviewingUserId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState("");

  const refresh = useCallback(() => getStaffApplications(guildId).then(setApplications), [guildId]);
  useEffect(() => {
    setLoading(true);
    refresh().catch((reason) => setError(reason instanceof Error ? reason.message : "Applications could not be loaded.")).finally(() => setLoading(false));
  }, [refresh]);

  const resetEditor = () => {
    setEditingId(null); setTitle(""); setDescription(""); setRoleId("");
    setEligibleRoles([]); setQuestions([newQuestion()]);
  };

  const editApplication = (application: StaffApplication) => {
    setEditingId(application.id); setTitle(application.title); setDescription(application.description || "");
    setRoleId(application.role_id); setEligibleRoles(application.eligible_role_ids || []);
    setQuestions(application.questions.map((question) => ({
      id: question.id, prompt: question.prompt, required: question.required,
      type: question.type || "paragraph", options: question.options?.length ? [...question.options] : ["", ""],
    })));
    setError(""); setNotice("");
    document.querySelector(".applications-editor")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const invalidChoices = questions.some((question) => ["single_choice", "multi_choice"].includes(question.type)
      && (question.options.filter((option) => option.trim()).length < 2 || question.options.some((option) => !option.trim())));
    if (invalidChoices) { setError("Each choice question needs at least two non-empty options."); return; }
    setSaving(true); setError(""); setNotice("");
    const body = {
      title, description, role_id: roleId, eligible_role_ids: eligibleRoles,
      questions: questions.map(({ id, prompt, required, type, options }) => ({ id, prompt, required, type, options: options.map((option) => option.trim()).filter(Boolean) })),
    };
    const save = editingId
      ? updateStaffApplication(guildId, editingId, body, csrfToken)
      : createStaffApplication(guildId, body, csrfToken);
    save.then(({ application }) => {
      setApplications((current) => editingId
        ? current.map((item) => item.id === application.id ? application : item)
        : [application, ...current]);
      resetEditor();
      setNotice(editingId ? "Application updated. Its link and saved responses are unchanged." : "Application created. Its link is ready to share.");
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Application could not be saved.")).finally(() => setSaving(false));
  };

  const deleteApplication = (application: StaffApplication) => {
    if (!window.confirm(`Delete “${application.title}” and permanently remove its ${application.submission_count} response${application.submission_count === 1 ? "" : "s"}? This cannot be undone.`)) return;
    deleteStaffApplication(guildId, application.id, csrfToken).then(() => {
      setApplications((current) => current.filter((item) => item.id !== application.id));
      if (selectedSubmissions === application.id) setSelectedSubmissions(null);
      setNotice("Application and its responses deleted."); setError("");
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Application could not be deleted."));
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

  const reviewSubmission = (applicationId: string, submission: StaffApplicationSubmission, status: "approved" | "denied") => {
    if (reviewingUserId) return;
    setReviewingUserId(submission.user_id); setError(""); setNotice("");
    reviewStaffSubmission(guildId, applicationId, submission.user_id, status, csrfToken).then((result) => {
      setSubmissions((current) => current.map((item) => item.user_id === submission.user_id
        ? { ...item, review_status: result.review_status, reviewed_by: result.reviewed_by, reviewed_at: result.reviewed_at }
        : item));
      setNotice(`Response ${status}.`);
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Response review could not be saved.")).finally(() => setReviewingUserId(null));
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
        <div className="panel-heading"><div><span className="panel-kicker">{editingId ? "Edit opening" : "New opening"}</span><h3>{editingId ? "Update role application" : "Create a role application"}</h3><p>{editingId ? "Changes apply to the existing link. Previously submitted answers remain attached." : "One saved opening per role and hiring round. Reopen it later to reuse its URL."}</p></div><span className="panel-icon"><Icon name={editingId ? "settings" : "plus"} /></span></div>
        <div className="form-grid applications-fields">
          <label className="form-field"><span className="form-label">Opening title</span><input required maxLength={100} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Community moderator" /></label>
          <label className="form-field"><span className="form-label">Discord role</span><select required value={roleId} onChange={(event) => setRoleId(event.target.value)}><option value="">Choose the role you’re hiring for</option>{(resources?.roles || []).map((role) => <option key={role.id} value={role.id}>@{role.name}</option>)}</select></label>
          <label className="form-field application-description"><span className="form-label">About this opening</span><textarea rows={3} maxLength={2000} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Share what the role involves and who you’re looking for." /></label>
          <label className="form-field application-role-gates"><span className="form-label">Eligibility role gates</span><select multiple value={eligibleRoles} onChange={(event) => setEligibleRoles(Array.from(event.target.selectedOptions, (option) => option.value))}>{(resources?.roles || []).map((role) => <option key={role.id} value={role.id}>@{role.name}</option>)}</select><small>Applicants need at least one selected role. Leave empty to allow any server member.</small></label>
        </div>
        <div className="application-question-heading"><div><span className="form-label">Application questions</span><small>Ask up to 12 questions. Required answers must be completed.</small></div><button type="button" className="button button-muted button-small" onClick={() => setQuestions((current) => current.length < 12 ? [...current, newQuestion()] : current)} disabled={questions.length >= 12}>＋ Add question</button></div>
        <div className="application-question-list">{questions.map((question, index) => <div className="application-question" key={question.id}>
          <label className="form-field"><span className="form-label">Question {index + 1}</span><input required maxLength={240} value={question.prompt} onChange={(event) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, prompt: event.target.value } : item))} placeholder="Why would you be a good fit?" /></label>
          <label className="form-field application-type-field"><span className="form-label">Answer type</span><select value={question.type} onChange={(event) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, type: event.target.value as ApplicationQuestionType } : item))}><option value="short_text">Short text</option><option value="paragraph">Long answer</option><option value="single_choice">Choose one</option><option value="multi_choice">Choose many</option><option value="yes_no">Yes / no</option><option value="date">Date</option></select></label>
          {["single_choice", "multi_choice"].includes(question.type) && <div className="application-options-field"><span className="form-label">Options <small>At least two choices</small></span><div className="application-option-list">{question.options.map((option, optionIndex) => <div className="application-option-row" key={`${question.id}-${optionIndex}`}><input required maxLength={100} aria-label={`Question ${index + 1}, option ${optionIndex + 1}`} value={option} onChange={(event) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, options: item.options.map((value, i) => i === optionIndex ? event.target.value : value) } : item))} placeholder={`Option ${optionIndex + 1}`} /><button type="button" className="application-option-remove" onClick={() => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, options: item.options.filter((_, i) => i !== optionIndex) } : item))} disabled={question.options.length <= 2} aria-label={`Remove option ${optionIndex + 1}`}>Remove</button></div>)}</div><button type="button" className="button button-muted button-small application-option-add" onClick={() => setQuestions((current) => current.map((item) => item.id === question.id && item.options.length < 20 ? { ...item, options: [...item.options, ""] } : item))} disabled={question.options.length >= 20}>＋ Add option</button></div>}
          <label className="application-required"><input type="checkbox" checked={question.required} onChange={(event) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, required: event.target.checked } : item))} /> Required</label>{questions.length > 1 && <button type="button" className="application-remove-question" onClick={() => setQuestions((current) => current.filter((item) => item.id !== question.id))} aria-label={`Remove question ${index + 1}`}>×</button>}
        </div>)}</div>
        <div className="setting-footer"><span>{editingId ? "The share link and existing responses are kept." : "Your public application link requires Discord sign-in and server membership."}</span><div className="application-editor-actions">{editingId && <button className="button button-muted" type="button" onClick={resetEditor} disabled={saving}>Cancel edit</button>}<button className="button button-primary" type="submit" disabled={saving || !resources?.roles.length}>{saving ? "Saving…" : editingId ? "Save changes" : "Create opening"}</button></div></div>
      </form>
      <aside className="applications-aside dash-panel"><span className="panel-kicker">Applicant checks</span><h3>Fair, verified submissions.</h3><p>Niko confirms membership directly with Discord before showing or submitting a form. Selected role gates are checked against the applicant’s current server roles.</p><div className="applications-check"><span>01</span><div><strong>Discord identity</strong><small>One verified account per response</small></div></div><div className="applications-check"><span>02</span><div><strong>Server membership</strong><small>Bot-verified at form load and submit</small></div></div><div className="applications-check"><span>03</span><div><strong>One application per opening</strong><small>Reopening never clears old submissions</small></div></div></aside>
    </section>
    <section className="applications-list-section"><div className="section-heading-row"><div><span className="panel-kicker">Opening library</span><h3>Applications & responses</h3></div><span className="section-count">{applications.length} total</span></div>
      {loading ? <div className="empty-state">Loading saved applications…</div> : applications.length === 0 ? <div className="empty-state">No applications yet. Create your first role opening above.</div> : <div className="applications-list">{applications.map((application) => <article className="application-card dash-panel" key={application.id}>
        <div className="application-card-main"><div className={`application-status ${application.status}`}>{application.status === "open" ? "Open" : "Closed"}</div><h4>{application.title}</h4><p>{application.description || "A role application for this server."}</p><div className="application-meta"><span>{resources?.roles.find((role) => role.id === application.role_id)?.name || `Role ${application.role_id}`}</span><span>{application.submission_count} {application.submission_count === 1 ? "response" : "responses"}</span><span>{application.eligible_role_ids.length ? `${application.eligible_role_ids.length} eligibility role${application.eligible_role_ids.length === 1 ? "" : "s"}` : "Open to all members"}</span></div></div>
        <div className="application-card-actions"><button className="button button-muted button-small" onClick={() => void copyLink(application)}><Icon name="link" /> {copiedId === application.id ? "Copied" : "Copy link"}</button><button className="button button-muted button-small" onClick={() => openSubmissions(application)}><Icon name="book" /> {selectedSubmissions === application.id ? "Hide responses" : "Responses"}</button><button className="button button-muted button-small" onClick={() => editApplication(application)}>Edit</button><button className={`button button-small ${application.status === "open" ? "button-muted" : "button-primary"}`} onClick={() => toggleStatus(application)}>{application.status === "open" ? "Close opening" : "Reopen"}</button><button className="button button-small application-delete-button" onClick={() => deleteApplication(application)}>Delete</button></div>
        {selectedSubmissions === application.id && <div className="application-response-list">{submissions.length === 0 ? <div className="empty-state compact">No responses yet, or loading…</div> : submissions.map((submission) => <details className="application-response" key={submission.user_id}><summary><span className="application-response-identity">{submission.avatar_url && <img src={submission.avatar_url} alt="" />}<strong>{submission.display_name}</strong></span><time>{submission.submitted_at ? new Date(`${submission.submitted_at}Z`).toLocaleString() : "Submitted"}</time></summary><div className="application-answers">{submission.answers.map((answer) => <div key={answer.question_id}><strong>{answer.prompt}</strong><p>{Array.isArray(answer.answer) ? answer.answer.join(", ") || "No answer provided." : answer.answer || "No answer provided."}</p></div>)}</div><footer className="application-review-footer"><span className={`application-review-status ${submission.review_status}`} role="status">{submission.review_status === "pending" ? "Awaiting review" : submission.review_status === "approved" ? "Approved" : "Denied"}</span><div className="application-review-actions"><button type="button" className={`button button-small application-review-approve${submission.review_status === "approved" ? " is-selected" : ""}`} onClick={() => reviewSubmission(application.id, submission, "approved")} disabled={reviewingUserId !== null} aria-pressed={submission.review_status === "approved"}>Approve</button><button type="button" className={`button button-small application-review-deny${submission.review_status === "denied" ? " is-selected" : ""}`} onClick={() => reviewSubmission(application.id, submission, "denied")} disabled={reviewingUserId !== null} aria-pressed={submission.review_status === "denied"}>Deny</button></div></footer></details>)}</div>}
      </article>)}</div>}
    </section>
  </>;
}
