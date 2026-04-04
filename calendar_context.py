import json
import os
import re
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

    def __init__(self):
        creds = Credentials.from_service_account_file(
            filename="gcloud-service-account-credentials.json",
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )
        self.service = build('calendar', 'v3', credentials=creds)
        self.calendar_owner = "rmitsbs@gmail.com"
        self.calendar = self.service.calendars().get(calendarId=self.calendar_owner).execute()


        self.url = "https://calendar.google.com/calendar/u/0?cid=cm1pdHNic0BnbWFpbC5jb20"


    def now(self) -> datetime: 
        return datetime.now(tz=ZoneInfo(self.calendar['timeZone']))
    
    
    def events(self):


        time_max = self.now() + timedelta(weeks=2)

        events_result = (
            self.service.events()
            .list(
                calendarId=self.calendar_owner,
                timeMin=self.now().isoformat(),
                timeMax=time_max.isoformat(),
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
    
    def next_discord_events(self):
        # recurring
        recurring_ids: str = set()
        next_events: Event = []

        for calendar_event in self.events():
            
            event = self.to_event(calendar_event)
            if not event.is_discord_event:
                continue

            # if recurring event only take the closest you find
            if not event.is_recurring:
                next_events.append(event)
            elif event.recurring_id not in recurring_ids: 
                recurring_ids.add(event.recurring_id)
                next_events.append(event)

        return next_events

    def to_event(self, event) -> Event:
        description = event.get("description", "")

        metadata = self.metadata(description)
        clean_description = self.strip_metadata(description)

        if metadata:
            print(f"getting metadata from {event.get('summary')}")
            print(f"metadata: {metadata}")

        event["description"] = clean_description
        return Event(event, metadata)
    
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
        
