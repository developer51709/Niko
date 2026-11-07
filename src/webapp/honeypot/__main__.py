"""Print a decoy file: ``python -m webapp.honeypot [--list|path]``."""

from . import main

raise SystemExit(main())
