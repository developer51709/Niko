"""
AI Debugging Tool for Niko Bot
================================
How it works:
1. An error is thrown anywhere in the bot
2. `send_debug_report()` posts the error + traceback to the designated debug
   channel with an "AI Debug" button
3. The developer clicks "AI Debug" — the AI analyzes the error and the
   relevant source file and replies with an explanation + fix suggestion
4. The developer clicks "Fix with AI" — the AI rewrites the affected cog
   file, a backup is saved, and the cog is hot-reloaded
5. If the fix is wrong the developer clicks "Revert Fix" to restore the
   backup instantly
"""

import os
import re
import sys
import shutil
import asyncio
import inspect
import textwrap
import traceback
import datetime
from pathlib import Path
from utils.ai_nikoapi import generate_reply_nikoapi

import discord
from discord.ext import commands
from utils import logging

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
DEBUG_CHANNEL_ID: int | None = (
    int(os.environ["AI_DEBUG_CHANNEL"])
    if os.environ.get("AI_DEBUG_CHANNEL", "").strip().isdigit()
    else None
)

COGS_DIR = Path("src/cogs")
BACKUP_DIR = Path("data/ai_debug_backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def _cog_file_for(cog_name: str) -> Path | None:
    """Return the source Path for a cog name, or None if unknown."""
    candidate = COGS_DIR / f"{cog_name}.py"
    return candidate if candidate.exists() else None


def _read_file_safe(path: Path, max_chars: int = 6000) -> str:
    try:
        text = path.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n... [truncated — {len(text)} chars total]"
        return text
    except Exception as exc:
        return f"<could not read file: {exc}>"


def _backup_cog(cog_name: str) -> Path | None:
    src = _cog_file_for(cog_name)
    if src is None:
        return None
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"{cog_name}_{ts}.py.bak"
    shutil.copy2(src, dest)
    return dest


def _latest_backup(cog_name: str) -> Path | None:
    backups = sorted(BACKUP_DIR.glob(f"{cog_name}_*.py.bak"), reverse=True)
    return backups[0] if backups else None


def _extract_code_block(text: str) -> str | None:
    """Pull the first ```python … ``` block from AI output."""
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None


def _container(*items) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(*items))
    return view


# ──────────────────────────────────────────────
# AI calls (sync — run in executor)
# ──────────────────────────────────────────────
def _ai_analyze(error_type: str, traceback_str: str, cog_name: str | None, code: str) -> str:
    code_section = f"\n\nRelevant source code ({cog_name}.py):\n```python\n{code}\n```" if code else ""

    prompt = (
        "You are an expert Python / discord.py debugging assistant.\n"
        "Analyze this error and explain:\n"
        "1. What caused it (be specific about the line / root cause)\n"
        "2. How to fix it (provide a clear, actionable solution)\n"
        "Keep the response concise — under 400 words.\n\n"
        f"Error type: {error_type}\n\n"
        f"Traceback:\n```\n{traceback_str}\n```"
        f"{code_section}"
    )

    # use the nikoapi to generate the response
    bot = commands.bot
    user_id = int(1484653109576732692)
    server = "Internal AI Debugging"
    username = "System Debug Handler"
    response = generate_reply_nikoapi(bot, user_id, server, prompt, username, prompt)
    
    return response


def _ai_fix(error_type: str, traceback_str: str, cog_name: str, code: str) -> str:
    prompt = (
        "You are an expert Python / discord.py engineer.\n"
        "Fix the bug described below by rewriting the COMPLETE source file.\n"
        "Rules:\n"
        "- Output ONLY the fixed Python code inside a single ```python … ``` block.\n"
        "- Do NOT add explanations outside the code block.\n"
        "- Preserve all existing functionality; change only what is necessary.\n"
        "- Keep the async setup() function at the bottom.\n\n"
        f"Error type: {error_type}\n\n"
        f"Traceback:\n```\n{traceback_str}\n```\n\n"
        f"Full source of {cog_name}.py:\n```python\n{code}\n```"
    )

    # use the nikoapi to generate the response
    bot = commands.bot
    user_id = int(1484653109576732692)
    server = "Internal AI Debugging"
    username = "System Debug Handler"
    response = generate_reply_nikoapi(bot, user_id, server, prompt, username, prompt)
    
    return response


