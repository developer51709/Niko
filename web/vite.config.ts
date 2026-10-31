import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Resvg } from "@resvg/resvg-js";
import * as fontkit from "fontkit";
import { CHANGELOG, type ChangelogEntry } from "./src/data/changelog";

const SITE_URL = "https://niko.sryze.cc";
const DOC_CONTENT_DIRECTORY = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "src/content/docs");
const DOC_FRONTMATTER_FIELD = /^([a-z_]+):\s*(.*)$/;
const DEFAULT_DESCRIPTION = "Niko is the warm, capable Discord companion for communities that care.";

// A page the backend renders a social preview, and a Discord component embed,
// for at request time. `landing` marks the pages that also advertise the live
// command, server, and member counts.
// https://docs.discord.com/developers/link-previews/component-embeds
type PageMetadata = { path: string; title: string; description: string; section: string; landing?: boolean };

function escapeHtml(value: string) {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;").replace(/'/g, "&#39;");
}

// The page list the backend renders social previews from. Discord reads the
// component embed out of the served HTML, and rendering it per request is what
// keeps the invite link and the live counts current — so the build only has to
// hand over each page's copy and the card image it uses.
// src/webapp/social_preview.py consumes this file.
function writeSocialPagesManifest(dist: string) {
  const pages = Object.fromEntries(PAGE_METADATA.map((metadata) => {
    const asset = metadata.path === "/" ? "home" : metadata.path.slice(1);
    return [metadata.path, {
      title: metadata.title,
      description: metadata.description,
      section: metadata.section,
      landing: Boolean(metadata.landing),
      image: `${SITE_URL}/og/${asset}.png`,
    }];
  }));
  fs.writeFileSync(
    path.join(dist, "social-pages.json"),
    `${JSON.stringify({ site: SITE_URL, pages }, null, 2)}\n`,
  );
}

function docsMetadata(): PageMetadata[] {
  return fs.readdirSync(DOC_CONTENT_DIRECTORY)
    .filter((file: string) => file.endsWith(".mdx"))
    .map((file: string) => {
      const source = fs.readFileSync(path.join(DOC_CONTENT_DIRECTORY, file), "utf8");
      const frontmatter = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
      if (!frontmatter) throw new Error(`Invalid MDX frontmatter in ${file}`);
      const values = new Map<string, string>();
      for (const line of frontmatter[1].split(/\r?\n/)) {
        const field = line.match(DOC_FRONTMATTER_FIELD);
        if (field) values.set(field[1], field[2]);
      }
      const slug = values.get("slug");
      const title = values.get("title");
      const excerpt = values.get("excerpt");
      if (!slug || !title || !excerpt) throw new Error(`Missing required MDX metadata in ${file}`);
      return {
        path: `/docs/${JSON.parse(slug) as string}`,
        title: `${JSON.parse(title) as string} — Niko docs`,
        description: JSON.parse(excerpt) as string,
        section: "Documentation",
      };
    });
}

function metadataForChangelog(entry: ChangelogEntry): PageMetadata {
  return { path: `/changelog/${entry.slug}`, title: `${entry.title} — Niko changelog`, description: entry.summary, section: entry.version ? `Changelog · v${entry.version}` : "Changelog" };
}

function changelogMarkdown(entry: ChangelogEntry) {
  const lines = [
    `# ${entry.title}`,
    "",
    `- Date: ${entry.date}`,
    ...(entry.version ? [`- Version: ${entry.version}`] : []),
    `- Tags: ${entry.tags.join(", ")}`,
    "",
    entry.summary,
    "",
    "## Highlights",
    ...entry.highlights.flatMap((highlight) => ["", `### ${highlight.title}`, highlight.description]),
    "",
    "## Changes",
    ...entry.changes.flatMap((group) => ["", `### ${group.category}`, ...group.items.map((item) => `- ${item}`)]),
    ...(entry.chart ? ["", "## Chart data", "", "```json", JSON.stringify(entry.chart, null, 2), "```"] : []),
    ...(entry.commits.length ? ["", "## Commits", ...entry.commits.map((commit) => `- ${commit}`)] : []),
  ];
  return `${lines.join("\n")}\n`;
}

