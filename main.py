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


def send_discord_webhook(webhook_url, message, username="Bot", avatar_url=None):
    if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
        raise ValueError("Invalid Discord webhook URL.")

    # If a role ID is provided, format the mention
    if ROLE_ID:
        message = f"<@&{ROLE_ID}> {message}"

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


def send_scheduled_webhooks(webhook_url, message_part, username="Bot", avatar_url=None):
    if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
        raise ValueError("Invalid Discord webhook URL.")

    headers = {
        "Content-Type": "application/json"
    }

    webhooks = [
        (0, f"${message_part} starts in 30 minutes ⏰"),
        (20 * 60, f"${message_part} starts in 10 minutes ⏰"),
        (10 * 60, f"${message_part} starts now!"),
    ]

    for delay, message in webhooks:
        time.sleep(delay)
        # If a role ID is provided, format the mention
        if ROLE_ID:
            message = f"<@&{ROLE_ID}> {message}"

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


@app.route("/arena", methods=["POST"])
@require_api_key
def arena():
    send_discord_webhook(
        webhook_url=os.getenv("ARENA_WEBHOOK_URL", ""),
        message="🔥 Arena reset in 15 mins! ⏰⚔️",
        username="Arena Reminder",
        avatar_url="https://i.postimg.cc/SN2jZmR5/REMINDER.png"
    )

    return "Arena notification sent successfully."


@app.route("/bear", methods=["POST"])
@require_api_key
def bear():
    body = request.json or { }
    thread = threading.Thread(
        target=send_scheduled_webhooks,
        kwargs={
            "webhook_url": os.getenv("BEAR_WEBHOOK_URL", ""),
            "message_part": body.get("event_type", "N/A"),
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