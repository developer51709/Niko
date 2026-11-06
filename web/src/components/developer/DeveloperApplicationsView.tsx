import { useCallback, useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import {
  createDeveloperApplication,
  deleteDeveloperApplication,
  getDeveloperApplicationReview,
  getDeveloperApplications,
  reviewDeveloperApplication,
  testDeveloperWebhook,
  updateDeveloperWebhook,
} from "../../api";
import { Icon } from "../Icon";
import { Field } from "../dashboard/FormField";
import { SectionTitle } from "../dashboard/SectionTitle";
import { SettingCard, SettingCards } from "../dashboard/SettingCards";
import { Switch } from "../dashboard/Switch";
import { DeveloperPage, DeveloperScopePicker } from "./DeveloperLayout";
import type {
  AuthStatus,
  DeveloperApplication,
  DeveloperApplicationList,
  DeveloperApplicationReviewList,
  DeveloperMe,
} from "../../types";
import { notifyError, notifySuccess } from "../../utils/toast";

function when(timestamp: number | null | undefined) {
  if (!timestamp) return "—";
  return new Date(timestamp * 1000).toLocaleString();
}

function ScopeChips({ scopes }: { scopes: string[] }) {
  return <div className="developer-key-scopes">{scopes.length ? scopes.map((scope) => <code key={scope}>{scope}</code>) : <span className="developer-muted-copy">No permissions</span>}</div>;
}

function ApplicationStatus({ status }: { status: DeveloperApplication["status"] }) {
  return <span className={`developer-application-status is-${status}`}>{status}</span>;
}

function ScreenshotExample() {
  return (
    <figure className="developer-screenshot-example" aria-label="Required Discord Developer Portal verification screenshot">
      <a href="/assets/developer-application-example.webp" target="_blank" rel="noreferrer" title="Open the example screenshot at full size">
        <img
          src="/assets/developer-application-example.webp"
          alt="Discord Developer Portal with the profile menu open above the General Information panel, showing the username and Application ID in the same screenshot."
          width={1080}
          height={817}
          loading="lazy"
        />
      </a>
      <figcaption>
        <strong>Required: the profile popup must be open.</strong> Your screenshot has to show Discord's profile popup with your username, together with the Application ID. An application submitted without the popup open is denied.{" "}
        <a href="/assets/developer-application-example.webp" target="_blank" rel="noreferrer">Open full size</a>.
      </figcaption>
    </figure>
  );
}

function WebhookEditor({
  application,
  csrfToken,
  developerScopes,
  availableEvents,
  onSaved,
}: {
  application: DeveloperApplication;
  csrfToken?: string;
  developerScopes: string[];
  availableEvents: DeveloperApplicationList["events"];
  onSaved: (updated: DeveloperApplication) => void;
}) {
  const [url, setUrl] = useState(application.webhook.url || "");
  const [enabled, setEnabled] = useState(Boolean(application.webhook.enabled));
  const [events, setEvents] = useState<string[]>(application.webhook.events || []);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const canReceiveEvents = application.approved_scopes.includes("warns:read") && developerScopes.includes("warns:read");

  const save = async () => {
    if (!csrfToken || saving) return;
    setSaving(true);
    try {
      const result = await updateDeveloperWebhook(application.id, { url, enabled, events }, csrfToken);
      onSaved({ ...application, webhook: result.webhook, webhook_configured: Boolean(result.webhook.url) });
      notifySuccess(result.webhook.enabled ? "Webhook delivery enabled." : "Webhook settings saved.", "developer-webhook");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The webhook could not be saved.", "developer-webhook");
    } finally {
      setSaving(false);
    }
  };

  const test = async () => {
    if (!csrfToken || testing) return;
    setTesting(true);
    try {
      const result = await testDeveloperWebhook(application.id, csrfToken);
      notifySuccess(`Test event delivered (HTTP ${result.status ?? "ok"}).`, "developer-webhook");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The test event could not be delivered.", "developer-webhook");
    } finally {
      setTesting(false);
    }
  };

  const toggleEvent = (event: string) => {
    setEvents((current) => current.includes(event) ? current.filter((item) => item !== event) : [...current, event]);
  };

  const copySecret = async () => {
    if (!application.webhook.secret) return;
    try {
      await navigator.clipboard.writeText(application.webhook.secret);
      notifySuccess("Webhook signing secret copied.", "developer-webhook");
    } catch {
      notifyError("The browser blocked clipboard access. Select the secret and copy it manually.", "developer-webhook");
    }
  };

  return (
    <div className="developer-webhook-editor">
      <SectionTitle
        label="Event delivery"
        title="Bot webhook"
        detail="Niko sends only events from guilds where this bot and Niko are both members. Verify X-Niko-Signature before trusting a delivery."
        action={<span className={`developer-status${enabled ? "" : " is-off"}`}>{enabled ? "Enabled" : "Off"}</span>}
      />
      {!canReceiveEvents ? <p className="setting-note" role="status"><strong>Warnings read is not available.</strong> Ask the owner to approve <code>warns:read</code> for this application and restore the same permission on your developer account before enabling warning events.</p> : null}
      <Field label="HTTPS endpoint" hint="The URL that receives signed POST requests from Niko.">
        <input value={url} placeholder="https://api.yourbot.dev/niko/events" onChange={(event) => setUrl(event.target.value)} />
      </Field>
      <Field label="Events" hint="Choose the event types this endpoint should receive.">
        <SettingCards className="developer-event-picker">
          {availableEvents.map((event) => (
            <SettingCard
              key={event.key}
              title={event.label}
              hint={event.description}
              action={<Switch size="sm" checked={events.includes(event.key)} onCheckedChange={() => toggleEvent(event.key)} aria-label={`${event.label} webhook event`} />}
            />
          ))}
        </SettingCards>
      </Field>
      <SettingCards>
        <SettingCard title="Enable deliveries" hint="Keep the endpoint saved while temporarily pausing event delivery." action={<Switch checked={enabled} onCheckedChange={setEnabled} aria-label="Enable webhook deliveries" />} />
      </SettingCards>
      <div className="setting-footer">
        <span role="status">The signing secret stays the same until the webhook is recreated.</span>
        <div className="developer-webhook-actions">
          <button className="button button-muted button-small" onClick={test} disabled={testing || !url.trim()}>{testing ? "Sending…" : "Send test event"}</button>
          <button className="button button-primary button-small" onClick={save} disabled={saving || !canReceiveEvents || (enabled && !url.trim())}>{saving ? "Saving…" : "Save webhook"}</button>
        </div>
      </div>
      {application.webhook.secret ? (
        <div className="developer-webhook-secret">
          <div><span>Signing secret</span><small>Use this to verify every delivery.</small></div>
          <code>{application.webhook.secret}</code>
          <button className="button button-small button-muted" onClick={copySecret}><Icon name="copy" /> Copy</button>
        </div>
      ) : null}
      <div className="developer-webhook-delivery">
        <span>Last delivery: {when(application.webhook.last_delivery_at)}</span>
        <span>{application.webhook.last_delivery_status ? `HTTP ${application.webhook.last_delivery_status}` : "No response yet"}</span>
        {application.webhook.last_delivery_error ? <span className="developer-webhook-error">{application.webhook.last_delivery_error}</span> : null}
      </div>
    </div>
  );
}

export function DeveloperApplicationsView({ auth, me }: { auth: AuthStatus; me: DeveloperMe }) {
  const [data, setData] = useState<DeveloperApplicationList | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [botUserId, setBotUserId] = useState("");
  const [selectedScopes, setSelectedScopes] = useState<string[]>([]);
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setData(await getDeveloperApplications());
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "Applications could not be loaded.", "developer-applications");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  useEffect(() => {
    if (!screenshot) {
      setPreview("");
      return;
    }
    const url = URL.createObjectURL(screenshot);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [screenshot]);

  // Escape closes the registration dialog, but never mid-submission.
  useEffect(() => {
    if (!formOpen) return;
    const handle = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !submitting) setFormOpen(false);
    };
    document.addEventListener("keydown", handle);
    return () => document.removeEventListener("keydown", handle);
  }, [formOpen, submitting]);

  const scopes = useMemo(() => data?.scopes || [], [data?.scopes]);
  const approvedApps = useMemo(() => (data?.applications || []).filter((app) => app.status === "approved"), [data?.applications]);

  const submit = async () => {
    if (!auth.csrf_token || submitting) return;
    if (!screenshot) {
      notifyError("Upload the Discord Developer Portal screenshot first.", "developer-application");
      return;
    }
    const form = new FormData();
    form.append("name", name);
    form.append("description", description);
    form.append("bot_user_id", botUserId);
    selectedScopes.forEach((scope) => form.append("scopes", scope));
    form.append("screenshot", screenshot);
    setSubmitting(true);
    try {
      const result = await createDeveloperApplication(form, auth.csrf_token);
      setData((current) => current ? { ...current, applications: [result.application, ...current.applications.filter((app) => app.id !== result.application.id)] } : current);
      setName("");
      setDescription("");
      setBotUserId("");
      setSelectedScopes([]);
      setScreenshot(null);
      setFormOpen(false);
      notifySuccess("Application submitted for owner review.", "developer-application");
      await load();
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The application could not be submitted.", "developer-application");
    } finally {
      setSubmitting(false);
    }
  };

  const remove = async (applicationId: string) => {
    if (!auth.csrf_token) return;
    try {
      await deleteDeveloperApplication(applicationId, auth.csrf_token);
      setConfirmDelete("");
      setData((current) => current ? { ...current, applications: current.applications.filter((app) => app.id !== applicationId) } : current);
      notifySuccess("Denied application removed.", "developer-application");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The application could not be removed.", "developer-application");
    }
  };

  if (loading && !data) {
    return <div className="settings-stack developer-settings-stack"><div className="empty-state">Loading applications…</div></div>;
  }

  return (
    <DeveloperPage
      eyebrow="Bot applications"
      title="Applications & webhooks"
      text="Register your bot, wait for owner verification, then receive detected guild events instead of polling for warnings."
      actions={<>
        <button className="button button-primary button-small" onClick={() => setFormOpen(true)}><Icon name="plus" /> Register application</button>
        <button className="button button-muted button-small" onClick={load} disabled={loading}><Icon name="refresh" /> Refresh</button>
      </>}
    >
      <p className="setting-note" role="note"><strong>Verification is manual.</strong> Your screenshot must show Discord's profile menu open with your username visible and the same Application ID you submit. The Niko owner compares it with the bot resolved from Discord before approving.</p>

      <section className="dash-panel settings-panel">
        <SectionTitle label="Your applications" title={`${data?.applications.length || 0} registered`} detail="Approved applications can be bound to API keys and receive signed webhook events." icon="terminal" />
        {!data?.applications.length ? <div className="empty-state">No applications yet. Use Register application to request reviewed access.</div> : (
          <div className="developer-application-list">
            {data.applications.map((application) => (
              <article key={application.id} className={`developer-application-card is-${application.status}`}>
                <div className="developer-application-card-head">
                  <div className="developer-application-identity">
                    {application.bot_avatar_url ? <img src={application.bot_avatar_url} alt="" /> : <span className="developer-avatar-fallback">{application.name.slice(0, 1).toUpperCase()}</span>}
                    <div>
                      <strong>{application.name}</strong>
                      <small>{application.bot_username ? `@${application.bot_username} · ` : ""}{application.bot_user_id}</small>
                    </div>
                  </div>
                  <ApplicationStatus status={application.status} />
                </div>
                <p>{application.description || "No description provided."}</p>
                <div className="developer-application-meta">
                  <span>Submitted {when(application.submitted_at)}</span>
                  <span>{application.status === "approved" ? `Approved ${when(application.reviewed_at)}` : application.status === "denied" ? `Reviewed ${when(application.reviewed_at)}` : "Waiting for owner review"}</span>
                  {application.screenshot ? <a href={application.screenshot.url} target="_blank" rel="noreferrer">View screenshot <Icon name="external" size={12} /></a> : null}
                </div>
                <div className="developer-application-scope-row">
                  <div><span className="developer-application-label">Requested</span><ScopeChips scopes={application.requested_scopes} /></div>
                  {application.status === "approved" ? <div><span className="developer-application-label">Approved</span><ScopeChips scopes={application.approved_scopes} /></div> : null}
                </div>
                {application.review_note ? <div className="developer-appeal-note"><span>Owner note</span>{application.review_note}</div> : null}
                {application.status === "approved" ? <WebhookEditor application={application} csrfToken={auth.csrf_token} developerScopes={me.access.scopes} availableEvents={data?.events || []} onSaved={(updated) => setData((current) => current ? { ...current, applications: current.applications.map((app) => app.id === updated.id ? updated : app) } : current)} /> : null}
                {application.status === "denied" ? (
                  <div className="developer-application-actions">
                    <span className="developer-muted-copy">Fix the submission and submit the same bot ID again to reopen review.</span>
                    {confirmDelete === application.id ? (
                      <><button className="button button-small developer-danger" onClick={() => remove(application.id)}>Confirm remove</button><button className="button button-small button-muted" onClick={() => setConfirmDelete("")}>Cancel</button></>
                    ) : <button className="button button-small button-muted" onClick={() => setConfirmDelete(application.id)}>Remove</button>}
                  </div>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </section>
      {approvedApps.length ? <p className="form-hint">Approved applications can create app-bound keys on the <a href="#keys">API keys</a> page.</p> : null}

      {formOpen ? createPortal(
        <div
          className="developer-form-backdrop"
          onMouseDown={(event) => {
            // Only a click that starts and ends on the backdrop dismisses; a
            // drag out of the dialog (selecting the popup text) must not.
            if (event.target === event.currentTarget && !submitting) setFormOpen(false);
          }}
        >
          <section className="developer-form-dialog" role="dialog" aria-modal="true" aria-labelledby="developer-application-form-title">
            <header className="developer-form-head">
              <div>
                <span className="panel-kicker">New submission</span>
                <h2 id="developer-application-form-title">Register your bot</h2>
                <p>Submit the bot identity, the permissions it needs, and a verification screenshot.</p>
              </div>
              <button type="button" className="developer-form-close" onClick={() => setFormOpen(false)} disabled={submitting} aria-label="Close registration form"><Icon name="close" /></button>
            </header>
            {!me.access.policy_accepted ? (
              <p className="setting-note" role="status"><strong>Accept the developer guidelines first.</strong> Application submission is locked until you agree to the developer policies.</p>
            ) : null}
            <div className="developer-application-form-layout">
              <div className="developer-application-fields">
                <div className="form-grid">
                  <Field label="Application name"><input autoFocus value={name} maxLength={80} placeholder="Aeris" onChange={(event) => setName(event.target.value)} /></Field>
                  <Field label="Bot user / Application ID" hint="Discord's bot user ID is the same as its Application ID."><input value={botUserId} inputMode="numeric" placeholder="1545846783253545081" onChange={(event) => setBotUserId(event.target.value.replace(/\D/g, ""))} /></Field>
                  <div className="developer-field-wide">
                    <Field label="What does it do?" hint="A short description helps the owner review the integration."><textarea value={description} maxLength={400} placeholder="A moderation syncing bridge for partnered communities." onChange={(event) => setDescription(event.target.value)} /></Field>
                  </div>
                </div>
                <div className="developer-field-wide">
                  <Field label="Requested permissions" hint="Only request the scopes this integration actually needs.">
                    <DeveloperScopePicker scopes={scopes} selected={selectedScopes} onToggle={(scope) => setSelectedScopes((current) => current.includes(scope) ? current.filter((item) => item !== scope) : [...current, scope])} />
                  </Field>
                </div>
                <Field label="Developer Portal screenshot" hint="PNG, JPEG, GIF, or WebP. Maximum 8 MB.">
                  <input type="file" accept="image/png,image/jpeg,image/gif,image/webp" onChange={(event) => setScreenshot(event.target.files?.[0] || null)} />
                </Field>
              </div>
              <div className="developer-verification-example">
                <ScreenshotExample />
                {preview ? <img className="developer-screenshot-preview" src={preview} alt="Selected verification screenshot preview" /> : null}
              </div>
            </div>
            <div className="setting-footer developer-form-footer">
              <span role="status">Submitting opens the application for owner review.</span>
              <div className="developer-form-actions">
                <button type="button" className="button button-muted" onClick={() => setFormOpen(false)} disabled={submitting}>Cancel</button>
                <button type="button" className="button button-primary" onClick={submit} disabled={submitting || !me.access.policy_accepted || !screenshot || !name.trim() || !botUserId.trim() || selectedScopes.length === 0}>
                  {submitting ? "Submitting…" : "Submit for review"}
                </button>
              </div>
            </div>
          </section>
        </div>,
        document.body,
      ) : null}
    </DeveloperPage>
  );
}

export function DeveloperApplicationReviewView({ auth }: { auth: AuthStatus }) {
  const [data, setData] = useState<DeveloperApplicationReviewList | null>(null);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [selectedScopes, setSelectedScopes] = useState<Record<string, string[]>>({});
  const [reviewing, setReviewing] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getDeveloperApplicationReview();
      setData(result);
      setSelectedScopes((current) => {
        const next = { ...current };
        result.applications.forEach((application) => {
          if (!next[application.id]) next[application.id] = application.requested_scopes;
        });
        return next;
      });
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The application review queue could not be loaded.", "developer-review");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const decide = async (application: DeveloperApplication, status: "approved" | "denied") => {
    if (!auth.csrf_token || reviewing) return;
    setReviewing(application.id);
    try {
      await reviewDeveloperApplication(application.id, {
        status,
        scopes: status === "approved" ? selectedScopes[application.id] || [] : undefined,
        note: notes[application.id] || "",
      }, auth.csrf_token);
      notifySuccess(status === "approved" ? "Application approved." : "Application denied.", "developer-review");
      setNotes((current) => ({ ...current, [application.id]: "" }));
      await load();
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The application decision could not be saved.", "developer-review");
    } finally {
      setReviewing("");
    }
  };

  const toggleScope = (applicationId: string, scope: string) => {
    setSelectedScopes((current) => {
      const selected = current[applicationId] || [];
      return {
        ...current,
        [applicationId]: selected.includes(scope) ? selected.filter((item) => item !== scope) : [...selected, scope],
      };
    });
  };

  const pending = data?.applications.filter((application) => application.status === "pending").length || 0;

  return (
    <DeveloperPage
      eyebrow="Owner only"
      title="Application review"
      text="Compare each screenshot with the resolved bot identity and Application ID before approving API access."
      actions={<>
        <span className="developer-status">{pending} pending</span>
        <button className="button button-muted button-small" onClick={load} disabled={loading}><Icon name="refresh" /> Refresh</button>
      </>}
    >
      <p className="setting-note" role="note"><strong>Verification checklist.</strong> The profile menu is open, the username is fully visible, and the Application ID in the screenshot matches the submitted bot/client ID. Special scopes are only for applications you have independently decided to trust.</p>
      {!data?.applications.length && !loading ? <div className="dash-panel settings-panel"><div className="empty-state">No applications have been submitted yet.</div></div> : (
        <div className="developer-review-list">
          {(data?.applications || []).map((application) => (
            <article key={application.id} className={`dash-panel settings-panel developer-review-card is-${application.status}`}>
              <div className="developer-review-layout">
                <div className="developer-review-evidence">
                  {application.screenshot ? <a href={application.screenshot.url} target="_blank" rel="noreferrer"><img src={application.screenshot.url} alt={`Verification screenshot for ${application.name}`} /></a> : <div className="empty-state compact">Screenshot unavailable</div>}
                  <span className="form-hint">Click the screenshot to inspect it at full size.</span>
                </div>
                <div className="developer-review-details">
                  <div className="developer-application-card-head">
                    <div className="developer-application-identity">
                      {application.bot_avatar_url ? <img src={application.bot_avatar_url} alt="" /> : <span className="developer-avatar-fallback">{application.name.slice(0, 1).toUpperCase()}</span>}
                      <div><strong>{application.name}</strong><small>{application.bot_username ? `@${application.bot_username} · ` : ""}{application.bot_user_id}</small></div>
                    </div>
                    <ApplicationStatus status={application.status} />
                  </div>
                  <p>{application.description || "No description provided."}</p>
                  <div className="developer-application-meta">
                    <span>Developer <code>@{application.owner_username || application.owner_id}</code>{application.owner_display_name && application.owner_display_name !== application.owner_username ? ` (${application.owner_display_name})` : ""}</span>
                    <span>{application.shared_guild_count || 0} shared guilds</span>
                    <span>Submitted {when(application.submitted_at)}</span>
                  </div>
                  <div className="developer-application-scope-row">
                    <div><span className="developer-application-label">Requested</span><ScopeChips scopes={application.requested_scopes} /></div>
                    {application.status === "approved" ? <div><span className="developer-application-label">Approved</span><ScopeChips scopes={application.approved_scopes} /></div> : null}
                  </div>
                  {application.status === "pending" ? (
                    <>
                      <Field label="Approved permissions" hint="Only grant the scopes this integration can safely use.">
                        <DeveloperScopePicker scopes={data?.scopes || []} selected={selectedScopes[application.id] || []} onToggle={(scope) => toggleScope(application.id, scope)} />
                      </Field>
                      <Field label="Review note" hint="Included in the review result and shown to the developer.">
                        <textarea value={notes[application.id] || ""} maxLength={2000} placeholder="Optional note for the developer" onChange={(event) => setNotes((current) => ({ ...current, [application.id]: event.target.value }))} />
                      </Field>
                      <div className="developer-application-actions">
                        <button className="button button-primary button-small" onClick={() => decide(application, "approved")} disabled={Boolean(reviewing)}>Approve application</button>
                        <button className="button button-small developer-danger" onClick={() => decide(application, "denied")} disabled={Boolean(reviewing)}>Deny</button>
                      </div>
                    </>
                  ) : application.review_note ? <div className="developer-appeal-note"><span>Review note</span>{application.review_note}</div> : null}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </DeveloperPage>
  );
}
