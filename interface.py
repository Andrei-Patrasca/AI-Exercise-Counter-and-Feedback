import tkinter as tk
from tkinter import messagebox
from app import run_pose_app
from tkinter import ttk


def start_biceps():
    run_pose_app()

def start_pushups():
    print("Push-ups not implemented yet")

def start_squats():
    print("Squats not implemented yet")

def start_abs():
    print("Abs crunches not implemented yet")

# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("Exercise Counter")

# Full screen
root.attributes("-fullscreen", True)

# Black background
root.configure(bg="black")

# Title label
title_label = tk.Label(
    root,
    text="Exercise Counter",
    font=("Arial", 32, "bold"),
    fg="white",
    bg="black"
)
title_label.pack(pady=20)

# Frame for buttons (horizontal layout)
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=20)

# Button style
button_style = {
    "font": ("Arial", 18, "bold"),
    "bg": "#222222",
    "fg": "white",
    "activebackground": "#444444",
    "activeforeground": "white",
    "width": 15,
    "height": 2,
    "bd": 0,
    "highlightthickness": 0
}

# Buttons left → right
btn_biceps = tk.Button(button_frame, text="Biceps Curls", command=start_biceps, **button_style)
btn_pushups = tk.Button(button_frame, text="Push-ups", command=start_pushups, **button_style)
btn_squats = tk.Button(button_frame, text="Squats", command=start_squats, **button_style)
btn_abs = tk.Button(button_frame, text="Abs Crunches", command=start_abs, **button_style)

btn_biceps.grid(row=0, column=0, padx=20)
btn_pushups.grid(row=0, column=1, padx=20)
btn_squats.grid(row=0, column=2, padx=20)
btn_abs.grid(row=0, column=3, padx=20)

# Escape key closes full screen
def exit_fullscreen(event):
    root.attributes("-fullscreen", False)

root.bind("<Escape>", exit_fullscreen)

root.mainloop()
