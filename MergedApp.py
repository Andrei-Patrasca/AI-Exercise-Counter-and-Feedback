import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import numpy as np

# ---------------- POSE TRACKER LOGIC (embedded version) ---------------- #

class PoseApp:
    def __init__(self, video_label):
        self.video_label = video_label
        self.cap = cv2.VideoCapture(0)

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

        self.counter = 0
        self.stage = None

        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5,
                                      min_tracking_confidence=0.5)

        self.running = False

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180:
            angle = 360 - angle
        return angle

    def start(self):
        self.running = True
        self.update_frame()

    def stop(self):
        self.running = False
        self.cap.release()

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)

        h, w, _ = image.shape

        try:
            landmarks = results.pose_landmarks.landmark

            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            angle = self.calculate_angle(shoulder, elbow, wrist)
            coords = tuple(np.multiply(elbow, [w, h]).astype(int))

            cv2.putText(image, str(int(angle)), coords,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if angle > 160:
                self.stage = "down"
            if angle < 30 and self.stage == "down":
                self.stage = "up"
                self.counter += 1

        except:
            pass

        # UI overlays
        cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)
        cv2.putText(image, 'REPS', (15, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(image, str(self.counter), (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

        cv2.putText(image, 'STAGE', (65, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(image, self.stage if self.stage else "", (60, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        # Convert to Tkinter image
        img = ImageTk.PhotoImage(Image.fromarray(image))
        self.video_label.imgtk = img
        self.video_label.configure(image=img)

        self.video_label.after(10, self.update_frame)


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("Exercise Counter")
root.attributes("-fullscreen", True)
root.configure(bg="black")

# Title
title_label = tk.Label(root, text="Exercise Counter",
                       font=("Arial", 32, "bold"),
                       fg="white", bg="black")
title_label.pack(pady=20)

# Button row
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=10)

# ---------------- ICONS (COMMENTED OUT FOR NOW) ---------------- #
"""
from PIL import Image

def load_icon(path, size=(64, 64)):
    img = Image.open(path).resize(size)
    return ImageTk.PhotoImage(img)

icon_biceps = load_icon("icon_biceps.png")
icon_pushups = load_icon("icon_pushups.png")
icon_squats = load_icon("icon_squats.png")
icon_abs = load_icon("icon_abs.png")
icon_exit = load_icon("icon_exit.png")
"""
# --------------------------------------------------------------- #

# Placeholder video label
video_label = Label(root, bg="black")
video_label.pack(pady=20)

pose_app = PoseApp(video_label)

# Shared button style
button_style = {
    "font": ("Arial", 18, "bold"),
    "bg": "#222222",
    "fg": "white",
    "activebackground": "#444444",
    "activeforeground": "white",
    "width": 15,
    "height": 2,
    "bd": 0
}

# Buttons (no icons)
tk.Button(button_frame, text="Biceps Curls",
          command=pose_app.start, **button_style).grid(row=0, column=0, padx=20)

tk.Button(button_frame, text="Push-ups",
          command=lambda: print("Push-ups"), **button_style).grid(row=0, column=1, padx=20)

tk.Button(button_frame, text="Squats",
          command=lambda: print("Squats"), **button_style).grid(row=0, column=2, padx=20)

tk.Button(button_frame, text="Abs Crunches",
          command=lambda: print("Abs"), **button_style).grid(row=0, column=3, padx=20)

# Exit button (safe override)
exit_style = button_style.copy()
exit_style["bg"] = "#880000"
exit_style["activebackground"] = "#aa0000"

tk.Button(button_frame, text="Exit",
          command=lambda: (pose_app.stop(), root.destroy()),
          **exit_style).grid(row=0, column=4, padx=20)

# ESC exits fullscreen
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

root.mainloop()
