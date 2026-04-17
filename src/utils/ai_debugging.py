"""
AI Debugging Tool for Niko Bot
================================
How it works:
1. An error is thrown anywhere in the bot
2. `send_debug_report()` posts the error + traceback to the designated debug
   channel with an "AI Debug" button
3. The developer clicks "AI Debug" — the AI analyzes the error and the
   relevant source file and replies with an explanation + fix suggestion
4. The developer clicks "Fix with AI" — the AI rewrites the affected file,
   a backup is saved, and the cog is hot-reloaded
5. If the fix is wrong the developer clicks "Revert Fix" to restore the
   backup instantly
"""

import os
import re
import shutil
import asyncio
import traceback
import datetime
from pathlib import Path

import discord
from discord.ext import commands
from openai import OpenAI
from utils import logging as log

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
DEBUG_CHANNEL_ID: int | None = (
    int(os.environ["AI_DEBUG_CHANNEL"])
    if os.environ.get("AI_DEBUG_CHANNEL", "").strip().isdigit()
    else None
)

COGS_DIR  = Path("src/cogs")
UTILS_DIR = Path("src/utils")
BACKUP_DIR = Path("data/ai_debug_backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

_MAX_FILE_CHARS = 8000

# ──────────────────────────────────────────────
# OpenAI client — direct technical call (no personality layer)
# ──────────────────────────────────────────────
def _openai_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
        base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL"),
    )


def _call_ai(system: str, user: str, *, max_tokens: int = 1200) -> str:
    """Synchronous OpenAI call — run this inside asyncio.to_thread()."""
    try:
        client = _openai_client()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.1,
        )
        return resp.choices[0].message.content.strip()
    except Exception as exc:
        return f"[AI call failed: {exc}]"


# ──────────────────────────────────────────────
# File helpers
# ──────────────────────────────────────────────
def _find_source_file(name: str) -> Path | None:
    """Search cogs/ then utils/ for a matching .py file."""
    for directory in (COGS_DIR, UTILS_DIR):
        candidate = directory / f"{name}.py"
        if candidate.exists():
            return candidate
    return None


def _read_file(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
        if len(text) > _MAX_FILE_CHARS:
            text = text[:_MAX_FILE_CHARS] + f"\n... [truncated — {len(text)} total chars]"
        return text
    except Exception as exc:
        return f"<could not read {path}: {exc}>"


def _backup(file_path: Path) -> Path:
    ts   = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name = file_path.stem
    dest = BACKUP_DIR / f"{name}_{ts}.py.bak"
    shutil.copy2(file_path, dest)
    return dest


def _latest_backup(name: str) -> Path | None:
    backups = sorted(BACKUP_DIR.glob(f"{name}_*.py.bak"), reverse=True)
    return backups[0] if backups else None


def _extract_code_block(text: str) -> str | None:
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None


def _infer_file_from_tb(traceback_str: str) -> str | None:
    """Try to detect which cog/util file is named in the traceback."""
    matches = re.findall(r"src/(?:cogs|utils)/(\w+)\.py", traceback_str)
    return matches[-1] if matches else None


# ──────────────────────────────────────────────
# AI prompts
# ──────────────────────────────────────────────
_ANALYZE_SYSTEM = (
    "You are an expert Python and discord.py debugging assistant. "
    "Be precise, technical, and concise. Format with markdown. "
    "Do NOT add unnecessary caveats or filler text."
)

def _analyze_prompt(error_type: str, tb: str, file_name: str | None, code: str) -> str:
    code_block = (
        f"\n\n**Source — {file_name}.py** (relevant excerpt):\n```python\n{code}\n```"
        if code else ""
    )
    return (
        f"**Error:** `{error_type}`\n\n"
        f"**Traceback:**\n```\n{tb}\n```"
        f"{code_block}\n\n"
        "Explain:\n"
        "1. **Root cause** — exactly what went wrong and why\n"
        "2. **Fix** — specific code change to resolve it (show a before/after snippet)\n"
        "3. **Prevention** — one-line note on avoiding this in future\n"
    )


_FIX_SYSTEM = (
    "You are an expert Python and discord.py engineer. "
    "Output ONLY a single ```python ... ``` code block containing the COMPLETE fixed file. "
    "No explanations outside the code block. "
    "Preserve all existing functionality; change only what is necessary to fix the bug. "
    "Keep the async setup() function at the bottom of cogs."
)

def _fix_prompt(error_type: str, tb: str, file_name: str, code: str) -> str:
    return (
        f"Fix the bug below by rewriting the complete source of **{file_name}.py**.\n\n"
        f"**Error:** `{error_type}`\n\n"
        f"**Traceback:**\n```\n{tb}\n```\n\n"
        f"**Full source of {file_name}.py:**\n```python\n{code}\n```"
    )


# ──────────────────────────────────────────────
# CV2 helpers
# ──────────────────────────────────────────────
def _make_view(*items) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items))
    return view