# ──────────────────────────────────────────────
# Discord Views
# ──────────────────────────────────────────────
class _AnalysisView(discord.ui.ActionRow):
    """View shown after the AI has analyzed the error — offers 'Fix with AI'."""

    def __init__(self, bot: commands.Bot, error_type: str, traceback_str: str, cog_name: str | None, analysis: str):
        super().__init__()
        self.bot = bot
        self.error_type = error_type
        self.traceback_str = traceback_str
        self.cog_name = cog_name
        self.analysis = analysis

        if cog_name and _cog_file_for(cog_name):
            fix_btn = discord.ui.Button(
                label="Fix with AI",
                style=discord.ButtonStyle.danger,
                emoji="🔧",
                custom_id="fix_with_ai",
            )
            fix_btn.callback = self._fix_callback
            self.add_item(fix_btn)

    async def _fix_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        cog_name = self.cog_name
        cog_file = _cog_file_for(cog_name)
        if cog_file is None:
            await interaction.followup.send("⚠️ Could not locate the cog source file.", ephemeral=True)
            return

        code = _read_file_safe(cog_file)

        loop = asyncio.get_event_loop()
        try:
            ai_output = await loop.run_in_executor(
                None, _ai_fix, self.error_type, self.traceback_str, cog_name, code
            )
        except Exception as exc:
            await interaction.followup.send(f"❌ AI call failed: `{exc}`", ephemeral=True)
            return

        fixed_code = _extract_code_block(ai_output)
        if not fixed_code:
            await interaction.followup.send(
                f"⚠️ The AI didn't return a valid code block. Raw output:\n```\n{ai_output[:1500]}\n```",
                ephemeral=True,
            )
            return

        backup_path = _backup_cog(cog_name)
        try:
            cog_file.write_text(fixed_code, encoding="utf-8")
        except Exception as exc:
            await interaction.followup.send(f"❌ Failed to write fix: `{exc}`", ephemeral=True)
            return

        try:
            await self.bot.reload_extension(f"cogs.{cog_name}")
            reload_status = f"✅ Cog `{cog_name}` reloaded successfully."
        except Exception as exc:
            reload_status = f"⚠️ Fix applied but cog reload failed: `{exc}`"

        view = _container(
            discord.ui.TextDisplay(content=f"### 🔧 Fix Applied — `{cog_name}.py`"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"{reload_status}\n-# Backup saved to `{backup_path.name}`"),
        )

        revert_view = _RevertView(cog_name=cog_name, backup_path=backup_path, bot=self.bot)
        await interaction.followup.send(view=view, components=revert_view)
        logging.success("AIDebugging", f"Applied AI fix to {cog_name}.py")


class _RevertView(discord.ui.View):
    """Standalone view with a Revert button attached to the fix-applied message."""

    def __init__(self, cog_name: str, backup_path: Path, bot: commands.Bot):
        super().__init__(timeout=600)
        self.cog_name = cog_name
        self.backup_path = backup_path
        self.bot = bot

        btn = discord.ui.Button(label="Revert Fix", style=discord.ButtonStyle.secondary, emoji="↩️")
        btn.callback = self._revert_callback
        self.add_item(btn)

    async def _revert_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        cog_file = _cog_file_for(self.cog_name)
        if cog_file is None or not self.backup_path.exists():
            await interaction.followup.send("⚠️ Backup file not found.", ephemeral=True)
            return

        shutil.copy2(self.backup_path, cog_file)

        try:
            await self.bot.reload_extension(f"cogs.{self.cog_name}")
            reload_status = f"✅ Cog `{self.cog_name}` reverted and reloaded."
        except Exception as exc:
            reload_status = f"⚠️ Reverted but reload failed: `{exc}`"

        view = _container(
            discord.ui.TextDisplay(content=f"### ↩️ Fix Reverted — `{self.cog_name}.py`"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=reload_status),
        )
        await interaction.followup.send(view=view)
        self.stop()
        logging.success("AIDebugging", f"Reverted AI fix on {self.cog_name}.py")


