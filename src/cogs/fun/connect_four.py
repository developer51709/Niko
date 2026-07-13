"""
Connect Four — cv2 LayoutView edition
──────────────────────────────────────
• Board + status displayed in a cv2 Container (no embed, no raw content)
• Column buttons split across two ActionRows (4 + 3) — cv2 max 5/row
• Accent colour follows the current player (red / gold / green / grey)
• Full bilingual support — English and German
"""

from __future__ import annotations

from typing import Optional

import discord
from discord.ext import commands

from config.emojis import get_emoji

# ───────────────────────────────────────────────────
#  PIECE EMOJIS
# ───────────────────────────────────────────────────

RED   = get_emoji("C4Red")
BLUE  = get_emoji("C4Yellow")
BLANK = get_emoji("C4Empty")

_CONTROLS = (
    get_emoji("White1"), get_emoji("White2"), get_emoji("White3"),
    get_emoji("White4"), get_emoji("White5"), get_emoji("White6"),
    get_emoji("White7"),
)

_TOP_ROW = (
    get_emoji("C4Top1"), get_emoji("C4Top2"), get_emoji("C4Top3"),
    get_emoji("C4Top4"), get_emoji("C4Top5"), get_emoji("C4Top6"),
    get_emoji("C4Top7"),
)

# ───────────────────────────────────────────────────
#  LOCALISATION
# ───────────────────────────────────────────────────

_UI: dict[str, dict[str, str]] = {
    "en": {
        "title":        "Connect Four",
        "vs":           "{red} **{rname}**  vs  {blue} **{bname}**",
        "turn":         "{emoji1} **{name}**'s turn  {emoji2}",
        "game_over":    "**Game Over**",
        "winner":       "🎉 **{name}** wins!",
        "tie":          "🤝 It's a tie!",
        "not_your_turn":"It's not your turn!",
        "col_full":     "That column is full!",
        "vs_self":      "You can't play against yourself!",
        "vs_bot":       "You can't play against a bot!",
    },
    "de": {
        "title":        "Vier Gewinnt",
        "vs":           "{red} **{rname}**  vs  {blue} **{bname}**",
        "turn":         "{emoji1} **{name}** ist dran  {emoji2}",
        "game_over":    "**Spiel vorbei**",
        "winner":       "🎉 **{name}** gewinnt!",
        "tie":          "🤝 Unentschieden!",
        "not_your_turn":"Du bist nicht dran!",
        "col_full":     "Diese Spalte ist voll!",
        "vs_self":      "Du kannst nicht gegen dich selbst spielen!",
        "vs_bot":       "Du kannst nicht gegen einen Bot spielen!",
    },
}


def _t(lang: str, key: str, **kw) -> str:
    text = _UI.get(lang, _UI["en"]).get(key, _UI["en"].get(key, key))
    return text.format(**kw) if kw else text


def get_lang(ctx_or_interaction=None) -> str:
    guild = None
    if isinstance(ctx_or_interaction, commands.Context):
        guild = ctx_or_interaction.guild
    elif isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
    elif isinstance(ctx_or_interaction, discord.Guild):
        guild = ctx_or_interaction
    if guild and guild.preferred_locale:
        if str(guild.preferred_locale).lower().startswith("de"):
            return "de"
        if str(guild.preferred_locale).lower().startswith("es"):
            return "es"
    return "en"


# ───────────────────────────────────────────────────
#  GAME LOGIC
# ───────────────────────────────────────────────────

class ConnectFour:
    def __init__(self, *, red: discord.Member, blue: discord.Member) -> None:
        self.red_player  = red
        self.blue_player = blue
        self.board: list[list[str]] = [[BLANK] * 7 for _ in range(6)]
        self.turn        = red
        self.winner: Optional[discord.Member] = None
        self.is_done     = False

        self._piece   = {red: RED,  blue: BLUE}
        self._by_piece = {RED: red, BLUE: blue}

    # ── display helpers ────────────────────────────

    def board_string(self) -> str:
        top  = "".join(_TOP_ROW)
        rows = "\n".join("".join(row) for row in self.board)
        return f"{top}\n{rows}"

    def status_text(self, lang: str) -> str:
        if not self.is_done:
            return _t(
                lang, "turn",
                name=self.turn.display_name,
                emoji1=get_emoji("icon_play"),
                emoji2=self._piece[self.turn],
            )
        if self.winner:
            return (
                f"{_t(lang, 'game_over')}\n"
                f"{_t(lang, 'winner', name=self.winner.display_name)}"
            )
        return f"{_t(lang, 'game_over')}\n{_t(lang, 'tie')}"

    def accent_colour(self) -> discord.Colour:
        if self.is_done:
            return discord.Colour(0x57F287) if self.winner else discord.Colour(0x5865F2)
        return discord.Colour(0xFF0000) if self.turn == self.red_player else discord.Colour(0xFFD700)

    # ── game logic ─────────────────────────────────

    def place_move(self, column: int, user: discord.Member) -> None:
        for row in range(5, -1, -1):
            if self.board[row][column] == BLANK:
                self.board[row][column] = self._piece[user]
                break
        self.turn = self.red_player if user == self.blue_player else self.blue_player

    def check_game_over(self) -> bool:
        """Check win / tie; sets self.winner and self.is_done. Returns is_done."""
        # Tie (top row full)
        if all(cell != BLANK for cell in self.board[0]):
            self.is_done = True
            return True

        b = self.board

        # Horizontal
        for r in range(6):
            for c in range(4):
                if b[r][c] == b[r][c+1] == b[r][c+2] == b[r][c+3] != BLANK:
                    self.winner  = self._by_piece[b[r][c]]
                    self.is_done = True
                    return True

        # Vertical
        for r in range(3):
            for c in range(7):
                if b[r][c] == b[r+1][c] == b[r+2][c] == b[r+3][c] != BLANK:
                    self.winner  = self._by_piece[b[r][c]]
                    self.is_done = True
                    return True

        # Diagonal ↘
        for r in range(3):
            for c in range(4):
                if b[r][c] == b[r+1][c+1] == b[r+2][c+2] == b[r+3][c+3] != BLANK:
                    self.winner  = self._by_piece[b[r][c]]
                    self.is_done = True
                    return True

        # Diagonal ↙
        for r in range(3, 6):
            for c in range(4):
                if b[r][c] == b[r-1][c+1] == b[r-2][c+2] == b[r-3][c+3] != BLANK:
                    self.winner  = self._by_piece[b[r][c]]
                    self.is_done = True
                    return True

        return False


