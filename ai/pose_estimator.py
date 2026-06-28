import cv2
import numpy as np
from ultralytics import YOLO


class KeypointProxy:
    def __init__(self, x, y, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


class PoseEstimator:
    # Only the body connections — no face, no bounding box
    SKELETON_CONNECTIONS = [
        # Torso
        (5, 6),   # left shoulder - right shoulder
        (5, 11),  # left shoulder - left hip
        (6, 12),  # right shoulder - right hip
        (11, 12), # left hip - right hip
        # Left arm
        (5, 7),   # left shoulder - left elbow
        (7, 9),   # left elbow - left wrist
        # Right arm
        (6, 8),   # right shoulder - right elbow
        (8, 10),  # right elbow - right wrist
        # Left leg
        (11, 13), # left hip - left knee
        (13, 15), # left knee - left ankle
        # Right leg
        (12, 14), # right hip - right knee
        (14, 16), # right knee - right ankle
    ]

    def __init__(self):
        self.model = YOLO("yolov8n-pose.pt")

    def process_frame(self, frame):
        results = self.model(frame, verbose=False)
        landmarks = None
        annotated = frame.copy()

        if results and len(results) > 0:
            result = results[0]

            if (result.keypoints is not None
                    and len(result.keypoints.xy) > 0):
                h, w = frame.shape[:2]
                kp_xy  = result.keypoints.xy[0].cpu().numpy()
                kp_conf= result.keypoints.conf[0].cpu().numpy()

                landmarks = [
                    KeypointProxy(
                        kp_xy[i][0] / w,
                        kp_xy[i][1] / h,
                        float(kp_conf[i])
                    )
                    for i in range(len(kp_xy))
                ]

                # Draw clean skeleton manually
                self._draw_skeleton(annotated, kp_xy, kp_conf, h, w)

        return annotated, landmarks

    def _draw_skeleton(self, frame, kp_xy, kp_conf, h, w):
        # Draw connections
        for a, b in self.SKELETON_CONNECTIONS:
            if kp_conf[a] > 0.4 and kp_conf[b] > 0.4:
                x1, y1 = int(kp_xy[a][0]), int(kp_xy[a][1])
                x2, y2 = int(kp_xy[b][0]), int(kp_xy[b][1])
                cv2.line(frame, (x1, y1), (x2, y2), (57, 255, 20), 2)

        # Draw joint dots (skip face keypoints 0-4)
        for i in range(5, len(kp_xy)):
            if kp_conf[i] > 0.4:
                x, y = int(kp_xy[i][0]), int(kp_xy[i][1])
                cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)
                cv2.circle(frame, (x, y), 7, (57, 255, 20), 2)

    def close(self):
        pass