import { createContext, useCallback, useContext, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { DiscordBadgeList } from "./DiscordBadgeList";
import { DiscordServerTagPill, type DiscordServerTagInfo } from "./DiscordServerTag";
import { DiscordStatusAvatar } from "./DiscordStatusAvatar";
import { BOT_EMOJIS } from "../data/botEmojis";
import { profileBadges } from "../data/profileBadges";
import type { CSSProperties, ReactNode, Ref } from "react";
import { resolveDiscordText } from "../api";

export type DiscordMentionNames = Partial<Record<"user" | "channel" | "role", Record<string, string>>>;
type Format = "bold" | "italic" | "italicAlt" | "underline" | "strike" | "spoiler";
type Node =
  | { kind: "text"; text: string }
  | { kind: "code"; text: string }
  | { kind: "link"; text: string; url: string }
  | { kind: "emoji"; name: string; id: string; animated: boolean }
  | { kind: "timestamp"; raw: string; unix: number; style: string }
  | { kind: "mention"; mention: "user" | "channel" | "role" | "everyone"; id: string }
  | { kind: "format"; format: Format; children: Node[] };
type Token = Node | { kind: "marker"; format: Format };

const markerText: Record<Format, string> = { bold: "**", italic: "*", italicAlt: "_", underline: "__", strike: "~~", spoiler: "||" };
const timestampStyles = new Set(["t", "T", "d", "D", "f", "F", "R"]);
// Every marker is a capture group, because the format each one opens is chosen
// by the group that matched: 8 bold (``**``), 9 underline (``__``), 10 italic
// (``*``), 11 italic-alt (``_``), 12 strike (``~~``), 13 spoiler (``||``).
const tokenPattern = /(`[^`\n]+`)|(<t:-?\d+(?::[tTdDfFR])?>)|(<@!?\d+>|<@&\d+>|<#\d+>|@everyone\b|@here\b)|(<a?:[\w~]+:\d+>)|(\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\))|(\*\*)|(__)|((?<!\*)\*(?!\*))|((?<!_)_(?!_))|(~~)|(\|\|)/g;

function timestampLabel(unix: number, style: string): string | null {
  if (!Number.isSafeInteger(unix) || !timestampStyles.has(style)) return null;
  const date = new Date(unix * 1000);
  if (!Number.isFinite(date.getTime())) return null;
  if (style === "R") {
    const seconds = unix - Math.floor(Date.now() / 1000);
    const distance = Math.abs(seconds);
    const unit = distance < 60 ? "second" : distance < 3600 ? "minute" : distance < 86400 ? "hour" : distance < 604800 ? "day" : distance < 2592000 ? "week" : distance < 31536000 ? "month" : "year";
    const divisor = { second: 1, minute: 60, hour: 3600, day: 86400, week: 604800, month: 2592000, year: 31536000 }[unit];
    return new Intl.RelativeTimeFormat(undefined, { numeric: "always" }).format(Math.round(seconds / divisor), unit);
  }
  const options: Intl.DateTimeFormatOptions = style === "t" || style === "T"
    ? { hour: "numeric", minute: "2-digit", ...(style === "T" ? { second: "2-digit" } : {}) }
    : style === "d" ? { year: "numeric", month: "2-digit", day: "2-digit" }
      : style === "D" ? { year: "numeric", month: "long", day: "numeric" }
        : style === "F" ? { weekday: "long", year: "numeric", month: "long", day: "numeric", hour: "numeric", minute: "2-digit" }
          : { year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" };
  return new Intl.DateTimeFormat(undefined, options).format(date);
}

function tokenize(text: string): Node[] {
  const tokens: Token[] = [];
  let cursor = 0;
  const appendPlain = (value: string) => {
    const urls = /(https?:\/\/[^\s<>)]+)/g;
    let from = 0;
    let match: RegExpExecArray | null;
    while ((match = urls.exec(value))) {
      if (match.index > from) tokens.push({ kind: "text", text: value.slice(from, match.index) });
      tokens.push({ kind: "link", text: match[0], url: match[0] });
      from = urls.lastIndex;
    }
    if (from < value.length) tokens.push({ kind: "text", text: value.slice(from) });
  };

  tokenPattern.lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = tokenPattern.exec(text))) {
    if (match.index > cursor) appendPlain(text.slice(cursor, match.index));
    const raw = match[0];
    if (match[1]) tokens.push({ kind: "code", text: raw.slice(1, -1) });
    else if (match[2]) {
      const parts = raw.match(/^<t:(-?\d+)(?::([tTdDfFR]))?>$/)!;
      tokens.push({ kind: "timestamp", raw, unix: Number(parts[1]), style: parts[2] || "f" });
    } else if (match[3]) {
      const user = raw.match(/^<@!?([0-9]+)>$/);
      const role = raw.match(/^<@&([0-9]+)>$/);
      const channel = raw.match(/^<#([0-9]+)>$/);
      tokens.push(user ? { kind: "mention", mention: "user", id: user[1] }
        : role ? { kind: "mention", mention: "role", id: role[1] }
          : channel ? { kind: "mention", mention: "channel", id: channel[1] }
            : { kind: "mention", mention: "everyone", id: raw });
    } else if (match[4]) {
      const [, animated, name, id] = raw.match(/^<(a?):([\w~]+):(\d+)>$/)!;
      tokens.push({ kind: "emoji", animated: animated === "a", name, id });
    } else if (match[5]) tokens.push({ kind: "link", text: match[6], url: match[7] });
    else if (match[8]) tokens.push({ kind: "marker", format: "bold" });
    else if (match[9]) tokens.push({ kind: "marker", format: "underline" });
    else if (match[10]) tokens.push({ kind: "marker", format: "italic" });
    else if (match[11]) tokens.push({ kind: "marker", format: "italicAlt" });
    else if (match[12]) tokens.push({ kind: "marker", format: "strike" });
    else if (match[13]) tokens.push({ kind: "marker", format: "spoiler" });
    cursor = tokenPattern.lastIndex;
  }
  if (cursor < text.length) appendPlain(text.slice(cursor));

  const roots: Node[] = [];
  const stack: { format: Format; children: Node[] }[] = [];
  const append = (node: Node) => (stack.length ? stack[stack.length - 1].children : roots).push(node);
  for (const token of tokens) {
    if (token.kind !== "marker") { append(token); continue; }
    const open = stack.findIndex((frame) => frame.format === token.format);
    if (open < 0) stack.push({ format: token.format, children: [] });
    else {
      const closed = stack.splice(open);
      const formatted: Node[] = [...closed[0].children];
      for (const frame of closed.slice(1)) formatted.push({ kind: "text", text: markerText[frame.format] }, ...frame.children);
      append({ kind: "format", format: token.format, children: formatted });
    }
  }
  while (stack.length) {
    const frame = stack.pop()!;
    const parent = stack.length ? stack[stack.length - 1].children : roots;
    parent.push({ kind: "text", text: markerText[frame.format] }, ...frame.children);
  }
  return roots;
}

/** The server an emoji token belongs to, provided by the transcript page. */
export type DiscordEmojiSource = {
  guildName?: string | null;
  guildIconUrl?: string | null;
};

const DiscordEmojiContext = createContext<DiscordEmojiSource>({});

/** Supplies the emoji popup's "This emoji is from" server row. */
export function DiscordEmojiProvider({ guildName, guildIconUrl, children }: {
  guildName?: string | null;
  guildIconUrl?: string | null;
  children: ReactNode;
}) {
  return <DiscordEmojiContext.Provider value={{ guildName, guildIconUrl }}>{children}</DiscordEmojiContext.Provider>;
}

// Application emojis live on the bot itself; every other custom emoji is a
// server emoji. The generated list is shared with the rendering lab, so the
// popup never has to guess from the emoji name.
const APPLICATION_EMOJI_IDS = new Set(BOT_EMOJIS.map((emoji) => emoji.id));

// Discord's own Nitro mark, used by the Get Nitro button in the client.
function NitroMark() {
  return <svg className="discord-emoji-popup-nitro-mark" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path fill="currentColor" d="M13.32 21.978a10.322 10.322 0 01-2.07-.36 6.638 6.638 0 01-.675-.219.152.152 0 00-.057-.019.372.372 0 01-.09-.03l-.137-.06a.383.383 0 00-.088-.03.418.418 0 01-.097-.038 7.412 7.412 0 00-.187-.088 8.155 8.155 0 01-.67-.325 4.26 4.26 0 01-.34-.19 1.966 1.966 0 01-.18-.11 1.274 1.274 0 00-.17-.103.763.763 0 01-.103-.07.397.397 0 00-.086-.056c-.007 0-.084-.054-.171-.12a1.052 1.052 0 00-.179-.12c-.011 0-.021-.008-.021-.018 0-.01-.072-.07-.16-.133a.873.873 0 01-.16-.132c0-.01-.01-.017-.02-.017-.012 0-.048-.027-.08-.06a.34.34 0 00-.069-.06.33.33 0 01-.068-.055 10.464 10.464 0 01-1.008-1.008.33.33 0 01-.055-.069.34.34 0 00-.06-.068c-.033-.033-.06-.068-.06-.08 0-.011-.008-.02-.017-.02a.873.873 0 01-.132-.16.825.825 0 00-.133-.16c-.01 0-.018-.01-.018-.022 0-.011-.054-.092-.12-.178a1.496 1.496 0 01-.12-.171.4.4 0 00-.055-.087c-.064-.084-.1-.14-.119-.182a.73.73 0 00-.055-.09 1.612 1.612 0 01-.11-.18 4.258 4.258 0 01-.19-.34 8.154 8.154 0 01-.325-.67 7.397 7.397 0 00-.088-.188.418.418 0 01-.038-.097.42.42 0 00-.033-.093c-.078-.175-.087-.2-.087-.221a.152.152 0 00-.02-.057c-.055-.098-.266-.812-.35-1.185-.06-.266-.161-.848-.181-1.045l-.014-.135-.523-.001c-.59-.001-.7-.018-.9-.139a.968.968 0 01.014-1.668c.189-.113.32-.132.89-.132h.498l.025-.225c.047-.438.196-1.222.29-1.525a.808.808 0 00.03-.125c0-.02-.352-.026-1.695-.026-1.446 0-1.714-.005-1.824-.03a1.116 1.116 0 01-.83-.83 1.111 1.111 0 01.83-1.329C.97 7.003 1.287 7 3.15 7c2.035 0 2.164-.003 2.193-.036a.35.35 0 00.043-.065c.018-.038.052-.095.103-.17.062-.093.089-.137.103-.17a.76.76 0 01.07-.103.397.397 0 00.057-.086c0-.007.054-.084.12-.17.066-.088.12-.168.12-.18 0-.011.008-.02.018-.02.01 0 .07-.073.133-.16a.873.873 0 01.132-.16c.01 0 .017-.01.017-.022 0-.01.027-.047.06-.079a.34.34 0 00.06-.069.33.33 0 01.055-.068c.03-.032.109-.118.175-.192.066-.074.131-.147.146-.162.021-.023-.233-.028-1.69-.033l-1.717-.006L3.208 5a1.48 1.48 0 01-.64-.392 1.44 1.44 0 01-.393-.651c-.038-.125-.046-.194-.046-.41 0-.216.008-.285.046-.41.085-.273.193-.451.393-.65.188-.19.346-.29.585-.372.283-.098.14-.096 6.016-.1 5.47-.002 5.626 0 6.12.063.236.03.698.112.956.17.366.083 1.082.294 1.18.35.019.01.045.019.057.019.012 0 .053.013.09.03l.136.06c.038.016.077.03.088.03.011 0 .055.017.097.038l.187.088a8.155 8.155 0 01.67.324 4.261 4.261 0 01.34.19c.057.03.112.064.18.11.093.062.138.089.17.103a.76.76 0 01.103.07c.04.031.08.057.086.057.008 0 .085.054.171.12.087.066.168.12.18.12.01 0 .02.008.02.018 0 .01.072.07.16.133.088.064.16.123.16.132 0 .01.01.017.021.017.012 0 .047.027.08.06a.34.34 0 00.068.06.33.33 0 01.068.055l.193.175a10.464 10.464 0 01.816.833.33.33 0 01.055.068.34.34 0 00.06.07c.033.031.06.067.06.078 0 .012.007.021.016.021.01 0 .07.072.132.16.064.088.124.16.134.16.01 0 .018.01.018.021 0 .012.054.092.12.18.066.086.12.163.12.17 0 .007.024.046.055.086.063.085.1.14.118.183a.727.727 0 00.055.09c.045.065.078.118.111.18a4.259 4.259 0 01.19.34 8.147 8.147 0 01.325.67c.027.06.067.145.088.187.02.043.038.086.038.097 0 .011.013.051.03.088l.06.136c.016.038.03.079.03.09a6.613 6.613 0 01.238.732 10.11 10.11 0 01-.219 6.176.152.152 0 00-.02.057.405.405 0 01-.031.095c-.078.175-.088.2-.088.22a.418.418 0 01-.038.096l-.088.187a8.153 8.153 0 01-.325.67 4.258 4.258 0 01-.19.34c-.03.057-.063.112-.11.181-.061.093-.088.137-.103.17a.764.764 0 01-.07.102.397.397 0 00-.056.087c0 .007-.054.084-.12.17-.066.087-.12.168-.12.18 0 .011-.008.02-.018.02-.01 0-.07.073-.134.16a.873.873 0 01-.132.16c-.009 0-.016.01-.016.021 0 .012-.027.047-.06.08a.34.34 0 00-.06.068.33.33 0 01-.055.068l-.175.193a10.463 10.463 0 01-.834.816.33.33 0 01-.068.055.34.34 0 00-.069.06c-.032.033-.067.06-.079.06-.011 0-.02.007-.02.017 0 .009-.073.068-.16.132a.825.825 0 00-.16.133c0 .01-.01.018-.022.018-.011 0-.092.054-.179.12-.086.066-.163.12-.17.12a.4.4 0 00-.087.055c-.084.063-.14.1-.183.118a.728.728 0 00-.09.055 1.612 1.612 0 01-.18.111 4.264 4.264 0 01-.34.19c-.099.05-.193.1-.21.111a8.155 8.155 0 01-.46.214c-.06.027-.144.067-.187.088a.419.419 0 01-.097.038.383.383 0 00-.088.03l-.136.06a.372.372 0 01-.09.03.153.153 0 00-.057.02c-.098.054-.814.266-1.18.348-.946.213-1.994.295-2.925.23zm1.74-3.135a7.374 7.374 0 001.66-.444c.346-.134 1.079-.535 1.35-.738.055-.042.172-.128.26-.191.088-.064.178-.136.2-.16.022-.025.13-.123.24-.218.243-.21.212-.18.423-.423.096-.11.196-.22.222-.247.027-.026.098-.116.16-.2.061-.084.145-.198.187-.253.176-.233.632-1.064.725-1.32l.092-.247c.446-1.186.543-2.575.271-3.853-.08-.377-.143-.581-.363-1.18-.095-.262-.55-1.089-.725-1.32a24.578 24.578 0 01-.191-.26 2.3 2.3 0 00-.16-.2 3.244 3.244 0 01-.16-.18 3.94 3.94 0 00-.536-.536 1.424 1.424 0 01-.175-.158c0-.008-.096-.084-.215-.17a5.702 5.702 0 01-.225-.167 4.486 4.486 0 00-.448-.288 6.844 6.844 0 00-2.937-.953 9.532 9.532 0 00-1.576.038c-.756.113-1.43.321-2.09.644-.249.122-.743.404-.77.439a1.6 1.6 0 01-.14.1c-.422.282-.954.771-1.328 1.223-.377.455-.64.854-.89 1.354a6.996 6.996 0 00-.558 4.564c.113.482.273.958.466 1.387.118.26.435.832.528.952.03.04.095.13.142.201a6.86 6.86 0 004.458 2.772c.453.076.609.086 1.243.08.467-.006.646-.016.86-.048zm-1.51-1.725a5.329 5.329 0 01-1.308-.308 5.763 5.763 0 01-.683-.326 7.122 7.122 0 01-.707-.482 6.14 6.14 0 01-.675-.676 7.121 7.121 0 01-.482-.707 5.026 5.026 0 01-.506-3.7 4.89 4.89 0 01.775-1.679c.17-.241.196-.274.385-.48.157-.171.3-.309.503-.484.115-.1.518-.373.707-.482a5.026 5.026 0 013.7-.505 4.89 4.89 0 011.68.774c.241.17.274.196.48.385.17.157.308.3.484.504.099.115.373.517.482.707a5.028 5.028 0 01.407 4.04 4.835 4.835 0 01-.677 1.338c-.17.242-.196.275-.385.481-.147.161-.15.164-.311.311-.206.19-.239.216-.48.386a4.89 4.89 0 01-1.68.774 5.276 5.276 0 01-1.71.129zm2.888-3.437c.477-.797.867-1.469.867-1.493 0-.036-1.485-2.586-1.697-2.914l-.049-.075H12.62l-.047.075c-.219.35-1.659 2.88-1.659 2.915 0 .036 1.46 2.567 1.658 2.875l.048.076 1.475-.006 1.475-.005z" />
  </svg>;
}

/** Discord's custom-emoji popup: application emoji or server emoji. */
function DiscordEmojiPopup({ name, id, animated, isApplication, guildName, guildIconUrl, popupRef, style }: {
  name: string;
  id: string;
  animated: boolean;
  isApplication: boolean;
  guildName?: string | null;
  guildIconUrl?: string | null;
  popupRef?: Ref<HTMLDivElement>;
  style?: CSSProperties;
}) {
  const initial = Array.from((guildName || "This server").trim())[0]?.toUpperCase() || "?";
  const art = `https://cdn.discordapp.com/emojis/${id}.${animated ? "gif" : "png"}`;
  return <div ref={popupRef} className="discord-emoji-popup" role="dialog" aria-label={`:${name}: emoji`} style={style}>
    <div className="discord-emoji-popup-main">
      <img className="discord-emoji-popup-art" src={art} alt="" />
      <div className="discord-emoji-popup-copy">
        <strong className="discord-emoji-popup-name">:{name}:</strong>
        <p>{isApplication ? "This emoji is from the Niko app" : "This emoji is from this server. Get Nitro to use it everywhere."}</p>
      </div>
    </div>
    {!isApplication && <>
      <a className="discord-emoji-popup-nitro" href="https://discord.com/nitro" target="_blank" rel="noopener noreferrer">
        <NitroMark />
        <span>Get Nitro</span>
      </a>
      <div className="discord-emoji-popup-source">
        <p>This emoji is from</p>
        <div className="discord-emoji-popup-guild">
          {guildIconUrl
            ? <img className="discord-emoji-popup-guild-icon" src={guildIconUrl} alt="" />
            : <span className="discord-emoji-popup-guild-icon discord-emoji-popup-guild-fallback" aria-hidden="true">{initial}</span>}
          <div className="discord-emoji-popup-guild-copy">
            <strong>{guildName || "This server"}</strong>
            <small>Invite-only server</small>
          </div>
        </div>
      </div>
    </>}
  </div>;
}

