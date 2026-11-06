import { useCallback, useEffect, useMemo, useState } from "react";
import {
  acceptDeveloperPolicy,
  createDeveloperKey,
  getAuth,
  getDeveloperAccess,
  getDeveloperApplications,
  getDeveloperKeys,
  getDeveloperLogs,
  getDeveloperMe,
  getStaffMe,
  grantDeveloperAccess,
  reviewDeveloperAppeal,
  revokeDeveloperAccess,
  revokeDeveloperKey,
} from "../api";
import { AuthScreen, DiscordSignIn } from "../components/AuthScreen";
import { DashboardShell, type ShellTab } from "../components/dashboard/DashboardShell";
import { StatCard } from "../components/dashboard/DashboardViews";
import { Field } from "../components/dashboard/FormField";
import { SectionTitle } from "../components/dashboard/SectionTitle";
import { Select } from "../components/dashboard/Select";
import { SettingCard, SettingCards } from "../components/dashboard/SettingCards";
import { Switch } from "../components/dashboard/Switch";
import { DeveloperApplicationReviewView, DeveloperApplicationsView } from "../components/developer/DeveloperApplicationsView";
import { DeveloperPage, DeveloperScopePicker, DeveloperScopeSummary } from "../components/developer/DeveloperLayout";
import { Icon } from "../components/Icon";
import { useStrings } from "../i18n";
import { dashboardServersPath, dashboardUserPath, navigate } from "../router";
import type {
  AuthStatus,
  DeveloperAccessList,
  DeveloperApplication,
  DeveloperAppeal,
  DeveloperKey,
  DeveloperMe,
  DeveloperUsageEntry,
} from "../types";
import { notifyError, notifySuccess } from "../utils/toast";

type PortalTab = "overview" | "applications" | "keys" | "logs" | "review" | "access";

const PORTAL_TABS: ShellTab[] = [
  { id: "overview", label: "Overview", icon: "grid" },
  { id: "applications", label: "Applications", icon: "terminal" },
  { id: "keys", label: "API keys", icon: "lock" },
  { id: "logs", label: "Usage logs", icon: "chart" },
];

const OWNER_REVIEW_TAB: ShellTab = { id: "review", label: "Application review", icon: "shield" };
const OWNER_ACCESS_TAB: ShellTab = { id: "access", label: "Access management", icon: "users" };

