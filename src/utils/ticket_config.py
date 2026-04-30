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

    # roles that get auto-permission inside every ticket and can run
    # in-ticket subcommands like add/remove/close/delete/claim
    support_roles: List[int] = field(default_factory=list)

    # persistent open tickets — each entry:
    #   channel_id, message_id, category, opener_id, status,
    #   claimed_by (Optional[int])
    open_tickets: List[dict] = field(default_factory=list)
