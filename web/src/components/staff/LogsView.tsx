import { memo, useEffect, useMemo, useRef, useState } from "react";
import { getOwnerLogs } from "../../api";
import { useStrings } from "../../i18n";
import type { OwnerLogEntry } from "../../types";
import { Select, selectOptions } from "../dashboard/Select";
import { Switch } from "../dashboard/Switch";

/**
 * The owner's live view of every process's console.
 *
 * The supervisor and each child keep independent append-only files, split by
 * level (see ``log_store.LogArchive``), so a busy bot can never roll the
 * dashboard's lines out and a DEBUG flood can never roll the ERROR lines away.
 * This page polls for the lines appended since its cursor in the process and
 * level it is showing. Nothing is re-rendered here: the ANSI codes the terminal
 * would draw are parsed into coloured spans, so a line looks the same in the
 * browser as it does on the host.
 *
 * The level menu selects a minimum: the archive is asked for that level's
 * buffer and every more severe one, so the bot's own console level stays
 * whatever the deployment configured while an owner can still read DEBUG lines
 * the terminal is hiding.
 */

const POLL_MS = 1200;

/**
 * Mirrors the bot's rings (see ``LogBufferHandler``): the bot's own lines get
 * 5,000 rows, each noisy library gets 2,000 of its own. Capping per source is
 * what stops a pymongo/urllib3 burst from pushing visible lines out here too.
 */
const SOURCE_LIMITS: Record<string, number> = { main: 5000, pymongo: 2000, urllib3: 2000, wavelink: 2000 };

/** The thresholds the bot logs at; unknown levels fall back to INFO. */
const LEVEL_WEIGHT: Record<string, number> = {
  DEBUG: 10,
  INFO: 20,
  SUCCESS: 25,
  WARNING: 30,
  ERROR: 40,
  CRITICAL: 50,
};

/** A library logger and all of its children (``pymongo.command``, ``urllib3.connectionpool``). */
const isLibraryLogger = (name: string | undefined, library: string) =>
  name === library || Boolean(name?.startsWith(`${library}.`));

/** The ring an entry came from, inferred for entries served before `source` existed. */
const sourceOf = (entry: OwnerLogEntry): string => {
  if (entry.source) return entry.source;
  if (isLibraryLogger(entry.logger, "pymongo")) return "pymongo";
  if (isLibraryLogger(entry.logger, "urllib3")) return "urllib3";
  if (isLibraryLogger(entry.logger, "wavelink")) return "wavelink";
  return "main";
};

/** Keep the newest rows of each ring, leaving the others untouched. */
const capBySource = (entries: OwnerLogEntry[]): OwnerLogEntry[] => {
  const counts: Record<string, number> = {};
  const kept: OwnerLogEntry[] = [];
  for (let index = entries.length - 1; index >= 0; index -= 1) {
    const entry = entries[index];
    const source = sourceOf(entry);
    const limit = SOURCE_LIMITS[source] ?? SOURCE_LIMITS.main;
    const count = counts[source] ?? 0;
    if (count >= limit) continue;
    counts[source] = count + 1;
    kept.push(entry);
  }
  return kept.reverse();
};

const PROCESS_VALUES = ["all", "supervisor", "db", "web", "bot"] as const;

const LEVELS = selectOptions([
  ["DEBUG", "DEBUG"],
  ["INFO", "INFO"],
  ["SUCCESS", "SUCCESS"],
  ["WARNING", "WARNING"],
  ["ERROR", "ERROR"],
]);

type Segment = { text: string; color?: string; bold?: boolean; dim?: boolean };

// The palette the console draws with. Bright variants are provided for the
// bold ANSI colours some messages use; anything unknown keeps the console ink.
const ANSI_COLORS: Record<number, string> = {
  30: "#3f444d",
  31: "#ff6b6b",
  32: "#7bd88f",
  33: "#f2cc60",
  34: "#82aaff",
  35: "#c792ea",
  36: "#5ad4e6",
  37: "#d7dae0",
  90: "#697386",
  91: "#ff8787",
  92: "#9be6a9",
  93: "#ffe08a",
  94: "#a3beff",
  95: "#d8a8ff",
  96: "#7fe6f2",
  97: "#ffffff",
};

