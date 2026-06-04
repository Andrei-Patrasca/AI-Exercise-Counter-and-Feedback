import numpy as np
import os

MODEL_PATH  = os.path.join(os.path.dirname(__file__), "exercise_model.keras")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "label_classes.npy")


class ExerciseClassifierCNN:
    def __init__(self):
        self.history      = []
        self.history_size = 15
        self.current_exercise = None
        self.model   = None
        self.classes = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH):
            import tensorflow as tf
            self.model   = tf.keras.models.load_model(MODEL_PATH)
            self.classes = np.load(LABELS_PATH, allow_pickle=True)
            print(f"CNN classifier loaded. Classes: {self.classes}")
        else:
            print("No trained model found — using rule-based classifier.")

    def classify(self, landmarks):
        if landmarks is None or len(landmarks) < 17:
            return "unknown"

        if self.model is not None:
            # CNN path
            features = np.array(
                [[lm.x, lm.y, lm.z] for lm in landmarks],
                dtype=np.float32
            ).flatten().reshape(1, -1)

            probs      = self.model.predict(features, verbose=0)[0]
            confidence = np.max(probs)

            if confidence < 0.7:
                prediction = "unknown"
            else:
                prediction = self.classes[np.argmax(probs)]
        else:
            # Fallback to rules if no model trained yet
            prediction = self._rule_based(landmarks)

        self.history.append(prediction)
        if len(self.history) > self.history_size:
            self.history.pop(0)

        smoothed = max(set(self.history), key=self.history.count)
        self.current_exercise = smoothed
        return smoothed

    def _rule_based(self, landmarks):
        """Fallback rules used before CNN is trained."""
        try:
            import numpy as np
            KEYPOINTS = {
                "LEFT_SHOULDER": 5,  "RIGHT_SHOULDER": 6,
                "LEFT_HIP":     11,  "RIGHT_HIP":     12,
                "LEFT_KNEE":    13,  "RIGHT_KNEE":    14,
                "LEFT_ANKLE":   15,  "RIGHT_ANKLE":   16,
                "LEFT_ELBOW":    7,  "RIGHT_ELBOW":    8,
                "LEFT_WRIST":    9,  "RIGHT_WRIST":   10,
            }
            def g(n): return landmarks[KEYPOINTS[n]]
            def ang(a, b, c):
                a = np.array([a.x, a.y])
                b = np.array([b.x, b.y])
                c = np.array([c.x, c.y])
                ba, bc = a-b, c-b
                cos = np.dot(ba, bc)/(np.linalg.norm(ba)*np.linalg.norm(bc)+1e-6)
                return np.degrees(np.arccos(np.clip(cos, -1, 1)))

            shoulder_y  = (g("LEFT_SHOULDER").y  + g("RIGHT_SHOULDER").y)  / 2
            hip_y       = (g("LEFT_HIP").y        + g("RIGHT_HIP").y)       / 2
            torso_diff  = abs(hip_y - shoulder_y)
            knee_angle  = (ang(g("LEFT_HIP"),  g("LEFT_KNEE"),  g("LEFT_ANKLE")) +
                           ang(g("RIGHT_HIP"), g("RIGHT_KNEE"), g("RIGHT_ANKLE"))) / 2
            hip_angle   = (ang(g("LEFT_SHOULDER"),  g("LEFT_HIP"),  g("LEFT_KNEE")) +
                           ang(g("RIGHT_SHOULDER"), g("RIGHT_HIP"), g("RIGHT_KNEE"))) / 2

            if torso_diff < 0.15:           return "pushup"
            elif knee_angle < 145:          return "squat"
            elif knee_angle > 150 and hip_angle > 150: return "bicep_curl"
            else:                           return "unknown"
        except Exception:
            return "unknown"

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