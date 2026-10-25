import type { ReactNode } from "react";

export type SettingCardFlag = "premium" | "experimental";

/**
 * Shared toggle layout for guild settings tabs and dashboard panels: one card
 * per switch, in a responsive grid, so every tab reads the same way.
 *
 * The card's control stays a fixed-size flex item while the copy takes the
 * remaining room, which keeps switches aligned across a row no matter how long
 * the description wraps.
 */
export function SettingCards({
  children,
  className,
  stacked = false,
}: {
  children: ReactNode;
  className?: string;
  /** One card per row — for cards whose control is wider than a switch. */
  stacked?: boolean;
}) {
  return (
    <div className={["setting-cards", stacked ? "is-stacked" : "", className ?? ""].filter(Boolean).join(" ")}>
      {children}
    </div>
  );
}

export function SettingCard({
  title,
  hint,
  flags,
  locked = false,
  action,
  className,
}: {
  title: ReactNode;
  hint?: ReactNode;
  flags?: SettingCardFlag[];
  locked?: boolean;
  action: ReactNode;
  className?: string;
}) {
  return (
    <div className={["setting-card", locked ? "is-locked" : "", className ?? ""].filter(Boolean).join(" ")}>
      <div className="setting-card-copy">
        <div className="setting-card-title">
          <strong>{title}</strong>
          {flags?.map((flag) => (
            <em key={flag} className={flag === "premium" ? "setting-flag-premium" : "setting-flag-experimental"}>{flag}</em>
          ))}
        </div>
        {hint ? <small>{hint}</small> : null}
      </div>
      <div className="setting-card-control">{action}</div>
    </div>
  );
}
