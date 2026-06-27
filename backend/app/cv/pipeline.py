"""Run a BallDetector over a video and derive structured results.

This is a real (classical-CV) derivation from actual detections — not a mock.
Speed is honestly flagged uncalibrated (tier t1). Stroke/spin classification is
a baseline placeholder until pose/deep models land (MASTER_SPEC Parts 05, 18, 26).
"""
from typing import Optional

import cv2

from .detector import BallDetector
from .opencv_detector import OpenCVBallDetector

MAX_GAP = 8  # frames of no-detection that split rallies


def _ms(frame_idx: int, fps: float) -> int:
    return int(frame_idx / max(fps, 1.0) * 1000)


def analyze_video(path: str, detector: Optional[BallDetector] = None) -> dict:
    det = detector or OpenCVBallDetector()
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"could not open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 0
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 0

    track = []  # (frame_idx, x, y, r, conf)
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        d = det.detect(frame, idx)
        if d is not None:
            track.append((idx, d.x, d.y, d.radius, d.confidence))
        idx += 1
    cap.release()

    total = idx
    detection_rate = (len(track) / total) if total else 0.0
    mean_conf = (sum(t[4] for t in track) / len(track)) if track else 0.0
    reliability_index = round(detection_rate * mean_conf, 3)
    px_per_m = (w / 2.74) if w else 0.0  # nominal: assume frame width ~ table length

    # Segment into rallies by detection gaps.
    rallies, current = [], []
    for t in track:
        if current and (t[0] - current[-1][0]) > MAX_GAP:
            rallies.append(current)
            current = []
        current.append(t)
    if current:
        rallies.append(current)

    out_rallies = []
    for ri, seg in enumerate(rallies):
        shots, events, shot_idx = [], [], 0
        wing = "fh"
        # serve marker at rally start
        events.append({
            "type": "serve", "frame": seg[0][0], "ts_ms": _ms(seg[0][0], fps),
            "position": {"x": seg[0][1], "y": seg[0][2]},
            "confidence": round(seg[0][4], 3),
            "provenance": {"source": det.name, "tier": "t1", "signals": ["rally_start"]},
        })
        for i in range(1, len(seg) - 1):
            f0, x0, y0, _, _ = seg[i - 1]
            f1, x1, y1, _, c1 = seg[i]
            f2, x2, y2, _, _ = seg[i + 1]
            if (f1 - f0) != 1 or (f2 - f1) != 1:
                continue
            vx0, vx1 = x1 - x0, x2 - x1
            vy0, vy1 = y1 - y0, y2 - y1
            # Bounce: vertical reversal (was going down, now up)
            if vy0 > 0 and vy1 <= 0:
                events.append({
                    "type": "bounce", "frame": f1, "ts_ms": _ms(f1, fps),
                    "position": {"x": round(x1, 1), "y": round(y1, 1)},
                    "confidence": round(c1, 3),
                    "provenance": {"source": det.name, "tier": "t1", "signals": ["vy_reversal"]},
                })
            # Shot/hit: horizontal reversal
            if vx0 != 0 and vx1 != 0 and (vx0 > 0) != (vx1 > 0):
                speed_px = ((vx0 ** 2 + vy0 ** 2) ** 0.5) * fps
                speed_kmh = round((speed_px / px_per_m) * 3.6, 1) if px_per_m else 0.0
                shots.append({
                    "idx": shot_idx, "frame": f1, "ts_ms": _ms(f1, fps),
                    "stroke_type": "drive", "spin_type": None, "wing": wing,
                    "speed_kmh": speed_kmh, "speed_ci": round(speed_kmh * 0.3, 1),
                    "quality": None, "confidence": round(c1, 3),
                    "provenance": {"source": det.name, "tier": "t1",
                                   "signals": ["vx_reversal"], "speed_calibrated": False},
                })
                shot_idx += 1
                wing = "bh" if wing == "fh" else "fh"

        start_f, end_f = seg[0][0], seg[-1][0]
        duration = round((end_f - start_f) / max(fps, 1.0), 2)
        quality = round(min(1.0, (len(shots) * 0.2 + duration / 15.0)) * 100, 1)
        out_rallies.append({
            "idx": ri, "start_frame": start_f, "end_frame": end_f,
            "start_ms": _ms(start_f, fps), "end_ms": _ms(end_f, fps),
            "duration_sec": duration, "quality": quality,
            "confidence": round(mean_conf, 3),
            "shots": shots, "events": events,
        })

    return {
        "fps": fps, "total_frames": total, "width": w, "height": h,
        "detector": det.name, "detection_rate": round(detection_rate, 3),
        "reliability_index": reliability_index,
        "px_per_m": round(px_per_m, 2), "speed_calibrated": False,
        "rallies": out_rallies,
    }
