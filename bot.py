import os
import discord
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from jam_commands import JamCommands
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
    await bot.add_cog(JamPolls(bot))
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Australia/Melbourne"))

    jam_polls = bot.get_cog("JamPolls")
    await jam_polls.add_scheduled_polls(scheduler)
    scheduler.start()



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
