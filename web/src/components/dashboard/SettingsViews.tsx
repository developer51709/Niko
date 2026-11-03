import { type CSSProperties, type FormEvent, type ReactElement, type ReactNode, cloneElement, isValidElement, useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { getGuildTickets, saveConfig, saveProfile, updateGuildTicketStatus } from "../../api";
import { Icon } from "../Icon";
import { DiscordMarkdown } from "../DiscordMarkdown";
import { DiscordAppBadge } from "../DiscordAppBadge";
import { useBotConfig } from "../../hooks/useBotConfig";
import { ColorPicker } from "./ColorPicker";
import { Switch } from "./Switch";
import { SettingCard, SettingCards, type SettingCardFlag } from "./SettingCards";
import { ChannelSelect } from "./ChannelSelect";
import { RolePicker } from "./RolePicker";
import { RoleSelect } from "./RoleSelect";
import { Select, localizeOptions, selectOptions } from "./Select";
import { clearToasts, notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { Trash2, X } from "lucide-react";
import type { GlobalProfile, GuildConfig, GuildResources, GuildProfile, GuildTicketsResponse, PresetFilter } from "../../types";
import { DashHeading } from "./DashboardViews";
import { navigate } from "../../router";
import { useStrings } from "../../i18n";

// Only the in-flight flag belongs in state now: every result is announced with a
// toast (see ../../utils/toast) instead of an inline line in the card footer.
type SaveState = { saving: boolean };
const initialSave: SaveState = { saving: false };

// Enum settings keep their choice lists here, so the panels stay readable. The
// labels are catalogue keys and are translated where the dropdown is rendered.
const ANTIRAID_ACTIONS = selectOptions([["kick", "moderation.action.kick"], ["ban", "moderation.action.ban"], ["softban", "moderation.action.softban"], ["slowmode", "moderation.action.slowmode"], ["lockdown", "moderation.action.lockdown"]]);
const ANTINUKE_ACTIONS = selectOptions([["strip", "moderation.action.strip"], ["kick", "moderation.action.kickOffender"], ["ban", "moderation.action.banOffender"]]);
const KICK_OR_BAN_ACTIONS = selectOptions([["kick", "moderation.action.kick"], ["ban", "moderation.action.ban"]]);
const OPERATOR_ACTIONS = selectOptions([["notify", "moderation.action.notify"], ["kick", "moderation.action.kick"], ["ban", "moderation.action.ban"]]);
const APP_ABUSE_ACTIONS = selectOptions([["kick", "moderation.action.kick"], ["ban", "moderation.action.ban"], ["warn", "moderation.action.warn"], ["log", "moderation.action.log"]]);
const CAPTCHA_METHODS = selectOptions([["click", "onboarding.method.click"], ["image", "onboarding.method.image"], ["web", "onboarding.method.web"]]);
// Display-name styles for the profile editor, keyed by Discord's own ids.
const NAME_FONTS = selectOptions([["3", "profile.font.sakura"], ["4", "profile.font.jellybean"], ["6", "profile.font.modern"], ["7", "profile.font.medieval"], ["8", "profile.font.bit"], ["10", "profile.font.vampyre"], ["11", "profile.font.ggSans"], ["12", "profile.font.tempo"]]);
const NAME_EFFECTS = selectOptions([["1", "profile.effect.solid"], ["2", "profile.effect.gradient"], ["3", "profile.effect.neon"], ["4", "profile.effect.toon"], ["5", "profile.effect.pop"], ["6", "profile.effect.glow"]]);

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
  // Custom pickers cannot be labelled by htmlFor, so they get the field label
  // as their accessible name instead.
  const picker = isValidElement(children) && (children.type === RoleSelect || children.type === ChannelSelect || children.type === RolePicker || children.type === Select)
    ? children as ReactElement<{ ariaLabel?: string }>
    : null;
  const controlId = control ? `${generatedId}-control` : undefined;
  return <div className="form-field">
    <label className="form-label" htmlFor={controlId}>{label}</label>
    {control ? cloneElement(control, { id: controlId }) : picker ? cloneElement(picker, { ariaLabel: picker.props.ariaLabel || label }) : children}
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
  const { t } = useStrings("dashboard");
  return <div className={`settings-intro${className ? ` ${className}` : ""}`}>
    <span className="settings-intro-icon"><Icon name={icon} /></span>
    <div><span className="panel-kicker">{label}</span><strong>{title}</strong><p>{text}</p></div>
    <span className="settings-intro-state"><span className="status-dot" /> {t("settings.perServer")}</span>
  </div>;
}

function SettingsSectionTitle({ label, title, detail, icon }: { label: string; title: string; detail?: string; icon?: string }) {
  return <div className="panel-heading settings-section-title">
    <div><span className="panel-kicker">{label}</span><h3>{title}</h3>{detail && <p>{detail}</p>}</div>
    {icon && <span className="panel-icon"><Icon name={icon} /></span>}
  </div>;
}

function SaveFooter({ state }: { state: SaveState }) {
  const { t } = useStrings("dashboard");
  return <div className="setting-footer"><span>{t("settings.footerNote")}</span><button className="button button-primary" type="submit" disabled={state.saving}>{t(state.saving ? "settings.saving" : "settings.saveChanges")}</button></div>;
}

function TicketCategoryList({ categories, onChange }: { categories: string[]; onChange: (value: string[]) => void }) {
  const { t } = useStrings("dashboard");
  const add = () => onChange([...categories, ""]);
  return <div className="settings-category-editor">
    <div className="settings-option-list">
      {categories.map((category, index) => <div className="settings-option-row" key={`${category}-${index}`}>
        <input aria-label={t("tickets.categoryAria", { count: index + 1 })} value={category} maxLength={80} onChange={(event) => onChange(categories.map((item, itemIndex) => itemIndex === index ? event.target.value : item))} placeholder={t("tickets.categoryPlaceholder", { count: index + 1 })} />
        <button type="button" className="settings-option-remove" onClick={() => onChange(categories.filter((_, itemIndex) => itemIndex !== index))} aria-label={t("tickets.categoryRemoveAria", { count: index + 1 })}>{t("server.remove")}</button>
      </div>)}
    </div>
    <div className="settings-category-actions">
      <button type="button" className="button button-muted button-small settings-option-add" onClick={add}>＋ {t("tickets.addCategory")}</button>
    </div>
    <small>{t("tickets.categoriesHint")}</small>
  </div>;
}

export function OnboardingView({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const { t } = useStrings("dashboard");
  const onboarding = config?.server?.onboarding || {};
  const [values, setValues] = useState({ welcome_channel: "", welcome_title: "", welcome_description: "", welcome_color: "#5865f2", welcome_image: "", goodbye_channel: "", goodbye_title: "", goodbye_description: "", goodbye_color: "#ed4245", goodbye_image: "", rules_channel: "", rules_text: "", rules_role_id: "", autorole_ids: [] as string[], bot_autorole_ids: [] as string[], captcha_enabled: false, captcha_channel_id: "", captcha_add_role_ids: [] as string[], captcha_remove_role_ids: [] as string[], captcha_kick_on_fail: false, captcha_mode: "image", captcha_block_proxies: false, captcha_block_vpn: false });
  const [state, setState] = useState(initialSave);
  useEffect(() => setValues({ welcome_channel: onboarding.welcome_channel ? String(onboarding.welcome_channel) : "", welcome_title: onboarding.welcome_title || "", welcome_description: onboarding.welcome_description || "", welcome_color: `#${Number(onboarding.welcome_color ?? 0x5865f2).toString(16).padStart(6, "0")}`, welcome_image: onboarding.welcome_image || "", goodbye_channel: onboarding.goodbye_channel ? String(onboarding.goodbye_channel) : "", goodbye_title: onboarding.goodbye_title || "", goodbye_description: onboarding.goodbye_description || "", goodbye_color: `#${Number(onboarding.goodbye_color ?? 0xed4245).toString(16).padStart(6, "0")}`, goodbye_image: onboarding.goodbye_image || "", rules_channel: onboarding.rules_channel ? String(onboarding.rules_channel) : "", rules_text: onboarding.rules_text || "", rules_role_id: onboarding.rules_role_id ? String(onboarding.rules_role_id) : "", autorole_ids: (onboarding.autorole_ids || []).map(String), bot_autorole_ids: (onboarding.bot_autorole_ids || []).map(String), captcha_enabled: Boolean(onboarding.captcha_enabled), captcha_channel_id: onboarding.captcha_channel_id ? String(onboarding.captcha_channel_id) : "", captcha_add_role_ids: (onboarding.captcha_add_role_ids || []).map(String), captcha_remove_role_ids: (onboarding.captcha_remove_role_ids || []).map(String), captcha_kick_on_fail: Boolean(onboarding.captcha_kick_on_fail), captcha_mode: onboarding.captcha_mode || "image", captcha_block_proxies: Boolean(onboarding.captcha_block_proxies), captcha_block_vpn: Boolean(onboarding.captcha_block_vpn) }), [config]);
  const set = (key: keyof typeof values, value: unknown) => setValues((current) => ({ ...current, [key]: value }));
  const submit = (event: FormEvent) => { event.preventDefault(); setState({ saving: true }); notifyLoading(t("onboarding.saving"), "settings-save"); saveConfig(guildId, "server", { onboarding: { ...values, autorole_ids: values.autorole_ids, bot_autorole_ids: values.bot_autorole_ids, captcha_add_role_ids: values.captcha_add_role_ids, captcha_remove_role_ids: values.captcha_remove_role_ids } }, csrfToken).then(() => { setState({ saving: false }); notifySuccess(t("onboarding.saved"), "settings-save"); }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : t("onboarding.saveFailed"), "settings-save"); }); };
  const channels = resources?.channels || [];
  const roles = resources?.roles || [];
  return <><DashHeading eyebrow={t("onboarding.eyebrow")} title={t("onboarding.title")} text={t("onboarding.text")} /><SettingsIntro icon="users" label={t("onboarding.kicker")} title={t("onboarding.introTitle")} text={t("onboarding.introText")} /><form onSubmit={submit} className="settings-stack guild-feature-settings onboarding-settings-stack"><section className="dash-panel settings-panel"><SettingsSectionTitle label={t("onboarding.welcomeLabel")} title={t("onboarding.welcomeTitle")} detail={t("onboarding.welcomeDetail")} icon="users" /><div className="form-grid"><Field label={t("onboarding.welcomeChannel")}><ChannelSelect channels={channels} value={values.welcome_channel} placeholder={t("onboarding.disabled")} onChange={(value) => set("welcome_channel", value)} /></Field><Field label={t("onboarding.welcomeTitleLabel")}><input maxLength={200} value={values.welcome_title} onChange={(event) => set("welcome_title", event.target.value)} placeholder={t("onboarding.welcomeTitlePlaceholder")} /></Field><Field label={t("onboarding.welcomeMessageLabel")} hint={t("onboarding.messageHint")}><textarea rows={4} maxLength={2000} value={values.welcome_description} onChange={(event) => set("welcome_description", event.target.value)} placeholder={t("onboarding.welcomeMessagePlaceholder")} /></Field><Field label={t("onboarding.welcomeColorLabel")} hint={t("onboarding.welcomeColorHint")}><ColorPicker label={t("onboarding.welcomeColorLabel")} value={values.welcome_color} onChange={(value) => set("welcome_color", value)} /></Field><Field label={t("onboarding.welcomeImage")}><input type="url" value={values.welcome_image} onChange={(event) => set("welcome_image", event.target.value)} placeholder="https://…" /></Field></div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label={t("onboarding.goodbyeLabel")} title={t("onboarding.goodbyeTitle")} detail={t("onboarding.goodbyeDetail")} icon="logout" /><div className="form-grid"><Field label={t("onboarding.goodbyeChannel")}><ChannelSelect channels={channelsWithSelected(resources, values.goodbye_channel)} value={values.goodbye_channel} placeholder={t("onboarding.disabled")} onChange={(value) => set("goodbye_channel", value)} /></Field><Field label={t("onboarding.goodbyeTitleLabel")}><input maxLength={200} value={values.goodbye_title} onChange={(event) => set("goodbye_title", event.target.value)} placeholder={t("onboarding.goodbyeTitlePlaceholder")} /></Field><Field label={t("onboarding.goodbyeMessageLabel")} hint={t("onboarding.messageHint")}><textarea rows={4} maxLength={2000} value={values.goodbye_description} onChange={(event) => set("goodbye_description", event.target.value)} placeholder={t("onboarding.goodbyeMessagePlaceholder")} /></Field><Field label={t("onboarding.goodbyeColorLabel")} hint={t("onboarding.goodbyeColorHint")}><ColorPicker label={t("onboarding.goodbyeColorLabel")} value={values.goodbye_color} onChange={(value) => set("goodbye_color", value)} /></Field><Field label={t("onboarding.goodbyeImage")}><input type="url" value={values.goodbye_image} onChange={(event) => set("goodbye_image", event.target.value)} placeholder="https://…" /></Field></div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label={t("onboarding.joinRolesLabel")} title={t("onboarding.joinRolesTitle")} detail={t("onboarding.joinRolesDetail")} icon="users" /><div className="form-grid"><Field label={t("onboarding.memberAutoroles")} hint={t("onboarding.memberAutorolesHint")}><RoleSelect roles={roles} value={values.autorole_ids} multiple ariaLabel={t("onboarding.memberAutoroles")} onChange={(value) => set("autorole_ids", value)} /></Field><Field label={t("onboarding.botAutoroles")} hint={t("onboarding.botAutorolesHint")}><RoleSelect roles={roles} value={values.bot_autorole_ids} multiple ariaLabel={t("onboarding.botAutoroles")} onChange={(value) => set("bot_autorole_ids", value)} /></Field></div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label={t("onboarding.verifyLabel")} title={t("onboarding.verifyTitle")} detail={t("onboarding.verifyDetail")} icon="shield" /><div className="form-grid"><Field label={t("onboarding.rulesChannel")}><ChannelSelect channels={channelsWithSelected(resources, values.rules_channel)} value={values.rules_channel} placeholder={t("onboarding.notConfigured")} onChange={(value) => set("rules_channel", value)} /></Field><Field label={t("onboarding.rulesRole")}><RoleSelect roles={roles} value={values.rules_role_id} placeholder={t("onboarding.noRole")} onChange={(value) => set("rules_role_id", value)} /></Field><Field label={t("onboarding.rulesText")}><textarea rows={4} maxLength={4000} value={values.rules_text} onChange={(event) => set("rules_text", event.target.value)} placeholder={t("onboarding.rulesPlaceholder")} /></Field><Field label={t("onboarding.verifyChannel")} hint={t("onboarding.verifyChannelHint")}><ChannelSelect channels={channelsWithSelected(resources, values.captcha_channel_id)} value={values.captcha_channel_id} placeholder={t("onboarding.notSet")} onChange={(value) => set("captcha_channel_id", value)} /></Field><Field label={t("onboarding.verifyMethod")} hint={t(values.captcha_mode === "click" ? "onboarding.hintClick" : values.captcha_mode === "web" ? "onboarding.hintWeb" : "onboarding.hintDm")}><Select placeholder={null} options={localizeOptions(CAPTCHA_METHODS, t)} value={values.captcha_mode} onChange={(value) => set("captcha_mode", value)} /></Field><Field label={t("onboarding.verifyAddRoles")}><RoleSelect roles={roles} value={values.captcha_add_role_ids} multiple ariaLabel={t("onboarding.verifyAddAria")} onChange={(value) => set("captcha_add_role_ids", value)} /></Field><Field label={t("onboarding.verifyRemoveRoles")}><RoleSelect roles={roles} value={values.captcha_remove_role_ids} multiple ariaLabel={t("onboarding.verifyRemoveAria")} onChange={(value) => set("captcha_remove_role_ids", value)} /></Field></div><SettingCards><SettingCard title={t("onboarding.enableCaptcha")} hint={t("onboarding.enableCaptchaHint")} action={<Switch checked={values.captcha_enabled} onCheckedChange={(value) => set("captcha_enabled", value)} aria-label={t("onboarding.enableCaptcha")} />} /><SettingCard title={t("onboarding.kickOnFail")} hint={t("onboarding.kickOnFailHint")} action={<Switch checked={values.captcha_kick_on_fail} onCheckedChange={(value) => set("captcha_kick_on_fail", value)} aria-label={t("onboarding.kickOnFail")} />} /><SettingCard title={t("onboarding.blockProxies")} hint={t("onboarding.blockProxiesHint")} action={<Switch checked={values.captcha_block_proxies} onCheckedChange={(value) => set("captcha_block_proxies", value)} aria-label={t("onboarding.blockProxies")} />} /><SettingCard title={t("onboarding.blockVpn")} hint={t("onboarding.blockVpnHint")} action={<Switch checked={values.captcha_block_vpn} onCheckedChange={(value) => set("captcha_block_vpn", value)} aria-label={t("onboarding.blockVpn")} />} /></SettingCards></section><SaveFooter state={state} /></form></>;
}

