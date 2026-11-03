import type { ReactNode } from "react";
import { Icon } from "./Icon";
import { PublicHeader } from "./PublicHeader";

type BackLink = {
  label: ReactNode;
  onClick?: () => void;
  href?: string;
  external?: boolean;
};

/**
 * Where a signed-out visitor should be sent back to after signing in.
 * Every sign-in prompt goes through `DiscordSignIn`, so the CTA and its
 * fallback notice look the same on every page.
 */
export function DiscordSignIn({ next, available = true, label = "Continue with Discord", unavailableNotice }: { next: string; available?: boolean; label?: string; unavailableNotice?: ReactNode }) {
  if (!available) return <div className="notice warning">{unavailableNotice ?? "Discord sign-in isn’t available right now. Try again later."}</div>;
  return <a className="button button-primary full-width" href={`/auth/login?next=${encodeURIComponent(next)}`}>
    <Icon name="lock" /> {label} <Icon name="arrow" />
  </a>;
}

/** The quiet link that sits under every card's primary action. */
export function AuthBackLink({ label, onClick, href, external = false }: BackLink) {
  if (href) {
    return <a className="back-link" href={href} onClick={onClick} {...(external ? { target: "_blank", rel: "noreferrer" } : {})}>{label}</a>;
  }
  return <button type="button" className="back-link" onClick={onClick}>{label}</button>;
}

/**
 * The one layout behind every signed-out and access-denied screen: a centred
 * card on the dashboard header, with the brand mark, an eyebrow, a heading and
 * a full-width primary action. Pages only supply their own copy and actions, so
 * spacing, type and buttons stay identical across the dashboard, staff pages and
 * restriction notices.
 */
export function AuthScreen({
  mark = "n",
  markClassName = "auth-mark",
  eyebrow,
  title,
  description,
  children,
  back,
  header = true,
  role,
  pageClassName,
  cardClassName,
}: {
  mark?: ReactNode;
  markClassName?: string;
  eyebrow: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  back?: BackLink;
  header?: boolean;
  role?: "alert";
  pageClassName?: string;
  cardClassName?: string;
}) {
  return <>
    {header && <PublicHeader page="dashboard" />}
    <div className={`auth-page${pageClassName ? ` ${pageClassName}` : ""}`}>
      <section className={`auth-card${cardClassName ? ` ${cardClassName}` : ""}`} role={role}>
        <span className={markClassName}>{mark}</span>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {description !== undefined && <p>{description}</p>}
        {children}
        {back && <AuthBackLink {...back} />}
      </section>
    </div>
  </>;
}
