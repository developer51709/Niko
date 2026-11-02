import { DiscordAppBadge } from "./DiscordAppBadge";
import { DiscordMarkdown, useDiscordProfile, useDiscordUser } from "./DiscordMarkdown";
import { botEmojiToken, useBotEmojis } from "../data/botEmojis";
import { useBotConfig } from "../hooks/useBotConfig";

/** `<:name:id>` for one of the bot's application emojis, or nothing. */
export type DemoEmojiToken = (name: string) => string;

/**
 * One example message, drawn as the Discord message it would be.
 *
 * The member rows at the top are theirs: the invocation Discord prints above a
 * slash command, and/or a message they sent themselves. Both carry the
 * account's real avatar and name, and clicking either opens the same profile
 * popup a mention does. The reply below is the bot's
 * message — its own avatar, APP tag and timestamp over a container that draws
 * the reply through DiscordMarkdown, so mentions, headings, subtext and the
 * bot's custom emojis all render the way they do in the client.
 */
export function DemoDiscordMessage({ userId, command, message, messageTime, time, reply, note }: {
  /** The member whose command or message the card shows. */
  userId: string;
  /** The command they ran; omitted for messages the bot posts on its own. */
  command?: string;
  /** Something the member said themselves, drawn above the bot's reply. */
  message?: string;
  /** Discord's timestamp for that member message. */
  messageTime?: string;
  /** Discord's own timestamp for the reply. */
  time: string;
  /** Builds the reply text from the bot's live emoji catalog. */
  reply: (emoji: DemoEmojiToken) => string;
  note: string;
}) {
  const config = useBotConfig();
  const emojis = useBotEmojis();
  // Only a card that draws the member reads their profile; a bot-only message
  // opens profiles from the mention in its text instead.
  const user = useDiscordUser(command || message ? userId : "");
  const { openProfile, dialog: profileDialog } = useDiscordProfile();

  const botName = config?.bot_display_name || config?.bot_name || "Niko";
  const botId = config?.application_id || "";
  const botAvatar = config?.bot_avatar_url || null;
  const botVerified = Boolean(config?.bot_verified);

  // The bot's ids go stale whenever an emoji is re-uploaded, so the token is
  // built from the catalog it reports and stays empty if the name is gone.
  const emoji: DemoEmojiToken = (name) => {
    const live = emojis.find((entry) => entry.name === name);
    return live ? botEmojiToken(live) : "";
  };
  const text = reply(emoji);

  // A server nickname wins over the global name, exactly as Discord shows it.
  const memberName = (user?.guild_nick || user?.display_name || user?.username || "").trim();
  // The profile API hands back a 1024px avatar; a 40px circle only needs 64.
  const memberAvatar = user?.avatar_url ? user.avatar_url.replace(/size=\d+/, "size=64") : null;
  // Discord prints the guild's server tag beside a name that has one, badge
  // first, exactly as the profile returns it. Accounts without one show none.
  const serverTag = (user?.guild_tag || "").trim();
  const serverTagBadge = user?.guild_badge_url || null;
  const serverTagChip = serverTag ? (
    <span className="dc-server-tag" title={`Server tag ${serverTag}`}>
      {serverTagBadge && <img className="dc-server-tag-badge" src={serverTagBadge} alt="" loading="lazy" />}
      {serverTag}
    </span>
  ) : null;

  const openMember = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    void openProfile(userId, event.currentTarget);
  };
  const openBot = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (!botId) return;
    event.preventDefault();
    void openProfile(botId, event.currentTarget);
  };

  return (
    <figure className="home-example">
      <div className="discord-window">
        {command && (
          <div className="dc-invocation">
            <button
              type="button"
              className="dc-avatar dc-invocation-avatar"
              data-discord-user-id={userId}
              onClick={openMember}
              aria-label={`Open ${memberName || "this member"}'s Discord profile`}
            >
              {memberAvatar ? <img src={memberAvatar} alt="" loading="lazy" /> : memberName.slice(0, 1) || "?"}
            </button>
            <p className="dc-invocation-text">
              <button type="button" className="dc-invocation-name" data-discord-user-id={userId} onClick={openMember}>
                {memberName || "member"}
              </button>
              {serverTagChip}
              {" used "}
              {/* Discord shows the slash in its own little tile, then the command
                  without the leading slash, the way the client prints it. */}
              <span className="dc-invocation-command">
                {/* Discord's own command glyph: the blurple square with the
                    slash knocked straight out of it. */}
                <span
                  className="mask-icon dc-invocation-command-glyph"
                  style={{ "--mask-icon": "url(/assets/discord-icons/from-discord/command.svg)" } as React.CSSProperties}
                  aria-hidden="true"
                />
                {command.replace(/^\//, "")}
              </span>
            </p>
          </div>
        )}

        {message && (
          <article className="dc-message">
            <button
              type="button"
              className="dc-avatar"
              data-discord-user-id={userId}
              onClick={openMember}
              aria-label={`Open ${memberName || "this member"}'s Discord profile`}
            >
              {memberAvatar ? <img src={memberAvatar} alt="" loading="lazy" /> : memberName.slice(0, 1) || "?"}
            </button>
            <div className="dc-message-body">
              <header className="dc-message-head">
                <button type="button" className="dc-author" data-discord-user-id={userId} onClick={openMember}>{memberName || "member"}</button>
                {serverTagChip}
                {messageTime && <time className="dc-timestamp">{messageTime}</time>}
              </header>
              <DiscordMarkdown className="dc-member-text" text={message} />
            </div>
          </article>
        )}

        <article className="dc-message">
          <button type="button" className="dc-avatar" data-discord-user-id={botId} onClick={openBot} aria-label={`Open ${botName}'s Discord profile`}>
            {botAvatar ? <img src={botAvatar} alt="" /> : botName.slice(0, 1)}
          </button>
          <div className="dc-message-body">
            <header className="dc-message-head">
              <button type="button" className="dc-author" data-discord-user-id={botId} onClick={openBot}>{botName}</button>
              <DiscordAppBadge verified={botVerified} />
              <time className="dc-timestamp">{time}</time>
            </header>
            <div className="dc-container dc-reply-body">
              <DiscordMarkdown text={text} />
            </div>
          </div>
        </article>
      </div>

      <figcaption className="home-example-note">{note}</figcaption>
      {profileDialog}
    </figure>
  );
}
