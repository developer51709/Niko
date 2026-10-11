import { useEffect, useState } from "react";
import { Particles } from "./components/Particles";
import PixelSnow from "./components/PixelSnow";
import { CommandsPage } from "./pages/CommandsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DocsPage, DocsSlugPage } from "./pages/DocsPage";
import { HomePage } from "./pages/HomePage";
import { DonatePage } from "./pages/DonatePage";
import { LegalPage } from "./pages/LegalPage";
import { TranscriptPage } from "./pages/TranscriptPage";
import { ChangelogPage } from "./pages/ChangelogPage";
import { ChangelogSlugPage } from "./pages/ChangelogSlugPage";
import { TeamPage, TeamMemberPage } from "./pages/TeamPage";
import { StaffDashboardPage } from "./pages/StaffDashboardPage";
import { BlacklistAppealPage } from "./pages/BlacklistAppealPage";
import { StaffApplicationPage } from "./pages/StaffApplicationPage";
import { DiscordRedirectPage, SupportPage } from "./pages/SupportPage";
import { pageFromPath, type Page } from "./router";

export function App() {
  const [page, setPage] = useState<Page>(pageFromPath);
  useEffect(() => {
    const handle = () => setPage(pageFromPath());
    window.addEventListener("popstate", handle);
    return () => window.removeEventListener("popstate", handle);
  }, []);

  let pageContent;
  if (page === "commands") pageContent = <CommandsPage />;
  else if (page === "docs-detail") {
    const pathParts = window.location.pathname.split("/");
    pageContent = <DocsSlugPage slug={pathParts[pathParts.length - 1]} />;
  } else if (page === "docs") pageContent = <DocsPage />;
  else if (page === "staff") pageContent = <StaffDashboardPage />;
  else if (page === "appeal") pageContent = <BlacklistAppealPage />;
  else if (page === "application") pageContent = <StaffApplicationPage />;
  else if (page === "dashboard") pageContent = <DashboardPage />;
  else if (page === "team") pageContent = <TeamPage />;
  else if (page === "team-member") pageContent = <TeamMemberPage id={window.location.pathname.split("/").filter(Boolean)[1] || ""} />;
  else if (page === "support") pageContent = <SupportPage />;
  else if (page === "discord") pageContent = <DiscordRedirectPage />;
  else if (page === "privacy") pageContent = <LegalPage type="privacy" />;
  else if (page === "terms") pageContent = <LegalPage type="terms" />;
  else if (page === "community") pageContent = <LegalPage type="community" />;
  else if (page === "donate") pageContent = <DonatePage />;
  else if (page === "transcript") {
    const pathParts = window.location.pathname.split("/").filter(Boolean);
    pageContent = <TranscriptPage transcriptId={pathParts[1] || ""} />;
  } else if (page === "changelog") pageContent = <ChangelogPage />;
  else if (page === "changelog-detail") {
    const pathParts = window.location.pathname.split("/");
    pageContent = <ChangelogSlugPage slug={pathParts[pathParts.length - 1]} />;
  } else pageContent = <HomePage />;

  const now = new Date();
  const isHolidaySeason = now.getMonth() === 11 || (now.getMonth() === 0 && now.getDate() <= 2);

  return (
    <>
      <div className="site-ambient" aria-hidden="true">
        {isHolidaySeason ? (
          <PixelSnow color="#ffffff" variant="snowflake" density={0.5} speed={1} wind={0.25} flakeSize={1} pixelSize={3} glow={0.8} mouseInteraction={false} opacity={1} intro lightMode={false} />
        ) : (
          <Particles particleColors={["#ffffff"]} particleCount={200} particleSpread={10} speed={0.1} particleBaseSize={100} moveParticlesOnHover={false} alphaParticles={false} disableRotation={false} pixelRatio={1} />
        )}
      </div>
      <div className="site-content">{pageContent}</div>
    </>
  );
}