function tabFromHash(owner: boolean): PortalTab {
  const raw = window.location.hash.replace(/^#/, "").trim() as PortalTab;
  if ((raw === "access" || raw === "review") && !owner) return "overview";
  return ["overview", "applications", "keys", "logs", "review", "access"].includes(raw) ? raw : "overview";
}

function when(timestamp: number | null | undefined) {
  if (!timestamp) return "Never";
  return new Date(timestamp * 1000).toLocaleString();
}

export function DeveloperPortalPage() {
  const { t } = useStrings("dashboard");
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [me, setMe] = useState<DeveloperMe | null>(null);
  // The developer portal renders its own shell, so it has to supply the staff
  // role the sidebar uses to show the staff workspace and mailbox entries.
  const [staffRole, setStaffRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<PortalTab>(() => tabFromHash(false));
  const [policyAgreed, setPolicyAgreed] = useState(false);
  const [policyDismissed, setPolicyDismissed] = useState(false);
  const [acceptingPolicy, setAcceptingPolicy] = useState(false);
  const [keys, setKeys] = useState<DeveloperKey[]>([]);
  const [logs, setLogs] = useState<DeveloperUsageEntry[]>([]);
  const [accessData, setAccessData] = useState<DeveloperAccessList | null>(null);
  const [loadingPanel, setLoadingPanel] = useState(false);
  const [allLogs, setAllLogs] = useState(false);
  const [keyName, setKeyName] = useState("");
  const [keyScopes, setKeyScopes] = useState<string[]>([]);
  const [keyApplicationId, setKeyApplicationId] = useState("");
  const [keyApplications, setKeyApplications] = useState<DeveloperApplication[]>([]);
  const [newSecret, setNewSecret] = useState("");
  const [savingKey, setSavingKey] = useState(false);
  const [confirmRevokeKey, setConfirmRevokeKey] = useState("");
  const [accessUserId, setAccessUserId] = useState("");
  const [accessNotes, setAccessNotes] = useState("");
  const [accessScopes, setAccessScopes] = useState<string[]>([]);
  const [accessEnabled, setAccessEnabled] = useState(true);
  const [savingAccess, setSavingAccess] = useState(false);
  const [confirmRevokeAccess, setConfirmRevokeAccess] = useState("");
  const [accessQuery, setAccessQuery] = useState("");
  const [appealNotes, setAppealNotes] = useState<Record<string, string>>({});
  const [reviewingAppeal, setReviewingAppeal] = useState("");

  const isOwner = Boolean(me?.access.is_owner);
  const tabs = useMemo(
    () => (isOwner ? [...PORTAL_TABS, OWNER_REVIEW_TAB, OWNER_ACCESS_TAB] : PORTAL_TABS),
    [isOwner],
  );

  useEffect(() => {
    let active = true;
    getAuth()
      .then(async (authStatus) => {
        if (!active) return;
        setAuth(authStatus);
        if (!authStatus.authenticated) return;
        const [developer, staffStatus] = await Promise.all([
          getDeveloperMe(),
          getStaffMe().catch(() => null),
        ]);
        if (!active) return;
        setMe(developer);
        setStaffRole(staffStatus?.role || null);
        const nextTab = tabFromHash(developer.access.is_owner);
        setTab(nextTab);
      })
      .catch((reason) => {
        if (active) setError(reason instanceof Error ? reason.message : "The developer portal is unavailable.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    const sync = () => setTab(tabFromHash(Boolean(me?.access.is_owner)));
    window.addEventListener("hashchange", sync);
    return () => window.removeEventListener("hashchange", sync);
  }, [me?.access.is_owner]);

  useEffect(() => {
    if (!me?.access.enabled) return;
    if (!tabs.some((item) => item.id === tab)) {
      setTab("overview");
      return;
    }
    const target = `#${tab}`;
    if (window.location.hash !== target) window.history.replaceState(null, "", target);
  }, [me?.access.enabled, tab, tabs]);

  const loadKeys = useCallback(async () => {
    setLoadingPanel(true);
    try {
      const [result, applications] = await Promise.all([
        getDeveloperKeys(),
        getDeveloperApplications(),
      ]);
      setKeys(result.keys);
      setKeyApplications(applications.applications.filter((application) => application.status === "approved"));
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "API keys could not be loaded.", "developer-keys");
    } finally {
      setLoadingPanel(false);
    }
  }, []);

  const loadLogs = useCallback(async () => {
    setLoadingPanel(true);
    try {
      const result = await getDeveloperLogs(allLogs);
      setLogs(result.entries);
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "Usage logs could not be loaded.", "developer-logs");
    } finally {
      setLoadingPanel(false);
    }
  }, [allLogs]);

  const loadAccess = useCallback(async () => {
    if (!isOwner) return;
    setLoadingPanel(true);
    try {
      setAccessData(await getDeveloperAccess());
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "Developer access could not be loaded.", "developer-access");
    } finally {
      setLoadingPanel(false);
    }
  }, [isOwner]);

  useEffect(() => {
    if (!me?.access.enabled) return;
    if (tab === "keys") void loadKeys();
    if (tab === "logs") void loadLogs();
    if (tab === "access") void loadAccess();
  }, [tab, me?.access.enabled, loadKeys, loadLogs, loadAccess]);

  useEffect(() => {
    if (!me) return;
    const application = keyApplications.find((item) => item.id === keyApplicationId);
    const allowed = application
      ? application.approved_scopes.filter((scope) => me.access.scopes.includes(scope))
      : me.access.scopes.filter((scope) => !scope.startsWith("warns:") && !["blacklist:read", "blacklist:write", "guilds:cross_server"].includes(scope));
    setKeyScopes((current) => current.filter((scope) => allowed.includes(scope)));
  }, [me?.access.scopes.join(","), keyApplicationId, keyApplications]);

  const changeTab = (next: string) => {
    setTab(next as PortalTab);
    setNewSecret("");
  };

  const acceptPolicy = async () => {
    if (!policyAgreed || !auth?.csrf_token || acceptingPolicy) return;
    setAcceptingPolicy(true);
    try {
      const result = await acceptDeveloperPolicy(auth.csrf_token);
      setMe((current) => current ? { ...current, access: result.access } : current);
      setPolicyDismissed(true);
      notifySuccess("Developer guidelines accepted.", "developer-policy");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The guidelines could not be saved.", "developer-policy");
    } finally {
      setAcceptingPolicy(false);
    }
  };

  const createKey = async () => {
    if (!auth?.csrf_token || savingKey) return;
    if (!me?.access.policy_accepted) {
      notifyError("Accept the developer guidelines before creating a key.", "developer-key");
      return;
    }
    setSavingKey(true);
    try {
      const result = await createDeveloperKey(keyName, keyScopes, auth.csrf_token, keyApplicationId || undefined);
      setNewSecret(result.secret);
      setKeys((current) => [result.key, ...current]);
      setKeyName("");
      setKeyScopes([]);
      setKeyApplicationId("");
      setMe((current) => current ? { ...current, key_count: current.key_count + 1 } : current);
      notifySuccess("API key created. Copy it now; it will not be shown again.", "developer-key");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The API key could not be created.", "developer-key");
    } finally {
      setSavingKey(false);
    }
  };

  const copySecret = async () => {
    try {
      await navigator.clipboard.writeText(newSecret);
      notifySuccess("API key copied.", "developer-key");
    } catch {
      notifyError("The browser blocked clipboard access. Select the key and copy it manually.", "developer-key");
    }
  };

  const revokeKey = async (keyId: string) => {
    if (!auth?.csrf_token) return;
    try {
      await revokeDeveloperKey(keyId, auth.csrf_token);
      setKeys((current) => current.map((key) => key.id === keyId ? { ...key, revoked_at: Date.now() / 1000 } : key));
      setMe((current) => current ? { ...current, key_count: Math.max(0, current.key_count - 1) } : current);
      setConfirmRevokeKey("");
      notifySuccess("API key revoked.", "developer-key");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The key could not be revoked.", "developer-key");
    }
  };

  const editAccess = (row: DeveloperAccessList["developers"][number]) => {
    setAccessUserId(row.user_id);
    setAccessNotes(row.notes || "");
    setAccessScopes(row.scopes);
    setAccessEnabled(row.enabled);
    setConfirmRevokeAccess("");
  };

  const saveAccess = async () => {
    if (!auth?.csrf_token || savingAccess) return;
    if (!/^\d{1,22}$/.test(accessUserId.trim())) {
      notifyError("Enter a valid Discord user ID.", "developer-access");
      return;
    }
    setSavingAccess(true);
    try {
      await grantDeveloperAccess(accessUserId.trim(), {
        scopes: accessScopes,
        enabled: accessEnabled,
        notes: accessNotes,
      }, auth.csrf_token);
      notifySuccess("Developer access saved.", "developer-access");
      setAccessUserId("");
      setAccessNotes("");
      setAccessScopes([]);
      setAccessEnabled(true);
      await loadAccess();
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "Developer access could not be saved.", "developer-access");
    } finally {
      setSavingAccess(false);
    }
  };

  const removeAccess = async (userId: string) => {
    if (!auth?.csrf_token) return;
    try {
      await revokeDeveloperAccess(userId, auth.csrf_token);
      setConfirmRevokeAccess("");
      setAccessUserId("");
      notifySuccess("Developer access revoked.", "developer-access");
      await loadAccess();
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "Access could not be revoked.", "developer-access");
    }
  };

  const reviewAppeal = async (appeal: DeveloperAppeal, status: "approved" | "denied") => {
    if (!auth?.csrf_token || reviewingAppeal) return;
    setReviewingAppeal(appeal.id);
    try {
      await reviewDeveloperAppeal(appeal.id, status, appealNotes[appeal.id] || "", auth.csrf_token);
      notifySuccess(
        status === "approved" ? "Appeal approved; access restored." : "Appeal denied; suspension remains.",
        "developer-appeals",
      );
      setAppealNotes((current) => ({ ...current, [appeal.id]: "" }));
      await loadAccess();
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The appeal decision could not be saved.", "developer-appeals");
    } finally {
      setReviewingAppeal("");
    }
  };

  const shell = (content: React.ReactNode, activeTab: PortalTab = tab) => (
    <DashboardShell
      user={auth!.user!}
      guilds={[]}
      selectedGuild={null}
      view="overview"
      section="overview"
      userTab="overview"
      stats={null}
      onHome={() => navigate(dashboardUserPath("overview"))}
      onServers={() => navigate(dashboardServersPath())}
      onGuildChange={() => navigate(dashboardUserPath("overview"))}
      onSectionChange={() => navigate(dashboardUserPath("overview"))}
      onUserTabChange={() => navigate(dashboardUserPath("overview"))}
      onRefresh={() => window.location.reload()}
      refreshing={false}
      staffRole={staffRole}
      developerAccess
      developerTabs={tabs}
      activeDeveloperTab={activeTab}
      onDeveloperTabChange={changeTab}
    >
      {content}
    </DashboardShell>
  );

  if (loading) return <div className="dashboard-state"><div className="loading-ring" /><p>Opening the developer portal…</p></div>;
  if (!auth) return <div className="dashboard-state"><div className="loading-ring" /><p>{t("auth.connecting")}</p></div>;
  if (!auth.authenticated) {
    return <AuthScreen
      eyebrow="Developer portal"
      title={<>Build with <em>Niko.</em></>}
      description="Sign in with Discord to open your developer workspace."
      back={{ label: t("auth.back"), onClick: () => navigate("/") }}
    >
      <DiscordSignIn next="/dashboard/developer" available={auth.oauth_available} />
    </AuthScreen>;
  }
  if (error) {
    return <AuthScreen
      mark="!"
      eyebrow="Developer portal"
      title={<>Portal <em>unavailable.</em></>}
      description={error}
      back={{ label: t("auth.back"), onClick: () => navigate("/dashboard") }}
    >
      <button className="button button-primary full-width" onClick={() => window.location.reload()}>Try again</button>
    </AuthScreen>;
  }
  if (me?.access.suspended) {
    const suspension = me.suspension || me.access.suspension;
    const appeal = me.appeal || me.access.appeal;
    return shell(
      <DeveloperPage
        eyebrow="Developer API · access limited"
        title="API access is suspended."
        text="Automated abuse protection paused this account. All API keys belonging to it have been revoked, and key management is locked until an appeal is approved."
        actions={<>
          <a className="button button-primary" href="/discord">Open a support ticket <Icon name="arrow" /></a>
          <a className="button button-muted" href="/developers/rate-limits">Read the rate-limit guide</a>
          <a className="button button-muted" href="/developers/policies">Developer policies</a>
        </>}
      >
        <section className="dash-panel settings-panel">
          <SectionTitle label="Account status" title="Access paused" detail="The facts behind this restriction and the current appeal state." icon="shield" />
          <div className="developer-suspension-facts">
            <div><span>Reason</span><strong>{suspension?.reason || "Automated abuse detection"}</strong></div>
            <div><span>Suspended</span><strong>{when(suspension?.at)}</strong></div>
            <div><span>Appeal</span><strong>{appeal ? appeal.status[0].toUpperCase() + appeal.status.slice(1) : "Not submitted"}</strong></div>
          </div>
          {appeal?.status === "pending" ? (
            <p className="setting-note" role="status"><strong>Your appeal is under review.</strong> Staff will send the decision in the same Discord DM that carried the appeal button. Keep that DM available.</p>
          ) : appeal?.status === "denied" ? (
            <p className="setting-note" role="status"><strong>Your appeal was denied.</strong> {appeal.note || "The decision was sent to your DMs. Open a support ticket if you need clarification."}</p>
          ) : (
            <p className="setting-note" role="status"><strong>Appeal from your DMs.</strong> Niko sent this account a DM with a persistent <strong>Submit an appeal</strong> button. If you cannot find it, open a support ticket.</p>
          )}
        </section>
      </DeveloperPage>,
    );
  }
  if (!me?.access.enabled) {
    return <AuthScreen
      eyebrow="Developer access"
      title={<>Access is <em>invite-only.</em></>}
      description="Developer API access is granted through a support ticket. Join the Niko support server and open a ticket to tell us what you are building."
      back={{ label: "Return to dashboard", onClick: () => navigate(dashboardUserPath("overview")) }}
    >
      <div className="developer-access-actions">
        <a className="button button-primary full-width" href="/discord">Join the support server <Icon name="arrow" /></a>
        <a className="button button-muted full-width" href="/developers">Read the developer docs</a>
      </div>
    </AuthScreen>;
  }

  const selectedKeyApplication = keyApplications.find((application) => application.id === keyApplicationId);
  const availableKeyScopes = selectedKeyApplication
    ? me.scopes.filter((scope) => me.access.scopes.includes(scope.key) && selectedKeyApplication.approved_scopes.includes(scope.key))
    : me.scopes.filter((scope) => me.access.scopes.includes(scope.key) && !scope.restricted && !scope.key.startsWith("warns:"));

  const policyOpen = !me.access.policy_accepted && !policyDismissed;
  const policyModal = policyOpen ? (
    <div className="developer-policy-backdrop">
      <section className="developer-policy-modal" role="dialog" aria-modal="true" aria-labelledby="developer-policy-title">
        <span className="developer-policy-kicker">Before your first key</span>
        <h2 id="developer-policy-title">Read the developer guidelines</h2>
        <p>API access is a responsibility. The full developer policies live in the developer documentation, beside the endpoint reference.</p>
        <ul>
          <li>Only request the scopes your integration actually needs.</li>
          <li>Never expose API keys, user IDs, or blacklist data in client-side code or public logs.</li>
          <li>Respect Discord's terms, server privacy choices, and user data-removal requests.</li>
          <li>Do not scrape, resell, or redistribute Niko data outside the approved integration.</li>
          <li>Report a leaked key or unexpected data exposure through the support server immediately.</li>
        </ul>
        <a className="developer-policy-link" href="/developers/policies" target="_blank" rel="noreferrer">Read the full developer policies <Icon name="external" size={14} /></a>
        <label className="developer-policy-agree">
          <input type="checkbox" checked={policyAgreed} onChange={(event) => setPolicyAgreed(event.target.checked)} />
          <span>I have read and agree to follow the developer policies and guidelines.</span>
        </label>
        <div className="developer-policy-actions">
          <button className="button button-primary" onClick={acceptPolicy} disabled={!policyAgreed || acceptingPolicy}>
            {acceptingPolicy ? "Saving…" : "Agree and continue"}
          </button>
          <button className="button button-muted" onClick={() => setPolicyDismissed(true)}>Review later</button>
        </div>
      </section>
    </div>
  ) : null;

  const overview = (
    <DeveloperPage
      eyebrow="Developer portal"
      title="Build with Niko."
      text="A small, scoped API for integrations that need leaderboard, leveling, economy, or moderation context. Register a bot application to receive warning events instead of polling."
      actions={<>
        <button className="button button-primary" onClick={() => changeTab("applications")}>Register a bot application <Icon name="arrow" /></button>
        <a className="button button-muted" href="/developers">Developer documentation <Icon name="external" /></a>
        <button className="button button-muted" onClick={() => changeTab("keys")}>Create an API key</button>
      </>}
    >
      <div className="dash-stats developer-overview-stats">
        <StatCard label="Access" value="Approved" note={me.access.is_owner ? "Bot owner · full scope" : "Granted by the Niko owner"} />
        <StatCard label="Active keys" value={String(me.key_count)} note="Secrets are shown once" />
        <StatCard label="Policy" value={me.access.policy_accepted ? "Accepted" : "Action needed"} note={`Version ${me.policy_version} · ${me.policy_updated}`} />
      </div>

      <section className="dash-panel settings-panel">
        <SectionTitle label="Your permissions" title="Granted scopes" detail="Every permission this developer account can use across its keys and applications." icon="lock" />
        <DeveloperScopeSummary scopes={me.scopes.filter((scope) => me.access.scopes.includes(scope.key))} />
      </section>

      <section className="dash-panel settings-panel developer-quickstart">
        <SectionTitle label="Quick start" title="Your first request" detail="Send the key as a bearer token against the website API base URL." icon="terminal" />
        <p>Send the key as a bearer token. The base URL is <code>/api/v1</code> on the website; an API subdomain omits the <code>/api</code> prefix.</p>
        <pre><code>{`curl https://niko.sryze.cc/api/v1/economy/leaderboard \
  -H "Authorization: Bearer niko_dev_..."`}</code></pre>
      </section>
    </DeveloperPage>
  );

  const keyApplicationOptions = [
    { value: "", label: "Generic key (no application)" },
    ...keyApplications.map((application) => ({ value: application.id, label: `${application.name} · ${application.bot_user_id}` })),
  ];

  const keysPanel = (
    <DeveloperPage
      eyebrow="Credentials"
      title="API keys"
      text="Each key carries a subset of your approved permissions. Bind it to an approved application for warn sync and webhook delivery."
      actions={<a className="button button-muted button-small" href="/developers/authentication">Key safety <Icon name="external" /></a>}
    >
      {!me.access.policy_accepted && (
        <div className="notice warning" role="status">
          <strong>Accept the guidelines first.</strong> Key creation is locked until you agree to the developer policies.{" "}
          <button className="developer-inline-button" onClick={() => setPolicyDismissed(false)}>Open the agreement</button>
        </div>
      )}

      {newSecret && (
        <section className="dash-panel settings-panel developer-secret">
          <SectionTitle label="Copy this now" title="Your new API key" detail="This secret is shown once. Store it in a password manager or the environment of the service that will use it." icon="lock" />
          <div className="developer-secret-value"><code>{newSecret}</code><button className="button button-small button-primary" onClick={copySecret}><Icon name="copy" /> Copy</button></div>
          <button className="developer-inline-button" onClick={() => setNewSecret("")}>I have stored it</button>
        </section>
      )}

      <section className="dash-panel settings-panel">
        <SectionTitle label="New credential" title="Create a key" detail="Name the integration and choose the exact permissions it needs." icon="plus" />
        <div className="form-grid">
          <Field label="Key name" hint="Use a name that identifies the service holding this key."><input value={keyName} maxLength={60} placeholder="My leveling bridge" onChange={(event) => setKeyName(event.target.value)} /></Field>
          <Field label="Application" hint="App-bound keys are limited to the application's approved permissions and guilds shared with its bot.">
            <Select options={keyApplicationOptions} value={keyApplicationId} placeholder="Generic key (no application)" onChange={setKeyApplicationId} />
          </Field>
        </div>
        <div className="developer-field-wide">
          <Field label="Permissions" hint="Only request the scopes this key actually needs.">
            <DeveloperScopePicker scopes={availableKeyScopes} selected={keyScopes} onToggle={(scope) => setKeyScopes((current) => current.includes(scope) ? current.filter((item) => item !== scope) : [...current, scope])} disabled={!me.access.policy_accepted} />
          </Field>
        </div>
        <div className="setting-footer">
          <span role="status">Secrets are shown once. Revoking a key takes effect immediately.</span>
          <button className="button button-primary" onClick={createKey} disabled={savingKey || !me.access.policy_accepted || !keyName.trim() || keyScopes.length === 0}>
            {savingKey ? "Creating…" : "Create API key"}
          </button>
        </div>
      </section>

      <section className="dash-panel settings-panel">
        <SectionTitle label="Your keys" title={`${keys.filter((key) => !key.revoked_at).length} active`} detail="Keys are bound to the permissions they were created with." icon="lock" action={<button className="button button-muted button-small" onClick={loadKeys} disabled={loadingPanel}><Icon name="refresh" /> Refresh</button>} />
        {loadingPanel && keys.length === 0 ? <div className="empty-state">Loading keys…</div> : keys.length === 0 ? <div className="empty-state">No API keys yet.</div> : (
          <div className="developer-key-list">
            {keys.map((key) => (
              <article key={key.id} className={`developer-key-row${key.revoked_at ? " is-revoked" : ""}`}>
                <div className="developer-key-main">
                  <div><strong>{key.name}</strong><code>{key.prefix}…</code></div>
                  <div className="developer-key-meta"><span>Created {when(key.created_at)}</span><span>Last used {when(key.last_used_at)}</span>{key.application_id ? <span>App {keyApplications.find((application) => application.id === key.application_id)?.name || key.application_id}</span> : <span>Generic key</span>}{key.revoked_at ? <span className="developer-key-revoked">Revoked</span> : null}</div>
                  <div className="developer-key-scopes">{key.scopes.map((scope) => <code key={scope}>{scope}</code>)}</div>
                </div>
                {!key.revoked_at && (confirmRevokeKey === key.id ? (
                  <div className="developer-confirm"><span>Revoke this key?</span><button className="button button-small developer-danger" onClick={() => revokeKey(key.id)}>Revoke</button><button className="button button-small button-muted" onClick={() => setConfirmRevokeKey("")}>Cancel</button></div>
                ) : <button className="button button-small button-muted" onClick={() => setConfirmRevokeKey(key.id)}>Revoke</button>)}
              </article>
            ))}
          </div>
        )}
      </section>
    </DeveloperPage>
  );

  const logsPanel = (
    <DeveloperPage
      eyebrow="Observability"
      title="API usage logs"
      text="Every keyed request is recorded with its scope, response status, and latency. Secrets and query strings are never logged."
      actions={<button className="button button-muted button-small" onClick={loadLogs} disabled={loadingPanel}><Icon name="refresh" /> Refresh</button>}
    >
      <section className="dash-panel settings-panel">
        <SectionTitle label="Request history" title="Recent API activity" detail="A live record of authenticated requests, newest first." icon="chart" />
        {me.access.is_owner && (
          <SettingCards className="developer-log-filter">
            <SettingCard title="All developers" hint="Include requests from every developer account, not just yours." action={<Switch checked={allLogs} onCheckedChange={setAllLogs} aria-label="Show all developer requests" />} />
          </SettingCards>
        )}
        {loadingPanel && logs.length === 0 ? <div className="empty-state">Loading usage…</div> : logs.length === 0 ? <div className="empty-state">No API requests have been logged yet.</div> : (
          <div className="developer-table-wrap">
            <table className="developer-table">
              <thead><tr><th>Time</th><th>Key</th><th>Request</th><th>Scope</th><th>Status</th><th>Latency</th>{allLogs ? <th>Developer</th> : null}</tr></thead>
              <tbody>{logs.map((entry) => (
                <tr key={entry.id}>
                  <td data-label="Time">{when(entry.at)}</td>
                  <td data-label="Key"><strong>{entry.key_name}</strong><code>{entry.key_prefix}…</code></td>
                  <td data-label="Request"><code>{entry.method} {entry.path.replace(/^\/api/, "")}</code></td>
                  <td data-label="Scope"><code>{entry.scope || "—"}</code></td>
                  <td data-label="Status"><span className={`developer-status${entry.status >= 400 ? " is-error" : ""}`}>{entry.status}</span></td>
                  <td data-label="Latency">{entry.latency_ms} ms</td>
                  {allLogs ? <td data-label="Developer"><code>{entry.user_id}</code></td> : null}
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </section>
    </DeveloperPage>
  );

  const filteredDevelopers = (accessData?.developers || []).filter((row) => {
    const query = accessQuery.trim().toLowerCase();
    if (!query) return true;
    return `${row.user_id} ${row.username} ${row.display_name} ${row.notes}`.toLowerCase().includes(query);
  });
  const appeals = accessData?.appeals || [];
  const pendingAppeals = appeals.filter((appeal) => appeal.status === "pending");
  const appealDeveloper = (userId?: string) => accessData?.developers.find((row) => row.user_id === userId);

  const accessPanel = (
    <DeveloperPage
      eyebrow="Owner only"
      title="Access management"
      text="Grant a developer access, choose the scopes they may use, and revoke everything in one place."
      actions={<button className="button button-muted button-small" onClick={loadAccess} disabled={loadingPanel}><Icon name="refresh" /> Refresh</button>}
    >
      <section className="dash-panel settings-panel">
        <SectionTitle label="Grant or edit" title="Developer access" detail="Enter a Discord user ID, set their permissions, and choose whether the account is active." icon="users" />
        <div className="form-grid">
          <Field label="Discord user ID" hint="The account must be reachable by Niko before it can use a key."><input value={accessUserId} inputMode="numeric" placeholder="1052690741874401360" onChange={(event) => setAccessUserId(event.target.value.replace(/\D/g, ""))} /></Field>
          <Field label="Internal note" hint="Visible only to owners in this roster."><input value={accessNotes} maxLength={1000} placeholder="What are they building?" onChange={(event) => setAccessNotes(event.target.value)} /></Field>
        </div>
        <div className="developer-field-wide">
          <Field label="Approved permissions" hint="These permissions are available to every key this developer creates.">
            <DeveloperScopePicker scopes={accessData?.scopes || me.scopes} selected={accessScopes} onToggle={(scope) => setAccessScopes((current) => current.includes(scope) ? current.filter((item) => item !== scope) : [...current, scope])} />
          </Field>
        </div>
        <SettingCards>
          <SettingCard title="Access enabled" hint="Disabled developers keep their history but cannot authenticate with a key." action={<Switch checked={accessEnabled} onCheckedChange={setAccessEnabled} aria-label="Developer access enabled" />} />
        </SettingCards>
        <div className="setting-footer">
          <span role="status">Saving replaces the permissions and status for this developer.</span>
          <button className="button button-primary" onClick={saveAccess} disabled={savingAccess || !accessUserId.trim()}>{savingAccess ? "Saving…" : accessUserId && accessData?.developers.some((row) => row.user_id === accessUserId) ? "Save changes" : "Grant access"}</button>
        </div>
      </section>

      <section className="dash-panel settings-panel">
        <SectionTitle label="Owner review" title="Suspension appeals" detail="Review the developer's explanation before restoring or denying API access." icon="shield" action={<span className="developer-status">{pendingAppeals.length} pending</span>} />
        {appeals.length === 0 ? <div className="empty-state">No suspension appeals have been submitted.</div> : (
          <div className="developer-appeal-list">
            {appeals.map((appeal) => {
              const developer = appealDeveloper(appeal.user_id);
              const name = developer?.display_name || developer?.username || appeal.user_id || "Developer";
              return (
                <article key={appeal.id} className={`developer-appeal-card is-${appeal.status}`}>
                  <div className="developer-appeal-head">
                    <div><strong>{name}</strong><small>{appeal.user_id} · {when(appeal.created_at)}</small></div>
                    <span className={`developer-status${appeal.status === "denied" ? " is-off" : ""}`}>{appeal.status}</span>
                  </div>
                  <p>{appeal.text}</p>
                  {appeal.note ? <div className="developer-appeal-note"><span>Staff note</span>{appeal.note}</div> : null}
                  {appeal.status === "pending" ? (
                    <div className="developer-appeal-review">
                      <Field label="Decision note" hint="Optional note included in the decision DM.">
                        <textarea
                          value={appealNotes[appeal.id] || ""}
                          maxLength={2000}
                          placeholder="Optional note included in the decision DM"
                          onChange={(event) => setAppealNotes((current) => ({ ...current, [appeal.id]: event.target.value }))}
                        />
                      </Field>
                      <div className="developer-appeal-actions">
                        <button className="button button-primary button-small" onClick={() => reviewAppeal(appeal, "approved")} disabled={Boolean(reviewingAppeal)}>Approve and restore</button>
                        <button className="button button-small developer-danger" onClick={() => reviewAppeal(appeal, "denied")} disabled={Boolean(reviewingAppeal)}>Deny appeal</button>
                      </div>
                    </div>
                  ) : null}
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="dash-panel settings-panel">
        <SectionTitle label="Approved developers" title={`${accessData?.developers.filter((row) => row.enabled).length || 0} active`} detail="Everyone who can currently authenticate with the Developer API." icon="users" />
        <div className="developer-search-field">
          <Field label="Search developers"><div className="developer-search"><Icon name="search" size={14} /><input value={accessQuery} placeholder="Search by name, ID, or note" onChange={(event) => setAccessQuery(event.target.value)} /></div></Field>
        </div>
        {(accessData?.owners || []).map((owner) => (
          <article key={owner.user_id} className="developer-access-row is-owner">
            <div><strong>{owner.user_id}</strong><span>{owner.notes}</span></div>
            <div className="developer-key-scopes">{owner.scopes.map((scope) => <code key={scope}>{scope}</code>)}</div>
            <span className="developer-status">Owner</span>
          </article>
        ))}
        {loadingPanel && !accessData ? <div className="empty-state">Loading access roster…</div> : filteredDevelopers.length === 0 ? <div className="empty-state">No developers have been granted access yet.</div> : filteredDevelopers.map((row) => (
          <article key={row.user_id} className={`developer-access-row${row.enabled ? "" : " is-disabled"}`}>
            <div className="developer-access-identity">
              {row.avatar_url ? <img src={row.avatar_url} alt="" /> : <span className="developer-avatar-fallback">{(row.display_name || row.username || row.user_id).slice(0, 1).toUpperCase()}</span>}
              <span><strong>{row.display_name || row.username || row.user_id}</strong><small>{row.user_id} · {row.key_count} key{row.key_count === 1 ? "" : "s"} · Last used {when(row.last_used_at)}</small>{row.notes ? <em>{row.notes}</em> : null}</span>
            </div>
            <div className="developer-key-scopes">{row.scopes.map((scope) => <code key={scope}>{scope}</code>)}</div>
            <span className={`developer-status${row.enabled ? "" : " is-off"}`}>{row.enabled ? "Active" : "Disabled"}</span>
            <div className="developer-access-actions">
              <button className="button button-small button-muted" onClick={() => editAccess(row)}>Edit</button>
              {confirmRevokeAccess === row.user_id ? <>
                <button className="button button-small developer-danger" onClick={() => removeAccess(row.user_id)}>Confirm revoke</button>
                <button className="button button-small button-muted" onClick={() => setConfirmRevokeAccess("")}>Cancel</button>
              </> : <button className="button button-small button-muted" onClick={() => setConfirmRevokeAccess(row.user_id)}>Revoke</button>}
            </div>
          </article>
        ))}
      </section>
    </DeveloperPage>
  );

  const content = tab === "applications"
    ? <DeveloperApplicationsView auth={auth} me={me} />
    : tab === "review"
      ? <DeveloperApplicationReviewView auth={auth} />
      : tab === "keys"
        ? keysPanel
        : tab === "logs"
          ? logsPanel
          : tab === "access"
            ? accessPanel
            : overview;
  return <>{shell(content)}{policyModal}</>;
}
