"""Analysis worker: turn a video into persisted match/rally/shot/event rows.

Scaffold runs this inline from the API (synthetic clips are fast). Production
moves it to a queue + GPU workers (Celery/RQ) — same `analyze_run` core, just a
different trigger. The CV detector is pluggable (MASTER_SPEC Part 26).
"""
import functools
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from . import ood, reliability, uncertainty
from .cv.pipeline import analyze_video
from .models import AnalysisRun, Event, Match, Rally, Shot, Video

# Documented prior for the detection-rate OOD / domain-shift gate (Part 40 §Y): a
# representative operating distribution centred a little below the (synthetic) golden
# set, used as the fallback until a real reference is fit.
_DETRATE_OOD_PRIOR = ood.OODGate(mean=0.9, std=0.1, z=3.0)


@functools.lru_cache(maxsize=1)
def _detrate_ood() -> ood.OODGate:
    """Detection-rate OOD reference (Part 40 §Y), *fit from the golden set* rather than
    hard-coded — measured once per process and cached. The std is floored (the synthetic
    golden set is too clean to estimate dispersion), and any failure falls back to the
    documented prior so reference-fitting can never break analysis."""
    try:
        from .benchmark import detection_rate_samples

        samples = detection_rate_samples()
        if len(samples) >= 2:
            return ood.OODGate.fit(samples, z=3.0, min_std=0.1)
    except Exception:  # noqa: BLE001 — never let reference-fitting break analysis
        pass
    return _DETRATE_OOD_PRIOR


def _now():
    return datetime.now(timezone.utc)


def _speed_envelope(shot: dict, tier: str | None, detector: str) -> reliability.ReliabilityEnvelope:
    """Per-shot speed reliability envelope (Part 40 §C/§K/§BH).

    Abstains — regardless of detection confidence — when the speed is undefined or the
    measurement SNR is below ``uncertainty.SNR_MIN`` (displacement not significant vs
    localisation noise: GUM linearisation invalid + ||Δp|| Rician-biased, §BH). Otherwise
    composes the two endpoint detections with `required_all` (min), not an
    independence-assuming product: they are both required and positively correlated
    (adjacent frames), so min is the appropriate, non-double-counting model (§H.6)."""
    prov = shot.get("provenance") or {}
    unc = prov.get("speed_uncertainty") or {}
    speed, ci = shot["speed_kmh"], shot["speed_ci"]
    if not speed or unc.get("significant") is False:
        return reliability.abstain(
            reason=(f"speed measurement SNR {unc.get('snr')} < {uncertainty.SNR_MIN}: "
                    "displacement not significant vs localisation noise (Part 40 §BH)"),
            tier=tier, unit="km/h", calibrated=False,
            source={"model": detector, "measure": "speed",
                    "snr": unc.get("snr"), "snr_min": uncertainty.SNR_MIN},
        )
    inputs = prov.get("speed_inputs_conf") or [shot["confidence"] or 0.0]
    speed_conf = reliability.compose(inputs, "required_all")
    return reliability.build(
        value=speed, confidence=speed_conf, tier=tier,
        ci=([round(speed - ci, 1), round(speed + ci, 1)] if ci else None),
        unit="km/h", calibrated=False,
        abstain_threshold=reliability.threshold_for("speed"),
        source={"model": detector, "measure": "speed", "ci_method": "gum_k2",
                "composition": "required_all", "composed_from": inputs},
    )


def _derive_capture_kpis(result: dict) -> dict:
    """KPIs measurable from the footage itself (operator-supplied values override
    these in the merge). Resolution is the vertical pixel count."""
    det = float(result.get("detection_rate") or 0.0)
    return {
        "resolution": result.get("height"),
        "frame_rate": result.get("fps"),
        "ball_visibility": round(det * 100.0, 1),
        "tracking_success": round(det * 100.0, 1),
        "dropped_frames": 0.0,
        "metadata_completeness": 100.0
        if (result.get("fps") and result.get("width") and result.get("height"))
        else 90.0,
    }


def _capture_acceptance(run, result, measurements, context):
    """Run the Capture Acceptance Framework (Part 35). Returns
    (result, compact_acceptance_dict, reliability_ceiling). Degrades gracefully:
    never fails the analysis."""
    # lazy import: schema load only when used
    from .capture_quality import compute_cqs, load_schema, reliability_ceiling_for

    schema = load_schema()
    merged = {**_derive_capture_kpis(result), **(measurements or {})}
    ctx = {
        "session_id": run.id,
        "software_version": "tt-os-backend",
        "model_version": result.get("detector"),
        **(context or {}),
    }
    res = compute_cqs(merged, context=ctx, schema=schema)
    ceiling = reliability_ceiling_for(res.certification, schema)
    compact = {
        "schema_version": res.schema_version,
        "certification": res.certification,
        "reliability_level": res.reliability_level,
        "capture_tier": res.capture_tier,
        "overall_state": res.overall_state,
        "effective_score": res.effective_score,
        "overall_score": res.overall_score,
        "target_certification": res.target_certification,
        "failed_gates": res.failed_gates,
        "warnings": res.warnings,
        "recommended_actions": res.recommended_actions,
        "reliability_envelope": res.reliability_envelope,
        "provenance_hash": res.provenance["hash"],
        "per_level": res.per_level,
    }
    return res, compact, ceiling