export function TicketsView({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const { t } = useStrings("dashboard");
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
  useEffect(() => { let active = true; setLoadingTickets(true); setTicketError(""); setData(null); setState(initialSave); clearToasts("settings-tickets"); getGuildTickets(guildId).then((result) => { if (active) { setData(result); setValues({ panel_title: result.config.panel_title || "", panel_description: result.config.panel_description || "", panel_color: `#${Number(result.config.panel_color ?? 0x5865f2).toString(16).padStart(6, "0")}`, panel_image: result.config.panel_image || "", panel_categories: result.config.panel_categories || [], panel_channel_id: result.config.panel_channel_id || "", support_roles: result.config.support_roles || [] }); } }).catch((error) => { if (active) setTicketError(error instanceof Error ? error.message : t("tickets.loadFailed")); }).finally(() => { if (active) setLoadingTickets(false); }); return () => { active = false; };  }, [guildId, ticketRetry, t]);
  useEffect(() => { if (config) setValues({ panel_title: tickets.panel_title || "", panel_description: tickets.panel_description || "", panel_color: `#${Number(tickets.panel_color ?? 0x5865f2).toString(16).padStart(6, "0")}`, panel_image: tickets.panel_image || "", panel_categories: tickets.panel_categories || [], panel_channel_id: tickets.panel_channel_id || "", support_roles: tickets.support_roles || [] }); }, [guildId, config]);
  const submit = (event: FormEvent) => { event.preventDefault(); setSavingConfig(true); setState({ saving: true }); notifyLoading(t("tickets.saving"), "settings-save"); saveConfig(guildId, "server", { tickets: { ...values, panel_categories: values.panel_categories.map((category) => category.trim()).filter(Boolean) } }, csrfToken).then(async () => { const freshData = await getGuildTickets(guildId); setData(freshData); setState({ saving: false }); notifySuccess(t("tickets.saved"), "settings-save"); }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : t("tickets.saveFailed"), "settings-save"); }).finally(() => setSavingConfig(false)); };
  const setTicketStatus = (channelId: string, status: "open" | "closed") => {
    setSaving(channelId);
    notifyLoading(t("tickets.updating"), "settings-tickets");
    updateGuildTicketStatus(guildId, channelId, status, csrfToken)
      .then(async () => { setData(await getGuildTickets(guildId)); notifySuccess(t(status === "closed" ? "tickets.closed" : "tickets.reopened"), "settings-tickets"); })
      .catch((error) => notifyError(error instanceof Error ? error.message : t("tickets.updateFailed"), "settings-tickets"))
      .finally(() => setSaving(""));
  };
  const channels = resources?.channels || [];
  const roles = resources?.roles || [];
  const filteredTickets = (data?.tickets || []).filter((ticket) => ticketFilter === "all" || (ticket.status || "open") === ticketFilter);
  return <>
    <DashHeading eyebrow={t("tickets.eyebrow")} title={t("tickets.title")} text={t("tickets.text")} />
    <SettingsIntro
      icon="users"
      label={t("tickets.kicker")}
      title={loadingTickets ? t("tickets.loadingActivity") : ticketError ? t("tickets.activityUnavailable") : t("tickets.currentCount", { count: data?.tickets.length || 0 })}
      text={ticketError ? t("tickets.errorIntro") : t("tickets.introText")}
    />
    {ticketError && <div className="inline-error" role="alert">
      <strong>{t("tickets.errorTitle")}</strong>
      <span>{ticketError}</span>
      <button className="button button-muted" type="button" onClick={() => setTicketRetry((attempt) => attempt + 1)}>{t("tickets.retry")}</button>
    </div>}
    <form onSubmit={submit} className="settings-stack guild-feature-settings ticket-settings-stack">
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label={t("tickets.panelLabel")} title={t("tickets.panelTitle")} detail={t("tickets.panelDetail")} icon="settings" />
        <div className="form-grid">
          <Field label={t("tickets.panelTitleLabel")}><input maxLength={200} value={values.panel_title} onChange={(event) => setValues({ ...values, panel_title: event.target.value })} placeholder={t("tickets.panelTitlePlaceholder")} /></Field>
          <Field label={t("tickets.panelChannelLabel")}><ChannelSelect channels={channelsWithSelected(resources, values.panel_channel_id)} value={values.panel_channel_id} placeholder={t("tickets.panelChannelPlaceholder")} onChange={(panel_channel_id) => setValues({ ...values, panel_channel_id })} /></Field>
          <Field label={t("tickets.panelDescriptionLabel")}><textarea rows={4} maxLength={2000} value={values.panel_description} onChange={(event) => setValues({ ...values, panel_description: event.target.value })} placeholder={t("tickets.panelDescriptionPlaceholder")} /></Field>
          <Field label={t("tickets.panelColorLabel")} hint={t("settings.hexHint")}><ColorPicker label={t("tickets.panelColorPicker")} value={values.panel_color} onChange={(panel_color) => setValues({ ...values, panel_color })} /></Field>
          <Field label={t("tickets.panelImageLabel")}><input type="url" value={values.panel_image} onChange={(event) => setValues({ ...values, panel_image: event.target.value })} placeholder="https://…" /></Field>
          <div className="form-grid-wide"><Field label={t("tickets.categoriesLabel")}><TicketCategoryList categories={values.panel_categories} onChange={(panel_categories) => setValues({ ...values, panel_categories })} /></Field></div>
          <Field label={t("tickets.supportRolesLabel")}><RoleSelect roles={roles} value={values.support_roles} multiple ariaLabel={t("tickets.supportRolesLabel")} onChange={(support_roles) => setValues({ ...values, support_roles: Array.isArray(support_roles) ? support_roles : [] })} /></Field>
        </div>
        <div className="setting-footer"><span>{t("settings.footerNote")}</span><button className="button button-primary" type="submit" disabled={savingConfig}>{t(savingConfig ? "settings.saving" : "settings.saveChanges")}</button></div>
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label={t("tickets.queueLabel")} title={t("tickets.queueTitle")} detail={t("tickets.queueDetail")} icon="users" />
        <div className="ticket-filter-row" role="group" aria-label={t("tickets.filterAria")}>
          {(["all", "open", "closed"] as const).map((filter) => <button type="button" key={filter} className={ticketFilter === filter ? "button button-secondary is-active" : "button button-quiet"} aria-pressed={ticketFilter === filter} onClick={() => setTicketFilter(filter)}>{filter === "all" ? t("tickets.filterAll", { count: data?.tickets.length || 0 }) : t(filter === "open" ? "tickets.filterOpen" : "tickets.filterClosed", { count: (data?.tickets || []).filter((ticket) => (ticket.status || "open") === filter).length })}</button>)}
        </div>
        {loadingTickets ? <div className="empty-state"><p>{t("tickets.loadingTickets")}</p></div>
          : ticketError ? <div className="empty-state"><p>{t("tickets.dataUnavailable")}</p></div>
          : filteredTickets.length ? <div className="ticket-admin-list">{filteredTickets.map((ticket) => <article className="ticket-admin-row" key={ticket.channel_id}><div><strong>#{ticket.channel_name || `ticket-${ticket.channel_id}`}</strong> <a className="ticket-channel-link" href={`https://discord.com/channels/${guildId}/${ticket.channel_id}`} target="_blank" rel="noreferrer">{t("tickets.openInDiscord")}</a><small>{t("tickets.openedBy", { category: ticket.category || t("tickets.general"), opener: ticket.opener_name || ticket.opener_id, claimed: ticket.claimed_by ? t("tickets.claimedBy", { name: ticket.claimed_by }) : "" })}</small></div><span className={`application-status ${ticket.status === "closed" ? "closed" : "open"}`}>{ticket.status || "open"}</span><button className="button button-muted button-small" disabled={saving === ticket.channel_id} type="button" onClick={() => setTicketStatus(ticket.channel_id, ticket.status === "closed" ? "open" : "closed")}>{saving === ticket.channel_id ? t("settings.saving") : t(ticket.status === "closed" ? "tickets.reopen" : "tickets.close")}</button></article>)}</div>
          : <div className="empty-state"><p>{t("tickets.none")}</p></div>}
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label={t("tickets.historyLabel")} title={t("tickets.historyTitle")} detail={t("tickets.historyDetail")} icon="book" />
        {ticketError ? <div className="empty-state"><p>{t("tickets.transcriptsUnavailable")}</p></div>
          : loadingTickets ? <div className="empty-state"><p>{t("tickets.loadingTranscripts")}</p></div>
          : data?.transcripts.length ? <div className="ticket-admin-list">{data.transcripts.map((transcript) => <article className="ticket-admin-row" key={transcript.transcript_id}><div><strong>#{transcript.channel_name}</strong><small>{t("tickets.transcriptMeta", { category: transcript.category, opener: transcript.opener_id, count: transcript.message_count, date: new Date(transcript.created_at).toLocaleString() })}</small></div><a className="button button-secondary button-small" href={transcript.url} target="_blank" rel="noreferrer">{t("tickets.viewTranscript")}</a></article>)}</div>
          : <div className="empty-state"><p>{t("tickets.noTranscripts")}</p></div>}
      </section>
    </form>
  </>;
}

export function ModerationView({ guildId, config, csrfToken }: { guildId: string; config: GuildConfig | null; csrfToken?: string }) {
  const { t } = useStrings("dashboard");
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
    event.preventDefault(); setState({ saving: true }); notifyLoading(t("moderation.saving"), "settings-save");
    saveConfig(guildId, "automod", values, csrfToken).then((result) => {
      applyConfig(result.config || {});
      setState({ saving: false }); notifySuccess(t("moderation.saved"), "settings-save");
    }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : t("moderation.saveFailed"), "settings-save"); });
  };
  const flags = [["antispam", "moderation.flag.antispam", "moderation.flag.antispamHint"], ["antilink", "moderation.flag.antilink", "moderation.flag.antilinkHint"], ["badwords", "moderation.flag.badwords", "moderation.flag.badwordsHint"], ["massmention", "moderation.flag.massmention", "moderation.flag.massmentionHint"], ["scam_image_filter", "moderation.flag.scam", "moderation.flag.scamHint"], ["nsfw_image_filter", "moderation.flag.nsfw", "moderation.flag.nsfwHint"], ["antinuke", "moderation.flag.antinuke", "moderation.flag.antinukeHint"], ["antiraid", "moderation.flag.antiraid", "moderation.flag.antiraidHint"], ["antiraid_ext", "moderation.flag.antiraidExt", "moderation.flag.antiraidExtHint"]] as const;
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
    <DashHeading eyebrow={t("moderation.eyebrow")} title={t("moderation.title")} text={t("moderation.text")} />
    <SettingsIntro icon="shield" label={t("moderation.kicker")} title={t("moderation.activeFlags", { active: activeFlags, total: flags.length })} text={t("moderation.introText")} />
    <form onSubmit={submit} className="settings-stack">
      <section className={`dash-panel settings-panel premium-banner${premiumActive ? " is-active" : ""}`} aria-label={t("moderation.premiumLabel")}>
        <div className="premium-banner-copy">
          <span className="panel-kicker">{t("moderation.premiumLabel")}</span>
          <strong>{premiumActive ? t(premiumUntil ? "moderation.premiumActiveUntil" : "moderation.premiumActive", { date: premiumUntil || "" }) : t("moderation.premiumPerk")}</strong>
          <p>{t(premiumActive ? "moderation.premiumActiveText" : "moderation.premiumUpsell")}</p>
        </div>
        <button type="button" className={`button ${premiumActive ? "button-muted" : "button-primary"} button-small`} onClick={() => navigate(`/billing?guild=${guildId}`)}>
          {t(premiumActive ? "moderation.managePremium" : "moderation.upgrade")}
        </button>
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label={t("moderation.rulesLabel")} title={t("moderation.rulesTitle")} detail={t("moderation.rulesDetail")} icon="shield" />
        <SettingCards>
          {flags.map(([key, label, hint]) => {
            const premiumFlag = key === "nsfw_image_filter";
            const locked = premiumFlag && !premiumActive;
            const cardFlags: SettingCardFlag[] = [];
            if (experimentalFlags.has(key)) cardFlags.push("experimental");
            if (premiumFlag) cardFlags.push("premium");
            return <SettingCard
              key={key}
              title={t(label)}
              hint={t(hint)}
              flags={cardFlags}
              locked={locked}
              action={<Switch checked={Boolean(values.automod?.[key])} disabled={locked} onCheckedChange={(value) => updateNested("automod", key, value)} aria-label={t(label)} />}
            />;
          })}
        </SettingCards>
        {experimentalFlags.size > 0 && <p className="setting-note setting-card-note">{t("moderation.scamNote")}</p>}
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label={t("moderation.wordsLabel")} title={t("moderation.wordsTitle")} detail={t("moderation.wordsDetail")} icon="shield" />
        <div className="settings-category-editor blocked-words-editor">
          <div className="blocked-words-toolbar">
            <span className="blocked-words-count">
              <span className={`status-dot${blockedWords.length ? "" : " is-idle"}`} aria-hidden="true" />
              {blockedWords.length === 0 ? t("moderation.noWords") : t(blockedWords.length === 1 ? "moderation.wordsOne" : "moderation.wordsMany", { count: blockedWords.length })}
            </span>
            <span className="blocked-words-rule">{t("moderation.matchRule")}</span>
          </div>
          {blockedWords.length === 0
            ? <div className="blocked-words-empty">
              <span className="blocked-words-empty-icon"><Icon name="shield" /></span>
              <strong>{t("moderation.emptyWordsTitle")}</strong>
              <span>{t("moderation.emptyWordsBefore")} <code>!badwords</code> {t("moderation.emptyWordsAfter")}</span>
            </div>
            : <ul className="blocked-word-chips" aria-label={t(blockedWords.length === 1 ? "moderation.blockedOne" : "moderation.blockedMany", { count: blockedWords.length })}>
              {blockedWords.map((word) => <li className="blocked-word-chip" key={word}>
                <code className="blocked-word-value" title={word}>{word}</code>
                <button type="button" className="blocked-word-remove" onClick={() => removeBlockedWord(word)} aria-label={t("moderation.removeWordAria", { word })}>
                  <X size={12} aria-hidden="true" />
                </button>
              </li>)}
            </ul>}
          <div className="blocked-word-add">
            <input
              type="text"
              value={wordDraft}
              maxLength={60}
              placeholder={t("moderation.wordPlaceholder")}
              aria-label={t("moderation.addWordAria")}
              autoComplete="off"
              spellCheck={false}
              onChange={(event) => setWordDraft(event.target.value)}
              onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); addBlockedWord(); } }}
            />
            <button type="button" className="button button-muted button-small" onClick={addBlockedWord} disabled={!wordDraft.trim()}>＋ {t("moderation.addWord")}</button>
          </div>
          <div className="blocked-words-response">
          <span className="blocked-words-response-label">{t("moderation.responseWhen")}</span>
          <div className="form-grid">
            <Field label={t("moderation.responseLabel")} hint={t("moderation.responseHint")}>
              <Select
                options={localizeOptions(selectOptions([["delete", "moderation.responseDelete"], ["censor", "moderation.responseCensor"]]), t)}
                value={values.badwords_action || "delete"}
                onChange={(value) => setValues({ ...values, badwords_action: value })}
                placeholder={null}
              />
            </Field>
            {values.badwords_action === "censor" && <Field label={t("moderation.maskLabel")} hint={t("moderation.maskHint")}>
              <input value={values.badwords_mask ?? "*"} maxLength={16} placeholder="*" onChange={(event) => setValues({ ...values, badwords_mask: event.target.value })} />
            </Field>}
          </div>
          {values.badwords_action === "censor" && <p className="setting-note">{t("moderation.censorNoteBefore")} <strong>{t("moderation.censorNotePermission")}</strong> {t("moderation.censorNoteAfter")}</p>}
          </div>
          <small className="blocked-words-note">{t("moderation.matchNoteBefore")} <code>cat</code> {t("moderation.matchNoteMiddle")} <code>*</code> {t("moderation.matchNoteSuffix")} <code>cat*</code> {t("moderation.matchNoteSuffixExample")} <code>*cat*</code> {t("moderation.matchNoteAnywhere")} <code>c.a.t</code> {t("moderation.matchNoteEnd")}</small>
        </div>
      </section>
      <section className="dash-panel settings-panel">
        <SettingsSectionTitle label={t("moderation.presetsLabel")} title={t("moderation.presetsTitle")} detail={t("moderation.presetsDetail")} icon="shield" />
        {presetCatalog.length === 0
          ? <p className="setting-note">{t("moderation.presetsUnavailable")}</p>
          : <SettingCards>
            {presetCatalog.map((preset) => <SettingCard
              key={preset.key}
              title={preset.label}
              hint={preset.description}
              action={<Switch checked={enabledPresets.includes(preset.key)} onCheckedChange={() => togglePreset(preset.key)} aria-label={preset.label} />}
            />)}
          </SettingCards>}
        <p className="setting-note setting-card-note">{t("moderation.presetsNote")}</p>
      </section>
      <section className="dash-panel settings-panel"><SettingsSectionTitle label={t("moderation.thresholdsLabel")} title={t("moderation.thresholdsTitle")} detail={t("moderation.thresholdsDetail")} /><div className="form-grid">
        <Field label={t("moderation.spamMessages")} hint={t("moderation.spamMessagesHint")}><input type="number" min="1" max="100" value={values.spam_threshold ?? 6} onChange={(e) => setValues({ ...values, spam_threshold: e.target.value })} /></Field>
        <Field label={t("moderation.spamInterval")}><input type="number" min="1" max="3600" value={values.spam_interval ?? 7} onChange={(e) => setValues({ ...values, spam_interval: e.target.value })} /></Field>
        <Field label={t("moderation.maxMentions")}><input type="number" min="1" max="100" value={values.max_mentions ?? 5} onChange={(e) => setValues({ ...values, max_mentions: e.target.value })} /></Field>
        <Field label={t("moderation.antiraidJoins")} hint={t("moderation.antiraidJoinsHint")}><input type="number" min="1" max="1000" value={values.antiraid?.join_threshold ?? 10} onChange={(e) => updateNested("antiraid", "join_threshold", e.target.value)} /></Field>
        <Field label={t("moderation.antiraidInterval")}><input type="number" min="1" max="3600" value={values.antiraid?.join_interval ?? 10} onChange={(e) => updateNested("antiraid", "join_interval", e.target.value)} /></Field>
        <Field label={t("moderation.antiraidAction")}><Select placeholder={null} options={localizeOptions(ANTIRAID_ACTIONS, t)} value={values.antiraid?.action ?? "kick"} onChange={(value) => updateNested("antiraid", "action", value)} /></Field>
        <Field label={t("moderation.newAccount")} hint={t("moderation.newAccountHint")}><input type="number" min="0" max="365" value={values.antiraid?.new_account_days ?? 0} onChange={(e) => updateNested("antiraid", "new_account_days", e.target.value)} /></Field>
        <Field label={t("moderation.lockdownSlowmode")} hint={t("moderation.lockdownSlowmodeHint")}><input type="number" min="1" max="21600" value={values.antiraid?.lockdown_slowmode ?? 30} onChange={(e) => updateNested("antiraid", "lockdown_slowmode", e.target.value)} /></Field>
      </div></section>
      <section className="dash-panel settings-panel"><SettingsSectionTitle label={t("moderation.antinukeLabel")} title={t("moderation.antinukeTitle")} detail={t("moderation.antinukeDetail")} icon="shield" /><div className="form-grid">
        <Field label={t("moderation.bans")}><input type="number" min="1" max="100" value={values.antinuke?.ban_threshold ?? 3} onChange={(e) => updateNested("antinuke", "ban_threshold", e.target.value)} /></Field>
        <Field label={t("moderation.kicks")}><input type="number" min="1" max="100" value={values.antinuke?.kick_threshold ?? 3} onChange={(e) => updateNested("antinuke", "kick_threshold", e.target.value)} /></Field>
        <Field label={t("moderation.channelDeletes")}><input type="number" min="1" max="100" value={values.antinuke?.channel_delete_threshold ?? 3} onChange={(e) => updateNested("antinuke", "channel_delete_threshold", e.target.value)} /></Field>
        <Field label={t("moderation.roleDeletes")}><input type="number" min="1" max="100" value={values.antinuke?.role_delete_threshold ?? 3} onChange={(e) => updateNested("antinuke", "role_delete_threshold", e.target.value)} /></Field>
        <Field label={t("moderation.channelCreates")}><input type="number" min="1" max="100" value={values.antinuke?.channel_create_threshold ?? 5} onChange={(e) => updateNested("antinuke", "channel_create_threshold", e.target.value)} /></Field>
        <Field label={t("moderation.webhookDeletes")}><input type="number" min="1" max="100" value={values.antinuke?.webhook_delete_threshold ?? 3} onChange={(e) => updateNested("antinuke", "webhook_delete_threshold", e.target.value)} /></Field>
        <Field label={t("moderation.interval")} hint={t("moderation.intervalHint")}><input type="number" min="1" max="3600" value={values.antinuke?.interval ?? 10} onChange={(e) => updateNested("antinuke", "interval", e.target.value)} /></Field>
        <Field label={t("moderation.actionLabel")}><Select placeholder={null} options={localizeOptions(ANTINUKE_ACTIONS, t)} value={values.antinuke?.action ?? "strip"} onChange={(value) => updateNested("antinuke", "action", value)} /></Field>
      </div></section>
      <section className="dash-panel settings-panel"><SettingsSectionTitle label={t("moderation.extLabel")} title={t("moderation.extTitle")} detail={t("moderation.extDetail")} icon="shield" /><div className="form-grid">
        <Field label={t("moderation.floodMembers")} hint={t("moderation.floodMembersHint")}><input type="number" min="1" max="1000" value={values.antiraid_ext?.interaction_threshold ?? 5} onChange={(e) => updateNested("antiraid_ext", "interaction_threshold", e.target.value)} /></Field>
        <Field label={t("moderation.floodWindow")}><input type="number" min="1" max="3600" value={values.antiraid_ext?.interaction_window ?? 30} onChange={(e) => updateNested("antiraid_ext", "interaction_window", e.target.value)} /></Field>
        <Field label={t("moderation.newFor")} hint={t("moderation.newForHint")}><input type="number" min="1" max="86400" value={values.antiraid_ext?.join_age_limit ?? 120} onChange={(e) => updateNested("antiraid_ext", "join_age_limit", e.target.value)} /></Field>
        <Field label={t("moderation.raiderAction")}><Select placeholder={null} options={localizeOptions(KICK_OR_BAN_ACTIONS, t)} value={values.antiraid_ext?.raider_action ?? "kick"} onChange={(value) => updateNested("antiraid_ext", "raider_action", value)} /></Field>
        <Field label={t("moderation.operatorAction")}><Select placeholder={null} options={localizeOptions(OPERATOR_ACTIONS, t)} value={values.antiraid_ext?.operator_action ?? "notify"} onChange={(value) => updateNested("antiraid_ext", "operator_action", value)} /></Field>
        <Field label={t("moderation.appCommands")}><input type="number" min="1" max="1000" value={values.antiraid_ext?.ext_app_threshold ?? 3} onChange={(e) => updateNested("antiraid_ext", "ext_app_threshold", e.target.value)} /></Field>
        <Field label={t("moderation.appWindow")}><input type="number" min="1" max="3600" value={values.antiraid_ext?.ext_app_window ?? 15} onChange={(e) => updateNested("antiraid_ext", "ext_app_window", e.target.value)} /></Field>
        <Field label={t("moderation.appAction")}><Select placeholder={null} options={localizeOptions(APP_ABUSE_ACTIONS, t)} value={values.antiraid_ext?.ext_app_action ?? "kick"} onChange={(value) => updateNested("antiraid_ext", "ext_app_action", value)} /></Field>
      </div></section>
      <SaveFooter state={state} />
    </form>
  </>;
}

