import { useState } from "react";
import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { useBotConfig } from "../hooks/useBotConfig";

/** The link partners paste: one URL that Discord renders as the ad card. */
const AD_PATH = "/discord/partnership";

const memberBenefits = [
  ["shield", "Moderation that stays calm", "Warnings, timeouts and AutoMod that explain what happened, so a rule break never turns into an argument."],
  ["chart", "Reasons to stay", "Leveling, an economy, games, music and a weekly lottery give people a reason to come back tomorrow."],
  ["message", "Help without a queue", "Private tickets, a public help forum and an assistant that answers the small questions for you."],
];

const partnerBenefits = [
  "A permanent listing in our partners channel, with the description you write",
  "A shout-out for your community from the partnerships team",
  "A direct line to us when something needs a human",
];

const partnerExpectations = [
  "An active, well-moderated community with a clear purpose",
  "Advertisements people opt into — no mass DMs, no invite bait",
  "Nothing built around scams, hate, or NSFW content",
];

export function PartnershipPage() {
  const config = useBotConfig();
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
            <div className="eyebrow">Niko partnerships</div>
            <h1>One link.<br /><em>A whole pitch.</em></h1>
            <p>
              Instead of pasting a bot message into your partnership channel, share a single link.
              Discord turns it into a clean card — headline, gallery and working buttons — so your
              recommendation looks deliberate, and joining takes one tap.
            </p>
            <div className="partner-actions">
              <button type="button" className="button button-primary" onClick={() => void copyLink()}>
                {copied ? "Link copied" : "Copy the ad link"} <Icon name="arrow" />
              </button>
              <a className="button button-muted" href="/discord">Visit the support server</a>
            </div>
            <div className="partner-link-field">
              <span>{adLink}</span>
              <a href={AD_PATH}>open <Icon name="external" /></a>
            </div>
            <p className="partner-note">
              Members who open it land on this page and can add Niko straight to their own server.
            </p>
          </div>

          {/* The card as Discord draws it from the link: the same sections, the
              same buttons. It is the whole advertisement, so it leads the page. */}
          <div className="partner-card" aria-label="The partnership card Discord shows for this link">
            <div className="partner-card-inner">
              <div className="partner-card-head">
                <span className="partner-card-mark">n</span>
                <div>
                  <strong>Partner with Niko</strong>
                  <small>A friendly bot for communities that care</small>
                </div>
              </div>
              <p className="partner-card-lead">
                Niko keeps the busywork off your staff: AutoMod that explains itself, private tickets,
                leveling, music, games and a full economy — configured from a dashboard.
              </p>
              <div className="partner-card-section">
                <p className="partner-card-heading">What your members get</p>
                <ul>
                  <li><b>Moderation that stays calm</b> — answered in plain language</li>
                  <li><b>Reasons to stay</b> — levels, coins, games and music</li>
                  <li><b>Help without a queue</b> — tickets and a help forum</li>
                </ul>
              </div>
              <div className="partner-card-rule" />
              <div className="partner-card-section">
                <p className="partner-card-heading">What partners get</p>
                <ul>
                  <li>A permanent listing with your own description</li>
                  <li>A shout-out from the partnerships team</li>
                </ul>
              </div>
              <div className="partner-card-gallery">
                <span /><span />
              </div>
              <div className="partner-card-buttons">
                <span>Add Niko</span><span>Partner with us</span><span>Join the server</span>
              </div>
            </div>
            <span className="partner-card-caption">Your link renders as this card</span>
          </div>
        </section>

        <section className="partner-section">
          <div className="partner-section-heading">
            <div className="section-kicker">What you are recommending</div>
            <h2>Tools your members will notice.</h2>
            <p>Niko is built to be configured once and then trusted: a dashboard for the staff team, and features members actually use.</p>
          </div>
          <div className="partner-grid">
            {memberBenefits.map(([icon, title, text]) => (
              <article className="partner-tile" key={title}>
                <span className="partner-tile-icon"><Icon name={icon} /></span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="partner-section partner-terms">
          <article className="partner-terms-card">
            <div className="section-kicker">What partners get</div>
            <h2>Something worth sharing.</h2>
            <ul>
              {partnerBenefits.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </article>
          <article className="partner-terms-card">
            <div className="section-kicker">What we look for</div>
            <h2>A community, not a link drop.</h2>
            <ul>
              {partnerExpectations.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </article>
        </section>

        <section className="partner-cta">
          <div>
            <div className="section-kicker">Ready when you are</div>
            <h2>Paste the link,<br />or say hello first.</h2>
            <p>Partnerships are reviewed by the Niko team. Introduce your community in the support server and we will take it from there.</p>
          </div>
          <div className="partner-cta-actions">
            <a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">
              Add Niko to your server <Icon name="external" />
            </a>
            <a className="button button-muted" href="/discord">Join the support server <Icon name="arrow" /></a>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
