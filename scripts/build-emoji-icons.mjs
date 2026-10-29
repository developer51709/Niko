/**
 * Draws Niko's emojis from icon-font artwork: Lucide outlines for the generic
 * icons, Simple Icons marks for the platform logos, Web3 Icons marks for the
 * cryptocurrencies.
 *
 *   1. Reads the icon outline from the installed `lucide-react` package — or,
 *      for a glyph Lucide has no icon for, from CUSTOM_GLYPHS below, which is
 *      drawn in the same 24-unit box and stroke as a Lucide outline — the brand
 *      marks from the installed `simple-icons` package (simpleicons.org), and
 *      the coin marks from `@web3icons/core` (web3icons.io)
 *   2. Rasterises it with sharp into the PNG emoji art in src/assets/emojis/,
 *      drawn as a coloured outline on a transparent tile. Colour is reserved
 *      for meaning — green for a pass, red for a removal, orange for a caution,
 *      gold for the premium crown — and everything else is one muted grey that
 *      reads on both Discord themes, so a help menu or a panel full of them
 *      reads as a single set instead of a pile of unrelated colours.
 *
 * The colour lives in the icon itself, so there is no badge, disc or plate
 * behind it — a Discord emoji is drawn straight onto the message background and
 * a background of its own would show as a coloured dot in every message.
 *
 * Run from the repository root:  node scripts/build-emoji-icons.mjs
 *
 * Only the emojis named in MAIN_EMOJIS, LOG_EMOJIS, LOGO_EMOJIS and
 * CRYPTO_EMOJIS below are written. The badge art
 * (scripts/build-badge-art.mjs), the Connect Four pieces, Niko's own logo and
 * the loading spinners are never generated here, and `assertWritable` refuses a
 * name from any of those families outright — so a mistyped table entry fails the
 * run instead of overwriting artwork another script owns.
 *
 * The platform logos come from Simple Icons, one mark per brand, so the whole
 * family shares the same 24-unit grid and the same tile as the rest of the set
 * instead of being a pile of hand-exported PNGs at whatever size and colour
 * each site happened to offer. Every logo is drawn in the neutral ink: the
 * marks are already identifiable by shape, and several brands ship black or
 * near-black art that would disappear on Discord's dark theme. The coin marks
 * follow the same rule, from Web3 Icons' mono variant for the same reason.
 *
 * A new emoji needs an entry in the table below, an entry in
 * src/config/emojis.py, and a run of this script.
 */

import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { svgs as WEB3_ICONS } from "@web3icons/core";
import sharp from "sharp";

const ROOT = path.resolve(import.meta.dirname, "..");
const EMOJI_ASSETS = path.join(ROOT, "src", "assets", "emojis");
const EMOJI_CONFIG = path.join(ROOT, "src", "config", "emojis.py");
const LUCIDE_ICONS = path.join(ROOT, "node_modules", "lucide-react", "dist", "esm", "icons");
const SIMPLE_ICONS = path.join(ROOT, "node_modules", "simple-icons", "icons");
const EMOJI_PX = 128;
// How much of the tile the icon's 24-unit box spans. A Lucide outline keeps a
// little padding of its own, so 0.78 fills roughly the same square the unicode
// emoji next to it does.
const GLYPH_RATIO = 0.78;
// A Simple Icons brand mark fills its 24-unit box edge to edge, so the same
// fraction would draw it ~15% larger than the Lucide icons beside it. 0.72 puts
// its widest dimension on the same ~93px the outline emojis occupy.
const LOGO_RATIO = 0.72;
// A Web3 Icons coin keeps a wide margin of its own inside the box (~75% of it is
// ink), so at the logo scale it would read a quarter smaller than the icons next
// to it. 0.95 brings the coin's ink onto the same ~92px.
const CRYPTO_RATIO = 0.95;

