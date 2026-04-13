import os
from flask import Flask, jsonify, request
import requests
import json
from dotenv import load_dotenv

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
        print("✅ NEK Bear 1 Reminder Message sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send NEK Bear 1 Reminder message: {e}")


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


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)