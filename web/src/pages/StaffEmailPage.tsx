import { useEffect, useMemo, useRef, useState } from "react";
import { ApiError, getAuth, getDeveloperMe, getGuilds, getStaffEmail, getStaffEmailMessage, getStaffMe, getStats, sendStaffEmail } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { EmailMessageBody } from "../components/EmailMessageBody";
import { Icon } from "../components/Icon";
import { LoadingCard } from "../components/LoadingCard";
import { Select } from "../components/dashboard/Select";
import { AuthScreen, DiscordSignIn } from "../components/AuthScreen";
import { RichTextEditor } from "../components/RichTextEditor";
import { dashboardPath, dashboardServersPath, dashboardUserPath, navigate, staffEmailReportsPath } from "../router";
import { notifyError, notifyLoading, notifySuccess } from "../utils/toast";
import { registerContextMenuExtras } from "../utils/contextMenu";
import { useStrings } from "../i18n";
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
function statusLabel(message: StaffEmailMessage, t: (key: string, values?: Record<string, string | number>) => string) {
  const opens = message.opened_count || 0;
  switch (message.status) {
    case "opened": return opens > 1 ? t("status.openedCount", { count: opens }) : t("status.opened");
    case "delivered": return t("status.delivered");
    case "accepted": return t("status.accepted");
    case "retrying": return t("status.retrying");
    case "failed": return t("status.notDelivered");
    case "complained": return t("status.markedSpam");
    case "unsubscribed": return t("status.unsubscribed");
    default: return t("status.sent");
  }
}

/** The provider's words for why a mail bounced, if it did. */
function failureReason(message: StaffEmailMessage) {
  const failure = message.events?.find((entry) => entry.reason && /fail|reject|drop|bounce/.test(entry.event));
  return failure?.reason || "";
}

/** What the provider's machine reasons mean, when it sent no sentence of its own. */
const FAILURE_HINT_KEYS: Record<string, string> = {
  espblock: "hint.espblock",
  spam: "hint.spam",
  "suppress-bounce": "hint.suppressBounce",
  "suppress-unsubscribe": "hint.suppressUnsubscribe",
  "suppress-complaint": "hint.suppressComplaint",
  mailboxfull: "hint.mailboxFull",
  notfound: "hint.notFound",
  timeout: "hint.timeout",
};

/** The provider's words, in the order they happened. */
const EVENT_KEYS: Record<string, string> = {
  accepted: "event.accepted",
  stored: "event.stored",
  delivered: "event.delivered",
  opened: "event.opened",
  clicked: "event.clicked",
  failed: "event.deliveryFailed",
  rejected: "event.rejected",
  dropped: "event.dropped",
  temporary_fail: "event.retrying",
  permanent_fail: "event.deliveryFailed",
  complained: "event.markedSpam",
  unsubscribed: "event.unsubscribed",
};

function formatStamp(epoch?: number | null) {
  if (!epoch) return "—";
  return new Date(epoch * 1000).toLocaleString();
}

function Receipt({ message, onOpen }: { message: StaffEmailMessage; onOpen: (message: StaffEmailMessage) => void }) {
  const { t } = useStrings("staff-email");
  return (
    <p className="staff-email-receipt">
      <button type="button" className="staff-email-receipt-state" onClick={() => onOpen(message)} title={t("receipt.showStatus")}>
        {statusLabel(message, t)}
      </button>
      {message.delivered_at ? <span>{t("receipt.delivered", { date: new Date(message.delivered_at * 1000).toLocaleString() })}</span> : null}
      {message.opened_at ? <span>{t("receipt.firstOpened", { date: new Date(message.opened_at * 1000).toLocaleString() })}</span> : null}
      {failureReason(message) ? <span>{failureReason(message)}</span> : null}
    </p>
  );
}

