"""Aggregate a player's analysis data into a style/strengths/weaknesses profile.

Scaffold note: the baseline CV does not yet attribute shots to a specific player
(that needs ReID/identity, Part 04), so a player's own videos are treated as their
shots. Confidence is capped accordingly and scales with sample size (Part 10).
"""
from collections import Counter

from .. import reliability
from ..models import Match, Rally, Shot, Video

ATTACK = {"drive", "loop", "hook_loop", "fade_loop", "counterloop", "smash", "flick", "banana_flick"}
DEFENSE = {"push_short", "push_long", "block", "chop", "lob", "fish", "chop_block"}
MIN_SAMPLE = 10


def _pct(n: int, total: int) -> float:
    return round(n / total * 100, 1) if total else 0.0


def _conf_tag(n: int) -> str:
    return "HIGH" if n >= MIN_SAMPLE * 3 else "MODERATE" if n >= MIN_SAMPLE else "LOW"


def _style(stats: dict) -> str:
    n = stats["total_shots"]
    if n < MIN_SAMPLE:
        return "all_rounder"
    if stats["attack_pct"] >= 55:
        return "fh_looper" if stats["fh_pct"] >= 65 else "two_winged_attacker"
    if stats["shot_dist"].get("chop", 0) + stats["shot_dist"].get("block", 0) >= n * 0.4:
        return "chopper"
    return "all_rounder"


def _strengths(stats: dict) -> list:
    out, n = [], stats["total_shots"]
    if stats["avg_speed_kmh"] and stats["avg_speed_kmh"] > 40:
        out.append({"text": f"High shot speed (~{stats['avg_speed_kmh']} km/h)",
                    "evidence": f"{n} shots", "confidence": _conf_tag(n)})
    if stats["attack_pct"] >= 55:
        out.append({"text": f"Aggressive attacker ({stats['attack_pct']}% attacking shots)",
                    "evidence": f"{n} shots", "confidence": _conf_tag(n)})
    if not out:
        out.append({"text": "No clear strengths yet", "evidence": f"{n} shots", "confidence": "LOW"})
    return out


def _weaknesses(stats: dict) -> list:
    out, sided = [], stats["fh_pct"] + stats["bh_pct"]
    if sided and stats["fh_pct"] >= 75:
        out.append({"text": f"Forehand over-reliance ({stats['fh_pct']}%)",
                    "evidence": "sided shots", "confidence": _conf_tag(stats["total_shots"])})
    if stats["total_shots"] < MIN_SAMPLE:
        out.append({"text": "Insufficient data for reliable weaknesses",
                    "evidence": f"{stats['total_shots']} shots", "confidence": "LOW"})
    return out


def aggregate_profile(db, org_id: str, player_id: str) -> dict:
    base = (
        db.query(Shot)
        .join(Rally, Shot.rally_id == Rally.id)
        .join(Match, Rally.match_id == Match.id)
        .join(Video, Match.video_id == Video.id)
        .filter(Video.player_id == player_id, Video.org_id == org_id)
    )
    shots = base.all()
    rallies = (
        db.query(Rally).join(Match, Rally.match_id == Match.id)
        .join(Video, Match.video_id == Video.id)
        .filter(Video.player_id == player_id, Video.org_id == org_id).all()
    )
    video_ids = [
        v.id for v in db.query(Video)
        .filter(Video.player_id == player_id, Video.org_id == org_id).all()
    ]

    n = len(shots)
    dist = Counter(s.stroke_type for s in shots if s.stroke_type)
    fh = sum(1 for s in shots if s.wing == "fh")
    bh = sum(1 for s in shots if s.wing == "bh")
    speeds = [s.speed_kmh for s in shots if s.speed_kmh]
    attack = sum(c for t, c in dist.items() if t in ATTACK)
    defense = sum(c for t, c in dist.items() if t in DEFENSE)
    durs = [r.duration_sec for r in rallies if r.duration_sec]

    stats = {
        "total_shots": n,
        "n_rallies": len(rallies),
        "shot_dist": dict(dist),
        "fh_pct": _pct(fh, fh + bh),
        "bh_pct": _pct(bh, fh + bh),
        "avg_speed_kmh": round(sum(speeds) / len(speeds), 1) if speeds else 0.0,
        "max_speed_kmh": round(max(speeds), 1) if speeds else 0.0,
        "attack_pct": _pct(attack, n),
        "defense_pct": _pct(defense, n),
        "avg_rally_sec": round(sum(durs) / len(durs), 2) if durs else 0.0,
    }
    confidence = round(min(1.0, n / (MIN_SAMPLE * 3)) * 0.6, 3)  # baseline cap 0.6
    note = "Preliminary — limited data." if n < MIN_SAMPLE else f"{n} shots aggregated."
    # Derived-artifact reliability (Part 40 §AE/§AF): bounded by sample size; the
    # baseline is uncalibrated so the status caps at "preliminary".
    rel = reliability.summarize(confidence, calibrated=False)
    rel["n_shots"] = n
    stats["reliability"] = rel
    return {
        "style_class": _style(stats),
        "aggregated_stats": stats,
        "strengths": _strengths(stats),
        "weaknesses": _weaknesses(stats),
        "source_video_ids": video_ids,
        "confidence": confidence,
        "data_note": note,
    }
