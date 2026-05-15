class RepCounter:
    THRESHOLDS = {
        "bicep_curl": {"down": 160, "up": 50},
        "squat":      {"down": 90,  "up": 160},
        "pushup":     {"down": 90,  "up": 160},
    }

    def __init__(self):
        self.counts = {"bicep_curl": 0, "squat": 0, "pushup": 0}
        self.stages = {"bicep_curl": None, "squat": None, "pushup": None}

    def process(self, exercise, angle):
        if exercise not in self.THRESHOLDS or angle is None:
            return False

        t     = self.THRESHOLDS[exercise]
        stage = self.stages[exercise]
        rep_completed = False

        if exercise == "bicep_curl":
            if angle > t["down"]:
                self.stages[exercise] = "down"
            if angle < t["up"] and stage == "down":
                self.stages[exercise] = "up"
                self.counts[exercise] += 1
                rep_completed = True
        else:
            if angle < t["down"]:
                self.stages[exercise] = "down"
            if angle > t["up"] and stage == "down":
                self.stages[exercise] = "up"
                self.counts[exercise] += 1
                rep_completed = True

        return rep_completed

    def get_count(self, exercise):
        return self.counts.get(exercise, 0)

    def get_progress(self, exercise, angle):
        if exercise not in self.THRESHOLDS or angle is None:
            return 0.0
        t = self.THRESHOLDS[exercise]
        if exercise == "bicep_curl":
            progress = 1.0 - ((angle - t["up"]) / (t["down"] - t["up"]))
        else:
            progress = 1.0 - ((angle - t["down"]) / (t["up"] - t["down"]))
        return max(0.0, min(1.0, progress))

    def reset(self):
        for key in self.counts:
            self.counts[key] = 0
            self.stages[key] = None