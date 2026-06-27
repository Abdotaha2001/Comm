"""Benchmark harness — 'measure before you trust' (MASTER_SPEC Parts 10, 16).

Evaluates the ball detector (detection rate + localisation error vs ground truth)
and the scoreboard OCR (exact-match accuracy) on synthetic clips with known
truth. The golden-set thresholds in tests/test_benchmark.py act as a regression
gate so accuracy can never silently drop (Part 10.18). Real datasets
(OpenTTGames / TTStroke-21 — Part 26) plug in the same way.

Run:  python -m app.benchmark
"""
import os
import statistics
import tempfile

import cv2
import numpy as np

from .cv.opencv_detector import OpenCVBallDetector
from .cv.scoreboard import read_scoreboard, render_scoreboard
from .cv.synth import write_synthetic_video


def run_detector_benchmark(n_clips: int = 3, n_frames: int = 60) -> dict:
    det = OpenCVBallDetector()
    total = detected = 0
    errors = []
    for _ in range(n_clips):
        fd, path = tempfile.mkstemp(suffix=".avi")
        os.close(fd)
        try:
            _, gt = write_synthetic_video(path, n_frames=n_frames, return_truth=True)
            gt_map = {f: (x, y) for f, x, y in gt}
            cap = cv2.VideoCapture(path)
            idx = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                d = det.detect(frame, idx)
                total += 1
                if d is not None:
                    detected += 1
                    if idx in gt_map:
                        gx, gy = gt_map[idx]
                        errors.append(((d.x - gx) ** 2 + (d.y - gy) ** 2) ** 0.5)
                idx += 1
            cap.release()
        finally:
            os.remove(path)
    return {
        "detector": det.name,
        "clips": n_clips,
        "frames": total,
        "detection_rate": round(detected / total, 3) if total else 0.0,
        "mean_loc_error_px": round(statistics.fmean(errors), 2) if errors else None,
        "max_loc_error_px": round(max(errors), 2) if errors else None,
    }


def run_scoreboard_benchmark(samples=((3, 1), (21, 19), (7, 2), (11, 9), (0, 0))) -> dict:
    correct = 0
    for p1, p2 in samples:
        img = np.zeros((48, 200, 3), dtype=np.uint8)
        render_scoreboard(img, p1, p2)
        r = read_scoreboard(img)
        if r is not None and (r[0], r[1]) == (p1, p2):
            correct += 1
    return {"samples": len(samples), "accuracy": round(correct / len(samples), 3)}


if __name__ == "__main__":
    print("detector :", run_detector_benchmark())
    print("scoreboard:", run_scoreboard_benchmark())
