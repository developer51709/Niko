import type { CSSProperties } from "react";
import { Toaster } from "react-hot-toast";

/**
 * The one place success and failure feedback appears.
 *
 * Mounted once from `App`, so every dashboard tab — and every public page —
 * reports results through the same stack instead of each card printing its own
 * status line.
 *
 * The look is inline rather than in a stylesheet on purpose: react-hot-toast
 * appends its portal to `<body>`, outside `.dashboard-layout`, where the
 * dashboard's own theme variables are redefined. Reading the root tokens here
 * keeps the toasts on the same palette and lets them follow the light/dark
 * theme with the rest of the page.
 */
const baseToastStyle: CSSProperties = {
  maxWidth: "min(420px, calc(100vw - 32px))",
  padding: "12px 14px",
  color: "var(--ink)",
  background: "var(--surface-raised)",
  backdropFilter: "blur(10px)",
  borderColor: "var(--line)",
  borderStyle: "solid",
  borderWidth: "1px 1px 1px 2px",
  borderLeftColor: "var(--sage)",
  borderRadius: "10px",
  boxShadow: "var(--shadow)",
  fontSize: "12px",
  lineHeight: 1.6,
  textAlign: "left",
};

export function ToastHost() {
  return (
    <Toaster
      position="top-right"
      gutter={10}
      containerClassName="niko-toast-stack"
      toastOptions={{
        duration: 4000,
        className: "niko-toast",
        style: baseToastStyle,
        success: {
          className: "niko-toast niko-toast-success",
          // A save confirmation is read once and dismissed, so it needs less
          // time on screen than a failure the reader has to act on.
          duration: 3200,
          iconTheme: { primary: "#8bd5b1", secondary: "#0f1113" },
          style: { borderLeftColor: "var(--sage)" },
        },
        error: {
          className: "niko-toast niko-toast-error",
          duration: 6500,
          iconTheme: { primary: "#d0786c", secondary: "#0f1113" },
          style: { borderLeftColor: "#d0786c" },
        },
        loading: {
          className: "niko-toast niko-toast-loading",
          iconTheme: { primary: "var(--accent-dark)", secondary: "var(--line)" },
        },
      }}
    />
  );
}
