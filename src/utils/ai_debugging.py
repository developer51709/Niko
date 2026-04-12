"""
experimental ai debugging tool
this is designed to debug and even fix the code using the ai
How it works:
1. an error is thrown
2. the bot sends a message to the designated channel with the error with the traceback and a "AI Debug" button
3. the user can click the button to send the error to the ai
4. the ai will then analyze the error and the code and then send a message explaining the error and how to fix it
5. the user can click the "Fix with AI" button to have the ai automatically fix the bots code and restart the affected cog(s)
6. all AI fixes can be reversed by the user
"""
import discord
from discord.ext import commands