/** An xterm-256 colour, for messages that use the extended SGR form. */
function xtermColor(index: number): string | undefined {
  if (index < 16) return ANSI_COLORS[index < 8 ? 30 + index : 82 + index];
  if (index >= 232) {
    const level = 8 + (index - 232) * 10;
    return `rgb(${level}, ${level}, ${level})`;
  }
  const value = index - 16;
  const steps = [0, 95, 135, 175, 215, 255];
  const r = steps[Math.floor(value / 36) % 6];
  const g = steps[Math.floor(value / 6) % 6];
  const b = steps[value % 6];
  return `rgb(${r}, ${g}, ${b})`;
}

/**
 * Split one ANSI line into coloured runs.
 *
 * Only SGR sequences matter here: the bot's console formatter uses colour,
 * bright, dim and reset, and messages occasionally carry their own codes. Any
 * other escape is dropped rather than printed, so a broken sequence can never
 * leave `\x1b[0m` visible in the console.
 */
export function ansiSegments(line: string): Segment[] {
  const segments: Segment[] = [];
  let color: string | undefined;
  let bold = false;
  let dim = false;
  let start = 0;

  const push = (text: string) => {
    // Any escape that is not an SGR colour (cursor moves, erases) has no
    // meaning in a browser; drop it instead of printing it as mojibake.
    const clean = text.replace(/\x1b\[[0-9;?]*[ -/]*[@-~]/g, "");
    if (clean) segments.push({ text: clean, color, bold, dim });
  };

  const escape = /\x1b\[([0-9;]*)m/g;
  let match: RegExpExecArray | null;
  while ((match = escape.exec(line)) !== null) {
    push(line.slice(start, match.index));
    const codes = match[1] ? match[1].split(";").map(Number) : [0];
    for (let index = 0; index < codes.length; index += 1) {
      const code = codes[index];
      if (code === 0) {
        color = undefined;
        bold = false;
        dim = false;
      } else if (code === 1) {
        bold = true;
      } else if (code === 2) {
        dim = true;
      } else if (code === 22) {
        bold = false;
        dim = false;
      } else if (code === 39) {
        color = undefined;
      } else if (ANSI_COLORS[code]) {
        color = ANSI_COLORS[code];
      } else if (code === 38 && codes[index + 1] === 5) {
        color = xtermColor(codes[index + 2] ?? 0) ?? color;
        index += 2;
      } else if (code === 38 && codes[index + 1] === 2) {
        color = `rgb(${codes[index + 2] ?? 0}, ${codes[index + 3] ?? 0}, ${codes[index + 4] ?? 0})`;
        index += 4;
      }
    }
    start = escape.lastIndex;
  }
  push(line.slice(start));
  return segments.length ? segments : [{ text: line }];
}

/**
 * One console row.
 *
 * Kept memoised by line id: a poll appends a handful of lines, and re-parsing
 * the two thousand rows above them on every tick would make a quiet console
 * feel busy.
 */
const LogLine = memo(function LogLine({ entry }: { entry: OwnerLogEntry }) {
  const segments = useMemo(() => ansiSegments(entry.line), [entry.line]);
  return (
    <div className="bot-log-line" data-level={entry.level}>
      {segments.map((segment, index) => (
        <span
          key={index}
          style={{
            color: segment.color,
            fontWeight: segment.bold ? 700 : undefined,
            opacity: segment.dim ? 0.65 : undefined,
          }}
        >
          {segment.text}
        </span>
      ))}
    </div>
  );
});

export function LogsView() {
  const { t } = useStrings("staff");
  const [entries, setEntries] = useState<OwnerLogEntry[]>([]);
  const [level, setLevel] = useState("INFO");
  const [process, setProcess] = useState("all");
  const processOptions = useMemo(
    () => selectOptions(PROCESS_VALUES.map((value) => {
      if (value === "all") return [value, t("logs.processAll")];
      if (value === "supervisor") return [value, t("logs.processSupervisor")];
      if (value === "db") return [value, t("logs.processDatabase")];
      if (value === "web") return [value, t("logs.processDashboard")];
      return [value, t("logs.processBot")];
    })),
    [t],
  );
  // MongoDB logs every operation at DEBUG, which buries the bot's own debug
  // lines. Start quiet; the switch is there when the database is the suspect.
  const [hidePymongo, setHidePymongo] = useState(true);
  // urllib3 logs every connection and retry at DEBUG; the production host
  // makes enough requests for those lines to crowd out the bot's own output.
  const [hideUrllib3, setHideUrllib3] = useState(true);
  // Wavelink's player/node lifecycle chatter is intermittent but still noise
  // when the owner is trying to follow the bot's own debug lines.
  const [hideWavelink, setHideWavelink] = useState(true);
  const [capacity, setCapacity] = useState(0);
  const [unavailable, setUnavailable] = useState(false);
  const [truncated, setTruncated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pinned, setPinned] = useState(true);
  const cursorRef = useRef("");
  const tokenRef = useRef("");
  const scrollerRef = useRef<HTMLDivElement>(null);
  // A poll can take longer than the interval; without this guard two reads
  // would race for the same cursor and append the same lines twice.
  const busyRef = useRef(false);

  // A different process or level is a different set of buffers: the composite
  // cursor names the old ones, so clear the console and let the next poll fill
  // it from the start of the new view.
  useEffect(() => {
    cursorRef.current = "";
    tokenRef.current = "";
    setEntries([]);
    setLoading(true);
    setError("");
  }, [process, level]);

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    const pull = async () => {
      if (!active || document.hidden || busyRef.current) return;
      busyRef.current = true;
      try {
        // A fresh page may be behind more lines than one response carries;
        // keep reading until the cursor reaches the buffer head.
        for (let page = 0; page < 20; page += 1) {
          const data = await getOwnerLogs(cursorRef.current, { process, level }, controller.signal);
          if (!active) return;
          setUnavailable(Boolean(data.unavailable));
          setCapacity(data.capacity);
          setTruncated(data.truncated);
          // A new token means a new buffer. Its ids start at 1 again, so the
          // old cursor can look valid even though it points into different
          // lines; the token is the reliable signal.
          const replaced = Boolean(data.token && tokenRef.current && data.token !== tokenRef.current);
          if (data.token) tokenRef.current = data.token;
          if (data.reset || replaced) {
            cursorRef.current = "";
            setEntries([]);
            continue;
          }
          if (data.lines.length) {
            setEntries((current) => capBySource([...current, ...data.lines]));
          }
          cursorRef.current = data.next;
          if (!data.has_more || data.lines.length === 0) break;
        }
        setError("");
      } catch (reason) {
        if (active && !controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : t("logs.error"));
        }
      } finally {
        busyRef.current = false;
        if (active) setLoading(false);
      }
    };

    void pull();
    const timer = window.setInterval(() => { if (!document.hidden) void pull(); }, POLL_MS);
    // A tab that was hidden for a while catches up in one poll when it returns.
    const onVisibility = () => { if (!document.hidden) void pull(); };
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      active = false;
      controller.abort();
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [t, process, level]);

  const threshold = LEVEL_WEIGHT[level] ?? LEVEL_WEIGHT.INFO;
  const visible = useMemo(
    () => entries.filter((entry) => {
      if ((LEVEL_WEIGHT[entry.level] ?? LEVEL_WEIGHT.INFO) < threshold) return false;
      const owner = entry.process ?? "bot";
      if (process !== "all" && owner !== process && !(process === "web" && owner === "api")) return false;
      const source = sourceOf(entry);
      if (hidePymongo && source === "pymongo") return false;
      if (hideUrllib3 && source === "urllib3") return false;
      if (hideWavelink && source === "wavelink") return false;
      return true;
    }),
    [entries, threshold, process, hidePymongo, hideUrllib3, hideWavelink],
  );

  // Follow the newest id, not the count: once the client cap is reached the
  // list length stays constant while lines keep arriving.
  const latestId = visible.length ? visible[visible.length - 1].id : 0;

  useEffect(() => {
    if (!pinned) return;
    const node = scrollerRef.current;
    if (node) node.scrollTop = node.scrollHeight;
  }, [latestId, pinned, level, process, hidePymongo, hideUrllib3, hideWavelink]);

  const onScroll = () => {
    const node = scrollerRef.current;
    if (!node) return;
    setPinned(node.scrollHeight - node.scrollTop - node.clientHeight < 48);
  };

  const jumpToLatest = () => {
    setPinned(true);
    const node = scrollerRef.current;
    if (node) node.scrollTop = node.scrollHeight;
  };

  return (
    <div className="bot-logs">
      <header className="staff-guilds-heading bot-logs-heading">
        <div>
          <span className="panel-kicker">{t("logs.kicker")}</span>
          <h2>{t("logs.title")}</h2>
          <p>{t("logs.body")}</p>
        </div>
        <div className={`bot-logs-status${unavailable ? " is-unavailable" : ""}`}>
          <i />
          <span>{unavailable ? t("logs.unavailable") : t("logs.live")}</span>
        </div>
      </header>

      <div className="staff-guild-toolbar bot-logs-toolbar">
        <div className="bot-logs-controls">
          <label className="bot-logs-level">
            <span className="form-label">{t("logs.level")}</span>
            <Select
              ariaLabel={t("logs.level")}
              placeholder={null}
              options={LEVELS}
              value={level}
              onChange={(next) => { setLevel(next); setPinned(true); }}
            />
          </label>
          <label className="bot-logs-level">
            <span className="form-label">{t("logs.process")}</span>
            <Select
              ariaLabel={t("logs.process")}
              placeholder={null}
              options={processOptions}
              value={process}
              onChange={(next) => { setProcess(next); setPinned(true); }}
            />
          </label>
          <div className="bot-logs-filter">
            <span className="bot-logs-filter-text">
              <strong>{t("logs.hidePymongo")}</strong>
              <small>{t("logs.hidePymongoHint")}</small>
            </span>
            <Switch
              size="sm"
              checked={hidePymongo}
              onCheckedChange={(next) => { setHidePymongo(next); setPinned(true); }}
              aria-label={t("logs.hidePymongo")}
            />
          </div>
          <div className="bot-logs-filter">
            <span className="bot-logs-filter-text">
              <strong>{t("logs.hideUrllib3")}</strong>
              <small>{t("logs.hideUrllib3Hint")}</small>
            </span>
            <Switch
              size="sm"
              checked={hideUrllib3}
              onCheckedChange={(next) => { setHideUrllib3(next); setPinned(true); }}
              aria-label={t("logs.hideUrllib3")}
            />
          </div>
          <div className="bot-logs-filter">
            <span className="bot-logs-filter-text">
              <strong>{t("logs.hideWavelink")}</strong>
              <small>{t("logs.hideWavelinkHint")}</small>
            </span>
            <Switch
              size="sm"
              checked={hideWavelink}
              onCheckedChange={(next) => { setHideWavelink(next); setPinned(true); }}
              aria-label={t("logs.hideWavelink")}
            />
          </div>
        </div>
        <div className="bot-logs-meta">
          <span>{t("logs.lines", { count: visible.length.toLocaleString() })}</span>
          {capacity > 0 && <span>{t("logs.buffer", { count: capacity.toLocaleString() })}</span>}
          {truncated && <span className="bot-logs-truncated">{t("logs.truncated")}</span>}
        </div>
      </div>

      {error && <div className="notice warning bot-logs-notice" role="alert">{error}</div>}

      <div className="bot-logs-terminal">
        <div className="bot-logs-console" ref={scrollerRef} onScroll={onScroll} role="log" aria-live="off" aria-label={t("logs.title")}>
          {loading && visible.length === 0 ? (
            <div className="bot-logs-empty">{t("logs.loading")}</div>
          ) : visible.length === 0 ? (
            <div className="bot-logs-empty">{entries.length > 0 ? t("logs.filteredEmpty") : t("logs.empty")}</div>
          ) : (
            visible.map((entry) => <LogLine key={entry.id} entry={entry} />)
          )}
        </div>
        {!pinned && visible.length > 0 && (
          <button type="button" className="bot-logs-jump" onClick={jumpToLatest}>
            {t("logs.jump")}
          </button>
        )}
      </div>
    </div>
  );
}
