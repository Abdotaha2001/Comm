import math
from typing import Optional

import cv2
import numpy as np

from .detector import Detection


class OpenCVBallDetector:
    """Classical baseline: find the brightest compact blob and score it by
    circularity. Real (if basic) computer vision — no deep model required.
    Replace with TTNet/TrackNet/YOLO for production accuracy (same interface)."""

    name = "opencv_ball_v1"

    def __init__(self, bright_thresh: int = 200, min_area: float = 6.0):
        self.bright_thresh = bright_thresh
        self.min_area = min_area

    def detect(self, frame, frame_idx: int) -> Optional[Detection]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, self.bright_thresh, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        if area < self.min_area:
            return None
        (x, y), radius = cv2.minEnclosingCircle(c)
        perim = cv2.arcLength(c, True)
        circularity = 4.0 * math.pi * area / (perim * perim + 1e-6)
        confidence = float(np.clip(circularity, 0.0, 1.0))
        return Detection(x=float(x), y=float(y), radius=float(radius), confidence=confidence)
