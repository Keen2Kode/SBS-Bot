# 🎵 RMIT SBS Club Bot

This bot is designed to support the operations of the Student Band Society, an RMIT-based Music Club. 

---

## ✨ Key Features

### 🗓️ 1. Automated Jam Polling and Alerts

The bot handles a weekly cycle of automated polls and follow-up alerts to ensure space access and jam coordination:

#### Weekly Jam Attendance Polls
Every **Monday at 12 PM**, the bot posts a poll in each jam session channel (`rock`, `jazz`, `pop`) asking members if they are attending and what instrument they plan to bring.

#### Weekly Card Holder Availability Poll
Simultaneously, a poll is posted in the `card-holders` channel to determine which card holders are available to unlock the space on:
- **Saturday at 12 PM**
- **Sunday at 12 PM**

#### Thursday Availability Alert
On **Thursday at 6 PM**, if **no card holders** have marked availability for either day, the bot sends an alert in the `card-holders` channel to prompt a response.

#### Friday Jam Session Warnings
On **Friday at 8 PM**, if any jam session does **not have a card holder available**, a message is sent to the relevant jam channels to notify members that the space may not be open.

---

### ℹ️ 2. Jam Info Command

The `!jam_info` command sends a detailed message explaining how jam sessions work, with helpful links to:
- The Creative Space location
- The shared Jam Songs spreadsheet

This message helps new members understand how to participate and prepare for weekly jam sessions.

---

## 🛠 Deployment

This bot is hosted 24/7 using a shady bot hosting service. But hey, it's cheap.

---
