import { useEffect, useState, type FormEvent } from "react";
import { getAuth, getBlacklistAppealStatus, getGuildBlacklistAppealStatus, submitBlacklistAppeal, submitGuildBlacklistAppeal } from "../api";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import type { AuthStatus, BlacklistAppealStatus } from "../types";

export function BlacklistAppealPage() {
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
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Appeal status is temporarily unavailable."))
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [guildId]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!auth?.csrf_token || text.trim().length < 1) return;
    setSending(true); setError("");
    const submitAppeal = guildId
      ? submitGuildBlacklistAppeal(guildId, text.trim(), auth.csrf_token)
      : submitBlacklistAppeal(text.trim(), auth.csrf_token);
    submitAppeal
      .then(() => (guildId ? getGuildBlacklistAppealStatus(guildId) : getBlacklistAppealStatus()).then(setAppeal))
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Your appeal could not be submitted."))
      .finally(() => setSending(false));
  };

  const status = appeal?.status;
  const statusCopy = status === "pending"
    ? ["Appeal under review", "Your appeal has been sent to the Niko owner and Head Admins. You can check back here for the decision."]
    : status === "denied"
      ? ["Appeal denied", "This decision is final. A new appeal cannot be submitted for this blacklist."]
      : status === "approved"
        ? ["Appeal approved", "Your blacklist appeal was approved. The historical record remains on file if the account is blacklisted again."]
        : status === "not_blacklisted"
          ? ["No active blacklist", guildId ? "This server does not currently have an active blacklist to appeal." : "This Discord account does not currently have an active blacklist to appeal."]
          : status === "not_eligible"
            ? ["This guild cannot appeal", "This blacklist is not currently eligible for an appeal."]
            : ["Make your case", "Explain why you believe the blacklist should be reviewed. This request goes directly to Niko staff — no support server join is needed."];

  return <><PublicHeader page="dashboard" /><main className="application-public-page blacklist-appeal-public"><div className="application-public-shell">
    <a className="application-back-link" href={guildId ? `/dashboard/${encodeURIComponent(guildId)}` : "/dashboard"}>← Back to dashboard</a>
    <div className="application-public-brand"><span className="application-public-mark"><Icon name="shield" /></span><span>BLACKLIST APPEALS <small>PRIVATE REVIEW · NIKO STAFF</small></span></div>
    <section className="application-public-card">
      {loading ? <div className="application-public-state"><div className="loading-ring" /><p>Checking your Discord account…</p></div>
        : !auth?.authenticated ? <div className="application-public-state"><div className="application-public-symbol"><Icon name="lock" /></div><span className="panel-kicker">Secure account verification</span><h1>Sign in to appeal.</h1><p>{guildId ? "Sign in with a Discord account that can manage this server to appeal its blacklist." : "Sign in with the Discord account that was blacklisted. Appeals are linked to your verified account."}</p>{auth?.oauth_available ? <a className="button button-primary" href={`/auth/login?next=${encodeURIComponent(`${window.location.pathname}${window.location.search}`)}`}>Continue with Discord <Icon name="arrow" /></a> : <p className="form-error">Discord sign-in isn’t available right now.</p>}</div>
        : <div className="application-public-state blacklist-appeal-state"><div className={`application-public-symbol appeal-status-${status || "eligible"}`}><Icon name={status === "approved" ? "check" : status === "denied" ? "close" : "shield"} /></div><span className="panel-kicker">NIKO TRUST &amp; SAFETY</span><h1>{statusCopy[0]}.</h1><p>{statusCopy[1]}</p>
          {appeal?.reason && <div className="blacklist-appeal-reason"><span className="panel-kicker">Blacklist reason on file</span><p>{appeal.reason}</p></div>}
          {appeal?.appeal_text && <div className="blacklist-appeal-reason"><span className="panel-kicker">Your appeal</span><p>{appeal.appeal_text}</p></div>}
          {appeal?.staff_note && <div className="blacklist-appeal-reason"><span className="panel-kicker">Staff note</span><p>{appeal.staff_note}</p></div>}
          {appeal?.can_appeal && <form className="blacklist-appeal-form" onSubmit={submit}><label className="form-field"><span className="form-label">Your appeal</span><textarea value={text} onChange={(event) => setText(event.target.value)} maxLength={4000} rows={7} placeholder="Share relevant context and why you’re requesting a review…" required /><small>{text.length}/4000 characters</small></label>{error && <div className="notice warning" role="alert">{error}</div>}<div className="application-submit-footer"><span>{guildId ? "Your submission and server ID are visible only to authorized staff." : "Your submission and account ID are visible only to authorized staff."}</span><button className="button button-primary" type="submit" disabled={sending || !text.trim()}>{sending ? "Submitting…" : "Submit appeal"}<Icon name="arrow" /></button></div></form>}
          {error && !appeal && <div className="notice warning" role="alert">{error}</div>}
          <a className="appeal-secondary-link" href={config?.support_server_url || "/support"}>Need another kind of help? Visit support <Icon name="arrow" /></a>
        </div>}
    </section>
    <footer className="application-public-footer">Appeals are reviewed by the bot owner and Head Admins.</footer>
  </div></main></>;
}
