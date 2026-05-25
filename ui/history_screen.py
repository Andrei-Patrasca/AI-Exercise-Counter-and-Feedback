import customtkinter as ctk
from database.workout_manager import WorkoutManager
from ui.styles import *


class HistoryScreen(ctk.CTkFrame):
    def __init__(self, master, user, on_back):
        super().__init__(master, fg_color=COLORS["bg"])
        self.user    = user
        self.on_back = on_back
        self.workout_manager = WorkoutManager(user["id"])
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top bar
        top = ctk.CTkFrame(self, fg_color=COLORS["surface"],
                           corner_radius=0, height=56)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            top, text="← Back",
            width=100, height=34,
            font=FONT_BODY,
            command=self.on_back,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["accent"],
            text_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"]
        ).grid(row=0, column=0, padx=20, pady=10)

        ctk.CTkLabel(top, text="Workout History",
                     font=FONT_H2,
                     text_color=COLORS["accent"]).grid(
            row=0, column=1, padx=20, pady=10)

        # Main content — two panels side by side
        content = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        content.grid(row=1, column=0, sticky="nsew", padx=16, pady=16)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)

        # LEFT — workout list
        left = ctk.CTkFrame(content, fg_color=COLORS["surface"],
                            corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Sessions",
                     font=FONT_H3,
                     text_color=COLORS["accent"]).grid(
            row=0, column=0, pady=(16, 8))

        self.workout_list = ctk.CTkScrollableFrame(
            left, fg_color=COLORS["surface_alt"], corner_radius=8
        )
        self.workout_list.grid(row=1, column=0, sticky="nsew",
                               padx=10, pady=(0, 10))

        # RIGHT — workout detail
        right = ctk.CTkFrame(content, fg_color=COLORS["surface"],
                             corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self.detail_title = ctk.CTkLabel(
            right, text="Select a session to view details",
            font=FONT_H3, text_color=COLORS["accent"]
        )
        self.detail_title.grid(row=0, column=0, pady=(16, 2))

        self.time_lbl = ctk.CTkLabel(
            right, text="",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["accent"]
        )
        self.time_lbl.grid(row=1, column=0, pady=(0, 6))

        self.detail_frame = ctk.CTkScrollableFrame(
            right, fg_color=COLORS["surface_alt"], corner_radius=8
        )
        self.detail_frame.grid(row=2, column=0, sticky="nsew",
                               padx=10, pady=(0, 10))

        self.summary_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.summary_frame.grid(row=3, column=0, sticky="ew",
                                padx=12, pady=(0, 16))

        self._load_workouts()

    def _load_workouts(self):
        """Load all workouts into the left panel."""
        for w in self.workout_list.winfo_children():
            w.destroy()

        workouts = self.workout_manager.get_workouts()

        if not workouts:
            ctk.CTkLabel(
                self.workout_list,
                text="No workouts yet.\nComplete a session first!",
                font=FONT_BODY,
                text_color=COLORS["text_sub"],
                justify="center"
            ).pack(pady=20)
            return

        for i, workout in enumerate(workouts):
            workout_id  = workout["id"]
            date        = workout["date"]
            start_time  = workout["start_time"]
            end_time    = workout["end_time"] or "In progress"

            # Duration calculation
            duration = ""
            if workout["end_time"]:
                try:
                    from datetime import datetime
                    fmt  = "%H:%M:%S"
                    diff = datetime.strptime(end_time, fmt) - \
                           datetime.strptime(start_time, fmt)
                    mins = int(diff.total_seconds() // 60)
                    secs = int(diff.total_seconds() % 60)
                    duration = f"  •  {mins}m {secs}s"
                except Exception:
                    duration = ""

            btn = ctk.CTkButton(
                self.workout_list,
                text=f"Workout {i + 1}\n{date}  •  {start_time}{duration}",
                width=200, height=56,
                font=FONT_SMALL,
                anchor="w",
                command=lambda wid=workout_id, idx=i+1: self._load_detail(wid, idx),
                fg_color=COLORS["surface"],
                hover_color=COLORS["surface_alt"],
                text_color=COLORS["text"],
                corner_radius=8
            )
            btn.pack(fill="x", padx=6, pady=4)

    def _load_detail(self, workout_id, index):
        from database.db import get_connection
        from datetime import datetime

        # Clear panels
        for w in self.detail_frame.winfo_children():
            w.destroy()
        for w in self.summary_frame.winfo_children():
            w.destroy()

        # Get workout times for duration
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT start_time, end_time FROM workouts WHERE id=?",
            (workout_id,)
        )
        row = cur.fetchone()
        conn.close()

        # Calculate duration string
        duration_str = ""
        if row and row["end_time"]:
            try:
                fmt = "%H:%M:%S"
                start = datetime.strptime(row["start_time"], fmt)
                end = datetime.strptime(row["end_time"], fmt)
                total = int((end - start).total_seconds())
                h = total // 3600
                m = (total % 3600) // 60
                if h > 0:
                    duration_str = f"  |  Duration: {h}h {m} min"
                else:
                    duration_str = f"  |  Duration: {m} min"
            except Exception:
                duration_str = ""

        self.detail_title.configure(
            text=f"Workout {index} — Details{duration_str}"
        )

        # Load sets
        sets = self.workout_manager.get_sets(workout_id)

        if not sets:
            ctk.CTkLabel(
                self.detail_frame,
                text="No exercises recorded.",
                font=FONT_BODY,
                text_color=COLORS["text_sub"]
            ).pack(pady=20)
            return

        names = {
            "bicep_curl": "Bicep Curl",
            "squat": "Squat",
            "pushup": "Push-up"
        }
        totals = {"bicep_curl": 0, "squat": 0, "pushup": 0}

        for s in sets:
            exercise = s["exercise"]
            reps = s["reps"]
            timestamp = s["timestamp"]
            totals[exercise] = totals.get(exercise, 0) + reps

            row_frame = ctk.CTkFrame(
                self.detail_frame,
                fg_color=COLORS["surface"],
                corner_radius=8
            )
            row_frame.pack(fill="x", padx=6, pady=3)

            ctk.CTkLabel(
                row_frame,
                text=f"  {names.get(exercise, exercise)}",
                font=FONT_BODY,
                text_color=COLORS["text"],
                anchor="w"
            ).pack(side="left", padx=8, pady=8)

            ctk.CTkLabel(
                row_frame,
                text=timestamp,
                font=FONT_SMALL,
                text_color=COLORS["text_muted"],
                anchor="e"
            ).pack(side="right", padx=4, pady=8)

            ctk.CTkLabel(
                row_frame,
                text=f"{reps} reps",
                font=("Segoe UI", 13, "bold"),
                text_color=COLORS["accent"],
                anchor="e"
            ).pack(side="right", padx=8, pady=8)

        # Summary totals
        ctk.CTkLabel(
            self.summary_frame,
            text="Totals:",
            font=FONT_H3,
            text_color=COLORS["text_sub"]
        ).pack(side="left", padx=(0, 12))

        for exercise, count in totals.items():
            if count > 0:
                ctk.CTkLabel(
                    self.summary_frame,
                    text=f"{names.get(exercise, exercise)}: {count}",
                    font=("Segoe UI", 13, "bold"),
                    text_color=COLORS["accent"]
                ).pack(side="left", padx=8)