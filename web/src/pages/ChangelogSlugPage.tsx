import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { getChangelogBySlug, type ChangelogChart, type ChangelogEntry } from "../data/changelog";
import { navigate } from "../router";

interface ChangelogSlugPageProps {
  slug: string;
}

export function ChangelogSlugPage({ slug }: ChangelogSlugPageProps) {
  const entry = getChangelogBySlug(slug);

  if (!entry) {
    return (
      <>
        <PublicHeader page="home" />
        <main className="shell page-main changelog-page">
          <div className="changelog-not-found">
            <Icon name="doc" size={48} />
            <h1>Entry Not Found</h1>
            <p>We couldn't find a changelog entry for "{slug}".</p>
            <button onClick={() => navigate("/changelog")}>
              View all changelog entries
            </button>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <PublicHeader page="home" />
      <main className="shell page-main changelog-page changelog-detail">
        {/* Back nav */}
        <div className="changelog-back">
          <button onClick={() => navigate("/changelog")} className="back-button">
            <Icon name="arrow" size={16} />
            Back to Changelog
          </button>
        </div>

        {/* Header */}
        <header className="changelog-detail-header">
          <div className="changelog-detail-meta">
            <time>
              {new Date(entry.date).toLocaleDateString("en-US", {
                month: "long",
                day: "numeric",
                year: "numeric",
              })}
            </time>
            {entry.version && <span className="changelog-version">v{entry.version}</span>}
          </div>
          <h1>{entry.title}</h1>
          <p className="changelog-detail-summary">{entry.summary}</p>
          <div className="changelog-detail-tags">
            {entry.tags.map((tag) => (
              <span key={tag} className="changelog-tag">{tag}</span>
            ))}
          </div>
        </header>

        {/* Highlights */}
        <section className="changelog-highlights-section">
          <h2 className="changelog-section-heading">Highlights</h2>
          <div className="changelog-highlights-grid">
            {entry.highlights.map((h) => (
              <div key={h.title} className="changelog-highlight-card">
                <span className="highlight-icon">
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
                    size={22}
                  />
                </span>
                <h3>{h.title}</h3>
                <p>{h.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Chart */}
        {entry.chart && <ChangelogChartSection chart={entry.chart} />}

        {/* Changes */}
        <section className="changelog-changes-section">
          <h2 className="changelog-section-heading">All Changes</h2>
          <div className="changelog-changes-grid">
            {entry.changes.map((group) => (
              <div key={group.category} className={`changelog-change-group changelog-change-${group.category}`}>
                <h3 className="change-group-title">
                  <span className={`change-badge change-badge-${group.category}`}>
                    {group.category}
                  </span>
                </h3>
                <ul>
                  {group.items.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Commits */}
        {entry.commits.length > 0 && (
          <section className="changelog-commits-section">
            <h2 className="changelog-section-heading">Commits</h2>
            <div className="changelog-commits-list">
              {entry.commits.map((c) => {
                const [hash, ...rest] = c.split(" ");
                return (
                  <div key={hash} className="changelog-commit">
                    <code className="commit-hash">{hash.slice(0, 7)}</code>
                    <span className="commit-msg">{rest.join(" ")}</span>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* Navigation */}
        <nav className="changelog-detail-nav">
          <button onClick={() => navigate("/changelog")}>
            <Icon name="arrow" size={14} />
            All releases
          </button>
        </nav>
      </main>
      <Footer />
    </>
  );
}

/* ── Chart Components ──────────────────────────────────────────────────────── */

function ChangelogChartSection({ chart }: { chart: ChangelogChart }) {
  return (
    <section className="changelog-chart-section">
      <h2 className="changelog-section-heading">{chart.title}</h2>
      <div className="changelog-chart-container">
        {chart.type === "bar" && <BarChart chart={chart} />}
        {chart.type === "pie" && <PieChart chart={chart} />}
        {chart.type === "comparison" && <ComparisonChart chart={chart} />}
        {chart.type === "line" && <BarChart chart={chart} />}
      </div>
    </section>
  );
}

function BarChart({ chart }: { chart: ChangelogChart }) {
  const max = Math.max(...chart.data.map((d) => d.value));
  return (
    <div className="chart-bar">
      {chart.data.map((d) => (
        <div key={d.label} className="chart-bar-row">
          <span className="chart-bar-label">{d.label}</span>
          <div className="chart-bar-track">
            <div
              className="chart-bar-fill"
              style={{
                width: `${(d.value / max) * 100}%`,
                background: d.color || "var(--accent)",
              }}
            />
            <span className="chart-bar-value">{d.value}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function PieChart({ chart }: { chart: ChangelogChart }) {
  const total = chart.data.reduce((s, d) => s + d.value, 0);
  let cumulative = 0;
  const segments = chart.data.map((d) => {
    const start = (cumulative / total) * 360;
    cumulative += d.value;
    const end = (cumulative / total) * 360;
    return { ...d, start, end };
  });

  const gradientStops = segments
    .map((s) => {
      const startPct = (s.start / 360) * 100;
      const endPct = (s.end / 360) * 100;
      return `${s.color || "#d96545"} ${startPct}% ${endPct}%`;
    })
    .join(", ");

  return (
    <div className="chart-pie-wrapper">
      <div
        className="chart-pie"
        style={{
          background: `conic-gradient(${gradientStops})`,
        }}
      />
      <div className="chart-pie-legend">
        {chart.data.map((d) => (
          <div key={d.label} className="chart-legend-item">
            <span
              className="chart-legend-dot"
              style={{ background: d.color || "var(--accent)" }}
            />
            <span className="chart-legend-label">{d.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ComparisonChart({ chart }: { chart: ChangelogChart }) {
  const mid = Math.ceil(chart.data.length / 2);
  const before = chart.data.slice(0, mid);
  const after = chart.data.slice(mid);
  const max = Math.max(...chart.data.map((d) => d.value));

  return (
    <div className="chart-comparison">
      <div className="chart-comparison-col">
        <h4 className="comparison-label comparison-before">Before</h4>
        {before.map((d) => (
          <div key={d.label} className="chart-bar-row">
            <span className="chart-bar-label">{d.label}</span>
            <div className="chart-bar-track">
              <div
                className="chart-bar-fill"
                style={{
                  width: `${(d.value / max) * 100}%`,
                  background: d.color || "var(--accent)",
                }}
              />
              <span className="chart-bar-value">{d.value}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="chart-comparison-divider">
        <Icon name="arrow" size={20} />
      </div>
      <div className="chart-comparison-col">
        <h4 className="comparison-label comparison-after">After</h4>
        {after.map((d) => (
          <div key={d.label} className="chart-bar-row">
            <span className="chart-bar-label">{d.label}</span>
            <div className="chart-bar-track">
              <div
                className="chart-bar-fill"
                style={{
                  width: `${(d.value / max) * 100}%`,
                  background: d.color || "var(--accent)",
                }}
              />
              <span className="chart-bar-value">{d.value}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
