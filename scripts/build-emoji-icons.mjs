/**
 * Draws Niko's emoji art from the With Icons families.
 *
 *   - withicons (outline) for the generic set
 *   - withicons-christmas / withicons-halloween / withicons-valentine for the
 *     seasonal variants of the celebration emojis
 *
 * Artwork is written to the seasonal asset tree:
 *
 *   src/assets/emojis/seasonal/default/<name>.png
 *   src/assets/emojis/seasonal/<season>/<name>_<season>.png
 *
 * The sync selects the active season by date, so all variants are uploaded
 * once and switching seasons only changes which id the config returns. The
 * `badges/`, `manual/` and `review/` folders are owned by other scripts or by
 * hand and are never written here.
 *
 * The icon paths are cached in scripts/withicons-icons.json so the build stays
 * offline. Rebuild that cache from the Iconify API when the tables below gain
 * an icon; the cache is checked for every icon this script needs.
 *
 * Run from the repository root:  node scripts/build-emoji-icons.mjs
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const ROOT = path.resolve(import.meta.dirname, "..");
const EMOJI_ASSETS = path.join(ROOT, "src", "assets", "emojis");
const SEASONAL_ASSETS = path.join(EMOJI_ASSETS, "seasonal");
const DEFAULT_ASSETS = path.join(SEASONAL_ASSETS, "default");
const EMOJI_CONFIG = path.join(ROOT, "src", "config", "emojis.py");
const ICON_CACHE = path.join(ROOT, "scripts", "withicons-icons.json");
const EMOJI_PX = 128;

// With Icons draws in a 24-unit box with no padding of its own. A 30-unit
// viewBox leaves three units of transparent space on each side, matching the
// apparent size of the old outline set and leaving a glyph room to breathe in
// a Discord message.
const VIEW_BOX = "-3 -3 30 30";

const ICONS = JSON.parse(await readFile(ICON_CACHE, "utf-8"));

// ── Palette ───────────────────────────────────
// The colour carries meaning, so it is applied to the outline icons only.
// GREEN means added/allowed/passed, RED removed/blocked, WARN a caution,
// AMBER the premium crown, and NEUTRAL everything else. Each clears 3:1 on
// Discord's dark (#313338) and light (#ffffff) backgrounds.
const NEUTRAL = "#858c96";
const GREEN = "#3ba55d";
const RED = "#ed4245";
const WARN = "#cf6f16";
const AMBER = "#bd7f10";

/**
 * The bot's general-purpose emojis, by their name in src/config/emojis.py.
 * The second field is the With Icons slug. Three old entries (pingpong,
 * roleplay, ram) are in src/assets/emojis/review/ instead: With Icons has no
 * clean paddle, theatre or memory-stick mark.
 */
