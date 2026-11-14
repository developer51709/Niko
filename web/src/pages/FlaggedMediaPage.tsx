import { useEffect, useState } from "react";
import { Footer } from "../components/Footer";
import { PublicHeader } from "../components/PublicHeader";
import { useStrings } from "../i18n";

// The one place the flag slugs are named on this side of the project. They match
// `utils/safety/flagged_media.py`, the placeholder files under /assets/placeholders/
// and the `?type=` on the links the bot posts in a deleted-message log.
const FLAG_TYPES = ["explicit", "gore", "self-harm"] as const;
type FlagType = (typeof FLAG_TYPES)[number];

function flagFromQuery(): FlagType | null {
  const value = new URLSearchParams(window.location.search).get("type");
  return FLAG_TYPES.includes(value as FlagType) ? (value as FlagType) : null;
}

/**
 * Why a log entry shows a placeholder instead of a deleted image.
 *
 * This page exists to answer one question, so it is one panel of plain text: the
 * flag the log entry named, what it means, and what the log still kept. Without
 * a usable `?type=` it lists the three flags instead of guessing.
 */
export function FlaggedMediaPage() {
  const { t } = useStrings("flagged-media");
  // The flags are read from the query, so a link to another type on this page
  // updates it without leaving the route.
  const [flag, setFlag] = useState(flagFromQuery);
  useEffect(() => {
    const sync = () => setFlag(flagFromQuery());
    window.addEventListener("popstate", sync);
    return () => window.removeEventListener("popstate", sync);
  }, []);

  return (
    <>
      <PublicHeader page="flagged-media" />
      <main className="shell page-main flagged-page">
        <article className="flagged-panel">
          <div className="eyebrow">{t("hero.eyebrow")}</div>
          <h1>{t("hero.title")}</h1>
          <p className="flagged-lead">{t("hero.lead")}</p>

          {flag ? (
            <section className="flagged-detail">
              <h2>{t(`type.${flag}.name`)}</h2>
              <p>{t(`type.${flag}.what`)}</p>
            </section>
          ) : (
            <dl className="flagged-detail">
              {FLAG_TYPES.map((type) => (
                <div key={type}>
                  <dt>{t(`type.${type}.name`)}</dt>
                  <dd>{t(`type.${type}.what`)}</dd>
                </div>
              ))}
            </dl>
          )}

          <p className="flagged-note">{t("note.notStored")}</p>
          <p className="flagged-kept">{t("note.kept")}</p>
          <p className="flagged-support">
            {t("support.before")} <a href="/support">{t("support.link")}</a>.
          </p>
        </article>
      </main>
      <Footer />
    </>
  );
}
