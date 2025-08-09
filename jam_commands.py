import discord
from discord.ext import commands
from sheet_context import SheetContext

class JamCommands(commands.Cog):
    ALLOWED_SHEETS = ["jazz", "rock", "pop"]

    def __init__(self, bot):
        self.bot = bot
        self.sheet_context = SheetContext("https://docs.google.com/spreadsheets/d/1B8CsbHZFHbz49ceJteTEL4s1_xq1G9WrqjtV0cBO8aw/edit?usp=sharing")

    @commands.command(help="General info about our Open Jam sessions.")
    async def jam_info(self, ctx):
        embed = discord.Embed(
            title="🎶 Weekly Open Jam Sessions!",
            description=(
                f"The Open Jams are a way to meet new people through your shared love of music. "
                f"Just show up with your preferred instrument and equipment! These jams focus on a more collaborative environment, "
                f"so if you're an instrument player, having some music theory knowledge is always useful — but not essential.\n\n"
                f"**📊 Weekly Polls**\n"
                f"Polls are posted in the respective jam channels. Vote ahead of time to get priority to play!\n\n"
                f"**📍 [RMIT Creative Space](https://maps.app.goo.gl/Rwnci4ZfqceH81zX6)**\n"
                f"**📄 [Jam Songs]({self.sheet_context.url})**"
            ),
            color=discord.Color.orange()
        )

        embed.set_image(url="https://media.discordapp.net/attachments/1385873633217482763/1392466068928200734/image.png?ex=688df515&is=688ca395&hm=c4e7f2426776a25d9d9918fed2d3dc343e7e66e39a81fd811ae9317c8672c1db&=&format=webp&quality=lossless&width=671&height=839")  # replace with your actual hosted image link

        await ctx.send(embed=embed)

    @commands.command(
        help="List top 10 jam songs from specified sheet (Jazz, Rock or Pop) by Vote Rank. Usage: !jam_songs <sheet_name: rock, jazz or pop> <amount: value between 1 and 10>"
    )
    async def jam_songs(self, ctx, sheet_name: str = "Jazz", sheet_amount: int = 10):
        if sheet_name.lower() not in self.ALLOWED_SHEETS:
            allowed = ", ".join(self.ALLOWED_SHEETS)
            return await ctx.send(f"Invalid sheet '{sheet_name}'. Choose one of: {allowed}.")
        
        print(sheet_amount)
        if not sheet_amount or (sheet_amount < 0 or sheet_amount > 10):
            sheet_amount = 10
            
        
        # Initialize context for the requested worksheet
        self.sheet_context.set_worksheet(sheet_name)
        # Fetch and sort records by Vote Rank descending
        records = self.sheet_context.get_all_records()
        sorted_records = sorted(
            records,
            key=lambda r: int(r.get(SheetContext.COL_VOTE_RANK, 0)),
            reverse=False
        )
        top_records = sorted_records[:sheet_amount]

        if not top_records:
            return await ctx.send(f"No songs found in sheet '{sheet_name}'.")

        embed = discord.Embed(
            title=f"🎶 Top {len(top_records)} Voted {sheet_name} Songs",
            description=f"[Song List]({self.sheet_context.url})",
            color=discord.Color.orange()
        )
        for idx, row in enumerate(top_records, start=1):
            title = row.get(SheetContext.COL_TITLE, "Untitled")
            vote_rank = row.get(SheetContext.COL_VOTE_RANK, "Missing")
            status = row.get(SheetContext.COL_STATUS, "")
            embed.add_field(
                name=f"{idx}. {title}",
                value=f"Vote Rank: {vote_rank} | Status: {status}",
                inline=False
            )

        await ctx.send(embed=embed)