/**
 * A Discord custom emoji.
 *
 * Discord never draws a broken emoji: when it cannot resolve one — a deleted
 * emoji, an emoji from another server, a stale id — it writes the name out
 * between colons as plain text. The fallback here is the same, which also keeps
 * a failed image from shifting the line or eating the formatting around it.
 *
 * A resolved emoji is clickable and opens Discord's own emoji popup. Application
 * emojis name the Niko app; server emojis name the transcript's server and show
 * the Nitro prompt, matching Discord's two popup layouts.
 */
export function DiscordEmoji({ name, id, animated = false, className, interactive = true, source }: {
  name: string;
  id: string;
  animated?: boolean;
  className?: string;
  interactive?: boolean;
  /** Lets the rendering lab preview a server popup with a known emoji id. */
  source?: "app" | "server";
}) {
  const [broken, setBroken] = useState(false);
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState({ left: 12, top: 12 });
  const triggerRef = useRef<HTMLImageElement>(null);
  const popupRef = useRef<HTMLDivElement>(null);
  const emojiContext = useContext(DiscordEmojiContext);
  const isApplication = source ? source === "app" : APPLICATION_EMOJI_IDS.has(id);

  const positionPopup = useCallback(() => {
    const trigger = triggerRef.current;
    const popup = popupRef.current;
    if (!trigger || !popup) return;
    const rect = trigger.getBoundingClientRect();
    const margin = 12;
    const gap = 8;
    const width = popup.offsetWidth;
    const height = popup.offsetHeight;
    const left = Math.max(margin, Math.min(rect.left + rect.width / 2 - width / 2, window.innerWidth - width - margin));
    const below = rect.bottom + gap;
    const top = below + height <= window.innerHeight - margin
      ? below
      : Math.max(margin, rect.top - height - gap);
    setPosition({ left, top: Math.min(top, window.innerHeight - height - margin) });
  }, []);

  useLayoutEffect(() => {
    if (open) positionPopup();
  }, [open, positionPopup]);

  useEffect(() => {
    if (!open) return;
    window.addEventListener("resize", positionPopup);
    window.addEventListener("scroll", positionPopup, true);
    return () => {
      window.removeEventListener("resize", positionPopup);
      window.removeEventListener("scroll", positionPopup, true);
    };
  }, [open, positionPopup]);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      const target = event.target;
      if (target instanceof Node && (triggerRef.current?.contains(target) || popupRef.current?.contains(target))) return;
      setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  if (!id || broken) {
    return <span className="discord-emoji-fallback" data-discord-emoji-name={name}>{`:${name}:`}</span>;
  }
  return <>
    <img
      ref={triggerRef}
      className={`${className || ""}${interactive ? " discord-emoji-trigger" : ""}`.trim() || undefined}
      data-discord-emoji-name={name}
      data-emoji-id={id}
      data-emoji-app={isApplication ? "1" : "0"}
      src={`https://cdn.discordapp.com/emojis/${id}.${animated ? "gif" : "png"}`}
      alt={`:${name}:`}
      title={`:${name}:`}
      role={interactive ? "button" : undefined}
      tabIndex={interactive ? 0 : undefined}
      aria-haspopup={interactive ? "dialog" : undefined}
      aria-expanded={interactive ? open : undefined}
      aria-label={interactive ? `:${name}: emoji` : undefined}
      onClick={interactive ? (event) => { event.preventDefault(); event.stopPropagation(); setOpen((value) => !value); } : undefined}
      onKeyDown={interactive ? (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        event.stopPropagation();
        setOpen((value) => !value);
      } : undefined}
      onError={() => setBroken(true)}
    />
    {interactive && open && createPortal(
      <DiscordEmojiPopup
        name={name}
        id={id}
        animated={animated}
        isApplication={isApplication}
        guildName={emojiContext.guildName}
        guildIconUrl={emojiContext.guildIconUrl}
        popupRef={popupRef}
        style={{ "--emoji-popup-left": `${position.left}px`, "--emoji-popup-top": `${position.top}px` } as CSSProperties}
      />,
      document.body,
    )}
  </>;
}

