import { useCallback, useEffect, useMemo, useState, type ReactElement } from "react";
import { getStaffMaintenance, setStaffMaintenance } from "../../api";
import type { StaffMaintenanceCog, StaffMaintenanceCommand, StaffMaintenanceResponse } from "../../types";
import { notifyError, notifyLoading, notifySuccess } from "../../utils/toast";
import { useStrings } from "../../i18n";

type Translate = (key: string, values?: Record<string, string | number>) => string;
import { Icon } from "../Icon";
import { Switch } from "./Switch";

const TOAST_KEY = "staff-maintenance";

function relativeTime(timestamp: number | null, t: Translate) {
  if (!timestamp) return "";
  const seconds = Math.max(0, Math.round(Date.now() / 1000 - timestamp));
  if (seconds < 60) return t("maintenance.justNow");
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return t("maintenance.minutesAgo", { count: minutes });
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return t("maintenance.hoursAgo", { count: hours });
  return t("maintenance.daysAgo", { count: Math.floor(hours / 24) });
}

type Apply = (kind: "cog" | "command", key: string, enabled: boolean, reason: string) => void;

/** One command row inside a cog card: switch plus its own optional reason. */
function CommandRow({
  command,
  draft,
  onDraft,
  onToggle,
  onSaveReason,
  busy,
}: {
  command: StaffMaintenanceCommand;
  draft: string;
  onDraft: (value: string) => void;
  onToggle: (enabled: boolean) => void;
  onSaveReason: () => void;
  busy: boolean;
}) {
  const { t } = useStrings("dashboard");
  const blockedByCog = command.maintenance && command.blocked_by !== command.name;
  const locked = blockedByCog;
  const reasonChanged = command.maintenance && !locked && draft.trim() !== (command.reason ?? "").trim();

  return (
    <div className={`maintenance-row${command.maintenance ? " is-paused" : ""}`}>
      <div className="maintenance-identity">
        <strong>/{command.name}</strong>
        {blockedByCog ? (
          <span className="maintenance-tag">{t("maintenance.pausedWithCog")}</span>
        ) : command.maintenance ? (
          <span className="maintenance-meta">
            {command.reason || t("maintenance.noReason")}
            {command.since ? t("maintenance.pausedSince", { time: relativeTime(command.since, t) }) : ""}
          </span>
        ) : null}
      </div>

      <div className="maintenance-controls">
        <label className="maintenance-reason-field">
          <input
            type="text"
            value={draft}
            maxLength={500}
            placeholder={t("maintenance.reasonPlaceholder")}
            aria-label={t("maintenance.reasonAria", { name: command.name })}
            disabled={busy || locked}
            onChange={(event) => onDraft(event.target.value)}
          />
          {reasonChanged && (
            <button type="button" className="button button-small button-muted" disabled={busy} onClick={onSaveReason}>
              {t("maintenance.saveReason")}
            </button>
          )}
        </label>
        <Switch
          size="sm"
          checked={command.maintenance}
          disabled={busy || locked}            aria-label={t(command.maintenance ? "maintenance.resumeCommand" : "maintenance.pauseCommand", { name: command.name })}
          onCheckedChange={onToggle}
        />
      </div>
    </div>
  );
}