type Experiment = { key: string; icon: string; title: string; hint: string; info: string };

/**
 * The learn-more sheet for one AI experiment. It is portalled to the body so the
 * blurred dashboard chrome around the settings page cannot clip it, and it wears
 * the same glass panel as the rest of the dashboard.
 */
function ExperimentDialog({ experiment, enabled, onClose }: { experiment: Experiment; enabled: boolean; onClose: () => void }) {
  const { t } = useStrings("dashboard");
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);
  return createPortal(
    <div className="ai-experiment-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <section className="ai-experiment-dialog" role="dialog" aria-modal="true" aria-labelledby="ai-experiment-title" aria-describedby="ai-experiment-copy">
        <header>
          <span className="ai-experiment-mark"><Icon name={experiment.icon} size={18} /></span>
          <div>
            <div className="ai-experiment-meta">
              <span className="panel-kicker">{t("ai.experiment")}</span>
              <span className={enabled ? "ai-experiment-state is-on" : "ai-experiment-state"}>{t(enabled ? "ai.on" : "ai.off")}</span>
            </div>
            <h2 id="ai-experiment-title">{t(experiment.title)}</h2>
          </div>
          <button type="button" className="profile-editor-close" onClick={onClose} aria-label={t("ai.closeExperiment")}><X size={17} /></button>
        </header>
        <p className="ai-experiment-lead">{t(experiment.hint)}</p>
        <p className="ai-experiment-copy" id="ai-experiment-copy">{t(experiment.info)}</p>
        <footer>
          <span className="ai-experiment-scope"><Icon name="lock" size={13} /> {t("ai.scopeNote")}</span>
          <button type="button" className="button button-primary" onClick={onClose}>{t("ai.gotIt")}</button>
        </footer>
      </section>
    </div>,
    document.body,
  );
}

