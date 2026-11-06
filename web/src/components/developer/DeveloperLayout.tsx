import type { ReactNode } from "react";
import { DashHeading } from "../dashboard/DashboardViews";
import { SettingCard, SettingCards } from "../dashboard/SettingCards";
import { Switch } from "../dashboard/Switch";
import type { DeveloperScope } from "../../types";

/**
 * The shared frame for every developer portal tab. It uses the same dashboard
 * heading and settings stack as the guild settings pages, so the portal lands
 * in the same rhythm as the rest of the authenticated product.
 */
export function DeveloperPage({
  eyebrow,
  title,
  text,
  actions,
  children,
}: {
  eyebrow: string;
  title: string;
  text: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <>
      <header className="developer-page-heading">
        <DashHeading eyebrow={eyebrow} title={title} text={text} />
        {actions ? <div className="developer-page-actions">{actions}</div> : null}
      </header>
      <div className="settings-stack guild-feature-settings developer-settings-stack">{children}</div>
    </>
  );
}

/** Scope selection built from the same setting cards and switches as guild settings. */
export function DeveloperScopePicker({
  scopes,
  selected,
  onToggle,
  disabled = false,
}: {
  scopes: DeveloperScope[];
  selected: string[];
  onToggle: (scope: string) => void;
  disabled?: boolean;
}) {
  return (
    <SettingCards className="developer-scope-picker">
      {scopes.map((scope) => (
        <SettingCard
          key={scope.key}
          title={
            <>
              {scope.label}
              {scope.sensitive ? <em className="developer-scope-badge">Sensitive</em> : null}
              {scope.restricted ? <em className="developer-scope-badge is-restricted">Owner only</em> : null}
            </>
          }
          hint={scope.description}
          action={
            <Switch
              size="sm"
              checked={selected.includes(scope.key)}
              onCheckedChange={() => onToggle(scope.key)}
              disabled={disabled}
              aria-label={`${scope.label} permission`}
            />
          }
        />
      ))}
    </SettingCards>
  );
}

/** Read-only scope list for overview panels. */
export function DeveloperScopeSummary({ scopes }: { scopes: DeveloperScope[] }) {
  if (scopes.length === 0) return <div className="empty-state">No scopes have been granted yet.</div>;
  return (
    <SettingCards className="developer-scope-summary">
      {scopes.map((scope) => (
        <SettingCard
          key={scope.key}
          title={<code>{scope.key}</code>}
          hint={scope.description}
          action={<span className="developer-scope-granted">Granted</span>}
        />
      ))}
    </SettingCards>
  );
}
