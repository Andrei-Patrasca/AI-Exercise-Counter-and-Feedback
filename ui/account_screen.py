import customtkinter as ctk
from auth.auth_manager import AuthManager
from auth.task_installer import install_task, remove_task, task_exists
from ui.styles import *


class AccountScreen(ctk.CTkFrame):
    def __init__(self, master, user, on_back, on_logout):
        super().__init__(master, fg_color=COLORS["bg"])
        self.user      = dict(user)
        self.on_back   = on_back
        self.on_logout = on_logout
        self.auth      = AuthManager()
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
            top, text="← Back", width=100, height=34,
            font=FONT_BODY, command=self.on_back,
            fg_color="transparent", border_width=1,
            border_color=COLORS["accent"],
            text_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"]
        ).grid(row=0, column=0, padx=20, pady=10)

        ctk.CTkLabel(top, text="Account Settings",
                     font=FONT_H2,
                     text_color=COLORS["accent"]).grid(
            row=0, column=1, padx=20, pady=10)

        # Scrollable content area
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg"]
        )
        scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        # ── Profile card ───────────────────────────────────────────────────────
        profile_card = ctk.CTkFrame(scroll, fg_color=COLORS["surface"],
                                    corner_radius=16)
        profile_card.grid(row=0, column=0, padx=60, pady=(20, 10),
                          sticky="ew")
        profile_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(profile_card, text="👤  Profile",
                     font=FONT_H2,
                     text_color=COLORS["accent"]).pack(pady=(24, 4))
        ctk.CTkLabel(profile_card,
                     text="Update your account information",
                     font=FONT_BODY,
                     text_color=COLORS["text_sub"]).pack(pady=(0, 16))

        # Username
        ctk.CTkLabel(profile_card, text="Username",
                     font=FONT_SMALL,
                     text_color=COLORS["text_sub"]).pack(anchor="w", padx=40)
        self.username_entry = ctk.CTkEntry(
            profile_card, width=400, height=44, font=FONT_BODY)
        self.username_entry.insert(0, self.user["username"])
        self.username_entry.pack(pady=(2, 10))

        # Email
        ctk.CTkLabel(profile_card, text="Email",
                     font=FONT_SMALL,
                     text_color=COLORS["text_sub"]).pack(anchor="w", padx=40)
        self.email_entry = ctk.CTkEntry(
            profile_card, width=400, height=44, font=FONT_BODY)
        self.email_entry.insert(0, self.user["email"])
        self.email_entry.pack(pady=(2, 10))

        # New password
        ctk.CTkLabel(profile_card,
                     text="New Password (leave blank to keep current)",
                     font=FONT_SMALL,
                     text_color=COLORS["text_sub"]).pack(anchor="w", padx=40)
        self.password_entry = ctk.CTkEntry(
            profile_card, width=400, height=44,
            font=FONT_BODY, show="●",
            placeholder_text="New password")
        self.password_entry.pack(pady=(2, 10))

        # Confirm password
        self.confirm_entry = ctk.CTkEntry(
            profile_card, width=400, height=44,
            font=FONT_BODY, show="●",
            placeholder_text="Confirm new password")
        self.confirm_entry.pack(pady=(2, 10))

        # Feedback
        self.profile_feedback = ctk.CTkLabel(
            profile_card, text="", font=FONT_SMALL,
            text_color=COLORS["accent"])
        self.profile_feedback.pack(pady=(4, 0))

        # Save button
        ctk.CTkButton(
            profile_card, text="Save Changes",
            width=400, height=44, font=FONT_H3,
            command=self._save_profile,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#000000"
        ).pack(pady=(8, 24))

        # ── Reminder card ──────────────────────────────────────────────────────
        reminder_card = ctk.CTkFrame(scroll, fg_color=COLORS["surface"],
                                     corner_radius=16)
        reminder_card.grid(row=1, column=0, padx=60, pady=(10, 10),
                           sticky="ew")
        reminder_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(reminder_card, text="🔔  Workout Reminder",
                     font=FONT_H2,
                     text_color=COLORS["accent"]).pack(pady=(24, 4))
        ctk.CTkLabel(reminder_card,
                     text="Sends a daily reminder email at the chosen time",
                     font=FONT_BODY,
                     text_color=COLORS["text_sub"]).pack(pady=(0, 16))

        # Enable toggle
        toggle_row = ctk.CTkFrame(reminder_card, fg_color="transparent")
        toggle_row.pack(pady=(0, 12))

        ctk.CTkLabel(toggle_row, text="Enable daily reminder:",
                     font=FONT_BODY,
                     text_color=COLORS["text"]).pack(side="left", padx=(0, 12))

        self.reminder_enabled = ctk.BooleanVar(
            value=bool(self.user.get("reminder_enabled", 0))
        )
        self.toggle = ctk.CTkSwitch(
            toggle_row, text="",
            variable=self.reminder_enabled,
            onvalue=True, offvalue=False,
            command=self._on_toggle,
            progress_color=COLORS["accent"]
        )
        self.toggle.pack(side="left")

        # Time picker row
        time_row = ctk.CTkFrame(reminder_card, fg_color="transparent")
        time_row.pack(pady=(0, 12))

        ctk.CTkLabel(time_row, text="Reminder time:",
                     font=FONT_BODY,
                     text_color=COLORS["text"]).pack(side="left", padx=(0, 12))

        # Hour spinbox
        current_time = self.user.get("reminder_time") or "08:00"
        try:
            h, m = current_time.split(":")
        except Exception:
            h, m = "08", "00"

        self.hour_var = ctk.StringVar(value=h)
        self.min_var  = ctk.StringVar(value=m)

        hour_frame = ctk.CTkFrame(time_row, fg_color="transparent")
        hour_frame.pack(side="left")

        ctk.CTkButton(hour_frame, text="▲", width=36, height=24,
                      font=FONT_SMALL,
                      command=lambda: self._increment("hour", 1),
                      fg_color=COLORS["surface_alt"],
                      text_color=COLORS["text"]).pack()
        self.hour_lbl = ctk.CTkLabel(
            hour_frame, textvariable=self.hour_var,
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["accent"], width=52)
        self.hour_lbl.pack()
        ctk.CTkButton(hour_frame, text="▼", width=36, height=24,
                      font=FONT_SMALL,
                      command=lambda: self._increment("hour", -1),
                      fg_color=COLORS["surface_alt"],
                      text_color=COLORS["text"]).pack()

        ctk.CTkLabel(time_row, text=":",
                     font=("Segoe UI", 28, "bold"),
                     text_color=COLORS["accent"]).pack(side="left", padx=4)

        min_frame = ctk.CTkFrame(time_row, fg_color="transparent")
        min_frame.pack(side="left")

        ctk.CTkButton(min_frame, text="▲", width=36, height=24,
                      font=FONT_SMALL,
                      command=lambda: self._increment("min", 5),
                      fg_color=COLORS["surface_alt"],
                      text_color=COLORS["text"]).pack()
        self.min_lbl = ctk.CTkLabel(
            min_frame, textvariable=self.min_var,
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["accent"], width=52)
        self.min_lbl.pack()
        ctk.CTkButton(min_frame, text="▼", width=36, height=24,
                      font=FONT_SMALL,
                      command=lambda: self._increment("min", -5),
                      fg_color=COLORS["surface_alt"],
                      text_color=COLORS["text"]).pack()

        # Reminder feedback
        self.reminder_feedback = ctk.CTkLabel(
            reminder_card, text="", font=FONT_SMALL,
            text_color=COLORS["accent"])
        self.reminder_feedback.pack(pady=(8, 0))

        # Save reminder button
        ctk.CTkButton(
            reminder_card, text="Save Reminder Settings",
            width=400, height=44, font=FONT_H3,
            command=self._save_reminder,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#000000"
        ).pack(pady=(8, 12))

        # Install/uninstall service
        service_row = ctk.CTkFrame(reminder_card, fg_color="transparent")
        service_row.pack(pady=(0, 24))

        self.install_btn = ctk.CTkButton(
            service_row,
            text="✔  Install Background Service" if not task_exists()
                 else "✔  Service Installed",
            width=240, height=38, font=FONT_BODY,
            command=self._install_service,
            fg_color="transparent", border_width=1,
            border_color=COLORS["accent"],
            text_color=COLORS["accent"],
            hover_color=COLORS["accent_dark"],
            state="normal" if not task_exists() else "disabled"
        )
        self.install_btn.pack(side="left", padx=6)

        self.remove_btn = ctk.CTkButton(
            service_row,
            text="✖  Remove Service",
            width=180, height=38, font=FONT_BODY,
            command=self._remove_service,
            fg_color="transparent", border_width=1,
            border_color=COLORS["error"],
            text_color=COLORS["error"],
            hover_color="#4a0000",
            state="normal" if task_exists() else "disabled"
        )
        self.remove_btn.pack(side="left", padx=6)

        # ── Danger zone card ───────────────────────────────────────────────────
        danger_card = ctk.CTkFrame(scroll, fg_color=COLORS["surface"],
                                   corner_radius=16)
        danger_card.grid(row=2, column=0, padx=60, pady=(10, 20),
                         sticky="ew")
        danger_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(danger_card, text="Logout",
                     font=FONT_H2,
                     text_color=COLORS["error"]).pack(pady=(24, 8))

        ctk.CTkButton(
            danger_card, text="Logout from FitTrack",
            width=400, height=44, font=FONT_H3,
            command=self.on_logout,
            fg_color="transparent", border_width=1,
            border_color=COLORS["error"],
            text_color=COLORS["error"],
            hover_color="#4a0000"
        ).pack(pady=(0, 24))

        # Apply initial toggle state
        self._on_toggle()

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _on_toggle(self):
        """Enable/disable time picker based on toggle state."""
        state = "normal" if self.reminder_enabled.get() else "disabled"
        self.hour_lbl.configure(
            text_color=COLORS["accent"] if self.reminder_enabled.get()
                       else COLORS["text_muted"]
        )
        self.min_lbl.configure(
            text_color=COLORS["accent"] if self.reminder_enabled.get()
                       else COLORS["text_muted"]
        )

    def _increment(self, field, delta):
        if not self.reminder_enabled.get():
            return
        if field == "hour":
            val = (int(self.hour_var.get()) + delta) % 24
            self.hour_var.set(f"{val:02d}")
        else:
            val = (int(self.min_var.get()) + delta) % 60
            self.min_var.set(f"{val:02d}")

    def _save_profile(self):
        username = self.username_entry.get().strip()
        email    = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm  = self.confirm_entry.get()

        if not username or not email:
            self.profile_feedback.configure(
                text="Username and email cannot be empty.",
                text_color=COLORS["error"])
            return
        if password and password != confirm:
            self.profile_feedback.configure(
                text="Passwords do not match.",
                text_color=COLORS["error"])
            return
        if password and len(password) < 6:
            self.profile_feedback.configure(
                text="Password must be at least 6 characters.",
                text_color=COLORS["error"])
            return

        self.auth.update_user(
            self.user["id"],
            username=username if username != self.user["username"] else None,
            email   =email    if email    != self.user["email"]    else None,
            password=password if password else None
        )
        self.profile_feedback.configure(
            text="✓ Profile saved successfully.",
            text_color=COLORS["accent"])

    def _save_reminder(self):
        time_str = f"{self.hour_var.get()}:{self.min_var.get()}"
        enabled  = self.reminder_enabled.get()

        self.auth.update_reminder(
            self.user["id"], time_str, enabled
        )
        self.reminder_feedback.configure(
            text=f"✓ Reminder {'enabled' if enabled else 'disabled'}"
                 + (f" at {time_str}" if enabled else "") + ". Saved.",
            text_color=COLORS["accent"]
        )

    def _install_service(self):
        ok, msg = install_task()
        if ok:
            self.reminder_feedback.configure(
                text="✓ " + msg, text_color=COLORS["accent"])
            self.install_btn.configure(
                text="✔  Service Installed", state="disabled")
            self.remove_btn.configure(state="normal")
        else:
            self.reminder_feedback.configure(
                text="✗ " + msg, text_color=COLORS["error"])

    def _remove_service(self):
        ok, msg = remove_task()
        if ok:
            self.reminder_feedback.configure(
                text="✓ " + msg, text_color=COLORS["accent"])
            self.remove_btn.configure(state="disabled")
            self.install_btn.configure(
                text="✔  Install Background Service", state="normal")
        else:
            self.reminder_feedback.configure(
                text="✗ " + msg, text_color=COLORS["error"])