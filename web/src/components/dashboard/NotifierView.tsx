import { useCallback, useEffect, useState, type FormEvent, type ReactNode } from "react";
import {
  addNotifierFollow,
  getGuildNotifier,
  removeNotifierFollow,
  saveNotifierConfig,
  testNotifierFollow,
  updateNotifierFollow,
} from "../../api";
import { Icon } from "../Icon";
import { RoleSelect } from "./RoleSelect";
import type { GuildResources, NotifierFollow, NotifierResponse } from "../../types";
import { DashHeading } from "./DashboardViews";

type Props = { guildId: string; resources: GuildResources | null; csrfToken?: string };
type Status = { notice: string; error: string };
type Draft = { channel_id: string; ping_role_id: string; template: string };

const initialStatus: Status = { notice: "", error: "" };

// Scoped to this view so a follow row reads clearly without adding global CSS.
const notifierStyles = `
.notifier-follow-card{display:grid;gap:12px;padding:14px 16px;background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:10px}
.notifier-follow-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.notifier-follow-head h3{margin:3px 0 2px;font-size:14px;letter-spacing:-.02em}
.notifier-follow-head small{color:var(--dim);font:8px "Space Mono",monospace;letter-spacing:.04em;word-break:break-all}
.notifier-follow-badges{display:flex;flex:0 0 auto;flex-wrap:wrap;justify-content:flex-end;gap:6px}
.notifier-badge{padding:3px 7px;border:1px solid currentColor;border-radius:999px;font:700 8px "Space Mono",monospace;letter-spacing:.08em;text-transform:uppercase}
.notifier-badge.is-active{color:var(--sage)}
.notifier-badge.is-paused{color:var(--muted)}
.notifier-badge.is-warning{color:#c9762e}
.notifier-follow-actions{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px}
.notifier-list{display:grid;gap:10px;margin-top:4px}
`;

