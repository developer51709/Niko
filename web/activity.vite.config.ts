import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = path.dirname(fileURLToPath(import.meta.url));

/** Drop the site's hosted-font import: the Activity carries its own copies. */
function localFonts(): { name: string; enforce: "pre"; transform: (code: string, id: string) => string | undefined } {
  return {
    name: "niko-activity-local-fonts",
    enforce: "pre",
    transform(code, id) {
      if (!id.endsWith("/web/src/styles.css")) return undefined;
      return code.replace(/@import url\("https:\/\/fonts\.googleapis\.com[^"]*"\);\n?/, "");
    },
  };
}

/**
 * The Discord Activity is a second entry point, not a separate design system.
 *
 * It shares `web/src/styles.css` and the site's React components, but builds to
 * its own directory with `/activity/` as the base because Discord's URL mapping
 * serves the app from that prefix. The bot serves the built files from
 * `src/webapp/activity/dist`.
 */
export default defineConfig({
  root: webRoot,
  base: "/activity/",
  // The Activity reuses the site stylesheet and shared React components, but
  // not the public site's static assets. Copying `web/public` here would add
  // ~16 MB for files the panel never references.
  publicDir: false,
  plugins: [localFonts(), react()],
  build: {
    outDir: "../src/webapp/activity/dist",
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(webRoot, "activity/index.html"),
    },
  },
  server: { host: "0.0.0.0", port: 5001, allowedHosts: true },
});
