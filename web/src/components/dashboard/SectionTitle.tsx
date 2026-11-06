import type { ReactNode } from "react";
import { Icon } from "../Icon";

/**
 * The heading of one section inside a settings panel: a small kicker, the
 * section title, a line of explanation, and the section's icon on the right.
 *
 * Server settings and the social notifier both draw their sections this way, so
 * the shape lives here rather than being restated in each view. A section that
 * needs a compact control (refresh, status, or filter) can put it in `action`,
 * which takes the icon's place on the right.
 */
export function SectionTitle({
  label,
  title,
  detail,
  icon,
  action,
}: {
  label: string;
  title: string;
  detail?: string;
  icon?: string;
  action?: ReactNode;
}) {
  return <div className="panel-heading settings-section-title">
    <div><span className="panel-kicker">{label}</span><h3>{title}</h3>{detail && <p>{detail}</p>}</div>
    {action ?? (icon ? <span className="panel-icon"><Icon name={icon} /></span> : null)}
  </div>;
}