/**
 * Discord's spoiler: the content stays hidden until it is clicked, and while it
 * is hidden every link inside it is inert. That way a spoiler can never be used
 * to trick someone into opening a link they have not chosen to reveal.
 */
function DiscordSpoiler({ children }: { children: ReactNode }) {
  const [revealed, setRevealed] = useState(false);
  const reveal = () => setRevealed(true);
  return <span
    className={`discord-md-spoiler${revealed ? " is-revealed" : ""}`}
    role="button"
    tabIndex={0}
    aria-expanded={revealed}
    aria-label={revealed ? undefined : "Spoiler, click to reveal"}
    onClick={(event) => {
      if (revealed) return;
      event.preventDefault();
      event.stopPropagation();
      reveal();
    }}
    onKeyDown={(event) => {
      if (revealed || (event.key !== "Enter" && event.key !== " ")) return;
      event.preventDefault();
      event.stopPropagation();
      reveal();
    }}
  >{children}</span>;
}

function renderInline(nodes: Node[], names?: DiscordMentionNames, prefix = "discord-md", interactiveUsers = true): ReactNode[] {
  return nodes.map((node, index) => {
    const key = `${prefix}-${index}`;
    if (node.kind === "text") return <span key={key}>{node.text}</span>;
    if (node.kind === "code") return <code key={key} className="discord-md-code">{node.text}</code>;
    if (node.kind === "link") return <a key={key} className="discord-md-link" href={node.url} target="_blank" rel="noopener noreferrer">{node.text}</a>;
    if (node.kind === "emoji") return <DiscordEmoji key={key} name={node.name} id={node.id} animated={node.animated} className="discord-md-emoji" />;
    if (node.kind === "timestamp") {
      const label = timestampLabel(node.unix, node.style);
      const date = new Date(node.unix * 1000);
      return label ? <time key={key} className="discord-md-timestamp" dateTime={date.toISOString()} title={node.raw}>{label}</time> : <span key={key}>{node.raw}</span>;
    }
    if (node.kind === "mention") {
      const label = node.mention === "everyone" ? node.id : names?.[node.mention]?.[node.id] || `${node.mention === "channel" ? "#" : "@"}${node.id}`;
      // Discord writes a sigil in front of every named mention, whether the
      // name came from the resolver or the id fallback.
      const mentionLabel = node.mention === "user" || node.mention === "role"
        ? (label.startsWith("@") ? label : `@${label}`)
        : node.mention === "channel"
          ? (label.startsWith("#") ? label : `#${label}`)
          : label;
      if (node.mention === "user" && interactiveUsers) {
        return <button key={key} type="button" className={`discord-md-mention discord-md-mention-${node.mention}`} data-discord-user-id={node.id} title={`user · ${node.id}`}>{mentionLabel}</button>;
      }
      return <span key={key} className={`discord-md-mention discord-md-mention-${node.mention}`} title={node.mention === "everyone" ? undefined : `${node.mention} · ${node.id}`}>{mentionLabel}</span>;
    }
    if (node.format === "spoiler") {
      return <DiscordSpoiler key={key}>{renderInline(node.children, names, key, interactiveUsers)}</DiscordSpoiler>;
    }
    const style: CSSProperties = node.format === "bold" ? { fontWeight: 700 }
      : node.format === "italic" || node.format === "italicAlt" ? { fontStyle: "italic" }
        : node.format === "underline" ? { textDecoration: "underline" }
          : { textDecoration: "line-through" };
    return <span key={key} style={style}>{renderInline(node.children, names, key, interactiveUsers)}</span>;
  });
}

