import discord
from discord.ext import commands

class JamCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def jam_songs(self, ctx):
        await ctx.send("Here's the [song list.](https://docs.google.com/spreadsheets/d/1B8CsbHZFHbz49ceJteTEL4s1_xq1G9WrqjtV0cBO8aw/edit?usp=sharing)")