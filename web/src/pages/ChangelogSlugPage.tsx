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
        {chart.type === "donut" && <DonutChart chart={chart} />}
        {chart.type === "line" && <LineChart chart={chart} />}
        {chart.type === "timeline" && <TimelineChart chart={chart} />}
        {chart.type === "comparison" && <ComparisonChart chart={chart} />}
        {chart.type === "metrics" && <MetricsChart chart={chart} />}
      </div>
    </section>
  );
}

function BarChart({ chart }: { chart: Extract<ChangelogChart, { type: "bar" }> }) {
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

function PieChart({ chart }: { chart: Extract<ChangelogChart, { type: "pie" }> }) {
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

function DonutChart({ chart }: { chart: Extract<ChangelogChart, { type: "donut" }> }) {
  const total = chart.data.reduce((sum, item) => sum + item.value, 0);
  const stops = chart.data.reduce<{ css: string; current: number }>(
    (result, item) => {
      const start = (result.current / total) * 100;
      const end = ((result.current + item.value) / total) * 100;
      result.css += `${item.color || "#d96545"} ${start}% ${end}%, `;
      result.current += item.value;
      return result;
    },
    { css: "", current: 0 },
  ).css.slice(0, -2);

  return (
    <div className="chart-donut-wrapper">
      <div className="chart-donut" style={{ background: `conic-gradient(${stops})` }}>
        <span>{chart.centerLabel || total}</span>
      </div>
      <div className="chart-pie-legend">
        {chart.data.map((item) => (
          <div key={item.label} className="chart-legend-item">
            <span className="chart-legend-dot" style={{ background: item.color || "var(--accent)" }} />
            <span className="chart-legend-label">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function LineChart({ chart }: { chart: Extract<ChangelogChart, { type: "line" }> }) {
  const max = Math.max(...chart.data.map((item) => item.value), 1);
  const points = chart.data
    .map((item, index) => {
      const x = chart.data.length === 1 ? 50 : (index / (chart.data.length - 1)) * 100;
      const y = 100 - (item.value / max) * 82 - 9;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="chart-line-wrapper">
      <svg className="chart-line" viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label={chart.title}>
        <polyline points={points} fill="none" stroke="var(--accent)" strokeWidth="3" vectorEffect="non-scaling-stroke" />
        {chart.data.map((item, index) => {
          const x = chart.data.length === 1 ? 50 : (index / (chart.data.length - 1)) * 100;
          const y = 100 - (item.value / max) * 82 - 9;
          return <circle key={item.label} cx={x} cy={y} r="3" fill="var(--accent)" vectorEffect="non-scaling-stroke" />;
        })}
      </svg>
      <div className="chart-line-labels">
        {chart.data.map((item) => <span key={item.label}>{item.label}</span>)}
      </div>
    </div>
  );
}

function TimelineChart({ chart }: { chart: Extract<ChangelogChart, { type: "timeline" }> }) {
  const max = Math.max(...chart.data.map((item) => item.value), 1);
  return (
    <div className="chart-timeline">
      {chart.data.map((item) => (
        <div key={item.label} className="chart-timeline-item">
          <div className="chart-timeline-marker" style={{ background: item.color || "var(--accent)" }} />
          <div className="chart-timeline-content">
            <strong>{item.label}</strong>
            <div className="chart-timeline-track">
              <div className="chart-timeline-fill" style={{ width: `${(item.value / max) * 100}%`, background: item.color || "var(--accent)" }} />
            </div>
            {item.detail && <span>{item.detail}</span>}
          </div>
        </div>
      ))}
    </div>
  );
}

function MetricsChart({ chart }: { chart: Extract<ChangelogChart, { type: "metrics" }> }) {
  return (
    <div className="chart-metrics">
      {chart.data.map((item) => (
        <div key={item.label} className="chart-metric" style={{ borderTopColor: item.color || "var(--accent)" }}>
          <span className="chart-metric-label">{item.label}</span>
          <strong>{item.value}</strong>
          {item.detail && <small>{item.detail}</small>}
        </div>
      ))}
    </div>
  );
}

function ComparisonChart({ chart }: { chart: Extract<ChangelogChart, { type: "comparison" }> }) {
  const max = Math.max(...chart.before.concat(chart.after).map((item) => item.value), 1);
  const renderColumn = (title: string, items: typeof chart.before, className: string) => (
    <div className="chart-comparison-col">
      <h4 className={`comparison-label ${className}`}>{title}</h4>
      {items.map((item) => (
        <div key={item.label} className="chart-bar-row">
          <span className="chart-bar-label">{item.label}</span>
          <div className="chart-bar-track">
            <div className="chart-bar-fill" style={{ width: `${(item.value / max) * 100}%`, background: item.color || "var(--accent)" }} />
            <span className="chart-bar-value">{item.value}</span>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="chart-comparison">
      {renderColumn("Before", chart.before, "comparison-before")}
      <div className="chart-comparison-divider"><Icon name="arrow" size={20} /></div>
      {renderColumn("After", chart.after, "comparison-after")}
    </div>
  );
}
