import { useState, useEffect } from "react";

type TranscriptMessage = {
  timestamp: string;
  author: string;
  author_id: string | number;
  content: string;
  attachments?: string[];
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
};

const FORMATS = [
  { key: "txt", label: "TXT", icon: "📄" },
  { key: "html", label: "HTML", icon: "🌐" },
  { key: "csv", label: "CSV", icon: "📊" },
  { key: "json", label: "JSON", icon: "{ }" },
] as const;

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
            <div
              key={i}
              style={{
                padding: "10px 16px",
                borderBottom: "1px solid #2b2d31",
                fontSize: 14,
                lineHeight: 1.6,
              }}
            >
              <span style={{ color: "#949ba4", fontSize: 11, fontFamily: "monospace" }}>
                {msg.timestamp}
              </span>{" "}
              <span style={{ color: "#f2f3f5", fontWeight: 600 }}>{msg.author}</span>{" "}
              <span style={{ color: "#949ba4", fontSize: 11 }}>({msg.author_id})</span>:{" "}
              <span style={{ color: "#dbdee1" }}>{msg.content}</span>
              {msg.attachments && msg.attachments.length > 0 && (
                <div style={{ marginTop: 4 }}>
                  {msg.attachments.map((url, j) => (
                    <a
                      key={j}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "#00a8fc", fontSize: 12, textDecoration: "none" }}
                    >
                      📎 Attachment
                    </a>
                  ))}
                </div>
              )}
            </div>
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
