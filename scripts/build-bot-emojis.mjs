/**
 * Writes the bot's custom emojis to web/src/data/botEmojis.ts.
 *
 *   1. Reads every ``<:name:id>`` / ``<a:name:id>`` token in src/config/emojis.py
 *   2. Writes them to the web app, so the rendering lab draws emoji rendering
 *      with the bot's real emojis instead of made-up samples.
 *
 * Run from the repository root:  node scripts/build-bot-emojis.mjs
 *
 * An emoji needs one run of this script after it is added to the config;
 * tests/test_emoji_rendering.py fails while the two files disagree.
 */

import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
const CONFIG = path.join(ROOT, "src", "config", "emojis.py");
const OUTPUT = path.join(ROOT, "web", "src", "data", "botEmojis.ts");
const TOKEN = /<(?<animated>a?):(?<name>[A-Za-z0-9_~]+):(?<id>\d+)>/g;

// Discord snowflakes are 17-19 digits. A shorter id is one of the stub ids the
// config uses until the startup emoji sync uploads the art and rewrites it.
const SNOWFLAKE_MIN_LENGTH = 15;

const config = await readFile(CONFIG, "utf-8");
const seen = new Set();
const emojis = [];
for (const match of config.matchAll(TOKEN)) {
  const { animated, name, id } = match.groups;
  const key = `${name}:${id}`;
  if (seen.has(key)) continue;
  seen.add(key);
  emojis.push({
    name,
    id,
    animated: animated === "a",
    placeholder: id.length < SNOWFLAKE_MIN_LENGTH,
  });
}

const rows = emojis
  .map((emoji) => `  { name: "${emoji.name}", id: "${emoji.id}", animated: ${emoji.animated}, placeholder: ${emoji.placeholder} },`)
  .join("\n");

const file = `// The bot's custom emojis, generated from src/config/emojis.py by
// scripts/build-bot-emojis.mjs — do not edit by hand.
//
// The rendering lab draws these exact emojis, so emoji rendering is checked
// with the names and ids Discord actually receives. An emoji whose id does not
// resolve (a \`placeholder\` the startup sync has not uploaded yet, a deleted
// emoji, one from another server) falls back to the \`:name:\` text Discord
// shows instead of a broken image.

export type BotEmoji = {
  /** The emoji name Discord stores, without the surrounding colons. */
  name: string;
  /** The emoji id, or a stub id until the startup sync uploads the art. */
  id: string;
  animated: boolean;
  /** True while the id is a config stub rather than an uploaded emoji. */
  placeholder: boolean;
};

export const BOT_EMOJIS: BotEmoji[] = [
${rows}
];

/** The \`<:name:id>\` token Discord and the bot use for this emoji. */
export function botEmojiToken(emoji: BotEmoji): string {
  return \`<\${emoji.animated ? "a" : ""}:\${emoji.name}:\${emoji.id}>\`;
}
`;

await writeFile(OUTPUT, file, "utf-8");
console.log(`Wrote ${emojis.length} bot emojis to ${path.relative(ROOT, OUTPUT)}`);
console.log(`  ${emojis.filter((emoji) => emoji.animated).length} animated, ${emojis.filter((emoji) => emoji.placeholder).length} placeholder ids`);
