export type Page = "home" | "commands" | "docs" | "docs-detail" | "status" | "leaderboard" | "guild-leaderboard" | "dashboard" | "staff" | "staff-email" | "staff-email-reports" | "email-report" | "appeal" | "application" | "team-application" | "team" | "team-member" | "support" | "discord" | "partnership" | "privacy" | "terms" | "data-removal" | "community" | "donate" | "billing" | "gift" | "transcript" | "changelog" | "changelog-detail" | "not-found" | "render-lab";

// Unlisted scratch route for eyeballing Discord text and profile popup
// rendering. It is deliberately not linked, documented, or prerendered.
export const RENDER_LAB_PATH = "/render-lab-b7f3e91c";
export type DashSection = "overview" | "leveling" | "moderation" | "server" | "onboarding" | "tickets" | "notifications" | "boosters" | "applications" | "ai" | "customization";
export type UserTab = "overview" | "economy" | "achievements";
export type DashboardView = "overview" | "servers" | "guild";

const USER_TABS: UserTab[] = ["overview", "economy", "achievements"];

declare global {
  interface Window {
    /**
     * What the server told the page when it served it (see
     * `social.render_site_shell`): the build it came from, and — on a section
     * subdomain — the apex path this host serves from its own root, "/dashboard"
     * on `dash.example.com`, where `/staff` is `/dashboard/staff`. Absent on the
     * apex, where paths already are what they say.
     */
    __NIKO_SHELL__?: {
      build?: string;
      prefix?: string;
      unknown?: boolean;
      site?: string;
      /** Apex section path → the origin that serves it (`/dashboard` →
       *  `https://dash.example.com`), present when subdomain routing is on. */
      sections?: Record<string, string>;
    };
  }
}

const SHELL = (typeof window === "undefined" ? undefined : window.__NIKO_SHELL__) || {};
const PATH_PREFIX = SHELL.prefix || "";

/** The apex path this host serves its root from; empty on the apex itself. */
export function pathPrefix() {
  return PATH_PREFIX;
}

/**
 * The build this page was served from; "" when the server could not name one
 * (a checkout without a bundle on disk). An open tab compares it with what the
 * site answers later to know whether it is running stale code.
 */
export function siteBuild() {
  return SHELL.build || "";
}

/**
 * True when the server answered this request because the host serves no site
 * (an unused subdomain of the site's own domain). The page is the subdomain
 * variant of the 404, whatever the path asks for.
 */
export function unknownHost() {
  return SHELL.unknown === true;
}

/** The site's own origin, set when the page was served from another host. */
export function siteOrigin() {
  return SHELL.site || "";
}

/** The origin that serves an apex section, or "" when it lives on this host. */
export function sectionOrigin(path: string) {
  const origin = (SHELL.sections || {})[path] || "";
  // This host already is that section (or the site does not route sections onto
  // their own hosts), so the path stays where it is.
  return PATH_PREFIX ? "" : origin;
}

/**
 * Where the dashboard lives, as something to hand to the browser: the short
 * form on its own subdomain when the site routes sections that way, and this
 * host's own ``/dashboard`` path otherwise. An absolute result is a real
 * navigation — the dashboard is a different origin then, not a page to push.
 */
export function dashboardHref() {
  const origin = sectionOrigin("/dashboard");
  if (!origin) return publicPath("/dashboard");
  // On the dash host the dashboard root is the site root, which the path prefix
  // already accounts for; everywhere else the long form is correct.
  return `${origin}/dashboard`;
}

/** The apex path behind a URL on this host: "/staff" -> "/dashboard/staff". */
export function apexPath(pathname: string) {
  if (!PATH_PREFIX) return pathname;
  if (pathname === "/") return PATH_PREFIX;
  if (pathname === PATH_PREFIX || pathname.startsWith(`${PATH_PREFIX}/`)) return pathname;
  return `${PATH_PREFIX}${pathname}`;
}

/** What this host's address bar shows for an apex path: "/dashboard/staff" -> "/staff". */
export function publicPath(path: string) {
  if (!PATH_PREFIX) return path;
  if (path === PATH_PREFIX) return "/";
  if (path.startsWith(`${PATH_PREFIX}/`)) return path.slice(PATH_PREFIX.length);
  return path;
}

/** The current page in the apex form, whichever host this is. */
export function currentPath() {
  return apexPath(window.location.pathname);
}

/**
 * The host of the site itself: a section host minus its label.
 * `dash.niko.sryze.cc` -> `niko.sryze.cc`, port and all.
 */
function apexHost() {
  return window.location.host.replace(/^[^.]+\./, "");
}

/**
 * A URL to hand to the browser for an apex path. On the apex it is the path
 * itself; on a section host it is the path where it really lives — the short
 * form for the host's own subtree, the site's own origin for everything else.
 */
export function siteHref(path: string) {
  if (!PATH_PREFIX || !path.startsWith("/")) return path;
  if (path === PATH_PREFIX || path.startsWith(`${PATH_PREFIX}/`)) return publicPath(path);
  return `${window.location.protocol}//${apexHost()}${path}`;
}

function normalizedPath(pathname: string) {
  return pathname.replace(/\/+$/, "") || "/";
}

export function pageFromPath(pathname = currentPath()): Page {
  const path = normalizedPath(pathname);
  if (path === RENDER_LAB_PATH) return "render-lab";
  if (path === "/appeals/blacklist") return "appeal";
  if (path === "/commands") return "commands";
  if (path === "/status") return "status";
  if (path === "/leaderboard") return "leaderboard";
  if (path.startsWith("/levels/")) return "guild-leaderboard";
  if (path === "/docs") return "docs";
  if (path.startsWith("/docs/")) return "docs-detail";
  if (path === "/dashboard/staff") return "staff";
  // The hidden staff mailbox sits beside the workspace, never under its hash
  // tabs, so it is its own page.
  if (path === "/dashboard/staff/email/reports") return "staff-email-reports";
  if (path === "/dashboard/staff/email") return "staff-email";
  // The public form behind the "report this message" link in a sent mail. It is
  // reached from an inbox, never from this site, so nothing links here.
  if (path.startsWith("/report/") && path.split("/").filter(Boolean).length >= 2) return "email-report";
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
  // Only the root is the home page. Everything else that matched nothing is a
  // page the site does not have, and saying so is better than showing the home
  // page under a URL that will keep looking broken.
  return path === "/" ? "home" : "not-found";
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

/** The bot owner's queue for reports filed from the footer of a sent mail. */
export function staffEmailReportsPath() {
  return "/dashboard/staff/email/reports";
}

export function dashboardRoute(): { view: DashboardView; guildId: string | null; section: DashSection; tab: UserTab } {
  const parts = normalizedPath(currentPath()).split("/").filter(Boolean);
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
  // A section host only serves its own subtree; anything outside it belongs to
  // the site, so it is a real navigation rather than a push into a page this
  // host cannot render.
  if (PATH_PREFIX && path !== PATH_PREFIX && !path.startsWith(`${PATH_PREFIX}/`)) {
    window.location.assign(siteHref(path));
    return;
  }
  // Paths are written in the apex form everywhere; a section host drops the
  // prefix it stands in for, which is what keeps the address bar short.
  window.history.pushState({}, "", publicPath(path));
  window.dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo({ top: 0, behavior: "smooth" });
}