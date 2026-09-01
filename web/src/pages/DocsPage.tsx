import { Footer } from "../components/Footer";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { navigate } from "../router";
import { useBotConfig } from "../hooks/useBotConfig";

export function DocsPage() {
  const config = useBotConfig();
  return (
    <>
      <PublicHeader page="docs" />
      <main className="shell page-main docs-page">
        <div className="page-heading"><div className="eyebrow">Documentation</div><h1>A clear starting point<br /><em>for every server.</em></h1><p>Niko is built to be approachable for members and manageable for moderators. Here are the paths people use most.</p></div>
        <div className="docs-grid">
          <article><span className="docs-number">01</span><h2>Invite & configure</h2><p>Add Niko with the permissions your server needs, then open the setup panels from Discord. Admin configuration is permission-gated.</p><a className="text-link" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">Invite Niko <Icon name="external" /></a></article>
          <article><span className="docs-number">02</span><h2>Build the room</h2><p>Use leveling, economy, tickets, polls, giveaways, and reminders to create repeatable rituals for your members.</p><a className="text-link" href="/commands" onClick={(e) => { e.preventDefault(); navigate("/commands"); }}>Browse commands <Icon name="arrow" /></a></article>
          <article><span className="docs-number">03</span><h2>Keep it healthy</h2><p>Turn on automod, anti-raid, logs, and AI controls one at a time. Every setting can be revisited from Discord or the dashboard.</p><a className="text-link" href="/dashboard" onClick={(e) => { e.preventDefault(); navigate("/dashboard"); }}>Open dashboard <Icon name="arrow" /></a></article>
        </div>
        <div className="docs-note"><Icon name="book" /><div><strong>Want the implementation details?</strong><p>The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in <code>docs/</code>.</p></div></div>
      </main>
      <Footer />
    </>
  );
}