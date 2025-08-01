import discord
from discord.ext import commands

class JamCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="General info about our Open Jam sessions.")
    async def jam_info(self, ctx):
        embed = discord.Embed(
            title="🎶 Weekly Open Jam Sessions!",
            description=(
                "The Open Jams are a way to meet new people through your shared love of music. "
                "Just show up with your preferred instrument and equipment! These jams focus on a more collaborative environment, "
                "so if you're an instrument player, having some music theory knowledge is always useful — but not essential.\n\n"
                "**📊 Weekly Polls**\n"
                "Polls are posted in the respective jam channels. Vote ahead of time to get priority to play!\n\n"
                "**📍 [RMIT Creative Space](https://maps.app.goo.gl/Rwnci4ZfqceH81zX6)**\n"
                "**📄 [Jam Songs](https://docs.google.com/spreadsheets/d/1B8CsbHZFHbz49ceJteTEL4s1_xq1G9WrqjtV0cBO8aw/edit?usp=sharing)**"
            ),
            color=discord.Color.orange()
        )

        embed.set_image(url="https://media.discordapp.net/attachments/1385873633217482763/1392466068928200734/image.png?ex=688df515&is=688ca395&hm=c4e7f2426776a25d9d9918fed2d3dc343e7e66e39a81fd811ae9317c8672c1db&=&format=webp&quality=lossless&width=671&height=839")  # replace with your actual hosted image link

        await ctx.send(embed=embed)
