# Discord Reminder Bot

A Python bot that lets you schedule reminders to be posted in any Discord channel.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your token**
   ```bash
   cp .env.example .env
   # Edit .env and paste in your bot token
   ```

3. **Run the bot**
   ```bash
   python bot.py
   ```

## Commands

| Command | Description | Example |
|---|---|---|
| `!remind #channel YYYY-MM-DD HH:MM message` | Schedule a reminder (times are UTC) | `!remind #general 2025-06-01 09:00 Standup in 10 mins!` |
| `!reminders` | List all upcoming reminders | `!reminders` |
| `!delreminder <number>` | Delete a reminder by its list number | `!delreminder 2` |

## Notes

- All times are in **UTC**
- Reminders are stored in `reminders.json` (auto-created)
- The bot checks for due reminders every **30 seconds**
- Reminders are deleted from storage after they fire
