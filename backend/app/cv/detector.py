from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class Detection:
    x: float
    y: float
    radius: float
    confidence: float  # 0..1


class BallDetector(Protocol):
    """Per-frame ball detector. Implementations: OpenCVBallDetector (baseline),
    or a deep model (TTNet/TrackNet/YOLO) — same interface (MASTER_SPEC Part 26)."""

    name: str

    def detect(self, frame, frame_idx: int) -> Optional[Detection]:
        ...
