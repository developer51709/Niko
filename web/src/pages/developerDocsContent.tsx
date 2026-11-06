import type { ReactNode } from "react";
import { DeveloperDocsLink } from "../components/DeveloperDocsLink";
import { DiscordCodeBlock } from "../components/DiscordCodeBlock";
import { Icon } from "../components/Icon";

export type DeveloperDocsNavItem = {
  slug: string;
  title: string;
  child?: boolean;
};

export type DeveloperDocsNavGroup = {
  label: string;
  items: DeveloperDocsNavItem[];
};

export type DeveloperDocsPageData = {
  slug: string;
  title: string;
  description: string;
  eyebrow: string;
  toc: { id: string; label: string }[];
  body: ReactNode;
};

export const DEVELOPER_DOCS_NAV: DeveloperDocsNavGroup[] = [
  {
    label: "Getting started",
    items: [
      { slug: "", title: "Introduction" },
      { slug: "quickstart", title: "Quickstart" },
    ],
  },
  {
    label: "Core concepts",
    items: [
      { slug: "authentication", title: "Authentication" },
      { slug: "versioning", title: "Versioning" },
      { slug: "applications", title: "Applications" },
      { slug: "scopes", title: "Permissions" },
    ],
  },
  {
    label: "API reference",
    items: [
      { slug: "endpoints", title: "Overview" },
      { slug: "endpoints/economy", title: "Economy", child: true },
      { slug: "endpoints/leveling", title: "Leveling", child: true },
      { slug: "endpoints/users", title: "Users", child: true },
      { slug: "endpoints/warnings", title: "Warnings", child: true },
      { slug: "endpoints/blacklist", title: "Blacklist", child: true },
    ],
  },
  {
    label: "Events",
    items: [
      { slug: "webhooks", title: "Webhooks" },
    ],
  },
  {
    label: "Reliability",
    items: [
      { slug: "rate-limits", title: "Rate limits & appeals" },
      { slug: "maintenance", title: "Maintenance" },
    ],
  },
  {
    label: "Resources",
    items: [
      { slug: "errors", title: "Errors" },
      { slug: "policies", title: "Developer policies" },
      { slug: "support", title: "Support" },
    ],
  },
];

const scopes = [
  ["economy:read", "Read global economy standings and a user's economy profile.", false, false],
  ["levels:read", "Read server leaderboards and individual member levels.", false, false],
  ["users:read", "Resolve Discord usernames, display names, and avatars by user ID.", false, false],
  ["warns:read", "Read warning cases for guilds where the integration is allowed to operate.", false, false],
  ["warns:write", "Create and remove warning cases for allowed guilds. Intended for bot synchronization.", true, false],
  ["levels:write", "Replace XP and level values in Niko's leveling data.", true, false],
  ["blacklist:read", "Read Niko's user and server blacklist records.", true, true],
  ["blacklist:write", "Add or remove blacklist entries. Owner-selected, trusted applications only.", true, true],
  ["guilds:cross_server", "Access approved moderation data for guilds the application's bot does not share with Niko.", true, true],
] as const;

const endpoints = [
  ["GET", "/v1/economy/leaderboard", "economy:read", "Global economy leaderboard."],
  ["GET", "/v1/guilds/{guild_id}/levels", "levels:read", "Server leveling leaderboard."],
  ["GET", "/v1/users/{user_id}", "users:read", "Discord profile for a user ID."],
  ["GET", "/v1/users/{user_id}/economy", "economy:read", "One user's economy profile."],
  ["GET", "/v1/guilds/{guild_id}/members/{user_id}/level", "levels:read", "One member's XP and level."],
  ["PUT", "/v1/guilds/{guild_id}/members/{user_id}/level", "levels:write", "Replace one member's XP and level."],
  ["GET", "/v1/guilds/{guild_id}/warns", "warns:read", "All warning cases in a shared guild."],
  ["GET", "/v1/guilds/{guild_id}/members/{user_id}/warns", "warns:read", "Warning cases for one member."],
  ["POST", "/v1/guilds/{guild_id}/members/{user_id}/warns", "warns:write", "Create a warning case."],
  ["DELETE", "/v1/guilds/{guild_id}/warns/{warn_id}", "warns:write", "Delete one warning case."],
  ["DELETE", "/v1/guilds/{guild_id}/members/{user_id}/warns", "warns:write", "Clear a member's warning cases."],
  ["GET", "/v1/blacklist", "blacklist:read", "User and server blacklist records."],
  ["POST", "/v1/blacklist", "blacklist:write", "Add or remove a blacklist entry."],
] as const;

function Link({ to, children }: { to: string; children: ReactNode }) {
  return <DeveloperDocsLink to={to}>{children}</DeveloperDocsLink>;
}

function Card({
  to,
  icon,
  eyebrow,
  title,
  children,
}: {
  to: string;
  icon: string;
  eyebrow: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <DeveloperDocsLink to={to} className="devdocs-card">
      <span className="devdocs-card-icon"><Icon name={icon} size={17} /></span>
      <span className="devdocs-card-copy">
        <span>{eyebrow}</span>
        <strong>{title}</strong>
        <small>{children}</small>
      </span>
      <Icon name="arrow" size={15} className="devdocs-card-arrow" />
    </DeveloperDocsLink>
  );
}

function Callout({
  tone = "info",
  title,
  children,
}: {
  tone?: "info" | "warning";
  title: string;
  children: ReactNode;
}) {
  return (
    <div className={`devdocs-callout is-${tone}`}>
      <Icon name={tone === "warning" ? "alert" : "spark"} size={16} />
      <div><strong>{title}</strong><p>{children}</p></div>
    </div>
  );
}

function Method({ method }: { method: string }) {
  return <span className={`developer-docs-method is-${method.toLowerCase()}`}>{method}</span>;
}

