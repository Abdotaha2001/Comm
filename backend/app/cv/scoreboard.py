"""Render and read a two-score 7-segment scoreboard at a fixed layout.

Scaffold layout is fixed (known cell positions). Production detects the
scoreboard region and reads arbitrary fonts with a deep OCR model (Part 26)
behind the same `read_scoreboard` signature.
"""
from typing import Optional, Tuple

import cv2
import numpy as np

from .sevenseg import decode_digit, render_digit

# Fixed layout (shared by render + read)
OX, OY = 8, 8
DW, DH = 14, 24
GAP = 4           # between the two digits of one score
SCORE_GAP = 14    # between p1 and p2


def _cells():
    x = OX
    p1_tens = (x, OY)
    p1_units = (x + DW + GAP, OY)
    x2 = x + 2 * DW + GAP + SCORE_GAP
    p2_tens = (x2, OY)
    p2_units = (x2 + DW + GAP, OY)
    return p1_tens, p1_units, p2_tens, p2_units


def render_scoreboard(img, p1: int, p2: int) -> None:
    p1t, p1u, p2t, p2u = _cells()
    # dark backing so digits read cleanly
    board_w = (p2u[0] + DW) - OX + 6
    cv2.rectangle(img, (OX - 4, OY - 4), (OX - 4 + board_w, OY + DH + 4), (15, 15, 15), -1)
    for (cx, cy), val in (
        (p1t, p1 // 10), (p1u, p1 % 10), (p2t, p2 // 10), (p2u, p2 % 10)
    ):
        render_digit(img, cx, cy, DW, DH, val)


def read_scoreboard(frame, min_conf: float = 0.99) -> Optional[Tuple[int, int, float]]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    p1t, p1u, p2t, p2u = _cells()
    digits, confs = [], []
    for (cx, cy) in (p1t, p1u, p2t, p2u):
        d, c = decode_digit(gray, cx, cy, DW, DH)
        digits.append(d)
        confs.append(c)
    conf = min(confs)
    if conf < min_conf:
        return None
    p1 = digits[0] * 10 + digits[1]
    p2 = digits[2] * 10 + digits[3]
    return p1, p2, round(conf, 3)
