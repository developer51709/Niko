import { FormEvent, useEffect, useState } from "react";
import { saveConfig } from "../../api";
import { Icon } from "../Icon";
import type { GuildConfig, GuildResources } from "../../types";
import { DashHeading } from "./DashboardViews";

type SaveState = { saving: boolean; message: string; error: string };
const initialSave: SaveState = { saving: false, message: "", error: "" };

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return <label className="form-field"><span className="form-label">{label}</span>{children}{hint && <small>{hint}</small>}</label>;
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
  const flags = [["antispam", "Anti-spam", "Detect repeated messages"], ["antilink", "Invite links", "Remove Discord invite links"], ["badwords", "Blocked words", "Filter words from the server list"], ["massmention", "Mass mentions", "Limit mention floods"], ["antinuke", "Anti-nuke", "Protect channels and roles"], ["antiraid", "Join raid protection", "React to sudden join waves"], ["antiraid_ext", "External app protection", "Detect user-installed app abuse"]];
  return <>
    <DashHeading eyebrow="Moderation" title="Keep the room feeling good." text="Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration." />
    <form onSubmit={submit} className="settings-stack">
      <section className="dash-panel settings-panel"><div className="panel-heading"><div><span className="panel-kicker">Protection rules</span><h3>AutoMod modules</h3></div><span className="panel-icon"><Icon name="shield" /></span></div><div className="setting-list">
        {flags.map(([key, label, hint]) => <label className="setting-row" key={key}><span><strong>{label}</strong><small>{hint}</small></span><input type="checkbox" checked={Boolean(values.automod?.[key])} onChange={(e) => updateNested("automod", key, e.target.checked)} /><i aria-hidden="true" /></label>)}
      </div></section>
      <section className="dash-panel settings-panel"><div className="panel-heading"><div><span className="panel-kicker">Thresholds</span><h3>Choose when protection steps in</h3></div></div><div className="form-grid">
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
  const [values, setValues] = useState({ personality: "cafe", enabled: true, ai_actions_experiment: false, better_context_experiment: false });
  const [state, setState] = useState(initialSave);
  useEffect(() => { const ai = config?.ai || {}; setValues({ personality: ai.personality || "cafe", enabled: ai.enabled !== "False" && ai.enabled !== false, ai_actions_experiment: ai.ai_actions_experiment === true || ai.ai_actions_experiment === "True", better_context_experiment: ai.better_context_experiment === true || ai.better_context_experiment === "True" }); }, [config]);
   const submit = (event: FormEvent) => { event.preventDefault(); setState({ saving: true, message: "", error: "" }); saveConfig(guildId, "ai", values, csrfToken).then((result) => { const ai = result.config || {}; setValues({ personality: ai.personality === "normal" ? "normal" : "cafe", enabled: ai.enabled !== "False" && ai.enabled !== false, ai_actions_experiment: ai.ai_actions_experiment === true || ai.ai_actions_experiment === "True", better_context_experiment: ai.better_context_experiment === true || ai.better_context_experiment === "True" }); setState({ saving: false, message: "AI settings saved to Niko.", error: "" }); }).catch((error) => setState({ saving: false, message: "", error: error instanceof Error ? error.message : "Could not save settings." })); };
  return <><DashHeading eyebrow="AI controls" title="Give Niko the right tone." text="AI is optional, configurable per server, and designed to stay out of the way when the room does not need it." /><form onSubmit={submit} className="settings-stack"><section className="dash-panel settings-panel"><div className="panel-heading"><div><span className="panel-kicker">Conversation</span><h3>Core settings</h3></div><span className="panel-icon"><Icon name="settings" /></span></div>
    <label className="setting-row"><span><strong>Enable AI chat</strong><small>Respond when Niko is mentioned</small></span><input type="checkbox" checked={values.enabled} onChange={(e) => setValues({ ...values, enabled: e.target.checked })} /><i aria-hidden="true" /></label>
    <div className="personality-options"><button type="button" className={values.personality === "cafe" ? "personality active" : "personality"} onClick={() => setValues({ ...values, personality: "cafe" })}><span className="personality-mark">n</span><span><strong>Café</strong><small>Warm, playful, familiar</small></span></button><button type="button" className={values.personality === "normal" ? "personality active" : "personality"} onClick={() => setValues({ ...values, personality: "normal" })}><span className="personality-mark">—</span><span><strong>Normal</strong><small>Clear and straightforward</small></span></button></div>
  </section><section className="dash-panel settings-panel"><div className="panel-heading"><div><span className="panel-kicker">Experiments</span><h3>Optional context</h3></div></div><label className="setting-row"><span><strong>Better context</strong><small>Use the last five channel messages</small></span><input type="checkbox" checked={values.better_context_experiment} onChange={(e) => setValues({ ...values, better_context_experiment: e.target.checked })} /><i aria-hidden="true" /></label><label className="setting-row"><span><strong>AI actions</strong><small>Allow confirmed actions requested in chat</small></span><input type="checkbox" checked={values.ai_actions_experiment} onChange={(e) => setValues({ ...values, ai_actions_experiment: e.target.checked })} /><i aria-hidden="true" /></label><SaveFooter state={state} /></section></form></>;
}

