import { DiscordMarkdown } from "../components/DiscordMarkdown";
import { Footer } from "../components/Footer";
import { PublicHeader } from "../components/PublicHeader";
import { useStrings } from "../i18n";
import { navigate } from "../router";

//: The revision date shown at the top of every document: when the copy was
//: last changed, not when the document was first written. Rendered by the
//: Discord markdown renderer, so every reader sees the date in their own locale
//: and timezone exactly as they would inside Discord.
const LAST_UPDATED = "<t:1793491200:F>";
//: The owner's Discord account, credited on every legal page.
const OWNER_USER_ID = "1052690741874401360";

type LegalBlock = { kind: "paragraph" | "subheading" | "item"; text: string };

/**
 * One document block per line, so a translator works with whole paragraphs
 * instead of fragments: a line starting with `## ` is a subheading and a line
 * starting with `- ` is a list item; anything else is a paragraph. Inline bold,
 * code and links stay Discord markdown inside the line.
 */
function legalBlocks(body: string): LegalBlock[] {
  return body.split("\n").filter(Boolean).map((line) => {
    if (line.startsWith("## ")) return { kind: "subheading" as const, text: line.slice(3) };
    if (line.startsWith("- ")) return { kind: "item" as const, text: line.slice(2) };
    return { kind: "paragraph" as const, text: line };
  });
}

type LegalGroup = { kind: "list"; items: LegalBlock[] } | LegalBlock;

/** Consecutive list items become one list, so the document outline stays tidy. */
function legalGroups(blocks: LegalBlock[]): LegalGroup[] {
  const groups: LegalGroup[] = [];
  for (const block of blocks) {
    const last = groups[groups.length - 1];
    if (block.kind !== "item") groups.push(block);
    else if (last && last.kind === "list") last.items.push(block);
    else groups.push({ kind: "list", items: [block] });
  }
  return groups;
}

function LegalBody({ body }: { body: string }) {
  return <>
    {legalGroups(legalBlocks(body)).map((group, index) => {
      if (group.kind === "list") {
        return <ul key={index}>{group.items.map((item, itemIndex) => <li key={itemIndex}><DiscordMarkdown text={item.text} inline interactiveUsers={false} /></li>)}</ul>;
      }
      const text = <DiscordMarkdown text={group.text} inline interactiveUsers={false} />;
      return group.kind === "subheading" ? <h3 key={index}>{text}</h3> : <p key={index}>{text}</p>;
    })}
  </>;
}

export function LegalPage({ type }: { type: "privacy" | "terms" | "community" }) {
  // Every string on this page, including the document itself, comes from the
  // page catalogue: `s0`, `s1`, … are its sections, in order.
  const { t } = useStrings(type);
  const sections = [];
  for (let index = 0; ; index += 1) {
    const headingKey = `s${index}.title`;
    const heading = t(headingKey);
    if (heading === headingKey) break;
    sections.push({ heading, body: t(`s${index}.body`) });
  }

  // Links inside the documents are internal routes, so they navigate without a
  // full page load like every other link on the site.
  const followInternalLink = (event: { target: EventTarget; preventDefault: () => void }) => {
    const link = (event.target as HTMLElement).closest("a");
    const href = link?.getAttribute("href");
    if (!href || !href.startsWith("/") || href.startsWith("//")) return;
    event.preventDefault();
    navigate(href);
  };

  return (
    <>
      <PublicHeader page={type} />
      <main className="shell page-main legal-page" onClick={followInternalLink}><div className="page-heading"><div className="eyebrow">{t("legal.eyebrow")}</div><h1>{t("doc.title")}</h1><p>{t("doc.intro")}</p><div className="legal-meta"><span>{t("legal.effective")} <DiscordMarkdown text={LAST_UPDATED} inline interactiveUsers={false} /></span><span>{t("legal.updatedBy")} <DiscordMarkdown text={`<@${OWNER_USER_ID}>`} inline /></span></div></div><div className="legal-copy">{sections.map((section, index) => <section key={index}><h2>{section.heading}</h2><LegalBody body={section.body} /></section>)}</div></main>
      <Footer />
    </>
  );
}
