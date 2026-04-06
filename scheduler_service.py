from datetime import datetime, timedelta


class SchedulerService:
    def __init__(self, scheduler, calendar_ctx, jam_polls, timezone, reminder_window: timedelta):
        self.scheduler = scheduler
        self.calendar_ctx = calendar_ctx
        self.jam_polls = jam_polls
        self.timezone = timezone
        self.reminder_window = reminder_window

    async def sync_jobs(self):
        events, cancelled_ids = await self.calendar_ctx.next_discord_events()

        # case 1: restart before event (job alr scheduled)
        #   job gets replaced/updated ("replace_existing")
        # case 2: restart after event (job already ran)
        #   run date in past
        # case 3: restart after event (missed job)
        #   misfire_grace_time
        self._remove_jobs(cancelled_ids)
        self._schedule_event_jobs(events)
        self._schedule_cardholder_jobs()







    def _remove_jobs(self, cancelled_ids):
        for job_id in cancelled_ids:
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

    def _schedule_event_jobs(self, events):
        now = datetime.now(tz=self.timezone)

        for event in events:
            run_time = event.get_run_time(self.reminder_window, now)
            if not run_time:
                continue

            self.scheduler.add_job(
                self.jam_polls.event_poll,
                trigger="date",
                run_date=run_time,
                id=event.id,
                kwargs={"event": event},
                replace_existing=True,
                misfire_grace_time=86400 * 4
            )

    def _schedule_cardholder_jobs(self):
        self.scheduler.add_job(
            self.jam_polls.card_holder_poll,
            trigger="cron",
            day_of_week="mon",
            hour=12,
            minute=0,
            id="card_holder_poll",
            replace_existing=True
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