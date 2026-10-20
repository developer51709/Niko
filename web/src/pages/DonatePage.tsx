import { useEffect } from "react";
import { PublicHeader } from "../components/PublicHeader";

/**
 * Legacy donation link.
 *
 * `/donate?token=…` used to render its own form with a hosted OxaPay invoice.
 * Donations now share the white-label checkout with premium, so old links and
 * the `/donate` command land on `/billing` with the signed token intact.
 */
export function DonatePage() {
  useEffect(() => {
    // A real navigation, not the SPA helper: this page's effect runs before the
    // app's popstate listener exists, so a pushState here would be swallowed.
    window.location.replace(`/billing${window.location.search}`);
  }, []);

  return (
    <>
      <PublicHeader page="home" />
      <main className="page-main">
        <div className="shell">
          <div className="docs-footer-note" role="status">
            <strong>Opening checkout</strong>
            <p>Taking you to the secure payment page…</p>
          </div>
        </div>
      </main>
    </>
  );
}
