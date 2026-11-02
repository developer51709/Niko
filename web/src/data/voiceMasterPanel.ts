// The strings the VoiceMaster control panel really renders, per language.
//
// These are copied from src/cogs/voicemaster/locales/*.json — the bot is the
// source of truth — so the landing page can replay the panel and its ephemeral
// replies exactly as members see them. Command names (Lock, Unlock, …) stay
// English in every language because they are literal commands, not prose.
//
// tests/test_voicemaster_panel.py checks that every string here still matches
// the bot's locale files.

export type PanelLanguage = "en" | "de" | "es" | "fr";

/** One button on the panel, in the panel's own order. */
export type PanelAction =
  | "lock"
  | "unlock"
  | "hide"
  | "reveal"
  | "claim"
  | "disconnect"
  | "view"
  | "increase"
  | "decrease";

export type PanelStrings = {
  title: string;
  /** The description that follows each command name in the legend. */
  legend: Record<PanelAction, string>;
  /** The ephemeral confirmation each action sends. */
  actions: Record<Exclude<PanelAction, "disconnect" | "view">, string>;
  info: {
    owner: string;
    members: string;
    limit: string;
    bitrate: string;
    region: string;
    status: string;
    noLimit: string;
    automatic: string;
    open: string;
    locked: string;
    hidden: string;
  };
  disconnect: { placeholder: string; option: string; done: string };
};

export const PANEL_LANGUAGES: { value: PanelLanguage; label: string; code: string }[] = [
  { value: "en", label: "English", code: "EN" },
  { value: "de", label: "Deutsch", code: "DE" },
  { value: "es", label: "Español", code: "ES" },
  { value: "fr", label: "Français", code: "FR" },
];

/** The command names the panel writes next to each emoji. */
export const PANEL_COMMANDS: Record<PanelAction, string> = {
  lock: "Lock",
  unlock: "Unlock",
  hide: "Hide",
  reveal: "Reveal",
  claim: "Claim",
  disconnect: "Disconnect",
  view: "View",
  increase: "Increase",
  decrease: "Decrease",
};

/** The bot's emoji keys for each button, with the ids from src/config/emojis.py. */
export const PANEL_EMOJI: Record<PanelAction | "tick" | "cross" | "unhide", { name: string; id: string }> = {
  lock: { name: "lock", id: "1564758089159282850" },
  unlock: { name: "unlock", id: "1564758095568183317" },
  hide: { name: "hide", id: "1564758085954965556" },
  unhide: { name: "unhide", id: "1564758092380377240" },
  reveal: { name: "unhide", id: "1564758092380377240" },
  claim: { name: "owner_icon", id: "1564758012453855323" },
  disconnect: { name: "disconnect", id: "1564757738427261120" },
  view: { name: "question", id: "1564757890798059540" },
  increase: { name: "plus", id: "1564757878680584365" },
  decrease: { name: "minus", id: "1564757858623684718" },
  tick: { name: "tick", id: "1564757931323293806" },
  cross: { name: "cross", id: "1564757780886331565" },
};

