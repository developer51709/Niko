import type { ReactNode } from "react";
import { Footer } from "../components/Footer";
import { PublicHeader } from "../components/PublicHeader";
import { SupportLink } from "../components/SupportLink";
import { navigate } from "../router";

const EFFECTIVE_DATE = "20 October 2026";

type LegalSection = readonly [heading: string, body: ReactNode];

interface LegalDocument {
  title: string;
  intro: string;
  sections: readonly LegalSection[];
}

const legalCopy: Record<"privacy" | "terms" | "community", LegalDocument> = {
  privacy: {
    title: "Privacy policy",
    intro: "Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",
    sections: [
      ["Information we use", "User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature. The dashboard stores daily aggregate message, join, and leave counts without message text or member IDs."],
      ["Scam-image filter (experimental)", "When a member reports a message through the right-click scam report, the reported images and message context are sent to Niko staff for review. On confirmation, a perceptual hash (a compact numeric fingerprint) and a copy of the image are stored so similar images can be detected and removed automatically. Nothing is stored for servers without the filter enabled."],
      ["Premium image moderation", "On servers with an active premium subscription, the URL of each image attachment posted in the server is sent to fal.ai's NSFW model so it can be scored. Niko stores the verdict (the confidence score, the file name, and the moderation action), not the image itself. Nothing is sent for servers without premium."],
      ["Payments", "Premium subscriptions and donations are processed by OxaPay. We store the order reference, OxaPay payment reference, the Discord user and server the payment belongs to, the amount and currency, the chosen crypto asset, the deposit address shown at checkout, and the payment status and timestamps. Niko never receives or stores card numbers, bank details, wallet private keys, or seed phrases. Payment records are kept for accounting, fraud prevention, refund handling, and billing support, including after a subscription ends."],
      ["Social notifier", "If a server follows social accounts, only the account name, platform, last-seen post ID, and target channel are stored."],
      ["How it is used", "Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],
      ["Storage and retention", "Data is stored by the server hosting Niko in a database (SQLite or MongoDB, depending on deployment). Economy, leveling, and configuration data remain until removed. Daily server activity totals are retained as aggregates. AI conversation history is limited and can be cleared with /clearhistory."],
      ["Third-party services", "When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Premium image moderation sends image URLs to fal.ai, and payments are handled by OxaPay; those providers' own privacy policies also apply. Other features may contact their respective services (social platforms for the notifier, Google Translate for translations); only the minimum data needed for the feature is shared. Niko does not sell or rent personal data, and does not use it for advertising."],
      ["Your choices", <>Use the <a href="/data-removal" onClick={(event) => { event.preventDefault(); navigate("/data-removal"); }}>data removal request form</a> to request deletion of your account data or a server you own. You must sign in with Discord so ownership can be confirmed. Material changes are announced in the <SupportLink />.</>],
      ["Data removal requests", "You can request deletion of personal account data or of a server's configuration data. A server request remains available after Niko is removed if you were its owner at the time. Every request is reviewed before deletion, and moderation and safety records are preserved: bot-level blacklists, warnings, mutes, moderation cases, logs and ticket transcripts, giveaway bans, abuse strikes, and scam-image reports. Submitting a request never lifts a restriction or erases evidence of abuse. Requests are retained as a compliance audit record."],
      ["Formal legal requests", <>If a law requires deletion of a preserved safety record, send a formal request directly to the bot owner at <a href="https://sorenthedev.indevs.in" target="_blank" rel="noreferrer">sorenthedev.indevs.in</a>. It must include a court record or signed legal document and the contact details of an official legal representative so authenticity can be verified. These matters are handled personally and confidentially; ordinary requests never override this process.</>],
    ],
  },
  terms: {
    title: "Terms of service",
    intro: "By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",
    sections: [
      ["Permitted use", "Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],
      ["Availability", "Niko is provided as-is, on a best-effort basis, without an uptime, latency, or feature-retention guarantee. Features may change, be restricted, or be removed without notice. Niko is not a paid-critical or life-safety service, and you should not rely on it as one."],
      ["Moderation", "The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],
      ["AI content", "AI replies and moderation verdicts can be inaccurate, incomplete, or unexpected. Automated image moderation is a helper, not a substitute for human moderation. Verify important information independently; the operator is not liable for harm from generated content or from a missed or mistaken classification."],
      ["Premium subscriptions", "Niko Premium costs $15 USD per server per month and is billed manually: you choose to renew, and a reminder is sent before the term ends. There is no automatic recurring charge. Premium is a licence to use server features for one server and one term; it is not a sale of software, does not create a partnership or fiduciary relationship, and does not give you any ownership in Niko. You must be old enough to enter a contract where you live, or have permission from a parent or guardian, to buy premium."],
      ["Payments and crypto", "Payments are collected through OxaPay, a third-party payment processor. Crypto transactions are irreversible once broadcast to the network, and the amount of crypto you send is set by the network and the provider's quote. You are responsible for sending the correct asset on the correct network, and for any taxes that apply to you. OxaPay's terms also apply to the payment itself. Never send funds to an address copied from somewhere other than the checkout page Niko shows you. If you believe a charge is wrong, contact support first; please do not start a chargeback or payment dispute for a service that was actually delivered, except where the law gives you that right."],
      ["Refunds", "Premium and donations are purchases of digital services delivered immediately and are generally non-refundable. If a payment was duplicated, charged in error, or never activated, contact us through the support server and we will review it in good faith and, where appropriate, extend the term, issue a credit, or arrange a refund through the processor. Nothing in these terms limits a mandatory consumer right you have under the law that applies to you."],
      ["Virtual items", "In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset. Premium is separate from virtual items and is never granted for in-bot currency."],
      ["Volunteer-run project", "Niko is a free, volunteer-run community project. It is not a company, partnership, registered business, or other legal entity. The project is maintained by individuals in their personal capacity, in their own time, without payment from subscription revenue beyond covering service costs. No volunteer, contributor, or maintainer is your employee, agent, partner, or fiduciary, and none of them makes any personal promise about the service."],
      ["Third-party services", "Niko depends on services we do not control, including Discord, OxaPay, fal.ai, and hosting providers. Outages, policy changes, or account actions on those services can interrupt or end features. We are not responsible for third-party services, and we are not affiliated with or endorsed by Discord, OxaPay, or fal.ai."],
      ["Limitation of liability", "To the maximum extent permitted by law, the operator, maintainers, and volunteers are not liable for indirect, incidental, special, consequential, exemplary, or punitive damages, or for lost profits, revenue, data, goodwill, or server growth, arising from or related to Niko, premium, or any payment. Our total aggregate liability for all claims relating to a server's subscription is limited to the greater of the amount actually paid for that subscription in the three months before the claim or $15 USD. This does not limit liability that cannot be limited by law."],
      ["Indemnity", "To the maximum extent permitted by law, you agree to indemnify and hold harmless the operator, maintainers, and volunteers from claims, damages, losses, and reasonable costs arising from your server's use of Niko, content posted in it, your breach of these terms, or your violation of another person's rights."],
      ["Changes and discontinuation", "We may change, suspend, or discontinue Niko or premium, including a specific feature. If premium is discontinued during a paid term, we will handle the remaining term in good faith, for example by keeping the service running to the end of the term or by offering a pro-rata credit through the processor. We do not guarantee a cash refund where the law does not require one."],
      ["Data deletion and safety records", <>Account and server deletion requests are handled through the <a href="/data-removal" onClick={(event) => { event.preventDefault(); navigate("/data-removal"); }}>data removal page</a>. Deletion is limited to personal and configuration data; moderation and safety records — blacklists, warnings, mutes, moderation cases, logs and ticket transcripts, giveaway bans, abuse strikes, and scam-image reports — are retained to protect communities and cannot be erased through that form. Using a deletion request to bypass a ban, warning, giveaway restriction, or investigation is a violation of these terms. Where the law requires release of a retained record, a formal legal request with a court record or signed legal document and an official legal contact must be sent to the bot owner at <a href="https://sorenthedev.indevs.in" target="_blank" rel="noreferrer">sorenthedev.indevs.in</a>; those matters are handled personally and confidentially.</>],
      ["Contact", <>Questions, payment issues, and data requests can be sent through the Niko <SupportLink />. Include the server ID and the payment or order reference so we can help quickly.</>],
    ],
  },
  community: {
    title: "Community policy",
    intro: "These community expectations apply to every server that uses Niko. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",
    sections: [
      ["Purpose", "Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines."],
      ["Discrimination and harassment", "Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic."],
      ["Illegal and malicious content", "Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law."],
      ["Other prohibited conduct", "Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form."],
      ["Enforcement and investigations", "When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action."],
      ["Obstruction of investigations", "Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants."],
      ["Reporting", <>If you believe a server using Niko is violating this policy, report it through the Niko <SupportLink />. Reports are reviewed by staff and handled confidentially.</>],
    ],
  },
};

export function LegalPage({ type }: { type: "privacy" | "terms" | "community" }) {
  const content = legalCopy[type];
  return (
    <>
      <PublicHeader page={type} />
      <main className="shell page-main legal-page"><div className="page-heading"><div className="eyebrow">Niko legal</div><h1>{content.title}</h1><p>{content.intro}</p><small>Effective date: {EFFECTIVE_DATE}</small></div><div className="legal-copy">{content.sections.map(([heading, text]) => <section key={heading}><h2>{heading}</h2><p>{text}</p></section>)}</div></main>
      <Footer />
    </>
  );
}