export function LevelingSettings({ guildId, config, resources, csrfToken }: { guildId: string; config: GuildConfig | null; resources: GuildResources | null; csrfToken?: string }) {
  const level = config?.leveling || {};
  const [values, setValues] = useState({ xp_enabled: true, xp_multiplier: 1, xp_cooldown: 0, level_up_channel: "", level_up_message: "" });
  const [state, setState] = useState(initialSave);
  useEffect(() => setValues({ xp_enabled: level.xp_enabled !== false, xp_multiplier: level.xp_multiplier ?? 1, xp_cooldown: level.xp_cooldown ?? 0, level_up_channel: level.level_up_channel || "", level_up_message: level.level_up_message || "" }), [config]);
   const submit = (event: FormEvent) => { event.preventDefault(); setState({ saving: true, message: "", error: "" }); saveConfig(guildId, "leveling", values, csrfToken).then((result) => { const level = result.config || {}; setValues({ xp_enabled: level.xp_enabled !== false, xp_multiplier: level.xp_multiplier ?? 1, xp_cooldown: level.xp_cooldown ?? 0, level_up_channel: level.level_up_channel || "", level_up_message: level.level_up_message || "" }); setState({ saving: false, message: "Leveling settings saved to Niko.", error: "" }); }).catch((error) => setState({ saving: false, message: "", error: error instanceof Error ? error.message : "Could not save settings." })); };
  return <form onSubmit={submit} className="settings-stack"><section className="dash-panel settings-panel"><div className="panel-heading"><div><span className="panel-kicker">Leveling settings</span><h3>Shape the pace</h3></div><span className="panel-icon"><Icon name="spark" /></span></div><label className="setting-row"><span><strong>Enable XP</strong><small>Track activity and award levels</small></span><input type="checkbox" checked={values.xp_enabled} onChange={(e) => setValues({ ...values, xp_enabled: e.target.checked })} /><i aria-hidden="true" /></label><div className="form-grid"><Field label="XP multiplier" hint="From 0.1× to 10×"><input type="number" min="0.1" max="10" step="0.1" value={values.xp_multiplier} onChange={(e) => setValues({ ...values, xp_multiplier: e.target.value as unknown as number })} /></Field><Field label="Cooldown (seconds)" hint="0 disables the cooldown"><input type="number" min="0" max="86400" value={values.xp_cooldown} onChange={(e) => setValues({ ...values, xp_cooldown: e.target.value as unknown as number })} /></Field><Field label="Level-up channel"><select value={values.level_up_channel} onChange={(e) => setValues({ ...values, level_up_channel: e.target.value })}><option value="">Same channel</option>{resources?.channels.map((channel) => <option value={channel.id} key={channel.id}>#{channel.name}</option>)}</select></Field><Field label="Level-up message" hint="Use {mention}, {level}, {name}, or {guild}"><textarea rows={3} maxLength={1000} value={values.level_up_message} onChange={(e) => setValues({ ...values, level_up_message: e.target.value })} placeholder="Leave blank for Niko's default message" /></Field></div><SaveFooter state={state} /></section></form>;
}