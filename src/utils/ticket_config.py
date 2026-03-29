from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TicketConfig:
    guild_id: int

    panel_title: Optional[str] = None
    panel_description: Optional[str] = None
    panel_color: Optional[int] = None
    panel_image: Optional[str] = None

    panel_categories: Optional[List[str]] = field(default_factory=list)

    panel_channel_id: Optional[int] = None
    panel_message_id: Optional[int] = None

    # persistent open tickets
    open_tickets: List[dict] = field(default_factory=list)