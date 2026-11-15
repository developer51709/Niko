import { parseChangelogEntry, sortChangelog, type ChangelogEntry } from "../content/changelog/schema";

export type { ChangelogChart, ChangelogDatum, ChangelogEntry } from "../content/changelog/schema";

/**
 * The changelog, assembled from `web/src/content/changelog/*.json`.
 *
 * One file per release, named after its slug. Adding a release means adding a
 * file: there is no index to update, and the build reads the same folder. The
 * entry shape and its validation live in `content/changelog/schema.ts`.
 */
const entries = import.meta.glob<unknown>("../content/changelog/*.json", {
  eager: true,
  query: "?json",
  import: "default",
});

export const CHANGELOG: ChangelogEntry[] = sortChangelog(
  Object.entries(entries).map(([filename, value]) => parseChangelogEntry(value, filename)),
);

export function getChangelogBySlug(slug: string): ChangelogEntry | undefined {
  return CHANGELOG.find((entry) => entry.slug === slug);
}

export function getChangelogTags(): string[] {
  const tags = new Set<string>();
  CHANGELOG.forEach((entry) => entry.tags.forEach((tag) => tags.add(tag)));
  return Array.from(tags).sort();
}
