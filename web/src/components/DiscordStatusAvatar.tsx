import type { ReactNode } from "react";
import { devtools, parsePresencePreview, useDevtoolsValue } from "../devtools";
import { useStrings } from "../i18n";

//: Discord's own presence words, as catalogue keys.
const STATUS_KEYS: Record<string, string> = {
  online: "status.online",
  idle: "status.idle",
  dnd: "status.dnd",
  offline: "status.offline",
  streaming: "status.streaming",
};

//: The statuses Discord also draws phone-shaped when the phone holds the presence.
const MOBILE_STATUSES = new Set(["online", "idle", "dnd"]);

export function DiscordStatusAvatar({ status, mobile, className, children, label }: {
  status?: string | null;
  /** The member's presence comes from their phone, so the mobile icon is drawn. */
  mobile?: boolean;
  className: string;
  children: ReactNode;
  label?: string;
}) {
  const { t } = useStrings("shared");
  // The owner devtools can fake a presence for this tab, which repaints every
  // avatar at once — the point of the switch is to check the icons everywhere.
  const preview = parsePresencePreview(useDevtoolsValue(devtools.presencePreview));
  const normalizedStatus = status && Object.prototype.hasOwnProperty.call(STATUS_KEYS, status) ? status : "offline";
  const shownStatus = preview?.status ?? normalizedStatus;
  const statusName = t(STATUS_KEYS[shownStatus]);
  const mobileIcon = (preview ? preview.mobile : Boolean(mobile)) && MOBILE_STATUSES.has(shownStatus);
  return <span className={`discord-status-avatar ${className}-status-wrap${mobileIcon ? " is-mobile" : ""}`}>
    {/* The mask that cuts the status notch lives on this wrapper, so it takes
        the same bite out of the avatar and any decoration drawn around it. The
        inner span keeps both in the avatar's own box. */}
    <span className="discord-status-avatar-art">
      <span className="discord-status-avatar-art-inner">{children}</span>
    </span>
    <img
      className="discord-status-icon"
      src={`/assets/discord-status/status_${shownStatus}${mobileIcon ? "_mobile" : ""}.png`}
      alt={label || statusName}
      title={label || statusName}
    />
  </span>;
}
