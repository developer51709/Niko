---
name: Python workflow runtime
description: How this workspace exposes Python dependencies to long-running workflows.
---

Python dependencies installed as Nix packages may not be visible to the base Python module's normal `python` command. Run Python web services through `nix-shell -p ... --run 'python ...'` so the package paths are included.

**Why:** The base Python module has no usable pip environment, and the package installer can hit the externally-managed-environment guard.

**How to apply:** When a Python workflow reports an installed module as missing, verify the interpreter path and use a Nix runtime-shell command rather than bypassing PEP 668.