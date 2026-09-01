import { useEffect, useState } from "react";
import { CommandsPage } from "./pages/CommandsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DocsPage } from "./pages/DocsPage";
import { HomePage } from "./pages/HomePage";
import { LegalPage } from "./pages/LegalPage";
import { pageFromPath, type Page } from "./router";

export function App() {
  const [page, setPage] = useState<Page>(pageFromPath);
  useEffect(() => {
    const handle = () => setPage(pageFromPath());
    window.addEventListener("popstate", handle);
    return () => window.removeEventListener("popstate", handle);
  }, []);
  if (page === "commands") return <CommandsPage />;
  if (page === "docs") return <DocsPage />;
  if (page === "dashboard") return <DashboardPage />;
  if (page === "privacy") return <LegalPage type="privacy" />;
  if (page === "terms") return <LegalPage type="terms" />;
  return <HomePage />;
}