type DiscordCustomStatus = {
  text: string | null;
  emoji_name: string | null;
  emoji_id: string | null;
  emoji_animated: boolean;
};

type DiscordProfileActivity = {
  type: string;
  title: string | null;
  artists: string[];
  album: string | null;
  album_cover_url: string;
  url: string | null;
  start: number | null;
  end: number | null;
  duration_seconds: number | null;
};

type TranscriptProfile = {
  id: string; username: string; display_name: string; avatar_url: string | null;
  banner_url: string | null;  banner_color: string | null; bio: string | null;
  guild_nick: string | null; guild_tag: string | null; guild_badge_url: string | null;
  server_tag?: DiscordServerTagInfo | null;
  status?: string | null;

  avatar_decoration_url: string | null;
  badges?: string[] | null;
  custom_status?: DiscordCustomStatus | null;
  activities?: DiscordProfileActivity[] | null;
};

// Presence lives on the gateway's live member cache and can change while a popup
// is open, so an open popup re-reads its profile on the same 5s cadence the Team
// page uses instead of freezing at the moment it was first opened.
const PROFILE_REFRESH_INTERVAL = 5000;

const PROFILE_STATUS_LABELS: Record<string, string> = {
  online: "Online",
  idle: "Idle",
  dnd: "Do Not Disturb",
  offline: "Offline",
  streaming: "Streaming",
};

