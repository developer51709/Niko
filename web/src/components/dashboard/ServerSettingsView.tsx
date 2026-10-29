import { type FormEvent, useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { saveConfig } from "../../api";
import { Icon } from "../Icon";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import type { GuildConfig, GuildResources, ServerConfig } from "../../types";
import { ChannelSelect } from "./ChannelSelect";
import { DashHeading } from "./DashboardViews";
import { Switch } from "./Switch";
import { SettingCard, SettingCards } from "./SettingCards";

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
  return <div className="form-field">
    <span className="form-label">{label}</span>
    <div className="settings-option-list">
      {options.map((option, index) => <div className="settings-option-row" key={`${label}-${index}`}>
        <input aria-label={`${label} ${index + 1}`} value={option} maxLength={100} onChange={(event) => onChange(options.map((item, itemIndex) => itemIndex === index ? event.target.value : item))} placeholder={`${placeholder} ${index + 1}`} disabled={disabled} />
        <button type="button" className="settings-option-remove" onClick={() => onChange(options.filter((_, itemIndex) => itemIndex !== index))} aria-label={`Remove ${label.toLowerCase()} ${index + 1}`} disabled={disabled}>Remove</button>
      </div>)}
    </div>
    <button type="button" className="button button-muted button-small settings-option-add" onClick={() => onChange([...options, ""])} disabled={disabled}>＋ Add option</button>
    <small>{hint}</small>
  </div>;
}

function SectionTitle({ label, title, detail, icon }: { label: string; title: string; detail: string; icon: string }) {
  return <div className="panel-heading settings-section-title">
    <div><span className="panel-kicker">{label}</span><h3>{title}</h3><p>{detail}</p></div>
    <span className="panel-icon"><Icon name={icon} /></span>
  </div>;
}

function SaveFooter({ state }: { state: SaveState }) {
  return <div className="setting-footer">
    <span>Changes apply to this server.</span>
    <button className="button button-primary" type="submit" disabled={state.saving}>{state.saving ? "Saving..." : "Save server settings"}</button>
  </div>;
}

// Fallback only: the bot serves its own category list in server.logging_categories,
// so a new category shows up here without a second hardcoded copy to update.
const fallbackLoggingCategories: [string, string][] = [
  ["moderation", "Moderation"], ["automod", "AutoMod"], ["messages", "Messages"],
  ["channels", "Channels"], ["members", "Members"], ["captcha", "Captcha"],
  ["invites", "Invites"], ["roles", "Roles"], ["server", "Server"], ["voice", "Voice"],
];

function loggingCategoryOptions(server?: ServerConfig): [string, string, string][] {
  const categories = server?.logging_categories;
  if (!categories?.length) return fallbackLoggingCategories.map(([key, label]) => [key, label, ""]);
  return categories.map((category) => [category.key, category.label, category.description || ""]);
}

function channelLabel(resources: GuildResources | null, id: string | number | null | undefined) {
  if (!id) return "Not set";
  return resources?.channels.find((channel) => String(channel.id) === String(id))?.name || `Saved channel · ${id}`;
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
    private_server: Boolean(server?.privacy?.private),
  };
}

export function ServerSettingsView({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const loggingCategories = loggingCategoryOptions(config?.server);
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
    notifyLoading("Saving server settings…", "settings-save");
    const prefixes = values.prefixes.map((prefix) => prefix.trim()).filter(Boolean);
    saveConfig(guildId, "server", {
      ...(config?.server?.prefix_override ? {} : { prefixes }),
      logging: {
        ...values.logging,
        disabled: values.disabled_logging,
      },
      privacy: { private: values.private_server },
    }, csrfToken).then((result) => {
      setValues(initialValues(result.config as ServerConfig));
      setState({ saving: false });
      notifySuccess("Server settings saved to Niko.", "settings-save");
    }).catch((error) => {
      setState({ saving: false });
      notifyError(error instanceof Error ? error.message : "Could not save server settings.", "settings-save");
    });
  };

  return <>
    <DashHeading eyebrow="Server settings" title="Make Niko fit your room." text="Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here." />
    <div className="settings-intro"><span className="settings-intro-icon"><Icon name="settings" /></span><div><span className="panel-kicker">Server control room</span><strong>{values.prefixes.filter((prefix) => prefix.trim()).length} command prefixes configured</strong><p>Command prefixes and log destinations live here.</p></div><span className="settings-intro-state"><span className="status-dot" /> Per server</span></div>
    <form onSubmit={submit} className="settings-stack server-settings-stack">
      <section className={`dash-panel settings-panel${config?.server?.prefix_override ? " prefix-settings-development" : ""}`} aria-disabled={config?.server?.prefix_override ? true : undefined}>
        <SectionTitle label="Commands" title="Prefixes" detail="Add each command prefix separately. Niko will respond to all configured prefixes." icon="terminal" />
        {config?.server?.prefix_override && <div className="prefix-development-note" role="note"><AlertTriangle size={16} /><span><strong>Prefix changes are disabled for this deployment.</strong><small>This instance uses the fixed prefix {config.server.prefix_override}.</small></span></div>}
        <div className="prefix-settings-edit-area">
          <StringOptionList label="Command prefixes" hint={`The default prefix is ${config?.server?.default_prefix || "."}`} options={values.prefixes} placeholder="Prefix" onChange={(prefixes) => setValue("prefixes", prefixes)} disabled={Boolean(config?.server?.prefix_override)} />
        </div>
      </section>

      <section className="dash-panel settings-panel"><SectionTitle label="Audit trail" title="Logging destinations" detail="Pick a channel for each event type and disable categories you do not need." icon="book" /><div className="server-logging-list">
        {loggingCategories.map(([key, label, description]) => { const channels = channelsWithSelected(resources, values.logging[key]); return <div className="server-logging-row" key={key} title={description || undefined}><div className="form-field"><span className="form-label">{label} logs</span><ChannelSelect channels={channels} value={String(values.logging[key] || "")} placeholder="Not set" ariaLabel={`${label} logs`} onChange={(value) => setLoggingChannel(key, value)} /></div><div className="server-logging-toggle"><span><strong>Enabled</strong><small>{channelLabel(resources, values.logging[key])}</small></span><Switch checked={!values.disabled_logging.includes(key)} onCheckedChange={() => toggleLogging(key)} aria-label={`Enable ${label} logging`} /></div></div>; })}
      </div></section>

      <section className="dash-panel settings-panel"><SectionTitle label="Privacy" title="Server tag popups" detail="Control what people see when they open this server's tag on a profile." icon="shield" /><SettingCards><SettingCard title="Private server" hint="Hide this server's name, icon, description, member counts, and invite from server tag popups. The tag itself stays visible." action={<Switch checked={values.private_server} onCheckedChange={(value) => setValue("private_server", value)} aria-label="Private server" />} /></SettingCards></section>

      <SaveFooter state={state} />
    </form>
  </>;
}
