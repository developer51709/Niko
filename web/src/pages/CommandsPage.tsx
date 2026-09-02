import { useEffect, useMemo, useState } from "react";
import { getCommands } from "../api";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { type Command, type CommandParameter, type CommandType } from "../types";

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

function normalizeType(command: Command): CommandType {
  return command.type && command.type in typeLabels ? command.type : "slash";
}

function contextLabel(command: Command) {
  return command.context_type === "user" ? "Right-click a user" : "Right-click a message";
}

function renderInvocation(command: Command) {
  const type = normalizeType(command);
  if (type === "slash") return <code>/{command.name}</code>;
  if (type === "prefix") return <code>.{command.name}</code>;
  if (type === "hybrid") return <><code>/{command.name}</code><span className="command-or">or</span><code>.{command.name}</code></>;
  return <code className="context-invocation">{contextLabel(command)} · {command.name}</code>;
}

function listValue(values?: string[]) {
  return values?.length ? values : ["Not specified"];
}

function CommandDetailDialog({ command, onClose }: { command: Command; onClose: () => void }) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const parameters = command.parameters || [];
  const subcommands = command.subcommands || [];
  const aliases = listValue(command.aliases);
  const permissions = listValue(command.permissions);

  return (
    <div className="command-dialog-backdrop" role="presentation" onMouseDown={(event) => { if (event.currentTarget === event.target) onClose(); }}>
      <section className="command-dialog" role="dialog" aria-modal="true" aria-labelledby="command-dialog-title">
        <header className="command-dialog-header">
          <div>
            <div className="command-dialog-kicker">{command.category} · {typeLabels[normalizeType(command)]}</div>
            <h2 id="command-dialog-title">{renderInvocation(command)}</h2>
          </div>
          <button className="dialog-close" type="button" onClick={onClose} aria-label="Close command details" title="Close command details"><Icon name="close" /></button>
        </header>
        <div className="command-dialog-body">
          <p className="command-dialog-description">{command.description || "A Niko command for your server."}</p>
          <div className="command-detail-grid">
            <section className="command-detail-section command-detail-wide">
              <h3>Usage</h3>
              <code className="command-usage">{command.usage || `${normalizeType(command) === "context" ? command.name : `/${command.name}`}`}</code>
            </section>
            <section className="command-detail-section">
              <h3>Permissions</h3>
              <ul className="command-detail-list">{permissions.map((permission) => <li key={permission}>{permission}</li>)}</ul>
            </section>
            <section className="command-detail-section">
              <h3>Aliases</h3>
              <ul className="command-detail-list">{aliases.map((alias) => <li key={alias}><code>{alias === "Not specified" ? alias : `.${alias}`}</code></li>)}</ul>
            </section>
          </div>
          {!!parameters.length && <section className="command-detail-section command-parameters"><h3>Parameters</h3><div className="command-parameter-list">{parameters.map((parameter: CommandParameter) => <div className="command-parameter" key={parameter.name}><div className="command-parameter-title"><code>{parameter.name}</code><span>{parameter.required ? "Required" : "Optional"} · {parameter.type}</span></div><p>{parameter.description || "No description provided."}</p></div>)}</div></section>}
          {!!subcommands.length && <section className="command-detail-section"><h3>Subcommands</h3><div className="subcommand-list">{subcommands.map((subcommand) => <code key={subcommand}>{command.name} {subcommand}</code>)}</div></section>}
        </div>
        <footer className="command-dialog-footer"><span>Command registry details are generated from the live bot.</span><button className="button button-primary button-small" type="button" onClick={onClose}>Done</button></footer>
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
      .then(setCommands)
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
    const haystack = `${command.name} ${command.description} ${command.category} ${typeLabels[normalizeType(command)]} ${command.context_type || ""} ${(command.aliases || []).join(" ")}`.toLowerCase();
    return (type === "all" || normalizeType(command) === type)
      && (category === "all" || command.category === category)
      && haystack.includes(query.trim().toLowerCase());
  });

  return (
    <>
      <PublicHeader page="commands" />
      <main className="shell page-main">
        <div className="page-heading"><div className="eyebrow">Reference library</div><h1>Everything Niko<br /><em>knows how to do.</em></h1><p>Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands.</p></div>
        <div className="command-toolbar">
          <label className="search-field"><span aria-hidden="true">⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search commands" aria-label="Search commands" /></label>
          <div className="command-filters">
            <div className="filter-list" aria-label="Command types">{commandTypeOptions.map((item) => <button type="button" className={type === item.value ? "filter active" : "filter"} aria-pressed={type === item.value} key={item.value} onClick={() => setType(item.value)}>{item.label}</button>)}</div>
            <div className="filter-list" aria-label="Command categories">{categories.map((item) => <button type="button" className={category === item ? "filter active" : "filter"} aria-pressed={category === item} key={item} onClick={() => setCategory(item)}>{item === "all" ? "All categories" : item}</button>)}</div>
          </div>
        </div>
        <div className="command-meta"><strong>{loading ? "…" : filtered.length}</strong> commands <span>·</span> live bot registry <span>·</span> select a card for details</div>
        {error && <div className="inline-error" role="alert"><strong>Could not load commands</strong><span>{error}</span></div>}
        <div className="commands-grid">
          {filtered.map((command) => <button className="command-card" type="button" key={`${normalizeType(command)}-${command.context_type || ""}-${command.category}-${command.name}`} onClick={() => setSelectedCommand(command)} aria-label={`View details for ${command.name}`}>
            <span className="command-card-head"><span className="command-name">{renderInvocation(command)}</span><span className="command-type">{typeLabels[normalizeType(command)]}</span></span>
            <span className="command-card-description">{command.description || "A Niko command for your server."}</span>
            <span className="command-card-footer"><span className="category-tag">{command.category}</span><span className="command-expand"><span>Details</span><Icon name="arrow" size={14} /></span></span>
          </button>)}
          {!loading && !error && !filtered.length && <div className="empty-state">No commands match that search.</div>}
        </div>
      </main>
      <Footer />
      {selectedCommand && <CommandDetailDialog command={selectedCommand} onClose={() => setSelectedCommand(null)} />}
    </>
  );
}
