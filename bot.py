import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from reminders import load_reminders, save_reminders

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    check_reminders.start()


@bot.command(name="remind")
async def add_reminder(ctx, channel: discord.TextChannel, date: str, time: str, *, message: str):
    """
    Add a reminder.
    Usage: !remind #channel YYYY-MM-DD HH:MM Your event message here
    Example: !remind #general 2025-06-01 09:00 Team standup starts in 10 minutes!
    """
    try:
        remind_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        remind_dt = remind_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        await ctx.send("❌ Invalid date/time format. Use: `YYYY-MM-DD HH:MM` (UTC)")
        return

    if remind_dt < datetime.now(timezone.utc):
        await ctx.send("❌ That date/time is in the past!")
        return

    reminders = load_reminders()
    reminders.append({
        "channel_id": channel.id,
        "datetime": remind_dt.isoformat(),
        "message": message,
        "added_by": str(ctx.author),
    })
    save_reminders(reminders)

    await ctx.send(
        f"✅ Reminder set!\n"
        f"📅 **When:** {remind_dt.strftime('%Y-%m-%d %H:%M')} UTC\n"
        f"📢 **Channel:** {channel.mention}\n"
        f"💬 **Message:** {message}"
    )


@bot.command(name="reminders")
async def list_reminders(ctx):
    """List all upcoming reminders."""
    reminders = load_reminders()
    now = datetime.now(timezone.utc)
    upcoming = [r for r in reminders if datetime.fromisoformat(r["datetime"]) > now]

    if not upcoming:
        await ctx.send("📭 No upcoming reminders.")
        return

    lines = ["**📋 Upcoming Reminders:**\n"]
    for i, r in enumerate(upcoming, 1):
        dt = datetime.fromisoformat(r["datetime"])
        channel = bot.get_channel(r["channel_id"])
        channel_mention = channel.mention if channel else f"(ID: {r['channel_id']})"
        lines.append(
            f"`{i}.` {dt.strftime('%Y-%m-%d %H:%M')} UTC — {channel_mention}\n"
            f"    💬 {r['message']}\n"
            f"    👤 Added by: {r['added_by']}"
        )

    await ctx.send("\n".join(lines))


@bot.command(name="delreminder")
async def delete_reminder(ctx, index: int):
    """Delete a reminder by its number from !reminders list."""
    reminders = load_reminders()
    now = datetime.now(timezone.utc)
    upcoming = [r for r in reminders if datetime.fromisoformat(r["datetime"]) > now]

    if index < 1 or index > len(upcoming):
        await ctx.send(f"❌ Invalid index. Use `!reminders` to see the list.")
        return

    to_remove = upcoming[index - 1]
    reminders.remove(to_remove)
    save_reminders(reminders)

    await ctx.send(f"🗑️ Deleted reminder #{index}: _{to_remove['message']}_")


@tasks.loop(seconds=30)
async def check_reminders():
    """Check every 30 seconds if any reminders are due."""
    now = datetime.now(timezone.utc)
    reminders = load_reminders()
    remaining = []
    fired = False

    for r in reminders:
        remind_dt = datetime.fromisoformat(r["datetime"])
        if remind_dt <= now:
            channel = bot.get_channel(r["channel_id"])
            if channel:
                await channel.send(f"🔔 **Reminder:** {r['message']}")
                fired = True
            else:
                print(f"Warning: Channel ID {r['channel_id']} not found.")
        else:
            remaining.append(r)

    if fired:
        save_reminders(remaining)


bot.run(TOKEN)
