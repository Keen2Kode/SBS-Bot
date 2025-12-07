import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
from channels import Channels
from apscheduler.triggers.cron import CronTrigger

class JamGenre:
    def __init__(self, name: str, time: str, embedUrl: str, channels: Channels, interval: CronTrigger):
        self.name = name
        self.time = time
        self.embedUrl = embedUrl
        self.channel = channels.jam(name)
        self.interval = interval
