import { useState } from "react";
import { navigate } from "../router";
import { Icon } from "./Icon";
import type { DocPage, SearchResult } from "../types";

interface DocCardProps {
  doc: DocPage | SearchResult;
  variant?: "default" | "compact" | "highlighted";
}

export function DocCard({ doc, variant = "default" }: DocCardProps) {
  const page = "page" in doc ? doc.page : doc;
  const [imageLoaded, setImageLoaded] = useState(false);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    navigate(`/docs/${page.slug}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      navigate(`/docs/${page.slug}`);
    }
  };

  if (variant === "compact") {
    return (
      <a
        href={`/docs/${page.slug}`}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className="doc-card-compact"
        tabIndex={0}
        role="button"
      >
        <div className="compact-content">
          <span className="compact-title">{page.title}</span>
          <span className="compact-excerpt">{page.excerpt}</span>
        </div>
      </a>
    );
  }

  const highlights = "highlights" in doc ? doc.highlights : [];

  return (
    <article className={`doc-card ${variant === "highlighted" ? "highlighted" : ""}`}>
      <div className={`doc-card-content ${imageLoaded ? "loaded" : ""}`}>
        <div className="doc-card-header">
          <span className="doc-category">{page.category.replace(/-/g, " ")}</span>
          <span className="doc-order">#{page.order}</span>
        </div>

        <h3 className="doc-title">{page.title}</h3>

        <p className="doc-excerpt">{page.excerpt}</p>

        {highlights.length > 0 && (
          <div className="doc-highlights">
            {highlights.slice(0, 2).map((highlight, i) => (
              <p key={i} className="highlight-snippet">
                {highlight.slice(0, 150)}
                {highlight.length > 150 ? "..." : ""}
              </p>
            ))}
          </div>
        )}

        <div className="doc-card-footer">
          <div className="doc-tags">
            {page.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="doc-tag">
                #{tag}
              </span>
            ))}
          </div>
          <a
            href={`/docs/${page.slug}`}
            onClick={handleClick}
            onKeyDown={handleKeyDown}
            className="doc-read-more"
          >
            Read more <Icon name="arrow" size={14} />
          </a>
        </div>
      </div>
    </article>
  );
}