function writeMachineReadableContent(dist: string) {
  const docLinks: string[] = [];
  for (const file of fs.readdirSync(DOC_CONTENT_DIRECTORY).filter((name: string) => name.endsWith(".mdx"))) {
    const source = fs.readFileSync(path.join(DOC_CONTENT_DIRECTORY, file), "utf8");
    const frontmatter = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
    if (!frontmatter) throw new Error(`Invalid MDX frontmatter in ${file}`);
    const values = new Map<string, string>();
    for (const line of frontmatter[1].split(/\r?\n/)) {
      const field = line.match(DOC_FRONTMATTER_FIELD);
      if (field) values.set(field[1], field[2]);
    }
    const slug = values.get("slug");
    const title = values.get("title");
    if (!slug || !title) throw new Error(`Missing required MDX metadata in ${file}`);
    const body = frontmatter[2].trim();
    const markdown = `${body.startsWith("#") ? "" : `# ${JSON.parse(title) as string}\n\n`}${body}\n`;
    const markdownPath = path.join(dist, "docs", `${JSON.parse(slug) as string}.md`);
    fs.mkdirSync(path.dirname(markdownPath), { recursive: true });
    fs.writeFileSync(markdownPath, markdown);
    docLinks.push(`- [${JSON.parse(title) as string}](https://niko.sryze.cc/docs/${JSON.parse(slug) as string}.md)`);
  }

  const changelogLinks = CHANGELOG.map((entry) => {
    const markdownPath = path.join(dist, "changelog", `${entry.slug}.md`);
    fs.mkdirSync(path.dirname(markdownPath), { recursive: true });
    fs.writeFileSync(markdownPath, changelogMarkdown(entry));
    return `- [${entry.title}](https://niko.sryze.cc/changelog/${entry.slug}.md) — ${entry.summary}`;
  });

  const index = [
    "# Niko",
    "",
    "> Niko is a Discord bot and companion for community servers. This index links to its complete public documentation and release notes in Markdown format.",
    "",
    "## Documentation",
    "",
    ...docLinks,
    "",
    "## Changelog",
    "",
    ...changelogLinks,
    "",
  ].join("\n");
  fs.writeFileSync(path.join(dist, "llms.txt"), index);
}

