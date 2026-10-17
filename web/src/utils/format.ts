export function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    notation: value > 9999 ? "compact" : "standard",
  }).format(value);
}

export function displayName(user?: { global_name?: string; username?: string } | null) {
  return user?.global_name || user?.username || "there";
}

export function initials(name: string) {
  return name.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
}