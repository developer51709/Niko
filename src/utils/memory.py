import os
import json

MEMORY_FILE = "memory.json"

# -----------------------------
# Internal memory structure
# -----------------------------
_memory_data = {
    "users": {},
    "favorability": {},
    "conversations": {}
}

# Load memory if it exists
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        _memory_data = json.load(f)


# -----------------------------
# Save memory to disk
# -----------------------------
def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(_memory_data, f, indent=4)


# -----------------------------
# User long‑term memory
# -----------------------------
def get_user_memory(user_id: int) -> str:
    return _memory_data.get("users", {}).get(str(user_id), "")


# -----------------------------
# Short‑term conversation history
# -----------------------------
def get_conversation_history(user_id: int, limit: int = 5) -> str:
    history = _memory_data.get("conversations", {}).get(str(user_id), [])
    return "\n".join([f"{h['role']}: {h['content']}" for h in history[-limit:]])


def update_user_memory(user_id: int, message: str, role: str = "User"):
    uid = str(user_id)

    # Long‑term memory
    prev = _memory_data["users"].get(uid, "")
    _memory_data["users"][uid] = (prev + "\n" + message).strip()

    # Short‑term conversation memory
    if uid not in _memory_data["conversations"]:
        _memory_data["conversations"][uid] = []

    _memory_data["conversations"][uid].append({"role": role, "content": message})

    # Keep last 10 messages
    _memory_data["conversations"][uid] = _memory_data["conversations"][uid][-10:]

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