// ── Palette ───────────────────────────────────
// One colour per meaning, and one neutral for everything that has none, so a
// panel full of these emojis reads as a set instead of a pile of unrelated
// colours. The colour is the glyph's own ink, drawn straight onto the message
// background, so it has to hold up on both of Discord's themes.
//
//   GREEN   something was added, allowed, passed or restored
//   RED     something was removed, blocked or refused
//   WARN    a caution, or a filter that tripped
//   AMBER   the premium crown, and nothing else
//   NEUTRAL everything else: navigation, categories, media controls, content,
//           machine stats, and the audit-only log entries
//
// Every ink here is checked against both of Discord's backgrounds at the ~20px
// an emoji is drawn at, and each clears the 3:1 floor in both: on the dark
// theme (#313338) and on the light one (#ffffff). That is why the orange and
// the gold are a step deeper than the bright versions they replace — a bright
// #f0b232 crown measures 1.9:1 on a light embed, i.e. nearly invisible.
const NEUTRAL = "#858c96"; // 3.7:1 dark, 3.4:1 light
const GREEN = "#3ba55d";   // 3.4:1 dark, 3.1:1 light
const RED = "#ed4245";     // 3.3:1 dark, 3.8:1 light
const WARN = "#cf6f16";    // 3.6:1 dark, 3.5:1 light
const AMBER = "#bd7f10";   // 3.7:1 dark, 3.4:1 light

/**
 * The bot's general-purpose emojis, by their name in src/config/emojis.py.
 * Brand emojis (discord, spotify, github, topgg, …) are deliberately absent.
 */
const MAIN_EMOJIS = [
  // Status and feedback. The outcome glyphs keep their colour; everything that
  // is only a label is neutral, which is most of the set.
  ["tick", "check", GREEN],
  ["cross", "x", RED],
  ["warning", "triangle-alert", WARN],
  ["danger", "octagon-alert", RED],
  ["important", "info", NEUTRAL],
  ["question", "circle-help", NEUTRAL],
  ["plus", "plus", GREEN],
  ["minus", "minus", RED],
  ["thumbs_up", "thumbs-up", GREEN],
  ["thumbs_down", "thumbs-down", RED],
  ["verified", "badge-check", GREEN],

  // Moderation and utility.
  ["ban", "ban", RED],
  ["lock", "lock", NEUTRAL],
  ["unlock", "lock-open", NEUTRAL],
  ["hide", "eye-off", NEUTRAL],
  ["unhide", "eye", NEUTRAL],
  ["edit", "pencil", NEUTRAL],
  ["trash", "trash-2", RED],
  ["broom", "broom", NEUTRAL],
  ["moderation", "shield", NEUTRAL],
  ["automod", "radar", NEUTRAL],
  ["utility", "wrench", NEUTRAL],
  ["nsfw", "circle-slash", RED],

  // Navigation and structure — the help menu and the panels are built from
  // these, so they are all neutral.
  ["home", "house", NEUTRAL],
  ["general", "layout-grid", NEUTRAL],
  ["categories", "folder-tree", NEUTRAL],
  ["settings", "settings", NEUTRAL],
  ["docs", "book-open", NEUTRAL],
  ["website", "globe", NEUTRAL],
  ["notepad", "notebook-pen", NEUTRAL],
  ["scroll", "scroll-text", NEUTRAL],
  ["stats", "chart-column", NEUTRAL],
  ["support", "life-buoy", NEUTRAL],
  ["arrow_left", "arrow-left", NEUTRAL],
  ["arrow_right", "arrow-right", NEUTRAL],

  // People and members.
  ["user", "user", NEUTRAL],
  ["join", "user-plus", NEUTRAL],
  ["leave", "user-minus", NEUTRAL],
  ["welcome", "heart-handshake", NEUTRAL],
  ["invite", "mail", NEUTRAL],

  // Content.
  ["message", "message-square", NEUTRAL],
  ["image", "image", NEUTRAL],
  ["link", "link", NEUTRAL],
  ["megaphone", "megaphone", NEUTRAL],
  ["lightbulb", "lightbulb", NEUTRAL],
  ["heart", "heart", NEUTRAL],
  ["star", "star", NEUTRAL],
  ["ai", "sparkles", NEUTRAL],
  ["bot", "bot", NEUTRAL],
  ["bug", "bug", NEUTRAL],

  // Media controls — all neutral. The music and voicemaster panels post a whole
  // row of these at once, and that is where mixed colours looked worst.
  ["play", "play", NEUTRAL],
  ["pause", "pause", NEUTRAL],
  ["stop", "square", NEUTRAL],
  ["skip", "skip-forward", NEUTRAL],
  ["rewind", "rewind", NEUTRAL],
  ["shuffle", "shuffle", NEUTRAL],
  ["loop", "repeat", NEUTRAL],
  ["queue", "list-music", NEUTRAL],
  // The two halves of the volume control. One wave and two waves read as
  // quieter/louder at 20px without needing a plus or a minus beside them.
  ["volume_down", "volume-1", NEUTRAL],
  ["volume_up", "volume-2", NEUTRAL],
  // Autoplay keeps the radio it was as a unicode glyph: a signal with waves
  // reads as "keep finding more" and stays legible beside the other controls.
  ["autoplay", "radio", NEUTRAL],
  ["refresh", "refresh-cw", NEUTRAL],
  ["music", "music", NEUTRAL],
  ["voicemaster", "mic-vocal", NEUTRAL],
  // The claim mark in the voicemaster panels. Premium's crown is the one gold
  // glyph; this one stays neutral so a fresh channel's controls match.
  ["owner_icon", "crown", NEUTRAL],
  ["disconnect", "plug-zap", NEUTRAL],
  // .ping's answer, and the one emoji here Lucide has no icon for.
  ["pingpong", "paddle", NEUTRAL],

  // Rewards and commands.
  ["premium", "crown", AMBER],
  ["gift", "gift", NEUTRAL],
  ["giveaway", "party-popper", NEUTRAL],
  ["ticket", "ticket", NEUTRAL],
  ["economy", "coins", NEUTRAL],
  ["leveling", "trending-up", NEUTRAL],
  ["gambling", "dice-5", NEUTRAL],
  ["games", "gamepad-2", NEUTRAL],
  ["roleplay", "theater", NEUTRAL],
  ["paint", "palette", NEUTRAL],
  ["reminder", "alarm-clock", NEUTRAL],
  // The giveaway setup panel's own controls, and the member list its manage
  // panel opens.
  ["duration", "timer", NEUTRAL],
  ["trophy", "trophy", NEUTRAL],
  ["participants", "users", NEUTRAL],
  // A giveaway that ended with no entries. The only face in the set, because
  // it is the only line that would otherwise drop a unicode emoji mid-sentence.
  ["sad", "frown", NEUTRAL],

  // Machine stats for the status commands.
  ["cpu", "cpu", NEUTRAL],
  ["ram", "memory-stick", NEUTRAL],
  ["disk", "hard-drive", NEUTRAL],
  ["host", "server", NEUTRAL],
];

