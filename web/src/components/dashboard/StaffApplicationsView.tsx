import { useCallback, useEffect, useState, type FormEvent } from "react";
import { createStaffApplication, deleteStaffApplication, getStaffApplications, getStaffSubmissions, reviewStaffSubmission, setStaffApplicationStatus, updateStaffApplication } from "../../api";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { Icon } from "../Icon";
import { DiscordMarkdown } from "../DiscordMarkdown";
import { RoleSelect } from "./RoleSelect";
import { Select, localizeOptions, selectOptions } from "./Select";
import type { StaffApplicationQuestionType, GuildResources, StaffApplication, StaffApplicationSubmission } from "../../types";
import { DashHeading } from "./DashboardViews";
import { useStrings } from "../../i18n";

type Props = { guildId: string; resources: GuildResources | null; csrfToken?: string };
type QuestionDraft = { id: string; prompt: string; required: boolean; type: StaffApplicationQuestionType; options: string[] };
const newQuestion = (): QuestionDraft => ({ id: crypto.randomUUID(), prompt: "", required: true, type: "paragraph", options: ["", ""] });
// Answer types store catalogue keys; the dropdown translates them at render.
const ANSWER_TYPES = selectOptions([["short_text", "applications.typeShort"], ["paragraph", "applications.typeLong"], ["single_choice", "applications.typeOne"], ["multi_choice", "applications.typeMany"], ["yes_no", "applications.typeYesNo"], ["date", "applications.typeDate"]]);

