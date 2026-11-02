import { type CSSProperties } from "react";
import { Select, type SelectOption } from "./Select";
import type { GuildResources } from "../../types";

type Channel = GuildResources["channels"][number];

type Props = {
  channels: Channel[];
  value: string;
  onChange: (value: string) => void;
  /** Label for the empty choice; pass null to make a channel mandatory. */
  placeholder?: string | null;
  ariaLabel?: string;
  disabled?: boolean;
  id?: string;
};

// Channel types as the bot reports them, mapped onto Discord's own icon set.
const CHANNEL_ICONS: Record<string, string> = {
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

function iconName(channel: Channel | undefined) {
  if (!channel) return "cross";
  return CHANNEL_ICONS[channel.type || ""] || "text-channel";
}

function ChannelGlyph({ channel, empty }: { channel?: Channel; empty?: boolean }) {
  const style = { "--mask-icon": `url(/assets/discord-icons/from-discord/${iconName(channel)}.svg)` } as CSSProperties;
  return <span className={`mask-icon channel-select-glyph${empty ? " is-empty" : ""}`} style={style} aria-hidden="true" />;
}

/** A channel picker: the shared `Select`, with Discord's channel icons as glyphs. */
export function ChannelSelect({ channels, value, onChange, placeholder = "Choose a channel", ariaLabel, disabled, id }: Props) {
  const options: SelectOption[] = channels.map((channel) => ({
    value: String(channel.id),
    label: `#${channel.name}`,
    glyph: <ChannelGlyph channel={channel} />,
  }));

  return <Select
    options={options}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    placeholderGlyph={placeholder === null ? undefined : <ChannelGlyph empty />}
    unknownOption={(saved) => ({ value: saved, label: `Saved channel · ${saved}`, glyph: <ChannelGlyph empty /> })}
    ariaLabel={ariaLabel}
    disabled={disabled}
    id={id}
  />;
}
