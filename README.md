# 🎵 RMIT SBS Club Bot

This bot is designed to support the operations of the Student Band Society, an RMIT-based Music Club. Its primary role is to ensure the **Creative Space is consistently open and accessible** for jam sessions each week through **automated polls and alerts**.

---

## ✨ Key Features

### 🎤 1. Weekly Jam Attendance Polls
Every **Monday at 12 PM**, the bot posts a poll in each jam session channel (`rock`, `jazz`, `pop`) asking members if they are attending and what instrument they plan to bring.

### 🔑 2. Weekly Card Holder Availability Poll
Simultaneously, a poll is posted in the `card-holders` channel to determine which card holders are available to unlock the space on:
- **Saturday at 12 PM**
- **Sunday at 12 PM**

### ⏰ 3. Thursday Availability Alert
On **Thursday at 6 PM**, if **no card holders** have marked availability for either day, the bot sends an alert in the `card-holders` channel to prompt a response.

### 🚨 4. Friday Jam Session Warnings
On **Friday at 8 PM**, if any jam session does **not have a card holder available**, a message is sent to the relevant jam channels to notify members that the space may not be open.

---

## 🛠 Deployment

This bot is hosted 24/7 using [Render.com](https://render.com) as a **background worker**.

---

## 📁 File Structure

- `bot.py`: Main script with all scheduled jobs and bot logic.
- `render.yaml`: Render deployment configuration.
- `requirements.txt`: Python dependencies.