"""Style-vs-style matchup edge + predicted win probability (rule-based priors
from MASTER_SPEC Part 21). Learned from data later (model M35)."""
from .profile import aggregate_profile

# my_style vs opp_style -> my advantage delta (bounded prior).
EDGES = {
    ("two_winged_attacker", "chopper"): 0.10,
    ("fh_looper", "chopper"): 0.06,
    ("two_winged_attacker", "short_pips_hitter"): 0.08,
    ("fh_looper", "short_pips_hitter"): 0.06,
    ("chopper", "two_winged_attacker"): -0.10,
    ("chopper", "fh_looper"): -0.06,
    ("two_winged_attacker", "combination_chopper"): -0.04,
    ("all_rounder", "chopper"): 0.03,
}


def build_matchup(db, org_id, my_player_id, dossier: dict) -> dict:
    my_prof = aggregate_profile(db, org_id, my_player_id)
    my_style = my_prof["style_class"]
    opp_style = dossier.get("style_class")
    edge = EDGES.get((my_style, opp_style), 0.0)

    # small nudge from relative average speed, if both available
    my_speed = my_prof["aggregated_stats"].get("avg_speed_kmh", 0)
    opp_speed = (dossier.get("summary", {}).get("stats", {}) or {}).get("avg_speed_kmh", 0)
    if my_speed and opp_speed:
        edge += max(-0.05, min(0.05, (my_speed - opp_speed) / 400.0))

    winprob = round(min(0.85, max(0.15, 0.5 + edge)), 3)
    confidence = round(min(my_prof["confidence"], dossier.get("confidence", 0.0)), 3)
    return {
        "predicted_winprob": winprob,
        "confidence": confidence,
        "h2h": {"my_style": my_style, "opp_style": opp_style, "edge": round(edge, 3)},
        "_my_profile": my_prof,
    }
