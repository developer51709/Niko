/**
 * Site localization, one catalogue folder per page.
 *
 * Every page owns a folder under `web/src/locales/<page>/`, the way every page
 * owns a generated Open Graph card: `en.json` holds the source copy and the
 * other languages live beside it as they are translated. A folder whose
 * translation is missing simply falls back to English, so a half-translated
 * site never shows raw keys or blank text.
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
  type ReactNode,
} from "react";

export const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "de", label: "German" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
] as const;

export type LanguageCode = (typeof LANGUAGES)[number]["code"];

/** Where the devtools override lives; only this browser sees it. */
const STORAGE_KEY = "niko.site.language";

type Catalogue = Record<string, string>;

/** `../locales/status/en.json` → `CATALOGUES.status.en`.
 *
 * Catalogues are read as raw text and parsed here, the same way the docs
 * pipeline reads its MDX: it keeps the file contents visible to a bad-catalogue
 * error instead of failing inside the bundler, and a typo names the file.
 */
const catalogueModules = import.meta.glob<string>("../locales/*/*.json", {
  eager: true,
  query: "?raw",
  import: "default",
});

const CATALOGUES: Record<string, Partial<Record<LanguageCode, Catalogue>>> = {};
for (const [path, source] of Object.entries(catalogueModules)) {
  const match = /locales\/([^/]+)\/([^/]+)\.json$/.exec(path);
  if (!match || !isLanguage(match[2])) continue;
  let strings: Catalogue;
  try {
    strings = JSON.parse(source) as Catalogue;
  } catch (error) {
    throw new Error(`Invalid locale catalogue ${path}: ${(error as Error).message}`);
  }
  CATALOGUES[match[1]] = { ...(CATALOGUES[match[1]] ?? {}), [match[2]]: strings };
}

function isLanguage(value: string | null | undefined): value is LanguageCode {
  return LANGUAGES.some((entry) => entry.code === value);
}

/** Map `de-DE`, `fr_CA`, … onto a shipped language, or null when unsupported. */
function matchLanguage(tag: string | null | undefined): LanguageCode | null {
  const code = String(tag ?? "").toLowerCase().split("-")[0];
  return isLanguage(code) ? code : null;
}

function browserLanguage(): LanguageCode {
  if (typeof navigator === "undefined") return "en";
  const preferred = navigator.languages?.length ? navigator.languages : [navigator.language];
  for (const candidate of preferred) {
    const code = matchLanguage(candidate);
    if (code) return code;
  }
  return "en";
}

function storedLanguage(): LanguageCode | null {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    return isLanguage(value) ? value : null;
  } catch {
    // Storage can be blocked; the browser default is still a good answer.
    return null;
  }
}

function interpolate(template: string, values: Record<string, string | number>) {
  return template.replace(/\{(\w+)\}/g, (whole, key: string) =>
    key in values ? String(values[key]) : whole,
  );
}

type LanguageContextValue = {
  language: LanguageCode;
  /** What the browser asked for, shown in devtools next to the override. */
  browser: LanguageCode;
  /** True while the owner devtools override is active. */
  overridden: boolean;
  setLanguage: (language: LanguageCode) => void;
  resetLanguage: () => void;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [browser] = useState(browserLanguage);
  const [override, setOverride] = useState<LanguageCode | null>(storedLanguage);
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
    () => ({ language, browser, overridden: override !== null && override !== browser, setLanguage, resetLanguage }),
    [language, browser, override, setLanguage, resetLanguage],
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
 */
export function useStrings(page: string) {
  const { language } = useLanguage();

  return useMemo(() => {
    const own = CATALOGUES[page]?.[language] ?? {};
    const ownEnglish = CATALOGUES[page]?.en ?? {};
    const shared = page === "shared" ? {} : CATALOGUES.shared?.[language] ?? {};
    const sharedEnglish = page === "shared" ? {} : CATALOGUES.shared?.en ?? {};

    const t = (key: string, values?: Record<string, string | number>) => {
      const template = own[key] ?? shared[key] ?? ownEnglish[key] ?? sharedEnglish[key] ?? key;
      return values ? interpolate(template, values) : template;
    };

    return { t, language };
  }, [page, language]);
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
  const { language } = useLanguage();

  useEffect(() => {
    if (STATIC_TITLELESS_PAGES.has(page)) return;
    const title = CATALOGUES[page]?.[language]?.title ?? CATALOGUES[page]?.en?.title;
    if (title) document.title = title;
  }, [page, language]);
}

/**
 * Routes whose URL identifies a record, so the server renders a title with that
 * record's name in it. The catalogue title is the generic fallback and would
 * make a guild board look like the default one.
 */
const STATIC_TITLELESS_PAGES = new Set([
  "guild-leaderboard",
  "docs-detail",
  "team-member",
  "changelog-detail",
  "transcript",
  "email-report",
  "application",
]);
