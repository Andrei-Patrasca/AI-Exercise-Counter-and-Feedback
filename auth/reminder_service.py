"""
FitTrack Reminder Service
Runs as a Windows scheduled task at login.
Checks every minute if it's time to send a workout reminder.
"""
import sys
import os
import time
from datetime import datetime

# Add project root to path so we can import our modules
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from database.db import get_connection, initialize_database
from auth.email_service import send_reminder_email


def check_and_send(sent_today):
    """
    sent_today is a set of user_ids already notified this minute.
    Cleared automatically when the minute changes.
    """
    now = datetime.now().strftime("%H:%M")

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, email, reminder_time
        FROM users
        WHERE reminder_enabled=1
          AND reminder_time IS NOT NULL
          AND reminder_time != ''
    """)
    users = cursor.fetchall()
    conn.close()

    for user in users:
        key = (user["id"], now)  # unique per user per minute
        if user["reminder_time"] == now and key not in sent_today:
            print(f"[{datetime.now()}] Sending reminder to {user['email']}")
            ok, msg = send_reminder_email(
                user["email"],
                user["username"],
                user["reminder_time"]
            )
            sent_today.add(key)
            print(f"  → Result: {ok} {msg}")


def main():
    print(f"FitTrack Reminder Service started at {datetime.now()}")
    initialize_database()

    sent_today = set()
    last_day   = datetime.now().strftime("%Y-%m-%d")

    while True:
        try:
            # Clear sent log at midnight each new day
            today = datetime.now().strftime("%Y-%m-%d")
            if today != last_day:
                sent_today.clear()
                last_day = today

            check_and_send(sent_today)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)


if __name__ == "__main__":
    main()


def main():
    print(f"FitTrack Reminder Service started at {datetime.now()}")
    initialize_database()

    while True:
        try:
            check_and_send()
        except Exception as e:
            print(f"Error: {e}")
        # Check every 60 seconds
        time.sleep(60)


if __name__ == "__main__":
    main()