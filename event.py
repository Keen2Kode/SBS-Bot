import json
from typing import Any
from urllib.parse import urlparse
import discord
from datetime import datetime
import re

class Event:

    # NEW: genre tied to the Calendar

    def __init__(self, calendar_event, metadata):
        self.id = calendar_event.get("id")
        self.title = calendar_event.get("summary", "")
        self.description = calendar_event.get("description", "")
        self.start = self.parse_dt(calendar_event["start"])
        self.end = self.parse_dt(calendar_event["end"])
        self.location = calendar_event.get("location", "Unspecified")


        self.is_discord_event = metadata is not None
        if metadata:
            self.channel_name = metadata.get("channel")
            self.embed_url = metadata.get("embed_url")

        self.recurring_id = calendar_event.get("recurringEventId")
        self.is_recurring = self.recurring_id is not None

    def human_description(self):
        return (
            f"\n..\n**{self.title}**\n\n"
            f"{self.description}\n"
            f"🗓️ {self.human_time()}\n"
            f"📍 {self.location}"
        )

    def human_time(self):
        if not self.start or not self.end:
            return "Not specified"
        start_str = self.start.strftime("%A %b %d, %I:%M %p")
        end_str = self.end.strftime("%I:%M%p")
        return f"{start_str} - {end_str}"


    def __str__(self):  
        return f"{self.title} {self.start}"
    
    def parse_dt(self, obj):
        return datetime.fromisoformat(
            obj.get("dateTime") or obj.get("date")
        )
    