const MAIN_EMOJIS = [
  // Status and feedback.
  ["tick", "check", GREEN],
  ["cross", "close", RED],
  ["warning", "alert-triangle", WARN],
  ["danger", "octagon-alert", RED],
  ["important", "info-circle", NEUTRAL],
  ["question", "help-circle", NEUTRAL],
  ["plus", "plus", GREEN],
  ["minus", "minus", RED],
  ["thumbs_up", "thumbs-up", GREEN],
  ["thumbs_down", "thumbs-down", RED],
  ["verified", "badge-check", GREEN],

  // Moderation and utility.
  ["ban", "ban", RED],
  ["lock", "lock", NEUTRAL],
  ["unlock", "unlock", NEUTRAL],
  ["hide", "eye-off", NEUTRAL],
  ["unhide", "eye", NEUTRAL],
  ["edit", "pencil", NEUTRAL],
  ["trash", "trash-2", RED],
  ["broom", "broom", NEUTRAL],
  ["moderation", "shield", NEUTRAL],
  ["automod", "radar", NEUTRAL],
  ["utility", "wrench", NEUTRAL],
  ["nsfw", "octagon-x", RED],

  // Navigation and structure.
  ["home", "home", NEUTRAL],
  ["general", "layout-grid", NEUTRAL],
  ["categories", "folder-tree", NEUTRAL],
  ["settings", "settings", NEUTRAL],
  ["docs", "book-open", NEUTRAL],
  ["website", "globe", NEUTRAL],
  ["notepad", "notebook-pen", NEUTRAL],
  ["scroll", "scroll-text", NEUTRAL],
  ["stats", "chart-bar", NEUTRAL],
  ["support", "life-buoy", NEUTRAL],
  ["arrow_left", "arrow-left", NEUTRAL],
  ["arrow_right", "arrow-right", NEUTRAL],

  // People and members.
  ["user", "user", NEUTRAL],
  ["join", "user-plus", NEUTRAL],
  ["leave", "user-minus", NEUTRAL],
  ["welcome", "heart-handshake", NEUTRAL],
  ["invite", "mail", NEUTRAL],
  ["participants", "users", NEUTRAL],

  // Content and social.
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
  ["sad", "frown", NEUTRAL],

  // Media controls.
  ["play", "play", NEUTRAL],
  ["pause", "pause", NEUTRAL],
  ["stop", "square", NEUTRAL],
  ["skip", "skip-forward", NEUTRAL],
  ["rewind", "rewind", NEUTRAL],
  ["shuffle", "shuffle", NEUTRAL],
  ["loop", "repeat", NEUTRAL],
  ["queue", "list-music", NEUTRAL],
  ["volume_down", "volume-1", NEUTRAL],
  ["volume_up", "volume", NEUTRAL],
  ["autoplay", "radio", NEUTRAL],
  ["refresh", "refresh", NEUTRAL],
  ["music", "music-2", NEUTRAL],
  ["voicemaster", "mic-vocal", NEUTRAL],
  ["owner_icon", "crown", NEUTRAL],
  ["disconnect", "plug-zap", NEUTRAL],

  // Rewards and commands.
  ["premium", "crown", AMBER],
  ["gift", "gift", NEUTRAL],
  ["giveaway", "party-popper", NEUTRAL],
  ["ticket", "ticket", NEUTRAL],
  ["economy", "coins", NEUTRAL],
  ["leveling", "trending-up", NEUTRAL],
  ["gambling", "dices", NEUTRAL],
  ["games", "gamepad", NEUTRAL],
  ["paint", "palette", NEUTRAL],
  ["reminder", "alarm-clock", NEUTRAL],
  ["duration", "timer", NEUTRAL],
  ["trophy", "trophy", NEUTRAL],

  // Machine stats.
  ["cpu", "cpu", NEUTRAL],
  ["disk", "hard-drive", NEUTRAL],
  ["host", "server", NEUTRAL],
];

/**
 * One emoji per server-log message type. The unmatched invite/role/unknown-join
 * and giveaway-ban marks stay in review/ rather than being forced onto an icon
 * that would read as a different event.
 */
const LOG_EMOJIS = [
  // Moderation.
  ["log_kick", "user-x", RED],
  ["log_ban", "ban", RED],
  ["log_unban", "user-check", GREEN],
  ["log_warn", "alert-triangle", WARN],
  ["log_clear_warnings", "list-x", GREEN],
  ["log_mute", "microphone-off", RED],
  ["log_tempmute", "timer", WARN],
  ["log_unmute", "microphone", GREEN],
  ["log_nickname", "tag", NEUTRAL],
  ["log_timeout", "hourglass", WARN],
  ["log_timeout_removed", "alarm-clock-off", GREEN],
  ["log_clear", "eraser", RED],
  ["log_purge", "trash-2", RED],
  ["log_lock", "lock", WARN],
  ["log_unlock", "unlock", GREEN],

  // AutoMod.
  ["log_anti_spam", "radar", WARN],
  ["log_anti_link", "unlink", WARN],
  ["log_bad_words", "spell-check", WARN],
  ["log_mass_mention", "at-sign", WARN],
  ["log_nsfw_filter", "eye-off", WARN],
  ["log_app_detected", "app-window", WARN],
  ["log_app_action", "gavel", RED],
  ["log_interaction_flood", "zap", WARN],
  ["log_anti_nuke", "bomb", RED],
  ["log_anti_raid", "waves", WARN],

  // Messages.
  ["log_message_deleted", "message-square-x", NEUTRAL],
  ["log_message_edited", "pen-line", NEUTRAL],

  // Channels.
  ["log_channel_created", "square-plus", NEUTRAL],
  ["log_channel_deleted", "square-x", NEUTRAL],
  ["log_channel_updated", "sliders", NEUTRAL],

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
  ["log_vanity_invite", "sparkles", NEUTRAL],

  // Roles.
  ["log_server_updated", "server-cog", NEUTRAL],
  ["log_emoji_updated", "smile", NEUTRAL],
  ["log_sticker_updated", "sticky-note", NEUTRAL],

  // Giveaways.
  ["log_giveaway_unban", "circle-check-big", GREEN],

  // Voice.
  ["log_voice_join", "headphones", NEUTRAL],
  ["log_voice_leave", "phone-off", NEUTRAL],
  ["log_voice_move", "arrow-left-right", NEUTRAL],
];

