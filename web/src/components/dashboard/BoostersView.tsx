import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { getBoosterSettings, saveBoosterSettings } from "../../api";
import { clearToasts, notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { Icon } from "../Icon";
import type { BoosterSettings, GuildResources } from "../../types";
import { ChannelSelect } from "./ChannelSelect";
import { DashHeading, SectionSkeleton } from "./DashboardViews";
import { Switch } from "./Switch";
import { SettingCard, SettingCards } from "./SettingCards";
import { useStrings } from "../../i18n";

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

function selectedChannels(resources: GuildResources | null, selected: string, savedLabel: string) {
  const channels = resources?.channels || [];
  if (!selected || channels.some((channel) => String(channel.id) === selected)) return channels;
  return [{ id: selected, name: savedLabel }, ...channels];
}

export function BoostersView({ guildId, resources, csrfToken, initialSettings }: Props) {
  const { t } = useStrings("dashboard");
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
  const [retryAttempt, setRetryAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    clearToasts("boosters-settings");
    setLoadError("");
    if (initialSettings) {
      setSettings(initialSettings);
      setLoading(false);
      return () => { active = false; };
    }
    setLoading(true);
    getBoosterSettings(guildId)
      .then((response) => { if (active) setSettings(response.config); })
      .catch((error) => { if (active) setLoadError(error instanceof Error ? error.message : t("boosters.loadError")); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [guildId, initialSettings, retryAttempt, t]);

  const update = (key: keyof Draft, value: string | boolean) => {
    setSettings((current) => ({ ...current, [key]: value }));
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    notifyLoading(t("boosters.savingToast"), "boosters-settings");
    saveBoosterSettings(guildId, settings, csrfToken)
      .then((response) => {
        setSettings(response.config);
        notifySuccess(t("boosters.savedToast"), "boosters-settings");
      })
      .catch((error) => notifyError(error instanceof Error ? error.message : t("boosters.saveFailed"), "boosters-settings"))
      .finally(() => setSaving(false));
  };

  if (loading) return <SectionSkeleton label={t("boosters.loading")} />;
  if (loadError) return <div className="inline-error" role="alert">
    <strong>{t("boosters.loadErrorTitle")}</strong>
    <span>{loadError}</span>
    <button className="button button-muted" type="button" onClick={() => { setLoading(true); setLoadError(""); setRetryAttempt((attempt) => attempt + 1); }}>{t("boosters.retry")}</button>
  </div>;

  return <>
    <DashHeading
      eyebrow={t("boosters.eyebrow")}
      title={t("boosters.title")}
      text={t("boosters.text")}
    />
    <form onSubmit={submit} className="settings-stack guild-feature-settings">
      <section className="dash-panel settings-panel">
        <div className="panel-heading settings-section-title">
          <div><span className="panel-kicker">{t("boosters.announceLabel")}</span><h3>{t("boosters.announceTitle")}</h3><p>{t("boosters.announceDetail")}</p></div>
          <span className="panel-icon"><Icon name="guild_notifications" /></span>
        </div>
        <SettingCards>
          <SettingCard
            title={t("boosters.enableAnnouncements")}
            hint={t("boosters.enableAnnouncementsHint")}
            action={<Switch checked={settings.notifications_enabled} onCheckedChange={(value) => update("notifications_enabled", value)} aria-label={t("boosters.enableAnnouncements")} />}
          />
        </SettingCards>
        <div className="form-grid">
          <Field label={t("boosters.channelLabel")}>
            <ChannelSelect
              channels={selectedChannels(resources, settings.channel_id, t("boosters.savedChannel", { id: settings.channel_id }))}
              value={settings.channel_id}
              placeholder={t("boosters.channelPlaceholder")}
              onChange={(value) => update("channel_id", value)}
            />
          </Field>
          <Field label={t("boosters.boostLabel")} hint={t("boosters.boostHint")}>
            <textarea rows={3} maxLength={2000} value={settings.boost_message} onChange={(event) => update("boost_message", event.target.value)} />
          </Field>
          <Field label={t("boosters.unboostLabel")} hint={t("boosters.unboostHint")}>
            <textarea rows={3} maxLength={2000} value={settings.unboost_message} onChange={(event) => update("unboost_message", event.target.value)} />
          </Field>
        </div>
      </section>

      <section className="dash-panel settings-panel">
        <div className="panel-heading settings-section-title">
          <div><span className="panel-kicker">{t("boosters.rolesLabel")}</span><h3>{t("boosters.rolesTitle")}</h3><p>{t("boosters.rolesDetail")}</p></div>
          <span className="panel-icon"><Icon name="users" /></span>
        </div>
        <SettingCards>
          <SettingCard
            title={t("boosters.enableRoles")}
            hint={t("boosters.enableRolesHint")}
            action={<Switch checked={settings.roles_enabled} onCheckedChange={(value) => update("roles_enabled", value)} aria-label={t("boosters.enableRoles")} />}
          />
        </SettingCards>
        <p className="form-hint" role="note">{t("boosters.rolesNote")}</p>
      </section>

      <div className="setting-footer">
        <span>{t("settings.footerNote")}</span>
        <button className="button button-primary" type="submit" disabled={saving}>
          {t(saving ? "settings.saving" : "boosters.save")}
        </button>
      </div>
    </form>
  </>;
}
