/**
 * The shape of one changelog entry, plus the checks a new entry has to pass.
 *
 * Entries live as one JSON file each in `web/src/content/changelog/`, named
 * after their slug. Nothing keeps a list of them: the dashboard globs the
 * folder and the build reads the same folder, so adding a release means adding
 * a file.
 *
 * A new entry needs `slug`, `title`, `date`, `tags`, `summary`, `highlights`
 * and `changes`. `version`, `chart` and `commits` are optional.
 */

export type ChangelogDatum = {
  label: string;
  value: number;
  color?: string;
};

export type ChangelogChart =
  | { type: "bar"; title: string; data: ChangelogDatum[] }
  | { type: "pie"; title: string; data: ChangelogDatum[] }
  | { type: "line"; title: string; data: (ChangelogDatum & { detail?: string })[] }
  | { type: "timeline"; title: string; data: (ChangelogDatum & { detail?: string })[] }
  | {
      type: "donut";
      title: string;
      data: ChangelogDatum[];
      centerLabel?: string;
    }
  | {
      type: "comparison";
      title: string;
      before: ChangelogDatum[];
      after: ChangelogDatum[];
    }
  | {
      type: "metrics";
      title: string;
      data: { label: string; value: string; detail?: string; color?: string }[];
    };

export const CHANGE_CATEGORIES = ["added", "improved", "fixed", "migrated"] as const;

export type ChangelogChangeCategory = (typeof CHANGE_CATEGORIES)[number];

export type ChangelogEntry = {
  slug: string;
  title: string;
  date: string;
  version?: string;
  tags: string[];
  summary: string;
  highlights: {
    title: string;
    description: string;
    icon: string;
  }[];
  changes: {
    category: ChangelogChangeCategory;
    items: string[];
  }[];
  chart?: ChangelogChart;
  commits: string[];
};

const CHART_TYPES = ["bar", "pie", "line", "timeline", "donut", "comparison", "metrics"] as const;

const SLUG_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

function invalid(source: string, message: string): never {
  throw new Error(`Invalid changelog entry in ${source}: ${message}`);
}

function isText(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function textField(entry: Record<string, unknown>, key: string, source: string): string {
  const value = entry[key];
  if (!isText(value)) invalid(source, `"${key}" must be a non-empty string`);
  return value;
}

function textList(value: unknown, key: string, source: string): string[] {
  if (!Array.isArray(value) || !value.every(isText)) {
    invalid(source, `"${key}" must be a list of non-empty strings`);
  }
  return value;
}

function validateChart(value: unknown, source: string): ChangelogChart {
  if (!value || typeof value !== "object") invalid(source, `"chart" must be an object`);
  const chart = value as Record<string, unknown>;
  const type = chart.type;
  if (typeof type !== "string" || !(CHART_TYPES as readonly string[]).includes(type)) {
    invalid(source, `"chart.type" must be one of ${CHART_TYPES.join(", ")}`);
  }
  if (!isText(chart.title)) invalid(source, `"chart.title" must be a non-empty string`);
  if (type === "comparison") {
    if (!Array.isArray(chart.before) || !Array.isArray(chart.after)) {
      invalid(source, `a comparison chart needs "before" and "after" lists`);
    }
  } else if (!Array.isArray(chart.data)) {
    invalid(source, `"chart.data" must be a list`);
  }
  return chart as unknown as ChangelogChart;
}

/**
 * Validate one entry read from disk and return it as a `ChangelogEntry`.
 *
 * `source` is the file name; it is checked against the slug so the folder stays
 * the index and a renamed file cannot silently change the public URL.
 */
export function parseChangelogEntry(value: unknown, source: string): ChangelogEntry {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    invalid(source, "expected an object");
  }
  const entry = value as Record<string, unknown>;

  const slug = textField(entry, "slug", source);
  if (!SLUG_PATTERN.test(slug)) {
    invalid(source, `"slug" must be lowercase words separated by dashes`);
  }
  const filename = source.split(/[\\/]/).pop() ?? source;
  if (filename.endsWith(".json") && filename !== `${slug}.json`) {
    invalid(source, `the file must be named "${slug}.json" to match its slug`);
  }

  const title = textField(entry, "title", source);
  const date = textField(entry, "date", source);
  if (!DATE_PATTERN.test(date)) invalid(source, `"date" must be YYYY-MM-DD`);

  let version: string | undefined;
  if (entry.version !== undefined) {
    if (!isText(entry.version)) invalid(source, `"version" must be a non-empty string`);
    version = entry.version;
  }

  const summary = textField(entry, "summary", source);
  const tags = textList(entry.tags, "tags", source);

  if (!Array.isArray(entry.highlights)) invalid(source, `"highlights" must be a list`);
  const highlights = entry.highlights.map((highlight, index) => {
    if (!highlight || typeof highlight !== "object") {
      invalid(source, `"highlights[${index}]" must be an object`);
    }
    const item = highlight as Record<string, unknown>;
    return {
      title: textField(item, "title", source),
      description: textField(item, "description", source),
      icon: textField(item, "icon", source),
    };
  });

  if (!Array.isArray(entry.changes)) invalid(source, `"changes" must be a list`);
  const changes = entry.changes.map((change, index) => {
    if (!change || typeof change !== "object") {
      invalid(source, `"changes[${index}]" must be an object`);
    }
    const group = change as Record<string, unknown>;
    if (
      typeof group.category !== "string"
      || !(CHANGE_CATEGORIES as readonly string[]).includes(group.category)
    ) {
      invalid(source, `"changes[${index}].category" must be one of ${CHANGE_CATEGORIES.join(", ")}`);
    }
    return {
      category: group.category as ChangelogChangeCategory,
      items: Array.isArray(group.items) ? textList(group.items, `changes[${index}].items`, source) : [],
    };
  });

  const chart = entry.chart === undefined ? undefined : validateChart(entry.chart, source);
  const commits = entry.commits === undefined ? [] : textList(entry.commits, "commits", source);

  return {
    slug,
    title,
    date,
    ...(version ? { version } : {}),
    tags,
    summary,
    highlights,
    changes,
    ...(chart ? { chart } : {}),
    commits,
  };
}

/** Compare two dotted versions so a newer release sorts first. */
function compareVersions(left: string | undefined, right: string | undefined): number {
  if (!left && !right) return 0;
  // A release without a version number sorts after versioned ones on its day.
  if (!left) return 1;
  if (!right) return -1;
  const leftParts = left.split(".").map((part) => Number.parseInt(part, 10) || 0);
  const rightParts = right.split(".").map((part) => Number.parseInt(part, 10) || 0);
  for (let index = 0; index < Math.max(leftParts.length, rightParts.length); index += 1) {
    const difference = (rightParts[index] ?? 0) - (leftParts[index] ?? 0);
    if (difference !== 0) return difference;
  }
  return 0;
}

/**
 * Newest first: by date, then by version for releases sharing a day, then by
 * slug so the order never depends on how the files are read from disk.
 */
export function sortChangelog(entries: ChangelogEntry[]): ChangelogEntry[] {
  return [...entries].sort(
    (left, right) =>
      right.date.localeCompare(left.date)
      || compareVersions(left.version, right.version)
      || left.slug.localeCompare(right.slug),
  );
}
