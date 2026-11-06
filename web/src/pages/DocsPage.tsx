import { useState, useEffect, useMemo } from "react";
import { PublicHeader } from "../components/PublicHeader";
import { PublicPageIntro } from "../components/PublicPageIntro";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { DocSearchBar } from "../components/DocSearchBar";
import { DocFilters } from "../components/DocFilters";
import { DocCard } from "../components/DocCard";
import { useDocSearch, useTagCloud } from "../hooks/useDocSearch";
import { useStrings } from "../i18n";
import { DOC_SECTIONS, DOCS } from "../data/docs";
import type { DocCategory } from "../types";
import { navigate } from "../router";

export { DocsSlugPage } from "./DocsSlugPage";

export function DocsPage() {
  const { t } = useStrings("docs");
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
    // Let a result button's click finish before unmounting the dropdown.
    // The query remains applied to the page; only its overlapping suggestions close.
    window.setTimeout(() => setShowResults(false), 180);
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
        <PublicPageIntro
          eyebrow={t("intro.eyebrow")}
          title={<>{t("intro.title")} <em>{t("intro.titleEm")}</em></>}
          description={t("intro.description")}
        />

        <a className="docs-developer-card" href="/developers" onClick={(event) => { event.preventDefault(); navigate("/developers"); }}>
          <span className="docs-developer-card-icon"><Icon name="terminal" size={18} /></span>
          <span><strong>Building an integration?</strong><small>API v1, scoped keys, and the developer policies live in a separate developer documentation portal.</small></span>
          <span className="docs-developer-card-link">Developer docs <Icon name="arrow" size={14} /></span>
        </a>

        {/* Search Section */}
        <div className={`docs-search-section ${showResults ? "active" : ""}`}>
          <div className="docs-search-container">
            <DocSearchBar
              value={filters.query}
              onChange={(value) => {
                setQuery(value);
                setShowResults(true);
              }}
              placeholder={t("search.placeholder")}
              ariaLabel={t("search.aria")}
              clearLabel={t("search.clear")}
              onFocus={handleSearchFocus}
              onBlur={handleSearchBlur}
              onEnter={() => setShowResults(false)}
            />

            {/* Results Dropdown */}
            {showResults && filters.query && results.length > 0 && (
              <div className="search-results-dropdown">
                <div className="search-results-header">
                  <span className="results-count">
                    {resultCount} {t(resultCount === 1 ? "count.result" : "count.results")}
                  </span>
                  <button
                    className="clear-search-btn"
                    onClick={() => {
              setQuery("");
              clearFilters();
              setSelectedSection("");
                    }}
                  >
                    {t("search.clear")}
                  </button>
                </div>
                <div className="search-results-list">
                  {results.slice(0, 8).map((result) => (
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
                      {t("search.showing", { count: results.length })}
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
            aria-label={t("menu.toggle")}
            aria-expanded={mobileMenuOpen}
          >
            <Icon name={mobileMenuOpen ? "close" : "menu"} size={20} />
          </button>
          {mobileMenuOpen && (
            <div className="mobile-nav-panel">
              <div className="mobile-nav-header">
                <h3>{t("menu.title")}</h3>
                <button
                  className="close-menu-btn"
                  onClick={() => setMobileMenuOpen(false)}
                  aria-label={t("menu.close")}
                >
                  <Icon name="close" size={15} />
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
              <Icon name="spark" size={14} />
              <span>{t("topics.title")}</span>
            </div>
            <div className="tags-cloud-list">
              {tagCloud.slice(0, 15).map(({ tag, count }) => (
                <button
                  key={tag}
                  className="tag-cloud-item"
                  onClick={() => toggleTag(tag)}
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
            allCategoriesLabel={t("filters.all")}
            ariaLabel={t("filters.aria")}
          />
        </div>

        {/* Results Header */}
        {hasActiveFilters && (
          <div className="docs-results-header">
            <div className="results-info">
              <span className="results-count-large">
                {resultCount} {t(resultCount === 1 ? "count.article" : "count.articles")}
              </span>
              {filters.query && (
                <span className="search-query-display">
                  {t("results.for")} "<strong>{filters.query}</strong>"
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
              <Icon name="close" size={13} />
              {t("results.clearAll")}
            </button>
          </div>
        )}

        {/* Documentation Content */}
        <div className="docs-content">
          {hasActiveFilters ? (
            !results.length ? (
              <div className="docs-empty">
                <span className="docs-empty-icon" aria-hidden="true"><Icon name="search" size={16} /></span>
                <strong>{t("empty.title")} {filters.query ? `“${filters.query}”` : t("empty.filters")}</strong>
                <p>{t("empty.body")}</p>
                <button className="button button-muted button-small" type="button" onClick={() => { clearFilters(); setSelectedSection(""); }}>
                  {t("empty.clear")}
                </button>
              </div>
            ) : (
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
            )
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
            <strong>{t("footer.title")}</strong>
            <p>
              {t("footer.bodyBefore")}{" "}
              <a href="https://github.com/developer51709/Niko" target="_blank" rel="noreferrer">
                docs/
              </a>{" "}
              {t("footer.bodyAfter")}
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}