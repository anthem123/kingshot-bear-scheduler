import os
from flask import Flask, jsonify, request
import requests
import json
from dotenv import load_dotenv
import threading
import time

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
ROLE_ID = os.getenv("ROLE_ID", None)

def require_api_key(f):
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key or key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper

event_type_role_dict = {
    "bear_sol_1": {
        "role_id": "1461925770732765438",
        "message": "SOL Bear Trap #1"
    },
    "bear_sol_2": {
        "role_id": "1461925770732765438",
        "message": "SOL Bear Trap #2"
    },
    "bear_nek_1": {
        "role_id": "1473861137467703346",
        "message": "NEK Bear Trap #1"
    },
    "bear_nek_2": {
        "role_id": "1473861137467703346",
        "message": "NEK Bear Trap #2"
    },
    "arena": {
        "role_id": "1461925772657688752",
        "message": "🔥 Arena reset in 15 mins! ⏰⚔️"
    }
}

def send_discord_webhook(
        webhook_url,
        event_type=None,
        username="Bot",
        avatar_url=None
):
    if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
        raise ValueError("Invalid Discord webhook URL.")

    # If a role ID is provided, format the mention
    message = ""
    if event_type:
        event_info = event_type_role_dict[event_type]
        message = f"<@&{event_info['role_id']}> {event_info['message']}"

    payload = {
        "content": message,
        "username": username
    }

    if avatar_url:
        payload["avatar_url"] = avatar_url

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Reminder message: {e}")


def send_scheduled_webhooks(webhook_url, event_type, username="Bot", avatar_url=None):
    if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
        raise ValueError("Invalid Discord webhook URL.")

    headers = {
        "Content-Type": "application/json"
    }

    message_part = event_type_role_dict[event_type]["message"]

    webhooks = [
        (0, f"{message_part} starts in 30 minutes ⏰"),
        (20 * 60, f"{message_part} starts in 10 minutes ⏰"),
        (10 * 60, f"{message_part} starts now!"),
    ]

    for delay, message in webhooks:
        time.sleep(delay)
        # If a role ID is provided, format the mention

        message = f"<@&{event_type_role_dict[event_type]['role_id']}> {message}"

        payload = {
            "content": message,
            "username": username
        }
        if avatar_url:
            payload["avatar_url"] = avatar_url
        try:
            response = requests.post(webhook_url, data=json.dumps(payload), headers=headers, timeout=10)
            response.raise_for_status()
            print("Message sent successfully.")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send Reminder message: {e}")

@app.route("/")
@require_api_key
def index():
    return jsonify({"message": "Hello, World!", "status": "ok"})


@app.route("/arena", methods=["GET", "POST"])
@require_api_key
def arena():
    send_discord_webhook(
        webhook_url=os.getenv("ARENA_WEBHOOK_URL", ""),
        event_type="arena",
        username="Arena Reminder",
        avatar_url="https://i.postimg.cc/SN2jZmR5/REMINDER.png"
    )

    return "Arena notification sent successfully."


@app.route("/bear", methods=["GET", "POST"])
@require_api_key
def bear():
    event_type = request.args.get("event_type", "N/A")
    print(event_type)
    thread = threading.Thread(
        target=send_scheduled_webhooks,
        kwargs={
            "webhook_url": os.getenv("BEAR_WEBHOOK_URL", ""),
            "event_type": event_type,
            "username": "Bear Reminder",
            "avatar_url": "https://i.postimg.cc/SN2jZmR5/REMINDER.png"
        },
        daemon=True
    )
    thread.start()
    return "Bear notification scheduled successfully."


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)