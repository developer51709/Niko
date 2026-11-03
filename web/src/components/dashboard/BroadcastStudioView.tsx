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
import { useStrings } from "../../i18n";

const MAX_MEDIA = 10;
const MAX_MEDIA_BYTES = 8 * 1024 * 1024;
const IMAGE_TYPES = new Set(["image/png", "image/jpeg", "image/gif", "image/webp"]);
const ACCENT_PRESETS = ["C8A882", "5865F2", "57F287", "FEE75C", "EB459E", "ED4245", "9B59B6", "3498DB"];

// Catalogue keys rather than text: each badge is translated where it renders.
const STATUS_LABELS: Record<StaffBroadcastStatus, string> = {
  draft: "broadcast.statusDraft",
  sending: "broadcast.statusSending",
  sent: "broadcast.statusSent",
  syncing: "broadcast.statusSyncing",
  failed: "broadcast.statusFailed",
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
  const { t } = useStrings("dashboard");
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
        if (!cancelled) setError(reason instanceof Error ? reason.message : t("broadcast.loadFailed"));
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
                ? t(broadcast.edited_count === 1 ? "broadcast.updatedOne" : "broadcast.updatedMany", { count: broadcast.edited_count })
                : t("broadcast.deliveredTo", { sent: broadcast.sent_count, total: broadcast.target_count }),
              "staff-broadcast",
            );
          } else {
            notifyError(broadcast.last_error || t("broadcast.finishedWithError"), "staff-broadcast");
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
    notifyLoading(t("broadcast.saving"), "staff-broadcast");
    try {
      const result = await updateStaffBroadcast(selected.id, { title, body, accent, footer }, csrfToken);
      const stored = applySaved(result.broadcast, result.syncing);
      loadFields(stored);
      if (result.syncing) {
        notifySuccess(t("broadcast.savedSyncing"), "staff-broadcast");
      } else {
        notifySuccess(t("broadcast.savedDraft"), "staff-broadcast");
      }
      return stored;
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("broadcast.saveFailed"), "staff-broadcast");
      return null;
    } finally {
      setBusy("");
    }
  };

  const send = async () => {
    if (!selected || busy) return;
    if (!title.trim() || !body.trim()) {
      notifyError(t("broadcast.needTitleAndBody"), "staff-broadcast");
      return;
    }
    if (!window.confirm(t("broadcast.sendConfirm"))) return;
    setBusy("sending");
    try {
      let current = selected;
      if (dirty) {
        const saved = await updateStaffBroadcast(current.id, { title, body, accent, footer }, csrfToken);
        current = saved.broadcast;
        applyBroadcast(current);
      }
      notifyLoading(t("broadcast.preparingQueue"), "staff-broadcast");
      const { broadcast } = await sendStaffBroadcast(current.id, csrfToken);
      applyBroadcast(broadcast);
      loadFields(broadcast);
      notifySuccess(t("broadcast.queued"), "staff-broadcast");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("broadcast.sendFailed"), "staff-broadcast");
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
      notifySuccess(t("broadcast.draftReady"), "staff-broadcast");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("broadcast.draftFailed"), "staff-broadcast");
    } finally {
      setBusy("");
    }
  };

  const removeBroadcast = async () => {
    if (!selected || busy) return;
    if (!window.confirm(t("broadcast.deleteConfirm"))) return;
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
      notifySuccess(t("broadcast.draftDeleted"), "staff-broadcast");
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("broadcast.deleteFailed"), "staff-broadcast");
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
      notifyError(t("broadcast.tooManyImages", { max: MAX_MEDIA }), "staff-broadcast");
      return;
    }
    setBusy("uploading");
    let uploaded = 0;
    let attachedBytes = selected.media.reduce((total, item) => total + item.size, 0);
    try {
      for (const file of files.slice(0, room)) {
        if (!IMAGE_TYPES.has(file.type)) {
          notifyError(t("broadcast.badImageType", { name: file.name }), "staff-broadcast");
          continue;
        }
        if (file.size > MAX_MEDIA_BYTES) {
          notifyError(t("broadcast.imageTooLarge", { name: file.name }), "staff-broadcast");
          continue;
        }
        if (attachedBytes + file.size > 20 * 1024 * 1024) {
          notifyError(t("broadcast.imagesTotalTooLarge"), "staff-broadcast");
          continue;
        }
        try {
          const result = await uploadStaffBroadcastMedia(selected.id, file, csrfToken);
          applySaved(result.broadcast, result.syncing);
          attachedBytes += file.size;
          uploaded += 1;
        } catch (reason) {
          notifyError(reason instanceof Error ? reason.message : t("broadcast.uploadFailed", { name: file.name }), "staff-broadcast");
        }
      }
      if (uploaded > 0) {
        notifySuccess(
          t(uploaded === 1 ? "broadcast.attachedOne" : "broadcast.attachedMany", { count: uploaded }) + " " + t(selected.status === "sent" ? "broadcast.copiesWillUpdate" : "broadcast.uploadedWithMessage"),
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
      notifyError(reason instanceof Error ? reason.message : t("broadcast.removeImageFailed"), "staff-broadcast");
    } finally {
      setBusy("");
    }
  };

  if (loading) {
    return <div className="broadcast-studio-state"><div className="loading-ring" /><p>{t("broadcast.opening")}</p></div>;
  }
  if (error) {
    return (
      <div className="broadcast-studio-state" role="alert">
        <Icon name="alert" />
        <p>{error}</p>
        <button type="button" className="button button-muted" onClick={() => window.location.reload()}>{t("broadcast.retry")}</button>
      </div>
    );
  }
  if (!selected) {
    return (
      <div className="broadcast-studio-state">
        <p>{t("broadcast.noneSelected")}</p>
        <button type="button" className="button button-primary" onClick={() => void newBroadcast()}>{t("broadcast.createBroadcast")}</button>
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
  const previewFooter = footer.trim() || selected.footer || t("broadcast.defaultFooter");

  return (
    <div className="broadcast-studio">
      <header className="broadcast-studio-heading">
        <div>
          <span className="panel-kicker">{t("broadcast.kicker")}</span>
          <h2>{t("broadcast.title")}</h2>
          <p>{t("broadcast.text")}</p>
        </div>
        <button type="button" className="button button-muted broadcast-new" onClick={() => void newBroadcast()} disabled={!!busy}>
          <Icon name="plus" /> {t("broadcast.newBroadcast")}
        </button>
      </header>

      {active && (
        <section className="broadcast-progress-panel" aria-live="polite">
          <div className="broadcast-progress-heading">
            <div>
              <span className="panel-kicker">{t(selected.status === "syncing" ? "broadcast.updatingCopies" : "broadcast.sendingBroadcast")}</span>
              <strong>
                {selected.status === "syncing"
                  ? t("broadcast.updatedOf", { edited: selected.edited_count, total: total || "…" })
                  : total
                    ? t("broadcast.processedOf", { done, total })
                    : t("broadcast.preparingQueue")}
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
            aria-label={t(selected.status === "syncing" ? "broadcast.updatingCopies" : "broadcast.sendingBroadcast")}
          >
            <span className="broadcast-progress-fill" style={total ? { width: `${percent}%` } : undefined} />
          </div>
          <div className="broadcast-progress-counts">
            <span><i className="is-sent" /> {t("broadcast.delivered")} <b>{selected.sent_count}</b></span>
            <span><i className="is-failed" /> {t("broadcast.failed")} <b>{selected.failed_count}</b></span>
            <span><i className="is-skipped" /> {t("broadcast.skipped")} <b>{selected.skipped_count}</b></span>
            <small>{t("broadcast.rateLimitNote")}</small>
          </div>
        </section>
      )}

      <div className="broadcast-studio-grid">
        <section className="broadcast-composer" aria-label={t("broadcast.editorAria")}>
          <label className="broadcast-field" htmlFor="broadcast-title">
            <span className="form-label">{t("broadcast.titleLabel")}</span>
            <input
              id="broadcast-title"
              value={title}
              maxLength={160}
              onChange={(event) => setTitle(event.target.value)}
              placeholder={t("broadcast.titlePlaceholder")}
              disabled={locked}
            />
          </label>

          <label className="broadcast-field" htmlFor="broadcast-body">
            <span className="form-label">{t("broadcast.messageLabel")}</span>
            <textarea
              id="broadcast-body"
              value={body}
              maxLength={3800}
              rows={9}
              onChange={(event) => setBody(event.target.value)}
              placeholder={t("broadcast.messagePlaceholder")}
              disabled={locked}
            />
            <small>{t("broadcast.messageCount", { count: body.length })}</small>
          </label>

          <div className="broadcast-field-row">
            <label className="broadcast-field" htmlFor="broadcast-footer">
              <span className="form-label">{t("broadcast.footerLabel")}</span>
              <input
                id="broadcast-footer"
                value={footer}
                maxLength={120}
                onChange={(event) => setFooter(event.target.value)}
                placeholder={t("broadcast.footerPlaceholder")}
                disabled={locked}
              />
            </label>
            <div className="broadcast-field broadcast-accent-field">
              <span className="form-label">{t("broadcast.accentLabel")}</span>
              <div className="broadcast-accent-controls">
                <div className="broadcast-swatches" role="group" aria-label={t("broadcast.accentPresets")}>
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
                  label={t("broadcast.accentPicker")}
                  value={`#${accent}`}
                  onChange={(hex) => setAccent(hex.replace(/^#/, "").toUpperCase())}
                />
              </div>
            </div>
          </div>

          <section className="broadcast-media" aria-label={t("broadcast.imagesAria")}>
            <div className="broadcast-media-heading">
              <div>
                <span className="form-label">{t("broadcast.imagesLabel")}</span>
                <small>{t("broadcast.imagesHint")}</small>
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
                      aria-label={t("broadcast.removeImageAria", { name: item.filename })}
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
              <span>{t(busy === "uploading" ? "broadcast.uploading" : "broadcast.addImages")}</span>
              <small>{t("broadcast.imageLimits")}</small>
            </button>
          </section>

          <footer className="broadcast-composer-actions">
            <div className="broadcast-composer-meta">
              <span className={`broadcast-status is-${selected.status}`}><i />{t(STATUS_LABELS[selected.status])}</span>
              <small>{dirty ? t("broadcast.unsaved") : t("broadcast.savedAt", { when: formatWhen(selected.updated_at) })}</small>
            </div>
            <div className="broadcast-composer-buttons">
              <button
                type="button"
                className="button button-muted"
                onClick={() => void save()}
                disabled={!!busy || !dirty || locked}
              >
                {t(busy === "saving" ? "notifier.saving" : delivered ? "broadcast.saveAndUpdate" : "broadcast.saveDraft")}
              </button>
              {!delivered && (
                <button
                  type="button"
                  className="button button-primary"
                  onClick={() => void send()}
                  disabled={!!busy || !title.trim() || !body.trim() || locked}
                >
                  {t(busy === "sending" ? "broadcast.sending" : "broadcast.sendBroadcast")}
                </button>
              )}
              {!delivered && (
                <button
                  type="button"
                  className="button button-danger broadcast-delete"
                  onClick={() => void removeBroadcast()}
                  disabled={!!busy}
                >
                  {t(busy === "deleting" ? "broadcast.deleting" : "broadcast.delete")}
                </button>
              )}
            </div>
          </footer>
        </section>

        <aside className="broadcast-preview-panel" aria-label={t("broadcast.previewAria")}>
          <div className="broadcast-preview-heading">
            <span className="panel-kicker">{t("broadcast.previewKicker")}</span>
            <span>{t("broadcast.previewSurface")}</span>
          </div>
          <div className="broadcast-preview-surface">
            <article className="broadcast-preview-card" style={{ borderLeftColor: `#${accent}` }}>
              <h3 className="broadcast-preview-title">{title.trim() || t("broadcast.previewTitle")}</h3>
              <span className="broadcast-preview-separator" />
              <DiscordMarkdown
                text={body.trim() || t("broadcast.previewBody")}
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
            {t("broadcast.previewNote")}
          </p>
        </aside>
      </div>

      <section className="broadcast-history" aria-label={t("broadcast.historyAria")}>
        <div className="broadcast-history-heading">
          <div>
            <span className="panel-kicker">{t("broadcast.historyKicker")}</span>
            <h3>{t("broadcast.historyTitle")}</h3>
          </div>
          <span>{t("broadcast.savedCount", { count: broadcasts.length })}</span>
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
                  <span className={`broadcast-status is-${item.status}`}><i />{t(STATUS_LABELS[item.status])}</span>
                  <span className="broadcast-history-copy">
                    <strong>{item.title.trim() || t("broadcast.untitled")}</strong>
                    <small>
                      {formatWhen(item.updated_at)}
                      {item.sent_count > 0 ? t("broadcast.historyDelivered", { count: item.sent_count }) : ""}
                      {item.failed_count > 0 ? t("broadcast.historyFailed", { count: item.failed_count }) : ""}
                      {item.media.length > 0 ? t(item.media.length === 1 ? "broadcast.historyImageOne" : "broadcast.historyImageMany", { count: item.media.length }) : ""}
                    </small>
                  </span>
                  <span className="broadcast-history-open-label">{t(item.id === selected.id ? "broadcast.editing" : "broadcast.open")}</span>
                </button>
                {running && (
                  <div className="broadcast-history-progress" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={itemPercent} aria-label={t("broadcast.progressAria", { status: t(STATUS_LABELS[item.status]) })}>
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
