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
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Australia/Melbourne"))
    common_job_kwargs = {
        "replace_existing": True,
        "misfire_grace_time": 60
    }

    scheduler.add_job(jam_poll, CronTrigger(day_of_week='mon', hour=12, minute=0), id="jam_poll", **common_job_kwargs)
    scheduler.add_job(card_holder_poll, CronTrigger(day_of_week='mon', hour=12, minute=0), id="card_holder_poll", **common_job_kwargs)
    scheduler.add_job(card_holder_alert_1, CronTrigger(day_of_week='thu', hour=18, minute=0), id="card_holder_alert_1", **common_job_kwargs)
    scheduler.add_job(card_holder_alert_2, CronTrigger(day_of_week='fri', hour=20, minute=0), id="card_holder_alert_2", **common_job_kwargs)


    
    # await jam_poll()
    # await card_holder_poll()
    scheduler.start()



@bot.command()
async def card_holder_alert_2(ctx: Context):
    await card_holder_alert_2()
    
async def card_holder_alert_2():
    print(f'card holder alert 2 entered')
    card_holder_channel = jam_channel('card-holders')

    answers_empty_flags = await no_card_holder_day_answers(card_holder_channel)

    if answers_empty_flags is None:
        await card_holder_channel.send("No active Card Holder poll found.")
        return
    
    channels = []
    for answer in answers_empty_flags:
        if "Saturday" in answer.text:
            channels.append(jam_channel('rock'))
            channels.append(jam_channel('pop'))
        if "Sunday" in answer.text:
            channels.append(jam_channel('jazz'))  

    for channel in channels:
        await channel.send(f"Staff is unavailable to open the space for this week. Please reach out to the SBS team for confirmation.")





@bot.command()
async def card_holder_alert_1(ctx: Context):
    await card_holder_alert_1()

async def card_holder_alert_1():    
    print(f'card holder alert 1 entered')
    card_holder_channel = jam_channel('card-holders')

    answers_empty_flags = await no_card_holder_day_answers(card_holder_channel)

    if answers_empty_flags is None:
        await card_holder_channel.send("No active Card Holder poll found.")
        return
    
    for answer in answers_empty_flags:
        await card_holder_channel.send(f"No one is available on {answer.text}!"
        " A message will be sent to the relevant jam channel on Friday if no one is available.")

    
async def no_card_holder_day_answers(card_holder_channel: discord.TextChannel) -> list[discord.PollAnswer] | None:
    async for message in card_holder_channel.history(limit=500):
        if message.author == bot.user and message.poll and not message.poll.is_finalized():
            return [answer for answer in message.poll.answers if answer.vote_count==0]
    return None


@bot.command()
async def card_holder_poll(ctx: Context):
    await card_holder_poll()

async def card_holder_poll():
    print(f'card holder poll entered')
    card_holder_channel = jam_channel('card-holders')

    p = discord.Poll(
        question=f"Card Holders, are you available to open the space at the following times?",
        duration=timedelta(days=5)
    )
    p.add_answer(text='Saturday 12pm')
    p.add_answer(text='Sunday 12pm')
    await card_holder_channel.send(poll=p)    



@bot.command()
async def jam_poll(ctx: Context):
    await jam_poll()

async def jam_poll():
    print(f'jam poll entered')
    mapping = {}
    mapping['rock'] = (jam_channel('rock'), "Saturday (3-6pm)")
    mapping['jazz'] = (jam_channel('jazz'), "Sunday (12-3pm)")
    mapping['pop'] = (jam_channel('pop'), "Saturday (12-3pm)")

    for name, (channel, time) in mapping.items():
        p = discord.Poll(
            question=f"Are you attending the {name.capitalize()} Jam this {time}? If YES, specify your instrument below for priority.",
            duration=timedelta(days=5)
        )
        for instrument in ["Guitar", "Piano", "Drums", "Bass", "Singing", "Other"]:
            p.add_answer(text=instrument)
        await channel.send(poll=p)

def jam_channel(channel_name):
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.category and channel.category.name == "Jams" and channel.name == channel_name:
                    return channel
    return None

bot.run(TOKEN)
