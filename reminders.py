import json
import os

REMINDERS_FILE = "reminders.json"


def load_reminders() -> list:
    """Load reminders from the JSON file."""
    if not os.path.exists(REMINDERS_FILE):
        return []
    with open(REMINDERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_reminders(reminders: list) -> None:
    """Save reminders to the JSON file."""
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=2)