def analyze_run(
    run_id: str,
    db: Session,
    capture_measurements: dict | None = None,
    capture_context: dict | None = None,
) -> str:
    run = db.get(AnalysisRun, run_id)
    if run is None:
        raise ValueError("analysis run not found")
    video = db.get(Video, run.video_id)
    if video is None or not video.storage_key:
        raise ValueError("video missing or has no storage_key")

    run.status = "processing"
    run.started_at = _now()
    db.commit()

    try:
        result = analyze_video(video.storage_key)

        # Scoreboard reliability (§K): the OCR consensus is the confidence; below
        # the scoreboard threshold (0.9) the read abstains.
        score = result.get("score") or {}
        if score:
            score["reliability"] = reliability.summarize(
                score.get("consensus", 0.0), tier=video.capture_tier, calibrated=True
            )
            if score.get("consensus", 0.0) < reliability.threshold_for("scoreboard"):
                score["reliability"]["status"] = reliability.STATUS_ABSTAIN
        match = Match(
            analysis_run_id=run.id,
            video_id=video.id,
            player1_id=video.player_id,
            score=score,
        )
        db.add(match)
        db.flush()

        for r in result["rallies"]:
            rally = Rally(
                match_id=match.id,
                idx=r["idx"],
                start_frame=r["start_frame"],
                end_frame=r["end_frame"],
                start_ms=r["start_ms"],
                end_ms=r["end_ms"],
                reason=None,
                duration_sec=r["duration_sec"],
                quality=r["quality"],
                confidence=r["confidence"],
            )
            db.add(rally)
            db.flush()
            for s in r["shots"]:
                # Per-value reliability envelopes (Part 40 §C/§K), tier-capped.
                # Speed + spin on the classical baseline are uncalibrated/markerless
                # → flagged + capped to "preliminary"; below threshold → abstain.
                # Speed abstains on low measurement SNR too, not just low confidence (§BH).
                speed_env = _speed_envelope(s, video.capture_tier, result["detector"])
                spin_conf = (s.get("provenance") or {}).get("spin_confidence") or 0.0
                spin_env = reliability.build(
                    value=s["spin_type"], confidence=spin_conf,
                    tier=video.capture_tier, calibrated=False,
                    abstain_threshold=reliability.threshold_for("spin"),
                    source={"model": result["detector"], "measure": "spin", "markerless": True},
                )
                db.add(Shot(
                    rally_id=rally.id, idx=s["idx"], frame=s["frame"], ts_ms=s["ts_ms"],
                    stroke_type=s["stroke_type"], spin_type=s["spin_type"], wing=s["wing"],
                    speed_kmh=s["speed_kmh"], speed_ci=s["speed_ci"],
                    quality=s["quality"], confidence=s["confidence"],
                    provenance=s["provenance"],
                    reliability={"speed": speed_env.to_dict(), "spin": spin_env.to_dict()},
                ))
            for e in r["events"]:
                prov = dict(e["provenance"] or {})
                prov["reliability"] = reliability.summarize(
                    e["confidence"] or 0.0, tier=video.capture_tier, calibrated=False
                )
                db.add(Event(
                    rally_id=rally.id, match_id=match.id, type=e["type"],
                    frame=e["frame"], ts_ms=e["ts_ms"], position=e.get("position"),
                    confidence=e["confidence"], provenance=prov,
                ))

        run.reliability_index = result["reliability_index"]
        run.input_quality = {
            "fps": result["fps"], "width": result["width"], "height": result["height"],
            "detection_rate": result["detection_rate"], "speed_calibrated": False,
            # Per-value reliability engine (Part 40): tier-capped status for the run.
            "reliability": reliability.summarize(
                result["reliability_index"], tier=video.capture_tier, calibrated=False
            ),
            # OOD / domain-shift signal vs the golden-set detection-rate reference (§Y),
            # fit from data (cached) rather than hard-coded.
            "ood": {
                "signal": "detection_rate", **_detrate_ood().to_dict(),
                "score": round(_detrate_ood().score(result["detection_rate"]), 2),
                "is_ood": _detrate_ood().is_ood(result["detection_rate"]),
            },
        }
        run.model_versions = {"ball_detector": result["detector"]}

        # Capture certification (Part 35) — only when a capture report is supplied.
        if capture_measurements is not None:
            try:
                res, acceptance, ceiling = _capture_acceptance(
                    run, result, capture_measurements, capture_context
                )
                run.capture_certification = res.certification
                run.capture_acceptance = acceptance
                # The capture grade caps analysis reliability (min, not average —
                # a poor capture can't yield a confident analysis, Part 10).
                footage = result["reliability_index"]
                capped = round(min(footage, ceiling), 4)
                run.reliability_index = capped
                run.input_quality = {
                    **(run.input_quality or {}),
                    "footage_reliability_index": footage,
                    "capture_certification": res.certification,
                    "reliability_status": res.reliability_envelope["status"],
                    "reliability_capped_by_capture": capped < footage,
                }
            except Exception as cap_exc:  # noqa: BLE001 — never fail analysis on this
                run.capture_acceptance = {"error": str(cap_exc)}

        run.status = "done"
        run.finished_at = _now()
        video.status = "done"
        db.commit()
        return match.id
    except Exception as exc:  # noqa: BLE001 — record failure, re-raise
        db.rollback()
        run = db.get(AnalysisRun, run_id)
        run.status = "failed"
        run.error = str(exc)
        run.finished_at = _now()
        db.commit()
        raise
