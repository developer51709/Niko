/**
 * Generates the website favicon and the PWA app icons from one vector mark.
 *
 *   1. Writes the shared app mark to web/public/niko-app-icon.svg
 *   2. Writes the favicon as favicon.svg plus a 32px PNG fallback
 *   3. Rasterises the mark into web/public/icons/:
 *        niko-192.png            "any" launcher/shortcut icon
 *        niko-512.png            "any" store/splash icon
 *        niko-maskable-512.png   full-bleed art for Android's maskable crop
 *        apple-touch-icon.png    opaque 180px icon iOS uses on the home screen
 *
 * The monogram sits well inside the 80% maskable safe zone, so a circle or
 * squircle crop never clips it. The package's `prebuild` hook runs this script,
 * so the icons are never hand-exported and can never drift from the mark the
 * site and render lab draw.
 *
 * Run it directly with:
 *
 *     node scripts/generate_site_icons.mjs
 */

import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const ROOT = path.resolve(import.meta.dirname, "..");
const PUBLIC_DIR = path.join(ROOT, "web", "public");
const ICON_DIR = path.join(PUBLIC_DIR, "icons");
// The built website is committed and served by Flask, so the icons are mirrored
// into it too: the running bot serves the new artwork before the next full
// build, exactly as the ticket banner does.
const MIRROR_DIR = path.join(ROOT, "src", "website", "dist");

// Niko's brand mark: a terracotta tile carrying a cream "N".
const TILE = "#d96545";
const GLYPH = "#fffaf5";
const GLYPH_PATH = "M137 368V144h53l132 143V144h53v224h-51L190 222v146z";
const TILE_RADIUS = 112;

/** The mark as SVG. `radius` 0 gives a full-bleed square for iOS and maskable use. */
function appMarkSvg(radius) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <title>Niko</title>
  <rect width="512" height="512" rx="${radius}" fill="${TILE}"/>
  <path fill="${GLYPH}" d="${GLYPH_PATH}"/>
</svg>
`;
}

const FAVICON_SVG = appMarkSvg(TILE_RADIUS);
const BLEED_SVG = appMarkSvg(0);

/** Rasterise at high density, then scale down so every edge stays smooth. */
function renderPng(svg, size) {
  return sharp(Buffer.from(svg), { density: 384 })
    .resize(size, size)
    .png({ compressionLevel: 9 })
    .toBuffer();
}

const ICONS = [
  { name: "niko-192.png", size: 192, svg: FAVICON_SVG },
  { name: "niko-512.png", size: 512, svg: FAVICON_SVG },
  { name: "niko-maskable-512.png", size: 512, svg: BLEED_SVG },
  { name: "apple-touch-icon.png", size: 180, svg: BLEED_SVG },
];
const ROOT_ICONS = [{ name: "favicon-32.png", size: 32, svg: FAVICON_SVG }];

async function writeEverywhere(targets, contents) {
  for (const target of targets) {
    await mkdir(path.dirname(target), { recursive: true });
    await writeFile(target, contents);
  }
}

// The favicon and the mark the render lab uses are the same artwork in two
// places, so a browser tab and an in-app guild icon always agree.
for (const name of ["favicon.svg", "niko-app-icon.svg"]) {
  await writeEverywhere([path.join(PUBLIC_DIR, name), path.join(MIRROR_DIR, name)], FAVICON_SVG);
}

for (const icon of [...ICONS, ...ROOT_ICONS]) {
  const png = await renderPng(icon.svg, icon.size);
  const directory = ICONS.includes(icon) ? ICON_DIR : PUBLIC_DIR;
  const mirrorDirectory = ICONS.includes(icon) ? path.join(MIRROR_DIR, "icons") : MIRROR_DIR;
  await writeEverywhere([path.join(directory, icon.name), path.join(mirrorDirectory, icon.name)], png);
  console.log(`  ${icon.name.padEnd(24)} ${icon.size}x${icon.size}`);
}

console.log(`Wrote the favicon and ${ICONS.length + ROOT_ICONS.length} PNG icons.`);
