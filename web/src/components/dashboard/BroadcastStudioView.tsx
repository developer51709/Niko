import { useEffect, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import {
  createStaffBroadcast,
  deleteStaffBroadcast,
  deleteStaffBroadcastMedia,
  getStaffBroadcast,
  getStaffBroadcasts,
  sendStaffBroadcast,
  updateStaffBroadcast,
  uploadStaffBroadcastMedia,
} from "../../api";
import { DiscordMarkdown } from "../DiscordMarkdown";
import { Icon } from "../Icon";
import { ColorPicker } from "./ColorPicker";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import type { StaffBroadcast, StaffBroadcastStatus } from "../../types";

const MAX_MEDIA = 10;
const MAX_MEDIA_BYTES = 8 * 1024 * 1024;
const IMAGE_TYPES = new Set(["image/png", "image/jpeg", "image/gif", "image/webp"]);
const ACCENT_PRESETS = ["C8A882", "5865F2", "57F287", "FEE75C", "EB459E", "ED4245", "9B59B6", "3498DB"];

const STATUS_LABELS: Record<StaffBroadcastStatus, string> = {
  draft: "Draft",
  sending: "Sending",
  sent: "Delivered",
  syncing: "Updating copies",
  failed: "Needs attention",
};

type BroadcastStudioProps = {
  csrfToken?: string;
};

function formatWhen(timestamp: number) {
  if (!timestamp) return "just now";
  return new Date(timestamp * 1000).toLocaleString(undefined, {
    month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
  });
}

function formatBytes(bytes: number) {
  if (!bytes) return "0 KB";
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Owner-only Components v2 broadcast composer.
 *
 * The tab is a single column on phones and a composer + live preview split on
 * wide screens. Sending and editing both run on the bot loop, so this view
 * polls the stored broadcast while the job runs and paints the progress bar
 * from the counters the job writes after every copy.
 */
export function BroadcastStudioView({ csrfToken }: BroadcastStudioProps) {
  const [broadcasts, setBroadcasts] = useState<StaffBroadcast[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [footer, setFooter] = useState("");
  const [accent, setAccent] = useState("C8A882");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<"" | "saving" | "sending" | "uploading" | "deleting" | "creating">("");
  const [error, setError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  const loadedFor = useRef<string | null>(null);
  const initialized = useRef(false);

  const selected = broadcasts.find((broadcast) => broadcast.id === selectedId) || null;
  const active = selected?.status === "sending" || selected?.status === "syncing";

  const loadFields = (broadcast: StaffBroadcast) => {
    setTitle(broadcast.title);
    setBody(broadcast.body);
    setFooter(broadcast.footer);
    setAccent(broadcast.accent);
  };

  const applyBroadcast = (broadcast: StaffBroadcast) => {
    setBroadcasts((current) => {
      const exists = current.some((item) => item.id === broadcast.id);
      const next = exists
        ? current.map((item) => (item.id === broadcast.id ? broadcast : item))
        : [broadcast, ...current];
      return next.sort((left, right) => right.updated_at - left.updated_at);
    });
  };

  // The save endpoint reads the row before the background update starts, so
  // the response still says "sent". Reflect the queued update immediately or
  // the poll would stop before it ever sees the progress.
  const applySaved = (broadcast: StaffBroadcast, syncing: boolean) => {
    const next: StaffBroadcast = syncing
      ? { ...broadcast, status: "syncing", edited_count: 0 }
      : broadcast;
    applyBroadcast(next);
    return next;
  };

  useEffect(() => {
    // React StrictMode re-runs effects in development; without this guard the
    // studio would create two empty drafts on its first visit.
    if (initialized.current) return;
    initialized.current = true;
    let cancelled = false;
    (async () => {
      try {
        const { broadcasts: stored } = await getStaffBroadcasts();
        if (cancelled) return;
        if (stored.length === 0) {
          const { broadcast } = await createStaffBroadcast(csrfToken);
          if (cancelled) return;
          setBroadcasts([broadcast]);
          setSelectedId(broadcast.id);
        } else {
          setBroadcasts(stored);
          setSelectedId(stored[0].id);
        }
        setError("");
      } catch (reason) {
        if (!cancelled) setError(reason instanceof Error ? reason.message : "The broadcast studio could not be loaded.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [csrfToken]);

  // Load the editor from the selected record. This only runs when the editor
  // switches broadcasts: a background poll must not overwrite what is typed.
  useEffect(() => {
    if (!selected || loadedFor.current === selected.id) return;
    loadedFor.current = selected.id;
    setTitle(selected.title);
    setBody(selected.body);
    setFooter(selected.footer);
    setAccent(selected.accent || "C8A882");
  }, [selected?.id]);

  // Live progress: the job updates counters after every copy. Polling pauses
  // automatically once the status settles back to sent or failed.
  useEffect(() => {
    if (!selectedId || !active) return;
    let cancelled = false;
    let timer = 0;
    const tick = async () => {
      try {
        const { broadcast } = await getStaffBroadcast(selectedId);
        if (cancelled) return;
        applyBroadcast(broadcast);
        if (broadcast.status !== "sending" && broadcast.status !== "syncing") {
          window.clearInterval(timer);
          if (broadcast.status === "sent") {
            notifySuccess(
              broadcast.status === "sent" && broadcast.edited_count > 0
                ? `Every delivered copy was updated (${broadcast.edited_count} message${broadcast.edited_count === 1 ? "" : "s"}).`
                : `Broadcast delivered to ${broadcast.sent_count} of ${broadcast.target_count} servers.`,
              "staff-broadcast",
            );
          } else {
            notifyError(broadcast.last_error || "The broadcast finished with an error.", "staff-broadcast");
          }
        }
      } catch {
        // Keep the last known counters on screen; the next tick retries.
      }
    };
    timer = window.setInterval(() => void tick(), 800);
    void tick();
    return () => { cancelled = true; window.clearInterval(timer); };
  }, [selectedId, active]);

  const dirty = !!selected && (
    title !== selected.title
    || body !== selected.body
    || footer !== selected.footer
    || accent !== selected.accent
  );

  const save = async (): Promise<StaffBroadcast | null> => {
    if (!selected || busy) return null;
    setBusy("saving");
    notifyLoading("Saving the broadcast…", "staff-broadcast");
    try {
      const result = await updateStaffBroadcast(selected.id, { title, body, accent, footer }, csrfToken);
      const stored = applySaved(result.broadcast, result.syncing);
      loadFields(stored);
      if (result.syncing) {
        notifySuccess("Saved. Every delivered copy is being updated now.", "staff-broadcast");
      } else {
        notifySuccess("Broadcast saved as a draft.", "staff-broadcast");
      }
      return stored;
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The broadcast could not be saved.", "staff-broadcast");
      return null;
    } finally {
      setBusy("");
    }
  };

  const send = async () => {
    if (!selected || busy) return;
    if (!title.trim() || !body.trim()) {
      notifyError("Add a title and a message before sending.", "staff-broadcast");
      return;
    }
    if (!window.confirm(`Send this broadcast to every configured Niko announcement channel?\n\nBlacklisted servers are skipped automatically.`)) return;
    setBusy("sending");
    try {
      let current = selected;
      if (dirty) {
        const saved = await updateStaffBroadcast(current.id, { title, body, accent, footer }, csrfToken);
        current = saved.broadcast;
        applyBroadcast(current);
      }
      notifyLoading("Preparing the delivery queue…", "staff-broadcast");
      const { broadcast } = await sendStaffBroadcast(current.id, csrfToken);
      applyBroadcast(broadcast);
      loadFields(broadcast);
      notifySuccess("Broadcast queued. Delivery progress is live below.", "staff-broadcast");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The broadcast could not be sent.", "staff-broadcast");
    } finally {
      setBusy("");
    }
  };

  const newBroadcast = async () => {
    if (busy) return;
    setBusy("creating");
    try {
      const { broadcast } = await createStaffBroadcast(csrfToken);
      applyBroadcast(broadcast);
      loadedFor.current = null;
      setSelectedId(broadcast.id);
      notifySuccess("New draft ready.", "staff-broadcast");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "A new draft could not be created.", "staff-broadcast");
    } finally {
      setBusy("");
    }
  };

  const removeBroadcast = async () => {
    if (!selected || busy) return;
    if (!window.confirm("Delete this draft? Its text and uploaded images are removed.")) return;
    setBusy("deleting");
    try {
      await deleteStaffBroadcast(selected.id, csrfToken);
      const remaining = broadcasts.filter((item) => item.id !== selected.id);
      setBroadcasts(remaining);
      loadedFor.current = null;
      setSelectedId(remaining[0]?.id ?? null);
      if (remaining.length === 0) {
        const { broadcast } = await createStaffBroadcast(csrfToken);
        setBroadcasts([broadcast]);
        setSelectedId(broadcast.id);
      }
      notifySuccess("Draft deleted.", "staff-broadcast");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The draft could not be deleted.", "staff-broadcast");
    } finally {
      setBusy("");
    }
  };

  const uploadFiles = async (event: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    event.target.value = "";
    if (!selected || files.length === 0 || busy) return;
    const room = MAX_MEDIA - selected.media.length;
    if (room <= 0) {
      notifyError(`A broadcast can carry up to ${MAX_MEDIA} images. Remove one first.`, "staff-broadcast");
      return;
    }
    setBusy("uploading");
    let uploaded = 0;
    let attachedBytes = selected.media.reduce((total, item) => total + item.size, 0);
    try {
      for (const file of files.slice(0, room)) {
        if (!IMAGE_TYPES.has(file.type)) {
          notifyError(`${file.name} is not a PNG, JPEG, GIF, or WebP image.`, "staff-broadcast");
          continue;
        }
        if (file.size > MAX_MEDIA_BYTES) {
          notifyError(`${file.name} is larger than 8 MB.`, "staff-broadcast");
          continue;
        }
        if (attachedBytes + file.size > 20 * 1024 * 1024) {
          notifyError("Images can total 20 MB per broadcast so Discord accepts every copy.", "staff-broadcast");
          continue;
        }
        try {
          const result = await uploadStaffBroadcastMedia(selected.id, file, csrfToken);
          applySaved(result.broadcast, result.syncing);
          attachedBytes += file.size;
          uploaded += 1;
        } catch (reason) {
          notifyError(reason instanceof Error ? reason.message : `${file.name} could not be uploaded.`, "staff-broadcast");
        }
      }
      if (uploaded > 0) {
        notifySuccess(
          `${uploaded} image${uploaded === 1 ? "" : "s"} attached. ${selected.status === "sent" ? "Delivered copies will be updated." : "They will be uploaded with the message."}`,
          "staff-broadcast",
        );
      }
    } finally {
      setBusy("");
    }
  };

  const removeMedia = async (mediaId: string) => {
    if (!selected || busy) return;
    setBusy("uploading");
    try {
      const result = await deleteStaffBroadcastMedia(selected.id, mediaId, csrfToken);
      applySaved(result.broadcast, result.syncing);
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The image could not be removed.", "staff-broadcast");
    } finally {
      setBusy("");
    }
  };

  if (loading) {
    return <div className="broadcast-studio-state"><div className="loading-ring" /><p>Opening the broadcast studio…</p></div>;
  }
  if (error) {
    return (
      <div className="broadcast-studio-state" role="alert">
        <Icon name="alert" />
        <p>{error}</p>
        <button type="button" className="button button-muted" onClick={() => window.location.reload()}>Try again</button>
      </div>
    );
  }
  if (!selected) {
    return (
      <div className="broadcast-studio-state">
        <p>No broadcast is selected.</p>
        <button type="button" className="button button-primary" onClick={() => void newBroadcast()}>Create a broadcast</button>
      </div>
    );
  }

  const locked = active || selected.status === "sending";
  const total = selected.target_count;
  const done = selected.status === "syncing"
    ? selected.edited_count
    : selected.sent_count + selected.failed_count + selected.skipped_count;
  const percent = total > 0 ? Math.min(100, Math.round((done / total) * 100)) : 0;
  const delivered = selected.sent_count > 0;
  const previewFooter = footer.trim() || selected.footer || "Official Niko staff announcement";

  return (
    <div className="broadcast-studio">
      <header className="broadcast-studio-heading">
        <div>
          <span className="panel-kicker">Owner-only · official announcements</span>
          <h2>Broadcast studio</h2>
          <p>Compose once, deliver to every configured server, and update every copy later without reposting.</p>
        </div>
        <button type="button" className="button button-muted broadcast-new" onClick={() => void newBroadcast()} disabled={!!busy}>
          <Icon name="plus" /> New broadcast
        </button>
      </header>

      {active && (
        <section className="broadcast-progress-panel" aria-live="polite">
          <div className="broadcast-progress-heading">
            <div>
              <span className="panel-kicker">{selected.status === "syncing" ? "Updating delivered copies" : "Sending broadcast"}</span>
              <strong>
                {selected.status === "syncing"
                  ? `${selected.edited_count} of ${total || "…"} messages updated`
                  : total
                    ? `${done} of ${total} servers processed`
                    : "Preparing the delivery queue…"}
              </strong>
            </div>
            <span className="broadcast-progress-percent">{total ? `${percent}%` : "…"}</span>
          </div>
          <div
            className={`broadcast-progress${total ? "" : " is-indeterminate"}`}
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={total ? percent : undefined}
            aria-label={selected.status === "syncing" ? "Updating delivered copies" : "Sending broadcast"}
          >
            <span className="broadcast-progress-fill" style={total ? { width: `${percent}%` } : undefined} />
          </div>
          <div className="broadcast-progress-counts">
            <span><i className="is-sent" /> Delivered <b>{selected.sent_count}</b></span>
            <span><i className="is-failed" /> Failed <b>{selected.failed_count}</b></span>
            <span><i className="is-skipped" /> Skipped <b>{selected.skipped_count}</b></span>
            <small>Requests are paced to stay inside Discord's rate limits.</small>
          </div>
        </section>
      )}

      <div className="broadcast-studio-grid">
        <section className="broadcast-composer" aria-label="Broadcast editor">
          <label className="broadcast-field" htmlFor="broadcast-title">
            <span className="form-label">Title</span>
            <input
              id="broadcast-title"
              value={title}
              maxLength={160}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="A short, clear headline"
              disabled={locked}
            />
          </label>

          <label className="broadcast-field" htmlFor="broadcast-body">
            <span className="form-label">Message</span>
            <textarea
              id="broadcast-body"
              value={body}
              maxLength={3800}
              rows={9}
              onChange={(event) => setBody(event.target.value)}
              placeholder="Write the announcement. Discord markdown is supported."
              disabled={locked}
            />
            <small>{body.length}/3800 characters · markdown supported</small>
          </label>

          <div className="broadcast-field-row">
            <label className="broadcast-field" htmlFor="broadcast-footer">
              <span className="form-label">Footer</span>
              <input
                id="broadcast-footer"
                value={footer}
                maxLength={120}
                onChange={(event) => setFooter(event.target.value)}
                placeholder="Official Niko staff announcement"
                disabled={locked}
              />
            </label>
            <div className="broadcast-field broadcast-accent-field">
              <span className="form-label">Accent</span>
              <div className="broadcast-accent-controls">
                <div className="broadcast-swatches" role="group" aria-label="Accent presets">
                  {ACCENT_PRESETS.map((preset) => (
                    <button
                      key={preset}
                      type="button"
                      className={`broadcast-swatch${accent.toUpperCase() === preset ? " is-active" : ""}`}
                      style={{ background: `#${preset}` }}
                      aria-label={`Use accent #${preset}`}
                      aria-pressed={accent.toUpperCase() === preset}
                      onClick={() => setAccent(preset)}
                      disabled={locked}
                    />
                  ))}
                </div>
                <ColorPicker
                  label="Broadcast accent color"
                  value={`#${accent}`}
                  onChange={(hex) => setAccent(hex.replace(/^#/, "").toUpperCase())}
                />
              </div>
            </div>
          </div>

          <section className="broadcast-media" aria-label="Broadcast images">
            <div className="broadcast-media-heading">
              <div>
                <span className="form-label">Images</span>
                <small>Uploaded with every message as attachments — copies never depend on an expiring link.</small>
              </div>
              <span className="broadcast-media-count">{selected.media.length}/{MAX_MEDIA}</span>
            </div>
            {selected.media.length > 0 && (
              <div className="broadcast-media-grid">
                {selected.media.map((item) => (
                  <figure className="broadcast-media-item" key={item.id}>
                    <img src={item.url} alt="" loading="lazy" />
                    <figcaption>
                      <strong title={item.filename}>{item.filename}</strong>
                      <small>{formatBytes(item.size)}</small>
                    </figcaption>
                    <button
                      type="button"
                      className="broadcast-media-remove"
                      onClick={() => void removeMedia(item.id)}
                      disabled={!!busy || locked}
                      aria-label={`Remove ${item.filename}`}
                    >
                      <Icon name="close" />
                    </button>
                  </figure>
                ))}
              </div>
            )}
            <input
              ref={fileInput}
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp"
              multiple
              className="broadcast-file-input"
              onChange={(event) => void uploadFiles(event)}
              disabled={!!busy || locked || selected.media.length >= MAX_MEDIA}
            />
            <button
              type="button"
              className="broadcast-upload"
              onClick={() => fileInput.current?.click()}
              disabled={!!busy || locked || selected.media.length >= MAX_MEDIA}
            >
              <Icon name="plus" />
              <span>{busy === "uploading" ? "Uploading…" : "Add images"}</span>
              <small>PNG, JPEG, GIF or WebP · 8 MB each · 20 MB total</small>
            </button>
          </section>

          <footer className="broadcast-composer-actions">
            <div className="broadcast-composer-meta">
              <span className={`broadcast-status is-${selected.status}`}><i />{STATUS_LABELS[selected.status]}</span>
              <small>{dirty ? "Unsaved changes" : `Saved ${formatWhen(selected.updated_at)}`}</small>
            </div>
            <div className="broadcast-composer-buttons">
              <button
                type="button"
                className="button button-muted"
                onClick={() => void save()}
                disabled={!!busy || !dirty || locked}
              >
                {busy === "saving" ? "Saving…" : delivered ? "Save & update copies" : "Save draft"}
              </button>
              {!delivered && (
                <button
                  type="button"
                  className="button button-primary"
                  onClick={() => void send()}
                  disabled={!!busy || !title.trim() || !body.trim() || locked}
                >
                  {busy === "sending" ? "Sending…" : "Send broadcast"}
                </button>
              )}
              {!delivered && (
                <button
                  type="button"
                  className="button button-danger broadcast-delete"
                  onClick={() => void removeBroadcast()}
                  disabled={!!busy}
                >
                  {busy === "deleting" ? "Deleting…" : "Delete"}
                </button>
              )}
            </div>
          </footer>
        </section>

        <aside className="broadcast-preview-panel" aria-label="Live Discord preview">
          <div className="broadcast-preview-heading">
            <span className="panel-kicker">Live preview</span>
            <span>Discord · Components v2</span>
          </div>
          <div className="broadcast-preview-surface">
            <article className="broadcast-preview-card" style={{ borderLeftColor: `#${accent}` }}>
              <h3 className="broadcast-preview-title">{title.trim() || "Your broadcast title"}</h3>
              <span className="broadcast-preview-separator" />
              <DiscordMarkdown
                text={body.trim() || "Your message appears here with Discord markdown, mentions, and emoji."}
                className="broadcast-preview-body"
              />
              {selected.media.length > 0 && (
                <div className={`broadcast-preview-gallery is-${Math.min(selected.media.length, 4)}`}>
                  {selected.media.slice(0, 4).map((item) => <img key={item.id} src={item.url} alt="" loading="lazy" />)}
                  {selected.media.length > 4 && <span className="broadcast-preview-more">+{selected.media.length - 4}</span>}
                </div>
              )}
              <span className="broadcast-preview-separator" />
              <p className="broadcast-preview-footer">-# {previewFooter}</p>
            </article>
          </div>
          <p className="broadcast-preview-note">
            Images are re-uploaded with each message, so the preview is the exact copy servers receive.
          </p>
        </aside>
      </div>

      <section className="broadcast-history" aria-label="Broadcast history">
        <div className="broadcast-history-heading">
          <div>
            <span className="panel-kicker">History</span>
            <h3>Recent broadcasts</h3>
          </div>
          <span>{broadcasts.length} saved</span>
        </div>
        <div className="broadcast-history-list">
          {broadcasts.map((item) => {
            const itemTotal = item.target_count;
            const itemDone = item.status === "syncing"
              ? item.edited_count
              : item.sent_count + item.failed_count + item.skipped_count;
            const itemPercent = itemTotal ? Math.min(100, Math.round((itemDone / itemTotal) * 100)) : 0;
            const running = item.status === "sending" || item.status === "syncing";
            return (
              <article className={`broadcast-history-item${item.id === selected.id ? " is-selected" : ""}`} key={item.id}>
                <button type="button" className="broadcast-history-open" onClick={() => setSelectedId(item.id)}>
                  <span className={`broadcast-status is-${item.status}`}><i />{STATUS_LABELS[item.status]}</span>
                  <span className="broadcast-history-copy">
                    <strong>{item.title.trim() || "Untitled broadcast"}</strong>
                    <small>
                      {formatWhen(item.updated_at)}
                      {item.sent_count > 0 ? ` · ${item.sent_count} delivered` : ""}
                      {item.failed_count > 0 ? ` · ${item.failed_count} failed` : ""}
                      {item.media.length > 0 ? ` · ${item.media.length} image${item.media.length === 1 ? "" : "s"}` : ""}
                    </small>
                  </span>
                  <span className="broadcast-history-open-label">{item.id === selected.id ? "Editing" : "Open"}</span>
                </button>
                {running && (
                  <div className="broadcast-history-progress" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={itemPercent} aria-label={`${STATUS_LABELS[item.status]} progress`}>
                    <span style={{ width: `${itemPercent}%` }} />
                  </div>
                )}
                {item.status === "failed" && item.last_error && <p className="broadcast-history-error">{item.last_error}</p>}
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}