/**
 * One emoji per server-log message type, so no two entries in a log channel
 * share an icon. The names are new on purpose: the startup emoji sync only
 * uploads art for names it does not find yet, so refreshed artwork under an
 * existing name never reaches Discord.
 *
 * Every title the logging cog and the automod log through it are listed here;
 * `LOG_EMOJI_KEYS` in src/cogs/logging/formatters.py is the other half of this
 * table and the two are checked against each other by tests.
 */
const LOG_EMOJIS = [
  // Moderation. Colour marks the outcome of the action: a removal or a block is
  // red, a reprieve is green, a caution is orange.
  ["log_kick", "user-x", RED],
  ["log_ban", "ban", RED],
  ["log_unban", "user-check", GREEN],
  ["log_warn", "triangle-alert", WARN],
  ["log_clear_warnings", "list-x", GREEN],
  ["log_mute", "mic-off", RED],
  ["log_tempmute", "timer", WARN],
  ["log_unmute", "mic", GREEN],
  ["log_nickname", "tag", NEUTRAL],
  ["log_timeout", "hourglass", WARN],
  ["log_timeout_removed", "alarm-clock-off", GREEN],
  ["log_clear", "eraser", RED],
  ["log_purge", "trash-2", RED],
  ["log_lock", "lock", WARN],
  ["log_unlock", "lock-open", GREEN],

  // AutoMod.
  ["log_anti_spam", "radar", WARN],
  ["log_anti_link", "link-2-off", WARN],
  ["log_bad_words", "spell-check", WARN],
  ["log_mass_mention", "at-sign", WARN],
  ["log_nsfw_filter", "eye-off", WARN],
  ["log_app_detected", "app-window", WARN],
  ["log_app_action", "gavel", RED],
  ["log_interaction_flood", "zap", WARN],
  ["log_anti_nuke", "bomb", RED],
  ["log_anti_raid", "waves", WARN],

  // Messages — the audit trail rather than an outcome, so no colour.
  ["log_message_deleted", "message-square-x", NEUTRAL],
  ["log_message_edited", "pencil-line", NEUTRAL],

  // Channels.
  ["log_channel_created", "square-plus", NEUTRAL],
  ["log_channel_deleted", "square-x", NEUTRAL],
  ["log_channel_updated", "sliders-horizontal", NEUTRAL],

  // Members.
  ["log_member_join", "user-plus", NEUTRAL],
  ["log_member_leave", "user-minus", NEUTRAL],
  ["log_member_updated", "user-cog", NEUTRAL],
  ["log_avatar", "camera", NEUTRAL],

  // Captcha.
  ["log_captcha_passed", "shield-check", GREEN],
  ["log_captcha_failed", "shield-x", RED],
  ["log_captcha_kicked", "shield-off", RED],

  // Invites.
  ["log_invite_created", "ticket-plus", NEUTRAL],
  ["log_invite_deleted", "ticket-x", NEUTRAL],
  ["log_invite_used", "ticket-check", NEUTRAL],
  ["log_vanity_invite", "sparkles", NEUTRAL],
  ["log_unknown_join", "badge-help", NEUTRAL],

  // Roles.
  ["log_role_created", "tag-plus", NEUTRAL],
  ["log_role_deleted", "tag-x", NEUTRAL],
  ["log_role_updated", "tags", NEUTRAL],

  // Server.
  ["log_server_updated", "server-cog", NEUTRAL],
  ["log_emoji_updated", "smile", NEUTRAL],
  ["log_sticker_updated", "sticker", NEUTRAL],

  // Giveaways. A ban is a removal and an unban a reprieve, so they follow the
  // same colour rule as the moderation entries above.
  ["log_giveaway_ban", "ticket-slash", RED],
  ["log_giveaway_unban", "circle-check", GREEN],

  // Voice.
  ["log_voice_join", "headphones", NEUTRAL],
  ["log_voice_leave", "phone-off", NEUTRAL],
  ["log_voice_move", "arrow-left-right", NEUTRAL],
];

