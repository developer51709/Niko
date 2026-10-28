import { type CSSProperties, type FormEvent, type ReactElement, type ReactNode, cloneElement, isValidElement, useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { getGuildTickets, saveConfig, saveProfile, updateGuildTicketStatus } from "../../api";
import { Icon } from "../Icon";
import { DiscordMarkdown } from "../DiscordMarkdown";
import { ColorPicker } from "./ColorPicker";
import { Switch } from "./Switch";
import { SettingCard, SettingCards, type SettingCardFlag } from "./SettingCards";
import { RoleSelect } from "./RoleSelect";
import { clearToasts, notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { X } from "lucide-react";
import type { GlobalProfile, GuildConfig, GuildResources, GuildProfile, GuildTicketsResponse, PresetFilter } from "../../types";
import { DashHeading } from "./DashboardViews";
import { navigate } from "../../router";

// Only the in-flight flag belongs in state now: every result is announced with a
// toast (see ../../utils/toast) instead of an inline line in the card footer.
type SaveState = { saving: boolean };
const initialSave: SaveState = { saving: false };

const LABELABLE_CONTROLS = new Set(["input", "select", "textarea"]);

/**
 * A settings field. The label points at its control with `htmlFor` instead of
 * wrapping it, so the click area stays the control itself rather than the label
 * text, the hint, and the rest of the stretched grid cell.
 */
function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  const generatedId = useId();
  const control = isValidElement(children) && typeof children.type === "string" && LABELABLE_CONTROLS.has(children.type)
    ? children as ReactElement<{ id?: string }>
    : null;
  const roleSelect = isValidElement(children) && children.type === RoleSelect
    ? children as ReactElement<{ ariaLabel?: string }>
    : null;
  const controlId = control ? `${generatedId}-control` : undefined;
  return <div className="form-field">
    <label className="form-label" htmlFor={controlId}>{label}</label>
    {control ? cloneElement(control, { id: controlId }) : roleSelect ? cloneElement(roleSelect, { ariaLabel: roleSelect.props.ariaLabel || label }) : children}
    {hint && <small>{hint}</small>}
  </div>;
}

function channelsWithSelected(resources: GuildResources | null, selected: string | number | null | undefined) {
  const selectedId = selected ? String(selected) : "";
  const channels = resources?.channels || [];
  if (!selectedId || channels.some((channel) => String(channel.id) === selectedId)) return channels;
  return [{ id: selectedId, name: `Saved channel · ${selectedId}` }, ...channels];
}

/** Level → role assignments in level order, as editable rows. */
function levelRewardRows(levelRoles: Record<string, string> | undefined) {
  return Object.entries(levelRoles || {})
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([level, role]) => ({ level: String(level), role: String(role) }));
}

function SettingsIntro({ icon, label, title, text, className }: { icon: string; label: string; title: string; text: string; className?: string }) {
  return <div className={`settings-intro${className ? ` ${className}` : ""}`}>
    <span className="settings-intro-icon"><Icon name={icon} /></span>
    <div><span className="panel-kicker">{label}</span><strong>{title}</strong><p>{text}</p></div>
    <span className="settings-intro-state"><span className="status-dot" /> Per server</span>
  </div>;
}

function SettingsSectionTitle({ label, title, detail, icon }: { label: string; title: string; detail?: string; icon?: string }) {
  return <div className="panel-heading settings-section-title">
    <div><span className="panel-kicker">{label}</span><h3>{title}</h3>{detail && <p>{detail}</p>}</div>
    {icon && <span className="panel-icon"><Icon name={icon} /></span>}
  </div>;
}

function SaveFooter({ state }: { state: SaveState }) {
  return <div className="setting-footer"><span>Changes apply to this server.</span><button className="button button-primary" type="submit" disabled={state.saving}>{state.saving ? "Saving…" : "Save changes"}</button></div>;
}

function TicketCategoryList({ categories, onChange }: { categories: string[]; onChange: (value: string[]) => void }) {
  const add = () => onChange([...categories, ""]);
  return <div className="settings-category-editor">
    <div className="settings-option-list">
      {categories.map((category, index) => <div className="settings-option-row" key={`${category}-${index}`}>
        <input aria-label={`Ticket category ${index + 1}`} value={category} maxLength={80} onChange={(event) => onChange(categories.map((item, itemIndex) => itemIndex === index ? event.target.value : item))} placeholder={`Category ${index + 1}`} />
        <button type="button" className="settings-option-remove" onClick={() => onChange(categories.filter((_, itemIndex) => itemIndex !== index))} aria-label={`Remove ticket category ${index + 1}`}>Remove</button>
      </div>)}
    </div>
    <div className="settings-category-actions">
      <button type="button" className="button button-muted button-small settings-option-add" onClick={add}>＋ Add category</button>
    </div>
    <small>Add a separate option for each kind of support request.</small>
  </div>;
}

