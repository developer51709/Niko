import { type FormEvent, type ReactNode, useState } from "react";
import { saveConfig } from "../../api";
import { Icon } from "../Icon";
import type { GuildConfig, GuildResources, ServerConfig } from "../../types";
import { DashHeading } from "./DashboardViews";

type SaveState = { saving: boolean; message: string; error: string };
const initialSave: SaveState = { saving: false, message: "", error: "" };

function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return <label className="form-field"><span className="form-label">{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

function SectionTitle({ label, title, detail, icon }: { label: string; title: string; detail: string; icon: string }) {
  return <div className="panel-heading settings-section-title">
    <div><span className="panel-kicker">{label}</span><h3>{title}</h3><p>{detail}</p></div>
    <span className="panel-icon"><Icon name={icon} /></span>
  </div>;
}

function SaveFooter({ state }: { state: SaveState }) {
  return <div className="setting-footer">
    {state.error ? <span className="form-error" role="alert">{state.error}</span> : <span role="status">{state.message || "Changes apply to this server."}</span>}
    <button className="button button-primary" type="submit" disabled={state.saving}>{state.saving ? "Saving..." : "Save server settings"}</button>
  </div>;
}

const loggingCategories = [
  ["moderation", "Moderation"], ["automod", "AutoMod"], ["messages", "Messages"],
  ["channels", "Channels"], ["members", "Members"], ["captcha", "Captcha"],
  ["invites", "Invites"], ["roles", "Roles"], ["server", "Server"], ["voice", "Voice"],
] as const;

function channelLabel(resources: GuildResources | null, id: string | number | null | undefined) {
  if (!id) return "Not set";
  return resources?.channels.find((channel) => channel.id === String(id))?.name || `Channel ${id}`;
}

function channelsWithSelected(resources: GuildResources | null, selected: string | number | null | undefined) {
  const selectedId = selected ? String(selected) : "";
  const channels = resources?.channels || [];
  if (!selectedId || channels.some((channel) => channel.id === selectedId)) return channels;
  return [{ id: selectedId, name: `Unavailable channel (${selectedId})` }, ...channels];
}

function rolesWithSelected(resources: GuildResources | null, selected: Array<string | number> = []) {
  const roles = resources?.roles || [];
  const known = new Set(roles.map((role) => role.id));
  const unavailable = selected
    .map(String)
    .filter((roleId, index, ids) => roleId && !known.has(roleId) && ids.indexOf(roleId) === index)
    .map((roleId) => ({ id: roleId, name: `Unavailable role (${roleId})` }));
  return [...unavailable, ...roles];
}

function initialValues(server?: ServerConfig) {
  const onboarding = server?.onboarding || {};
  const tickets = server?.tickets || {};
  return {
    prefixes: (server?.prefixes?.length ? server.prefixes : ["."]).join("\n"),
    welcome_channel: onboarding.welcome_channel ? String(onboarding.welcome_channel) : "",
    welcome_title: onboarding.welcome_title || "",
    welcome_description: onboarding.welcome_description || "",
    welcome_color: onboarding.welcome_color === null || onboarding.welcome_color === undefined ? "5865F2" : onboarding.welcome_color.toString(16).padStart(6, "0"),
    welcome_image: onboarding.welcome_image || "",
    rules_channel: onboarding.rules_channel ? String(onboarding.rules_channel) : "",
    rules_text: onboarding.rules_text || "",
    rules_role_id: onboarding.rules_role_id ? String(onboarding.rules_role_id) : "",
    logging: Object.fromEntries(
      Object.entries(server?.logging || {}).map(([key, value]) => [key, value === null || value === undefined ? "" : String(value)]),
    ),
    disabled_logging: [...(server?.logging?.disabled || [])].map(String),
    panel_title: tickets.panel_title || "",
    panel_description: tickets.panel_description || "",
    panel_categories: (tickets.panel_categories || []).join("\n"),
    panel_channel_id: tickets.panel_channel_id ? String(tickets.panel_channel_id) : "",
    support_roles: [...(tickets.support_roles || [])].map(String),
  };
}

export function ServerSettingsView({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const [values, setValues] = useState(() => initialValues(config?.server));
  const [state, setState] = useState(initialSave);

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
    setState({ saving: true, message: "", error: "" });
    const prefixes = values.prefixes.split(/\r?\n|,/).map((prefix) => prefix.trim()).filter(Boolean);
    const categories = values.panel_categories.split(/\r?\n|,/).map((category) => category.trim()).filter(Boolean);
    saveConfig(guildId, "server", {
      prefixes,
      onboarding: {
        welcome_channel: values.welcome_channel,
        welcome_title: values.welcome_title,
        welcome_description: values.welcome_description,
        welcome_color: values.welcome_color,
        welcome_image: values.welcome_image,
        rules_channel: values.rules_channel,
        rules_text: values.rules_text,
        rules_role_id: values.rules_role_id,
      },
      logging: {
        ...values.logging,
        disabled: values.disabled_logging,
      },
      tickets: {
        panel_title: values.panel_title,
        panel_description: values.panel_description,
        panel_categories: categories,
        panel_channel_id: values.panel_channel_id,
        support_roles: values.support_roles,
      },
    }, csrfToken).then((result) => {
      setValues(initialValues(result.config as ServerConfig));
      setState({ saving: false, message: "Server settings saved to Niko.", error: "" });
    }).catch((error) => setState({ saving: false, message: "", error: error instanceof Error ? error.message : "Could not save server settings." }));
  };

  const welcomeChannel = values.welcome_channel;
  const ticketChannel = values.panel_channel_id;
  const welcomeChannels = channelsWithSelected(resources, values.welcome_channel);
  const rulesChannels = channelsWithSelected(resources, values.rules_channel);
  const ticketChannels = channelsWithSelected(resources, values.panel_channel_id);
  const supportRoles = rolesWithSelected(resources, values.support_roles);

  return <>
    <DashHeading eyebrow="Server settings" title="Make Niko fit your room." text="Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here." />
    <div className="settings-intro"><span className="settings-intro-icon"><Icon name="settings" /></span><div><span className="panel-kicker">Server control room</span><strong>{values.prefixes.split(/\r?\n|,/).filter(Boolean).length || 0} command prefixes configured</strong><p>Welcome flows, log destinations, and ticket panels all live here.</p></div><span className="settings-intro-state"><span className="status-dot" /> Per server</span></div>
    <form onSubmit={submit} className="settings-stack server-settings-stack">
      <section className="dash-panel settings-panel"><SectionTitle label="Commands" title="Prefixes" detail="Use one prefix per line. Niko will respond to all of them." icon="terminal" /><Field label="Command prefixes" hint="The default prefix is ."><textarea rows={3} maxLength={200} value={values.prefixes} onChange={(event) => setValue("prefixes", event.target.value)} placeholder=".\n!" /></Field></section>

      <section className="dash-panel settings-panel"><SectionTitle label="Welcome flow" title="Welcome and rules" detail="Choose where new members see your welcome message and rules." icon="users" /><div className="form-grid">
        <Field label="Welcome channel"><select value={welcomeChannel} onChange={(event) => setValue("welcome_channel", event.target.value)}><option value="">Disabled</option>{welcomeChannels.map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}</select></Field>
        <Field label="Welcome title"><input value={values.welcome_title} maxLength={200} onChange={(event) => setValue("welcome_title", event.target.value)} placeholder="Welcome to the server" /></Field>
        <Field label="Welcome message" hint="Supports {user} and {name}"><textarea rows={4} maxLength={2000} value={values.welcome_description} onChange={(event) => setValue("welcome_description", event.target.value)} placeholder="Welcome {user}!" /></Field>
        <Field label="Accent color" hint="Hex color, for example 5865F2"><input value={values.welcome_color} maxLength={7} onChange={(event) => setValue("welcome_color", event.target.value)} placeholder="5865F2" /></Field>
        <Field label="Welcome image URL"><input type="url" value={values.welcome_image} onChange={(event) => setValue("welcome_image", event.target.value)} placeholder="https://..." /></Field>
        <Field label="Rules channel"><select value={values.rules_channel} onChange={(event) => setValue("rules_channel", event.target.value)}><option value="">Not configured</option>{rulesChannels.map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}</select></Field>
        <Field label="Rules text"><textarea rows={4} maxLength={2000} value={values.rules_text} onChange={(event) => setValue("rules_text", event.target.value)} placeholder="Write the rules members should acknowledge." /></Field>
        <Field label="Role after rules acknowledgment"><select value={values.rules_role_id} onChange={(event) => setValue("rules_role_id", event.target.value)}><option value="">No role</option>{rolesWithSelected(resources, values.rules_role_id ? [values.rules_role_id] : []).map((role) => <option value={role.id} key={role.id}>@{role.name}</option>)}</select></Field>
      </div></section>

      <section className="dash-panel settings-panel"><SectionTitle label="Audit trail" title="Logging destinations" detail="Pick a channel for each event type and disable categories you do not need." icon="book" /><div className="server-logging-list">
        {loggingCategories.map(([key, label]) => { const channels = channelsWithSelected(resources, values.logging[key]); return <div className="server-logging-row" key={key}><label className="form-field"><span className="form-label">{label} logs</span><select value={String(values.logging[key] || "")} onChange={(event) => setLoggingChannel(key, event.target.value)}><option value="">Not set</option>{channels.map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}</select></label><label className="setting-row compact-setting-row"><span><strong>Enabled</strong><small>{channelLabel(resources, values.logging[key])}</small></span><input type="checkbox" checked={!values.disabled_logging.includes(key)} onChange={() => toggleLogging(key)} /><i aria-hidden="true" /></label></div>; })}
      </div></section>

      <section className="dash-panel settings-panel"><SectionTitle label="Support desk" title="Ticket panel" detail="Configure the public panel and decide who can handle tickets." icon="users" /><div className="form-grid">
        <Field label="Panel title"><input value={values.panel_title} maxLength={200} onChange={(event) => setValue("panel_title", event.target.value)} placeholder="Open a Ticket" /></Field>
        <Field label="Panel channel"><select value={ticketChannel} onChange={(event) => setValue("panel_channel_id", event.target.value)}><option value="">Keep current panel channel</option>{ticketChannels.map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}</select></Field>
        <Field label="Panel description"><textarea rows={4} maxLength={2000} value={values.panel_description} onChange={(event) => setValue("panel_description", event.target.value)} placeholder="Tell members what the ticket panel is for." /></Field>
        <Field label="Ticket categories" hint="One category per line"><textarea rows={4} value={values.panel_categories} onChange={(event) => setValue("panel_categories", event.target.value)} placeholder="General\nSupport\nReports" /></Field>
        <Field label="Support roles" hint="Hold Ctrl/Cmd to select more than one"><select multiple value={values.support_roles} onChange={(event) => setValue("support_roles", Array.from(event.target.selectedOptions, (option) => option.value))}>{supportRoles.map((role) => <option value={role.id} key={role.id}>@{role.name}</option>)}</select></Field>
      </div><p className="form-hint">Saving panel settings updates the existing posted panel when Niko can find its saved message.</p></section>
      <SaveFooter state={state} />
    </form>
  </>;
}