export function AiView({ guildId, config, csrfToken }: { guildId: string; config: GuildConfig | null; csrfToken?: string }) {
  const { t } = useStrings("dashboard");
  const [values, setValues] = useState({ ai_name: "Niko", personality: "cafe", enabled: true, ai_actions_experiment: false, better_context_experiment: false, multimodal_experiment: false });
  const [state, setState] = useState(initialSave);
  const [learnMore, setLearnMore] = useState<string | null>(null);
  const readBool = (value: unknown) => value === true || value === "True";
  const applyConfig = (ai: Record<string, any>) => setValues({ ai_name: ai.ai_name || "Niko", personality: ai.personality === "normal" ? "normal" : "cafe", enabled: ai.enabled !== "False" && ai.enabled !== false, ai_actions_experiment: readBool(ai.ai_actions_experiment), better_context_experiment: readBool(ai.better_context_experiment), multimodal_experiment: readBool(ai.multimodal_experiment) });
  useEffect(() => applyConfig(config?.ai || {}), [config]);
  const submit = (event: FormEvent) => { event.preventDefault(); setState({ saving: true }); notifyLoading(t("ai.saving"), "settings-save"); saveConfig(guildId, "ai", values, csrfToken).then((result) => { applyConfig(result.config || {}); setState({ saving: false }); notifySuccess(t("ai.saved"), "settings-save"); }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : t("ai.saveFailed"), "settings-save"); }); };
  // Titles, hints and explanations are catalogue keys; the dialog and the cards
  // translate them at render.
  const experiments = [{ key: "better_context_experiment", icon: "message", title: "ai.context.title", hint: "ai.context.hint", info: "ai.context.info" }, { key: "ai_actions_experiment", icon: "shield", title: "ai.actions.title", hint: "ai.actions.hint", info: "ai.actions.info" }, { key: "multimodal_experiment", icon: "attach", title: "ai.multimodal.title", hint: "ai.multimodal.hint", info: "ai.multimodal.info" }] as const;
  return <><DashHeading eyebrow={t("ai.eyebrow")} title={t("ai.title")} text={t("ai.text")} /><SettingsIntro icon="settings" label={t("ai.kicker")} title={t(values.enabled ? "ai.ready" : "ai.quiet", { name: values.ai_name })} text={t("ai.introText")} /><form onSubmit={submit} className="settings-stack"><section className="dash-panel settings-panel"><SettingsSectionTitle label={t("ai.conversationLabel")} title={t("ai.coreTitle")} detail={t("ai.coreDetail")} icon="settings" /><div className="form-grid"><Field label={t("ai.nameLabel")} hint={t("ai.nameHint")}><input value={values.ai_name} minLength={3} maxLength={32} onChange={(e) => setValues({ ...values, ai_name: e.target.value })} /></Field></div><SettingCards><SettingCard title={t("ai.enable")} hint={t("ai.enableHint")} action={<Switch checked={values.enabled} onCheckedChange={(value) => setValues({ ...values, enabled: value })} aria-label={t("ai.enable")} />} /></SettingCards><div className="personality-options"><button type="button" className={values.personality === "cafe" ? "personality active" : "personality"} onClick={() => setValues({ ...values, personality: "cafe" })}><span className="personality-mark">n</span><span><strong>{t("ai.cafe")}</strong><small>{t("ai.cafeHint")}</small></span></button><button type="button" className={values.personality === "normal" ? "personality active" : "personality"} onClick={() => setValues({ ...values, personality: "normal" })}><span className="personality-mark">—</span><span><strong>{t("ai.normal")}</strong><small>{t("ai.normalHint")}</small></span></button></div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label={t("ai.experimentsLabel")} title={t("ai.experimentsTitle")} detail={t("ai.experimentsDetail")} /><SettingCards stacked>{experiments.map((experiment) => <SettingCard key={experiment.key} title={t(experiment.title)} hint={t(experiment.hint)} action={<><button type="button" className="button button-secondary" onClick={() => setLearnMore(experiment.key)}>{t("ai.learnMore")}</button><Switch size="sm" checked={values[experiment.key]} onCheckedChange={(value) => setValues({ ...values, [experiment.key]: value })} aria-label={t("ai.enableExperiment", { name: t(experiment.title) })} /></>} />)}</SettingCards><SaveFooter state={state} /></section></form>{learnMore && <ExperimentDialog experiment={experiments.find((item) => item.key === learnMore) ?? experiments[0]} enabled={values[learnMore as keyof typeof values] === true} onClose={() => setLearnMore(null)} />}</>;
}