/**
 * Emojis with seasonal variants. The same base name is generated for every
 * season in SEASONAL_SETS; the config resolves `<name>_<season>` only while
 * that season is active. The unsuffixed file in default/ is the fallback.
 */
const SEASONAL_EMOJIS = [
  ["heart", "heart"],
  ["gift", "gift"],
  ["star", "star"],
  ["welcome", "heart-handshake"],
  ["giveaway", "party-popper"],
  ["premium", "crown"],
  ["ticket", "ticket"],
  ["trophy", "trophy"],
  ["economy", "coins"],
  ["games", "gamepad"],
];

const SEASONAL_SETS = {
  christmas: "withicons-christmas",
  halloween: "withicons-halloween",
  valentine: "withicons-valentine",
};

/**
 * Generated emojis that have no clean With Icons equivalent. Their existing
 * PNGs are in src/assets/emojis/review/ and still reach Discord through the
 * sync; they are simply not overwritten by this script until they are reviewed.
 */
const REVIEW_EMOJIS = [
  {
    family: "general",
    names: ["pingpong", "roleplay", "ram"],
    reason: "With Icons has no clean paddle, theatre or memory-stick mark",
  },
  {
    family: "log",
    names: [
      "log_invite_created",
      "log_invite_deleted",
      "log_invite_used",
      "log_unknown_join",
      "log_role_created",
      "log_role_deleted",
      "log_role_updated",
      "log_giveaway_ban",
    ],
    reason: "With Icons has no plus/x/check ticket, tag-plus/x/tags or badge-help marks",
  },
  {
    family: "brand",
    names: [
      "discord",
      "github",
      "python",
      "topgg",
      "lastfm",
      "spotify",
      "instagram",
      "tiktok",
      "twitterx",
      "youtube",
      "youtube_shorts",
      "reddit",
      "bluesky",
      "soundcloud",
      "twitch",
    ],
    reason: "With Icons ships no brand marks; the existing Simple Icons art is isolated",
  },
  {
    family: "crypto",
    names: [
      "crypto_bitcoin",
      "crypto_ethereum",
      "crypto_bnb",
      "crypto_dogecoin",
      "crypto_ltc",
      "crypto_monero",
      "crypto_tether_usdt",
      "crypto_tron",
    ],
    reason: "With Icons has no cryptocurrency family",
  },
  {
    family: "number",
    names: [
      "number_zero",
      "number_one",
      "number_two",
      "number_three",
      "number_four",
      "number_five",
      "number_six",
      "number_seven",
      "number_eight",
      "number_nine",
    ],
    reason: "With Icons has no plain 0-9 digits",
  },
];

const PROTECTED = [
  ["badge art", /^badge/i],
  ["Connect Four", /^(?:c4|white)/i],
  ["loading spinner", /loading/i],
];

const PRESENCE = /^status_/;

function assertWritable(name) {
  for (const [family, pattern] of PROTECTED) {
    if (pattern.test(name)) {
      throw new Error(`Refusing to generate ${name}: it belongs to the ${family} emojis.`);
    }
  }
  if (PRESENCE.test(name)) {
    throw new Error(`Refusing to generate ${name}: it is not an icon-font emoji.`);
  }
}

