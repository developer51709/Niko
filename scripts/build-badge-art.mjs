/**
 * Builds Niko's badge artwork.
 *
 *   1. Writes the custom Niko role badges to web/public/assets/badges/niko_*.svg
 *   2. Rasterises every badge (Discord profile badges included) into the PNG
 *      emoji art in src/assets/emojis/, because Discord only accepts PNG, JPEG
 *      or GIF emoji images and never SVG.
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
const EMOJI_ASSETS = path.join(ROOT, "src", "assets", "emojis");
const EMOJI_PX = 128;

/**
 * The Niko badge family. Colours mirror the support-server role colours in
 * src/cogs/staff/support_server.py, so a badge always matches its role.
 */
const NIKO_BADGES = {
  niko_owner: {
    label: "Niko Owner",
    color: "#c8a882",
    // A crown, for the person who owns Niko.
    glyph: () =>
      `<path fill="#fff" d="M6.9 9.2 9.4 11.5 12 8.2l2.6 3.3 2.5-2.3v6.4H6.9Z"/>`,
  },
  niko_staff: {
    label: "Niko Staff",
    color: "#d96545",
    glyph: () =>
      `<path fill="#fff" d="M12 6.6l1.47 3.58 3.85.29-2.94 2.5.91 3.76L12 14.7l-3.29 2.03.91-3.76-2.94-2.5 3.85-.29Z"/>`,
  },
  niko_head_admin: {
    label: "Head Admin",
    color: "#e74c3c",
    glyph: (color) =>
      `<path fill="#fff" d="M12 5.4l5.6 2.1v4.3c0 3.2-2.3 5.6-5.6 6.8-3.3-1.2-5.6-3.6-5.6-6.8V7.5Z"/>` +
      `<path fill="none" stroke="${color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" d="M9.5 11.9l1.8 1.8 3.5-3.7"/>`,
  },
  niko_moderator: {
    label: "Moderator",
    color: "#e67e22",
    // The gavel is the smallest glyph of the set, so it is scaled up to match.
    scale: 1.15,
    nudge: [0.44, -0.07],
    // A gavel, tilted so it reads at 20 pixels.
    glyph: () =>
      `<g fill="#fff" transform="rotate(-38 12 12)"><rect x="8.3" y="8.1" width="7.4" height="3.8" rx="1.2"/><rect x="11.1" y="11.9" width="1.8" height="6.4" rx="0.9"/></g>`,
  },
  niko_head_support: {
    label: "Head of Support",
    color: "#3498db",
    // The Support Team badge is a plain headset, so the head of that team wears
    // the same headset with its microphone boom: the two never read as one
    // badge at 20 pixels. Scaled down a little because the boom makes the
    // glyph taller than the rest of the family.
    scale: 0.9,
    nudge: [0, -0.1],
    glyph: () =>
      // Boom, hugging the left ear cup and ending in a microphone.
      `<path fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" d="M6.3 16.4c0 1.9 1.6 3 3.4 3h1.7"/>` +
      `<circle cx="12" cy="19.4" r="1.05" fill="#fff"/>` +
      // Band and ear cups.
      `<path fill="none" stroke="#fff" stroke-width="1.7" stroke-linecap="round" d="M6.4 12.4v-1.8a5.6 5.6 0 0 1 11.2 0v1.8"/>` +
      `<rect x="5.1" y="11.6" width="2.6" height="4.8" rx="1.3" fill="#fff"/>` +
      `<rect x="16.3" y="11.6" width="2.6" height="4.8" rx="1.3" fill="#fff"/>`,
  },
  niko_support: {
    label: "Support Team",
    color: "#2ecc71",
    nudge: [0.06, 0.56],
    glyph: () =>
      `<path fill="none" stroke="#fff" stroke-width="1.7" stroke-linecap="round" d="M6.4 13.6v-1.8a5.6 5.6 0 0 1 11.2 0v1.8"/>` +
      `<rect x="5.1" y="12.8" width="2.6" height="4.8" rx="1.3" fill="#fff"/>` +
      `<rect x="16.3" y="12.8" width="2.6" height="4.8" rx="1.3" fill="#fff"/>`,
  },
  niko_graphic_designer: {
    label: "Graphic Designer",
    color: "#9b59b6",
    // A brush rather than a palette: at 20 pixels the palette's paint wells
    // blurred into one blob, while the brush keeps its bristles, ferrule and
    // handle apart. Drawn upright and tilted 45 degrees, then centred.
    nudge: [-0.81, 0.94],
    glyph: () =>
      `<g transform="rotate(45 12 12)">` +
      `<path fill="#fff" d="M9.7 3.4h4.6l-.6 4.6h-3.4Z"/>` +
      `<rect x="10.1" y="8" width="3.8" height="2.4" rx="0.7" fill="#fff"/>` +
      `<rect x="10.9" y="10.4" width="2.2" height="9.4" rx="1.1" fill="#fff"/>` +
      `</g>`,
  },
  niko_event_coordinator: {
    label: "Event Coordinator",
    color: "#1abc9c",
    glyph: (color) =>
      `<rect x="5.8" y="7.4" width="12.4" height="10.6" rx="2" fill="#fff"/>` +
      `<rect x="5.8" y="7.4" width="12.4" height="3.2" rx="1.6" fill="${color}" fill-opacity="0.75"/>` +
      `<rect x="8.6" y="5.6" width="1.6" height="2.8" rx="0.8" fill="#fff"/>` +
      `<rect x="13.8" y="5.6" width="1.6" height="2.8" rx="0.8" fill="#fff"/>`,
  },
  niko_partnerships_promotions_lead: {
    label: "Partnerships & Promotions Lead",
    color: "#e67e22",
    nudge: [1.88, -0.75],
    glyph: () =>
      `<path fill="#fff" d="M14.6 7.2 9 9.8H6.7a1 1 0 0 0-1 1v1.6a1 1 0 0 0 1 1H9l5.6 2.6Z"/>` +
      `<rect x="8.1" y="14.2" width="1.9" height="4.2" rx="0.95" fill="#fff"/>`,
  },
  niko_partnership_manager: {
    label: "Partnership Manager",
    color: "#3498db",
    glyph: (color) =>
      `<rect x="5.6" y="9" width="12.8" height="9" rx="2" fill="#fff"/>` +
      `<path fill="none" stroke="#fff" stroke-width="1.5" d="M9.9 9V8a1.4 1.4 0 0 1 1.4-1.4h1.4A1.4 1.4 0 0 1 14.1 8v1"/>` +
      `<rect x="5.6" y="12.5" width="12.8" height="1.5" fill="${color}" fill-opacity="0.7"/>`,
  },
  niko_supporter: {
    label: "Supporter",
    color: "#f1c40f",
    // The cup and saucer are wide, so the glyph is scaled to the family size.
    scale: 0.92,
    nudge: [-1.09, -1.09],
    // A cup of coffee for the person who bought Niko one.
    glyph: () =>
      `<path fill="#fff" d="M8 11.6h7.6v3.9a2.8 2.8 0 0 1-2.8 2.8h-2a2.8 2.8 0 0 1-2.8-2.8Z"/>` +
      `<path fill="none" stroke="#fff" stroke-width="1.4" stroke-linecap="round" d="M15.6 12.4h1.1a1.9 1.9 0 0 1 0 3.8h-1.1"/>` +
      `<rect x="7.2" y="18.9" width="9.2" height="1.3" rx="0.65" fill="#fff"/>` +
      `<path fill="#fff" d="M12 7.1c.7-1.3 2.9-1 2.9.8 0 1.3-1.9 2.5-2.9 3.2-1-.7-2.9-1.9-2.9-3.2 0-1.8 2.2-2.1 2.9-.8Z"/>`,
  },
  niko_bug_hunter: {
    label: "Bug Bounty Hunter",
    color: "#e84393",
    nudge: [0.06, 0.81],
    glyph: () =>
      `<ellipse cx="12" cy="13.9" rx="3.5" ry="4.2" fill="#fff"/>` +
      `<circle cx="12" cy="8.4" r="2.3" fill="#fff"/>` +
      `<g fill="none" stroke="#fff" stroke-width="1.2" stroke-linecap="round">` +
      `<path d="M5.6 11.4h2.6M5.6 14.1h2.6M6 16.8l2.2-1.1M15.8 11.4h2.6M15.8 14.1h2.6M15.8 15.7l2.2 1.1M10.4 6.6 9.1 4.9M13.6 6.6l1.3-1.7"/>` +
      `</g>`,
  },
  niko_partner: {
    label: "Partner",
    color: "#1abc9c",
    // Two linked rings: Niko and the partner server. Fatter and barely
    // overlapping, because the old thin pair read as one small blob once the
    // badge was drawn at 20 pixels.
    glyph: () =>
      `<circle cx="9.2" cy="12" r="4" fill="none" stroke="#fff" stroke-width="1.9"/>` +
      `<circle cx="14.8" cy="12" r="4" fill="none" stroke="#fff" stroke-width="1.9"/>`,
  },
};