export const DEVELOPER_DOCS_PAGES: DeveloperDocsPageData[] = [
  {
    slug: "",
    title: "Niko API",
    description: "A small, scoped HTTP API for bots, dashboards, migration tools, and community services built on Niko.",
    eyebrow: "Introduction",
    toc: [
      { id: "what-is-niko-api", label: "What is the Niko API?" },
      { id: "what-you-can-build", label: "What you can build" },
      { id: "how-access-works", label: "How access works" },
      { id: "conventions", label: "Conventions" },
    ],
    body: (
      <>
        <div className="devdocs-cards">
          <Card to="/developers/quickstart" icon="terminal" eyebrow="Start here" title="Quickstart">
            Request access, create a key, and make your first request.
          </Card>
          <Card to="/developers/endpoints" icon="book" eyebrow="API reference" title="Endpoints">
            Seven scoped endpoints for economy, leveling, profiles, and moderation context.
          </Card>
          <Card to="/developers/policies" icon="shield" eyebrow="Before your first key" title="Policies">
            The rules that apply to every integration with API access.
          </Card>
        </div>

        <h2 id="what-is-niko-api">What is the Niko API?</h2>
        <p>The Niko API exposes selected data from the official Niko bot over JSON. It exists for integrations that have a specific, reviewed reason to read or write a slice of Niko data; it is not a general-purpose Discord data source.</p>
        <p>Every endpoint is versioned, keyed, and scope-checked. A key can only carry permissions that were granted to its developer account, and an endpoint only serves data inside the key's scopes. That means an integration approved to migrate economy data cannot read the blacklist or overwrite leveling records by changing a URL.</p>
        <div className="developer-docs-facts">
          <div><span>Base URL</span><strong>niko.sryze.cc/api/v1</strong></div>
          <div><span>Format</span><strong>JSON over HTTPS</strong></div>
          <div><span>Authentication</span><strong>Bearer API key</strong></div>
          <div><span>Current version</span><strong>v1 · stable</strong></div>
        </div>

        <h2 id="what-you-can-build">What you can build</h2>
        <div className="devdocs-use-grid">
          <div><Icon name="chart" size={16} /><strong>Economy migration</strong><p>Import a server's public economy standings into another bot while respecting leaderboard privacy.</p></div>
          <div><Icon name="guild_leveling" size={16} /><strong>Leveling bridges</strong><p>Read a member's current XP and level, or write a migrated value with an explicitly granted write scope.</p></div>
          <div><Icon name="users" size={16} /><strong>Community dashboards</strong><p>Resolve profile details for a known user ID instead of asking members to retype their identity.</p></div>
          <div><Icon name="shield" size={16} /><strong>Moderator tooling</strong><p>Let trusted staff check blacklist context from an approved internal tool, never from a public surface.</p></div>
        </div>

        <h2 id="how-access-works">How access works</h2>
        <div className="devdocs-steps">
          <div><span>01</span><div><strong>Open a support ticket</strong><p>Join the Niko support server and tell us what you are building, which scopes you need, and how you will handle the data.</p></div></div>
          <div><span>02</span><div><strong>Get reviewed and granted</strong><p>The owner reviews the request and grants access to your Discord account. Access is not transferable.</p></div></div>
          <div><span>03</span><div><strong>Accept the policies</strong><p>The first time you open the Developer portal, read and accept the developer policies before creating a key.</p></div></div>
          <div><span>04</span><div><strong>Create a least-privilege key</strong><p>Choose only the permissions the integration needs. The secret is shown once and must stay server-side.</p></div></div>
        </div>

        <h2 id="conventions">Conventions</h2>
        <ul>
          <li>Discord IDs are strings in paths and responses. They are never rounded through a JavaScript number.</li>
          <li>All request and response bodies are JSON. Send <code>Content-Type: application/json</code> on writes.</li>
          <li>Successful responses use <code>2xx</code>; failures use the status codes documented in <Link to="/developers/errors">Errors</Link>.</li>
          <li>The version is part of the path. Unversioned paths are not part of the developer API.</li>
        </ul>
        <Callout title="Not a web-scraping shortcut">
          The public website still uses its own same-origin data routes for public pages. Those routes are not a substitute for the API, and transcripts are never available through an API key.
        </Callout>
      </>
    ),
  },
  {
    slug: "quickstart",
    title: "Quickstart",
    description: "Request developer access, accept the guidelines, create a key, and make a first keyed request.",
    eyebrow: "Getting started",
    toc: [
      { id: "request-access", label: "Request access" },
      { id: "create-a-key", label: "Create a key" },
      { id: "first-request", label: "Your first request" },
      { id: "next-steps", label: "Next steps" },
    ],
    body: (
      <>
        <h2 id="request-access">Request access</h2>
        <p>Access is invite-only and handled through a support ticket. Join the <Link to="/discord">Niko support server</Link>, open a ticket, and include enough detail for a real review.</p>
        <ol>
          <li>Your Discord account ID, or the account that will own the integration.</li>
          <li>What the integration does and who it is for.</li>
          <li>The scopes you believe you need, and why each one is necessary.</li>
          <li>How the service stores, protects, and deletes Niko data.</li>
          <li>A rough request volume and whether it will be public or internal.</li>
        </ol>
        <Callout tone="warning" title="Tickets are the only access channel">
          Do not ask for keys in DMs, public channels, or unrelated support threads. Access can be declined without a reason, and approved access can be narrowed or removed at any time.
        </Callout>

        <h2 id="create-a-key">Create a key</h2>
        <p>Once the owner grants access, open the <Link to="/dashboard/developer">Developer portal</Link> from your dashboard. The first visit shows the developer policies; you must accept them before the portal will create a key.</p>
        <div className="devdocs-steps compact">
          <div><span>01</span><div><strong>Accept the guidelines</strong><p>Read the policies in this portal. The agreement applies to the current policy version.</p></div></div>
          <div><span>02</span><div><strong>Choose scopes</strong><p>The key picker only shows permissions your account has been granted. Pick the smallest set.</p></div></div>
          <div><span>03</span><div><strong>Store the secret</strong><p>The raw key starts with <code>niko_dev_</code> and is shown once. Put it in a server-side secret manager.</p></div></div>
        </div>
        <p>Never place a key in a browser bundle, mobile binary, public repository, screenshot, or support ticket. If a key leaks, revoke it immediately and open a ticket.</p>

        <h2 id="first-request">Your first request</h2>
        <p>Send the key as a bearer token. This example reads one user's public profile:</p>
        <DiscordCodeBlock language="bash" code={`curl https://niko.sryze.cc/api/v1/users/1052690741874401360 \\
  -H "Authorization: Bearer niko_dev_..."`} />
        <p>A successful response looks like this:</p>
        <DiscordCodeBlock language="json" code={`{
  "user": {
    "id": "1052690741874401360",
    "username": "niko",
    "display_name": "Niko",
    "avatar_url": "https://cdn.discordapp.com/..."
  }
}`} />
        <Callout title="Use the API subdomain without /api">
          If your deployment serves the API from an API subdomain, the same request is <code>https://&lt;api-host&gt;/v1/users/...</code>. The <code>/api</code> segment is omitted there.
        </Callout>

        <h2 id="next-steps">Next steps</h2>
        <div className="devdocs-next-grid">
          <Link to="/developers/authentication">Read about authentication <Icon name="arrow" size={14} /></Link>
          <Link to="/developers/scopes">Choose the right scopes <Icon name="arrow" size={14} /></Link>
          <Link to="/developers/endpoints">Browse the endpoint reference <Icon name="arrow" size={14} /></Link>
        </div>
      </>
    ),
  },
  {
    slug: "authentication",
    title: "Authentication",
    description: "How developer keys are sent, stored, scoped, revoked, and kept out of the wrong hands.",
    eyebrow: "Core concepts",
    toc: [
      { id: "authorization-header", label: "Authorization header" },
      { id: "key-lifecycle", label: "Key lifecycle" },
      { id: "key-safety", label: "Key safety" },
      { id: "authentication-failures", label: "Authentication failures" },
    ],
    body: (
      <>
        <h2 id="authorization-header">Authorization header</h2>
        <p>Send the key in the <code>Authorization</code> header as a bearer token. The API also accepts <code>X-API-Key</code>, but bearer auth is preferred because it works with standard HTTP tooling.</p>
        <DiscordCodeBlock language="http" code={`GET /v1/economy/leaderboard HTTP/1.1
Host: niko.sryze.cc
Authorization: Bearer niko_dev_...
Accept: application/json`} />
        <p>Keys are scoped credentials, not user sessions. They do not grant dashboard access, and a dashboard session cannot be used in place of a key.</p>

        <h2 id="key-lifecycle">Key lifecycle</h2>
        <p>Keys start with <code>niko_dev_</code> and are generated once. Niko stores a peppered SHA-256 hash plus a short display prefix, never the raw secret. A lost key cannot be recovered; revoke it and create a replacement.</p>
        <ul>
          <li><strong>Create</strong> a named key in the Developer portal after accepting the current policies.</li>
          <li><strong>Use</strong> one key per service and, where possible, one key per environment.</li>
          <li><strong>Inspect</strong> the prefix and last-used time in the portal to identify stale credentials.</li>
          <li><strong>Revoke</strong> a key the moment it is no longer needed or may have been exposed.</li>
        </ul>
        <p>When the owner disables a developer account, every active key for that account is revoked automatically.</p>

        <h2 id="key-safety">Key safety</h2>
        <Callout tone="warning" title="Never ship a key to a client">
          A Discord bot token, a server environment variable, or a secret manager is the right home for a key. A browser, mobile app, or public repository is not.
        </Callout>
        <ul>
          <li>Do not commit keys, paste them into tickets, or include them in screenshots or logs.</li>
          <li>Do not share a key between integrations; create a separate key for each service.</li>
          <li>Rotate keys on a schedule appropriate to the integration, and immediately after any suspected leak.</li>
          <li>Use <code>X-Niko-Scopes</code> in responses to verify the effective scope set during debugging.</li>
        </ul>

        <h2 id="authentication-failures">Authentication failures</h2>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Status</th><th>What happened</th></tr></thead>
            <tbody>
              <tr><td><code>401</code></td><td>The key is missing, malformed, unknown, or revoked.</td></tr>
              <tr><td><code>403</code></td><td>The key is valid but does not include the endpoint's scope, or the developer account is no longer enabled.</td></tr>
            </tbody>
          </table>
        </div>
        <p>If a key worked recently and now returns <code>401</code>, check whether the owner revoked access or the key. If it returns <code>403</code>, compare the key's scopes with the required scope in the <Link to="/developers/endpoints">endpoint reference</Link>.</p>
      </>
    ),
  },
  {
    slug: "versioning",
    title: "Versioning",
    description: "The version is in the URL. Here are the supported base URLs and the rules for breaking changes.",
    eyebrow: "Core concepts",
    toc: [
      { id: "base-urls", label: "Base URLs" },
      { id: "api-subdomain", label: "API subdomain" },
      { id: "version-policy", label: "Version policy" },
      { id: "snowflakes", label: "Discord IDs" },
    ],
    body: (
      <>
        <h2 id="base-urls">Base URLs</h2>
        <p>The current stable version is <code>v1</code>. It is part of the URL, not a header, so every request makes its version explicit.</p>
        <div className="developer-docs-bases">
          <div><span>Main website</span><code>https://niko.sryze.cc/api/v1</code></div>
          <div><span>API subdomain</span><code>https://&lt;api-host&gt;/v1</code></div>
        </div>
        <p>The path after <code>/v1</code> is the resource. For example, a server leaderboard is <code>/v1/guilds/&#123;guild_id&#125;/levels</code>.</p>

        <h2 id="api-subdomain">API subdomain</h2>
        <p>When the API is served from its own subdomain, omit the <code>/api</code> segment. The two forms below resolve to the same handler and return the same payload:</p>
        <DiscordCodeBlock language="bash" code={`# Main domain
curl https://niko.sryze.cc/api/v1/guilds/123456789012345678/levels \\
  -H "Authorization: Bearer niko_dev_..."

# API subdomain
curl https://api.example.com/v1/guilds/123456789012345678/levels \\
  -H "Authorization: Bearer niko_dev_..."`} />
        <p>Unversioned aliases are not supported. Do not build a fallback that silently drops the version.</p>

        <h2 id="version-policy">Version policy</h2>
        <ul>
          <li><strong>Additive changes</strong> may ship inside <code>v1</code>: new optional fields, new optional query parameters, and new endpoints.</li>
          <li><strong>Breaking changes</strong> require a new path version, such as <code>v2</code>.</li>
          <li>A superseded version remains available through a documented migration window before it is retired.</li>
          <li>Pin the version in your request URL and review this portal before upgrading.</li>
        </ul>

        <h2 id="snowflakes">Discord IDs</h2>
        <p>Discord snowflakes exceed JavaScript's safe integer range. The API returns every user and guild ID as a string and expects string path segments. Store IDs as strings in your own database as well.</p>
        <DiscordCodeBlock language="json" code={`{
  "user_id": "1052690741874401360",
  "guild_id": "123456789012345678"
}`} />
      </>
    ),
  },
  {
    slug: "applications",
    title: "Applications & verification",
    description: "Register a bot, verify it with the Discord Developer Portal, and bind reviewed keys to that identity.",
    eyebrow: "Core concepts",
    toc: [
      { id: "why-applications", label: "Why applications" },
      { id: "submit", label: "Submit an application" },
      { id: "screenshot", label: "Verification screenshot" },
      { id: "owner-review", label: "Owner review" },
      { id: "app-keys", label: "App-bound keys" },
      { id: "shared-guilds", label: "Shared guilds" },
      { id: "special-scopes", label: "Special scopes" },
    ],
    body: (
      <>
        <h2 id="why-applications">Why applications</h2>
        <p>A generic API key proves that a developer account was approved. An application adds a verified bot identity. That extra identity is what lets Niko answer two questions safely: which bot is asking, and whether that bot is actually in the server whose warnings it wants.</p>
        <p>Applications are required for warning synchronization and webhook delivery. They are optional for the existing leaderboard and profile endpoints.</p>

        <h2 id="submit">Submit an application</h2>
        <ol>
          <li>Open the <Link to="/dashboard/developer#applications">Developer portal</Link> and choose <strong>Applications</strong>.</li>
          <li>Enter the bot's display name, a short description, and the bot user or Application ID.</li>
          <li>Select the permissions the bot needs. Special scopes cannot be requested here; only the owner can grant them.</li>
          <li>Upload the verification screenshot described below and submit.</li>
        </ol>
        <p>A bot or Application ID can only be registered once. A denied application can be resubmitted by the same developer with the same ID after correcting the problem. Pending and approved applications cannot be duplicated.</p>

        <h2 id="screenshot">Verification screenshot</h2>
        <p>The screenshot must be taken from Discord's <strong>Developer Portal → General Information</strong> page for the same application. Before taking it, click your profile picture in the top-right corner so the account menu is open and your username is fully visible.</p>
        <div className="developer-docs-facts">
          <div><span>Must show</span><strong>The open profile menu and your username</strong></div>
          <div><span>Must match</span><strong>The submitted Application ID</strong></div>
          <div><span>File types</span><strong>PNG, JPEG, GIF, or WebP</strong></div>
          <div><span>Maximum size</span><strong>8 MB</strong></div>
        </div>
        <Callout tone="warning" title="The screenshot is evidence, not proof">
          The owner compares the screenshot with the bot identity resolved from Discord and with the account that submitted it. A cropped, edited, or mismatched screenshot is denied. Do not include unrelated tokens, secrets, or personal information in the image.
        </Callout>

        <h2 id="owner-review">Owner review</h2>
        <p>Applications are reviewed manually by the Niko owner. The review checks the bot identity, the screenshot, the requested permissions, and whether the integration's purpose justifies them. The owner may approve fewer permissions than requested, approve with a note, or deny the application.</p>
        <p>Approval does not grant permissions that your developer account does not already hold. The application and the developer account must both allow a permission before an app-bound key can use it.</p>

        <h2 id="app-keys">App-bound keys</h2>
        <p>Create a key on the <Link to="/dashboard/developer#keys">API keys</Link> page and select an approved application. The key's effective permissions are the intersection of:</p>
        <ul>
          <li>the scopes you assign to the key;</li>
          <li>the scopes the owner approved for the application;</li>
          <li>the scopes your developer account currently holds.</li>
        </ul>
        <p>An app-bound key is also tied to the application's bot membership for guild moderation data, and it can receive the application's webhook configuration. Generic keys cannot be used for warn synchronization or events.</p>

        <h2 id="shared-guilds">Shared guilds</h2>
        <p>For warning endpoints, Niko requires both the application's bot and Niko to be in the requested guild. Changing the <code>guild_id</code> in the path cannot widen access. If the bot leaves a server, subsequent event delivery and warning API requests for that server stop immediately.</p>
        <DiscordCodeBlock language="json" code={`{
  "error": "This application's bot does not share that server with Niko.",
  "code": "GUILD_NOT_SHARED",
  "docs": "/developers/endpoints/warnings"
}`} />

        <h2 id="special-scopes">Special scopes</h2>
        <p>Three permissions are restricted to applications the owner has independently decided to trust:</p>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Scope</th><th>What it changes</th></tr></thead>
            <tbody>
              <tr><td><code>guilds:cross_server</code></td><td>Allows moderation access and event delivery for guilds the app's bot does not share with Niko. The requested guild must still be one Niko is in.</td></tr>
              <tr><td><code>blacklist:read</code></td><td>Allows reading Niko's blacklist records.</td></tr>
              <tr><td><code>blacklist:write</code></td><td>Allows adding and removing blacklist entries. Every write is attributed and reviewed.</td></tr>
            </tbody>
          </table>
        </div>
        <p>These scopes are never part of a normal application request and cannot be added to a generic key. The owner selects them during review. A trusted application still needs an app-bound key that includes the scope and a developer account that still holds the grant; scope approval alone does not create access.</p>
      </>
    ),
  },
  {
    slug: "scopes",
    title: "Permissions",
    description: "Scopes decide what a key can read or write. Access is granted per developer, reviewed per application, then narrowed again per key.",
    eyebrow: "Core concepts",
    toc: [
      { id: "available-scopes", label: "Available scopes" },
      { id: "how-scopes-are-enforced", label: "How scopes are enforced" },
      { id: "special-scopes", label: "Special scopes" },
      { id: "choosing-scopes", label: "Choosing scopes" },
      { id: "changing-scopes", label: "Changing scopes" },
    ],
    body: (
      <>
        <h2 id="available-scopes">Available scopes</h2>
        <p>These are the only permissions the developer API understands. Unknown scope names are ignored and cannot be used to widen access.</p>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Scope</th><th>Allows</th><th>Review</th></tr></thead>
            <tbody>{scopes.map(([scope, description, sensitive, restricted]) => (
              <tr key={scope}>
                <td><code>{scope}</code></td>
                <td>{description}</td>
                <td>{restricted ? <span className="developer-docs-tag is-sensitive">Owner only</span> : sensitive ? <span className="developer-docs-tag is-sensitive">Sensitive</span> : <span className="developer-docs-tag">Standard</span>}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>

        <h2 id="how-scopes-are-enforced">How scopes are enforced</h2>
        <p>There are three checks on every request:</p>
        <ol>
          <li>The key must include the endpoint's required scope.</li>
          <li>The developer account must still be enabled and still hold that scope.</li>
          <li>If the key belongs to an application, the owner must have approved that scope for the application and the shared-guild rule must pass.</li>
        </ol>
        <p>For an app-bound key, the effective scope set is the intersection of all three lists. If the owner narrows your account or the application, existing keys stop serving the removed permission immediately, even if the key still lists it in the portal.</p>
        <p><code>warns:read</code> and <code>warns:write</code> only work on an app-bound key. A generic key cannot carry them, because a bot identity is needed to enforce the shared-guild rule.</p>
        <Callout tone="warning" title="Sensitive scopes are separate decisions">
          A grant for <code>economy:read</code> does not imply <code>blacklist:read</code> or <code>levels:write</code>. Warn access is deliberately separate from leveling access, and <code>warns:write</code> is not a generic moderation credential.
        </Callout>

        <h2 id="special-scopes">Special scopes</h2>
        <p><code>guilds:cross_server</code>, <code>blacklist:read</code>, and <code>blacklist:write</code> are restricted. They are never selectable on a normal application request or a generic key. The owner grants them during application review to a bot they have independently decided to trust, and you must still assign the scope to an app-bound key.</p>
        <p>Trust is not a bypass of Niko's own membership: <code>guilds:cross_server</code> can cross the bot-membership restriction, but Niko must still be in the requested guild.</p>

        <h2 id="choosing-scopes">Choosing scopes</h2>
        <div className="devdocs-use-grid two">
          <div><strong>Economy migration</strong><p><code>economy:read</code> + <code>levels:read</code> is enough to read standings and levels. Add <code>levels:write</code> only if you are writing migrated values.</p></div>
          <div><strong>Profile companion</strong><p><code>users:read</code> alone resolves a known user ID. There is no search endpoint, and profile access does not imply economy access.</p></div>
          <div><strong>Warning sync bot</strong><p><code>warns:read</code> and <code>warns:write</code> on an app-bound key let a bot mirror cases for shared guilds and subscribe to events instead of polling.</p></div>
          <div><strong>Moderator dashboard</strong><p><code>blacklist:read</code> should be paired with a private, staff-only interface. Never expose the response to public members.</p></div>
          <div><strong>Read-only leaderboard</strong><p><code>economy:read</code> and <code>levels:read</code> cover the two leaderboard families. The public privacy flags still apply.</p></div>
        </div>

        <h2 id="changing-scopes">Changing scopes</h2>
        <p>Only the bot owner can change a developer account's grants or an application's approved scopes. You can narrow an individual key at any time by revoking it and creating a smaller one; keys cannot be edited in place. If your integration needs a new standard scope, update the application or open a support ticket explaining why. Restricted scopes can only be added by the owner during review.</p>
      </>
    ),
  },
  {
    slug: "endpoints",
    title: "API reference",
    description: "Every v1 endpoint, its required scope, and the conventions shared by the reference pages.",
    eyebrow: "API reference",
    toc: [
      { id: "endpoint-index", label: "Endpoint index" },
      { id: "request-conventions", label: "Request conventions" },
      { id: "pagination", label: "Pagination" },
      { id: "privacy", label: "Privacy behavior" },
    ],
    body: (
      <>
        <h2 id="endpoint-index">Endpoint index</h2>
        <p>All paths are relative to <code>https://niko.sryze.cc/api/v1</code>, or <code>/v1</code> on an API subdomain. Every endpoint requires a key.</p>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table developer-docs-endpoint-table">
            <thead><tr><th>Method</th><th>Path</th><th>Scope</th><th>Description</th></tr></thead>
            <tbody>{endpoints.map(([method, path, scope, description]) => (
              <tr key={`${method}-${path}`}>
                <td><Method method={method} /></td>
                <td><code>{path}</code></td>
                <td><code>{scope}</code></td>
                <td>{description}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
        <div className="devdocs-next-grid">
          <Link to="/developers/endpoints/economy">Economy reference <Icon name="arrow" size={14} /></Link>
          <Link to="/developers/endpoints/leveling">Leveling reference <Icon name="arrow" size={14} /></Link>
          <Link to="/developers/endpoints/users">Users reference <Icon name="arrow" size={14} /></Link>
          <Link to="/developers/endpoints/warnings">Warnings reference <Icon name="arrow" size={14} /></Link>
          <Link to="/developers/endpoints/blacklist">Blacklist reference <Icon name="arrow" size={14} /></Link>
          <Link to="/developers/webhooks">Webhook events <Icon name="arrow" size={14} /></Link>
        </div>

        <h2 id="request-conventions">Request conventions</h2>
        <ul>
          <li><strong>Authentication:</strong> <code>Authorization: Bearer niko_dev_...</code> on every request.</li>
          <li><strong>Content type:</strong> JSON. Writes must send <code>Content-Type: application/json</code>.</li>
          <li><strong>IDs:</strong> all Discord snowflakes are strings and are never rounded.</li>
          <li><strong>Errors:</strong> JSON with a stable <code>code</code>, a docs link, and an <code>error</code> message; see <Link to="/developers/errors">Errors</Link>.</li>
          <li><strong>Scope headers:</strong> successful keyed responses include <code>X-Niko-Key</code> and <code>X-Niko-Scopes</code>.</li>
        </ul>

        <h2 id="pagination">Pagination</h2>
        <p>Leaderboard endpoints accept <code>page</code> and <code>page_size</code>. Pages start at <code>1</code>. The economy default is 20, leveling default is 25, and the maximum is 100 for both.</p>
        <DiscordCodeBlock language="bash" code={`curl "https://niko.sryze.cc/api/v1/economy/leaderboard?page=2&page_size=50" \\
  -H "Authorization: Bearer niko_dev_..."`} />
        <p>Responses include <code>total</code> and <code>pages</code>. Invalid or non-positive values return <code>400</code>. The last page can be shorter, and privacy filtering can leave a row sparse without changing the total.</p>

        <h2 id="privacy">Privacy behavior</h2>
        <p>Private leaderboard members remain in the ranking but omit <code>user_id</code> and all profile fields, and return <code>private: true</code>. An integration must preserve that behavior and must not attempt to re-identify hidden rows.</p>
        <Callout title="Respect the original visibility">
          Do not use a second endpoint, a cached profile, or another data source to reveal a member who opted out of the public leaderboard.
        </Callout>
      </>
    ),
  },
  {
    slug: "endpoints/economy",
    title: "Economy",
    description: "Read a global leaderboard or one user's economy profile with economy:read.",
    eyebrow: "API reference · Economy",
    toc: [
      { id: "economy-leaderboard", label: "Economy leaderboard" },
      { id: "leaderboard-parameters", label: "Parameters" },
      { id: "leaderboard-response", label: "Response" },
      { id: "user-economy", label: "User economy" },
    ],
    body: (
      <>
        <h2 id="economy-leaderboard">Economy leaderboard</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="GET" /><code>/v1/economy/leaderboard</code></div>
          <span><code>economy:read</code></span>
        </div>
        <p>Returns ranked economy profiles from the global leaderboard. Rows are ordered by net worth and include the member's rank, economy value, and public profile details.</p>
        <h3 id="leaderboard-parameters">Parameters</h3>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Name</th><th>In</th><th>Default</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td><code>page</code></td><td>query</td><td><code>1</code></td><td>Page number, starting at 1.</td></tr>
              <tr><td><code>page_size</code></td><td>query</td><td><code>20</code></td><td>Rows per page, maximum 100.</td></tr>
            </tbody>
          </table>
        </div>
        <h3 id="leaderboard-response">Response</h3>
        <DiscordCodeBlock language="json" code={`{
  "entries": [
    {
      "key": "profile-key",
      "user_id": "1052690741874401360",
      "rank": 1,
      "net_worth": 842310,
      "private": false,
      "username": "niko",
      "display_name": "Niko",
      "avatar_url": "https://cdn.discordapp.com/..."
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1,
  "pages": 1
}`} />
        <p>Private members keep their rank and <code>net_worth</code> but omit <code>user_id</code>, <code>username</code>, <code>display_name</code>, and <code>avatar_url</code>, with <code>private: true</code>.</p>
        <h3 id="user-economy">User economy</h3>
        <div className="devdocs-endpoint-head">
          <div><Method method="GET" /><code>/v1/users/&#123;user_id&#125;/economy</code></div>
          <span><code>economy:read</code></span>
        </div>
        <p>Returns one user's economy record, or <code>404</code> if no record exists.</p>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Field</th><th>Type</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td><code>balance</code></td><td>number</td><td>Coins in the user's wallet.</td></tr>
              <tr><td><code>bank</code></td><td>number</td><td>Coins in the user's bank.</td></tr>
              <tr><td><code>net_worth</code></td><td>number</td><td>Combined wallet and bank value used by the leaderboard.</td></tr>
              <tr><td><code>level</code></td><td>number</td><td>Economy level associated with the profile.</td></tr>
              <tr><td><code>job</code></td><td>string or null</td><td>Current economy job.</td></tr>
              <tr><td><code>daily_streak</code></td><td>number</td><td>Consecutive daily reward claims.</td></tr>
              <tr><td><code>achievements</code></td><td>number</td><td>Unlocked achievement count.</td></tr>
              <tr><td><code>total_earned</code></td><td>number</td><td>Lifetime earned coins.</td></tr>
              <tr><td><code>leaderboard_private</code></td><td>boolean</td><td>Whether the user opted out of public standings.</td></tr>
            </tbody>
          </table>
        </div>
        <Callout tone="warning" title="A private leaderboard still has a profile">
          The single-user endpoint returns the economy record when the caller knows the ID, but your integration must not publish that record or use it to re-identify a hidden leaderboard row.
        </Callout>
      </>
    ),
  },
  {
    slug: "endpoints/leveling",
    title: "Leveling",
    description: "Read server leveling standings and member levels, or write a migrated level with levels:write.",
    eyebrow: "API reference · Leveling",
    toc: [
      { id: "server-leaderboard", label: "Server leaderboard" },
      { id: "guild-parameters", label: "Parameters" },
      { id: "member-level", label: "Member level" },
      { id: "write-member-level", label: "Write a level" },
      { id: "write-safety", label: "Write safety" },
    ],
    body: (
      <>
        <h2 id="server-leaderboard">Server leaderboard</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="GET" /><code>/v1/guilds/&#123;guild_id&#125;/levels</code></div>
          <span><code>levels:read</code></span>
        </div>
        <p>Returns one page of a server's leveling leaderboard. The guild must be one Niko is currently in. <code>/v1/levels/&#123;guild_id&#125;</code> is an equivalent alias.</p>
        <h3 id="guild-parameters">Parameters</h3>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Name</th><th>In</th><th>Default</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td><code>page</code></td><td>query</td><td><code>1</code></td><td>Page number, starting at 1.</td></tr>
              <tr><td><code>page_size</code></td><td>query</td><td><code>25</code></td><td>Rows per page, maximum 100.</td></tr>
            </tbody>
          </table>
        </div>
        <DiscordCodeBlock language="json" code={`{
  "guild": {
    "id": "123456789012345678",
    "name": "Cozy Corner",
    "icon_url": "https://cdn.discordapp.com/...",
    "member_count": 412
  },
  "leveling_enabled": true,
  "entries": [
    {
      "key": "profile-key",
      "user_id": "1052690741874401360",
      "rank": 1,
      "level": 24,
      "xp": 12400,
      "xp_for_next": 14800,
      "username": "niko",
      "display_name": "Niko",
      "avatar_url": "https://cdn.discordapp.com/..."
    }
  ],
  "page": 1,
  "page_size": 25,
  "total": 1,
  "pages": 1
}`} />
        <p><code>xp_for_next</code> is the XP required to reach the next level. <code>leveling_enabled</code> reports the server's XP setting even when the leaderboard is otherwise readable.</p>

        <h2 id="member-level">Member level</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="GET" /><code>/v1/guilds/&#123;guild_id&#125;/members/&#123;user_id&#125;/level</code></div>
          <span><code>levels:read</code></span>
        </div>
        <p>Returns one member's XP and level in a server. A missing level record is not an error: the response is <code>xp: 0</code> and <code>level: 0</code>.</p>
        <DiscordCodeBlock language="json" code={`{
  "guild_id": "123456789012345678",
  "user_id": "1052690741874401360",
  "xp": 12400,
  "level": 24,
  "xp_for_next": 14800
}`} />

        <h2 id="write-member-level">Write a level</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="PUT" /><code>/v1/guilds/&#123;guild_id&#125;/members/&#123;user_id&#125;/level</code></div>
          <span><code>levels:write</code></span>
        </div>
        <p>Replaces both values for one member. Send a JSON object with non-negative integers:</p>
        <DiscordCodeBlock language="bash" code={`curl -X PUT https://niko.sryze.cc/api/v1/guilds/123456789012345678/members/1052690741874401360/level \\
  -H "Authorization: Bearer niko_dev_..." \\
  -H "Content-Type: application/json" \\
  -d '{"xp": 12400, "level": 24}'`} />
        <p>The response echoes the stored values and the next-level XP requirement. The guild must be one Niko is in, and the leveling storage must be available.</p>

        <h2 id="write-safety">Write safety</h2>
        <Callout tone="warning" title="Write only the purpose you were approved for">
          A write key is not a general admin credential. Do not mass-edit a server, overwrite unrelated members, or retry failed writes in a tight loop.
        </Callout>
        <ul>
          <li>Use a separate <code>levels:write</code> key for migrations; do not add the scope to a read-only key.</li>
          <li>Back up the source values before writing, and make the migration idempotent.</li>
          <li>Respect the range limits: XP up to <code>10^15</code> and level up to <code>10^9</code>.</li>
          <li>If a write fails, fix the request or report the issue instead of retrying blindly.</li>
        </ul>
      </>
    ),
  },
  {
    slug: "endpoints/users",
    title: "Users",
    description: "Resolve Discord profile details for a known user ID with users:read.",
    eyebrow: "API reference · Users",
    toc: [
      { id: "user-profile", label: "User profile" },
      { id: "user-fields", label: "Response fields" },
      { id: "user-limits", label: "Limits" },
    ],
    body: (
      <>
        <h2 id="user-profile">User profile</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="GET" /><code>/v1/users/&#123;user_id&#125;</code></div>
          <span><code>users:read</code></span>
        </div>
        <p>Returns the public Discord profile for a known user ID. This endpoint resolves identity; it does not list, search, or enumerate users.</p>
        <DiscordCodeBlock language="bash" code={`curl https://niko.sryze.cc/api/v1/users/1052690741874401360 \\
  -H "Authorization: Bearer niko_dev_..."`} />
        <h3 id="user-fields">Response fields</h3>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Field</th><th>Type</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td><code>id</code></td><td>string</td><td>The requested Discord user ID.</td></tr>
              <tr><td><code>username</code></td><td>string</td><td>Discord username.</td></tr>
              <tr><td><code>display_name</code></td><td>string</td><td>Global display name when available, otherwise the username.</td></tr>
              <tr><td><code>avatar_url</code></td><td>string or null</td><td>Display avatar URL.</td></tr>
            </tbody>
          </table>
        </div>
        <DiscordCodeBlock language="json" code={`{
  "user": {
    "id": "1052690741874401360",
    "username": "niko",
    "display_name": "Niko",
    "avatar_url": "https://cdn.discordapp.com/..."
  }
}`} />
        <h2 id="user-limits">Limits</h2>
        <ul>
          <li>The user must be resolvable by Niko. Unknown or unavailable IDs return <code>404</code>.</li>
          <li>Profile access does not grant economy, leveling, or blacklist access.</li>
          <li>Do not build a searchable people directory or enrich profiles with outside data.</li>
          <li>Store only the profile fields your integration actually needs, and honour removal requests.</li>
        </ul>
      </>
    ),
  },
  {
    slug: "endpoints/warnings",
    title: "Warnings",
    description: "Read and synchronize guild warning cases with warns:read and warns:write, limited to shared guilds.",
    eyebrow: "API reference · Warnings",
    toc: [
      { id: "warn-model", label: "Warning model" },
      { id: "shared-guild-rule", label: "Shared guild rule" },
      { id: "list-guild-warns", label: "List guild warnings" },
      { id: "member-warns", label: "Member warnings" },
      { id: "create-warn", label: "Create a warning" },
      { id: "delete-warn", label: "Delete a warning" },
      { id: "clear-warns", label: "Clear member warnings" },
      { id: "sync-pattern", label: "Sync pattern" },
    ],
    body: (
      <>
        <h2 id="warn-model">Warning model</h2>
        <p>Warnings are Niko's per-guild moderation cases. Each case has a numeric warning ID, the guild and member IDs, the moderator, a reason, and a timestamp. Warning IDs are stable and are included in webhook events so a bot can reconcile its local copy.</p>
        <DiscordCodeBlock language="json" code={`{
  "id": 88421355114902,
  "guild_id": "123456789012345678",
  "user_id": "1052690741874401360",
  "moderator_id": "1545846783253545081",
  "reason": "Repeated spam in general",
  "created_at": "2026-11-05T18:22:41.320000+00:00"
}`} />

        <h2 id="shared-guild-rule">Shared guild rule</h2>
        <p>Warning endpoints require an <strong>app-bound key</strong>. Unless the owner granted <code>guilds:cross_server</code>, the application's bot must share the requested guild with Niko. Niko must also be in the guild. A request that does not satisfy both conditions returns <code>GUILD_NOT_SHARED</code> or <code>GUILD_NOT_FOUND</code>.</p>

        <h2 id="list-guild-warns">List guild warnings</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="GET" /><code>/v1/guilds/&#123;guild_id&#125;/warns</code></div>
          <span><code>warns:read</code></span>
        </div>
        <p>Returns warning cases for the guild, oldest first. Optional <code>user_id</code> filters to one member. Pages start at <code>1</code>; the default page size is <code>100</code> and the maximum is <code>500</code>.</p>
        <DiscordCodeBlock language="bash" code={`curl "https://niko.sryze.cc/api/v1/guilds/123456789012345678/warns?page=1&page_size=100" \\
  -H "Authorization: Bearer niko_dev_..."`} />
        <DiscordCodeBlock language="json" code={`{
  "guild_id": "123456789012345678",
  "warns": [
    {
      "id": 88421355114902,
      "guild_id": "123456789012345678",
      "user_id": "1052690741874401360",
      "moderator_id": "1545846783253545081",
      "reason": "Repeated spam in general",
      "created_at": "2026-11-05T18:22:41.320000+00:00"
    }
  ],
  "page": 1,
  "page_size": 100,
  "total": 1,
  "pages": 1
}`} />

        <h2 id="member-warns">Member warnings</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="GET" /><code>/v1/guilds/&#123;guild_id&#125;/members/&#123;user_id&#125;/warns</code></div>
          <span><code>warns:read</code></span>
        </div>
        <p>Returns all warning cases for one member, up to 500. This is the simplest endpoint for a bot that is repairing one user's local warning count.</p>
        <DiscordCodeBlock language="json" code={`{
  "guild_id": "123456789012345678",
  "user_id": "1052690741874401360",
  "warns": [],
  "total": 0
}`} />

        <h2 id="create-warn">Create a warning</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="POST" /><code>/v1/guilds/&#123;guild_id&#125;/members/&#123;user_id&#125;/warns</code></div>
          <span><code>warns:write</code></span>
        </div>
        <p>Creates one warning case. <code>reason</code> is required and limited to 1,000 characters. <code>moderator_id</code> is optional and defaults to the application's bot user ID. Send JSON with <code>Content-Type: application/json</code>.</p>
        <DiscordCodeBlock language="bash" code={`curl -X POST https://niko.sryze.cc/api/v1/guilds/123456789012345678/members/1052690741874401360/warns \\
  -H "Authorization: Bearer niko_dev_..." \\
  -H "Content-Type: application/json" \\
  -d '{"reason": "Repeated spam in general", "moderator_id": "1545846783253545081"}'`} />
        <p>The response is <code>201</code> with <code>&#123; "ok": true, "warn": &#123; ... &#125; &#125;</code>. The same case is emitted as a <code>warn.created</code> webhook event after it is stored.</p>

        <h2 id="delete-warn">Delete a warning</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="DELETE" /><code>/v1/guilds/&#123;guild_id&#125;/warns/&#123;warn_id&#125;</code></div>
          <span><code>warns:write</code></span>
        </div>
        <p>Deletes one warning case, scoped to the guild. A missing or cross-guild ID returns <code>WARN_NOT_FOUND</code>. The deleted case is emitted as <code>warn.deleted</code>.</p>
        <DiscordCodeBlock language="bash" code={`curl -X DELETE https://niko.sryze.cc/api/v1/guilds/123456789012345678/warns/88421355114902 \\
  -H "Authorization: Bearer niko_dev_..."`} />

        <h2 id="clear-warns">Clear member warnings</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="DELETE" /><code>/v1/guilds/&#123;guild_id&#125;/members/&#123;user_id&#125;/warns</code></div>
          <span><code>warns:write</code></span>
        </div>
        <p>Deletes every warning for one member in the guild. The response reports how many cases were removed, and a single <code>warns.cleared</code> event contains the removed warning IDs.</p>
        <DiscordCodeBlock language="json" code={`{
  "ok": true,
  "guild_id": "123456789012345678",
  "user_id": "1052690741874401360",
  "cleared": 3
}`} />

        <h2 id="sync-pattern">Sync pattern</h2>
        <ul>
          <li>Use webhook events for changes that happen after your bot is configured. Use the list endpoints for the initial reconciliation and after downtime.</li>
          <li>Store warning IDs and the guild ID together. A warning ID is only meaningful inside its guild.</li>
          <li>Make creates idempotent on your side: a retried request creates a new Niko case, so check the local case before retrying an ambiguous timeout.</li>
          <li>Re-read current state before retrying a delete or clear. The first request may have committed even when the connection failed.</li>
          <li>Never use warning data outside the guild and tool the owner approved, and do not publish reasons or member IDs.</li>
        </ul>
      </>
    ),
  },
  {
    slug: "endpoints/blacklist",
    title: "Blacklist",
    description: "Read or change Niko's protected blacklist records with owner-granted scopes.",
    eyebrow: "API reference · Blacklist",
    toc: [
      { id: "blacklist-endpoint", label: "Blacklist endpoint" },
      { id: "blacklist-parameters", label: "Filtering" },
      { id: "blacklist-response", label: "Response" },
      { id: "blacklist-write", label: "Write an entry" },
      { id: "blacklist-handling", label: "Handling the data" },
    ],
    body: (
      <>
        <h2 id="blacklist-endpoint">Blacklist endpoint</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="GET" /><code>/v1/blacklist</code></div>
          <span><code>blacklist:read</code></span>
        </div>
        <p>Returns Niko's user and server blacklist records. This is a sensitive moderation scope and is reviewed separately from economy and leveling access. The endpoint requires an app-bound key for an application the owner has approved for blacklist access; a generic key cannot use it.</p>
        <h2 id="blacklist-parameters">Filtering</h2>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Name</th><th>Values</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td><code>type</code></td><td><code>users</code>, <code>guilds</code>, <code>all</code></td><td>Choose one record family. Defaults to <code>all</code>.</td></tr>
            </tbody>
          </table>
        </div>
        <DiscordCodeBlock language="bash" code={`curl "https://niko.sryze.cc/api/v1/blacklist?type=users" \\
  -H "Authorization: Bearer niko_dev_..."`} />
        <h2 id="blacklist-response">Response</h2>
        <DiscordCodeBlock language="json" code={`{
  "users": [
    {
      "id": "1052690741874401360",
      "reason": "Recorded reason",
      "added_by": "123456789012345678",
      "timestamp": 1762300000,
      "expires_at": null
    }
  ]
}`} />
        <p>Timestamps are Unix seconds. User records may include an expiry; guild records do not. The response only contains the record families requested by <code>type</code>.</p>
        <h2 id="blacklist-write">Write an entry</h2>
        <div className="devdocs-endpoint-head">
          <div><Method method="POST" /><code>/v1/blacklist</code></div>
          <span><code>blacklist:write</code></span>
        </div>
        <p>Adds or removes one user or guild entry. This scope is only available to app-bound keys for applications the owner has explicitly trusted. The request shape is:</p>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Field</th><th>Required</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td><code>type</code></td><td>Yes</td><td><code>user</code> or <code>guild</code>.</td></tr>
              <tr><td><code>action</code></td><td>Yes</td><td><code>add</code> or <code>remove</code>.</td></tr>
              <tr><td><code>id</code></td><td>Yes</td><td>The Discord user or guild ID as a numeric string.</td></tr>
              <tr><td><code>reason</code></td><td>When adding</td><td>1,000 characters or fewer. Required for <code>add</code>.</td></tr>
              <tr><td><code>expires_at</code></td><td>No</td><td>Future Unix timestamp. User entries may expire; guild entries do not.</td></tr>
            </tbody>
          </table>
        </div>
        <DiscordCodeBlock language="bash" code={`curl -X POST https://niko.sryze.cc/api/v1/blacklist \\
  -H "Authorization: Bearer niko_dev_..." \\
  -H "Content-Type: application/json" \\
  -d '{\"type\": \"user\", \"action\": \"add\", \"id\": \"1052690741874401360\", \"reason\": \"Confirmed scam reports\"}'`} />
        <p>A successful write returns <code>&#123; "ok": true, "changed": true, "type": "user", "action": "add", "id": "..." &#125;</code>. <code>changed</code> can be <code>false</code> when the entry already existed or was already absent. A guild addition records the entry but does not automatically enable per-feature lockdown; that remains an owner action in the dashboard.</p>
        <Callout tone="warning" title="Names are attributed">
          The write is attributed to the application's bot user or the developer account. Do not use this scope for bulk moderation, retaliation, or entries outside the purpose the owner approved.
        </Callout>
        <h2 id="blacklist-handling">Handling the data</h2>
        <Callout tone="warning" title="Blacklist data is not public">
          Do not expose blacklist entries to public members, publish them, or use them to harass or profile a user. Use the data only inside the approved, staff-only tool described in your ticket.
        </Callout>
        <ul>
          <li>Keep query and response logs free of blacklist reasons and IDs.</li>
          <li>Do not cache the full list longer than necessary; fetch on demand in the approved context.</li>
          <li>Never share raw records with another bot, service, or server owner.</li>
          <li>Report accidental exposure through the support server immediately.</li>
        </ul>
      </>
    ),
  },
  {
    slug: "webhooks",
    title: "Webhooks",
    description: "Receive signed warning events for shared guilds instead of polling the API.",
    eyebrow: "Events",
    toc: [
      { id: "configure", label: "Configure an endpoint" },
      { id: "events", label: "Event types" },
      { id: "payload", label: "Payload" },
      { id: "signature", label: "Verify the signature" },
      { id: "delivery", label: "Delivery and retries" },
      { id: "guild-filter", label: "Guild filtering" },
      { id: "security", label: "Security rules" },
    ],
    body: (
      <>
        <h2 id="configure">Configure an endpoint</h2>
        <p>Webhooks are available after an application is approved. Open <strong>Applications</strong> in the <Link to="/dashboard/developer#applications">Developer portal</Link>, expand the approved application, and add an HTTPS endpoint. Choose the events to receive, enable delivery, and save. Use <strong>Send test event</strong> to verify the endpoint before relying on it.</p>
        <p>The endpoint must use HTTPS and resolve only to public addresses. Private, loopback, link-local, and metadata addresses are rejected.</p>

        <h2 id="events">Event types</h2>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Event</th><th>When it is sent</th><th>Data</th></tr></thead>
            <tbody>
              <tr><td><code>warn.created</code></td><td>A warning case was created through the API or Niko's moderation commands.</td><td><code>warn</code> object</td></tr>
              <tr><td><code>warn.deleted</code></td><td>One warning case was deleted.</td><td><code>warn</code> object</td></tr>
              <tr><td><code>warns.cleared</code></td><td>Every warning for one member was cleared.</td><td><code>user_id</code>, <code>count</code>, <code>warn_ids</code></td></tr>
            </tbody>
          </table>
        </div>
        <p>The test delivery uses type <code>webhook.test</code> and contains no guild data. It is not a selectable event.</p>

        <h2 id="payload">Payload</h2>
        <DiscordCodeBlock language="json" code={`{
  "id": "9dc7b4f0a184c1f438e664b2",
  "type": "warn.created",
  "created_at": 1762366961.42,
  "application_id": "8c3b1ef4-2b28-4e30-9f7e-d79c9e27c8a1",
  "guild_id": "123456789012345678",
  "data": {
    "warn": {
      "id": 88421355114902,
      "guild_id": "123456789012345678",
      "user_id": "1052690741874401360",
      "moderator_id": "1545846783253545081",
      "reason": "Repeated spam in general",
      "created_at": "2026-11-05T18:22:41.320000+00:00"
    }
  }
}`} />
        <p>Parse <code>id</code> and deduplicate on it. Delivery can be attempted more than once after a timeout or crash, so the receiver must be idempotent.</p>

        <h2 id="signature">Verify the signature</h2>
        <p>Every delivery includes <code>X-Niko-Signature: t=&#123;timestamp&#125;,v1=&#123;digest&#125;</code>. The digest is HMAC-SHA256 over the exact string <code>timestamp + "." + raw_body</code>, using the application's signing secret. Verify against the raw request body before JSON parsing, use a constant-time comparison, and reject old timestamps.</p>
        <DiscordCodeBlock language="python" code={`import hashlib, hmac, time

received = request.headers["X-Niko-Signature"]
timestamp, digest = received.removeprefix("t=").split(",v1=")
if abs(time.time() - int(timestamp)) > 300:
    raise ValueError("stale webhook")

signed = (timestamp + "." + body).encode()
expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
if not hmac.compare_digest(expected, digest):
    raise ValueError("bad signature")`} />
        <DiscordCodeBlock language="javascript" code={`import crypto from "node:crypto";

const received = req.get("X-Niko-Signature");
const [timestamp, digest] = received.replace("t=", "").split(",v1=");
if (Math.abs(Date.now() / 1000 - Number(timestamp)) > 300) throw new Error("stale webhook");

const expected = crypto
  .createHmac("sha256", secret)
  .update(timestamp + "." + rawBody)
  .digest("hex");
if (!crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(digest))) {
  throw new Error("bad signature");
}`} />
        <p>Other headers are <code>X-Niko-Application</code>, <code>X-Niko-Delivery</code>, and <code>X-Niko-Event</code>. Treat the secret like an API key and rotate it if it leaks.</p>

        <h2 id="delivery">Delivery and retries</h2>
        <ul>
          <li>Return any <code>2xx</code> promptly to acknowledge delivery. The body is not used.</li>
          <li>Transient failures and <code>429</code> are retried up to three attempts with delays of about 0, 2, and 6 seconds.</li>
          <li>Other <code>4xx</code> responses are treated as a final rejection and are not retried.</li>
          <li>Each request times out after 8 seconds. Slow receivers block only their own delivery.</li>
          <li>The portal records the last delivery time, HTTP status, event type, and last error.</li>
        </ul>
        <p>Events are emitted after the database write. A webhook failure never rolls back a warning change. If your endpoint is down for longer than the retry window, reconcile with the list endpoints.</p>

        <h2 id="guild-filter">Guild filtering</h2>
        <p>An application receives an event only when its bot currently shares the guild with Niko. This check happens per application at delivery time, not once when the webhook is saved. If the bot leaves the guild, delivery stops. Only an application explicitly approved for <code>guilds:cross_server</code> receives events for guilds its bot does not share.</p>
        <p>Events never contain data from a guild the application is not allowed to access, and changing the endpoint does not change that boundary.</p>

        <h2 id="security">Security rules</h2>
        <ul>
          <li>Verify the signature before acting on a payload. A publicly reachable URL is not authentication by itself.</li>
          <li>Always use HTTPS. Do not redirect deliveries to a private address or a different host.</li>
          <li>Do not log signing secrets, raw authorization headers, or full warning reasons in a shared log.</li>
          <li>Process events asynchronously and return quickly. Do not call back into Niko from the webhook handler.</li>
          <li>Store only the fields the approved integration needs, and keep the endpoint's secret in a secret manager.</li>
        </ul>
      </>
    ),
  },
  {
    slug: "rate-limits",
    title: "Rate limits & appeals",
    description: "IP-level request limits, automated abuse detection, account suspension, and the appeal process.",
    eyebrow: "Reliability",
    toc: [
      { id: "request-budget", label: "Request budget" },
      { id: "limit-headers", label: "Limit headers" },
      { id: "too-many-requests", label: "429 responses" },
      { id: "abuse-detection", label: "Abuse detection" },
      { id: "suspension", label: "Suspension & appeals" },
      { id: "good-client", label: "Building a good client" },
    ],
    body: (
      <>
        <h2 id="request-budget">Request budget</h2>
        <p>Every external request is limited by source IP before a key is read. This protects the API even when a caller is using an invalid, revoked, or leaked key.</p>
        <div className="developer-docs-facts">
          <div><span>IP allowance</span><strong>120 requests / 60 seconds</strong></div>
          <div><span>Key safety threshold</span><strong>300 requests / 60 seconds</strong></div>
          <div><span>Error burst threshold</span><strong>80 errors / 60 seconds</strong></div>
          <div><span>Distributed-use signal</span><strong>12 addresses / 5 minutes</strong></div>
        </div>
        <p>The IP allowance is shared by every request from the same server, NAT, or datacenter egress. A key safety threshold is not a second allowance to spend: crossing it is treated as automated abuse. Design integrations to stay far below both numbers and cache data that does not need to be fetched on every member action.</p>

        <h2 id="limit-headers">Limit headers</h2>
        <p>Every IP-limited API response includes the current budget in its headers:</p>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Header</th><th>Meaning</th></tr></thead>
            <tbody>
              <tr><td><code>X-RateLimit-Limit</code></td><td>Requests allowed in the current window.</td></tr>
              <tr><td><code>X-RateLimit-Remaining</code></td><td>Requests left for this address in the current window.</td></tr>
              <tr><td><code>X-RateLimit-Reset</code></td><td>Unix timestamp when the window resets.</td></tr>
              <tr><td><code>Retry-After</code></td><td>Seconds to wait. Present on <code>429</code> and maintenance responses.</td></tr>
            </tbody>
          </table>
        </div>

        <h2 id="too-many-requests">429 responses</h2>
        <p>When the IP allowance is exhausted, the API answers <code>429</code> with the standard error envelope and code <code>RATE_LIMITED</code>:</p>
        <DiscordCodeBlock language="json" code={`{
  "error": "Too many requests from this address. Retry in 17 seconds.",
  "code": "RATE_LIMITED",
  "docs": "/developers/rate-limits",
  "limit": 120,
  "remaining": 0,
  "retry_after": 17
}`} />
        <p>Wait at least <code>Retry-After</code> seconds. Do not rotate keys, addresses, or hostnames to get around the limit; that is exactly the pattern the abuse detector is designed to catch.</p>

        <h2 id="abuse-detection">Abuse detection</h2>
        <p>Niko automatically reviews authenticated traffic for signals that a script is probing, scraping, or intentionally exhausting the API. A developer account is suspended when the evidence crosses the safety thresholds. The signals include:</p>
        <ul>
          <li>Sustained authenticated volume above the key safety threshold.</li>
          <li>Large error bursts, especially when most requests are failing.</li>
          <li>One key used from an unusually wide set of source addresses.</li>
          <li>Repeated IP-level rate-limit blocks in a short period.</li>
        </ul>
        <p>Detection is deliberately separate from a single burst or a normal retry loop. A short spike, an occasional <code>429</code>, or a transient backend failure does not suspend an account on its own.</p>

        <h2 id="suspension">Suspension & appeals</h2>
        <p>When a developer account is suspended, Niko revokes the key that triggered the detection and every other key owned by that developer. Key authentication stops immediately, and the Developer portal locks key creation, revocation, and usage logs while the account is suspended.</p>
        <p>Niko sends the developer a Discord DM that states the account is suspended, explains the trigger, and includes a persistent <strong>Submit an appeal</strong> button. The button continues to work after a bot restart. Submitting it opens a short form in the DM; the developer can submit one appeal per suspension.</p>
        <p>The owner reviews the appeal in the portal. Whether it is approved or denied, the developer receives a follow-up DM with the decision. An approval restores portal access but does not revive the revoked secrets; create new keys after approval. The approval DM links directly to this rate-limit guide, the <Link to="/developers/policies">developer policies</Link>, and Discord's own rate-limit documentation.</p>
        <Callout tone="warning" title="Suspension is not an automatic ban">
          A suspension is an API-access action. It does not remove Niko from a server and does not replace moderation or blacklist enforcement. Appeals are reviewed by the bot owner, not by an automated system.
        </Callout>

        <h2 id="good-client">Building a good client</h2>
        <ul>
          <li>Use one shared limiter per key, even when the integration runs several processes or containers.</li>
          <li>Budget by endpoint: leaderboard and bulk reads are more expensive than a single profile lookup.</li>
          <li>Cache stable data for a short, deliberate time instead of polling every few seconds.</li>
          <li>On <code>429</code>, honour <code>Retry-After</code> and then apply exponential backoff with jitter.</li>
          <li>Do not retry <code>400</code>, <code>401</code>, <code>403</code>, or <code>404</code> in a loop. A failing request is not a license to increase concurrency.</li>
          <li>Monitor the <Link to="/status">status page</Link> and pause background jobs during a <Link to="/developers/maintenance">maintenance window</Link>.</li>
        </ul>
      </>
    ),
  },
  {
    slug: "maintenance",
    title: "Maintenance",
    description: "How the API answers during an owner-scheduled endpoint maintenance window.",
    eyebrow: "Reliability",
    toc: [
      { id: "what-maintenance-means", label: "What maintenance means" },
      { id: "maintenance-response", label: "Maintenance response" },
      { id: "handling-maintenance", label: "Handling it safely" },
      { id: "status-and-reports", label: "Status and reports" },
    ],
    body: (
      <>
        <h2 id="what-maintenance-means">What maintenance means</h2>
        <p>Niko can pause an individual API endpoint while it is being fixed, migrated, or investigated. Maintenance is endpoint-specific and is managed by the bot owner. It is not the same as a backend outage: the rest of the API may continue serving normally.</p>
        <p>The pause applies to both <code>/api/v1/*</code> and the API-subdomain alias <code>/v1/*</code>. Status, health, authentication, and the signed-in developer portal stay available so an owner can still investigate and clear the pause.</p>

        <h2 id="maintenance-response">Maintenance response</h2>
        <p>A paused endpoint always answers <code>503</code> with the standard error envelope, code <code>API_MAINTENANCE</code>, an <code>X-Error-Code: API_MAINTENANCE</code> header, a <code>Retry-After</code> header, and a <code>maintenance</code> object:</p>
        <DiscordCodeBlock language="json" code={`{
  "error": "This API is in maintenance mode.",
  "code": "API_MAINTENANCE",
  "docs": "/developers/maintenance",
  "maintenance": {
    "kind": "api",
    "key": "api_v1_economy_leaderboard",
    "label": "Economy leaderboard API",
    "reason": "Rebuilding the leaderboard cache",
    "since": 1762300000
  },
  "report_code": "ABC123"
}`} />
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Field</th><th>Meaning</th></tr></thead>
            <tbody>
              <tr><td><code>maintenance.kind</code></td><td>Always <code>api</code> for this API.</td></tr>
              <tr><td><code>maintenance.key</code></td><td>The internal endpoint key. Log it for support, but do not branch on it.</td></tr>
              <tr><td><code>maintenance.label</code></td><td>A human-readable endpoint name.</td></tr>
              <tr><td><code>maintenance.reason</code></td><td>The owner's reason, or <code>null</code> when none was recorded.</td></tr>
              <tr><td><code>maintenance.since</code></td><td>Unix timestamp when the pause started.</td></tr>
              <tr><td><code>report_code</code></td><td>Present when the pause is linked to a staff error report. Quote it in a support ticket.</td></tr>
              <tr><td><code>X-Error-Code</code></td><td>Always <code>API_MAINTENANCE</code>; the same value is in the body.</td></tr>
              <tr><td><code>Retry-After</code></td><td>Suggested wait in seconds. Niko currently sends <code>300</code>.</td></tr>
            </tbody>
          </table>
        </div>

        <h2 id="handling-maintenance">Handling it safely</h2>
        <ul>
          <li>Treat <code>503</code> as retryable, but stop after a small number of attempts and widen the delay.</li>
          <li>Do not retry writes in a tight loop. A paused write did not execute, but a timed-out write may have; read the current value before retrying.</li>
          <li>Keep background jobs paused until maintenance clears instead of queueing an unbounded backlog.</li>
          <li>Log the <code>maintenance.key</code>, <code>maintenance.since</code>, and <code>report_code</code> if you open a ticket.</li>
          <li>Do not create replacement keys or a second integration to bypass a paused endpoint.</li>
        </ul>

        <h2 id="status-and-reports">Status and reports</h2>
        <p>The public <Link to="/status">status page</Link> lists active API maintenance and owner-published incidents. A maintenance response is not itself an error report; if the owner linked one, the same six-character <code>report_code</code> appears in the status timeline.</p>
        <p>For every unexpected server failure, the response includes a <code>report_code</code> from the same error-report system staff use for bot and website incidents. Include that code in a support ticket along with the endpoint, timestamp, and key prefix. Never include the full API key.</p>
      </>
    ),
  },
  {
    slug: "errors",
    title: "Errors",
    description: "Stable error codes, report references, status codes, retries, and the details worth logging.",
    eyebrow: "Resources",
    toc: [
      { id: "error-shape", label: "Error shape" },
      { id: "error-codes", label: "Error codes" },
      { id: "report-codes", label: "Report codes" },
      { id: "status-codes", label: "Status codes" },
      { id: "retries", label: "Retries" },
      { id: "debugging", label: "Debugging" },
    ],
    body: (
      <>
        <h2 id="error-shape">Error shape</h2>
        <p>Every API failure is a JSON object with a stable <code>code</code>, a human-readable <code>error</code>, and a <code>docs</code> link. Do not parse the message or status alone: branch on <code>code</code>.</p>
        <DiscordCodeBlock language="json" code={`{
  "error": "This key does not have the required permission.",
  "code": "SCOPE_REQUIRED",
  "docs": "/developers/scopes",
  "required_scope": "economy:read"
}`} />
        <p>Some errors add context. Authentication failures include an <code>auth</code> hint, rate limits include <code>limit</code>, <code>remaining</code>, and <code>retry_after</code>, suspensions include a <code>suspension</code> object and appeal state, and maintenance includes the <code>maintenance</code> object documented on the <Link to="/developers/maintenance">Maintenance</Link> page.</p>

        <h2 id="error-codes">Error codes</h2>
        <p>These codes are stable for API v1. New codes may be added without a version bump when a new failure mode is introduced, so ignore unknown codes gracefully rather than refusing to parse the response.</p>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Code</th><th>Status</th><th>Meaning</th></tr></thead>
            <tbody>
              <tr><td><code>AUTH_KEY_REQUIRED</code></td><td>401</td><td>No bearer key or <code>X-API-Key</code> was supplied.</td></tr>
              <tr><td><code>AUTH_KEY_INVALID</code></td><td>401</td><td>The key is unknown, malformed, or normally revoked.</td></tr>
              <tr><td><code>SCOPE_REQUIRED</code></td><td>403</td><td>The key is valid but lacks the endpoint's required scope.</td></tr>
              <tr><td><code>ACCESS_FORBIDDEN</code></td><td>403</td><td>The account is not allowed to perform this action.</td></tr>
              <tr><td><code>ACCESS_NOT_GRANTED</code></td><td>403</td><td>Developer access has not been granted or has been revoked.</td></tr>
              <tr><td><code>ACCESS_SUSPENDED</code></td><td>403</td><td>Automated abuse protection has suspended the developer account.</td></tr>
              <tr><td><code>RATE_LIMITED</code></td><td>429</td><td>The source IP exceeded its request allowance.</td></tr>
              <tr><td><code>API_MAINTENANCE</code></td><td>503</td><td>The endpoint is paused by the owner.</td></tr>
              <tr><td><code>INVALID_BODY</code></td><td>400</td><td>The JSON body is missing or has the wrong shape.</td></tr>
              <tr><td><code>INVALID_ID</code></td><td>400</td><td>A guild or user ID is not numeric.</td></tr>
              <tr><td><code>INVALID_USER_ID</code></td><td>400</td><td>A user ID is missing, non-numeric, or too long.</td></tr>
              <tr><td><code>INVALID_PAGINATION</code></td><td>400</td><td><code>page</code> or <code>page_size</code> is not a positive integer.</td></tr>
              <tr><td><code>INVALID_RANGE</code></td><td>400</td><td>A level or XP value is outside the accepted range.</td></tr>
              <tr><td><code>INVALID_TYPE</code></td><td>400</td><td>A filter value is not one of the documented options.</td></tr>
              <tr><td><code>INVALID_KEY</code></td><td>400</td><td>A portal key name or scope selection is invalid.</td></tr>
              <tr><td><code>INVALID_ACCESS_GRANT</code></td><td>400</td><td>An owner's developer-access change is invalid.</td></tr>
              <tr><td><code>INVALID_APPEAL_DECISION</code></td><td>400</td><td>An appeal decision is not approved or denied.</td></tr>
              <tr><td><code>GUILD_NOT_FOUND</code></td><td>404</td><td>Niko is not in the guild, or the guild is unavailable.</td></tr>
              <tr><td><code>APPLICATION_REQUIRED</code></td><td>403</td><td>Warning access requires a key bound to an approved application.</td></tr>
              <tr><td><code>GUILD_NOT_SHARED</code></td><td>404</td><td>The application's bot does not share the guild with Niko.</td></tr>
              <tr><td><code>WARN_NOT_FOUND</code></td><td>404</td><td>The warning case does not exist in that guild.</td></tr>
              <tr><td><code>APPLICATION_NOT_FOUND</code></td><td>404</td><td>The application does not belong to this developer or does not exist.</td></tr>
              <tr><td><code>APPLICATION_EXISTS</code></td><td>409</td><td>That bot or Application ID already has a pending or approved application.</td></tr>
              <tr><td><code>APPLICATION_LOCKED</code></td><td>409</td><td>The application is pending or approved and cannot be resubmitted.</td></tr>
              <tr><td><code>APPLICATION_NOT_APPROVED</code></td><td>403</td><td>The application must be approved before this action.</td></tr>
              <tr><td><code>APPLICATION_FORBIDDEN</code></td><td>403</td><td>This developer does not own the application.</td></tr>
              <tr><td><code>INVALID_APPLICATION</code></td><td>400</td><td>An application field is invalid.</td></tr>
              <tr><td><code>INVALID_BOT_ID</code></td><td>400</td><td>The bot or Application ID is not a valid Discord snowflake.</td></tr>
              <tr><td><code>INVALID_APPLICATION_REVIEW</code></td><td>400</td><td>An owner review decision or scope selection is invalid.</td></tr>
              <tr><td><code>INVALID_DECISION</code></td><td>400</td><td>A review decision is not approved or denied.</td></tr>
              <tr><td><code>SCREENSHOT_REQUIRED</code></td><td>400</td><td>Registration requires a verification screenshot.</td></tr>
              <tr><td><code>SCREENSHOT_INVALID</code></td><td>400</td><td>The screenshot type or image content is invalid.</td></tr>
              <tr><td><code>SCREENSHOT_TOO_LARGE</code></td><td>413</td><td>The screenshot exceeds 8 MB.</td></tr>
              <tr><td><code>SCREENSHOT_NOT_FOUND</code></td><td>404</td><td>The stored screenshot for this application is unavailable.</td></tr>
              <tr><td><code>INVALID_WEBHOOK</code></td><td>400</td><td>The webhook URL or event selection is invalid.</td></tr>
              <tr><td><code>WEBHOOK_DELIVERY_FAILED</code></td><td>502</td><td>The test event could not be delivered to the configured endpoint.</td></tr>
              <tr><td><code>INVALID_REASON</code></td><td>400</td><td>A warn or blacklist reason is missing or too long.</td></tr>
              <tr><td><code>INVALID_MODERATOR_ID</code></td><td>400</td><td>The moderator ID is not numeric.</td></tr>
              <tr><td><code>INVALID_ACTION</code></td><td>400</td><td>A blacklist action is not <code>add</code> or <code>remove</code>.</td></tr>
              <tr><td><code>INVALID_EXPIRY</code></td><td>400</td><td>A blacklist expiry is not a future Unix timestamp.</td></tr>
              <tr><td><code>USER_NOT_FOUND</code></td><td>404</td><td>Discord could not resolve the user.</td></tr>
              <tr><td><code>RECORD_NOT_FOUND</code></td><td>404</td><td>The requested economy or level record does not exist.</td></tr>
              <tr><td><code>KEY_NOT_FOUND</code></td><td>404</td><td>The API key does not belong to this account.</td></tr>
              <tr><td><code>ACCESS_NOT_FOUND</code></td><td>404</td><td>The developer access grant does not exist.</td></tr>
              <tr><td><code>APPEAL_NOT_PENDING</code></td><td>409</td><td>The appeal was already reviewed.</td></tr>
              <tr><td><code>OWNER_ONLY</code></td><td>403</td><td>Only the bot owner can manage developer access or appeals.</td></tr>
              <tr><td><code>WEBSITE_ONLY</code></td><td>403</td><td>A first-party website route was called from outside the site.</td></tr>
              <tr><td><code>METHOD_NOT_ALLOWED</code></td><td>405</td><td>The endpoint exists but not for that HTTP method.</td></tr>
              <tr><td><code>NOT_FOUND</code></td><td>404</td><td>The API path does not exist.</td></tr>
              <tr><td><code>UPSTREAM_UNAVAILABLE</code></td><td>503</td><td>Discord, the database, or another dependency is unavailable.</td></tr>
              <tr><td><code>STORAGE_UNAVAILABLE</code></td><td>503</td><td>Leveling storage is unavailable.</td></tr>
              <tr><td><code>WRITE_FAILED</code></td><td>503</td><td>The requested write could not be committed.</td></tr>
              <tr><td><code>INTERNAL_SERVER_ERROR</code></td><td>500</td><td>An unexpected server failure occurred.</td></tr>
            </tbody>
          </table>
        </div>

        <h2 id="report-codes">Report codes</h2>
        <p>The API uses the same error-report system as the bot and website. When a server-side failure is stored for staff review, the response adds a six-character <code>report_code</code> and an <code>X-Error-Report</code> header. Maintenance responses can also carry the report code linked to the pause.</p>
        <DiscordCodeBlock language="json" code={`{
  "error": "An unexpected server error occurred.",
  "code": "INTERNAL_SERVER_ERROR",
  "docs": "/developers/errors",
  "report_code": "ABC123"
}`} />
        <p>Include <code>code</code> and, when present, <code>report_code</code> in a support ticket. Staff can look up the report and the redacted request context. Expected client mistakes such as invalid input, missing scopes, and rate limits do not create reports.</p>

        <h2 id="status-codes">Status codes</h2>
        <div className="developer-docs-table-wrap">
          <table className="developer-docs-table">
            <thead><tr><th>Status</th><th>Meaning</th><th>What to do</th></tr></thead>
            <tbody>
              <tr><td><code>400</code></td><td>Invalid path, query, body, or value.</td><td>Fix the request; do not retry unchanged.</td></tr>
              <tr><td><code>401</code></td><td>Missing, malformed, unknown, or revoked key.</td><td>Check the key and whether access was revoked.</td></tr>
              <tr><td><code>403</code></td><td>Missing scope, disabled access, or active suspension.</td><td>Compare scopes; use the suspension DM appeal path.</td></tr>
              <tr><td><code>404</code></td><td>Endpoint, user, guild, or record not found.</td><td>Verify the path, ID, and Niko's guild membership.</td></tr>
              <tr><td><code>429</code></td><td>The source IP exceeded its request allowance.</td><td>Honour <code>Retry-After</code>; do not rotate addresses or keys.</td></tr>
              <tr><td><code>500</code></td><td>An unexpected server failure occurred.</td><td>Retry once with backoff, then report the <code>report_code</code>.</td></tr>
              <tr><td><code>503</code></td><td>Backend unavailable or endpoint maintenance.</td><td>Back off, check <code>code</code>, and retry later.</td></tr>
            </tbody>
          </table>
        </div>

        <h2 id="retries">Retries</h2>
        <p>Retry only transient failures, and use exponential backoff with jitter. Do not retry <code>400</code>, <code>401</code>, <code>403</code>, or <code>404</code> unchanged. For <code>429</code>, wait at least <code>Retry-After</code>. For <code>500</code> or <code>503</code>, retry a small number of times with a widening delay; if it persists, check the <Link to="/status">status page</Link> and open a ticket with the error and report codes.</p>
        <p>Writes are especially important to make idempotent. A timed-out write may have succeeded, so read the member's level before trying again.</p>

        <h2 id="debugging">Debugging</h2>
        <ul>
          <li>Log the status, <code>code</code>, <code>report_code</code>, request path, latency, and key prefix; never log the raw key or query string.</li>
          <li>Read <code>X-Niko-Scopes</code> to confirm the effective scopes returned by the API.</li>
          <li>Use the <Link to="/dashboard/developer">Developer portal</Link> usage log to compare your request with what Niko recorded.</li>
          <li>Include the request path, timestamp, key prefix, error code, and report code in a support ticket, never the full secret.</li>
        </ul>
      </>
    ),
  },
  {
    slug: "policies",
    title: "Developer policies",
    description: "The rules every API integration agrees to before creating its first key.",
    eyebrow: "Resources",
    toc: [
      { id: "use-only-what-you-need", label: "1. Use only what you need" },
      { id: "respect-user-privacy", label: "2. Respect user privacy" },
      { id: "protect-credentials", label: "3. Protect credentials" },
      { id: "do-not-abuse-writes", label: "4. Do not abuse writes" },
      { id: "no-automated-abuse", label: "5. No automated abuse" },
      { id: "no-resale-or-redistribution", label: "6. No resale or redistribution" },
      { id: "be-honest-about-failures", label: "7. Be honest about failures" },
      { id: "access-can-change", label: "8. Access can change" },
    ],
    body: (
      <>
        <p>These guidelines apply to every developer with API access. They sit alongside the <Link to="/terms">Terms of Service</Link> and <Link to="/privacy">Privacy Policy</Link>; where they are stricter, these guidelines control your API use.</p>

        <h2 id="use-only-what-you-need">1. Use only what you need</h2>
        <p>Request the smallest scope that makes the integration work. Do not request <code>blacklist:read</code> or <code>levels:write</code> "for later", and do not create broad keys for convenience. Keys are reviewed by the owner and can be narrowed at any time.</p>

        <h2 id="respect-user-privacy">2. Respect user privacy</h2>
        <p>Do not expose user IDs, profile data, economy records, level records, or blacklist information publicly. Do not build searchable people directories, scrape the API, or combine its data with other sources to identify or profile users. Honour opt-outs: private leaderboard rows must remain private in your integration.</p>

        <h2 id="protect-credentials">3. Protect credentials</h2>
        <p>Keep keys server-side. Do not commit them, ship them in clients, paste them into tickets, or share them between integrations. A key belongs to one service and, when possible, one environment. Revoke keys you no longer use.</p>

        <h2 id="do-not-abuse-writes">4. Do not abuse writes</h2>
        <p>Writing levels is allowed only for the purpose approved in your ticket. Do not overwrite unrelated members, mass-edit a server, or use writes to interfere with Niko's leveling. Do not retry failed writes in a tight loop.</p>

        <h2 id="no-automated-abuse">5. No automated abuse</h2>
        <p>Do not scrape, fuzz, enumerate, or rotate addresses and keys to exceed the <Link to="/developers/rate-limits">IP and key safety limits</Link>. Automated abuse protection may revoke every key on an account and suspend developer-portal key management without prior warning.</p>

        <h2 id="no-resale-or-redistribution">6. No resale or redistribution</h2>
        <p>You may not sell API data, provide a proxy or mirror of the API, or redistribute Niko's blacklist or moderation records. Building a product on top of the API is fine; handing the raw data or access to someone else is not.</p>

        <h2 id="be-honest-about-failures">7. Be honest about failures</h2>
        <p>Report leaked keys, unexpected data exposure, and bugs that could affect users through the support server promptly. Do not hide an incident or use it to gather more data. Access may be suspended while an incident is investigated.</p>

        <h2 id="access-can-change">8. Access can change</h2>
        <p>Access is a privilege, not a permanent grant. The owner may decline, narrow, suspend, or revoke access at any time, including when an integration stops following these guidelines. Breaking these rules can also lead to a blacklist from Niko services.</p>
        <p>If automated abuse protection suspends your account, Niko sends a DM with a persistent <strong>Submit an appeal</strong> button. One appeal is reviewed per suspension, and the decision arrives in the same DM. Approval restores access but does not restore the revoked keys.</p>
        <p className="developer-docs-updated">Policies version 2 · Updated 5 November 2026</p>
      </>
    ),
  },
  {
    slug: "support",
    title: "Support",
    description: "Request access, report a key leak, or ask a question through a support ticket.",
    eyebrow: "Resources",
    toc: [
      { id: "support-server", label: "Support server" },
      { id: "what-to-include", label: "What to include" },
      { id: "reporting-an-api-error", label: "Reporting an API error" },
      { id: "appeals", label: "Suspension appeals" },
      { id: "security-incidents", label: "Security incidents" },
    ],
    body: (
      <>
        <h2 id="support-server">Support server</h2>
        <p>Questions about access, scopes, endpoints, or a failing integration go through the <Link to="/discord">Niko support server</Link>. Open a ticket rather than posting in a public channel so account, guild, and key-prefix details stay private.</p>
        <p>Access requests are only handled through tickets. The support team can help with the process, but only the bot owner can grant, narrow, or revoke developer access.</p>

        <h2 id="what-to-include">What to include</h2>
        <ul>
          <li>The Discord account that owns the integration.</li>
          <li>The endpoint and method you are calling, with the request path.</li>
          <li>The status code, response body, and timestamp in UTC.</li>
          <li>The error <code>code</code> and, when present, the <code>report_code</code>.</li>
          <li>The key prefix, never the full key.</li>
          <li>What you expected to happen and what happened instead.</li>
          <li>For access requests, the integration's purpose, scopes, and data-handling plan.</li>
        </ul>
        <Callout title="We will never ask for your full key">
          Niko staff do not need a full API key to diagnose a request. If someone asks you to paste one in a ticket or DM, stop and report it to the owner.
        </Callout>

        <h2 id="reporting-an-api-error">Reporting an API error</h2>
        <p>Every API failure returns a stable <code>code</code> in the JSON body; the same value is in the <code>X-Error-Code</code> header. Unexpected server failures and owner-linked maintenance pauses also include a six-character <code>report_code</code> (also in <code>X-Error-Report</code>). Quote both codes in the ticket so staff can open the matching error report.</p>
        <p>Expected client mistakes such as <code>INVALID_PAGINATION</code>, <code>SCOPE_REQUIRED</code>, and <code>RATE_LIMITED</code> do not create reports. For those, fix the request first. For <code>INTERNAL_SERVER_ERROR</code>, <code>UPSTREAM_UNAVAILABLE</code>, or <code>WRITE_FAILED</code>, retry once with backoff, then report it.</p>
        <p>See <Link to="/developers/errors">Errors</Link> for the full code table and <Link to="/developers/maintenance">Maintenance</Link> for the maintenance envelope.</p>

        <h2 id="appeals">Suspension appeals</h2>
        <p>A suspension DM contains a persistent <strong>Submit an appeal</strong> button. Pressing it opens a form in the same DM; submit once, then wait for the decision DM. The owner reviews the appeal, and the decision is sent to the same DM. Do not open a support ticket to request an appeal or to ask for a faster decision.</p>
        <p>If the appeal is approved, portal access returns but revoked keys stay revoked. Create a new key and implement a shared limiter before resuming traffic. The approval DM links to the <Link to="/developers/rate-limits">rate-limit guide</Link> and the <Link to="/developers/policies">developer policies</Link>.</p>

        <h2 id="security-incidents">Security incidents</h2>
        <p>If a key leaks, revoke it in the <Link to="/dashboard/developer">Developer portal</Link> immediately, then open a ticket with the key prefix, the time you noticed the exposure, and what data the key could access. Prompt reporting limits the impact and is expected under the developer policies.</p>
        <div className="developer-docs-cta">
          <div><strong>Need a key or a scope?</strong><span>Join the support server and open a ticket describing what you are building.</span></div>
          <DeveloperDocsLink to="/discord" className="button button-primary button-small">Open the support server <Icon name="arrow" size={14} /></DeveloperDocsLink>
        </div>
      </>
    ),
  },
];

export const DEVELOPER_DOCS_BY_SLUG = new Map(
  DEVELOPER_DOCS_PAGES.map((page) => [page.slug, page]),
);

export const DEVELOPER_DOCS_ORDER = DEVELOPER_DOCS_NAV.flatMap((group) => group.items);
