import numpy as np


class ExerciseClassifier:
    KEYPOINTS = {
        "LEFT_SHOULDER": 5,  "RIGHT_SHOULDER": 6,
        "LEFT_ELBOW":    7,  "RIGHT_ELBOW":    8,
        "LEFT_WRIST":    9,  "RIGHT_WRIST":   10,
        "LEFT_HIP":     11,  "RIGHT_HIP":     12,
        "LEFT_KNEE":    13,  "RIGHT_KNEE":    14,
        "LEFT_ANKLE":   15,  "RIGHT_ANKLE":   16,
    }

    def __init__(self):
        self.history      = []
        self.history_size = 15
        self.current_exercise = None

    def _get(self, landmarks, name):
        return landmarks[self.KEYPOINTS[name]]

    def _angle(self, a, b, c):
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        ba = a - b
        bc = c - b
        cosine = np.dot(ba, bc) / (
            np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6
        )
        return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    def classify(self, landmarks):
        if landmarks is None or len(landmarks) < 17:
            return "unknown"
        try:
            ls = self._get(landmarks, "LEFT_SHOULDER")
            rs = self._get(landmarks, "RIGHT_SHOULDER")
            lh = self._get(landmarks, "LEFT_HIP")
            rh = self._get(landmarks, "RIGHT_HIP")
            lk = self._get(landmarks, "LEFT_KNEE")
            rk = self._get(landmarks, "RIGHT_KNEE")
            la = self._get(landmarks, "LEFT_ANKLE")
            ra = self._get(landmarks, "RIGHT_ANKLE")
            le = self._get(landmarks, "LEFT_ELBOW")
            re = self._get(landmarks, "RIGHT_ELBOW")
            lw = self._get(landmarks, "LEFT_WRIST")
            rw = self._get(landmarks, "RIGHT_WRIST")

            shoulder_y = (ls.y + rs.y) / 2
            hip_y      = (lh.y + rh.y) / 2
            torso_diff = abs(hip_y - shoulder_y)

            knee_angle  = (self._angle(lh, lk, la) + self._angle(rh, rk, ra)) / 2
            hip_angle   = (self._angle(ls, lh, lk) + self._angle(rs, rh, rk)) / 2

            if torso_diff < 0.15:
                prediction = "pushup"
            elif knee_angle < 145 and torso_diff > 0.15:
                prediction = "squat"
            elif knee_angle > 150 and hip_angle > 150 and torso_diff > 0.15:
                prediction = "bicep_curl"
            else:
                prediction = "unknown"

        except Exception:
            prediction = "unknown"

        self.history.append(prediction)
        if len(self.history) > self.history_size:
            self.history.pop(0)

        smoothed = max(set(self.history), key=self.history.count)
        self.current_exercise = smoothed
        return smoothed

    def get_display_name(self, exercise):
        return {
            "pushup":     "Push-up",
            "squat":      "Squat",
            "bicep_curl": "Bicep Curl",
            "unknown":    "No exercise detected"
        }.get(exercise, "Unknown")

    def reset(self):
        self.history = []
        self.current_exercise = None