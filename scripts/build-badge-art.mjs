/**
 * Builds Niko's badge artwork.
 *
 *   1. Writes the Niko role badges to web/public/assets/badges/niko_*.svg,
 *      using the Material Symbols artwork cached in scripts/material-badge-icons.json
 *   2. Rasterises every badge (Discord profile badges included) into the PNG
 *      emoji art in src/assets/emojis/badges/, because Discord only accepts
 *      PNG, JPEG or GIF emoji images and never SVG.
 *
 * Run from the repository root:  node scripts/build-badge-art.mjs
 *
 * The PNG names are the emoji names in src/config/emojis.py, so a new badge
 * only needs an entry in the emoji config plus a run of this script.
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const ROOT = path.resolve(import.meta.dirname, "..");
const PUBLIC_ASSETS = path.join(ROOT, "web", "public", "assets");
const EMOJI_ASSETS = path.join(ROOT, "src", "assets", "emojis", "badges");
const EMOJI_PX = 128;

// Material Symbols are stored locally so the build never depends on the
// Iconify API. scripts/material-badge-icons.json is the source of the icon
// paths; the badge colours and labels stay below.
const MATERIAL_ICONS = JSON.parse(
  await readFile(path.join(ROOT, "scripts", "material-badge-icons.json"), "utf-8"),
);

/**
 * The Niko badge family. Colours mirror the support-server role colours in
 * src/cogs/staff/support_server.py, so a badge always matches its role.
 */
const NIKO_BADGES = {
  niko_owner: { label: "Niko Owner", color: "#c8a882", icon: "crown-rounded" },
  niko_staff: { label: "Niko Staff", color: "#d96545", icon: "star-rounded" },
  niko_head_admin: { label: "Head Admin", color: "#e74c3c", icon: "verified-user-rounded" },
  niko_moderator: { label: "Moderator", color: "#e67e22", icon: "gavel-rounded" },
  niko_head_support: { label: "Head of Support", color: "#3498db", icon: "headset-mic-rounded" },
  niko_support: { label: "Support Team", color: "#2ecc71", icon: "support" },
  niko_graphic_designer: { label: "Graphic Designer", color: "#9b59b6", icon: "palette" },
  niko_event_coordinator: { label: "Event Coordinator", color: "#1abc9c", icon: "event-rounded" },
  niko_partnerships_promotions_lead: {
    label: "Partnerships & Promotions Lead",
    color: "#e67e22",
    icon: "campaign-rounded",
  },
  niko_partnership_manager: { label: "Partnership Manager", color: "#3498db", icon: "handshake-rounded" },
  niko_supporter: { label: "Supporter", color: "#f1c40f", icon: "coffee-rounded" },
  niko_bug_hunter: { label: "Bug Bounty Hunter", color: "#e84393", icon: "bug-report-rounded" },
  niko_partner: { label: "Partner", color: "#1abc9c", icon: "link-rounded" },
};

