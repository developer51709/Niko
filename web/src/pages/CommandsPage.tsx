import { useEffect, useMemo, useState } from "react";
import { getCommands } from "../api";
import { Footer } from "../components/Footer";
import { PublicHeader } from "../components/PublicHeader";
import { type Command } from "../types";

export function CommandsPage() {
  const [commands, setCommands] = useState<Command[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  useEffect(() => { getCommands().then(setCommands).catch(() => undefined); }, []);
  const categories = useMemo(() => ["all", ...Array.from(new Set(commands.map((command) => command.category))).sort()], [commands]);
  const filtered = commands.filter((command) => (category === "all" || command.category === category) && `${command.name} ${command.description}`.toLowerCase().includes(query.toLowerCase()));
  return (
    <>
      <PublicHeader page="commands" />
      <main className="shell page-main">
        <div className="page-heading"><div className="eyebrow">Reference library</div><h1>Everything Niko<br /><em>knows how to do.</em></h1><p>Browse the live command registry from the bot. Search by name, description, or category.</p></div>
        <div className="command-toolbar"><label className="search-field"><span aria-hidden="true">⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search commands" aria-label="Search commands" /></label><div className="filter-list" aria-label="Command categories">{categories.map((item) => <button className={category === item ? "filter active" : "filter"} key={item} onClick={() => setCategory(item)}>{item}</button>)}</div></div>
        <div className="command-meta"><strong>{filtered.length}</strong> commands <span>·</span> updated from the connected bot</div>
        <div className="commands-grid">{filtered.map((command) => <article className="command-card" key={`${command.category}-${command.name}`}><div className="command-name">/{command.name}</div><p>{command.description || "A Niko command for your server."}</p><span className="category-tag">{command.category}</span></article>)}{!filtered.length && <div className="empty-state">No commands match that search.</div>}</div>
      </main>
      <Footer />
    </>
  );
}