export function OnboardingView({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const onboarding = config?.server?.onboarding || {};
  const [values, setValues] = useState({ welcome_channel: "", welcome_title: "", welcome_description: "", welcome_color: "#5865f2", welcome_image: "", goodbye_channel: "", goodbye_title: "", goodbye_description: "", goodbye_color: "#ed4245", goodbye_image: "", rules_channel: "", rules_text: "", rules_role_id: "", autorole_ids: [] as string[], bot_autorole_ids: [] as string[], captcha_enabled: false, captcha_channel_id: "", captcha_add_role_ids: [] as string[], captcha_remove_role_ids: [] as string[], captcha_kick_on_fail: false, captcha_mode: "image", captcha_block_proxies: false, captcha_block_vpn: false });
  const [state, setState] = useState(initialSave);
  useEffect(() => setValues({ welcome_channel: onboarding.welcome_channel ? String(onboarding.welcome_channel) : "", welcome_title: onboarding.welcome_title || "", welcome_description: onboarding.welcome_description || "", welcome_color: `#${Number(onboarding.welcome_color ?? 0x5865f2).toString(16).padStart(6, "0")}`, welcome_image: onboarding.welcome_image || "", goodbye_channel: onboarding.goodbye_channel ? String(onboarding.goodbye_channel) : "", goodbye_title: onboarding.goodbye_title || "", goodbye_description: onboarding.goodbye_description || "", goodbye_color: `#${Number(onboarding.goodbye_color ?? 0xed4245).toString(16).padStart(6, "0")}`, goodbye_image: onboarding.goodbye_image || "", rules_channel: onboarding.rules_channel ? String(onboarding.rules_channel) : "", rules_text: onboarding.rules_text || "", rules_role_id: onboarding.rules_role_id ? String(onboarding.rules_role_id) : "", autorole_ids: (onboarding.autorole_ids || []).map(String), bot_autorole_ids: (onboarding.bot_autorole_ids || []).map(String), captcha_enabled: Boolean(onboarding.captcha_enabled), captcha_channel_id: onboarding.captcha_channel_id ? String(onboarding.captcha_channel_id) : "", captcha_add_role_ids: (onboarding.captcha_add_role_ids || []).map(String), captcha_remove_role_ids: (onboarding.captcha_remove_role_ids || []).map(String), captcha_kick_on_fail: Boolean(onboarding.captcha_kick_on_fail), captcha_mode: onboarding.captcha_mode || "image", captcha_block_proxies: Boolean(onboarding.captcha_block_proxies), captcha_block_vpn: Boolean(onboarding.captcha_block_vpn) }), [config]);
  const set = (key: keyof typeof values, value: unknown) => setValues((current) => ({ ...current, [key]: value }));
  const submit = (event: FormEvent) => { event.preventDefault(); setState({ saving: true }); notifyLoading("Saving onboarding settings…", "settings-save"); saveConfig(guildId, "server", { onboarding: { ...values, autorole_ids: values.autorole_ids, bot_autorole_ids: values.bot_autorole_ids, captcha_add_role_ids: values.captcha_add_role_ids, captcha_remove_role_ids: values.captcha_remove_role_ids } }, csrfToken).then(() => { setState({ saving: false }); notifySuccess("Onboarding settings saved.", "settings-save"); }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : "Could not save onboarding settings.", "settings-save"); }); };
  const channels = resources?.channels || [];
  const roles = resources?.roles || [];
  return <><DashHeading eyebrow="Onboarding" title="Make every arrival feel intentional." text="Tune the welcome, goodbye, verification, and role experience for new members and bots." /><SettingsIntro icon="users" label="First impressions" title="A calmer front door" text="Configure the welcome and goodbye messages, rules, captcha, and separate role assignments for people and bots." /><form onSubmit={submit} className="settings-stack guild-feature-settings onboarding-settings-stack"><section className="dash-panel settings-panel"><SettingsSectionTitle label="Welcome" title="Welcome message" detail="Choose the channel and message new members see when they join." icon="users" /><div className="form-grid"><Field label="Welcome channel"><select value={values.welcome_channel} onChange={(event) => set("welcome_channel", event.target.value)}><option value="">Disabled</option>{channels.map((channel) => <option key={channel.id} value={channel.id}>#{channel.name}</option>)}</select></Field><Field label="Welcome title"><input maxLength={200} value={values.welcome_title} onChange={(event) => set("welcome_title", event.target.value)} placeholder="Welcome to the server" /></Field><Field label="Welcome message" hint="Use {user}, {name}, or {guild}"><textarea rows={4} maxLength={2000} value={values.welcome_description} onChange={(event) => set("welcome_description", event.target.value)} placeholder="Welcome {user}!" /></Field><Field label="Welcome accent color" hint="Six-digit hex color, for example 5865F2"><ColorPicker label="Welcome accent color" value={values.welcome_color} onChange={(value) => set("welcome_color", value)} /></Field><Field label="Welcome image URL"><input type="url" value={values.welcome_image} onChange={(event) => set("welcome_image", event.target.value)} placeholder="https://…" /></Field></div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label="Goodbye" title="Goodbye message" detail="Posted in the channel you pick when a member leaves. Leave the channel unset and Niko stays quiet." icon="logout" /><div className="form-grid"><Field label="Goodbye channel"><select value={values.goodbye_channel} onChange={(event) => set("goodbye_channel", event.target.value)}><option value="">Disabled</option>{channelsWithSelected(resources, values.goodbye_channel).map((channel) => <option key={channel.id} value={channel.id}>#{channel.name}</option>)}</select></Field><Field label="Goodbye title"><input maxLength={200} value={values.goodbye_title} onChange={(event) => set("goodbye_title", event.target.value)} placeholder="Goodbye!" /></Field><Field label="Goodbye message" hint="Use {user}, {name}, or {guild}"><textarea rows={4} maxLength={2000} value={values.goodbye_description} onChange={(event) => set("goodbye_description", event.target.value)} placeholder="See you around, {name}." /></Field><Field label="Goodbye accent color" hint="Six-digit hex color, for example ED4245"><ColorPicker label="Goodbye accent color" value={values.goodbye_color} onChange={(value) => set("goodbye_color", value)} /></Field><Field label="Goodbye image URL"><input type="url" value={values.goodbye_image} onChange={(event) => set("goodbye_image", event.target.value)} placeholder="https://…" /></Field></div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label="Join roles" title="Member and bot autoroles" detail="Keep human member roles and bot-specific roles independent." icon="users" /><div className="form-grid"><Field label="Member autoroles" hint="Assigned to people as they join."><RoleSelect roles={roles} value={values.autorole_ids} multiple ariaLabel="Member autoroles" onChange={(value) => set("autorole_ids", value)} /></Field><Field label="Bot autoroles" hint="Assigned only when another bot joins."><RoleSelect roles={roles} value={values.bot_autorole_ids} multiple ariaLabel="Bot autoroles" onChange={(value) => set("bot_autorole_ids", value)} /></Field></div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label="Rules and verification" title="A guided first step" detail="Set a rules channel and optional captcha gate." icon="shield" /><div className="form-grid"><Field label="Rules channel"><select value={values.rules_channel} onChange={(event) => set("rules_channel", event.target.value)}><option value="">Not configured</option>{channelsWithSelected(resources, values.rules_channel).map((channel) => <option key={channel.id} value={channel.id}>#{channel.name}</option>)}</select></Field><Field label="Rules acknowledgment role"><RoleSelect roles={roles} value={values.rules_role_id} placeholder="No role" onChange={(value) => set("rules_role_id", value)} /></Field><Field label="Rules text"><textarea rows={4} maxLength={4000} value={values.rules_text} onChange={(event) => set("rules_text", event.target.value)} placeholder="Write the rules members should acknowledge." /></Field><Field label="Verification panel channel" hint="Save to post or refresh the public Verify panel in this channel."><select value={values.captcha_channel_id} onChange={(event) => set("captcha_channel_id", event.target.value)}><option value="">Not set</option>{channelsWithSelected(resources, values.captcha_channel_id).map((channel) => <option key={channel.id} value={channel.id}>#{channel.name}</option>)}</select></Field><Field label="Verification method" hint={values.captcha_mode === "click" ? "Pressing Verify verifies immediately — no challenge." : values.captcha_mode === "web" ? "Pressing Verify opens a short captcha page on the website." : "Pressing Verify sends a captcha image in DMs."}><select value={values.captcha_mode} onChange={(event) => set("captcha_mode", event.target.value)}><option value="click">One-click verify</option><option value="image">Image captcha in DMs</option><option value="web">Captcha on the website</option></select></Field><Field label="Roles after verification"><RoleSelect roles={roles} value={values.captcha_add_role_ids} multiple ariaLabel="Roles granted after captcha" onChange={(value) => set("captcha_add_role_ids", value)} /></Field><Field label="Roles removed after verification"><RoleSelect roles={roles} value={values.captcha_remove_role_ids} multiple ariaLabel="Roles removed after captcha" onChange={(value) => set("captcha_remove_role_ids", value)} /></Field></div><SettingCards><SettingCard title="Enable captcha verification" hint="Members press Verify in the public panel and complete the method you chose below" action={<Switch checked={values.captcha_enabled} onCheckedChange={(value) => set("captcha_enabled", value)} aria-label="Enable captcha verification" />} /><SettingCard title="Kick members who fail verification" hint="Remove users after their verification attempts are exhausted" action={<Switch checked={values.captcha_kick_on_fail} onCheckedChange={(value) => set("captcha_kick_on_fail", value)} aria-label="Kick members who fail verification" />} /><SettingCard title="Refuse proxies and VPNs" hint="Website method only: refuse open proxies, VPN exits, and Tor" action={<Switch checked={values.captcha_block_proxies} onCheckedChange={(value) => set("captcha_block_proxies", value)} aria-label="Refuse proxy and VPN connections" />} /><SettingCard title="Refuse hosting and datacenter addresses" hint="Website method only: refuse the ranges most VPNs and bypass scripts run from" action={<Switch checked={values.captcha_block_vpn} onCheckedChange={(value) => set("captcha_block_vpn", value)} aria-label="Refuse hosting and datacenter addresses" />} /></SettingCards></section><SaveFooter state={state} /></form></>;
}

export function TicketsView({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const [data, setData] = useState<GuildTicketsResponse | null>(null);
  const [loadingTickets, setLoadingTickets] = useState(true);
  const [ticketError, setTicketError] = useState("");
  const [ticketRetry, setTicketRetry] = useState(0);
  const [savingConfig, setSavingConfig] = useState(false);
  const [ticketFilter, setTicketFilter] = useState<"all" | "open" | "closed">("all");
  const [state, setState] = useState(initialSave);
  const [saving, setSaving] = useState("");
  const tickets = config?.server?.tickets || {};
  const [values, setValues] = useState({ panel_title: "", panel_description: "", panel_color: "#5865f2", panel_image: "", panel_categories: [] as string[], panel_channel_id: "", support_roles: [] as string[] });
  useEffect(() => { let active = true; setLoadingTickets(true); setTicketError(""); setData(null); setState(initialSave); clearToasts("settings-tickets"); getGuildTickets(guildId).then((result) => { if (active) { setData(result); setValues({ panel_title: result.config.panel_title || "", panel_description: result.config.panel_description || "", panel_color: `#${Number(result.config.panel_color ?? 0x5865f2).toString(16).padStart(6, "0")}`, panel_image: result.config.panel_image || "", panel_categories: result.config.panel_categories || [], panel_channel_id: result.config.panel_channel_id || "", support_roles: result.config.support_roles || [] }); } }).catch((error) => { if (active) setTicketError(error instanceof Error ? error.message : "Could not load ticket data."); }).finally(() => { if (active) setLoadingTickets(false); }); return () => { active = false; }; }, [guildId, ticketRetry]);
  useEffect(() => { if (config) setValues({ panel_title: tickets.panel_title || "", panel_description: tickets.panel_description || "", panel_color: `#${Number(tickets.panel_color ?? 0x5865f2).toString(16).padStart(6, "0")}`, panel_image: tickets.panel_image || "", panel_categories: tickets.panel_categories || [], panel_channel_id: tickets.panel_channel_id || "", support_roles: tickets.support_roles || [] }); }, [guildId, config]);
  const submit = (event: FormEvent) => { event.preventDefault(); setSavingConfig(true); setState({ saving: true }); notifyLoading("Saving ticket settings…", "settings-save"); saveConfig(guildId, "server", { tickets: { ...values, panel_categories: values.panel_categories.map((category) => category.trim()).filter(Boolean) } }, csrfToken).then(async () => { const freshData = await getGuildTickets(guildId); setData(freshData); setState({ saving: false }); notifySuccess("Ticket settings saved.", "settings-save"); }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : "Could not save ticket settings.", "settings-save"); }).finally(() => setSavingConfig(false)); };
  const setTicketStatus = (channelId: string, status: "open" | "closed") => {
    setSaving(channelId);
    notifyLoading("Updating ticket…", "settings-tickets");
    updateGuildTicketStatus(guildId, channelId, status, csrfToken)
      .then(async () => { setData(await getGuildTickets(guildId)); notifySuccess(status === "closed" ? "Ticket closed." : "Ticket reopened.", "settings-tickets"); })
      .catch((error) => notifyError(error instanceof Error ? error.message : "Could not update ticket.", "settings-tickets"))
      .finally(() => setSaving(""));
  };
  const channels = resources?.channels || [];
  const roles = resources?.roles || [];
  const filteredTickets = (data?.tickets || []).filter((ticket) => ticketFilter === "all" || (ticket.status || "open") === ticketFilter);
  return <>
    <DashHeading eyebrow="Tickets" title="Support, without losing the thread." text="Manage your ticket panel, check current conversations, and find saved transcripts." />
    <SettingsIntro
      icon="users"
      label="Support desk"
      title={loadingTickets ? "Loading ticket activity…" : ticketError ? "Ticket activity unavailable" : `${data?.tickets.length || 0} current tickets`}
      text={ticketError ? "The queue and transcript history could not be retrieved. Your ticket settings are still available." : "Ticket status and historical transcripts for this server, together in one place."}
    />
    {ticketError && <div className="inline-error" role="alert">
      <strong>Couldn’t load ticket activity.</strong>
      <span>{ticketError}</span>
      <button className="button button-muted" type="button" onClick={() => setTicketRetry((attempt) => attempt + 1)}>Try again</button>
    </div>}
    <form onSubmit={submit} className="settings-stack guild-feature-settings ticket-settings-stack">
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label="Panel" title="Ticket system configuration" detail="Set up the public panel members use to ask for help." icon="settings" />
        <div className="form-grid">
          <Field label="Panel title"><input maxLength={200} value={values.panel_title} onChange={(event) => setValues({ ...values, panel_title: event.target.value })} placeholder="Open a Ticket" /></Field>
          <Field label="Panel channel"><select value={values.panel_channel_id} onChange={(event) => setValues({ ...values, panel_channel_id: event.target.value })}><option value="">Keep current channel</option>{channels.map((channel) => <option key={channel.id} value={channel.id}>#{channel.name}</option>)}</select></Field>
          <Field label="Panel description"><textarea rows={4} maxLength={2000} value={values.panel_description} onChange={(event) => setValues({ ...values, panel_description: event.target.value })} placeholder="Tell members what the ticket panel is for." /></Field>
          <Field label="Panel accent color" hint="Six-digit hex color, for example 5865F2"><ColorPicker label="Ticket panel accent color" value={values.panel_color} onChange={(panel_color) => setValues({ ...values, panel_color })} /></Field>
          <Field label="Panel image URL"><input type="url" value={values.panel_image} onChange={(event) => setValues({ ...values, panel_image: event.target.value })} placeholder="https://…" /></Field>
          <div className="form-grid-wide"><Field label="Ticket categories"><TicketCategoryList categories={values.panel_categories} onChange={(panel_categories) => setValues({ ...values, panel_categories })} /></Field></div>
          <Field label="Support roles"><RoleSelect roles={roles} value={values.support_roles} multiple ariaLabel="Support roles" onChange={(support_roles) => setValues({ ...values, support_roles: Array.isArray(support_roles) ? support_roles : [] })} /></Field>
        </div>
        <div className="setting-footer"><span>Changes apply to this server.</span><button className="button button-primary" type="submit" disabled={savingConfig}>{savingConfig ? "Saving…" : "Save changes"}</button></div>
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label="Live queue" title="Current tickets" detail="Quickly reopen or close a ticket channel." icon="users" />
        <div className="ticket-filter-row" role="group" aria-label="Filter tickets">
          {(["all", "open", "closed"] as const).map((filter) => <button type="button" key={filter} className={ticketFilter === filter ? "button button-secondary is-active" : "button button-quiet"} aria-pressed={ticketFilter === filter} onClick={() => setTicketFilter(filter)}>{filter === "all" ? `All · ${data?.tickets.length || 0}` : `${filter === "open" ? "Open" : "Closed"} · ${(data?.tickets || []).filter((ticket) => (ticket.status || "open") === filter).length}`}</button>)}
        </div>
        {loadingTickets ? <div className="empty-state"><p>Loading current tickets…</p></div>
          : ticketError ? <div className="empty-state"><p>Ticket data is unavailable.</p></div>
          : filteredTickets.length ? <div className="ticket-admin-list">{filteredTickets.map((ticket) => <article className="ticket-admin-row" key={ticket.channel_id}><div><strong>#{ticket.channel_name || `ticket-${ticket.channel_id}`}</strong> <a className="ticket-channel-link" href={`https://discord.com/channels/${guildId}/${ticket.channel_id}`} target="_blank" rel="noreferrer">Open in Discord</a><small>{ticket.category || "General"} · Opened by {ticket.opener_name || ticket.opener_id}{ticket.claimed_by ? ` · Claimed by ${ticket.claimed_by}` : ""}</small></div><span className={`application-status ${ticket.status === "closed" ? "closed" : "open"}`}>{ticket.status || "open"}</span><button className="button button-muted button-small" disabled={saving === ticket.channel_id} type="button" onClick={() => setTicketStatus(ticket.channel_id, ticket.status === "closed" ? "open" : "closed")}>{saving === ticket.channel_id ? "Saving…" : ticket.status === "closed" ? "Reopen" : "Close"}</button></article>)}</div>
          : <div className="empty-state"><p>No tickets are currently recorded for this server.</p></div>}
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label="History" title="Ticket transcripts" detail="Recent transcripts saved by Niko for this server." icon="book" />
        {ticketError ? <div className="empty-state"><p>Transcript history is unavailable until ticket data can be loaded.</p></div>
          : loadingTickets ? <div className="empty-state"><p>Loading transcripts…</p></div>
          : data?.transcripts.length ? <div className="ticket-admin-list">{data.transcripts.map((transcript) => <article className="ticket-admin-row" key={transcript.transcript_id}><div><strong>#{transcript.channel_name}</strong><small>{transcript.category} · Opened by {transcript.opener_id} · {transcript.message_count} messages · {new Date(transcript.created_at).toLocaleString()}</small></div><a className="button button-secondary button-small" href={transcript.url} target="_blank" rel="noreferrer">View transcript</a></article>)}</div>
          : <div className="empty-state"><p>No transcripts have been generated for this server yet.</p></div>}
      </section>
    </form>
  </>;
}

export function ModerationView({ guildId, config, csrfToken }: { guildId: string; config: GuildConfig | null; csrfToken?: string }) {
  const [values, setValues] = useState<Record<string, any>>({});
  const [wordDraft, setWordDraft] = useState("");
  const [state, setState] = useState(initialSave);
  const [presetCatalog, setPresetCatalog] = useState<PresetFilter[]>([]);
  const applyConfig = (moderation: Record<string, any>) => {
    // The preset catalog rides along with the config as reference data. It is
    // kept out of `values` so it is never posted back as a saved setting.
    if (Array.isArray(moderation.preset_filters)) setPresetCatalog(moderation.preset_filters);
    setValues({
      automod: { ...(moderation.automod || {}) },
      // Word entries arrive as text; the API normalizes them again on save.
      blocked_words: (moderation.blocked_words || []).map(String),
      badwords_presets: (moderation.badwords_presets || []).map(String),
      badwords_action: moderation.badwords_action === "censor" ? "censor" : "delete",
      badwords_mask: moderation.badwords_mask ?? "*",
      spam_threshold: moderation.spam_threshold ?? 6,
      spam_interval: moderation.spam_interval ?? 7,
      max_mentions: moderation.max_mentions ?? 5,
      antinuke: { ...(moderation.antinuke || {}) },
      antiraid: { ...(moderation.antiraid || {}) },
      antiraid_ext: { ...(moderation.antiraid_ext || {}) },
    });
  };
  useEffect(() => { applyConfig(config?.moderation || {}); }, [config]);
  const updateNested = (section: string, key: string, value: unknown) => setValues((current) => ({ ...current, [section]: { ...current[section], [key]: value } }));
  const blockedWords: string[] = values.blocked_words || [];
  const addBlockedWord = () => {
    const word = wordDraft.trim().toLowerCase();
    setWordDraft("");
    if (!word || blockedWords.includes(word)) return;
    setValues({ ...values, blocked_words: [...blockedWords, word] });
  };
  const removeBlockedWord = (word: string) => setValues({ ...values, blocked_words: blockedWords.filter((entry) => entry !== word) });
  const enabledPresets: string[] = values.badwords_presets || [];
  const togglePreset = (key: string) => setValues({
    ...values,
    badwords_presets: enabledPresets.includes(key)
      ? enabledPresets.filter((entry) => entry !== key)
      : [...enabledPresets, key],
  });
  const submit = (event: FormEvent) => {
    event.preventDefault(); setState({ saving: true }); notifyLoading("Saving moderation settings…", "settings-save");
    saveConfig(guildId, "automod", values, csrfToken).then((result) => {
      applyConfig(result.config || {});
      setState({ saving: false }); notifySuccess("Moderation settings saved to Niko.", "settings-save");
    }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : "Could not save settings.", "settings-save"); });
  };
  const flags = [["antispam", "Anti-spam", "Detect repeated messages"], ["antilink", "Invite links", "Remove Discord invite links"], ["badwords", "Blocked words", "Filter the words listed below"], ["massmention", "Mass mentions", "Limit mention floods"], ["scam_image_filter", "Scam image filter", "Delete known MrBeast scam images"], ["nsfw_image_filter", "NSFW image filter", "AI-detect and delete NSFW images"], ["antinuke", "Anti-nuke", "Protect channels and roles"], ["antiraid", "Join raid protection", "React to sudden join waves"], ["antiraid_ext", "External app protection", "Detect user-installed app abuse"]] as const;
  // Only the scam-image filter is still experimental. The NSFW filter runs on
  // fal.ai's dedicated model behind premium, so it no longer carries the badge.
  const experimentalFlags = new Set(["scam_image_filter"]);
  const activeFlags = flags.filter(([key]) => Boolean(values.automod?.[key])).length;
  // Premium entitlement comes from the config payload, so the toggle and the
  // upgrade link always agree with what the bot will actually run.
  const premium = config?.premium;
  const premiumActive = Boolean(premium?.active);
  const premiumUntil = premium?.expires_at
    ? new Date(premium.expires_at.replace(" ", "T") + "Z").toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" })
    : null;
  return <>
    <DashHeading eyebrow="Moderation" title="Keep the room feeling good." text="Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration." />
    <SettingsIntro icon="shield" label="Protection desk" title={`${activeFlags} of ${flags.length} safeguards active`} text="Start with the essentials, then tune thresholds below when you know the room’s rhythm." />
    <form onSubmit={submit} className="settings-stack">
      <section className={`dash-panel settings-panel premium-banner${premiumActive ? " is-active" : ""}`} aria-label="Niko Premium">
        <div className="premium-banner-copy">
          <span className="panel-kicker">Niko Premium</span>
          <strong>{premiumActive ? `AI image moderation is active${premiumUntil ? ` until ${premiumUntil}` : ""}` : "AI image moderation is a premium perk"}</strong>
          <p>{premiumActive ? "Every image in this server is scored by fal.ai's NSFW model and removed when it crosses the threshold." : "Upgrade this server to run fal.ai NSFW detection on every image. Billed monthly, cancel by not renewing."}</p>
        </div>
        <button type="button" className={`button ${premiumActive ? "button-muted" : "button-primary"} button-small`} onClick={() => navigate(`/billing?guild=${guildId}`)}>
          {premiumActive ? "Manage premium" : "Upgrade — $15/mo"}
        </button>
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label="Protection rules" title="AutoMod modules" detail="Toggle only the responses you want Niko to handle." icon="shield" />
        <SettingCards>
          {flags.map(([key, label, hint]) => {
            const premiumFlag = key === "nsfw_image_filter";
            const locked = premiumFlag && !premiumActive;
            const cardFlags: SettingCardFlag[] = [];
            if (experimentalFlags.has(key)) cardFlags.push("experimental");
            if (premiumFlag) cardFlags.push("premium");
            return <SettingCard
              key={key}
              title={label}
              hint={hint}
              flags={cardFlags}
              locked={locked}
              action={<Switch checked={Boolean(values.automod?.[key])} disabled={locked} onCheckedChange={(value) => updateNested("automod", key, value)} aria-label={label} />}
            />;
          })}
        </SettingCards>
        {experimentalFlags.size > 0 && <p className="setting-note setting-card-note">The scam image filter is still in early testing and may have some reliability issues.</p>}
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label="Word filter" title="Blocked words" detail="Niko handles messages containing these words when the “Blocked words” switch above is on." icon="shield" />
        <div className="settings-category-editor">
          <div className="settings-option-list">
            {blockedWords.length === 0 && <p className="setting-note">No blocked words yet — add one below. The same list is editable with <code>!badwords</code> in Discord.</p>}
            {blockedWords.map((word) => <div className="settings-option-row blocked-word-row" key={word}>
              <code className="blocked-word-value">{word}</code>
              <button type="button" className="settings-option-remove" onClick={() => removeBlockedWord(word)} aria-label={`Remove the blocked word ${word}`}>Remove</button>
            </div>)}
          </div>
          <div className="settings-category-actions blocked-word-actions">
            <input
              value={wordDraft}
              maxLength={60}
              placeholder="Add a word or phrase"
              aria-label="Add a blocked word"
              onChange={(event) => setWordDraft(event.target.value)}
              onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); addBlockedWord(); } }}
            />
            <button type="button" className="button button-muted button-small settings-option-add" onClick={addBlockedWord} disabled={!wordDraft.trim()}>＋ Add word</button>
          </div>
          <div className="form-grid">
            <Field label="Response" hint="What Niko does with a message that uses a blocked word">
              <select value={values.badwords_action || "delete"} onChange={(event) => setValues({ ...values, badwords_action: event.target.value })}>
                <option value="delete">Delete the message</option>
                <option value="censor">Censor &amp; repost it</option>
              </select>
            </Field>
            {values.badwords_action === "censor" && <Field label="Censor mask" hint="Replaces each blocked word; a single character repeats to match its length">
              <input value={values.badwords_mask ?? "*"} maxLength={16} placeholder="*" onChange={(event) => setValues({ ...values, badwords_mask: event.target.value })} />
            </Field>}
          </div>
          {values.badwords_action === "censor" && <p className="setting-note">Censoring deletes the flagged message and reposts the text through a webhook in that channel using the member&apos;s name and avatar, so Niko needs <strong>Manage Webhooks</strong> in the channels you want censored. If the webhook cannot be created the message is deleted instead.</p>}
          <small>Matching is whole-word and case-insensitive, like Discord: blocking <code>ass</code> leaves “class” and “grass” alone. End a word with <code>*</code> to also catch longer forms (<code>fuck*</code> blocks “fucking”), and wrap it as <code>*word*</code> to match it anywhere. Separators between letters are ignored, so <code>a.s.s</code> is still caught.</small>
        </div>
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label="Preset filters" title="Curated regex filters" detail="Turn on ready-made filters for slurs and other content. Each one is a regular expression, so it also catches the spellings people use to slip past a word list." icon="shield" />
        {presetCatalog.length === 0
          ? <p className="setting-note">Preset filters are unavailable right now — reload the page to try again.</p>
          : <SettingCards>
            {presetCatalog.map((preset) => <SettingCard
              key={preset.key}
              title={preset.label}
              hint={preset.description}
              action={<Switch checked={enabledPresets.includes(preset.key)} onCheckedChange={() => togglePreset(preset.key)} aria-label={preset.label} />}
            />)}
          </SettingCards>}
        <p className="setting-note setting-card-note">Presets run with the same response as the word list above: delete the message, or censor and repost it. They tolerate leet substitutions (<code>n1gg3r</code>), separators (<code>n i g g e r</code>), repeated letters, self-censored letters (<code>sh*t</code>), look-alike unicode characters and fullwidth forms — while leaving ordinary words such as “class”, “analysis” and “spices” untouched. Matching is deliberately aggressive: a term is blocked wherever it stands on its own, so “Niger” on its own trips the slur preset.</p>
      </section>
      <section className="dash-panel settings-panel"><SettingsSectionTitle label="Thresholds" title="Choose when protection steps in" detail="These limits apply across the server." /><div className="form-grid">
        <Field label="Spam messages" hint="Messages inside the spam interval"><input type="number" min="1" max="100" value={values.spam_threshold ?? 6} onChange={(e) => setValues({ ...values, spam_threshold: e.target.value })} /></Field>
        <Field label="Spam interval (seconds)"><input type="number" min="1" max="3600" value={values.spam_interval ?? 7} onChange={(e) => setValues({ ...values, spam_interval: e.target.value })} /></Field>
        <Field label="Maximum mentions"><input type="number" min="1" max="100" value={values.max_mentions ?? 5} onChange={(e) => setValues({ ...values, max_mentions: e.target.value })} /></Field>
        <Field label="Anti-raid joins" hint="Joins inside the join interval"><input type="number" min="1" max="1000" value={values.antiraid?.join_threshold ?? 10} onChange={(e) => updateNested("antiraid", "join_threshold", e.target.value)} /></Field>
        <Field label="Anti-raid interval (seconds)"><input type="number" min="1" max="3600" value={values.antiraid?.join_interval ?? 10} onChange={(e) => updateNested("antiraid", "join_interval", e.target.value)} /></Field>
        <Field label="Anti-raid action"><select value={values.antiraid?.action ?? "kick"} onChange={(e) => updateNested("antiraid", "action", e.target.value)}><option value="kick">Kick</option><option value="ban">Ban</option><option value="softban">Soft-ban</option><option value="slowmode">Slowmode</option><option value="lockdown">Lockdown</option></select></Field>
        <Field label="New-account filter (days)" hint="Act on members whose account is younger than this; 0 turns the filter off"><input type="number" min="0" max="365" value={values.antiraid?.new_account_days ?? 0} onChange={(e) => updateNested("antiraid", "new_account_days", e.target.value)} /></Field>
        <Field label="Lockdown slowmode (seconds)" hint="Applied to every channel when the anti-raid action is “Lockdown”"><input type="number" min="1" max="21600" value={values.antiraid?.lockdown_slowmode ?? 30} onChange={(e) => updateNested("antiraid", "lockdown_slowmode", e.target.value)} /></Field>
      </div></section>
      <section className="dash-panel settings-panel"><SettingsSectionTitle label="Anti-nuke" title="Stop a mass wipe" detail="Niko follows audit-log actions from one moderator and responds when a limit is crossed. Every one of these is also editable with /automod in Discord." icon="shield" /><div className="form-grid">
        <Field label="Bans"><input type="number" min="1" max="100" value={values.antinuke?.ban_threshold ?? 3} onChange={(e) => updateNested("antinuke", "ban_threshold", e.target.value)} /></Field>
        <Field label="Kicks"><input type="number" min="1" max="100" value={values.antinuke?.kick_threshold ?? 3} onChange={(e) => updateNested("antinuke", "kick_threshold", e.target.value)} /></Field>
        <Field label="Channel deletes"><input type="number" min="1" max="100" value={values.antinuke?.channel_delete_threshold ?? 3} onChange={(e) => updateNested("antinuke", "channel_delete_threshold", e.target.value)} /></Field>
        <Field label="Role deletes"><input type="number" min="1" max="100" value={values.antinuke?.role_delete_threshold ?? 3} onChange={(e) => updateNested("antinuke", "role_delete_threshold", e.target.value)} /></Field>
        <Field label="Channel creates"><input type="number" min="1" max="100" value={values.antinuke?.channel_create_threshold ?? 5} onChange={(e) => updateNested("antinuke", "channel_create_threshold", e.target.value)} /></Field>
        <Field label="Webhook deletes"><input type="number" min="1" max="100" value={values.antinuke?.webhook_delete_threshold ?? 3} onChange={(e) => updateNested("antinuke", "webhook_delete_threshold", e.target.value)} /></Field>
        <Field label="Interval (seconds)" hint="The window these actions are counted in"><input type="number" min="1" max="3600" value={values.antinuke?.interval ?? 10} onChange={(e) => updateNested("antinuke", "interval", e.target.value)} /></Field>
        <Field label="Action"><select value={values.antinuke?.action ?? "strip"} onChange={(e) => updateNested("antinuke", "action", e.target.value)}><option value="strip">Strip dangerous roles</option><option value="kick">Kick the offender</option><option value="ban">Ban the offender</option></select></Field>
      </div></section>
      <section className="dash-panel settings-panel"><SettingsSectionTitle label="External apps" title="Limit what new members can trigger" detail="Detects coordinated interaction floods from freshly joined members and abuse of user-installed apps." icon="shield" /><div className="form-grid">
        <Field label="Flood: unique members" hint="Newly joined members triggering interactions at the same time"><input type="number" min="1" max="1000" value={values.antiraid_ext?.interaction_threshold ?? 5} onChange={(e) => updateNested("antiraid_ext", "interaction_threshold", e.target.value)} /></Field>
        <Field label="Flood: window (seconds)"><input type="number" min="1" max="3600" value={values.antiraid_ext?.interaction_window ?? 30} onChange={(e) => updateNested("antiraid_ext", "interaction_window", e.target.value)} /></Field>
        <Field label="Count as new for (seconds)" hint="How long after joining a member still counts as new"><input type="number" min="1" max="86400" value={values.antiraid_ext?.join_age_limit ?? 120} onChange={(e) => updateNested("antiraid_ext", "join_age_limit", e.target.value)} /></Field>
        <Field label="Raider action"><select value={values.antiraid_ext?.raider_action ?? "kick"} onChange={(e) => updateNested("antiraid_ext", "raider_action", e.target.value)}><option value="kick">Kick</option><option value="ban">Ban</option></select></Field>
        <Field label="Operator action"><select value={values.antiraid_ext?.operator_action ?? "notify"} onChange={(e) => updateNested("antiraid_ext", "operator_action", e.target.value)}><option value="notify">Notify only</option><option value="kick">Kick</option><option value="ban">Ban</option></select></Field>
        <Field label="App abuse: commands per member"><input type="number" min="1" max="1000" value={values.antiraid_ext?.ext_app_threshold ?? 3} onChange={(e) => updateNested("antiraid_ext", "ext_app_threshold", e.target.value)} /></Field>
        <Field label="App abuse: window (seconds)"><input type="number" min="1" max="3600" value={values.antiraid_ext?.ext_app_window ?? 15} onChange={(e) => updateNested("antiraid_ext", "ext_app_window", e.target.value)} /></Field>
        <Field label="App abuse: action"><select value={values.antiraid_ext?.ext_app_action ?? "kick"} onChange={(e) => updateNested("antiraid_ext", "ext_app_action", e.target.value)}><option value="kick">Kick</option><option value="ban">Ban</option><option value="warn">Warn</option><option value="log">Log only</option></select></Field>
      </div></section>
      <SaveFooter state={state} />
    </form>
  </>;
}