export function LevelingSettings({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const { t } = useStrings("dashboard");
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
  const submit = (event: FormEvent) => { event.preventDefault(); if (rewards.some((row) => !row.level.trim() !== !row.role)) { notifyError(t("leveling.incompleteReward"), "settings-save"); return; } setState({ saving: true }); notifyLoading(t("leveling.saving"), "settings-save"); saveConfig(guildId, "leveling", { ...values, level_roles: rewardPayload }, csrfToken).then((result) => { applyConfig(result.config || {}); applyRewards((result.config || {}).level_roles); setState({ saving: false }); notifySuccess(t("leveling.saved"), "settings-save"); }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : t("leveling.saveFailed"), "settings-save"); }); };
  const levelUpChannels = channelsWithSelected(resources, values.level_up_channel);
  const channels = [...(resources?.channels || []), ...(resources?.voice_channels || []).map((channel) => ({ ...channel, name: `🔊 ${channel.name}` }))];
  const channelName = (id: string) => channels.find((channel) => String(channel.id) === id)?.name || t("leveling.channelFallback", { id });
  const toggleExcluded = (id: string) => setValues({ ...values, xp_excluded_channels: values.xp_excluded_channels.includes(id) ? values.xp_excluded_channels.filter((selected) => selected !== id) : [...values.xp_excluded_channels, id] });
  const roles = resources?.roles || [];
  // Rows the member has not finished filling in are dropped rather than sent.
  const rewardPayload = Object.fromEntries(rewards.filter((row) => row.level.trim() && row.role).map((row) => [String(Number(row.level)), row.role]));
  const updateReward = (index: number, patch: Partial<{ level: string; role: string }>) => setRewards(rewards.map((row, rowIndex) => rowIndex === index ? { ...row, ...patch } : row));
  return <><SettingsIntro className="leveling-settings-intro" icon="spark" label={t("leveling.kicker")} title={t(values.xp_enabled ? "leveling.flowing" : "leveling.paused")} text={t("leveling.introText")} /><form onSubmit={submit} className="settings-stack"><section className="dash-panel settings-panel"><SettingsSectionTitle label={t("leveling.settingsLabel")} title={t("leveling.settingsTitle")} detail={t("leveling.settingsDetail")} icon="spark" /><SettingCards><SettingCard title={t("leveling.enable")} hint={t("leveling.enableHint")} action={<Switch checked={values.xp_enabled} onCheckedChange={(value) => setValues({ ...values, xp_enabled: value })} aria-label={t("leveling.enable")} />} /></SettingCards><div className="form-grid"><Field label={t("leveling.multiplierLabel")} hint={t("leveling.multiplierHint")}><input type="number" min="0.1" max="10" step="0.1" value={values.xp_multiplier} onChange={(e) => setValues({ ...values, xp_multiplier: e.target.value as unknown as number })} /></Field><Field label={t("leveling.cooldownLabel")} hint={t("leveling.cooldownHint")}><input type="number" min="0" max="86400" value={values.xp_cooldown} onChange={(e) => setValues({ ...values, xp_cooldown: e.target.value as unknown as number })} /></Field><Field label={t("leveling.levelUpChannel")}><ChannelSelect channels={levelUpChannels} value={values.level_up_channel} placeholder={t("leveling.sameChannel")} onChange={(level_up_channel) => setValues({ ...values, level_up_channel })} /></Field>        <Field label={t("leveling.levelUpMessage")} hint={t("leveling.levelUpHint")}><textarea rows={3} maxLength={1000} value={values.level_up_message} onChange={(e) => setValues({ ...values, level_up_message: e.target.value })} placeholder={t("leveling.levelUpPlaceholder")} />{values.level_up_message.trim() && <DiscordMarkdown text={values.level_up_message.replace(/\{mention\}/g, "@member").replace(/\{level\}/g, "12").replace(/\{name\}/g, "member").replace(/\{guild\}/g, t("leveling.previewGuild"))} className="role-select-preview" interactiveUsers={false} />}</Field>
