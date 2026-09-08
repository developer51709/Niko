import { useState } from "react";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { CHANGELOG, getChangelogTags } from "../data/changelog";
import { navigate } from "../router";

export function ChangelogPage() {
  const [selectedTag, setSelectedTag] = useState<string>("");
  const tags = getChangelogTags();

  const filtered = selectedTag
    ? CHANGELOG.filter((e) => e.tags.includes(selectedTag))
    : CHANGELOG;

  return (
    <>
      <PublicHeader page="home" />
      <main className="shell page-main changelog-page">
        {/* Hero */}
        <div className="changelog-hero">
          <div className="eyebrow">
            <span className="status-dot" /> What's new
          </div>
          <h1 className="changelog-title">
            Changelog
            <br />
            <span className="title-accent">& updates</span>
          </h1>
          <p className="changelog-subtitle">
            A record of every improvement, fix, and new feature added to Niko.
            Grouped by release for clarity.
          </p>
        </div>

        {/* Tags */}
        <div className="changelog-tags">
          <button
            className={`changelog-tag-btn ${selectedTag === "" ? "active" : ""}`}
            onClick={() => setSelectedTag("")}
          >
            All
          </button>
          {tags.slice(0, 12).map((tag) => (
            <button
              key={tag}
              className={`changelog-tag-btn ${selectedTag === tag ? "active" : ""}`}
              onClick={() => setSelectedTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>

        {/* Timeline */}
        <div className="changelog-timeline">
          {filtered.map((entry, idx) => (
            <article key={entry.slug} className="changelog-entry">
              <div className="changelog-entry-date-col">
                <div className="changelog-date-dot" />
                {idx < filtered.length - 1 && (
                  <div className="changelog-date-line" />
                )}
              </div>
              <div className="changelog-entry-card">
                <div className="changelog-entry-header">
                  <div className="changelog-entry-meta">
                    <time className="changelog-entry-date">
                      {new Date(entry.date).toLocaleDateString("en-US", {
                        month: "long",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </time>
                    {entry.version && (
                      <span className="changelog-version">v{entry.version}</span>
                    )}
                  </div>
                  <h2 className="changelog-entry-title">{entry.title}</h2>
                  <p className="changelog-entry-summary">{entry.summary}</p>
                </div>

                {/* Highlights preview */}
                <div className="changelog-entry-highlights">
                  {entry.highlights.slice(0, 2).map((h) => (
                    <div key={h.title} className="changelog-highlight-mini">
                      <span className="highlight-mini-icon">
                        <Icon
                          name={
                            h.icon as
                              | "spark"
                              | "chart"
                              | "shield"
                              | "users"
                              | "settings"
                              | "utility"
                              | "doc"
                          }
                          size={16}
                        />
                      </span>
                      <div>
                        <strong>{h.title}</strong>
                        <p>{h.description.slice(0, 120)}...</p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Tags */}
                <div className="changelog-entry-tags">
                  {entry.tags.map((tag) => (
                    <span key={tag} className="changelog-tag">
                      {tag}
                    </span>
                  ))}
                </div>

                <button
                  className="changelog-read-more"
                  onClick={() => {
                    navigate(`/changelog/${entry.slug}`);
                  }}
                >
                  Read full release notes <Icon name="arrow" size={14} />
                </button>
              </div>
            </article>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="changelog-empty">
            <Icon name="doc" size={40} />
            <p>No changelog entries match this filter.</p>
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}
