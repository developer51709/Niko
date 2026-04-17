from __future__ import annotations

import asyncio
from typing import Optional, Union

import discord
from discord.ui import View, Button
from discord.ext import commands
from config.emojis import get_emoji

RED = get_emoji('C4Red')
BLUE = get_emoji('C4Yellow')
BLANK = get_emoji('C4Empty')

class ConnectFourView(View):
    def __init__(self, game: ConnectFour):
        super().__init__(timeout=None)
        self.game = game
        for index, emoji in enumerate(self.game._controls):
            self.add_item(ConnectFourButton(index, emoji))

class ConnectFourButton(Button):
    def __init__(self, column: int, emoji: str):
        super().__init__(style=discord.ButtonStyle.primary, emoji=emoji)
        self.column = column

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.game.turn:
            return await interaction.response.send_message("It's not your turn!", ephemeral=True)
        
        if self.view.game.board[0][self.column] != BLANK:
            return await interaction.response.send_message("This column is full!", ephemeral=True)
        
        self.view.game.place_move(self.column, interaction.user)
        status = self.view.game.is_game_over()
        embed = self.view.game.make_embed(status=status)
        await interaction.response.defer() 
        await interaction.message.edit(embed=embed, content=self.view.game.board_string(), view=self.view if not status else None)

class ConnectFour:
    def __init__(self, *, red: discord.User, blue: discord.User) -> None:
        self.red_player = red
        self.blue_player = blue
        self.board: list[list[str]] = [[BLANK for _ in range(7)] for _ in range(6)]
        self._controls: tuple[str, ...] = (get_emoji("White1"), get_emoji("White2"), get_emoji("White3"), get_emoji("White4"), get_emoji("White5"), get_emoji("White6"), get_emoji("White7"))
        self.turn = self.red_player
        self.winner: Optional[discord.User] = None
        self.player_to_emoji: dict[discord.User, str] = {self.red_player: RED, self.blue_player: BLUE}
        self.emoji_to_player: dict[str, discord.User] = {v: k for k, v in self.player_to_emoji.items()}
        
    def make_embed(self, *, status: bool) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.random())
        if not status:
            embed.description = f"**Turn:** {self.turn.name}\n**Piece:** {self.player_to_emoji[self.turn]}"
        else:
            status_ = f"{self.winner} won!" if self.winner else "Tie"
            embed.description = f"**Game over**\n{status_}"
        return embed

    def board_string(self) -> str:
        board = f"{get_emoji('C4Top1')}{get_emoji('C4Top2')}{get_emoji('C4Top3')}{get_emoji('C4Top4')}{get_emoji('C4Top5')}{get_emoji('C4Top6')}{get_emoji('C4Top7')}\n"
        for row in self.board:
            board += "".join(row) + "\n"
        return board


    def place_move(self, column: int, user: discord.User) -> None:
        for x in range(5, -1, -1):
            if self.board[x][column] == BLANK:
                self.board[x][column] = self.player_to_emoji[user]
                break
        self.turn = self.red_player if user == self.blue_player else self.blue_player

    def is_game_over(self) -> bool:
        if all(i != BLANK for i in self.board[0]):
            return True
        for x in range(6):
            for i in range(4):
                if self.board[x][i] == self.board[x][i+1] == self.board[x][i+2] == self.board[x][i+3] != BLANK:
                    self.winner = self.emoji_to_player[self.board[x][i]]
                    return True
        for x in range(3):
            for i in range(7):
                if self.board[x][i] == self.board[x+1][i] == self.board[x+2][i] == self.board[x+3][i] != BLANK:
                    self.winner = self.emoji_to_player[self.board[x][i]]
                    return True
        for x in range(3):
            for i in range(4):
                if self.board[x][i] == self.board[x+1][i+1] == self.board[x+2][i+2] == self.board[x+3][i+3] != BLANK:
                    self.winner = self.emoji_to_player[self.board[x][i]]
                    return True
        for x in range(5, 2, -1):
            for i in range(4):
                if self.board[x][i] == self.board[x-1][i+1] == self.board[x-2][i+2] == self.board[x-3][i+3] != BLANK:
                    self.winner = self.emoji_to_player[self.board[x][i]]
                    return True
        return False

    async def start(self, ctx: commands.Context[commands.Bot]):
        embed = self.make_embed(status=False)
        self.view = ConnectFourView(self)
        self.message = await ctx.send(embed=embed, content=self.board_string(), view=self.view)

class ConnectFourCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="connectfour",
        aliases=["connect4", "c4"],
        help="{ 'en': 'Play a game of Connect Four with another user.', 'de': 'Spiele ein Spiel Connect Four mit einem anderen Benutzer.' }",
    )
    async def connect_four(self, ctx: commands.Context[commands.Bot], user: discord.User):
        if user == ctx.author:
            return await ctx.send("You can't play against yourself!")
        if user.bot:
            return await ctx.send("You can't play against a bot!")
        game = ConnectFour(red=ctx.author, blue=user)
        await game.start(ctx)


async def setup(bot: commands.Bot):
    await bot.add_cog(ConnectFourCog(bot))