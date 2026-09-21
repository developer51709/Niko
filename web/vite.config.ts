import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
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
  const description = escapeHtml(metadata.description.slice(0, 160));
  const section = escapeHtml(metadata.section.toUpperCase());
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#17181a"/><stop offset="1" stop-color="#33251f"/></linearGradient><pattern id="grid" width="42" height="42" patternUnits="userSpaceOnUse"><path d="M42 0H0V42" fill="none" stroke="#f4f0e9" stroke-opacity=".06"/></pattern></defs>
  <rect width="1200" height="630" fill="url(#bg)"/><rect width="1200" height="630" fill="url(#grid)"/><circle cx="1040" cy="-30" r="260" fill="#d96545" fill-opacity=".18"/><circle cx="1080" cy="20" r="150" fill="#d96545" fill-opacity=".14"/>
  <rect x="72" y="72" width="58" height="58" rx="14" fill="#d96545"/><text x="101" y="112" text-anchor="middle" fill="#fffaf5" font-family="Arial,sans-serif" font-size="32" font-weight="700">N</text>
  <text x="72" y="190" fill="#d9957f" font-family="Arial,sans-serif" font-size="20" font-weight="700" letter-spacing="4">${section}</text>
  <text x="72" y="285" fill="#f4f0e9" font-family="Arial,sans-serif" font-size="58" font-weight="700">${title}</text>
  <foreignObject x="72" y="330" width="800" height="100"><div xmlns="http://www.w3.org/1999/xhtml" style="color:#c8c1b8;font:24px Arial,sans-serif;line-height:1.4">${description}</div></foreignObject>
  <text x="72" y="555" fill="#8c918e" font-family="monospace" font-size="18">NIKO.SRYZE.CC</text><text x="1128" y="555" text-anchor="end" fill="#d96545" font-family="monospace" font-size="18">NIKO</text>
</svg>`;
}

function staticMetadataPlugin(): Plugin {
  return {
    name: "niko-static-social-metadata",
    closeBundle() {
      const dist = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "../src/website/dist");
      const shell = fs.readFileSync(path.join(dist, "index.html"), "utf8");
      for (const metadata of PAGE_METADATA) {
        const route = metadata.path === "/" ? "" : metadata.path.slice(1);
        const htmlPath = path.join(dist, route, "index.html");
        const imagePath = path.join(dist, "og", `${route || "home"}.svg`);
        const canonical = `${SITE_URL}${metadata.path}`;
        const sourceImage = `${SITE_URL}/og/${route || "home"}.svg`;
        const image = `https://wsrv.nl/?url=${encodeURIComponent(sourceImage)}&output=png`;
        const tags = `<title>${escapeHtml(metadata.title)}</title><meta name="description" content="${escapeHtml(metadata.description)}" /><link rel="canonical" href="${canonical}" /><meta property="og:type" content="website" /><meta property="og:url" content="${canonical}" /><meta property="og:title" content="${escapeHtml(metadata.title)}" /><meta property="og:description" content="${escapeHtml(metadata.description)}" /><meta property="og:image" content="${escapeHtml(image)}" /><meta property="og:image:width" content="1200" /><meta property="og:image:height" content="630" /><meta name="twitter:card" content="summary_large_image" /><meta name="twitter:title" content="${escapeHtml(metadata.title)}" /><meta name="twitter:description" content="${escapeHtml(metadata.description)}" /><meta name="twitter:image" content="${escapeHtml(image)}" />`;
        const generated = shell.replace(/<meta name="description"[\s\S]*?<title>.*?<\/title>/, tags);
        fs.mkdirSync(path.dirname(htmlPath), { recursive: true });
        fs.mkdirSync(path.dirname(imagePath), { recursive: true });
        fs.writeFileSync(htmlPath, generated);
        fs.writeFileSync(imagePath, createOgCardSvg(metadata));
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
