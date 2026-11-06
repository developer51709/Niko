/**
 * Site localization, one catalogue folder per page.
 *
 * Every page owns a folder under `web/src/locales/<page>/`, the way every page
 * owns a generated Open Graph card: `en.json` holds the source copy and the
 * other languages live beside it as they are translated. A folder whose
 * translation is missing simply falls back to English, so a half-translated
 * site never shows raw keys or blank text.
 *
 * A page with many sub pages — the dashboard, the staff area — puts each one's
 * copy in a subfolder (`<page>/<sub>/en.json`) and keeps only the page chrome in
 * its own file, so the files stay small enough to work in. Both levels are
 * merged into the single catalogue `useStrings("<page>")` reads.
 *
 * The bundled catalogues are only the *base*, though: while a translation pass
 * is being written on the beta instance, the live site reads the newer files
 * from `/api/locales/index.json` and `/api/locales/<page>/<lang>.json` (see
 * `webapp/locale_feed.py`). That is what makes a language appear here as soon as
 * someone starts translating it — no rebuild, no restart, no git pull. If the
 * feed is off or unreachable the bundled files answer, exactly as before.
 *
 * `shared/` is the chrome every page renders — navigation, and anything else
 * cross-page — and is always consulted after the page's own catalogue, so a page
 * can override a shared string when its own wording is better.
 *
 * The active language is chosen in this order: the owner devtools override (kept
 * in localStorage so a reload keeps it), then the browser's preferred
 * languages, then English. It is a website-only choice; the bot's Discord
 * replies keep following each guild's locale.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
  type ReactNode,
} from "react";

export type LanguageOption = { code: string; label: string };

/** Language codes are open-ended: the feed can add one before a build does. */
export type LanguageCode = string;

/**
 * The languages the build ships, used until the feed answers.
 *
 * The label is the language's own name: the picker is read by the visitor who
 * wants that language, and "Русский" is more useful to them than "Russian".
 */
export const LANGUAGES: LanguageOption[] = [
  { code: "en", label: "English" },
  { code: "de", label: "Deutsch" },
  { code: "es", label: "Español" },
  { code: "fr", label: "Français" },
  { code: "ru", label: "Русский" },
  { code: "ja", label: "日本語" },
  { code: "zh", label: "中文" },
  { code: "hi", label: "हिन्दी" },
  { code: "ar", label: "العربية" },
];

/** Where the devtools override lives; only this browser sees it. */
const STORAGE_KEY = "niko.site.language";

/** `../locales/status/en.json` and `../locales/dashboard/leveling/en.json` both
 * land in the same place: `CATALOGUES.status.en`, `CATALOGUES.dashboard.en`.
 *
 * Catalogues are read as raw text and parsed here, the same way the docs
 * pipeline reads its MDX: it keeps the file contents visible to a bad-catalogue
 * error instead of failing inside the bundler, and a typo names the file.
 */
// `**` covers both the page's own file and any subfolder below it.
const catalogueModules = import.meta.glob<string>("../locales/*/**/*.json", {
  eager: true,
  query: "?raw",
  import: "default",
});

type Catalogue = Record<string, string>;

/** Page-level files before subfolders, then alphabetically.
 *
 * The merge order has to be fixed rather than whatever order the glob returns:
 * a key defined twice resolves the same way in every build, and the page file
 * wins over a subfolder.
 */
const cataloguePaths = Object.keys(catalogueModules).sort(
  (left, right) => left.split("/").length - right.split("/").length || left.localeCompare(right),
);

const CATALOGUES: Record<string, Partial<Record<LanguageCode, Catalogue>>> = {};
for (const path of cataloguePaths) {
  const match = /locales\/([^/]+)\/(?:[^/]+\/)?([^/]+)\.json$/.exec(path);
  if (!match) continue;
  let strings: Catalogue;
  try {
    strings = JSON.parse(catalogueModules[path]) as Catalogue;
  } catch (error) {
    throw new Error(`Invalid locale catalogue ${path}: ${(error as Error).message}`);
  }
  const page = match[1];
  const language = match[2];
  const target = CATALOGUES[page] ?? (CATALOGUES[page] = {});
  target[language] = { ...(target[language] ?? {}), ...strings };
}

