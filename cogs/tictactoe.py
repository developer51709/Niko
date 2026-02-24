import discord
from discord.ext import commands
from typing import List

# personality mode: "normal" or "cafe"
PERSONALITY = "cafe"

# -----------------------------
# MESSAGE DICTIONARY
# -----------------------------
MESSAGES = {
    "normal": {
        "en": {
            "not_your_turn": "{mention}, it is not your turn.",
            "winner_x": "{p1} is the winner!",
            "winner_o": "{p2} is the winner!",
            "tie": "It's a tie!",
            "mention_user": "Please mention a user.",
            "cannot_play_self": "You cannot play against yourself.",
            "game_start": "{opponent}, your game has started!",
        },
        "de": {
            "not_your_turn": "{mention}, du bist noch nicht dran.",
            "winner_x": "{p1} hat gewonnen!",
            "winner_o": "{p2} hat gewonnen!",
            "tie": "Unentschieden!",
            "mention_user": "Bitte erwähne einen Benutzer.",
            "cannot_play_self": "Du kannst nicht gegen dich selbst spielen.",
            "game_start": "{opponent}, euer Spiel hat begonnen!",
        },
    },

    "cafe": {
        "en": {
            "not_your_turn": "hey {mention}, it’s not your turn yet ☕😔",
            "winner_x": "yaaay {p1} wins — brewed that victory perfectly ☕✨",
            "winner_o": "yaaay {p2} wins — cozy lil champion ☕🌿",
            "tie": "it’s a tie… like two pastries fighting for the last crumb 🍰😔",
            "mention_user": "bestie pls mention someone to play with ☕💛",
            "cannot_play_self": "you can’t play against yourself silly ☕😆",
            "game_start": "{opponent}, your cozy café match has begun ☕🎮",
        },
        "de": {
            "not_your_turn": "hey {mention}, du bist noch nicht dran ☕😔",
            "winner_x": "yaaay {p1} gewinnt — perfekt aufgebrüht ☕✨",
            "winner_o": "yaaay {p2} gewinnt — kleines café‑champion ☕🌿",
            "tie": "unentschieden… wie zwei kuchenstücke im kampf 🍰😔",
            "mention_user": "liebchen, bitte erwähne jemanden zum spielen ☕💛",
            "cannot_play_self": "du kannst nicht gegen dich selbst spielen hehe ☕😆",
            "game_start": "{opponent}, euer gemütliches café‑spiel beginnt ☕🎮",
        },
    },

    # future personalities can be added here
}

# -----------------------------
# LANGUAGE + PERSONALITY HELPERS
# -----------------------------
def get_lang(ctx):
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        if str(ctx.guild.preferred_locale).lower().startswith("de"):
            return "de"
    return "en"


def get_personality():
    return PERSONALITY if PERSONALITY in MESSAGES else "normal"


def msg(ctx, key, **kwargs):
    personality = get_personality()
    lang = get_lang(ctx)

    block = MESSAGES.get(personality, {}).get(lang, {})
    text = block.get(key)

    if text is None:
        text = MESSAGES.get(personality, {}).get("en", {}).get(key)

    if text is None:
        text = MESSAGES["normal"].get(lang, {}).get(key)

    if text is None:
        text = MESSAGES["normal"]["en"].get(key, key)

    return text.format(**kwargs) if kwargs else text


# -----------------------------
# TIC TAC TOE BUTTON
# -----------------------------
class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        global player1, player2

        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]

        if state in (view.X, view.O):
            return

        # X turn
        if view.current_player == view.X:
            if interaction.user != player1:
                embed = discord.Embed(
                    color=discord.Color.yellow(),
                    description=msg(interaction, "not_your_turn", mention=interaction.user.mention)
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"{player2.mention}"

        # O turn
        else:
            if interaction.user != player2:
                embed = discord.Embed(
                    color=discord.Color.yellow(),
                    description=msg(interaction, "not_your_turn", mention=interaction.user.mention)
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"{player1.mention}"

        # Check winner
        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = msg(interaction, "winner_x", p1=player1.mention)
            elif winner == view.O:
                content = msg(interaction, "winner_o", p2=player2.mention)
            else:
                content = msg(interaction, "tie")

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


# -----------------------------
# TIC TAC TOE VIEW
# -----------------------------
class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [[0, 0, 0] for _ in range(3)]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self):
        # rows
        for row in self.board:
            s = sum(row)
            if s == 3:
                return self.O
            if s == -3:
                return self.X

        # columns
        for col in range(3):
            s = self.board[0][col] + self.board[1][col] + self.board[2][col]
            if s == 3:
                return self.O
            if s == -3:
                return self.X

        # diagonals
        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        if diag == -3:
            return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        if diag == -3:
            return self.X

        # tie
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


# -----------------------------
# COG
# -----------------------------
class tictactoe(commands.Cog):
    """TicTacToe game with cozy café personality + bilingual support."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=["ttt"],
        help="play a cozy tic‑tac‑toe match ☕ | spiele tictactoe mit einem nutzer"
    )
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def tictactoe(self, ctx, member: discord.Member = None):
        if member is None:
            return await ctx.reply(msg(ctx, "mention_user"))

        if member == ctx.author:
            return await ctx.reply(msg(ctx, "cannot_play_self"))

        global player1, player2
        player1 = ctx.author
        player2 = member

        await ctx.reply(msg(ctx, "game_start", opponent=member.mention), view=TicTacToe())


async def setup(bot):
    await bot.add_cog(tictactoe(bot))