# ───────────────────────────────────────────────────
#  CV2 BUTTON
# ───────────────────────────────────────────────────

class ConnectFourButton(discord.ui.Button):
    def __init__(self, column: int, emoji: str):
        super().__init__(style=discord.ButtonStyle.primary, emoji=emoji)
        self.column = column

    async def callback(self, interaction: discord.Interaction):
        game: ConnectFour = self.view.game
        lang: str         = self.view.lang
        msg_id = interaction.message.id
        await interaction.response.defer()

        # Wrong player
        if interaction.user != game.turn:
            err = _error_view(_t(lang, "not_your_turn"))
            try:
                return await interaction.followup.send(view=err, ephemeral=True)
            except Exception as e:
                print(f"Connect four error: {e}")

        # Column full
        if game.board[0][self.column] != BLANK:
            err = _error_view(_t(lang, "col_full"))
            try:
                return await interaction.followup.send(view=err, ephemeral=True)
            except Exception as e:
                print(f"Connect four error: {e}")

        game.place_move(self.column, interaction.user)
        game.check_game_over()

        new_view = ConnectFourView(game, lang)
        try:
            await interaction.followup.edit_message(view=new_view, message_id=msg_id)
        except Exception as e:
            print(f"Connect four error: {e}")


# ───────────────────────────────────────────────────
#  CV2 LAYOUT VIEW
# ───────────────────────────────────────────────────

def _error_view(text: str) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('icon_cross')} {text}"),
        accent_colour=discord.Colour(0xED4245),
    ))
    return view


class ConnectFourView(discord.ui.LayoutView):
    """
    cv2 LayoutView for a Connect Four game.

    Structure:
      Container:
        TextDisplay  — title
        Separator
        TextDisplay  — "Red vs Blue" players line
        Separator
        TextDisplay  — board grid
        Separator
        TextDisplay  — turn / game-over status
        [Separator + ActionRow x2 with column buttons — only while game is active]
    """

    def __init__(self, game: ConnectFour, lang: str = "en"):
        super().__init__(timeout=None)
        self.game = game
        self.lang = lang
        self._build()

    def _build(self):
        lang = self.lang
        game = self.game

        players_line = _t(
            lang, "vs",
            red=RED,  rname=game.red_player.display_name,
            blue=BLUE, bname=game.blue_player.display_name,
        )

        items: list = [
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_games')} {_t(lang, 'title')}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=players_line),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=game.board_string()),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=game.status_text(lang)),
        ]

        if not game.is_done:
            items.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
            # Row 1: columns 0-3
            row1 = discord.ui.ActionRow(
                *[ConnectFourButton(c, _CONTROLS[c]) for c in range(4)]
            )
            # Row 2: columns 4-6
            row2 = discord.ui.ActionRow(
                *[ConnectFourButton(c, _CONTROLS[c]) for c in range(4, 7)]
            )
            items.append(row1)
            items.append(row2)

        container = discord.ui.Container(*items, accent_colour=game.accent_colour())
        self.add_item(container)


# ───────────────────────────────────────────────────
#  COG
# ───────────────────────────────────────────────────

class ConnectFourCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="connectfour",
        aliases=["connect4", "c4"],
        help="{ 'en': 'challenge someone to Connect Four 🎮', 'de': 'fordere jemanden zu Vier Gewinnt heraus 🎮' }",
    )
    async def connect_four(self, ctx: commands.Context, opponent: discord.Member):
        lang = get_lang(ctx)

        if opponent == ctx.author:
            err = _error_view(_t(lang, "vs_self"))
            return await ctx.send(view=err)

        if opponent.bot:
            err = _error_view(_t(lang, "vs_bot"))
            return await ctx.send(view=err)

        game = ConnectFour(red=ctx.author, blue=opponent)
        view = ConnectFourView(game, lang)
        await ctx.send(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(ConnectFourCog(bot))
