import { useEffect, useMemo, useRef, useState } from "react";
import { getCommands } from "../api";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { PublicPageIntro } from "../components/PublicPageIntro";
import { type Translate, useLanguage, useStrings } from "../i18n";
import { type Command, type CommandParameter, type CommandType } from "../types";

const BROWSER_LOCALE = typeof navigator !== "undefined" ? (navigator.language || "en").slice(0, 2) : "en";

/** One entry of a ``{locale: text}`` map, matching ``de`` against ``de-DE`` too. */
function localizedValue(value: Record<string, string>, code: string): string | undefined {
  const direct = value[code];
  if (direct && direct.trim()) return direct;
  const match = Object.keys(value).find((key) => key.toLowerCase().split("-")[0] === code);
  const text = match ? value[match] : "";
  return text && text.trim() ? text : undefined;
}

/**
 * Wording arrives as a ``{locale: text}`` map from the bot's locale files.
 *
 * The site language is asked for first, so a language picked in the owner
 * devtools changes the command cards even when the browser or device locale
 * says something else; the browser language, English and finally whatever the
 * registry offers are the fallbacks behind it.
 */
function pickLocalized(value: string | Record<string, string> | undefined, language: string): string | undefined {
  if (typeof value === "string") return value.trim() || undefined;
  if (!value || typeof value !== "object") return undefined;
  return localizedValue(value, language)
    ?? localizedValue(value, BROWSER_LOCALE)
    ?? localizedValue(value, "en")
    ?? Object.values(value).find((text) => typeof text === "string" && text.trim());
}

/**
 * Command wording for the active site language. Both the card list and the
 * detail dialog read it from here, so they always agree.
 */
function useCommandCopy() {
  const { language } = useLanguage();
  const { t } = useStrings("commands");

  // The registry can be missing a description, so the page supplies one. That
  // fallback is page copy like any other heading, and comes from the catalogue.
  return useMemo(() => ({
    describe: (command: Command) => pickLocalized(command.description, language) || t("fallback.description"),
    describeParameter: (parameter: CommandParameter) =>
      pickLocalized(parameter.description, language) || t("fallback.parameter"),
  }), [language, t]);
}

// Filter chips keep their order and value here; the label is a catalogue key.
const commandTypeOptions: { value: "all" | CommandType; key: string }[] = [
  { value: "all", key: "filter.all" },
  { value: "slash", key: "filter.slash" },
  { value: "prefix", key: "filter.prefix" },
  { value: "hybrid", key: "filter.hybrid" },
  { value: "context", key: "filter.context" },
];

const typeKeys: Record<CommandType, string> = {
  slash: "type.slash",
  prefix: "type.prefix",
  hybrid: "type.hybrid",
  context: "type.context",
};

/** The small glyph tile that leads a card and the dialog header. */
const typeSigils: Record<CommandType, string> = {
  slash: "/",
  prefix: ".",
  hybrid: "/.",
  context: "▸",
};

function normalizeType(command: Command): CommandType {
  return command.type && command.type in typeKeys ? command.type : "slash";
}

function contextLabel(command: Command, t: Translate) {
  return command.context_type === "user" ? t("context.user") : t("context.message");
}

/** Context menus are opened from an avatar or message, so the card names them by their menu. */
function cardTypeHint(command: Command, t: Translate) {
  return normalizeType(command) === "context" ? contextLabel(command, t) : t(typeKeys[normalizeType(command)]);
}

function renderInvocation(command: Command, t: Translate) {
  const type = normalizeType(command);
  if (type === "slash") return <code>/{command.name}</code>;
  if (type === "prefix") return <code>.{command.name}</code>;
  if (type === "hybrid") return <><code>/{command.name}</code><span className="command-or">{t("invocation.or")}</span><code>.{command.name}</code></>;
  return <code className="context-invocation">{contextLabel(command, t)} · {command.name}</code>;
}

function renderCardName(command: Command, t: Translate) {
  const type = normalizeType(command);
  if (type === "slash") return <code>/{command.name}</code>;
  if (type === "prefix") return <code>.{command.name}</code>;
  if (type === "hybrid") return <><code>/{command.name}</code><span className="command-or">{t("invocation.or")}</span><code>.{command.name}</code></>;
  return <code>{command.name}</code>;
}

function usageOf(command: Command) {
  if (command.usage) return command.usage;
  return normalizeType(command) === "context" ? command.name : `/${command.name}`;
}

function detailValues(values?: string[]) {
  return (values || []).filter((value) => typeof value === "string" && value.trim());
}

