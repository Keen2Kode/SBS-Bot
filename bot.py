from datetime import timedelta
import os
from zoneinfo import ZoneInfo
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from jam_commands import JamCommands
from jam_polls import JamPolls
from channels import Channels
from calendar_context import CalendarContext
from scheduler_service import SchedulerService

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


class JamBot(commands.Bot):

    # for non async stuff and stuff that can be prepped before Discord is ready
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.members = True

        super().__init__(command_prefix='!', intents=intents)

        # persistent state
        self.timezone = ZoneInfo("Australia/Melbourne")
        self.reminder_window = timedelta(days=7)
        self.calendar_ctx = CalendarContext(self.timezone, self.reminder_window)

        # in set up hook
        self.scheduler_service: SchedulerService | None = None

    # runs exactly once per process
    # initialize async stuff
    async def setup_hook(self):
        # runs exactly once per process

        await self.add_cog(JamCommands(self))

        jam_polls = JamPolls(self)
        await self.add_cog(jam_polls)

        self.scheduler_service = SchedulerService(
            self.calendar_ctx, 
            jam_polls, 
            self.timezone,
            self.reminder_window
        )

        # don't worry about on_ready(), these are static tasks
        self.scheduler_service.start()
        self.scheduler_service.schedule_cardholder_jobs()
        self.schedule_jobs_loop.start()

    async def on_ready(self):
        print(f'{self.user} is ready')

    @tasks.loop(hours=12)
    async def schedule_jobs_loop(self):
        if not self.is_ready():
            return
        print("get next event set")

        await self.scheduler_service.sync_event_jobs()


bot = JamBot()


@bot.check
async def globally_block_commands(ctx):
    if ctx.channel and ctx.channel in Channels(bot).bot_channels():
        return True
    raise commands.CheckFailure(
        "Please use this bot only in the designated bot channels."
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(str(error))
    else:
        raise error


bot.run(TOKEN)