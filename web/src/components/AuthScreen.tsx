import { useEffect, useRef, type ReactNode } from "react";
import { Icon } from "./Icon";
import { PublicHeader } from "./PublicHeader";
import { useStrings } from "../i18n";
import { publicPath } from "../router";
import { registerContextMenuExtras } from "../utils/contextMenu";

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
export function DiscordSignIn({ next, available = true, label, unavailableNotice }: { next: string; available?: boolean; label?: string; unavailableNotice?: ReactNode }) {
  const { t } = useStrings("shared");
  const linkRef = useRef<HTMLAnchorElement | null>(null);
  // ``next`` is written in the apex form like every other path here; on a
  // section host it is the short form that the visitor comes back to.
  const href = `/auth/login?next=${encodeURIComponent(publicPath(next))}`;

  // Discord's Canary and PTB builds keep sessions of their own, so a sign-in
  // started on one of them authorizes with the account that build is logged
  // into — the way a second account gets in without signing out of the first.
  // The rows sit on this button because they change the same sign-in; the build
  // is a parameter of the route, so the callback, the state and the way back
  // stay exactly as they are.
  useEffect(
    () =>
      registerContextMenuExtras((target) => {
        const anchor = target.closest("[data-discord-signin]");
        if (!anchor || anchor !== linkRef.current) return null;
        const begin = (client: string) => () => window.location.assign(`${href}&client=${client}`);
        return [
          { key: "discord-canary", label: t("auth.signInCanary"), icon: "external", action: begin("canary") },
          { key: "discord-ptb", label: t("auth.signInPtb"), icon: "external", action: begin("ptb") },
        ];
      }),
    [href, t],
  );

  if (!available) return <div className="notice warning">{unavailableNotice ?? t("auth.unavailable")}</div>;
  return <a ref={linkRef} data-discord-signin className="button button-primary full-width" href={href}>
    <Icon name="lock" /> {label ?? t("auth.continue")} <Icon name="arrow" />
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
