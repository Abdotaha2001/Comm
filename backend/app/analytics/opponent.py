"""Build an opponent dossier — from an in-system player (use their aggregated
profile) or a sparse external reference (name + footage count)."""
from .profile import aggregate_profile


def build_dossier(db, org_id, subject_player_id, opponent_player_id=None,
                  opponent_ref=None, video_ids=None) -> dict:
    if opponent_player_id:
        prof = aggregate_profile(db, org_id, opponent_player_id)
        return {
            "style_class": prof["style_class"],
            "summary": {
                "weaknesses": prof["weaknesses"],
                "strengths": prof["strengths"],
                "stats": prof["aggregated_stats"],
            },
            "footage_count": len(prof["source_video_ids"]),
            "confidence": prof["confidence"],
        }
    footage = len(video_ids or [])
    return {
        "style_class": None,
        "summary": {"note": "Opponent not in system; minimal dossier from name/footage only."},
        "footage_count": footage,
        "confidence": round(0.1 if footage else 0.05, 3),
    }
