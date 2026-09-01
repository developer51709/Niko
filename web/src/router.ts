export type Page = "home" | "commands" | "docs" | "dashboard" | "privacy" | "terms";
export type DashSection = "overview" | "economy" | "leveling" | "moderation" | "ai";

function normalizedPath(pathname: string) {
  return pathname.replace(/\/+$/, "") || "/";
}

export function pageFromPath(pathname = window.location.pathname): Page {
  const path = normalizedPath(pathname);
  if (path === "/commands") return "commands";
  if (path === "/docs") return "docs";
  if (path === "/dashboard" || path.startsWith("/dashboard/")) return "dashboard";
  if (path === "/privacy") return "privacy";
  if (path === "/terms") return "terms";
  return "home";
}

export function dashboardPath(guildId?: string, section: DashSection = "overview") {
  return guildId ? `/dashboard/${guildId}/${section}` : "/dashboard";
}

export function dashboardRoute(): { guildId: string | null; section: DashSection } {
  const parts = normalizedPath(window.location.pathname).split("/").filter(Boolean);
  const known: DashSection[] = ["overview", "economy", "leveling", "moderation", "ai"];
  return {
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