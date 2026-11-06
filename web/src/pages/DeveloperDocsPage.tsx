import { useEffect, useState } from "react";
import { DeveloperDocsLink } from "../components/DeveloperDocsLink";
import { Icon } from "../components/Icon";
import { currentPath } from "../router";
import {
  DEVELOPER_DOCS_BY_SLUG,
  DEVELOPER_DOCS_NAV,
  DEVELOPER_DOCS_ORDER,
  type DeveloperDocsPageData,
} from "./developerDocsContent";

function notFoundPage(): DeveloperDocsPageData {
  return {
    slug: "__not-found__",
    title: "Page not found",
    description: "This route is not part of the Niko developer documentation.",
    eyebrow: "Developer docs",
    toc: [],
    body: (
      <div className="devdocs-not-found">
        <span><Icon name="search" size={18} /></span>
        <h2>That page does not exist.</h2>
        <p>It may have moved, or the link may be incomplete. The API reference and quickstart are good places to continue.</p>
        <div className="devdocs-next-grid">
          <DeveloperDocsLink to="/developers">Introduction <Icon name="arrow" size={14} /></DeveloperDocsLink>
          <DeveloperDocsLink to="/developers/endpoints">API reference <Icon name="arrow" size={14} /></DeveloperDocsLink>
          <DeveloperDocsLink to="/developers/quickstart">Quickstart <Icon name="arrow" size={14} /></DeveloperDocsLink>
        </div>
      </div>
    ),
  };
}

function docSlug(pathname: string) {
  const parts = pathname.split("/").filter(Boolean);
  return parts[0] === "developers" ? parts.slice(1).join("/") : "";
}

