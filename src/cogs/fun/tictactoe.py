import discord
from discord.ext import commands
from typing import List
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

# -----------------------------
# MESSAGE DICTIONARY
# -----------------------------
MESSAGES = load_locales("cogs.fun", "tictactoe")

msg = make_flat_msg(MESSAGES)


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
                nyt_view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=msg(interaction, "not_your_turn", mention=interaction.user.mention)
                    )
                )
                nyt_view.add_item(container)
                return await interaction.response.send_message(view=nyt_view, ephemeral=True)

            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"{player2.mention}"

        # O turn
        else:
            if interaction.user != player2:
                nyt_view = discord.ui.LayoutView()
                container = discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=msg(interaction, "not_your_turn", mention=interaction.user.mention)
                    )
                )
                nyt_view.add_item(container)
                return await interaction.response.send_message(view=nyt_view, ephemeral=True)

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
    """TicTacToe game with bilingual support."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=["ttt"],
        help=CMDS.help("tictactoe"),
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