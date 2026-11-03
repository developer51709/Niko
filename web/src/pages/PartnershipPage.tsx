import { useState } from "react";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";
import { useStrings } from "../i18n";

/** The link partners paste: one URL that Discord renders as the ad card. */
const AD_PATH = "/discord/partnership";

// Icon names stay here; the copy they sit beside lives in the catalogue.
const memberBenefits = [
  { icon: "shield", title: "benefits.calm.title", body: "benefits.calm.body" },
  { icon: "chart", title: "benefits.stay.title", body: "benefits.stay.body" },
  { icon: "message", title: "benefits.help.title", body: "benefits.help.body" },
];

const partnerBenefits = ["terms.benefits.1", "terms.benefits.2", "terms.benefits.3"];
const partnerExpectations = ["terms.expect.1", "terms.expect.2", "terms.expect.3"];

export function PartnershipPage() {
  const config = useBotConfig();
  const { t } = useStrings("partnership");
  const [copied, setCopied] = useState(false);
  const adLink = `${window.location.origin}${AD_PATH}`;

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(adLink);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      // A browser without clipboard access still shows the link below the
      // button, so nothing is lost by leaving the label alone.
    }
  };

  return (
    <>
      <PublicHeader page="support" />
      <main className="shell page-main partner-page">
        <section className="partner-hero">
          <div className="partner-hero-copy">
            <div className="eyebrow">{t("hero.eyebrow")}</div>
            <h1>{t("hero.titleA")}<br /><em>{t("hero.titleEm")}</em></h1>
            <p>{t("hero.body")}</p>
            <div className="partner-actions">
              <button type="button" className="button button-primary" onClick={() => void copyLink()}>
                {t(copied ? "hero.copied" : "hero.copy")} <Icon name="arrow" />
              </button>
              <a className="button button-muted" href="/discord">{t("hero.support")}</a>
            </div>
            <div className="partner-link-field">
              <span>{adLink}</span>
              <a href={AD_PATH}>{t("link.open")} <Icon name="external" /></a>
            </div>
            <p className="partner-note">{t("hero.note")}</p>
          </div>

          {/* The card as Discord draws it from the link: the same sections, the
              same buttons. It is the whole advertisement, so it leads the page. */}
          <div className="partner-card" aria-label={t("card.aria")}>
            <div className="partner-card-inner">
              <div className="partner-card-head">
                <span className="partner-card-mark">n</span>
                <div>
                  <strong>{t("card.title")}</strong>
                  <small>{t("card.subtitle")}</small>
                </div>
              </div>
              <p className="partner-card-lead">{t("card.lead")}</p>
              <div className="partner-card-section">
                <p className="partner-card-heading">{t("card.membersTitle")}</p>
                <ul>
                  <li><b>{t("card.members.calm")}</b> — {t("card.members.calm.body")}</li>
                  <li><b>{t("card.members.stay")}</b> — {t("card.members.stay.body")}</li>
                  <li><b>{t("card.members.help")}</b> — {t("card.members.help.body")}</li>
                </ul>
              </div>
              <div className="partner-card-rule" />
              <div className="partner-card-section">
                <p className="partner-card-heading">{t("card.partnersTitle")}</p>
                <ul>
                  <li>{t("card.partners.listing")}</li>
                  <li>{t("card.partners.shoutout")}</li>
                </ul>
              </div>
              <div className="partner-card-gallery">
                <span /><span />
              </div>
              <div className="partner-card-buttons">
                <span>{t("card.buttons.add")}</span><span>{t("card.buttons.partner")}</span><span>{t("card.buttons.server")}</span>
              </div>
            </div>
            <span className="partner-card-caption">{t("card.caption")}</span>
          </div>
        </section>

        <section className="partner-section">
          <div className="partner-section-heading">
            <div className="section-kicker">{t("section.kicker")}</div>
            <h2>{t("section.title")}</h2>
            <p>{t("section.body")}</p>
          </div>
          <div className="partner-grid">
            {memberBenefits.map((benefit) => (
              <article className="partner-tile" key={benefit.title}>
                <span className="partner-tile-icon"><Icon name={benefit.icon} /></span>
                <h3>{t(benefit.title)}</h3>
                <p>{t(benefit.body)}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="partner-section partner-terms">
          <article className="partner-terms-card">
            <div className="section-kicker">{t("terms.get.kicker")}</div>
            <h2>{t("terms.get.title")}</h2>
            <ul>
              {partnerBenefits.map((key) => <li key={key}>{t(key)}</li>)}
            </ul>
          </article>
          <article className="partner-terms-card">
            <div className="section-kicker">{t("terms.look.kicker")}</div>
            <h2>{t("terms.look.title")}</h2>
            <ul>
              {partnerExpectations.map((key) => <li key={key}>{t(key)}</li>)}
            </ul>
          </article>
        </section>

        <section className="partner-cta">
          <div>
            <div className="section-kicker">{t("cta.kicker")}</div>
            <h2>{t("cta.titleA")}<br />{t("cta.titleB")}</h2>
            <p>{t("cta.body")}</p>
          </div>
          <div className="partner-cta-actions">
            <a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">
              {t("cta.add")} <Icon name="external" />
            </a>
            <a className="button button-muted" href="/discord">{t("cta.support")} <Icon name="arrow" /></a>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