/** Emoji name in src/config/emojis.py -> badge SVG, relative to web/public/assets. */
const EMOJI_ART = {
  // Discord profile badges Niko had no emoji art for. The SVGs in
  // web/public/assets are the bare glyphs the popups draw, so these are the
  // badges the bot card used to show as a unicode fallback or an unrelated
  // emoji. Badges Discord's own art already covers in src/assets/emojis
  // (partner, the HypeSquad houses, the developer badges) are deliberately not
  // rasterised here: replacing that art with a bare glyph would be a downgrade.
  staff_badge: "badges/staff.svg",
  bug_hunter_badge: "badges/bug_hunter_level_1.svg",
  bug_hunter_gold_badge: "badges/bug_hunter_level_2.svg",
  hypesquad_events: "hypesquad/events.svg",
  early_supporter_badge: "badges/early_supporter.svg",
  certified_moderator_badge: "badges/certified_moderator.svg",
  supports_commands_badge: "badges/supports_commands.svg",
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

function badgeSvg(label, color, glyph, { scale, nudge } = {}) {
  const transforms = [];
  if (nudge) transforms.push(`translate(${nudge[0]} ${nudge[1]})`);
  if (scale) transforms.push(`translate(12 12) scale(${scale}) translate(-12 -12)`);
  const body = transforms.length
    ? `<g transform="${transforms.join(" ")}">${glyph}</g>`
    : glyph;
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
  for (const [key, { label, color, glyph, scale, nudge }] of Object.entries(NIKO_BADGES)) {
    const file = path.join(PUBLIC_ASSETS, "badges", `${key}.svg`);
    await writeFile(file, badgeSvg(label, color, glyph(color), { scale, nudge }), "utf-8");
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
