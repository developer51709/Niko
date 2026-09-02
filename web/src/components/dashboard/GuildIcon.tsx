import type { Guild } from "../../types";

export function GuildIcon({ guild, className = "guild-avatar" }: { guild: Guild; className?: string }) {
  return <span className={className} aria-hidden="true">
    {guild.icon_url ? <img src={guild.icon_url} alt="" /> : guild.name.slice(0, 1).toUpperCase()}
  </span>;
}