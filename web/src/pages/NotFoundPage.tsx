import { Brand } from "../components/Brand";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useStrings } from "../i18n";
import { siteOrigin } from "../router";

/**
 * The two faces of a wrong address.
 *
 * `page` is a used host — the site's own domain or a subdomain it serves — with
 * a path that is not a page: everything around it still works, so it is shown
 * inside the normal chrome, with the paths that do work underneath. `subdomain`
 * is a host that serves no site at all; every relative link on it would land
 * back on this same 404, so it stands alone, carries the mark itself and links
 * out to the real site with absolute URLs.
 */
export function NotFoundPage({ variant }: { variant: "page" | "subdomain" }) {
  const { t } = useStrings("not-found");
  const { t: tShared } = useStrings("shared");
  const path = window.location.pathname;

  if (variant === "subdomain") {
    const site = siteOrigin();
    // No configured origin means the server could not name the real site; the
    // link then stays relative rather than inventing an address.
    const home = site ? `${site}/` : "/";
    const support = site ? `${site}/support` : "/support";
    const siteLabel = site.replace(/^https?:\/\//, "") || window.location.host;

    // No header or footer on a host that serves no site, so this card owns the
    // whole viewport instead of the space below the site chrome.
    return (
      <main className="shell page-main not-found-page not-found-page-alone">
        <section className="not-found-card not-found-card-alone">
          <div className="not-found-brand"><Brand /></div>
          <span className="not-found-code">{t("subdomain.eyebrow")}</span>
          <h1>{t("subdomain.title")}</h1>
          <p className="not-found-body">{t("subdomain.body")}</p>
          {/* The two addresses side by side: what was asked for, and where the
              site actually is. */}
          <p className="not-found-target" title={t("subdomain.hint", { host: window.location.host, site: siteLabel })}>
            <code>{window.location.host}</code>
            <Icon name="arrow" />
            <code>{siteLabel}</code>
          </p>
          <div className="not-found-actions">
            <a className="button button-primary" href={home}>{t("action.site")} <Icon name="arrow" /></a>
            <a className="button button-muted" href={support}>{t("action.support")}</a>
          </div>
        </section>
      </main>
    );
  }

  return (
    <>
      <PublicHeader page="not-found" />
      <main className="shell page-main not-found-page">
        <section className="not-found-card">
          <span className="not-found-code">{t("page.eyebrow")}</span>
          <h1>{t("page.title")}</h1>
          <p className="not-found-body">{t("page.body")}</p>
          {/* The address that missed, so a typo is visible without scrolling a
              long URL in the browser bar. */}
          <p className="not-found-target" title={t("page.hint", { path })}>
            <Icon name="link" />
            <code>{path}</code>
          </p>
          <div className="not-found-actions">
            <a className="button button-primary" href="/">{t("action.home")} <Icon name="arrow" /></a>
            <a className="button button-muted" href="/support">{t("action.support")}</a>
          </div>
          <nav className="not-found-links">
            <a href="/commands">{tShared("nav.commands")}</a>
            <a href="/docs">{tShared("nav.docs")}</a>
            <a href="/status">{tShared("nav.status")}</a>
            <a href="/changelog">{tShared("nav.changelog")}</a>
          </nav>
        </section>
      </main>
      <Footer />
    </>
  );
}
