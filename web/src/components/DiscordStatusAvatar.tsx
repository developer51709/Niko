import type { ReactNode } from "react";

const STATUS_NAMES: Record<string, string> = {
  online: "Online",
  idle: "Idle",
  dnd: "Do Not Disturb",
  offline: "Offline",
  streaming: "Streaming",
};

export function DiscordStatusAvatar({ status, className, children, label }: {
  status?: string | null;
  className: string;
  children: ReactNode;
  label?: string;
}) {
  const normalizedStatus = status && Object.prototype.hasOwnProperty.call(STATUS_NAMES, status) ? status : "offline";
  const statusName = STATUS_NAMES[normalizedStatus];
  return <span className={`discord-status-avatar ${className}-status-wrap`}>
    {children}
    <img className="discord-status-icon" src={`/assets/discord-status/status_${normalizedStatus}.png`} alt={label || statusName} title={label || statusName} />
  </span>;
}
