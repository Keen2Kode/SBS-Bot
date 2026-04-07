# 🎵 RMIT SBS Club Bot

This bot is designed to support the operations of the Student Band Society, an RMIT-based music club.

---

## ✨ Key Features

### 🗓️ 1. Calendar-Driven Event Polls and Alerts

The bot integrates with Google Calendar to help coordinate club events automatically. Here's the problems that 
- **No more manual setup:** Organisers don’t need to edit code or restart the bot just to schedule a jam — simply create an event in the calendar
- **Easy to change plans:** If a jam time, location, or details change, just update the calendar — the bot will reflect those changes automatically
- **Cancelling is simple:** Removing an event from the calendar automatically stops any reminders from being sent. This is useful during holiday or break periods.
- **Recurring jams are effortless:** Weekly jams only need to be set up once as a recurring calendar event — no need to manage them week by week
- **One-off events are just as easy:** Special events like gigs or workshops can be added the same way, without any extra setup.

#### Discord Event Detection
The bot regularly syncs with the club calendar for upcoming events and event updates that have been marked for Discord posting.

Each Discord Event post can include:
- The event title and description
- The date and time
- The location
- Event picture
- An Yes/No attendance poll


#### Smart Channel Posting
Events can be configured so that their reminders are posted in the Discord channel specified in the calendar event.

#### Calendar Event Reminders
The bot automatically schedules the Discord Event post **7 days before the event** so members have time to respond.

#### Handling Calendar Updates
Until the Discord Event is posted, The bot can handle calendar event updates such as:
- Cancellations
- updates to its details, such as title, location etc. 

Note that after posting, any updates will not trigger a repost. This is to avoid duplicate announcements for the same event.

#### Recurring Event Support
For recurring calendar events, the **earliest** upcoming event is posted.

---

### 🗳️ 2. Card Holder Polls and Follow-Up Alerts

The bot handles a weekly cycle of automated polls and follow-up alerts to help coordinate access to the club space.

#### Weekly Card Holder Availability Poll
Every **Monday at 12 PM**, a poll is posted in the `card-holders` channel asking card holders when they are available to open the space for:
- **Saturday**
- **Sunday**

A follow-up message also includes a link to the Bookings Calendar so card holders can check the required opening time.

#### Thursday Availability Alert
On **Thursday at 6 PM**, if nobody has voted for one or more days, the bot sends an alert in the `card-holders` channel to prompt a response.

#### Friday Jam Session Warnings
On **Friday at 8 PM**, if a day still has no available card holder, the bot sends a warning to the relevant jam channels so members know that the space may not be available.

---

### ℹ️ 3. Jam Commands

The bot also includes jam-related commands for sharing useful club information.

The `!jam_info` command sends a helpful explanation of how jam sessions work, along with useful links such as:
- The Creative Space location
- The shared Jam Songs spreadsheet

The `!jam_songs <sheet_name> <song_amount>` command lists songs from the selected sheet, such as `Jazz`, `Rock`, or `Pop`, using data from the shared Jam Songs spreadsheet.

---

### 🛠️ 4. Admin / Testing Commands

To make testing and manual control easier, the bot includes admin-only commands for triggering the card holder workflow manually:

- `!committeepoll`
- `!cardalert1`
- `!cardalert2`

These are useful for testing bot behaviour without waiting for the scheduled times.

---

## 🛠 Deployment

This bot is hosted 24/7 using a shady bot hosting service. But hey, it's cheap.
