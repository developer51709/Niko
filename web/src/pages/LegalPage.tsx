import { Footer } from "../components/Footer";
import { PublicHeader } from "../components/PublicHeader";

const legalCopy = {
  privacy: {
    title: "Privacy policy",
    intro: "Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",
    sections: [
      ["Information we use", "User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],
      ["How it is used", "Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],
      ["Storage and retention", "Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],
      ["Third-party services", "When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],
      ["Your choices", "Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."],
    ],
  },
  terms: {
    title: "Terms of service",
    intro: "By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",
    sections: [
      ["Permitted use", "Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],
      ["Availability", "Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],
      ["Moderation", "The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],
      ["AI content", "AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],
      ["Virtual items", "In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],
      ["Contact", "Questions or concerns can be sent through the Niko support server."],
    ],
  },
} as const;

export function LegalPage({ type }: { type: "privacy" | "terms" }) {
  const content = legalCopy[type];
  return (
    <>
      <PublicHeader page={type} />
      <main className="shell page-main legal-page"><div className="page-heading"><div className="eyebrow">Niko legal</div><h1>{content.title}</h1><p>{content.intro}</p><small>Effective date: 1 January 2025</small></div><div className="legal-copy">{content.sections.map(([heading, text]) => <section key={heading}><h2>{heading}</h2><p>{text}</p></section>)}</div></main>
      <Footer />
    </>
  );
}