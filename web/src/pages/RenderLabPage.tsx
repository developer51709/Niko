import { useMemo, useState } from "react";
import { DiscordBadgeList } from "../components/DiscordBadgeList";
import { DiscordEmoji, DiscordEmojiProvider, DiscordMarkdown, type DiscordMentionNames } from "../components/DiscordMarkdown";
import { botEmojiToken, botEmojisFailed, useBotEmojis } from "../data/botEmojis";
import { BADGE_GROUPS, profileBadges } from "../data/profileBadges";
import { navigate, RENDER_LAB_PATH } from "../router";

// A scratch page for eyeballing Discord text + profile popup rendering. It is
// intentionally unlinked, undocumented, and sign-in free: nothing here talks to
// an authenticated endpoint, so the only thing a visitor could ever find is a
// pile of sample messages.

type Sample = { label: string; source: string };

const SAMPLE_GROUPS: { group: string; samples: Sample[] }[] = [
  {
    group: "Inline formatting",
    samples: [
      { label: "Bold / italic / both", source: "**bold** *italic* ***both*** __underline__ _italic alt_ **_underline bold_**" },
      { label: "Strikethrough & spoiler", source: "~~struck out~~ and ||a spoiler|| plus ~~||both||~~" },
      { label: "Inline code", source: "Run `/help` to see `**markdown**` stay literal: `` not a thing" },
      { label: "Unclosed markers", source: "**never closed and *one asterisk* and __also open" },
      { label: "Escaped-looking markers", source: "5 * 3 = 15, a_b_c, snake_case_names, 2 ** 8" },
      { label: "Mixed nesting", source: "**bold with *italic inside* back to bold** and ||spoiler with **bold**||" },
    ],
  },
  {
    group: "Headings, quotes & subtext",
    samples: [
      { label: "Headings 1-4", source: "# Heading one\n## Heading two\n### Heading three\n#### Heading four" },
      { label: "Quote", source: "> Quoted line\n> second quoted line\nregular line after" },
      { label: "Subtext", source: "-# small print line\nNormal sized line" },
      { label: "Blank lines", source: "first paragraph\n\n\nsecond paragraph" },
    ],
  },
  {
    group: "Lists & tables",
    samples: [
      { label: "Bullets", source: "- first bullet\n- second bullet\n* third bullet with **bold**" },
      { label: "Ordered", source: "1. first step\n2. second step\n10. tenth step" },
      { label: "Task list", source: "- [x] shipped rendering\n- [ ] verify popup\n- [X] uppercase check" },
      {
        label: "Table",
        source: "| Command | What it does |\n| --- | --- |\n| /help | Shows the help menu |\n| /ban | Bans a member |",
      },
      { label: "Table without separator", source: "| a | b |\n| c | d |" },
    ],
  },
  {
    group: "Code blocks",
    samples: [
      { label: "Fenced block", source: "```\nplain code block\n  indented line\n```" },
      { label: "Fenced with language", source: "```python\nprint(\"hello\")\n# comment\n```" },
      { label: "Fenced JSON", source: "```json\n{\"level\": 42, \"coins\": 1200}\n```" },
      { label: "Unclosed fence", source: "```\nthis fence never closes\nsecond line" },
    ],
  },
  {
    group: "Links & emoji",
    samples: [
      { label: "Bare URL", source: "Read the docs at https://niko.sryze.cc/docs for details." },
      { label: "Masked link", source: "[Niko documentation](https://niko.sryze.cc/docs) and a [bad one]()" },
      { label: "Link with spoiler", source: "||[spoiler link](https://example.com)||" },
      { label: "Unknown & invalid emoji", source: "<:coffee:123456> unknown id, <a:wave:654321> animated unknown, :not_an_emoji: plain colons, <:no_id:> no id" },
      { label: "Unicode emoji", source: "✨ cozy vibes 🌙 é 😀 (no colon syntax needed)" },
    ],
  },
  {
    group: "Timestamps",
    samples: [
      { label: "Short time / long time", source: "<t:1788800225:t> then <t:1788800225:T>" },
      { label: "Dates", source: "<t:1788800225:d> · <t:1788800225:D> · <t:1788800225:f> · <t:1788800225:F>" },
      { label: "Relative", source: "Released <t:1788800225:R>" },
      { label: "No style / invalid", source: "<t:1788800225> <t:not-a-number:f> <t:1788800225:x>" },
    ],
  },
  {
    group: "Mentions",
    samples: [
      { label: "User mention", source: "Ping <@123456789012345678> and legacy <@!123456789012345678>" },
      { label: "Role & channel", source: "Role <@&111111111111111111> in <#222222222222222222>" },
      { label: "Everyone & here", source: "@everyone @here heads up" },
      { label: "Broken mention", source: "<@> <@!> <@&> <#> not mentions" },
    ],
  },
  {
    group: "Edge cases",
    samples: [
      { label: "Empty-ish", source: "   " },
      { label: "Very long unbroken string", source: "https://example.com/" + "a".repeat(180) },
      { label: "Mixed script", source: "こんにちは 世界 مرحبا بالعالم Ω≈ç√∫˜µ≤≥÷ ᴮᴸᴼᴼᴰ" },
      { label: "Markdown-ish symbols", source: "| pipe | ` tick | ** stars ** | __ underscores __ | ~~ tilde ~~" },
      { label: "Multiple blank lines at end", source: "ends with newlines\n\n\n" },
    ],
  },
];

