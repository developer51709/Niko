import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { LanguageProvider } from "../i18n";
import "../styles.css";
import "./activity.css";
import { ActivityApp } from "./ActivityApp";

// DiscordMarkdown reads shared strings, so the player needs the same language
// context the site provides around every page.
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <LanguageProvider>
      <ActivityApp />
    </LanguageProvider>
  </StrictMode>,
);
