import { type FormEvent, useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { saveConfig } from "../../api";
import { Icon } from "../Icon";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { useStrings } from "../../i18n";
import type { GuildConfig, GuildResources, ServerConfig } from "../../types";
import { ChannelSelect } from "./ChannelSelect";
import { DashHeading } from "./DashboardViews";
import { SectionTitle } from "./SectionTitle";
import { Switch } from "./Switch";

// Only the in-flight flag belongs in state now: every result is announced with a
// toast (see ../../utils/toast) instead of an inline line in the card footer.
type SaveState = { saving: boolean };
const initialSave: SaveState = { saving: false };

function StringOptionList({ label, hint, options, placeholder, onChange, disabled = false }: {
  label: string;
  hint: string;
  options: string[];
  placeholder: string;
  onChange: (options: string[]) => void;
  disabled?: boolean;
}) {
  const { t } = useStrings("dashboard");
  return <div className="form-field">
    <span className="form-label">{label}</span>
    <div className="settings-option-list">
      {options.map((option, index) => <div className="settings-option-row" key={`${label}-${index}`}>
        <input aria-label={`${label} ${index + 1}`} value={option} maxLength={100} onChange={(event) => onChange(options.map((item, itemIndex) => itemIndex === index ? event.target.value : item))} placeholder={`${placeholder} ${index + 1}`} disabled={disabled} />
        <button type="button" className="settings-option-remove" onClick={() => onChange(options.filter((_, itemIndex) => itemIndex !== index))} aria-label={`${t("server.remove")} ${label.toLowerCase()} ${index + 1}`} disabled={disabled}>{t("server.remove")}</button>
      </div>)}
    </div>
    <button type="button" className="button button-muted button-small settings-option-add" onClick={() => onChange([...options, ""])} disabled={disabled}>＋ {t("server.addOption")}</button>
    <small>{hint}</small>
  </div>;
}

function SaveFooter({ state }: { state: SaveState }) {
  const { t } = useStrings("dashboard");
  return <div className="setting-footer">
    <span>{t("settings.footerNote")}</span>
    <button className="button button-primary" type="submit" disabled={state.saving}>
      {t(state.saving ? "settings.saving" : "settings.saveServer")}
    </button>
  </div>;
}

// Fallback only: the bot serves its own category list in server.logging_categories,
// so a new category shows up here without a second hardcoded copy to update.
const fallbackLoggingCategories: [string, string][] = [
  ["moderation", "server.category.moderation"], ["automod", "server.category.automod"], ["messages", "server.category.messages"],
  ["channels", "server.category.channels"], ["members", "server.category.members"], ["captcha", "server.category.captcha"],
  ["invites", "server.category.invites"], ["roles", "server.category.roles"], ["server", "server.category.server"], ["voice", "server.category.voice"],
];

function loggingCategoryOptions(server: ServerConfig | undefined, t: (key: string) => string): [string, string, string][] {
  const categories = server?.logging_categories;
  if (!categories?.length) return fallbackLoggingCategories.map(([key, label]) => [key, t(label), ""]);
  return categories.map((category) => [category.key, category.label, category.description || ""]);
}

function channelLabel(resources: GuildResources | null, id: string | number | null | undefined, t: (key: string, values?: Record<string, string | number>) => string) {
  if (!id) return t("server.notSet");
  return resources?.channels.find((channel) => String(channel.id) === String(id))?.name || t("server.savedChannel", { id });
}

function channelsWithSelected(resources: GuildResources | null, selected: string | number | null | undefined) {
  const selectedId = selected ? String(selected) : "";
  const channels = resources?.channels || [];
  if (!selectedId || channels.some((channel) => String(channel.id) === selectedId)) return channels;
  return [{ id: selectedId, name: `Saved channel · ${selectedId}` }, ...channels];
}

function initialValues(server?: ServerConfig) {
  return {
    prefixes: server?.prefixes?.length ? [...server.prefixes] : ["."],
    logging: Object.fromEntries(
      Object.entries(server?.logging || {}).map(([key, value]) => [key, value === null || value === undefined ? "" : String(value)]),
    ),
    disabled_logging: [...(server?.logging?.disabled || [])].map(String),
  };
}

export function ServerSettingsView({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const { t } = useStrings("dashboard");
  const loggingCategories = loggingCategoryOptions(config?.server, t);
  const [values, setValues] = useState(() => initialValues(config?.server));
  const [state, setState] = useState(initialSave);

  useEffect(() => {
    if (config?.server) setValues(initialValues(config.server));
  }, [config]);

  const setValue = (key: string, value: unknown) => setValues((current) => ({ ...current, [key]: value }));
  const setLoggingChannel = (category: string, value: string) => setValues((current) => ({ ...current, logging: { ...current.logging, [category]: value } }));
  const toggleLogging = (category: string) => setValues((current) => ({
    ...current,
    disabled_logging: current.disabled_logging.includes(category)
      ? current.disabled_logging.filter((item) => item !== category)
      : [...current.disabled_logging, category],
  }));

  const submit = (event: FormEvent) => {
    event.preventDefault();
    setState({ saving: true });
    notifyLoading(t("server.saving"), "settings-save");
    const prefixes = values.prefixes.map((prefix) => prefix.trim()).filter(Boolean);
    saveConfig(guildId, "server", {
      ...(config?.server?.prefix_override ? {} : { prefixes }),
      logging: {
        ...values.logging,
        disabled: values.disabled_logging,
      },
    }, csrfToken).then((result) => {
      setValues(initialValues(result.config as ServerConfig));
      setState({ saving: false });
      notifySuccess(t("server.saved"), "settings-save");
    }).catch((error) => {
      setState({ saving: false });
      notifyError(error instanceof Error ? error.message : t("server.saveFailed"), "settings-save");
    });
  };

  return <>
    <DashHeading eyebrow={t("server.eyebrow")} title={t("server.title")} text={t("server.text")} />
    <div className="settings-intro"><span className="settings-intro-icon"><Icon name="settings" /></span><div><span className="panel-kicker">{t("server.kicker")}</span><strong>{t("server.prefixCount", { count: values.prefixes.filter((prefix) => prefix.trim()).length })}</strong><p>{t("server.introText")}</p></div><span className="settings-intro-state"><span className="status-dot" /> {t("settings.perServer")}</span></div>
    <form onSubmit={submit} className="settings-stack server-settings-stack">
      <section className={`dash-panel settings-panel${config?.server?.prefix_override ? " prefix-settings-development" : ""}`} aria-disabled={config?.server?.prefix_override ? true : undefined}>
        <SectionTitle label={t("server.commandsLabel")} title={t("server.prefixesTitle")} detail={t("server.prefixesDetail")} icon="terminal" />
        {config?.server?.prefix_override && <div className="prefix-development-note" role="note"><AlertTriangle size={16} /><span><strong>{t("server.prefixLocked")}</strong><small>{t("server.prefixFixed", { prefix: config.server.prefix_override })}</small></span></div>}
        <div className="prefix-settings-edit-area">
          <StringOptionList label={t("server.prefixesLabel")} hint={t("server.prefixHint", { prefix: config?.server?.default_prefix || "." })} options={values.prefixes} placeholder={t("server.prefixPlaceholder")} onChange={(prefixes) => setValue("prefixes", prefixes)} disabled={Boolean(config?.server?.prefix_override)} />
        </div>
      </section>

      <section className="dash-panel settings-panel"><SectionTitle label={t("server.auditLabel")} title={t("server.loggingTitle")} detail={t("server.loggingDetail")} icon="book" /><div className="server-logging-list">
        {loggingCategories.map(([key, label, description]) => { const channels = channelsWithSelected(resources, values.logging[key]); const fieldLabel = t("server.logsFor", { category: label }); return <div className="server-logging-row" key={key} title={description || undefined}><div className="form-field"><span className="form-label">{fieldLabel}</span><ChannelSelect channels={channels} value={String(values.logging[key] || "")} placeholder={t("server.notSet")} ariaLabel={fieldLabel} onChange={(value) => setLoggingChannel(key, value)} /></div><div className="server-logging-toggle"><span><strong>{t("server.enabled")}</strong><small>{channelLabel(resources, values.logging[key], t)}</small></span><Switch checked={!values.disabled_logging.includes(key)} onCheckedChange={() => toggleLogging(key)} aria-label={t("server.enableLogging", { category: label })} /></div></div>; })}
      </div></section>

      <SaveFooter state={state} />
    </form>
  </>;
}