function icon(prefix, name) {
  const found = ICONS[prefix]?.[name];
  if (!found?.body) {
    throw new Error(`Missing cached ${prefix} artwork for "${name}".`);
  }
  return found;
}

/**
 * The seasonal sets paint a full 24x24 decorative backdrop behind some icons.
 * An emoji is drawn straight onto Discord's message background, so that tile
 * would become a coloured square in every message. Removing only the full-tile
 * path keeps every actual decoration and leaves a transparent emoji.
 */
function withoutBackdrop(body) {
  return body.replace(/<path\b[^>]*\bd="M0 0h24v24H0Z"[^>]*\/>/gi, "");
}

function emojiSvg(art, color, { seasonal = false } = {}) {
  const body = seasonal ? withoutBackdrop(art.body) : art.body;
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${EMOJI_PX}" height="${EMOJI_PX}" viewBox="${VIEW_BOX}" color="${color}">`,
    body,
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

const names = new Set();
for (const [name] of [...MAIN_EMOJIS, ...LOG_EMOJIS]) {
  assertWritable(name);
  if (names.has(name)) {
    throw new Error(`"${name}" is listed twice.`);
  }
  names.add(name);
}
for (const [base] of SEASONAL_EMOJIS) {
  if (!names.has(base)) {
    throw new Error(`Seasonal base "${base}" is not in the default set.`);
  }
  for (const season of Object.keys(SEASONAL_SETS)) {
    const name = `${base}_${season}`;
    if (names.has(name)) {
      throw new Error(`"${name}" is listed twice.`);
    }
    names.add(name);
  }
}

const configured = await configuredNames();
const unconfigured = [...names].filter((name) => !configured.has(name));
if (unconfigured.length) {
  throw new Error(
    `These emojis have no entry in src/config/emojis.py, so the bot could never send them: ${unconfigured.join(", ")}`,
  );
}

const reviewed = REVIEW_EMOJIS.flatMap((group) => group.names);
for (const name of reviewed) {
  if (names.has(name)) {
    throw new Error(`"${name}" is both generated and in review.`);
  }
  if (!configured.has(name)) {
    throw new Error(`"${name}" is in review but has no config entry.`);
  }
}

await mkdir(DEFAULT_ASSETS, { recursive: true });
let bytes = 0;
for (const [name, iconName, color] of [...MAIN_EMOJIS, ...LOG_EMOJIS]) {
  const png = await renderPng(emojiSvg(icon("withicons", iconName), color));
  const file = path.join(DEFAULT_ASSETS, `${name}.png`);
  await writeFile(file, png);
  bytes += png.length;
  console.log(`  default/${name.padEnd(26)} ${iconName.padEnd(22)} ${color}  ${png.length} bytes`);
}

for (const [season, prefix] of Object.entries(SEASONAL_SETS)) {
  const directory = path.join(SEASONAL_ASSETS, season);
  await mkdir(directory, { recursive: true });
  for (const [base, iconName] of SEASONAL_EMOJIS) {
    const png = await renderPng(emojiSvg(icon(prefix, iconName), NEUTRAL, { seasonal: true }));
    const name = `${base}_${season}`;
    const file = path.join(directory, `${name}.png`);
    await writeFile(file, png);
    bytes += png.length;
    console.log(`  ${season}/${name.padEnd(26)} ${iconName.padEnd(22)} seasonal  ${png.length} bytes`);
  }
}

console.log(
  `Wrote ${MAIN_EMOJIS.length + LOG_EMOJIS.length} default and ` +
    `${SEASONAL_EMOJIS.length * Object.keys(SEASONAL_SETS).length} seasonal emoji PNGs to ` +
    `${path.relative(ROOT, SEASONAL_ASSETS)} (${(bytes / 1024).toFixed(0)} KiB).`,
);
console.log(
  `Left untouched: ${reviewed.length} review emojis, badges, manual art, Connect Four and loading spinners.`,
);