function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return <label className="form-field"><span className="form-label">{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

function SectionTitle({ label, title, detail, icon }: { label: string; title: string; detail: string; icon: string }) {
  return <div className="panel-heading settings-section-title">
    <div><span className="panel-kicker">{label}</span><h3>{title}</h3><p>{detail}</p></div>
    <span className="panel-icon"><Icon name={icon} /></span>
  </div>;
}

function followKey(follow: NotifierFollow) {
  return `${follow.platform}:${follow.username}`;
}

function draftFor(follow: NotifierFollow): Draft {
  return {
    channel_id: follow.channel_id || "",
    ping_role_id: follow.ping_role_id || "",
    template: follow.template || "",
  };
}

function draftMap(follows: NotifierFollow[]): Record<string, Draft> {
  const next: Record<string, Draft> = {};
  for (const follow of follows) next[followKey(follow)] = draftFor(follow);
  return next;
}

function formatChecked(value: string | null) {
  if (!value) return "Never checked yet";
  // The API writes UTC timestamps; an unparseable legacy value is shown as-is
  // rather than as “Invalid Date”.
  const parsed = new Date(value.includes("T") ? value : `${value.replace(" ", "T")}Z`);
  return Number.isNaN(parsed.getTime()) ? value : `Last checked ${parsed.toLocaleString()}`;
}

function channelLabel(resources: GuildResources | null, id: string | null) {
  if (!id) return "No channel";
  return resources?.channels.find((channel) => String(channel.id) === String(id))?.name || `Saved channel · ${id}`;
}

/** Keep a saved channel selectable even when the bot cannot list it any more. */
function channelsWithSelected(resources: GuildResources | null, selected: string) {
  const channels = resources?.channels || [];
  if (!selected || channels.some((channel) => String(channel.id) === selected)) return channels;
  return [{ id: selected, name: `Saved channel · ${selected}` }, ...channels];
}

// A pasted profile URL almost always names its platform. This only pre-fills
// the picker: the server validates the account against the real platform API,
// so a wrong guess costs one click and can never store a bad follow.
const DETECTORS: [RegExp, string][] = [
  [/(?:^|[/.])(?:youtube\.com|youtu\.be)\//, "youtube"],
  [/(?:^|[/.])twitch\.tv\//, "twitch"],
  [/(?:^|[/.])(?:x\.com|twitter\.com)\//, "twitter"],
  [/(?:^|[/.])tiktok\.com\//, "tiktok"],
  [/(?:^|[/.])bsky\.app\/|\.bsky\.social(?:$|\/)/, "bluesky"],
  [/(?:^|[/.])reddit\.com\/r\//, "reddit"],
];

function detectPlatform(value: string) {
  const lowered = value.trim().toLowerCase();
  if (!lowered) return "";
  if (lowered.startsWith("r/")) return "reddit";
  for (const [pattern, platform] of DETECTORS) {
    if (pattern.test(lowered)) return platform;
  }
  return "";
}

export function NotifierView({ guildId, resources, csrfToken }: Props) {
  const [data, setData] = useState<NotifierResponse | null>(null);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [status, setStatus] = useState<Status>(initialStatus);
  const [savingConfig, setSavingConfig] = useState(false);
  const [adding, setAdding] = useState(false);
  const [busyFollow, setBusyFollow] = useState("");
  const [confirmRemove, setConfirmRemove] = useState("");
  const [configDraft, setConfigDraft] = useState({ enabled: true, default_channel_id: "", ping_role_id: "" });
  const [form, setForm] = useState({ platform: "", query: "", channel_id: "", ping_role_id: "", template: "" });
  const [manualPlatform, setManualPlatform] = useState(false);

  const load = useCallback(() => getGuildNotifier(guildId).then((response) => {
    setData(response);
    setDrafts(draftMap(response.follows));
    setConfigDraft({
      enabled: response.config.enabled,
      default_channel_id: response.config.default_channel_id || "",
      ping_role_id: response.config.ping_role_id || "",
    });
    setForm((current) => ({
      ...current,
      channel_id: current.channel_id || response.config.default_channel_id || "",
      ping_role_id: current.ping_role_id || response.config.ping_role_id || "",
    }));
  }), [guildId]);

  useEffect(() => {
    let active = true;
    setLoading(true); setLoadError(""); setStatus(initialStatus);
    load()
      .catch((reason) => { if (active) setLoadError(reason instanceof Error ? reason.message : "Social notifications could not be loaded."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [load]);

  useEffect(() => {
    if (!confirmRemove) return;
    const timer = window.setTimeout(() => setConfirmRemove(""), 6000);
    return () => window.clearTimeout(timer);
  }, [confirmRemove]);

  if (loading) return <div className="section-loading" role="status">Loading social notifications…</div>;
  if (loadError || !data) return <div className="inline-error" role="alert">
    <strong>Couldn’t load social notifications.</strong>
    <span>{loadError || "This server has no notification data yet."}</span>
    <button className="button button-muted" onClick={() => { setLoadError(""); setLoading(true); load().catch((reason) => setLoadError(reason instanceof Error ? reason.message : "Social notifications could not be loaded.")).finally(() => setLoading(false)); }}>Try again</button>
  </div>;

  const platforms = data.platforms;
  const platformLabel = (id: string) => platforms.find((platform) => platform.id === id)?.label || id;
  const platformFor = (id: string) => platforms.find((platform) => platform.id === id);
  const countFor = (id: string) => data.follows.filter((follow) => follow.platform === id).length;
  const atGuildLimit = data.follows.length >= data.limits.max_follows;
  const atPlatformLimit = Boolean(form.platform) && countFor(form.platform) >= data.limits.max_follows_per_platform;
  const addBlocked = atGuildLimit || atPlatformLimit || platforms.length === 0;
  const blockedReason = atGuildLimit
    ? `This server already follows ${data.limits.max_follows} accounts. Remove one before adding another.`
    : atPlatformLimit
      ? `This server already follows ${data.limits.max_follows_per_platform} ${platformLabel(form.platform)} accounts. Remove one before adding another.`
      : platforms.length === 0
        ? "The notifier platforms are unavailable right now. Reload the dashboard in a moment."
        : "";

  const applyFollow = (follow: NotifierFollow) => {
    setData((current) => current && ({
      ...current,
      follows: current.follows.some((item) => followKey(item) === followKey(follow))
        ? current.follows.map((item) => followKey(item) === followKey(follow) ? follow : item)
        : [...current.follows, follow],
    }));
    setDrafts((current) => ({ ...current, [followKey(follow)]: draftFor(follow) }));
  };

  const saveServerSettings = (event: FormEvent) => {
    event.preventDefault();
    setSavingConfig(true); setStatus(initialStatus);
    saveNotifierConfig(guildId, {
      enabled: configDraft.enabled,
      default_channel_id: configDraft.default_channel_id,
      ping_role_id: configDraft.ping_role_id,
    }, csrfToken)
      .then((result) => {
        setData((current) => current && ({ ...current, config: result.config }));
        setStatus({ notice: "Notification settings saved for this server.", error: "" });
      })
      .catch((reason) => setStatus({ notice: "", error: reason instanceof Error ? reason.message : "Notification settings could not be saved." }))
      .finally(() => setSavingConfig(false));
  };

  const submitAdd = (event: FormEvent) => {
    event.preventDefault();
    if (addBlocked) { setStatus({ notice: "", error: blockedReason }); return; }
    if (!form.platform) { setStatus({ notice: "", error: "Pick the platform you want to follow." }); return; }
    if (!form.channel_id) { setStatus({ notice: "", error: "Pick the channel announcements should go to." }); return; }
    setAdding(true); setStatus(initialStatus);
    addNotifierFollow(guildId, {
      platform: form.platform,
      query: form.query,
      channel_id: form.channel_id,
      ping_role_id: form.ping_role_id,
      template: form.template,
    }, csrfToken)
      .then((result) => {
        applyFollow(result.follow);
        setForm((current) => ({ ...current, query: "", template: "" }));
        setManualPlatform(false);
        setStatus({ notice: result.created ? "Account added. New posts will be announced now." : "That account was already followed, so its settings were updated.", error: "" });
      })
      .catch((reason) => setStatus({ notice: "", error: reason instanceof Error ? reason.message : "That account could not be added." }))
      .finally(() => setAdding(false));
  };

  const saveFollow = (follow: NotifierFollow) => {
    const draft = drafts[followKey(follow)] || draftFor(follow);
    if (!draft.channel_id) { setStatus({ notice: "", error: "Pick a channel for that account." }); return; }
    // Only send what actually changed, so two people editing different fields
    // of the same account never overwrite each other.
    const body: { platform: string; username: string; channel_id?: string; ping_role_id?: string; template?: string } = {
      platform: follow.platform,
      username: follow.username,
    };
    if (draft.channel_id !== (follow.channel_id || "")) body.channel_id = draft.channel_id;
    if (draft.ping_role_id !== (follow.ping_role_id || "")) body.ping_role_id = draft.ping_role_id;
    if (draft.template !== (follow.template || "")) body.template = draft.template;
    if (body.channel_id === undefined && body.ping_role_id === undefined && body.template === undefined) {
      setStatus({ notice: "Nothing to save for that account.", error: "" });
      return;
    }
    setBusyFollow(followKey(follow)); setStatus(initialStatus);
    updateNotifierFollow(guildId, body, csrfToken)
      .then((result) => { applyFollow(result.follow); setStatus({ notice: `${result.follow.display} updated.`, error: "" }); })
      .catch((reason) => setStatus({ notice: "", error: reason instanceof Error ? reason.message : "That account could not be updated." }))
      .finally(() => setBusyFollow(""));
  };

  const toggleFollow = (follow: NotifierFollow) => {
    setBusyFollow(followKey(follow)); setStatus(initialStatus);
    updateNotifierFollow(guildId, { platform: follow.platform, username: follow.username, enabled: !follow.enabled }, csrfToken)
      .then((result) => { applyFollow(result.follow); setStatus({ notice: `${result.follow.display} is ${result.follow.enabled ? "active again" : "paused"}.`, error: "" }); })
      .catch((reason) => setStatus({ notice: "", error: reason instanceof Error ? reason.message : "That account could not be updated." }))
      .finally(() => setBusyFollow(""));
  };

  const sendTest = (follow: NotifierFollow) => {
    setBusyFollow(followKey(follow)); setStatus(initialStatus);
    testNotifierFollow(guildId, follow.platform, follow.username, csrfToken)
      .then((result) => setStatus({
        notice: result.delivered ? `Test notification posted in #${result.channel}.` : result.message || "Nothing was sent.",
        error: "",
      }))
      .catch((reason) => setStatus({ notice: "", error: reason instanceof Error ? reason.message : "The test notification could not be sent." }))
      .finally(() => setBusyFollow(""));
  };

  const removeFollow = (follow: NotifierFollow) => {
    const key = followKey(follow);
    if (confirmRemove !== key) { setConfirmRemove(key); return; }
    setBusyFollow(key); setConfirmRemove(""); setStatus(initialStatus);
    removeNotifierFollow(guildId, follow.platform, follow.username, csrfToken)
      .then(() => {
        setData((current) => current && ({ ...current, follows: current.follows.filter((item) => followKey(item) !== key) }));
        setDrafts((current) => {
          const next = { ...current };
          delete next[key];
          return next;
        });
        setStatus({ notice: `Stopped following ${follow.display}.`, error: "" });
      })
      .catch((reason) => setStatus({ notice: "", error: reason instanceof Error ? reason.message : "That account could not be removed." }))
      .finally(() => setBusyFollow(""));
  };

  const updateDraft = (follow: NotifierFollow, patch: Partial<Draft>) => {
    const key = followKey(follow);
    setDrafts((current) => ({ ...current, [key]: { ...(current[key] || draftFor(follow)), ...patch } }));
  };

  const platformHint = platformFor(form.platform);

  return <>
    <style>{notifierStyles}</style>
    <DashHeading eyebrow="Community · notifications" title="Never miss a post again." text="Niko watches your favourite creators and posts their new videos, streams and updates straight into a channel you choose." />
    <div className="settings-intro">
      <span className="settings-intro-icon"><Icon name="message" /></span>
      <div>
        <span className="panel-kicker">Social feed desk</span>
        <strong>{data.follows.filter((follow) => follow.enabled).length} active · {data.follows.length} of {data.limits.max_follows} slots used</strong>
        <p>Add an account once, then point each one at its own channel, role ping or custom message.</p>
      </div>
      <span className="settings-intro-state"><span className="status-dot" /> Per server</span>
    </div>
    {status.error && <div className="notice warning" role="alert">{status.error}</div>}
    {status.notice && <div className="notice" role="status">{status.notice}</div>}
    {!data.config.enabled && <div className="notice warning" role="status">Announcements are switched off for this server. Every account below is paused until you re-enable them.</div>}

    <form className="settings-stack" onSubmit={saveServerSettings}>
      <section className="dash-panel settings-panel">
        <SectionTitle label="Per server" title="Announcement defaults" detail="Choose where new accounts post and who gets pinged when you do not set that per account." icon="settings" />
        <div className="form-grid">
          <Field label="Default channel" hint="Used when an account has no channel of its own.">
            <select value={configDraft.default_channel_id} onChange={(event) => setConfigDraft({ ...configDraft, default_channel_id: event.target.value })}>
              <option value="">No default channel</option>
              {channelsWithSelected(resources, configDraft.default_channel_id).map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}
            </select>
          </Field>
          <Field label="Default ping role" hint="Leave empty for a quiet announcement.">
            <RoleSelect roles={resources?.roles || []} value={configDraft.ping_role_id} placeholder="No ping" onChange={(value) => setConfigDraft({ ...configDraft, ping_role_id: String(value) })} />
          </Field>
        </div>
        <label className="setting-row">
          <span><strong>Post new content automatically</strong><small>Turn this off to pause every announcement without removing your accounts</small></span>
          <input type="checkbox" checked={configDraft.enabled} onChange={(event) => setConfigDraft({ ...configDraft, enabled: event.target.checked })} /><i aria-hidden="true" />
        </label>
        <div className="setting-footer">
          <span role="status">{savingConfig ? "Saving…" : `${data.follows.length} of ${data.limits.max_follows} account slots used`}</span>
          <button className="button button-primary" type="submit" disabled={savingConfig}>{savingConfig ? "Saving…" : "Save settings"}</button>
        </div>
      </section>
    </form>

    <form className="dash-panel settings-panel" onSubmit={submitAdd}>
      <SectionTitle label="New follow" title="Add an account" detail="Paste a profile link or type the account name — Niko checks it against the platform before saving." icon="plus" />
      <div className="form-grid">
        <Field label="Platform">
          <select value={form.platform} onChange={(event) => { const value = event.target.value; setManualPlatform(Boolean(value)); setForm({ ...form, platform: value }); }}>
            <option value="">Choose a platform</option>
            {platforms.map((platform) => <option value={platform.id} key={platform.id}>{platform.label}</option>)}
          </select>
        </Field>
        <Field label={platformHint?.field_label || "Account"} hint="A profile link is fine too.">
          <input
            value={form.query}
            maxLength={200}
            onChange={(event) => {
              const query = event.target.value;
              const detected = detectPlatform(query);
              setForm((current) => ({ ...current, query, platform: manualPlatform ? current.platform : detected || current.platform }));
            }}
            placeholder={platformHint?.field_placeholder || "https://twitch.tv/name or @handle"}
          />
        </Field>
        <Field label="Announcement channel">
          <select value={form.channel_id} onChange={(event) => setForm({ ...form, channel_id: event.target.value })}>
            <option value="">Choose a channel</option>
            {channelsWithSelected(resources, form.channel_id).map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}
          </select>
        </Field>
        <Field label="Ping role" hint="Optional — mentioned with every announcement.">
          <RoleSelect roles={resources?.roles || []} value={form.ping_role_id} placeholder="No ping" onChange={(value) => setForm({ ...form, ping_role_id: String(value) })} />
        </Field>
        <Field label="Custom message" hint={`Optional. Use ${data.limits.template_placeholders.map((name) => `{${name}}`).join(", ")} · up to ${data.limits.max_template_length} characters.`}>
          <input value={form.template} maxLength={data.limits.max_template_length} onChange={(event) => setForm({ ...form, template: event.target.value })} placeholder="New from {account}: {title}" />
        </Field>
        <Field label="Capacity" hint="Adding the same account again updates its channel, ping role and message.">
          <span className="form-hint">{`${countFor(form.platform)} of ${data.limits.max_follows_per_platform} used on this platform · ${data.follows.length} of ${data.limits.max_follows} total`}</span>
        </Field>
      </div>
      <div className="setting-footer">
        <span role="status">{blockedReason || "Niko validates the account live, so this can take a second."}</span>
        <button className="button button-primary" type="submit" disabled={adding || addBlocked}>{adding ? "Checking that account…" : "Add account"}</button>
      </div>
    </form>

    <section className="dash-panel settings-panel">
      <SectionTitle label="Followed accounts" title={`${data.follows.length} account${data.follows.length === 1 ? "" : "s"} watched`} detail="Each account keeps its own channel, ping role and message, and can be paused without losing its history." icon="chart" />
      {data.follows.length === 0
        ? <div className="empty-state">Nothing is being tracked yet. Add your first account above and Niko will start announcing it.</div>
        : <div className="notifier-list">
          {data.follows.map((follow) => {
            const key = followKey(follow);
            const draft = drafts[key] || draftFor(follow);
            const busy = busyFollow === key;
            return <article className="notifier-follow-card" key={key}>
              <div className="notifier-follow-head">
                <div>
                  <span className="panel-kicker">{platformLabel(follow.platform)}</span>
                  <h3>{follow.display}</h3>
                  <small>{follow.username}{draft.channel_id ? ` → #${channelLabel(resources, draft.channel_id)}` : " → pick a channel"}</small>
                </div>
                <div className="notifier-follow-badges">
                  <span className={`notifier-badge ${follow.enabled ? "is-active" : "is-paused"}`}>{follow.enabled ? "Active" : "Paused"}</span>
                  {follow.failures > 0 && <span className="notifier-badge is-warning">{follow.failures} failed check{follow.failures === 1 ? "" : "s"}</span>}
                </div>
              </div>
              <div className="form-grid">
                <Field label="Channel">
                  <select value={draft.channel_id} onChange={(event) => updateDraft(follow, { channel_id: event.target.value })}>
                    <option value="">Choose a channel</option>
                    {channelsWithSelected(resources, draft.channel_id).map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}
                  </select>
                </Field>
                <Field label="Ping role" hint="Leave empty for a quiet announcement.">
                  <RoleSelect roles={resources?.roles || []} value={draft.ping_role_id} placeholder="No ping" onChange={(value) => updateDraft(follow, { ping_role_id: String(value) })} />
                </Field>
                <Field label="Custom message" hint="Sent above the announcement.">
                  <input value={draft.template} maxLength={data.limits.max_template_length} onChange={(event) => updateDraft(follow, { template: event.target.value })} placeholder="Optional message" />
                </Field>
              </div>
              <div className="setting-footer">
                <span role="status">{follow.failures > 0 ? `${formatChecked(follow.last_checked_at)} · check the account name` : formatChecked(follow.last_checked_at)}</span>
                <div className="notifier-follow-actions">
                  <button className="button button-muted button-small" type="button" onClick={() => sendTest(follow)} disabled={busy}><Icon name="spark" /> Send test</button>
                  <button className="button button-muted button-small" type="button" onClick={() => toggleFollow(follow)} disabled={busy}>{follow.enabled ? "Pause" : "Resume"}</button>
                  <button className={`button button-small ${confirmRemove === key ? "button-primary" : "button-muted"}`} type="button" onClick={() => removeFollow(follow)} disabled={busy}>{confirmRemove === key ? "Confirm remove" : "Remove"}</button>
                  <button className="button button-primary button-small" type="button" onClick={() => saveFollow(follow)} disabled={busy}>{busy ? "Saving…" : "Save changes"}</button>
                </div>
              </div>
            </article>;
          })}
        </div>}
    </section>
  </>;
}
