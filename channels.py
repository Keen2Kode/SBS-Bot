import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot

class Channels:
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    def jam(self, name):
        if name is None:
            return None
        
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if (channel.category 
                    and channel.category.name == "Jams" 
                    and name.strip().casefold() in channel.name.strip().casefold()):
                    return channel
        return None
    
    def committee(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.name.lower() == "committee":
                    return channel
        return None


    def bot_channels(self):
        return [ch for guild in self.bot.guilds for ch in guild.text_channels if ch.name.startswith("bot")]
