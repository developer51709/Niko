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

  useEffect(() => {
    Promise.all([getAuth(), getStaffMe(), getStats(), getGuilds()])
      .then(([authStatus, staffStatus, botStats, availableGuilds]) => {
        setAuth(authStatus);
        setStaff(staffStatus);
        setStats(botStats);
        setGuilds(availableGuilds);
        const profile = staffStatus.profile;
        setForm({
          public_bio: profile.bio || "",
          public_banner_url: profile.public_banner_url || "",
          public_visible: profile.visible !== false,
        });
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Staff access unavailable."));
  }, []);

  if (!auth || (!staff && !error)) return <div className="dashboard-state"><div className="loading-ring" /><p>Checking staff access…</p></div>;
  if (error || !staff || !auth.authenticated) return <><PublicHeader page="dashboard" /><main className="auth-page"><div className="auth-card"><div className="eyebrow">Staff workspace</div><h1>Private team area.</h1><p>{!auth?.authenticated ? "Sign in with Discord to continue." : error || "This area is only available to official Niko staff."}</p>{!auth?.authenticated && <a className="button button-primary full-width" href="/auth/login?next=/dashboard/staff">Continue with Discord</a>}<button className="back-link" onClick={() => navigate("/dashboard")}>Return to dashboard</button></div></main></>;

  const canManageGlobal = ["owner", "head_admin", "graphic_designer"].includes(staff.role);
  const update = (key: string, value: string | boolean) => setForm((current) => ({ ...current, [key]: value }));
  const save = async () => {
    if (saving) return;
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await saveStaffProfile(form, auth.csrf_token);
      setMessage("Your public team listing was saved.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save listing.");
    } finally {
      setSaving(false);
    }
  };
  const saveGlobal = async () => { setError(""); setMessage(""); try { await saveGlobalProfile(global, auth.csrf_token); setMessage("Niko's global profile was updated."); } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not update global profile."); } };

  const content = <div className="staff-page"><div className="page-heading"><div className="eyebrow">Staff workspace · {staff.role_label}</div><h1>Shape your presence.</h1><p>Manage only the controls granted to your role. Support staff can maintain their public listing without touching global bot settings.</p></div>
    <section className="staff-panel"><div className="panel-heading"><div><span className="panel-kicker">Public listing</span><h2>How the team sees you</h2></div></div><div className="form-grid"><label className="form-field"><span className="form-label">Banner URL</span><input value={form.public_banner_url} onChange={(e) => update("public_banner_url", e.target.value)} placeholder="https://…" /></label><label className="form-field"><span className="form-label">Extended introduction</span><textarea value={form.public_bio} onChange={(e) => update("public_bio", e.target.value)} maxLength={1200} placeholder="Tell the community what you do…" /></label></div><label className="setting-row"><span><strong>Show me on the public Team page</strong><small>Hide your listing without removing your staff access.</small></span><input type="checkbox" checked={form.public_visible} onChange={(e) => update("public_visible", e.target.checked)} /><i /></label><button type="button" className="button button-primary" onClick={save} disabled={saving}>{saving ? "Saving…" : "Save public listing"}</button></section>
    {canManageGlobal && <section className="staff-panel"><div className="panel-heading"><div><span className="panel-kicker">Graphic direction</span><h2>Global Niko profile</h2></div></div><p className="form-hint">Graphic Designers, Head Admins, and owners can update the bot-wide avatar and banner. Paste publicly reachable image URLs.</p><div className="form-grid"><label className="form-field"><span className="form-label">Bot avatar URL</span><input value={global.avatar_url} onChange={(e) => setGlobal({ ...global, avatar_url: e.target.value })} /></label><label className="form-field"><span className="form-label">Bot banner URL</span><input value={global.banner_url} onChange={(e) => setGlobal({ ...global, banner_url: e.target.value })} /></label></div><button className="button button-primary" onClick={saveGlobal}>Update global profile</button></section>}
    {message && <div className="notice">{message}</div>}{error && <div className="notice warning">{error}</div>}
  </div>;

  return <DashboardShell user={auth.user!} guilds={guilds} selectedGuild={null} view="overview" section="overview" stats={stats} staffRole={staff.role} onHome={() => navigate(dashboardPath())} onServers={() => navigate(dashboardServersPath())} onGuildChange={() => undefined} onSectionChange={() => undefined} onRefresh={() => window.location.reload()} refreshing={false}>{content}</DashboardShell>;
}
