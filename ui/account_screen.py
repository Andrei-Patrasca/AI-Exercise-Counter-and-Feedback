import customtkinter as ctk
from auth.auth_manager import AuthManager
from ui.styles import *


class AccountScreen(ctk.CTkFrame):
    def __init__(self, master, user, on_back, on_logout):
        super().__init__(master, fg_color=COLORS["bg"])
        self.user     = dict(user)
        self.on_back  = on_back
        self.on_logout= on_logout
        self.auth     = AuthManager()
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

        ctk.CTkLabel(top, text="Account Settings",
                     font=FONT_H2,
                     text_color=COLORS["accent"]).grid(
            row=0, column=1, padx=20, pady=10)

        # Center card
        center = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        center.grid(row=1, column=0, sticky="nsew")
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(center, fg_color=COLORS["surface"],
                            corner_radius=16)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.configure(width=480, height=620)
        card.grid_propagate(False)

        ctk.CTkLabel(card, text="⚙️  Profile",
                     font=FONT_H2,
                     text_color=COLORS["accent"]).pack(pady=(30, 4))
        ctk.CTkLabel(card,
                     text="Update your account information below",
                     font=FONT_BODY,
                     text_color=COLORS["text_sub"]).pack(pady=(0, 20))

        # Username
        ctk.CTkLabel(card, text="Username",
                     font=FONT_SMALL,
                     text_color=COLORS["text_sub"],
                     anchor="w").pack(fill="x", padx=40)
        self.username_entry = ctk.CTkEntry(
            card, width=360, height=44, font=FONT_BODY
        )
        self.username_entry.insert(0, self.user["username"])
        self.username_entry.pack(pady=(2, 10))

        # Email
        ctk.CTkLabel(card, text="Email",
                     font=FONT_SMALL,
                     text_color=COLORS["text_sub"],
                     anchor="w").pack(fill="x", padx=40)
        self.email_entry = ctk.CTkEntry(
            card, width=360, height=44, font=FONT_BODY
        )
        self.email_entry.insert(0, self.user["email"])
        self.email_entry.pack(pady=(2, 10))

        # New password
        ctk.CTkLabel(card, text="New Password (leave blank to keep current)",
                     font=FONT_SMALL,
                     text_color=COLORS["text_sub"],
                     anchor="w").pack(fill="x", padx=40)
        self.password_entry = ctk.CTkEntry(
            card, width=360, height=44,
            font=FONT_BODY, show="●",
            placeholder_text="New password"
        )
        self.password_entry.pack(pady=(2, 10))

        # Confirm password
        self.confirm_entry = ctk.CTkEntry(
            card, width=360, height=44,
            font=FONT_BODY, show="●",
            placeholder_text="Confirm new password"
        )
        self.confirm_entry.pack(pady=(2, 10))

        # Feedback label
        self.feedback_lbl = ctk.CTkLabel(
            card, text="", font=FONT_SMALL,
            text_color=COLORS["accent"]
        )
        self.feedback_lbl.pack(pady=(4, 0))

        # Save button
        ctk.CTkButton(
            card, text="Save Changes",
            width=360, height=44,
            font=FONT_H3,
            command=self._save,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#000000"
        ).pack(pady=(8, 6))

        # Divider
        ctk.CTkFrame(card, fg_color=COLORS["border"],
                     height=1, width=360).pack(pady=12)

        # Logout
        ctk.CTkButton(
            card, text="Logout",
            width=360, height=44,
            font=FONT_H3,
            command=self.on_logout,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["error"],
            text_color=COLORS["error"],
            hover_color="#4a0000"
        ).pack(pady=6)

    def _save(self):
        username = self.username_entry.get().strip()
        email    = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm  = self.confirm_entry.get()

        if not username or not email:
            self.feedback_lbl.configure(
                text="Username and email cannot be empty.",
                text_color=COLORS["error"]
            )
            return

        if password and password != confirm:
            self.feedback_lbl.configure(
                text="Passwords do not match.",
                text_color=COLORS["error"]
            )
            return

        if password and len(password) < 6:
            self.feedback_lbl.configure(
                text="Password must be at least 6 characters.",
                text_color=COLORS["error"]
            )
            return

        self.auth.update_user(
            self.user["id"],
            username = username if username != self.user["username"] else None,
            email    = email    if email    != self.user["email"]    else None,
            password = password if password else None
        )

        self.feedback_lbl.configure(
            text="✓ Changes saved successfully.",
            text_color=COLORS["accent"]
        )