// `landing: true` marks the pages that pitch Niko itself — they carry the live
// command, server, and member counts in their Discord embed.
const PAGE_METADATA: PageMetadata[] = [
  { path: "/", title: "Niko — Discord companion", description: DEFAULT_DESCRIPTION, section: "Discord companion", landing: true },
  { path: "/commands", title: "Commands — Niko", description: "Browse every slash, prefix, hybrid, and context command available in Niko.", section: "Command reference", landing: true },
  { path: "/team", title: "Team — Niko", description: "Meet the owners, developers, moderators, support staff, and creatives behind Niko.", section: "Niko team" },
  { path: "/team/apply", title: "Join the Niko Team — Staff Applications", description: "Explore open staff roles and apply to help build a safer, friendlier Niko community.", section: "Staff applications" },
  { path: "/leaderboard", title: "Global Economy Leaderboard — Niko", description: "See the global Niko economy standings and discover who has earned the most coins.", section: "Global leaderboard" },
  // The base copy for a server's own board, `/levels/<id>`. The backend
  // renders that page from the server it belongs to (guild name, icon,
  // member and ranked counts), so this entry is only what non-Discord
  // clients and an unknown server see.
  { path: "/levels", title: "Server Leaderboard — Niko", description: "Live leveling standings for one Discord server, ranked by level and XP.", section: "Server leaderboard" },
  { path: "/support", title: "Support — Niko", description: "Find answers, browse Niko documentation, and connect with the community for help.", section: "Niko support", landing: true },
  { path: "/discord", title: "Niko support server", description: "Join the official Niko Discord support server for help, community updates, and feedback.", section: "Join the community", landing: true },
  // The partnership ad. Partners paste this one link; Discord renders the card
  // from the backend (``webapp/social.py``), so only its Open Graph fallback and
  // the page copy live here.
  { path: "/discord/partnership", title: "Niko partnerships", description: "Share one link and Discord renders the Niko partnership ad: what members get, what partners get, and how to apply.", section: "Partnership ad" },
  { path: "/docs", title: "Documentation — Niko", description: "Guides, command references, and practical tips for getting the most out of Niko.", section: "Documentation center" },
  { path: "/changelog", title: "Changelog — Niko", description: "A clear record of every improvement, fix, and new feature added to Niko.", section: "What's new" },
  { path: "/privacy", title: "Privacy policy — Niko", description: "Learn what information Niko uses and how it supports Discord communities.", section: "Niko legal" },
  { path: "/terms", title: "Terms of service — Niko", description: "The terms that apply when you use Niko in a Discord server.", section: "Niko legal" },
  { path: "/data-removal", title: "Data removal — Niko", description: "Request deletion of your Niko account data or a server you own, and read the strict policy that protects moderation records.", section: "Privacy" },
  { path: "/community", title: "Community policy — Niko", description: "The community expectations for every server using Niko.", section: "Niko legal" },
  ...docsMetadata(),
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
  const descriptionSvg = descriptionLines.slice(0, 3).map((line, index) => `<text x="72" y="${360 + index * 34}" fill="#b4bac3" font-family="Inter,sans-serif" font-size="24">${escapeHtml(line)}</text>`).join("");
  const section = escapeHtml(metadata.section.toUpperCase());
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#050607"/><stop offset=".58" stop-color="#0a0b0e"/><stop offset="1" stop-color="#111317"/></linearGradient><pattern id="grid" width="42" height="42" patternUnits="userSpaceOnUse"><path d="M42 0H0V42" fill="none" stroke="#dce1e8" stroke-opacity=".045"/></pattern></defs>
  <rect width="1200" height="630" fill="url(#bg)"/><rect width="1200" height="630" fill="url(#grid)"/><circle cx="1080" cy="40" r="280" fill="#aab1ba" fill-opacity=".065"/><circle cx="1080" cy="40" r="190" fill="#d5d9df" fill-opacity=".035"/><path d="M72 470H1128" stroke="#dce1e8" stroke-opacity=".12"/>
  <rect x="72" y="72" width="58" height="58" rx="17" fill="#15171b" stroke="#dce1e8" stroke-opacity=".2"/><text x="101" y="112" text-anchor="middle" fill="#f4f5f7" font-family="Inter,sans-serif" font-size="32" font-weight="700">N</text>
  <text x="72" y="190" fill="#c2c8d0" font-family="Inter,sans-serif" font-size="20" font-weight="700" letter-spacing="4">${section}</text>
  <text x="72" y="285" fill="#f4f5f7" font-family="Inter,sans-serif" font-size="58" font-weight="700">${title}</text>
  ${descriptionSvg}
  <text x="72" y="555" fill="#828994" font-family="Inter,sans-serif" font-size="18">NIKO.SRYZE.CC</text><text x="1128" y="555" text-anchor="end" fill="#aab1ba" font-family="Inter,sans-serif" font-size="18">NIKO</text>
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
    pathForText(bold, "N", 101, 112, 32, "#f4f5f7", "middle"),
    pathForText(bold, section, 72, 190, 20, "#c2c8d0"),
    pathForText(bold, title, 72, 285, 58, "#f4f5f7"),
    ...lines.slice(0, 3).map((value, index) => pathForText(regular, value, 72, 360 + index * 34, 24, "#b4bac3")),
    pathForText(regular, "NIKO.SRYZE.CC", 72, 555, 18, "#828994"),
    pathForText(regular, "NIKO", 1128, 555, 18, "#aab1ba", "end"),
  ].join("");
}

