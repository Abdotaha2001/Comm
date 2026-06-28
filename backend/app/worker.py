"""Analysis worker: turn a video into persisted match/rally/shot/event rows.

Scaffold runs this inline from the API (synthetic clips are fast). Production
moves it to a queue + GPU workers (Celery/RQ) — same `analyze_run` core, just a
different trigger. The CV detector is pluggable (MASTER_SPEC Part 26).
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .cv.pipeline import analyze_video
from .models import AnalysisRun, Event, Match, Rally, Shot, Video


def _now():
    return datetime.now(timezone.utc)


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
    """Run the Capture Acceptance Framework (Part 35). Returns (certification,
    compact_acceptance_dict). Degrades gracefully: never fails the analysis."""
    from .capture_quality import compute_cqs  # lazy: schema load only when used

    merged = {**_derive_capture_kpis(result), **(measurements or {})}
    ctx = {
        "session_id": run.id,
        "software_version": "tt-os-backend",
        "model_version": result.get("detector"),
        **(context or {}),
    }
    res = compute_cqs(merged, context=ctx)
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
    return res.certification, compact


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

        match = Match(
            analysis_run_id=run.id,
            video_id=video.id,
            player1_id=video.player_id,
            score=result.get("score") or {},
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
                db.add(Shot(
                    rally_id=rally.id, idx=s["idx"], frame=s["frame"], ts_ms=s["ts_ms"],
                    stroke_type=s["stroke_type"], spin_type=s["spin_type"], wing=s["wing"],
                    speed_kmh=s["speed_kmh"], speed_ci=s["speed_ci"],
                    quality=s["quality"], confidence=s["confidence"],
                    provenance=s["provenance"],
                ))
            for e in r["events"]:
                db.add(Event(
                    rally_id=rally.id, match_id=match.id, type=e["type"],
                    frame=e["frame"], ts_ms=e["ts_ms"], position=e.get("position"),
                    confidence=e["confidence"], provenance=e["provenance"],
                ))

        run.reliability_index = result["reliability_index"]
        run.input_quality = {
            "fps": result["fps"], "width": result["width"], "height": result["height"],
            "detection_rate": result["detection_rate"], "speed_calibrated": False,
        }
        run.model_versions = {"ball_detector": result["detector"]}

        # Capture certification (Part 35) — only when a capture report is supplied.
        if capture_measurements is not None:
            try:
                cert, acceptance = _capture_acceptance(
                    run, result, capture_measurements, capture_context
                )
                run.capture_certification = cert
                run.capture_acceptance = acceptance
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
