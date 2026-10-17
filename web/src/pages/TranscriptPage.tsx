import { useState, useEffect } from "react";
import type { CSSProperties } from "react";
import { DiscordMarkdown, type DiscordMentionNames } from "../components/DiscordMarkdown";

// ── Types mirroring the stored transcript message payloads ────────────────

type TranscriptEmbed = {
  title?: string;
  description?: string;
  url?: string;
  color?: number;
  type?: string;
  timestamp?: string;
  footer?: { text?: string; icon_url?: string; proxy_icon_url?: string };
  image?: { url?: string; proxy_url?: string; width?: number; height?: number };
  thumbnail?: { url?: string; proxy_url?: string; width?: number; height?: number };
  video?: { url?: string; proxy_url?: string };
  author?: { name?: string; url?: string; icon_url?: string; proxy_icon_url?: string };
  fields?: { name?: string; value?: string; inline?: boolean }[];
  provider?: { name?: string; url?: string };
};

type Cv2Media = {
  url?: string;
  proxy_url?: string;
  width?: number;
  height?: number;
  content_type?: string;
};

type Cv2GalleryItem = {
  media?: Cv2Media;
  description?: string;
  spoiler?: boolean;
};

type Cv2Component = {
  type: number;
  accent_color?: number;
  components?: Cv2Component[];
  accessory?: Cv2Component;
  content?: string;
  divider?: boolean;
  spacing?: number;
  items?: Cv2GalleryItem[];
  media?: Cv2Media;
  description?: string;
  label?: string;
  url?: string;
  style?: number;
  disabled?: boolean;
  emoji?: { name?: string; id?: string; animated?: boolean };
  spoiler?: boolean;
};

type TranscriptMessage = {
  timestamp: string;
  author: string;
  author_id: string | number;
  content: string;
  attachments?: string[];
  embeds?: TranscriptEmbed[];
  components?: Cv2Component[];
  stickers?: TranscriptSticker[];
};

type TranscriptSticker = {
  id?: string | number;
  name?: string;
  format_type?: number;
  url?: string;
};

type TranscriptData = {
  transcript_id: string;
  guild_id: number;
  channel_id: number;
  channel_name: string;
  opener_id: number;
  category: string;
  claimed_by: number | null;
  message_count: number;
  messages: TranscriptMessage[];
  created_at: string;
  mention_names?: DiscordMentionNames;
};

const FORMATS = [
  { key: "txt", label: "TXT", icon: "📄" },
  { key: "html", label: "HTML", icon: "🌐" },
  { key: "csv", label: "CSV", icon: "📊" },
  { key: "json", label: "JSON", icon: "{ }" },
] as const;

// ── Small helpers ──────────────────────────────────────────────────────────

const colorCss = (color?: number): string => {
  if (typeof color !== "number" || color < 0 || color > 0xffffff) return "";
  return `#${color.toString(16).padStart(6, "0")}`;
};

const mediaUrl = (media?: Cv2Media): string => media?.url || media?.proxy_url || "";

const isImageUrl = (url: string): boolean =>
  /\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)/i.test(url) || url.startsWith("data:image/");

const isVideoUrl = (url: string): boolean =>
  /\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)/i.test(url) || url.startsWith("data:video/");

const stickerUrl = (sticker: TranscriptSticker): string => {
  if (sticker.url) return sticker.url;
  if (!sticker.id) return "";
  return `https://cdn.discordapp.com/stickers/${sticker.id}.${sticker.format_type === 4 ? "gif" : "png"}`;
};

function isVideoMedia(media?: Cv2Media): boolean {
  const url = mediaUrl(media);
  if (!url) return false;
  if (media?.content_type?.startsWith("video/")) return true;
  return isVideoUrl(url);
}

// ── Discord-style markdown renderer ───────────────────────────────────────
function MarkdownBlock({ text, mentionNames }: { text: string; mentionNames?: DiscordMentionNames }) {
  return <DiscordMarkdown text={text} mentionNames={mentionNames} />;
}

// ── Embed renderer ─────────────────────────────────────────────────────────

