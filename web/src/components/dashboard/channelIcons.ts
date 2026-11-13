/**
 * Discord's own channel glyphs, chosen from the kind the bot reports.
 *
 * Kept free of imports so the mapping is a plain data + function module: the
 * picker renders it, and the Python test suite executes it through Bun to pin
 * every kind's icon.
 */

/** The parts of a channel the icon depends on, as the resources API sends them. */
export type ChannelKind = { type?: string; nsfw?: boolean; rules?: boolean };

// Channel types as the bot reports them, mapped onto Discord's icon set.
export const CHANNEL_ICONS: Record<string, string> = {
  text: "text-channel",
  news: "announcement-channel",
  forum: "forum-channel",
  media: "media-channel",
  voice: "voice-channel",
  stage_voice: "stage-channel",
  public_thread: "thread",
  private_thread: "thread",
  announcement_thread: "thread",
};

// Discord draws a channel's special role and its age gate into the icon itself,
// so those win over the channel kind.
const NSFW_CHANNEL_TYPES = new Set(["text", "news"]);

export function channelIconName(channel: ChannelKind | undefined | null): string {
  if (!channel) return "cross";
  if (channel.rules) return "rules-channel";
  if (channel.nsfw && NSFW_CHANNEL_TYPES.has(channel.type || "")) return "text-channel-nsfw";
  return CHANNEL_ICONS[channel.type || ""] || "text-channel";
}