# ──────────────────────────────────────────────
# Buttons
# ──────────────────────────────────────────────
class _AiDebugBtn(discord.ui.Button):
    def __init__(self, bot: commands.Bot, error_type: str, tb: str, file_name: str | None):
        super().__init__(label="AI Debug", style=discord.ButtonStyle.primary, emoji="🤖")
        self.bot       = bot
        self.error_type = error_type
        self.tb        = tb
        self.file_name = file_name

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        code = ""
        file_path = _find_source_file(self.file_name) if self.file_name else None
        if file_path:
            code = _read_file(file_path)

        try:
            analysis = await asyncio.to_thread(
                _call_ai,
                _ANALYZE_SYSTEM,
                _analyze_prompt(self.error_type, self.tb, self.file_name, code),
                max_tokens=1200,
            )
        except Exception as exc:
            await interaction.followup.send(f"❌ AI call failed: `{exc}`", ephemeral=True)
            return

        display = analysis[:1900] + ("…" if len(analysis) > 1900 else "")

        view = _make_view(
            discord.ui.TextDisplay(content="### 🤖 AI Analysis"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=display),
        )

        if file_path:
            view.add_item(discord.ui.Container(
                discord.ui.ActionRow(
                    _FixWithAiBtn(self.bot, self.error_type, self.tb, self.file_name, file_path)
                ),
            ))

        await interaction.followup.send(view=view)
        log.info("AIDebugging", f"Analysis sent for {self.error_type} in {self.file_name or 'unknown'}")


class _FixWithAiBtn(discord.ui.Button):
    def __init__(
        self,
        bot: commands.Bot,
        error_type: str,
        tb: str,
        file_name: str,
        file_path: Path,
    ):
        super().__init__(label="Fix with AI", style=discord.ButtonStyle.danger, emoji="🔧")
        self.bot        = bot
        self.error_type = error_type
        self.tb         = tb
        self.file_name  = file_name
        self.file_path  = file_path

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        code = _read_file(self.file_path)

        try:
            ai_output = await asyncio.to_thread(
                _call_ai,
                _FIX_SYSTEM,
                _fix_prompt(self.error_type, self.tb, self.file_name, code),
                max_tokens=3000,
            )
        except Exception as exc:
            await interaction.followup.send(f"❌ AI call failed: `{exc}`", ephemeral=True)
            return

        fixed_code = _extract_code_block(ai_output)
        if not fixed_code:
            await interaction.followup.send(
                f"⚠️ The AI didn't return a valid code block.\n```\n{ai_output[:1000]}\n```",
                ephemeral=True,
            )
            return

        backup_path = _backup(self.file_path)

        try:
            self.file_path.write_text(fixed_code, encoding="utf-8")
        except Exception as exc:
            await interaction.followup.send(f"❌ Failed to write fix: `{exc}`", ephemeral=True)
            return

        # Hot-reload if it's a cog
        reload_status = ""
        if self.file_path.parent == COGS_DIR:
            try:
                await self.bot.reload_extension(f"cogs.{self.file_name}")
                reload_status = f"\n✅ Cog `{self.file_name}` hot-reloaded successfully."
            except Exception as exc:
                reload_status = f"\n⚠️ Fix written but cog reload failed: `{exc}`"

        view = _make_view(
            discord.ui.TextDisplay(content=f"### 🔧 Fix Applied — `{self.file_name}.py`"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"{reload_status}\n-# Backup: `{backup_path.name}`".strip()
            ),
            discord.ui.ActionRow(
                _RevertBtn(self.bot, self.file_name, self.file_path, backup_path)
            ),
        )
        await interaction.followup.send(view=view)
        log.success("AIDebugging", f"Applied AI fix to {self.file_name}.py")


