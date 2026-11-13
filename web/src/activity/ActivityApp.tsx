import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode, SyntheticEvent } from "react";
import { AnimatedDetails } from "../components/AnimatedDetails";
import { DiscordMarkdown } from "../components/DiscordMarkdown";
import { Icon } from "../components/Icon";
import { ShaderBackground } from "../components/ShaderBackground";
import { ToastHost } from "../components/ToastHost";
import { notifyError } from "../utils/toast";

type Track = {
  title: string;
  author: string;
  artwork?: string | null;
  length?: number;
  uri?: string;
  source?: string;
};

type QueueEntry = {
  index: number;
  title: string;
  author: string;
  uri?: string;
  length?: number;
};

type Playlist = {
  id: string;
  name: string;
  count: number;
  owner_id: string;
  can_edit: boolean;
};

type PlaylistTrack = {
  title: string;
  author?: string;
  uri?: string;
  length?: number;
  added_by?: string | null;
  added_by_name?: string | null;
};

type Snapshot = {
  ok: true;
  guild: { id: string; name: string };
  channel: { id: string; name: string } | null;
  track: Track | null;
  paused: boolean;
  playing: boolean;
  volume: number;
  position: number;
  loop: boolean;
  autoplay: boolean;
  queue: QueueEntry[];
  queue_count: number;
  autoplay_queue: Track[];
  playlists: Playlist[];
  listeners: number;
  dj_required: boolean;
  user: { id: string; is_dj: boolean };
  artwork_url?: string;
  bot_avatar_url?: string;
  updated_at: number;
};

type DiscordSDK = {
  ready: () => Promise<void>;
  guildId?: string;
  channelId?: string;
  commands: {
    authorize: (args: Record<string, unknown>) => Promise<{ code: string }>;
    authenticate: (args: { access_token: string }) => Promise<void>;
    setActivity: (args: { activity: unknown }) => Promise<unknown>;
  };
};

declare global {
  interface Window {
    DiscordSDK: new (clientId: string) => DiscordSDK;
    __NIKO_ACTIVITY__?: { clientId?: string };
  }
}

const DJ_ACTIONS = new Set([
  "skip", "previous", "stop", "toggle_loop", "toggle_autoplay", "volume",
  "queue_remove", "queue_move", "queue_jump", "queue_clear", "queue_shuffle",
  "playlist_play",
]);

function clock(value: number) {
  const total = Math.max(0, Math.round((Number(value) || 0) / 1000));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const seconds = String(total % 60).padStart(2, "0");
  return hours ? `${hours}:${String(minutes).padStart(2, "0")}:${seconds}` : `${minutes}:${seconds}`;
}

function errorText(code?: string) {
  switch (code) {
    case "dj_only": return "Only DJs can use that control.";
    case "no_history": return "There is no previous track.";
    case "no_player": return "Niko is not playing in this server right now.";
    case "not_in_channel": return "Join the voice channel the player is in.";
    case "not_a_member": return "You are not a member of this server.";
    case "guild_unavailable": return "Niko cannot see this server right now.";
    case "autoplay_unavailable": return "Autoplay is not configured (no Last.fm key).";
    case "node_unavailable": return "The music server did not respond. Try again.";
    case "nothing_playing": return "There is nothing playing right now.";
    case "bad_index": return "That queue slot moved. Try again.";
    case "db_unavailable": return "The music database is unavailable right now.";
    case "playlist_not_found": return "That playlist no longer exists.";
    case "playlist_empty": return "That playlist has no playable tracks.";
    case "playlist_editor_only": return "Only this playlist's editors can change it.";
    case "playlist_duplicate": return "That track is already in the playlist.";
    case "unauthorized": return "Your player session expired. Reopen the player from Discord.";
    default: return "That did not work. Try again.";
  }
}

function embedded() {
  return new URLSearchParams(window.location.search).has("frame_id");
}

