"""Real 7-segment digit rendering + decoding (classical CV, deterministic).

Many scoreboards use 7-seg displays; this is genuine OCR for them and is fully
testable with no model. General-font scoreboards use a deep OCR model
(PaddleOCR/TrOCR — MASTER_SPEC Part 26) behind the same read interface.

Segment indices: 0=a(top) 1=b(top-right) 2=c(bottom-right) 3=d(bottom)
4=e(bottom-left) 5=f(top-left) 6=g(middle).
"""
from typing import Tuple

import cv2
import numpy as np

# digit -> set of lit segment indices
PATTERNS = {
    0: {0, 1, 2, 3, 4, 5},
    1: {1, 2},
    2: {0, 1, 6, 4, 3},
    3: {0, 1, 2, 3, 6},
    4: {5, 6, 1, 2},
    5: {0, 5, 6, 2, 3},
    6: {0, 5, 6, 4, 2, 3},
    7: {0, 1, 2},
    8: {0, 1, 2, 3, 4, 5, 6},
    9: {0, 1, 2, 3, 5, 6},
}
_BITS = {d: tuple(1 if i in segs else 0 for i in range(7)) for d, segs in PATTERNS.items()}


def render_digit(img, x: int, y: int, w: int, h: int, digit: int, color=(255, 255, 255)) -> None:
    t = max(2, int(h * 0.12))
    m = t
    segs = PATTERNS[digit]
    rects = {
        0: ((x + m, y), (x + w - m, y + t)),                      # a
        6: ((x + m, y + h // 2 - t // 2), (x + w - m, y + h // 2 + t // 2)),  # g
        3: ((x + m, y + h - t), (x + w - m, y + h)),              # d
        5: ((x, y + m), (x + t, y + h // 2)),                     # f
        1: ((x + w - t, y + m), (x + w, y + h // 2)),             # b
        4: ((x, y + h // 2), (x + t, y + h - m)),                 # e
        2: ((x + w - t, y + h // 2), (x + w, y + h - m)),         # c
    }
    for seg in segs:
        (x0, y0), (x1, y1) = rects[seg]
        cv2.rectangle(img, (x0, y0), (x1, y1), color, -1)


def _sample(gray, cx: int, cy: int) -> float:
    h, w = gray.shape[:2]
    x0, x1 = max(0, cx - 1), min(w, cx + 2)
    y0, y1 = max(0, cy - 1), min(h, cy + 2)
    return float(gray[y0:y1, x0:x1].mean()) if x1 > x0 and y1 > y0 else 0.0


def decode_digit(gray, x: int, y: int, w: int, h: int, thresh: float = 127.0) -> Tuple[int, float]:
    t = max(2, int(h * 0.12))
    pts = {
        0: (x + w // 2, y + t // 2),
        1: (x + w - t // 2, y + h // 4),
        2: (x + w - t // 2, y + 3 * h // 4),
        3: (x + w // 2, y + h - t // 2),
        4: (x + t // 2, y + 3 * h // 4),
        5: (x + t // 2, y + h // 4),
        6: (x + w // 2, y + h // 2),
    }
    lit = tuple(1 if _sample(gray, *pts[i]) > thresh else 0 for i in range(7))
    best_d, best_ham = 0, 8
    for d, bits in _BITS.items():
        ham = sum(a != b for a, b in zip(lit, bits))
        if ham < best_ham:
            best_ham, best_d = ham, d
    return best_d, round((7 - best_ham) / 7.0, 3)
