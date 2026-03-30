import json
import os
from dataclasses import dataclass, asdict

DATA_DIR = "data/onboarding"


@dataclass
class OnboardingConfig:
    # Welcome
    welcome_channel: int | None = None
    welcome_title: str | None = None
    welcome_description: str | None = None
    welcome_color: int | None = 0x5865F2
    welcome_image: str | None = None

    # Rules
    rules_channel: int | None = None
    rules_message_id: int | None = None
    rules_text: str | None = None
    rules_role_id: int | None = None  # role to assign on acknowledgment

    # Role menu
    role_menu_channel: int | None = None
    role_menu_message_id: int | None = None
    role_menu_options: list[dict] | None = None  # [{role_id, label, description, emoji}]


def _get_path(guild_id: int) -> str:
    return os.path.join(DATA_DIR, f"{guild_id}.json")


def load_config(guild_id: int) -> OnboardingConfig:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = _get_path(guild_id)

    if not os.path.exists(path):
        return OnboardingConfig()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return OnboardingConfig(**data)


def save_config(guild_id: int, cfg: OnboardingConfig):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = _get_path(guild_id)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(cfg), f, indent=4)


def load_all_configs() -> list[tuple[int, "OnboardingConfig"]]:
    """Return a list of (guild_id, config) for every saved guild."""
    os.makedirs(DATA_DIR, exist_ok=True)
    results = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".json"):
            try:
                gid = int(fname[:-5])
                results.append((gid, load_config(gid)))
            except (ValueError, Exception):
                pass
    return results