/** Discord may report a status enum or a plain string; unknown values are offline. */
function profileStatusKey(status?: string | null) {
  const value = typeof status === "string" ? status.trim().toLowerCase().replace(/^status\./, "") : "";
  return Object.prototype.hasOwnProperty.call(PROFILE_STATUS_LABELS, value) ? value : "offline";
}

function profileStatusLabel(status?: string | null) {
  return PROFILE_STATUS_LABELS[profileStatusKey(status)];
}

async function fetchDiscordProfile(userId: string): Promise<TranscriptProfile> {
  const response = await fetch(`/api/discord/users/${encodeURIComponent(userId)}`);
  if (!response.ok) throw new Error("Could not load this Discord profile.");
  return await response.json() as TranscriptProfile;
}

function statusEmoji(status: DiscordCustomStatus) {
  if (status.emoji_id) {
    return <DiscordEmoji name={status.emoji_name || "emoji"} id={status.emoji_id} animated={status.emoji_animated} className="discord-profile-status-emoji" interactive={false} />;
  }
  return status.emoji_name ? <span className="discord-profile-status-emoji">{status.emoji_name}</span> : null;
}

/**
 * Discord's custom-status bubble. An emoji-only status is a compact square that
 * holds just the emoji; text clamps to two lines and expands on click, the way
 * Discord truncates a long status and opens it in full.
 */
function ProfileCustomStatus({ status }: { status: DiscordCustomStatus }) {
  const emoji = statusEmoji(status);
  const text = status.text?.trim() || "";
  const [expanded, setExpanded] = useState(false);
  const [clamped, setClamped] = useState(false);
  const textRef = useRef<HTMLSpanElement>(null);
  useLayoutEffect(() => {
    const node = textRef.current;
    if (expanded || !text || !node) {
      setClamped(false);
      return;
    }
    setClamped(node.scrollHeight > node.clientHeight + 1);
  }, [expanded, text, status.emoji_id, status.emoji_name]);
  const toggle = useCallback(() => setExpanded((current) => !current), []);
  if (!text) return <div className="discord-profile-status is-emoji-only">{emoji}</div>;
  const expandable = clamped || expanded;
  return <div
    className={`discord-profile-status${expanded ? " is-expanded" : ""}${clamped ? " is-clamped" : ""}`}
    role={expandable ? "button" : undefined}
    tabIndex={expandable ? 0 : undefined}
    aria-expanded={expandable ? expanded : undefined}
    aria-label={expandable ? (expanded ? "Collapse custom status" : "Show full custom status") : undefined}
    title={expandable ? (expanded ? "Show less" : "Show full status") : undefined}
    onClick={expandable ? toggle : undefined}
    onKeyDown={expandable ? (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      toggle();
    } : undefined}
  >
    <span ref={textRef} className="discord-profile-status-text">{emoji}{text}</span>
  </div>;
}