function CommandDetailDialog({ command, onClose }: { command: Command; onClose: () => void }) {
  const dialogRef = useRef<HTMLElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const [copied, setCopied] = useState(false);
  const { t } = useStrings("commands");
  const { describe, describeParameter } = useCommandCopy();
  const close = useRef(onClose);
  close.current = onClose;

  // Escape closes, Tab stays inside the dialog, and focus returns to the card
  // that opened it once the dialog unmounts.
  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        close.current();
        return;
      }
      if (event.key !== "Tab") return;
      const root = dialogRef.current;
      if (!root) return;
      const focusable = Array.from(root.querySelectorAll<HTMLElement>("button, [href], input, select, textarea")).filter((element) => !element.hasAttribute("disabled"));
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      previouslyFocused?.focus?.();
    };
  }, []);

  useEffect(() => {
    if (!copied) return;
    const timer = window.setTimeout(() => setCopied(false), 1800);
    return () => window.clearTimeout(timer);
  }, [copied]);

  const usage = usageOf(command);
  const parameters = command.parameters || [];
  const subcommands = command.subcommands || [];
  const aliases = detailValues(command.aliases);
  const permissions = detailValues(command.permissions);
  const type = normalizeType(command);

  const copyUsage = async () => {
    try {
      await navigator.clipboard.writeText(usage);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="command-dialog-backdrop" role="presentation" onMouseDown={(event) => { if (event.currentTarget === event.target) onClose(); }}>
      <section className="command-dialog" role="dialog" aria-modal="true" aria-labelledby="command-dialog-title" aria-describedby="command-dialog-description" ref={dialogRef}>
        <header className="command-dialog-header">
          <div className="command-dialog-heading">
            <span className="command-sigil command-sigil-large" aria-hidden="true">{typeSigils[type]}</span>
            <div className="command-dialog-title-group">
              <div className="command-dialog-kicker">
                <span>{command.category}</span>
                <i aria-hidden="true" />
                <span>{t(typeKeys[type])}</span>
                {type === "context" && <><i aria-hidden="true" /><span>{contextLabel(command, t)}</span></>}
              </div>
              <h2 id="command-dialog-title">{renderInvocation(command, t)}</h2>
            </div>
          </div>
          <button className="dialog-close" type="button" onClick={onClose} aria-label={t("dialog.close")} title={t("dialog.close")} ref={closeRef}><Icon name="close" /></button>
        </header>
        <div className="command-dialog-body">
          <p className="command-dialog-description" id="command-dialog-description">{describe(command)}</p>
          <section className="command-detail-section command-usage-section">
            <div className="command-section-head">
              <h3>{t("dialog.usage")}</h3>
              <button className="command-copy" type="button" onClick={copyUsage} aria-label={t("dialog.copyAria")}>
                {copied && <Icon name="check" size={12} />}
                {t(copied ? "dialog.copied" : "dialog.copy")}
              </button>
            </div>
            <code className="command-usage">{usage}</code>
          </section>
          {!!parameters.length && (
            <section className="command-detail-section command-parameters-section">
              <div className="command-section-head">
                <h3>{t("dialog.parameters")}</h3>
                <span className="command-section-count">{parameters.length}</span>
              </div>
              <div className="command-parameter-list">
                {parameters.map((parameter: CommandParameter) => (
                  <div className="command-parameter" key={parameter.name}>
                    <div className="command-parameter-title">
                      <code>{parameter.name}</code>
                      <span className={`command-param-flag${parameter.required ? " is-required" : ""}`}>{t(parameter.required ? "dialog.required" : "dialog.optional")}</span>
                      {parameter.type && <span className="command-param-type">{parameter.type}</span>}
                    </div>
                    <p>{describeParameter(parameter)}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
          <div className="command-detail-grid">
            <section className="command-detail-section">
              <h3>{t("dialog.permissions")}</h3>
              <ul className="command-detail-list">
                {permissions.length ? permissions.map((permission) => <li key={permission}>{permission}</li>) : <li className="command-detail-empty">{t("dialog.noneRequired")}</li>}
              </ul>
            </section>
            <section className="command-detail-section">
              <h3>{t("dialog.aliases")}</h3>
              <ul className="command-detail-list">
                {aliases.length ? aliases.map((alias) => <li key={alias}><code>.{alias}</code></li>) : <li className="command-detail-empty">{t("dialog.none")}</li>}
              </ul>
            </section>
          </div>
          {!!subcommands.length && (
            <section className="command-detail-section">
              <div className="command-section-head">
                <h3>{t("dialog.subcommands")}</h3>
                <span className="command-section-count">{subcommands.length}</span>
              </div>
              <div className="subcommand-list">{subcommands.map((subcommand) => <code key={subcommand}>{command.name} {subcommand}</code>)}</div>
            </section>
          )}
        </div>
        <footer className="command-dialog-footer">
          <span>{t("dialog.footer")}</span>
          <button className="button button-primary button-small" type="button" onClick={onClose}>{t("dialog.done")}</button>
        </footer>
      </section>
    </div>
  );
}

export function CommandsPage() {
  const { t } = useStrings("commands");
  const { describe } = useCommandCopy();
  const [commands, setCommands] = useState<Command[]>([]);
  const [selectedCommand, setSelectedCommand] = useState<Command | null>(null);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [type, setType] = useState<"all" | CommandType>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getCommands()
      .then((result) => {
        if (!Array.isArray(result)) throw new Error(t("error.invalidResponse"));
        setCommands(result);
      })
      .catch(() => setError("error.unavailable"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedCommand) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = previousOverflow; };
  }, [selectedCommand]);

  const categories = useMemo(() => ["all", ...Array.from(new Set(commands.map((command) => command.category))).sort()], [commands]);
  const filtered = commands.filter((command) => {
    // Search every language the registry sent, so switching the site language
    // never makes a command harder to find by the words it was already under.
    const descriptions = typeof command.description === "string"
      ? command.description
      : Object.values(command.description || {}).join(" ");
    const haystack = `${command.name} ${descriptions} ${command.category} ${t(typeKeys[normalizeType(command)])} ${command.context_type || ""} ${(command.aliases || []).join(" ")}`.toLowerCase();
    return (type === "all" || normalizeType(command) === type)
      && (category === "all" || command.category === category)
      && haystack.includes(query.trim().toLowerCase());
  });

  const hasFilters = type !== "all" || category !== "all" || Boolean(query.trim());
  const resetFilters = () => { setQuery(""); setType("all"); setCategory("all"); };

  return (
    <>
      <PublicHeader page="commands" />
      <main className="shell page-main commands-page">
        <PublicPageIntro
          eyebrow={t("intro.eyebrow")}
          title={<>{t("intro.title")} <em>{t("intro.titleEm")}</em></>}
          description={t("intro.description")}
        />
        <section className="command-toolbar" aria-label={t("toolbar.aria")}>
          <div className="command-search-row">
            <div className="search-field">
              <Icon name="search" size={15} />
              <label className="sr-only" htmlFor="command-search">{t("search.label")}</label>
              <input id="command-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t("search.placeholder")} />
              {!!query && <button className="search-clear" type="button" onClick={() => setQuery("")} aria-label={t("search.clear")}><Icon name="close" size={12} /></button>}
            </div>
            <div className="command-count" role="status" aria-live="polite">
              <strong>{loading ? "…" : filtered.length}</strong>
              <span>{t(filtered.length === 1 ? "count.one" : "count.many")}</span>
            </div>
          </div>
          <div className="command-filter-rows">
            <div className="command-filter-row">
              <span className="command-filter-label" aria-hidden="true">{t("filter.type")}</span>
              <div className="filter-list" role="group" aria-label={t("filter.types")}>{commandTypeOptions.map((item) => <button type="button" className={type === item.value ? "filter active" : "filter"} aria-pressed={type === item.value} key={item.value} onClick={() => setType(item.value)}>{t(item.key)}</button>)}</div>
            </div>
            <div className="command-filter-row">
              <span className="command-filter-label" aria-hidden="true">{t("filter.category")}</span>
              <div className="filter-list" role="group" aria-label={t("filter.categories")}>{categories.map((item) => <button type="button" className={category === item ? "filter active" : "filter"} aria-pressed={category === item} key={item} onClick={() => setCategory(item)}>{item === "all" ? t("filter.allCategories") : item}</button>)}</div>
            </div>
          </div>
          <div className="command-toolbar-footer">
            <span className="command-registry-note"><i aria-hidden="true" />{t("registry.live")}</span>
            {hasFilters
              ? <button className="command-reset" type="button" onClick={resetFilters}>{t("filters.reset")}</button>
              : <span className="command-registry-hint">{t("registry.hint")}</span>}
          </div>
        </section>
        {error && <div className="inline-error" role="alert"><strong>{t("error.title")}</strong><span>{t(error)}</span></div>}
        {loading && !error && (
          <div className="commands-grid commands-skeleton" aria-hidden="true">
            {Array.from({ length: 6 }).map((_, index) => <div className="command-card-skeleton" key={index}><span /><span /><span /></div>)}
          </div>
        )}
        {!loading && <div className="commands-grid">
          {filtered.map((command) => <button className="command-card" type="button" key={`${normalizeType(command)}-${command.context_type || ""}-${command.category}-${command.name}`} onClick={() => setSelectedCommand(command)} aria-label={t("card.view", { name: command.name })}>
            <span className="command-card-top">
              <span className={`command-sigil is-${normalizeType(command)}`} aria-hidden="true">{typeSigils[normalizeType(command)]}</span>
              <span className="command-card-title">
                <span className="command-name">{renderCardName(command, t)}</span>
                <span className="command-type">{cardTypeHint(command, t)}</span>
              </span>
            </span>
            <span className="command-card-description">{describe(command)}</span>
            <span className="command-card-footer"><span className="category-tag">{command.category}</span><span className="command-expand"><span>{t("card.details")}</span><Icon name="arrow" size={14} /></span></span>
          </button>)}
          {!error && !filtered.length && <div className="commands-empty">
            <span className="commands-empty-icon" aria-hidden="true"><Icon name="search" size={16} /></span>
            <strong>{t("empty.title")} {query.trim() ? `“${query.trim()}”` : t("empty.filters")}</strong>
            <p>{t("empty.body")}</p>
            {hasFilters && <button className="button button-muted button-small" type="button" onClick={resetFilters}>{t("filters.reset")}</button>}
          </div>}
        </div>}
      </main>
      <Footer />
      {selectedCommand && <CommandDetailDialog command={selectedCommand} onClose={() => setSelectedCommand(null)} />}
    </>
  );
}
