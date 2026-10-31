export type Page = "home" | "commands" | "docs" | "docs-detail" | "leaderboard" | "guild-leaderboard" | "dashboard" | "staff" | "appeal" | "application" | "team-application" | "team" | "team-member" | "support" | "discord" | "partnership" | "privacy" | "terms" | "data-removal" | "community" | "donate" | "billing" | "gift" | "transcript" | "changelog" | "changelog-detail" | "render-lab";

// Unlisted scratch route for eyeballing Discord text and profile popup
// rendering. It is deliberately not linked, documented, or prerendered.
export const RENDER_LAB_PATH = "/render-lab-b7f3e91c";
export type DashSection = "overview" | "leveling" | "moderation" | "server" | "onboarding" | "tickets" | "notifications" | "boosters" | "applications" | "ai" | "customization";
export type UserTab = "overview" | "economy" | "achievements";
export type DashboardView = "overview" | "servers" | "guild";

const USER_TABS: UserTab[] = ["overview", "economy", "achievements"];

function normalizedPath(pathname: string) {
  return pathname.replace(/\/+$/, "") || "/";
}

export function pageFromPath(pathname = window.location.pathname): Page {
  const path = normalizedPath(pathname);
  if (path === RENDER_LAB_PATH) return "render-lab";
  if (path === "/appeals/blacklist") return "appeal";
  if (path === "/commands") return "commands";
  if (path === "/leaderboard") return "leaderboard";
  if (path.startsWith("/levels/")) return "guild-leaderboard";
  if (path === "/docs") return "docs";
  if (path.startsWith("/docs/")) return "docs-detail";
  if (path === "/dashboard/staff" || path === "/dashboard/staff/") return "staff";
  if (path === "/team/apply" || path.startsWith("/team/apply/")) return "team-application";
  if (path.startsWith("/apply/")) return "application";
  if (path === "/dashboard" || path.startsWith("/dashboard/")) return "dashboard";
  if (path === "/team") return "team";
  if (path === "/support") return "support";
  if (path === "/discord/partnership") return "partnership";
  if (path === "/discord") return "discord";
  if (path.startsWith("/team/")) return "team-member";
  if (path === "/privacy") return "privacy";
  if (path === "/terms") return "terms";
  if (path === "/data-removal") return "data-removal";
  if (path === "/community") return "community";
  if (path === "/donate" || path.startsWith("/donate")) return "donate";
  if (path === "/billing/gift") return "gift";
  if (path === "/billing" || path.startsWith("/billing/")) return "billing";
  if (path === "/transcript" || path.startsWith("/transcript/")) return "transcript";
  if (path === "/changelog") return "changelog";
  if (path.startsWith("/changelog/")) return "changelog-detail";
  return "home";
}

export function dashboardPath(guildId?: string, section: DashSection = "overview") {
  return guildId ? `/dashboard/${guildId}/${section}` : "/dashboard";
}

/** Personal tabs live under `/dashboard` and never select a server. */
export function dashboardUserPath(tab: UserTab = "overview") {
  return tab === "overview" ? "/dashboard" : `/dashboard/me/${tab}`;
}

export function dashboardServersPath() {
  return "/dashboard/servers";
}

export function dashboardRoute(): { view: DashboardView; guildId: string | null; section: DashSection; tab: UserTab } {
  const parts = normalizedPath(window.location.pathname).split("/").filter(Boolean);
  const known: DashSection[] = ["overview", "leveling", "moderation", "server", "onboarding", "tickets", "notifications", "boosters", "applications", "ai", "customization"];
  if (parts[1] === "servers") {
    return { view: "servers", guildId: null, section: "overview", tab: "overview" };
  }
  if (!parts[1] || parts[1] === "staff") {
    return { view: "overview", guildId: null, section: "overview", tab: "overview" };
  }
  if (parts[1] === "me") {
    return {
      view: "overview",
      guildId: null,
      section: "overview",
      tab: USER_TABS.includes(parts[2] as UserTab) ? parts[2] as UserTab : "overview",
    };
  }
  return {
    view: "guild",
    guildId: parts[1] || null,
    section: known.includes(parts[2] as DashSection) ? parts[2] as DashSection : "overview",
    tab: "overview",
  };
}

export function navigate(path: string) {
  if (!path.startsWith("/")) return;
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo({ top: 0, behavior: "smooth" });
}