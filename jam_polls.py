from typing import List
import discord
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from jam_commands import JamCommands
from channels import Channels
from jam_genre import JamGenre

# load_dotenv()
# TOKEN = os.getenv("DISCORD_TOKEN")

# intents = discord.Intents.default()
# intents.message_content = True  # Required to read message content
# intents.guilds = True
# intents.guild_messages = True
# intents.members = True

# bot = commands.Bot(command_prefix='!', intents=intents)

class JamPolls(commands.Cog):

    def __init__(self, bot, genres: List[JamGenre]):
        self.bot = bot
        self.genres = genres
        self.channels = Channels(bot)




    @commands.command(name="jampoll")
    async def jam_poll_cmd(self, ctx: Context, genre_string: str = ""):
        if not ctx.author.guild_permissions.administrator:
            return

        genre_string = genre_string.lower()

        for genre in self.genres:
            if genre.name.lower() == genre_string:
                await self.jam_poll(genre)
                return

        await ctx.send(f"Unknown genre '{genre_string}'")

    @commands.command(name="committeepoll")
    async def card_holder_poll_cmd(self, ctx: Context):
        if ctx.message.author.guild_permissions.administrator:
            await self.card_holder_poll()

    @commands.command(name="cardalert1")
    async def card_holder_alert_1_cmd(self, ctx: Context):
        if ctx.message.author.guild_permissions.administrator:
            await self.card_holder_alert_1()

    @commands.command(name="cardalert2")
    async def card_holder_alert_2_cmd(self, ctx: Context):
        if ctx.message.author.guild_permissions.administrator:
            await self.card_holder_alert_2()




    async def add_scheduled_polls(self, scheduler: AsyncIOScheduler):
        common_job_kwargs = {
            "replace_existing": True,
            "misfire_grace_time": 60
        }

        for genre in self.genres:
            scheduler.add_job(self.jam_poll, genre.interval, id=f"jam_poll_{genre.name}", kwargs={"genre": genre}, **common_job_kwargs)
        # scheduler.add_job(self.jam_poll, CronTrigger(day_of_week='mon', hour=12, minute=0), id="jam_poll", **common_job_kwargs)
        scheduler.add_job(self.card_holder_poll, CronTrigger(day_of_week='mon', hour=12, minute=0), id="card_holder_poll", **common_job_kwargs)
        scheduler.add_job(self.card_holder_alert_1, CronTrigger(day_of_week='thu', hour=18, minute=0), id="card_holder_alert_1", **common_job_kwargs)
        scheduler.add_job(self.card_holder_alert_2, CronTrigger(day_of_week='fri', hour=20, minute=0), id="card_holder_alert_2", **common_job_kwargs)

        return scheduler



    async def card_holder_poll(self):
            print(f'card holder poll entered')
            card_holder_channel = self.channels.committee()

            p = discord.Poll(
                question=f"Card Holders, are you available to open the space at the following times?",
                duration=timedelta(days=5),
                multiple=True
            )
            p.add_answer(text='Saturday 12pm')
            p.add_answer(text='Sunday 12pm')
            await card_holder_channel.send(poll=p)    

    # async def jam_poll(self):
    #     print(f'jam poll entered')
    #     mapping = {}
    #     mapping['rock'] = (self.channels.jam('rock'), "Saturday (3-6pm)")
    #     mapping['jazz'] = (self.channels.jam('jazz'), "Sunday (12-3pm)")
    #     mapping['pop'] = (self.channels.jam('pop'), "Saturday (12-3pm)")

    #     for name, (channel, time) in mapping.items():
    #         p = discord.Poll(
    #             question=f"Are you attending the {name.capitalize()} Jam this {time}? If YES, specify your instrument below for priority.",
    #             duration=timedelta(days=5)
    #         )
    #         for instrument in ["Guitar", "Piano", "Drums", "Bass", "Singing", "Other"]:
    #             p.add_answer(text=instrument)
    #         await channel.send(poll=p)

    async def jam_poll(self, genre: JamGenre): 
        print(f'jam poll entered')

        p = discord.Poll(
            question=f"Are you attending the {genre.name.capitalize()} Jam this {genre.time}? If YES, specify your instrument below for priority.",
            duration=timedelta(days=5)
        )
        for instrument in ["Guitar", "Piano", "Drums", "Bass", "Singing", "Other"]:
            p.add_answer(text=instrument)
        await genre.channel.send(poll=p)



    async def card_holder_alert_1(self):    
        print(f'card holder alert 1 entered')
        card_holder_channel = self.channels.committee()

        answers_empty_flags = await self.no_card_holder_day_answers(card_holder_channel)

        if answers_empty_flags is None:
            await card_holder_channel.send("No active Card Holder poll found.")
            return
        
        for answer in answers_empty_flags:
            await card_holder_channel.send(f"No one is available on {answer.text}!"
            " A message will be sent to the relevant jam channel on Friday if no one is available.")
        
    async def card_holder_alert_2(self):
        print(f'card holder alert 2 entered')
        card_holder_channel = self.channels.committee()

        answers_empty_flags = await self.no_card_holder_day_answers(card_holder_channel)

        if answers_empty_flags is None:
            await card_holder_channel.send("No active Card Holder poll found.")
            return
        
        channels = []
        for answer in answers_empty_flags:
            if "Saturday" in answer.text:
                channels.append(self.channels.jam('rock'))
                channels.append(self.channels.jam('pop'))
            if "Sunday" in answer.text:
                channels.append(self.channels.jam('jazz'))  

        for channel in channels:
            await channel.send(f"Staff is unavailable to open the space for this week. Please reach out to the SBS team for confirmation.")


   





    async def no_card_holder_day_answers(self, card_holder_channel: discord.TextChannel) -> list[discord.PollAnswer] | None:
        async for message in card_holder_channel.history(limit=500):
            if message.author == self.bot.user and message.poll and not message.poll.is_finalized():
                return [answer for answer in message.poll.answers if answer.vote_count==0]
        return None



