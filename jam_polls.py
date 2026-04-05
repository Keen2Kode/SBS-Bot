from typing import List
import discord
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from event import Event
from jam_commands import JamCommands
from channels import Channels
from jam_genre import JamGenre



class JamPolls(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.channels = Channels(bot)




    # @commands.command(name="jampoll")
    # async def jam_poll_cmd(self, ctx: Context, genre_string: str = ""):
    #     if not ctx.author.guild_permissions.administrator:
    #         return

    #     genre_string = genre_string.casefold().strip()

    #     for genre in self.genres:
    #         if genre_string in genre.name:
    #             await self.jam_poll(genre)
    #             return

    #     await ctx.send(f"Unknown genre '{genre_string}'")

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




    async def add_scheduled_polls(self, scheduler: AsyncIOScheduler, events: List[Event], cancelled_event_ids: List[str]):
        # case 1: restart before event (job alr scheduled)
        #   job gets replaced/updated ("replace_existing")
        # case 2: restart after event (job already ran)
        #   run date in past
        # case 3: restart after event (missed job)
        #   misfire_grace_time

        day_duration = 86400
        common_job_kwargs = {
            "replace_existing": True,
            "misfire_grace_time": day_duration*4
        }

        for id in cancelled_event_ids:
            scheduler.remove_job(job_id=id)

        for event in events:
            # # run immediately
            # scheduler.add_job(self.event_poll, 
            #     id=event.id, 
            #     trigger="date", 
            #     run_date=None, 
            #     kwargs={"event": event}, 
            #     **common_job_kwargs
            # )
            scheduler.add_job(
                self.event_poll,
                id=event.id,
                trigger="date",
                run_date=event.start,
                kwargs={"event": event},
                **common_job_kwargs
            )
        

        # scheduler.add_job(self.card_holder_poll, CronTrigger(day_of_week='mon', hour=12, minute=0), id="card_holder_poll", **common_job_kwargs)
        # scheduler.add_job(self.card_holder_alert_1, CronTrigger(day_of_week='thu', hour=18, minute=0), id="card_holder_alert_1", **common_job_kwargs)
        # scheduler.add_job(self.card_holder_alert_2, CronTrigger(day_of_week='fri', hour=20, minute=0), id="card_holder_alert_2", **common_job_kwargs)
        return scheduler

    async def event_poll(self, event: Event): 
        print(f'event added to discord ' + event.title)


        p = discord.Poll(
            question=f"Are you attending this Event?",
            duration=timedelta(days=5)
        )
        p.add_answer(text="Yes")
        p.add_answer(text="No") 



        channel = self.channels.get_channel(event.channel_name)

        if not channel:
            bot_channel = self.channels.bot_channels()[0]
            await bot_channel.send(f"specified channel to post this event {event.title} not found.")
        else:
            if event.embed_url:
                await channel.send(file=discord.File(event.embed_url))
            await channel.send(content=event.human_description())
            await channel.send(poll=p)


    async def card_holder_poll(self):
        print(f'card holder poll entered')
        card_holder_channel = self.channels.committee()

        p = discord.Poll(
            question=f"Card Holders, when are you available to open the space?",
            duration=timedelta(days=5),
            multiple=True
        )
        p.add_answer(text='Saturday')
        p.add_answer(text='Sunday')
        await card_holder_channel.send(poll=p) 
        await card_holder_channel.send(f"You can check the required opening time from the earliest booking in the [Bookings Calendar.](https://calendar.google.com/calendar/u/0/embed?src=rmitsbs@gmail.com&ctz=Australia/Melbourne)")
          





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