export const PANEL_STRINGS: Record<PanelLanguage, PanelStrings> = {
  en: {
    title: "VoiceMaster | Interface",
    legend: {
      lock: "the voice channel",
      unlock: "the voice channel",
      hide: "the voice channel",
      reveal: "the voice channel",
      claim: "the voice channel",
      disconnect: "a member",
      view: "channel information",
      increase: "the user limit",
      decrease: "the user limit",
    },
    actions: {
      lock: "Voice channel locked.",
      unlock: "Voice channel unlocked.",
      hide: "Voice channel hidden.",
      reveal: "Voice channel revealed.",
      claim: "Voice channel claimed.",
      increase: "User limit increased.",
      decrease: "User limit decreased.",
    },
    info: {
      owner: "Owner",
      members: "Members",
      limit: "Limit",
      bitrate: "Bitrate",
      region: "Region",
      status: "Status",
      noLimit: "No limit",
      automatic: "Automatic",
      open: "Open",
      locked: "Locked",
      hidden: "Hidden",
    },
    disconnect: {
      placeholder: "Choose members to disconnect...",
      option: "Disconnect {user}",
      done: "Disconnected: {users}",
    },
  },
  de: {
    title: "VoiceMaster | Interface",
    legend: {
      lock: "den Sprachkanal",
      unlock: "den Sprachkanal",
      hide: "den Sprachkanal",
      reveal: "den Sprachkanal",
      claim: "den Sprachkanal",
      disconnect: "ein Mitglied",
      view: "Kanalinformationen",
      increase: "das Nutzerlimit",
      decrease: "das Nutzerlimit",
    },
    actions: {
      lock: "Sprachkanal gesperrt.",
      unlock: "Sprachkanal entsperrt.",
      hide: "Sprachkanal verborgen.",
      reveal: "Sprachkanal wieder sichtbar.",
      claim: "Sprachkanal übernommen.",
      increase: "Nutzerlimit erhöht.",
      decrease: "Nutzerlimit verringert.",
    },
    info: {
      owner: "Besitzer",
      members: "Mitglieder",
      limit: "Limit",
      bitrate: "Bitrate",
      region: "Region",
      status: "Status",
      noLimit: "Kein Limit",
      automatic: "Automatisch",
      open: "Offen",
      locked: "Gesperrt",
      hidden: "Verborgen",
    },
    disconnect: {
      placeholder: "Mitglieder zum Trennen auswählen...",
      option: "{user} trennen",
      done: "Getrennt: {users}",
    },
  },
  es: {
    title: "VoiceMaster | Interfaz",
    legend: {
      lock: "el canal de voz",
      unlock: "el canal de voz",
      hide: "el canal de voz",
      reveal: "el canal de voz",
      claim: "el canal de voz",
      disconnect: "un miembro",
      view: "la información del canal",
      increase: "el límite de usuarios",
      decrease: "el límite de usuarios",
    },
    actions: {
      lock: "Canal de voz bloqueado.",
      unlock: "Canal de voz desbloqueado.",
      hide: "Canal de voz oculto.",
      reveal: "Canal de voz visible de nuevo.",
      claim: "Canal de voz reclamado.",
      increase: "Límite de usuarios aumentado.",
      decrease: "Límite de usuarios reducido.",
    },
    info: {
      owner: "Propietario",
      members: "Miembros",
      limit: "Límite",
      bitrate: "Bitrate",
      region: "Región",
      status: "Estado",
      noLimit: "Sin límite",
      automatic: "Automática",
      open: "Abierto",
      locked: "Bloqueado",
      hidden: "Oculto",
    },
    disconnect: {
      placeholder: "Elige los miembros a desconectar...",
      option: "Desconectar a {user}",
      done: "Desconectados: {users}",
    },
  },
  fr: {
    title: "VoiceMaster | Interface",
    legend: {
      lock: "le salon vocal",
      unlock: "le salon vocal",
      hide: "le salon vocal",
      reveal: "le salon vocal",
      claim: "le salon vocal",
      disconnect: "un membre",
      view: "les informations du salon",
      increase: "la limite d'utilisateurs",
      decrease: "la limite d'utilisateurs",
    },
    actions: {
      lock: "Salon vocal verrouillé.",
      unlock: "Salon vocal déverrouillé.",
      hide: "Salon vocal masqué.",
      reveal: "Salon vocal rendu visible.",
      claim: "Salon vocal pris en charge.",
      increase: "Limite d'utilisateurs augmentée.",
      decrease: "Limite d'utilisateurs réduite.",
    },
    info: {
      owner: "Propriétaire",
      members: "Membres",
      limit: "Limite",
      bitrate: "Débit",
      region: "Région",
      status: "Statut",
      noLimit: "Aucune limite",
      automatic: "Automatique",
      open: "Ouvert",
      locked: "Verrouillé",
      hidden: "Masqué",
    },
    disconnect: {
      placeholder: "Choisis les membres à déconnecter...",
      option: "Déconnecter {user}",
      done: "Déconnectés : {users}",
    },
  },
};

/** The owner of the demo channel and every mention the panel shows. */
export const PANEL_OWNER_ID = "1052690741874401360";

/** `SUPPORT_SERVER` in src/config/links.py: the site's own /discord route. */
export const PANEL_SUPPORT_URL = "https://niko.sryze.cc/discord";

/** Members Discord would list in the disconnect picker. */
export const PANEL_MEMBERS = ["Soren", "Mika", "Rowan"];
