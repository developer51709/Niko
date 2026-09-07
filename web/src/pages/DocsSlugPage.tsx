import { isValidElement, useEffect } from "react";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { DocFilters } from "../components/DocFilters";
import { useDocSearch } from "../hooks/useDocSearch";
import { DOC_SECTIONS, getDocBySlug } from "../data/docs";
import type { DocCategory } from "../types";
import { navigate } from "../router";

interface DocsSlugPageProps {
  slug: string;
}

export function DocsSlugPage({ slug }: DocsSlugPageProps) {
  const { setCategory, results, clearFilters } = useDocSearch();

  useEffect(() => {
    // Add hash to URL for deep linking
    if (window.location.hash !== `#/docs/${slug}`) {
      window.history.replaceState(null, "", `#/docs/${slug}`);
    }
  }, [slug]);

  const page = getDocBySlug(slug);

  if (!page) {
    return (
      <>
        <PublicHeader page="docs" />
        <main className="shell page-main docs-page">
          <div className="docs-not-found">
            <Icon name="doc" size={48} className="not-found-icon" />
            <h1>Page Not Found</h1>
            <p>We couldn't find documentation for "{slug}".</p>
            <div className="not-found-actions">
              <button onClick={() => navigate("/docs")}>
                Browse all documentation
              </button>
              <button
                onClick={() => {
                  navigate("/docs");
                  clearFilters();
                }}
              >
                Clear filters
              </button>
            </div>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  // Inline markdown: bold, italic, inline code, and links
  const renderInline = (text: string): React.ReactNode[] => {
    const nodes: React.ReactNode[] = [];
    const pattern = /(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;
    let key = 0;
    while ((match = pattern.exec(text)) !== null) {
      if (match.index > lastIndex) {
        nodes.push(text.slice(lastIndex, match.index));
      }
      const token = match[0];
      if (token.startsWith("`") && token.endsWith("`") && token.length > 2) {
        nodes.push(<code key={key++} className="doc-inline-code">{token.slice(1, -1)}</code>);
      } else if (token.startsWith("[")) {
        const link = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
        if (link) {
          nodes.push(
            <a key={key++} href={link[2]} target="_blank" rel="noreferrer">
              {renderInline(link[1])}
            </a>
          );
        } else {
          nodes.push(token);
        }
      } else if (token.startsWith("**")) {
        nodes.push(<strong key={key++}>{renderInline(token.slice(2, -2))}</strong>);
      } else if (token.startsWith("*")) {
        nodes.push(<em key={key++}>{renderInline(token.slice(1, -1))}</em>);
      } else {
        nodes.push(token);
      }
      lastIndex = match.index + token.length;
    }
    if (lastIndex < text.length) {
      nodes.push(text.slice(lastIndex));
    }
    return nodes;
  };

  // Parse markdown-like content (simple rendering)
  const renderContent = (content: string) => {
    const lines = content.split("\n");
    const elements: React.ReactNode[] = [];
    let i = 0;
    let listType: "ul" | "ol" | null = null;
    let listItems: string[] = [];

    const flushList = () => {
      if (listItems.length === 0) return;
      const Tag = listType === "ol" ? "ol" : "ul";
      elements.push(
        <Tag
          key={`list-${elements.length}`}
          className={`doc-content-list ${listType === "ol" ? "doc-content-list-ol" : ""}`}
        >
          {listItems.map((item, j) => (
            <li key={j}>{renderInline(item)}</li>
          ))}
        </Tag>
      );
      listItems = [];
      listType = null;
    };

    const pushSpacer = () => {
      const last = elements[elements.length - 1];
      const alreadySpacer =
        isValidElement(last) &&
        (last.props as { className?: string } | undefined)?.className === "doc-content-spacer";
      if (!alreadySpacer) {
        elements.push(<div key={`spacer-${elements.length}`} className="doc-content-spacer" />);
      }
    };

    while (i < lines.length) {
      const line = lines[i];
      const trimmed = line.trim();

      // Empty line
      if (!trimmed) {
        flushList();
        pushSpacer();
        i += 1;
        continue;
      }

      // Fenced code block — consume through the closing fence so the block
      // content is not rendered a second time as plain paragraphs below it.
      if (trimmed.startsWith("```")) {
        flushList();
        const codeContent: string[] = [];
        let j = i + 1;
        while (j < lines.length && lines[j].trim() !== "```") {
          codeContent.push(lines[j]);
          j += 1;
        }
        elements.push(
          <pre key={`code-${i}`} className="doc-code-block">
            <code>{codeContent.join("\n")}</code>
          </pre>
        );
        i = j + 1; // skip past the closing fence
        continue;
      }

      // Table — consume consecutive pipe rows in one pass.
      if (trimmed.startsWith("|")) {
        flushList();
        const rows: string[][] = [];
        let j = i;
        while (j < lines.length && lines[j].trim().startsWith("|")) {
          const cells = lines[j]
            .trim()
            .replace(/^\|/, "")
            .replace(/\|$/, "")
            .split("|")
            .map((cell) => cell.trim());
          rows.push(cells);
          j += 1;
        }
        const isSeparatorRow =
          rows.length > 1 && rows[1].every((cell) => /^:?-{2,}:?$/.test(cell.replace(/\s+/g, "")));
        const header = rows[0];
        const body = isSeparatorRow ? rows.slice(2) : rows.slice(1);
        if (header.length > 1) {
          elements.push(
            <table key={`table-${i}`} className="doc-table">
              <thead>
                <tr>
                  {header.map((cell, c) => (
                    <th key={c}>{renderInline(cell)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {body.map((row, r) => (
                  <tr key={r}>
                    {row.map((cell, c) => (
                      <td key={c}>{renderInline(cell)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          );
        }
        i = j;
        continue;
      }

      // Headings (longest prefix first)
      if (trimmed.startsWith("### ")) {
        flushList();
        elements.push(
          <h4 key={`h-${i}`} className="doc-heading doc-heading-h4">
            {trimmed.slice(4)}
          </h4>
        );
        i += 1;
        continue;
      }
      if (trimmed.startsWith("## ")) {
        flushList();
        elements.push(
          <h3 key={`h-${i}`} className="doc-heading doc-heading-h3">
            {trimmed.slice(3)}
          </h3>
        );
        i += 1;
        continue;
      }
      if (trimmed.startsWith("# ")) {
        flushList();
        elements.push(
          <h2 key={`h-${i}`} className="doc-heading doc-heading-h2">
            {trimmed.slice(2)}
          </h2>
        );
        i += 1;
        continue;
      }

      // Blockquote
      if (trimmed.startsWith("> ")) {
        flushList();
        elements.push(
          <blockquote key={`q-${i}`} className="doc-blockquote">
            {renderInline(trimmed.slice(2))}
          </blockquote>
        );
        i += 1;
        continue;
      }

      // Bullet list item
      const ulMatch = trimmed.match(/^[-*]\s+(.*)$/);
      if (ulMatch) {
        if (listType !== "ul") flushList();
        listType = "ul";
        listItems.push(ulMatch[1]);
        i += 1;
        continue;
      }

      // Numbered list item
      const olMatch = trimmed.match(/^\d+\.\s+(.*)$/);
      if (olMatch) {
        if (listType !== "ol") flushList();
        listType = "ol";
        listItems.push(olMatch[1]);
        i += 1;
        continue;
      }

      // Regular paragraph
      flushList();
      elements.push(
        <p key={`p-${i}`} className="doc-paragraph">
          {renderInline(trimmed)}
        </p>
      );
      i += 1;
    }

    flushList();
    return elements;
  };

  const contentElements = renderContent(page.content);
  const tocHeadings = contentElements.filter(
    (el): el is React.ReactElement<{ className?: string; children?: React.ReactNode }> =>
      isValidElement(el) && (el.type === "h2" || el.type === "h3")
  );

  return (
    <>
      <PublicHeader page="docs" />
      <main className="shell page-main docs-page docs-detail-page">
        {/* Back Nav */}
        <div className="docs-detail-back">
          <button
            onClick={() => navigate("/docs")}
            className="back-button"
          >
            <Icon name="arrow" size={16} />
            Back to Documentation
          </button>
        </div>

        {/* Article Header */}
        <header className="doc-article-header">
          <div className="doc-article-meta">
            <span className="doc-category-badge">
              {DOC_SECTIONS.find((s) => s.id === page.category)?.label || page.category}
            </span>
            <span className="doc-order-badge">Article #{page.order}</span>
          </div>
          <h1 className="doc-article-title">{page.title}</h1>
          <p className="doc-article-excerpt">{page.excerpt}</p>

          <div className="doc-article-tags">
            {page.tags.map((tag) => (
              <span key={tag} className="doc-tag-pill">
                #{tag}
              </span>
            ))}
          </div>
        </header>

        {/* Article Content */}
        <article className="doc-article-content">
          {contentElements}
        </article>

        {/* Navigation Footer */}
        <footer className="doc-article-footer">
          <div className="doc-nav-container">
            <div className="doc-nav-col">
              <span className="doc-nav-label">Category</span>
              <button
                className="doc-nav-link"
                onClick={() => {
                  setCategory(page.category as DocCategory);
                  navigate("/docs");
                }}
              >
                <Icon name="arrow" size={14} />
                View all {DOC_SECTIONS.find((s) => s.id === page.category)?.label}
              </button>
            </div>
          </div>
        </footer>

        {/* Table of Contents */}
        {tocHeadings.length > 0 && (
          <aside className="doc-toc">
            <div className="toc-title">
              <Icon name="utility" size={16} />
              <span>On this page</span>
            </div>
            <nav className="toc-nav">
              {tocHeadings.map((el, i) => {
                  const isH2 = el.props.className?.includes("doc-heading-h2");
                  return (
                    <a
                      key={i}
                      href={`#${isH2 ? "h2-" : "h3-"}-${i}`}
                      className={`toc-link ${isH2 ? "toc-h2" : "toc-h3"}`}
                    >
                      {el.props.children}
                    </a>
                  );
                })}
            </nav>
          </aside>
        )}
      </main>
      <Footer />
    </>
  );
}

// Route wrapper component
interface DocsRouteProps {
  slug: string;
}

export function DocsRoute({ slug }: DocsRouteProps) {
  return <DocsSlugPage slug={slug} />;
}