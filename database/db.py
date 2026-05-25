import sqlite3
import os

# The .db file will be created in the project root folder
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fittrack.db")

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn

def initialize_database():
    """Creates all tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            username         TEXT    NOT NULL UNIQUE,
            email            TEXT    NOT NULL,
            password         TEXT    NOT NULL,
            reminder_time    TEXT    DEFAULT NULL,
            reminder_enabled INTEGER DEFAULT 0
        )
    """)

    # Safe migration — adds columns if they don't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN reminder_time TEXT DEFAULT NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN reminder_enabled INTEGER DEFAULT 0")
    except Exception:
        pass
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            date        TEXT    NOT NULL,
            start_time  TEXT    NOT NULL,
            end_time    TEXT    DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_sets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id  INTEGER NOT NULL,
            exercise    TEXT    NOT NULL,
            reps        INTEGER NOT NULL,
            timestamp   TEXT    NOT NULL,
            FOREIGN KEY (workout_id) REFERENCES workouts(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")