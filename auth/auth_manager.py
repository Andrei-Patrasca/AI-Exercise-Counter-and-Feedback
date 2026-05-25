import bcrypt
from database.db import get_connection

class AuthManager:

    def register_user(self, username, email, password):
        """
        Creates a new user. Returns (True, "success") or (False, "error message").
        """
        if not username or not email or not password:
            return False, "All fields are required."

        # Hash the password before storing — never store plain text
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed.decode("utf-8"))
            )
            conn.commit()
            conn.close()
            return True, "Registration successful."
        except Exception as e:
            error = str(e)
            if "username" in error:
                return False, "Username already taken."
            elif "email" in error:
                return False, "Email already registered."
            return False, f"Database error: {error}"

    def login_user(self, username, password):
        """
        Checks credentials. Returns (True, user_row) or (False, "error message").
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            return False, "Username not found."

        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        )

        if not password_matches:
            return False, "Incorrect password."

        return True, user

    def update_user(self, user_id, username=None, email=None, password=None):
        """Updates account fields. Only updates fields that are provided."""
        conn = get_connection()
        cursor = conn.cursor()

        if username:
            cursor.execute("UPDATE users SET username=? WHERE id=?", (username, user_id))
        if email:
            cursor.execute("UPDATE users SET email=? WHERE id=?", (email, user_id))
        if password:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password=? WHERE id=?",
                           (hashed.decode("utf-8"), user_id))

        conn.commit()
        conn.close()

    def update_reminder(self, user_id, reminder_time, reminder_email):
        """Saves the daily workout reminder settings for a user."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET reminder_time=?, reminder_email=? WHERE id=?",
            (reminder_time, reminder_email, user_id)
        )
        conn.commit()
        conn.close()

    def update_reminder(self, user_id, reminder_time, reminder_enabled):
        """Save reminder time and enabled state for a user."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET reminder_time=?, reminder_enabled=? WHERE id=?",
            (reminder_time, 1 if reminder_enabled else 0, user_id)
        )
        conn.commit()
        conn.close()

    def get_user_by_id(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user