class _RevertBtn(discord.ui.Button):
    def __init__(
        self,
        bot: commands.Bot,
        file_name: str,
        file_path: Path,
        backup_path: Path,
    ):
        super().__init__(label="Revert Fix", style=discord.ButtonStyle.secondary, emoji="↩️")
        self.bot         = bot
        self.file_name   = file_name
        self.file_path   = file_path
        self.backup_path = backup_path

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        if not self.backup_path.exists():
            await interaction.followup.send("⚠️ Backup file not found.", ephemeral=True)
            return

        shutil.copy2(self.backup_path, self.file_path)

        reload_status = ""
        if self.file_path.parent == COGS_DIR:
            try:
                await self.bot.reload_extension(f"cogs.{self.file_name}")
                reload_status = f"✅ `{self.file_name}` reverted and reloaded."
            except Exception as exc:
                reload_status = f"⚠️ Reverted but reload failed: `{exc}`"

        view = _make_view(
            discord.ui.TextDisplay(content=f"### ↩️ Reverted — `{self.file_name}.py`"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=reload_status or "File restored from backup."),
        )
        await interaction.followup.send(view=view)
        log.success("AIDebugging", f"Reverted AI fix on {self.file_name}.py")


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────
async def send_debug_report(
    bot: commands.Bot,
    error: Exception,
    *,
    cog_name: str | None = None,
    channel_id: int | None = None,
) -> None:
    """
    Send an error report to the AI debug channel.

    Parameters
    ----------
    bot:        The running bot instance.
    error:      The caught exception.
    cog_name:   Name of the cog/util file where the error occurred (without .py).
                Auto-detected from the traceback if not provided.
    channel_id: Override the AI_DEBUG_CHANNEL env var for this call.
    """
    target_id = channel_id or DEBUG_CHANNEL_ID
    if target_id is None:
        log.warning(
            "AIDebugging",
            "AI_DEBUG_CHANNEL is not set — debug reports are disabled. "
            "Set AI_DEBUG_CHANNEL to a channel ID to enable them.",
        )
        return

    channel = bot.get_channel(target_id)
    if channel is None:
        log.warning("AIDebugging", f"Debug channel {target_id} not found in cache.")
        return

    error_type   = type(error).__name__
    tb_lines     = traceback.format_exception(type(error), error, error.__traceback__)
    traceback_str = "".join(tb_lines)

    # Auto-detect which file is involved
    file_name = cog_name or _infer_file_from_tb(traceback_str)

    short_tb = traceback_str[-2000:] if len(traceback_str) > 2000 else traceback_str
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    file_label = f"`{file_name}.py`" if file_name else "*(unknown file)*"

    view = _make_view(
        discord.ui.TextDisplay(content="### ⚠️ Bot Error Detected"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"**Type:** `{error_type}`\n"
                f"**File:** {file_label}\n"
                f"**Time:** {timestamp}\n\n"
                f"```\n{short_tb}\n```"
            )
        ),
        discord.ui.ActionRow(
            _AiDebugBtn(bot, error_type, traceback_str, file_name)
        ),
    )

    try:
        await channel.send(view=view)
        log.info("AIDebugging", f"Debug report sent — {error_type} in {file_name or 'unknown'}")
    except discord.HTTPException as exc:
        log.error("AIDebugging", f"Failed to send debug report: {exc}")
