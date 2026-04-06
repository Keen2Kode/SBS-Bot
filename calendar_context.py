import asyncio
import json
import os
import re
from typing import List, Set
import yaml
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timedelta, timezone

from channels import Channels
from event import Event

class CalendarContext:
    """
    Encapsulates Google Calendar to an object accessible to jam commands
    For creating event notifications directly from the calendar event
    """

    def __init__(self, timezone: ZoneInfo):
        creds = Credentials.from_service_account_file(
            filename="gcloud-service-account-credentials.json",
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )
        self.service = build('calendar', 'v3', credentials=creds)
        self.calendar_owner = "rmitsbs@gmail.com"
        self.calendar = self.service.calendars().get(calendarId=self.calendar_owner).execute()
        self.timezone = timezone
        self.sent_events = set()

        self.url = "https://calendar.google.com/calendar/u/0?cid=cm1pdHNic0BnbWFpbC5jb20"



    def now(self) -> datetime: 
        return datetime.now(tz=self.timezone)
    
    
    async def events(self):


        time_max = self.now() + timedelta(weeks=2)

        # sync method, so wrap it in async thread so it doesn't block the bot process
        events_result = await asyncio.to_thread(
            lambda: self.service.events()
                .list(
                    calendarId=self.calendar_owner,
                    timeMin=self.now().isoformat(),
                    timeMax=time_max.isoformat(),
                    maxResults=20,
                    singleEvents=True,
                    showDeleted=True,
                    orderBy="startTime",
                )
                .execute()
        )
        return events_result.get("items", [])
    

    async def next_discord_events(self):
        # recurring
        recurring_ids: Set[str] = set()
        next_events: List[Event] = []
        to_delete: List[str] = []

        
        for calendar_event in await self.events():
            
            is_cancelled = "cancelled" == calendar_event.get("status")
            if is_cancelled:
                to_delete.append(calendar_event.get("id"))
                continue

            event = self.to_event(calendar_event)
            if not event.need_to_add(self.sent_events, recurring_ids):
                continue

            # only use immediate next event
            if event.recurring_id and event.recurring_id not in recurring_ids:
                recurring_ids.add(event.recurring_id)
            
            next_events.append(event)

        self.update_sent_events(next_events)

        return next_events, to_delete
    

    
    def update_sent_events(self, events: List[Event]):
        # add all events to sent events
        # will only affect the events to add next time around
        self.sent_events.update(events)
        
        # remove sent events once you crossed the date
        # TODO: ALSO keep out events that have not yet reached reminder window (see jam_poll class)
        # aka if the event changes, its job can still be updated
        self.sent_events = {e for e in self.sent_events if self.now() < e.start}

    def to_event(self, event) -> Event:
        
        description = event.get("description", "")
        metadata = self.metadata(description)
        event["description"] = self.strip_metadata(description)

        return Event(event, metadata, self.timezone)
    
    def strip_metadata(self, description):
        return re.sub(r'--discord--\s*\n(.*)$', '', description, flags=re.S).strip()

    def metadata(self, description):
        # Capture everything after --discord-- until end of string
        match = re.search(r'--discord--\s*\n(.*)$', description, re.S)

        if not match:
            return None

        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            print(f"failed to get metadata from event with description: {description} ")
            return None
        