export function StaffApplicationsView({ guildId, resources, csrfToken }: Props) {
  const { t } = useStrings("dashboard");
  const [applications, setApplications] = useState<StaffApplication[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [roleId, setRoleId] = useState("");
  const [eligibleRoles, setEligibleRoles] = useState<string[]>([]);
  const [questions, setQuestions] = useState<QuestionDraft[]>([newQuestion()]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedSubmissions, setSelectedSubmissions] = useState<string | null>(null);
  const [submissions, setSubmissions] = useState<StaffApplicationSubmission[]>([]);
  const [reviewingUserId, setReviewingUserId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState("");

  const refresh = useCallback(() => getStaffApplications(guildId).then(setApplications), [guildId]);
  useEffect(() => {
    setLoading(true);
    refresh().catch((reason) => notifyError(reason instanceof Error ? reason.message : t("applications.loadFailed"), "applications-editor")).finally(() => setLoading(false));
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
    document.querySelector(".applications-editor")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!roleId) { notifyError(t("applications.roleRequired"), "applications-editor"); return; }
    const invalidChoices = questions.some((question) => ["single_choice", "multi_choice"].includes(question.type)
      && (question.options.filter((option) => option.trim()).length < 2 || question.options.some((option) => !option.trim())));
    if (invalidChoices) { notifyError(t("applications.invalidChoices"), "applications-editor"); return; }
    setSaving(true);
    notifyLoading(t("applications.saving"), "applications-editor");
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
      notifySuccess(t(editingId ? "applications.savedEdit" : "applications.savedNew"), "applications-editor");
    }).catch((reason) => notifyError(reason instanceof Error ? reason.message : t("applications.saveFailed"), "applications-editor")).finally(() => setSaving(false));
  };

  const deleteApplication = (application: StaffApplication) => {
    if (!window.confirm(t(application.submission_count === 1 ? "applications.deleteConfirmOne" : "applications.deleteConfirmMany", { title: application.title, count: application.submission_count }))) return;
    notifyLoading(t("applications.deleting"), "applications-editor");
    deleteStaffApplication(guildId, application.id, csrfToken).then(() => {
      setApplications((current) => current.filter((item) => item.id !== application.id));
      if (selectedSubmissions === application.id) setSelectedSubmissions(null);
      notifySuccess(t("applications.deleted"), "applications-editor");
    }).catch((reason) => notifyError(reason instanceof Error ? reason.message : t("applications.deleteFailed"), "applications-editor"));
  };

  const toggleStatus = (application: StaffApplication) => {
    const status = application.status === "open" ? "closed" : "open";
    notifyLoading(t(status === "open" ? "applications.reopening" : "applications.closing"), "applications-editor");
    setStaffApplicationStatus(guildId, application.id, status, csrfToken).then(() => {
      setApplications((current) => current.map((item) => item.id === application.id ? { ...item, status } : item));
      notifySuccess(t(status === "open" ? "applications.reopened" : "applications.closed"), "applications-editor");
    }).catch((reason) => notifyError(reason instanceof Error ? reason.message : t("applications.statusFailed"), "applications-editor"));
  };

  const openSubmissions = (application: StaffApplication) => {
    if (selectedSubmissions === application.id) { setSelectedSubmissions(null); return; }
    setSelectedSubmissions(application.id);
    setSubmissions([]);
    getStaffSubmissions(guildId, application.id).then((result) => setSubmissions(result.submissions)).catch((reason) => notifyError(reason instanceof Error ? reason.message : t("applications.responsesFailed"), "applications-review"));
  };

  const reviewSubmission = (applicationId: string, submission: StaffApplicationSubmission, status: "approved" | "denied") => {
    if (reviewingUserId) return;
    const wasReviewed = submission.review_status !== "pending";
    setReviewingUserId(submission.user_id);
    notifyLoading(t("applications.savingDecision"), "applications-review");
    reviewStaffSubmission(guildId, applicationId, submission.user_id, status, csrfToken).then((result) => {
      setSubmissions((current) => current.map((item) => item.user_id === submission.user_id
        ? { ...item, review_status: result.review_status, reviewed_by: result.reviewed_by, reviewed_at: result.reviewed_at }
        : item));
      notifySuccess(result.unchanged
        ? t("applications.decisionUnchanged")
        : wasReviewed
          ? t("applications.decisionRevised", { status })
          : t("applications.decisionRecorded", { status }), "applications-review");
    }).catch((reason) => notifyError(reason instanceof Error ? reason.message : t("applications.reviewFailed"), "applications-review")).finally(() => setReviewingUserId(null));
  };

  const copyLink = async (application: StaffApplication) => {
    const link = `${window.location.origin}/apply/${guildId}/${application.id}`;
    try {
      await navigator.clipboard.writeText(link);
      setCopiedId(application.id); window.setTimeout(() => setCopiedId(""), 1800);
    } catch {
      notifyError(t("applications.copyFailed"), "applications-editor");
    }
  };

  return <>
    <DashHeading eyebrow={t("applications.eyebrow")} title={t("applications.title")} text={t("applications.text")} />
    <div className="applications-intro"><span className="applications-intro-icon"><Icon name="users" /></span><div><span className="panel-kicker">{t("applications.kicker")}</span><strong>{t("applications.summary", { open: applications.filter((item) => item.status === "open").length, total: applications.length })}</strong><p>{t("applications.introText")}</p></div><a href={`/apply/${guildId}`} target="_blank" rel="noreferrer" className="button button-muted button-small">{t("applications.previewLink")} <Icon name="arrow" /></a></div>
    <section className="applications-layout">
      <form className="dash-panel applications-editor" onSubmit={submit}>
        <div className="panel-heading"><div><span className="panel-kicker">{t(editingId ? "applications.editOpening" : "applications.newOpening")}</span><h3>{t(editingId ? "applications.updateTitle" : "applications.createTitle")}</h3><p>{t(editingId ? "applications.updateDetail" : "applications.createDetail")}</p></div><span className="panel-icon"><Icon name={editingId ? "settings" : "plus"} /></span></div>
        <div className="form-grid applications-fields">
          <label className="form-field"><span className="form-label">{t("applications.openingTitle")}</span><input required maxLength={100} value={title} onChange={(event) => setTitle(event.target.value)} placeholder={t("applications.titlePlaceholder")} /></label>
          <div className="form-field"><span className="form-label">{t("applications.discordRole")}</span><RoleSelect roles={resources?.roles || []} value={roleId} placeholder={t("applications.rolePlaceholder")} ariaLabel={t("applications.discordRole")} onChange={(value) => setRoleId(String(value))} /></div>
          <label className="form-field application-description"><span className="form-label">{t("applications.aboutOpening")}</span><textarea rows={3} maxLength={2000} value={description} onChange={(event) => setDescription(event.target.value)} placeholder={t("applications.descriptionPlaceholder")} />{description.trim() && <DiscordMarkdown text={description} className="role-select-preview" interactiveUsers={false} />}</label>
          <label className="form-field application-role-gates"><span className="form-label">{t("applications.eligibility")}</span><RoleSelect roles={resources?.roles || []} value={eligibleRoles} multiple ariaLabel={t("applications.eligibility")} onChange={(value) => setEligibleRoles(Array.isArray(value) ? value : [])} /><small>{t("applications.eligibilityHint")}</small></label>
        </div>
        <div className="application-question-heading"><div><span className="form-label">{t("applications.questionsLabel")}</span><small>{t("applications.questionsHint")}</small></div><button type="button" className="button button-muted button-small" onClick={() => setQuestions((current) => current.length < 12 ? [...current, newQuestion()] : current)} disabled={questions.length >= 12}>＋ {t("applications.addQuestion")}</button></div>
        <div className="application-question-list">{questions.map((question, index) => <div className="application-question" key={question.id}>
          <label className="form-field"><span className="form-label">{t("applications.questionIndex", { count: index + 1 })}</span><input required maxLength={240} value={question.prompt} onChange={(event) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, prompt: event.target.value } : item))} placeholder={t("applications.questionPlaceholder")} /></label>
          <div className="form-field application-type-field"><span className="form-label">{t("applications.answerType")}</span><Select ariaLabel={t("applications.answerType")} placeholder={null} options={localizeOptions(ANSWER_TYPES, t)} value={question.type} onChange={(value) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, type: value as StaffApplicationQuestionType } : item))} /></div>
          {["single_choice", "multi_choice"].includes(question.type) && <div className="application-options-field"><span className="form-label">{t("applications.optionsLabel")} <small>{t("applications.optionsHint")}</small></span><div className="application-option-list">{question.options.map((option, optionIndex) => <div className="application-option-row" key={`${question.id}-${optionIndex}`}><input required maxLength={100} aria-label={t("applications.optionAria", { question: index + 1, option: optionIndex + 1 })} value={option} onChange={(event) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, options: item.options.map((value, i) => i === optionIndex ? event.target.value : value) } : item))} placeholder={t("applications.optionPlaceholder", { count: optionIndex + 1 })} /><button type="button" className="application-option-remove" onClick={() => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, options: item.options.filter((_, i) => i !== optionIndex) } : item))} disabled={question.options.length <= 2} aria-label={t("applications.removeOptionAria", { count: optionIndex + 1 })}>{t("applications.remove")}</button></div>)}</div><button type="button" className="button button-muted button-small application-option-add" onClick={() => setQuestions((current) => current.map((item) => item.id === question.id && item.options.length < 20 ? { ...item, options: [...item.options, ""] } : item))} disabled={question.options.length >= 20}>＋ {t("applications.addOption")}</button></div>}
          <label className="application-required"><input type="checkbox" checked={question.required} onChange={(event) => setQuestions((current) => current.map((item) => item.id === question.id ? { ...item, required: event.target.checked } : item))} /> {t("applications.required")}</label>{questions.length > 1 && <button type="button" className="application-remove-question" onClick={() => setQuestions((current) => current.filter((item) => item.id !== question.id))} aria-label={t("applications.removeQuestionAria", { count: index + 1 })}>×</button>}
        </div>)}</div>
        <div className="setting-footer"><span>{t(editingId ? "applications.footerKeep" : "applications.footerNew")}</span><div className="application-editor-actions">{editingId && <button className="button button-muted" type="button" onClick={resetEditor} disabled={saving}>{t("applications.cancelEdit")}</button>}<button className="button button-primary" type="submit" disabled={saving || !resources?.roles.length}>{t(saving ? "applications.savingShort" : editingId ? "applications.saveChanges" : "applications.createOpening")}</button></div></div>
      </form>
      <aside className="applications-aside dash-panel"><span className="panel-kicker">{t("applications.asideKicker")}</span><h3>{t("applications.asideTitle")}</h3><p>{t("applications.asideText")}</p><div className="applications-check"><span>01</span><div><strong>{t("applications.check1Title")}</strong><small>{t("applications.check1Hint")}</small></div></div><div className="applications-check"><span>02</span><div><strong>{t("applications.check2Title")}</strong><small>{t("applications.check2Hint")}</small></div></div><div className="applications-check"><span>03</span><div><strong>{t("applications.check3Title")}</strong><small>{t("applications.check3Hint")}</small></div></div></aside>
    </section>
    <section className="applications-list-section"><div className="section-heading-row"><div><span className="panel-kicker">{t("applications.libraryKicker")}</span><h3>{t("applications.libraryTitle")}</h3></div><span className="section-count">{t("applications.totalCount", { count: applications.length })}</span></div>
      {loading ? <div className="empty-state">{t("applications.loading")}</div> : applications.length === 0 ? <div className="empty-state">{t("applications.none")}</div> : <div className="applications-list">{applications.map((application) => <article className="application-card dash-panel" key={application.id}>
        <div className="application-card-main"><div className={`application-status ${application.status}`}>{t(application.status === "open" ? "applications.statusOpen" : "applications.statusClosed")}</div><h4>{application.title}</h4><div className="application-description-preview">{application.description ? <DiscordMarkdown text={application.description} interactiveUsers={false} /> : t("applications.fallbackDescription")}</div><div className="application-meta"><span>{resources?.roles.find((role) => role.id === application.role_id)?.name || t("applications.roleFallback", { id: application.role_id })}</span><span>{t(application.submission_count === 1 ? "applications.responsesOne" : "applications.responsesMany", { count: application.submission_count })}</span><span>{application.eligible_role_ids.length ? t(application.eligible_role_ids.length === 1 ? "applications.eligibilityOne" : "applications.eligibilityMany", { count: application.eligible_role_ids.length }) : t("applications.openToAll")}</span></div></div>
        <div className="application-card-actions"><button className="button button-muted button-small" onClick={() => void copyLink(application)}><Icon name="link" /> {t(copiedId === application.id ? "applications.copied" : "applications.copyLink")}</button><button className="button button-muted button-small" onClick={() => openSubmissions(application)}><Icon name="book" /> {t(selectedSubmissions === application.id ? "applications.hideResponses" : "applications.responses")}</button><button className="button button-muted button-small" onClick={() => editApplication(application)}>{t("applications.edit")}</button><button className={`button button-small ${application.status === "open" ? "button-muted" : "button-primary"}`} onClick={() => toggleStatus(application)}>{t(application.status === "open" ? "applications.closeOpening" : "applications.reopen")}</button><button className="button button-small application-delete-button" onClick={() => deleteApplication(application)}>{t("applications.delete")}</button></div>
        {selectedSubmissions === application.id && <div className="application-response-list">{submissions.length === 0 ? <div className="empty-state compact">{t("applications.noResponses")}</div> : submissions.map((submission) => <details className="application-response" key={submission.user_id}><summary><span className="application-response-identity">{submission.avatar_url && <img src={submission.avatar_url} alt="" />}<strong>{submission.display_name}</strong></span><time>{submission.submitted_at ? new Date(`${submission.submitted_at}Z`).toLocaleString() : t("applications.submitted")}</time></summary><div className="application-answers">{submission.answers.map((answer) => <div key={answer.question_id}><strong>{answer.prompt}</strong><p>{Array.isArray(answer.answer) ? answer.answer.join(", ") || t("applications.noAnswer") : answer.answer || t("applications.noAnswer")}</p></div>)}</div><footer className="application-review-footer"><span className={`application-review-status ${submission.review_status}`} role="status">{t(submission.review_status === "pending" ? "applications.awaiting" : submission.review_status === "approved" ? "applications.approved" : "applications.denied")}</span>{submission.reviewed_at && <small className="application-review-meta">{t("applications.reviewedAt", { date: new Date(`${submission.reviewed_at}Z`).toLocaleString() })}{submission.reviewed_by ? t("applications.staffId", { id: submission.reviewed_by }) : ""}</small>}<div className="application-review-actions"><button type="button" className={`button button-small application-review-approve${submission.review_status === "approved" ? " is-selected" : ""}`} onClick={() => reviewSubmission(application.id, submission, "approved")} disabled={reviewingUserId !== null} aria-pressed={submission.review_status === "approved"}>{t("applications.approve")}</button><button type="button" className={`button button-small application-review-deny${submission.review_status === "denied" ? " is-selected" : ""}`} onClick={() => reviewSubmission(application.id, submission, "denied")} disabled={reviewingUserId !== null} aria-pressed={submission.review_status === "denied"}>{t("applications.deny")}</button></div></footer></details>)}</div>}
      </article>)}</div>}
    </section>
  </>;
}
