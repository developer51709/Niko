import { useState } from "react";
import { DiscordMarkdown } from "../components/DiscordMarkdown";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { PublicPageIntro } from "../components/PublicPageIntro";
import { CHANGELOG, getChangelogTags } from "../data/changelog";
import { useStrings } from "../i18n";
import { navigate } from "../router";

/** Release prose is written in Discord's own markdown, so `code`, **bold** and
 *  *italic* read here exactly as they do in the client. Inline keeps it inside
 *  the paragraph the page already styles, and the mention popups are switched
 *  off because this is a public page rather than a transcript. */
export const renderChangelogMarkdown = (text: string) => (
  <DiscordMarkdown text={text} inline className="changelog-inline-markdown" interactiveUsers={false} />
);

export function ChangelogPage() {
  const { t } = useStrings("changelog");
  const [selectedTag, setSelectedTag] = useState<string>("");
  const tags = getChangelogTags();

  const filtered = selectedTag
    ? CHANGELOG.filter((e) => e.tags.includes(selectedTag))
    : CHANGELOG;

  return (
    <>
      <PublicHeader page="changelog" />
      <main className="shell page-main changelog-page">
        <PublicPageIntro
          eyebrow={t("intro.eyebrow")}
          title={<>{t("intro.title")} <em>{t("intro.titleEm")}</em></>}
          description={t("intro.description")}
        />

        {/* Tags */}
        <div className="changelog-tags">
          <button
            className={`changelog-tag-btn ${selectedTag === "" ? "active" : ""}`}
            onClick={() => setSelectedTag("")}
          >
            {t("filters.all")}
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
                  <p className="changelog-entry-summary">{renderChangelogMarkdown(entry.summary)}</p>
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
                        <p>{renderChangelogMarkdown(`${h.description.slice(0, 120)}...`)}</p>
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
                  {t("entry.readMore")} <Icon name="arrow" size={14} />
                </button>
              </div>
            </article>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="changelog-empty">
            <Icon name="doc" size={40} />
            <p>{t("empty")}</p>
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}
