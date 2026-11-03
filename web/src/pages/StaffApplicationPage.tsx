import { useEffect, useState, type FormEvent } from "react";
import { getAuth, getPublicOpenings, getPublicStaffApplication, submitStaffApplication } from "../api";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import { useStrings } from "../i18n";
import { navigate } from "../router";
import type { AuthStatus, PublicStaffApplication } from "../types";

export function StaffApplicationPage() {
  const { t } = useStrings("application");
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
      if (active) setError(reason instanceof Error ? reason.message : t("error.load"));
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [guildId, applicationId, config?.support_server_url, t]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!application) return;
    const unanswered = application.questions.find((question) => {
      if (!question.required) return false;
      const answer = answers[question.id];
      return Array.isArray(answer) ? answer.length === 0 : !answer?.trim();
    });
    if (unanswered) {
      setError(t("error.answer", { prompt: unanswered.prompt }));
      return;
    }
    setSending(true); setError("");
    submitStaffApplication(guildId, application.id, answers, auth?.csrf_token).then(() => setSubmitted(true)).catch((reason) => setError(reason instanceof Error ? reason.message : t("error.submit"))).finally(() => setSending(false));
  };

  const loginUrl = `/auth/login?next=${encodeURIComponent(returnPath)}`;
  const serverName = application?.guild_name || t("serverFallback");

  return <><PublicHeader page="dashboard" /><main className="application-public-page"><div className="application-public-shell">
    <a className="application-back-link" href="/" onClick={(event) => { event.preventDefault(); navigate("/"); }}>{t("back")}</a>
    <div className="application-public-brand"><span className="application-public-mark">n</span><span>{t("brand")} <small>{t("brand.small")}</small></span></div>
    <div className="application-public-card">
      {loading ? <div className="application-public-state"><div className="loading-ring" /><p>{t("loading")}</p></div>
        : !auth?.authenticated ? <div className="application-public-state"><div className="application-public-symbol"><Icon name="lock" /></div><span className="panel-kicker">{t("signin.kicker")}</span><h1>{t("signin.title")}</h1><p>{t("signin.body")}</p>{auth?.oauth_available ? <a className="button button-primary" href={loginUrl}>{t("signin.cta")} <Icon name="arrow" /></a> : <p className="form-error">{t("signin.unavailable")}</p>}</div>
        : submitted ? <div className="application-public-state"><div className="application-success-mark">✓</div><span className="panel-kicker">{t("done.kicker")}</span><h1>{t("done.title")}</h1><p>{t("done.body", { server: serverName })}</p><a className="button button-muted" href={`/apply/${guildId}`}>{t("done.cta")} <Icon name="arrow" /></a></div>
        : error && !application && openings.length === 0 ? <div className="application-public-state"><div className="application-public-symbol"><Icon name="shield" /></div><span className="panel-kicker">{t("fail.kicker")}</span><h1>{t("fail.title")}</h1><p>{error}</p><a className="button button-muted" href="/">{t("fail.cta")}</a></div>
        : application?.already_submitted ? <div className="application-public-state"><div className="application-success-mark">✓</div><span className="panel-kicker">{t("submitted.kicker")}</span><h1>{t("submitted.title")}</h1><p>{t("submitted.body", { title: application.title })}</p><a className="button button-muted" href={`/apply/${guildId}`}>{t("done.cta")} <Icon name="arrow" /></a></div>
        : application ? <>
          <div className="application-public-topline"><span className="application-status open">{t("topline.open")}</span><span className="application-server-tag">{serverName}</span></div>
          <div className="application-public-heading"><span className="panel-kicker">{t("heading.kicker", { role: application.role_name || t("heading.roleFallback") })}</span><h1>{application.title}</h1><p>{application.description || t("heading.body")}</p></div>
          <div className="application-verified"><span className="application-verified-icon"><Icon name="shield" /></span><span><strong>{t("verified.title")}</strong><small>{t("verified.body", { user: auth.user?.global_name || auth.user?.username || t("verified.fallback") })}</small></span><a href="/auth/logout">{t("verified.switch")}</a></div>
          <form className="application-public-form" onSubmit={submit}>
            {application.questions.map((question, index) => {
              const type = question.type || "paragraph";
              const value = answers[question.id] ?? (type === "multi_choice" ? [] : "");
              const setValue = (next: string | string[]) => setAnswers((current) => ({ ...current, [question.id]: next }));
              return <fieldset className="form-field application-answer-field" key={question.id}><legend><span className="application-question-count">{String(index + 1).padStart(2, "0")}</span><span className="form-label">{question.prompt}{question.required && <i>{t("form.required")}</i>}</span></legend>
                {type === "short_text" ? <input type="text" required={question.required} maxLength={200} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} placeholder={t("form.answer")} />
                  : type === "single_choice" ? <div className="application-choice-list application-single-choice">{(question.options || []).map((option) => <label className={value === option ? "is-selected" : ""} key={option}><input type="radio" name={question.id} required={question.required && !value} checked={value === option} onChange={() => setValue(option)} /><span>{option}</span></label>)}</div>
                  : type === "multi_choice" ? <div className="application-choice-list application-multi-choice">{(question.options || []).map((option) => <label className={Array.isArray(value) && value.includes(option) ? "is-selected" : ""} key={option}><input type="checkbox" checked={Array.isArray(value) && value.includes(option)} onChange={(event) => setValue(event.target.checked ? [...(Array.isArray(value) ? value : []), option] : (Array.isArray(value) ? value : []).filter((item) => item !== option))} /><span>{option}</span></label>)}</div>
                  : type === "yes_no" ? <div className="application-choice-list application-yes-no">{["yes", "no"].map((option) => <label className={value === option ? "is-selected" : ""} key={option}><input type="radio" name={question.id} required={question.required && !value} checked={value === option} onChange={() => setValue(option)} /><span>{option === "yes" ? t("form.yes") : t("form.no")}</span></label>)}</div>
                  : type === "date" ? <input type="date" required={question.required} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} />
                  : <><textarea required={question.required} maxLength={4000} rows={4} value={typeof value === "string" ? value : ""} onChange={(event) => setValue(event.target.value)} placeholder={t("form.placeholder")} /><small>{t("form.chars", { count: (typeof value === "string" ? value : "").length })}</small></>}
              </fieldset>;
            })}
            {error && <div className="notice warning" role="alert">{error}</div>}
            <div className="application-submit-footer"><span>{t("form.privacy")}</span><button type="submit" className="button button-primary" disabled={sending}>{t(sending ? "form.sending" : "form.submit")} <Icon name="arrow" /></button></div>
          </form>
        </>
        : openings.length > 0 ? <div className="application-public-state application-opening-state"><span className="panel-kicker">{t("opening.kicker", { server: serverName })}</span><h1>{t("opening.title")}</h1><p>{t("opening.body")}</p><div className="public-opening-list">{openings.map((opening) => <article className="public-opening-card" key={opening.id}><div><span className={`application-status ${opening.already_submitted ? "closed" : opening.eligible ? "open" : "closed"}`}>{t(opening.already_submitted ? "opening.applied" : opening.eligible ? "opening.eligible" : "opening.roleRequired")}</span><h2>{opening.title}</h2><p>{opening.description || t("opening.description", { role: opening.role_name || t("heading.roleFallback") })}</p></div>{opening.eligible && !opening.already_submitted && <a className="button button-primary" href={`/apply/${guildId}/${opening.id}`}>{t("opening.apply")} <Icon name="arrow" /></a>}</article>)}</div></div>
        : <div className="application-public-state"><div className="application-public-symbol"><Icon name="users" /></div><span className="panel-kicker">{t("empty.kicker")}</span><h1>{t("empty.title")}</h1><p>{error || t("empty.body")}</p><a className="button button-muted" href="/">{t("empty.cta")}</a></div>}
    </div>
    <footer className="application-public-footer"><span>{t("footer")}</span>{config?.bot_avatar_url && <img src={config.bot_avatar_url} alt="Niko" />}</footer>
  </div></main></>;
}