/**
 * The platform logos, by Simple Icons slug (https://simpleicons.org).
 *
 * These used to be hand-exported brand PNGs, so the family was a 36px Last.fm
 * mark next to a 128px Instagram one, an animated gif for Discord and four
 * different background colours. Sourcing them from Simple Icons gives every
 * brand the same grid, the same tile and the same ink as the icons around them;
 * the slug is kept separately from the emoji name because a few brands spell
 * them differently (`twitterx` → `x`, `lastfm` → `lastdotfm`).
 */
const LOGO_EMOJIS = [
  // The bot itself and the developer platforms it is listed on.
  ["discord", "discord", NEUTRAL],
  ["github", "github", NEUTRAL],
  ["python", "python", NEUTRAL],
  ["topgg", "topdotgg", NEUTRAL],
  ["lastfm", "lastdotfm", NEUTRAL],
  ["spotify", "spotify", NEUTRAL],

  // Social media.
  ["instagram", "instagram", NEUTRAL],
  ["tiktok", "tiktok", NEUTRAL],
  ["twitterx", "x", NEUTRAL],
  ["youtube", "youtube", NEUTRAL],
  ["youtube_shorts", "youtubeshorts", NEUTRAL],
  ["reddit", "reddit", NEUTRAL],
  ["bluesky", "bluesky", NEUTRAL],
  ["soundcloud", "soundcloud", NEUTRAL],
  ["twitch", "twitch", NEUTRAL],
];

