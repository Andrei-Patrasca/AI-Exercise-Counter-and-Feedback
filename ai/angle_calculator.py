import numpy as np


class AngleCalculator:
    KEYPOINTS = {
        "NOSE": 0,
        "LEFT_SHOULDER": 5,  "RIGHT_SHOULDER": 6,
        "LEFT_ELBOW":    7,  "RIGHT_ELBOW":    8,
        "LEFT_WRIST":    9,  "RIGHT_WRIST":   10,
        "LEFT_HIP":     11,  "RIGHT_HIP":     12,
        "LEFT_KNEE":    13,  "RIGHT_KNEE":    14,
        "LEFT_ANKLE":   15,  "RIGHT_ANKLE":   16,
    }

    def calculate_angle(self, a, b, c):
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        ba = a - b
        bc = c - b
        cosine = np.dot(ba, bc) / (
            np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6
        )
        return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    def get_exercise_angles(self, landmarks, exercise):
        def lm(name):
            return landmarks[self.KEYPOINTS[name]]

        if exercise == "bicep_curl":
            left  = self.calculate_angle(
                lm("LEFT_SHOULDER"), lm("LEFT_ELBOW"), lm("LEFT_WRIST"))
            right = self.calculate_angle(
                lm("RIGHT_SHOULDER"), lm("RIGHT_ELBOW"), lm("RIGHT_WRIST"))
            return (left + right) / 2

        elif exercise == "squat":
            left  = self.calculate_angle(
                lm("LEFT_HIP"), lm("LEFT_KNEE"), lm("LEFT_ANKLE"))
            right = self.calculate_angle(
                lm("RIGHT_HIP"), lm("RIGHT_KNEE"), lm("RIGHT_ANKLE"))
            return (left + right) / 2

        elif exercise == "pushup":
            left  = self.calculate_angle(
                lm("LEFT_SHOULDER"), lm("LEFT_ELBOW"), lm("LEFT_WRIST"))
            right = self.calculate_angle(
                lm("RIGHT_SHOULDER"), lm("RIGHT_ELBOW"), lm("RIGHT_WRIST"))
            return (left + right) / 2

        return None