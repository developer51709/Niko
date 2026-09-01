import { useEffect, useMemo, useState } from "react";
import { getCommands } from "../api";
import { Footer } from "../components/Footer";
import { PublicHeader } from "../components/PublicHeader";
import { type Command, type CommandType } from "../types";

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

export function CommandsPage() {
  const [commands, setCommands] = useState<Command[]>([]);
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
  const categories = useMemo(() => ["all", ...Array.from(new Set(commands.map((command) => command.category))).sort()], [commands]);
  const filtered = commands.filter((command) => {
    const haystack = `${command.name} ${command.description} ${command.category} ${typeLabels[normalizeType(command)]} ${command.context_type || ""}`.toLowerCase();
    return (type === "all" || normalizeType(command) === type)
      && (category === "all" || command.category === category)
      && haystack.includes(query.trim().toLowerCase());
  });
  return (
    <>
      <PublicHeader page="commands" />
      <main className="shell page-main">
        <div className="page-heading"><div className="eyebrow">Reference library</div><h1>Everything Niko<br /><em>knows how to do.</em></h1><p>Browse slash, prefix, hybrid, and context commands from the live bot registry. Search by name, description, or category.</p></div>
        <div className="command-toolbar">
          <label className="search-field"><span aria-hidden="true">⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search commands" aria-label="Search commands" /></label>
          <div className="command-filters">
            <div className="filter-list" aria-label="Command types">{commandTypeOptions.map((item) => <button type="button" className={type === item.value ? "filter active" : "filter"} aria-pressed={type === item.value} key={item.value} onClick={() => setType(item.value)}>{item.label}</button>)}</div>
            <div className="filter-list" aria-label="Command categories">{categories.map((item) => <button type="button" className={category === item ? "filter active" : "filter"} aria-pressed={category === item} key={item} onClick={() => setCategory(item)}>{item === "all" ? "All categories" : item}</button>)}</div>
          </div>
        </div>
        <div className="command-meta"><strong>{loading ? "…" : filtered.length}</strong> commands <span>·</span> live bot registry</div>
        {error && <div className="inline-error" role="alert"><strong>Could not load commands</strong><span>{error}</span></div>}
        <div className="commands-grid">{filtered.map((command) => <article className="command-card" key={`${normalizeType(command)}-${command.context_type || ""}-${command.category}-${command.name}`}><div className="command-card-head"><div className="command-name">{renderInvocation(command)}</div><span className="command-type">{typeLabels[normalizeType(command)]}</span></div><p>{command.description || "A Niko command for your server."}</p><span className="category-tag">{command.category}</span></article>)}{!loading && !error && !filtered.length && <div className="empty-state">No commands match that search.</div>}</div>
      </main>
      <Footer />
    </>
  );
}