// Pure helpers behind the live economy leaderboard, kept out of the component
// so the polling arithmetic is easy to reason about and check on its own.

export type RankedRow = { key: string; rank: number };

/** Index a page of standings by row key. */
export function rankMap(rows: RankedRow[]): Map<string, number> {
  const ranks = new Map<string, number>();
  for (const row of rows) ranks.set(row.key, row.rank);
  return ranks;
}

/**
 * Places each row gained since the previous poll.
 *
 * A positive number means the row climbed (its rank number went down), and a
 * negative number means it slipped. Rows seen for the first time, or that hold
 * their place, are omitted so the page only animates actual movement.
 */
export function rankChanges(previousRanks: Map<string, number>, rows: RankedRow[]): Record<string, number> {
  const changes: Record<string, number> = {};
  for (const row of rows) {
    const previous = previousRanks.get(row.key);
    if (previous === undefined || previous === row.rank) continue;
    changes[row.key] = previous - row.rank;
  }
  return changes;
}
