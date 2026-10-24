import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { getBoosterSettings, saveBoosterSettings } from "../../api";
import { clearToasts, notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { Icon } from "../Icon";
import type { BoosterSettings, GuildResources } from "../../types";
import { DashHeading } from "./DashboardViews";

type Props = {
  guildId: string;
  resources: GuildResources | null;
  csrfToken?: string;
  initialSettings: BoosterSettings | null;
};

type Draft = BoosterSettings;

function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return <label className="form-field"><span className="form-label">{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

function selectedChannels(resources: GuildResources | null, selected: string) {
  const channels = resources?.channels || [];
  if (!selected || channels.some((channel) => String(channel.id) === selected)) return channels;
  return [{ id: selected, name: `Saved channel · ${selected}` }, ...channels];
}

export function BoostersView({ guildId, resources, csrfToken, initialSettings }: Props) {
  const [settings, setSettings] = useState<Draft>(initialSettings || {
    notifications_enabled: false,
    roles_enabled: false,
    channel_id: "",
    boost_message: "Thank you {user} for boosting {server}! We now have {boost_count} boosts.",
    unboost_message: "{user} is no longer boosting {server}. We now have {boost_count} boosts.",
  });
  const [loading, setLoading] = useState(!initialSettings);
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    let active = true;
    clearToasts("boosters-settings");
    if (initialSettings) {
      setSettings(initialSettings);
      setLoading(false);
      setLoadError("");
      return () => { active = false; };
    }
    setLoading(true);
    getBoosterSettings(guildId)
      .then((response) => { if (active) setSettings(response.config); })
      .catch((error) => { if (active) setLoadError(error instanceof Error ? error.message : "Booster settings could not be loaded."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [guildId, initialSettings]);

  const update = (key: keyof Draft, value: string | boolean) => {
    setSettings((current) => ({ ...current, [key]: value }));
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    notifyLoading("Saving booster settings…", "boosters-settings");
    saveBoosterSettings(guildId, settings, csrfToken)
      .then((response) => {
        setSettings(response.config);
        notifySuccess("Booster settings saved.", "boosters-settings");
      })
      .catch((error) => notifyError(error instanceof Error ? error.message : "Booster settings could not be saved.", "boosters-settings"))
      .finally(() => setSaving(false));
  };

  if (loading) return <div className="section-loading" role="status">Loading booster settings…</div>;
  if (loadError) return <div className="inline-error" role="alert">
    <strong>Couldn’t load booster settings.</strong>
    <span>{loadError}</span>
    <button className="button button-muted" onClick={() => window.location.reload()}>Try again</button>
  </div>;

  return <>
    <DashHeading
      eyebrow="Boosters"
      title="Give every boost a personal thank-you."
      text="Set up boost announcements and let active boosters create and share their own server role."
    />
    <form onSubmit={submit} className="settings-stack guild-feature-settings">
      <section className="dash-panel settings-panel">
        <div className="panel-heading settings-section-title">
          <div><span className="panel-kicker">Announcements</span><h3>Boost notifications</h3><p>Choose where boost and unboost messages appear, then customize both messages.</p></div>
          <span className="panel-icon"><Icon name="guild_notifications" /></span>
        </div>
        <label className="setting-row">
          <span><strong>Post boost and unboost announcements</strong><small>Messages are only posted after a member starts or stops boosting.</small></span>
          <input type="checkbox" checked={settings.notifications_enabled} onChange={(event) => update("notifications_enabled", event.target.checked)} />
          <i aria-hidden="true" />
        </label>
        <div className="form-grid">
          <Field label="Announcement channel">
            <select value={settings.channel_id} onChange={(event) => update("channel_id", event.target.value)}>
              <option value="">Choose a text channel</option>
              {selectedChannels(resources, settings.channel_id).map((channel) => (
                <option key={channel.id} value={channel.id}>#{channel.name}</option>
              ))}
            </select>
          </Field>
          <Field label="Boost message" hint="Placeholders: {user}, {name}, {server}, {boost_count}, {boost_level}">
            <textarea rows={3} maxLength={2000} value={settings.boost_message} onChange={(event) => update("boost_message", event.target.value)} />
          </Field>
          <Field label="Unboost message" hint="Uses the same placeholders as the boost message.">
            <textarea rows={3} maxLength={2000} value={settings.unboost_message} onChange={(event) => update("unboost_message", event.target.value)} />
          </Field>
        </div>
      </section>

      <section className="dash-panel settings-panel">
        <div className="panel-heading settings-section-title">
          <div><span className="panel-kicker">Personal roles</span><h3>Booster role access</h3><p>Each active booster gets a separate role they can customize and share.</p></div>
          <span className="panel-icon"><Icon name="users" /></span>
        </div>
        <label className="setting-row">
          <span><strong>Enable personal booster roles</strong><small>Active boosters can use /boosterrole to rename, recolor, set an icon, and share or unshare their role.</small></span>
          <input type="checkbox" checked={settings.roles_enabled} onChange={(event) => update("roles_enabled", event.target.checked)} />
          <i aria-hidden="true" />
        </label>
        <p className="form-hint" role="note">
          Turning this off deletes Niko-managed booster roles and removes them from the boosters and anyone they shared them with. Role icons and gradient colors are available only when Discord unlocks those perks for your server.
        </p>
      </section>

      <div className="setting-footer">
        <span>Changes apply to this server.</span>
        <button className="button button-primary" type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save changes"}
        </button>
      </div>
    </form>
  </>;
}
