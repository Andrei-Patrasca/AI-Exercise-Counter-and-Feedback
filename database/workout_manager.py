from database.db import get_connection
from datetime import datetime


class WorkoutManager:
    def __init__(self, user_id):
        self.user_id    = user_id
        self.workout_id = None

    def start_workout(self):
        now  = datetime.now()
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO workouts (user_id, date, start_time) VALUES (?, ?, ?)",
            (self.user_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))
        )
        conn.commit()
        self.workout_id = cur.lastrowid
        conn.close()
        return self.workout_id

    def log_set(self, exercise, reps):
        if not self.workout_id or reps <= 0:
            return
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO exercise_sets (workout_id, exercise, reps, timestamp) VALUES (?, ?, ?, ?)",
            (self.workout_id, exercise,
             reps, datetime.now().strftime("%H:%M:%S"))
        )
        conn.commit()
        conn.close()

    def finish_workout(self):
        if not self.workout_id:
            return
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            "UPDATE workouts SET end_time=? WHERE id=?",
            (datetime.now().strftime("%H:%M:%S"), self.workout_id)
        )
        conn.commit()
        conn.close()

    def get_workouts(self):
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            """SELECT id, date, start_time, end_time FROM workouts
               WHERE user_id=? ORDER BY date DESC, start_time DESC""",
            (self.user_id,)
        )
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_sets(self, workout_id):
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            """SELECT exercise, reps, timestamp FROM exercise_sets
               WHERE workout_id=? ORDER BY id ASC""",
            (workout_id,)
        )
        rows = cur.fetchall()
        conn.close()
        return rows