/** Everything the provider has said about one sent mail, in one panel. */
function StatusDialog({ message, domain, onClose }: { message: StaffEmailMessage; domain: string; onClose: () => void }) {
  const { t } = useStrings("staff-email");
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
          <span className="panel-kicker">{t("dialog.kicker")}</span>
          <h3 id="staff-email-status-title">{message.subject || t("dialog.noSubject")}</h3>
          <p>{statusLabel(message, t)} · {message.to_address}</p>
        </div>
        <button type="button" className="button button-muted" onClick={onClose}>{t("dialog.close")}</button>
      </div>

      <dl className="staff-email-status-facts">
        <div><dt>{t("dialog.status")}</dt><dd>{statusLabel(message, t)}</dd></div>
        <div><dt>{t("dialog.sent")}</dt><dd>{formatStamp(message.created_at)}</dd></div>
        <div><dt>{t("dialog.delivered")}</dt><dd>{formatStamp(message.delivered_at)}</dd></div>
        <div><dt>{t("dialog.firstOpened")}</dt><dd>{formatStamp(message.opened_at)}</dd></div>
        <div><dt>{t("dialog.opens")}</dt><dd>{message.opened_count || 0}</dd></div>
        <div><dt>{t("dialog.address")}</dt><dd>{message.mailbox}@{domain}</dd></div>
        <div className="is-wide"><dt>{t("dialog.from")}</dt><dd>{message.from_address}</dd></div>
        <div className="is-wide"><dt>{t("dialog.to")}</dt><dd>{message.to_address}</dd></div>
      </dl>

      <AttachmentList files={message.attachments} />

      <div className="staff-email-status-events">
        <h4>{t("dialog.events")}</h4>
        {events.length === 0
          ? <p>{t("dialog.noEvents")}</p>
          : <ol>
            {events.map((entry) => <li key={`${entry.event}-${entry.occurred_at}-${entry.recipient}`}>
              <div className="staff-email-status-event-head">
                <strong>{EVENT_KEYS[entry.event] ? t(EVENT_KEYS[entry.event]) : entry.event}</strong>
                <time dateTime={new Date(entry.occurred_at * 1000).toISOString()}>{formatStamp(entry.occurred_at)}</time>
              </div>
              {entry.reason ? <p className="staff-email-status-code">
                {entry.reason}{entry.severity ? ` · ${entry.severity}` : ""}
              </p> : null}
              {entry.detail
                ? <p className="staff-email-status-detail">{entry.detail}</p>
                : FAILURE_HINT_KEYS[entry.reason] ? <p className="staff-email-status-detail">{t(FAILURE_HINT_KEYS[entry.reason])}</p> : null}
            </li>)}
          </ol>}
      </div>
    </section>
  </div>;
}

