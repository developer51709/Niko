import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { LanguageProvider } from "./i18n";
import "./styles.css";
import "./styles/guild-settings.css";
import "./styles/color-picker.css";
import "./styles/switch.css";
import "./styles/billing.css";
import "./styles/data-removal.css";
import "./styles/broadcast-studio.css";
import "./styles/staff-card.css";
import "./styles/discord-name-fonts.css";
import "./styles/devtools.css";
import "./styles/team-applications.css";
import "./styles/test-fonts.css";
import { installFontTester } from "./fontTester";

// Public on purpose: the typeface tester is for anyone with a console, not just
// an owner session, so it is installed before the app renders.
installFontTester();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    void navigator.serviceWorker.register("/service-worker.js").catch((error: unknown) => {
      console.warn("Niko app support could not be initialized.", error);
    });
  });
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <LanguageProvider>
      <App />
    </LanguageProvider>
  </StrictMode>,
);