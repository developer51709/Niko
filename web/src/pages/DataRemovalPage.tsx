import { useCallback, useEffect, useState } from "react";
import { api, ApiError, getAuth } from "../api";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { SupportLink } from "../components/SupportLink";
import { navigate } from "../router";
import type { DataRemovalOverview, DataRemovalRequest } from "../types";

const OWNER_CONTACT = "https://sorenthedev.indevs.in";

const STATUS_LABELS: Record<string, string> = {
  pending: "Awaiting review",
  completed: "Completed",
  denied: "Not approved",
  withdrawn: "Withdrawn",
};

function formatDate(value?: number | null) {
  if (!value) return "—";
  return new Date(value * 1000).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function DataRemovalPage() {
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
        setError(reason instanceof Error ? reason.message : "Your data requests could not be loaded.");
      }
    } finally {
      setLoadingRequests(false);
    }
  }, [guildId]);

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
        if (active) setError("Sign-in status could not be checked. Refresh the page to try again.");
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
      setError(reason instanceof Error ? reason.message : "The request could not be submitted.");
    } finally {
      setBusy(false);
    }
  };

  const withdraw = async (request: DataRemovalRequest) => {
    if (!window.confirm("Withdraw this request? You can submit a new one later.")) return;
    setError("");
    setSuccess("");
    try {
      await api(`/api/privacy/data-removal/${request.id}`, {
        method: "DELETE",
        headers: { "X-CSRF-Token": csrf },
      });
      setSuccess("Request withdrawn. Nothing was deleted.");
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The request could not be withdrawn.");
    }
  };

  return (
    <>
      <PublicHeader page="data-removal" />
      <main className="shell page-main data-removal-page">
        <div className="page-heading data-removal-heading">
          <div className="eyebrow">Privacy · data removal</div>
          <h1>Your data.<br />Your decision.</h1>
          <p>
            Request deletion of account data or a server's data. Every request is reviewed and
            ownership is verified first. Safety and moderation records are protected on purpose —
            so this process can never be used to erase a ban, warning, or investigation.
          </p>
          <div className="data-removal-badges">
            <span><Icon name="lock" /> Discord sign-in required</span>
            <span><Icon name="shield" /> Ownership verified</span>
            <span><Icon name="users" /> Reviewed by the bot owner</span>
          </div>
        </div>

        <div className="data-removal-layout">
          <section className="data-removal-policy" aria-labelledby="data-removal-policy-title">
            <span className="panel-kicker">The policy</span>
            <h2 id="data-removal-policy-title">What this process can and cannot delete</h2>

            <article>
              <h3>Account data</h3>
              <p>
                Deletes the personal data attached to your Discord account: economy balances,
                leveling XP, birthdays, reminders, AFK state, music library, giveaway entries,
                poll votes, roleplay preferences, staff application submissions, and any public
                staff profile (bio, banner, and links). Your name is also removed from suggestions
                and giveaway hosts where it was attached to server content.
              </p>
            </article>

            <article>
              <h3>Server data</h3>
              <p>
                Deletes a server's Niko configuration and content: AutoMod and logging settings,
                leveling data, tickets configuration, giveaways, polls, starboard entries,
                social notifier follows, voicemaster settings, profiles, and related settings.
                The server's deletion stays available after Niko is removed, as long as you were
                the owner when it left.
              </p>
            </article>

            <article className="data-removal-preserved">
              <h3>What is always preserved</h3>
              <p>
                Moderation and safety records are <strong>not</strong> deleted by an account or
                server request. This includes bot-level blacklists, warnings, mutes, moderation
                cases, logs and ticket transcripts, giveaway bans, abuse strikes, and scam-image
                reports. Deleting everything else does not lift a restriction, restore access, or
                remove evidence of abuse.
              </p>
            </article>

            <article>
              <h3>Legal or court-ordered deletion</h3>
              <p>
                If a law requires deletion of a preserved moderation or safety record, do not use
                this form. Send a formal legal request directly to the bot owner through{" "}
                <a href={OWNER_CONTACT} target="_blank" rel="noreferrer">sorenthedev.indevs.in</a>.
                It must include a court record or a signed legal document and the contact details
                of an official legal representative so authenticity can be verified. These
                requests are handled personally and confidentially. Ordinary requests never
                receive special treatment, and the strict review protects the community from
                people trying to erase the consequences of abuse.
              </p>
            </article>

            <article>
              <h3>How review works</h3>
              <ul>
                <li>Requests are accepted only from the signed-in Discord account they belong to.</li>
                <li>A server request must match the recorded owner, or the current owner if Niko is still in the server.</li>
                <li>One open request is allowed per account or server, with a small daily limit.</li>
                <li>The bot owner reviews every request. Withdraw a pending request at any time.</li>
                <li>Deletion is irreversible. Financial records required for accounting, fraud prevention, and refunds are retained.</li>
              </ul>
            </article>

            <p className="data-removal-contact">
              Questions about a request? Open a private ticket in the <SupportLink /> and quote your
              request ID. Do not post identity documents in a public channel.
            </p>
          </section>

          <section className="data-removal-form" aria-labelledby="data-removal-form-title">
            <span className="panel-kicker">Request form</span>
            <h2 id="data-removal-form-title">Start a deletion request</h2>

            {!authChecked ? (
              <div className="data-removal-loading"><span className="loading-ring" /><p>Checking your session…</p></div>
            ) : !authenticated ? (
              <div className="data-removal-signin">
                <span className="data-removal-signin-icon"><Icon name="lock" /></span>
                <h3>Sign in to verify ownership</h3>
                <p>
                  Deletion requests are tied to the Discord account that owns the data or server.
                  Signing in is how that ownership is confirmed.
                </p>
                <a
                  className="button button-primary"
                  href={`/auth/login?next=${encodeURIComponent("/data-removal")}`}
                >
                  Sign in with Discord <Icon name="arrow" />
                </a>
              </div>
            ) : (
              <>
                <div className="data-removal-scope" role="tablist" aria-label="Deletion target">
                  <button
                    type="button"
                    role="tab"
                    aria-selected={scope === "account"}
                    className={scope === "account" ? "is-selected" : ""}
                    onClick={() => { setScope("account"); setConfirmation(""); }}
                  >
                    <Icon name="users" />
                    <span><strong>My account</strong><small>Personal data only</small></span>
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={scope === "server"}
                    className={scope === "server" ? "is-selected" : ""}
                    onClick={() => { setScope("server"); setConfirmation(""); }}
                  >
                    <Icon name="shield" />
                    <span><strong>A server</strong><small>Owner-verified</small></span>
                  </button>
                </div>

                {scope === "server" && (
                  <div className="data-removal-field">
                    <span className="data-removal-label">Server</span>
                    {loadingRequests && !overview ? (
                      <div className="data-removal-skeleton" />
                    ) : overview && overview.servers.length > 0 ? (
                      <div className="data-removal-servers" role="radiogroup" aria-label="Server">
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
                                {server.pending
                                  ? "Request pending"
                                  : server.bot_present
                                    ? "Niko is in this server · you are the owner"
                                    : "Niko was removed · owner at removal recorded"}
                              </small>
                            </span>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="data-removal-hint">
                        No owner-verified servers were found. Only the member who owns the server,
                        or owned it when Niko was removed, can request its deletion.
                      </p>
                    )}
                    {overview && overview.servers.length === 0 && (
                      <p className="data-removal-hint">
                        If you removed Niko before this ownership record existed, contact the bot
                        owner through the support server with proof that you owned the server.
                      </p>
                    )}
                  </div>
                )}

                <label className="data-removal-field">
                  <span className="data-removal-label">Why are you requesting this?</span>
                  <textarea
                    rows={4}
                    maxLength={2000}
                    value={reason}
                    onChange={(event) => setReason(event.target.value)}
                    placeholder="Required. A short, honest explanation helps the review go quickly."
                  />
                  <small>{reason.trim().length}/2000 · minimum {overview?.confirmations.min_reason_length || 20} characters</small>
                </label>

                <label className="data-removal-field">
                  <span className="data-removal-label">
                    Type {scope === "server" ? "the server name" : <code>{overview?.confirmations.account}</code>} to confirm
                  </span>
                  <input
                    value={confirmation}
                    onChange={(event) => setConfirmation(event.target.value)}
                    placeholder={expectedConfirmation || "Select a server first"}
                    autoComplete="off"
                  />
                </label>

                <label className="data-removal-check">
                  <input type="checkbox" checked={understood} onChange={(event) => setUnderstood(event.target.checked)} />
                  <span>
                    I understand that moderation and safety records are preserved, that this does
                    not lift any restriction, and that deletion cannot be undone.
                  </span>
                </label>

                {error && <p className="data-removal-error" role="alert">{error}</p>}
                {success && <p className="data-removal-success" role="status">{success}</p>}

                <button type="button" className="data-removal-submit" onClick={() => void submit()} disabled={!canSubmit}>
                  {busy ? "Submitting…" : "Submit for review"} <Icon name="arrow" />
                </button>
                <p className="data-removal-fineprint">
                  Submitting does not delete anything immediately. A pending request can be withdrawn.
                </p>
              </>
            )}

            {authenticated && overview && overview.requests.length > 0 && (
              <div className="data-removal-history">
                <h3>Your requests</h3>
                {overview.requests.map((request) => (
                  <article key={request.id} className={`data-removal-request is-${request.status}`}>
                    <div className="data-removal-request-head">
                      <div>
                        <strong>{request.scope === "account" ? "Account data" : request.guild_name || "Server data"}</strong>
                        <small>{formatDate(request.created_at)} · ID {request.id.slice(0, 8)}</small>
                      </div>
                      <span className={`data-removal-status is-${request.status}`}>
                        {STATUS_LABELS[request.status] || request.status}
                      </span>
                    </div>
                    {request.review_note && <p className="data-removal-note">{request.review_note}</p>}
                    {request.status === "pending" && (
                      <button type="button" className="data-removal-withdraw" onClick={() => void withdraw(request)}>
                        Withdraw request
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
            ← Read the full privacy policy
          </button>
          <button type="button" className="link-button" onClick={() => navigate("/terms")}>
            Read the terms of service →
          </button>
        </div>
      </main>
      <Footer />
    </>
  );
}
