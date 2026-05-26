from __future__ import annotations
from typing import Dict, List, Optional
from pathlib import Path
import json

from .ticket_config import TicketConfig

DATA_PATH = Path("data")
DATA_FILE = DATA_PATH / "tickets.json"

_ticket_configs: Dict[int, TicketConfig] = {}
_loaded = False


def _ensure_data_dir():
    DATA_PATH.mkdir(parents=True, exist_ok=True)


def _load_all() -> None:
    global _ticket_configs, _loaded
    _ensure_data_dir()

    if not DATA_FILE.exists():
        _ticket_configs = {}
        _loaded = True
        return

    with DATA_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    cfgs = {}
    for gid_str, data in raw.items():
        gid = int(gid_str)
        cfg = TicketConfig(
            guild_id=gid,
            panel_title=data.get("panel_title"),
            panel_description=data.get("panel_description"),
            panel_color=data.get("panel_color"),
            panel_image=data.get("panel_image"),
            panel_categories=data.get("panel_categories") or [],
            panel_channel_id=data.get("panel_channel_id"),
            panel_message_id=data.get("panel_message_id"),
            support_roles=data.get("support_roles") or [],
            open_tickets=data.get("open_tickets") or [],
        )
        cfgs[gid] = cfg

    _ticket_configs = cfgs
    _loaded = True


def _save_all() -> None:
    _ensure_data_dir()

    raw = {}
    for gid, cfg in _ticket_configs.items():
        raw[str(gid)] = {
            "guild_id": cfg.guild_id,
            "panel_title": cfg.panel_title,
            "panel_description": cfg.panel_description,
            "panel_color": cfg.panel_color,
            "panel_image": cfg.panel_image,
            "panel_categories": cfg.panel_categories,
            "panel_channel_id": cfg.panel_channel_id,
            "panel_message_id": cfg.panel_message_id,
            "support_roles": cfg.support_roles,
            "open_tickets": cfg.open_tickets,
        }

    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)


def get_ticket_config(guild_id: int) -> TicketConfig:
    if not _loaded:
        _load_all()

    cfg = _ticket_configs.get(guild_id)
    if cfg is None:
        cfg = TicketConfig(guild_id=guild_id)
        _ticket_configs[guild_id] = cfg
        _save_all()
    return cfg


def update_ticket_config(guild_id: int, cfg: TicketConfig) -> None:
    _ticket_configs[guild_id] = cfg
    _save_all()


def get_all_ticket_configs() -> List[TicketConfig]:
    if not _loaded:
        _load_all()
    return list(_ticket_configs.values())


def find_open_ticket(guild_id: int, channel_id: int) -> Optional[dict]:
    """Return the open-ticket entry for a given channel, or None."""
    cfg = get_ticket_config(guild_id)
    for t in cfg.open_tickets:
        if t.get("channel_id") == channel_id:
            return t
    return None
