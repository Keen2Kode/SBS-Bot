import os
from typing import List
import discord
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from jam_commands import JamCommands
from jam_genre import JamGenre
from jam_polls import JamPolls
from channels import Channels

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.guilds = True
intents.guild_messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)



@bot.event
async def on_ready():
    print(f'{bot.user} is ready')
    await bot.add_cog(JamCommands(bot))
    await bot.add_cog(JamPolls(bot, genres()))
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Australia/Melbourne"))

    jam_polls = bot.get_cog("JamPolls")
    await jam_polls.add_scheduled_polls(scheduler)
    scheduler.start()

def genres() -> List[JamGenre]:
    channels = Channels(bot)
    weekly_jam_embed = (
        "https://media.discordapp.net/attachments/1385873633217482763/"
        "1392466068928200734/image.png?ex=688df515&is=688ca395&hm=c4e7f24267"
        "76a25d9d9918fed2d3dc343e7e66e39a81fd811ae9317c8672c1db&=&format=webp"
        "&quality=lossless&width=671&height=839"
    )

    jazz = JamGenre("jazz", "Sunday (12-3pm)", weekly_jam_embed, channels, CronTrigger(day_of_week='mon', hour=12, minute=0))
    rock = JamGenre("rock", "Saturday (3-6pm)", weekly_jam_embed, channels, CronTrigger(day_of_week='mon', hour=12, minute=0))
    pop = JamGenre("pop", "Saturday (12-3pm)", weekly_jam_embed, channels, CronTrigger(day_of_week='mon', hour=12, minute=0))
    girls = JamGenre("girls", "Sunday (3-6pm)", weekly_jam_embed, channels, CronTrigger(day="1st sun", hour=5, minute=0))

    return [jazz, rock, pop, girls]



@bot.check
async def globally_block_commands(ctx):
    if ctx.channel and ctx.channel in Channels(bot).bot_channels():
        return True
    raise commands.CheckFailure("Please use this bot only in the designated bot channels.")

# only let the bot command error send a message
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(str(error))
    else:
        raise error  # Let other errors surface normally
    



bot.run(TOKEN)
