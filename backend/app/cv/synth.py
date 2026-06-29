"""Generate a synthetic test clip: a bright ball moving and bouncing on a dark
background. Lets us exercise the real CV pipeline end-to-end with no external
video, no GPU, and deterministic content (great for CI)."""
from typing import Optional, Tuple

import cv2
import numpy as np

from .scoreboard import render_scoreboard


def write_synthetic_video(
    path: str,
    n_frames: int = 90,
    w: int = 320,
    h: int = 240,
    fps: int = 30,
    score: Optional[Tuple[int, int]] = None,
    return_truth: bool = False,
):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")  # AVI/MJPG works without ffmpeg
    writer = cv2.VideoWriter(path, fourcc, fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError("could not open VideoWriter (MJPG/AVI)")

    x, y = 20.0, 60.0
    vx, vy = 4.0, 3.0
    g = 0.6  # gravity → bounces
    truth = []
    for fidx in range(n_frames):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        if score is not None:
            render_scoreboard(frame, score[0], score[1])
        vy += g
        x += vx
        y += vy
        if y > h - 12:  # bounce off the "table"
            y = h - 12
            vy = -abs(vy) * 0.8
        if x > w - 12 or x < 12:  # bounce off the sides → a "shot"
            vx = -vx
            x = float(np.clip(x, 12, w - 12))
        cx, cy = int(x), int(y)
        cv2.circle(frame, (cx, cy), 7, (255, 255, 255), -1)
        writer.write(frame)
        truth.append((fidx, float(cx), float(cy)))  # ground-truth ball centre
    writer.release()
    return (path, truth) if return_truth else path
