import type { DocPage, DocCategory, DocSection } from "../types";

const docModules = import.meta.glob<string>("../content/docs/*.mdx", {
  eager: true,
  query: "?raw",
  import: "default",
});

function parseDoc(source: string, filename: string): DocPage {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) throw new Error(`Invalid MDX frontmatter in ${filename}`);
  const metadata = new Map<string, string>();
  for (const line of match[1].split(/\r?\n/)) {
    const field = line.match(/^([a-z_]+):\s*(.*)$/);
    if (field) metadata.set(field[1], field[2]);
  }
  const readString = (key: string) => {
    const value = metadata.get(key);
    if (!value) throw new Error(`Missing ${key} in ${filename}`);
    return JSON.parse(value) as string;
  };
  const tagsValue = metadata.get("tags");
  const orderValue = metadata.get("order");
  if (!tagsValue || !orderValue) throw new Error(`Missing tags or order in ${filename}`);
  return {
    slug: readString("slug"),
    title: readString("title"),
    category: readString("category") as DocCategory,
    excerpt: readString("excerpt"),
    tags: JSON.parse(tagsValue) as string[],
    order: Number(orderValue),
    content: match[2].trim(),
  };
}

export const DOCS: DocPage[] = Object.entries(docModules)
  .map(([filename, source]) => parseDoc(source, filename))
  .sort((a, b) => a.category.localeCompare(b.category) || a.order - b.order || a.slug.localeCompare(b.slug));

export function getDocBySlug(slug: string): DocPage | undefined {
  return DOCS.find((doc) => doc.slug === slug);
}

export function getDocsByCategory(category: DocCategory): DocPage[] {
  return DOCS.filter((doc) => doc.category === category).sort((a, b) => a.order - b.order);
}

export function getAllCategories(): DocCategory[] {
  const cats = new Set<DocCategory>();
  DOCS.forEach((doc) => cats.add(doc.category));
  return Array.from(cats);
}

export const DOC_SECTIONS: DocSection[] = [
  { id: "getting-started", label: "Getting Started", description: "New to Niko? Start here.", icon: "icon_home", count: DOCS.filter((d) => d.category === "getting-started").length },
  { id: "setup", label: "Setup", description: "Configure Niko for your server.", icon: "icon_settings", count: DOCS.filter((d) => d.category === "setup").length },
  { id: "economy", label: "Economy", description: "Money, jobs, banking, and more.", icon: "icon_economy", count: DOCS.filter((d) => d.category === "economy").length },
  { id: "leveling", label: "Leveling", description: "XP, levels, and rankings.", icon: "icon_leveling", count: DOCS.filter((d) => d.category === "leveling").length },
  { id: "moderation", label: "Moderation", description: "Moderation tools and commands.", icon: "icon_moderation", count: DOCS.filter((d) => d.category === "moderation").length },
  { id: "automod", label: "AutoMod", description: "Automated moderation features.", icon: "icon_automod", count: DOCS.filter((d) => d.category === "automod").length },
  { id: "logging", label: "Logging", description: "Server event logging.", icon: "icon_settings", count: DOCS.filter((d) => d.category === "logging").length },
  { id: "social", label: "Social", description: "Community engagement features.", icon: "icon_heart", count: DOCS.filter((d) => d.category === "social").length },
  { id: "utility", label: "Utility", description: "Helpful tools and utilities.", icon: "icon_utility", count: DOCS.filter((d) => d.category === "utility").length },
  { id: "voice", label: "Voice", description: "Voice and music features.", icon: "icon_bot", count: DOCS.filter((d) => d.category === "voice").length },
  { id: "ai", label: "AI", description: "AI-powered features.", icon: "icon_ai", count: DOCS.filter((d) => d.category === "ai").length },
  { id: "dashboard", label: "Dashboard", description: "Web dashboard guides.", icon: "icon_settings", count: DOCS.filter((d) => d.category === "dashboard").length },
  { id: "tips", label: "Tips", description: "Tips and best practices.", icon: "icon_lightbulb", count: DOCS.filter((d) => d.category === "tips").length },
];
