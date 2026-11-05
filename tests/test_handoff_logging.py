"""The handoff has to log through the project logger.

``utils.logging.info(module, message)`` is a two-argument wrapper that tags the
record with a module name. The stdlib function of the same name is not: its
second argument is a ``%`` formatting argument, so calling it the same way made
every handoff line raise ``TypeError: not all arguments converted during string
formatting`` inside the console formatter — the message was lost and Python
printed a logging traceback instead.
"""

from pathlib import Path

from utils import handoff
from utils import logging as project_logging


ROOT = Path(__file__).resolve().parents[1]


def test_the_handoff_imports_the_project_logger():
    assert handoff.logging is project_logging


def test_the_dashboard_adoption_line_passes_one_log_argument():
    source = (ROOT / "src/api_server.py").read_text(encoding="utf-8")

    # This file needs the stdlib module for its werkzeug filter, so the tagged
    # logger name has to be spelled out and the message passed on its own.
    assert 'logging.getLogger("Startup").info(' in source
    assert 'logging.info("Startup",' not in source


def test_the_handoff_does_not_import_the_stdlib_logger():
    source = (ROOT / "src/utils/handoff.py").read_text(encoding="utf-8")

    assert "from utils import logging" in source
    assert "\nimport logging\n" not in source