// ──────────────────────────────────────────────────────────────────────────────
// Live catalogues
// ──────────────────────────────────────────────────────────────────────────────

/** `/api/locales/index.json`: what exists, and the hash of every file. */
type LocaleIndex = {
  languages?: LanguageOption[];
  pages?: Record<string, { keys: number; langs: Record<string, { translated: number; hash: string }> }>;
  source?: { mode: "beta" | "local"; stale?: boolean };
};

/** How long the index is reused before asking the server again. */
const INDEX_TTL = 30_000;
const INDEX_STORAGE = "niko.locales.index";
const CATALOGUE_STORAGE = "niko.locales.";

/** The language list the picker and the browser match should use. */
let languages: LanguageOption[] = LANGUAGES;

/** Newest strings, keyed `<page>:<language>`. */
const remote: Record<string, Catalogue> = {};
/** `<page>:<language>` → hash of the file the server currently has. */
const hashes: Record<string, string> = {};
const requested = new Set<string>();

let index: LocaleIndex | null = null;
let indexAt = 0;
let indexTried = 0;
let indexPromise: Promise<LocaleIndex | null> | null = null;

let revision = 0;
const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function getRevision() {
  return revision;
}

function publish() {
  revision += 1;
  for (const listener of listeners) listener();
}

function readStorage<T>(key: string): T | null {
  try {
    const raw = window.sessionStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: unknown) {
  try {
    window.sessionStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Private mode and full quotas are allowed to just skip the cache.
  }
}

function applyIndex(document: LocaleIndex) {
  index = document;
  indexAt = Date.now();
  writeStorage(INDEX_STORAGE, { at: indexAt, document });
  if (Array.isArray(document.languages) && document.languages.length) {
    languages = document.languages.filter((entry) => entry && entry.code).map((entry) => ({
      code: entry.code,
      label: entry.label || entry.code.toUpperCase(),
    }));
  }
  for (const [page, entry] of Object.entries(document.pages ?? {})) {
    for (const [language, file] of Object.entries(entry?.langs ?? {})) {
      if (!file?.hash) continue;
      const key = `${page}:${language}`;
      const seen = hashes[key];
      hashes[key] = file.hash;
      // A page that is already on screen and whose file changed on beta is
      // fetched again straight away; everything else waits for its next visit.
      if (seen && seen !== file.hash && remote[key]) {
        requested.delete(key);
        loadCatalogue(page, language);
      }
    }
  }
  publish();
}

/** Restore the last index before React mounts, so the picker has no empty tick. */
function restoreIndex(): LocaleIndex | null {
  const stored = readStorage<{ at: number; document: LocaleIndex }>(INDEX_STORAGE);
  if (!stored?.document || !stored.at) return null;
  if (Date.now() - stored.at > INDEX_TTL) return null;
  return stored.document;
}

const restored = typeof window === "undefined" ? null : restoreIndex();
if (restored) applyIndex(restored);

function loadIndex(force = false): Promise<LocaleIndex | null> {
  if (typeof window === "undefined") return Promise.resolve(null);
  if (!force && index && Date.now() - indexAt < INDEX_TTL) return Promise.resolve(index);
  // A feed that is off or down should not be re-asked by every component that
  // renders a string; the bundled catalogues already answered.
  if (!index && !force && Date.now() - indexTried < 10_000) return Promise.resolve(null);
  if (indexPromise) return indexPromise;
  indexTried = Date.now();
  indexPromise = fetch("/api/locales/index.json", { cache: "no-store" })
    .then((response) => (response.ok ? (response.json() as Promise<LocaleIndex>) : null))
    .then((document) => {
      if (document) applyIndex(document);
      return document;
    })
    .catch(() => index)
    .finally(() => {
      indexPromise = null;
    });
  return indexPromise;
}

/** Fetch one page's catalogue if the server has a file this tab has not seen. */
function loadCatalogue(page: string, language: LanguageCode) {
  if (typeof window === "undefined") return;
  const key = `${page}:${language}`;
  if (requested.has(key)) return;
  const hash = hashes[key];
  if (!hash) return;
  requested.add(key);

  const cached = readStorage<{ hash: string; strings: Catalogue }>(`${CATALOGUE_STORAGE}${key}`);
  if (cached && cached.hash === hash && cached.strings) {
    remote[key] = cached.strings;
    publish();
    return;
  }

  fetch(`/api/locales/${page}/${language}.json`, { cache: "no-cache" })
    .then((response) => (response.ok ? (response.json() as Promise<Catalogue>) : null))
    .then((strings) => {
      if (!strings) return;
      remote[key] = strings;
      writeStorage(`${CATALOGUE_STORAGE}${key}`, { hash, strings });
      publish();
    })
    .catch(() => {
      // The bundled catalogue already answered; this is only the newer copy.
    });
}

/**
 * Trigger the feed for one page and subscribe to it.
 *
 * Both `useStrings` and `usePageTitle` go through here, so a page with no visible
 * copy of its own still gets its translated title.
 */
function useCatalogue(page: string) {
  const { language } = useLanguage();
  const revision = useSyncExternalStore(subscribe, getRevision, getRevision);

  useEffect(() => {
    let live = true;
    void loadIndex().then(() => {
      if (live) loadCatalogue(page, language);
    });
    return () => {
      live = false;
    };
  }, [page, language]);

  return { language, revision };
}

/**
 * The signature of the `t` a page gets from `useStrings`.
 *
 * Views that hand their translate function to a helper (a formatter, a nested
 * row component) import this instead of restating the shape.
 */
export type Translate = (key: string, values?: Record<string, string | number>) => string;

function interpolate(template: string, values: Record<string, string | number>) {
  return template.replace(/\{(\w+)\}/g, (whole, key: string) =>
    key in values ? String(values[key]) : whole,
  );
}

type LanguageContextValue = {
  language: LanguageCode;
  /** Every language with a catalogue, from the feed when it has one. */
  languages: LanguageOption[];
  /** What the browser asked for, shown in devtools next to the override. */
  browser: LanguageCode;
  /** True while the owner devtools override is active. */
  overridden: boolean;
  setLanguage: (language: LanguageCode) => void;
  resetLanguage: () => void;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

/** Map `de-DE`, `fr_CA`, … onto a language that has a catalogue, or null. */
function matchLanguage(tag: string | null | undefined, available: LanguageOption[]): LanguageCode | null {
  const code = String(tag ?? "").toLowerCase().split("-")[0];
  return available.some((entry) => entry.code === code) ? code : null;
}

function browserTags(): string[] {
  if (typeof navigator === "undefined") return [];
  return navigator.languages?.length ? [...navigator.languages] : [navigator.language];
}

function storedLanguage(): LanguageCode | null {
  try {
    return window.localStorage.getItem(STORAGE_KEY) || null;
  } catch {
    // Storage can be blocked; the browser default is still a good answer.
    return null;
  }
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [tags] = useState(browserTags);
  const [override, setOverride] = useState<LanguageCode | null>(storedLanguage);
  const revision = useSyncExternalStore(subscribe, getRevision, getRevision);

  // Ask for the index once per tab: it carries the language list and the hashes
  // the first page needs.
  useEffect(() => {
    void loadIndex();
  }, []);

  const available = useMemo(() => languages, [revision]);
  const browser = useMemo(() => {
    for (const tag of tags) {
      const code = matchLanguage(tag, available);
      if (code) return code;
    }
    return "en";
  }, [tags, available]);
  const language = override ?? browser;

  // The document language drives hyphenation, screen-reader voice, and
  // `:lang()` styling, so it follows the same choice the copy does.
  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const setLanguage = useCallback((next: LanguageCode) => {
    setOverride(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Nothing to recover from: the provider still holds the choice.
    }
  }, []);

  const resetLanguage = useCallback(() => {
    setOverride(null);
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Same as above.
    }
  }, []);

  const value = useMemo<LanguageContextValue>(
    () => ({ language, languages: available, browser, overridden: override !== null && override !== browser, setLanguage, resetLanguage }),
    [language, available, browser, override, setLanguage, resetLanguage],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageContextValue {
  const value = useContext(LanguageContext);
  if (!value) throw new Error("useLanguage must be used inside <LanguageProvider>.");
  return value;
}

/**
 * Strings for one page, in the active language.
 *
 * `t("nav.home")` reads the page catalogue first, then `shared`, then the
 * English fallback of each; an unknown key returns the key itself, which makes a
 * missing string obvious in development instead of silently empty.
 *
 * The catalogue starts as the bundled one and the feed's newer file is laid over
 * it the moment it arrives, so a translation written on beta shows up on the
 * next navigation without a deploy — and a feed that answers with only part of
 * a page can never make the rest of it fall back to raw keys.
 */
export function useStrings(page: string) {
  const { language, revision } = useCatalogue(page);

  return useMemo(() => {
    const key = `${page}:${language}`;
    // Overlay, never replace: the feed is allowed to be newer, but it is served
    // by another machine and may be a partial file — a page split across locale
    // subfolders is merged server-side, and an older server answers with only
    // the page's own chrome. Keys the feed does not carry keep their bundled
    // copy, so the worst case is yesterday's wording instead of raw keys.
    const own = { ...(CATALOGUES[page]?.[language] ?? {}), ...(remote[key] ?? {}) };
    const ownEnglish = { ...(CATALOGUES[page]?.en ?? {}), ...(remote[`${page}:en`] ?? {}) };
    const shared = page === "shared" ? {} : { ...(CATALOGUES.shared?.[language] ?? {}), ...(remote[`shared:${language}`] ?? {}) };
    const sharedEnglish = page === "shared" ? {} : { ...(CATALOGUES.shared?.en ?? {}), ...(remote["shared:en"] ?? {}) };

    const t = (key: string, values?: Record<string, string | number>) => {
      const template = own[key] ?? shared[key] ?? ownEnglish[key] ?? sharedEnglish[key] ?? key;
      return values ? interpolate(template, values) : template;
    };

    return { t, language };
    // `revision` is the feed's version counter: it changes when a newer
    // catalogue lands, which is the only reason `t` can give a different answer.
  }, [page, language, revision]);
}

/**
 * Point the browser tab at the page's localized title.
 *
 * Pages without a catalogue (a doc article, a team profile, a changelog entry)
 * keep whatever title the server rendered, which is already the specific one —
 * and so do pages whose server title carries a server or member name, which a
 * generic catalogue title must not overwrite.
 */
export function usePageTitle(page: string) {
  const { language, revision } = useCatalogue(page);

  useEffect(() => {
    if (STATIC_TITLELESS_PAGES.has(page)) return;
    const title = remote[`${page}:${language}`]?.title
      ?? CATALOGUES[page]?.[language]?.title
      ?? remote[`${page}:en`]?.title
      ?? CATALOGUES[page]?.en?.title;
    if (title) document.title = title;
  }, [page, language, revision]);
}

/**
 * Routes whose URL identifies a record, so the server renders a title with that
 * record's name in it. The catalogue title is the generic fallback and would
 * make a guild board look like the default one.
 */
const STATIC_TITLELESS_PAGES = new Set([
  "guild-leaderboard",
  "docs-detail",
  // The developer docs set their own title per routed page.
  "developers",
  "team-member",
  "changelog-detail",
  "transcript",
  "email-report",
  "application",
]);
