"""
Music System — user-facing messages (EN / DE / ES).

The wording itself lives in ``cogs/music/locales`` so the music cog keeps
every string it can send together with the rest of its files. This module stays
in ``utils/music`` because the playback helpers (autoplay, spotify, nodes)
import ``msg`` from here and must not depend on the Discord command layer.
"""

from utils.i18n import make_flat_msg
from utils.locales import load_locales

MESSAGES = load_locales("cogs.music", "messages")

msg = make_flat_msg(MESSAGES)
