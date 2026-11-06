import type { ReactNode } from "react";

/**
 * Discord fenced code with a small, dependency-free syntax highlighter.
 *
 * Discord itself highlights a fenced block when the fence names a language.
 * The site used to render every block as flat text, so pasted examples lost
 * the visual cues developers rely on. The palette below follows VS Code's
 * Dark+ theme: keywords are blue, strings orange, comments green, and
 * functions yellow. Unknown languages still render, just without colour.
 */

type TokenKind =
  | "comment"
  | "string"
  | "keyword"
  | "control"
  | "constant"
  | "number"
  | "function"
  | "property"
  | "tag"
  | "operator";

type Language = {
  id: string;
  label: string;
  keywords?: string[];
  controls?: string[];
  constants?: string[];
  comment?: string;
  strings?: boolean;
  properties?: boolean;
  functions?: boolean;
  html?: boolean;
  diff?: boolean;
};

const KEYWORDS = {
  javascript: [
    "async", "await", "break", "case", "catch", "class", "const", "continue", "debugger",
    "default", "delete", "do", "else", "export", "extends", "finally", "for", "from",
    "function", "get", "if", "import", "in", "instanceof", "let", "new", "of", "return",
    "set", "static", "super", "switch", "this", "throw", "try", "typeof", "var", "void",
    "while", "with", "yield", "interface", "type", "enum", "implements", "declare",
    "namespace", "readonly", "private", "protected", "public", "abstract", "as", "satisfies",
  ],
  python: [
    "and", "as", "assert", "async", "await", "break", "class", "continue", "def", "del",
    "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in",
    "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while",
    "with", "yield", "match", "case",
  ],
  bash: [
    "if", "then", "else", "elif", "fi", "for", "in", "do", "done", "while", "until",
    "case", "esac", "function", "select", "time", "coproc", "return", "exit", "local",
    "export", "readonly", "declare", "typeset", "unset", "shift", "source",
  ],
  sql: [
    "select", "from", "where", "and", "or", "not", "insert", "into", "values", "update",
    "set", "delete", "create", "table", "alter", "drop", "join", "left", "right", "inner",
    "outer", "on", "group", "by", "order", "having", "limit", "offset", "as", "distinct",
    "union", "all", "case", "when", "then", "else", "end", "with", "returning", "primary",
    "key", "foreign", "references", "index", "if", "exists", "null", "is", "like", "in",
  ],
  css: ["important", "media", "supports", "keyframes", "from", "to", "and", "or", "not"],
};

const LANGUAGE_MAP: Record<string, Language> = {};
function register(language: Language, aliases: string[]) {
  for (const alias of aliases) LANGUAGE_MAP[alias] = language;
}

const JavaScript: Language = {
  id: "javascript",
  label: "JavaScript",
  keywords: KEYWORDS.javascript,
  controls: ["if", "else", "for", "while", "do", "switch", "case", "try", "catch", "finally", "return", "throw", "await", "yield", "break", "continue"],
  constants: ["true", "false", "null", "undefined", "NaN", "Infinity"],
  comment: "//[^\\n]*|/\\*[\\s\\S]*?\\*/",
  strings: true,
  functions: true,
};
register(JavaScript, ["js", "javascript", "jsx", "mjs", "cjs"]);
register({ ...JavaScript, id: "typescript", label: "TypeScript", keywords: [...KEYWORDS.javascript, "any", "boolean", "number", "string", "unknown", "never", "object", "keyof", "infer", "asserts", "is", "module", "require"] }, ["ts", "typescript", "tsx"]);

const Python: Language = {
  id: "python",
  label: "Python",
  keywords: KEYWORDS.python,
  controls: ["if", "elif", "else", "for", "while", "try", "except", "finally", "return", "raise", "yield", "with", "match", "case"],
  constants: ["True", "False", "None", "NotImplemented", "Ellipsis", "self", "cls"],
  comment: "#[^\\n]*",
  strings: true,
  functions: true,
};
register(Python, ["py", "python", "python3"]);

const Bash: Language = {
  id: "bash",
  label: "Bash",
  keywords: KEYWORDS.bash,
  controls: ["if", "then", "else", "elif", "fi", "for", "while", "until", "case", "esac", "function", "return", "exit"],
  constants: ["true", "false"],
  comment: "#[^\\n]*",
  strings: true,
  functions: true,
};
register(Bash, ["sh", "bash", "shell", "zsh", "fish", "console"]);

const JSONLanguage: Language = {
  id: "json",
  label: "JSON",
  constants: ["true", "false", "null"],
  strings: true,
  properties: true,
};
register(JSONLanguage, ["json", "jsonc", "json5"]);

const SQL: Language = {
  id: "sql",
  label: "SQL",
  keywords: KEYWORDS.sql,
  constants: ["true", "false", "null"],
  comment: "--[^\\n]*|/\\*[\\s\\S]*?\\*/",
  strings: true,
  functions: true,
};
register(SQL, ["sql", "postgres", "postgresql", "sqlite", "mysql"]);

const CSSLanguage: Language = {
  id: "css",
  label: "CSS",
  keywords: KEYWORDS.css,
  constants: ["inherit", "initial", "unset", "revert", "none", "auto"],
  comment: "/\\*[\\s\\S]*?\\*/",
  strings: true,
  properties: true,
};
register(CSSLanguage, ["css", "scss", "sass", "less"]);

