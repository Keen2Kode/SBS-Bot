import json
from typing import Any
from urllib.parse import urlparse
import discord
from datetime import datetime, timedelta
import re

class Event:

    # NEW: genre tied to the Calendar

    def __eq__(self, other):
        return isinstance(other, Event) and self.id == other.id

    def __hash__(self):
        return hash(self.id)
    
    def __str__(self):  
        return f"{self.title} {self.start}"

    def __init__(self, calendar_event, metadata, timezone):
        self.id = calendar_event.get("id")
        self.title = calendar_event.get("summary", "")
        self.description = calendar_event.get("description", "")
        self.start = self.parse_dt(calendar_event["start"], timezone)
        self.end = self.parse_dt(calendar_event["end"], timezone)
        self.location = calendar_event.get("location", "Unspecified")


        self.is_discord_event = metadata is not None
        if metadata:
            self.channel_name = metadata.get("channel")
            self.embed_url = metadata.get("embed_url")

        self.recurring_id = calendar_event.get("recurringEventId")
        self.is_recurring = self.recurring_id is not None

    def human_description(self):
        return (
            f"\n\n**{self.title}**\n"
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



    
    def parse_dt(self, obj, timezone):
        dt = datetime.fromisoformat(obj.get("dateTime") or obj.get("date"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone)
    
    def get_run_time(self, reminder_window, now):


        if not self.start:
            return None

        run_time = max(self.start - reminder_window, now)

        if run_time >= self.start:
            return None

        return run_time
    
    def need_to_add(self, sent_events, recurring_ids):
        if not self.is_discord_event:
            return False

        if self in sent_events:
            return False

        if self.recurring_id in recurring_ids:
            return False
        return True
        
    








