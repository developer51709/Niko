import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  addNotifierFollow,
  getGuildNotifier,
  removeNotifierFollow,
  saveNotifierConfig,
  testNotifierFollow,
  updateNotifierFollow,
} from "../../api";
import { clearToasts, notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { Icon } from "../Icon";
import { ChannelSelect } from "./ChannelSelect";
import { RolePicker } from "./RolePicker";
import { Field } from "./FormField";
import { SectionTitle } from "./SectionTitle";
import { Select } from "./Select";
import type { GuildResources, NotifierFollow, NotifierResponse } from "../../types";
import { DashHeading, SectionSkeleton } from "./DashboardViews";
import { Switch } from "./Switch";
import { SettingCard, SettingCards } from "./SettingCards";
import { type Translate, useStrings } from "../../i18n";

type Props = { guildId: string; resources: GuildResources | null; csrfToken?: string };
type Draft = { channel_id: string; ping_role_id: string; template: string };

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
.notifier-list{display:grid;gap:14px;padding-top:12px}
`;

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

function formatChecked(value: string | null, t: Translate) {
  if (!value) return t("notifier.neverChecked");
  // The API writes UTC timestamps; an unparseable legacy value is shown as-is
  // rather than as “Invalid Date”.
  const parsed = new Date(value.includes("T") ? value : `${value.replace(" ", "T")}Z`);
  return Number.isNaN(parsed.getTime()) ? value : t("notifier.lastChecked", { date: parsed.toLocaleString() });
}

function channelLabel(resources: GuildResources | null, id: string | null, t: Translate) {
  if (!id) return t("notifier.noChannel");
  return resources?.channels.find((channel) => String(channel.id) === String(id))?.name || t("notifier.savedChannel", { id });
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
  const { t } = useStrings("dashboard");
  const [data, setData] = useState<NotifierResponse | null>(null);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [retryAttempt, setRetryAttempt] = useState(0);
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
      // The default channel is applied by the server when the picker is left
      // blank, so it is never preselected here: the picker stays optional while
      // a default exists and becomes required as soon as the default is cleared.
      ping_role_id: current.ping_role_id || response.config.ping_role_id || "",
    }));
  }), [guildId]);

  useEffect(() => {
    let active = true;
    setLoading(true); setLoadError(""); clearToasts();
    load()
      .catch((reason) => { if (active) setLoadError(reason instanceof Error ? reason.message : t("notifier.loadFailed")); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [load, retryAttempt]);

  useEffect(() => {
    if (!confirmRemove) return;
    const timer = window.setTimeout(() => setConfirmRemove(""), 6000);
    return () => window.clearTimeout(timer);
  }, [confirmRemove]);

  if (loading) return <SectionSkeleton label={t("notifier.skeleton")} />;
  if (loadError || !data) return <div className="inline-error" role="alert">
    <strong>{t("notifier.errorTitle")}</strong>
    <span>{loadError || t("notifier.noData")}</span>
    <button className="button button-muted" type="button" onClick={() => { setLoadError(""); setLoading(true); setRetryAttempt((attempt) => attempt + 1); }}>{t("notifier.retry")}</button>
  </div>;

  const platforms = data.platforms;
  const platformLabel = (id: string) => platforms.find((platform) => platform.id === id)?.label || id;
  const platformFor = (id: string) => platforms.find((platform) => platform.id === id);
  const countFor = (id: string) => data.follows.filter((follow) => follow.platform === id).length;
  const atGuildLimit = data.follows.length >= data.limits.max_follows;
  const atPlatformLimit = Boolean(form.platform) && countFor(form.platform) >= data.limits.max_follows_per_platform;
  const defaultChannelId = data.config.default_channel_id || "";
  const defaultChannelLabel = defaultChannelId ? channelLabel(resources, defaultChannelId, t) : "";
  const addChannelRequired = !defaultChannelId;
  const addBlocked = atGuildLimit || atPlatformLimit || platforms.length === 0;
  const blockedReason = atGuildLimit
    ? t("notifier.limitGuild", { count: data.limits.max_follows })
    : atPlatformLimit
      ? t("notifier.limitPlatform", { count: data.limits.max_follows_per_platform, platform: platformLabel(form.platform) })
      : platforms.length === 0
        ? t("notifier.platformsUnavailable")
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
    setSavingConfig(true);
    notifyLoading(t("notifier.savingSettings"), "notifier-config");
    saveNotifierConfig(guildId, {
      enabled: configDraft.enabled,
      default_channel_id: configDraft.default_channel_id,
      ping_role_id: configDraft.ping_role_id,
    }, csrfToken)
      .then((result) => {
        setData((current) => current && ({ ...current, config: result.config }));
        notifySuccess(t("notifier.settingsSaved"), "notifier-config");
      })
      .catch((reason) => notifyError(reason instanceof Error ? reason.message : t("notifier.settingsSaveFailed"), "notifier-config"))
      .finally(() => setSavingConfig(false));
  };

  const submitAdd = (event: FormEvent) => {
    event.preventDefault();
    if (addBlocked) { notifyError(blockedReason, "notifier-add"); return; }
    if (!form.platform) { notifyError(t("notifier.pickPlatform"), "notifier-add"); return; }
    // A blank picker is fine while the server has a default channel; the API
    // falls back to it. Only a server with no default has to choose here.
    if (!form.channel_id && addChannelRequired) { notifyError(t("notifier.pickChannel"), "notifier-add"); return; }
    setAdding(true);
    notifyLoading(t("notifier.checkingAccount"), "notifier-add");
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
        notifySuccess(t(result.created ? "notifier.accountAdded" : "notifier.accountUpdated"), "notifier-add");
      })
      .catch((reason) => notifyError(reason instanceof Error ? reason.message : t("notifier.addFailed"), "notifier-add"))
      .finally(() => setAdding(false));
  };

  const saveFollow = (follow: NotifierFollow) => {
    const key = followKey(follow);
    const draft = drafts[key] || draftFor(follow);
    if (!draft.channel_id) { notifyError(t("notifier.pickAccountChannel"), key); return; }
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
      notifySuccess(t("notifier.nothingToSave"), key);
      return;
    }
    setBusyFollow(key);
    notifyLoading(t("notifier.saving"), key);
    updateNotifierFollow(guildId, body, csrfToken)
      .then((result) => { applyFollow(result.follow); notifySuccess(`${result.follow.display} updated.`, key); })
      .catch((reason) => notifyError(reason instanceof Error ? reason.message : t("notifier.updateFailed"), key))
      .finally(() => setBusyFollow(""));
  };

  const toggleFollow = (follow: NotifierFollow) => {
    const key = followKey(follow);
    setBusyFollow(key);
    notifyLoading(t(follow.enabled ? "notifier.pausing" : "notifier.resuming"), key);
    updateNotifierFollow(guildId, { platform: follow.platform, username: follow.username, enabled: !follow.enabled }, csrfToken)
      .then((result) => { applyFollow(result.follow); notifySuccess(t(result.follow.enabled ? "notifier.resumed" : "notifier.paused", { name: result.follow.display }), key); })
      .catch((reason) => notifyError(reason instanceof Error ? reason.message : t("notifier.updateFailed"), key))
      .finally(() => setBusyFollow(""));
  };

  const sendTest = (follow: NotifierFollow) => {
    const key = followKey(follow);
    setBusyFollow(key);
    notifyLoading(t("notifier.sendingTest"), key);
    testNotifierFollow(guildId, follow.platform, follow.username, csrfToken)
      .then((result) => {
        const message = result.delivered ? t("notifier.testPosted", { channel: result.channel || "" }) : result.message || t("notifier.nothingSent");
        if (result.delivered) notifySuccess(message, key);
        else notifyError(message, key);
      })
      .catch((reason) => notifyError(reason instanceof Error ? reason.message : t("notifier.testFailed"), key))
      .finally(() => setBusyFollow(""));
  };

  const removeFollow = (follow: NotifierFollow) => {
    const key = followKey(follow);
    if (confirmRemove !== key) { setConfirmRemove(key); return; }
    setBusyFollow(key); setConfirmRemove("");
    notifyLoading(t("notifier.removing"), key);
    removeNotifierFollow(guildId, follow.platform, follow.username, csrfToken)
      .then(() => {
        setData((current) => current && ({ ...current, follows: current.follows.filter((item) => followKey(item) !== key) }));
        setDrafts((current) => {
          const next = { ...current };
          delete next[key];
          return next;
        });
        notifySuccess(t("notifier.unfollowed", { name: follow.display }), key);
      })
      .catch((reason) => notifyError(reason instanceof Error ? reason.message : t("notifier.removeFailed"), key))
      .finally(() => setBusyFollow(""));
  };

  const updateDraft = (follow: NotifierFollow, patch: Partial<Draft>) => {
    const key = followKey(follow);
    setDrafts((current) => ({ ...current, [key]: { ...(current[key] || draftFor(follow)), ...patch } }));
  };

  const platformHint = platformFor(form.platform);

  return <>
    <style>{notifierStyles}</style>
    <DashHeading eyebrow={t("notifier.eyebrow")} title={t("notifier.title")} text={t("notifier.text")} />
    <div className="settings-intro">
      <span className="settings-intro-icon"><Icon name="message" /></span>
      <div>
        <span className="panel-kicker">{t("notifier.kicker")}</span>
        <strong>{t("notifier.summary", { active: data.follows.filter((follow) => follow.enabled).length, used: data.follows.length, max: data.limits.max_follows })}</strong>
        <p>{t("notifier.introText")}</p>
      </div>
      <span className="settings-intro-state"><span className="status-dot" /> {t("settings.perServer")}</span>
    </div>
    {!data.config.enabled && <div className="notice warning" role="status">{t("notifier.disabledNotice")}</div>}

    {/* One shared grid for every card on this tab, exactly like the other
        feature tabs, so the panels are spaced instead of touching. */}
    <div className="settings-stack guild-feature-settings notifier-settings-stack">
    <form className="settings-stack" onSubmit={saveServerSettings}>
      <section className="dash-panel settings-panel">
        <SectionTitle label={t("settings.perServer")} title={t("notifier.defaultsTitle")} detail={t("notifier.defaultsDetail")} icon="settings" />
        <div className="form-grid">
          <Field label={t("notifier.defaultChannel")} hint={t("notifier.defaultChannelHint")}>
            <ChannelSelect
              channels={channelsWithSelected(resources, configDraft.default_channel_id)}
              value={configDraft.default_channel_id}
              placeholder={t("notifier.noDefaultChannel")}
              ariaLabel={t("notifier.defaultChannel")}
              onChange={(value) => setConfigDraft({ ...configDraft, default_channel_id: value })}
            />
          </Field>
          <Field label={t("notifier.defaultPingRole")} hint={t("notifier.quietHint")}>
            <RolePicker roles={resources?.roles || []} value={configDraft.ping_role_id} placeholder={t("notifier.noPing")} ariaLabel={t("notifier.defaultPingRole")} onChange={(value) => setConfigDraft({ ...configDraft, ping_role_id: value })} />
          </Field>
        </div>
        <SettingCards>
          <SettingCard
            title={t("notifier.autopost")}
            hint={t("notifier.autopostHint")}
            action={<Switch checked={configDraft.enabled} onCheckedChange={(value) => setConfigDraft({ ...configDraft, enabled: value })} aria-label={t("notifier.autopost")} />}
          />
        </SettingCards>
        <div className="setting-footer">
          <span role="status">{savingConfig ? t("notifier.saving") : t("notifier.slotsUsed", { used: data.follows.length, max: data.limits.max_follows })}</span>
          <button className="button button-primary" type="submit" disabled={savingConfig}>{t(savingConfig ? "notifier.saving" : "notifier.saveSettings")}</button>
        </div>
      </section>
    </form>

    <form className="dash-panel settings-panel" onSubmit={submitAdd}>
      <SectionTitle label={t("notifier.newFollowLabel")} title={t("notifier.addTitle")} detail={t("notifier.addDetail")} icon="plus" />
      <div className="form-grid">
        <Field label={t("notifier.platform")}>
          <Select
            placeholder={t("notifier.choosePlatform")}
            options={platforms.map((platform) => ({ value: platform.id, label: platform.label }))}
            value={form.platform}
            onChange={(value) => { setManualPlatform(Boolean(value)); setForm({ ...form, platform: value }); }}
          />
        </Field>
        <Field label={platformHint?.field_label || t("notifier.account")} hint={t("notifier.accountHint")}>
          <input
            value={form.query}
            maxLength={200}
            onChange={(event) => {
              const query = event.target.value;
              const detected = detectPlatform(query);
              setForm((current) => ({ ...current, query, platform: manualPlatform ? current.platform : detected || current.platform }));
            }}
            placeholder={platformHint?.field_placeholder || t("notifier.accountPlaceholder")}
          />
        </Field>
        <Field
          label={t(addChannelRequired ? "notifier.channelRequired" : "notifier.channel")}
          hint={addChannelRequired
            ? t("notifier.channelRequiredHint")
            : t("notifier.channelHint", { channel: defaultChannelLabel })}
        >
          <ChannelSelect
            channels={channelsWithSelected(resources, form.channel_id)}
            value={form.channel_id}
            placeholder={defaultChannelId ? t("notifier.useDefault", { channel: defaultChannelLabel }) : t("pickers.chooseChannel")}
            ariaLabel={t(addChannelRequired ? "notifier.channelRequired" : "notifier.channel")}
            onChange={(value) => setForm({ ...form, channel_id: value })}
          />
        </Field>
        <Field label={t("notifier.pingRole")} hint={t("notifier.pingRoleHint")}>
          <RolePicker roles={resources?.roles || []} value={form.ping_role_id} placeholder={t("notifier.noPing")} ariaLabel={t("notifier.pingRole")} onChange={(value) => setForm({ ...form, ping_role_id: value })} />
        </Field>
        <Field label={t("notifier.customMessage")} hint={t("notifier.customMessageHint", { placeholders: data.limits.template_placeholders.map((name) => `{${name}}`).join(", "), max: data.limits.max_template_length })}>
          <input value={form.template} maxLength={data.limits.max_template_length} onChange={(event) => setForm({ ...form, template: event.target.value })} placeholder={t("notifier.templatePlaceholder")} />
        </Field>
        <Field label={t("notifier.capacity")} hint={t("notifier.capacityHint")}>
          <span className="form-hint">{t("notifier.capacityLine", { platform: countFor(form.platform), platformMax: data.limits.max_follows_per_platform, total: data.follows.length, max: data.limits.max_follows })}</span>
        </Field>
      </div>
      <div className="setting-footer">
        <span role="status">{blockedReason || t("notifier.validatesLive")}</span>
        <button className="button button-primary" type="submit" disabled={adding || addBlocked}>{t(adding ? "notifier.checkingAccount" : "notifier.addAccount")}</button>
      </div>
    </form>

    <section className="dash-panel settings-panel">
      <SectionTitle label={t("notifier.followedLabel")} title={t(data.follows.length === 1 ? "notifier.watchedOne" : "notifier.watchedMany", { count: data.follows.length })} detail={t("notifier.followedDetail")} icon="chart" />
      {data.follows.length === 0
        ? <div className="empty-state">{t("notifier.empty")}</div>
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
                  <small>{follow.username}{draft.channel_id ? ` → #${channelLabel(resources, draft.channel_id, t)}` : t("notifier.pickAChannel")}</small>
                </div>
                <div className="notifier-follow-badges">
                  <span className={`notifier-badge ${follow.enabled ? "is-active" : "is-paused"}`}>{t(follow.enabled ? "notifier.active" : "notifier.pausedBadge")}</span>
                  {follow.failures > 0 && <span className="notifier-badge is-warning">{t(follow.failures === 1 ? "notifier.failedOne" : "notifier.failedMany", { count: follow.failures })}</span>}
                </div>
              </div>
              <div className="form-grid">
                <Field label={t("notifier.channel")}>
                  <ChannelSelect
                    channels={channelsWithSelected(resources, draft.channel_id)}
                    value={draft.channel_id}
                    placeholder={t("pickers.chooseChannel")}
                    ariaLabel={t("notifier.channelFor", { name: follow.display })}
                    onChange={(value) => updateDraft(follow, { channel_id: value })}
                  />
                </Field>
                <Field label={t("notifier.pingRole")} hint={t("notifier.quietHint")}>
                  <RolePicker roles={resources?.roles || []} value={draft.ping_role_id} placeholder={t("notifier.noPing")} ariaLabel={t("notifier.pingRoleFor", { name: follow.display })} onChange={(value) => updateDraft(follow, { ping_role_id: value })} />
                </Field>
                <Field label={t("notifier.customMessage")} hint={t("notifier.customMessageHintShort")}>
                  <input value={draft.template} maxLength={data.limits.max_template_length} onChange={(event) => updateDraft(follow, { template: event.target.value })} placeholder={t("notifier.optionalMessage")} />
                </Field>
              </div>
              <div className="setting-footer">
                <span role="status">{follow.failures > 0 ? t("notifier.checkedWithWarning", { date: formatChecked(follow.last_checked_at, t) }) : formatChecked(follow.last_checked_at, t)}</span>
                <div className="notifier-follow-actions">
                  <button className="button button-muted button-small" type="button" onClick={() => sendTest(follow)} disabled={busy}><Icon name="spark" /> {t("notifier.sendTest")}</button>
                  <button className="button button-muted button-small" type="button" onClick={() => toggleFollow(follow)} disabled={busy}>{t(follow.enabled ? "notifier.pause" : "notifier.resume")}</button>
                  <button className={`button button-small ${confirmRemove === key ? "button-primary" : "button-muted"}`} type="button" onClick={() => removeFollow(follow)} disabled={busy}>{t(confirmRemove === key ? "notifier.confirmRemove" : "notifier.remove")}</button>
                  <button className="button button-primary button-small" type="button" onClick={() => saveFollow(follow)} disabled={busy}>{t(busy ? "notifier.saving" : "settings.saveChanges")}</button>
                </div>
              </div>
            </article>;
          })}
        </div>}
    </section>
    </div>
  </>;
}
