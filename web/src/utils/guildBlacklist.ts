import { lockdownStaffGuild, setStaffGuildBlacklist } from "../api";
import type { LockdownStepResult, LockdownStepStatus } from "../types";
import { notifyError, notifyLoading, notifySuccess } from "./toast";

/**
 * The dashboard half of a guild blacklist.
 *
 * Blacklisting a server is not one write: the entry is saved, then each Niko
 * feature that server still uses is switched off and its owner is told. That
 * work is a sequence of independently-reported steps (`utils/guild_lockdown.py`
 * owns them) and this module drives it one request at a time so the person
 * doing it sees which feature is being paused — a single opaque request would
 * leave them watching a spinner and hide exactly which step failed.
 *
 * The step keys and wording are a contract with the Python module's
 * `LOCKDOWN_STEPS`; keep the two lists in the same order. A parity test guards
 * that (`tests/test_guild_lockdown.py`).
 */
export const LOCKDOWN_STEPS = [
  ["database", "Saving to database…"],
  ["social", "Pausing social notifs…"],
  ["starboard", "Disabling starboard…"],
  ["polls", "Disabling polls…"],
  ["giveaways", "Disabling giveaways…"],
  ["notification", "Sending blacklist notification…"],
] as const;

/** The steps the API runs; `database` is the blacklist write itself. */
export const LOCKDOWN_FEATURE_STEPS = LOCKDOWN_STEPS.filter(([key]) => key !== "database").map(([key]) => key);

export type GuildLockdownSummary = {
  guildId: string;
  guildName: string;
  steps: LockdownStepResult[];
};

export const LOCKDOWN_STATUS_LABELS: Record<LockdownStepStatus, string> = {
  done: "Paused",
  skipped: "Not in use",
  failed: "Failed",
};

/** Result buckets for the summary popup, in the order it shows them. */
export function groupLockdownSteps(steps: LockdownStepResult[]) {
  const pick = (status: LockdownStepStatus) => steps.filter((step) => step.status === status);
  return { paused: pick("done"), skipped: pick("skipped"), failed: pick("failed") };
}

/** One-line outcome for the completion toast. */
export function lockdownToastMessage(summary: GuildLockdownSummary) {
  const { paused, skipped, failed } = groupLockdownSteps(summary.steps);
  const parts = [
    paused.length ? `${paused.length} paused` : "",
    skipped.length ? `${skipped.length} skipped` : "",
    failed.length ? `${failed.length} failed` : "",
  ].filter(Boolean);
  return `${summary.guildName} blacklisted${parts.length ? ` · ${parts.join(" · ")}` : ""}.`;
}

/**
 * Blacklist one guild and pause its features, reporting each step.
 *
 * Returns `null` when the blacklist entry itself could not be saved: nothing was
 * paused in that case and the caller must not show a summary. Once the entry is
 * saved the flow always finishes — a feature that could not be switched off is
 * listed as failed in the summary while the server stays blacklisted.
 */
export async function blacklistGuildWithLockdown({
  guildId,
  guildName,
  reason,
  csrfToken,
  onStep,
}: {
  guildId: string;
  guildName: string;
  reason: string;
  csrfToken?: string;
  onStep?: (step: LockdownStepResult) => void;
}): Promise<GuildLockdownSummary | null> {
  const taskId = `staff-guild-lockdown-${guildId}`;
  const steps: LockdownStepResult[] = [];
  const record = (step: LockdownStepResult) => {
    steps.push(step);
    onStep?.(step);
  };

  const [databaseKey, databaseLabel] = LOCKDOWN_STEPS[0];
  notifyLoading(databaseLabel, taskId);
  try {
    await setStaffGuildBlacklist(guildId, "add", reason, csrfToken);
    record({ step: databaseKey, label: databaseLabel, status: "done", detail: "Blacklist entry saved." });
  } catch (error) {
    notifyError(error instanceof Error ? error.message : "The guild could not be blacklisted.", taskId);
    return null;
  }

  for (const [step] of LOCKDOWN_STEPS.slice(1)) {
    notifyLoading(LOCKDOWN_STEPS.find(([key]) => key === step)?.[1] || step, taskId);
    try {
      const result = await lockdownStaffGuild(guildId, step, csrfToken);
      record({ step: result.step, label: result.label, status: result.status, detail: result.detail });
    } catch (error) {
      record({
        step,
        label: LOCKDOWN_STEPS.find(([key]) => key === step)?.[1] || step,
        status: "failed",
        detail: error instanceof Error ? error.message : "This feature could not be paused.",
      });
    }
  }

  const summary = { guildId, guildName, steps };
  notifySuccess(lockdownToastMessage(summary), taskId);
  return summary;
}
