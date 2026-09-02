import { useEffect } from "react";
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

  // Parse markdown-like content (simple rendering)
  const renderContent = (content: string) => {
    const lines = content.split("\n");
    const elements: React.ReactNode[] = [];
    let inList = false;
    let listItems: string[] = [];

    const flushList = () => {
      if (listItems.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} className="doc-content-list">
            {listItems.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        );
        listItems = [];
        inList = false;
      }
    };

    lines.forEach((line, index) => {
      const trimmed = line.trim();

      // Empty line
      if (!trimmed) {
        flushList();
        elements.push(<div key={index} className="doc-content-spacer" />);
        return;
      }

      // Headings
      if (trimmed.startsWith("# ")) {
        flushList();
        elements.push(
          <h2 key={index} className="doc-heading doc-heading-h2">
            {trimmed.slice(2)}
          </h2>
        );
        return;
      }
      if (trimmed.startsWith("## ")) {
        flushList();
        elements.push(
          <h3 key={index} className="doc-heading doc-heading-h3">
            {trimmed.slice(3)}
          </h3>
        );
        return;
      }
      if (trimmed.startsWith("### ")) {
        flushList();
        elements.push(
          <h4 key={index} className="doc-heading doc-heading-h4">
            {trimmed.slice(4)}
          </h4>
        );
        return;
      }

      // Blockquote
      if (trimmed.startsWith("> ")) {
        flushList();
        elements.push(
          <blockquote key={index} className="doc-blockquote">
            {trimmed.slice(2)}
          </blockquote>
        );
        return;
      }

      // Code block
      if (trimmed.startsWith("```")) {
        flushList();
        const codeContent: string[] = [];
        let isCodeBlock = true;
        let i = index + 1;
        while (i < lines.length && lines[i].trim() !== "```") {
          codeContent.push(lines[i]);
          i++;
        }
        elements.push(
          <pre key={index} className="doc-code-block">
            <code>{codeContent.join("\n")}</code>
          </pre>
        );
        return;
      }

      // Inline code
      if (trimmed.startsWith("`") && trimmed.endsWith("`") && trimmed.length > 2) {
        flushList();
        elements.push(
          <code key={index} className="doc-inline-code">
            {trimmed.slice(1, -1)}
          </code>
        );
        return;
      }

      // List item
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        inList = true;
        listItems.push(trimmed.slice(2));
        return;
      }

      // Numbered list
      if (/^\d+\.\s/.test(trimmed)) {
        inList = true;
        listItems.push(trimmed.replace(/^\d+\.\s/, ""));
        return;
      }

      // Regular paragraph
      flushList();
      elements.push(
        <p key={index} className="doc-paragraph">
          {trimmed}
        </p>
      );
    });

    flushList();
    return elements;
  };

  const contentElements = renderContent(page.content);

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
        {contentElements.filter((el) => el.type === "h2" || el.type === "h3").length > 0 && (
          <aside className="doc-toc">
            <div className="toc-title">
              <Icon name="utility" size={16} />
              <span>On this page</span>
            </div>
            <nav className="toc-nav">
              {contentElements
                .filter((el): el is React.ReactElement<{ className?: string; children?: React.ReactNode }> => el.type === "h2" || el.type === "h3")
                .map((el, i) => {
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