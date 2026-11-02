import { useEffect, useMemo, useRef, useState } from "react";
import { getCommands } from "../api";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { PublicPageIntro } from "../components/PublicPageIntro";
import { type Command, type CommandParameter, type CommandType } from "../types";

const PREFERRED_LOCALE = typeof navigator !== "undefined" ? (navigator.language || "en").slice(0, 2) : "en";

/** Wording arrives as a ``{locale: text}`` map from the bot's locale files. */
function pickLocalized(value?: string | Record<string, string>): string | undefined {
  if (typeof value === "string") return value.trim() || undefined;
  if (value && typeof value === "object") {
    if (value[PREFERRED_LOCALE]) return value[PREFERRED_LOCALE];
    if (value["en"]) return value["en"];
    const first = Object.values(value).find((text) => typeof text === "string" && text.trim());
    if (first) return first;
  }
  return undefined;
}

function describe(command: Command): string {
  return pickLocalized(command.description) || "A Niko command for your server.";
}

function describeParameter(parameter: CommandParameter): string {
  return pickLocalized(parameter.description) || "No description provided.";
}


const commandTypeOptions: { value: "all" | CommandType; label: string }[] = [
  { value: "all", label: "All commands" },
  { value: "slash", label: "Slash" },
  { value: "prefix", label: "Prefix" },
  { value: "hybrid", label: "Hybrid" },
  { value: "context", label: "Context menus" },
];

const typeLabels: Record<CommandType, string> = {
  slash: "Slash command",
  prefix: "Prefix command",
  hybrid: "Hybrid command",
  context: "Context menu",
};

/** The small glyph tile that leads a card and the dialog header. */
const typeSigils: Record<CommandType, string> = {
  slash: "/",
  prefix: ".",
  hybrid: "/.",
  context: "▸",
};

function normalizeType(command: Command): CommandType {
  return command.type && command.type in typeLabels ? command.type : "slash";
}

function contextLabel(command: Command) {
  return command.context_type === "user" ? "Right-click a user" : "Right-click a message";
}

/** Context menus are opened from an avatar or message, so the card names them by their menu. */
function cardTypeHint(command: Command) {
  return normalizeType(command) === "context" ? contextLabel(command) : typeLabels[normalizeType(command)];
}

function renderInvocation(command: Command) {
  const type = normalizeType(command);
  if (type === "slash") return <code>/{command.name}</code>;
  if (type === "prefix") return <code>.{command.name}</code>;
  if (type === "hybrid") return <><code>/{command.name}</code><span className="command-or">or</span><code>.{command.name}</code></>;
  return <code className="context-invocation">{contextLabel(command)} · {command.name}</code>;
}