export function AiView({ guildId, config, csrfToken }: { guildId: string; config: GuildConfig | null; csrfToken?: string }) {
  const [values, setValues] = useState({ ai_name: "Niko", personality: "cafe", enabled: true, ai_actions_experiment: false, better_context_experiment: false, multimodal_experiment: false });
  const [state, setState] = useState(initialSave);
  const [learnMore, setLearnMore] = useState<string | null>(null);
  const readBool = (value: unknown) => value === true || value === "True";
  const applyConfig = (ai: Record<string, any>) => setValues({ ai_name: ai.ai_name || "Niko", personality: ai.personality === "normal" ? "normal" : "cafe", enabled: ai.enabled !== "False" && ai.enabled !== false, ai_actions_experiment: readBool(ai.ai_actions_experiment), better_context_experiment: readBool(ai.better_context_experiment), multimodal_experiment: readBool(ai.multimodal_experiment) });
  useEffect(() => applyConfig(config?.ai || {}), [config]);
  const submit = (event: FormEvent) => { event.preventDefault(); setState({ saving: true }); notifyLoading("Saving AI settings…", "settings-save"); saveConfig(guildId, "ai", values, csrfToken).then((result) => { applyConfig(result.config || {}); setState({ saving: false }); notifySuccess("AI settings saved.", "settings-save"); }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : "Could not save settings.", "settings-save"); }); };
  const experiments = [{ key: "better_context_experiment", title: "Better context", hint: "Use the last five channel messages", info: "Adds recent conversation and replied-to message context so responses understand ongoing discussions more naturally. It is useful for follow-ups, but sends more conversation context to the AI provider." }, { key: "ai_actions_experiment", title: "AI actions", hint: "Allow confirmed actions requested in chat", info: "Lets the AI propose polls and server actions such as moderation or channel management. Every action requires confirmation and is still limited by Discord permissions." }, { key: "multimodal_experiment", title: "Multimodal conversation", hint: "Understand images and voice in AI replies", info: "Allows Niko to inspect image attachments and use voice-message transcriptions as context when the AI is already triggered by name, ping, or the ai command. Attachments never start a conversation on their own. Media is processed only while enabled and provider usage costs may apply." }] as const;
  return <><DashHeading eyebrow="AI controls" title="Give your AI the right tone." text="Configure the AI identity, personality, and opt-in experiments for this server." /><SettingsIntro icon="settings" label="Conversation desk" title={values.enabled ? `${values.ai_name} is ready to respond` : `${values.ai_name} is staying quiet`} text="All settings apply only to this server." /><form onSubmit={submit} className="settings-stack"><section className="dash-panel settings-panel"><SettingsSectionTitle label="Conversation" title="Core settings" detail="Decide when the AI joins the conversation." icon="settings" /><div className="form-grid"><Field label="AI name" hint="3–32 characters; this is also the mention trigger"><input value={values.ai_name} minLength={3} maxLength={32} onChange={(e) => setValues({ ...values, ai_name: e.target.value })} /></Field></div><SettingCards><SettingCard title="Enable AI chat" hint="Respond when the configured name is mentioned" action={<Switch checked={values.enabled} onCheckedChange={(value) => setValues({ ...values, enabled: value })} aria-label="Enable AI chat" />} /></SettingCards><div className="personality-options"><button type="button" className={values.personality === "cafe" ? "personality active" : "personality"} onClick={() => setValues({ ...values, personality: "cafe" })}><span className="personality-mark">n</span><span><strong>Café</strong><small>Warm, playful, familiar</small></span></button><button type="button" className={values.personality === "normal" ? "personality active" : "personality"} onClick={() => setValues({ ...values, personality: "normal" })}><span className="personality-mark">—</span><span><strong>Normal</strong><small>Clear and straightforward</small></span></button></div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label="Experiments" title="Optional capabilities" detail="Each experiment includes a learn-more explanation before you enable it." /><SettingCards stacked>{experiments.map((experiment) => <SettingCard key={experiment.key} title={experiment.title} hint={experiment.hint} action={<><button type="button" className="button button-secondary" onClick={() => setLearnMore(experiment.key)}>Learn more</button><Switch size="sm" checked={values[experiment.key]} onCheckedChange={(value) => setValues({ ...values, [experiment.key]: value })} aria-label={`Enable ${experiment.title}`} /></>} />)}</SettingCards><SaveFooter state={state} /></section></form>{learnMore && <div className="modal-backdrop" role="presentation" onClick={() => setLearnMore(null)}><div className="modal-card" role="dialog" aria-modal="true" aria-labelledby="ai-experiment-title" onClick={(e) => e.stopPropagation()}><div className="panel-heading"><div><span className="panel-kicker">AI experiment</span><h3 id="ai-experiment-title">{experiments.find((item) => item.key === learnMore)?.title}</h3></div><button type="button" className="button button-secondary" onClick={() => setLearnMore(null)}>Close</button></div><p>{experiments.find((item) => item.key === learnMore)?.info}</p></div></div>}</>;
}

