export type Page = "home" | "commands" | "docs" | "docs-detail" | "dashboard" | "privacy" | "terms" | "donate";
export type DashSection = "overview" | "leveling" | "moderation" | "server" | "ai" | "customization";
export type DashboardView = "overview" | "servers" | "guild";

function normalizedPath(pathname: string) {
  return pathname.replace(/\/+$/, "") || "/";
}

export function pageFromPath(pathname = window.location.pathname): Page {
  const path = normalizedPath(pathname);
  if (path === "/commands") return "commands";
  if (path === "/docs") return "docs";
  if (path.startsWith("/docs/")) return "docs-detail";
  if (path === "/dashboard" || path.startsWith("/dashboard/")) return "dashboard";
  if (path === "/privacy") return "privacy";
  if (path === "/terms") return "terms";
  if (path === "/donate" || path.startsWith("/donate")) return "donate";
  return "home";
}

export function dashboardPath(guildId?: string, section: DashSection = "overview") {
  return guildId ? `/dashboard/${guildId}/${section}` : "/dashboard";
}

export function dashboardServersPath() {
  return "/dashboard/servers";
}

export function dashboardRoute(): { view: DashboardView; guildId: string | null; section: DashSection } {
  const parts = normalizedPath(window.location.pathname).split("/").filter(Boolean);
  const known: DashSection[] = ["overview", "leveling", "moderation", "server", "ai", "customization"];
  if (parts[1] === "servers") {
    return { view: "servers", guildId: null, section: "overview" };
  }
  if (!parts[1]) {
    return { view: "overview", guildId: null, section: "overview" };
  }
  return {
    view: "guild",
    guildId: parts[1] || null,
    section: known.includes(parts[2] as DashSection) ? parts[2] as DashSection : "overview",
  };
}

export function navigate(path: string) {
  if (!path.startsWith("/")) return;
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo({ top: 0, behavior: "smooth" });
}