/**
 * The cryptocurrency emojis, by Web3 Icons token symbol (web3icons.io).
 *
 * These were hand-exported coin logos at a mix of sizes and colours. Web3 Icons
 * ships every token in a `branded`, `mono` and `background` variant; the mono
 * one is the same kind of single-ink mark as the rest of this set, so a payment
 * row reads as icons instead of a row of differently-framed coins. The symbol is
 * kept separately from the emoji name because the name says which coin it is
 * (`crypto_tether_usdt`) and the symbol is the library's key (`usdt`).
 */
const CRYPTO_EMOJIS = [
  ["crypto_bitcoin", "btc", NEUTRAL],
  ["crypto_ethereum", "eth", NEUTRAL],
  ["crypto_bnb", "bnb", NEUTRAL],
  ["crypto_dogecoin", "doge", NEUTRAL],
  ["crypto_ltc", "ltc", NEUTRAL],
  ["crypto_monero", "xmr", NEUTRAL],
  ["crypto_tether_usdt", "usdt", NEUTRAL],
  ["crypto_tron", "trx", NEUTRAL],
];

/**
 * Families this script must never write.
 *
 * badge art belongs to scripts/build-badge-art.mjs, the Connect Four pieces are
 * game sprites, and the loading spinners are animation frames. A name that
 * matches any of these throws, so a bad table entry cannot quietly overwrite
 * art another script owns.
 */
const PROTECTED = [
  ["badge art", /^badge/i],
  ["Connect Four", /^(?:c4|white)/i],
  ["loading spinner", /loading/i],
];

// The numeric emoji art (number_zero … number_nine) never comes from an icon
// font, and the Discord presence dots are Discord's own badges.
const NUMERIC = /^number_/;
const PRESENCE = /^status_/;

function assertWritable(name) {
  for (const [family, pattern] of PROTECTED) {
    if (pattern.test(name)) {
      throw new Error(`Refusing to generate ${name}: it belongs to the ${family} emojis.`);
    }
  }
  if (NUMERIC.test(name) || PRESENCE.test(name)) {
    throw new Error(`Refusing to generate ${name}: it is not an icon-font emoji.`);
  }
}

/**
 * The glyphs Lucide has no icon for, drawn by hand in the same 24-unit box and
 * with the same 2-unit round-capped stroke as a Lucide outline, so they scale
 * and read exactly like the icons around them.
 */
const CUSTOM_GLYPHS = {
  // A table-tennis paddle and ball. lucide-react ships no paddle, racket or
  // ball icon, and .ping's answer is a paddle, so the blade is drawn the way
  // Lucide draws its magnifier and the ball flies at the top right.
  paddle: [
    ["circle", { cx: "9.2", cy: "10.4", r: "6" }],
    ["path", { d: "m13.6 14.8 5.6 5.6" }],
    ["circle", { cx: "19", cy: "4.6", r: "1.7" }],
  ],
};

/**
 * The outline of an icon, as `[tag, attributes]` pairs in the icon's own
 * 24-unit coordinate system.
 *
 * lucide-react is the only Lucide package the project installs, and its icon
 * modules export the outline as `__iconNode` (`__iconData` in older builds). Its
 * aliases (smile → the full face-slightly-smiling module, trash-2, waves,
 * circle-help) re-export only the default component, so an alias is followed to
 * the module that owns the data. A name in CUSTOM_GLYPHS is taken as is, so the
 * table never has to branch.
 */
async function loadIcon(name) {
  if (CUSTOM_GLYPHS[name]) {
    return CUSTOM_GLYPHS[name];
  }
  let file = path.join(LUCIDE_ICONS, `${name}.mjs`);
  let source;
  try {
    source = await readFile(file, "utf-8");
  } catch {
    throw new Error(`Lucide has no icon named "${name}".`);
  }
  const alias = source.match(/export \{ default \} from '\.\/([a-z0-9-]+)\.mjs';/);
  if (alias) {
    file = path.join(LUCIDE_ICONS, `${alias[1]}.mjs`);
  }
  const module = await import(pathToFileURL(file).href);
  const data = module.__iconNode ?? module.__iconData;
  const nodes = Array.isArray(data) ? data : data?.node;
  if (!nodes) {
    throw new Error(`Lucide icon "${name}" does not expose its outline.`);
  }
  return nodes;
}