/** A cog as a collapsible card, with the cog-level switch in its header. */
function CogCard({
  cog,
  commands,
  busyKey,
  draft,
  onDraft,
  apply,
  forceOpen,
  renderCommand,
}: {
  cog: StaffMaintenanceCog;
  commands: StaffMaintenanceCommand[];
  busyKey: string | null;
  draft: string;
  onDraft: (value: string) => void;
  apply: Apply;
  forceOpen: boolean;
  renderCommand: (command: StaffMaintenanceCommand) => ReactElement;
}) {
  const { t } = useStrings("dashboard");
  // A paused cog opens itself, and a search that matched one of its commands
  // expands the card so the hit is visible without another click.
  const [open, setOpen] = useState(cog.maintenance);
  useEffect(() => {
    if (forceOpen) setOpen(true);
  }, [forceOpen]);

  const panelId = `maintenance-panel-${cog.name.replace(/\./g, "-")}`;
  const locked = cog.declared || cog.state === "failed" || cog.state === "disabled";
  const note = cog.declared
    ? t("maintenance.setInCode")
    : cog.state === "failed"
      ? t("maintenance.failedToLoad")
      : cog.state === "disabled"
        ? t("maintenance.disabledInCode")
        : null;
  const busy = busyKey === cog.name;
  const pausedCommands = commands.filter((command) => command.maintenance).length;
  const reasonChanged = cog.maintenance && !locked && draft.trim() !== (cog.reason ?? "").trim();

  return (
    <article className={`maintenance-cog-card${open ? " is-open" : ""}${cog.maintenance ? " is-paused" : ""}`}>
      <header className="maintenance-cog-header">
        <button
          type="button"
          className="maintenance-cog-toggle"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen((current) => !current)}
        >
          <span className="maintenance-cog-caret" aria-hidden="true" />
          <span className="maintenance-cog-title">
            <strong>{cog.label}</strong>
            <small>{t(cog.commands === 1 ? "maintenance.commandCountOne" : "maintenance.commandCountMany", { count: cog.commands })} · {cog.name}</small>
            {cog.maintenance && cog.reason && <span className="maintenance-cog-reason" title={cog.reason}>{cog.reason}</span>}
          </span>
          {cog.maintenance && <span className="maintenance-cog-state">{t("maintenance.badge")}</span>}
          {note && <span className="maintenance-cog-state is-quiet" title={note}>{note}</span>}
        </button>

        <div className="maintenance-cog-controls">
          <label className="maintenance-reason-field">
            <input
              type="text"
              value={draft}
              maxLength={500}
              placeholder={t("maintenance.cogReasonPlaceholder")}
              aria-label={t("maintenance.cogReasonAria", { name: cog.label })}
              disabled={busy || locked}
              onChange={(event) => onDraft(event.target.value)}
            />
            {reasonChanged && (
              <button type="button" className="button button-small button-muted" disabled={busy} onClick={() => apply("cog", cog.name, true, draft)}>
                {t("maintenance.saveReason")}
              </button>
            )}
          </label>
          <Switch
            size="sm"
            checked={cog.maintenance}
            disabled={busy || locked}
            aria-label={t(cog.maintenance ? "maintenance.resumeCog" : "maintenance.pauseCog", { name: cog.label })}
            onCheckedChange={(enabled) => apply("cog", cog.name, enabled, draft)}
          />
        </div>
      </header>

      {open && (
        <div className="maintenance-cog-body" id={panelId}>
          <p className="maintenance-cog-summary">
            {locked && note
              ? t("maintenance.lockedNote", { note })
              : cog.maintenance
                ? t(cog.reason ? "maintenance.cogPausedWithReason" : "maintenance.cogPaused", { reason: cog.reason || "" })
                : pausedCommands
                  ? t("maintenance.commandsPaused", { paused: pausedCommands, total: commands.length })
                  : t("maintenance.allAvailable")}
          </p>
          {commands.length === 0
            ? <p className="maintenance-empty">{t("maintenance.noCommands")}</p>
            : commands.map((command) => renderCommand(command))}
        </div>
      )}
    </article>
  );
}

