import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Resvg } from "@resvg/resvg-js";
import * as fontkit from "fontkit";
import { CHANGELOG, type ChangelogEntry } from "./src/data/changelog";
import { DOCS } from "./src/data/docs";
import type { DocPage } from "./src/types";

const SITE_URL = "https://niko.sryze.cc";
const DEFAULT_DESCRIPTION = "Niko is the warm, capable Discord companion for communities that care.";

type PageMetadata = { path: string; title: string; description: string; section: string };

function escapeHtml(value: string) {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;").replace(/'/g, "&#39;");
}

function metadataForDoc(doc: DocPage): PageMetadata {
  return { path: `/docs/${doc.slug}`, title: `${doc.title} — Niko docs`, description: doc.excerpt, section: "Documentation" };
}

function metadataForChangelog(entry: ChangelogEntry): PageMetadata {
  return { path: `/changelog/${entry.slug}`, title: `${entry.title} — Niko changelog`, description: entry.summary, section: entry.version ? `Changelog · v${entry.version}` : "Changelog" };
}

const PAGE_METADATA: PageMetadata[] = [
  { path: "/", title: "Niko — Discord companion", description: DEFAULT_DESCRIPTION, section: "Discord companion" },
  { path: "/commands", title: "Commands — Niko", description: "Browse every slash, prefix, hybrid, and context command available in Niko.", section: "Command reference" },
  { path: "/team", title: "Team — Niko", description: "Meet the owners, developers, moderators, support staff, and creatives behind Niko.", section: "Niko team" },
  { path: "/support", title: "Support — Niko", description: "Find answers, browse Niko documentation, and connect with the community for help.", section: "Niko support" },
  { path: "/discord", title: "Niko support server", description: "Join the official Niko Discord support server for help, community updates, and feedback.", section: "Join the community" },
  { path: "/docs", title: "Documentation — Niko", description: "Guides, command references, and practical tips for getting the most out of Niko.", section: "Documentation center" },
  { path: "/changelog", title: "Changelog — Niko", description: "A clear record of every improvement, fix, and new feature added to Niko.", section: "What's new" },
  { path: "/privacy", title: "Privacy policy — Niko", description: "Learn what information Niko uses and how it supports Discord communities.", section: "Niko legal" },
  { path: "/terms", title: "Terms of service — Niko", description: "The terms that apply when you use Niko in a Discord server.", section: "Niko legal" },
  { path: "/community", title: "Community policy — Niko", description: "The community expectations for every server using Niko.", section: "Niko legal" },
  ...DOCS.map(metadataForDoc),
  ...CHANGELOG.map(metadataForChangelog),
];

