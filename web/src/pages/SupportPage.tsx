import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useBotConfig } from "../hooks/useBotConfig";
import { Footer } from "../components/Footer";
import { PublicHeader } from "../components/PublicHeader";
import { Icon } from "../components/Icon";
import { SupportLink } from "../components/SupportLink";
import { useStrings } from "../i18n";

// The FAQ is page copy, so it is built from the catalogue. Two answers point at
// the support server mid-sentence, which is why they are split around the link
// rather than baked into one string.
function useFaqItems() {
  const { t } = useStrings("support");

  return useMemo<{ question: string; answer: ReactNode; docsLink?: boolean }[]>(() => [
    { question: t("faq.invite.question"), answer: t("faq.invite.answer") },
    { question: t("faq.setup.question"), answer: t("faq.setup.answer"), docsLink: true },
    { question: t("faq.broken.question"), answer: <>{t("faq.broken.before")} <SupportLink />.</> },
    { question: t("faq.bug.question"), answer: <>{t("faq.bug.before")} <SupportLink /> {t("faq.bug.after")}</> },
    { question: t("faq.data.question"), answer: <>{t("faq.data.before")} <SupportLink /> {t("faq.data.after")}</> },
  ], [t]);
}

export function SupportPage() {
  const config = useBotConfig();
  const { t } = useStrings("support");
  const supportUrl = config?.support_server_url?.trim();
  const [openFaq, setOpenFaq] = useState<number | null>(0);
  const faqItems = useFaqItems();

  return (
    <>
      <PublicHeader page="support" />
      <main className="shell page-main support-page">
        <section className="support-hero">
          <div className="eyebrow">{t("hero.eyebrow")}</div>
          <h1>{t("hero.title")} <em>{t("hero.titleEm")}</em></h1>
          <p>{t("hero.body")}</p>
          <div className="support-actions">
            <a className="button button-primary" href="/docs">{t("hero.docs")} <Icon name="arrow" /></a>
            {supportUrl && <a className="button button-muted" href="/discord">{t("hero.discord")} <Icon name="arrow" /></a>}
          </div>
        </section>

        <section className="support-faq" aria-labelledby="support-faq-title">
          <div className="support-section-heading">
            <div><div className="eyebrow">{t("faq.eyebrow")}</div><h2 id="support-faq-title">{t("faq.title")}</h2></div>
            <span className="support-faq-count">{t("faq.count", { count: faqItems.length })}</span>
          </div>
          <div className="support-faq-list">
            {faqItems.map((item, index) => {
              const expanded = openFaq === index;
              const answerId = `support-faq-answer-${index}`;
              return <article className={`support-faq-item${expanded ? " is-open" : ""}`} key={item.question}>
                <h3><button type="button" aria-expanded={expanded} aria-controls={answerId} onClick={() => setOpenFaq(expanded ? null : index)}>
                  <span className="support-faq-question"><span className="support-faq-number">{String(index + 1).padStart(2, "0")}</span>{item.question}</span>
                  <span className="support-faq-toggle"><Icon name={expanded ? "minus" : "plus"} /></span>
                </button></h3>
                <div id={answerId} className="support-faq-answer" aria-hidden={!expanded}>
                  <div className="support-faq-answer-inner"><p>{item.answer}{item.docsLink && <> <a href="/docs" tabIndex={expanded ? 0 : -1}>{t("faq.openDocs")} <span aria-hidden="true">↗</span></a>.</>}</p></div>
                </div>
              </article>; 
            })}
          </div>
        </section>

        <aside className="support-contact-card">
          <div className="support-contact-mark"><Icon name="message" /></div>
          <div><div className="eyebrow">{t("contact.eyebrow")}</div><h2>{t("contact.title")}</h2><p>{t("contact.body")}</p></div>
          {supportUrl ? <a className="button button-primary" href="/discord">{t("contact.open")} <Icon name="arrow" /></a> : <p className="support-missing-link" role="status">{t("contact.missing")}</p>}
        </aside>
      </main>
      <Footer />
    </>
  );
}

export function DiscordRedirectPage() {
  const config = useBotConfig();
  const { t } = useStrings("discord");
  const supportUrl = config?.support_server_url?.trim();

  useEffect(() => {
    if (supportUrl) window.location.replace(supportUrl);
  }, [supportUrl]);

  if (!config) return <main className="discord-redirect-state"><div className="loading-ring" /><p>{t("checking")}</p></main>;
  if (supportUrl) return <main className="discord-redirect-state"><div className="loading-ring" /><p>{t("redirecting")}</p><a href={supportUrl}>{t("continue")}</a></main>;

  return <><PublicHeader page="support" /><main className="shell page-main discord-redirect-missing"><div className="eyebrow">{t("missing.eyebrow")}</div><h1>{t("missing.title")}</h1><p>{t("missing.body")}</p><a className="button button-primary" href="/support">{t("missing.action")}</a></main><Footer /></>;
}