export function LevelingSettings({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const level = config?.leveling || {};
  const [values, setValues] = useState({ xp_enabled: true, xp_multiplier: 1, xp_cooldown: 0, level_up_channel: "", level_up_message: "", xp_excluded_channels: [] as string[], xp_vc_enabled: false });
  const [rewards, setRewards] = useState<{ level: string; role: string }[]>([]);
  const [state, setState] = useState(initialSave);
  const applyConfig = (next: GuildConfig["leveling"]) => setValues({
    xp_enabled: next.xp_enabled !== false,
    xp_multiplier: next.xp_multiplier ?? 1,
    xp_cooldown: next.xp_cooldown ?? 0,
    level_up_channel: next.level_up_channel ? String(next.level_up_channel) : "",
    level_up_message: next.level_up_message || "",
    xp_excluded_channels: (next.xp_excluded_channels || []).map(String),
    xp_vc_enabled: next.xp_vc_enabled === true,
  });
  const applyRewards = (levelRoles: Record<string, string> | undefined) => setRewards(levelRewardRows(levelRoles));
  useEffect(() => { applyConfig(level); applyRewards(level.level_roles); }, [config]);
  const submit = (event: FormEvent) => { event.preventDefault(); setState({ saving: true }); notifyLoading("Saving leveling settings…", "settings-save"); saveConfig(guildId, "leveling", { ...values, level_roles: rewardPayload }, csrfToken).then((result) => { applyConfig(result.config || {}); applyRewards((result.config || {}).level_roles); setState({ saving: false }); notifySuccess("Leveling settings saved to Niko.", "settings-save"); }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : "Could not save settings.", "settings-save"); }); };
  const levelUpChannels = channelsWithSelected(resources, values.level_up_channel);
  const channels = [...(resources?.channels || []), ...(resources?.voice_channels || []).map((channel) => ({ ...channel, name: `🔊 ${channel.name}` }))];
  const channelName = (id: string) => channels.find((channel) => String(channel.id) === id)?.name || `Channel ${id}`;
  const toggleExcluded = (id: string) => setValues({ ...values, xp_excluded_channels: values.xp_excluded_channels.includes(id) ? values.xp_excluded_channels.filter((selected) => selected !== id) : [...values.xp_excluded_channels, id] });
  const roles = resources?.roles || [];
  // Rows the member has not finished filling in are dropped rather than sent.
  const rewardPayload = Object.fromEntries(rewards.filter((row) => row.level.trim() && row.role).map((row) => [String(Number(row.level)), row.role]));
  const updateReward = (index: number, patch: Partial<{ level: string; role: string }>) => setRewards(rewards.map((row, rowIndex) => rowIndex === index ? { ...row, ...patch } : row));
  return <><SettingsIntro className="leveling-settings-intro" icon="spark" label="Participation desk" title={values.xp_enabled ? "XP is flowing" : "XP is paused"} text="Set a pace that rewards regulars without turning every message into a transaction." /><form onSubmit={submit} className="settings-stack"><section className="dash-panel settings-panel"><SettingsSectionTitle label="Leveling settings" title="Shape the pace" detail="These controls apply to every member in this server." icon="spark" /><SettingCards><SettingCard title="Enable XP" hint="Track activity and award levels" action={<Switch checked={values.xp_enabled} onCheckedChange={(value) => setValues({ ...values, xp_enabled: value })} aria-label="Enable XP" />} /></SettingCards><div className="form-grid"><Field label="XP multiplier" hint="From 0.1× to 10×"><input type="number" min="0.1" max="10" step="0.1" value={values.xp_multiplier} onChange={(e) => setValues({ ...values, xp_multiplier: e.target.value as unknown as number })} /></Field><Field label="Cooldown (seconds)" hint="0 disables the cooldown"><input type="number" min="0" max="86400" value={values.xp_cooldown} onChange={(e) => setValues({ ...values, xp_cooldown: e.target.value as unknown as number })} /></Field><Field label="Level-up channel"><select value={values.level_up_channel} onChange={(e) => setValues({ ...values, level_up_channel: e.target.value })}><option value="">Same channel</option>{levelUpChannels.map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}</select></Field>        <Field label="Level-up message" hint="Use {mention}, {level}, {name}, or {guild}"><textarea rows={3} maxLength={1000} value={values.level_up_message} onChange={(e) => setValues({ ...values, level_up_message: e.target.value })} placeholder="Leave blank for Niko's default message" />{values.level_up_message.trim() && <DiscordMarkdown text={values.level_up_message.replace(/\{mention\}/g, "@member").replace(/\{level\}/g, "12").replace(/\{name\}/g, "member").replace(/\{guild\}/g, "your server")} className="role-select-preview" interactiveUsers={false} />}</Field>