export function DeveloperDocsPage() {
  const [pathname, setPathname] = useState(currentPath);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const syncPath = () => setPathname(currentPath());
    window.addEventListener("popstate", syncPath);
    return () => window.removeEventListener("popstate", syncPath);
  }, []);

  const slug = docSlug(pathname);
  const page = DEVELOPER_DOCS_BY_SLUG.get(slug) || notFoundPage();
  const activeIndex = DEVELOPER_DOCS_ORDER.findIndex((item) => item.slug === page.slug);
  const previous = activeIndex > 0 ? DEVELOPER_DOCS_ORDER[activeIndex - 1] : null;
  const next = activeIndex >= 0 && activeIndex < DEVELOPER_DOCS_ORDER.length - 1
    ? DEVELOPER_DOCS_ORDER[activeIndex + 1]
    : null;

  useEffect(() => {
    document.title = page.slug === "__not-found__"
      ? "Page not found — Niko developer docs"
      : page.slug === ""
        ? "Niko API v1 — Developer documentation"
        : `${page.title} — Niko API v1`;
    setMobileOpen(false);
    const hash = window.location.hash.replace(/^#/, "");
    if (hash) {
      window.requestAnimationFrame(() => document.getElementById(hash)?.scrollIntoView());
    } else {
      window.scrollTo({ top: 0 });
    }
  }, [pathname, page.slug, page.title]);

  return (
    <div className="devdocs-shell">
      <header className="devdocs-topbar">
        <div className="devdocs-topbar-leading">
          <button
            className="devdocs-menu-button"
            type="button"
            aria-label={mobileOpen ? "Close developer docs navigation" : "Open developer docs navigation"}
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((open) => !open)}
          >
            <Icon name={mobileOpen ? "close" : "menu"} />
          </button>
          <DeveloperDocsLink to="/" className="devdocs-brand">
            <span className="devdocs-brand-mark">n</span>
            <span className="devdocs-brand-name"><strong>Niko</strong><small>Developers</small></span>
          </DeveloperDocsLink>
          <span className="devdocs-topbar-divider" />
          <span className="devdocs-topbar-product">API documentation</span>
        </div>
        <div className="devdocs-topbar-actions">
          <span className="devdocs-version-chip"><span className="status-dot" />v1 stable</span>
          <DeveloperDocsLink to="/docs" className="devdocs-topbar-link">Product docs</DeveloperDocsLink>
          <DeveloperDocsLink to="/dashboard/developer" className="devdocs-portal-button">
            Developer portal <Icon name="external" size={13} />
          </DeveloperDocsLink>
        </div>
      </header>

      <div className="devdocs-frame">
        <button
          className={`devdocs-sidebar-backdrop${mobileOpen ? " is-visible" : ""}`}
          type="button"
          aria-label="Close developer docs navigation"
          aria-hidden={!mobileOpen}
          tabIndex={mobileOpen ? 0 : -1}
          onClick={() => setMobileOpen(false)}
        />
        <aside className={`devdocs-sidebar${mobileOpen ? " is-open" : ""}`} aria-label="Developer documentation">
          <div className="devdocs-sidebar-head-mobile">
            <span>Developer docs</span>
            <button type="button" onClick={() => setMobileOpen(false)} aria-label="Close navigation"><Icon name="close" /></button>
          </div>
          <nav className="devdocs-nav">
            {DEVELOPER_DOCS_NAV.map((group) => (
              <div className="devdocs-nav-group" key={group.label}>
                <span className="devdocs-nav-label">{group.label}</span>
                {group.items.map((item) => (
                  <DeveloperDocsLink
                    key={item.slug || "introduction"}
                    to={item.slug ? `/developers/${item.slug}` : "/developers"}
                    className={`devdocs-nav-link${item.child ? " is-child" : ""}${page.slug === item.slug ? " active" : ""}`}
                    ariaCurrent={page.slug === item.slug ? "page" : undefined}
                  >
                    <span>{item.title}</span>
                    {page.slug === item.slug ? <span className="devdocs-nav-dot" /> : null}
                  </DeveloperDocsLink>
                ))}
              </div>
            ))}
          </nav>
          <div className="devdocs-sidebar-footer">
            <DeveloperDocsLink to="/" className="devdocs-site-link">
              <Icon name="back" size={14} />
              <span><strong>Main website</strong><small>niko.sryze.cc</small></span>
              <Icon name="external" size={12} />
            </DeveloperDocsLink>
            <DeveloperDocsLink to="/discord" className="devdocs-access-link">
              Need access? Join the support server <Icon name="arrow" size={13} />
            </DeveloperDocsLink>
            <span className="devdocs-sidebar-note">Developer docs are separate from the public Niko documentation.</span>
          </div>
        </aside>

        <div className="devdocs-main">
          <article className="devdocs-article">
            <div className="devdocs-breadcrumb">
              <DeveloperDocsLink to="/developers">Developer docs</DeveloperDocsLink>
              <span>/</span>
              <span>{page.eyebrow}</span>
            </div>

            <header className="devdocs-page-head">
              <div>
                <span className="devdocs-eyebrow">{page.eyebrow}</span>
                <h1>{page.title}{page.slug === "" ? <em>v1</em> : null}</h1>
                <p>{page.description}</p>
              </div>
              {page.slug === "" ? (
                <div className="devdocs-page-head-actions">
                  <DeveloperDocsLink to="/developers/quickstart" className="button button-primary button-small">
                    Get started <Icon name="arrow" size={14} />
                  </DeveloperDocsLink>
                  <DeveloperDocsLink to="/developers/endpoints" className="button button-muted button-small">
                    API reference
                  </DeveloperDocsLink>
                </div>
              ) : null}
            </header>

            <div className="devdocs-content">{page.body}</div>

            <nav className="devdocs-pager" aria-label="Developer documentation pages">
              {previous ? (
                <DeveloperDocsLink to={previous.slug ? `/developers/${previous.slug}` : "/developers"} className="devdocs-pager-link is-previous">
                  <span><Icon name="back" size={14} /> Previous</span>
                  <strong>{previous.title}</strong>
                </DeveloperDocsLink>
              ) : <span />}
              {next ? (
                <DeveloperDocsLink to={next.slug ? `/developers/${next.slug}` : "/developers"} className="devdocs-pager-link is-next">
                  <span>Next <Icon name="arrow" size={14} /></span>
                  <strong>{next.title}</strong>
                </DeveloperDocsLink>
              ) : null}
            </nav>

            <footer className="devdocs-article-footer">
              <span>Niko API v1 · Developer documentation</span>
              <DeveloperDocsLink to="/">Back to the main website <Icon name="external" size={12} /></DeveloperDocsLink>
            </footer>
          </article>

          {page.toc.length > 0 ? (
            <aside className="devdocs-toc" aria-label="On this page">
              <span>On this page</span>
              {page.toc.map((item) => <a key={item.id} href={`#${item.id}`}>{item.label}</a>)}
              <div className="devdocs-toc-footer">
                <Icon name="message" size={14} />
                <span>Questions? <DeveloperDocsLink to="/discord">Open a ticket</DeveloperDocsLink>.</span>
              </div>
            </aside>
          ) : null}
        </div>
      </div>
    </div>
  );
}