/** A shared playlist whose tracks load only once the card is opened. */
function PlaylistCard({ playlist, owned, canPlay, canAdd, onPlay, onAdd, loadTracks }: {
  playlist: Playlist;
  owned: boolean;
  canPlay: boolean;
  canAdd: boolean;
  onPlay: () => void;
  onAdd: () => void;
  loadTracks: (name: string) => Promise<PlaylistTrack[] | null>;
}) {
  const [tracks, setTracks] = useState<PlaylistTrack[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggle = async (event: SyntheticEvent<HTMLDetailsElement>) => {
    const details = event.currentTarget;
    if (!details.open || tracks !== null || loading) return;
    setLoading(true);
    setError(null);
    const loaded = await loadTracks(playlist.name);
    if (loaded) setTracks(loaded);
    else setError("Could not load this playlist. Try again.");
    setLoading(false);
  };

  return (
    <li className="activity-playlist-card">
      <details className="activity-playlist-details" onToggle={handleToggle}>
        <summary className="activity-playlist-summary">
          <span className="activity-playlist-copy">
            <b><DiscordMarkdown text={playlist.name} inline /></b>
            <small>
              {tracks?.length ?? playlist.count} track{(tracks?.length ?? playlist.count) === 1 ? "" : "s"} ·{" "}
              {owned ? "yours" : "shared"}
            </small>
          </span>
          <Icon name="chevron" size={14} className="activity-playlist-chevron" />
        </summary>
        <div className="activity-playlist-body">
          <div className="activity-playlist-actions">
            <button className="button button-primary button-small" disabled={!canPlay}
              onClick={onPlay}>Play</button>
            <button className="button button-muted button-small" disabled={!canAdd}
              title="Add the current track to this playlist"
              onClick={onAdd}>+ Current</button>
          </div>
          {loading ? (
            <p className="activity-empty">Loading tracks…</p>
          ) : error ? (
            <p className="activity-empty">{error}</p>
          ) : tracks && tracks.length > 0 ? (
            <ol className="activity-playlist-tracks">
              {tracks.map((entry, index) => (
                <li className="activity-playlist-track" key={`${entry.uri || entry.title}-${index}`}>
                  <span className="activity-index">{String(index + 1).padStart(2, "0")}</span>
                  <span className="activity-queue-copy">
                    <b><DiscordMarkdown text={entry.title || "Unknown"} inline /></b>
                    {entry.author && <small><DiscordMarkdown text={entry.author} inline /></small>}
                    <small className="activity-playlist-added">
                      {entry.added_by
                        ? <>Added by <DiscordMarkdown
                          text={`<@${entry.added_by}>`}
                          mentionNames={entry.added_by_name ? { user: { [entry.added_by]: entry.added_by_name } } : undefined}
                          inline
                        /></>
                        : "Added by an unknown member"}
                    </small>
                  </span>
                  <span className="activity-autoplay-length">
                    {entry.length ? clock(entry.length) : ""}
                  </span>
                </li>
              ))}
            </ol>
          ) : tracks ? (
            <p className="activity-empty">This playlist has no tracks yet.</p>
          ) : null}
        </div>
      </details>
    </li>
  );
}

/** The site backdrop, glass shell and toast stack wrap every player state. */
function ActivityFrame({ children }: { children: ReactNode }) {
  return (
    <>
      <div className="site-ambient" aria-hidden="true">
        <ShaderBackground className="ambient-effect-canvas" />
      </div>
      <div className="site-content">{children}</div>
      <ToastHost />
    </>
  );
}

export function ActivityApp() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [status, setStatus] = useState<"connecting" | "ready" | "error">("connecting");
  const [problem, setProblem] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [clockNow, setClockNow] = useState(Date.now());

  const sdkRef = useRef<DiscordSDK | null>(null);
  const sessionRef = useRef<string | null>(null);
  const guildRef = useRef<string | null>(null);
  const channelRef = useRef<string | null>(null);

  useEffect(() => {
    // Startup failures stay in the centered state below; once the player is
    // live, a dropped poll or refused action is reported by the site's toast
    // stack instead of a banner that pushes the layout around.
    if (status !== "ready" || !problem) return;
    notifyError(problem, "activity-problem");
  }, [problem, status]);

  const refresh = useCallback(async () => {
    if (!sessionRef.current || !guildRef.current) return null;
    const params = new URLSearchParams({ guild_id: guildRef.current });
    if (channelRef.current) params.set("channel_id", channelRef.current);
    let response: Response;
    try {
      response = await fetch(`/api/activity/state?${params}`, {
        headers: { Authorization: `Bearer ${sessionRef.current}` },
        cache: "no-store",
      });
    } catch {
      setProblem("Could not reach the bot. Retrying…");
      return null;
    }
    const data = await response.json().catch(() => ({}));
    if (response.status === 401) {
      setStatus("error");
      setProblem(errorText("unauthorized"));
      return null;
    }
    if (!response.ok || !data.ok) {
      setProblem(errorText(data.error));
      return null;
    }
    setProblem(null);
    setStatus("ready");
    setSnapshot(data as Snapshot);
    return data as Snapshot;
  }, []);

  const loadPlaylistTracks = useCallback(async (name: string): Promise<PlaylistTrack[] | null> => {
    const session = sessionRef.current;
    const guild = guildRef.current;
    if (!session || !guild) return null;
    const params = new URLSearchParams({ guild_id: guild, name });
    if (channelRef.current) params.set("channel_id", channelRef.current);
    try {
      const response = await fetch(`/api/activity/playlist?${params}`, {
        headers: { Authorization: `Bearer ${session}` },
        cache: "no-store",
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.ok) {
        setProblem(errorText(data.error));
        return null;
      }
      return Array.isArray(data.tracks) ? data.tracks as PlaylistTrack[] : [];
    } catch {
      setProblem("Could not reach the bot. Try again.");
      return null;
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    let poll = 0;
    let tick = 0;

    const boot = async () => {
      if (!embedded()) {
        setStatus("error");
        setProblem("Open the player from the voice channel's now-playing panel in Discord.");
        return;
      }
      try {
        const sdk = new window.DiscordSDK(window.__NIKO_ACTIVITY__?.clientId || "");
        await sdk.ready();

        let authorization: { code: string };
        try {
          authorization = await sdk.commands.authorize({
            client_id: window.__NIKO_ACTIVITY__?.clientId,
            response_type: "code",
            state: "",
            prompt: "none",
            scope: ["identify", "guilds", "rpc.activities.write"],
          });
        } catch {
          // A client that has not granted rich-presence access can still use
          // every playback control, so fall back to the plain sign-in scopes.
          authorization = await sdk.commands.authorize({
            client_id: window.__NIKO_ACTIVITY__?.clientId,
            response_type: "code",
            state: "",
            prompt: "none",
            scope: ["identify", "guilds"],
          });
        }

        const tokenResponse = await fetch("/api/activity/token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: authorization.code }),
        });
        const tokenData = await tokenResponse.json().catch(() => ({}));
        if (!tokenResponse.ok || !tokenData.session) {
          throw new Error(tokenData.error || "Discord sign-in failed.");
        }
        await sdk.commands.authenticate({ access_token: tokenData.access_token });

        if (cancelled) return;
        sdkRef.current = sdk;
        sessionRef.current = tokenData.session;
        guildRef.current = sdk.guildId || null;
        channelRef.current = sdk.channelId || null;
        if (!guildRef.current) {
          setStatus("error");
          setProblem("Launch the player from a server's voice channel, not a direct message.");
          return;
        }

        await refresh();
        poll = window.setInterval(refresh, 4000);
        tick = window.setInterval(() => setClockNow(Date.now()), 500);
      } catch (error) {
        console.error("Niko Player failed to start", error);
        if (!cancelled) {
          setStatus("error");
          setProblem("The player could not connect. Reopen it from Discord.");
        }
      }
    };

    void boot();
    return () => {
      cancelled = true;
      window.clearInterval(poll);
      window.clearInterval(tick);
      // Leaving the Activity clears the listening status it set on the profile.
      void sdkRef.current?.commands.setActivity({ activity: null }).catch(() => undefined);
    };
  }, [refresh]);

  useEffect(() => {
    const onVisible = () => {
      if (!document.hidden) void refresh();
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => document.removeEventListener("visibilitychange", onVisible);
  }, [refresh]);

  // Artwork changes with the track, including when a song replays from the
  // same queue entry, so the URL is part of the identity that triggers a
  // presence update.
  const trackKey = snapshot?.track
    ? [snapshot.track.uri || snapshot.track.title, snapshot.track.author, snapshot.artwork_url || ""].join("|")
    : null;

  // The Activity may set the member's own rich presence. A type-2 activity is
  // the "Listening to" line Discord shows under their name, so it names the
  // track and artist the room is hearing. Re-sending is cheap, but only a track
  // change (or pause state) needs to; polling otherwise is not a new status.
  useEffect(() => {
    const sdk = sdkRef.current;
    if (!sdk || status !== "ready") return;
    if (!snapshot?.track) {
      void sdk.commands.setActivity({ activity: null }).catch(() => undefined);
      return;
    }
    const artwork = snapshot.artwork_url
      ? new URL(snapshot.artwork_url, window.location.origin).toString()
      : undefined;
    // The bot's picture is the small badge on every listening status, even one
    // whose track has no artwork, so the status always has an icon.
    const botAvatar = snapshot.bot_avatar_url
      ? new URL(snapshot.bot_avatar_url, window.location.origin).toString()
      : undefined;
    const assets = {
      ...(artwork ? { large_image: artwork, large_text: "Listening to a track" } : {}),
      ...(botAvatar ? { small_image: botAvatar, small_text: "Niko Music" } : {}),
    };
    void sdk.commands.setActivity({
      activity: {
        type: 2,
        details: snapshot.track.title,
        state: snapshot.track.author || "Niko Music",
        ...(Object.keys(assets).length ? { assets } : {}),
      },
    }).catch(() => undefined);
  }, [status, trackKey, snapshot?.paused]);

  const position = useMemo(() => {
    if (!snapshot?.track) return 0;
    const base = Number(snapshot.position) || 0;
    const drift = snapshot.playing && !snapshot.paused
      ? Math.max(0, clockNow - Number(snapshot.updated_at || clockNow))
      : 0;
    const length = Number(snapshot.track.length) || 0;
    return length ? Math.min(base + drift, length) : base + drift;
  }, [snapshot, clockNow]);

  const isDj = !snapshot?.user || snapshot.user.is_dj !== false;
  const canControl = (action: string) => {
    if (!snapshot?.track) return false;
    return !(DJ_ACTIONS.has(action) && !isDj);
  };

  async function send(action: string, value?: unknown) {
    if (busy || !sessionRef.current || !snapshot) return;
    if (DJ_ACTIONS.has(action) && !isDj) {
      setProblem(errorText("dj_only"));
      return;
    }
    setBusy(true);
    try {
      const response = await fetch("/api/activity/control", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionRef.current}`,
        },
        body: JSON.stringify({
          action,
          value,
          guild_id: guildRef.current,
          channel_id: channelRef.current,
        }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.ok) {
        setProblem(errorText(data.error));
        return;
      }
      setProblem(null);
      setSnapshot(data as Snapshot);
    } catch {
      setProblem("Could not reach the bot. Try again.");
    } finally {
      setBusy(false);
    }
  }

  if (status === "connecting" && !snapshot) {
    return (
      <ActivityFrame>
        <main className="activity-root activity-centered">
          <span className="activity-spinner" aria-hidden="true" />
          <p className="activity-muted">Connecting to Discord…</p>
        </main>
      </ActivityFrame>
    );
  }

  if (status === "error" && !snapshot) {
    return (
      <ActivityFrame>
        <main className="activity-root activity-centered">
          <div className="brand"><span className="brand-mark">n</span><span>niko</span></div>
          <h1>Player unavailable</h1>
          <p className="activity-muted">{problem}</p>
        </main>
      </ActivityFrame>
    );
  }

  if (!snapshot) return null;

  const track = snapshot.track;
  const fill = track?.length ? Math.min(100, (position / track.length) * 100) : 0;
  const paused = snapshot.paused;

  return (
    <ActivityFrame>
    <main className="activity-root">

      <header className="activity-head">
        <div className="brand">
          <span className="brand-mark">n</span>
          <span>niko</span>
        </div>
        <span className={`activity-pulse${status === "ready" ? " is-live" : ""}`} aria-hidden="true" />
        <span className="activity-where" title="Voice channel">
          {snapshot.channel?.name || "Voice channel"}
        </span>
        {snapshot.listeners > 0 && (
          <span className="activity-listeners">{snapshot.listeners} listening</span>
        )}
      </header>

      <section className="activity-now" aria-label="Now playing">
        <div className="activity-art">
          {snapshot.artwork_url ? (
            <img src={snapshot.artwork_url} alt="" />
          ) : (
            <Icon name="music" size={46} />
          )}
        </div>
        <div className="activity-meta">
          <p className="eyebrow">{track ? (paused ? "Paused" : "Now playing") : "Nothing playing"}</p>
          <h1><DiscordMarkdown text={track?.title || "Nothing playing"} inline /></h1>
          <p className="activity-artist">
            {track ? <DiscordMarkdown text={track.author} inline /> : "Add something with /play."}
          </p>
          <div className="activity-progress">
            <span>{clock(position)}</span>
            <span className="activity-bar"><i style={{ width: `${fill}%` }} /></span>
            <span>{track?.length ? clock(track.length) : track ? "LIVE" : "0:00"}</span>
          </div>
          <p className="activity-badges">
            {snapshot.loop && <span className="is-on">Loop</span>}
            {snapshot.autoplay && <span className="is-on">Autoplay</span>}
            {snapshot.dj_required && <span className={isDj ? "is-on" : undefined}>{isDj ? "DJ" : "DJ controls locked"}</span>}
            {track?.source && <span>{track.source}</span>}
          </p>
        </div>
      </section>

      <section className="activity-controls" aria-label="Playback">
        <button className="activity-control" title="Previous track" aria-label="Previous track"
          disabled={!canControl("previous")} onClick={() => send("previous")}>
          <Icon name="previous" size={19} />
        </button>
        <button className="activity-control is-primary" title={paused ? "Resume" : "Pause"}
          aria-label={paused ? "Resume" : "Pause"} disabled={!track}
          onClick={() => send("toggle_pause")}>
          <Icon name={paused ? "play" : "pause"} size={19} />
        </button>
        <button className="activity-control" title="Skip" aria-label="Skip"
          disabled={!canControl("skip")} onClick={() => send("skip")}>
          <Icon name="skip" size={19} />
        </button>
        <button className="activity-control is-danger" title="Stop and clear the queue" aria-label="Stop"
          disabled={!canControl("stop")} onClick={() => send("stop")}>
          <Icon name="stop" size={19} />
        </button>
      </section>

      <section className="activity-modes" aria-label="Playback modes">
        <button className="activity-mode" disabled={!canControl("queue_shuffle") || snapshot.queue_count < 2}
          onClick={() => send("queue_shuffle")}><Icon name="shuffle" size={13} />Shuffle</button>
        <button className={`activity-mode${snapshot.loop ? " is-on" : ""}`}
          disabled={!canControl("toggle_loop")} onClick={() => send("toggle_loop")}><Icon name="loop" size={13} />Loop</button>
        <button className={`activity-mode${snapshot.autoplay ? " is-on" : ""}`}
          disabled={!canControl("toggle_autoplay")} onClick={() => send("toggle_autoplay")}><Icon name="spark" size={13} />Autoplay</button>
        <label className="activity-volume">
          <Icon name="volume" size={16} />
          <input type="range" min="0" max="100" step="5" value={snapshot.volume}
            disabled={!canControl("volume")}
            onChange={(event) => setSnapshot({ ...snapshot, volume: Number(event.target.value) })}
            onPointerUp={(event) => send("volume", Number((event.target as HTMLInputElement).value))}
            onKeyUp={(event) => send("volume", Number((event.target as HTMLInputElement).value))}
            aria-label="Volume" />
          <output>{snapshot.volume}%</output>
        </label>
      </section>

      <div className="activity-workspace">
        <section className="activity-card dash-panel" aria-labelledby="activity-queue-title">
          <header className="panel-heading">
            <div className="activity-card-heading">
              <span className="panel-icon"><Icon name="queue" /></span>
              <div>
                <p className="panel-kicker">Up next</p>
                <h3 id="activity-queue-title">Queue {snapshot.queue_count > 0 && <span>· {snapshot.queue_count}</span>}</h3>
              </div>
            </div>
            <button className="button button-muted button-small" disabled={!snapshot.queue_count || !isDj}
              onClick={() => send("queue_clear")}>Clear</button>
          </header>

          {snapshot.queue.length > 0 ? (
            <ol className="activity-queue">
              {snapshot.queue.map((entry, index) => (
                <li className="activity-queue-row" key={`${entry.index}-${entry.uri || entry.title}`}>
                  <span className="activity-index">{String(entry.index + 1).padStart(2, "0")}</span>
                  <span className="activity-queue-copy">
                    <b><DiscordMarkdown text={entry.title || "Unknown"} inline /></b>
                    {entry.author && <small><DiscordMarkdown text={entry.author} inline /></small>}
                  </span>
                  <span className="activity-queue-tools">
                    <button className="activity-icon" title="Play this track now" aria-label="Play this track now"
                      disabled={!isDj} onClick={() => send("queue_jump", entry.index)}><Icon name="play" size={14} /></button>
                    <button className="activity-icon" title="Move up" aria-label="Move up"
                      disabled={!isDj || index === 0}
                      onClick={() => send("queue_move", { from: entry.index, to: entry.index - 1 })}><Icon name="arrow_up" size={14} /></button>
                    <button className="activity-icon" title="Move down" aria-label="Move down"
                      disabled={!isDj || index >= snapshot.queue.length - 1}
                      onClick={() => send("queue_move", { from: entry.index, to: entry.index + 1 })}><Icon name="arrow_down" size={14} /></button>
                    <button className="activity-icon is-danger" title="Remove from queue" aria-label="Remove from queue"
                      disabled={!isDj} onClick={() => send("queue_remove", entry.index)}><Icon name="close" size={14} /></button>
                  </span>
                </li>
              ))}
            </ol>
          ) : (
            <p className="activity-empty">Nothing queued. Add a track or play a playlist.</p>
          )}

          {snapshot.autoplay && (
            <AnimatedDetails className="activity-autoplay">
              <summary>
                <span>
                  <b>Autoplay queue</b>
                  <small>Last.fm picks that play when the queue runs dry</small>
                </span>
                <span className="activity-autoplay-count">
                  {snapshot.autoplay_queue.length || "—"}
                </span>
              </summary>
              {snapshot.autoplay_queue.length > 0 ? (
                <ol className="activity-autoplay-list">
                  {snapshot.autoplay_queue.map((entry, index) => (
                    <li key={`${entry.uri || entry.title}-${index}`}>
                      <span className="activity-index">{String(index + 1).padStart(2, "0")}</span>
                      <span className="activity-queue-copy">
                        <b><DiscordMarkdown text={entry.title || "Unknown"} inline /></b>
                        {entry.author && <small><DiscordMarkdown text={entry.author} inline /></small>}
                      </span>
                      <span className="activity-autoplay-length">
                        {entry.length ? clock(entry.length) : ""}
                      </span>
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="activity-empty">Finding something similar to play next…</p>
              )}
            </AnimatedDetails>
          )}
        </section>

        <section className="activity-card dash-panel" aria-labelledby="activity-playlists-title">
          <header className="panel-heading">
            <div className="activity-card-heading">
              <span className="panel-icon"><Icon name="music" /></span>
              <div>
                <p className="panel-kicker">Shared queues</p>
                <h3 id="activity-playlists-title">Playlists</h3>
              </div>
            </div>
          </header>

          {snapshot.playlists.length > 0 ? (
            <ul className="activity-playlists">
              {snapshot.playlists.map((playlist) => (
                <PlaylistCard
                  key={playlist.id}
                  playlist={playlist}
                  owned={playlist.owner_id === snapshot.user.id}
                  canPlay={Boolean(playlist.count && isDj)}
                  canAdd={Boolean(playlist.can_edit && track)}
                  onPlay={() => send("playlist_play", playlist.name)}
                  onAdd={() => send("playlist_add", playlist.name)}
                  loadTracks={loadPlaylistTracks}
                />
              ))}
            </ul>
          ) : (
            <p className="activity-empty">
              No shared playlists yet. Create one with <code>.playlist create</code>.
            </p>
          )}
        </section>
      </div>

      <p className="activity-foot">
        Controls follow this server's DJ role. Every change updates the channel's now-playing panel too.
      </p>
    </main>
    </ActivityFrame>
  );
}