</div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label="Channels & voice" title="Choose where XP counts" detail="Excluded channels never award XP, and ticket channels are always excluded automatically." icon="settings" /><SettingCards><SettingCard title="Voice XP" hint="Earn XP for every minute spent in a voice channel. AFK channels never count." action={<Switch checked={values.xp_vc_enabled} onCheckedChange={(value) => setValues({ ...values, xp_vc_enabled: value })} aria-label="Enable voice XP" />} /></SettingCards><Field label="Excluded channels" hint="Select the channels that should never award XP."><div className="role-select role-select-multiple"><span className="role-select-control"><select multiple value={values.xp_excluded_channels} onChange={(event) => setValues({ ...values, xp_excluded_channels: Array.from(event.currentTarget.selectedOptions, (option) => option.value) })} size={Math.min(Math.max(channels.length, 3), 7)} aria-label="Channels excluded from XP">{channels.map((channel) => <option key={channel.id} value={channel.id}>#{channel.name}</option>)}</select></span>{values.xp_excluded_channels.length > 0 && <div className="role-select-selected" aria-label={`${values.xp_excluded_channels.length} channels excluded from XP`}>{values.xp_excluded_channels.map((id) => <span className="role-select-chip" key={id}>#{channelName(id)}<button type="button" onClick={() => toggleExcluded(id)} aria-label={`Stop excluding #${channelName(id)}`}><X size={12} aria-hidden="true" /></button></span>)}</div>}</div></Field></section><section className="dash-panel settings-panel"><SettingsSectionTitle label="Rewards" title="Level role rewards" detail="Niko grants these roles automatically when a member reaches the level. The same list is editable with /leveling panel in Discord." icon="spark" /><div className="settings-category-editor"><div className="settings-option-list">{rewards.map((row, index) => <div className="settings-option-row level-role-row" key={`${row.role}-${index}`}><input aria-label={`Reward level ${index + 1}`} type="number" min="1" max="1000" value={row.level} onChange={(event) => updateReward(index, { level: event.target.value })} placeholder="Level" /><RoleSelect roles={roles} value={row.role} placeholder="Choose a role" ariaLabel={`Role awarded at level ${row.level || index + 1}`} onChange={(value) => updateReward(index, { role: String(value) })} /><button type="button" className="settings-option-remove" onClick={() => setRewards(rewards.filter((_, rowIndex) => rowIndex !== index))} aria-label={`Remove the level ${row.level || index + 1} reward`}>Remove</button></div>)}</div><div className="settings-category-actions"><button type="button" className="button button-muted button-small settings-option-add" onClick={() => setRewards([...rewards, { level: "", role: "" }])}>＋ Add level reward</button></div><small>Members keep roles they have already earned, so removing a reward here stops Niko from awarding it but does not take it back.</small></div></section><SaveFooter state={state} /></form></>;
}

export function CustomizationSettings({ guildId, config, csrfToken }: { guildId: string; config: GuildConfig | null; csrfToken?: string }) {
  const profile = config?.server?.profile || {};
  // A server inherits Niko's global avatar and banner until it sets its own.
  const globalProfile: GlobalProfile = config?.server?.global_profile || {};
  const [values, setValues] = useState({
    display_name: profile.display_name || "",
    bio: profile.bio || "",
    avatar_url: profile.avatar_url || "",
    banner_url: profile.banner_url || "",
    avatar_upload_data: "",
    banner_upload_data: "",
    name_font_id: profile.name_font_id ?? 11,
    name_effect_id: profile.name_effect_id ?? 2,
    name_colors: profile.name_colors?.length ? profile.name_colors : [5793266, 5763719],
  });
  const [state, setState] = useState(initialSave);
  useEffect(() => {
    const p = config?.server?.profile || {};
    setValues({
      display_name: p.display_name || "",
      bio: p.bio || "",
      avatar_url: p.avatar_url || "",
      banner_url: p.banner_url || "",
      avatar_upload_data: "",
      banner_upload_data: "",
      name_font_id: p.name_font_id ?? 11,
      name_effect_id: p.name_effect_id ?? 2,
      name_colors: p.name_colors?.length ? p.name_colors : [5793266, 5763719],
    });
  }, [config]);
  const submit = (event: FormEvent) => {
    event.preventDefault(); setState({ saving: true }); notifyLoading("Saving profile…", "settings-save");
    saveProfile(guildId, {
      display_name: values.display_name || null,
      bio: values.bio || null,
      avatar_url: values.avatar_url || null,
      banner_url: values.banner_url || null,
      name_font_id: values.name_font_id,
      name_effect_id: values.name_effect_id,
      ...(values.avatar_upload_data ? { avatar_upload_data: values.avatar_upload_data } : {}),
      ...(values.banner_upload_data ? { banner_upload_data: values.banner_upload_data } : {}),
      name_colors: values.name_effect_id === 2
        ? [values.name_colors[0] ?? 5793266, values.name_colors[1] ?? 5763719]
        : values.name_effect_id === 6
          ? values.name_colors.slice(0, 2)
          : values.name_colors.slice(0, 1),
    }, csrfToken).then((result) => {
      const p = result.profile || {};
      setValues({
        display_name: p.display_name || "",
        bio: p.bio || "",
        avatar_url: p.avatar_url || "",
        banner_url: p.banner_url || "",
        avatar_upload_data: "",
        banner_upload_data: "",
        name_font_id: p.name_font_id ?? 11,
        name_effect_id: p.name_effect_id ?? 2,
        name_colors: p.name_colors?.length ? p.name_colors : [5793266, 5763719],
      });setImageChoice(null); setState({ saving: false }); notifySuccess("Bot profile updated.", "settings-save");
    }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : "Could not save profile.", "settings-save"); });
  };
  const [editor, setEditor] = useState<"avatar" | "banner" | "name" | "bio" | null>(null);
  const [imageChoice, setImageChoice] = useState<"avatar" | "banner" | null>(null);
  const [imageSource, setImageSource] = useState<"file" | "url">("file");
  const avatarFileRef = useRef<HTMLInputElement>(null);
  const bannerFileRef = useRef<HTMLInputElement>(null);
  const [nameSettings, setNameSettings] = useState({ font: values.name_font_id, effect: values.name_effect_id, colors: values.name_colors });
  const updateValues = (patch: Partial<typeof values>) => setValues((current) => ({ ...current, ...patch }));
  const chooseImage = (kind: "avatar" | "banner") => { setImageChoice(kind); setImageSource("file"); };
  const readImageFile = (kind: "avatar" | "banner", file?: File) => {
    if (!file) return;
    if (!file.type.startsWith("image/")) { notifyError("Choose an image file.", "profile-image"); return; }
    if (file.size > 8 * 1024 * 1024) { notifyError("Images must be 8 MB or smaller.", "profile-image"); return; }
    const reader = new FileReader();
    reader.onload = () => {
      const data = typeof reader.result === "string" ? reader.result : "";
      if (kind === "avatar") updateValues({ avatar_upload_data: data });
      else updateValues({ banner_upload_data: data });
      setImageChoice(null);
      clearToasts("profile-image");
    };
    reader.onerror = () => notifyError("Could not read that image file.", "profile-image");
    reader.readAsDataURL(file);
  };
  const colors = nameSettings.colors || [];
  const colorHex = (value: number) => `#${Math.max(0, Math.min(0xffffff, value)).toString(16).padStart(6, "0")}`;
  const colorOptions = [{ label: "White", value: 16777215 }, { label: "Black", value: 0 }, { label: "Blurple", value: 5793266 }, { label: "Green", value: 5763719 }, { label: "Red", value: 15548997 }, { label: "Yellow", value: 16705372 }, { label: "Pink", value: 16711935 }, { label: "Purple", value: 8388736 }, { label: "Blue", value: 5865 }, { label: "Gold", value: 16766720 }, { label: "Cyan", value: 65535 }];
  const nameStyle: CSSProperties = {};
  if (values.name_colors?.length && values.name_effect_id === 2) {
    nameStyle.backgroundImage = `linear-gradient(90deg, ${values.name_colors.map(colorHex).join(", ")})`;
    nameStyle.color = "transparent";
    nameStyle.backgroundClip = "text";
  } else if (values.name_colors?.length) {
    nameStyle.color = colorHex(values.name_colors[0]);
  }
  const previewNameSettings = { ...nameSettings, colors };
  const namePreviewStyle: CSSProperties = {};
  if (previewNameSettings.colors.length && previewNameSettings.effect === 2) {
    namePreviewStyle.backgroundImage = `linear-gradient(90deg, ${previewNameSettings.colors.map(colorHex).join(", ")})`;
    namePreviewStyle.color = "transparent";
    namePreviewStyle.backgroundClip = "text";
  } else if (previewNameSettings.colors.length) {
    namePreviewStyle.color = colorHex(previewNameSettings.colors[0]);
  }
  // Empty strings rather than nullable URLs: they feed an <img src> and a
  // background-image, which do not accept null.
  const inheritedAvatar = globalProfile.avatar_url || "";
  const inheritedBanner = globalProfile.banner_url || "";
  // True while every image in this server's preview still comes from Niko's global profile.
  const inheritsGlobalImages = !values.avatar_upload_data && !values.avatar_url && !values.banner_upload_data && !values.banner_url && Boolean(inheritedAvatar || inheritedBanner);
  return <>
    <DashHeading eyebrow="Customization" title="Niko's server presence." text="Shape how Niko appears in this server. Click any part of the preview to edit it." />
    <SettingsIntro icon="paint" label="Identity desk" title="Server-specific identity" text="Each server can have its own Niko persona. Changes apply only to this server." />
    <form onSubmit={submit} className="settings-stack profile-editor-form">
      <section className="dash-panel settings-panel profile-editor-panel">
        <div className="profile-editor-heading"><div><span className="panel-kicker">Live preview</span><h2>Your server profile</h2><p>Choose a surface to edit it. Your preview updates as you type.</p></div><span className="profile-server-tag"><span className="status-dot" /> Server only</span></div>
        <div className="profile-preview-card">
          <button type="button" className="profile-preview-banner" onClick={() => chooseImage("banner")} style={values.banner_upload_data || values.banner_url || inheritedBanner ? { backgroundImage: `linear-gradient(180deg, transparent, rgba(9,10,12,.4)), url("${values.banner_upload_data || values.banner_url || inheritedBanner}")` } : undefined} aria-label="Change profile banner"><span><Icon name="paint" size={14} /></span></button>
          <button type="button" className="profile-preview-avatar" onClick={() => chooseImage("avatar")} aria-label="Change profile avatar">{values.avatar_upload_data || values.avatar_url || inheritedAvatar ? <img src={values.avatar_upload_data || values.avatar_url || inheritedAvatar} alt="" /> : <span>N</span>}<i><Icon name="paint" size={13} /></i></button>
          <div className="profile-preview-body"><button type="button" className={`profile-preview-name profile-preview-name-font-${editor === "name" ? previewNameSettings.font : values.name_font_id}`} style={editor === "name" ? namePreviewStyle : nameStyle} onClick={() => { setNameSettings({ font: values.name_font_id, effect: values.name_effect_id, colors: values.name_colors }); setEditor("name"); }} aria-label="Edit display name and style">{values.display_name || "Niko"}</button><button type="button" className="profile-preview-bio" onClick={() => setEditor("bio")} aria-label="Edit bio">{values.bio || "A warm Discord companion, ready to help your community."}</button><div className="profile-preview-presence"><i /> Online · Bot</div></div>
        </div>
        <div className="profile-edit-hint"><Icon name="spark" size={14} /> {inheritsGlobalImages ? "This server is showing Niko's global avatar and banner — upload or paste your own to give it a unique identity." : "Select the avatar, banner, display name, or bio above to customize it."}</div>
      </section>
      <SaveFooter state={state} />
    </form>
    {imageChoice && createPortal(<div className="profile-editor-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setImageChoice(null); }}><section className="profile-editor-dialog profile-image-dialog" role="dialog" aria-modal="true" aria-labelledby="profile-image-title"><header><div><span className="panel-kicker">Profile image</span><h2 id="profile-image-title">Change {imageChoice}</h2></div><button type="button" className="profile-editor-close" onClick={() => setImageChoice(null)} aria-label="Close image options"><X size={17} /></button></header><div className="profile-image-choice-tabs"><button type="button" className={imageSource === "file" ? "active" : ""} onClick={() => setImageSource("file")}>Upload to Discord</button><button type="button" className={imageSource === "url" ? "active" : ""} onClick={() => setImageSource("url")}>Use image URL</button></div>{imageSource === "file" ? <div className="profile-image-upload"><input ref={imageChoice === "avatar" ? avatarFileRef : bannerFileRef} type="file" accept="image/*" onChange={(event) => readImageFile(imageChoice, event.target.files?.[0])} /><p>Set an image on this server’s Discord profile. Discord hosts it on its CDN. PNG, JPG, GIF, or WebP · max 8 MB.</p><button type="button" className="button button-primary" onClick={() => (imageChoice === "avatar" ? avatarFileRef.current : bannerFileRef.current)?.click()}>Choose image</button></div> : <Field label="Public image URL" hint="Must be an HTTPS image URL"><input autoFocus type="url" value={imageChoice === "avatar" ? values.avatar_url : values.banner_url} onChange={(event) => imageChoice === "avatar" ? updateValues({ avatar_url: event.target.value, avatar_upload_data: "" }) : updateValues({ banner_url: event.target.value, banner_upload_data: "" })} placeholder="https://cdn.example.com/image.png" /></Field>}<footer><button type="button" className="button button-quiet" onClick={() => setImageChoice(null)}>Cancel</button><button type="button" className="button button-primary" onClick={() => setImageChoice(null)}>Done</button></footer></section></div>, document.body)}
    {editor && createPortal(<div className="profile-editor-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setEditor(null); }}><section className="profile-editor-dialog" role="dialog" aria-modal="true" aria-labelledby="profile-editor-title"><header><div><span className="panel-kicker">Profile edit</span><h2 id="profile-editor-title">{editor === "name" ? "Name & style" : `Edit ${editor}`}</h2></div><button type="button" className="profile-editor-close" onClick={() => setEditor(null)} aria-label="Close editor"><X size={17} /></button></header>{editor === "bio" && <Field label="About Niko" hint={`${values.bio.length}/190 characters`}><textarea autoFocus maxLength={190} rows={5} value={values.bio} onChange={(e) => updateValues({ bio: e.target.value })} placeholder="A warm Discord companion" /></Field>}{editor === "name" && <><Field label="Display name" hint={`${values.display_name.length}/32 characters`}><input autoFocus maxLength={32} value={values.display_name} onChange={(e) => updateValues({ display_name: e.target.value })} placeholder="Niko" /></Field><Field label="Font"><select value={nameSettings.font} onChange={(e) => setNameSettings({ ...nameSettings, font: Number(e.target.value) })}><option value={3}>Sakura</option><option value={4}>Jellybean</option><option value={6}>Modern</option><option value={7}>Medieval</option><option value={8}>8Bit</option><option value={10}>Vampyre</option><option value={11}>gg sans (Default)</option><option value={12}>Tempo</option></select></Field><Field label="Color style"><select value={nameSettings.effect} onChange={(e) => setNameSettings({ ...nameSettings, effect: Number(e.target.value) })}><option value={1}>Solid</option><option value={2}>Gradient</option><option value={3}>Neon</option><option value={4}>Toon</option><option value={5}>Pop</option><option value={6}>Glow</option></select></Field><div className="profile-color-fields">{[0, 1].slice(0, nameSettings.effect === 2 ? 2 : 1).map((index) => <Field key={index} label={`Color ${index + 1}`}><select value={colors[index] ?? (index ? 5763719 : 5793266)} onChange={(e) => { const next = [...colors]; next[index] = Number(e.target.value); setNameSettings({ ...nameSettings, colors: next }); }}><option value="">Choose color</option>{colorOptions.map((option) => <option value={option.value} key={option.value}>{option.label}</option>)}</select></Field>)}</div></>}<footer><button type="button" className="button button-quiet" onClick={() => setEditor(null)}>Done</button><button type="button" className="button button-primary" onClick={() => { if (editor === "name") updateValues({ name_font_id: nameSettings.font, name_effect_id: nameSettings.effect, name_colors: nameSettings.colors }); setEditor(null); }}>Apply to preview</button></footer></section></div>, document.body)}
  </>;
}