function createOgCardSvg(metadata: PageMetadata) {
  const title = escapeHtml(metadata.title.replace(/ — Niko( docs| changelog)?$/, ""));
  const descriptionWords = metadata.description.slice(0, 160).split(/\s+/);
  const descriptionLines: string[] = [];
  let descriptionLine = "";
  for (const word of descriptionWords) {
    if (`${descriptionLine} ${word}`.trim().length > 58) {
      descriptionLines.push(descriptionLine);
      descriptionLine = word;
    } else {
      descriptionLine = `${descriptionLine} ${word}`.trim();
    }
  }
  if (descriptionLine) descriptionLines.push(descriptionLine);
  const descriptionSvg = descriptionLines.slice(0, 3).map((line, index) => `<text x="72" y="${360 + index * 34}" fill="#c8c1b8" font-family="Inter,sans-serif" font-size="24">${escapeHtml(line)}</text>`).join("");
  const section = escapeHtml(metadata.section.toUpperCase());
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#17181a"/><stop offset="1" stop-color="#33251f"/></linearGradient><pattern id="grid" width="42" height="42" patternUnits="userSpaceOnUse"><path d="M42 0H0V42" fill="none" stroke="#f4f0e9" stroke-opacity=".06"/></pattern></defs>
  <rect width="1200" height="630" fill="url(#bg)"/><rect width="1200" height="630" fill="url(#grid)"/><circle cx="1040" cy="-30" r="260" fill="#d96545" fill-opacity=".18"/><circle cx="1080" cy="20" r="150" fill="#d96545" fill-opacity=".14"/>
  <rect x="72" y="72" width="58" height="58" rx="14" fill="#d96545"/><text x="101" y="112" text-anchor="middle" fill="#fffaf5" font-family="Inter,sans-serif" font-size="32" font-weight="700">N</text>
  <text x="72" y="190" fill="#d9957f" font-family="Inter,sans-serif" font-size="20" font-weight="700" letter-spacing="4">${section}</text>
  <text x="72" y="285" fill="#f4f0e9" font-family="Inter,sans-serif" font-size="58" font-weight="700">${title}</text>
  ${descriptionSvg}
  <text x="72" y="555" fill="#8c918e" font-family="Inter,sans-serif" font-size="18">NIKO.SRYZE.CC</text><text x="1128" y="555" text-anchor="end" fill="#d96545" font-family="Inter,sans-serif" font-size="18">NIKO</text>
</svg>`;
}

function createRasterTextPaths(metadata: PageMetadata, fontRoot: string) {
  const regular = fontkit.create(fs.readFileSync(path.join(fontRoot, "inter-latin-400-normal.woff")));
  const bold = fontkit.create(fs.readFileSync(path.join(fontRoot, "inter-latin-700-normal.woff")));
  const pathForText = (font: any, text: string, x: number, baseline: number, size: number, fill: string, anchor: "start" | "middle" | "end" = "start") => {
    const run = font.layout(text);
    const scale = size / font.unitsPerEm;
    const width = run.glyphs.reduce((total: number, glyph: any, index: number) => total + (run.positions[index]?.xAdvance || glyph.advanceWidth) * scale, 0);
    let cursor = anchor === "middle" ? x - width / 2 : anchor === "end" ? x - width : x;
    return run.glyphs.map((glyph: any, index: number) => {
      const d = glyph.path.toSVG();
      const advance = (run.positions[index]?.xAdvance || glyph.advanceWidth) * scale;
      const result = `<path d="${d}" transform="translate(${cursor} ${baseline}) scale(${scale} ${-scale})" fill="${fill}"/>`;
      cursor += advance;
      return result;
    }).join("");
  };
  const title = metadata.title.replace(/ — Niko( docs| changelog)?$/, "");
  const section = metadata.section.toUpperCase();
  const words = metadata.description.slice(0, 160).split(" ").filter(Boolean);
  const lines: string[] = [];
  let line = "";
  for (const word of words) {
    if (`${line} ${word}`.trim().length > 58) { lines.push(line); line = word; }
    else line = `${line} ${word}`.trim();
  }
  if (line) lines.push(line);
  return [
    pathForText(bold, "N", 101, 112, 32, "#fffaf5", "middle"),
    pathForText(bold, section, 72, 190, 20, "#d9957f"),
    pathForText(bold, title, 72, 285, 58, "#f4f0e9"),
    ...lines.slice(0, 3).map((value, index) => pathForText(regular, value, 72, 360 + index * 34, 24, "#c8c1b8")),
    pathForText(regular, "NIKO.SRYZE.CC", 72, 555, 18, "#8c918e"),
    pathForText(regular, "NIKO", 1128, 555, 18, "#d96545", "end"),
  ].join("");
}

function staticMetadataPlugin(): Plugin {
  return {
    name: "niko-static-social-metadata",
    async closeBundle() {
      const dist = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "../src/website/dist");
      const shell = fs.readFileSync(path.join(dist, "index.html"), "utf8");
      for (const metadata of PAGE_METADATA) {
        const route = metadata.path === "/" ? "" : metadata.path.slice(1);
        const htmlPath = path.join(dist, route, "index.html");
        const assetPath = route || "home";
        const svgPath = path.join(dist, "og", `${assetPath}.svg`);
        const pngPath = path.join(dist, "og", `${assetPath}.png`);
        const canonical = `${SITE_URL}${metadata.path}`;
        const image = `${SITE_URL}/og/${assetPath}.png`;
        const tags = `<link rel="icon" type="image/svg+xml" href="${SITE_URL}/favicon.svg" /><title>${escapeHtml(metadata.title)}</title><meta name="description" content="${escapeHtml(metadata.description)}" /><link rel="canonical" href="${canonical}" /><meta property="og:type" content="website" /><meta property="og:url" content="${canonical}" /><meta property="og:title" content="${escapeHtml(metadata.title)}" /><meta property="og:description" content="${escapeHtml(metadata.description)}" /><meta property="og:image" content="${escapeHtml(image)}" /><meta property="og:image:width" content="1200" /><meta property="og:image:height" content="630" /><meta name="twitter:card" content="summary_large_image" /><meta name="twitter:title" content="${escapeHtml(metadata.title)}" /><meta name="twitter:description" content="${escapeHtml(metadata.description)}" /><meta name="twitter:image" content="${escapeHtml(image)}" />`;
        const generated = shell.replace(/<meta name="description"[\s\S]*?<title>.*?<\/title>/, tags);
        const svg = createOgCardSvg(metadata);
        fs.mkdirSync(path.dirname(htmlPath), { recursive: true });
        fs.mkdirSync(path.dirname(svgPath), { recursive: true });
        fs.writeFileSync(htmlPath, generated);
        fs.writeFileSync(svgPath, svg);
        const fontRoot = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "../node_modules/@fontsource/inter/files");
        // Remove native SVG text before adding outlined glyph paths so the PNG
        // contains each label only once. The SVG card retains its native text.
        const rasterSvg = svg
          .replace(/<text[^>]*>.*?<\/text>/gs, "")
          .replace("</svg>", `${createRasterTextPaths(metadata, fontRoot)}</svg>`);
        const raster = new Resvg(rasterSvg, {
          fitTo: { mode: "width", value: 1200 },
        }).render();
        fs.writeFileSync(pngPath, raster.asPng());
      }
    },
  };
}

export default defineConfig({
  root: "web",
  plugins: [react(), staticMetadataPlugin()],
  server: { host: "0.0.0.0", port: 5000, allowedHosts: true },
  build: { outDir: "../src/website/dist", emptyOutDir: true },
});
