import { useEffect, useState, type FormEvent } from "react";
import { getAuth, getBlacklistAppealStatus, getGuildBlacklistAppealStatus, submitBlacklistAppeal, submitGuildBlacklistAppeal } from "../api";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import { useStrings } from "../i18n";
import type { AuthStatus, BlacklistAppealStatus } from "../types";

// Everything the visitor reads is page copy, so each status maps to a catalogue
// prefix rather than to an English sentence pair.
function statusKey(status?: string) {
  if (status === "pending") return "pending";
  if (status === "denied") return "denied";
  if (status === "approved") return "approved";
  if (status === "not_blacklisted") return "notBlacklisted";
  if (status === "not_eligible") return "notEligible";
  return "eligible";
}

export function BlacklistAppealPage() {
  const { t } = useStrings("appeal");
  const guildId = new URLSearchParams(window.location.search).get("guild_id");
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [appeal, setAppeal] = useState<BlacklistAppealStatus | null>(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const config = useBotConfig();

  useEffect(() => {
    let active = true;
    getAuth().then((status) => {
      if (!active) return;
      setAuth(status);
      if (status.authenticated) {
        const getStatus = guildId ? getGuildBlacklistAppealStatus(guildId) : getBlacklistAppealStatus();
        return getStatus.then((result) => { if (active) setAppeal(result); });
      }
    }).catch((reason) => setError(reason instanceof Error ? reason.message : t("error.status")))
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [guildId, t]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!auth?.csrf_token || text.trim().length < 1) return;
    setSending(true); setError("");
    const submitAppeal = guildId
      ? submitGuildBlacklistAppeal(guildId, text.trim(), auth.csrf_token)
      : submitBlacklistAppeal(text.trim(), auth.csrf_token);
    submitAppeal
      .then(() => (guildId ? getGuildBlacklistAppealStatus(guildId) : getBlacklistAppealStatus()).then(setAppeal))
      .catch((reason) => setError(reason instanceof Error ? reason.message : t("error.submit")))
      .finally(() => setSending(false));
  };

  const key = statusKey(appeal?.status);
  const body = key === "notBlacklisted" && guildId
    ? t("status.notBlacklisted.bodyGuild")
    : t(`status.${key}.body`);

  return <><PublicHeader page="dashboard" /><main className="application-public-page blacklist-appeal-public"><div className="application-public-shell">
    <a className="application-back-link" href={guildId ? `/dashboard/${encodeURIComponent(guildId)}` : "/dashboard"}>{t("back")}</a>
    <div className="application-public-brand"><span className="application-public-mark"><Icon name="shield" /></span><span>{t("brand")} <small>{t("brand.small")}</small></span></div>
    <section className="application-public-card">
      {loading ? <div className="application-public-state"><div className="loading-ring" /><p>{t("loading")}</p></div>
        : !auth?.authenticated ? <div className="application-public-state"><div className="application-public-symbol"><Icon name="lock" /></div><span className="panel-kicker">{t("signin.kicker")}</span><h1>{t("signin.title")}</h1><p>{guildId ? t("signin.bodyGuild") : t("signin.bodyUser")}</p>{auth?.oauth_available ? <a className="button button-primary" href={`/auth/login?next=${encodeURIComponent(`${window.location.pathname}${window.location.search}`)}`}>{t("signin.cta")} <Icon name="arrow" /></a> : <p className="form-error">{t("signin.unavailable")}</p>}</div>
        : <div className="application-public-state blacklist-appeal-state"><div className={`application-public-symbol appeal-status-${appeal?.status || "eligible"}`}><Icon name={appeal?.status === "approved" ? "check" : appeal?.status === "denied" ? "close" : "shield"} /></div><span className="panel-kicker">{t("kicker")}</span><h1>{t(`status.${key}.title`)}.</h1><p>{body}</p>
          {appeal?.reason && <div className="blacklist-appeal-reason"><span className="panel-kicker">{t("reason.kicker")}</span><p>{appeal.reason}</p></div>}
          {appeal?.appeal_text && <div className="blacklist-appeal-reason"><span className="panel-kicker">{t("appealText.kicker")}</span><p>{appeal.appeal_text}</p></div>}
          {appeal?.staff_note && <div className="blacklist-appeal-reason"><span className="panel-kicker">{t("staff.kicker")}</span><p>{appeal.staff_note}</p></div>}
          {appeal?.can_appeal && <form className="blacklist-appeal-form" onSubmit={submit}><label className="form-field"><span className="form-label">{t("form.label")}</span><textarea value={text} onChange={(event) => setText(event.target.value)} maxLength={4000} rows={7} placeholder={t("form.placeholder")} required /><small>{t("form.chars", { count: text.length })}</small></label>{error && <div className="notice warning" role="alert">{error}</div>}<div className="application-submit-footer"><span>{guildId ? t("form.privacyGuild") : t("form.privacyUser")}</span><button className="button button-primary" type="submit" disabled={sending || !text.trim()}>{t(sending ? "form.sending" : "form.submit")}<Icon name="arrow" /></button></div></form>}
          {error && !appeal && <div className="notice warning" role="alert">{error}</div>}
          <a className="appeal-secondary-link" href={config?.support_server_url || "/support"}>{t("support")} <Icon name="arrow" /></a>
        </div>}
    </section>
    <footer className="application-public-footer">{t("footer")}</footer>
  </div></main></>;
}
