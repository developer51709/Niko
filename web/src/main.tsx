import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";
import "./styles/guild-settings.css";
import "./styles/color-picker.css";
import "./styles/switch.css";
import "./styles/billing.css";
import "./styles/data-removal.css";
import "./styles/broadcast-studio.css";
import "./styles/staff-card.css";
import "./styles/discord-name-fonts.css";

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    void navigator.serviceWorker.register("/service-worker.js").catch((error: unknown) => {
      console.warn("Niko app support could not be initialized.", error);
    });
  });
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);