/** Serialise one icon node without the React keys Lucide carries. */
function element([tag, attributes]) {
  const rendered = Object.entries(attributes)
    .filter(([key]) => key !== "key")
    .map(([key, value]) => `${key}="${value}"`)
    .join(" ");
  return `<${tag} ${rendered}/>`;
}

/**
 * The emoji as SVG: the icon's outline drawn in the family colour, with nothing
 * behind it.
 *
 * The glyph keeps Lucide's own 2-unit stroke width and 24-unit box, and the
 * whole group is scaled up to fill the square the way a normal emoji does;
 * scaling the group scales the stroke with it, so the icon looks exactly like
 * the one the website draws, just larger. Without a disc to frame it the glyph
 * can take more of the tile than the old inset allowed, which is what keeps it
 * the same apparent size as the unicode emoji in the same message.
 */
function emojiSvg(nodes, color) {
  const glyph = (EMOJI_PX * GLYPH_RATIO).toFixed(4);
  const scale = (glyph / 24).toFixed(6);
  const offset = ((EMOJI_PX - glyph) / 2).toFixed(4);
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${EMOJI_PX}" height="${EMOJI_PX}" viewBox="0 0 ${EMOJI_PX} ${EMOJI_PX}">`,
    // The few glyphs filled with currentColor (the tags, the palette) resolve to
    // `color`, so their filled shapes are drawn in the same colour as the stroke.
    `  <g transform="translate(${offset} ${offset}) scale(${scale})" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" color="${color}">`,
    ...nodes.map((node) => `    ${element(node)}`),
    "  </g>",
    "</svg>",
    "",
  ].join("\n");
}

/**
 * A brand mark's outline, from the installed `simple-icons` package.
 *
 * Simple Icons ships one `<slug>.svg` per brand in a 24-unit box, filled black
 * with no stroke. Only the path is taken, so the tile, the ink and the scale are
 * this script's own and every logo matches the icons around it. A missing slug
 * throws instead of writing a blank emoji.
 */
async function loadLogo(slug) {
  let source;
  try {
    source = await readFile(path.join(SIMPLE_ICONS, `${slug}.svg`), "utf-8");
  } catch {
    throw new Error(`Simple Icons has no brand named "${slug}".`);
  }
  const outline = source.match(/<path d="([^"]+)"/);
  if (!outline) {
    throw new Error(`Simple Icons brand "${slug}" has no path data.`);
  }
  return outline[1];
}

/**
 * The logo as SVG: the brand's filled mark in one ink, with nothing behind it.
 *
 * A brand mark has no stroke to carry its weight, so it is scaled slightly
 * smaller than an outline glyph — its ink runs to the edge of the 24-unit box,
 * and at LOGO_RATIO it covers the same square the Lucide emojis do.
 */
function logoSvg(outline, color) {
  const glyph = (EMOJI_PX * LOGO_RATIO).toFixed(4);
  const scale = (glyph / 24).toFixed(6);
  const offset = ((EMOJI_PX - glyph) / 2).toFixed(4);
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${EMOJI_PX}" height="${EMOJI_PX}" viewBox="0 0 ${EMOJI_PX} ${EMOJI_PX}">`,
    `  <g transform="translate(${offset} ${offset}) scale(${scale})" fill="${color}">`,
    `    <path d="${outline}"/>`,
    "  </g>",
    "</svg>",
    "",
  ].join("\n");
}

/**
 * A coin mark, from the installed `@web3icons/core` package.
 *
 * Every token is published as `svgs.tokens.<variant>.<symbol>.default`, an SVG
 * string on the same 24-unit box as the other two sources. The mono variant
 * paints its shapes white so a React caller can recolour them; the string is
 * taken as is and the white is swapped for the family ink, which keeps the
 * artwork pixel-identical apart from its colour.
 */
function loadCrypto(symbol) {
  const module = WEB3_ICONS.tokens.mono[symbol];
  const svg = module?.default ?? module;
  if (typeof svg !== "string") {
    throw new Error(`Web3 Icons has no mono token icon for "${symbol}".`);
  }
  return svg;
}