function trackClock(seconds: number) {
  const total = Math.max(0, Math.round(seconds));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

/** The Spotify card Discord shows at the bottom of a profile popout. */
function ProfileSpotifyCard({ activity }: { activity: DiscordProfileActivity }) {
  const start = activity.start;
  const end = activity.end;
  const hasWindow = typeof start === "number" && typeof end === "number" && end > start;
  const [now, setNow] = useState(() => Math.floor(Date.now() / 1000));
  useEffect(() => {
    if (!hasWindow) return;
    setNow(Math.floor(Date.now() / 1000));
    const timer = window.setInterval(() => setNow(Math.floor(Date.now() / 1000)), 1000);
    return () => window.clearInterval(timer);
  }, [hasWindow, start, end]);
  const total = activity.duration_seconds || (hasWindow ? (end as number) - (start as number) : 0);
  const elapsed = hasWindow ? Math.min(Math.max(now - (start as number), 0), total) : 0;
  const card = <div className="discord-profile-spotify">
    <div className="discord-profile-spotify-head"><img src="/spotify.svg" alt="" /><span>Listening to Spotify</span></div>
    <div className="discord-profile-spotify-body">
      <img className="discord-profile-spotify-art" src={activity.album_cover_url} alt="" />
      <div className="discord-profile-spotify-copy">
        <strong title={activity.title || "Spotify"}>{activity.title || "Spotify"}</strong>
        {activity.artists.length > 0 && <small title={activity.artists.join(", ")}>{activity.artists.join(", ")}</small>}
        {hasWindow && total > 0 && <div className="discord-profile-spotify-progress">
          <span>{trackClock(elapsed)}</span>
          <span className="discord-profile-spotify-track" aria-hidden="true"><i style={{ width: `${(elapsed / total) * 100}%` }} /></span>
          <span>{trackClock(total)}</span>
        </div>}
      </div>
    </div>
  </div>;
  return activity.url
    ? <a className="discord-profile-spotify-link" href={activity.url} target="_blank" rel="noreferrer">{card}</a>
    : card;
}

/** The circular "..." menu in the popup's top corner, with Copy User ID. */
function ProfileMenu({ userId }: { userId: string }) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      if (event.target instanceof Node && menuRef.current?.contains(event.target)) return;
      setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [open]);
  useEffect(() => {
    if (!copied) return;
    const timer = window.setTimeout(() => setCopied(false), 1800);
    return () => window.clearTimeout(timer);
  }, [copied]);
  const copyUserId = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(userId);
      setCopied(true);
    } catch {
      // A browser without clipboard access: leave the label alone rather than
      // claiming a copy that did not happen.
      setCopied(false);
    }
  }, [userId]);
  return <div className="discord-profile-menu" ref={menuRef}>
    <button
      type="button"
      className="discord-profile-menu-button"
      aria-label="More options"
      aria-haspopup="menu"
      aria-expanded={open}
      onClick={() => setOpen((value) => !value)}
    >
      <span className="discord-profile-menu-dots" aria-hidden="true"><i /><i /><i /></span>
    </button>
    {open && <div className="discord-profile-menu-list" role="menu">
      <button type="button" className="discord-profile-menu-item" role="menuitem" onClick={() => void copyUserId()}>
        {copied ? "Copied!" : "Copy User ID"}
      </button>
    </div>}
  </div>;
}

// A profile popup is global: opening another user's card closes the last one,
// even when the two triggers live in different markdown blocks.
const PROFILE_OPEN_EVENT = "niko:discord-profile-open";
let profileOwnerSequence = 0;

