import { useEffect, useMemo, useState } from "react";
import { getAuth, getGuilds, getStaffEmail, getStaffEmailMessage, getStaffMe, getStats, sendStaffEmail } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { dashboardPath, dashboardServersPath, dashboardUserPath, navigate } from "../router";
import { notifyError, notifyLoading, notifySuccess } from "../utils/toast";
import type { AuthStatus, BotStats, Guild, StaffEmailInbox, StaffEmailMessage } from "../types";

/** Only these roles hold a staff address; the API enforces the same rule. */
const MAILBOX_ROLES = ["owner", "head_admin"];

type Compose = { mailbox: string; to: string; subject: string; body: string };

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

  useEffect(() => {
    let active = true;
    getAuth().then(async (authStatus) => {
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
      if (!MAILBOX_ROLES.includes(staffStatus.role)) return;
      const [botStats, availableGuilds] = await Promise.all([getStats(), getGuilds()]);
      if (!active) return;
      setStats(botStats);
      setGuilds(availableGuilds);
      void loadInbox();
    }).catch((reason) => {
      if (active) {
        setAccessError(reason instanceof Error ? reason.message : "Staff mailbox unavailable.");
        setAccessLoading(false);
      }
    });
    return () => { active = false; };
  }, []);

  async function loadInbox() {
    setInboxLoading(true);
    try {
      setInbox(await getStaffEmail());
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : "The mailbox could not be loaded.", "staff-email");
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
    const fallback = mailboxFilter || inbox?.mailboxes[0]?.local || "admin";
    if (!message) {
      setSelected(null);
      setCompose({ mailbox: fallback, to: "", subject: "", body: "" });
      return;
    }
    const subject = message.subject || "";
    setCompose({
      mailbox: message.mailbox || fallback,
      to: counterpart(message),
      subject: /^re:/i.test(subject) ? subject : `Re: ${subject || "(no subject)"}`,
      body: "",
    });
  }

  async function submitCompose() {
    if (sending || !compose) return;
    if (!compose.to.trim() || !compose.subject.trim() || !compose.body.trim()) {
      notifyError("Add a recipient, a subject, and a message.", "staff-email");
      return;
    }
    setSending(true);
    notifyLoading("Sending from Niko…", "staff-email");
    try {
      const result = await sendStaffEmail(compose, auth?.csrf_token);
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

  if (accessLoading) return <div className="dashboard-state"><div className="loading-ring" /><p>Checking your staff access…</p></div>;
  if (accessError || !auth?.authenticated) {
    return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><div className="eyebrow">Staff mailbox</div><h1>{auth && !auth.authenticated ? "Sign in to continue." : "This mailbox is private."}</h1><p>{auth && !auth.authenticated ? "The staff mailbox opens with your Discord account." : accessError || "Only official Niko staff can open this page."}</p>{auth && !auth.authenticated && <a className="button button-primary full-width" href="/auth/login?next=/dashboard/staff/email">Continue with Discord</a>}<button className="back-link" onClick={() => navigate("/dashboard")}>Return to dashboard</button></div></main></>;
  }
  if (!staffRole || !MAILBOX_ROLES.includes(staffRole)) {
    return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><div className="eyebrow">Staff mailbox</div><h1>Owner and Head Admins only.</h1><p>Niko's own-domain mail is limited to the bot owner and Head Admins. Your current staff role does not include a mailbox.</p><button className="back-link" onClick={() => navigate("/dashboard/staff")}>Back to the staff workspace</button></div></main></>;
  }

  const mailboxes = inbox?.mailboxes || [];
  const activeMailboxLabel = inbox?.mailboxes.find((mailbox) => mailbox.local === mailboxFilter)?.label || "All addresses";

  const content = <div className="staff-page staff-email-page">
    <header className="staff-heading">
      <div>
        <div className="eyebrow">Correspondence</div>
        <h1>Staff mailbox.</h1>
        <p>Niko's own-domain inbox. Partners, applicants, and members write to the addresses below, and every reply leaves from the same address — nothing here is linked from the public site.</p>
      </div>
      <div className="staff-role-card"><span className="staff-role-mark staff-email-mark"><Icon name="mail" /></span><span><small>{mailboxes.length > 1 ? "All addresses" : "Your address"}</small><strong>{activeMailboxLabel}</strong></span></div>
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
            <button type="button" className={mailboxFilter ? "" : "active"} onClick={() => setMailboxFilter("")}>All <span>{inbox.messages.length}</span></button>
            {mailboxes.map((mailbox) => <button type="button" key={mailbox.local} className={mailboxFilter === mailbox.local ? "active" : ""} onClick={() => setMailboxFilter(mailbox.local)}>{mailbox.label} <span>{inbox.messages.filter((message) => message.mailbox === mailbox.local).length}</span></button>)}
          </div>
          <button type="button" className="button button-primary button-small" onClick={() => startCompose()}><Icon name="plus" /> Write</button>
        </div>
        <div className="staff-email-toolbar">
          <label className="staff-guild-search"><Icon name="search" /><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search the mailbox" aria-label="Search the mailbox" /></label>
          <button type="button" className="staff-email-refresh" onClick={() => void loadInbox()} disabled={inboxLoading} aria-label="Refresh mailbox"><Icon name="spark" /></button>
        </div>
        {inboxLoading && inbox.messages.length === 0 ? <div className="staff-guild-empty"><div className="loading-ring" /><p>Loading messages…</p></div>
          : visible.length === 0 ? <div className="staff-email-empty-list">{inbox.messages.length ? "No messages match that search." : "No mail yet. Anything sent to your address lands here."}</div>
          : <div className="staff-email-list">
            {visible.map((message) => <button
              type="button"
              key={message.message_id}
              className={`staff-email-item${selected?.message_id === message.message_id ? " is-open" : ""}${message.read ? "" : " is-unread"}`}
              onClick={() => void openMessage(message)}
            >
              <span className="staff-email-item-top">
                <strong>{message.direction === "outbound" ? `To ${message.to_address}` : message.from_name || message.from_address}</strong>
                <time dateTime={new Date(message.created_at * 1000).toISOString()}>{formatWhen(message.created_at)}</time>
              </span>
              <span className="staff-email-item-subject">{message.subject}{message.direction === "outbound" && <em>Sent</em>}</span>
              <span className="staff-email-item-preview">{message.preview || "No message text."}</span>
              <span className="staff-email-item-address">{message.mailbox}@{inbox.domain}</span>
            </button>)}
          </div>}
      </aside>

      <section className="staff-email-reader" aria-label="Message">
        {compose ? <div className="staff-email-compose">
          <div className="staff-email-reader-head">
            <div><span className="panel-kicker">New message</span><h2>Write from Niko</h2></div>
            <button type="button" className="button button-muted button-small" onClick={() => setCompose(null)}>Cancel</button>
          </div>
          <div className="staff-fields">
            <label className="form-field"><span className="form-label">From</span>
              <select value={compose.mailbox} onChange={(event) => setCompose({ ...compose, mailbox: event.target.value })}>
                {mailboxes.map((mailbox) => <option value={mailbox.local} key={mailbox.local}>{mailbox.address}</option>)}
              </select>
            </label>
            <label className="form-field"><span className="form-label">To</span>
              <input type="email" value={compose.to} onChange={(event) => setCompose({ ...compose, to: event.target.value })} placeholder="name@example.com" autoComplete="off" />
            </label>
            <label className="form-field"><span className="form-label">Subject</span>
              <input value={compose.subject} onChange={(event) => setCompose({ ...compose, subject: event.target.value })} maxLength={300} placeholder="What is this about?" />
            </label>
            <label className="form-field"><span className="form-label">Message</span>
              <textarea className="staff-email-body-input" value={compose.body} onChange={(event) => setCompose({ ...compose, body: event.target.value })} rows={14} placeholder="Write the reply…" />
            </label>
          </div>
          <div className="staff-panel-footer"><span>Sent from {compose.mailbox}@{inbox.domain} · a copy is kept in this mailbox.</span><button type="button" className="button button-primary" onClick={() => void submitCompose()} disabled={sending}>{sending ? "Sending…" : "Send message"}</button></div>
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
              </div>
              <button type="button" className="button button-primary button-small" onClick={() => startCompose(selected)}><Icon name="arrow" /> Reply</button>
            </div>
            <pre className="staff-email-body">{selected.body || "This message arrived without a text body."}</pre>
          </article>
          : <div className="staff-email-reader-empty">
            <span className="staff-email-reader-icon"><Icon name="mail" /></span>
            <h2>{inbox.messages.length ? "Pick a message." : "The inbox is empty."}</h2>
            <p>{inbox.messages.length ? "Messages sent to your address appear on the left; opening one shows the full text and a reply button." : `Mail sent to ${mailboxes.map((mailbox) => mailbox.address).join(" or ")} will show up here as soon as the provider forwards it.`}</p>
            <button type="button" className="button button-muted" onClick={() => startCompose()}><Icon name="plus" /> Write a message</button>
          </div>}
      </section>
    </div>}
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
