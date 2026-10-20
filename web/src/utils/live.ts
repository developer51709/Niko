// Shared wording for the live-updating surfaces (economy leaderboard, guild
// analytics), so a synced board says the same thing everywhere.

/** Relative "synced N seconds ago" label for a live badge. */
export function syncedLabel(lastSync: number | null, now: number): string {
  if (!lastSync) return "Waiting for the first standings";
  const seconds = Math.max(0, Math.round((now - lastSync) / 1000));
  if (seconds < 2) return "Synced just now";
  if (seconds < 60) return `Synced ${seconds}s ago`;
  return `Synced ${Math.round(seconds / 60)}m ago`;
}
