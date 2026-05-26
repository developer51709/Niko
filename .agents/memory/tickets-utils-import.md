---
name: Tickets utils import
description: The correct module name for TicketConfig inside utils/tickets/
---

`src/utils/tickets/utils.py` must import:
```python
from .config import TicketConfig
```

**Why:** During the utils folder restructure, `ticket_config.py` was renamed to `config.py`, but `utils.py` still referenced the old name. This causes `cogs.tickets` to fail with `No module named 'utils.tickets.ticket_config'`.

**How to apply:** Any future import from the tickets utils package should use `from utils.tickets.config import TicketConfig`, never `ticket_config`.
