"""The identity of the site build this process is serving.

The shell and its assets live in ``src/website/dist`` and are read from disk, so
a deploy — or an update applied from beta — replaces them under a process that
keeps running. A tab that is already open keeps the bundle it loaded, which is
correct until the files behind it change; ``build_id`` is how such a tab notices
that the site is no longer the one it is running.
"""

import os
import re

from . import config

#: Vite's entry script. Its hash is derived from the modules in the bundle, so
#: it changes exactly when the running code would change.
_ENTRY_ASSET = re.compile(r'src="(/assets/index-[^"]+\.js)"')


def build_id() -> str:
    """The current build's name, or "" when there is no build on disk.

    The entry script doubles as the build's identity: two builds that change any
    bundled module produce a different name, and a rebuild that changes nothing
    the bundle imports keeps the old one — which is right, because the open tabs
    are still running the current code.

    The shell is small and the site already reads it once per page, so this
    reads it again rather than caching by timestamp: a cache keyed on a
    coarse-grained mtime could hand back the previous build's name right after
    an update, which is the one moment the answer matters.
    """
    path = os.path.join(config.WEB_DIST_DIR, "index.html")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            shell = handle.read()
    except OSError:
        return ""
    match = _ENTRY_ASSET.search(shell)
    return match.group(1) if match else ""
