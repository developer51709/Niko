import { useRef, useState } from "react";
import { DiscordAppBadge } from "./DiscordAppBadge";
import { DiscordEmoji, DiscordMarkdown, useDiscordProfile } from "./DiscordMarkdown";
import { SelectMenu } from "./SelectMenu";
import { useBotEmojis } from "../data/botEmojis";
import { useBotConfig } from "../hooks/useBotConfig";
import {
  PANEL_COMMANDS,
  PANEL_EMOJI,
  PANEL_LANGUAGES,
  PANEL_MEMBERS,
  PANEL_OWNER_ID,
  PANEL_STRINGS,
  PANEL_SUPPORT_URL,
  type PanelAction,
  type PanelLanguage,
} from "../data/voiceMasterPanel";

// The panel is two rows of buttons, exactly as `VoiceMasterInterface` builds it.
const BUTTON_ROWS: PanelAction[][] = [
  ["lock", "unlock", "hide", "reveal", "claim"],
  ["disconnect", "view", "increase", "decrease"],
];

// "Soren's Channel" is what the bot names a channel for its owner
// (`"{user}'s Channel"` in cog.py), so the demo channel is named the same way.
const CHANNEL_NAME = "Soren's Channel";

// Discord prints the panel's own timestamp in the short form once the message
// is not from today, and ephemeral replies sit under the next day's divider.
const PANEL_TIME = "10/31/26, 3:04 PM";
const EPHEMERAL_TIME = "7:47 AM";
const EPHEMERAL_DATE = "November 2, 2026";

type Reply =
  | { kind: "notice"; tone: "success" | "error"; emoji: keyof typeof PANEL_EMOJI; text: string }
  | { kind: "info" }
  | { kind: "disconnect" };

/**
 * The bot's VoiceMaster panel, rebuilt as a real interactive message.
 *
 * Every string goes through DiscordMarkdown, so the legend, the subtext replies
 * and the channel card draw the bot's own application emojis, headings, quotes
 * and mentions instead of a hand-drawn imitation. The buttons send the same
 * ephemeral replies the cog sends, and the ephemeral header can dismiss them.
 */