export function StaffEmailPage() {
  const { t } = useStrings("staff-email");
  // The menu's own copy confirmations, so this page does not carry a second set.
  const { t: sharedT } = useStrings("shared");
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [accessLoading, setAccessLoading] = useState(true);
  const [accessError, setAccessError] = useState("");
  const [staffRole, setStaffRole] = useState<string | null>(null);
  // Keeps the developer portal entry in the sidebar while the mailbox is open.
  const [developerAccess, setDeveloperAccess] = useState(false);
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
        const [staffStatus, developerStatus] = await Promise.all([getStaffMe(), getDeveloperMe().catch(() => null)]);
        if (!active) return;
        setStaffRole(staffStatus.role);
        setDeveloperAccess(Boolean(developerStatus?.access.enabled));
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
          if (active) setAccessError(reason instanceof Error ? reason.message : t("error.mailboxLoad"));
        }
      } catch (reason) {
        if (active) {
          setAccessError(reason instanceof Error ? reason.message : t("error.mailboxUnavailable"));
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
        notifyError(reason instanceof Error ? reason.message : t("error.mailboxLoad"), "staff-email");
      }
    } finally {
      setInboxLoading(false);
    }
  }

  function copy(value: string) {
    navigator.clipboard
      .writeText(value)
      .then(() => notifySuccess(sharedT("contextMenu.copied"), "staff-email"))
      .catch(() => notifyError(sharedT("contextMenu.copyFailed"), "staff-email"));
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
      notifyError(reason instanceof Error ? reason.message : t("error.openMessage"), "staff-email");
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
      subject: /^re:/i.test(subject) ? subject : `Re: ${subject || t("dialog.noSubject")}`,
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
        notifyError(t("error.tooManyAttachments", { count: MAX_ATTACHMENTS }), "staff-email");
        break;
      }
      if (next.some((item) => item.name === file.name && item.size === file.size)) continue;
      next.push(file);
    }
    if (next.reduce((total, file) => total + file.size, 0) > MAX_ATTACHMENT_BYTES) {
      notifyError(t("error.attachmentsTooLarge"), "staff-email");
      return;
    }
    setCompose({ ...compose, attachments: next });
  }

  async function submitCompose() {
    if (sending || !compose) return;
    if (!compose.to.trim() || !compose.subject.trim() || !compose.text.trim()) {
      notifyError(t("error.composeIncomplete"), "staff-email");
      return;
    }
    setSending(true);
    notifyLoading(t("sending"), "staff-email");
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
      notifySuccess(t("sent", { address: result.message.to_address }), "staff-email");
      setCompose(null);
      setSelected(result.message);
      await loadInbox();
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("error.sendFailed"), "staff-email");
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

  // Every element that stands for one mail — a list row, the open message, a
  // turn of its thread — answers the context menu with the same three rows.
  // Reply is the one action the list itself cannot reach; the copies save
  // selecting an address or a subject out of the reader by hand.
  useEffect(() => {
    const messageFor = (id: string) => {
      const fromInbox = inbox?.messages.find((item) => item.message_id === id);
      if (fromInbox) return fromInbox;
      if (selected?.message_id === id) return selected;
      return selected?.thread?.find((item) => item.message_id === id) || null;
    };
    return registerContextMenuExtras((target) => {
      const holder = target.closest<HTMLElement>("[data-email-message-id]");
      const message = holder ? messageFor(holder.dataset.emailMessageId || "") : null;
      if (!message) return null;
      return [
        { key: "email-reply", label: t("menu.reply"), icon: "arrow", action: () => startCompose(message) },
        { key: "email-copy-address", label: t("menu.copyAddress"), icon: "mail", action: () => copy(counterpart(message)) },
        {
          key: "email-copy-subject",
          label: t("menu.copySubject"),
          icon: "copy",
          action: () => copy(message.subject || t("dialog.noSubject")),
        },
      ];
    });
  }, [inbox, selected, mailboxFilter, t, sharedT]);

  if (accessLoading) return <div className="dashboard-state"><div className="loading-ring" /><p>{t("auth.checkingAccess")}</p></div>;
  if (!auth?.authenticated) {
    return <AuthScreen
      eyebrow={t("auth.eyebrow")}
      title={<>{t("auth.signInBefore")} <em>{t("auth.signInEmphasis")}</em></>}
      description={t("auth.signedOutText")}
      back={{ label: t("auth.back"), onClick: () => navigate("/dashboard") }}
    >
      <DiscordSignIn next="/dashboard/staff/email" available={auth?.oauth_available} />
    </AuthScreen>;
  }
  if (!staffRole) {
    return <AuthScreen
      eyebrow={t("auth.eyebrow")}
      title={<>{t("auth.staffOnlyBefore")} <em>{t("auth.staffOnlyEmphasis")}</em></>}
      description={t("auth.staffOnlyText")}
      back={{ label: t("auth.backStaff"), onClick: () => navigate("/dashboard/staff") }}
    />;
  }
  if (accessError && !inbox) {
    return <AuthScreen
      eyebrow={t("auth.eyebrow")}
      title={<>{t("auth.noMailboxBefore")} <em>{t("auth.noMailboxEmphasis")}</em></>}
      description={accessError}
      back={{ label: t("auth.backStaff"), onClick: () => navigate("/dashboard/staff") }}
    />;
  }

  const mailboxes = inbox?.mailboxes || [];
  const activeMailboxLabel = inbox?.mailboxes.find((mailbox) => mailbox.local === mailboxFilter)?.label || t("inbox.allAddresses");
  const selectedKey = selected ? threadKey(selected) : "";
  const composeMailbox = mailboxes.find((mailbox) => mailbox.local === compose?.mailbox);
  const personalAddress = mailboxes.find((mailbox) => mailbox.kind === "personal")?.address;

  const content = <div className="staff-page staff-email-page">
    <header className="staff-heading">
      <div>
        <div className="eyebrow">{t("page.eyebrow")}</div>
        <h1>{t("page.title")}</h1>
        <p>{t("page.body")}</p>
      </div>
      <div className="staff-email-head-side">
        {staffRole === "owner" && <button type="button" className="button button-muted button-small" onClick={() => navigate(staffEmailReportsPath())}>
          <Icon name="alert" /> {t("page.reportQueue")}
        </button>}
        <div className="staff-role-card"><span className="staff-role-mark staff-email-mark"><Icon name="mail" /></span><span><small>{mailboxes.length > 1 ? t("inbox.allAddresses") : t("inbox.yourAddress")}</small><strong>{activeMailboxLabel}</strong></span></div>
      </div>
    </header>

    {!inbox && inboxLoading && <LoadingCard message={t("inbox.loading")} />}

    {inbox && !inbox.configured && <section className="staff-email-setup" role="status">
      <div className="staff-email-setup-copy">
        <span className="panel-kicker">{t("setup.kicker")}</span>
        <h2>{t("setup.title")}</h2>
        <p>{t("setup.before")} <strong>{inbox.domain}</strong> {t("setup.between")} <code>/api/staff/email/inbound</code>{t("setup.after")}</p>
      </div>
      <ul className="staff-email-setup-keys">
        {inbox.missing.map((name) => <li key={name}><code>{name}</code></li>)}
      </ul>
    </section>}

    {inbox && <div className="staff-email-layout">
      <aside className="staff-email-inbox" aria-label={t("inbox.aria")}>
        <div className="staff-email-inbox-head">
          <div className="staff-email-mailboxes" role="group" aria-label={t("inbox.addresses")}>
            <button type="button" className={mailboxFilter ? "" : "active"} onClick={() => setMailboxFilter("")}>{t("inbox.all")} <span>{conversations.length}</span></button>
            {mailboxes.map((mailbox) => <button type="button" key={mailbox.local} className={mailboxFilter === mailbox.local ? "active" : ""} onClick={() => setMailboxFilter(mailbox.local)}>{mailbox.label} <span>{conversations.filter((conversation) => conversation.latest.mailbox === mailbox.local).length}</span></button>)}
          </div>
          <button type="button" className="button button-primary button-small" onClick={() => startCompose()}><Icon name="plus" /> {t("inbox.write")}</button>
        </div>
        <div className="staff-email-toolbar">
          <label className="staff-guild-search"><Icon name="search" /><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t("inbox.search")} aria-label={t("inbox.search")} /></label>
          <button type="button" className="staff-email-refresh" onClick={() => void loadInbox()} disabled={inboxLoading} aria-label={t("inbox.refresh")}><Icon name="spark" /></button>
        </div>
        {inboxLoading && inbox.messages.length === 0 ? <LoadingCard message={t("inbox.loadingMessages")} />
          : conversations.length === 0 ? <div className="staff-email-empty-list">{inbox.messages.length ? t("inbox.noMatch") : t("inbox.emptyList")}</div>
          : <div className="staff-email-list">
            {conversations.map((conversation) => {
              const message = conversation.latest;
              return <button
                type="button"
                key={conversation.key}
                data-email-message-id={message.message_id}
                className={`staff-email-item${selectedKey === conversation.key ? " is-open" : ""}${conversation.unread ? " is-unread" : ""}`}
                onClick={() => void openMessage(message)}
              >
                <span className="staff-email-item-top">
                  <strong>{message.direction === "outbound" ? t("item.to", { address: message.to_address }) : message.from_name || message.from_address}</strong>
                  <span className="staff-email-item-when">
                    {conversation.messages.length > 1 && <b className="staff-email-thread-count" title={t("thread.count", { count: conversation.messages.length })}>{conversation.messages.length}</b>}
                    <time dateTime={new Date(message.created_at * 1000).toISOString()}>{formatWhen(message.created_at)}</time>
                  </span>
                </span>
                <span className="staff-email-item-subject">{message.subject}{message.direction === "outbound" && <em>{statusLabel(message, t)}</em>}</span>
                <span className="staff-email-item-preview">{message.preview || t("item.noPreview")}</span>
                <span className="staff-email-item-address">{conversation.messages.length > 1 ? t("item.addressConversation", { address: `${message.mailbox}@${inbox.domain}`, count: conversation.messages.length }) : `${message.mailbox}@${inbox.domain}`}</span>
              </button>;
            })}
          </div>}
      </aside>

      <section className="staff-email-reader" aria-label={t("reader.aria")}>
        {compose ? <div className="staff-email-compose">
          <div className="staff-email-reader-head">
            <div><span className="panel-kicker">{compose.thread_id ? t("compose.replyKicker") : t("compose.newKicker")}</span><h2>{t("compose.title")}</h2></div>
            <button type="button" className="button button-muted button-small" onClick={() => setCompose(null)}>{t("compose.cancel")}</button>
          </div>
          <div className="staff-fields">
            <div className="form-field"><span className="form-label">{t("compose.from")}</span>
              <Select ariaLabel={t("compose.from")} placeholder={null} options={mailboxes.map((mailbox) => ({ value: mailbox.local, label: mailbox.address }))} value={compose.mailbox} onChange={(value) => setCompose({ ...compose, mailbox: value })} />
            </div>
            {composeMailbox?.kind === "shared" && <p className="staff-email-signature-note">
              <Icon name="mail" />
              <span>{t("compose.signature", { address: personalAddress || t("compose.yourAddress") })}</span>
            </p>}
            <label className="form-field"><span className="form-label">{t("compose.to")}</span>
              <input type="email" value={compose.to} onChange={(event) => setCompose({ ...compose, to: event.target.value })} placeholder="name@example.com" autoComplete="off" />
            </label>
            <label className="form-field"><span className="form-label">{t("compose.subject")}</span>
              <input value={compose.subject} onChange={(event) => setCompose({ ...compose, subject: event.target.value })} maxLength={300} placeholder={t("compose.subjectPlaceholder")} />
            </label>
            <div className="form-field">
              <span className="form-label">{t("compose.message")}</span>
              <RichTextEditor
                value={compose.html}
                onChange={(html, text) => setCompose((current) => current ? { ...current, html, text } : current)}
                placeholder={t("compose.placeholder")}
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
                <Icon name="attach" /> {t("compose.attach")}
              </button>
              <span className="staff-email-attach-note">{t("compose.attachNote", { count: MAX_ATTACHMENTS })}</span>
            </div>
            {compose.attachments.length > 0 && <ul className="staff-email-attach-list">
              {compose.attachments.map((file, index) => <li key={`${file.name}-${index}`}>
                <Icon name="file" />
                <span>{file.name}</span>
                <small>{formatBytes(file.size)}</small>
                <button
                  type="button"
                  aria-label={t("compose.removeFile", { name: file.name })}
                  onClick={() => setCompose((current) => current ? { ...current, attachments: current.attachments.filter((_, item) => item !== index) } : current)}
                ><Icon name="close" /></button>
              </li>)}
            </ul>}
          </div>
          <div className="staff-panel-footer"><span>{t("compose.footer", { address: `${compose.mailbox}@${inbox.domain}` })}{compose.thread_id ? t("compose.footerReply") : ""}</span><button type="button" className="button button-primary" onClick={() => void submitCompose()} disabled={sending}>{sending ? t("compose.sending") : t("compose.send")}</button></div>
        </div>
          : selected ? <article className="staff-email-message" data-email-message-id={selected.message_id}>
            <div className="staff-email-reader-head">
              <div>
                <span className="panel-kicker">{selected.direction === "outbound" ? t("reader.sent") : t("reader.receivedOn", { address: selected.to_address })}</span>
                <h2>{selected.subject || t("dialog.noSubject")}</h2>
                <p className="staff-email-meta">
                  <strong>{selected.from_name ? `${selected.from_name} · ` : ""}{selected.from_address}</strong>
                  <span>{new Date(selected.created_at * 1000).toLocaleString()}</span>
                </p>
                {selected.direction === "outbound" && <Receipt message={selected} onOpen={(message) => void openStatus(message)} />}
                <AttachmentList files={selected.attachments} />
              </div>
              <button type="button" className="button button-primary button-small" onClick={() => startCompose(selected)}><Icon name="arrow" /> {t("reader.reply")}</button>
            </div>
            {selected.thread && selected.thread.length > 1 ? <div className="staff-email-thread">
              <p className="staff-email-thread-head"><span>{t("thread.count", { count: selected.thread.length })}</span><small>{t("thread.oldestFirst")}</small></p>
              {selected.thread.map((entry) => <article key={entry.message_id} data-email-message-id={entry.message_id} className={`staff-email-turn is-${entry.direction}${entry.message_id === selected.message_id ? " is-current" : ""}`}>
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
            <h2>{inbox.messages.length ? t("reader.pickTitle") : t("reader.emptyTitle")}</h2>
            <p>{inbox.messages.length ? t("reader.pickBody") : t("reader.emptyBody", { addresses: mailboxes.map((mailbox) => mailbox.address).join(" / ") })}</p>
            <button type="button" className="button button-muted" onClick={() => startCompose()}><Icon name="plus" /> {t("reader.writeMessage")}</button>
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
    developerAccess={developerAccess}
    onHome={() => navigate(dashboardPath())}
    onServers={() => navigate(dashboardServersPath())}
    onGuildChange={() => undefined}
    onSectionChange={() => undefined}
    onUserTabChange={(tab) => navigate(dashboardUserPath(tab))}
    onRefresh={() => void loadInbox()}
    refreshing={inboxLoading}
  >{content}</DashboardShell>;
}