// Every badge the popups can draw, grouped the way the badge section below
// shows them. Built once so each group is resolved a single time.
const BADGE_SECTIONS = BADGE_GROUPS.map((group) => ({ ...group, badges: profileBadges(group.keys) }));

// An emoji the CDN cannot resolve — a stale id, a deleted emoji, one from
// another server — has to read as `:name:` text and leave the formatting around
// it alone.
const BROKEN_EMOJI_SAMPLE =
  "**bold** <:not_a_real_emoji:123456789012345678> *italic* <:badge_owner:900001> __underline__ <:deleted:0> ~~strike~~ ||spoiler|| \u00e9 <a:ghost:900002>";

const SAMPLE_NAMES: DiscordMentionNames = {
  user: { "123456789012345678": "Known User" },
  role: { "111111111111111111": "Known Role" },
  channel: { "222222222222222222": "known-channel" },
};

function readIdsFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const raw = `${params.get("users") || ""},${params.get("user") || ""}`;
  return raw
    .split(",")
    .map((value) => value.trim())
    .filter((value) => /^\d{1,22}$/.test(value))
    .slice(0, 20);
}

const labStyles = `
.render-lab{max-width:1100px;margin:0 auto;padding:34px 20px 80px}
.render-lab>h1{margin:10px 0 8px;font-size:30px;letter-spacing:-.02em}
.render-lab-section>h2{margin:0 0 4px;font-size:18px}
/* Only the lab's own section labels, never the Discord headings rendered in a
   sample — those keep their real sizes and casing. */
.render-lab-section>h3,.render-lab-badge-group>h3{margin:0 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--dim)}
.render-lab p{margin:0;color:var(--muted);font-size:13px;line-height:1.7}
.render-lab-kicker{color:var(--accent-dark);font:700 9px "Space Mono",monospace;letter-spacing:.14em;text-transform:uppercase}
.render-lab-path{display:inline-block;margin-top:6px;padding:4px 7px;background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:5px;color:var(--muted);font:11px "Space Mono",monospace}
.render-lab-controls{display:flex;flex-wrap:wrap;align-items:flex-end;gap:10px;margin:16px 0 0;padding:12px;background:var(--surface);border:1px solid var(--line-soft);border-radius:9px}
.render-lab-controls label{display:grid;gap:4px;font:700 9px "Space Mono",monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--dim)}
.render-lab-controls input{min-width:280px;padding:7px 9px;color:var(--ink);background:var(--surface-muted);border:1px solid var(--line);border-radius:6px;font:11px "Space Mono",monospace}
.render-lab-controls button{align-self:flex-end;padding:7px 11px;color:var(--ink);background:var(--surface-muted);border:1px solid var(--line);border-radius:6px;font-size:11px;font-weight:650}
.render-lab-controls button:hover{border-color:var(--accent-dark);color:var(--accent-dark)}
.render-lab-empty{margin-top:10px;padding:12px;color:var(--muted);background:var(--surface-muted);border:1px dashed var(--line);border-radius:8px;font-size:12px}
.render-lab-section{margin-top:26px;padding:18px;background:var(--surface);border:1px solid var(--line-soft);border-radius:12px}
.render-lab-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:12px;margin-top:14px}
.render-lab-sample{min-width:0;padding:12px;background:#0f1013;border:1px solid #26282d;border-radius:9px}
.render-lab-sample>h4{margin:0 0 8px;color:#dce1e8;font-size:11px;font-weight:650}
.render-lab-source{max-height:150px;margin:0 0 10px;padding:9px 10px;overflow:auto;color:#8f96a1;background:#08090b;border:1px solid #22242a;border-radius:6px;font:11px/1.5 "Space Mono",monospace;white-space:pre-wrap;overflow-wrap:anywhere}
.render-lab-render{padding:10px;color:#dbdee1;background:#313338;border-radius:8px;font-size:13.5px}
.render-lab-render .discord-md-block-code{margin:6px 0}
.render-lab-badge-group{margin-top:18px}
.render-lab-badge-group>p{margin-bottom:0}
.render-lab-emoji-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,240px),1fr));gap:6px;margin:14px 0 0;padding:0;list-style:none}
.render-lab-emoji-list li{display:flex;align-items:center;gap:8px;min-width:0;padding:7px 9px;background:var(--surface-muted);border:1px solid var(--line-soft);border-radius:8px}
.render-lab-emoji-list .discord-markdown{flex:0 0 auto;color:#dbdee1}
.render-lab-emoji-list code{min-width:0;overflow:hidden;color:var(--muted);font:10.5px "Space Mono",monospace;text-overflow:ellipsis;white-space:nowrap}
.render-lab-emoji-list .render-lab-emoji-note{color:var(--accent-dark);font:700 9px "Space Mono",monospace;letter-spacing:.06em;text-transform:uppercase}
.render-lab-mentions{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
@media(max-width:560px){.render-lab{padding:22px 14px 60px}.render-lab-controls input{min-width:0;width:100%}}
`;