const HTML: Language = { id: "html", label: "HTML", html: true, comment: "<!--[\\s\\S]*?-->" };
register(HTML, ["html", "htm", "xml", "svg", "vue"]);

const YAML: Language = {
  id: "yaml",
  label: "YAML",
  constants: ["true", "false", "null", "yes", "no", "on", "off"],
  comment: "#[^\\n]*",
  strings: true,
  properties: true,
};
register(YAML, ["yaml", "yml"]);

const Diff: Language = { id: "diff", label: "Diff", diff: true };
register(Diff, ["diff", "patch"]);

const Markdown: Language = { id: "markdown", label: "Markdown", strings: true };
register(Markdown, ["md", "markdown", "mdx"]);

const HTTP: Language = { id: "http", label: "HTTP", comment: "#[^\\n]*", strings: true, properties: true };
register(HTTP, ["http", "https"]);

const Plain: Language = { id: "text", label: "Plain text" };
register(Plain, ["txt", "text", "plain", "plaintext", ""]);

function languageFor(raw: string): Language {
  const name = raw.trim().toLowerCase().split(/\s+/)[0].replace(/^\{\.?/, "").replace(/\}$/, "");
  return LANGUAGE_MAP[name] || { id: name || "text", label: raw.trim() || "Plain text", strings: true, functions: true };
}

function tokenClass(kind: TokenKind) {
  return `discord-code-token discord-code-${kind}`;
}

function tokenSpans(code: string, language: Language): ReactNode[] {
  if (!code) return [""];
  if (language.diff) {
    return code.split("\n").map((line, index) => {
      const kind = line.startsWith("+") && !line.startsWith("+++")
        ? "is-added"
        : line.startsWith("-") && !line.startsWith("---")
          ? "is-removed"
          : line.startsWith("@@")
            ? "is-hunk"
            : "";
      return <span key={index} className={`discord-code-token ${kind}`.trim()}>{line}{index < code.split("\n").length - 1 ? "\n" : ""}</span>;
    });
  }
  if (language.html) {
    const pattern = /(?<comment><!--[\s\S]*?-->)|(?<tag><\/?[\w:-]+)|(?<attribute>[\w:-]+)(?=\s*=)|(?<string>"[^"]*"|'[^']*')|(?<operator>[<>/=])/g;
    return collectTokens(code, pattern, (groups) => {
      if (groups.comment) return "comment";
      if (groups.tag) return "tag";
      if (groups.attribute) return "property";
      if (groups.string) return "string";
      return "operator";
    });
  }

  const source: string[] = [];
  if (language.comment) source.push(`(?<comment>${language.comment})`);
  if (language.strings) source.push(`(?<string>"(?:\\\\.|[^"\\\\\\n])*"|'(?:\\\\.|[^'\\\\\\n])*'|\`(?:\\\\.|[^\`\\\\])*\`)`);
  if (language.properties) source.push(`(?<property>(?:"(?:\\\\.|[^"\\\\\\n])*"|'[^'\\n]*'|[A-Za-z_$][\\w$.-]*)(?=\\s*:))`);
  if (language.keywords?.length) source.push(`(?<keyword>\\b(?:${language.keywords.join("|")})\\b)`);
  if (language.controls?.length) source.push(`(?<control>\\b(?:${language.controls.join("|")})\\b)`);
  if (language.constants?.length) source.push(`(?<constant>\\b(?:${language.constants.join("|")})\\b)`);
  source.push("(?<number>\\b(?:0[xX][0-9a-fA-F]+|0[bB][01]+|\\d+(?:\\.\\d+)?(?:e[+-]?\\d+)?)\\b)");
  if (language.functions) source.push("(?<function>[A-Za-z_$][\\w$]*(?=\\s*\\())");
  if (!source.length) return [code];

  let pattern: RegExp;
  try {
    pattern = new RegExp(source.join("|"), "g");
  } catch {
    return [code];
  }
  return collectTokens(code, pattern, (groups) => {
    if (groups.comment) return "comment";
    if (groups.string) return "string";
    if (groups.property) return "property";
    if (groups.keyword) return "keyword";
    if (groups.control) return "control";
    if (groups.constant) return "constant";
    if (groups.number) return "number";
    if (groups.function) return "function";
    return "operator";
  });
}

function collectTokens(
  code: string,
  pattern: RegExp,
  classify: (groups: Record<string, string | undefined>) => TokenKind,
): ReactNode[] {
  const nodes: ReactNode[] = [];
  let cursor = 0;
  let index = 0;
  pattern.lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(code))) {
    if (match.index > cursor) nodes.push(code.slice(cursor, match.index));
    const groups = (match.groups || {}) as Record<string, string | undefined>;
    nodes.push(<span key={`token-${index++}`} className={tokenClass(classify(groups))}>{match[0]}</span>);
    cursor = pattern.lastIndex;
    if (pattern.lastIndex === match.index) pattern.lastIndex += 1;
  }
  if (cursor < code.length) nodes.push(code.slice(cursor));
  return nodes;
}

export function DiscordCodeBlock({ code, language = "" }: { code: string; language?: string }) {
  const spec = languageFor(language);
  const hasLanguage = Boolean(language.trim());
  return (
    <div className={`discord-md-codeblock${hasLanguage ? " has-language" : ""}`} data-language={spec.id}>
      {hasLanguage && <div className="discord-md-codeblock-head"><span>{spec.label}</span></div>}
      <pre className="discord-md-block-code"><code>{tokenSpans(code, spec)}</code></pre>
    </div>
  );
}
