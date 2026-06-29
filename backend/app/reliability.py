"""Per-value reliability engine (Part 40 — the authoritative reliability law).

The *capture-level* envelope lives in ``capture_quality.py``; this module is the
per-measured-value engine used everywhere a number is emitted:

  * the reliability envelope `{value, confidence, ci, tier, source, status}` (§C),
  * status mapping from calibrated confidence (§E),
  * confidence **composition** — product (independent chain) or **min** (required-all);
    averaging is forbidden (§B.3/§H),
  * **tier caps** (confidence is bounded by the capture grade, §I), reusing the
    Part-35 certification ceilings as the single source of truth,
  * the **abstain** decision (§F) — a first-class result, never a fabricated number.

No heavy imports at module load; the Part-35 schema is loaded lazily only when a
certification cap is requested.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Optional

# --- Status bands (Part 40 §AQ; config defaults, not magic numbers) ---------- #
HIGH = 0.90
MODERATE = 0.70
PRELIMINARY = 0.50
DEFAULT_ABSTAIN = 0.50
UNCALIBRATED_CAP = 0.70  # uncalibrated estimates cannot exceed "preliminary" (§M)

STATUS_VERIFIED = "verified"
STATUS_HIGH = "high"
STATUS_MODERATE = "moderate"
STATUS_PRELIMINARY = "preliminary"
STATUS_UNRELIABLE = "unreliable"
STATUS_ABSTAIN = "abstain"

# --- Per-tier ceilings (Part 40 §I/§L). Certification ceilings are the SoT in
#     the Part-35 schema and are reused via apply_cap(certification=...). -------- #
TIER_CEILING = {"T1": 0.6, "T2": 0.75, "T3": 0.9, "T3_OFFICIATING": 1.0}

# --- Per-domain abstain thresholds (Part 40 §K/§AB; config, not magic numbers).
#     A domain whose confidence falls below its threshold MUST abstain. -------- #
DOMAIN_THRESHOLDS = {
    "ball_detection": 0.50,
    "speed": 0.50,
    "spin": 0.50,
    "stroke": 0.50,
    "event": 0.50,
    "scoreboard": 0.90,   # an OCR digit below 0.9 abstains the read (§K)
    "profile_stat": 0.50,
    "officiating": 0.95,  # decisive calls require near-certainty (§K/§BM)
}


def threshold_for(domain: str) -> float:
    """The abstain threshold for a measurement domain (§K). Unknown → default."""
    return DOMAIN_THRESHOLDS.get(domain, DEFAULT_ABSTAIN)


def clamp01(x: float) -> float:
    x = float(x)
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def status_for(
    confidence: float,
    *,
    calibrated: bool = True,
    validated: bool = False,
    abstain_threshold: float = DEFAULT_ABSTAIN,
) -> str:
    """Map a (capped) confidence to a reliability status (§E).

    Below the domain threshold → abstain. Uncalibrated estimates are capped at
    `preliminary` (§M). `verified` requires external/ground-truth validation (§E).
    """
    c = clamp01(confidence)
    if c < abstain_threshold:
        return STATUS_ABSTAIN
    if not calibrated:
        return STATUS_PRELIMINARY if c >= PRELIMINARY else STATUS_ABSTAIN
    if validated and c >= 0.95:
        return STATUS_VERIFIED
    if c >= HIGH:
        return STATUS_HIGH
    if c >= MODERATE:
        return STATUS_MODERATE
    if c >= PRELIMINARY:
        return STATUS_PRELIMINARY
    return STATUS_UNRELIABLE


def compose(confidences: Iterable[float], mode: str = "chain") -> float:
    """Compose stage confidences. `chain` = product (independent stages),
    `required_all` = min (a single weak required component governs, §H.4).
    Averaging is forbidden (§B.3) — any other mode raises.

    Independence caveat (§H.6): `chain` (product) assumes the stages fail
    *independently*. For **positively correlated** inputs — e.g. the two endpoint
    detections of one inter-frame displacement (same detector, adjacent frames,
    near-identical conditions) — the product **under**-estimates the joint
    confidence (it double-counts shared error), so it is a conservative lower
    bound, not the true value. When the components are both *required* and
    strongly correlated, `required_all` (min) is the better model: it is the exact
    limit under perfect correlation and avoids the spurious independence penalty.
    Reserve `chain` for genuinely independent pipeline stages."""
    cs = [clamp01(c) for c in confidences]
    if not cs:
        return 1.0
    if mode == "chain":
        p = 1.0
        for c in cs:
            p *= c
        return p
    if mode == "required_all":
        return min(cs)
    raise ValueError(
        "compose mode must be 'chain' or 'required_all'; "
        "averaging uncertainty is forbidden (Part 40 §B.3/§H)"
    )


def ceiling_for_tier(tier: Optional[str]) -> float:
    if not tier:
        return 1.0
    return TIER_CEILING.get(str(tier).upper(), 1.0)


def apply_cap(
    confidence: float, *, tier: Optional[str] = None, certification: Optional[str] = None
) -> float:
    """Cap confidence by the capture grade (§I): min(confidence, ceiling).
    Certification ceilings come from the Part-35 schema (single source)."""
    cap = 1.0
    if certification is not None:
        from .capture_quality import load_schema, reliability_ceiling_for  # lazy

        cap = reliability_ceiling_for(certification, load_schema())
    elif tier is not None:
        cap = ceiling_for_tier(tier)
    return min(clamp01(confidence), cap)


@dataclass
class ReliabilityEnvelope:
    """Canonical per-value envelope (Part 40 §C)."""
    value: Any
    confidence: float
    status: str
    tier: Optional[str] = None
    ci: Optional[list] = None
    unit: Optional[str] = None
    calibrated: bool = True
    source: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def build(
    value: Any,
    confidence: float,
    *,
    tier: Optional[str] = None,
    certification: Optional[str] = None,
    ci: Optional[list] = None,
    unit: Optional[str] = None,
    calibrated: bool = True,
    validated: bool = False,
    abstain_threshold: float = DEFAULT_ABSTAIN,
    source: Optional[dict] = None,
) -> ReliabilityEnvelope:
    """Build a reliability envelope, applying the tier cap (§I) and status (§E).
    When the result abstains, `value` is set to `null` (§F) — never fabricated."""
    c = apply_cap(confidence, tier=tier, certification=certification)
    if not calibrated:
        c = min(c, UNCALIBRATED_CAP)
    status = status_for(
        c, calibrated=calibrated, validated=validated, abstain_threshold=abstain_threshold
    )
    return ReliabilityEnvelope(
        value=None if status == STATUS_ABSTAIN else value,
        confidence=round(c, 4),
        status=status,
        tier=tier,
        ci=ci,
        unit=unit,
        calibrated=calibrated,
        source=source or {},
    )


def abstain(
    reason: str,
    *,
    tier: Optional[str] = None,
    unit: Optional[str] = None,
    calibrated: bool = True,
    source: Optional[dict] = None,
) -> ReliabilityEnvelope:
    """An explicit abstention (§F): value=null, status=abstain, reason recorded.
    `unit`/`calibrated` keep the envelope shape consistent with `build()` so an
    abstained value is indistinguishable in schema from a reported one."""
    src = dict(source or {})
    src["abstain_reason"] = reason
    return ReliabilityEnvelope(
        value=None, confidence=0.0, status=STATUS_ABSTAIN, tier=tier,
        unit=unit, calibrated=calibrated, source=src,
    )


def decide(confidence: float, *, threshold: float = DEFAULT_ABSTAIN) -> bool:
    """Selective prediction (§F/§AA): answer iff confidence ≥ threshold."""
    return clamp01(confidence) >= threshold


def summarize(confidence: float, *, tier: Optional[str] = None, calibrated: bool = True) -> dict:
    """Lightweight reliability summary for attaching to a record (capped + status)."""
    c = apply_cap(confidence, tier=tier)
    if not calibrated:
        c = min(c, UNCALIBRATED_CAP)
    return {
        "confidence": round(c, 4),
        "status": status_for(c, calibrated=calibrated),
        "tier": tier,
        "calibrated": calibrated,
    }
