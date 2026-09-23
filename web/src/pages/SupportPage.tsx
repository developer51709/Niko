import { useEffect, useState } from "react";
import { useBotConfig } from "../hooks/useBotConfig";
import { Footer } from "../components/Footer";
import { PublicHeader } from "../components/PublicHeader";
import { Icon } from "../components/Icon";

const faqItems = [
  {
    question: "How do I invite Niko to my server?",
    answer: "Use the Add to Discord button in the site header to start the invite flow. You’ll need permission to add apps to the server.",
  },
  {
    question: "Where can I find setup instructions and command help?",
    answer: "The documentation library includes setup guides, feature walkthroughs, and a searchable command reference.",
  },
  {
    question: "Why isn’t a command or feature working?",
    answer: "Check that Niko is online and has the permissions needed in the channel. If the issue continues, share the command name and a short description in the support server.",
  },
  {
    question: "How do I report a bug or request a feature?",
    answer: "Join the support server and post in the appropriate help or feedback channel. Include steps to reproduce bugs, and never share passwords or private tokens.",
  },
  {
    question: "How can I request deletion of my data?",
    answer: "Contact the Niko team through the support server and include your Discord user ID so staff can locate the relevant data.",
  },
];

export function SupportPage() {
  const config = useBotConfig();
  const supportUrl = config?.support_server_url?.trim();
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  return (
    <>
      <PublicHeader page="support" />
      <main className="shell page-main support-page">
        <section className="support-hero">
          <div className="eyebrow">Niko support</div>
          <h1>Let’s get you <em>unstuck.</em></h1>
          <p>Browse quick answers, explore the guides, or talk with the community and Niko team.</p>
          <div className="support-actions">
            <a className="button button-primary" href="/docs">Browse documentation <Icon name="arrow" /></a>
            {supportUrl && <a className="button button-muted" href="/discord">Join the support server <Icon name="arrow" /></a>}
          </div>
        </section>

        <section className="support-faq" aria-labelledby="support-faq-title">
          <div className="support-section-heading">
            <div><div className="eyebrow">Quick answers</div><h2 id="support-faq-title">Frequently asked questions</h2></div>
            <span className="support-faq-count">{faqItems.length} helpful guides</span>
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
                  <div className="support-faq-answer-inner"><p>{item.answer}{index === 1 && <> <a href="/docs" tabIndex={expanded ? 0 : -1}>Open the docs <span aria-hidden="true">↗</span></a>.</>}</p></div>
                </div>
              </article>; 
            })}
          </div>
        </section>

        <aside className="support-contact-card">
          <div className="support-contact-mark"><Icon name="message" /></div>
          <div><div className="eyebrow">Need a hand?</div><h2>Find us in the community.</h2><p>Get help from other Niko users and the staff team in the official support server.</p></div>
          {supportUrl ? <a className="button button-primary" href="/discord">Open support server <Icon name="arrow" /></a> : <p className="support-missing-link" role="status">The support server link isn’t available right now. Please check back later.</p>}
        </aside>
      </main>
      <Footer />
    </>
  );
}

export function DiscordRedirectPage() {
  const config = useBotConfig();
  const supportUrl = config?.support_server_url?.trim();

  useEffect(() => {
    if (supportUrl) window.location.replace(supportUrl);
  }, [supportUrl]);

  if (!config) return <main className="discord-redirect-state"><div className="loading-ring" /><p>Checking the Niko support link…</p></main>;
  if (supportUrl) return <main className="discord-redirect-state"><div className="loading-ring" /><p>Taking you to the Niko support server…</p><a href={supportUrl}>Continue if you aren’t redirected</a></main>;

  return <><PublicHeader page="support" /><main className="shell page-main discord-redirect-missing"><div className="eyebrow">Niko support</div><h1>We couldn’t find the support link.</h1><p>The official support server link isn’t configured right now. Please check back later.</p><a className="button button-primary" href="/support">Visit support</a></main><Footer /></>;
}
