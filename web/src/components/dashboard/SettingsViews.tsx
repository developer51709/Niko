import { type CSSProperties, type FormEvent, type ReactNode, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { saveConfig, saveProfile } from "../../api";
import { Icon } from "../Icon";
import { X } from "lucide-react";
import type { GuildConfig, GuildResources, GuildProfile } from "../../types";
import { DashHeading } from "./DashboardViews";

type SaveState = { saving: boolean; message: string; error: string };
const initialSave: SaveState = { saving: false, message: "", error: "" };

function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return <label className="form-field"><span className="form-label">{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

function channelsWithSelected(resources: GuildResources | null, selected: string | number | null | undefined) {
  const selectedId = selected ? String(selected) : "";
  const channels = resources?.channels || [];
  if (!selectedId || channels.some((channel) => String(channel.id) === selectedId)) return channels;
  return [{ id: selectedId, name: `Saved channel · ${selectedId}` }, ...channels];
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
  return <div className="setting-footer">{state.error ? <span className="form-error" role="alert">{state.error}</span> : <span role="status">{state.message || "Changes apply to this server."}</span>}<button className="button button-primary" type="submit" disabled={state.saving}>{state.saving ? "Saving…" : "Save changes"}</button></div>;
}

export function ModerationView({ guildId, config, csrfToken }: { guildId: string; config: GuildConfig | null; csrfToken?: string }) {
  const [values, setValues] = useState<Record<string, any>>({});
  const [state, setState] = useState(initialSave);
  useEffect(() => {
    const moderation = config?.moderation || {};
    setValues({
      automod: { ...(moderation.automod || {}) },
      spam_threshold: moderation.spam_threshold ?? 6,
      spam_interval: moderation.spam_interval ?? 7,
      max_mentions: moderation.max_mentions ?? 5,
      antinuke: { ...(moderation.antinuke || {}) },
      antiraid: { ...(moderation.antiraid || {}) },
      antiraid_ext: { ...(moderation.antiraid_ext || {}) },
    });
  }, [config]);
  const updateNested = (section: string, key: string, value: unknown) => setValues((current) => ({ ...current, [section]: { ...current[section], [key]: value } }));
  const submit = (event: FormEvent) => {
    event.preventDefault(); setState({ saving: true, message: "", error: "" });
    saveConfig(guildId, "automod", values, csrfToken).then((result) => {
      const moderation = result.config || {};
      setValues({
        automod: { ...(moderation.automod || {}) },
        spam_threshold: moderation.spam_threshold ?? 6,
        spam_interval: moderation.spam_interval ?? 7,
        max_mentions: moderation.max_mentions ?? 5,
        antinuke: { ...(moderation.antinuke || {}) },
        antiraid: { ...(moderation.antiraid || {}) },
        antiraid_ext: { ...(moderation.antiraid_ext || {}) },
      });
      setState({ saving: false, message: "Moderation settings saved to Niko.", error: "" });
    }).catch((error) => setState({ saving: false, message: "", error: error instanceof Error ? error.message : "Could not save settings." }));
  };
  const flags = [["antispam", "Anti-spam", "Detect repeated messages"], ["antilink", "Invite links", "Remove Discord invite links"], ["badwords", "Blocked words", "Filter words from the server list"], ["massmention", "Mass mentions", "Limit mention floods"], ["scam_image_filter", "Scam image filter", "Delete known MrBeast scam images"], ["nsfw_image_filter", "NSFW image filter", "AI-detect and delete NSFW images"], ["antinuke", "Anti-nuke", "Protect channels and roles"], ["antiraid", "Join raid protection", "React to sudden join waves"], ["antiraid_ext", "External app protection", "Detect user-installed app abuse"]] as const;
  const experimentalFlags = new Set(["scam_image_filter", "nsfw_image_filter"]);
  const activeFlags = flags.filter(([key]) => Boolean(values.automod?.[key])).length;
  return <>
    <DashHeading eyebrow="Moderation" title="Keep the room feeling good." text="Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration." />
    <SettingsIntro icon="shield" label="Protection desk" title={`${activeFlags} of ${flags.length} safeguards active`} text="Start with the essentials, then tune thresholds below when you know the room’s rhythm." />
    <form onSubmit={submit} className="settings-stack">
      <section className="dash-panel settings-panel"><SettingsSectionTitle label="Protection rules" title="AutoMod modules" detail="Toggle only the responses you want Niko to handle." icon="shield" /><div className="setting-list">
        {flags.map(([key, label, hint]) => <label className="setting-row" key={key}><span><strong>{label}{experimentalFlags.has(key) && <em className="setting-flag-experimental">experimental</em>}</strong><small>{hint}</small></span><input type="checkbox" checked={Boolean(values.automod?.[key])} onChange={(e) => updateNested("automod", key, e.target.checked)} /><i aria-hidden="true" /></label>)}
        {experimentalFlags.size > 0 && <p className="setting-note">⚠️ The scam image filter is still in early testing and may have some reliability issues.</p>}
      </div></section>
      <section className="dash-panel settings-panel"><SettingsSectionTitle label="Thresholds" title="Choose when protection steps in" detail="These limits apply across the server." /><div className="form-grid">
        <Field label="Spam messages" hint="Messages inside the spam interval"><input type="number" min="1" max="100" value={values.spam_threshold ?? 6} onChange={(e) => setValues({ ...values, spam_threshold: e.target.value })} /></Field>
        <Field label="Spam interval (seconds)"><input type="number" min="1" max="3600" value={values.spam_interval ?? 7} onChange={(e) => setValues({ ...values, spam_interval: e.target.value })} /></Field>
        <Field label="Maximum mentions"><input type="number" min="1" max="100" value={values.max_mentions ?? 5} onChange={(e) => setValues({ ...values, max_mentions: e.target.value })} /></Field>
        <Field label="Anti-raid joins" hint="Joins inside the join interval"><input type="number" min="1" max="1000" value={values.antiraid?.join_threshold ?? 10} onChange={(e) => updateNested("antiraid", "join_threshold", e.target.value)} /></Field>
        <Field label="Anti-raid interval (seconds)"><input type="number" min="1" max="3600" value={values.antiraid?.join_interval ?? 10} onChange={(e) => updateNested("antiraid", "join_interval", e.target.value)} /></Field>
        <Field label="Anti-raid action"><select value={values.antiraid?.action ?? "kick"} onChange={(e) => updateNested("antiraid", "action", e.target.value)}><option value="kick">Kick</option><option value="ban">Ban</option><option value="softban">Soft-ban</option><option value="slowmode">Slowmode</option><option value="lockdown">Lockdown</option></select></Field>
      </div><SaveFooter state={state} /></section>
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
  const submit = (event: FormEvent) => { event.preventDefault(); setState({ saving: true, message: "", error: "" }); saveConfig(guildId, "ai", values, csrfToken).then((result) => { applyConfig(result.config || {}); setState({ saving: false, message: "AI settings saved.", error: "" }); }).catch((error) => setState({ saving: false, message: "", error: error instanceof Error ? error.message : "Could not save settings." })); };
  const experiments = [{ key: "better_context_experiment", title: "Better context", hint: "Use the last five channel messages", info: "Adds recent conversation and replied-to message context so responses understand ongoing discussions more naturally. It is useful for follow-ups, but sends more conversation context to the AI provider." }, { key: "ai_actions_experiment", title: "AI actions", hint: "Allow confirmed actions requested in chat", info: "Lets the AI propose polls and server actions such as moderation or channel management. Every action requires confirmation and is still limited by Discord permissions." }, { key: "multimodal_experiment", title: "Multimodal conversation", hint: "Understand images and voice in AI replies", info: "Allows Niko to inspect image attachments and use voice-message transcriptions as context when the AI is already triggered by name, ping, or the ai command. Attachments never start a conversation on their own. Media is processed only while enabled and provider usage costs may apply." }] as const;
  return <><DashHeading eyebrow="AI controls" title="Give your AI the right tone." text="Configure the AI identity, personality, and opt-in experiments for this server." /><SettingsIntro icon="settings" label="Conversation desk" title={values.enabled ? `${values.ai_name} is ready to respond` : `${values.ai_name} is staying quiet`} text="All settings apply only to this server." /><form onSubmit={submit} className="settings-stack"><section className="dash-panel settings-panel"><SettingsSectionTitle label="Conversation" title="Core settings" detail="Decide when the AI joins the conversation." icon="settings" /><div className="form-grid"><Field label="AI name" hint="1–32 characters; this is also the mention trigger"><input value={values.ai_name} maxLength={32} onChange={(e) => setValues({ ...values, ai_name: e.target.value })} /></Field></div><label className="setting-row"><span><strong>Enable AI chat</strong><small>Respond when the configured name is mentioned</small></span><input type="checkbox" checked={values.enabled} onChange={(e) => setValues({ ...values, enabled: e.target.checked })} /><i aria-hidden="true" /></label><div className="personality-options"><button type="button" className={values.personality === "cafe" ? "personality active" : "personality"} onClick={() => setValues({ ...values, personality: "cafe" })}><span className="personality-mark">n</span><span><strong>Café</strong><small>Warm, playful, familiar</small></span></button><button type="button" className={values.personality === "normal" ? "personality active" : "personality"} onClick={() => setValues({ ...values, personality: "normal" })}><span className="personality-mark">—</span><span><strong>Normal</strong><small>Clear and straightforward</small></span></button></div></section><section className="dash-panel settings-panel"><SettingsSectionTitle label="Experiments" title="Optional capabilities" detail="Each experiment includes a learn-more explanation before you enable it." />{experiments.map((experiment) => <div className="setting-row experiment-row" key={experiment.key}><span><strong>{experiment.title}</strong><small>{experiment.hint}</small></span><div className="experiment-actions"><button type="button" className="button button-secondary" onClick={() => setLearnMore(experiment.key)}>Learn more</button><label className="toggle-control" aria-label={`Enable ${experiment.title}`}><input type="checkbox" checked={values[experiment.key]} onChange={(e) => setValues({ ...values, [experiment.key]: e.target.checked })} /><i aria-hidden="true" /></label></div></div>)}<SaveFooter state={state} /></section></form>{learnMore && <div className="modal-backdrop" role="presentation" onClick={() => setLearnMore(null)}><div className="modal-card" role="dialog" aria-modal="true" aria-labelledby="ai-experiment-title" onClick={(e) => e.stopPropagation()}><div className="panel-heading"><div><span className="panel-kicker">AI experiment</span><h3 id="ai-experiment-title">{experiments.find((item) => item.key === learnMore)?.title}</h3></div><button type="button" className="button button-secondary" onClick={() => setLearnMore(null)}>Close</button></div><p>{experiments.find((item) => item.key === learnMore)?.info}</p></div></div>}</>;
}

export function LevelingSettings({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const level = config?.leveling || {};
  const [values, setValues] = useState({ xp_enabled: true, xp_multiplier: 1, xp_cooldown: 0, level_up_channel: "", level_up_message: "" });
  const [state, setState] = useState(initialSave);
  useEffect(() => setValues({ xp_enabled: level.xp_enabled !== false, xp_multiplier: level.xp_multiplier ?? 1, xp_cooldown: level.xp_cooldown ?? 0, level_up_channel: level.level_up_channel ? String(level.level_up_channel) : "", level_up_message: level.level_up_message || "" }), [config]);
   const submit = (event: FormEvent) => { event.preventDefault(); setState({ saving: true, message: "", error: "" }); saveConfig(guildId, "leveling", values, csrfToken).then((result) => { const level = result.config || {}; setValues({ xp_enabled: level.xp_enabled !== false, xp_multiplier: level.xp_multiplier ?? 1, xp_cooldown: level.xp_cooldown ?? 0, level_up_channel: level.level_up_channel ? String(level.level_up_channel) : "", level_up_message: level.level_up_message || "" }); setState({ saving: false, message: "Leveling settings saved to Niko.", error: "" }); }).catch((error) => setState({ saving: false, message: "", error: error instanceof Error ? error.message : "Could not save settings." })); };   const levelUpChannels = channelsWithSelected(resources, values.level_up_channel);
  return <><SettingsIntro className="leveling-settings-intro" icon="spark" label="Participation desk" title={values.xp_enabled ? "XP is flowing" : "XP is paused"} text="Set a pace that rewards regulars without turning every message into a transaction." /><form onSubmit={submit} className="settings-stack"><section className="dash-panel settings-panel"><SettingsSectionTitle label="Leveling settings" title="Shape the pace" detail="These controls apply to every member in this server." icon="spark" /><label className="setting-row"><span><strong>Enable XP</strong><small>Track activity and award levels</small></span><input type="checkbox" checked={values.xp_enabled} onChange={(e) => setValues({ ...values, xp_enabled: e.target.checked })} /><i aria-hidden="true" /></label><div className="form-grid"><Field label="XP multiplier" hint="From 0.1× to 10×"><input type="number" min="0.1" max="10" step="0.1" value={values.xp_multiplier} onChange={(e) => setValues({ ...values, xp_multiplier: e.target.value as unknown as number })} /></Field><Field label="Cooldown (seconds)" hint="0 disables the cooldown"><input type="number" min="0" max="86400" value={values.xp_cooldown} onChange={(e) => setValues({ ...values, xp_cooldown: e.target.value as unknown as number })} /></Field><Field label="Level-up channel"><select value={values.level_up_channel} onChange={(e) => setValues({ ...values, level_up_channel: e.target.value })}><option value="">Same channel</option>{levelUpChannels.map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}</select></Field><Field label="Level-up message" hint="Use {mention}, {level}, {name}, or {guild}"><textarea rows={3} maxLength={1000} value={values.level_up_message} onChange={(e) => setValues({ ...values, level_up_message: e.target.value })} placeholder="Leave blank for Niko's default message" /></Field></div><SaveFooter state={state} /></section></form></>;
}

export function CustomizationSettings({ guildId, config, csrfToken }: { guildId: string; config: GuildConfig | null; csrfToken?: string }) {
  const profile = config?.server?.profile || {};
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
    event.preventDefault(); setState({ saving: true, message: "", error: "" });
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
      });
      setImageChoice(null);
      setState({ saving: false, message: "Bot profile updated.", error: "" });
    }).catch((error) => setState({ saving: false, message: "", error: error instanceof Error ? error.message : "Could not save profile." }));
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
    if (!file.type.startsWith("image/")) { setState({ saving: false, message: "", error: "Choose an image file." }); return; }
    if (file.size > 8 * 1024 * 1024) { setState({ saving: false, message: "", error: "Images must be 8 MB or smaller." }); return; }
    const reader = new FileReader();
    reader.onload = () => {
      const data = typeof reader.result === "string" ? reader.result : "";
      if (kind === "avatar") updateValues({ avatar_upload_data: data });
      else updateValues({ banner_upload_data: data });
      setImageChoice(null);
      setState(initialSave);
    };
    reader.onerror = () => setState({ saving: false, message: "", error: "Could not read that image file." });
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
  return <>
    <DashHeading eyebrow="Customization" title="Niko's server presence." text="Shape how Niko appears in this server. Click any part of the preview to edit it." />
    <SettingsIntro icon="paint" label="Identity desk" title="Server-specific identity" text="Each server can have its own Niko persona. Changes apply only to this server." />
    <form onSubmit={submit} className="settings-stack profile-editor-form">
      <section className="dash-panel settings-panel profile-editor-panel">
        <div className="profile-editor-heading"><div><span className="panel-kicker">Live preview</span><h2>Your server profile</h2><p>Choose a surface to edit it. Your preview updates as you type.</p></div><span className="profile-server-tag"><span className="status-dot" /> Server only</span></div>
        <div className="profile-preview-card">
          <button type="button" className="profile-preview-banner" onClick={() => chooseImage("banner")} style={values.banner_upload_data || values.banner_url ? { backgroundImage: `linear-gradient(180deg, transparent, rgba(9,10,12,.4)), url("${values.banner_upload_data || values.banner_url}")` } : undefined} aria-label="Change profile banner"><span><Icon name="paint" size={14} /></span></button>
          <button type="button" className="profile-preview-avatar" onClick={() => chooseImage("avatar")} aria-label="Change profile avatar">{values.avatar_upload_data || values.avatar_url ? <img src={values.avatar_upload_data || values.avatar_url} alt="" /> : <span>N</span>}<i><Icon name="paint" size={13} /></i></button>
          <div className="profile-preview-body"><button type="button" className={`profile-preview-name profile-preview-name-font-${editor === "name" ? previewNameSettings.font : values.name_font_id}`} style={editor === "name" ? namePreviewStyle : nameStyle} onClick={() => { setNameSettings({ font: values.name_font_id, effect: values.name_effect_id, colors: values.name_colors }); setEditor("name"); }} aria-label="Edit display name and style">{values.display_name || "Niko"}</button><button type="button" className="profile-preview-bio" onClick={() => setEditor("bio")} aria-label="Edit bio">{values.bio || "A warm Discord companion, ready to help your community."}</button><div className="profile-preview-presence"><i /> Online · Bot</div></div>
        </div>
        <div className="profile-edit-hint"><Icon name="spark" size={14} /> Select the avatar, banner, display name, or bio above to customize it.</div>
      </section>
      <SaveFooter state={state} />
    </form>
    {imageChoice && createPortal(<div className="profile-editor-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setImageChoice(null); }}><section className="profile-editor-dialog profile-image-dialog" role="dialog" aria-modal="true" aria-labelledby="profile-image-title"><header><div><span className="panel-kicker">Profile image</span><h2 id="profile-image-title">Change {imageChoice}</h2></div><button type="button" className="profile-editor-close" onClick={() => setImageChoice(null)} aria-label="Close image options"><X size={17} /></button></header><div className="profile-image-choice-tabs"><button type="button" className={imageSource === "file" ? "active" : ""} onClick={() => setImageSource("file")}>Upload to Discord</button><button type="button" className={imageSource === "url" ? "active" : ""} onClick={() => setImageSource("url")}>Use image URL</button></div>{imageSource === "file" ? <div className="profile-image-upload"><input ref={imageChoice === "avatar" ? avatarFileRef : bannerFileRef} type="file" accept="image/*" onChange={(event) => readImageFile(imageChoice, event.target.files?.[0])} /><p>Set an image on this server’s Discord profile. Discord hosts it on its CDN. PNG, JPG, GIF, or WebP · max 8 MB.</p><button type="button" className="button button-primary" onClick={() => (imageChoice === "avatar" ? avatarFileRef.current : bannerFileRef.current)?.click()}>Choose image</button></div> : <Field label="Public image URL" hint="Must be an HTTPS image URL"><input autoFocus type="url" value={imageChoice === "avatar" ? values.avatar_url : values.banner_url} onChange={(event) => imageChoice === "avatar" ? updateValues({ avatar_url: event.target.value, avatar_upload_data: "" }) : updateValues({ banner_url: event.target.value, banner_upload_data: "" })} placeholder="https://cdn.example.com/image.png" /></Field>}<footer><button type="button" className="button button-quiet" onClick={() => setImageChoice(null)}>Cancel</button><button type="button" className="button button-primary" onClick={() => setImageChoice(null)}>Done</button></footer></section></div>, document.body)}
    {editor && createPortal(<div className="profile-editor-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setEditor(null); }}><section className="profile-editor-dialog" role="dialog" aria-modal="true" aria-labelledby="profile-editor-title"><header><div><span className="panel-kicker">Profile edit</span><h2 id="profile-editor-title">{editor === "name" ? "Name & style" : `Edit ${editor}`}</h2></div><button type="button" className="profile-editor-close" onClick={() => setEditor(null)} aria-label="Close editor"><X size={17} /></button></header>{editor === "bio" && <Field label="About Niko" hint={`${values.bio.length}/190 characters`}><textarea autoFocus maxLength={190} rows={5} value={values.bio} onChange={(e) => updateValues({ bio: e.target.value })} placeholder="A warm Discord companion" /></Field>}{editor === "name" && <><Field label="Display name" hint={`${values.display_name.length}/32 characters`}><input autoFocus maxLength={32} value={values.display_name} onChange={(e) => updateValues({ display_name: e.target.value })} placeholder="Niko" /></Field><Field label="Font"><select value={nameSettings.font} onChange={(e) => setNameSettings({ ...nameSettings, font: Number(e.target.value) })}><option value={3}>Sakura</option><option value={4}>Jellybean</option><option value={6}>Modern</option><option value={7}>Medieval</option><option value={8}>8Bit</option><option value={10}>Vampyre</option><option value={11}>gg sans (Default)</option><option value={12}>Tempo</option></select></Field><Field label="Color style"><select value={nameSettings.effect} onChange={(e) => setNameSettings({ ...nameSettings, effect: Number(e.target.value) })}><option value={1}>Solid</option><option value={2}>Gradient</option><option value={3}>Neon</option><option value={4}>Toon</option><option value={5}>Pop</option><option value={6}>Glow</option></select></Field><div className="profile-color-fields">{[0, 1].slice(0, nameSettings.effect === 2 ? 2 : 1).map((index) => <Field key={index} label={`Color ${index + 1}`}><select value={colors[index] ?? (index ? 5763719 : 5793266)} onChange={(e) => { const next = [...colors]; next[index] = Number(e.target.value); setNameSettings({ ...nameSettings, colors: next }); }}><option value="">Choose color</option>{colorOptions.map((option) => <option value={option.value} key={option.value}>{option.label}</option>)}</select></Field>)}</div></>}<footer><button type="button" className="button button-quiet" onClick={() => setEditor(null)}>Done</button><button type="button" className="button button-primary" onClick={() => { if (editor === "name") updateValues({ name_font_id: nameSettings.font, name_effect_id: nameSettings.effect, name_colors: nameSettings.colors }); setEditor(null); }}>Apply to preview</button></footer></section></div>, document.body)}
  </>;
}