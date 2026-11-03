import type { ReactNode } from "react";
import { useStrings } from "../i18n";

//: Discord's own presence words, as catalogue keys.
const STATUS_KEYS: Record<string, string> = {
  online: "status.online",
  idle: "status.idle",
  dnd: "status.dnd",
  offline: "status.offline",
  streaming: "status.streaming",
};

export function DiscordStatusAvatar({ status, className, children, label }: {
  status?: string | null;
  className: string;
  children: ReactNode;
  label?: string;
}) {
  const { t } = useStrings("shared");
  const normalizedStatus = status && Object.prototype.hasOwnProperty.call(STATUS_KEYS, status) ? status : "offline";
  const statusName = t(STATUS_KEYS[normalizedStatus]);
  return <span className={`discord-status-avatar ${className}-status-wrap`}>
    {children}
    <img className="discord-status-icon" src={`/assets/discord-status/status_${normalizedStatus}.png`} alt={label || statusName} title={label || statusName} />
  </span>;
}