/**
 * The coin mark as SVG: Web3 Icons' shapes in one ink, with nothing behind it.
 *
 * The source tile is stripped so its 24-unit viewBox can be redrawn at the same
 * scale as the logos beside it, and the white fill the mono variant uses is
 * replaced with the ink.
 */
function cryptoSvg(source, color) {
  const inner = source
    .replace(/^\s*<svg[^>]*>/, "")
    .replace(/<\/svg>\s*$/, "")
    .replaceAll('fill="#fff"', `fill="${color}"`)
    .trim();
  const glyph = (EMOJI_PX * CRYPTO_RATIO).toFixed(4);
  const scale = (glyph / 24).toFixed(6);
  const offset = ((EMOJI_PX - glyph) / 2).toFixed(4);
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${EMOJI_PX}" height="${EMOJI_PX}" viewBox="0 0 ${EMOJI_PX} ${EMOJI_PX}">`,
    `  <g transform="translate(${offset} ${offset}) scale(${scale})">`,
    ...inner.split("\n").map((line) => `    ${line.trim()}`),
    "  </g>",
    "</svg>",
    "",
  ].join("\n");
}

/** Render the SVG on the same high density the other asset scripts use. */
function renderPng(svg) {
  return sharp(Buffer.from(svg), { density: 384 })
    .resize(EMOJI_PX, EMOJI_PX, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png({ compressionLevel: 9 })
    .toBuffer();
}

/** Every name the config knows, so the emoji list can never drift from the bot. */
async function configuredNames() {
  const source = await readFile(EMOJI_CONFIG, "utf-8");
  return new Set([...source.matchAll(/emoji_name == "([A-Za-z0-9_]+)"/g)].map((match) => match[1]));
}

const emojis = [...MAIN_EMOJIS, ...LOG_EMOJIS];
const logos = LOGO_EMOJIS;
const cryptos = CRYPTO_EMOJIS;
const names = new Set();
for (const [name] of [...emojis, ...logos, ...cryptos]) {
  assertWritable(name);
  if (names.has(name)) {
    throw new Error(`"${name}" is listed twice.`);
  }
  names.add(name);
}

const configured = await configuredNames();
const unconfigured = [...names].filter((name) => !configured.has(name));
if (unconfigured.length) {
  throw new Error(
    `These emojis have no entry in src/config/emojis.py, so the bot could never send them: ${unconfigured.join(", ")}`,
  );
}

let bytes = 0;
for (const [name, icon, color] of emojis) {
  const png = await renderPng(emojiSvg(await loadIcon(icon), color));
  await writeFile(path.join(EMOJI_ASSETS, `${name}.png`), png);
  bytes += png.length;
  console.log(`  ${name.padEnd(24)} ${icon.padEnd(20)} ${color}  ${png.length} bytes`);
}
for (const [name, slug, color] of logos) {
  const png = await renderPng(logoSvg(await loadLogo(slug), color));
  await writeFile(path.join(EMOJI_ASSETS, `${name}.png`), png);
  bytes += png.length;
  console.log(`  ${name.padEnd(24)} ${slug.padEnd(20)} ${color}  ${png.length} bytes`);
}
for (const [name, symbol, color] of cryptos) {
  const png = await renderPng(cryptoSvg(loadCrypto(symbol), color));
  await writeFile(path.join(EMOJI_ASSETS, `${name}.png`), png);
  bytes += png.length;
  console.log(`  ${name.padEnd(24)} ${symbol.padEnd(20)} ${color}  ${png.length} bytes`);
}

console.log(
  `Wrote ${emojis.length + logos.length + cryptos.length} emoji PNGs to ` +
    `${path.relative(ROOT, EMOJI_ASSETS)} (${MAIN_EMOJIS.length} main, ${LOG_EMOJIS.length} log, ` +
    `${logos.length} logo, ${cryptos.length} crypto) — ${(bytes / 1024).toFixed(0)} KiB.`,
);
console.log("Left untouched: badge art, Connect Four, and the loading emojis.");
