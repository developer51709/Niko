import { useEffect, useState } from "react";
import { CommandsPage } from "./pages/CommandsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DocsPage, DocsSlugPage } from "./pages/DocsPage";
import { LeaderboardPage } from "./pages/LeaderboardPage";
import { StatusPage } from "./pages/StatusPage";
import { GuildLeaderboardPage } from "./pages/GuildLeaderboardPage";
import { HomePage } from "./pages/HomePage";
import { DonatePage } from "./pages/DonatePage";
import { BillingPage } from "./pages/BillingPage";
import { GiftPremiumPage } from "./pages/GiftPremiumPage";
import { LegalPage } from "./pages/LegalPage";
import { DataRemovalPage } from "./pages/DataRemovalPage";
import { TranscriptPage } from "./pages/TranscriptPage";
import { ChangelogPage } from "./pages/ChangelogPage";
import { ChangelogSlugPage } from "./pages/ChangelogSlugPage";
import { TeamPage, TeamMemberPage } from "./pages/TeamPage";
import { RenderLabPage } from "./pages/RenderLabPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { StaffDashboardPage } from "./pages/StaffDashboardPage";
import { StaffEmailPage } from "./pages/StaffEmailPage";
import { StaffEmailReportsPage } from "./pages/StaffEmailReportsPage";
import { EmailReportPage } from "./pages/EmailReportPage";
import { BlacklistAppealPage } from "./pages/BlacklistAppealPage";
import { StaffApplicationPage } from "./pages/StaffApplicationPage";
import { TeamStaffApplicationPage } from "./pages/TeamStaffApplicationPage";
import { DiscordRedirectPage, SupportPage } from "./pages/SupportPage";
import { PartnershipPage } from "./pages/PartnershipPage";
import { ToastHost } from "./components/ToastHost";
import { UpdatePrompt } from "./components/UpdatePrompt";
import { OwnerDevtools } from "./components/OwnerDevtools";
import { ShaderBackground } from "./components/ShaderBackground";
import { currentPath, pageFromPath, unknownHost, type Page } from "./router";
import { usePageTitle } from "./i18n";

export function App() {
  const [page, setPage] = useState<Page>(pageFromPath);
  // Client-side navigation never asks the server for a new document, so the tab
  // title is re-stamped here from the page's catalogue in the chosen language.
  usePageTitle(page);
  useEffect(() => {
    const handle = () => setPage(pageFromPath());
    window.addEventListener("popstate", handle);
    return () => window.removeEventListener("popstate", handle);
  }, []);

  let pageContent;
  // A host that serves no site is a 404 whatever the path says; the server
  // already answered with a 404 status and said so in the shell state.
  if (unknownHost()) pageContent = <NotFoundPage variant="subdomain" />;
  else if (page === "commands") pageContent = <CommandsPage />;
  else if (page === "status") pageContent = <StatusPage />;
  else if (page === "leaderboard") pageContent = <LeaderboardPage />;
  else if (page === "guild-leaderboard") {
    // Read through the router: on a section subdomain the address bar is short
    // and the apex path behind it is what the page params are cut from.
    const pathParts = currentPath().split("/").filter(Boolean);
    pageContent = <GuildLeaderboardPage guildId={pathParts[1] || ""} />;
  }
  else if (page === "docs-detail") {
    const pathParts = currentPath().split("/").filter(Boolean);
    pageContent = <DocsSlugPage slug={pathParts[pathParts.length - 1] || ""} />;
  } else if (page === "docs") pageContent = <DocsPage />;
  else if (page === "staff") pageContent = <StaffDashboardPage />;
  else if (page === "staff-email") pageContent = <StaffEmailPage />;
  else if (page === "staff-email-reports") pageContent = <StaffEmailReportsPage />;
  else if (page === "email-report") pageContent = <EmailReportPage />;
  else if (page === "appeal") pageContent = <BlacklistAppealPage />;
  else if (page === "application") pageContent = <StaffApplicationPage />;
  else if (page === "team-application") pageContent = <TeamStaffApplicationPage />;
  else if (page === "dashboard") pageContent = <DashboardPage />;
  else if (page === "team") pageContent = <TeamPage />;
  else if (page === "team-member") pageContent = <TeamMemberPage profileKey={currentPath().split("/").filter(Boolean)[1] || ""} />;
  else if (page === "support") pageContent = <SupportPage />;
  else if (page === "discord") pageContent = <DiscordRedirectPage />;
  else if (page === "partnership") pageContent = <PartnershipPage />;
  else if (page === "privacy") pageContent = <LegalPage type="privacy" />;
  else if (page === "terms") pageContent = <LegalPage type="terms" />;
  else if (page === "data-removal") pageContent = <DataRemovalPage />;
  else if (page === "community") pageContent = <LegalPage type="community" />;
  else if (page === "donate") pageContent = <DonatePage />;
  else if (page === "billing") pageContent = <BillingPage />;
  else if (page === "gift") pageContent = <GiftPremiumPage />;
  else if (page === "transcript") {
    const pathParts = currentPath().split("/").filter(Boolean);
    pageContent = <TranscriptPage transcriptId={pathParts[1] || ""} />;
  } else if (page === "render-lab") pageContent = <RenderLabPage />;
  else if (page === "changelog") pageContent = <ChangelogPage />;
  else if (page === "changelog-detail") {
    const pathParts = currentPath().split("/").filter(Boolean);
    pageContent = <ChangelogSlugPage slug={pathParts[pathParts.length - 1] || ""} />;
  } else if (page === "not-found") pageContent = <NotFoundPage variant="page" />;
  else pageContent = <HomePage />;

  return (
    <>
      <div className="site-ambient" aria-hidden="true">
        <ShaderBackground className="ambient-effect-canvas" />
      </div>
      <div className="site-content">{pageContent}</div>
      <ToastHost />
      <UpdatePrompt />
      <OwnerDevtools />
    </>
  );
}
