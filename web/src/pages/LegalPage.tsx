import type { ReactNode } from "react";
import { DiscordMarkdown } from "../components/DiscordMarkdown";
import { Footer } from "../components/Footer";
import { PublicHeader } from "../components/PublicHeader";
import { SupportLink } from "../components/SupportLink";
import { navigate } from "../router";

//: Rendered by the Discord markdown renderer, so every reader sees the date in
//: their own locale and timezone exactly as they would inside Discord.
const EFFECTIVE_DATE = "<t:1793491200:F>";
//: The owner's Discord account, credited on every legal page.
const OWNER_USER_ID = "1052690741874401360";
//: Formal legal requests are read in the owner team mailbox on our own domain.
const OWNER_EMAIL = "owner@niko.sryze.cc";

type LegalSection = readonly [heading: string, body: ReactNode];

interface LegalDocument {
  title: string;
  intro: string;
  sections: readonly LegalSection[];
}

const legalCopy: Record<"privacy" | "terms" | "community", LegalDocument> = {
  privacy: {
    title: "Privacy policy",
    intro:
      "Niko stores only what it needs to run its Discord features, keeps it for no longer than the feature or the law requires, and never sells it. This page is the public, human-readable version of the policy, including Niko's full data retention schedule.",
    sections: [
      [
        "Who we are",
        "Niko is a free, volunteer-run Discord bot. It is not a company, a registered business, a partnership, or any other legal entity: it is built and maintained by individuals in their personal capacity, in their own time. In this policy, “we”, “us” and “Niko” mean those maintainers, and “official instances” means the Niko bot and the website we operate ourselves at https://niko.sryze.cc, together with its dashboard, public leaderboards, support server, and web forms.",
      ],
      [
        "Which instances this policy covers",
        <>
          <p>This policy describes how the official public Niko instances handle data. It does not describe every copy of the software, because we do not run them.</p>
          <ul>
            <li><strong>Official public instances</strong> (the bot invited from our website, and everything at niko.sryze.cc). All user data for these instances — account and server settings, economy and leveling records, AI memory, moderation and safety records, payment references, staff mail, and the anonymous usage counters — is stored in a <strong>private MongoDB database</strong> that we control. That database is not publicly reachable, is not shared with other bots or services, and is readable only with credentials held by the maintainers who operate Niko.</li>
            <li><strong>Private, beta, and self-hosted instances.</strong> Niko's source is public, so anyone can run their own copy. Those deployments may use the <strong>deprecated SQLite storage method</strong> instead of MongoDB, may store data in JSON files or a different database, and may keep it on hardware we have never seen.</li>
            <li><strong>Self-hosted instances are outside our control.</strong> We do not operate, host, administer, or have access to them, and we cannot read, export, correct, or delete anything they hold. We therefore <strong>cannot handle data-removal requests, access requests, safety reports, or support requests about self-hosted, private, or beta instances</strong>. Whoever runs such an instance is a separate controller: they decide what is collected, how long it is kept, how it is secured, and who can see it, and they are responsible for answering your requests and for their own legal obligations. Send any request about one of those instances to its operator, not to us.</li>
            <li><strong>How to tell which one you are using.</strong> If the bot's profile, help command, or website links to niko.sryze.cc, you are on an official instance. If it points somewhere else, or was started by someone you know, treat its operator as the responsible party.</li>
          </ul>
        </>,
      ],
      [
        "Information we collect",
        <>
          <p>We keep the categories below. Nothing else is collected for advertising, profiling, or resale.</p>
          <ul>
            <li><strong>Discord identifiers.</strong> Your user ID links your economy balance, XP and level, reminders, birthday, highlights, AI memory, roleplay blocks, AFK state, and warnings to you. Server and channel IDs keep each server's settings apart from every other server's.</li>
            <li><strong>Message content.</strong> Messages are read in real time to answer AI mentions, run automod and the scam filter, serve snipe and highlight commands, and award XP. Content is not stored as a chat log: it is stored only in the narrow cases listed in the retention schedule below (AI memory, the snipe cache, ticket transcripts, and reported scam images).</li>
            <li><strong>Names and avatars you already show in Discord.</strong> Where a feature has to display a person — public leaderboards, staff profiles, server ownership records, ticket transcripts, giveaways, suggestions, and polls — the username, display name, and avatar URL are stored next to the record.</li>
            <li><strong>Server data.</strong> Server name, icon URL, owner ID, member count, and the per-server configuration for every feature an admin has touched.</li>
            <li><strong>Content you submit.</strong> Ticket transcripts, staff and team applications, appeals, reports, suggestions, polls, giveaways, birthdays, reminders, music playlists, and liked songs.</li>
            <li><strong>Presence, voice state, and activity.</strong> Presence and voice state are read while a feature needs them (member lists, music, VoiceMaster) and are not stored. Daily message, join, and leave totals are stored as aggregate counters for the dashboard, without message text and without member IDs.</li>
            <li><strong>Scam-image reports.</strong> When a member reports a message through the right-click scam report, the reported images and message context go to Niko staff for review. On confirmation, a perceptual hash (a compact numeric fingerprint) and a copy of the image are stored so variants can be detected and removed automatically.</li>
            <li><strong>Premium image moderation.</strong> On a server with an active premium subscription, the URL of each image attachment posted there is sent to fal.ai's NSFW model so it can be scored. Niko stores the verdict (confidence score, file name, and moderation action), never the image itself.</li>
            <li><strong>Payments.</strong> Premium subscriptions and donations are processed by OxaPay. We store the order reference, the OxaPay payment reference, the Discord user and server the payment belongs to, the amount and currency, the chosen crypto asset, the deposit address shown at checkout, and the payment status and timestamps. Niko never receives or stores card numbers, bank details, wallet private keys, or seed phrases.</li>
            <li><strong>Staff mail.</strong> Mail sent to a Niko address on our own domain, and our replies to it, are stored so the team can read and answer them from one mailbox.</li>
            <li><strong>Global analytics.</strong> Anonymous aggregate counters only, described in their own section below.</li>
          </ul>
        </>,
      ],
      [
        "AI features and Groq",
        <>
          <p>
            Niko's AI replies, image understanding, and voice-message transcription are provided through{" "}
            <a href="https://groq.com" target="_blank" rel="noreferrer">Groq</a>, an AI inference provider. Groq is
            the AI provider used by the official Niko instances; it is not an advertiser, a data broker, or a
            partner in any commercial sense.
          </p>
          <ul>
            <li><strong>What is sent.</strong> When a member asks Niko to answer, Niko sends Groq the message being answered, the member's Discord username, the server name and member count, up to three recent turns of that member's AI conversation in that server, a short memory note, up to three recent channel messages used as context, a short excerpt of the message being replied to, and — when the member attached them — up to three image URLs or a transcription of their voice message.</li>
            <li><strong>Default models.</strong> Chat runs on <code>openai/gpt-oss-20b</code>, image understanding on <code>qwen/qwen3.8-27b</code>, and transcription on <code>whisper-large-v3-turbo</code>. These defaults are configurable by the instance operator through the <code>GROQ_*</code> environment variables, so a self-hosted copy may use different models.</li>
            <li><strong>What Groq does with it.</strong> Groq processes the request and returns a reply. Its handling of that request is governed by its own privacy policy and terms, which you should read alongside this one: <a href="https://groq.com/privacy-policy/" target="_blank" rel="noreferrer">groq.com/privacy-policy</a>. We do not control Groq's infrastructure, and we cannot delete data that Groq keeps under its own policy.</li>
            <li><strong>What we do with it.</strong> We use the reply to answer in Discord and store only the short conversation memory described in the retention schedule. We do not use your messages to train models, we do not sell them, and we do not share them with any other AI provider.</li>
            <li><strong>How to avoid it.</strong> AI features are per-server and can be turned off by an admin in the dashboard. A member can erase their own conversation memory at any time with <code>/clearhistory</code>, and can simply not mention the bot. With AI disabled, no message content is sent to Groq.</li>
          </ul>
        </>,
      ],
      [
        "How we use information",
        "Data is used to run the features a server has enabled, to keep communities safe (automod, scam detection, moderation cases, blacklist enforcement, appeals), to answer support and staff mail, to keep payment and accounting records accurate, to fix bugs, and to decide which commands, fixes, and translations to work on next. We do not profile members for advertising, we do not build advertising audiences, and we do not sell, rent, or trade personal data to anyone.",
      ],
      [
        "Legal bases, where the GDPR applies",
        "Where European data-protection law applies, we rely on: performance of a contract or your request (running the features a server enabled, answering your support mail); our legitimate interests (keeping communities safe from scams and abuse, preventing fraud, securing the service, and improving it with anonymous counters); compliance with legal obligations (accounting, tax, and responding to valid legal process); and consent where a feature asks for it. You may object to processing based on legitimate interests at any time through the data removal page or the support server, and we will stop unless we have an overriding legal ground — which, for preserved safety records, is usually the protection of other users.",
      ],
      [
        "Storage and security",
        <>
          <p>On official public instances, all user data is held in a private MongoDB database that we operate. Some auxiliary stores (for example the music library's playlists) live in a separate database on the same private infrastructure.</p>
          <ul>
            <li>Access is limited to the maintainers who run Niko, through credentials that are not published and are rotated when someone leaves the team. Staff members see only the parts of the dashboard their role allows.</li>
            <li>Traffic between Niko, Discord, our database, and the providers listed below is encrypted in transit.</li>
            <li>Payment card data never reaches us; OxaPay handles the checkout, and we store references rather than credentials.</li>
            <li>Where the database operator takes backups, they serve disaster recovery only, are access-restricted in the same way as the live database, and are rotated; deleted data ages out of them as they rotate.</li>
            <li>No system is perfectly secure. If a breach affects your data, we will announce it in the support server and, where the law requires it, notify the people affected and the relevant authority.</li>
          </ul>
        </>,
      ],
      [
        "Data retention policy",
        <>
          <p>
            Retention is deliberate, not incidental. Each category below has a stated lifetime and a stated trigger. Where a fixed period is
            possible we use one; where a record exists to protect other people, we keep it for as long as that protection may be needed and
            say so plainly rather than promising a number we would not honour. Deletion, when it happens, removes the row from the live
            database immediately; a copy that sits inside a rotating backup ages out as that backup is replaced.
          </p>
          <h3>How long we keep what</h3>
          <ul>
            <li><strong>Economy, leveling, and profile data</strong> (balances, XP, jobs, inventories, achievements, streaks, leaderboard privacy) — kept until you delete your account data through the data removal page, at which point the rows are removed.</li>
            <li><strong>Server configuration</strong> (automod, logging, tickets, starboard, leveling, welcome, suggestions, notifier, and every other per-server setting) — kept while the server uses Niko, and removed when its owner completes a server deletion request.</li>
            <li><strong>AI conversation memory</strong> — a rolling window of your last three exchanges per server plus a short memory note of a few hundred characters. It is overwritten continuously as you keep talking, so nothing older survives a new exchange. It is erased immediately by <code>/clearhistory</code>, by an account deletion, or by a server deletion.</li>
            <li><strong>Snipe cache</strong> (the last deleted or edited message per channel) — held in memory only, overwritten by the next deletion in that channel, and cleared on every restart. Never written to disk.</li>
            <li><strong>Dashboard activity counters</strong> (daily messages, joins, and leaves per server) — aggregate numbers only, with no message text and no member IDs; kept while the server uses Niko and removed with a server deletion.</li>
            <li><strong>Global analytics</strong> — daily counters for the last 90 days plus lifetime totals, described in their own section below.</li>
            <li><strong>Logging revert snapshots</strong> (the message state behind a “revert” button on a log entry) — pruned automatically after 30 days, on a sweep that runs at most once an hour.</li>
            <li><strong>Verification challenges</strong> — minutes. A challenge is deleted as soon as it is solved, and expired challenges are swept automatically.</li>
            <li><strong>Temporary blacklists and timeouts</strong> — deleted automatically the moment they expire; expiry is checked when the restriction is read and again on startup.</li>
            <li><strong>Permanent blacklists, warnings, mutes, moderation cases, giveaway bans, abuse strikes, ticket transcripts, and logging records</strong> — kept without an automatic expiry for as long as they are needed to protect communities, settle appeals, and recognise repeat abuse. They survive account and server deletion requests, and are released only through the formal legal process described below.</li>
            <li><strong>Scam-image reports and confirmed fingerprints</strong> — the report, the confirmed perceptual hash, and the stored image copy are kept while they remain useful for detecting variants, with no automatic expiry, because an expiring fingerprint would let known scam images return.</li>
            <li><strong>Premium image moderation verdicts</strong> — kept with the server's premium records (score, file name, and action; never the image) for as long as the subscription record exists.</li>
            <li><strong>Payment and billing records</strong> — Payment records are kept after a subscription ends, for accounting, tax, fraud prevention, refunds, chargeback windows, and billing support — typically for as long as accounting and tax law and the payment provider's dispute windows require. When that period ends, the record is deleted or reduced to figures that no longer identify you.</li>
            <li><strong>Data removal requests</strong> — kept after completion as a compliance audit record: what was requested, what was removed, what was preserved, when, and by whom it was reviewed. This is how we can show that a deletion actually happened and that a preserved safety record was not erased.</li>
            <li><strong>Staff and team applications</strong> — kept while an application is reviewed and afterwards as a recruitment record; removed with an account deletion request.</li>
            <li><strong>Birthdays, AFK state, reminders, roleplay blocks, giveaway entries, poll votes, and music playlists or liked songs</strong> — kept until you remove them, the feature ends, or you delete your account data.</li>
            <li><strong>Server ownership records</strong> (server ID, owner ID, name, icon, and whether Niko is still present) — kept after Niko is removed from a server so that its owner can still prove ownership and request deletion; it holds no member content.</li>
            <li><strong>Staff mail</strong> — mail to a Niko address and our replies are kept so the conversation can be answered, audited, and handed over between staff roles; they are deleted when they are no longer needed for that purpose.</li>
            <li><strong>Aggregated and anonymised data</strong> — totals and counters that cannot be traced back to a person or a server have no retention limit, because they are no longer personal data.</li>
          </ul>
          <h3>What ends retention early</h3>
          <p>
            A completed account deletion request removes the personal and configuration data listed on the{" "}
            <a href="/data-removal" onClick={(event) => { event.preventDefault(); navigate("/data-removal"); }}>data removal page</a>;
            a completed server request does the same for a server you own. <code>/clearhistory</code> erases your AI memory immediately.
            Turning off a feature stops new collection at once. A restart clears the snipe cache. Expiry dates delete temporary
            restrictions without anyone asking.
          </p>
          <h3>What survives a deletion request, and why</h3>
          <p>
            Moderation and safety records survive on purpose. They are the evidence that protects other communities: bot-level
            blacklists, warnings, mutes, moderation cases, logs and ticket transcripts, giveaway bans, abuse strikes, and scam-image
            reports. A deletion request never lifts a restriction, restores access, or erases evidence of abuse, and using one to try is a
            violation of the Terms of Service. Data removal requests themselves are kept as the audit trail described above.
          </p>
          <h3>Legal holds and disputes</h3>
          <p>
            If a record is needed for an active investigation, an appeal, a payment dispute, a chargeback, or actual or threatened legal
            proceedings, its retention is extended until the matter is closed — including records that would otherwise have expired. Once
            the hold ends, the normal schedule applies again.
          </p>
          <h3>Instances we do not run</h3>
          <p>
            This schedule describes official public instances only. Private, beta, and self-hosted deployments — including those still
            using the deprecated SQLite storage — set their own retention, and we cannot shorten, extend, enforce, or answer questions
            about it. Ask the operator of that instance.
          </p>
        </>,
      ],
      [
        "Your rights",
        <>
          <p>Subject to the preserved records described above, and to the law where you live, you can ask to:</p>
          <ul>
            <li><strong>See</strong> what Niko holds about you, and receive a copy of it.</li>
            <li><strong>Correct</strong> anything wrong — most profile and settings fields you can change yourself in Discord or the dashboard.</li>
            <li><strong>Delete</strong> your account data or a server you own through the data removal form.</li>
            <li><strong>Restrict or object</strong> to a particular use, such as having your identity shown on the public leaderboard, which has its own privacy toggle in the dashboard.</li>
            <li><strong>Withdraw consent</strong> for any feature that asked for it, by turning the feature off.</li>
            <li><strong>Complain</strong> to your local data-protection authority. We would rather you came to us first, but you do not need our permission.</li>
          </ul>
          <p>Every request is answered through the support server or the contact routes below, and we may ask you to prove control of the Discord account or server concerned so that nobody can delete somebody else's data.</p>
        </>,
      ],
      [
        "Data removal requests",
        <>
          <p>
            You can request deletion of personal account data or of a server's configuration data through the{" "}
            <a href="/data-removal" onClick={(event) => { event.preventDefault(); navigate("/data-removal"); }}>data removal form</a>.
            You must sign in with Discord so ownership can be confirmed, and a server request remains available after Niko is removed if
            you were its owner at the time.
          </p>
          <p>
            Every request is reviewed before deletion runs, so that a request cannot be used to erase a safety record or to escape a
            restriction. The review looks at the scope you asked for, your ownership evidence, and whether a legal hold applies. Requests
            are retained as a compliance audit record.
          </p>
        </>,
      ],
      [
        "Formal legal requests",
        <p>
          If a law requires deletion or release of a preserved safety record, send a formal request by email to the bot owner at{" "}
          <a href={`mailto:${OWNER_EMAIL}`}>{OWNER_EMAIL}</a>. It must include a court
          record or signed legal document and the contact details of an official legal representative so authenticity can be verified.
          These matters are handled personally and confidentially; ordinary requests never override this process.
        </p>,
      ],
      [
        "Global analytics",
        "Niko keeps bot-wide usage statistics so that updates can be aimed at what communities actually use. What is counted is a daily total per command name, how each command was invoked (slash command, prefix command, or right-click/context command), the Discord language each server is set to, how many distinct servers used Niko that day, and the daily total of servers and members Niko is in. These are anonymous aggregate counters only: no message content, no user ID, no server or channel ID, and no individual person's activity is recorded, and a counter can never be traced back to a server or a person. The counters are kept for the last 90 days plus all-time totals, are visible only to Niko's staff, and are used solely to decide which features, fixes, and language translations to build and release next. Global analytics data is anonymous and is never seen, published, shared, or sold to any third-party company or individual.",
      ],
      [
        "Third-party services",
        <>
          <p>We share the minimum a feature needs, and only with the provider that feature uses:</p>
          <ul>
            <li><strong>Groq</strong> — AI replies, image understanding, and voice transcription (see the AI section above), under <a href="https://groq.com/privacy-policy/" target="_blank" rel="noreferrer">Groq's privacy policy</a>.</li>
            <li><strong>fal.ai</strong> — premium image moderation, which sends image URLs for scoring, under <a href="https://fal.ai/privacy" target="_blank" rel="noreferrer">fal.ai's privacy policy</a>. Never used on servers without premium.</li>
            <li><strong>OxaPay</strong> — premium and donation payments, under <a href="https://oxapay.com/privacy" target="_blank" rel="noreferrer">OxaPay's privacy policy</a>.</li>
            <li><strong>Discord</strong> — everything Niko does happens on Discord and is subject to Discord's own privacy policy.</li>
            <li><strong>Hosting and infrastructure providers</strong> — the servers and database where the official instances run.</li>
            <li><strong>Google Translate</strong> — only when a translation feature is used, and only the text being translated.</li>
          </ul>
          <p>Niko does not sell or rent personal data, does not use it for advertising, and does not share it with data brokers.</p>
        </>,
      ],
      [
        "Children",
        "Niko is not directed at children. Discord requires users to be at least 13 years old, or older where local law sets a higher minimum, and Niko follows that rule. If we learn that a child below the applicable age has used an official instance, we will remove their data on request from a parent or guardian and may restrict the account's access to Niko.",
      ],
      [
        "International transfers",
        "Niko's maintainers and providers may process data in countries other than yours, including the United States. Where a transfer needs a legal safeguard, we rely on the provider's contractual protections and on the necessity of the transfer to deliver a feature you or your server asked for.",
      ],
      [
        "Changes to this policy",
        <>
          <p>Material changes — a new provider, a new category of data, or a shorter or longer retention period — are announced in the <SupportLink /> before or when they take effect, and the effective date at the top of this page moves. Continued use of Niko after a change constitutes acceptance of the updated policy.</p>
          <p>Questions about this policy, a request under it, or a concern about how an official instance handled your data can be sent through the <SupportLink />.</p>
        </>,
      ],
    ],
  },
  terms: {
    title: "Terms of service",
    intro:
      "By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines. They apply to the official public Niko instances described below.",
    sections: [
      [
        "1. Acceptance",
        "By inviting Niko to a server, using its commands, or using the website and dashboard, you agree to these terms. If you do not agree, remove the bot and stop using the site. If you accept on behalf of a server, you confirm you are allowed to do so.",
      ],
      [
        "2. Scope: official instances and self-hosted instances",
        <>
          <p>These terms cover the official public Niko instances we operate: the bot invited from niko.sryze.cc and everything served from that domain.</p>
          <ul>
            <li><strong>Official public instances</strong> store all user data in a private MongoDB database we control, as described in the Privacy Policy.</li>
            <li><strong>Private, beta, and self-hosted instances</strong> are copies run by other people. They may use the deprecated SQLite storage method, a different database, or plain files, and their data may be held anywhere.</li>
            <li><strong>We do not control self-hosted instances.</strong> We do not operate, host, or administer them and cannot see or change their data. We therefore cannot provide support, moderation, safety, access, or data-removal help for them, and we are not responsible for their uptime, security, content, or legal compliance. Requests about those instances must go to their operator.</li>
            <li>If you run your own instance, you are its operator and its controller: you are responsible for its security, for answering requests from its users, for what it stores and for how long, and for complying with Discord's rules and the law where you and its users are.</li>
          </ul>
        </>,
      ],
      [
        "3. Eligibility",
        "You must be old enough to use Discord where you live (at least 13, or older where local law requires) and old enough to enter a contract to buy premium, or have permission from a parent or guardian. If you are under the age of majority where you live, you confirm a parent or guardian has reviewed these terms with you.",
      ],
      [
        "4. Permitted use",
        "Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, resell as a service, or disrupt the service or other servers. Do not attempt to access data, commands, or staff areas you are not authorised to use, and do not use Niko to evade a blacklist, mute, or investigation.",
      ],
      [
        "5. Availability and changes",
        "Niko is provided as-is, on a best-effort basis, without an uptime, latency, or feature-retention guarantee. Features may change, be restricted, or be removed without notice, and data may be lost in a failure. Niko is not a paid-critical or life-safety service, and you should not rely on it as one. Keep your own copies of anything you need to keep.",
      ],
      [
        "6. Moderation and blacklists",
        "The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms or the Community Policy, with or without notice, and may restrict features per server. A blacklist can be appealed once through the appeals process; an appeal does not guarantee reinstatement, and using a data-removal request to escape a restriction is itself a violation.",
      ],
      [
        "7. AI-generated content and Groq",
        <>
          <p>
            Niko's AI replies, image understanding, and voice transcription are provided through{" "}
            <a href="https://groq.com" target="_blank" rel="noreferrer">Groq</a>. When the AI feature is enabled on a server,
            the message being answered and the limited context described in the Privacy Policy are sent to Groq to generate a reply, and
            Groq's own terms and privacy policy apply to that request.
          </p>
          <p>
            AI output can be inaccurate, incomplete, biased, or unexpected. Automated moderation — including premium image scoring — is a
            helper, not a substitute for human moderation. Verify important information independently. The operator is not liable for harm
            from generated content or from a missed or mistaken classification. Operators of self-hosted instances may point their copy at
            a different provider; their choice is theirs, not ours.
          </p>
        </>,
      ],
      [
        "8. Payments and crypto",
        "Payments are collected through OxaPay, a third-party payment processor. Crypto transactions are irreversible once broadcast to the network, and the amount of crypto you send is set by the network and the provider's quote. You are responsible for sending the correct asset on the correct network, and for any taxes that apply to you. OxaPay's terms also apply to the payment itself. Never send funds to an address copied from somewhere other than the checkout page Niko shows you. If you believe a charge is wrong, contact support first; please do not start a chargeback or payment dispute for a service that was actually delivered, except where the law gives you that right.",
      ],
      [
        "9. Refunds",
        "Premium and donations are purchases of digital services delivered immediately and are generally non-refundable. If a payment was duplicated, charged in error, or never activated, contact us through the support server and we will review it in good faith and, where appropriate, extend the term, issue a credit, or arrange a refund through the processor. Nothing in these terms limits a mandatory consumer right you have under the law that applies to you.",
      ],
      [
        "10. Premium subscriptions",
        "Niko Premium costs $15 USD per server per month and is billed manually: you choose to renew, and a reminder is sent before the term ends. There is no automatic recurring charge. Premium is a licence to use server features for one server and one term; it is not a sale of software, does not create a partnership or fiduciary relationship, and does not give you any ownership in Niko. Premium follows the server, not the person who paid, and it is not transferable to another server without our agreement.",
      ],
      [
        "11. Economy and virtual items",
        "In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset, corrected, or wiped — for example after an exploit, a duplication bug, or a season reset. Premium is separate from virtual items and is never granted for in-bot currency. Buying, selling, or trading in-bot value for real money is not permitted.",
      ],
      [
        "12. Data retention and deletion",
        <>
          <p>
            The Privacy Policy sets out exactly what official instances keep, for how long, and what survives a deletion request. In
            summary: personal and configuration data is kept until you remove it or complete a{" "}
            <a href="/data-removal" onClick={(event) => { event.preventDefault(); navigate("/data-removal"); }}>data removal request</a>;
            AI conversation memory is a rolling window you can erase with <code>/clearhistory</code>; anonymous counters are kept for 90
            days plus lifetime totals; and moderation and safety records — blacklists, warnings, mutes, moderation cases, logs and ticket
            transcripts, giveaway bans, abuse strikes, and scam-image reports — are retained to protect communities and cannot be erased
            through that form.
          </p>
          <p>
            Using a deletion request to bypass a ban, warning, giveaway restriction, or investigation is a violation of these terms, and
            requests are reviewed before deletion runs. Where the law requires release of a retained record, a formal legal request with a
            court record or signed legal document and an official legal contact must be emailed to the bot owner at{" "}
            <a href={`mailto:${OWNER_EMAIL}`}>{OWNER_EMAIL}</a>; those matters are handled
            personally and confidentially. Self-hosted instances set their own retention and handle their own requests; we cannot delete or
            release data we do not hold.
          </p>
        </>,
      ],
      [
        "13. Volunteer-run project",
        "Niko is a free, volunteer-run community project. It is not a company, partnership, registered business, or other legal entity. The project is maintained by individuals in their personal capacity, in their own time, without payment from subscription revenue beyond covering service costs. No volunteer, contributor, or maintainer is your employee, agent, partner, or fiduciary, and none of them makes any personal promise about the service.",
      ],
      [
        "14. Third-party services",
        "Niko depends on services we do not control, including Discord, Groq, OxaPay, fal.ai, and hosting providers. Outages, policy changes, price changes, or account actions on those services can interrupt or end features. We are not responsible for third-party services, and we are not affiliated with or endorsed by Discord, Groq, OxaPay, or fal.ai.",
      ],
      [
        "15. Limitation of liability",
        "To the maximum extent permitted by law, the operator, maintainers, and volunteers are not liable for indirect, incidental, special, consequential, exemplary, or punitive damages, or for lost profits, revenue, data, goodwill, or server growth, arising from or related to Niko, premium, or any payment. Our total aggregate liability for all claims relating to a server's subscription is limited to the greater of the amount actually paid for that subscription in the three months before the claim or $15 USD. This does not limit liability that cannot be limited by law.",
      ],
      [
        "16. Indemnity",
        "To the maximum extent permitted by law, you agree to indemnify and hold harmless the operator, maintainers, and volunteers from claims, damages, losses, and reasonable costs arising from your server's use of Niko, content posted in it, your breach of these terms, or your violation of another person's rights.",
      ],
      [
        "17. Changes and discontinuation",
        "We may change, suspend, or discontinue Niko or premium, including a specific feature. If premium is discontinued during a paid term, we will handle the remaining term in good faith, for example by keeping the service running to the end of the term or by offering a pro-rata credit through the processor. We do not guarantee a cash refund where the law does not require one. If any provision of these terms is unenforceable, the rest stays in effect, and these terms are governed by the law that applies to the operator's place of residence, without overriding mandatory protections you have where you live.",
      ],
      [
        "18. Contact",
        <p>
          Questions, payment issues, and data requests can be sent through the Niko <SupportLink />. Data removal has its own page at{" "}
          <a href="/data-removal" onClick={(event) => { event.preventDefault(); navigate("/data-removal"); }}>/data-removal</a>, and
          formal legal requests go to the owner at{" "}
          <a href={`mailto:${OWNER_EMAIL}`}>{OWNER_EMAIL}</a>. Include the server ID and
          the payment or order reference so we can help quickly. Requests about a self-hosted instance must go to that instance's operator.
        </p>,
      ],
    ],
  },
  community: {
    title: "Community policy",
    intro:
      "These community expectations apply to every server that uses an official public Niko instance. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",
    sections: [
      [
        "Scope and instances",
        <>
          <p>This policy is enforced on the official public Niko instances we operate. Private, beta, and self-hosted copies are run by other people: we cannot investigate, moderate, or enforce anything on them, and reports about them cannot be handled by us. Send those to the operator of that instance.</p>
          <p>On official instances, enforcement applies to the server and to the people involved in a violation, whether or not they are its owners.</p>
        </>,
      ],
      [
        "Purpose",
        "Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines. These rules apply to channels, threads, voice channels, server profiles, and anything else a server controls where Niko is present.",
      ],
      [
        "Discrimination and harassment",
        "Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic. This includes slurs, coordinated targeting, and channels built around humiliating a person or group.",
      ],
      [
        "Illegal and malicious content",
        "Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law. Niko's scam filter exists to catch the worst of this automatically; it does not replace a server's own moderation.",
      ],
      [
        "Other prohibited conduct",
        "Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form. Servers must not use Niko to coordinate raids, mass-reporting campaigns, or the evasion of another server's moderation.",
      ],
      [
        "Enforcement and investigations",
        "When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action. Depending on what the investigation finds, we may warn, restrict individual features, blacklist the server, blacklist the accounts involved, or remove Niko from the server.",
      ],
      [
        "Obstruction of investigations",
        "Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants.",
      ],
      [
        "Evidence and records",
        "During an investigation we may preserve logs, transcripts, reports, and messages relevant to it. Those records are moderation and safety records: they are kept to protect communities and are not erased by a data-removal request. They are released only under the formal legal process described in the Privacy Policy.",
      ],
      [
        "Appeals",
        "A blacklist can be appealed once through the appeals process described in the support server. An appeal must be honest and complete; a second appeal for the same decision is not accepted, and appealing does not pause the restriction. A decision made to protect other users may stand even where a deletion request is later approved.",
      ],
      [
        "Reporting",
        <p>
          If you believe a server using Niko is violating this policy, report it through the Niko <SupportLink />. Include the server ID and,
          where possible, links or message IDs. Reports are reviewed by staff and handled confidentially, and a report made in good faith
          will never be held against you.
        </p>,
      ],
    ],
  },
};

export function LegalPage({ type }: { type: "privacy" | "terms" | "community" }) {
  const content = legalCopy[type];
  return (
    <>
      <PublicHeader page={type} />
      <main className="shell page-main legal-page"><div className="page-heading"><div className="eyebrow">Niko legal</div><h1>{content.title}</h1><p>{content.intro}</p><div className="legal-meta"><span>Effective date: <DiscordMarkdown text={EFFECTIVE_DATE} inline interactiveUsers={false} /></span><span>Updated by <DiscordMarkdown text={`<@${OWNER_USER_ID}>`} inline /></span></div></div><div className="legal-copy">{content.sections.map(([heading, text]) => <section key={heading}><h2>{heading}</h2>{typeof text === "string" ? <p>{text}</p> : text}</section>)}</div></main>
      <Footer />
    </>
  );
}
