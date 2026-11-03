import { useCallback, useEffect, useState } from "react";
import { api, ApiError, getAuth } from "../api";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { SupportLink } from "../components/SupportLink";
import { useStrings } from "../i18n";
import { navigate } from "../router";
import type { DataRemovalOverview, DataRemovalRequest } from "../types";

/** The owner's own-domain mailbox, which is where legal requests are read. */
const OWNER_EMAIL = "owner@niko.sryze.cc";

// Catalogue keys: a request status is interface copy, not server data.
const STATUS_KEYS: Record<string, string> = {
  pending: "status.pending",
  completed: "status.completed",
  denied: "status.denied",
  withdrawn: "status.withdrawn",
};

function formatDate(value?: number | null) {
  if (!value) return "—";
  return new Date(value * 1000).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function DataRemovalPage() {
  const { t } = useStrings("data-removal");
  const [authChecked, setAuthChecked] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [csrf, setCsrf] = useState("");
  const [overview, setOverview] = useState<DataRemovalOverview | null>(null);
  const [scope, setScope] = useState<"account" | "server">("account");
  const [guildId, setGuildId] = useState("");
  const [reason, setReason] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [understood, setUnderstood] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loadingRequests, setLoadingRequests] = useState(false);

  const load = useCallback(async () => {
    setLoadingRequests(true);
    setError("");
    try {
      const result = await api<DataRemovalOverview>("/api/privacy/data-removal");
      setOverview(result);
      if (!guildId && result.servers.length > 0) setGuildId(result.servers[0].id);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) {
        setOverview(null);
        setAuthenticated(false);
      } else {
        setError(reason instanceof Error ? reason.message : t("error.load"));
      }
    } finally {
      setLoadingRequests(false);
    }
  }, [guildId, t]);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const auth = await getAuth();
        if (!active) return;
        setAuthenticated(auth.authenticated);
        setCsrf(auth.csrf_token || "");
        if (auth.authenticated) await load();
      } catch {
        if (active) setError(t("error.auth"));
      } finally {
        if (active) setAuthChecked(true);
      }
    })();
    return () => { active = false; };
  }, [load]);

  const selectedServer = overview?.servers.find((server) => server.id === guildId) || null;
  const targetName = scope === "server" ? selectedServer?.name || "" : "account data";
  const expectedConfirmation = scope === "server" ? selectedServer?.name || "" : overview?.confirmations.account || "DELETE MY DATA";
  const canSubmit = Boolean(
    authenticated
    && understood
    && reason.trim().length >= (overview?.confirmations.min_reason_length || 20)
    && confirmation === expectedConfirmation
    && (scope === "account" || selectedServer)
    && !busy
    && !(scope === "account" && overview?.account.pending)
    && !(scope === "server" && selectedServer?.pending),
  );

  const submit = async () => {
    if (!canSubmit) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await api<{ ok: boolean }>("/api/privacy/data-removal", {
        method: "POST",
        headers: { "X-CSRF-Token": csrf },
        body: JSON.stringify({
          scope,
          guild_id: scope === "server" ? guildId : undefined,
          reason,
          confirmation,
        }),
      });
      setSuccess(`Request received for ${targetName}. The bot owner will review it before anything is deleted.`);
      setReason("");
      setConfirmation("");
      setUnderstood(false);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : t("error.submit"));
    } finally {
      setBusy(false);
    }
  };

  const withdraw = async (request: DataRemovalRequest) => {
    if (!window.confirm(t("confirm.withdraw"))) return;
    setError("");
    setSuccess("");
    try {
      await api(`/api/privacy/data-removal/${request.id}`, {
        method: "DELETE",
        headers: { "X-CSRF-Token": csrf },
      });
      setSuccess(t("success.withdrawn"));
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : t("error.withdraw"));
    }
  };

  return (
    <>
      <PublicHeader page="data-removal" />
      <main className="shell page-main data-removal-page">
        <div className="page-heading data-removal-heading">
          <div className="eyebrow">{t("heading.eyebrow")}</div>
          <h1>{t("heading.titleA")}<br />{t("heading.titleB")}</h1>
          <p>{t("heading.body")}</p>
          <div className="data-removal-badges">
            <span><Icon name="lock" /> {t("badge.signin")}</span>
            <span><Icon name="shield" /> {t("badge.ownership")}</span>
            <span><Icon name="users" /> {t("badge.owner")}</span>
          </div>
        </div>

        <div className="data-removal-layout">
          <section className="data-removal-policy" aria-labelledby="data-removal-policy-title">
            <span className="panel-kicker">{t("policy.kicker")}</span>
            <h2 id="data-removal-policy-title">{t("policy.title")}</h2>

            <article>
              <h3>{t("policy.account.title")}</h3>
              <p>{t("policy.account.body")}</p>
            </article>

            <article>
              <h3>{t("policy.server.title")}</h3>
              <p>{t("policy.server.body")}</p>
            </article>

            <article>
              <h3>{t("policy.instances.title")}</h3>
              <p>
                {t("policy.instances.bodyBefore")}{" "}
                <a href="/privacy" onClick={(event) => { event.preventDefault(); navigate("/privacy"); }}>{t("policy.instances.link")}</a>{" "}
                {t("policy.instances.bodyAfter")}
              </p>
            </article>

            <article className="data-removal-preserved">
              <h3>{t("policy.preserved.title")}</h3>
              <p>
                {t("policy.preserved.bodyBefore")} <strong>{t("policy.preserved.not")}</strong> {t("policy.preserved.bodyAfter")}
              </p>
            </article>

            <article>
              <h3>{t("policy.legal.title")}</h3>
              <p>
                {t("policy.legal.bodyBefore")}{" "}
                <a href={`mailto:${OWNER_EMAIL}`}>{OWNER_EMAIL}</a>{" "}
                {t("policy.legal.bodyAfter")}
              </p>
            </article>

            <article>
              <h3>{t("policy.review.title")}</h3>
              <ul>
                <li>{t("policy.review.account")}</li>
                <li>{t("policy.review.owner")}</li>
                <li>{t("policy.review.limit")}</li>
                <li>{t("policy.review.ownerReview")}</li>
                <li>{t("policy.review.irreversible")}</li>
              </ul>
            </article>

            <p className="data-removal-contact">
              {t("policy.contact.before")} <SupportLink>{t("policy.contact.link")}</SupportLink> {t("policy.contact.after")}
            </p>
          </section>

          <section className="data-removal-form" aria-labelledby="data-removal-form-title">
            <span className="panel-kicker">{t("form.kicker")}</span>
            <h2 id="data-removal-form-title">{t("form.title")}</h2>

            {!authChecked ? (
              <div className="data-removal-loading"><span className="loading-ring" /><p>{t("loading")}</p></div>
            ) : !authenticated ? (
              <div className="data-removal-signin">
                <span className="data-removal-signin-icon"><Icon name="lock" /></span>
                <h3>{t("signin.title")}</h3>
                <p>{t("signin.body")}</p>
                <a
                  className="button button-primary"
                  href={`/auth/login?next=${encodeURIComponent("/data-removal")}`}
                >
                  {t("signin.cta")} <Icon name="arrow" />
                </a>
              </div>
            ) : (
              <>
                <div className="data-removal-scope" role="tablist" aria-label={t("scope.aria")}>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={scope === "account"}
                    className={scope === "account" ? "is-selected" : ""}
                    onClick={() => { setScope("account"); setConfirmation(""); }}
                  >
                    <Icon name="users" />
                    <span><strong>{t("scope.account")}</strong><small>{t("scope.accountDetail")}</small></span>
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={scope === "server"}
                    className={scope === "server" ? "is-selected" : ""}
                    onClick={() => { setScope("server"); setConfirmation(""); }}
                  >
                    <Icon name="shield" />
                    <span><strong>{t("scope.server")}</strong><small>{t("scope.serverDetail")}</small></span>
                  </button>
                </div>

                {scope === "server" && (
                  <div className="data-removal-field">
                    <span className="data-removal-label">{t("server.label")}</span>
                    {loadingRequests && !overview ? (
                      <div className="data-removal-skeleton" />
                    ) : overview && overview.servers.length > 0 ? (
                      <div className="data-removal-servers" role="radiogroup" aria-label={t("server.label")}>
                        {overview.servers.map((server) => (
                          <button
                            key={server.id}
                            type="button"
                            role="radio"
                            aria-checked={guildId === server.id}
                            className={`data-removal-server${guildId === server.id ? " is-selected" : ""}`}
                            disabled={server.pending}
                            onClick={() => { setGuildId(server.id); setConfirmation(""); }}
                          >
                            <span className="data-removal-server-icon">
                              {server.icon_url ? <img src={server.icon_url} alt="" /> : <b>{server.name.slice(0, 1)}</b>}
                            </span>
                            <span className="data-removal-server-text">
                              <strong>{server.name}</strong>
                              <small>
                                {t(server.pending
                                  ? "server.pending"
                                  : server.bot_present
                                    ? "server.present"
                                    : "server.removed")}
                              </small>
                            </span>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="data-removal-hint">{t("server.empty")}</p>
                    )}
                    {overview && overview.servers.length === 0 && (
                      <p className="data-removal-hint">{t("server.emptyLegacy")}</p>
                    )}
                  </div>
                )}

                <label className="data-removal-field">
                  <span className="data-removal-label">{t("reason.label")}</span>
                  <textarea
                    rows={4}
                    maxLength={2000}
                    value={reason}
                    onChange={(event) => setReason(event.target.value)}
                    placeholder={t("reason.placeholder")}
                  />
                  <small>{t("reason.count", { count: reason.trim().length, min: overview?.confirmations.min_reason_length || 20 })}</small>
                </label>

                <label className="data-removal-field">
                  <span className="data-removal-label">
                    {scope === "server" ? t("confirm.labelServer") : t("confirm.labelAccount", { account: overview?.confirmations.account ?? "" })}
                  </span>
                  <input
                    value={confirmation}
                    onChange={(event) => setConfirmation(event.target.value)}
                    placeholder={expectedConfirmation || t("confirm.placeholder")}
                    autoComplete="off"
                  />
                </label>

                <label className="data-removal-check">
                  <input type="checkbox" checked={understood} onChange={(event) => setUnderstood(event.target.checked)} />
                  <span>{t("understood")}</span>
                </label>

                {error && <p className="data-removal-error" role="alert">{error}</p>}
                {success && <p className="data-removal-success" role="status">{success}</p>}

                <button type="button" className="data-removal-submit" onClick={() => void submit()} disabled={!canSubmit}>
                  {t(busy ? "submitting" : "submit")} <Icon name="arrow" />
                </button>
                <p className="data-removal-fineprint">{t("fineprint")}</p>
              </>
            )}

            {authenticated && overview && overview.requests.length > 0 && (
              <div className="data-removal-history">
                <h3>{t("history.title")}</h3>
                {overview.requests.map((request) => (
                  <article key={request.id} className={`data-removal-request is-${request.status}`}>
                    <div className="data-removal-request-head">
                      <div>
                        <strong>{request.scope === "account" ? t("history.account") : request.guild_name || t("history.server")}</strong>
                        <small>{formatDate(request.created_at)} · ID {request.id.slice(0, 8)}</small>
                      </div>
                      <span className={`data-removal-status is-${request.status}`}>
                        {STATUS_KEYS[request.status] ? t(STATUS_KEYS[request.status]) : request.status}
                      </span>
                    </div>
                    {request.review_note && <p className="data-removal-note">{request.review_note}</p>}
                    {request.status === "pending" && (
                      <button type="button" className="data-removal-withdraw" onClick={() => void withdraw(request)}>
                        {t("history.withdraw")}
                      </button>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>

        <div className="data-removal-back">
          <button type="button" className="link-button" onClick={() => navigate("/privacy")}>
            {t("back.privacy")}
          </button>
          <button type="button" className="link-button" onClick={() => navigate("/terms")}>
            {t("back.terms")}
          </button>
        </div>
      </main>
      <Footer />
    </>
  );
}
