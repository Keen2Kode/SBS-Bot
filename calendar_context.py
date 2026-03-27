import os
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timezone

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


        self.url = "https://calendar.google.com/calendar/u/0?cid=cm1pdHNic0BnbWFpbC5jb20"


    def now(self) -> str: 
        calendar = self.service.calendars().get(calendarId=self.calendar_owner).execute()
        return datetime.now(tz=ZoneInfo(calendar['timeZone'])).isoformat()
    
    def events(self):

        events_result = (
            self.service.events()
            .list(
                calendarId=self.calendar_owner,
                timeMin=self.now(),
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    def print_events(self):
        events = self.events()
        if not events:
            print("No upcoming events found.")
            return
        
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            bla = event.get("summary", "no summary")
            print(f"{start}, {bla}")
            # print(event.keys())