/** Emoji name in src/config/emojis.py -> badge SVG, relative to web/public/assets. */
const EMOJI_ART = {
  // Discord profile badges, drawn from the same SVGs the popups use so the
  // bot card and the website always show the same art. The HypeSquad houses and
  // the developer badges keep Discord's own emoji art in src/assets/emojis/manual.
  staff_badge: "badges/staff.svg",
  // The old partner emoji art no longer matched the rest of the set, so the
  // badge is generated from the profile badge asset like the others.
  partner_badge: "badges/partner.svg",
  bug_hunter_badge: "badges/bug_hunter_level_1.svg",
  bug_hunter_gold_badge: "badges/bug_hunter_level_2.svg",
  hypesquad_events: "hypesquad/events.svg",
  early_supporter_badge: "badges/early_supporter.svg",
  certified_moderator_badge: "badges/certified_moderator.svg",
  supports_commands_badge: "badges/supports_commands.svg",
  // Discord's account-age tiers. Their SVGs come from the official badge set;
  // the bot and the popups draw only the highest tier the account reached.
  ...Object.fromEntries(
    ["seed", "sprout", "bud", "sapling", "blossom", "redwood", "sequoia", "bristlecone", "stromatolite", "primordial"]
      .map((name) => [`account_age_${name}`, `badges/account_age_${name}.svg`]),
  ),
  // Discord draws a different boosting badge for every tier, and the bot and
  // the popups pick the one the streak has reached.
  ...Object.fromEntries(
    [1, 2, 3, 6, 9, 12, 15, 18, 24].map((months) => [
      `boosting_${months}_months`,
      `badges/boosting_${months}_months.svg`,
    ]),
  ),
  // Niko's own role badges.
  badge_owner: "badges/niko_owner.svg",
  badge_staff: "badges/niko_staff.svg",
  badge_head_admin: "badges/niko_head_admin.svg",
  badge_moderator: "badges/niko_moderator.svg",
  badge_head_support: "badges/niko_head_support.svg",
  badge_support: "badges/niko_support.svg",
  badge_graphic_designer: "badges/niko_graphic_designer.svg",
  badge_event_coordinator: "badges/niko_event_coordinator.svg",
  // Discord caps emoji names at 32 characters, so the file name is short even
  // though the badge key (and the role it stands for) is not.
  badge_partnership_lead: "badges/niko_partnerships_promotions_lead.svg",
  badge_partnership_manager: "badges/niko_partnership_manager.svg",
  // The community role badges ship under new names: the original badge_supporter
  // / badge_bugbounty / badge_partner application emojis already exist on
  // Discord with the old art, and the sync only uploads names it does not find
  // yet.
  badge_supporter_role: "badges/niko_supporter.svg",
  badge_bug_hunter_role: "badges/niko_bug_hunter.svg",
  badge_partner_role: "badges/niko_partner.svg",
};

function badgeSvg(label, color, icon) {
  const [, , width, height] = icon.viewBox.split(" ").map(Number);
  const size = 14.2;
  const scale = Math.min(size / width, size / height);
  const x = (24 - width * scale) / 2;
  const y = (24 - height * scale) / 2;
  const body = `<g transform="translate(${x.toFixed(3)} ${y.toFixed(3)}) scale(${scale.toFixed(5)})">${icon.body}</g>`;
  return [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">',
    // An SVG is parsed as XML, so the label's ampersand has to be escaped.
    `  <title>${label.replace(/&/g, "&amp;")}</title>`,
    `  <rect x="1.25" y="1.25" width="21.5" height="21.5" rx="6.75" fill="${color}"/>`,
    '  <rect x="2" y="2" width="20" height="20" rx="6" fill="none" stroke="#fff" stroke-opacity="0.22" stroke-width="1.5"/>',
    `  ${body}`,
    "</svg>",
    "",
  ].join("\n");
}

async function writeNikoBadges() {
  const written = [];
  for (const [key, { label, color, icon }] of Object.entries(NIKO_BADGES)) {
    const art = MATERIAL_ICONS[key];
    if (!art || art.icon !== icon) {
      throw new Error(`Missing cached Material Symbols art for ${key} (${icon})`);
    }
    const file = path.join(PUBLIC_ASSETS, "badges", `${key}.svg`);
    await writeFile(file, badgeSvg(label, color, art), "utf-8");
    written.push(path.relative(ROOT, file));
  }
  return written;
}

async function writeEmojiPngs() {
  await mkdir(EMOJI_ASSETS, { recursive: true });
  const written = [];
  for (const [emoji, relative] of Object.entries(EMOJI_ART)) {
    const source = path.join(PUBLIC_ASSETS, relative);
    const svg = await readFile(source);
    const png = await sharp(svg, { density: 384 })
      .resize(EMOJI_PX, EMOJI_PX, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png({ compressionLevel: 9 })
      .toBuffer();
    const file = path.join(EMOJI_ASSETS, `${emoji}.png`);
    await writeFile(file, png);
    written.push(`${path.relative(ROOT, file)} (${png.length} bytes)`);
  }
  return written;
}

const badges = await writeNikoBadges();
const emojis = await writeEmojiPngs();

console.log(`Wrote ${badges.length} Niko badge SVGs:`);
for (const file of badges) console.log(`  ${file}`);
console.log(`Wrote ${emojis.length} emoji PNGs:`);
for (const file of emojis) console.log(`  ${file}`);
