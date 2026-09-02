import type { User } from "../../types";
import { initials } from "../../utils/format";

export function UserAvatar({ user, className = "avatar" }: { user: User; className?: string }) {
  const avatarUrl = user.avatar
    ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.${user.avatar.startsWith("a_") ? "gif" : "png"}?size=64`
    : null;

  return <span className={className} aria-hidden="true">
    {avatarUrl ? <img src={avatarUrl} alt="" /> : initials(user.global_name || user.username || "Niko")}
  </span>;
}

export function MemberAvatar({ name, avatarUrl, className = "member-avatar" }: { name: string; avatarUrl?: string | null; className?: string }) {
  return <span className={className} aria-hidden="true">
    {avatarUrl ? <img src={avatarUrl} alt="" /> : initials(name)}
  </span>;
}