function renderCardName(command: Command) {
  const type = normalizeType(command);
  if (type === "slash") return <code>/{command.name}</code>;
  if (type === "prefix") return <code>.{command.name}</code>;
  if (type === "hybrid") return <><code>/{command.name}</code><span className="command-or">or</span><code>.{command.name}</code></>;
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
                <span>{typeLabels[type]}</span>
                {type === "context" && <><i aria-hidden="true" /><span>{contextLabel(command)}</span></>}
              </div>
              <h2 id="command-dialog-title">{renderInvocation(command)}</h2>
            </div>
          </div>
          <button className="dialog-close" type="button" onClick={onClose} aria-label="Close command details" title="Close command details" ref={closeRef}><Icon name="close" /></button>
        </header>
        <div className="command-dialog-body">
          <p className="command-dialog-description" id="command-dialog-description">{describe(command)}</p>
          <section className="command-detail-section command-usage-section">
            <div className="command-section-head">
              <h3>Usage</h3>
              <button className="command-copy" type="button" onClick={copyUsage} aria-label="Copy usage to clipboard">
                {copied && <Icon name="check" size={12} />}
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
            <code className="command-usage">{usage}</code>
          </section>
          {!!parameters.length && (
            <section className="command-detail-section command-parameters-section">
              <div className="command-section-head">
                <h3>Parameters</h3>
                <span className="command-section-count">{parameters.length}</span>
              </div>
              <div className="command-parameter-list">
                {parameters.map((parameter: CommandParameter) => (
                  <div className="command-parameter" key={parameter.name}>
                    <div className="command-parameter-title">
                      <code>{parameter.name}</code>
                      <span className={`command-param-flag${parameter.required ? " is-required" : ""}`}>{parameter.required ? "Required" : "Optional"}</span>
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
              <h3>Permissions</h3>
              <ul className="command-detail-list">
                {permissions.length ? permissions.map((permission) => <li key={permission}>{permission}</li>) : <li className="command-detail-empty">None required</li>}
              </ul>
            </section>
            <section className="command-detail-section">
              <h3>Aliases</h3>
              <ul className="command-detail-list">
                {aliases.length ? aliases.map((alias) => <li key={alias}><code>.{alias}</code></li>) : <li className="command-detail-empty">None</li>}
              </ul>
            </section>
          </div>
          {!!subcommands.length && (
            <section className="command-detail-section">
              <div className="command-section-head">
                <h3>Subcommands</h3>
                <span className="command-section-count">{subcommands.length}</span>
              </div>
              <div className="subcommand-list">{subcommands.map((subcommand) => <code key={subcommand}>{command.name} {subcommand}</code>)}</div>
            </section>
          )}
        </div>
        <footer className="command-dialog-footer">
          <span>Command registry details are generated from the live bot.</span>
          <button className="button button-primary button-small" type="button" onClick={onClose}>Done</button>
        </footer>
      </section>
    </div>
  );
}

export function CommandsPage() {
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
        if (!Array.isArray(result)) throw new Error("The command registry returned an invalid response.");
        setCommands(result);
      })
      .catch(() => setError("The command registry is unavailable right now."))
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
    const haystack = `${command.name} ${describe(command)} ${command.category} ${typeLabels[normalizeType(command)]} ${command.context_type || ""} ${(command.aliases || []).join(" ")}`.toLowerCase();
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
          eyebrow="Reference library"
          title={<>Everything Niko <em>knows how to do.</em></>}
          description="Browse slash, prefix, hybrid, and context commands from the live bot registry. Select a command to see its permissions, aliases, parameters, usage, and subcommands."
        />
        <section className="command-toolbar" aria-label="Search and filter commands">
          <div className="command-search-row">
            <div className="search-field">
              <Icon name="search" size={15} />
              <label className="sr-only" htmlFor="command-search">Search commands</label>
              <input id="command-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by name, description, category or alias" />
              {!!query && <button className="search-clear" type="button" onClick={() => setQuery("")} aria-label="Clear search"><Icon name="close" size={12} /></button>}
            </div>
            <div className="command-count" role="status" aria-live="polite">
              <strong>{loading ? "…" : filtered.length}</strong>
              <span>{filtered.length === 1 ? "command" : "commands"}</span>
            </div>
          </div>
          <div className="command-filter-rows">
            <div className="command-filter-row">
              <span className="command-filter-label" aria-hidden="true">Type</span>
              <div className="filter-list" role="group" aria-label="Command types">{commandTypeOptions.map((item) => <button type="button" className={type === item.value ? "filter active" : "filter"} aria-pressed={type === item.value} key={item.value} onClick={() => setType(item.value)}>{item.label}</button>)}</div>
            </div>
            <div className="command-filter-row">
              <span className="command-filter-label" aria-hidden="true">Category</span>
              <div className="filter-list" role="group" aria-label="Command categories">{categories.map((item) => <button type="button" className={category === item ? "filter active" : "filter"} aria-pressed={category === item} key={item} onClick={() => setCategory(item)}>{item === "all" ? "All categories" : item}</button>)}</div>
            </div>
          </div>
          <div className="command-toolbar-footer">
            <span className="command-registry-note"><i aria-hidden="true" />Live bot registry</span>
            {hasFilters
              ? <button className="command-reset" type="button" onClick={resetFilters}>Reset filters</button>
              : <span className="command-registry-hint">Select a command for its full details</span>}
          </div>
        </section>
        {error && <div className="inline-error" role="alert"><strong>Could not load commands</strong><span>{error}</span></div>}
        {loading && !error && (
          <div className="commands-grid commands-skeleton" aria-hidden="true">
            {Array.from({ length: 6 }).map((_, index) => <div className="command-card-skeleton" key={index}><span /><span /><span /></div>)}
          </div>
        )}
        {!loading && <div className="commands-grid">
          {filtered.map((command) => <button className="command-card" type="button" key={`${normalizeType(command)}-${command.context_type || ""}-${command.category}-${command.name}`} onClick={() => setSelectedCommand(command)} aria-label={`View details for ${command.name}`}>
            <span className="command-card-top">
              <span className={`command-sigil is-${normalizeType(command)}`} aria-hidden="true">{typeSigils[normalizeType(command)]}</span>
              <span className="command-card-title">
                <span className="command-name">{renderCardName(command)}</span>
                <span className="command-type">{cardTypeHint(command)}</span>
              </span>
            </span>
            <span className="command-card-description">{describe(command)}</span>
            <span className="command-card-footer"><span className="category-tag">{command.category}</span><span className="command-expand"><span>Details</span><Icon name="arrow" size={14} /></span></span>
          </button>)}
          {!error && !filtered.length && <div className="commands-empty">
            <span className="commands-empty-icon" aria-hidden="true"><Icon name="search" size={16} /></span>
            <strong>No commands match {query.trim() ? `“${query.trim()}”` : "these filters"}</strong>
            <p>Try another search term, or widen the type and category filters.</p>
            {hasFilters && <button className="button button-muted button-small" type="button" onClick={resetFilters}>Reset filters</button>}
          </div>}
        </div>}
      </main>
      <Footer />
      {selectedCommand && <CommandDetailDialog command={selectedCommand} onClose={() => setSelectedCommand(null)} />}
    </>
  );
}
