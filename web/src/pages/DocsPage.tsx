import { useState, useEffect, useMemo } from "react";
import { PublicHeader } from "../components/PublicHeader";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { DocSearchBar } from "../components/DocSearchBar";
import { DocFilters } from "../components/DocFilters";
import { DocCard } from "../components/DocCard";
import { useDocSearch, useTagCloud } from "../hooks/useDocSearch";
import { DOC_SECTIONS, DOCS } from "../data/docs";
import type { DocCategory } from "../types";
import { navigate } from "../router";

export { DocsSlugPage } from "./DocsSlugPage";

export function DocsPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [selectedSection, setSelectedSection] = useState<string>("");
  const [showResults, setShowResults] = useState(false);

  const {
    filters,
    setQuery,
    setCategory,
    toggleTag,
    clearFilters,
    results,
    hasActiveFilters,
    resultCount,
  } = useDocSearch();

  const tagCloud = useTagCloud();

  // Handle URL hash for deep linking
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash.startsWith("#/docs/")) {
        const slug = hash.replace("#/docs/", "");
        const doc = DOCS.find((d) => d.slug === slug);
        if (doc) {
          setSelectedSection(doc.category);
          setCategory(doc.category as DocCategory);
        }
      }
    };

    handleHashChange();
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const handleSearchFocus = () => {
    setShowResults(true);
  };

  const handleCategoryChange = (category: DocCategory | "") => {
    setSelectedSection(category);
    setCategory(category);
    setMobileMenuOpen(false);
  };

  const handleSearchBlur = () => {
    // Keep results visible if there's a query
    if (!filters.query) {
      setShowResults(false);
    }
  };

  const handleResultClick = (slug: string) => {
    navigate(`/docs/${slug}`);
    setQuery("");
    setShowResults(false);
  };

  // Group results by category for display
  const groupedResults = useMemo(() => {
    const groups: Record<string, typeof results> = {};
    results.forEach((result) => {
      const category = result.page.category;
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(result);
    });
    return groups;
  }, [results]);

  return (
    <>
      <PublicHeader page="docs" />
      <main className="shell page-main docs-page">
        {/* Hero Section */}
        <div className="docs-hero">
          <div className="docs-hero-content">
            <div className="eyebrow docs-eyebrow">Documentation Center</div>
            <h1 className="docs-title">
              Everything you need to know about
              <br />
              <span className="title-accent">using Niko</span>
            </h1>
            <p className="docs-subtitle">
              Comprehensive guides, command references, and tips to help you
              get the most out of your server bot.
            </p>
          </div>
        </div>

        {/* Search Section */}
        <div className={`docs-search-section ${showResults ? "active" : ""}`}>
          <div className="docs-search-container">
            <DocSearchBar
              value={filters.query}
              onChange={setQuery}
              placeholder="Search documentation, commands, guides..."
              onFocus={handleSearchFocus}
              onBlur={handleSearchBlur}
            />

            {/* Results Dropdown */}
            {showResults && filters.query && results.length > 0 && (
              <div className="search-results-dropdown">
                <div className="search-results-header">
                  <span className="results-count">
                    {resultCount} {resultCount === 1 ? "result" : "results"}
                  </span>
                  <button
                    className="clear-search-btn"
                    onClick={() => {
              setQuery("");
              clearFilters();
              setSelectedSection("");
                    }}
                  >
                    Clear
                  </button>
                </div>
                <div className="search-results-list">
                  {results.slice(0, 8).map((result, index) => (
                    <button
                      key={result.page.slug}
                      className="search-result-item"
                      onClick={() => handleResultClick(result.page.slug)}
                      onMouseEnter={() => {}}
                    >
                      <div className="result-icon">
                        <Icon name="doc" size={18} />
                      </div>
                      <div className="result-content">
                        <div className="result-title">{result.page.title}</div>
                        <div className="result-excerpt">{result.page.excerpt}</div>
                        {result.highlights.length > 0 && (
                          <div className="result-highlight">
                            {result.highlights[0].slice(0, 100)}...
                          </div>
                        )}
                      </div>
                      <Icon name="arrow" size={14} className="result-arrow" />
                    </button>
                  ))}
                </div>
                {results.length > 8 && (
                  <div className="search-results-footer">
                    <span>
                      Showing 8 of {results.length} results. Browse all docs below.
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="docs-mobile-nav">
          <button
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle documentation menu"
          >
            <Icon name="utility" size={20} />
          </button>
          {mobileMenuOpen && (
            <div className="mobile-nav-panel">
              <div className="mobile-nav-header">
                <h3>Documentation</h3>
                <button
                  className="close-menu-btn"
                  onClick={() => setMobileMenuOpen(false)}
                  aria-label="Close menu"
                >
                  <Icon name="utility" size={16} className="rotated" />
                </button>
              </div>
              <div className="mobile-nav-sections">
                {DOC_SECTIONS.map((section) => (
                  <button
                    key={section.id}
                    className={`mobile-nav-item ${selectedSection === section.id ? "active" : ""}`}
                    onClick={() => {
                      handleCategoryChange(section.id as DocCategory);
                    }}
                  >
                    <Icon
                      name={
                        section.icon as "icon_home" | "icon_settings" | "icon_economy" | "icon_leveling" | "icon_moderation" | "icon_automod" | "icon_heart" | "icon_utility" | "icon_bot" | "icon_ai" | "icon_lightbulb"
                      }
                      size={18}
                    />
                    <span className="mobile-section-label">{section.label}</span>
                    <span className="mobile-section-count">{section.count}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Tags Cloud */}
        {tagCloud.length > 0 && !hasActiveFilters && (
          <div className="docs-tags-cloud">
            <div className="tags-cloud-title">
              <Icon name="utility" size={16} />
              <span>Popular Topics</span>
            </div>
            <div className="tags-cloud-list">
              {tagCloud.slice(0, 15).map(({ tag, count }) => (
                <button
                  key={tag}
                  className="tag-cloud-item"
                  onClick={() => toggleTag(tag)}
                  style={{
                    fontSize: `${0.75 + Math.min(count / 4, 1)}rem`,
                  }}
                >
                  #{tag}
                  <span className="tag-count">{count}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Category Filters */}
        <div className="docs-category-filters">
          <DocFilters
            selectedCategory={filters.category}
            onSelectCategory={handleCategoryChange}
            sections={DOC_SECTIONS}
          />
        </div>

        {/* Results Header */}
        {hasActiveFilters && (
          <div className="docs-results-header">
            <div className="results-info">
              <span className="results-count-large">
                {resultCount} {resultCount === 1 ? "article" : "articles"}
              </span>
              {filters.query && (
                <span className="search-query-display">
                  for "<strong>{filters.query}</strong>"
                </span>
              )}
            </div>
            <button
              className="clear-all-btn"
              onClick={() => {
                clearFilters();
                setSelectedSection("");
              }}
              disabled={!hasActiveFilters}
            >
              <Icon name="utility" size={14} />
              Clear all filters
            </button>
          </div>
        )}

        {/* Documentation Content */}
        <div className="docs-content">
          {hasActiveFilters ? (
            /* Search Results View */
            <div className="search-results-view">
              {Object.entries(groupedResults).map(([category, categoryResults]) => (
                <section key={category} className="results-category">
                  <h2 className="category-title">
                    {DOC_SECTIONS.find((s) => s.id === category)?.label || category}
                  </h2>
                  <div className="category-results-grid">
                    {categoryResults.map((result) => (
                      <DocCard key={result.page.slug} doc={result} variant="highlighted" />
                    ))}
                  </div>
                </section>
              ))}
            </div>
          ) : selectedSection ? (
            /* Single Category View */
            <div className="category-view">
              <div className="category-header">
                <h2 className="category-page-title">
                  {DOC_SECTIONS.find((s) => s.id === selectedSection)?.label || selectedSection}
                </h2>
                <p className="category-description">
                  {DOC_SECTIONS.find((s) => s.id === selectedSection)?.description}
                </p>
              </div>
              <div className="category-articles">
                {DOCS
                  .filter((d) => d.category === selectedSection)
                  .sort((a, b) => a.order - b.order)
                  .map((doc) => (
                    <DocCard key={doc.slug} doc={doc} />
                  ))}
              </div>
            </div>
          ) : (
            /* All Categories View (Default) */
            <div className="all-categories-view">
              {DOC_SECTIONS.map((section) => (
                <section
                  key={section.id}
                  className="docs-section"
                  id={`section-${section.id}`}
                >
                  <div className="section-header">
                    <div className="section-icon">
                      <Icon
                        name={
                          section.icon as "icon_home" | "icon_settings" | "icon_economy" | "icon_leveling" | "icon_moderation" | "icon_automod" | "icon_heart" | "icon_utility" | "icon_bot" | "icon_ai" | "icon_lightbulb"
                        }
                        size={28}
                      />
                    </div>
                    <div className="section-info">
                      <h2 className="section-title">{section.label}</h2>
                      <p className="section-description">{section.description}</p>
                    </div>
                    <span className="section-count">{section.count}</span>
                  </div>
                  <div className="section-articles">
                    {DOCS
                      .filter((d) => d.category === section.id)
                      .sort((a, b) => a.order - b.order)
                      .map((doc) => (
                        <DocCard key={doc.slug} doc={doc} />
                      ))}
                  </div>
                </section>
              ))}
            </div>
          )}
        </div>

        {/* Footer Note */}
        <div className="docs-footer-note">
          <Icon name="book" size={20} />
          <div>
            <strong>Want more detail?</strong>
            <p>
              The repository includes setup, maintenance, intent verification,
              provider compatibility, and API documentation in the{" "}
              <a href="https://github.com/developer51709/Niko" target="_blank" rel="noreferrer">
                docs/
              </a>{" "}
              folder.
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}