function staticMetadataPlugin(): Plugin {
  let buildStarted = false;
  let buildFailed = false;
  return {
    name: "niko-static-social-metadata",
    buildStart() {
      buildStarted = true;
    },
    buildEnd(error) {
      if (error) buildFailed = true;
    },
    async closeBundle() {
      // Rollup still runs closeBundle after a failed build. A failure before
      // Rollup starts (for example, while emptying dist) never reaches
      // buildEnd, so a missing buildStart is also treated as a failed build.
      // Generating cards there would write into a half-cleaned dist and print
      // a progress bar for work the failed build never produced.
      if (!buildStarted || buildFailed) return;
      // The favicon and every PWA icon are generated before the build by
      // scripts/generate_site_icons.mjs, so the public directory already holds
      // the final PNGs Vite copies into dist.
      const dist = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "../src/website/dist");
      writeMachineReadableContent(dist);
      // One HTML shell is served for every route and decorated per request by
      // the backend, so nothing here writes a page.
      writeSocialPagesManifest(dist);
      const totalPages = PAGE_METADATA.length;
      const progressStartedAt = Date.now();
      const colorEnabled = Boolean(process.stdout.isTTY)
        && !("NO_COLOR" in process.env)
        && process.env.TERM !== "dumb";
      const paint = (code: string, value: string) => colorEnabled ? `\u001b[${code}m${value}\u001b[0m` : value;
      const barWidth = Math.max(8, Math.min(30, (process.stdout.columns ?? 80) - 52));
      for (const [index, metadata] of PAGE_METADATA.entries()) {
        const route = metadata.path === "/" ? "" : metadata.path.slice(1);
        const assetPath = route || "home";
        const svgPath = path.join(dist, "og", `${assetPath}.svg`);
        const pngPath = path.join(dist, "og", `${assetPath}.png`);
        const svg = createOgCardSvg(metadata);
        fs.mkdirSync(path.dirname(svgPath), { recursive: true });
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
        const completed = index + 1;
        const ratio = completed / Math.max(1, totalPages);
        const percent = Math.round(ratio * 100);
        const filled = completed === totalPages
          ? barWidth
          : Math.max(1, Math.round(ratio * barWidth));
        const empty = Math.max(0, barWidth - filled);
        const elapsedMs = Date.now() - progressStartedAt;
        const elapsed = elapsedMs < 10_000 ? `${(elapsedMs / 1000).toFixed(1)}s` : `${Math.round(elapsedMs / 1000)}s`;
        const count = `${String(completed).padStart(String(totalPages).length)}/${totalPages}`;
        const plainBar = `${"#".repeat(filled)}${"-".repeat(empty)}`;
        // A sage-to-mint bar with a dim track, matching the dashboard palette
        // instead of the old cyan/green terminal defaults.
        const coloredBar = `${
          filled > 1 ? paint("38;5;115", "█".repeat(filled - 1)) : ""
        }${
          filled > 0 ? paint("1;38;5;157", "█") : ""
        }${
          empty > 0 ? paint("38;5;238", "░".repeat(empty)) : ""
        }`;
        const line = colorEnabled
          ? `${paint("38;5;245", "Open Graph cards")} ${paint("38;5;240", "[")}${coloredBar}${paint("38;5;240", "]")} ${paint("1;38;5;115", `${String(percent).padStart(3)}%`)}  ${paint("38;5;250", count)}  ${paint("38;5;238", "·")}  ${paint("38;5;245", elapsed)}`
          : `Open Graph cards [${plainBar}] ${String(percent).padStart(3)}%  ${count}  ·  ${elapsed}`;
        if (process.stdout.isTTY) {
          process.stdout.write(`\r\u001b[2K${line}`);
          if (completed === totalPages) process.stdout.write("\n");
        } else if (completed === totalPages) {
          process.stdout.write(`${line}\n`);
        }
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
