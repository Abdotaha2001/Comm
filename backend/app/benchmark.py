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

from . import calibration as cal
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


def detection_rate_samples(n_clips: int = 3, n_frames: int = 60) -> list[float]:
    """Per-clip detection rates on the golden set — the empirical reference
    distribution used to *fit* the detection-rate OOD gate (Part 40 §Y) instead of
    hard-coding it. NOTE: the golden set is synthetic (an easy, near-1.0 distribution),
    so the fitted reference is a placeholder until representative real footage is
    registered; the OOD fit floors the std to avoid a degenerate gate."""
    det = OpenCVBallDetector()
    rates: list[float] = []
    for _ in range(n_clips):
        fd, path = tempfile.mkstemp(suffix=".avi")
        os.close(fd)
        try:
            write_synthetic_video(path, n_frames=n_frames)
            cap = cv2.VideoCapture(path)
            total = detected = idx = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                total += 1
                if det.detect(frame, idx) is not None:
                    detected += 1
                idx += 1
            cap.release()
            if total:
                rates.append(detected / total)
        finally:
            os.remove(path)
    return rates


def run_scoreboard_benchmark(samples=((3, 1), (21, 19), (7, 2), (11, 9), (0, 0))) -> dict:
    correct = 0
    for p1, p2 in samples:
        img = np.zeros((48, 200, 3), dtype=np.uint8)
        render_scoreboard(img, p1, p2)
        r = read_scoreboard(img)
        if r is not None and (r[0], r[1]) == (p1, p2):
            correct += 1
    return {"samples": len(samples), "accuracy": round(correct / len(samples), 3)}


def run_calibration_benchmark(n_clips: int = 3, n_frames: int = 60, tol_px: float = 5.0) -> dict:
    """Calibration of the detector's confidence on the golden set (Part 40 §G/§N).

    Pairs each detection's confidence with whether it localised the ball within
    `tol_px` of ground truth, then reports ECE/MCE/Brier and how much temperature
    scaling improves the proper score (NLL — the quantity the fit minimises).
    The classical baseline is *uncalibrated* (Part 40 §G.6), so calibration is
    measured + reported here, not hard-gated; the ECE gate (§G.4) applies to
    calibrated models at promotion.
    """
    det = OpenCVBallDetector()
    confs: list[float] = []
    correct: list[bool] = []
    covered = cov_total = 0
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
                if d is not None and idx in gt_map:
                    gx, gy = gt_map[idx]
                    err = ((d.x - gx) ** 2 + (d.y - gy) ** 2) ** 0.5
                    confs.append(d.confidence)
                    correct.append(err <= tol_px)
                    cov_total += 1
                    if err <= d.radius:
                        covered += 1
                idx += 1
            cap.release()
        finally:
            os.remove(path)

    if not confs:
        return {"detector": det.name, "n": 0}

    t = cal.fit_temperature(confs, correct)
    nll_before = cal.nll(confs, correct)
    nll_after = cal.nll(cal.apply_temperature(confs, t), correct)
    report = cal.calibration_report(confs, correct)
    report.update({
        "detector": det.name,
        "calibrated": False,  # classical baseline (Part 40 §G.6)
        "temperature": round(t, 3),
        "nll_before": round(nll_before, 4),
        "nll_after": round(nll_after, 4),
        "ece_after_temperature": round(cal.ece(cal.apply_temperature(confs, t), correct), 4),
        # NLL is what the fit minimises (T=1 is in range) -> guaranteed not worse.
        "calibration_improved": nll_after <= nll_before + 1e-9,
        "localization_picp": round(covered / cov_total, 3) if cov_total else None,
    })
    return report


def calibration_record(n_clips: int = 3, n_frames: int = 60) -> dict:
    """A model-card reliability record for the baseline detector (Part 40 §G.1/§BE).

    Packages the golden-set calibration metrics + the fitted temperature with
    provenance metadata. The classical baseline stays `calibrated=false` (§G.6);
    a trained model would promote only after passing the ECE gate (§G.4).
    """
    from datetime import datetime, timezone

    rep = run_calibration_benchmark(n_clips=n_clips, n_frames=n_frames)
    return {
        "schema": "reliability_model_card_v1",
        "model": rep.get("detector"),
        "calibrated": False,
        "method": "temperature_scaling",
        "dataset": "golden_synthetic",
        "metrics": {
            k: rep.get(k) for k in (
                "ece", "mce", "brier", "temperature",
                "ece_after_temperature", "localization_picp", "n",
            )
        },
        # A persistable, applicable calibrator (Part 40 §G/§BE) — fitted on the
        # golden (synthetic) set; live application awaits a representative set.
        "calibrator": cal.Calibrator(
            temperature=rep.get("temperature", 1.0), dataset="golden_synthetic"
        ).to_dict(),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


if __name__ == "__main__":
    print("detector   :", run_detector_benchmark())
    print("scoreboard :", run_scoreboard_benchmark())
    print("calibration:", run_calibration_benchmark())
    print("model_card :", calibration_record())