export function VoiceMasterPanel({ className }: { className?: string }) {
  const config = useBotConfig();
  const emojis = useBotEmojis();
  const [language, setLanguage] = useState<PanelLanguage>("en");
  const [reply, setReply] = useState<Reply | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const { openProfile, dialog: profileDialog } = useDiscordProfile();
  const strings = PANEL_STRINGS[language];

  // Discord prints the bot's global display name above its messages, so the
  // panel does too; the name and avatar open the same profile popup a mention
  // opens for any other member.
  const botName = config?.bot_display_name || config?.bot_name || "Niko";
  const botId = config?.application_id || "";
  const botAvatar = config?.bot_avatar_url || null;
  const botVerified = Boolean(config?.bot_verified);
  const openBot = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (!botId) return;
    event.preventDefault();
    void openProfile(botId, event.currentTarget);
  };

  // The ids in src/config/emojis.py go stale whenever an emoji is re-uploaded,
  // so prefer the catalog the bot itself reports and fall back to the ids.
  const emoji = (key: keyof typeof PANEL_EMOJI) => {
    const configured = PANEL_EMOJI[key];
    const live = emojis.find((entry) => entry.name === configured.name);
    return live
      ? { name: live.name, id: live.id, animated: live.animated }
      : { name: configured.name, id: configured.id, animated: false };
  };
  const token = (key: keyof typeof PANEL_EMOJI) => {
    const value = emoji(key);
    return `<${value.animated ? "a" : ""}:${value.name}:${value.id}>`;
  };

  // The cog's legend: emoji, an em dash, the command as a link, its description.
  const supportUrl = config?.support_server_url || PANEL_SUPPORT_URL;
  const legend = (Object.keys(PANEL_COMMANDS) as PanelAction[])
    .map((action) => `${token(action)} — [\`${PANEL_COMMANDS[action]}\`](${supportUrl}) ${strings.legend[action]}`)
    .join("\n");

  const infoDetails = [
    `> - **${strings.info.owner}:** <@${PANEL_OWNER_ID}>`,
    `> - **${strings.info.members}:** ${PANEL_MEMBERS.length}`,
    `> - **${strings.info.limit}:** ${strings.info.noLimit}`,
    `> - **${strings.info.bitrate}:** 64 kbps`,
    `> - **${strings.info.region}:** ${strings.info.automatic}`,
    `> - **${strings.info.status}:** ${strings.info.open}`,
  ].join("\n");

  const act = (action: PanelAction) => {
    if (action === "view") setReply({ kind: "info" });
    else if (action === "disconnect") setReply({ kind: "disconnect" });
    else setReply({ kind: "notice", tone: "success", emoji: action, text: strings.actions[action] });
  };

  const accent = reply?.kind === "info" ? "#ffffff" : reply?.kind === "notice" ? "#00cc66" : undefined;

  return (
    <figure className={`vm-demo${className ? ` ${className}` : ""}`}>
      <div className="vm-demo-bar">
        <span className="vm-demo-label">VoiceMaster · live preview</span>
        <SelectMenu
          label="Panel language"
          value={language}
          options={PANEL_LANGUAGES}
          onChange={(next) => { setLanguage(next); setReply(null); }}
          compact
        />
      </div>

      <div className="discord-window" ref={panelRef}>
        <article className="dc-message">
          <button type="button" className="dc-avatar" data-discord-user-id={botId} onClick={openBot} aria-label={`Open ${botName}'s Discord profile`}>
            {botAvatar ? <img src={botAvatar} alt="" /> : botName.slice(0, 1)}
          </button>
          <div className="dc-message-body">
            <header className="dc-message-head">
              <button type="button" className="dc-author" data-discord-user-id={botId} onClick={openBot}>{botName}</button>
              <DiscordAppBadge verified={botVerified} />
              <time className="dc-timestamp">{PANEL_TIME}</time>
            </header>
            <div className="dc-container">
              <DiscordMarkdown className="dc-panel-title" text={`## ${strings.title}`} />
              <div className="dc-separator" />
              <DiscordMarkdown className="dc-legend" text={legend} />
              <div className="dc-separator" />
              {BUTTON_ROWS.map((row, index) => (
                <div className="dc-button-row" key={index}>
                  {row.map((action) => {
                    const art = emoji(action);
                    return (
                      <button
                        key={action}
                        type="button"
                        className="dc-button"
                        title={`${PANEL_COMMANDS[action]} ${strings.legend[action]}`}
                        aria-label={`${PANEL_COMMANDS[action]} ${strings.legend[action]}`}
                        onClick={() => act(action)}
                      >
                        <DiscordEmoji name={art.name} id={art.id} animated={art.animated} interactive={false} className="dc-button-emoji" />
                      </button>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </article>

        {reply && (
          <>
            <div className="dc-date-divider" role="separator" aria-label={EPHEMERAL_DATE}>
              <span>{EPHEMERAL_DATE}</span>
            </div>
            <article className="dc-message dc-message-ephemeral" aria-live="polite">
              <div className="dc-reply-indicator">
                <span className="dc-reply-avatar">
                  {botAvatar ? <img src={botAvatar} alt="" /> : botName.slice(0, 1)}
                </span>
                <DiscordAppBadge verified={botVerified} small />
                <strong className="dc-reply-author">{botName}</strong>
                <button
                  type="button"
                  className="dc-reply-jump"
                  onClick={() => panelRef.current?.scrollIntoView({ behavior: "smooth", block: "center" })}
                >
                  Click to see message
                </button>
              </div>
              <div className="dc-reply-row">
                <button type="button" className="dc-avatar" data-discord-user-id={botId} onClick={openBot} aria-label={`Open ${botName}'s Discord profile`}>
                  {botAvatar ? <img src={botAvatar} alt="" /> : botName.slice(0, 1)}
                </button>
                <div className="dc-message-body">
                  <header className="dc-message-head">
                    <button type="button" className="dc-author" data-discord-user-id={botId} onClick={openBot}>{botName}</button>
                    <DiscordAppBadge verified={botVerified} />
                    <time className="dc-timestamp">{EPHEMERAL_TIME}</time>
                  </header>
                  {reply.kind === "disconnect" ? (
                    <DisconnectPicker
                      placeholder={strings.disconnect.placeholder}
                      optionLabel={strings.disconnect.option}
                      onPick={(name) => setReply({
                        kind: "notice",
                        tone: "success",
                        emoji: "tick",
                        text: strings.disconnect.done.replace("{users}", name),
                      })}
                    />
                  ) : (
                    <div className="dc-container dc-reply" style={accent ? { borderLeftColor: accent } : undefined}>
                      {reply.kind === "info" ? (
                        <>
                          <DiscordMarkdown text={`## ${CHANNEL_NAME}`} />
                          <div className="dc-separator" />
                          <DiscordMarkdown className="dc-info" text={infoDetails} />
                        </>
                      ) : (
                        <DiscordMarkdown text={`${token(reply.emoji)} ${reply.text}`} />
                      )}
                    </div>
                  )}
                </div>
              </div>
              <footer className="dc-ephemeral-footer">
                <svg className="dc-ephemeral-eye" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                  <path d="M12 5.2c-5.6 0-9.7 4.6-10.7 6.2a1.2 1.2 0 0 0 0 1.2C2.3 14.2 6.4 18.8 12 18.8s9.7-4.6 10.7-6.2a1.2 1.2 0 0 0 0-1.2C21.7 9.8 17.6 5.2 12 5.2Z" fill="none" stroke="currentColor" strokeWidth="1.6" />
                  <circle cx="12" cy="12" r="3.2" fill="none" stroke="currentColor" strokeWidth="1.6" />
                </svg>
                <span>Only you can see this</span>
                <span aria-hidden="true">•</span>
                <button type="button" className="dc-ephemeral-dismiss" onClick={() => setReply(null)}>Dismiss message</button>
              </footer>
            </article>
          </>
        )}
      </div>

      <figcaption className="vm-demo-caption">
        The bot’s real control panel. Press a button for the ephemeral reply it sends, or switch the language above.
      </figcaption>
      {profileDialog}
    </figure>
  );
}

/** The member picker `interaction.response.send_message` attaches to Disconnect. */
function DisconnectPicker({ placeholder, optionLabel, onPick }: {
  placeholder: string;
  optionLabel: string;
  onPick: (name: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [dropUp, setDropUp] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const members = PANEL_MEMBERS.slice(1);
  // The list is taller than the space under the card on a phone, so it opens
  // upward when what is below the trigger would not fit it.
  const toggle = () => {
    if (!open && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      setDropUp(window.innerHeight - rect.bottom < 240 && rect.top > 240);
    }
    setOpen(!open);
  };
  return (
    <div className="dc-select">
      <button
        ref={triggerRef}
        type="button"
        className="dc-select-trigger"
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={toggle}
      >
        <span>{placeholder}</span>
        <svg viewBox="0 0 12 12" aria-hidden="true" focusable="false">
          <path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {open && (
        <div className={`dc-select-list${dropUp ? " is-up" : ""}`} role="listbox" aria-label={placeholder}>
          {members.map((member) => (
            <button key={member} type="button" role="option" aria-selected={false} onClick={() => onPick(member)}>
              <span className="dc-select-avatar">{member.slice(0, 1)}</span>
              <span>{optionLabel.replace("{user}", member)}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
