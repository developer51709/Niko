from __future__ import annotations
from typing import Dict

from .ticket_config import TicketConfig


# simple in-memory store; swap to JSON/DB later if needed
_ticket_configs: Dict[int, TicketConfig] = {}


def get_ticket_config(guild_id: int) -> TicketConfig:
    cfg = _ticket_configs.get(guild_id)
    if cfg is None:
        cfg = TicketConfig(guild_id=guild_id)
        _ticket_configs[guild_id] = cfg
    return cfg


def update_ticket_config(guild_id: int, cfg: TicketConfig) -> None:
    _ticket_configs[guild_id] = cfg