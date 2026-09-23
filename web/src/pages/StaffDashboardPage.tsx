import { useEffect, useState } from "react";
import { getAuth, getGuilds, getStaffMe, getStats, saveGlobalProfile, saveStaffProfile } from "../api";
import { DashboardShell } from "../components/dashboard/DashboardShell";
import { PublicHeader } from "../components/PublicHeader";
import { dashboardPath, dashboardServersPath, navigate } from "../router";
import type { AuthStatus, BotStats, Guild, StaffMember } from "../types";

export function StaffDashboardPage() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [staff, setStaff] = useState<{ role: string; role_label: string; profile: StaffMember } | null>(null);
  const [stats, setStats] = useState<BotStats | null>(null);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [form, setForm] = useState({ public_bio: "", public_banner_url: "", public_visible: true });
  const [global, setGlobal] = useState({ avatar_url: "", banner_url: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [savingGlobal, setSavingGlobal] = useState(false);

  useEffect(() => {
    Promise.all([getAuth(), getStaffMe(), getStats(), getGuilds()])
      .then(([authStatus, staffStatus, botStats, availableGuilds]) => {
        setAuth(authStatus);
        setStaff(staffStatus);
        setStats(botStats);
        setGuilds(availableGuilds);
        setForm({
          public_bio: staffStatus.profile.bio || "",
          public_banner_url: staffStatus.profile.public_banner_url || "",
          public_visible: staffStatus.profile.visible !== false,
        });
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Staff access unavailable."));
  }, []);

  if (!auth || (!staff && !error)) return <div className="dashboard-state"><div className="loading-ring" /><p>Checking staff access…</p></div>;
  if (error || !staff || !auth.authenticated) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><div className="eyebrow">Staff workspace</div><h1>Private team area.</h1><p>{!auth?.authenticated ? "Sign in with Discord to continue." : error || "This area is only available to official Niko staff."}</p>{!auth?.authenticated && <a className="button button-primary full-width" href="/auth/login?next=/dashboard/staff">Continue with Discord</a>}<button className="back-link" onClick={() => navigate("/dashboard")}>Return to dashboard</button></div></main></>;

  const signedInUser = auth.user!;
  const discordDefaultAvatar = `https://cdn.discordapp.com/embed/avatars/${Number(BigInt(signedInUser.id) % 5n)}.png`;
  const signedInAvatar = signedInUser.avatar
    ? `https://cdn.discordapp.com/avatars/${signedInUser.id}/${signedInUser.avatar}.png?size=128`
    : discordDefaultAvatar;
  const canManageGlobal = ["owner", "head_admin", "graphic_designer"].includes(staff.role);
  const update = (key: string, value: string | boolean) => setForm((current) => ({ ...current, [key]: value }));
  const save = async () => {
    if (saving) return;
    setSaving(true); setError(""); setMessage("");
    try { await saveStaffProfile(form, auth.csrf_token); setMessage("Your public team listing was saved."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not save listing."); }
    finally { setSaving(false); }
  };
  const saveGlobal = async () => {
    if (savingGlobal) return;
    setSavingGlobal(true); setError(""); setMessage("");
    try { await saveGlobalProfile(global, auth.csrf_token); setMessage("Niko's global profile was updated."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not update global profile."); }
    finally { setSavingGlobal(false); }
  };

  const content = <div className="staff-page">
    <header className="staff-heading">
      <div><div className="eyebrow">Staff workspace</div><h1>Shape your presence.</h1><p>Manage the public details granted to your <strong>{staff.role_label}</strong> role. Your name and avatar always come directly from Discord.</p></div>
      <div className="staff-role-card"><span className="staff-role-mark"><img src={signedInAvatar} alt="Your Discord profile" onError={(event) => { event.currentTarget.onerror = null; event.currentTarget.src = discordDefaultAvatar; }} /></span><span><small>Signed in as</small><strong>{staff.role_label}</strong></span></div>
    </header>

    <div className="staff-layout">
      <section className="staff-panel staff-panel-main">
        <div className="staff-panel-heading"><div><span className="panel-kicker">Public listing</span><h2>How the team sees you</h2><p>Keep your introduction current while Discord remains the source of truth for your identity.</p></div><span className="staff-step">01</span></div>
        <div className="staff-fields">
          <label className="form-field"><span className="form-label">Banner URL</span><input value={form.public_banner_url} onChange={(e) => update("public_banner_url", e.target.value)} placeholder="https://…" /><small>Use a publicly reachable image. Leave blank for no banner.</small></label>
          <label className="form-field staff-bio-field"><span className="form-label">Extended introduction</span><textarea value={form.public_bio} onChange={(e) => update("public_bio", e.target.value)} maxLength={1200} placeholder="Tell the community what you do…" /><small>{form.public_bio.length}/1200 characters</small></label>
        </div>
        <label className="setting-row staff-visibility"><span><strong>Show me on the public Team page</strong><small>Hide your listing without removing your staff access.</small></span><input type="checkbox" checked={form.public_visible} onChange={(e) => update("public_visible", e.target.checked)} /><i /></label>
        <div className="staff-panel-footer"><span>Changes apply immediately to your public profile.</span><button type="button" className="button button-primary" onClick={save} disabled={saving}>{saving ? "Saving…" : "Save public listing"}</button></div>
      </section>

      <aside className="staff-sidebar-card"><span className="panel-kicker">Profile rules</span><h3>Stay consistent with Discord</h3><p>Your global display name and profile picture sync automatically, so updates made in Discord are reflected here without another form.</p><div className="staff-rule"><span>Identity</span><strong>Discord synced</strong></div><div className="staff-rule"><span>Editable</span><strong>Bio · banner · visibility</strong></div></aside>
    </div>

    {canManageGlobal && <section className="staff-panel staff-global-panel"><div className="staff-panel-heading"><div><span className="panel-kicker">Graphic direction</span><h2>Global Niko profile</h2><p>Reserved for Graphic Designers, Head Admins, and owners. Paste publicly reachable image URLs.</p></div><span className="staff-step">02</span></div><div className="staff-fields staff-fields-two"><label className="form-field"><span className="form-label">Bot avatar URL</span><input value={global.avatar_url} onChange={(e) => setGlobal({ ...global, avatar_url: e.target.value })} placeholder="https://…" /></label><label className="form-field"><span className="form-label">Bot banner URL</span><input value={global.banner_url} onChange={(e) => setGlobal({ ...global, banner_url: e.target.value })} placeholder="https://…" /></label></div><div className="staff-panel-footer"><span>Updates the bot-wide Discord profile.</span><button type="button" className="button button-primary" onClick={saveGlobal} disabled={savingGlobal}>{savingGlobal ? "Updating…" : "Update global profile"}</button></div></section>}
    {message && <div className="notice">{message}</div>}{error && <div className="notice warning">{error}</div>}
  </div>;

  return <DashboardShell user={auth.user!} guilds={guilds} selectedGuild={null} view="overview" section="overview" stats={stats} staffRole={staff.role} onHome={() => navigate(dashboardPath())} onServers={() => navigate(dashboardServersPath())} onGuildChange={() => undefined} onSectionChange={() => undefined} onRefresh={() => window.location.reload()} refreshing={false}>{content}</DashboardShell>;
}
