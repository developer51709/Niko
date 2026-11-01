import { useEffect, useMemo, useRef, useState } from "react";
import { ApiError, getAuth, getGuilds, getStaffEmail, getStaffEmailMessage, getStaffMe, getStats, sendStaffEmail } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { EmailMessageBody } from "../components/EmailMessageBody";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { RichTextEditor } from "../components/RichTextEditor";
import { dashboardPath, dashboardServersPath, dashboardUserPath, navigate, staffEmailReportsPath } from "../router";
import { notifyError, notifyLoading, notifySuccess } from "../utils/toast";
import type { AuthStatus, BotStats, Guild, StaffEmailAttachment, StaffEmailInbox, StaffEmailMessage } from "../types";

/** Mirrors the server's limits so the composer refuses what the API would. */
const MAX_ATTACHMENTS = 5;
const MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024;

type Compose = {
  mailbox: string;
  to: string;
  subject: string;
  html: string;
  text: string;
  thread_id?: string;
  attachments: File[];
};

/** One conversation: every message that answered the same mail, oldest first. */
type Conversation = {
  key: string;
  messages: StaffEmailMessage[];
  latest: StaffEmailMessage;
  unread: number;
};

/** A mail list reads best with a clock for today and a date for anything older. */
function formatWhen(epoch: number) {
  const when = new Date(epoch * 1000);
  if (!Number.isFinite(when.getTime())) return "";
  const now = new Date();
  if (when.toDateString() === now.toDateString()) {
    return when.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  return when.toLocaleDateString([], { month: "short", day: "numeric" });
}

function counterpart(message: StaffEmailMessage) {
  return message.direction === "inbound" ? message.from_address : message.to_address;
}

function formatBytes(size: number) {
  if (!size) return "";
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function AttachmentList({ files }: { files?: StaffEmailAttachment[] }) {
  if (!files || files.length === 0) return null;
  return <ul className="staff-email-attachment-list">
    {files.map((file) => <li key={`${file.name}-${file.size}`}>
      <Icon name="file" />
      <span>{file.name}</span>
      {file.size ? <small>{formatBytes(file.size)}</small> : null}
    </li>)}
  </ul>;
}

function threadKey(message: StaffEmailMessage) {
  return message.thread_id || message.message_id;
}

/** What the provider last reported about a sent mail, in one word. */
function statusLabel(message: StaffEmailMessage) {
  const opens = message.opened_count || 0;
  switch (message.status) {
    case "opened": return opens > 1 ? `Opened ${opens}×` : "Opened";
    case "delivered": return "Delivered";
    case "accepted": return "Accepted";
    case "retrying": return "Retrying";
    case "failed": return "Not delivered";
    case "complained": return "Marked spam";
    case "unsubscribed": return "Unsubscribed";
    default: return "Sent";
  }
}

/** The provider's words for why a mail bounced, if it did. */
function failureReason(message: StaffEmailMessage) {
  const failure = message.events?.find((entry) => entry.reason && /fail|reject|drop|bounce/.test(entry.event));
  return failure?.reason || "";
}

/** What the provider's machine reasons mean, when it sent no sentence of its own. */
const FAILURE_HINTS: Record<string, string> = {
  espblock: "The receiving provider blocked it as spam. This is usually the sending domain's reputation, not this recipient's address.",
  spam: "The receiving provider filed it as spam.",
  "suppress-bounce": "An earlier mail to this address bounced, so the provider will not try it again.",
  "suppress-unsubscribe": "The recipient unsubscribed, so the provider will not send to them.",
  "suppress-complaint": "The recipient marked earlier mail as spam, so the provider suppresses mail to them.",
  mailboxfull: "The recipient's mailbox is full.",
  notfound: "The recipient's server says that address does not exist.",
  timeout: "The recipient's server did not answer in time; the provider will retry.",
};

/** The provider's words, in the order they happened. */
const EVENT_LABELS: Record<string, string> = {
  accepted: "Accepted",
  stored: "Stored",
  delivered: "Delivered",
  opened: "Opened",
  clicked: "Link clicked",
  failed: "Delivery failed",
  rejected: "Rejected",
  dropped: "Dropped",
  temporary_fail: "Retrying",
  permanent_fail: "Delivery failed",
  complained: "Marked as spam",
  unsubscribed: "Unsubscribed",
};

function formatStamp(epoch?: number | null) {
  if (!epoch) return "—";
  return new Date(epoch * 1000).toLocaleString();
}

function Receipt({ message, onOpen }: { message: StaffEmailMessage; onOpen: (message: StaffEmailMessage) => void }) {
  return (
    <p className="staff-email-receipt">
      <button type="button" className="staff-email-receipt-state" onClick={() => onOpen(message)} title="Show the full delivery status">
        {statusLabel(message)}
      </button>
      {message.delivered_at ? <span>Delivered {new Date(message.delivered_at * 1000).toLocaleString()}</span> : null}
      {message.opened_at ? <span>First opened {new Date(message.opened_at * 1000).toLocaleString()}</span> : null}
      {failureReason(message) ? <span>{failureReason(message)}</span> : null}
    </p>
  );
}

/** Everything the provider has said about one sent mail, in one panel. */
function StatusDialog({ message, domain, onClose }: { message: StaffEmailMessage; domain: string; onClose: () => void }) {
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  const events = message.events || [];
  return <div className="modal-backdrop" role="presentation" onClick={onClose}>
    <section
      className="modal-card staff-email-status-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="staff-email-status-title"
      onClick={(event) => event.stopPropagation()}
    >
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">Delivery status</span>
          <h3 id="staff-email-status-title">{message.subject || "(no subject)"}</h3>
          <p>{statusLabel(message)} · {message.to_address}</p>
        </div>
        <button type="button" className="button button-muted" onClick={onClose}>Close</button>
      </div>

      <dl className="staff-email-status-facts">
        <div><dt>Status</dt><dd>{statusLabel(message)}</dd></div>
        <div><dt>Sent</dt><dd>{formatStamp(message.created_at)}</dd></div>
        <div><dt>Delivered</dt><dd>{formatStamp(message.delivered_at)}</dd></div>
        <div><dt>First opened</dt><dd>{formatStamp(message.opened_at)}</dd></div>
        <div><dt>Opens</dt><dd>{message.opened_count || 0}</dd></div>
        <div><dt>Address</dt><dd>{message.mailbox}@{domain}</dd></div>
        <div className="is-wide"><dt>From</dt><dd>{message.from_address}</dd></div>
        <div className="is-wide"><dt>To</dt><dd>{message.to_address}</dd></div>
      </dl>

      <AttachmentList files={message.attachments} />

      <div className="staff-email-status-events">
        <h4>Provider events</h4>
        {events.length === 0
          ? <p>No delivery events are recorded for this message. The provider reports them a moment after a mail leaves, so a fresh send often has none.</p>
          : <ol>
            {events.map((entry) => <li key={`${entry.event}-${entry.occurred_at}-${entry.recipient}`}>
              <div className="staff-email-status-event-head">
                <strong>{EVENT_LABELS[entry.event] || entry.event}</strong>
                <time dateTime={new Date(entry.occurred_at * 1000).toISOString()}>{formatStamp(entry.occurred_at)}</time>
              </div>
              {entry.reason ? <p className="staff-email-status-code">
                {entry.reason}{entry.severity ? ` · ${entry.severity}` : ""}
              </p> : null}
              {entry.detail
                ? <p className="staff-email-status-detail">{entry.detail}</p>
                : FAILURE_HINTS[entry.reason] ? <p className="staff-email-status-detail">{FAILURE_HINTS[entry.reason]}</p> : null}
            </li>)}
          </ol>}
      </div>
    </section>
  </div>;
}

export function StaffEmailPage() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [accessLoading, setAccessLoading] = useState(true);
  const [accessError, setAccessError] = useState("");
  const [staffRole, setStaffRole] = useState<string | null>(null);
  const [stats, setStats] = useState<BotStats | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [inbox, setInbox] = useState<StaffEmailInbox | null>(null);
  const [inboxLoading, setInboxLoading] = useState(false);
  const [mailboxFilter, setMailboxFilter] = useState("");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<StaffEmailMessage | null>(null);
  const [openingId, setOpeningId] = useState<string | null>(null);
  const [compose, setCompose] = useState<Compose | null>(null);
  const [sending, setSending] = useState(false);
  const [statusFor, setStatusFor] = useState<StaffEmailMessage | null>(null);
  const attachInput = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const authStatus = await getAuth();
        if (!active) return;
        setAuth(authStatus);
        if (!authStatus.authenticated) {
          setAccessLoading(false);
          return;
        }
        const staffStatus = await getStaffMe();
        if (!active) return;
        setStaffRole(staffStatus.role);
        setAccessLoading(false);
        if (!staffStatus.role) return;
        const [botStats, availableGuilds] = await Promise.all([getStats(), getGuilds()]);
        if (!active) return;
        setStats(botStats);
        setGuilds(availableGuilds);
        try {
          const loaded = await getStaffEmail();
          if (active) setInbox(loaded);
        } catch (reason) {
          if (active) setAccessError(reason instanceof Error ? reason.message : "The mailbox could not be loaded.");
        }
      } catch (reason) {
        if (active) {
          setAccessError(reason instanceof Error ? reason.message : "Staff mailbox unavailable.");
          setAccessLoading(false);
        }
      }
    })();
    return () => { active = false; };
  }, []);

  async function loadInbox() {
    setInboxLoading(true);
    try {
      setInbox(await getStaffEmail());
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 403) {
        setAccessError(reason.message);
      } else {
        notifyError(reason instanceof Error ? reason.message : "The mailbox could not be loaded.", "staff-email");
      }
    } finally {
      setInboxLoading(false);
    }
  }

  async function openMessage(message: StaffEmailMessage) {
    if (openingId) return;
    setOpeningId(message.message_id);
    setCompose(null);
    try {
      const result = await getStaffEmailMessage(message.message_id);
      setSelected(result.message);
      if (!message.read && message.direction === "inbound") {
        setInbox((current) => current && {
          ...current,
          unread: Math.max(0, current.unread - 1),
          messages: current.messages.map((item) => item.message_id === message.message_id ? { ...item, read: true } : item),
        });
      }
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "That message could not be opened.", "staff-email");
    } finally {
      setOpeningId(null);
    }
  }

  function startCompose(message?: StaffEmailMessage) {
    const fallback = mailboxFilter || inbox?.mailboxes[0]?.local || "support";
    if (!message) {
      setSelected(null);
      setCompose({ mailbox: fallback, to: "", subject: "", html: "", text: "", attachments: [] });
      return;
    }
    const subject = message.subject || "";
    setCompose({
      mailbox: message.mailbox || fallback,
      to: counterpart(message),
      subject: /^re:/i.test(subject) ? subject : `Re: ${subject || "(no subject)"}`,
      html: "",
      text: "",
      attachments: [],
      thread_id: threadKey(message),
    });
  }

  /** The pill opens the full status; a message the page has not loaded in
   * detail yet (a reply inside a conversation) is fetched so its events show. */
  async function openStatus(message: StaffEmailMessage) {
    setStatusFor(message);
    if (message.events) return;
    try {
      const result = await getStaffEmailMessage(message.message_id);
      setStatusFor((current) => current && current.message_id === message.message_id ? result.message : current);
    } catch {
      // The panel still shows what the list knew; a failed refresh is silent.
    }
  }

  function addAttachments(files: FileList | null) {
    if (!compose || !files || files.length === 0) return;
    const next = [...compose.attachments];
    for (const file of Array.from(files)) {
      if (next.length >= MAX_ATTACHMENTS) {
        notifyError(`Attach at most ${MAX_ATTACHMENTS} files.`, "staff-email");
        break;
      }
      if (next.some((item) => item.name === file.name && item.size === file.size)) continue;
      next.push(file);
    }
    if (next.reduce((total, file) => total + file.size, 0) > MAX_ATTACHMENT_BYTES) {
      notifyError("Those attachments are too large together. Keep them under 10 MB.", "staff-email");
      return;
    }
    setCompose({ ...compose, attachments: next });
  }

  async function submitCompose() {
    if (sending || !compose) return;
    if (!compose.to.trim() || !compose.subject.trim() || !compose.text.trim()) {
      notifyError("Add a recipient, a subject, and a message.", "staff-email");
      return;
    }
    setSending(true);
    notifyLoading("Sending from Niko…", "staff-email");
    try {
      const result = await sendStaffEmail({
        mailbox: compose.mailbox,
        to: compose.to,
        subject: compose.subject,
        body: compose.text,
        html: compose.html,
        thread_id: compose.thread_id,
        attachments: compose.attachments,
      }, auth?.csrf_token);
      notifySuccess(`Sent to ${result.message.to_address}.`, "staff-email");
      setCompose(null);
      setSelected(result.message);
      await loadInbox();
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The message could not be sent.", "staff-email");
    } finally {
      setSending(false);
    }
  }

  const visible = useMemo(() => {
    const items = inbox?.messages || [];
    const search = query.trim().toLocaleLowerCase();
    return items.filter((message) => {
      if (mailboxFilter && message.mailbox !== mailboxFilter) return false;
      if (!search) return true;
      return `${message.subject} ${message.from_address} ${message.from_name || ""} ${message.to_address} ${message.preview || ""}`
        .toLocaleLowerCase()
        .includes(search);
    });
  }, [inbox, mailboxFilter, query]);

  // Replies are filed under the mail they answer, so the list shows one row per
  // conversation rather than one row per message.
  const conversations = useMemo<Conversation[]>(() => {
    const groups = new Map<string, StaffEmailMessage[]>();
    for (const message of visible) {
      const key = threadKey(message);
      const group = groups.get(key);
      if (group) group.push(message);
      else groups.set(key, [message]);
    }
    return Array.from(groups.entries())
      .map(([key, messages]) => {
        const ordered = [...messages].sort((a, b) => a.created_at - b.created_at);
        return {
          key,
          messages: ordered,
          latest: ordered[ordered.length - 1],
          unread: ordered.filter((message) => message.direction === "inbound" && !message.read).length,
        };
      })
      .sort((a, b) => b.latest.created_at - a.latest.created_at);
  }, [visible]);

  if (accessLoading) return <div className="dashboard-state"><div className="loading-ring" /><p>Checking your staff access…</p></div>;
  if (!auth?.authenticated) {
    return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><div className="eyebrow">Staff mailbox</div><h1>Sign in to continue.</h1><p>The staff mailbox opens with your Discord account.</p><a className="button button-primary full-width" href="/auth/login?next=/dashboard/staff/email">Continue with Discord</a><button className="back-link" onClick={() => navigate("/dashboard")}>Return to dashboard</button></div></main></>;
  }
  if (!staffRole) {
    return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><div className="eyebrow">Staff mailbox</div><h1>Staff only.</h1><p>Niko's own-domain mail is limited to the staff team. Your account does not hold a staff role.</p><button className="back-link" onClick={() => navigate("/dashboard/staff")}>Back to the staff workspace</button></div></main></>;
  }
  if (accessError && !inbox) {
    return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><div className="eyebrow">Staff mailbox</div><h1>No mailbox yet.</h1><p>{accessError}</p><button className="back-link" onClick={() => navigate("/dashboard/staff")}>Back to the staff workspace</button></div></main></>;
  }

  const mailboxes = inbox?.mailboxes || [];
  const activeMailboxLabel = inbox?.mailboxes.find((mailbox) => mailbox.local === mailboxFilter)?.label || "All addresses";
  const selectedKey = selected ? threadKey(selected) : "";
  const composeMailbox = mailboxes.find((mailbox) => mailbox.local === compose?.mailbox);
  const personalAddress = mailboxes.find((mailbox) => mailbox.kind === "personal")?.address;

  const content = <div className="staff-page staff-email-page">
    <header className="staff-heading">
      <div>
        <div className="eyebrow">Correspondence</div>
        <h1>Staff mailbox.</h1>
        <p>Niko's own-domain inbox. Partners, applicants, and members write to the team addresses and to each staff member's private address, and replies stay in one conversation per exchange. Nothing here is linked from the public site.</p>
      </div>
      <div className="staff-email-head-side">
        {staffRole === "owner" && <button type="button" className="button button-muted button-small" onClick={() => navigate(staffEmailReportsPath())}>
          <Icon name="alert" /> Report queue
        </button>}
        <div className="staff-role-card"><span className="staff-role-mark staff-email-mark"><Icon name="mail" /></span><span><small>{mailboxes.length > 1 ? "All addresses" : "Your address"}</small><strong>{activeMailboxLabel}</strong></span></div>
      </div>
    </header>

    {!inbox && inboxLoading && <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading the mailbox…</p></div>}

    {inbox && !inbox.configured && <section className="staff-email-setup" role="status">
      <div className="staff-email-setup-copy">
        <span className="panel-kicker">Not connected yet</span>
        <h2>The addresses exist, the mail service is not wired up.</h2>
        <p>Add these keys in the environment settings, add <strong>{inbox.domain}</strong> at Mailgun together with the DNS records it gives you, then add a receive route that forwards to <code>/api/staff/email/inbound</code>. Until then the page shows what it knows and refuses to pretend a message was sent.</p>
      </div>
      <ul className="staff-email-setup-keys">
        {inbox.missing.map((name) => <li key={name}><code>{name}</code></li>)}
      </ul>
    </section>}

    {inbox && <div className="staff-email-layout">
      <aside className="staff-email-inbox" aria-label="Inbox">
        <div className="staff-email-inbox-head">
          <div className="staff-email-mailboxes" role="group" aria-label="Addresses">
            <button type="button" className={mailboxFilter ? "" : "active"} onClick={() => setMailboxFilter("")}>All <span>{conversations.length}</span></button>
            {mailboxes.map((mailbox) => <button type="button" key={mailbox.local} className={mailboxFilter === mailbox.local ? "active" : ""} onClick={() => setMailboxFilter(mailbox.local)}>{mailbox.label} <span>{conversations.filter((conversation) => conversation.latest.mailbox === mailbox.local).length}</span></button>)}
          </div>
          <button type="button" className="button button-primary button-small" onClick={() => startCompose()}><Icon name="plus" /> Write</button>
        </div>
        <div className="staff-email-toolbar">
          <label className="staff-guild-search"><Icon name="search" /><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search the mailbox" aria-label="Search the mailbox" /></label>
          <button type="button" className="staff-email-refresh" onClick={() => void loadInbox()} disabled={inboxLoading} aria-label="Refresh mailbox"><Icon name="spark" /></button>
        </div>
        {inboxLoading && inbox.messages.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading messages…</p></div>
          : conversations.length === 0 ? <div className="staff-email-empty-list">{inbox.messages.length ? "No messages match that search." : "No mail yet. Anything sent to your address lands here."}</div>
          : <div className="staff-email-list">
            {conversations.map((conversation) => {
              const message = conversation.latest;
              return <button
                type="button"
                key={conversation.key}
                className={`staff-email-item${selectedKey === conversation.key ? " is-open" : ""}${conversation.unread ? " is-unread" : ""}`}
                onClick={() => void openMessage(message)}
              >
                <span className="staff-email-item-top">
                  <strong>{message.direction === "outbound" ? `To ${message.to_address}` : message.from_name || message.from_address}</strong>
                  <span className="staff-email-item-when">
                    {conversation.messages.length > 1 && <b className="staff-email-thread-count" title={`${conversation.messages.length} messages in this conversation`}>{conversation.messages.length}</b>}
                    <time dateTime={new Date(message.created_at * 1000).toISOString()}>{formatWhen(message.created_at)}</time>
                  </span>
                </span>
                <span className="staff-email-item-subject">{message.subject}{message.direction === "outbound" && <em>{statusLabel(message)}</em>}</span>
                <span className="staff-email-item-preview">{message.preview || "No message text."}</span>
                <span className="staff-email-item-address">{conversation.messages.length > 1 ? `${message.mailbox}@${inbox.domain} · ${conversation.messages.length} messages` : `${message.mailbox}@${inbox.domain}`}</span>
              </button>;
            })}
          </div>}
      </aside>

      <section className="staff-email-reader" aria-label="Message">
        {compose ? <div className="staff-email-compose">
          <div className="staff-email-reader-head">
            <div><span className="panel-kicker">{compose.thread_id ? "Reply in this conversation" : "New message"}</span><h2>Write from Niko</h2></div>
            <button type="button" className="button button-muted button-small" onClick={() => setCompose(null)}>Cancel</button>
          </div>
          <div className="staff-fields">
            <label className="form-field"><span className="form-label">From</span>
              <select value={compose.mailbox} onChange={(event) => setCompose({ ...compose, mailbox: event.target.value })}>
                {mailboxes.map((mailbox) => <option value={mailbox.local} key={mailbox.local}>{mailbox.address}</option>)}
              </select>
            </label>
            {composeMailbox?.kind === "shared" && <p className="staff-email-signature-note">
              <Icon name="mail" />
              <span>Your signature is added automatically: your display name, your Discord handle, and {personalAddress || "your Niko address"}.</span>
            </p>}
            <label className="form-field"><span className="form-label">To</span>
              <input type="email" value={compose.to} onChange={(event) => setCompose({ ...compose, to: event.target.value })} placeholder="name@example.com" autoComplete="off" />
            </label>
            <label className="form-field"><span className="form-label">Subject</span>
              <input value={compose.subject} onChange={(event) => setCompose({ ...compose, subject: event.target.value })} maxLength={300} placeholder="What is this about?" />
            </label>
            <div className="form-field">
              <span className="form-label">Message</span>
              <RichTextEditor
                value={compose.html}
                onChange={(html, text) => setCompose((current) => current ? { ...current, html, text } : current)}
                placeholder="Write the message…"
                disabled={sending}
              />
            </div>
            <div className="staff-email-attach-row">
              <input
                ref={attachInput}
                type="file"
                multiple
                className="staff-email-file-input"
                onChange={(event) => { addAttachments(event.target.files); event.target.value = ""; }}
              />
              <button type="button" className="button button-muted button-small" onClick={() => attachInput.current?.click()} disabled={sending}>
                <Icon name="attach" /> Attach files
              </button>
              <span className="staff-email-attach-note">Images or files · up to {MAX_ATTACHMENTS} files · 10 MB total</span>
            </div>
            {compose.attachments.length > 0 && <ul className="staff-email-attach-list">
              {compose.attachments.map((file, index) => <li key={`${file.name}-${index}`}>
                <Icon name="file" />
                <span>{file.name}</span>
                <small>{formatBytes(file.size)}</small>
                <button
                  type="button"
                  aria-label={`Remove ${file.name}`}
                  onClick={() => setCompose((current) => current ? { ...current, attachments: current.attachments.filter((_, item) => item !== index) } : current)}
                ><Icon name="close" /></button>
              </li>)}
            </ul>}
          </div>
          <div className="staff-panel-footer"><span>Sent from {compose.mailbox}@{inbox.domain}{compose.thread_id ? " · this reply joins the conversation" : ""} · a copy is kept in this mailbox.</span><button type="button" className="button button-primary" onClick={() => void submitCompose()} disabled={sending}>{sending ? "Sending…" : "Send message"}</button></div>
        </div>
          : selected ? <article className="staff-email-message">
            <div className="staff-email-reader-head">
              <div>
                <span className="panel-kicker">{selected.direction === "outbound" ? "Sent" : `Received on ${selected.to_address}`}</span>
                <h2>{selected.subject || "(no subject)"}</h2>
                <p className="staff-email-meta">
                  <strong>{selected.from_name ? `${selected.from_name} · ` : ""}{selected.from_address}</strong>
                  <span>{new Date(selected.created_at * 1000).toLocaleString()}</span>
                </p>
                {selected.direction === "outbound" && <Receipt message={selected} onOpen={(message) => void openStatus(message)} />}
                <AttachmentList files={selected.attachments} />
              </div>
              <button type="button" className="button button-primary button-small" onClick={() => startCompose(selected)}><Icon name="arrow" /> Reply</button>
            </div>
            {selected.thread && selected.thread.length > 1 ? <div className="staff-email-thread">
              <p className="staff-email-thread-head"><span>{selected.thread.length} messages in this conversation</span><small>Oldest first</small></p>
              {selected.thread.map((entry) => <article key={entry.message_id} className={`staff-email-turn is-${entry.direction}${entry.message_id === selected.message_id ? " is-current" : ""}`}>
                <header>
                  <strong>{entry.direction === "outbound" ? `Niko · ${entry.from_address}` : entry.from_name || entry.from_address}</strong>
                  <time dateTime={new Date(entry.created_at * 1000).toISOString()}>{new Date(entry.created_at * 1000).toLocaleString()}</time>
                </header>
                {entry.direction === "outbound" && <Receipt message={entry} onOpen={(message) => void openStatus(message)} />}
                <AttachmentList files={entry.attachments} />
                <EmailMessageBody message={entry} />
              </article>)}
            </div>
              : <EmailMessageBody message={selected} />}
          </article>
          : <div className="staff-email-reader-empty">
            <span className="staff-email-reader-icon"><Icon name="mail" /></span>
            <h2>{inbox.messages.length ? "Pick a conversation." : "The inbox is empty."}</h2>
            <p>{inbox.messages.length ? "Conversations are on the left; opening one shows every message in it and a reply button." : `Mail sent to ${mailboxes.map((mailbox) => mailbox.address).join(" or ")} will show up here as soon as the provider forwards it.`}</p>
            <button type="button" className="button button-muted" onClick={() => startCompose()}><Icon name="plus" /> Write a message</button>
          </div>}
      </section>
    </div>}
    {statusFor && inbox && <StatusDialog message={statusFor} domain={inbox.domain} onClose={() => setStatusFor(null)} />}
  </div>;

  return <DashboardShell
    user={auth.user!}
    guilds={guilds}
    selectedGuild={null}
    view="overview"
    section="overview"
    userTab="overview"
    stats={stats}
    staffRole={staffRole}
    onHome={() => navigate(dashboardPath())}
    onServers={() => navigate(dashboardServersPath())}
    onGuildChange={() => undefined}
    onSectionChange={() => undefined}
    onUserTabChange={(tab) => navigate(dashboardUserPath(tab))}
    onRefresh={() => void loadInbox()}
    refreshing={inboxLoading}
  >{content}</DashboardShell>;
}
