import os
import json
import threading

MEMORY_FILE = "memory.json"

# Replies are generated on worker threads, so two saves can overlap; the lock
# plus the write-and-replace below keep the file valid JSON either way.
_write_lock = threading.Lock()

# -----------------------------
# Internal memory structure
# -----------------------------
_EMPTY_MEMORY = {
    "users": {},
    "favorability": {},
    "conversations": {}
}


def _load_memory() -> dict:
    """Read the memory file, surviving a missing, unreadable, or corrupt file.

    A single bad write used to raise on import and take every AI reply down with
    it, so an unreadable file is set aside as ``memory.json.corrupt`` (nothing is
    deleted) and memory starts fresh instead.
    """
    memory = {key: dict(value) for key, value in _EMPTY_MEMORY.items()}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return memory
    except (OSError, ValueError) as error:
        try:
            os.replace(MEMORY_FILE, MEMORY_FILE + ".corrupt")
        except OSError:
            pass
        print(f"[AI] {MEMORY_FILE} could not be read ({error}) — starting fresh memory")
        return memory

    if not isinstance(data, dict):
        return memory
    for key, default in _EMPTY_MEMORY.items():
        value = data.get(key)
        memory[key] = value if isinstance(value, dict) else dict(default)
    return memory


# Load memory if it exists
_memory_data = _load_memory()


# -----------------------------
# Save memory to disk
# -----------------------------
def save_memory():
    """Write the memory file atomically, never raising into the reply path."""
    with _write_lock:
        payload = json.dumps(_memory_data, indent=4)
        temp_file = f"{MEMORY_FILE}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(payload)
            os.replace(temp_file, MEMORY_FILE)
        except OSError as error:
            # A full or read-only disk must not lose the reply the user is
            # waiting on — the in-memory memory stays correct for this session.
            print(f"[AI] Could not save {MEMORY_FILE}: {error}")
            try:
                os.remove(temp_file)
            except OSError:
                pass


# -----------------------------
# User long‑term memory
# -----------------------------
def get_user_memory(user_id: int) -> str:
    memory = _memory_data.get("users", {}).get(str(user_id), "")
    return memory if isinstance(memory, str) else ""


# -----------------------------
# Short‑term conversation history
# -----------------------------
def _user_history(user_id: int) -> list:
    """The stored conversation turns for a user, ignoring malformed entries."""
    history = _memory_data.get("conversations", {}).get(str(user_id), [])
    if not isinstance(history, list):
        return []
    return [turn for turn in history if isinstance(turn, dict)]


def get_conversation_history(user_id: int, limit: int = 5) -> str:
    history = _user_history(user_id)
    return "\n".join([f"{h.get('role', 'User')}: {h.get('content', '')}" for h in history[-limit:]])


def update_user_memory(user_id: int, message: str, role: str = "User"):
    uid = str(user_id)

    # Long‑term memory
    prev = _memory_data["users"].get(uid, "")
    if not isinstance(prev, str):
        prev = ""
    _memory_data["users"][uid] = (prev + "\n" + str(message)).strip()

    # Short‑term conversation memory
    history = _user_history(user_id)
    history.append({"role": role, "content": message})

    # Keep last 10 messages
    _memory_data["conversations"][uid] = history[-10:]

    save_memory()


# -----------------------------
# Favorability system
# -----------------------------
def adjust_favorability(user_id: int, delta: int = 1):
    uid = str(user_id)
    current = _memory_data["favorability"].get(uid, 0)
    _memory_data["favorability"][uid] = current + delta
    save_memory()


def get_favorability(user_id: int) -> int:
    return _memory_data["favorability"].get(str(user_id), 0)


def clear_conversation_history(user_id: int) -> None:
    """Erase both the short-term conversation history and long-term memory for a user."""
    uid = str(user_id)
    _memory_data.get("conversations", {}).pop(uid, None)
    _memory_data.get("users", {}).pop(uid, None)
    _memory_data.get("favorability", {}).pop(uid, None)
    save_memory()


# ── Public aliases used by cogs ───────────────────────────────────────────────
def get_favorability_score(user_id: int) -> int:
    """Alias for get_favorability — returns the vibe score for a user."""
    return get_favorability(user_id)


def get_memory_content(user_id: int) -> str:
    """Return the long-term memory string for a user (empty str if none)."""
    return get_user_memory(user_id)