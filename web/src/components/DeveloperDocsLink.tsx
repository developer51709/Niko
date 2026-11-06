import type { MouseEvent, ReactNode } from "react";
import { navigate } from "../router";

/** A normal link that keeps developer-docs navigation inside the SPA. */
export function DeveloperDocsLink({
  to,
  className,
  children,
  title,
  ariaCurrent,
}: {
  to: string;
  className?: string;
  children: ReactNode;
  title?: string;
  ariaCurrent?: "page";
}) {
  const onClick = (event: MouseEvent<HTMLAnchorElement>) => {
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) return;
    event.preventDefault();
    navigate(to);
  };

  return (
    <a
      href={to}
      className={className}
      title={title}
      aria-current={ariaCurrent}
      onClick={onClick}
    >
      {children}
    </a>
  );
}
