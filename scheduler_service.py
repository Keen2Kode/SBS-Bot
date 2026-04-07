from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_EXECUTED

from calendar_context import CalendarContext


class SchedulerService:
    def __init__(self, calendar_ctx: CalendarContext, jam_polls, timezone, reminder_window: timedelta):
        self.scheduler = AsyncIOScheduler(timezone=timezone)
        self.calendar_ctx = calendar_ctx
        self.jam_polls = jam_polls
        self.timezone = timezone
        self.reminder_window = reminder_window

        # 👇 moved here (owned by service)
        self.sent_event_ids: set[str] = set()

    def start(self):
        self.scheduler.add_listener(self._on_job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.start()

    async def sync_event_jobs(self):
        events, cancelled_ids = await self.calendar_ctx.next_discord_events()

        # case 1: restart before event (job alr scheduled)
        #   job gets replaced/updated ("replace_existing")
        # case 2: restart after event (job already ran)
        #   run date in past
        # case 3: restart after event (missed job)
        #   misfire_grace_time
        self._remove_event_jobs(cancelled_ids)
        self._schedule_event_jobs(events)







    def _remove_event_jobs(self, cancelled_ids):
        for job_id in cancelled_ids:
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # also clean up sent store
            self.sent_event_ids.discard(job_id)

    def _schedule_event_jobs(self, events):
        now = datetime.now(tz=self.timezone)

        for event in events:
            # 👇 dedup here (NOT in CalendarContext anymore)
            if event.id in self.sent_event_ids:
                continue

            run_time = event.get_run_time(self.reminder_window, now)
            if not run_time:
                continue

            self.scheduler.add_job(
                self.jam_polls.event_poll,
                trigger="date",
                run_date=run_time,
                id="event_" + event.id,
                kwargs={"event": event},
                replace_existing=True,
                misfire_grace_time=86400 * 4
            )


    def _on_job_executed(self, ap_event):
        if ap_event.job_id.startswith("event"):
            self.sent_event_ids.add(ap_event.job_id)
        
        #TODO: this line has to be compatible, unfortunately that requires having the ENTIRE event object
        # # events whose jobs have already completed and removed from job store
        # # self.events() updating should not readd the same event back to the scheduler
        # self.sent_events = {e for e in self.sent_events if self.now() < e.start}

    def schedule_cardholder_jobs(self):
        self.scheduler.add_job(
            self.jam_polls.card_holder_poll,
            trigger="cron",
            day_of_week="mon",
            hour=12,
            minute=0,
            id="card_holder_poll",
            replace_existing=True,
            misfire_grace_time=86400 * 4
        )

        self.scheduler.add_job(
            self.jam_polls.card_holder_alert_1,
            trigger="cron",
            day_of_week="thu",
            hour=18,
            minute=0,
            id="card_holder_alert_1",
            replace_existing=True
        )

        self.scheduler.add_job(
            self.jam_polls.card_holder_alert_2,
            trigger="cron",
            day_of_week="fri",
            hour=20,
            minute=0,
            id="card_holder_alert_2",
            replace_existing=True
        )