</div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label={t("leveling.channelsLabel")} title={t("leveling.channelsTitle")} detail={t("leveling.channelsDetail")} icon="settings" /><SettingCards><SettingCard title={t("leveling.voice")} hint={t("leveling.voiceHint")} action={<Switch checked={values.xp_vc_enabled} onCheckedChange={(value) => setValues({ ...values, xp_vc_enabled: value })} aria-label={t("leveling.voice")} />} /></SettingCards><Field label={t("leveling.excludedLabel")} hint={t("leveling.excludedHint")}><div className="role-select role-select-multiple"><span className="role-select-control"><select multiple value={values.xp_excluded_channels} onChange={(event) => setValues({ ...values, xp_excluded_channels: Array.from(event.currentTarget.selectedOptions, (option) => option.value) })} size={Math.min(Math.max(channels.length, 3), 7)} aria-label={t("leveling.excludedAria")}>{channels.map((channel) => <option key={channel.id} value={channel.id}>#{channel.name}</option>)}</select></span>{values.xp_excluded_channels.length > 0 && <div className="role-select-selected" aria-label={t("leveling.excludedCountAria", { count: values.xp_excluded_channels.length })}>{values.xp_excluded_channels.map((id) => <span className="role-select-chip" key={id}>#{channelName(id)}<button type="button" onClick={() => toggleExcluded(id)} aria-label={t("leveling.stopExcluding", { channel: channelName(id) })}><X size={12} aria-hidden="true" /></button></span>)}</div>}</div></Field></section><section className="dash-panel settings-panel"><SettingsSectionTitle label={t("leveling.rewardsLabel")} title={t("leveling.rewardsTitle")} detail={t("leveling.rewardsDetail")} icon="spark" /><div className="level-reward-editor"><div className="level-reward-toolbar"><span className="level-reward-summary"><span className={`status-dot${rewards.length === 0 ? " is-idle" : ""}`} />{rewards.length === 0 ? t("leveling.noRewards") : t(rewards.length === 1 ? "leveling.rewardsOne" : "leveling.rewardsMany", { count: rewards.length })}</span><button type="button" className="button button-muted button-small" onClick={() => setRewards([...rewards, { level: "", role: "" }])}>＋ {t("leveling.addReward")}</button></div>{rewards.length === 0 ? <div className="level-reward-empty"><strong>{t("leveling.emptyTitle")}</strong><span>{t("leveling.emptyBody")}</span></div> : <ol className="level-reward-list">{rewards.map((row, index) => <li className="level-reward-card" key={index}><label className="level-reward-field level-reward-field-level"><span>{t("leveling.levelLabel")}</span><input aria-label={t("leveling.rewardLevelAria", { count: index + 1 })} type="number" inputMode="numeric" min="1" max="1000" value={row.level} onChange={(event) => updateReward(index, { level: event.target.value })} placeholder="10" /></label><div className="level-reward-field level-reward-field-role"><span>{t("leveling.roleLabel")}</span><RoleSelect roles={roles} value={row.role} placeholder={t("leveling.rolePlaceholder")} ariaLabel={t("leveling.roleAria", { level: row.level || index + 1 })} onChange={(value) => updateReward(index, { role: String(value) })} /></div><button type="button" className="level-reward-remove" onClick={() => setRewards(rewards.filter((_, rowIndex) => rowIndex !== index))} aria-label={t("leveling.removeRewardAria", { level: row.level || index + 1 })}><Trash2 size={14} aria-hidden="true" /><span>{t("server.remove")}</span></button></li>)}</ol>}<small className="level-reward-note">{t("leveling.rewardsNote")}</small></div></section><SaveFooter state={state} /></form></>;
}

export function CustomizationSettings({ guildId, config, csrfToken }: { guildId: string; config: GuildConfig | null; csrfToken?: string }) {
  const { t } = useStrings("dashboard");
  const profile = config?.server?.profile || {};
  // A server inherits Niko's global avatar and banner until it sets its own.
  const globalProfile: GlobalProfile = config?.server?.global_profile || {};
  // Discord decides the tick, so the badge follows the application's real
  // verified state instead of a per-server setting.
  const botConfig = useBotConfig();
  const botVerified = Boolean(botConfig?.bot_verified);
  // Discord no longer tags migrated accounts (they report "0"), so only append
  // a discriminator when the bot actually has one.
  const botTag = botConfig?.bot_discriminator && botConfig.bot_discriminator !== "0" ? `#${botConfig.bot_discriminator}` : "";
  const botUsername = botConfig?.bot_name ? `${botConfig.bot_name.trim()}${botTag}` : "";
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
    event.preventDefault(); setState({ saving: true }); notifyLoading(t("profile.saving"), "settings-save");
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
      });setImageChoice(null); setState({ saving: false }); notifySuccess(t("profile.saved"), "settings-save");
    }).catch((error) => { setState({ saving: false }); notifyError(error instanceof Error ? error.message : t("profile.saveFailed"), "settings-save"); });
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
    if (!file.type.startsWith("image/")) { notifyError(t("profile.imageTypeError"), "profile-image"); return; }
    if (file.size > 8 * 1024 * 1024) { notifyError(t("profile.imageSizeError"), "profile-image"); return; }
    const reader = new FileReader();
    reader.onload = () => {
      const data = typeof reader.result === "string" ? reader.result : "";
      if (kind === "avatar") updateValues({ avatar_upload_data: data });
      else updateValues({ banner_upload_data: data });
      setImageChoice(null);
      clearToasts("profile-image");
    };
    reader.onerror = () => notifyError(t("profile.imageReadError"), "profile-image");
    reader.readAsDataURL(file);
  };
  const colors = nameSettings.colors || [];
  const colorHex = (value: number) => `#${Math.max(0, Math.min(0xffffff, value)).toString(16).padStart(6, "0")}`;
  const colorOptions = [{ label: "profile.color.white", value: 16777215 }, { label: "profile.color.black", value: 0 }, { label: "profile.color.blurple", value: 5793266 }, { label: "profile.color.green", value: 5763719 }, { label: "profile.color.red", value: 15548997 }, { label: "profile.color.yellow", value: 16705372 }, { label: "profile.color.pink", value: 16711935 }, { label: "profile.color.purple", value: 8388736 }, { label: "profile.color.blue", value: 5865 }, { label: "profile.color.gold", value: 16766720 }, { label: "profile.color.cyan", value: 65535 }];
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
  // The bot's own bio, used wherever this server has not written one yet.
  const inheritedBio = globalProfile.bio?.trim() || "";
  const previewBio = (values.bio || inheritedBio).trim();
  // True while every image in this server's preview still comes from Niko's global profile.
  const inheritsGlobalImages = !values.avatar_upload_data && !values.avatar_url && !values.banner_upload_data && !values.banner_url && Boolean(inheritedAvatar || inheritedBanner);
  return <>
    <DashHeading eyebrow={t("profile.eyebrow")} title={t("profile.title")} text={t("profile.text")} />
    <SettingsIntro icon="paint" label={t("profile.kicker")} title={t("profile.introTitle")} text={t("profile.introText")} />
    <form onSubmit={submit} className="settings-stack profile-editor-form">
      <section className="dash-panel settings-panel profile-editor-panel">
        <div className="profile-editor-heading"><div><span className="panel-kicker">{t("profile.previewKicker")}</span><h2>{t("profile.previewTitle")}</h2><p>{t("profile.previewText")}</p></div><span className="profile-server-tag"><span className="status-dot" /> {t("profile.serverOnly")}</span></div>
        <div className="profile-preview-card">
          <button type="button" className="profile-preview-banner" onClick={() => chooseImage("banner")} style={values.banner_upload_data || values.banner_url || inheritedBanner ? { backgroundImage: `linear-gradient(180deg, transparent, rgba(9,10,12,.4)), url("${values.banner_upload_data || values.banner_url || inheritedBanner}")` } : undefined} aria-label={t("profile.changeBanner")}><span><Icon name="paint" size={14} /></span></button>
          <button type="button" className="profile-preview-avatar" onClick={() => chooseImage("avatar")} aria-label={t("profile.changeAvatar")}>{values.avatar_upload_data || values.avatar_url || inheritedAvatar ? <img src={values.avatar_upload_data || values.avatar_url || inheritedAvatar} alt="" /> : <span>N</span>}<i><Icon name="paint" size={13} /></i></button>
          <div className="profile-preview-body">
            <div className="profile-preview-identity">
              <button type="button" className={`profile-preview-name profile-preview-name-font-${editor === "name" ? previewNameSettings.font : values.name_font_id}`} style={editor === "name" ? namePreviewStyle : nameStyle} onClick={() => { setNameSettings({ font: values.name_font_id, effect: values.name_effect_id, colors: values.name_colors }); setEditor("name"); }} aria-label={t("profile.editNameAria")}>{values.display_name || "Niko"}</button>
              <DiscordAppBadge verified={botVerified} />
            </div>
            {botUsername && <span className="profile-preview-handle">{botUsername}</span>}
            <div className="profile-preview-divider" />
            <span className="profile-preview-label">{t("profile.aboutMe")}</span>
            <div
              className={`profile-preview-bio${previewBio ? "" : " is-empty"}`}
              role="button"
              tabIndex={0}
              aria-label={t("profile.editBio")}
              onClick={(event) => {
                // A link inside the rendered bio keeps its own behaviour.
                if ((event.target as HTMLElement).closest("a")) return;
                setEditor("bio");
              }}
              onKeyDown={(event) => {
                if (event.key !== "Enter" && event.key !== " ") return;
                event.preventDefault();
                setEditor("bio");
              }}
            >
              {previewBio ? <DiscordMarkdown text={previewBio} guildId={guildId} interactiveUsers={false} /> : t("profile.addBio")}
            </div>
          </div>
        </div>
        <div className="profile-edit-hint"><Icon name="spark" size={14} /> {t(inheritsGlobalImages ? "profile.hintInherited" : "profile.hint")}</div>
      </section>
      <SaveFooter state={state} />
    </form>
    {imageChoice && createPortal(<div className="profile-editor-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setImageChoice(null); }}><section className="profile-editor-dialog profile-image-dialog" role="dialog" aria-modal="true" aria-labelledby="profile-image-title"><header><div><span className="panel-kicker">{t("profile.imageKicker")}</span><h2 id="profile-image-title">{t(imageChoice === "avatar" ? "profile.changeAvatar" : "profile.changeBanner")}</h2></div><button type="button" className="profile-editor-close" onClick={() => setImageChoice(null)} aria-label={t("profile.closeImageOptions")}><X size={17} /></button></header><div className="profile-image-choice-tabs"><button type="button" className={imageSource === "file" ? "active" : ""} onClick={() => setImageSource("file")}>{t("profile.uploadToDiscord")}</button><button type="button" className={imageSource === "url" ? "active" : ""} onClick={() => setImageSource("url")}>{t("profile.useImageUrl")}</button></div>{imageSource === "file" ? <div className="profile-image-upload"><input ref={imageChoice === "avatar" ? avatarFileRef : bannerFileRef} type="file" accept="image/*" onChange={(event) => readImageFile(imageChoice, event.target.files?.[0])} /><p>{t("profile.uploadText")}</p><button type="button" className="button button-primary" onClick={() => (imageChoice === "avatar" ? avatarFileRef.current : bannerFileRef.current)?.click()}>{t("profile.chooseImage")}</button></div> : <Field label={t("profile.imageUrlLabel")} hint={t("profile.imageUrlHint")}><input autoFocus type="url" value={imageChoice === "avatar" ? values.avatar_url : values.banner_url} onChange={(event) => imageChoice === "avatar" ? updateValues({ avatar_url: event.target.value, avatar_upload_data: "" }) : updateValues({ banner_url: event.target.value, banner_upload_data: "" })} placeholder="https://cdn.example.com/image.png" /></Field>}<footer><button type="button" className="button button-quiet" onClick={() => setImageChoice(null)}>{t("profile.cancel")}</button><button type="button" className="button button-primary" onClick={() => setImageChoice(null)}>{t("profile.done")}</button></footer></section></div>, document.body)}
    {editor && createPortal(<div className="profile-editor-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setEditor(null); }}><section className="profile-editor-dialog" role="dialog" aria-modal="true" aria-labelledby="profile-editor-title"><header><div><span className="panel-kicker">{t("profile.editKicker")}</span><h2 id="profile-editor-title">{editor === "name" ? t("profile.nameAndStyle") : t("profile.editBio")}</h2></div><button type="button" className="profile-editor-close" onClick={() => setEditor(null)} aria-label={t("profile.closeEditor")}><X size={17} /></button></header>{editor === "bio" && <Field label={t("profile.aboutNiko")} hint={t("profile.bioCount", { count: values.bio.length })}><textarea autoFocus maxLength={190} rows={5} value={values.bio} onChange={(e) => updateValues({ bio: e.target.value })} placeholder={inheritedBio} /></Field>}{editor === "name" && <><Field label={t("profile.displayName")} hint={t("profile.nameCount", { count: values.display_name.length })}><input autoFocus maxLength={32} value={values.display_name} onChange={(e) => updateValues({ display_name: e.target.value })} placeholder="Niko" /></Field><Field label={t("profile.font")}><Select placeholder={null} options={localizeOptions(NAME_FONTS, t)} value={String(nameSettings.font)} onChange={(value) => setNameSettings({ ...nameSettings, font: Number(value) })} /></Field><Field label={t("profile.colorStyle")}><Select placeholder={null} options={localizeOptions(NAME_EFFECTS, t)} value={String(nameSettings.effect)} onChange={(value) => setNameSettings({ ...nameSettings, effect: Number(value) })} /></Field><div className="profile-color-fields">{[0, 1].slice(0, nameSettings.effect === 2 ? 2 : 1).map((index) => <Field key={index} label={t("profile.colorIndex", { count: index + 1 })}><Select placeholder={null} options={localizeOptions(colorOptions.map((option) => ({ value: String(option.value), label: option.label })), t)} value={String(colors[index] ?? (index ? 5763719 : 5793266))} onChange={(value) => { const next = [...colors]; next[index] = Number(value); setNameSettings({ ...nameSettings, colors: next }); }} /></Field>)}</div></>}<footer><button type="button" className="button button-quiet" onClick={() => setEditor(null)}>{t("profile.done")}</button><button type="button" className="button button-primary" onClick={() => { if (editor === "name") updateValues({ name_font_id: nameSettings.font, name_effect_id: nameSettings.effect, name_colors: nameSettings.colors }); setEditor(null); }}>{t("profile.applyToPreview")}</button></footer></section></div>, document.body)}
  </>;
}