function SampleCard({ sample }: { sample: Sample }) {
  return (
    <article className="render-lab-sample">
      <h4>{sample.label}</h4>
      <pre className="render-lab-source">{sample.source}</pre>
      <DiscordMarkdown text={sample.source} className="render-lab-render" />
    </article>
  );
}

export function RenderLabPage() {
  const initialIds = useMemo(readIdsFromUrl, []);
  const [ids, setIds] = useState<string[]>(initialIds);
  const [draft, setDraft] = useState("");
  const [guildId, setGuildId] = useState("");
  // The bot's own emojis (src/config/emojis.py), read from the bot at runtime:
  // the parade below is every one of them, and the list draws each emoji next
  // to the exact token the bot sends. Nothing here is a copy of the config, so
  // an added or re-uploaded emoji shows up on the next page load.
  const emojis = useBotEmojis();
  const emojiParade = useMemo(() => emojis.map(botEmojiToken).join(" "), [emojis]);
  // The popup samples draw whichever id the bot currently has for that emoji,
  // so a re-uploaded emoji never leaves a dead id in the lab.
  const popupSample = emojis.find((emoji) => emoji.name === "hypesquad_bravery") || emojis[0];

  const addIds = () => {
    const next = draft
      .split(/[\s,]+/)
      .map((value) => value.trim())
      .filter((value) => /^\d{1,22}$/.test(value));
    if (!next.length) return;
    setIds((current) => Array.from(new Set([...current, ...next])).slice(0, 20));
    setDraft("");
  };

  const mentionText = ids.map((id) => `<@${id}>`).join(" · ");

  return (
    <DiscordEmojiProvider guildName="Niko" guildIconUrl="/niko-app-icon.svg">
    <>
      <style>{labStyles}</style>
      <main className="render-lab">
        <div className="render-lab-kicker">Internal scratch page</div>
        <h1>Discord text &amp; profile rendering lab</h1>
        <p>
          Every supported markdown case and the user profile popup, rendered with the real components and the real public
          APIs. No sign-in is needed and nothing here writes any data — it exists only so text rendering can be checked
          by eye.
        </p>
        <span className="render-lab-path">{RENDER_LAB_PATH}</span>
        <p style={{ marginTop: 10 }}>
          <a href="/" onClick={(event) => { event.preventDefault(); navigate("/"); }}>← Back to the site</a>
        </p>

        <section className="render-lab-section" aria-labelledby="render-lab-popup">
          <h2 id="render-lab-popup">Profile popup</h2>
          <p>Click a mention below to open the Discord profile popup. Popups load from <code>/api/discord/users/&lt;id&gt;</code>.</p>
          <div className="render-lab-controls">
            <label>
              User IDs (comma separated)
              <input
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => { if (event.key === "Enter") addIds(); }}
                placeholder="123456789012345678, 987654321098765432"
                aria-label="Discord user IDs to test"
              />
            </label>
            <button type="button" onClick={addIds}>Add</button>
            <button type="button" onClick={() => setIds([])}>Clear</button>
            <label>
              Guild ID (optional, for mention names)
              <input
                value={guildId}
                onChange={(event) => setGuildId(event.target.value.replace(/[^\d]/g, ""))}
                placeholder="123456789012345678"
                aria-label="Guild ID for mention name resolution"
              />
            </label>
          </div>
          {ids.length ? (
            <>
              <div className="render-lab-render" style={{ marginTop: 14 }}>
                <DiscordMarkdown text={mentionText} guildId={guildId || undefined} />
              </div>
              <div className="render-lab-render" style={{ marginTop: 10 }}>
                <DiscordMarkdown text={mentionText} guildId={guildId || undefined} interactiveUsers={false} />
                <p style={{ marginTop: 6, fontSize: 11 }}>Same mentions with <code>interactiveUsers=false</code>: no popup.</p>
              </div>
            </>
          ) : (
            <p className="render-lab-empty">
              Add a Discord user ID to test the popup. Use your own ID (or a teammate&apos;s) — the lookup is the same public
              endpoint the transcript popups use, so an ID the bot cannot see returns the error state.
            </p>
          )}
        </section>

        <section className="render-lab-section" aria-labelledby="render-lab-badges">
          <h2 id="render-lab-badges">Profile badges</h2>
          <p>
            Every badge the profile popups can draw. Click any badge to see the art, name and description its popup shows.
          </p>
          {BADGE_SECTIONS.map((group) => (
            <div className="render-lab-badge-group" key={group.title}>
              <h3>{group.title}</h3>
              <p>{group.blurb}</p>
              <div className="render-lab-render" style={{ marginTop: 10 }}>
                <DiscordBadgeList badges={group.badges} label={`${group.title} preview`} />
              </div>
            </div>
          ))}
        </section>

        <section className="render-lab-section" aria-labelledby="render-lab-emoji">
          <h2 id="render-lab-emoji">Custom emoji</h2>
          <p>
            The bot's own emojis, read live from <code>/api/emojis</code> — the names and ids parsed out of{" "}
            <code>src/config/emojis.py</code> with the ids the bot's emoji sync re-uploaded, so this page draws whatever the
            bot is sending right now. An emoji the CDN cannot resolve falls back to the <code>:name:</code> text Discord
            shows, so a dead emoji can neither leave a broken image nor break the formatting around it.
          </p>
          {emojis.length ? (
            <div className="render-lab-render" style={{ marginTop: 12 }}>
              <DiscordMarkdown text={emojiParade} />
            </div>
          ) : (
            <p className="render-lab-empty">
              {botEmojisFailed()
                ? <>The bot's emojis could not be read from <code>/api/emojis</code>. Reload the page to try again.</>
                : <>Loading the bot's emojis from <code>/api/emojis</code>…</>}
            </p>
          )}
          <h3 style={{ marginTop: 18 }}>Emoji popup layouts</h3>
          <p>
            Click either emoji: the first opens the application-emoji popup, the second previews the server-emoji popup
            with its Nitro prompt and server row.
          </p>
          {popupSample ? (
            <div className="render-lab-render" style={{ marginTop: 10 }}>
              <span className="discord-markdown"><DiscordEmoji name={popupSample.name} id={popupSample.id} animated={popupSample.animated} className="discord-md-emoji" /></span>
              <span> application emoji · </span>
              <span className="discord-markdown"><DiscordEmoji name={popupSample.name} id={popupSample.id} animated={popupSample.animated} className="discord-md-emoji" source="server" /></span>
              <span> server emoji</span>
            </div>
          ) : (
            <p className="render-lab-empty">The popup samples need the emoji list above.</p>
          )}
          <h3 style={{ marginTop: 18 }}>Emoji the CDN cannot resolve</h3>
          <p>Bold, italic, underline, strike and spoiler around emojis with an unknown id, a stale id and no id at all.</p>
          <div className="render-lab-render" style={{ marginTop: 10 }}>
            <DiscordMarkdown text={BROKEN_EMOJI_SAMPLE} />
          </div>
          <h3 style={{ marginTop: 18 }}>Every bot emoji</h3>
          <p>
            Each emoji next to the exact <code>&lt;:name:id&gt;</code> token the bot sends, so a missing one is visible as
            text in the list as well.
          </p>
          {emojis.length > 0 && <ul className="render-lab-emoji-list">
            {emojis.map((emoji) => <li key={`${emoji.name}-${emoji.id}`}>
              <DiscordMarkdown text={botEmojiToken(emoji)} inline />
              <code title={botEmojiToken(emoji)}>{botEmojiToken(emoji)}</code>
              {emoji.placeholder && <span className="render-lab-emoji-note">stub id</span>}
            </li>)}
          </ul>}
        </section>

        <section className="render-lab-section" aria-labelledby="render-lab-inline">
          <h2 id="render-lab-inline">Mentions with names supplied</h2>
          <p>Mention labels come from <code>mentionNames</code> here instead of the resolver API.</p>
          <div className="render-lab-render" style={{ marginTop: 12 }}>
            <DiscordMarkdown
              text="Ping <@123456789012345678> in <#222222222222222222> with <@&111111111111111111>."
              mentionNames={SAMPLE_NAMES}
            />
          </div>
        </section>

        <section className="render-lab-section" aria-labelledby="render-lab-inline-text">
          <h2 id="render-lab-inline-text">Inline variant</h2>
          <p><code>inline</code> renders as a span, used inside compact UI such as log lines and list rows.</p>
          <div className="render-lab-render" style={{ marginTop: 12 }}>
            <DiscordMarkdown text="**Inline** sample with a ||spoiler|| and `code`" inline />
          </div>
        </section>

        {SAMPLE_GROUPS.map((group, groupIndex) => (
          <section className="render-lab-section" key={group.group} aria-labelledby={`render-lab-group-${groupIndex}`}>
            <h3 id={`render-lab-group-${groupIndex}`}>{group.group}</h3>
            <div className="render-lab-grid">
              {group.samples.map((sample) => <SampleCard sample={sample} key={sample.label} />)}
            </div>
          </section>
        ))}
      </main>
    </>
    </DiscordEmojiProvider>
  );
}