export function MaintenanceView({ csrfToken }: { csrfToken?: string }) {
  const { t } = useStrings("dashboard");
  const [data, setData] = useState<StaffMaintenanceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [query, setQuery] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setData(await getStaffMaintenance());
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : t("maintenance.loadFailed"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const cogs = data?.cogs ?? [];
  const commands = data?.commands ?? [];

  const pausedCogs = cogs.filter((cog) => cog.maintenance).length;
  const pausedCommands = commands.filter((command) => command.maintenance && command.blocked_by === command.name).length;

  const apply = async (kind: "cog" | "command", key: string, enabled: boolean, reason: string) => {
    if (!data) return;
    setBusyKey(key);
    notifyLoading(t(enabled ? "maintenance.pausing" : "maintenance.resuming"), TOAST_KEY);
    try {
      const next = await setStaffMaintenance({ kind, key, enabled, reason }, csrfToken);
      setData(next);
      setDrafts((current) => {
        const updated = { ...current };
        delete updated[key];
        return updated;
      });
      notifySuccess(
        t(enabled ? "maintenance.nowPaused" : "maintenance.nowAvailable", { key }),
        TOAST_KEY,
      );
    } catch (reason) {
      notifyError(reason instanceof Error ? reason.message : t("maintenance.saveFailed"), TOAST_KEY);
    } finally {
      setBusyKey(null);
    }
  };

  const term = query.trim().toLowerCase();

  // Commands are grouped under the cog that owns them, so every switch sits on
  // the card it belongs to instead of in a second, parallel list.
  const cards = useMemo(() => {
    const grouped = new Map<string, StaffMaintenanceCommand[]>();
    for (const command of commands) {
      if (!command.cog) continue;
      const list = grouped.get(command.cog);
      if (list) list.push(command);
      else grouped.set(command.cog, [command]);
    }
    return cogs.map((cog) => {
      const own = grouped.get(cog.name) ?? [];
      const cogMatches = !term || `${cog.label} ${cog.name} ${cog.reason ?? ""}`.toLowerCase().includes(term);
      const matching = cogMatches ? own : own.filter((command) => `${command.name} ${command.reason ?? ""}`.toLowerCase().includes(term));
      return { cog, commands: matching, visible: cogMatches || matching.length > 0, forceOpen: Boolean(term) && !cogMatches && matching.length > 0 };
    });
  }, [cogs, commands, term]);

  const visibleCards = cards.filter((card) => card.visible);
  const looseCommands = useMemo(
    () => commands.filter((command) => !command.cog && (!term || `${command.name} ${command.reason ?? ""}`.toLowerCase().includes(term))),
    [commands, term],
  );

  const renderCommand = (command: StaffMaintenanceCommand) => (
    <CommandRow
      key={command.name}
      command={command}
      draft={drafts[command.name] ?? (command.maintenance && command.blocked_by === command.name ? command.reason ?? "" : "")}
      busy={busyKey === command.name}
      onDraft={(value) => setDrafts((current) => ({ ...current, [command.name]: value }))}
      onToggle={(enabled) => void apply("command", command.name, enabled, drafts[command.name] ?? command.reason ?? "")}
      onSaveReason={() => void apply("command", command.name, true, drafts[command.name] ?? "")}
    />
  );

  return (
    <div className="maintenance-view">
      <header className="staff-guilds-heading">
        <div>
          <span className="panel-kicker">{t("maintenance.kicker")}</span>
          <h2>{t("maintenance.title")}</h2>
          <p>
            {t("maintenance.text")}
          </p>
        </div>
        <div className={`maintenance-badge${pausedCogs + pausedCommands ? " is-on" : ""}`}>
          <i />
          <span>
            <small>{t("maintenance.pausedBadge")}</small>
            <strong>
              {pausedCogs + pausedCommands
                ? [
                  pausedCogs ? t(pausedCogs === 1 ? "maintenance.cogCountOne" : "maintenance.cogCountMany", { count: pausedCogs }) : "",
                  pausedCommands ? t(pausedCommands === 1 ? "maintenance.commandCountOneLabel" : "maintenance.commandCountManyLabel", { count: pausedCommands }) : "",
                ].filter(Boolean).join(" · ")
                : t("maintenance.everythingLive")}
            </strong>
          </span>
        </div>
      </header>

      {error && <div className="notice warning" role="status">{error}</div>}

      <div className="maintenance-toolbar">
        <label className="staff-guild-search">
          <Icon name="search" />
          <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t("maintenance.searchPlaceholder")} aria-label={t("maintenance.searchAria")} />
        </label>
        <button type="button" className="button button-muted button-small" disabled={loading} onClick={() => void load()}>
          <Icon name="refresh" />{t(loading ? "maintenance.refreshing" : "maintenance.refresh")}
        </button>
      </div>

      {loading && !data ? (
        <div className="staff-guild-empty"><div className="loading-ring" /><p>{t("maintenance.loading")}</p></div>
      ) : visibleCards.length === 0 && looseCommands.length === 0 ? (
        <div className="staff-guild-empty">{t("maintenance.noMatches")}</div>
      ) : (
        <div className="maintenance-cards">
          {visibleCards.map(({ cog, commands: own, forceOpen }) => (
            <CogCard
              key={cog.name}
              cog={cog}
              commands={own}
              busyKey={busyKey}
              draft={drafts[cog.name] ?? cog.reason ?? ""}
              onDraft={(value) => setDrafts((current) => ({ ...current, [cog.name]: value }))}
              apply={(kind, key, enabled, reason) => void apply(kind, key, enabled, reason)}
              forceOpen={forceOpen}
              renderCommand={renderCommand}
            />
          ))}

          {looseCommands.length > 0 && (
            <article className="maintenance-cog-card is-open">
              <header className="maintenance-cog-header">
                <div className="maintenance-cog-toggle is-static">
                  <span className="maintenance-cog-caret is-static" aria-hidden="true" />
                  <span className="maintenance-cog-title">
                    <strong>{t("maintenance.otherCommands")}</strong>
                    <small>{t(looseCommands.length === 1 ? "maintenance.looseOne" : "maintenance.looseMany", { count: looseCommands.length })}</small>
                  </span>
                </div>
              </header>
              <div className="maintenance-cog-body">
                {looseCommands.map((command) => renderCommand(command))}
              </div>
            </article>
          )}
        </div>
      )}

      <p className="maintenance-note">
        A paused command never reaches its own checks, cooldowns, or usage counters, and a paused cog takes every
        command in it with it. Toggles are written to the bot's database immediately, so a restart or a redeploy
        keeps them exactly where you left them.
      </p>
    </div>
  );
}