/** Shared profile-popup state for mention links and transcript author rows. */
export function useDiscordProfile(enabled = true) {
  const ownerRef = useRef(0);
  if (ownerRef.current === 0) ownerRef.current = ++profileOwnerSequence;
  const [profile, setProfile] = useState<TranscriptProfile | null>(null);
  const [profilePosition, setProfilePosition] = useState({ left: 12, top: 12 });
  const profileCardRef = useRef<HTMLDivElement>(null);
  const profileTriggerRef = useRef<HTMLElement | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState("");
  const requestRef = useRef(0);
  const profileBadgeList = profileBadges(profile?.badges);
  const customStatus = profile?.custom_status || null;
  const spotifyActivity = (profile?.activities || []).find((activity) => Boolean(activity.album_cover_url)) || null;
  const closeProfile = useCallback(() => {
    requestRef.current += 1;
    profileTriggerRef.current = null;
    setProfile(null);
    setProfileLoading(false);
    setProfileError("");
  }, []);
  const positionProfile = useCallback(() => {
    const trigger = profileTriggerRef.current;
    const card = profileCardRef.current;
    if (!trigger || !card) return;
    const rect = trigger.getBoundingClientRect();
    const margin = 12;
    const gap = 8;
    const width = card.offsetWidth;
    const height = card.offsetHeight;
    const left = Math.max(margin, Math.min(rect.left, window.innerWidth - width - margin));
    const below = rect.bottom + gap;
    const top = below + height <= window.innerHeight - margin
      ? below
      : Math.max(margin, rect.top - height - gap);
    setProfilePosition({ left, top: Math.min(top, window.innerHeight - height - margin) });
  }, []);
  useLayoutEffect(() => {
    if (!profileLoading && !profileError && !profile) return;
    positionProfile();
  }, [positionProfile, profile, profileError, profileLoading]);
  useEffect(() => {
    if (!profileLoading && !profileError && !profile) return;
    window.addEventListener("resize", positionProfile);
    window.addEventListener("scroll", positionProfile, true);
    return () => {
      window.removeEventListener("resize", positionProfile);
      window.removeEventListener("scroll", positionProfile, true);
    };
  }, [positionProfile, profile, profileError, profileLoading]);
  const openProfile = useCallback(async (userId: string, trigger: HTMLElement) => {
    if (!enabled || !/^\d{1,22}$/.test(userId)) return;
    // The previous card belongs to another trigger, so it yields to this one.
    document.dispatchEvent(new CustomEvent(PROFILE_OPEN_EVENT, { detail: ownerRef.current }));
    const requestId = ++requestRef.current;
    profileTriggerRef.current = trigger;
    setProfilePosition({ left: 12, top: 12 });
    setProfile(null);
    setProfileError("");
    setProfileLoading(true);
    try {
      const result = await fetchDiscordProfile(userId);
      if (requestRef.current === requestId) setProfile(result);
    } catch (error) {
      if (requestRef.current === requestId) setProfileError(error instanceof Error ? error.message : "Could not load this Discord profile.");
    } finally {
      if (requestRef.current === requestId) setProfileLoading(false);
    }
  }, [enabled]);
  const openProfileId = profile?.id || "";
  useEffect(() => {
    if (!openProfileId) return;
    let active = true;
    const refresh = () => {
      // A transient poll failure keeps the last known presence: the popup never
      // blanks out or flashes a loading state while it refreshes.
      fetchDiscordProfile(openProfileId)
        .then((next) => {
          if (active) setProfile((current) => (current && current.id === next.id ? next : current));
        })
        .catch(() => {});
    };
    const handleVisibility = () => {
      if (document.visibilityState === "visible") refresh();
    };

    const interval = window.setInterval(() => {
      if (document.visibilityState === "visible") refresh();
    }, PROFILE_REFRESH_INTERVAL);
    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      active = false;
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [openProfileId]);
  useEffect(() => {
    if (!enabled || (!profile && !profileLoading && !profileError)) return;
    const closeOther = (event: Event) => {
      if ((event as CustomEvent<number>).detail !== ownerRef.current) closeProfile();
    };
    document.addEventListener(PROFILE_OPEN_EVENT, closeOther);
    return () => document.removeEventListener(PROFILE_OPEN_EVENT, closeOther);
  }, [closeProfile, enabled, profile, profileError, profileLoading]);
  useEffect(() => {
    if (!enabled || (!profile && !profileLoading && !profileError)) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      // A floating server-tag popup is the topmost layer, so Escape closes it
      // and leaves the profile underneath open for the next Escape.
      if (document.querySelector(".discord-server-tag-popup")) return;
      closeProfile();
    };
    const onClick = (event: MouseEvent) => {
      const target = event.target;
      // The badge popup floats outside the card, so a click inside it keeps the
      // profile open.
      if (target instanceof Element && !target.closest(".discord-profile-card") && !target.closest(".discord-badge-popup") && !target.closest(".discord-server-tag-popup") && !target.closest("[data-discord-user-id]")) closeProfile();
    };
    window.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onClick);
    return () => { window.removeEventListener("keydown", onKey); document.removeEventListener("mousedown", onClick); };
  }, [closeProfile, enabled, profile, profileError, profileLoading]);

  const dialog = enabled && (profileLoading || profileError || profile)
    ? createPortal(<div className="discord-profile-popover" role="presentation">
      <div ref={profileCardRef} className="discord-profile-card" role={profileError ? "alert" : profileLoading ? "status" : "dialog"} aria-label={profile ? `${profile.display_name} Discord profile` : undefined} style={{ "--profile-left": `${profilePosition.left}px`, "--profile-top": `${profilePosition.top}px` } as CSSProperties}>
        {profileLoading ? <div className="discord-profile-state">Loading Discord profile…</div> : profileError ? <div className="discord-profile-state">{profileError}</div> : profile && <>
          {profile.banner_url
            ? <img className="discord-profile-banner" src={profile.banner_url} alt="" />
            : <div className="discord-profile-banner" style={{ backgroundColor: profile.banner_color || "#202225" }} />}
          {/* Keyed by user so an open menu never carries over to the next popup. */}
          <ProfileMenu key={profile.id} userId={profile.id} />
          <div className="discord-profile-body">
            <div className="discord-profile-head">
              {profile.avatar_url && <DiscordStatusAvatar status={profileStatusKey(profile.status)} className="discord-profile-avatar-wrap" label={profileStatusLabel(profile.status)}>
                <img className="discord-profile-avatar" src={profile.avatar_url} alt="" />
                {profile.avatar_decoration_url && <img className="discord-profile-avatar-decoration" src={profile.avatar_decoration_url} alt="" />}
              </DiscordStatusAvatar>}
              {customStatus && (customStatus.text || customStatus.emoji_id || customStatus.emoji_name) && <ProfileCustomStatus status={customStatus} />}
            </div>
            <h2 className="discord-profile-name">{profile.display_name}</h2>
            {/* Discord puts the server tag pill on the username row and the
                profile badges on the line directly below it. */}
            <p className="discord-profile-username">
              <span className="discord-profile-user-tag">{profile.username}</span>
              {profile.guild_tag && <DiscordServerTagPill
                server={profile.server_tag || null}
                tag={profile.guild_tag}
                badgeUrl={profile.guild_badge_url}
              />}
            </p>
            {/* Badge artwork ships with the app; clicking one opens the badge
                popup owned by DiscordBadgeList. */}
            <DiscordBadgeList badges={profileBadgeList} />
            {profile.bio && <section className="discord-profile-about"><h3>About Me</h3><p>{profile.bio}</p></section>}
            {spotifyActivity && <ProfileSpotifyCard activity={spotifyActivity} />}
            <a className="discord-profile-full-link" href={`https://discord.com/users/${profile.id}`} target="_blank" rel="noopener noreferrer">Open Discord profile</a>
          </div>
        </>}
      </div>
    </div>, document.body)
    : null;

  return { openProfile, closeProfile, dialog };
}