function EmbedView({ embed, mentionNames }: { embed: TranscriptEmbed; mentionNames?: DiscordMentionNames }) {
  const color = colorCss(embed.color) || "#5865f2";
  const author = embed.author;
  const footer = embed.footer;
  const thumbUrl = mediaUrl(embed.thumbnail);
  const imgUrl = mediaUrl(embed.image);

  return (
    <div
      style={{
        display: "flex",
        gap: 12,
        maxWidth: 560,
        marginTop: 8,
        background: "#2b2d31",
        border: "1px solid #3f4147",
        borderLeft: `4px solid ${color}`,
        borderRadius: 6,
        padding: "10px 12px",
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        {author?.name && (
          <div style={{ color: "#f2f3f5", fontWeight: 600, fontSize: 13, marginBottom: 4 }}>
            {author.icon_url && (
              <img
                src={author.icon_url || author.proxy_icon_url}
                alt=""
                style={{ width: 18, height: 18, borderRadius: "50%", verticalAlign: "-4px", marginRight: 6 }}
              />
            )}
            {author.name}
          </div>
        )}
        {embed.title && (
          <div style={{ color: "#00a8fc", fontWeight: 600, margin: "2px 0 4px", fontSize: 14 }}>
            {embed.url ? (
              <a href={embed.url} target="_blank" rel="noopener noreferrer" style={{ color: "inherit", textDecoration: "none" }}>
                <MarkdownBlock text={embed.title} mentionNames={mentionNames} />
              </a>
            ) : (
              <MarkdownBlock text={embed.title} mentionNames={mentionNames} />
            )}
          </div>
        )}
        {embed.description && (
          <div style={{ color: "#dbdee1", fontSize: 13, lineHeight: 1.5 }}>
            <MarkdownBlock text={embed.description} mentionNames={mentionNames} />
          </div>
        )}
        {embed.fields && embed.fields.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px 12px", marginTop: 8 }}>
            {embed.fields.map((field, i) => (
              <div
                key={i}
                style={{ flex: field.inline ? "0 1 45%" : "1 1 100%", minWidth: 0, marginBottom: 4 }}
              >
                {field.name && (
                  <div style={{ color: "#f2f3f5", fontWeight: 600, fontSize: 13, marginBottom: 2 }}>
                    <MarkdownBlock text={field.name} mentionNames={mentionNames} />
                  </div>
                )}
                {field.value && (
                  <div style={{ color: "#dbdee1", fontSize: 13 }}>
                    <MarkdownBlock text={field.value} mentionNames={mentionNames} />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        {imgUrl && (
          <a href={imgUrl} target="_blank" rel="noopener noreferrer" style={{ display: "block", marginTop: 8 }}>
            <img
              src={imgUrl}
              alt=""
              style={{ maxWidth: "100%", maxHeight: 300, borderRadius: 4, display: "block" }}
              onError={(e) => {
                (e.currentTarget as HTMLImageElement).style.display = "none";
              }}
            />
          </a>
        )}
        {(footer?.text || embed.timestamp) && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6, color: "#949ba4", fontSize: 11 }}>
            {footer?.icon_url && (
              <img
                src={footer.icon_url || footer.proxy_icon_url}
                alt=""
                style={{ width: 16, height: 16, borderRadius: "50%" }}
              />
            )}
            {footer?.text && <span>{footer.text}</span>}
            {embed.timestamp && <span>{String(embed.timestamp).replace("T", " ").replace("+00:00", " UTC")}</span>}
          </div>
        )}
      </div>
      {thumbUrl && (
        <a href={thumbUrl} target="_blank" rel="noopener noreferrer" style={{ flex: "0 0 auto" }}>
          <img
            src={thumbUrl}
            alt=""
            style={{ width: 80, height: 80, borderRadius: 6, objectFit: "cover" }}
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        </a>
      )}
    </div>
  );
}

// ── CV2 component renderer ─────────────────────────────────────────────────

function Cv2ComponentView({ component, mentionNames }: { component: Cv2Component; mentionNames?: DiscordMentionNames }) {
  switch (component.type) {
    case 17: {
      // Container
      const accent = colorCss(component.accent_color);
      return (
        <div
          style={{
            display: "flex",
            overflow: "hidden",
            maxWidth: 560,
            marginTop: 8,
            background: "#2b2d31",
            border: `1px solid ${accent || "#3f4147"}`,
            borderRadius: 12,
          }}
        >
          {accent && (
            <div style={{ flex: "0 0 4px", background: accent }} />
          )}
          <div style={{ flex: 1, minWidth: 0, padding: "6px 12px 8px" }}>
            {(component.components || []).map((child, i) => (
              <Cv2ComponentView key={i} component={child} mentionNames={mentionNames} />
            ))}
          </div>
        </div>
      );
    }
    case 1: {
      // Action row
      return (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, margin: "6px 0" }}>
          {(component.components || []).map((child, i) => (
            <Cv2ComponentView key={i} component={child} mentionNames={mentionNames} />
          ))}
        </div>
      );
    }
    case 2: {
      // Button
      const emoji = component.emoji;
      const label = `${emoji?.name ?? ""}${component.label ? ` ${component.label}` : ""}`.trim();
      const isLink = component.style === 5 && !!component.url;
      if (isLink) {
        return (
          <a
            href={component.url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "inline-block",
              padding: "3px 14px",
              background: "#5865f2",
              borderRadius: 4,
              color: "#fff",
              fontSize: 13,
              fontWeight: 600,
              textDecoration: "none",
            }}
          >
            {label || "Button"}
          </a>
        );
      }
      return (
        <span
          style={{
            display: "inline-block",
            padding: "3px 14px",
            background: "#4e5058",
            borderRadius: 4,
            color: component.disabled ? "#8a8e96" : "#f2f3f5",
            fontSize: 13,
            cursor: component.disabled ? "not-allowed" : "default",
            opacity: component.disabled ? 0.55 : 1,
          }}
        >
          {label || "Button"}
        </span>
      );
    }
    case 9: {
      // Section
      const children = [...(component.components || [])];
      if (component.accessory) children.push(component.accessory);
      return (
        <div style={{ display: "flex", alignItems: "center", gap: 10, margin: "4px 0" }}>
          {children.map((child, i) => (
            <Cv2ComponentView key={i} component={child} mentionNames={mentionNames} />
          ))}
        </div>
      );
    }
    case 10: {
      // TextDisplay
      return (
        <div style={{ color: "#dbdee1", fontSize: 14, lineHeight: 1.5, margin: "4px 0", wordBreak: "break-word" }}>
          <MarkdownBlock text={component.content || ""} mentionNames={mentionNames} />
        </div>
      );
    }
    case 18: {
      // Label
      return (
        <div
          style={{
            color: "#f2f3f5",
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.04em",
            fontSize: 12,
            margin: "4px 0",
          }}
        >
          {component.content}
        </div>
      );
    }
    case 14: {
      // Separator
      return (
        <div
          style={{
            margin: component.divider === false ? "6px 0" : "9px 0",
            ...(component.divider === false ? {} : { borderTop: "1px solid #3f4147" }),
          }}
        />
      );
    }
    case 11: {
      // Thumbnail
      const url = mediaUrl(component.media);
      if (!url) return null;
      return (
        <a href={url} target="_blank" rel="noopener noreferrer" style={{ flex: "0 0 auto" }}>
          <img
            src={url}
            alt={component.description || ""}
            style={{ width: 40, height: 40, borderRadius: "50%", objectFit: "cover", display: "block" }}
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        </a>
      );
    }
    case 12: {
      // MediaGallery
      const items = component.items || [];
      const visible = items.filter((item) => mediaUrl(item.media));
      if (visible.length === 0) return null;
      return (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(auto-fill, minmax(${Math.min(220, Math.max(140, Math.floor(560 / Math.max(1, visible.length))))}px, 1fr))`,
            gap: 6,
            margin: "6px 0",
          }}
        >
          {visible.map((item, i) => {
            const url = mediaUrl(item.media)!;
            const caption = item.description;
            if (isVideoMedia(item.media)) {
              return (
                <figure key={i} style={{ margin: 0 }}>
                  <video
                    src={url}
                    controls
                    preload="metadata"
                    style={{ width: "100%", maxHeight: 260, borderRadius: 6, background: "#1e1f22" }}
                  />
                  {caption && (
                    <figcaption style={{ color: "#949ba4", fontSize: 11, marginTop: 2 }}>{caption}</figcaption>
                  )}
                </figure>
              );
            }
            if (isImageUrl(url)) {
              return (
                <figure key={i} style={{ margin: 0 }}>
                  <a href={url} target="_blank" rel="noopener noreferrer" style={{ display: "block" }}>
                    <img
                      src={url}
                      alt={caption || ""}
                      style={{ width: "100%", maxHeight: 260, objectFit: "cover", borderRadius: 6, display: "block", background: "#1e1f22" }}
                      onError={(e) => {
                        (e.currentTarget as HTMLImageElement).style.display = "none";
                      }}
                    />
                  </a>
                  {caption && (
                    <figcaption style={{ color: "#949ba4", fontSize: 11, marginTop: 2 }}>{caption}</figcaption>
                  )}
                </figure>
              );
            }
            return (
              <a
                key={i}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "6px 10px",
                  background: "#383a40",
                  borderRadius: 6,
                  color: "#dbdee1",
                  fontSize: 12,
                  textDecoration: "none",
                }}
              >
                📎 {caption || "Attachment"}
              </a>
            );
          })}
        </div>
      );
    }
    case 13: {
      // FileComponent (attachment inside a layout message)
      const url = mediaUrl(component.media) || component.url || "";
      if (!url) return null;
      return (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          style={{ display: "block", margin: "4px 0", color: "#00a8fc", fontSize: 12.5, textDecoration: "none" }}
        >
          📎 {component.label || "Attachment"}
        </a>
      );
    }
    default:
      return null;
  }
}

function Cv2Components({ components, mentionNames }: { components: Cv2Component[]; mentionNames?: DiscordMentionNames }) {
  return (
    <>
      {components.map((comp, i) => (
        <Cv2ComponentView key={i} component={comp} mentionNames={mentionNames} />
      ))}
    </>
  );
}

// ── One transcript message ─────────────────────────────────────────────────

function MessageContent({ text, mentionNames }: { text: string; mentionNames?: DiscordMentionNames }) {
  return <MarkdownBlock text={text} mentionNames={mentionNames} />;
}

function TranscriptMessageView({ msg, mentionNames }: { msg: TranscriptMessage; mentionNames?: DiscordMentionNames }) {
  const hasRich = !!(
    (msg.attachments && msg.attachments.length > 0) ||
    (msg.embeds && msg.embeds.length > 0) ||
    (msg.components && msg.components.length > 0) ||
    (msg.stickers && msg.stickers.length > 0)
  );

  return (
    <div
      style={{
        padding: "10px 16px",
        borderBottom: "1px solid #2b2d31",
        fontSize: 14,
        lineHeight: 1.6,
      }}
    >
      <div style={{ marginBottom: 2 }}>
        <span style={{ color: "#949ba4", fontSize: 11, fontFamily: "monospace" }}>{msg.timestamp}</span>{" "}
        <span style={{ color: "#f2f3f5", fontWeight: 600 }}>{msg.author}</span>{" "}
        <span style={{ color: "#949ba4", fontSize: 11 }}>({msg.author_id})</span>
      </div>

      {msg.content ? (
        <div style={{ color: "#dbdee1" }}>
          <MessageContent text={msg.content} mentionNames={mentionNames} />
        </div>
      ) : !hasRich ? (
        <div style={{ color: "#6d737a", fontStyle: "italic", fontSize: 13 }}>
          Message content unavailable
        </div>
      ) : null}

      {msg.attachments && msg.attachments.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 4 }}>
          {msg.attachments.map((url, j) => {
            if (isVideoUrl(url)) {
              return (
                <video
                  key={j}
                  src={url}
                  controls
                  preload="metadata"
                  style={{ maxWidth: 360, maxHeight: 260, borderRadius: 6, background: "#1e1f22" }}
                />
              );
            }
            if (isImageUrl(url)) {
              return (
                <a key={j} href={url} target="_blank" rel="noopener noreferrer" style={{ display: "block" }}>
                  <img
                    src={url}
                    alt=""
                    style={{ maxWidth: 300, maxHeight: 260, objectFit: "cover", borderRadius: 6, display: "block", background: "#1e1f22" }}
                    onError={(e) => {
                      // If inline preview fails, degrade to a file link
                      const el = e.currentTarget as HTMLImageElement;
                      el.style.display = "none";
                    }}
                  />
                </a>
              );
            }
            return (
              <a
                key={j}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#00a8fc", fontSize: 12, textDecoration: "none" }}
              >
                📎 Attachment
              </a>
            );
          })}
        </div>
      )}

      {msg.embeds && msg.embeds.length > 0 && (
        <>
          {msg.embeds.map((embed, i) => (
            <EmbedView key={i} embed={embed} mentionNames={mentionNames} />
          ))}
        </>
      )}

      {msg.stickers && msg.stickers.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
          {msg.stickers.map((sticker, i) => {
            const url = stickerUrl(sticker);
            return url ? (
              <a key={i} href={url} target="_blank" rel="noopener noreferrer" style={{ display: "block" }}>
                <img
                  src={url}
                  alt={sticker.name || "Discord sticker"}
                  title={sticker.name || "Discord sticker"}
                  style={{ width: 160, maxWidth: "100%", maxHeight: 160, objectFit: "contain", display: "block" }}
                />
              </a>
            ) : null;
          })}
        </div>
      )}

      {msg.components && msg.components.length > 0 && <Cv2Components components={msg.components} mentionNames={mentionNames} />}
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────

export function TranscriptPage({ transcriptId }: { transcriptId: string }) {
  const [data, setData] = useState<TranscriptData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    fetch(`/api/transcript/${transcriptId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Transcript not found");
        return res.json();
      })
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load transcript");
        setLoading(false);
      });
  }, [transcriptId]);

  const download = (format: string) => {
    window.open(`/api/transcript/${transcriptId}/download?format=${format}`, "_blank");
  };

  if (loading) {
    return (
      <div className="page-main">
        <div className="shell" style={{ textAlign: "center", padding: "60px 20px" }}>
          <div style={{ color: "var(--muted)", fontSize: 14 }}>Loading transcript…</div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="page-main">
        <div className="shell" style={{ textAlign: "center", padding: "60px 20px" }}>
          <h2 style={{ marginBottom: 12 }}>Transcript not found</h2>
          <p style={{ color: "var(--muted)" }}>
            {error || "This transcript doesn't exist or has been deleted."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-main">
      <div className="shell" style={{ maxWidth: 800 }}>
        {/* Header */}
        <div
          style={{
            background: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: 8,
            padding: 24,
            marginBottom: 20,
          }}
        >
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
            <div>
              <div className="eyebrow" style={{ marginBottom: 8 }}>
                Ticket Transcript
              </div>
              <h1 style={{ fontSize: 24, letterSpacing: "-0.04em", margin: 0 }}>
                #{data.channel_name}
              </h1>
              <div style={{ color: "var(--muted)", fontSize: 13, marginTop: 6 }}>
                {data.category} · {data.message_count} messages · {data.created_at}
              </div>
            </div>

            {/* Download buttons */}
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {FORMATS.map((fmt) => (
                <button
                  key={fmt.key}
                  className="button button-small button-muted"
                  onClick={() => download(fmt.key)}
                  style={{ minWidth: 70 }}
                >
                  <span>{fmt.icon}</span>
                  <span>{fmt.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Messages */}
        <div
          style={{
            background: "#1e1f22",
            border: "1px solid #3f4147",
            borderRadius: 8,
            overflow: "hidden",
          }}
        >
          {data.messages.map((msg, i) => (
            <TranscriptMessageView key={i} msg={msg} mentionNames={data.mention_names} />
          ))}
          {data.messages.length === 0 && (
            <div style={{ padding: 40, textAlign: "center", color: "#949ba4" }}>
              No messages in this transcript.
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            marginTop: 16,
            padding: "12px 0",
            textAlign: "center",
            color: "var(--dim)",
            fontSize: 12,
          }}
        >
          Transcript ID: <code style={{ fontFamily: "monospace" }}>{transcriptId}</code>
        </div>
      </div>
    </div>
  );
}