class _DebugReportView(discord.ui.ActionRow):
    """Initial report view — has a single 'AI Debug' button."""

    def __init__(self, bot: commands.Bot, error_type: str, traceback_str: str, cog_name: str | None):
        super().__init__()
        self.bot = bot
        self.error_type = error_type
        self.traceback_str = traceback_str
        self.cog_name = cog_name

        btn = discord.ui.Button(label="AI Debug", style=discord.ButtonStyle.primary, emoji="🤖")
        btn.callback = self._debug_callback
        self.add_item(btn)

    async def _debug_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        code = ""
        if self.cog_name:
            f = _cog_file_for(self.cog_name)
            if f:
                code = _read_file_safe(f)

        loop = asyncio.get_event_loop()
        try:
            analysis = await loop.run_in_executor(
                None, _ai_analyze, self.error_type, self.traceback_str, self.cog_name, code
            )
        except Exception as exc:
            await interaction.followup.send(f"❌ AI call failed: `{exc}`", ephemeral=True)
            return

        # Trim for Discord's 2000-char limit inside a TextDisplay
        display_analysis = analysis[:1800] + ("…" if len(analysis) > 1800 else "")

        layout = _container(
            discord.ui.TextDisplay(content="### 🤖 AI Analysis"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=display_analysis),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        )

        analysis_view = _AnalysisView(
            bot=self.bot,
            error_type=self.error_type,
            traceback_str=self.traceback_str,
            cog_name=self.cog_name,
            analysis=analysis,
        )
        if analysis_view.children:
            layout.add_item(analysis_view)
        await interaction.followup.send(view=layout)


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
    cog_name:   Name of the cog where the error occurred (without .py).
                If None the AI Debug button will still appear but won't
                offer a code fix.
    channel_id: Override the AI_DEBUG_CHANNEL env var for this call.
    """
    target_id = channel_id or DEBUG_CHANNEL_ID
    if target_id is None:
        logging.warning(
            "AIDebugging",
            "AI_DEBUG_CHANNEL is not set — skipping debug report. "
            "Set this env var to a channel ID to enable AI debugging.",
        )
        return

    channel = bot.get_channel(target_id)
    if channel is None:
        logging.warning("AIDebugging", f"Channel {target_id} not found in cache.")
        return

    error_type = type(error).__name__
    tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
    traceback_str = "".join(tb_lines)
    short_tb = traceback_str[-1500:] if len(traceback_str) > 1500 else traceback_str

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    cog_line = f"`{cog_name}.py`" if cog_name else "*(unknown cog)*"

    button = _DebugReportView(
        bot=bot,
        error_type=error_type,
        traceback_str=traceback_str,
        cog_name=cog_name,
    )

    layout = _container(
        discord.ui.TextDisplay(content=f"### ⚠️ Bot Error Detected"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(
            content=(
                f"**Type:** `{error_type}`\n"
                f"**Cog:** {cog_line}\n"
                f"**Time:** {timestamp}\n\n"
                f"```\n{short_tb}\n```"
            )
        ),
        button,
    )

    try:
        await channel.send(view=layout)
        logging.info("AIDebugging", f"Debug report sent for {error_type} in {cog_name or 'unknown'}")
    except discord.HTTPException as exc:
        logging.error("AIDebugging", f"Failed to send debug report: {exc}")