export function DiscordMarkdown({ text, mentionNames, guildId, className, style, interactiveUsers = true, inline = false }: {
  text: string;
  mentionNames?: DiscordMentionNames;
  guildId?: string;
  className?: string;
  style?: CSSProperties;
  interactiveUsers?: boolean;
  inline?: boolean;
}) {
  const [resolvedNames, setResolvedNames] = useState<{ key: string; names: DiscordMentionNames }>({ key: "", names: {} });
  const resolutionKey = `${guildId || ""}:${text}`;
  const mentionNamesKey = JSON.stringify(mentionNames || {});
  useEffect(() => {
    const mentions = { user: new Set<string>(), channel: new Set<string>(), role: new Set<string>() };
    const mentionPattern = /<@!?(\d+)>|<@&(\d+)>|<#(\d+)>/g;
    let match: RegExpExecArray | null;
    while ((match = mentionPattern.exec(text))) {
      if (match[1]) mentions.user.add(match[1]);
      else if (match[2]) mentions.role.add(match[2]);
      else if (match[3]) mentions.channel.add(match[3]);
    }
    const hasMissingNames = (["user", "channel", "role"] as const).some((kind) =>
      Array.from(mentions[kind]).some((id) => !mentionNames?.[kind]?.[id]),
    );
    if (!hasMissingNames) return;
    let active = true;
    void resolveDiscordText(text, guildId).then((result) => {
      if (active) setResolvedNames({ key: resolutionKey, names: result.mention_names });
    }).catch(() => {
      // Keep the ID fallback when Discord name lookup is unavailable.
    });
    return () => { active = false; };
  }, [guildId, mentionNamesKey, resolutionKey, text]);
  const resolvedMentionNames: DiscordMentionNames = {
    ...(resolvedNames.key === resolutionKey ? resolvedNames.names : {}),
    ...mentionNames,
    user: { ...(resolvedNames.key === resolutionKey ? resolvedNames.names.user : {}), ...mentionNames?.user },
    channel: { ...(resolvedNames.key === resolutionKey ? resolvedNames.names.channel : {}), ...mentionNames?.channel },
    role: { ...(resolvedNames.key === resolutionKey ? resolvedNames.names.role : {}), ...mentionNames?.role },
  };
  const { openProfile, dialog } = useDiscordProfile(interactiveUsers);

  const lines = text.split("\n");
  const children: ReactNode[] = [];
  const renderInlineText = (line: string, key: string | number) => {
    let content = line;
    const task = content.match(/^\s*[-*]\s+\[([ xX])\]\s+(.*)$/);
    const ordered = content.match(/^\s*(\d+)\.\s+(.*)$/);
    if (task) content = `• ${task[2]}`;
    else if (/^\s*[-*]\s+/.test(content)) content = `• ${content.replace(/^\s*[-*]\s+/, "")}`;
    else if (ordered) content = `${ordered[1]}. ${ordered[2]}`;
    return <span key={key} className={task ? "discord-md-task" : undefined}>{renderInline(tokenize(content), resolvedMentionNames, `line-${key}`, interactiveUsers)}</span>;
  };
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const trimmed = line.trimStart();
    if (trimmed.startsWith("```")) {
      const code: string[] = [];
      index += 1;
      while (index < lines.length && !lines[index].trimStart().startsWith("```")) code.push(lines[index++]);
      children.push(<pre className="discord-md-block-code" key={`code-${index}`}><code>{code.join("\n")}</code></pre>);
      continue;
    }
    // A double pipe is a spoiler, not the first cell of a table row.
    const isTableRow = (value: string) => value.trimStart().startsWith("|") && !value.trimStart().startsWith("||");
    if (isTableRow(line)) {
      const rows: string[][] = [];
      while (index < lines.length && isTableRow(lines[index])) {
        rows.push(lines[index++].trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim()));
      }
      index -= 1;
      const isSeparator = (cells: string[]) => cells.length > 0 && cells.every((cell) => /^:?-{2,}:?$/.test(cell.replace(/\s+/g, "")));
      const header = rows[0];
      const body = rows.length > 1 && isSeparator(rows[1]) ? rows.slice(2) : rows.slice(1);
      children.push(<div className="discord-md-table-wrap" key={`table-${index}`}><table className="discord-md-table"><thead><tr>{header.map((cell, cellIndex) => <th key={cellIndex}>{renderInline(tokenize(cell), resolvedMentionNames, `table-head-${index}-${cellIndex}`, interactiveUsers)}</th>)}</tr></thead><tbody>{body.map((row, rowIndex) => <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={cellIndex}>{renderInline(tokenize(cell), resolvedMentionNames, `table-${index}-${rowIndex}-${cellIndex}`, interactiveUsers)}</td>)}</tr>)}</tbody></table></div>);
      continue;
    }
    const heading = trimmed.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      const Heading = `h${heading[1].length}` as "h1" | "h2" | "h3" | "h4";
      children.push(<Heading className="discord-md-heading" key={index}>{renderInline(tokenize(heading[2]), resolvedMentionNames, `line-${index}`, interactiveUsers)}</Heading>);
      continue;
    }
    const quote = trimmed.match(/^>\s?(.*)$/);
    if (quote) {
      // Consecutive quote lines are one quote in Discord: a single rounded bar
      // runs down the left of the whole run instead of restarting per line.
      const quoteLines: string[] = [];
      const quoteStart = index;
      while (index < lines.length) {
        const next = lines[index].trimStart().match(/^>\s?(.*)$/);
        if (!next) break;
        quoteLines.push(next[1]);
        index += 1;
      }
      index -= 1;
      children.push(<blockquote className="discord-md-quote" key={`quote-${quoteStart}`}>
        {quoteLines.map((quoteLine, quoteIndex) => <span key={quoteIndex}>
          {renderInlineText(quoteLine, `quote-${quoteStart}-${quoteIndex}`)}
          {quoteIndex < quoteLines.length - 1 ? <br /> : null}
        </span>)}
      </blockquote>);
      continue;
    }
    const subtext = trimmed.startsWith("-# ");
    const content = subtext ? trimmed.slice(3) : line;
    const inline = renderInlineText(content, index);
    children.push(subtext
      ? <small className="discord-md-subtext" key={index}>{inline}{index < lines.length - 1 ? <br /> : null}</small>
      : <span key={index}>{inline}{index < lines.length - 1 ? <br /> : null}</span>);
  }
  const Wrapper = inline ? "span" : "div";
  return <Wrapper className={`discord-markdown${inline ? " discord-markdown-inline" : ""}${className ? ` ${className}` : ""}`} style={style} onClick={interactiveUsers ? (event) => {
    const target = event.target;
    if (target instanceof Element) {
      const mention = target.closest<HTMLElement>("[data-discord-user-id]");
      if (mention) {
        event.preventDefault();
        void openProfile(mention.dataset.discordUserId || "", mention);
      }
    }
  } : undefined}>
    {children}
    {dialog}
  </Wrapper>;
}
